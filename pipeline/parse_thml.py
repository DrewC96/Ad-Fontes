"""
Parse an ANF, NPNF Series I, or NPNF Series II volume's ThML XML into
structured records ready for the Ad Fontes `authors` / `works` /
`passages` tables. Dispatches on the work_id prefix - one entry point
for all three collections, replacing the three separate parse_thml*.py
files (same consolidation pattern as thml_inspect.py for inspection).

    anf01..anf38      -> parse_anf_volume()   (unchanged legacy logic)
    npnf101..npnf114   -> parse_npnf_volume() with NPNF1's author resolver
    npnf201..npnf214   -> parse_npnf_volume() with NPNF2's author resolver

--- ANF (div1 = author) ---
Confirmed structure (from raw/anf01_raw.xml):
    ThML > ThML.body > div1 (author) > div2 (work) > div3 (chapter, optional) > p (paragraph)
Kept exactly as originally written - already validated and ingested,
so no reason to route it through the newer NPNF logic below.

--- NPNF1 / NPNF2 (div1 = work, or a collection of works) ---
NPNF1 volumes come in two shapes:
  Pattern A (npnf101, npnf102): <div1> IS a single work, and its
  internal <div2> subsections carry a `type` attribute directly
  (type="Book"), with <div3 type="Chapter"> nested inside those.
  Pattern B (npnf103, and others): <div1> is a COLLECTION wrapper
  ("Doctrinal Treatises of St. Augustin"), and the real works live one
  level down as <div2> children - but those work-level <div2> elements
  carry NO `type` attribute at all (only their own internal
  subsections do). NPNF2 volumes follow the same two shapes.

Because of Pattern B, `type` presence can't be the front-matter filter
on its own - a real work-level div2 and a front-matter div2 both lack
it. The actual signal is the TITLE: front matter ("Introductory Essay",
"Translator's Preface", "Argument", "Preface", "Title Page", etc.) is
identifiable by title regardless of depth or type attribute.

`type` is still useful for ONE decision: whether a <div1>'s div2
children are Pattern A (typed - div1 is one work) or Pattern B (untyped
- div1 is a collection of separate works). A further wrinkle: some
untyped div2 children are just bare numbered labels of ONE work's
parts ("Book I", "Psalm L", "Homily I on Acts i. 1, 2.") rather than
distinct compositions - when ALL of a div1's non-front-matter div2
children match that pattern, they're merged back into one work instead
of split into many (see find_work_boundaries).

Author resolution differs between the two series:
  NPNF1 is one author per whole volume (NPNF1_AUTHOR_MAP).
  NPNF2 is NOT - several volumes mix multiple authors (Vol. 2: Socrates
  & Sozomen; Vol. 3: Theodoret, Jerome, Gennadius, Rufinus; Vol. 13:
  Gregory the Great, Ephraim Syrus, Aphrahat), and even a nominally
  single-author volume can embed a primary source by someone else
  (Vol. 1: Eusebius's "Life of Constantine" embeds Constantine's own
  "Oration to the Assembly of the Saints" - Constantine's composition,
  not Eusebius's). NPNF2 resolves the author per WORK, via
  NPNF2_WORK_AUTHOR_OVERRIDE (checked first) falling back to
  NPNF2_DEFAULT_AUTHOR (one default per volume, where a sensible single
  default exists). If a work matches neither, parsing FAILS LOUDLY
  rather than silently mis-attributing it - add the missing entry and
  re-run. Deliberately stricter than NPNF1's simple map, because
  silent misattribution is a worse failure mode than a script error.

This script does NOT write to Supabase. It writes a JSON file so you
can review/spot-check the parse before running insert_to_supabase.py.

Usage:
    python parse_thml.py anf01
    python parse_thml.py npnf101
    python parse_thml.py npnf201
Reads:  raw/{work_id}_raw.xml    (from thml_inspect.py fetch)
Writes: raw/{work_id}_parsed.json
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


# ===========================================================================
# ANF - unchanged legacy logic (div1 = author). Already validated/ingested.
# ===========================================================================

def _anf_extract_text_and_refs(p_elem):
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


def _anf_collect_paragraphs(elem, results, citation=None):
    """Recursively walk a <div2>, tracking the nearest div3 title as the
    citation context, collecting (text, refs, citation) per real <p>.
    Never descends into <note> - footnote paragraphs are excluded."""
    for child in elem:
        if child.tag == "note":
            continue
        if child.tag == "div3":
            child_citation = child.get("title") or child.get("shorttitle") or citation
            _anf_collect_paragraphs(child, results, citation=child_citation)
        elif child.tag == "p":
            text, refs = _anf_extract_text_and_refs(child)
            if text:
                results.append((text, refs, citation))
        else:
            _anf_collect_paragraphs(child, results, citation=citation)


def _anf_chunk_paragraphs(paragraphs, target_words=CHUNK_TARGET_WORDS):
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


def parse_anf_volume(path):
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

            # Skip 19th-century editorial commentary (Roberts/Donaldson/Coxe),
            # not primary patristic text - this project is retrieval of the
            # Fathers' own words, not editor notes.
            skip_patterns = ("introductory note", "elucidation")
            if work_title.strip().lower().startswith(skip_patterns):
                continue

            work_slug = slugify(f"{author_slug}-{work_title}")

            paragraphs = []
            _anf_collect_paragraphs(div2, paragraphs)
            passages = _anf_chunk_paragraphs(paragraphs)

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


# ===========================================================================
# NPNF1 / NPNF2 - shared structural logic, differing only in author
# resolution (see module docstring).
# ===========================================================================

# One author per NPNF1 volume.
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

# One sensible default author per NPNF2 volume, where the volume has
# one - leave a volume OUT of this dict entirely if it's genuinely
# mixed (e.g. Vol. 2, Vol. 3, Vol. 13) so every work in it must be
# resolved via NPNF2_WORK_AUTHOR_OVERRIDE instead.
NPNF2_DEFAULT_AUTHOR = {
    "npnf201": "Eusebius of Caesarea",
    "npnf204": "Athanasius of Alexandria",
    "npnf205": "Gregory of Nyssa",
    "npnf206": "Jerome",
    "npnf208": "Basil of Caesarea",
    "npnf210": "Ambrose of Milan",
    "npnf212": "Leo the Great",
}

# Exceptions to the default above, keyed by volume then by a lowercase
# substring of the work's title (checked with `in`). Checked BEFORE
# falling back to NPNF2_DEFAULT_AUTHOR.
NPNF2_WORK_AUTHOR_OVERRIDE = {
    "npnf201": {
        "oration of constantine": "Constantine the Great",
    },
    "npnf202": {
        "socrates scholasticus": "Socrates Scholasticus",
        "sozomen": "Sozomen",
    },
    "npnf203": {
        # Theodoret section
        "anathemas of cyril": "Cyril of Alexandria",
        "counter-statements of theodoret": "Theodoret of Cyrus",
        "ecclesiastical history of theodoret": "Theodoret of Cyrus",
        "eranistes": "Theodoret of Cyrus",
        "letters of the blessed theodoret": "Theodoret of Cyrus",
        # Jerome and Gennadius section
        "jerome. lives of illustrious men": "Jerome",
        "gennadius. lives of illustrious men": "Gennadius of Marseilles",
        # Rufinus section
        "translation of pamphilus": "Pamphilus of Caesarea",
        "epilogue to pamphilus": "Rufinus of Aquileia",
        "apology in defence of himself": "Rufinus of Aquileia",
        "letter of anastasius": "Anastasius I of Rome",
        "addressed to apronianus": "Rufinus of Aquileia",
        "apology for himself against the books of rufinus": "Jerome",
        "commentary on the apostles": "Rufinus of Aquileia",
        "peroration of rufinus": "Rufinus of Aquileia",
    },
    "npnf204": {
        "letter of eusebius": "Eusebius of Caesarea",
        "historia acephala": "Author of the Historia Acephala",
    },
    "npnf207": {
        "catechetical lectures": "Cyril of Jerusalem",
        "gregory nazianzen": "Gregory of Nazianzus",
    },
    "npnf209": {
        "exact exposition": "John of Damascus",
    },
    "npnf210": {
        # Symmachus's pagan Memorial, preserved within Ambrose's correspondence
        "memorial of symmachus": "Symmachus",
    },
    "npnf211": {
        "sulpitius severus": "Sulpitius Severus",
        "life of st. martin": "Sulpitius Severus",
        "commonitory": "Vincent of Lerins",
        "cassian": "John Cassian",
        "twelve books on the institutes": "John Cassian",
    },
    "npnf212": {
        "pastoral rule": "Gregory the Great",
        "gregory the great": "Gregory the Great",
    },
    "npnf213": {
        "selected epistles of gregory the great": "Gregory the Great",
        "ephraim syrus": "Ephrem the Syrian",
        "aphrahat": "Aphrahat",
    },
    "npnf214": {
        # Regional councils bundled in one div1 with no single section
        # default - each already splits into its own work via the
        # collection-detection logic, resolved individually here.
        "council of ancyra": "Council of Ancyra (314)",
        "council of neocæsarea": "Council of Neocaesarea (315)",
        "council of grangra": "Council of Gangra (340)",  # [sic] source title's own spelling
        "synod of antioch in encæniis": "Synod of Antioch (341)",
        "synod of laodicea": "Council of Laodicea (363)",
        "council of sardica": "Council of Sardica (343)",
        "ccxvii blessed fathers who assembled at carthage": "Council of Carthage (419)",
        "constantinople held under nectarius": "Council of Constantinople under Nectarius (394)",
        "carthage held under cyprian": "Council of Carthage under Cyprian (256)",

        # Individually-authored letters embedded within council sections -
        # checked before the section defaults above catch them as generic
        # conciliar material.
        "cyril": "Cyril of Alexandria",
        "letter of pope cœlestine": "Celestine I of Rome",
        "tome of st. leo": "Leo the Great",
        "anathematisms of the emperor justinian": "Justinian I",
        "decretal letter of pope vigilius": "Vigilius of Rome",
        "letter of pope agatho": "Agatho of Rome",
        "letter of agatho and of the roman synod": "Agatho of Rome",

        # Appendix of non-conciliar canons and letters - genuinely many
        # individual authors, several referred to only as "Of the Same" /
        # "The Same" after their first mention, resolved here by a
        # distinguishing phrase from each one's own title rather than by
        # tracking document order.
        "canons of the holy and altogether august apostles": "Apostolic Canons (Anonymous)",
        "blessed dionysius": "Dionysius of Alexandria",
        "blessed peter, archbishop of alexandria": "Peter of Alexandria",
        "thaumaturgus": "Gregory Thaumaturgus",
        "athanasius": "Athanasius of Alexandria",
        "basil": "Basil of Caesarea",
        "second canonical epistle of the same": "Basil of Caesarea",
        "third epistle of the same to the same": "Basil of Caesarea",
        "difference of meats": "Basil of Caesarea",
        "diodorus bishop of tarsus": "Basil of Caesarea",
        "separate from a woman": "Basil of Caesarea",
        "chorepiscopi": "Basil of Caesarea",
        "suffragans": "Basil of Caesarea",
        "st. letoïus": "Gregory of Nyssa",
        "gregory theologus": "Gregory of Nazianzus",
        "amphilochius the bishop to seleucus": "Amphilochius of Iconium",
        "timothy the most holy bishop of alexandria": "Timothy of Alexandria",
        "prosphonesus of theophilus": "Theophilus of Alexandria",
        "account of lycus": "Theophilus of Alexandria",
        "to agatho the bishop": "Theophilus of Alexandria",
        "to menas the bishop": "Theophilus of Alexandria",
        "cathari": "Theophilus of Alexandria",
        "libya and pentapolis": "Cyril of Alexandria",
        "patriarch of constantinople and of the holy synod": "Gennadius of Constantinople",
    },
}


# Some NPNF2 volumes (npnf214, the Ecumenical Councils compilation) bundle
# MULTIPLE distinct councils under one volume, each needing its own default
# author - a single whole-volume default isn't enough, and the same work
# title ("Extracts from the Acts. Session I.") recurs identically under
# several different councils, so work-title alone can't disambiguate which
# one it belongs to either. This maps work_id -> a list of
# (div1_title_substring, author) pairs, checked against the ENCLOSING
# section's own title, after NPNF2_WORK_AUTHOR_OVERRIDE and before falling
# back to NPNF2_DEFAULT_AUTHOR.
NPNF2_SECTION_DEFAULT_AUTHOR = {
    "npnf214": [
        ("first ecumenical council", "First Council of Nicaea (325)"),
        ("second ecumenical council", "First Council of Constantinople (381)"),
        ("third ecumenical council", "Council of Ephesus (431)"),
        ("fourth ecumenical council", "Council of Chalcedon (451)"),
        ("fifth ecumenical council", "Second Council of Constantinople (553)"),
        ("sixth ecumenical council", "Third Council of Constantinople (680)"),
        ("council in trullo", "Council in Trullo (692)"),
        ("seventh ecumenical council", "Second Council of Nicaea (787)"),
    ],
}


def _npnf1_resolve_author(work_id: str, div1_title: str, work_title: str) -> str:
    author_name = NPNF1_AUTHOR_MAP.get(work_id)
    if author_name is None:
        raise ValueError(f"No author mapped for {work_id!r} - add it to NPNF1_AUTHOR_MAP")
    return author_name


def _npnf2_resolve_author(work_id: str, div1_title: str, work_title: str) -> str:
    t = work_title.strip().lower().rstrip(".")
    for key, author in NPNF2_WORK_AUTHOR_OVERRIDE.get(work_id, {}).items():
        if key in t:
            return author

    section_defaults = NPNF2_SECTION_DEFAULT_AUTHOR.get(work_id)
    if section_defaults:
        d1 = (div1_title or "").strip().lower().rstrip(".")
        for section_key, author in section_defaults:
            if section_key in d1:
                return author

    default = NPNF2_DEFAULT_AUTHOR.get(work_id)
    if default is not None:
        return default

    raise ValueError(
        f"Can't resolve an author for work {work_title!r} (section {div1_title!r}) "
        f"in {work_id!r} - add an entry to NPNF2_WORK_AUTHOR_OVERRIDE, "
        f"NPNF2_SECTION_DEFAULT_AUTHOR, or NPNF2_DEFAULT_AUTHOR."
    )


# Front matter is identified by title, matched as a case-insensitive
# substring - deliberately broad, since front-matter section titles
# vary a lot in wording across editors/volumes ("Preface", "Editor's
# Preface", "Preface to the American Edition" all match on "preface").
# Applies at ANY depth (div1, div2, div3). Shared by NPNF1 and NPNF2.
FRONT_MATTER_TITLE_CONTAINS = (
    "title page",
    "series title",
    "preface",
    "prefatory",  # "Prefatory Note", "Prefatory Remarks" - doesn't share a stem with "preface"
    "contents",
    "dedication",
    "credits",
    "advertisement",  # publisher's front-matter note, e.g. npnf108's "Advertisement."
    "introduct",  # stem covers "Introduction." AND "Introductory Essay/Notice/Note"
    "bibliography",
    "abstract",
    "translator's preface",
    "translator\u2019s preface",
    "argument",
    "comparative table",
    "index",  # catches "Index of Subjects", "Subject Index", "Subject Indexes", "Indexes" - all variants
    "the opinion of st. augustin",  # editorial front matter specific to npnf101's Confessions
    "testimonies of the ancients",  # editorial apparatus preceding npnf201's Church History
    "supplementary notes",  # modern editor's reference tables/appendix, e.g. npnf201's chronological tables
    "memoir of",  # editorial biographical sketch, e.g. npnf202's "Memoir of Sozomen."
    "manuscripts",  # bibliographic apparatus, e.g. npnf203's "Manuscripts and Editions of Separate Works."
    "chronological table",  # e.g. npnf203's "Chronological Tables to accompany the History and Life of Theodoret."
    "excursus",  # modern editor's scholarly digression, e.g. npnf204's "Excursus A."
    "dates of treatises",  # editor's chronology table, e.g. npnf205's "Dates of Treatises, &c., Here Translated."
    "life and writings of",  # translator's biographical intro, e.g. npnf211's "Life and Writings of Sulpitius Severus."
    "note on section",  # translator's appendix notes, e.g. npnf211's "Appendix I. Note on Section 41, Page 143."
    "general literature",  # editor's bibliography, e.g. npnf213's "General Literature of Gregory's Life and Times."
    "(notes)",  # editorial manuscript/textual notes, e.g. npnf213's "Regula Pastoralis (Notes)."
    "historical note",  # e.g. npnf214's "Historical Note on the Lost 'Tome' of the Second Council."
    "appended note",  # e.g. npnf214's div1 "Appended Note on the Eastern Editions of Synodical Literature."
    "note on the",  # e.g. npnf214's "Note on the Emperor's Edict to the Synod." (superset of "note on section")
    "additional note",  # editor's appended scholarly note, e.g. npnf204's "Additional Note on Apol. C. Arianos, \u00a750."
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


def is_front_matter_title(title: str) -> bool:
    t = (title or "").strip().lower().rstrip(".")
    if not t:
        return True  # untitled containers are never real content
    return any(k in t for k in FRONT_MATTER_TITLE_CONTAINS)


# Titles that are only skippable as a WHOLE WORK, never as a nested
# citation label. Kept separate from FRONT_MATTER_TITLE_CONTAINS because a
# nested "Prologue." is real content elsewhere (Theodoret's Dialogues, the
# Life of Antony) - dropping it there would change already-verified
# volumes. As a standalone work, though, a bare "Note." or "Prologue."
# (npnf209, John of Damascus) is editorial/prefatory framing.
WORK_LEVEL_SKIP_EXACT = {
    "note", "prologue",
    # npnf210: a short editorial summary of Symmachus's memorial, distinct
    # from (and duplicating) "The Memorial of Symmachus, Prefect of the
    # City." which has the actual primary text - kept, this one dropped.
    "memorial of symmachus, the prefect of the city",
    # npnf214: modern editorial analysis of a medieval authorship dispute
    # (citing 16th/17th-century scholars), not ancient content at all -
    # despite sitting under the Nicaea II section, it isn't a council
    # document or anyone's primary composition.
    "examination of the caroline books",
}


def is_skippable_work_title(title: str) -> bool:
    if is_front_matter_title(title):
        return True
    return (title or "").strip().lower().rstrip(".") in WORK_LEVEL_SKIP_EXACT


def _npnf_extract_text_and_refs(p_elem):
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


def _normalize_for_compare(s: str) -> str:
    s = s.replace("\u2014", "-").replace("\u2013", "-")  # em/en dash -> hyphen
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s.rstrip(".")


def is_heading_restatement(p_text: str, shorttitle: str, title: str) -> bool:
    """True if a paragraph is just '<Shorttitle>.—<Title>' restating the
    div's own heading (e.g. 'Chapter I.—He Proclaims the Greatness of
    God...') rather than actual body prose.

    Tries the shorttitle attribute first, but some editions leave that
    attribute present-but-empty and only spell the "Chapter II .—"
    label out in the rendered paragraph text itself - the regex
    fallback below catches that case by matching a generic
    "<Label> <number> [.-]" prefix directly against the text, with no
    dependency on the shorttitle attribute at all.
    """
    if not title:
        return False
    p_norm = _normalize_for_compare(p_text)
    title_norm = _normalize_for_compare(title)

    if shorttitle:
        short_norm = _normalize_for_compare(shorttitle)
        if p_norm.startswith(short_norm):
            remainder = p_norm[len(short_norm):].lstrip(".- ")
            if remainder == title_norm or remainder in title_norm or title_norm in remainder:
                return True

    m = re.match(r"^(book|chapter|section|letter|homily)\s+[ivxlcdm0-9]+\s*[.\-]*\s*", p_norm)
    if m:
        remainder = p_norm[m.end():].lstrip(".- ")
        if remainder == title_norm or remainder in title_norm or title_norm in remainder:
            return True

    # Some editions restate a chapter's descriptive title as its own first
    # paragraph with NO numbering prefix at all (e.g. Sulpitius Severus,
    # John Cassian) - the paragraph text just IS the title, verbatim. If
    # a short paragraph exactly equals the title with nothing else, it's
    # the heading, not body prose.
    if p_norm == title_norm:
        return True

    return False


def _npnf_collect_paragraphs(elem, results, citation=None, own_title=None, own_shorttitle=None):
    """Recursively walk a work's boundary container (a <div1> in
    Pattern A, or a work-level <div2> in Pattern B), building a
    citation string as we descend through non-front-matter div2/div3
    elements - filtered by TITLE, not by `type` attribute (see module
    docstring for why).

    A container's OWN direct <p> children are only kept if it has no
    real (non-front-matter) div2/div3 children of its own - containers
    that do have such children open with a few paragraphs of
    running-header/epigraph text before their first real subsection,
    which isn't body prose and gets skipped in favor of the deeper
    content.

    At a leaf level, the very first <p> is often just the section's
    own heading restated, duplicating what's already in the citation -
    skipped via is_heading_restatement so it doesn't become a
    near-empty passage.
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
            _npnf_collect_paragraphs(
                child, results, citation=child_citation,
                own_title=child.get("title"), own_shorttitle=child.get("shorttitle"),
            )
        elif child.tag == "p":
            if has_real_children:
                continue  # header/epigraph before the first real subsection - skip
            text, refs = _npnf_extract_text_and_refs(child)
            if text:
                if not seen_first_p and is_heading_restatement(text, own_shorttitle, own_title):
                    seen_first_p = True
                    continue
                seen_first_p = True
                results.append((text, refs, citation))
        else:
            _npnf_collect_paragraphs(
                child, results, citation=citation,
                own_title=own_title, own_shorttitle=own_shorttitle,
            )


