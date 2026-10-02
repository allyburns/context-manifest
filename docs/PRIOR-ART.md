# Prior art

Most decisions in this specification were borrowed from something that came before it, or made to avoid a problem something else ran into. This file lists the sources.

Roughly, formats that ran on what people already had, and did something useful the first time, spread. Formats that needed new storage or a new identity system mostly did not. This one is designed to need neither.

## What it borrows from

### robots.txt (1994)

Martijn Koster's convention is one plain-text file at a known path, with no registry, no signature and no negotiation. A crawler author could implement it in an afternoon and a site owner could write it by hand. It became RFC 9309 in 2022, nearly thirty years later. Context Manifest takes the single file at a known path, written by hand if need be.

### security.txt (RFC 9116)

security.txt started as an Internet-Draft by Edwin Foudil in 2017, became RFC 9116 in 2022 with Yakov Shafranovich as co-author, and is registered in the IANA well-known URI registry. It shows that one person's proposal can become a published standard when the format is small. Context Manifest intends to follow the same route: keep the core small, and register the well-known URI once the format has settled.

### Web App Manifest (W3C, first draft 2013)

`manifest.json` describes a web app with its name, icons, start URL and display mode. Developers already understand a "manifest" to be a small JSON file describing something, and the name was chosen for that reason.

### OAuth 2.0 (2012) and OpenID Connect (2014)

The OAuth consent screen ("this app wants access to your email and calendar") is familiar to almost everyone who uses the web. Scopes are short strings, and consent is a list of them with a line of purpose. OpenID Connect Core also defined standard claim names such as `given_name`, `locale`, `zoneinfo` and `birthdate`. Context Manifest uses a scope string for every request, and reuses OIDC claim names in the core vocabulary wherever one fits.

### vCard and iCalendar

vCard (proposed in 1995, version 2.1 in 1996) and iCalendar (RFC 2445, 1998) are plain text, still in use, and each describes one well-defined kind of thing. Both let anyone add properties prefixed `X-` without waiting for a committee. That is where `x-` ids and `ext` objects come from.

### UK Open Banking (2018)

Open Banking gave UK customers explicit permission lists, an access dashboard at the larger banks where they can see and cancel what they have shared, and a 90-day check. Until 2022 the customer had to re-authenticate with the bank every 90 days. Since then, the provider using the data asks the customer to reconfirm instead. Context Manifest takes `ttl`, the receipt, the manage and revoke endpoints, and new consent when the terms change.

### Global Privacy Control (2020) and Do Not Track (2009)

Both are browser signals that tell sites what the user wants done with their data. Do Not Track, proposed in 2009, asked sites not to track the user. The W3C working group on it closed in January 2019, and Safari removed it the same year. Global Privacy Control, announced in October 2020, asks sites not to sell or share the user's data. California's privacy regulations require businesses to honour signals like it, and in 2022 the California Attorney General's $1.2 million settlement with Sephora cited, among other things, a failure to process it. GPC had a legal duty behind it and DNT did not, which explains much of the difference. Offers are linked to an existing right for the same reason, the right to data portability in Article 20 of the GDPR.

### Apple App Store privacy labels (2020)

Since December 2020, new apps and app updates on the App Store have had to declare what data they collect, in fixed categories such as Contact Info, Health & Fitness, Financial Info, Location, Purchases and Usage Data. Context Manifest takes the idea that the categories are fixed by the specification, not invented by each site. Its four classes are coarser on purpose. `registry/vocabulary.md` maps Apple's categories to them.

### SMART on FHIR (2014)

SMART on FHIR lets apps connect to health records. Version 1 of its App Launch specification (2018) uses scopes such as `patient/Observation.read`: a resource, a dot and an action. Version 2 (2021) added a finer syntax, such as `.rs`. The grammar is small enough to fit in a URL and a log line. Context Manifest uses `context:<id>.read` and `context:<id>.offer`.

### OpenAPI

OpenAPI began as Swagger, created at Wordnik in 2010 and released as open source in 2011. It is a JSON or YAML description of an API, and much of its use comes through the tools built on it, such as generated documentation and client libraries. AI tools read OpenAPI documents directly; ChatGPT's GPT Actions, for example, are defined with one. Context Manifest takes JSON Schema for every value, and the habit of shipping examples alongside the normative text.

### A2A agent cards (2025)

Google announced the Agent2Agent protocol in April 2025. An A2A agent describes itself in a JSON file at `/.well-known/agent-card.json` (renamed from `agent.json` in version 0.3.0), which is registered with IANA. This established that a well-known JSON file for AI agents to discover and read is an accepted pattern. Context Manifest uses the same kind of location and assumes, as A2A does, that a model reads the file before a person does.

