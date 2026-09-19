"""
Batch fetch + parse NPNF Series I, volumes 102-114 (101 already done).

Reuses parse_volume() from parse_thml_npnf1.py so every volume goes
through the exact same logic already verified against npnf101 - no
re-implementation, just looping it.

For each volume:
  1. Skip the download if raw/{work_id}_raw.xml already exists (safe
     to re-run; won't re-hit CCEL for volumes you already have).
  2. Otherwise fetch it from CCEL (same URL pattern as inspect_thml.py),
     with the same retry/backoff and 1s courtesy delay between requests.
  3. Parse it with parse_thml_npnf1.parse_volume().
  4. Write raw/{work_id}_parsed.json.
  5. Print a one-line summary so you can eyeball all 13 volumes for
     anything that looks structurally off (e.g. a Chrysostom homily
     volume with a very different div2/div3 pattern) before moving on
     to insert_to_supabase.py.

Usage:
    python batch_parse_npnf1.py
    python batch_parse_npnf1.py npnf105 npnf109   # just specific volumes
"""

import sys
import time
import json
import requests

from parse_thml_npnf1 import parse_volume, NPNF1_AUTHOR_MAP

ALL_VOLUMES = [f"npnf1{n:02d}" for n in range(2, 15)]  # 102..114 (101 already done)


def fetch(work_id: str, max_retries: int = 3) -> bytes:
    url = f"https://ccel.org/ccel/s/schaff/{work_id}.xml"
    print(f"  Fetching {url} ...")
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "ad-fontes-research/0.1 (personal project)"},
                timeout=30,
            )
            resp.raise_for_status()
            time.sleep(1)  # be polite to CCEL between requests
            return resp.content
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"    Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(3)
    raise RuntimeError(f"Failed to fetch {work_id} after {max_retries} attempts") from last_error


def ensure_raw(work_id: str) -> str:
    raw_path = f"raw/{work_id}_raw.xml"
    try:
        with open(raw_path, "rb") as f:
            f.read(1)
        print(f"  raw/{work_id}_raw.xml already exists, skipping download")
        return raw_path
    except FileNotFoundError:
        pass

    data = fetch(work_id)
    with open(raw_path, "wb") as f:
        f.write(data)
    print(f"  Saved raw/{work_id}_raw.xml")
    return raw_path


def process_volume(work_id: str):
    print(f"\n=== {work_id} ({NPNF1_AUTHOR_MAP.get(work_id, 'UNKNOWN AUTHOR')}) ===")
    raw_path = ensure_raw(work_id)

    data = parse_volume(raw_path, work_id)
    out_path = f"raw/{work_id}_parsed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_works = sum(len(a["works"]) for a in data)
    total_passages = sum(w["passage_count"] for a in data for w in a["works"])
    print(f"  Parsed {total_works} works, {total_passages} passages -> {out_path}")
    for a in data:
        for w in a["works"]:
            print(f"    - {w['title']}  [{w['passage_count']} passages]")

    return {"work_id": work_id, "works": total_works, "passages": total_passages}


if __name__ == "__main__":
    volumes = sys.argv[1:] if len(sys.argv) > 1 else ALL_VOLUMES

    unknown = [v for v in volumes if v not in NPNF1_AUTHOR_MAP]
    if unknown:
        print(f"Unknown volume id(s), not in NPNF1_AUTHOR_MAP: {unknown}")
        sys.exit(1)

    summary = []
    for work_id in volumes:
        try:
            summary.append(process_volume(work_id))
        except Exception as e:
            print(f"  ERROR on {work_id}: {e}")
            summary.append({"work_id": work_id, "error": str(e)})

    print("\n=== Batch summary ===")
    for s in summary:
        if "error" in s:
            print(f"  {s['work_id']}: FAILED - {s['error']}")
        else:
            print(f"  {s['work_id']}: {s['works']} works, {s['passages']} passages")
