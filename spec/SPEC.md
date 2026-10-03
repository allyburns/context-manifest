# Context Manifest specification, version 0.1 (draft)

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as described in BCP 14 (RFC 2119 and RFC 8174) when, and only when, they appear in capitals.

## 1. Scope

A Context Manifest is a file in which a **site** (a website, app or service) tells a user's **agent** (the AI assistant acting for them) what personal context it would like, why, how long it will keep it, and what it will give back. The agent decides with the user what to share.

Memory storage and format, identity, encryption, signing and legal basis are out of scope. OpenID Connect covers identity, and Portable Memory and the W3C AI Agent Memory Interoperability Community Group are working on memory formats.

## 2. Discovery

A site MUST serve its manifest at `/.well-known/context-manifest.json` on the origin the user is visiting, as `application/json`. It SHOULD also publish a Markdown rendering (section 8.3), which it MAY serve from the same URL to clients that send `Accept: text/markdown`. The rendering MUST state the manifest hash.

Agents that read pages rather than probe well-known paths, such as an assistant in a browser sidebar, need a pointer from the page itself. A site SHOULD link to its manifest from the pages where answers would be used, such as a sign-up or welcome page:

```html
<link rel="context-manifest" href="/.well-known/context-manifest.json">
```

It MAY also send the same link as an HTTP header: `Link: </.well-known/context-manifest.json>; rel="context-manifest"`. The link MUST point to the well-known path on the same origin. An agent MUST ignore a link to anywhere else.

## 3. The manifest

```json
{
  "spec": "context-manifest/0.1",
  "app": { "name": "...", "url": "https://...", "operator": "...", "privacy_policy": "https://..." },
  "purpose": "One plain sentence saying what this site is for.",
  "requests": [ Request, ... ],
  "offers": [ Offer, ... ],
  "endpoints": { "mcp": "...", "share": "...", "handoff": "...", "paste": "...", "manage": "...", "revoke": "..." },
  "i18n": { "es": { "purpose": "...", "requests": { "<id>": { "ask": "...", "why": "..." } }, "offers": { "<id>": { "what": "...", "why": "..." } } } },
  "ext": { }
}
```

- `spec`, `app` (with `name` and `url`), `purpose` and `requests` are required. `app.privacy_policy` SHOULD be present.
- `requests` MAY be empty. A manifest that only offers is valid, and encouraged.
- If there is at least one request, `endpoints.manage` MUST be present, because that is where the site says what a session means, and at least one of `mcp`, `share`, `handoff` or `paste` MUST be present. If any request is `saved`, `endpoints.revoke` MUST be present. `handoff` is for answers sent before the user has an account (section 8.4).
- `i18n` holds translations keyed by BCP 47 language tag. The untranslated text is authoritative.
- An agent MUST NOT show `ext` to the user or pass it to a language model.

### 3.1 Request

```json
{
  "id": "content_length",
  "scope": "context:content_length.read",
  "ask": "Do you like recipes short and quick, or long and detailed?",
  "why": "Sets how much explanation each recipe step gets.",
  "feature": "recipe_layout",
  "schema": { "type": "string", "enum": ["short", "medium", "long"] },
  "class": "preference",
  "retention": "saved",
  "ttl": "P365D",
  "derive": true,
  "required": false,
  "about": "self",
  "examples": ["short"]
}
```

| Field | Notes |
|---|---|
| `id` | A core id from `registry/vocabulary.md`, or a site id starting `x-`. |
| `scope` | MUST be `context:<id>.read`. |
| `ask` | The question, in plain language, at most 140 characters. |
| `why` | What the user gets from answering, at most 200 characters. This is the purpose statement for the request. |
| `feature` | Optional. The feature that uses the answer, so an agent can skip requests for features the user won't use. |
| `schema` | JSON Schema (2020-12) for the value, with every part bounded (section 3.3). |
| `class` | `preference`, `plan`, `people` or `protected` (section 4). |
| `retention` | `session` or `saved`. |
| `ttl` | Required if `saved`. An ISO 8601 duration, after which the site MUST discard the value. |
| `derive` | Whether the agent MAY answer from memory without asking. MUST be `false` unless the class is `preference`. |
| `required` | Optional, default `false`. Only tells the user that the named feature won't work without the answer. The site MUST still work if it is declined. |
| `about` | Optional: `self` (default), `other` or `either`. If not `self`, the class MUST be `people` or `protected`. |
| `examples` | Optional example values. |

