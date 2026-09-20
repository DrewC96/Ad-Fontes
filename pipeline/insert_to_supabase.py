"""
Load a parsed volume JSON (from parse_thml.py or parse_thml_npnf1.py) into
Supabase, populating `authors`, `works`, and `passages`. Embeddings are
left NULL here - a separate embed.py pass will fill those in via the
Gemini API, so this script is safe to re-run without burning embedding
API calls.

Setup:
    pip install supabase python-dotenv

Usage:
    python insert_to_supabase.py anf01
    python insert_to_supabase.py npnf101
    python insert_to_supabase.py npnf101 --replace     # delete a work's existing
                                                         # passages before inserting -
                                                         # use when re-running after a
                                                         # parser fix changed passage
                                                         # counts, so stale trailing
                                                         # rows don't linger
    python insert_to_supabase.py npnf101 npnf102 ...    # multiple volumes in one run
    python insert_to_supabase.py --all-npnf1            # all 14 NPNF Series I volumes
    python insert_to_supabase.py --all-npnf1 --replace
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

# Original language per author, by slug (matches slugify() output from the
# parse scripts). Used as a fallback ONLY when AUTHORS_META doesn't already
# specify a language for that author - added because the old hardcoded
# "Greek" default was ANF-specific and silently wrong for NPNF's Augustine
# volumes (Augustine wrote in Latin; Chrysostom in Greek).
ORIGINAL_LANGUAGE_BY_AUTHOR_SLUG = {
    "augustine-of-hippo": "Latin",
    "john-chrysostom": "Greek",
}
DEFAULT_ORIGINAL_LANGUAGE = "Greek"  # preserves prior ANF-era default behavior


def parse_work_id(work_id: str):
    """Return (collection, volume_number) for a work_id.

    - "anf01".."anf38"      -> ("ANF", 1..38)
    - "npnf101".."npnf114"  -> ("NPNF1", 1..14)   (Series I)
    - "npnf201".."npnf214"  -> ("NPNF2", 1..14)   (Series II, once added)

    NOTE: the old approach (int("".join(digit chars))) breaks for NPNF -
    "npnf101" has digits "101", which is the wrong number (should be 1,
    volume 1 of series 1) - it collided the series digit into the volume
    number. This parses series and volume as distinct fields instead.
    """
    if work_id.startswith("anf"):
        return "ANF", int(work_id[len("anf"):])

    if work_id.startswith("npnf"):
        series = work_id[len("npnf")]  # "1" or "2"
        volume_number = int(work_id[len("npnf") + 1:])
        return f"NPNF{series}", volume_number

    raise ValueError(f"Don't know how to parse work_id {work_id!r} - expected an anf* or npnf* prefix")


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
                        collection: str, volume_number: int, original_language: str) -> int:
    existing = supabase.table("works").select("id").eq("slug", work_slug).execute()
    if existing.data:
        return existing.data[0]["id"]

    row = {
        "author_id": author_id,
        "title": title,
        "slug": work_slug,
        "collection": collection,
        "volume_number": volume_number,
        "original_language": original_language,
    }
    result = supabase.table("works").insert(row).execute()
    return result.data[0]["id"]


def delete_existing_passages(supabase, work_id: int):
    supabase.table("passages").delete().eq("work_id", work_id).execute()


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


def main(work_id: str, replace: bool = False):
    collection, volume_number = parse_work_id(work_id)

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

        original_language = ORIGINAL_LANGUAGE_BY_AUTHOR_SLUG.get(
            author["slug"], DEFAULT_ORIGINAL_LANGUAGE
        )

        for work in author["works"]:
            work_id_db = get_or_create_work(
                supabase, author_id, work["slug"], work["title"],
                collection, volume_number, original_language
            )
            if replace:
                delete_existing_passages(supabase, work_id_db)
            count = insert_passages(supabase, work_id_db, work["passages"])
            total_passages += count
            print(f"  Work: {work['title']}  -> {count} passages inserted")

    print(f"\nDone. {total_passages} total passages inserted for {work_id}.")
    print("Embeddings are NULL - run embed.py next before search will work.")


ALL_NPNF1_VOLUMES = [f"npnf1{n:02d}" for n in range(1, 15)]  # npnf101..npnf114


if __name__ == "__main__":
    args = sys.argv[1:]
    replace = "--replace" in args
    args = [a for a in args if a != "--replace"]

    if "--all-npnf1" in args:
        args = [a for a in args if a != "--all-npnf1"]
        work_ids = ALL_NPNF1_VOLUMES
    elif args:
        work_ids = args
    else:
        work_ids = ["anf01"]

    if len(work_ids) == 1:
        main(work_ids[0], replace=replace)
    else:
        summary = []
        for work_id in work_ids:
            print(f"\n=== {work_id} ===")
            try:
                main(work_id, replace=replace)
                summary.append((work_id, "ok"))
            except Exception as e:
                print(f"  ERROR on {work_id}: {e}")
                summary.append((work_id, f"FAILED - {e}"))

        print("\n=== Batch insert summary ===")
        for work_id, status in summary:
            print(f"  {work_id}: {status}")