def _npnf_chunk_paragraphs(paragraphs, target_words=CHUNK_TARGET_WORDS):
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
    AND are not just bare numbered labels of one work's parts, div1 is
    a Pattern B collection wrapper of genuinely separate compositions -
    each such div2 becomes its own work.

    Otherwise - div2s are typed (Pattern A), there are no div2
    children at all, or the div2 children are ALL bare numbered labels
    - div1 itself is a single work, and _npnf_collect_paragraphs will
    build the numbered labels into the citation string as it descends.
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


def parse_npnf_volume(path, work_id, resolve_author):
    """Shared NPNF1/NPNF2 parse loop. `resolve_author(work_id, work_title)`
    is the one thing that differs between the two series - see
    _npnf1_resolve_author (fixed per volume) vs _npnf2_resolve_author
    (per work, with override/default resolution)."""
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
            if is_skippable_work_title(work_title):
                continue

            paragraphs = []
            _npnf_collect_paragraphs(container, paragraphs)
            passages = _npnf_chunk_paragraphs(paragraphs)

            if not passages:
                continue  # nothing but front matter found here - not a real work

            author_name = resolve_author(work_id, div1_title, work_title)
            author_slug = slugify(author_name)

            work_slug = slugify(f"{author_slug}-{work_title}")
            if work_slug in seen_slugs:
                # Defensive: shouldn't normally happen, but avoid silently
                # dropping a duplicate-titled work by disambiguating it.
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


