"""
Parse an NPNF Series I volume's ThML XML into structured records ready
for the Ad Fontes `authors` / `works` / `passages` tables.

Confirmed from inspecting npnf101 and npnf103, NPNF1 volumes come in
(at least) two different shapes:

  Pattern A (npnf101, npnf102): <div1> IS a single work, and its
  internal <div2> subsections carry a `type` attribute directly
  (type="Book"), with <div3 type="Chapter"> nested inside those.

  Pattern B (npnf103, and likely others): <div1> is a COLLECTION
  wrapper ("Doctrinal Treatises of St. Augustin"), and the real works
  live one level down as <div2> children - but critically, those
  work-level <div2> elements carry NO `type` attribute at all (only
  their own internal subsections do, and even then the type value
  varies: "Book", "Chapter", or "Section" depending on the work).

Because of Pattern B, `type` presence can't be used as the front-matter
filter on its own - a real work-level div2 and a front-matter div2 both
lack it. The actual signal that works is the TITLE: front matter
("Introductory Essay", "Translator's Preface", "Argument",
"Introductory Notice", "Preface", "Title Page", etc.) is identifiable
by title regardless of depth or type attribute, and everything else
that isn't front matter is real content.

`type` is still useful, but only for ONE decision: whether a <div1>'s
div2 children are Pattern A (typed - div1 is one work) or Pattern B
(untyped - div1 is a collection of separate works).

Unlike ANF, one NPNF1 volume = one author for the whole file, so the
author isn't in the markup - it comes from NPNF1_AUTHOR_MAP below.

This script does NOT write to Supabase. It writes a JSON file so you
can review/spot-check the parse before running insert_to_supabase.py.

Usage:
    python parse_thml_npnf1.py npnf101
Reads:  raw/npnf101_raw.xml   (from inspect.py fetch / thml_inspect.py)
Writes: raw/npnf101_parsed.json
"""

import sys
import json
import re
import xml.etree.ElementTree as ET

CHUNK_TARGET_WORDS = 250

# One author per NPNF1 volume. Extend this as you pull more volumes.
NPNF1_AUTHOR_MAP = {
    "npnf101": "Augustine of Hippo",
    "npnf102": "Augustine of Hippo",
    "npnf103": "Augustine of Hippo",
    "npnf104": "Augustine of Hippo",
    "npnf105": "Augustine of Hippo",
    "npnf106": "Augustine of Hippo",
    "npnf107": "Augustine of Hippo",
    "npnf108": "Augustine of Hippo",
    "npnf109": "John Chrysostom",
    "npnf110": "John Chrysostom",
    "npnf111": "John Chrysostom",
    "npnf112": "John Chrysostom",
    "npnf113": "John Chrysostom",
    "npnf114": "John Chrysostom",
}

# Front matter is identified by title, matched as a case-insensitive
# substring - deliberately broad, since front-matter section titles
# vary a lot in wording across editors/volumes ("Preface", "Editor's
# Preface", "Preface to the American Edition" all match on "preface").
# Applies at ANY depth (div1, div2, div3).
FRONT_MATTER_TITLE_CONTAINS = (
    "title page",
    "series title",
    "preface",
    "contents",
    "dedication",
    "credits",
    "advertisement",  # publisher's front-matter note, e.g. npnf108's "Advertisement."
    "introduct",  # stem covers "Introduction." AND "Introductory Essay/Notice/Note" ("introduction" alone missed the latter - different suffix)
    "bibliography",
    "abstract",
    "translator's preface",
    "translator\u2019s preface",
    "argument",
    "comparative table",
    "index",  # catches "Index of Subjects", "Subject Index", "Subject Indexes", "Indexes" - all variants
    "the opinion of st. augustin",  # editorial front matter specific to the Confessions volume (npnf101)
    "elucidation",
    "prolegomena",
    "chief events",
    "as a homilist",  # e.g. "St. Chrysostom as a Homilist" - editorial essay
)

