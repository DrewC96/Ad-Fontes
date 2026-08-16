"""
Load a parsed volume JSON (from parse_thml.py) into Supabase, populating
`authors`, `works`, and `passages`. Embeddings are left NULL here - a
separate embed.py pass will fill those in via the Gemini API, so this
script is safe to re-run without burning embedding API calls.

Setup:
    pip install supabase python-dotenv

Create a `.env` file in this folder (add it to .gitignore!):
    SUPABASE_URL=https://your-project.supabase.co
    SUPABASE_KEY=your-service-role-key   # NOT the anon key - inserts need write access

Usage:
    python insert_to_supabase.py anf01
"""

import sys
import json
import os
from dotenv import load_dotenv
from supabase import create_client

from authors_meta import AUTHORS_META

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]


def get_or_create_era(supabase, era_name: str) -> int:
    existing = supabase.table("eras").select("id").eq("name", era_name).execute()
    if existing.data:
        return existing.data[0]["id"]
    raise ValueError(
        f"Era '{era_name}' not found in `eras` table. "
        f"Seed the eras table first (Apostolic Fathers, Ante-Nicene, "
        f"Nicene, Post-Nicene, Byzantine) before running this script."
    )


def get_or_create_author(supabase, era_cache, slug: str, fallback_name: str) -> int:
    existing = supabase.table("authors").select("id").eq("slug", slug).execute()
    if existing.data:
        return existing.data[0]["id"]

    meta = AUTHORS_META.get(slug)
    if meta is None:
        print(f"  WARNING: no metadata for author slug '{slug}' - inserting with name only")
        row = {"name": fallback_name, "slug": slug}
    else:
        if meta["era"] not in era_cache:
            era_cache[meta["era"]] = get_or_create_era(supabase, meta["era"])
        row = {
            "name": meta["name"],
            "slug": slug,
            "era_id": era_cache[meta["era"]],
            "birth_year": meta["birth_year"],
            "death_year": meta["death_year"],
            "region": meta["region"],
            "bio": meta["bio"],
        }

    result = supabase.table("authors").insert(row).execute()
    return result.data[0]["id"]


def get_or_create_work(supabase, author_id: int, work_slug: str, title: str,
                        collection: str, volume_number: int) -> int:
    existing = supabase.table("works").select("id").eq("slug", work_slug).execute()
    if existing.data:
        return existing.data[0]["id"]

    row = {
        "author_id": author_id,
        "title": title,
        "slug": work_slug,
        "collection": collection,
        "volume_number": volume_number,
        "original_language": "Greek",  # default for ANF; override per-work later if needed
    }
    result = supabase.table("works").insert(row).execute()
    return result.data[0]["id"]


def insert_passages(supabase, work_id: int, passages: list):
    rows = []
    for idx, p in enumerate(passages):
        rows.append({
            "work_id": work_id,
            "chunk_index": idx,
            "citation": p["citation"] or "",
            "chunk_text": p["text"],
            "word_count": p["word_count"],
            # embedding intentionally omitted - filled in by embed.py later
        })

    # Batch insert, 500 rows at a time to stay well under request limits
    batch_size = 500
    inserted = 0
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        supabase.table("passages").upsert(
            batch, on_conflict="work_id,chunk_index"
        ).execute()
        inserted += len(batch)
    return inserted


def main(work_id: str):
    collection = "ANF" if work_id.startswith("anf") else "NPNF"
    volume_number = int("".join(c for c in work_id if c.isdigit()) or 0)

    with open(f"raw/{work_id}_parsed.json", encoding="utf-8") as f:
        data = json.load(f)

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    era_cache = {}

    total_passages = 0
    for author in data:
        author_id = get_or_create_author(
            supabase, era_cache, author["slug"], author["name"]
        )
        print(f"Author: {author['name']} (id={author_id})")

        for work in author["works"]:
            work_id_db = get_or_create_work(
                supabase, author_id, work["slug"], work["title"],
                collection, volume_number
            )
            count = insert_passages(supabase, work_id_db, work["passages"])
            total_passages += count
            print(f"  Work: {work['title']}  -> {count} passages inserted")

    print(f"\nDone. {total_passages} total passages inserted for {work_id}.")
    print("Embeddings are NULL - run embed.py next before search will work.")


if __name__ == "__main__":
    work_id = sys.argv[1] if len(sys.argv) > 1 else "anf01"
    main(work_id)
