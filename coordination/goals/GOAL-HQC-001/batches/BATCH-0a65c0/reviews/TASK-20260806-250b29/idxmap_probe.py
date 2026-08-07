#!/usr/bin/env python3
"""RED TEAM probe of CTRL-IDXMAP.  TASK-20260806-250b29.

CTRL-IDXMAP is NEW in amendment_v3.yaml, is ranked 3 of 8, is declared BLOCKING,
and claims detection probability "1, DETERMINISTICALLY".  It has never been run
on the real instrument (the producer's own OPEN-9).  Its only demonstration is
recalibrate.py phase `idxmap`, hard-coded at n=71, N=60, n_e=6, L=10.

This probe implements the control EXACTLY AS THE AMENDMENT SPECIFIES IT and
applies it to the contract's four real parameter sets, which the demonstration
never did.

Spec text (amendment_v3.yaml -> R2_controls -> CTRL_IDXMAP -> construction):
  "The control recomputes both arrays from the frozen (n, N, n_e, n_2, dup)
   alone ... trunc_idx[i] = i for i < N; block_idx[j] = [j*L, j*L+1, ...,
   j*L+L-1] with L = n_2*dup"

Claim tier TOY.  Pure integer arithmetic; no HQC object, no sampling, no
statistic.
"""
import json

# experiments/EXP-HQC-982268/specification.yaml, parameter_sets
SETS = {
    "PS-A":  dict(n=17669, N=17664, n_e=46, n_2=384, dup=3),
    "PS-R1": dict(n=5923,  N=5888,  n_e=46, n_2=128, dup=1),
    "PS-R3": dict(n=7187,  N=7168,  n_e=56, n_2=128, dup=1),
    "PS-R5": dict(n=11549, N=11520, n_e=90, n_2=128, dup=1),
}


def reference_map(n, N, n_e, L):
    """The amendment's reference expression, verbatim."""
    trunc = list(range(N))
    return trunc, [[trunc[j * L + t] for t in range(L)] for j in range(n_e)]


def instrument_map(n, N, n_e, n_2, dup, defect="none"):
    """What stage_a.py ACTUALLY reads, expressed as index arrays.

    stage_a truncates with `epp & mask_N` (coordinates 0..N-1 of e'') and
    partitions with `bits.reshape(B, n_e, n_2)` (contiguous windows of n_2), so
    the true block length in e-tilde coordinates is n_2, and n_e*n_2 = N.
    """
    trunc = list(range(N))
    if defect == "none":
        return trunc, [[trunc[j * n_2 + t] for t in range(n_2)] for j in range(n_e)]
    if defect == "V1-truncation-offset":
        trunc = [(i + 1) % n for i in range(N)]
        return trunc, [[trunc[j * n_2 + t] for t in range(n_2)] for j in range(n_e)]
    if defect == "V2-interleaved-partition":
        return trunc, [[trunc[j + t * n_e] for t in range(n_2)] for j in range(n_e)]
    if defect == "V3-last-block-early":
        return trunc, [[trunc[j * n_2 + t - (1 if j == n_e - 1 else 0)] for t in range(n_2)]
                       for j in range(n_e)]
    if defect == "DUP-STRIDE-fold":
        # OPEN-10 / the defect v3 moved to UNTESTED: the Reed-Muller duplication
        # fold reshaped (n_e,128,dup) instead of (n_e,dup,128).  Block j reads
        # EXACTLY the same coordinates in EXACTLY the same order; only the
        # grouping inside the decoder changes.
        return trunc, [[trunc[j * n_2 + t] for t in range(n_2)] for j in range(n_e)]
    raise ValueError(defect)


def compare(ref, got):
    rt, rb = ref
    gt, gb = got
    mt = sum(1 for a, b in zip(rt, gt) if a != b) + abs(len(rt) - len(gt))
    mb = sum(1 for A, B in zip(rb, gb) for a, b in zip(A, B) if a != b)
    mb += sum(abs(len(A) - len(B)) for A, B in zip(rb, gb))
    mb += abs(len(rb) - len(gb)) * max(len(rb[0]), len(gb[0]))
    return mt, mb