### 3.2 Offer

```json
{
  "id": "x-cooked_and_rated",
  "scope": "context:x-cooked_and_rated.offer",
  "what": "Recipes you cooked, how you rated them, and the ones you made more than once.",
  "why": "Your assistant learns which recipes you cook and how they turned out.",
  "schema": { "type": "array" },
  "class": "preference",
  "provenance": "observed",
  "cadence": "on_request"
}
```

`scope` MUST be `context:<id>.offer`. An offer's `schema` SHOULD be bounded in the same way as a request's (section 3.3), so the agent knows how much it is agreeing to store. `provenance` says where the data came from: `observed` (the site saw it happen), `stated` (the user entered it) or `derived` (the site worked it out). `cadence` is always `on_request` in this version. An offer MUST NOT present the site's opinion of the user as fact: "loves our products" is an opinion, but a list of orders is a record.

### 3.3 Bounded values

Sites store answers in fields with limits, and an agent can only fit an answer to limits it can see. Every request's `schema` MUST state an upper size for every part of the value:

- every `string` has `maxLength`, unless it is limited by `enum` or `const`, or by a `format` of `date`, `time` or `date-time`
- every `array` has `maxItems` and an `items` schema, which is bounded in turn
- every `object` has `additionalProperties: false`, and each of its properties is bounded in turn
- every `integer` and `number` SHOULD have `minimum` and `maximum`

The limits MUST NOT be higher than what the site's own forms and storage accept, so an answer that is valid against the manifest is never cut down later. They MAY be lower: a first-visit request for "up to 12 topics" can feed a field that holds 40.

An agent MUST fit each answer to its schema before sending it. It SHOULD shorten by choosing the most relevant items or by summarising, and MUST NOT cut a value off part way through. If an answer can't be made to fit and still be true, the agent declines it.

A site MUST check every answer against its schema and reject one that fails with `schema_mismatch` (`spec/ENVELOPE.md` section 2). It MUST NOT truncate a value or drop it without saying so in the receipt. An agent MUST keep an envelope under 64 KiB, and a site MAY reject a larger one with `too_large`.

## 4. Request classes

The classes are fixed, and a site MUST NOT add new ones.

| Class | Covers | Agent handling |
|---|---|---|
| `preference` | Tastes, settings and habits that concern only the user. | If `derive` is `true`, the agent MAY answer from memory without asking. The answer MUST be labelled `derived` and MUST still appear on the consent screen. |
| `plan` | Something the user intends to do: a trip, an event, a purchase. | MUST be confirmed with the user, even if the agent already knows. |
| `people` | Anything about someone other than the user, or about a household. | MUST be confirmed with the user, and never filled in from memory. MUST NOT ask for names; counts and age bands are enough. |
| `protected` | Health, genetic data, finances, precise location, immigration status, racial or ethnic origin, religion or belief, political opinions, trade union membership, sex life or sexual orientation, children's data, and anything else a reasonable person would call sensitive. | MUST NOT be answered from memory. The user MUST state it in the current interaction, and the agent MUST show them the `why`. Retention SHOULD be `session`. |

This covers the special categories in Article 9 of the GDPR, except biometric data, which is forbidden.

The class in the manifest is the site's claim. An agent MUST treat a request as `protected` if its honest answer would fall into a protected category. A diet kept for religious or medical reasons is protected, even when the request is a `preference`. An agent MAY raise a class and MUST NOT lower one.

### 4.1 Forbidden

