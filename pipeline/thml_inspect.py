"""
Consolidated inspection/diagnostic tooling for the ingestion pipeline.
Replaces: inspect_thml.py, inspect_raw_local.py, inspect_thml_nested.py,
check_letters.py - same behavior, one file, dispatched by subcommand.
(Named thml_inspect.py, NOT inspect.py - a file called inspect.py shadows
Python's own stdlib `inspect` module and breaks imports.)

Usage:
    python thml_inspect.py fetch anf01
    python thml_inspect.py fetch npnf205 npnf206 npnf207
        Download one or more volumes' raw ThML XML from CCEL, save each to
        raw/{work_id}_raw.xml. With a single volume, also prints its
        top-level div1 structure. With several, just saves them and prints
        a summary (a failed download is reported at the end and doesn't
        abort the rest).

    python thml_inspect.py top raw/npnf103_raw.xml
        Top-level structural scan of an already-downloaded raw XML file.
        Also flags any <div1> elements nested somewhere other than as a
        direct child of ThML.body.

    python thml_inspect.py nested raw/npnf101_raw.xml "The Confessions"
        Deep-dive into one <div1>'s nested div2/div3/p structure, by
        matching a substring of its title attribute.

    python thml_inspect.py works npnf205 npnf206 npnf207
        Preview which WORKS parse_thml.py would create for each volume
        (after front-matter filtering and work-boundary detection), with
        passage counts - WITHOUT resolving authors. Use this to see every
        work title in a volume at once, so all the author overrides for
        it can be written in one pass instead of discovering them one
        parse failure at a time. Needs raw/{work_id}_raw.xml already
        downloaded (see `fetch`).

    python thml_inspect.py letters raw/npnf101_parsed.json
        Sanity-check citation formatting on already-parsed "Letter"
        works in a parsed JSON output file.
"""

import os
import sys
import json
import time
import argparse
import requests
import xml.etree.ElementTree as etree


# ---------------------------------------------------------------------------
# Shared fetch. Deliberately duplicated (not imported) from a pipeline
# stage script, so the fetch/top/nested/letters tools have no dependency
# on parse_thml.py. (Only the `works` subcommand imports from it, lazily.)
# ---------------------------------------------------------------------------