# A div2 title that's just a bare numbered label ("Book I", "Letter II",
# "Psalm L", "Homily I on Acts i. 1, 2.") rather than a distinct
# composition title ("On the Holy Trinity", "The Enchiridion"). When
# ALL of a div1's non-front-matter div2 children match this, they're
# numbered parts of ONE work, not separate compositions - see
# find_work_boundaries().
BARE_SUBDIVISION_RE = re.compile(
    r"^(book|chapter|section|letter|homily|psalm|division|canon|oration|"
    r"discourse|epistle|sermon|tractate)\s+[ivxlcdm0-9]+\b",
    re.IGNORECASE,
)


def is_bare_subdivision_title(title: str) -> bool:
    return bool(BARE_SUBDIVISION_RE.match((title or "").strip()))


def slugify(text: str) -> str:
    text = text.lower()
    text = text.replace("\u00e6", "ae").replace("\u0153", "oe")  # æ, œ
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def is_front_matter_title(title: str) -> bool:
    t = (title or "").strip().lower().rstrip(".")
    if not t:
        return True  # untitled containers are never real content
    return any(k in t for k in FRONT_MATTER_TITLE_CONTAINS)


def extract_text_and_refs(p_elem):
    """Return (clean_text, scripture_refs) for one <p>, skipping any
    nested <note> subtree entirely. Unchanged from parse_thml.py."""
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


def normalize_for_compare(s: str) -> str:
    s = s.replace("\u2014", "-").replace("\u2013", "-")  # em/en dash -> hyphen
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.rstrip(".")


def is_heading_restatement(p_text: str, shorttitle: str, title: str) -> bool:
    """True if a paragraph is just '<Shorttitle>.—<Title>' restating the
    div's own heading (e.g. 'Chapter I.—He Proclaims the Greatness of
    God...') rather than actual body prose."""
    if not shorttitle or not title:
        return False
    p_norm = normalize_for_compare(p_text)
    short_norm = normalize_for_compare(shorttitle)
    title_norm = normalize_for_compare(title)
    if not p_norm.startswith(short_norm):
        return False
    remainder = p_norm[len(short_norm):].lstrip(".- ")
    return remainder == title_norm or remainder in title_norm or title_norm in remainder


def collect_paragraphs(elem, results, citation=None, own_title=None, own_shorttitle=None):
    """Recursively walk a work's boundary container (a <div1> in
    Pattern A, or a work-level <div2> in Pattern B), building a
    citation string as we descend through non-front-matter div2/div3
    elements - filtered by TITLE now, not by `type` attribute (see
    module docstring for why).

    A container's OWN direct <p> children are only kept if it has no
    real (non-front-matter) div2/div3 children of its own - containers
    that do have such children open with a few paragraphs of
    running-header/epigraph text before their first real subsection,
    which isn't body prose and gets skipped in favor of the deeper
    content.

    At a leaf level, the very first <p> is often just the section's
    own heading restated (e.g. "Chapter I.—He Proclaims..."),
    duplicating what's already in the citation - skipped via
    is_heading_restatement so it doesn't become a near-empty passage.
    """
    real_children = [
        c for c in elem
        if c.tag in ("div2", "div3") and not is_front_matter_title(c.get("title") or c.get("shorttitle"))
    ]
    has_real_children = len(real_children) > 0
    seen_first_p = False

    for child in elem:
        if child.tag == "note":
            continue

        if child.tag in ("div2", "div3"):
            title = child.get("title") or child.get("shorttitle") or ""
            if is_front_matter_title(title):
                continue  # front matter at any depth - skip whole subtree
            part_label = child.get("shorttitle") or child.get("title") or ""
            child_citation = f"{citation}, {part_label}" if citation else part_label
            collect_paragraphs(
                child, results, citation=child_citation,
                own_title=child.get("title"), own_shorttitle=child.get("shorttitle"),
            )
        elif child.tag == "p":
            if has_real_children:
                continue  # header/epigraph before the first real subsection - skip
            text, refs = extract_text_and_refs(child)
            if text:
                if not seen_first_p and is_heading_restatement(text, own_shorttitle, own_title):
                    seen_first_p = True
                    continue
                seen_first_p = True
                results.append((text, refs, citation))
        else:
            collect_paragraphs(
                child, results, citation=citation,
                own_title=own_title, own_shorttitle=own_shorttitle,
            )