def main():
    out = {}
    print("=" * 78)
    print("A.  The control's reference expression, AS SPECIFIED (L = n_2*dup),")
    print("    against the CORRECT instrument at the four real parameter sets.")
    print("=" * 78)
    print("%-7s %6s %6s %4s %6s %8s  %s" % ("set", "N", "n_2", "dup", "L_spec",
                                            "n_e*L", "CTRL-IDXMAP verdict on a CORRECT run"))
    for s, p in SETS.items():
        L = p["n_2"] * p["dup"]
        rec = dict(N=p["N"], n_2=p["n_2"], dup=p["dup"], L_spec=L, n_e_times_L=p["n_e"] * L)
        try:
            ref = reference_map(p["n"], p["N"], p["n_e"], L)
            got = instrument_map(**{k: p[k] for k in ("n", "N", "n_e", "n_2", "dup")},
                                 defect="none")
            mt, mb = compare(ref, got)
            v = ("PASS" if mt + mb == 0
                 else "FIRES ON THE CORRECT INSTRUMENT (%d trunc, %d block mismatches)" % (mt, mb))
            rec.update(error=None, trunc_mismatch=mt, block_mismatch=mb, verdict=v)
        except IndexError as e:
            v = "IndexError: %s  -- reference map runs off the end of e-tilde" % e
            rec.update(error=str(e), verdict=v)
        print("%-7s %6d %6d %4d %6d %8d  %s" % (s, p["N"], p["n_2"], p["dup"], L,
                                                p["n_e"] * L, v))
        out.setdefault("A_spec_L_on_correct_instrument", {})[s] = rec

    print()
    print("    Cross-reference, SAME FILE: CTRL_POSHOM_v3 asserts 'n_e*L = N < n'")
    for s, p in SETS.items():
        print("      %-7s N/n_e = %-5d   n_2 = %-5d   n_2*dup = %-5d   %s"
              % (s, p["N"] // p["n_e"], p["n_2"], p["n_2"] * p["dup"],
                 "consistent" if p["N"] // p["n_e"] == p["n_2"] * p["dup"]
                 else "*** CONTRADICTS CTRL_IDXMAP ***"))
    print()
    print("    recalibrate.py phase `idxmap` used n=71, N=60, n_e=6, L=10, i.e.")
    print("    n_2=10 and dup=1 -- the one regime where n_2 == n_2*dup.  The")
    print("    demonstration cannot distinguish the two formulas.")

    print()
    print("=" * 78)
    print("B.  With the arithmetic REPAIRED (L = N/n_e = n_2): does the control do")
    print("    what it claims -- fire deterministically on V1/V2/V3?")
    print("=" * 78)
    print("%-7s %-26s %8s %8s %s" % ("set", "defect", "trunc", "block", "fires"))
    for s, p in SETS.items():
        L = p["N"] // p["n_e"]
        ref = reference_map(p["n"], p["N"], p["n_e"], L)
        for d in ("none", "V1-truncation-offset", "V2-interleaved-partition",
                  "V3-last-block-early", "DUP-STRIDE-fold"):
            got = instrument_map(**{k: p[k] for k in ("n", "N", "n_e", "n_2", "dup")}, defect=d)
            mt, mb = compare(ref, got)
            fires = (mt + mb) > 0
            print("%-7s %-26s %8d %8d %s" % (s, d, mt, mb, "YES" if fires else "no"))
            out.setdefault("B_repaired_L", {}).setdefault(s, {})[d] = dict(
                trunc_mismatch=mt, block_mismatch=mb, fires=fires)
        print()

    print("=" * 78)
    print("C.  Coverage of the accepted blind class after the repair.")
    print("=" * 78)
    print("  DUP-STRIDE-fold changes WHICH COORDINATES ARE COMBINED, not which are")
    print("  READ, so its index map is bit-identical to the correct one at every")
    print("  parameter set above -- CTRL-IDXMAP is blind to it BY CONSTRUCTION.")
    print("  amendment_v3.yaml's own text says the same defect is")
    print("  'position-equivariant by construction', which by the amendment's own")
    print("  structural argument makes CTRL-POSHOM blind to it too.  It is the")
    print("  defect v3 moved from the CATCH side to UNTESTED (OPEN-10), and it is")
    print("  only realisable at dup > 1, i.e. at PS-A, the set v3 drops from (iv).")
    json.dump(out, open("idxmap_probe.json", "w"), indent=1)


if __name__ == "__main__":
    main()
