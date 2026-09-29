# Ad Fontes

_A semantic search engine for the Church Fathers — pure retrieval, no AI summaries._

**Live site: [ad-fontes.net](https://ad-fontes.net)**

## What this is

Ad Fontes is a scholarly retrieval application over the ANF/NPNF corpus (38
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

**Corpus**

- ANF Volumes I–II fully ingested and embedded (authors, works, passages in
  Supabase).
- NPNF Series I pipeline built and partially verified. Volume 1 (Augustine) parses
  cleanly; some later volumes use a different ThML nesting (works as `div2` children
  of a `div1` collection wrapper) and need parser support before batch ingestion.
- NPNF Series II and the remaining volumes are queued.

**Frontend (live at [ad-fontes.net](https://ad-fontes.net))**

- Full-viewport landing hero with search bar, and author cards sorted
  era-chronologically (Apostolic → Byzantine).
- Semantic search end-to-end: query → server-side Gemini embedding
  (`RETRIEVAL_QUERY`) → `search_passages` Postgres RPC → results rendered as
  torn-parchment passage fragments. The query lives in the URL
  (`/search?q=...`), so results are linkable and survive refresh.
- Per-author works pages at `/fathers/[slug]`.
- Work reading page at `/works/[id]`: paginated by chapter (contiguous passages
  sharing a citation), with prev/next navigation and a chapter jump menu.
- Search-to-passage flow: clicking a result opens the right chapter, scrolls to the
  matched passage, and highlights it with a "Matched passage" label. The
  breadcrumb keeps a link back to the originating search
  (`Home › Search: "…" › Author › Work`) through chapter navigation.

**Database**

- Supabase Postgres + pgvector, with a `search_passages` RPC joining passages to
  author/era metadata.
- Row-level security enabled; `passages` has a public read policy for the anon
  key.
- Cleaned of parser-artifact rows; author eras corrected and verified.

**Not yet built:** tradition-alignment verdicts against reference sources,
contested-topic tagging, Protestant tradition support.

## Tech stack

| Layer              | Choice                                                                |
| ------------------ | --------------------------------------------------------------------- |
| Frontend           | Next.js (JavaScript, App Router), Tailwind CSS v4                     |
| Database           | Supabase (Postgres + pgvector)                                        |
| Embeddings         | Google Gemini `gemini-embedding-001`, 768-dim (Matryoshka truncation) |
| Ingestion pipeline | Python 3.13, `google-genai` SDK                                       |
| Deployment         | Vercel (Next.js app only)                                             |

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
   inspect_thml.py → parse_thml.py / parse_thml_npnf1.py → authors_meta.py
   → insert_to_supabase.py → embed.py
        │
        ▼
Supabase (Postgres + pgvector)
   authors · works · passages (+ embedding vector) · eras · traditions
        │
        ▼
Search page (server component) — lib/search: Gemini query embedding
(RETRIEVAL_QUERY), then the search_passages RPC (pgvector similarity)
        │
        ▼
Search UI — results as .af-fragment cards → /works/[id] reading page
(chapter view, matched passage highlighted)
```

Reference sources used for future tradition-alignment (Catechism, Denzinger,
Pomazansky) are RLS-protected in the database: public access is limited to
citations and alignment verdicts, never full-text display, respecting their
copyright.

The Python pipeline runs locally against Supabase; only the Next.js app is
deployed.

## Getting started

### Prerequisites

- Node.js and npm
- A Google Gemini API key (needed for search, since queries are embedded
  server-side)
- To run the ingestion pipeline: Python 3.13 with a virtual environment
- To use your own database: a Supabase project with pgvector enabled

### Environment variables (`.env.local`)

Copy `.env.example` to `.env.local`. It includes a public, read-only Supabase anon
key pointing at the shared project, so you can run the dev server without setting
up your own database (access is limited by row-level security).

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
GEMINI_API_KEY=          # server-side only, no NEXT_PUBLIC_ prefix; supply your own
```

### Install & run

```bash
npm install
npm run dev
```

### Ingestion pipeline

Only needed if you're populating your own database.

```bash
cd pipeline
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python parse_thml.py
python insert_to_supabase.py
python embed.py
```

## Deployment

The app is deployed on [Vercel](https://vercel.com) at
[ad-fontes.net](https://ad-fontes.net).

- Set the three environment variables above in the Vercel project settings.
  `GEMINI_API_KEY` must **not** be prefixed with `NEXT_PUBLIC_`, so it stays on
  the server.
- Deploys run from the Git repository; Vercel builds the Next.js app only. The
  Python pipeline is never deployed.
- The app currently runs on free tiers (Vercel Hobby, Supabase free). If the
  database outgrows the 500 MB free limit as more volumes are ingested, options
  include upgrading to Supabase Pro or sharding passages across projects.

## Project structure

```
/src
  /app                 Next.js App Router pages
    page.js, HomeClient.js   Landing page
    /search            Search results page (server component)
    /fathers/[slug]    Per-author works pages
    /works/[id]        Chapter reading page
      ChapterJump.js   Chapter dropdown (client)
      PassageList.js   Passage rendering + matched-passage highlight (client)
    /api               API routes
  /components          Shared UI (Breadcrumb, BackToTop, ...)
  /lib                 search.js (embedding + RPC), trail.js (search breadcrumb trail)
/pipeline              Python ingestion/embedding pipeline
  inspect_thml.py
  parse_thml.py
  parse_thml_npnf1.py
  batch_parse_npnf1.py
  authors_meta.py
  insert_to_supabase.py
  embed.py
```

## Roadmap

1. **Ingest remaining ANF/NPNF volumes** — finish NPNF Series I (parser support for
   collection-wrapper volumes), then NPNF Series II.
2. **Tradition-alignment feature** — match passages against reference sources,
   surface Catholic/Orthodox alignment verdicts.
3. **Contested-topic tagging** — LLM-assisted tagging across ~15–20 contested
   topics, with human review.
4. **Protestant tradition support** (v2) — schema already reserves an `active`
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
- Motion is progressive enhancement: subtle animation on desktop, static on
  mobile, and respecting `prefers-reduced-motion` everywhere.
- No scroll-jacking or spatial-navigation animation — rejected as too risky for a
  scholarly audience.

## License & content notes

Primary-source texts (ANF/NPNF) are public domain. Reference sources used
internally for tradition alignment (Catechism, Denzinger, Pomazansky) remain under
copyright and are never displayed in full — only cited and linked to an official
source.

---

_This project also serves as a portfolio piece demonstrating semantic search,
RAG-adjacent retrieval architecture, and multi-tradition theological
classification — built without generative summarization._