### llms.txt (2024)

Jeremy Howard proposed llms.txt in September 2024: a Markdown file that summarises a site for language models. It is easy to write, but there is little evidence that the major AI crawlers fetch it, and Google has said that Search does not use it. The Markdown rendering of a manifest has a narrower job for that reason. It is the text of the paste-flow prompt, which the user copies into their assistant, so it does not depend on any crawler fetching it.

## Harder lessons

### P3P (W3C, 2002)

The Platform for Privacy Preferences is the closest ancestor to this specification. Sites described their privacy practices in machine-readable form so that browsers could act on them. It became a W3C Recommendation in 2002 and was made obsolete in 2018.

The compact form used tokens such as `NOI DSP COR NID`, which few people could read and few site owners could write by hand. Internet Explorer was the only browser that used it seriously, and its main visible effect was cookie filtering. Support in Netscape and Mozilla was partial and later removed.

In response, every `ask` and `why` here is a plain sentence, the user gets something on the first visit, and there is more than one binding, so adoption doesn't depend on one vendor.

### Solid (2016)

Solid began at MIT in 2015 and was released in 2016 under Tim Berners-Lee. Apps ask for access to the user's pod, a personal data store the user hosts themselves or rents from a provider. Personal data servers such as Vana's follow a similar idea. Solid asks a lot of its users and developers: RDF, WebID and a pod to run or rent. Context Manifest needs no setup from the user, because their assistant already holds the memory.

### OpenTravel Alliance (1999)

The OpenTravel Alliance, founded in 1999, publishes message specifications covering most of the travel industry, originally in XML and now also in JSON. Covering a whole industry makes for a large specification. Context Manifest keeps its normative text short and puts its vocabulary in a separate registry that grows as sites need new terms.

### Microformats (2005)

hCard and the other microformats embedded structured data in ordinary HTML. Microformats.org launched in 2005. Google started using them in search results in 2009, and in 2011 Google, Bing and Yahoo launched schema.org with their own vocabulary. Because a format is only useful once something reads it, this repository ships a validator, and a reference MCP server and a renderer for the paste prompt are planned for 0.2.

### Data Transfer Project (2018)

Google, Facebook, Microsoft and Twitter announced the Data Transfer Project in July 2018, Apple joined in 2019, and since 2023 the project has been run by the Data Transfer Initiative. It moves a user's data directly from one service to another. An assistant has a different need: a small, structured record it can use straight away. That is what an offer delivery is for.

## Related work

- `ai-manifest.json` is an IETF individual draft (draft-han-ai-manifest, first published in April 2026). The current revision describes "friction-recovery descriptors": guidance that helps browser agents get through a site's interface. The purpose is different and the name is close, so this project always writes `context-manifest` in full.
- Web Bot Auth: the IETF webbotauth working group is defining how an automated client proves who it is to a site, using HTTP message signatures. The Signature Agent Card is in a separate individual draft. It could later make the envelope's `agent` field verifiable.
- Portable Memory and the W3C AI Agent Memory Interoperability Community Group both deal with how memory is shaped, stored and moved. Portable Memory is a proposal from MacPaw Research (July 2026) for a `.mem` bundle. The W3C community group, chartered in June 2026, covers encrypted memory, sharing, revocation and deletion. Context Manifest does not compete with either, and an offer value could be stored in either format.
- Vana launched a personal server with an MCP endpoint, in beta, in July 2026. A server like this could answer a Context Manifest on the user's behalf in the same way an assistant would.
- MCP elicitation, added in the 2025-06-18 revision, lets a server ask the user for input. A Context Manifest request is close to an elicitation with a purpose, a class, a retention period and permission to answer from memory. The MCP binding in this specification uses tools rather than elicitation. The 2026-07-28 revision of MCP added a formal extensions mechanism, which is the intended home for that binding.
- IEEE 7012-2025 (MyTerms), published in January 2026, lets a person proffer standard privacy terms that a site agrees to. It runs in the opposite direction to a manifest, where the site states what it wants. See the questions section of `CHALLENGES.md` for how the two might fit together.
- ISO/IEC TS 27560:2023 defines a structure for consent records, and the W3C Data Privacy Vocabulary community group has mapped it to DPV. A later version of the receipt could follow that structure.
- Sign in with ChatGPT launched with a limited set of partners, including Airtable, GitLab, HubSpot, Notion, Supabase and Vercel. Signing in gives a site the user's name, email address and profile picture, and does not share their conversations or memory. A site can request further access separately. It shows assistant vendors starting to act as the link between a user and the sites they visit, through their own account systems.
