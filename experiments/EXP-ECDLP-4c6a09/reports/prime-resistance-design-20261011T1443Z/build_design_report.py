#!/usr/bin/env python3
"""Render a proposed study. Reads prior measurements; runs no cryptographic trials."""

import argparse
import csv
import hashlib
import json
import math
import platform
import shutil
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import typst


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    plan = json.loads((out / "plan.json").read_text())
    assert plan["status"] == "proposed_design_not_executed"
    assert plan["official_ledger_registration"] is False
    assert plan["main_prime_sample"]["total_moduli"] == 108
    with (out / "inputs/historical-curve-identities.csv").open() as handle:
        curves = list(csv.DictReader(handle))
    assert len(curves) == 6
    for row in curves:
        assert int(row["group_order"]) == int(row["subgroup_order"]) * int(row["cofactor"])
        assert len(row["curve_uid"].split(":")[-1]) == 64

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "svg.fonttype": "none", "axes.spines.top": False,
                         "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(10.5, 4.1))
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.1)
    ax.axis("off")

    def box(x, y, w, h, label, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                   boxstyle="round,pad=0.07", linewidth=1.2,
                                   edgecolor=color, facecolor=color + "18"))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=10)

    def arrow(start, end):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                                    mutation_scale=13, color="#52616b", linewidth=1.3))

    ax.text(0, 3.95, "PROPOSED: three separate measurements", fontsize=14,
            weight="bold", va="top", color="#18394c")
    box(.15, 2.15, 2.75, 1.15,
        "36 sparse-prime blocks\nS + nearby random R\n+ residue-matched random C\n108 main moduli", "#236f93")
    box(3.65, 2.3, 2.75, .85,
        "Uniform curve audit\n32 nonsingular models / p", "#38815f")
    box(7.1, 2.3, 3.05, .85,
        "Subgroup size + flags\nCurve-generation outcome", "#38815f")
    box(3.65, .95, 2.75, .85,
        "512-model candidate pools\nSubgroup order ratio ≤1.10", "#7454a1")
    box(7.1, .95, 3.05, .85,
        "Rho work / √ell + BSGS\nAttack-specific cost", "#7454a1")
    box(.15, .12, 2.75, .9,
        "Fixed arithmetic workloads\nCommon reducer, then\nspecialized S reducer", "#a06a24")
    box(3.65, .12, 2.75, .52,
        "CPU / wall time per operation", "#a06a24")
    arrow((2.98, 2.72), (3.55, 2.72))
    arrow((6.49, 2.72), (6.99, 2.72))
    arrow((2.98, 2.25), (3.55, 1.45))
    arrow((6.49, 1.37), (6.99, 1.37))
    arrow((1.52, 2.07), (1.52, 1.1))
    arrow((2.98, .4), (3.55, .4))
    fig.tight_layout(pad=.4)
    fig.savefig(out / "comparison-design.svg", metadata={"Date": None})
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    for A, B, color, marker, label in [(-3, 3, "#236f93", "o", "A = −3, B = 3 (3 groups)"),
                                     (7, 1, "#a7652d", "s", "A = 7, B = 1 (3 groups)")]:
        subset = sorted([r for r in curves if int(r["A"]) == A], key=lambda r: int(r["p"]))
        xs = [int(r["p"]).bit_length() for r in subset]
        ys = [math.log2(int(r["subgroup_order"])) for r in subset]
        ax.plot(xs, ys, marker=marker, color=color, label=label, lw=1.4, ms=7)
        for row, x, y in zip(subset, xs, ys):
            offset = (-6, -19 if A == -3 else 8) if x >= 30 else (8, 7 if A == -3 else -17)
            ax.annotate(f"ell = {int(row['subgroup_order']):,}", (x, y),
                        xytext=offset, textcoords="offset points", fontsize=9,
                        color=color, ha="left" if x < 30 else "right")
    ax.set_xlabel("Field-prime bit length (bits)")
    ax.set_ylabel("log₂ of prime subgroup order ell (bits)")
    ax.set_xticks([18, 21, 36])
    ax.set_xlim(16.5, 38)
    ax.set_ylim(5.5, 29)
    ax.grid(axis="y", color="#e2e6e9", lw=.6)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.set_title("Measured historical subgroups: field size does not fix attack size", loc="left", fontsize=13)
    fig.text(.08, .015,
             "n = 6 exact groups; RUN-ECDLP-6d910b / 9e6cc1. No sampling uncertainty bars.\n"
             "Previously selected curves; this is not a random-prime comparison.", fontsize=8.5)
    fig.tight_layout(rect=(0, .08, 1, 1))
    fig.savefig(out / "historical-subgroup-confounding.svg", metadata={"Date": None})
    plt.close(fig)

    controls = [
        ("R", "Nearby random prime", "Same bit length; magnitude within 1%; total family contrast"),
        ("C", "Residue-matched random prime", "R rules plus same residue modulo 12; mechanistic contrast"),
        ("ell", "Matched subgroup size", "Largest prime orders within ratio 1.10; normalize work by sqrt(ell)"),
        ("sham", "Same-group permuted tags", "Exact scalar answers and operation counts must agree"),
        ("iso", "Isomorphic curve", "Transported hash reproduces trace; native hash detects representation effects"),
        ("oracle", "Opaque cyclic group interface", "Hides field coordinates and prime representation from attacker"),
        ("rho32", "32-adding replication", "Fixed independent walk, all main matched groups"),
        ("BSGS", "Independent solver", "Verified scalar; declared memory and complete target coverage"),
        ("easy", "Small-prime subgroup", "Correct recovery and lower raw work; absence fails instrument pass"),
        ("reducer", "Generic versus sparse reduction", "Identical inputs, exact agreement; timing separate from search work"),
        ("timing", "Isolated randomized batches", "One pinned timing worker; ABBA/randomized order"),
        ("truth", "Validation and counter replay", "Every scalar verified; deterministic counters replay exactly"),
    ]
    with (out / "controls.csv").open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["id", "control", "purpose_or_pass_condition"])
        writer.writerows(controls)

    uid_blocks = []
    for r in curves:
        uid_blocks.append(
            f"#text(size:7.4pt)[A={r['A']}, B={r['B']}, p={r['p']}, k={r['k']}\\\n"
            f"N={r['group_order']}; ell={r['subgroup_order']}; h={r['cofactor']}; "
            f"G=({r['G_x']}, {r['G_y']})\\\n{r['curve_uid']}]\n")
    document = r'''#set page(paper:"a4",margin:16mm,footer:context [#text(size:8pt)[EXP-ECDLP-5184f7 • proposed design • no new attack results] #h(1fr) #counter(page).display()])
#set text(font:"DejaVu Sans",size:9.5pt)
#set par(leading:.5em)
= Are Solinas primes more resistant to ECDLP?
Controlled study design • 2026-10-11 UTC • related EXP-ECDLP-4c6a09

*Measure three distinct effects: which curves are generated, attack work at matched subgroup size, and arithmetic speed.* No new trial was run. This is a design report; solver/oracle/timing integration remains subsequent implementation work.

== Main sample: 36 paired prime blocks
12 sparse primes each at 24, 28 and 32 bits, drawn without replacement from the deduplicated verified catalog p = 2ᵇ − 2ᵃ + s·2ᶜ + t, 1 ≤ c < a ≤ b−2, s,t ∈ {−1,+1}. This specified sparse ensemble does not represent every Solinas family.

#table(columns:(.5fr,1.3fr,2fr),inset:5pt,
 [Arm],[Prime-selection rule],[What it tests],
 [S],[Specified sparse catalog],[Prime family of interest],
 [R],[Same bits; within 1% of S],[Total sparse-versus-random contrast],
 [C],[R rules + same p mod 12],[Effect beyond this congruence control])
Random controls use uniform odd-integer rejection sampling with exact primality checks, excluding the sparse catalog and historical anchors. No next-prime sampling and no outcome-dependent replacement. Freeze all 108 main moduli before curve counts or attack timings.

#image("comparison-design.svg",width:100%)

== Separate historical case studies
Six exact earlier primes, each with R/C controls, add 18 moduli. Their sizes are 18, 21, 32, 36, 56 and 72 bits. The four smaller cases receive the toy attack stage; 56-/72-bit cases are structural audits only. They are reported individually, never pooled with the 36 main blocks.

#pagebreak()
= Attack measurements and controls
Audit the first 32 uniform nonsingular coefficient models per modulus without security screening: full curve order/factorization, largest prime subgroup ell, cofactor, trace, twist and weak-curve flags. This retains potential differences in curve-generation outcomes.

For conditional attacks, prepare 512 models per eligible modulus. Fixed screen: ordinary, N≠p, j outside {0,1728}, largest prime ell of 16–26 bits appearing once, and no embedding degree ≤20. This removes obvious confounders and is not a comprehensive security certificate.

Match S/R and S/C subgroup orders within ratio 1.10, before attacks. Use at most eight common S groups per block. Retain short/empty blocks. Every G must satisfy G≠O and ell·G=O; retain full EC1 identities and all selection records.

== Primary metric
Pollard rho, 16-adding walk, Brent cycle detection; four uniform synthetic targets per group and four walk seeds per target. Verify every scalar independently. At most 13,824 main rho attempts. Count search group operations W and measure *U = min(W/√ell,20)*. The exact integer cap is ceil(20√ell); setup, preparation and verification have separate counters, with end-to-end cost as a secondary outcome.

The √ell normalization comes from birthday collisions: after about √ell sampled group states, collisions become likely. Increasing ell alone therefore increases raw generic attack work. It need not indicate an effect of the field-prime shape.

BSGS uses the same targets with M=min(4096,ceil√ell) stored points. Retain actual bytes and complete target coverage. At most 3,456 main BSGS attempts. All arms first use the same generic arithmetic implementation.

#table(columns:(1.2fr,2.3fr),inset:4pt,
 [Control],[Interpretation or required behavior],
 [Sham family tags],[Exact same-group counts and answers],
 [Isomorphic curve],[Transported hashing reproduces the walk; native hashing checks encoding effects],
 [Opaque group + 32-adding walk],[All main groups; distinguish coordinate/walk artifacts],
 [BSGS + easy subgroups],[Independent correct solver and instrument sensitivity],
 [Generic/sparse reducers],[Same operands; exact agreement; timing separate],
 [Truth, replay, isolated timing],[No exposed scalar truth; deterministic counters; pinned single worker])

== Decision rule fixed in advance
Compute curve means including capped attempts; paired log ratios; equal block weights. Bootstrap whole prime blocks within size strata, 10,000 replicates, for 99% confidence intervals. Repeated targets/seeds are not independent primes. Higher measured rho cost requires the overall S/R lower bound >1.20, direction agreement in at least two sizes, and passing controls. Practical similarity requires the entire interval within [1/1.20,1.20]; otherwise inconclusive. Over 5% censoring limits claims to the declared capped work. Achieved statistical power is not asserted.

#pagebreak()
= Why subgroup size must be controlled
*Measured context only:* the preceding number-field experiment held base primes fixed. It did not compare Solinas with random primes. The two rational models below were previously selected for rank gains, so they are diagnostics rather than the new primary sample.

#image("historical-subgroup-confounding.svg",width:100%)
Six exact subgroup identities are listed on the next page. No uncertainty bars are shown because these are exact orders of six recorded groups, rather than estimates from the proposed sampling scheme. Source: internal immutable RUN-ECDLP-6d910b / RUN-ECDLP-9e6cc1 records and copied curve-identities.csv.

== How to interpret possible outcomes
#table(columns:(1.3fr,2fr),inset:5pt,
 [Observation],[Supported conclusion],
 [Larger ell in the unconditional S audit],[Different curve-generation outcomes under this recipe],
 [Same normalized calls; different seconds],[Arithmetic or implementation-speed effect],
 [More coordinate-walk calls; no oracle effect],[Representation or walk effect],
 [Higher normalized rho cost across controls],[Higher cost for that declared attack in this sample],
 [Interval entirely within the practical margin],[Practical similarity within the tested scope],
 [Wide interval or failed controls],[Inconclusive; preserve failures and unmatched samples])

== What would establish stronger resistance?
Two cyclic prime-order groups of the same order are abstractly isomorphic. A generic attacker behind an opaque interface cannot read the binary shape of the field prime. A higher rho benchmark constant alone therefore does not establish intrinsic generic hardness.

A broader claim would need a validated structure-dependent shortcut that works on comparable random-prime curves and is avoided by the specified sparse-prime curves, with independent reproduction and review. Retain the cheaper applicable generic control. Toy results do not establish deployed-curve or asymptotic security.

#pagebreak()
= Identities, provenance and execution boundary
== Exact identities for the historical chart
''' + "\n".join(uid_blocks) + r'''
== Reproduction and scope
The adjacent protocol.md is the detailed source-linked protocol. plan.json is the initial machine-readable plan; measurement-boundary.json authoritatively clarifies the common normalized horizon. No samples or scientific observations changed. design-provenance.json hashes internal evidence and lists the exact six anchor moduli. controls.csv is a compact control inventory.

build_design_report.py renders both editable SVG figures and this PDF from the plan and the six copied historical identities. It does not run primality catalogs, point counting, or ECDLP trials. Future preparation must materialize the catalog, matching, EC1 records and all source/seed traces; identities for unsampled groups are not invented here.

Resource protection: at most two preparation workers, one isolated timing worker, 4 GiB address-space limit per worker, 8 GiB headroom and a 600-second process watchdog. Fixed samples and operation caps define stops; there is no campaign wall-clock/batch ceiling. Infrastructure failures are not mathematical evidence.

The proposed identifier is not an officially registered or approved executable experiment. No independent scientific review, hypothesis promotion or canonical frontier update occurred in this design session. Earlier immutable results and reports remain unchanged.
'''
    (out / "report.typ").write_text(document)
    typst.compile(str(out / "report.typ"), output=str(out / "report.pdf"), root=str(out))
    own = Path(__file__).resolve()
    if own != out / own.name:
        shutil.copyfile(own, out / own.name)
    write_json(out / "render-environment.json", {
        "rendered_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "matplotlib": matplotlib.__version__,
        "typst": "0.15.0", "new_attack_results": None,
        "source_files": {str(p.relative_to(out)): digest(p) for p in [
            out / "plan.json", out / "measurement-boundary.json",
            out / "inputs/historical-curve-identities.csv", out / "build_design_report.py",
            out / "report.typ"]},
        "pdf_sha256": digest(out / "report.pdf")})
    print(json.dumps({"status": "rendered_design_only", "out": str(out),
                      "pdf_sha256": digest(out / "report.pdf")}))


if __name__ == "__main__":
    main()
