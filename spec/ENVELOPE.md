# Answer envelope, receipt and offer delivery (0.1 draft)

The agent sends an answer envelope. The site replies with a receipt. If the user accepted any offers, the site also sends an offer delivery. All three name the manifest hash (SPEC section 6), so either side can later show which version of the manifest the user agreed to. Both sides SHOULD keep a copy.

The snippets below are shortened. The complete files are in `examples/`.

## 1. Answer envelope (agent to site)

```json
{
  "spec": "context-manifest/0.1",
  "manifest_hash": "sha256:a16f7452…",
  "sent": "2026-09-26T21:14:00Z",
  "agent": { "name": "Claude", "client": "claude.ai", "account_hint": "a…@…" },
  "about": "self",
  "answers": [
    {
      "id": "diet",
      "value": { "pattern": "vegetarian", "dislikes": ["coriander"] },
      "provenance": "derived",
      "confidence": 0.85,
      "asked_user": false,
      "retention": "saved"
    },
    {
      "id": "upcoming_events",
      "value": [{ "date": "2026-10-10", "occasion": "dinner for friends" }],
      "provenance": "stated",
      "asked_user": true,
      "retention": "session"
    },
    {
      "id": "household_size",
      "provenance": "declined"
    }
  ],
  "offers_accepted": ["x-cooked_and_rated"],
  "session": { "hint": "web-3f9a", "expires": "2026-09-27T21:14:00Z" }
}
```

Rules:

- `manifest_hash` MUST be the hash of the manifest the user consented to, computed as SPEC section 6 describes. A site that does not recognise the hash MUST reject the envelope with an `unknown_manifest_hash` error.
- Every request in the manifest MUST appear once in `answers`, including declined ones, so the site can tell a refusal from a request the agent never saw.
- `provenance` is `stated` (the user gave the answer during this interaction), `derived` (the agent answered from memory or inference) or `declined`. A declined answer has no `value`.
- A `derived` answer MUST include `confidence`, the agent's honest estimate on a scale from 0 to 1. Sites SHOULD ask the user to confirm on screen any derived answer below 0.6.
- Every answer that is not declined MUST include `retention`, which MUST be the same as the manifest's retention for that request or shorter. An agent MAY downgrade `saved` to `session` and MUST NOT upgrade.
- `about` on the envelope is the default subject of the answers. An answer MAY set its own `about` when the request allowed `either`.
- `agent.account_hint` helps someone on a shared device see which account is sharing. It is at most two characters followed by `…@…`, such as `a…@…`, and MUST NOT include a domain or anything else that identifies the account.
- `offers_accepted` lists the offers the user agreed to receive. If it is missing, the user accepted none.
- `session` is optional. `hint` is a short label the agent can show the user to identify this session, and `expires` is when the agent expects the site's session to end.

## 2. Receipt (site to agent)

```json
{
  "spec": "context-manifest/0.1",
  "kind": "share",
  "receipt_id": "rcpt_01J9SBX3QK",
  "manifest_hash": "sha256:a16f7452…",
  "issued": "2026-09-26T21:14:02Z",
  "stored": [
    { "id": "diet", "retention": "saved", "expires": "2027-09-26T21:14:02Z", "provenance": "derived" }
  ],
  "session_only": ["upcoming_events"],
  "declined": ["household_size"],
  "rejected": [],
  "offers": [{ "id": "x-cooked_and_rated", "fetch": "mcp" }],
  "manage": "https://saltbox.example/context",
  "revoke": "https://saltbox.example/context/revoke",
  "paste_code": "SBX-7K2QM4XD"
}
```

Rules:

- `kind` is `share` for a receipt that answers an envelope, `handoff` for one that answers an envelope sent before the user has an account (section 3), `revocation` for one that confirms a deletion (section 4), and `held` for one that answers `get_shared_context`. A `held` receipt has the same `stored` and `session_only` lists as a share receipt, describing everything the site holds for the user now.
- A share receipt MUST list every id from the envelope in exactly one of `stored`, `session_only`, `declined` or `rejected`. A rejected id has a `reason`: `schema_mismatch` (including a value over its limits, SPEC section 3.3), `unknown_id`, `retention_upgrade`, `low_confidence` or `other`.
- `expires` MUST be computed from the manifest's `ttl`, not from a site default.
- A stored value about someone other than the user MUST have `about: "other"`.
- Each entry in `offers` says how the agent can collect the offer: `mcp` (the `get_offer` tool), `http` (`GET endpoints.share?offers=<id>`) or `paste` (the paste page shows it).
- `paste_code` appears in the paste flow. The user can give it to their assistant to record the receipt. It follows the rules in SPEC section 7.
- Agents SHOULD keep the receipt with their record of having shared, so a later question such as "what does Saltbox know about me?" can be answered without contacting the site.

