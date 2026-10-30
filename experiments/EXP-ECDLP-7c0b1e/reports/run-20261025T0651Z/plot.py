#!/usr/bin/env python3
"""Rebuild every figure and the seven-page report from descriptive sealed-data extracts.

This performs plotting and arithmetic only. It never invokes an ECDLP experiment.
Python 3.12, numpy and matplotlib are the only dependencies.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import textwrap

HERE = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".inspection/mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(HERE / ".inspection/cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

FIGURES = HERE / "figures"
FIGURES.mkdir(exist_ok=True)
D = json.loads((HERE / "data/decoder-summary.json").read_text())
P = json.loads((HERE / "data/projection-summary.json").read_text())
R = json.loads((HERE / "data/runtime-summary.json").read_text())
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
    "font.size": 10, "axes.titlesize": 11, "axes.labelsize": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.use14corefonts": False, "pdf.fonttype": 42, "ps.useafm": False, "svg.fonttype": "none",
    "savefig.facecolor": "white", "axes.grid": True,
    "grid.alpha": .22, "grid.linewidth": .6,
})
COLORS = {"x_mod_7": "#246c91", "power_residue_5": "#bb5c2c",
          "x_hash_7": "#628854", "constant": "#777777"}
LABEL = {"x_mod_7": "x mod 7", "power_residue_5": "fifth residue",
         "x_hash_7": "x hash 7", "constant": "constant"}
STAMP = dt.datetime(2026, 10, 25, tzinfo=dt.timezone.utc)
PDF_META = {"Title": "Classical ECDLP follow-up: sealed observations", "Author": "Codex",
            "CreationDate": STAMP, "ModDate": STAMP}


def save(fig, name):
    svg = FIGURES / f"{name}.svg"
    fig.savefig(svg, bbox_inches="tight")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight", metadata=PDF_META)


def projection_fig():
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.15), layout="constrained")
    for metric, ax in enumerate(axes):
        ax.axhline(0, color="#555555", lw=.7)
        for feature in ["x_mod_7", "power_residue_5", "x_hash_7"]:
            rows = [r for r in P["gap_by_feature_size"] if r["feature"] == feature]
            x = [r["subgroup_bits"] for r in rows]
            means = [r["gap_mean_min_max"][metric][0] for r in rows]
            lower = [a - r["gap_mean_min_max"][metric][1] for a, r in zip(means, rows)]
            upper = [r["gap_mean_min_max"][metric][2] - a for a, r in zip(means, rows)]
            shift = {"x_mod_7": -.12, "power_residue_5": 0, "x_hash_7": .12}[feature]
            ax.errorbar(np.array(x) + shift, means, yerr=[lower, upper],
                        marker="o", lw=1.25, ms=4, capsize=2,
                        color=COLORS[feature], label=LABEL[feature])
        ax.set_xticks([8, 10, 12])
        ax.set_xlabel("Prime subgroup order (bits)")
        ax.set_title(["Pair addition", "D0: double", "D1: double + P"][metric])
    axes[0].set_ylabel("Observed minus matched null (bits)")
    axes[2].legend(loc="lower right", fontsize=8, framealpha=.95)
    fig.suptitle("Exact population entropies: mean and range across fresh curves", fontsize=12)
    return fig


def decoder_fig():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.2), layout="constrained", sharey=True)
    features = ["constant", "x_hash_7", "x_mod_7", "power_residue_5"]
    for ax, beam in zip(axes, [1, 8]):
        for mode, offset, alpha in [("model", -.19, .55), ("exact", .19, 1)]:
            for i, feature in enumerate(features):
                row = next(r for r in D["outcomes_by_configuration"]
                           if r[0:3] == [feature, mode, beam])
                height = 100 * row[4] / row[3]
                ax.bar(i + offset, height, .35, color=COLORS[feature], alpha=alpha,
                       label=mode if i == 0 else None)
                ax.text(i + offset, height + .18, f"{row[4]}/{row[3]}",
                        ha="center", va="bottom", fontsize=7.5, rotation=90 if beam == 1 else 0)
                reference = 100 * row[7] / row[3]
                ax.plot([i + offset - .17, i + offset + .17], [reference] * 2,
                        color="black", lw=1)
        ax.set_xticks(range(4), [LABEL[f] for f in features], rotation=16)
        ax.set_title(f"Beam width {beam}; model / exact prefixes")
        ax.set_ylim(0, 8.6)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("Verified hit cases (%)")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.suptitle("Public-target decoder: per-configuration toy recovery", fontsize=12)
    return fig


def calibration_fig():
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.15), layout="constrained")
    for feature in ["x_mod_7", "power_residue_5", "x_hash_7"]:
        rows = [r for r in D["heldout_calibration_by_size"] if r[0] == feature]
        axes[0].plot([r[1] for r in rows], [r[4] - r[3] for r in rows],
                     marker="o", color=COLORS[feature], label=LABEL[feature])
        axes[1].plot([r[1] for r in rows], [r[8] for r in rows], marker="o",
                     color=COLORS[feature], label=LABEL[feature])
    axes[0].axhline(0, color="black", lw=.7)
    axes[0].set_ylabel("Marginal minus conditional loss (bits)")
    axes[0].set_title("Heldout one-step prediction; both bits")
    axes[1].set_ylabel("Median max(delta0, delta1)")
    axes[1].set_title("Fitted-kernel Dobrushin diagnostic")
    for ax in axes:
        ax.set_xticks([8, 10, 12])
        ax.set_xlabel("Prime subgroup order (bits)")
    axes[1].legend(fontsize=8)
    fig.suptitle("Calibration gains shrink with size in this finite panel", fontsize=12)
    return fig


def timeline_fig():
    fig, ax = plt.subplots(figsize=(10, 3.15), layout="constrained")
    origin = dt.datetime.fromisoformat(R["started_at"])
    phases = [("build", "#b9c3cb"), ("self_test", "#a693b5"), ("measurement", "#246c91")]
    labels = []
    for y, module in enumerate(R["module_execution"]):
        labels.append(module["name"])
        for phase, color in phases:
            rec = module[phase]
            begin = (dt.datetime.fromisoformat(rec["started_utc"]) - origin).total_seconds()
            end = (dt.datetime.fromisoformat(rec["finished_utc"]) - origin).total_seconds()
            ax.broken_barh([(begin, end-begin)], (y-.32, .64),
                           facecolors=color, label=phase if y == 0 else None)
            if end-begin < .12:
                ax.plot(begin, y, marker="|", ms=9, color=color, mew=1.5)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel("Seconds after 2026-10-25 06:51:10.594266 UTC")
    ax.set_xlim(0, 125)
    ax.axvline(121.795798, color="#bb5c2c", lw=1, ls="--", label="command complete")
    ax.axvline(124.715335, color="#777777", lw=1, ls=":", label="output validated")
    ax.set_title("Three-worker pool: projection census overlaps decoder and local audit")
    ax.legend(fontsize=7.5, loc="center left")
    return fig


def page(number, title, subtitle=""):
    fig = plt.figure(figsize=(8.27, 11.69))
    fig.text(.085, .946, title, fontsize=18, fontweight="bold", color="#22495c")
    if subtitle:
        fig.text(.085, .915, subtitle, fontsize=9.5, color="#555555")
    fig.text(.085, .038, "EXP-ECDLP-7c0b1e / RUN-ECDLP-0b7dd5 | observations only", fontsize=8, color="#666666")
    fig.text(.905, .038, f"{number}/7", ha="right", fontsize=8, color="#666666")
    return fig


def para(fig, y, text, size=11, width=92, gap=.019):
    lines = textwrap.wrap(text, width=width)
    fig.text(.085, y, "\n".join(lines), va="top", fontsize=size, linespacing=1.35)
    return y - gap * len(lines) - .019


def section(fig, y, label):
    fig.text(.085, y, label, fontsize=12, fontweight="bold", color="#22495c", va="top")
    return y - .032


def table(fig, y, columns, rows, widths=None, height=.034, size=9):
    h = height * (len(rows) + 1)
    ax = fig.add_axes([.085, y - h, .83, h])
    ax.axis("off")
    t = ax.table(cellText=rows, colLabels=columns, colWidths=widths,
                 cellLoc="left", colLoc="left", bbox=[0, 0, 1, 1])
    t.auto_set_font_size(False)
    t.set_fontsize(size)
    for (row, _), cell in t.get_celld().items():
        cell.set_linewidth(.4)
        cell.set_edgecolor("#d9dfe2")
        if row == 0:
            cell.set_facecolor("#edf2f5")
            cell.set_text_props(fontweight="bold")
    return y - h - .025


def build_report():
    # The report is text/tables, with vector charts supplied as separate files.
    with PdfPages(HERE / "report.pdf", metadata=PDF_META) as pdf:
        fig = page(1, "Classical ECDLP follow-up", "Fresh curves, a public-input decoder and a scoped local obstruction | 25 October 2026")
        y = section(fig, .865, "What completed")
        y = para(fig, y, "Three classical follow-up tracks ran to output validation: an exact projection census, a public-input ladder decoder, and an expanded local basis audit. Five jobs used at most three simultaneous workers on four allocated CPUs. All 3,624 producer rows and the public witness replay passed the declared output checks.")
        y = table(fig, y, ["Track", "Measured workload", "Rows"], [
            ["Projection scale", "24 curves; six feature/control families", "144"],
            ["Public decoder", "90 kernels; 2,880 target cases; six NAs", "2,976"],
            ["Local basis audit", "Expanded exact grammar and polynomial certificate", "504"]], [.24, .65, .11])
        y = section(fig, y, "Observations")
        y = para(fig, y, "Pair-entropy deficits broadly persist on fresh curves but become much smaller. At 12 subgroup bits, x-mod-7 gaps are about -0.00060 to -0.00024 bits; fifth-residue gaps are about -0.00088 to -0.00037 bits. Unary doubling and doubling-plus-P gaps have mixed signs. These are descriptive finite-panel observations, not an asymptotic law.")
        y = para(fig, y, "The decoder produced 69 verified case witnesses, corresponding to 44 distinct targets across 12-16 configurations. This union is not one solver's success rate. The constant feature itself recovered seven targets at beam eight. No cost-matched advantage or novelty is established.")
        y = para(fig, y, "The expanded rational grammar finds 16 AND-only bases, correcting any extrapolation from the pilot's 48 failures. A characteristic-two invariant excludes independent invertible leg gauges for the fixed isolated AND tensor. Its scope does not cover block encodings or global ECDLP complexity.")
        y = section(fig, y, "Scope and custody")
        y = para(fig, y, "The panel contains 24 fresh ordinary curves with prime subgroup orders 139-4,001 (8, 10 and 12 bits) and 192 public targets. Six fifth-residue cases are structurally inapplicable. Private target scalars were absent from decoder and verifier inputs; separation was enforced by source interfaces, not formal operating-system isolation. Analysis is from the same session, without independent scientific review.")
        para(fig, y, "Command envelope: 121.795798 seconds. Full supervisor through output checking: 124.715335 seconds. Runtime varies with host scheduling; no wall-time solver comparison is made. Full raw records, all null arrays, controls and zero-hit cases remain available.", size=10, width=99, gap=.017)
        pdf.savefig(fig); plt.close(fig)

        fig = page(2, "Exact projection census", "Matched sign symmetry; every population state and required pair enumerated")
        y = para(fig, .865, "Primary features are x mod 7 and fifth-residue class, with x-hash-7 as a reference. Per curve, the census records H(phi(X+Y)|phi(X),phi(Y)), H(phi(2X)|phi(X)), and H(phi(2X+P)|phi(X)). Gaps subtract the mean of 99 sign-pair-matched null outcomes. The exact observed population entropies have no sampling error; the null permutations remain Monte Carlo outcomes.")
        rows = []
        for feature in ["x_mod_7", "power_residue_5", "x_hash_7"]:
            for rec in P["gap_by_feature_size"]:
                if rec["feature"] == feature:
                    vals = [f"{v[0]:+.6f}" for v in rec["gap_mean_min_max"]]
                    rows.append([LABEL[feature], str(rec["subgroup_bits"]), str(rec["curves"]), *vals])
        y = table(fig, y, ["Feature", "Bits", "n", "Pair mean", "D0 mean", "D1 mean"], rows,
                  [.24, .08, .06, .21, .21, .20], height=.030, size=9)
        y = para(fig, y, "Equal weight per applicable curve. Eight curves per size for x-mod and hash; fifth-residue has 6, 5 and 7 applicable curves respectively. Strata have four unrestricted ordinary curves and four curves forced to p = 1 mod 5 per size; ordinary curves can also satisfy that congruence. The six NAs are retained.", size=10, width=98, gap=.017)
        y = section(fig, y, "Control accounting")
        y = para(fig, y, "Full-point and constant nulls are analytic zeros. Matched Kummer relabeling only renames its image, so its null values are analytic reuse, not simulated visits. Kummer obeys pair entropy (1-1/r)^2, D0=0 and D1=(r-1)/r. All checks passed; maximum recorded-gap arithmetic discrepancy was 5.83e-16 bits.", size=10, width=98, gap=.017)
        y = para(fig, y, "Raw data retain 13,662 unrestricted and 11,286 matched outcome triples: 8,910 and 6,534 were actually measured, respectively. Every retained null length and finiteness check passed. The source labels analytic controls explicitly. Features reuse curves and labels; the table does not create independent trials.", size=10, width=98, gap=.017)
        para(fig, y, "Figure: figures/projection-entropy.svg and .pdf show means and complete curve ranges, not confidence intervals. Full size/stratum and per-curve tables are in data/projection-summary.json.", size=10, width=98, gap=.017)
        pdf.savefig(fig); plt.close(fig)

        fig = page(3, "Public-input ladder decoder", "Paired model / exact prefixes; unchanged training and target budgets")
        y = para(fig, .865, "Each applicable fixture-feature kernel uses 2,048 unlabelled subgroup samples and an independent 512-state heldout set. Four public random offsets supply terminal feature labels; the candidate score is an approximate product-of-means rule. Model prefixes propagate a fitted kernel; exact prefixes compute the public guessed-prefix point. Neither uses scalar-labelled orbit lookup or hidden intermediate traces.")
        rows = []
        for r in D["outcomes_by_configuration"]:
            rows.append([LABEL[r[0]], r[1], str(r[2]), f"{r[4]}/{r[3]}", str(r[6]), f"{r[7]:.3f}"])
        y = table(fig, y, ["Feature", "Prefix", "Beam", "Hits/cases", "Checks", "Sum B/r"], rows,
                  [.24, .12, .09, .20, .17, .18], height=.025, size=8.5)
        y = para(fig, y, "All returned candidate lists contain exactly B distinct legal scalars. For constant labels, B/r is the exact per-case probability under the ideal uniform hidden-scalar model. For target-dependent features, Sum B/r is only a candidate-count-matched uniform-guess reference. Targets are shared, and constant mode pairs give identical lists; cases are not independent trials.", size=10, width=99, gap=.017)
        y = para(fig, y, "The all-configuration union uses 54-72 candidate checks per target, and 35-60 distinct target/guess pairs (median 52.5). Its 44/192 recovered targets cannot be reported as a beam-eight method. All 2,880 recorded outcomes agree with the separately coded Jacobian verifier; recompilation and replay also matched. Positive witnesses include chance-control hits.", size=10, width=99, gap=.017)
        para(fig, y, "Figure: figures/decoder-recovery.svg and .pdf. Black ticks indicate Sum B/r per case, with the reference scope above. Full paired outcomes, all size/stratum cells and zero-hit cells are retained in data/decoder-summary.json.", size=10, width=99, gap=.017)
        pdf.savefig(fig); plt.close(fig)

        fig = page(4, "Calibration and charged work", "Fitted-kernel diagnostics do not establish true EC Markov dynamics")
        y = section(fig, .865, "One-step heldout calibration")
        rows = []
        for r in D["heldout_calibration_by_size"]:
            if r[0] != "constant":
                rows.append([LABEL[r[0]], str(r[1]), f"{r[3]:.4f}", f"{r[4]:.4f}", f"{r[8]:.4f}"])
        y = table(fig, y, ["Feature", "Bits", "Conditional loss", "Marginal loss", "Median delta"], rows,
                  [.25, .09, .23, .23, .20], height=.025, size=9)
        y = para(fig, y, "Losses are bits per transition, combining both transition bits. There was no heldout tuning. At 12 bits, fitted x-mod and hash conditional losses are slightly higher than their marginal references. Some rare feature rows have zero training counts and receive Laplace smoothing. Worst-row Dobrushin coefficients concern the fitted kernels only; they do not bound true EC memory or scalar concentration.", size=10, width=99, gap=.017)
        y = section(fig, y, "Work for the entire tested matrix")
        rows = []
        stage_keys = [("Training once", "training_construction_once"), ("Heldout once", "heldout_calibration_once"),
                      ("Views once", "shared_views_once"), ("All inference", "all_tested_inference_and_verification"),
                      ("Whole study", "whole_decoder_study_total")]
        for label, key in stage_keys:
            v = D["costs"][key]
            rows.append([label, f"{v['group_additions']:,}", f"{v['scalar_multiplications']:,}", f"{v['field_multiplications']:,}"])
        y = table(fig, y, ["Stage", "Group-add calls", "Scalar-mul calls", "Field multiplies"], rows,
                  [.24, .25, .25, .26], height=.030, size=9)
        y = para(fig, y, "The whole-study total also includes 24 shared fixture validations. Charge 90 trained kernels, 90 calibrations and 720 feature/target view setups (2,880 offsets) once each. All inference cases together use 37,544,384 DP terms and 12,960 candidate checks. Reused setup is not counted repeatedly across paired modes or widths.", size=10, width=99, gap=.017)
        y = para(fig, y, "These are instrumented call and step counts, not CPU cycles or a cold/warm solver bound. Scalar multiplication invokes group additions; do not add those counts as disjoint primitive work. The study has no matched optimized rho run, so no speedup conclusion follows. The full counter breakdown and per-configuration costs are in data/decoder-summary.json.", size=10, width=99, gap=.017)
        pdf.savefig(fig); plt.close(fig)

        fig = page(5, "What the local audit excludes", "Fixed isolated AND tensor; exact rational grammar and characteristic-two certificate")
        y = para(fig, .865, "This is one global 504-row basis audit, not 504 independent curve experiments. The rational search expands matrix entries to [-2,2] and filters for invertibility. All tensor coefficients and basis transformations are exact.")
        y = table(fig, y, ["Declared rational grammar", "Count"], [
            ["All matrices before filtering", "625"], ["Invertible matrices", "496"],
            ["AND-only parity-pure survivors", "16"], ["Preserve both independent pins", "32"],
            ["AND and both-pin survivors", "0"]], [.78, .22], height=.036)
        y = para(fig, y, "The rational matrix [[1,2],[1,0]] is a positive control: it makes AND even parity, but fails a pin. Thus the earlier pilot's 48 AND failures were a bounded-grammar result. They were not a universal rational-basis impossibility. Preserving both isolated pins in a common GL2 field basis forces monomial structure, leaving AND mixed.")
        y = section(fig, y, "Characteristic-two invariant")
        y = para(fig, y, "For an arity-three tensor f over a commutative ring of characteristic two, define B(f) = f000*f111 + f001*f110 + f010*f101 + f011*f100. Under independent invertible leg matrices A,C,D, the identity is B((A tensor C tensor D)f) = det(A)*det(C)*det(D)*B(f). Fixed AND has B=1; every parity-pure arity-three tensor has B=0. Unit determinants therefore exclude this fixed isolated interface.")
        y = para(fig, y, "The serialized polynomial certificate has 20 indeterminates, equal 32-term degree-eight expressions and an empty residual. It uses ordinary polynomial exponents; no x^2=x reduction. Regression checks include all six uniform invertible F2 bases, 216 independent F2 triples and 96 single-tag-ring uniform bases. Calibration and mutation controls passed.")
        y = section(fig, y, "Boundary of the conclusion")
        y = para(fig, y, "The invariant does not cover block regrouping, internal variable elimination or pin absorption, sums of parity tensors, alternate Boolean encodings, or a changed global construction. A sum-of-two-parity control explicitly survives outside the single-tensor requirement. No ECDLP lower bound or closure of the research goal follows. The certificate is not proof-assistant checked.")
        pdf.savefig(fig); plt.close(fig)

        fig = page(6, "Mathematical follow-up and limits", "Data-free reasoning after the frozen run; no decoder retuning or new trials")
        y = section(fig, .865, "Fifth-character single-step bound")
        y = para(fig, y, "For p>3, p=1 mod5 and subgroup H=[h]E(Fp), with p not dividing h, a divisor witness proves that x(X)^a*x(2X+bP)^c is not a geometric fifth power for any nonzero character exponent pair. Etale pullback by [h] preserves a witness valuation. Five Kummer twists, tame Riemann-Hurwitz and Hasse-Weil give a deliberately coarse moment bound.")
        y = para(fig, y, "Write N = #E(Fp), q = Pr[both coordinates finite and nonzero], and Gamma = (60*h^2+2)*sqrt(p) + 75*h^2. Set eta = min(1,Gamma/(N*q)). Conditioned on the good event, each nontrivial fifth-character moment has magnitude at most eta, and log2(5)-H(V|U,good) <= 24*eta^2/ln(2). For bounded h and q bounded away from zero, the conditional deficit is O(1/p).", size=10.5, width=90, gap=.018)
        y = para(fig, y, "The full feature includes identity and zero symbols. Their total exceptional mass is at most 15/r, and needs a separate binary-entropy correction. The explicit constants can be vacuous at these toy sizes. This bound concerns a single unary transition: it is not the pair-addition statistic, the full-alphabet worst-row contraction, or ECDLP security.")
        y = section(fig, y, "A fixed-signature budget ceiling")
        y = para(fig, y, "Condition on public training and seeds independent of uniform hidden k. If Q affects candidate selection only through m terminal labels from an alphabet of size d, and the procedure proposes at most B guesses per signature, success is at most min(1,B*d^m/r). Public guessed-prefix points do not add Q-dependent information. The present d<=8, m=4, B=8 bound is 32768/r and is vacuous here, but rules out constant success at fixed parameters as r grows.")
        y = para(fig, y, "This conditional ceiling applies to each stated configuration, not a pooled union with a larger budget. Growing m,d,B or allowing richer Q-dependent observations escapes it. It is not an ECDLP lower bound, and assumes ideal uniform target sampling rather than conditioning on a deterministic private PRNG seed.")
        y = section(fig, y, "Prior art and unresolved construction")
        y = para(fig, y, "The repository already contains a lossy double-and-add belief-propagation lead. HMM and beam-search decoding have prior cryptanalytic use, often with side-channel traces. This candidate receives only public points and no such traces. Neither the architecture nor this follow-up has established novelty. The central EC-specific constructive cancellation identity remains missing.")
        y = para(fig, y, "The frozen matrix is complete, not an exhaustion of the mathematical leads. More training alone cannot escape the fixed-signature interface. Block grouping, internal elimination and sums can escape the isolated-AND obstruction. No proposed construction yet gives a cheap EC-specific rule with full-cost advantage over a strong rho baseline.", size=10, width=99, gap=.017)
        pdf.savefig(fig); plt.close(fig)

        fig = page(7, "Execution, evidence and reproduction", "Actual timestamps and unchanged sealed records")
        y = table(fig, .865, ["Stage", "UTC start", "UTC finish", "Wall (s)"], [
            [m["name"].replace("projection_scale_", "projection "),
             m["measurement"]["started_utc"][11:23], m["measurement"]["finished_utc"][11:23],
             f"{m['measurement']['wall_seconds']:.6f}"] for m in R["module_execution"]],
             [.30, .23, .23, .24], height=.035, size=9)
        y = para(fig, y, "Builds and self-tests run sequentially before the three-worker pool. All three projection shards start near 06:51:33 UTC. Decoder and basis work begin as projection workers free up, so measurement intervals overlap. Source byte hashes, arguments, binaries, start/finish times and exit statuses are in raw-result.json. No worker failed or hit its watchdog.")
        y = section(fig, y, "Custody")
        y = para(fig, y, "All 348 declared run artifacts remain byte-for-byte sealed. The execution receipt binds 347 other artifacts; the 288 producer/verifier partition slots reconstruct each logical stream with its original SHA-256. Five producer streams contain 3,624 rows. Unused declared slots are empty. Raw null arrays, NAs and unsuccessful decoder candidates remain present.")
        y = para(fig, y, "The public witness verifier is a separate Jacobian arithmetic implementation. Every recorded candidate was checked against [k]P=Q, followed by independent recompilation/replay of that implementation. This is arithmetic implementation diversity, not an independent scientific review session. The run certificate is explicitly per-instance and toy; attack_advantage_claimed is false.")
        y = section(fig, y, "Frozen provenance")
        y = para(fig, y, "Source authority: f0ac7434a55fba113e7f81d3e1c8c0f62e47bbc9. Verified archive receipt commit: 3e6ca92887e07e4d9a1710eddd8c450e70fc86fa (349 paths, including the receipt). Full plan/source digests are in the run receipts; raw evidence is at ../../runs/RUN-ECDLP-0b7dd5/. Committed target labels and seeds are revealed separately after sealing; they were not candidate inputs.", size=10, width=98, gap=.017)
        y = section(fig, y, "Reproduce this report")
        y = para(fig, y, "Run ./build.sh with Python, numpy and matplotlib available. It reads only the three JSON summaries in data/ and regenerates report.pdf plus four editable SVG/PDF chart pairs. This command performs no EC experiments and changes no sealed run output. Observations.md links all detailed tables; HEADER.md records report provenance and the actual archival binding once available.", size=10, width=98, gap=.017)
        pdf.savefig(fig); plt.close(fig)


def main():
    for name, builder in [("projection-entropy", projection_fig), ("decoder-recovery", decoder_fig),
                          ("calibration", calibration_fig), ("execution-timeline", timeline_fig)]:
        fig = builder(); save(fig, name); plt.close(fig)
    build_report()
    for p in [HERE / "report.pdf", *FIGURES.glob("*.pdf")]:
        if p.stat().st_size > 65536:
            raise RuntimeError(f"PDF exceeds canonical 64 KiB data policy: {p} ({p.stat().st_size})")
    print("Rebuilt four SVG/PDF chart pairs and seven-page report; all PDFs <=64 KiB.")


if __name__ == "__main__":
    main()
