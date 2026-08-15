"""
Parse an ANF (or NPNF) volume's ThML XML into structured records ready
for the Ad Fontes `authors` / `works` / `passages` tables.

Confirmed structure (from raw/anf01_raw.xml):
    ThML > ThML.body > div1 (author) > div2 (work) > div3 (chapter, optional) > p (paragraph)
    <note place="end"> footnotes are inline in the body and must be
        skipped entirely - they contain their own <p class="endnote">
        elements that are NOT part of the main text.
    <scripRef osisRef="..." passage="..."> scripture citations are
        already hand-tagged - capture them for the later scripture
        cross-reference layer instead of re-detecting them.

This script does NOT write to Supabase. It writes a JSON file so you
can review/spot-check the parse before we build the DB insert step.

Usage:
    python parse_thml.py anf01
Reads:  raw/anf01_raw.xml   (from inspect_thml.py)
Writes: raw/anf01_parsed.json
"""

import sys
import json
import re
import xml.etree.ElementTree as ET

CHUNK_TARGET_WORDS = 250


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("\u00e6", "ae").replace("\u0153", "oe")  # æ, œ
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def extract_text_and_refs(p_elem):
    """Return (clean_text, scripture_refs) for one <p>, skipping any
    nested <note> subtree entirely."""
    text_parts = []
    scrip_refs = []

    def walk(node):
        if node.tag == "note":
            return
        if node.text:
            text_parts.append(node.text)
        for child in node:
            if child.tag == "scripRef":
                scrip_refs.append({
                    "osisRef": child.get("osisRef"),
                    "passage": child.get("passage"),
                })
            walk(child)
            if child.tail:
                text_parts.append(child.tail)

    walk(p_elem)
    text = " ".join(t.strip() for t in text_parts if t and t.strip())
    text = re.sub(r"\s+", " ", text).strip()
    return text, scrip_refs


def collect_paragraphs(elem, results, citation=None):
    """Recursively walk a <div2>, tracking the nearest div3 title as the
    citation context, collecting (text, refs, citation) per real <p>.
    Never descends into <note> - footnote paragraphs are excluded."""
    for child in elem:
        if child.tag == "note":
            continue
        if child.tag == "div3":
            child_citation = child.get("title") or child.get("shorttitle") or citation
            collect_paragraphs(child, results, citation=child_citation)
        elif child.tag == "p":
            text, refs = extract_text_and_refs(child)
            if text:
                results.append((text, refs, citation))
        else:
            collect_paragraphs(child, results, citation=citation)


def chunk_paragraphs(paragraphs, target_words=CHUNK_TARGET_WORDS):
    """Group paragraph tuples into ~target_words passages. Never splits
    a single paragraph across two chunks."""
    chunks = []
    buf_text, buf_refs, buf_words, buf_citation = [], [], 0, None

    for text, refs, citation in paragraphs:
        word_count = len(text.split())
        if buf_words + word_count > target_words and buf_text:
            chunks.append({
                "text": " ".join(buf_text),
                "word_count": buf_words,
                "citation": buf_citation,
                "scripture_refs": buf_refs,
            })
            buf_text, buf_refs, buf_words, buf_citation = [], [], 0, None

        buf_text.append(text)
        buf_refs.extend(refs)
        buf_words += word_count
        if buf_citation is None:
            buf_citation = citation

    if buf_text:
        chunks.append({
            "text": " ".join(buf_text),
            "word_count": buf_words,
            "citation": buf_citation,
            "scripture_refs": buf_refs,
        })
    return chunks


def parse_volume(path):
    tree = ET.parse(path)
    root = tree.getroot()
    body = root.find("ThML.body")

    authors_out = []

    for div1 in body.findall("div1"):
        author_title = div1.get("title") or div1.get("shorttitle") or ""
        if author_title.strip().lower() == "title page":
            continue  # front matter, not a work

        author_slug = slugify(author_title)
        works_out = []

        div2s = div1.findall("div2")
        if not div2s:
            div2s = [div1]  # fallback: no work-level split, treat div1 as one work

        for div2 in div2s:
            work_title = div2.get("title") or div2.get("shorttitle") or author_title
            work_slug = slugify(f"{author_slug}-{work_title}")

            paragraphs = []
            collect_paragraphs(div2, paragraphs)
            passages = chunk_paragraphs(paragraphs)

            works_out.append({
                "title": work_title,
                "slug": work_slug,
                "passage_count": len(passages),
                "passages": passages,
            })

        authors_out.append({
            "name": author_title.title(),
            "slug": author_slug,
            "works": works_out,
        })

    return authors_out


if __name__ == "__main__":
    work_id = sys.argv[1] if len(sys.argv) > 1 else "anf01"
    data = parse_volume(f"raw/{work_id}_raw.xml")

    out_path = f"raw/{work_id}_parsed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_works = sum(len(a["works"]) for a in data)
    total_passages = sum(w["passage_count"] for a in data for w in a["works"])
    print(f"Parsed {len(data)} authors, {total_works} works, {total_passages} passages")
    print(f"Written to {out_path}\n")

    print("Author / work breakdown:")
    for a in data:
        print(f"  {a['name']} ({len(a['works'])} works)")
        for w in a["works"]:
            print(f"    - {w['title']}  [{w['passage_count']} passages]")

    if data and data[0]["works"] and data[0]["works"][0]["passages"]:
        sample = data[0]["works"][0]["passages"][0]
        print(f"\nSample passage (citation={sample['citation']!r}, {sample['word_count']} words):")
        print(f"  {sample['text'][:300]}...")
