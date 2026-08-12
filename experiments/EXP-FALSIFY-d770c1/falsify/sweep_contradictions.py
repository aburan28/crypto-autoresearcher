"""F-9: mechanical sweep for quantities the corpus quotes at more than one value.

    python3 experiments/EXP-FALSIFY-d770c1/falsify/sweep_contradictions.py

Groups numeric claims by the symbol immediately preceding them and reports every
symbol carrying more than one distinct value across more than one finding.

RECALL IS A FLOOR, NOT AN ESTIMATE. The grouping key is a surface string, so a
quantity named `C(p)` in one record and `the character sum constant` in another
is invisible to this pass. Two hits from one crude sweep bounds from below what
a careful pass would find; it does not bound it from above. A clean result here
is not evidence that the corpus is internally consistent.

Executed 2026-08-08: returned `C(p)` (-> F-3, EV-FALSIFY-40291d) and `speedup`
(-> F-4, EV-FALSIFY-67150b). Both pointers led to real defects.
"""

import collections
import glob
import os
import re
import sys

VALUE = r'([Oo]\(1\)|p\^\{?[-0-9.]+\}?|[0-9]+\.[0-9]+|[0-9]+(?:\.[0-9]+)?x)'
CLAIM = re.compile(r'([A-Za-z_][A-Za-z0-9_{}\\^\(\)\*\-\+ ]{0,24}?)\s*'
                   r'(?:~|≈|=|is|of)\s*' + VALUE)
STOP = {'the', 'a', 'and', 'it', 'this', 'that', 'is', 'of', 'in', 'to', 'at',
        'for', 'with', 'as', 'by', 'or', 'be', 'are', 'was'}


def sweep(root='knowledge/findings'):
    hits = collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(root, '*.md'))):
        text = open(path).read()
        rec = os.path.basename(path)[:-3]
        for m in CLAIM.finditer(text):
            sym = m.group(1).strip().lower()
            if len(sym) < 2 or sym in STOP:
                continue
            hits[sym].append((rec, m.group(2)))
    return {k: v for k, v in hits.items()
            if len({x[1] for x in v}) > 1 and len({x[0] for x in v}) > 1}


def main():
    conflicts = sweep()
    print('F-9 corpus contradiction sweep')
    print(f'  symbols with >1 distinct value across >1 finding: {len(conflicts)}\n')
    for sym, rows in sorted(conflicts.items(), key=lambda kv: -len(kv[1])):
        vals = collections.Counter(v for _, v in rows)
        srcs = sorted({r for r, _ in rows})
        print(f"  {sym!r}")
        print(f"      values : {dict(vals)}")
        print(f"      records: {', '.join(srcs)}")
    print('\n  Recall is a floor. The grouping key is a surface string, so the '
          'same\n  quantity named two ways is invisible here. A clean result is '
          'not evidence\n  of consistency.')
    return 0 if not conflicts else 1


if __name__ == '__main__':
    sys.exit(main())
