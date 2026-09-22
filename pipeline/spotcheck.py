import json, sys

with open(sys.argv[1], encoding="utf-8") as f:
    data = json.load(f)

# Optional second arg: substring to filter which works to sample (case-insensitive).
# With no second arg, samples every work in the file.
title_filter = sys.argv[2].lower() if len(sys.argv) > 2 else None

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