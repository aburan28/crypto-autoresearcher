# EXP-SIG-003 driver — syzygy <-> d_reg-deficit link test
# (H-SIG-001; dispatched by DEC-20260718-017 next_actions, handoff TASK-20260718-SIG-F3).
#
# Reuses the EXP-SIG-001/002 instrument BIT-IDENTICALLY (src/h013_f5_signatures.sage
# sha256 1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087).
# All link-test logic lives in this driver; the pinned instrument is loaded,
# never modified.
#
# Usage (from repo root):
#   sage experiments/EXP-SIG-003/SIG3_run.sage --mode link --n 12 --seed 2 \
#        --arm sem --out experiments/EXP-SIG-003/runs/RUN-EXP-SIG-003-a/raw.json
#
# Per cell (n, seed, arm):
#   D3/D4 classification with transformation-tracked kernel bases (extract=True);
#   residual_4 via the verbatim EXP-SIG-002 v3-multiples logic;
#   D5 count-only classification (extract=False) -> rank, sr_pred, deficit,
#     kernel_dim, rankK5, extra_5, rows_5, kpiv_5;
#   LINK: rank mod K5 of the multiplication closure of all lower-degree
#     non-model syzygies:
#       A3  = rank { nu * kernel_3 : deg(nu) <= 2 } mod K5
#       A4  = rank { nu * kernel_4 : nu in {1} u {x_j} } mod K5
#       A4_beyond_A3 = incremental rank of A4 over kpiv5 u P3
#       A4_id = rank of identity embeddings of kernel_4 mod K5
#       residual_5 = extra_5 - A4
#   K4-images land in K5 (Koszul/principal multipliers compose; vanishing
#   multiples map to vanishing multiples), so A4 is the rank of the closure of
#   the D4 EXTRA space. Merge (i) <=> residual_5 == 0; independence (ii) <=>
#   residual_5 > 0.
#
# Controls per spec: C1/C2 continuity anchors, C3 null (extra=0, rank=pred,
# A3=A4=residual_5=0), C5 input-side instance filter, C6 dimension sanity.
# Determinism C4 is a separate identical invocation + compare_determinism.py.

import sys, os, time, json, argparse, platform, datetime, itertools, hashlib
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--mode', required=True, choices=['link'])
p.add_argument('--out', required=True)
p.add_argument('--n', type=int, required=True)
p.add_argument('--seed', type=int, required=True)
p.add_argument('--arm', required=True, choices=['sem', 'null'])
p.add_argument('--soft-cap', type=int, default=540,
               help='do not start the D5 stage after this many seconds')
args = p.parse_args()

EXPDIR = Path(args.out).resolve().parents[2]
sys.path.insert(0, str(EXPDIR / 'src'))
import sage.version
from sage.all import GF, PolynomialRing, set_random_seed
load(str(EXPDIR / 'src' / 'h013_f5_signatures.sage'))

t_start = time.time()
started_at = datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha256(pth):
    return hashlib.sha256(Path(pth).read_bytes()).hexdigest()


instrument_hashes = {f.name: sha256(f) for f in sorted((EXPDIR / 'src').iterdir())}

out = {
    "experiment": "EXP-SIG-003",
    "mode": args.mode,
    "args": vars(args),
    "environment": {
        "sage_version": str(sage.version.version),
        "python_version": sys.version.split()[0],
        "os": platform.platform(),
        "machine": platform.machine(),
    },
    "instrument_sha256": instrument_hashes,
    "started_at": started_at,
}

stage_times = {}