def fetch(work_id: str, max_retries: int = 3) -> bytes:
    url = f"https://ccel.org/ccel/s/schaff/{work_id}.xml"
    print(f"Fetching {url} ...")
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(
                url,
                headers={"User-Agent": "ad-fontes-research/0.1 (personal project)"},
                timeout=30,
            )
            resp.raise_for_status()
            time.sleep(1)
            return resp.content
        except requests.exceptions.RequestException as e:
            last_error = e
            print(f"  Attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(3)
    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts") from last_error


# ---------------------------------------------------------------------------
# `top` - top-level div1 structural scan
# ---------------------------------------------------------------------------

def inspect_top(xml_bytes: bytes, max_children_shown: int = 60):
    tree = etree.fromstring(xml_bytes)

    print(f"\nRoot tag: <{tree.tag}>")
    print(f"Root attributes: {dict(tree.attrib)}\n")

    body = tree.find("ThML.body")
    if body is None:
        print("No <ThML.body> found - falling back to scanning the whole tree.")
        body = tree

    print("ThML.body direct children (tag counts):")
    tag_counts = {}
    for child in body:
        tag_counts[child.tag] = tag_counts.get(child.tag, 0) + 1
    for tag, count in tag_counts.items():
        print(f"  <{tag}>: {count}")

    print(f"\nAll direct children of ThML.body (up to {max_children_shown}), with their own child tag counts:")
    for i, child in enumerate(body):
        if i >= max_children_shown:
            print("  ...")
            break
        title = child.get("title", "")
        child_tag_counts = {}
        for grandchild in child:
            child_tag_counts[grandchild.tag] = child_tag_counts.get(grandchild.tag, 0) + 1
        print(f"  [{i}] <{child.tag}> title={title!r}")
        print(f"       children: {child_tag_counts}")

    all_div1 = tree.findall(".//div1")
    direct_div1 = body.findall("div1")
    print(f"\nTotal <div1> ANYWHERE in document (.//div1): {len(all_div1)}")
    print(f"Direct <div1> children of ThML.body only: {len(direct_div1)}")
    if len(all_div1) != len(direct_div1):
        print("  -> MISMATCH: some <div1> elements are nested inside something else,")
        print("     not direct children of ThML.body. Listing the non-direct ones:")
        direct_ids = {id(d) for d in direct_div1}
        for d in all_div1:
            if id(d) not in direct_ids:
                print(f"     - {d.get('title', '(no title)')!r}")

    scrip_refs = tree.findall(".//scripRef")
    foreign = tree.findall(".//foreign")
    print(f"\n<scripRef> count: {len(scrip_refs)}")
    print(f"<foreign> count: {len(foreign)}")


# ---------------------------------------------------------------------------
# `nested` - deep-dive into one div1's div2/div3/p structure
# ---------------------------------------------------------------------------

def find_div1_by_title(tree, title_substring: str):
    for div1 in tree.findall(".//div1"):
        if title_substring.lower() in div1.get("title", "").lower():
            return div1
    return None


def describe(el, depth=0, max_depth=3, max_children=15):
    indent = "  " * depth
    title = el.get("title", "")
    n = el.get("n", "")
    print(f"{indent}<{el.tag}> title={title!r} n={n!r} attrs={dict(el.attrib)}")
    if depth >= max_depth:
        return
    children_by_tag = {}
    for child in el:
        children_by_tag.setdefault(child.tag, []).append(child)

    for tag, children in children_by_tag.items():
        print(f"{indent}  [{len(children)}x <{tag}>]")
        for child in children[:max_children]:
            describe(child, depth + 2, max_depth, max_children)
        if len(children) > max_children:
            print(f"{indent}    ... ({len(children) - max_children} more <{tag}> not shown)")


def inspect_nested(path: str, title_substring: str):
    tree = etree.parse(path).getroot()

    div1 = find_div1_by_title(tree, title_substring)
    if div1 is None:
        print(f"No <div1> found matching {title_substring!r}. Available titles:")
        for d in tree.findall(".//div1"):
            print(f"  - {d.get('title', '(no title)')}")
        sys.exit(1)

    print(f"Found div1: {div1.get('title')!r}\n")
    describe(div1, max_depth=4, max_children=6)

    sample_p = div1.find(".//p")
    if sample_p is not None:
        print("\nSample <p> element (inner structure):")
        print(f"  attrs: {dict(sample_p.attrib)}")
        print(f"  text preview: {(sample_p.text or '')[:200]!r}")
        print(f"  child tags inside this <p>: {[c.tag for c in sample_p]}")


# ---------------------------------------------------------------------------
# `works` - preview the works parse_thml.py would create, minus authors
# ---------------------------------------------------------------------------

def inspect_works(work_id: str):
    # Lazy import: only this subcommand depends on the parser, so the
    # other diagnostic tools keep working even if parse_thml.py is mid-edit.
    from parse_thml import (
        is_front_matter_title,
        find_work_boundaries,
        _npnf_collect_paragraphs,
        _npnf_chunk_paragraphs,
    )

    path = f"raw/{work_id}_raw.xml"
    if not os.path.exists(path):
        print(f"=== {work_id} === MISSING {path} - run `python thml_inspect.py fetch {work_id}` first\n")
        return

    root = etree.parse(path).getroot()
    body = root.find("ThML.body")

    print(f"=== {work_id} ===")
    total_works = 0
    total_passages = 0
    for div1 in body.findall("div1"):
        div1_title = div1.get("title") or div1.get("shorttitle") or ""
        if is_front_matter_title(div1_title):
            continue

        boundaries = find_work_boundaries(div1)
        is_collection = not (len(boundaries) == 1 and boundaries[0][1] is div1)
        mode = "COLLECTION of separate works" if is_collection else "single work"
        print(f"\n  [div1] {div1_title!r}  ({mode})")

        for work_title, container in boundaries:
            if is_front_matter_title(work_title):
                continue
            paragraphs = []
            _npnf_collect_paragraphs(container, paragraphs)
            passages = _npnf_chunk_paragraphs(paragraphs)
            if not passages:
                continue
            total_works += 1
            total_passages += len(passages)
            print(f"      - {work_title!r}  [{len(passages)} passages]")

    print(f"\n  => {total_works} works, {total_passages} passages\n")


# ---------------------------------------------------------------------------
# `letters` - QA check on parsed JSON output for "Letter" works
# ---------------------------------------------------------------------------

def inspect_letters(path: str):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for author in data:
        for work in author["works"]:
            if "letter" in work["title"].lower():
                print(f"Work: {work['title']}  ({work['passage_count']} passages)\n")
                citations_seen = [p["citation"] for p in work["passages"][:20]]
                print("First 20 citations:")
                for c in citations_seen:
                    print(f"  {c!r}")
                print("\nSample passage (first one):")
                sample = work["passages"][0]
                print(f"  citation={sample['citation']!r}, words={sample['word_count']}")
                print(f"  {sample['text'][:300]}")


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="Download one or more volumes from CCEL")
    p_fetch.add_argument("work_ids", nargs="*", default=["anf01"])

    p_top = sub.add_parser("top", help="Inspect an already-downloaded raw XML file")
    p_top.add_argument("raw_path", nargs="?", default="raw/npnf103_raw.xml")

    p_nested = sub.add_parser("nested", help="Deep-dive into one div1's nested structure")
    p_nested.add_argument("raw_path")
    p_nested.add_argument("title_substring")

    p_works = sub.add_parser("works", help="Preview the works the parser would create, minus authors")
    p_works.add_argument("work_ids", nargs="+")

    p_letters = sub.add_parser("letters", help="QA-check Letter works in parsed JSON output")
    p_letters.add_argument("json_path", nargs="?", default="raw/npnf101_parsed.json")

    args = parser.parse_args()

    if args.command == "fetch":
        os.makedirs("raw", exist_ok=True)
        failures = []
        for work_id in args.work_ids:
            try:
                data = fetch(work_id)
            except Exception as e:
                print(f"  FAILED: {work_id}: {e}\n")
                failures.append(work_id)
                continue
            with open(f"raw/{work_id}_raw.xml", "wb") as f:
                f.write(data)
            print(f"Saved raw copy to raw/{work_id}_raw.xml")
            if len(args.work_ids) == 1:
                inspect_top(data)

        if len(args.work_ids) > 1:
            ok = [w for w in args.work_ids if w not in failures]
            print(f"\nDownloaded {len(ok)}/{len(args.work_ids)}: {', '.join(ok) or '(none)'}")
            if failures:
                print(f"FAILED (re-run just these): {' '.join(failures)}")

    elif args.command == "top":
        with open(args.raw_path, "rb") as f:
            data = f.read()
        inspect_top(data)

    elif args.command == "nested":
        inspect_nested(args.raw_path, args.title_substring)

    elif args.command == "works":
        for work_id in args.work_ids:
            inspect_works(work_id)

    elif args.command == "letters":
        inspect_letters(args.json_path)


if __name__ == "__main__":
    main()