# ===========================================================================
# Dispatch
# ===========================================================================

def parse_volume(work_id: str):
    path = f"raw/{work_id}_raw.xml"

    if work_id.startswith("anf"):
        return parse_anf_volume(path)
    if re.match(r"npnf1\d+$", work_id):
        return parse_npnf_volume(path, work_id, _npnf1_resolve_author)
    if re.match(r"npnf2\d+$", work_id):
        return parse_npnf_volume(path, work_id, _npnf2_resolve_author)

    raise ValueError(
        f"Don't know how to parse work_id {work_id!r} - expected an "
        f"anf*, npnf1*, or npnf2* prefix"
    )



def _run_one(work_id: str, show_sample: bool):
    data = parse_volume(work_id)

    out_path = f"raw/{work_id}_parsed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_works = sum(len(a["works"]) for a in data)
    total_passages = sum(w["passage_count"] for a in data for w in a["works"])
    print(f"\n=== {work_id}: {len(data)} author(s), {total_works} works, "
          f"{total_passages} passages -> {out_path}")
    for a in data:
        print(f"  {a['name']} ({len(a['works'])} works)")
        for w in a["works"]:
            print(f"    - {w['title']}  [{w['passage_count']} passages]")

    if show_sample and data and data[0]["works"] and data[0]["works"][0]["passages"]:
        sample = data[0]["works"][0]["passages"][0]
        print(f"\nSample passage (citation={sample['citation']!r}, {sample['word_count']} words):")
        print(f"  {sample['text'][:300]}...")


if __name__ == "__main__":
    work_ids = sys.argv[1:] or ["anf01"]
    failures = []
    for work_id in work_ids:
        try:
            _run_one(work_id, show_sample=(len(work_ids) == 1))
        except Exception as e:
            print(f"\n=== {work_id}: FAILED - {e}")
            failures.append(work_id)

    if len(work_ids) > 1:
        print(f"\nParsed {len(work_ids) - len(failures)}/{len(work_ids)} volumes.")
        if failures:
            print(f"FAILED: {' '.join(failures)}")