def flush():
    out["elapsed_s_so_far"] = round(time.time() - t_start, 2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(jsonsafe(out), fh, indent=1)


def softcap_hit():
    return (time.time() - t_start) > args.soft_cap


def multiplier_sets(nb, maxdeg):
    ms = [frozenset()]
    for md in range(1, maxdeg + 1):
        for combo in itertools.combinations(range(nb), md):
            ms.append(frozenset(combo))
    return ms


def images_of(kernel_basis, rows_src, tag2idx5, mults):
    """Monomial multiples of kernel-basis syzygies embedded in the D5 row
    space. Returns (list of GF(2) bitmasks over D5 row indices, miss count)."""
    imgs = []
    misses = 0
    for kv in kernel_basis:
        pos = bits_to_positions(kv)
        tags = [rows_src[pp][0] for pp in pos]
        for nu in mults:
            img = 0
            for (i, mu) in tags:
                ix = tag2idx5.get((i, mu | nu))
                if ix is None:
                    misses += 1
                else:
                    img = img ^^ (1 << ix)
            if img:
                imgs.append(int(img))
    return imgs, misses


def full_reduce(v, piv):
    """Canonical reduction of v modulo the echelon pivot family piv (lead ->
    vector, lead = highest set bit). Unlike the instrument's reduce_against
    (which stops at the topmost non-pivot bit and is exact only for
    membership testing), this clears EVERY pivot-lead bit top-down, so the
    result is the unique canonical remainder: full_reduce(v) = 0 iff v is in
    the span, and full_reduce is LINEAR. Consequently
    rank(full_reduce(family)) == the family's TRUE rank mod span(piv).
    (Pilot RUN-a proved the early-break variant overestimates quotient ranks:
    it gave A3+A4_beyond_A3 = 618 < 671 = A4, arithmetically impossible for
    true ranks since the v3 images lie inside span(v4 images).)"""
    bb = int(v)
    out = 0
    while bb:
        lead = bb.bit_length() - 1
        if lead in piv:
            bb = bb ^^ piv[lead]
        else:
            out = out | (1 << lead)
            bb = bb ^^ (1 << lead)
    return out


def rank_reduced(vecs, piv):
    red = [full_reduce(v, piv) for v in vecs]
    red = [r for r in red if r]
    return vec_echelon(red)


# ==========================================================================
# EXP-SIG-002 D5 continuity anchors (standard instances, sem arm)
D5_ANCHORS = {12: {2: {"rank": 28097, "deficit": 1321, "extra": 1322}},
              15: {1: {"rank": 69073, "deficit": 1862, "extra": 1863}}}
RESIDUAL4_ANCHORS = {12: 9, 15: 10}

print("=== EXP-SIG-003 link cell: n=%d seed=%d arm=%s ===" % (args.n, args.seed, args.arm), flush=True)

# ---- build + input-side instance filter (C5)
t0 = time.time()
monosets, nb, meta = build_boolean_semaev(args.n, 3, args.seed)
if monosets is None:
    out["cell"] = {"n": args.n, "seed": args.seed, "arm": args.arm,
                   "status": "skipped: no decomposable R", "meta": meta}
    flush()
    print("skipped: no decomposable R", flush=True)
    sys.exit(0)
rx_zero = str(meta.get("R_x", "")).strip() == "0"
has_lin = int(meta.get("eq_degs_hist", {}).get("1", 0)) > 0
standard = (not rx_zero) and (not has_lin)
filt = {"rx_zero": bool(rx_zero), "has_linear_eq": bool(has_lin),
        "standard": bool(standard)}
cell = {"n": args.n, "seed": args.seed, "arm": args.arm, "nb": int(nb),
        "meta": meta, "filter": filt, "status": "completed"}
out["cell"] = cell
stage_times["build_s"] = round(time.time() - t0, 2)
print("  built: nb=%d n_eqs=%d hist=%s R_x=%s... standard=%s (%.1fs)" % (
    nb, meta.get("n_eqs"), meta.get("eq_degs_hist"),
    str(meta.get("R_x"))[:24], standard, stage_times["build_s"]), flush=True)
flush()

if args.arm == "null":
    rng = random.Random(stable_seed("null", args.n, 3, args.seed))
    ms = boolean_null(monosets, nb, rng)
else:
    ms = monosets

# ---- D3 / D4 with kernel bases (extract=True)
t0 = time.time()
rec3, rows3, kernel3, kpiv3 = analyze_syzygy_space(ms, nb, 3, extract=True, block_size=args.n)
rec4, rows4, kernel4, kpiv4 = analyze_syzygy_space(ms, nb, 4, extract=True, block_size=args.n)
cell["D3"] = rec3
cell["D4"] = rec4
stage_times["d3d4_s"] = round(time.time() - t0, 2)
print("  D3: def=%d extra=%d rankK=%d kernel=%d | D4: def=%d extra=%d rankK=%d kernel=%d (%.1fs)" % (
    rec3["deficit"], rec3["extra"], rec3["rankK"], rec3["kernel_dim"],
    rec4["deficit"], rec4["extra"], rec4["rankK"], rec4["kernel_dim"],
    stage_times["d3d4_s"]), flush=True)
flush()

# ---- residual_4: verbatim EXP-SIG-002 v3-multiples logic
t0 = time.time()
tag2idx4 = {tag: ix for ix, (tag, _) in enumerate(rows4)}
v3_mults = []
for kv in kernel3:
    pos3 = bits_to_positions(kv)
    tags3 = [rows3[pp][0] for pp in pos3]
    for j in range(nb):
        img = 0
        for (i, mu) in tags3:
            ix = tag2idx4.get((i, mu | {j}))
            if ix is not None:
                img = img ^^ (1 << ix)
        if img:
            v3_mults.append(int(img))
red = [reduce_against(v, kpiv4) for v in v3_mults]
red = [r for r in red if r]
rank_v3mod, _ = vec_echelon(red)
residual4 = int(rec4["extra"] - rank_v3mod)
cell["v3_multiples_at_D4"] = {
    "n_d3_syzygies": len(kernel3),
    "n_mult_images": len(v3_mults),
    "rank_mod_K4": int(rank_v3mod),
    "residual_new_at_D4": residual4,
}
stage_times["residual4_s"] = round(time.time() - t0, 2)
print("  residual_4 = extra_4(%d) - rank_v3mod(%d) = %d (%.1fs)" % (
    rec4["extra"], rank_v3mod, residual4, stage_times["residual4_s"]), flush=True)
flush()

# ---- D5 count-only stage (checkpoint boundary: soft cap guards its start)
if softcap_hit():
    cell["status"] = "censored_softcap_before_D5"
    cell["stage_times"] = stage_times
    flush()
    print("  CENSORED at soft cap before D5 stage (infrastructure, not evidence)", flush=True)
    sys.exit(0)
t0 = time.time()
rec5, rows5, _, kpiv5 = analyze_syzygy_space(ms, nb, 5, extract=False, block_size=args.n)
rec5.pop("extra_reps", None)
cell["D5"] = rec5
stage_times["d5_s"] = round(time.time() - t0, 2)
print("  D5: nrows=%d rank=%d pred=%d deficit=%d kernel=%d rankK=%d extra=%d (%.1fs)" % (
    rec5["nrows"], rec5["rank"], rec5["sr_pred"], rec5["deficit"],
    rec5["kernel_dim"], rec5["rankK"], rec5["extra"], stage_times["d5_s"]), flush=True)
flush()

# ---- LINK computation
t0 = time.time()
tag2idx5 = {tag: ix for ix, (tag, _) in enumerate(rows5)}
m2 = multiplier_sets(nb, 2)
m1 = multiplier_sets(nb, 1)
v3_imgs, miss3 = images_of(kernel3, rows3, tag2idx5, m2)
v4_imgs, miss4 = images_of(kernel4, rows4, tag2idx5, m1)
v4_id_imgs, miss4id = images_of(kernel4, rows4, tag2idx5, [frozenset()])
A3, P3 = rank_reduced(v3_imgs, kpiv5)
A4, P4 = rank_reduced(v4_imgs, kpiv5)
merged = dict(kpiv5)
merged.update(P3)
red4b = [full_reduce(v, merged) for v in v4_imgs]
A4_beyond_A3, _ = vec_echelon([r for r in red4b if r])
A4_id, _ = rank_reduced(v4_id_imgs, kpiv5)
residual5 = int(rec5["extra"] - A4)
link = {
    "reduction_semantics": "canonical full_reduce (exact mod-K5 ranks); residual_4 anchor above keeps the pinned instrument semantics verbatim",
    "n_v3_imgs": len(v3_imgs), "n_v4_imgs": len(v4_imgs),
    "n_v4_id_imgs": len(v4_id_imgs),
    "miss3": miss3, "miss4": miss4, "miss4id": miss4id,
    "A3": int(A3), "A4": int(A4), "A4_beyond_A3": int(A4_beyond_A3),
    "A4_id": int(A4_id),
    "extra_5": rec5["extra"], "deficit_5": rec5["deficit"],
    "extra_4": rec4["extra"], "residual_4": residual4,
    "residual_5": residual5,
    "coverage_vs_deficit": (A4 / rec5["deficit"]) if rec5["deficit"] else None,
    "coverage_vs_extra5": (A4 / rec5["extra"]) if rec5["extra"] else None,
    "amplification_vs_extra4": (A4 / rec4["extra"]) if rec4["extra"] else None,
    "bound_extra4_x_nb1": rec4["extra"] * (1 + nb),
    "sanity": {
        "A3_le_A4": bool(A3 <= A4),
        "A4_le_extra5": bool(A4 <= rec5["extra"]),
        "A4_le_bound": bool(A4 <= rec4["extra"] * (1 + nb)),
        "A3_plus_beyond_eq_A4": bool(A3 + A4_beyond_A3 == A4),
        "A4_id_le_A4": bool(A4_id <= A4),
        "no_missing_rows": bool(miss3 == 0 and miss4 == 0 and miss4id == 0),
        "residual5_nonneg": bool(residual5 >= 0),
    },
}
cell["link"] = link
stage_times["link_s"] = round(time.time() - t0, 2)
print("  LINK: A3=%d A4=%d (bound %d) A4_beyond_A3=%d A4_id=%d | extra_5=%d deficit_5=%d residual_5=%d coverage=%.4f amplification=%.2f (%.1fs)" % (
    A3, A4, link["bound_extra4_x_nb1"], A4_beyond_A3, A4_id,
    rec5["extra"], rec5["deficit"], residual5,
    link["coverage_vs_deficit"] or -1, link["amplification_vs_extra4"] or -1,
    stage_times["link_s"]), flush=True)
flush()

# ---- controls
if args.arm == "sem":
    anch = D5_ANCHORS.get(args.n, {}).get(args.seed)
    c1 = (rec3["deficit"] == 1 and rec3["extra"] == 1
          and rec4["deficit"] == (8 * args.n) // 3 and rec4["extra"] == (8 * args.n) // 3
          and residual4 == RESIDUAL4_ANCHORS.get(args.n))
    c2 = True if anch is None else (
        rec5["rank"] == anch["rank"] and rec5["deficit"] == anch["deficit"]
        and rec5["extra"] == anch["extra"])
    cell["controls"] = {
        "c1_continuity_d3d4": bool(c1),
        "c2_continuity_d5": bool(c2),
        "c2_anchor": anch,
        "c6_sanity_all": all(link["sanity"].values()),
        "c5_standard_instance": bool(standard),
    }
else:
    c3 = (rec3["extra"] == 0 and rec4["extra"] == 0 and rec5["extra"] == 0
          and rec3["rank"] == rec3["sr_pred"] and rec4["rank"] == rec4["sr_pred"]
          and rec5["rank"] == rec5["sr_pred"]
          and residual4 == 0 and A3 == 0 and A4 == 0 and residual5 == 0)
    cell["controls"] = {
        "c3_null_zero_everywhere": bool(c3),
        "c6_sanity_all": all(link["sanity"].values()),
    }

cell["stage_times"] = stage_times
out["finished_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
out["wall_seconds"] = round(time.time() - t_start, 2)
flush()
print("wrote %s (%.1fs)" % (args.out, out["wall_seconds"]), flush=True)
