#!/usr/bin/env python3
"""Validate everything in examples/ against schema/, then check the rules a
JSON Schema cannot express on its own.

File name decides the schema:
  envelope-*.json  answer-envelope.schema.json
  receipt-*.json   receipt.schema.json
  offer-*.json     offer-delivery.schema.json
  error-*.json     error.schema.json
  anything else    context-manifest.schema.json

Cross-checks:
  - each scope is context:<id>.read or context:<id>.offer
  - each id is a core id from registry/vocabulary.md or starts with x-
  - each envelope, receipt and offer delivery names the hash of a manifest
    in examples/, computed as SPEC.md section 6 describes
  - an envelope answers every request exactly once, derives only where the
    manifest allows it, and never upgrades retention
  - a share receipt puts every answered id in exactly one bucket, and its
    expiry dates follow the manifest's ttl when the ttl is in days or weeks
  - an offer delivery contains only accepted offers, each valid against the
    offer's schema in the manifest

Exits non-zero if anything fails.
"""

import copy
import datetime
import hashlib
import json
import re
import sys
from pathlib import Path

import rfc8785
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_FILES = {
    "manifest": "context-manifest.schema.json",
    "envelope": "answer-envelope.schema.json",
    "receipt": "receipt.schema.json",
    "offer": "offer-delivery.schema.json",
    "error": "error.schema.json",
}


def kind_of(path):
    for prefix in ("envelope", "receipt", "offer", "error"):
        if path.name.startswith(prefix + "-"):
            return prefix
    return "manifest"


def manifest_hash(manifest):
    """SPEC.md section 6: drop the non-material members, canonicalise, hash."""
    m = copy.deepcopy(manifest)
    m.pop("i18n", None)
    m.pop("ext", None)
    for r in m.get("requests", []):
        for key in ("ask", "examples", "ext"):
            r.pop(key, None)
    for o in m.get("offers", []):
        o.pop("ext", None)
    return "sha256:" + hashlib.sha256(rfc8785.dumps(m)).hexdigest()


def core_ids():
    text = (ROOT / "registry" / "vocabulary.md").read_text(encoding="utf-8")
    ids = set()
    for line in text.splitlines():
        if line.startswith("| `"):
            first_cell = line.split("|")[1]
            ids.update(re.findall(r"`([a-z][a-z0-9_]+)`", first_cell))
    return ids


def check_manifest(m, core):
    problems = []
    for kind, items, suffix in (("request", m.get("requests", []), "read"), ("offer", m.get("offers", []), "offer")):
        for item in items:
            if item["scope"] != f"context:{item['id']}.{suffix}":
                problems.append(f"{kind} {item['id']}: scope should be context:{item['id']}.{suffix}")
            if not item["id"].startswith("x-") and item["id"] not in core:
                problems.append(f"{kind} {item['id']}: not a core id, so it needs an x- prefix")
    return problems


def check_envelope(env, manifest):
    problems = []
    requests = {r["id"]: r for r in manifest["requests"]}
    answered = [a["id"] for a in env["answers"]]
    for rid in requests:
        if answered.count(rid) != 1:
            problems.append(f"request {rid} answered {answered.count(rid)} times, expected once")
    for a in env["answers"]:
        r = requests.get(a["id"])
        if r is None:
            problems.append(f"answer {a['id']} is not a request in the manifest")
            continue
        if a["provenance"] == "derived" and not (r["class"] == "preference" and r["derive"]):
            problems.append(f"answer {a['id']} is derived, but the manifest does not allow deriving it")
        if a.get("retention") == "saved" and r["retention"] == "session":
            problems.append(f"answer {a['id']} upgrades retention from session to saved")
    offer_ids = {o["id"] for o in manifest.get("offers", [])}
    for oid in env.get("offers_accepted", []):
        if oid not in offer_ids:
            problems.append(f"accepted offer {oid} is not in the manifest")
    return problems


def check_receipt(rcpt, env):
    problems = []
    buckets = (
        [s["id"] for s in rcpt["stored"]]
        + rcpt["session_only"]
        + rcpt["declined"]
        + [r["id"] for r in rcpt["rejected"]]
    )
    for a in env["answers"]:
        if buckets.count(a["id"]) != 1:
            problems.append(f"id {a['id']} appears in {buckets.count(a['id'])} receipt buckets, expected one")
    return problems


