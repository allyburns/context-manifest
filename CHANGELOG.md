# Changelog

## 0.1 draft, revised 3 October 2026

Still `context-manifest/0.1`: the draft has no implementations yet, so these changes don't take a new version number.

- **Handoff before sign-up.** A new `endpoints.handoff` and MCP tool `start_handoff` accept answers without an account and return a `handoff` receipt with a single-use URL. Only session answers can be handed off, protected requests are declined, and the URL expires within an hour (SPEC section 8.4). The paste flow also works before sign-in.
- **Values the user submits.** A session value the user sees and submits on the site's own form becomes information they entered, and the site must show which fields came from their assistant (SPEC section 5.1).
- **Bounded values.** Every part of a requested value must have a limit no higher than the site accepts. Agents fit answers by choosing or summarising, sites reject what doesn't fit, and envelopes stay under 64 KiB, with a new `too_large` error (SPEC section 3.3).
- **Discovery from the page.** `<link rel="context-manifest">` and a matching `Link` header, for assistants that read pages rather than well-known paths.
- **Don't ask for what the browser knows.** Sites should not request the time zone or language unless the browser's answer is often wrong for the purpose.
- New example: sign-up for a running app, with a handoff envelope, a handoff receipt and a `too_large` error. Every example manifest now bounds its values, so the food example's hash changed. The software example asks how work is tracked today instead of the time zone.
- The validator checks bounded values, that each request's examples fit its schema, and the handoff rules.

## 0.1 (draft, October 2026)

First public draft.

- The manifest, served at `/.well-known/context-manifest.json`, with four fixed request classes and a list of forbidden requests.
- The answer envelope, the receipt (for sharing and for revocation), the offer delivery and the error object, each with a JSON Schema.
- A manifest hash computed over a canonical form (RFC 8785), so that rewording a question or a translation does not force new consent.
- Three bindings: MCP tools, HTTP and a paste flow.
- Six example manifests, plus a complete set of exchanges for the recipe example.
- A validator that checks the examples against the schemas and against the rules a schema can't express.
- Notes on prior art, use cases, open challenges and client behaviour, and a core vocabulary.

Planned for 0.2, not yet agreed:

- `last_confirmed` on each answer
- a `persona` hint for work and personal assistants
- manifest signing
- the site pushing offer updates (`on_change`)
- the MCP binding packaged as an MCP extension
- a reference MCP server and a renderer for the paste prompt