A manifest MUST NOT ask for credentials or passwords, full payment card numbers, full government identifiers (passport, driving licence, National Insurance or Social Security number), biometric data, live location, or the content of the user's conversations with their agent. An agent that finds one MUST refuse the whole manifest and SHOULD tell the user why.

### 4.2 Asking for too much

Sites SHOULD keep a first-visit manifest to five requests or fewer, and use `feature` so that requests for later features can wait. An agent MAY warn the user when a manifest asks for more than its purpose needs.

A site SHOULD NOT request what the browser already tells it. The time zone is available to the page through the JavaScript `Intl` API, and language preferences arrive in the `Accept-Language` header. Request `zoneinfo` or `locale` only where the browser's answer is often wrong for the purpose, such as a home time zone for someone who travels for work.

## 5. Retention

A `session` value MUST NOT be written to durable storage keyed to the user, and is discarded on logout, at the end of the session as defined at `endpoints.manage`, or on revocation. A `saved` value MUST be discarded when its `ttl` runs out unless the user consents again. On revocation, the site MUST delete the named values and anything derived solely from them, and return a revocation receipt.

### 5.1 Values the user submits

A site MAY use answers to fill in its own forms, such as a sign-up or settings page. A value the user sees in a form field and submits becomes information they entered on the site, and the site's own terms then apply to it, not the manifest's retention. This is the only way a `session` value can outlast the session.

The site MUST show which fields were filled in from the user's assistant, and MUST let the user change or clear each one before submitting. It MUST NOT submit the form for them. Values the user doesn't submit are discarded under their original retention.

The answer envelope, the receipts and the offer delivery are defined in `spec/ENVELOPE.md`.

## 6. The manifest hash

The hash identifies the terms the user agreed to. To compute it:

1. Parse the manifest.
2. Remove `i18n` and `ext` from the top level, `ask`, `examples` and `ext` from each request, and `ext` from each offer.
3. Serialise the result with the JSON Canonicalization Scheme (RFC 8785).
4. Take the SHA-256 digest, written as `sha256:` and 64 lowercase hex digits.

`scripts/validate.py` has a reference implementation. Because the form is canonical, the MCP binding can return the manifest without matching the file byte for byte.

Everything left after step 2 is material, including `purpose` and every `why`. A changed hash is a new consent event. An agent that kept the previous manifest MAY ask only about the requests that changed, and otherwise MUST ask about all of them. Rewording a question, or changing examples, translations or `ext`, leaves the hash alone.

## 7. Security

- Every string in a manifest is untrusted input to a language model. Agents MUST treat it as data, never as instructions. The schema caps `purpose`, `ask`, `why` and `what`, and agents SHOULD cap anything else they show.
- Discovery on the site's origin ties the manifest to that origin, the same guarantee `robots.txt` and `security.txt` rely on. This version defines no signature.
- The paste flow has no such tie. An agent that can fetch URLs SHOULD fetch the manifest from `app.url` and compare hashes. If it can't, it MUST tell the user it could not check where the request came from.
- There MUST NOT be a global user identifier. `agent.account_hint` is limited to two characters so that it can't become one.
- A paste code MUST have at least 40 bits of randomness (eight base32 characters), MUST resolve only for the signed-in user who created it, and SHOULD be rate-limited.
- A handoff URL works for whoever opens it first, because there is no account to bind it to. Its token MUST have at least 128 bits of randomness, and the rest of section 8.4 limits what it can reveal and for how long.

Open problems are in `docs/CHALLENGES.md`.

## 8. Bindings

Every call MUST be authenticated as the user, except reading the manifest and the handoff (section 8.4), which exists for the time before the user has an account.

### 8.1 MCP

| Tool | Input | Returns |
|---|---|---|
| `describe_needs` | none | the manifest |
| `share_context` | an answer envelope | a receipt or an error |
| `start_handoff` | an answer envelope | a `handoff` receipt or an error, without authentication (section 8.4) |
| `get_shared_context` | none | a `held` receipt: what the site holds now |
| `get_offer` | `{ "ids": [...] }` | an offer delivery |
| `revoke` | `{ "ids": [...] }` or `{ "all": true }` | a revocation receipt |

