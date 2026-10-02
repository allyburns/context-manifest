# Changelog

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
