import json, sys

def spotcheck_file(path, title_filter):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    for author in data:
        for work in author["works"]:
            if title_filter and title_filter not in work["title"].lower():
                continue
            n = len(work["passages"])
            if n == 0:
                continue
            print(f"Work: {work['title']} ({author['name']}, {n} passages)\n")
            indices = sorted(set([0, n // 4, n // 2, (3 * n) // 4, n - 1]))
            for idx in indices:
                p = work["passages"][idx]
                print(f"[idx {idx}] citation={p['citation']!r} words={p['word_count']}")
                print(f"  {p['text'][:200]}")
                print()

if __name__ == "__main__":
    args = sys.argv[1:]
    # Optional trailing arg starting with "filter=" restricts by title substring;
    # everything else is treated as a JSON path. With no paths, defaults to one.
    title_filter = None
    paths = []
    for a in args:
        if a.startswith("filter="):
            title_filter = a[len("filter="):].lower()
        else:
            paths.append(a)
    if not paths:
        paths = ["raw/npnf101_parsed.json"]

    for path in paths:
        print(f"\n########## {path} ##########\n")
        spotcheck_file(path, title_filter)