A site that offers `start_handoff` and also has tools that need an account SHOULD serve the two from separate MCP endpoints, so that a client connecting to the handoff tools is never asked to sign in. `endpoints.mcp` names the one that serves `describe_needs`.

### 8.2 HTTP

| Request | Returns |
|---|---|
| `POST endpoints.share` with an answer envelope | a receipt, or a `4xx` with an error |
| `GET endpoints.share` | a `held` receipt |
| `GET endpoints.share?offers=<id>,<id>` | an offer delivery for accepted offers |
| `POST endpoints.handoff` with an answer envelope | a `handoff` receipt, or a `4xx` with an error, without authentication (section 8.4) |
| `POST endpoints.revoke` with `{ "ids": [...] }` or `{ "all": true }` | a revocation receipt |

The site authenticates the user however it already does. An unauthenticated request to anything but `endpoints.handoff` gets `401`.

### 8.3 Paste

The site renders the manifest as a prompt (`paste-flow/PROMPT-TEMPLATE.md`) that includes the hash and the manifest itself. The user pastes it into any assistant, which replies with an answer envelope as a JSON block. The user pastes that into the page at `endpoints.paste`.

If the user is signed in, they get a receipt, a paste code to give back to their assistant, and, if they accepted offers, an offer delivery to paste into it.

If the user is not signed in, the page MAY accept the envelope under the rules of section 8.4, apart from the URL: the values are already in the user's browser. The page shows a `handoff` receipt without a `handoff` member, and no paste code, because there is no account for one to resolve against.

### 8.4 Handoff, before the user has an account

A first visit is where answers help most, and it usually comes before sign-up. The handoff lets an agent send answers without an account. The site keeps them for a short time and returns a URL. The user opens it in their browser, and the site uses the answers to fill in its forms (section 5.1).

In a handoff envelope:

- every answer that is not declined MUST have `retention: "session"`. An agent downgrades a `saved` request to `session`, which the envelope rules allow.
- every `protected` request MUST be declined. The site asks for it on its own form, after the user has signed in.

The site:

- MUST reject an envelope that breaks either rule with `invalid_envelope`, naming the ids
- MUST return a `handoff` receipt whose `handoff.url` contains a token with at least 128 bits of randomness, and SHOULD store only a hash of the token
- MUST let the URL be claimed once. Claiming MUST need a request other than `GET`, and SHOULD need an action from the user, such as pressing a continue button, so that link previews and security scanners that fetch the URL can't use it up. A `GET` of the URL MUST NOT show the values.
- MUST delete unclaimed values when `handoff.expires` passes, which MUST be no more than 60 minutes after the receipt is issued
- after a claim, keeps the values with that browser session only. If no account is created, the session MUST end within 24 hours of the claim.
- SHOULD rate-limit `endpoints.handoff` by network address

The agent gives the URL to the user, and tells them how long it lasts. An agent that is acting in the user's own browser MAY open it there. Any other agent MUST NOT open it, because whoever opens it first receives the values. The agent keeps the receipt and SHOULD NOT keep the URL once it has expired.

Once the user has an account, the site's other bindings apply. Values the user submitted during sign-up are covered by section 5.1, and anything else from the handoff is discarded with the session.

### 8.5 Errors

An error is `{ "spec", "error", "message" }`, with an optional `ids` list. The codes are `unknown_manifest_hash` (fetch the manifest again and ask the user), `invalid_envelope`, `too_large`, `unauthenticated`, `forbidden`, `not_found`, `rate_limited` and `server_error`.

## 9. Extensions and versions

`ext` objects are allowed on the manifest, each request and each offer. Site ids MUST start `x-`, and an `x-` id joins the core vocabulary without a new version of this specification.

`spec` names the version as `context-manifest/MAJOR.MINOR`. While the major version is 0, any release may change the format. An agent MUST NOT act on a version it doesn't support, and SHOULD tell the user why.