def chunk_paragraphs(paragraphs, target_words=CHUNK_TARGET_WORDS):
    """Group paragraph tuples into ~target_words passages. Never splits
    a single paragraph across two chunks, AND never merges paragraphs
    from two different citations into one chunk - a citation change
    forces a flush even if the word-count target hasn't been reached
    yet."""
    chunks = []
    buf_text, buf_refs, buf_words, buf_citation = [], [], 0, None

    for text, refs, citation in paragraphs:
        word_count = len(text.split())
        citation_changed = buf_citation is not None and citation != buf_citation
        if buf_text and (buf_words + word_count > target_words or citation_changed):
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


def find_work_boundaries(div1):
    """Return a list of (work_title, container_elem) for one <div1>.

    If div1's non-front-matter div2 children carry NO `type` attribute
    AND are not just bare numbered labels of one work's parts ("Book
    I", "Homily I on Acts i. 1, 2.", "Psalm L"), div1 is a Pattern B
    collection wrapper of genuinely separate compositions - each such
    div2 becomes its own work.

    Otherwise - div2s are typed (Pattern A), there are no div2
    children at all (content sits directly under div1), or the div2
    children are ALL bare numbered labels (they're internal parts of
    ONE work, like Book I-VI of "On the Priesthood" or Psalm I-CL of
    "Expositions on the Psalms") - div1 itself is a single work, and
    collect_paragraphs will build the numbered labels into the
    citation string as it descends, same as Pattern A.
    """
    div1_title = div1.get("title") or div1.get("shorttitle") or ""
    non_fm_div2 = [
        c for c in div1.findall("div2")
        if not is_front_matter_title(c.get("title") or c.get("shorttitle"))
    ]
    titles = [c.get("title") or c.get("shorttitle") or "" for c in non_fm_div2]

    is_untyped_collection = non_fm_div2 and not any(c.get("type") for c in non_fm_div2)
    all_bare_subdivisions = titles and all(is_bare_subdivision_title(t) for t in titles)

    if is_untyped_collection and not all_bare_subdivisions:
        return list(zip(titles, non_fm_div2))

    return [(div1_title, div1)]


def parse_volume(path, work_id):
    author_name = NPNF1_AUTHOR_MAP.get(work_id)
    if author_name is None:
        raise ValueError(
            f"No author mapped for {work_id!r} - add it to NPNF1_AUTHOR_MAP"
        )
    author_slug = slugify(author_name)

    tree = ET.parse(path)
    root = tree.getroot()
    body = root.find("ThML.body")

    works_out = []
    seen_slugs = set()

    for div1 in body.findall("div1"):
        div1_title = div1.get("title") or div1.get("shorttitle") or ""
        if is_front_matter_title(div1_title):
            continue

        for work_title, container in find_work_boundaries(div1):
            if is_front_matter_title(work_title):
                continue

            paragraphs = []
            collect_paragraphs(container, paragraphs)
            passages = chunk_paragraphs(paragraphs)

            if not passages:
                continue  # nothing but front matter found here - not a real work

            work_slug = slugify(f"{author_slug}-{work_title}")
            if work_slug in seen_slugs:
                # Defensive: shouldn't normally happen, but avoid silently
                # dropping a duplicate-titled work by disambiguating it.
                work_slug = f"{work_slug}-{len(seen_slugs)}"
            seen_slugs.add(work_slug)

            works_out.append({
                "title": work_title,
                "slug": work_slug,
                "passage_count": len(passages),
                "passages": passages,
            })

    return [{
        "name": author_name,
        "slug": author_slug,
        "works": works_out,
    }]


if __name__ == "__main__":
    work_id = sys.argv[1] if len(sys.argv) > 1 else "npnf101"
    data = parse_volume(f"raw/{work_id}_raw.xml", work_id)

    out_path = f"raw/{work_id}_parsed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_works = sum(len(a["works"]) for a in data)
    total_passages = sum(w["passage_count"] for a in data for w in a["works"])
    print(f"Parsed {len(data)} author(s), {total_works} works, {total_passages} passages")
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