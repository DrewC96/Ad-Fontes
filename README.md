# Ad Fontes
 
*A semantic search engine for the Church Fathers — pure retrieval, no AI summaries.*
 
## What this is
 
Ad Fontes is a scholarly retrieval application over the full ANF/NPNF corpus (38
volumes, five eras: Apostolic, Ante-Nicene, Nicene, Post-Nicene, Byzantine). Ask a
natural-language question and get back actual patristic passages with citations —
never a paraphrased or AI-generated answer.
 
Orthodox theological framing is the default. On contested doctrinal ground, results
are grouped by tradition (Catholic and Orthodox in v1; Protestant support is
structurally reserved for a later phase) rather than flattened into a single verdict.
 
## Why this doesn't already exist
 
Existing tools each solve half the problem:
 
- **Static archives** (CCEL, New Advent, sacred-texts.com, earlychristianwritings.com)
  host the texts but offer no semantic search and no tradition lens.
- **AI answer apps** (Holy Sophia AI, Magisterium AI, Catholic AI, CatéGPT) either do
  broad semantic search with no tradition grouping, or commit to one tradition and
  generate a summarized answer as if it's the only reading.
Ad Fontes cross-references patristic passages against each tradition's own
systematic sources — Catechism / Denzinger for Catholic, Pomazansky / John of
Damascus for Orthodox — to classify and group results by tradition, while staying
retrieval-only. That combination doesn't exist elsewhere as of this writing.
 
## Current status
 
- ANF Volumes I–II fully ingested and embedded (authors, works, passages in
  Supabase); remaining volumes queued for ingestion.
- Frontend live with real data: full-viewport landing hero with search bar, author
  cards sorted era-chronologically (Apostolic → Byzantine), per-author works pages
  at `/fathers/[slug]`.
- Semantic search live end-to-end: query → server-side Gemini embedding
  (`RETRIEVAL_QUERY`) → `search_passages` Postgres RPC → results rendered as
  torn-parchment passage fragments.
- Database cleaned of parser-artifact rows; author eras corrected and verified.
Not yet built: passage detail view (unrolled-scroll treatment), tradition-alignment
verdicts against reference sources, contested-topic tagging, Protestant tradition
support.
 
## Tech stack
 
| Layer | Choice |
|---|---|
| Frontend | Next.js (JavaScript, App Router), Tailwind CSS v4 |
| Database | Supabase (Postgres + pgvector) |
| Embeddings | Google Gemini `gemini-embedding-001`, 768-dim (Matryoshka truncation) |
| Ingestion pipeline | Python 3.13, `google-genai` SDK |
| Deployment | Vercel |
 
Two intentional design constraints carried through the whole stack:
 
- **Asymmetric embeddings.** Ingestion embeds with task type `RETRIEVAL_DOCUMENT`;
  queries embed with `RETRIEVAL_QUERY`. These are different vectors on purpose —
  don't unify them.
- **Pure retrieval, no summarization.** The app is not permitted to generate or
  paraphrase an answer. It surfaces primary-source passages and lets the reader
  draw conclusions.
## Architecture
 
```
Source texts (CCEL ThML XML)
        │
        ▼
Python pipeline (parse → chunk → embed)
   inspect_thml.py → parse_thml.py → authors_meta.py
   → insert_to_supabase.py → embed.py
        │
        ▼
Supabase (Postgres + pgvector)
   authors · works · passages (+ embedding vector) · eras · traditions
        │
        ▼
Next.js API route (/api/search) — Gemini query embedding (RETRIEVAL_QUERY)
        │
        ▼
search_passages RPC (pgvector similarity search)
        │
        ▼
Search UI — results as .af-fragment cards, citations + source links
```
 
Reference sources used for future tradition-alignment (Catechism, Denzinger,
Pomazansky) are RLS-protected in the database: public access is limited to
citations and alignment verdicts, never full-text display, respecting their
copyright.
 
## Getting started
 
### Prerequisites
 
- Node.js and npm
- Python 3.13 with a virtual environment
- A Supabase project (Postgres + pgvector enabled)
- A Google Gemini API key
### Environment variables (`.env.local`)
 
```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
GEMINI_API_KEY=          # server-side only, no NEXT_PUBLIC_ prefix
```
 
### Install & run
 
```bash
npm install
npm run dev
```
 
### Ingestion pipeline
 
```bash
cd pipeline
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python parse_thml.py
python insert_to_supabase.py
python embed.py
```
 
## Project structure
 
```
/app                 Next.js App Router pages
  /fathers/[slug]     Per-author works pages
  /api/search         Search API route (server-side embedding + RPC call)
/components           Shared UI components
/pipeline             Python ingestion/embedding pipeline
  inspect_thml.py
  parse_thml.py
  authors_meta.py
  insert_to_supabase.py
  embed.py
```
 
## Roadmap
 
1. **Ingest remaining ANF/NPNF volumes** via the Python pipeline.
2. **Passage detail view** — unrolled-scroll treatment (locked design element).
3. **Tradition-alignment feature** — match passages against reference sources,
   surface Catholic/Orthodox alignment verdicts.
4. **Contested-topic tagging** — LLM-assisted tagging across ~15–20 contested
   topics, with human review.
5. **Protestant tradition support** (v2) — schema already reserves an `active`
   boolean on `traditions`; no single authoritative reference source has been
   settled on yet.
## Design principles
 
- No AI-generated answers, ever — retrieval only.
- Semantic, not keyword, search — natural-language questions should surface
  passages that never use the literal query terms.
- Corpus stays patristic-era only; later theology (Aquinas, Calvin, Luther, etc.)
  is out of scope. Denominational nuance is handled by tagging which Fathers each
  tradition emphasizes, not by expanding the corpus.
- Two visual systems: a photoreal warm-study aesthetic for the landing page, and a
  locked parchment component system (oxblood/parchment/gold, Cormorant Garamond
  display, Crimson Pro body, IBM Plex Mono citations) for text-reading UI.
- No scroll-jacking or spatial-navigation animation — rejected as too risky for a
  scholarly audience.
## License & content notes
 
Primary-source texts (ANF/NPNF) are public domain. Reference sources used
internally for tradition alignment (Catechism, Denzinger, Pomazansky) remain under
copyright and are never displayed in full — only cited and linked to an official
source.
 
---
 
*This project also serves as a portfolio piece demonstrating semantic search,
RAG-adjacent retrieval architecture, and multi-tradition theological
classification — built without generative summarization.*
 