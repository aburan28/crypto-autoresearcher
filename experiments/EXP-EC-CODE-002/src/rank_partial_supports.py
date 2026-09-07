#!/usr/bin/env python3
"""EXP-EC-CODE-002: search target-aware partial-support features.

Standard-library toy experiment. Labels are computed by exhaustive EC addition only
for evaluation. Feature extraction never completes a candidate support, never uses
scalar logs, and never evaluates the full 3-support determinant.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import combinations
import json
from math import isqrt
from pathlib import Path
from random import Random

Point = tuple[int, int] | None


def prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def rref(a: list[list[int]], p: int):
    if not a:
        return [], []
    m = [[x % p for x in row] for row in a]
    piv, r = [], 0
    for c in range(len(m[0])):
        k = next((i for i in range(r, len(m)) if m[i][c]), None)
        if k is None:
            continue
        m[r], m[k] = m[k], m[r]
        inv = pow(m[r][c], -1, p)
        m[r] = [x * inv % p for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                t = m[i][c]
                m[i] = [(x - t*y) % p for x, y in zip(m[i], m[r])]
        piv.append(c)
        r += 1
        if r == len(m):
            break
    return m, piv


def rank(a: list[list[int]], p: int) -> int:
    return len(rref(a, p)[1]) if a else 0


def nullspace(a: list[list[int]], p: int, ncols: int | None = None) -> list[list[int]]:
    if not a:
        n = 0 if ncols is None else ncols
        return [[int(i == j) for i in range(n)] for j in range(n)]
    red, piv = rref(a, p)
    n = len(a[0])
    out = []
    for c in range(n):
        if c in piv:
            continue
        v = [0] * n
        v[c] = 1
        for rr, pc in enumerate(piv):
            v[pc] = -red[rr][c] % p
        out.append(v)
    return out


def add(u: Point, v: Point, p: int, a: int) -> Point:
    if u is None:
        return v
    if v is None:
        return u
    x, y = u; z, w = v
    if x == z and (y + w) % p == 0:
        return None
    if u == v:
        if y % p == 0:
            return None
        s = (3*x*x + a) * pow(2*y, -1, p) % p
    else:
        s = (w-y) * pow((z-x) % p, -1, p) % p
    nx = (s*s-x-z) % p
    return nx, (s*(x-nx)-y) % p


def neg(u: Point, p: int) -> Point:
    return None if u is None else (u[0], -u[1] % p)


def curve_points(p: int, a: int, b: int) -> list[tuple[int, int]]:
    roots = defaultdict(list)
    for y in range(p):
        roots[y*y % p].append(y)
    return [(x, y) for x in range(p)
            for y in roots[(x*x*x + a*x + b) % p]]


def find_curve(p: int) -> tuple[int, int, list[tuple[int, int]], int]:
    for a in (1, 2, 3, 5, 7):
        for b in range(1, min(p, 80)):
            if (4*a*a*a + 27*b*b) % p == 0:
                continue
            pts = curve_points(p, a, b)
            order = len(pts) + 1
            if prime(order) and len({x for x, _ in pts}) >= 48:
                return a, b, pts, order
    raise RuntimeError(f'no prime-order toy curve found over F_{p}')


def eval_rows(points: list[tuple[int, int]], p: int) -> list[list[int]]:
    return [
        [1 for _ in points],
        [x for x, _ in points],
        [y for _, y in points],
        [x*x % p for x, _ in points],
    ]


def linear_combos(coeffs: list[list[int]], rows: list[list[int]], p: int) -> list[list[int]]:
    return [[sum(c[i]*rows[i][j] for i in range(len(rows))) % p
             for j in range(len(rows[0]))] for c in coeffs]


def schur_product(u: list[list[int]], v: list[list[int]], p: int) -> list[list[int]]:
    return [[x*y % p for x, y in zip(a, b)] for a in u for b in v]


def append_delta(rows: list[list[int]], p: int) -> int:
    if not rows or not rows[0]:
        return 0
    return rank(rows, p) - rank([r[:-1] for r in rows], p)


def partial_features(base, target, support, p):
    domain = base + [neg(target, p)]
    v = eval_rows(domain, p)
    constraints = [[v[r][i] for r in range(4)] for i in support]
    coeffs = nullspace(constraints, p, 4)
    shortened = linear_combos(coeffs, v, p)
    sv = schur_product(shortened, v, p)
    ss = schur_product(shortened, shortened, p)
    fullsq = schur_product(v, v, p)
    # All features are computed from the selected partial support plus the public
    # target evaluation coordinate. No completion point is introduced.
    inter_base = rank([r[:-1] for r in sv], p) + rank([r[:-1] for r in fullsq], p) - rank(
        [r[:-1] for r in sv + fullsq], p)
    inter_target = rank(sv, p) + rank(fullsq, p) - rank(sv + fullsq, p)
    return {
        'short_dim': rank(shortened, p),
        'short_square_dim': rank(ss, p),
        'short_times_full_dim': rank(sv, p),
        'target_rank_delta_short_square': append_delta(ss, p),
        'target_rank_delta_short_times_full': append_delta(sv, p),
        'target_intersection_delta': inter_target - inter_base,
    }


def auc(rows, feature):
    pos = [r[feature] for r in rows if r['label']]
    negs = [r[feature] for r in rows if not r['label']]
    if not pos or not negs:
        return None
    wins = 0.0
    for x in pos:
        for y in negs:
            wins += 1 if x > y else 0.5 if x == y else 0
    raw = wins / (len(pos)*len(negs))
    return max(raw, 1-raw)  # orientation-free feature screening


def run_curve(p: int, base_size: int, targets: int):
    a, b, points, order = find_curve(p)
    # Frozen coordinate-only factor base: increasing x, lower y sign.
    by_x = {}
    for x, y in points:
        by_x.setdefault(x, []).append(y)
    base = [(x, min(by_x[x])) for x in sorted(by_x)[:base_size]]
    candidates = [q for q in points if q not in base and neg(q, p) not in base]
    selected_targets = candidates[::max(1, len(candidates)//targets)][:targets]
    feature_rows = []
    target_summaries = []
    for target in selected_targets:
        triples = []
        extendable = {1: set(), 2: set()}
        for inds in combinations(range(len(base)), 3):
            s = add(add(base[inds[0]], base[inds[1]], p, a), base[inds[2]], p, a)
            if s == target:
                triples.append(inds)
                for k in (1, 2):
                    extendable[k].update(combinations(inds, k))
        if not triples:
            continue
        target_rows = []
        for k in (1, 2):
            for support in combinations(range(len(base)), k):
                row = {'support_size': k, 'label': support in extendable[k]}
                row.update(partial_features(base, target, support, p))
                target_rows.append(row)
        feature_rows.extend(target_rows)
        target_summaries.append({'target': target, 'decompositions': len(triples)})
    features = [k for k in feature_rows[0] if k not in {'support_size', 'label'}] if feature_rows else []
    metrics = {str(k): {f: auc([r for r in feature_rows if r['support_size'] == k], f)
                        for f in features} for k in (1, 2)}
    return {
        'curve': {'p': p, 'a': a, 'b': b, 'order': order},
        'base_size': len(base),
        'targets_with_positive_decompositions': len(target_summaries),
        'target_summaries': target_summaries,
        'metrics_orientation_free_auc': metrics,
        'rows': len(feature_rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=Path)
    ap.add_argument('--quick', action='store_true')
    args = ap.parse_args()
    primes = [1009, 1013, 1019, 1021, 1031, 1033, 1039, 1049]
    sizes = [24] if args.quick else [24, 32, 40]
    ts = 4 if args.quick else 16
    runs, failures = [], []
    for p in primes[:3] if args.quick else primes:
        for n in sizes:
            try:
                runs.append(run_curve(p, n, ts))
            except Exception as e:
                failures.append({'p': p, 'base_size': n, 'error': repr(e)})
    report = {
        'experiment': 'EXP-EC-CODE-002',
        'claim_boundary': 'Feature screening only; not an ECDLP speedup claim.',
        'forbidden_oracles_used_in_features': False,
        'runs': runs,
        'failures': failures,
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text+'\n')
    print(text)


if __name__ == '__main__':
    main()
