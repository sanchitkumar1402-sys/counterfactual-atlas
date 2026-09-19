# Data and content licences

The MIT licence in [LICENSE](LICENSE) covers **the code in this repository only**. The
historical text, images and structured data this project ingests arrive under their own
terms, several of which are share-alike and none of which are ours to relicense.

Every `media_asset` and text record stores its source and licence on the row itself, so
attribution survives the pipeline rather than living only in this file.

| Source | What we take | Licence | What it requires of us |
|---|---|---|---|
| **Wikidata** | Events, entities, places, dates, coordinates | CC0 1.0 | Nothing legally; we attribute anyway |
| **Wikipedia** | Summary and descriptive prose | CC BY-SA 4.0 | Attribution **and** share-alike — derived text must carry CC BY-SA, so it is stored and displayed separately from our own prose, never merged into it |
| **Wikimedia Commons** | Images | Mixed, file by file (CC0 / CC BY / CC BY-SA / PD) | Per-file check; the licence of each file is recorded on its row. Requests must send a descriptive `User-Agent` identifying this project and a contact address |
| **Europeana** | Cultural heritage media and metadata | Mixed; per-item rights statement | API key required. Honour the per-item rights statement; some items are display-only |
| **The Metropolitan Museum of Art** | Open Access images and object metadata | CC0 1.0 | None; attributed as courtesy |
| **Smithsonian Open Access** | Images and object metadata | CC0 1.0 | None; attributed as courtesy |

## Rules this project follows

1. **No mixing of licences in one field.** CC BY-SA prose is stored in its own column and
   rendered with its licence visible. Our own writing stays separately licensed.
2. **AI-generated counterfactual text is our own output**, but it is grounded in sourced
   material — every generated branch links to the events and citations it was built from.
3. **The licence travels with the row.** A media asset without a recorded licence is a bug
   and fails ingestion validation.
4. **`User-Agent` on every Wikimedia request**, identifying the project and a contact.
   Omitting it gets us blocked, correctly.