def ttl_days(ttl):
    """Days in an ISO 8601 duration made only of weeks and days, else None."""
    m = re.fullmatch(r"P(?:(\d+)W)?(?:(\d+)D)?", ttl or "")
    if not m or not any(m.groups()):
        return None
    return int(m.group(1) or 0) * 7 + int(m.group(2) or 0)


def check_expiry(rcpt, manifest):
    problems = []
    ttls = {r["id"]: r.get("ttl") for r in manifest["requests"]}
    issued = datetime.datetime.fromisoformat(rcpt["issued"].replace("Z", "+00:00"))
    for item in rcpt.get("stored", []):
        days = ttl_days(ttls.get(item["id"]))
        if days is None:
            continue
        expected = issued + datetime.timedelta(days=days)
        actual = datetime.datetime.fromisoformat(item["expires"].replace("Z", "+00:00"))
        if actual != expected:
            problems.append(f"stored {item['id']} expires {item['expires']}, but the ttl gives {expected.isoformat()}")
    return problems


def check_offer_delivery(delivery, manifest, envelope):
    problems = []
    offers = {o["id"]: o for o in manifest.get("offers", [])}
    accepted = set(envelope.get("offers_accepted", [])) if envelope else set()
    for item in delivery["offers"]:
        offer = offers.get(item["id"])
        if offer is None:
            problems.append(f"offer {item['id']} is not in the manifest")
            continue
        if item["id"] not in accepted:
            problems.append(f"offer {item['id']} was not accepted in the envelope")
        if item["provenance"] != offer["provenance"]:
            problems.append(f"offer {item['id']} has provenance {item['provenance']}, the manifest says {offer['provenance']}")
        for err in Draft202012Validator(offer["schema"], format_checker=FormatChecker()).iter_errors(item["value"]):
            problems.append(f"offer {item['id']} value: {err.message}")
    return problems


def main():
    validators = {}
    for kind, name in SCHEMA_FILES.items():
        schema = json.loads((ROOT / "schema" / name).read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        validators[kind] = Draft202012Validator(schema, format_checker=FormatChecker())

    examples = sorted((ROOT / "examples").glob("*.json"))
    if not examples:
        print("No examples found.")
        return 1

    docs, results = {}, {}
    for path in examples:
        kind = kind_of(path)
        problems = []
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            results[path] = (kind, [f"not valid JSON: {exc}"])
            continue
        for err in sorted(validators[kind].iter_errors(doc), key=lambda e: list(e.absolute_path)):
            where = "/".join(str(p) for p in err.absolute_path) or "(root)"
            problems.append(f"{where}: {err.message}")
        docs[path] = (kind, doc)
        results[path] = (kind, problems)

    core = core_ids()
    manifests = {}
    for path, (kind, doc) in docs.items():
        if kind == "manifest":
            manifests[manifest_hash(doc)] = doc
            results[path][1].extend(check_manifest(doc, core))

    envelopes = {}
    for path, (kind, doc) in docs.items():
        if kind in ("envelope", "receipt", "offer") and doc.get("manifest_hash") not in manifests:
            results[path][1].append("manifest_hash does not match any manifest in examples/")
        elif kind == "envelope":
            envelopes[doc["manifest_hash"]] = doc
            results[path][1].extend(check_envelope(doc, manifests[doc["manifest_hash"]]))
    for path, (kind, doc) in docs.items():
        h = doc.get("manifest_hash")
        if kind == "receipt" and h in manifests and doc.get("kind") == "share":
            results[path][1].extend(check_expiry(doc, manifests[h]))
            if h in envelopes:
                results[path][1].extend(check_receipt(doc, envelopes[h]))
        elif kind == "offer" and h in manifests:
            results[path][1].extend(check_offer_delivery(doc, manifests[h], envelopes.get(h)))

    failures = 0
    for path in examples:
        kind, problems = results[path]
        rel = path.relative_to(ROOT)
        if problems:
            failures += 1
            print(f"FAIL  {rel}  [{kind}]")
            for p in problems:
                print(f"      {p}")
        else:
            print(f"PASS  {rel}  [{kind}]")

    print(f"\n{len(examples) - failures} of {len(examples)} examples valid.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
