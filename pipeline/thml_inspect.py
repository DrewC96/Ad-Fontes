"""
Consolidated inspection/diagnostic tooling for the ingestion pipeline.
Replaces: inspect_thml.py, inspect_raw_local.py, inspect_thml_nested.py,
check_letters.py — same behavior, one file, dispatched by subcommand.

Usage:
    python inspect.py fetch anf01
        Download one volume's raw ThML XML from CCEL, save it to
        raw/{work_id}_raw.xml, and print its top-level div1 structure.
        (was: inspect_thml.py)

    python inspect.py top raw/npnf103_raw.xml
        Same top-level structural scan as `fetch`, but reads an
        already-downloaded raw XML file instead of hitting the network.
        Also flags any <div1> elements nested somewhere other than as a
        direct child of ThML.body.
        (was: inspect_raw_local.py)

    python inspect.py nested raw/npnf101_raw.xml "The Confessions"
        Deep-dive into one <div1>'s nested div2/div3/p structure, by
        matching a substring of its title attribute.
        (was: inspect_thml_nested.py)

    python inspect.py letters raw/npnf101_parsed.json
        Sanity-check citation formatting on already-parsed "Letter"
        works in a parsed JSON output file.
        (was: check_letters.py)
"""

import sys
import json
import time
import argparse
import requests
import xml.etree.ElementTree as etree


# ---------------------------------------------------------------------------
# Shared fetch. Deliberately duplicated (not imported) from
# batch_parse_npnf1.py, so this diagnostic tool has no dependency on a
# real pipeline-stage script.
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
# `top` — top-level div1 structural scan (from inspect_thml.py +
# inspect_raw_local.py, merged — the local-file version had a couple of
# extra checks the remote version didn't, so this keeps the superset).
# ---------------------------------------------------------------------------

def inspect_top(xml_bytes: bytes, max_children_shown: int = 60):
    tree = etree.fromstring(xml_bytes)

    print(f"\nRoot tag: <{tree.tag}>")
    print(f"Root attributes: {dict(tree.attrib)}\n")

    body = tree.find("ThML.body")
    if body is None:
        print("No <ThML.body> found — falling back to scanning the whole tree.")
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
# `nested` — deep-dive into one div1's div2/div3/p structure
# (from inspect_thml_nested.py, unchanged)
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
# `letters` — QA check on parsed JSON output for "Letter" works
# (from check_letters.py, unchanged)
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

    p_fetch = sub.add_parser("fetch", help="Download + inspect one volume from CCEL")
    p_fetch.add_argument("work_id", nargs="?", default="anf01")

    p_top = sub.add_parser("top", help="Inspect an already-downloaded raw XML file")
    p_top.add_argument("raw_path", nargs="?", default="raw/npnf103_raw.xml")

    p_nested = sub.add_parser("nested", help="Deep-dive into one div1's nested structure")
    p_nested.add_argument("raw_path")
    p_nested.add_argument("title_substring")

    p_letters = sub.add_parser("letters", help="QA-check Letter works in parsed JSON output")
    p_letters.add_argument("json_path", nargs="?", default="raw/npnf101_parsed.json")

    args = parser.parse_args()

    if args.command == "fetch":
        data = fetch(args.work_id)
        with open(f"raw/{args.work_id}_raw.xml", "wb") as f:
            f.write(data)
        print(f"Saved raw copy to raw/{args.work_id}_raw.xml\n")
        inspect_top(data)

    elif args.command == "top":
        with open(args.raw_path, "rb") as f:
            data = f.read()
        inspect_top(data)

    elif args.command == "nested":
        inspect_nested(args.raw_path, args.title_substring)

    elif args.command == "letters":
        inspect_letters(args.json_path)


if __name__ == "__main__":
    main()