## 3. Handoff receipt

An envelope sent to `endpoints.handoff` or the `start_handoff` tool (SPEC section 8.4) gets a receipt with `kind: "handoff"`:

```json
{
  "spec": "context-manifest/0.1",
  "kind": "handoff",
  "receipt_id": "rcpt_01JAPMK4XR",
  "manifest_hash": "sha256:5e5c3e47…",
  "issued": "2026-10-03T19:42:10Z",
  "session_only": ["x-running_experience", "time_budget", "x-target_race", "equipment"],
  "declined": ["health_conditions"],
  "rejected": [],
  "handoff": {
    "url": "https://pacemark.example/start/7XQ2MAKDGPZB6WTN3HRV5CYJQF",
    "expires": "2026-10-03T20:42:10Z"
  },
  "manage": "https://pacemark.example/context"
}
```

Rules:

- A handoff receipt MUST list every id from the envelope in exactly one of `session_only`, `declined` or `rejected`. It has no `stored` list, because nothing is saved before the user has an account.
- `handoff.url` is where the user continues in their browser, and `handoff.expires` is when it stops working: no more than 60 minutes after `issued`.
- A handoff receipt has no `paste_code` and no `offers`. Offers need an account, so an agent asks for them again after sign-up.
- A receipt for a paste made before sign-in (SPEC section 8.3) is a handoff receipt without the `handoff` member.

## 4. Revocation

The agent revokes with `revoke({ "ids": ["diet"] })` or `revoke({ "all": true })` over MCP, or with the same body sent to `POST endpoints.revoke`. The site replies with a revocation receipt:

```json
{
  "spec": "context-manifest/0.1",
  "kind": "revocation",
  "receipt_id": "rcpt_01JA2SBX9TW",
  "manifest_hash": "sha256:a16f7452…",
  "issued": "2026-11-02T09:30:11Z",
  "deleted": [
    { "id": "diet", "also_deleted": ["x-recommended_for_you"] },
    { "id": "equipment" }
  ]
}
```

`also_deleted` lists values the site removed because they were derived solely from what was revoked. A site MUST NOT keep a derived value whose only inputs were revoked. It MAY keep aggregate statistics that no longer identify the user.

## 5. Offer delivery (site to agent)

```json
{
  "spec": "context-manifest/0.1",
  "manifest_hash": "sha256:a16f7452…",
  "origin": "https://saltbox.example",
  "issued": "2026-10-14T18:02:40Z",
  "offers": [
    {
      "id": "x-cooked_and_rated",
      "provenance": "observed",
      "as_of": "2026-10-14T18:02:40Z",
      "value": [{ "recipe": "Mushroom and leek pie", "cooked": "2026-10-04", "rating": 5, "times_cooked": 2 }]
    }
  ]
}
```

- An offer delivery contains only offers the user accepted.
- `value` MUST be valid against the offer's `schema` in the manifest.
- `as_of` is when the value was last true. The agent stores it alongside the value, so it can tell recent records from old ones.

## 6. What the agent keeps

For each site, the agent SHOULD keep the manifest hash, the receipt ids, the ids it shared with their provenance, the offers accepted, and the manage and revoke URLs.

It SHOULD NOT keep a separate copy of values it derived, because it already holds the memory they came from. It SHOULD keep values the user stated during the flow, since the user has now told it those things.

## 7. Session

The site defines "session" in plain language at `endpoints.manage`. Reasonable definitions include "until you log out" and "until you close the tab, plus 30 minutes". A site whose session lasts thirty days is not describing a session. An agent MAY refuse `session` retention from a site whose session lasts longer than 24 hours, and treat the request as `saved` when it asks the user for consent.
