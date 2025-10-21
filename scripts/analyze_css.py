#!/usr/bin/env python3
import re
import sys
from collections import Counter
from typing import List, Dict

if len(sys.argv) < 2:
    print("Usage: analyze_css.py <path-to-css>", file=sys.stderr)
    sys.exit(2)

path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

n = len(css)

def skip_comment(s: str, i: int) -> int:
    j = s.find('*/', i+2)
    return (j+2) if j != -1 else len(s)

selectors: List[str] = []

i = 0
while i < n:
    if css.startswith('/*', i):
        i = skip_comment(css, i)
        continue
    c = css[i]
    if c.isspace():
        i += 1
        continue
    if c == '@':
        # at-rule: skip whole block if has braces; otherwise read to semicolon
        j = css.find('{', i)
        ksemi = css.find(';', i)
        if j == -1 or (ksemi != -1 and (ksemi < j)):
            # at-rule without block
            i = (ksemi+1) if ksemi != -1 else n
            continue
        depth = 0
        k = j
        while k < n:
            if css.startswith('/*', k):
                k = skip_comment(css, k)
                continue
            if css[k] == '{':
                depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0:
                    k += 1
                    break
            k += 1
        i = k
        continue
    # normal rule
    j = css.find('{', i)
    if j == -1:
        break
    selector = re.sub(r"\s+", " ", css[i:j].strip())
    # read to matching closing
    k = j + 1
    depth = 1
    while k < n:
        if css.startswith('/*', k):
            k = skip_comment(css, k)
            continue
        if css[k] == '{':
            depth += 1
        elif css[k] == '}':
            depth -= 1
            if depth == 0:
                k += 1
                break
        k += 1
    selectors.append(selector)
    i = k

counts = Counter(selectors)
num_rules = len(selectors)
num_unique = sum(1 for s, c in counts.items() if c >= 1)
num_dupes = sum(c-1 for c in counts.values() if c > 1)

dupes = [(s, c) for s, c in counts.items() if c > 1]
dupes.sort(key=lambda x: (-x[1], x[0]))

print(f"File: {path}")
print(f"Total top-level rules: {num_rules}")
print(f"Unique selectors: {num_unique}")
print(f"Duplicate instances removed if deduped (sum over counts-1): {num_dupes}")
print("Top duplicates:")
for s, c in dupes[:20]:
    print(f"  {c}x  {s}")
