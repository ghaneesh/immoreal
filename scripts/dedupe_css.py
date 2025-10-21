#!/usr/bin/env python3
import re
import sys
from typing import List, Dict, Tuple

CSSPath = sys.argv[1] if len(sys.argv) > 1 else None
if not CSSPath:
    print("Usage: dedupe_css.py <path-to-css>", file=sys.stderr)
    sys.exit(2)

with open(CSSPath, 'r', encoding='utf-8') as f:
    css = f.read()

# Simple tokenizer preserving top-level @-blocks and normal rule blocks

tokens = []  # list of dicts with type: 'rule'|'at'|'comment'|'other'
i = 0
n = len(css)

# Utility to skip comments

def skip_comment(s: str, pos: int) -> int:
    end = s.find('*/', pos + 2)
    return (end + 2) if end != -1 else n

while i < n:
    # Skip whitespace
    if css[i].isspace():
        i += 1
        continue
    # Comments
    if css.startswith('/*', i):
        j = skip_comment(css, i)
        tokens.append({'type': 'comment', 'text': css[i:j]})
        i = j
        continue
    # At-rule (we keep as-is; including nested blocks)
    if css[i] == '@':
        j = css.find('{', i)
        if j == -1:
            # Malformed; append rest
            tokens.append({'type': 'other', 'text': css[i:]})
            break
        header = css[i:j].strip()
        # Read balanced braces
        depth = 0
        k = j
        while k < n:
            if css.startswith('/*', k):
                k = skip_comment(css, k)
                continue
            c = css[k]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    k += 1
                    break
            k += 1
        body = css[j+1:k-1]
        tokens.append({'type': 'at', 'header': header, 'body': body})
        i = k
        continue
    # Normal rule
    j = css.find('{', i)
    if j == -1:
        tokens.append({'type': 'other', 'text': css[i:]})
        break
    selector = css[i:j].strip()
    # Read until matching '}' at the same level
    k = j + 1
    depth = 1
    while k < n:
        if css.startswith('/*', k):
            k = skip_comment(css, k)
            continue
        c = css[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                break
        k += 1
    body = css[j+1:k].strip()
    tokens.append({'type': 'rule', 'selector': selector, 'body': body})
    i = k + 1

# Helper to parse declarations inside a rule body

def strip_comments(s: str) -> str:
    return re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", s)

def parse_decls(body: str) -> List[Tuple[str, str]]:
    s = strip_comments(body)
    decls = []
    buf = []
    for ch in s:
        if ch == ';':
            part = ''.join(buf).strip()
            if part:
                decls.append(part)
            buf = []
        else:
            buf.append(ch)
    # last one without semicolon
    trailing = ''.join(buf).strip()
    if trailing:
        decls.append(trailing)
    result = []
    for d in decls:
        if ':' in d:
            prop, val = d.split(':', 1)
            result.append((prop.strip(), val.strip()))
    return result

# Aggregate declarations per selector at top-level only (not inside @)
selector_info: Dict[str, Dict] = {}

for idx, t in enumerate(tokens):
    if t['type'] != 'rule':
        continue
    # Normalize selector spacing for matching
    key = re.sub(r"\s+", " ", t['selector']).strip()
    info = selector_info.get(key)
    if info is None:
        info = {
            'first_index': idx,
            'last_index': idx,
            'decls': {},       # prop -> value (last one wins)
            'order': [],       # property order by first sighting
            'selector_text': t['selector'],  # last occurrence text
        }
        selector_info[key] = info
    else:
        info['last_index'] = idx
        info['selector_text'] = t['selector']
    for prop, val in parse_decls(t['body']):
        if prop not in info['decls']:
            info['order'].append(prop)
        info['decls'][prop] = val

# Rebuild CSS: keep comments and @-blocks as-is.
# For rules: only emit at their last_index, with merged declarations.

emitted = set()
output_lines: List[str] = []

for idx, t in enumerate(tokens):
    if t['type'] == 'comment':
        output_lines.append(t['text'])
        continue
    if t['type'] == 'other':
        output_lines.append(t['text'])
        continue
    if t['type'] == 'at':
        output_lines.append(f"{t['header']}{{{t['body']}}}")
        continue
    # rule
    key = re.sub(r"\s+", " ", t['selector']).strip()
    info = selector_info.get(key)
    if info is None:
        # shouldn't happen; emit original
        output_lines.append(f"{t['selector']}{{{t['body']}}}")
        continue
    if idx != info['last_index']:
        # skip earlier duplicates
        continue
    if key in emitted:
        continue
    emitted.add(key)
    decl_str = ''.join([f"\n  {p}: {info['decls'][p]};" for p in info['order']])
    output_lines.append(f"{info['selector_text']}{{{decl_str}\n}}")

new_css = '\n'.join(output_lines)

with open(CSSPath, 'w', encoding='utf-8') as f:
    f.write(new_css)

print(f"Deduplicated: wrote {len(new_css)} bytes")
