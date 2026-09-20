"""
Parse an NPNF Series II volume's ThML XML into structured records ready
for the Ad Fontes `authors` / `works` / `passages` tables.

Shares its structural-parsing logic with parse_thml_npnf1.py (front
matter detection by title, Pattern A/B work-boundary detection, bare-
subdivision merging, heading-restatement skip, citation-aware chunking)
- see that file's docstring for the reasoning behind each of those.

The one fundamental difference: NPNF1 is one author per whole volume.
NPNF2 is NOT - several volumes mix multiple authors (Vol. 2: Socrates
& Sozomen; Vol. 3: Theodoret, Jerome, Gennadius, Rufinus; Vol. 13:
Gregory the Great, Ephraim Syrus, Aphrahat), and even a nominally
single-author volume can embed a primary source by someone else
(Vol. 1: Eusebius's "Life of Constantine" embeds Constantine's own
"Oration to the Assembly of the Saints" - that's Constantine's
composition, not Eusebius's, misattributing it would be a real
citation error for a scholarly app).

So instead of one author-per-volume map, this file resolves the author
per WORK, via NPNF2_WORK_AUTHOR_OVERRIDE (exact matches, checked first)
falling back to NPNF2_DEFAULT_AUTHOR (one default per volume, where a
sensible single default exists). If a work matches neither, parsing
FAILS LOUDLY rather than silently mis-attributing it to a guessed
default - add the missing entry and re-run. This is deliberately
stricter than NPNF1_AUTHOR_MAP's simplicity, because silent
misattribution is a worse failure mode than a script error here.

Usage:
    python parse_thml_npnf2.py npnf201
Reads:  raw/npnf201_raw.xml   (from thml_inspect.py fetch)
Writes: raw/npnf201_parsed.json
"""

import sys
import json
import re
import xml.etree.ElementTree as ET

CHUNK_TARGET_WORDS = 250

# One sensible default author per volume, where the volume has one -
# leave a volume OUT of this dict entirely if it's genuinely mixed
# (e.g. Vol. 2, Vol. 3, Vol. 13) so every work in it must be resolved
# via NPNF2_WORK_AUTHOR_OVERRIDE instead (forcing an explicit decision
# per work rather than a guessed default).
NPNF2_DEFAULT_AUTHOR = {
    "npnf201": "Eusebius of Caesarea",
}

# Exceptions to the default above, keyed by volume then by a lowercase
# substring of the work's title (checked with `in`, so partial matches
# work - e.g. "oration of constantine" matches "The Oration of
# Constantine."). Checked BEFORE falling back to NPNF2_DEFAULT_AUTHOR.
NPNF2_WORK_AUTHOR_OVERRIDE = {
    "npnf201": {
        "oration of constantine": "Constantine the Great",
    },
}


def resolve_author(work_id: str, work_title: str) -> str:
    t = work_title.strip().lower().rstrip(".")
    for key, author in NPNF2_WORK_AUTHOR_OVERRIDE.get(work_id, {}).items():
        if key in t:
            return author

    default = NPNF2_DEFAULT_AUTHOR.get(work_id)
    if default is not None:
        return default

    raise ValueError(
        f"Can't resolve an author for work {work_title!r} in {work_id!r} - "
        f"add an entry to NPNF2_WORK_AUTHOR_OVERRIDE (or NPNF2_DEFAULT_AUTHOR "
        f"if this volume turns out to have one sensible default after all)."
    )


# Front matter is identified by title, matched as a case-insensitive
# substring - deliberately broad, since front-matter section titles
# vary a lot in wording across editors/volumes. Applies at ANY depth
# (div1, div2, div3). Shared verbatim with parse_thml_npnf1.py's list -
# keep the two in sync if you add a new pattern in one.
FRONT_MATTER_TITLE_CONTAINS = (
    "title page",
    "series title",
    "preface",
    "contents",
    "dedication",
    "credits",
    "advertisement",
    "introduct",  # stem covers "Introduction." AND "Introductory Essay/Notice/Note"
    "bibliography",
    "abstract",
    "translator's preface",
    "translator\u2019s preface",
    "argument",
    "comparative table",
    "index",  # catches "Index of Subjects", "Subject Index", "Subject Indexes", "Indexes" - all variants
    "elucidation",
    "prolegomena",
    "chief events",
    "as a homilist",
)

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
        return True
    return any(k in t for k in FRONT_MATTER_TITLE_CONTAINS)


def extract_text_and_refs(p_elem):
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
    s = s.replace("\u2014", "-").replace("\u2013", "-")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.rstrip(".")


def is_heading_restatement(p_text: str, shorttitle: str, title: str) -> bool:
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
                continue
            part_label = child.get("shorttitle") or child.get("title") or ""
            child_citation = f"{citation}, {part_label}" if citation else part_label
            collect_paragraphs(
                child, results, citation=child_citation,
                own_title=child.get("title"), own_shorttitle=child.get("shorttitle"),
            )
        elif child.tag == "p":
            if has_real_children:
                continue
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
    tree = ET.parse(path)
    root = tree.getroot()
    body = root.find("ThML.body")

    works_by_author = {}  # author_name -> list of work dicts
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
                continue

            author_name = resolve_author(work_id, work_title)
            author_slug = slugify(author_name)

            work_slug = slugify(f"{author_slug}-{work_title}")
            if work_slug in seen_slugs:
                work_slug = f"{work_slug}-{len(seen_slugs)}"
            seen_slugs.add(work_slug)

            works_by_author.setdefault(author_name, []).append({
                "title": work_title,
                "slug": work_slug,
                "passage_count": len(passages),
                "passages": passages,
            })

    return [
        {"name": name, "slug": slugify(name), "works": works}
        for name, works in works_by_author.items()
    ]


if __name__ == "__main__":
    work_id = sys.argv[1] if len(sys.argv) > 1 else "npnf201"
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
