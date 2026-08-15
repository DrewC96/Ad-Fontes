"""
Inspect a ThML file from CCEL for structure and content, printing out the root tag, attributes, top-level children, and counts of certain elements like <div1>, <scripRef>, and <foreign>.
Usage:
    python inspect_thml.py [work_id]
"""

import sys
import time
import requests
import xml.etree.ElementTree as etree

def fetch(work_id: str) -> bytes:
    url = f"https://ccel.org/ccel/s/schaff/{work_id}.xml"
    print(f"Fetching {url} ...")
    resp = requests.get(url, headers={"User-Agent": "ad-fontes-research/0.1 (personal project)"})
    resp.raise_for_status()
    time.sleep(1)
    return resp.content

def inspect(xml_bytes: bytes, max_children_shown: int = 40):
    tree = etree.fromstring(xml_bytes)

    print(f"\nRoot tag: <{tree.tag}>")
    print(f"Root attributes: {dict(tree.attrib)}\n")

    print("Top-level children (first 40):")
    for i, child in enumerate(tree):
        if i >= max_children_shown:
            print("  ...")
            break
        title = child.get("title", "")
        print(f"  <{child.tag}> title={title!r} attrs={dict(child.attrib)}")

    # Try to find likely "work" boundaries — div1 is the ThML convention,
    # but we confirm rather than assume.
    div1s = tree.findall(".//div1")
    print(f"\nFound {len(div1s)} <div1> elements (likely = individual works/sections)")
    for d in div1s[:15]:
        print(f"  - {d.get('title', '(no title attr)')}")

    # Check for scripture references and foreign-language (Greek) spans,
    # relevant to your scripture cross-reference layer later.
    scrip_refs = tree.findall(".//scripRef")
    foreign = tree.findall(".//foreign")
    print(f"\n<scripRef> count: {len(scrip_refs)}")
    print(f"<foreign> count: {len(foreign)}")

if __name__ == "__main__":
    work_id = sys.argv[1] if len(sys.argv) > 1 else "anf01"
    data = fetch(work_id)
    # Save raw copy for manual inspection in a text editor too
    with open(f"{work_id}_raw.xml", "wb") as f:
        f.write(data)
    print(f"Saved raw copy to {work_id}_raw.xml\n")
    inspect(data)