#!/usr/bin/env python3
"""jsondiff - Compare two JSON files with structured diff."""
import json, argparse, sys

def diff(a, b, path=''):
    changes = []
    if type(a) != type(b):
        changes.append(('type', path, f"{type(a).__name__} → {type(b).__name__}", a, b))
    elif isinstance(a, dict):
        for k in set(a) | set(b):
            p = f"{path}.{k}" if path else k
            if k not in b: changes.append(('removed', p, a[k], None))
            elif k not in a: changes.append(('added', p, None, b[k]))
            else: changes.extend(diff(a[k], b[k], p))
    elif isinstance(a, list):
        for i in range(max(len(a), len(b))):
            p = f"{path}[{i}]"
            if i >= len(b): changes.append(('removed', p, a[i], None))
            elif i >= len(a): changes.append(('added', p, None, b[i]))
            else: changes.extend(diff(a[i], b[i], p))
    elif a != b:
        changes.append(('changed', path, a, b))
    return changes

def main():
    p = argparse.ArgumentParser(description='JSON structural diff')
    p.add_argument('file1')
    p.add_argument('file2')
    p.add_argument('-j', '--json', action='store_true', help='JSON output')
    p.add_argument('--stats', action='store_true', help='Stats only')
    args = p.parse_args()

    with open(args.file1) as f: a = json.load(f)
    with open(args.file2) as f: b = json.load(f)

    changes = diff(a, b)

    if args.json:
        print(json.dumps([{'type': c[0], 'path': c[1], 'old': c[2], 'new': c[3]} for c in changes], indent=2, default=str))
    elif args.stats:
        from collections import Counter
        counts = Counter(c[0] for c in changes)
        for t, n in counts.most_common():
            print(f"  {t:<10} {n}")
        print(f"  total     {len(changes)}")
    else:
        if not changes:
            print("Files are identical."); return
        for change_type, path, old, new in changes:
            if change_type == 'added':
                print(f"  \033[32m+ {path}: {json.dumps(new, default=str)[:80]}\033[0m")
            elif change_type == 'removed':
                print(f"  \033[31m- {path}: {json.dumps(old, default=str)[:80]}\033[0m")
            elif change_type == 'changed':
                print(f"  \033[33m~ {path}: {json.dumps(old, default=str)[:40]} → {json.dumps(new, default=str)[:40]}\033[0m")
            elif change_type == 'type':
                print(f"  \033[35m! {path}: {old}\033[0m")
        print(f"\n  {len(changes)} differences")

if __name__ == '__main__':
    main()
