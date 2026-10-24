#!/usr/bin/env python3
"""Render a source-linked addendum from recorded counts and the blind review.

This performs no scientific trial or root extraction. Use a fresh copy of this
directory for a rendering replay; source and report outputs are write-once.
"""
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
if len(sys.argv)>1:
    sys.path.insert(0,sys.argv[1])
os.environ.setdefault("MPLCONFIGDIR","/tmp/joint-smallroot-review-matplotlib")


def save(path,text):
    with path.open("x") as stream:
        stream.write(text)


review=STUDY/"independent-review.md"
digest=hashlib.sha256(review.read_bytes()).hexdigest()
counts=json.loads((STUDY/"artifacts/finite-audit.json").read_text())
single=counts["single_s3"][0]
joint=counts["joint_union_support"][0]
assert (single["dimension"],single["row_modulus_exponent"],single["budget"]) == (13,12,1)
comparison={
    "review_task":"TASK-20261024-da3810",
    "review_source_sha256":digest,
    "independently_derived_formula":"K = t*N - q",
    "independently_checked_single_s3":{"t":1,"N":13,"q":12,"K":1,
        "coordinate_exponents":[11,11,11],"determinant":"101^12 * 2^33"},
    "parent_comparison":{
        "historical_jm_rhs":12,"independently_derived_rhs":1,
        "successor_rhs":single["budget"],
        "single_equal_beta":str(Fraction(1,33)),
        "scope":"One exact matching fixture; review derived the identity blind, parent compared to producer source/results"},
    "reviewer_assessed_producer_implementation":False,
    "reviewer_certified_joint_candidate_counts":False,
    "reviewer_certified_optimized_shifts":False,
    "root_extraction_certified":False,
    "pipeline_improvement_demonstrated":False,
    "scientific_state_transition":False,
}
save(HERE/"comparison.json",json.dumps(comparison,indent=2)+"\n")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(8,3.4))
labels=["Single S3 fixture\nindependently derived", "Joint candidate\nproducer counts only"]
for offset,key,label,color in [(-.23,"divisibility_exponent","Target tN","#566b87"),
                              (0,"row_modulus_exponent","Modulus exponent q","#c08c54"),
                              (.23,"budget","Available budget tN-q","#146b68")]:
    values=[r[key] for r in (single,joint)]
    ax.bar([i+offset for i in range(2)],values,width=.23,label=label,color=color)
    for i,value in enumerate(values):
        ax.text(i+offset,value+.5,str(value),ha="center",fontsize=9)
ax.set_xticks(range(2),labels)
ax.set_ylabel("Exponent of p in determinant accounting")
ax.set_ylim(0,36)
ax.set_title("Finite t=1 accounting: distinct provenance for the two fixtures")
ax.legend(loc="upper left",fontsize=8)
fig.tight_layout()
svg=HERE/"accounting.svg"
fig.savefig(svg)
svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
plt.close(fig)

save(HERE/"report.md",f"""# Publication and independent-derivation addendum

2026-10-24. Archival task TASK-20261024-6c911a. This is a scoped software/math
audit addendum, not an ECDLP experiment or a scientific-state transition.

The prepared branch is published in [PR #2547](https://github.com/aburan28/crypto-autoresearcher/pull/2547).
The user explicitly authorized publication after the initial automatic-review
refusal. Hosted CI was queued at the latest inspection. Auto-merge was separately
refused because publication authorization did not cover a future merge into main.

## Independent mathematical result

[TASK-20261024-da3810's report](../independent-review.md), SHA-256 `{digest}`,
derives K=tN-q from the specified row divisibility and triangular determinant,
including the LLL/norm correction. It derives the full-box limiting equal-beta
statistic 2/[n*d*(n+1)] and independently reconstructs the exact sparse S3
determinant 101^12 * 2^33 using standard-library polynomial arithmetic and
fraction-free Bareiss elimination.

The reviewer saw only the four committed input/role files, plus disclosed
environment-runtime guidance and metadata. It read no producer implementation,
results, tests, closure note or sibling review. A runtime-path deviation was
disclosed. The report's verdict on calculator compatibility is explicitly
inconclusive because that implementation was deliberately unseen. No backend
probe or scientific-state promotion is claimed.

## Parent comparison

For the matching t=1 fixture the historical calculator returns q=12 as its RHS.
The independent derivation requires tN-q=13-12=1; the successor reports 1.
This parent comparison identifies the finite accounting discrepancy. It does
not turn the blind review into an independent audit of every implementation
path or a guarantee that the joint candidate extracts roots.

![Exact finite accounting and provenance](accounting.svg)

All plotted values are exact recorded counts from the original finite-audit.json,
one deterministic fixture per column group, with no sampling uncertainty. The
joint counts remain producer/test artifacts; the reviewer derived the conditional
joint determinant identity but did not inspect or certify that candidate.

## Remaining scope

The original report and artifacts remain unchanged. Twenty-three software tests
and the deterministic replay were already recorded there. This addendum adds an
independent derivation, not new solver performance measurements. The proposed
optimal shift construction, weighted-bound normalization, higher-rank GAPs,
root-extraction success/cost, random-target relation rank/yield and matched
complete IC comparison remain open. No verified IC improvement is established.

See [comparison.json](comparison.json) for the scoped composition, the original
[report](../report.md), and the [named problem](../../../problems/joint-smallroot-reach-baseline-and-oracle-unverified.md).
""")

save(HERE/"report.typ","""#set page(paper: "a4", margin: 20mm)
#set text(size: 10pt)
= Independent derivation and publication update
2026-10-24. TASK-20261024-da3810; archive TASK-20261024-6c911a.
This is a scoped mathematical/software audit, not an ECDLP experiment.

== Independent result
The blind reviewer derives K = t N - q, with LLL and evaluation-norm losses
explicitly separated. The full-box limiting equal-beta determinant statistic
is 2 divided by n d (n+1). Independently expanded S3 and exact Bareiss
elimination reproduce the determinant 101 to the power 12 times 2 to the power
33 on the assigned 13-column fixture.

The reviewer read four committed input/role files, plus disclosed environment
guidance and metadata. No producer code, result, tests or sibling report was
read. The report discloses its runtime-path deviation and absent model probe.
It returns inconclusive on compatibility with the unseen implementation.

== Parent comparison and provenance
For the matching fixture N=13, q=12 and t=1. The historical RHS is 12;
the independently derived available budget is 1, which the successor reports.
This is a finite arithmetic/software comparison, not an optimized joint reach
bound or a working decomposition oracle.

#image("accounting.svg", width: 100%)

Exact recorded counts, one deterministic fixture per group. The joint candidate
counts are producer artifacts, not independently reviewed measurements.

== Publication and remaining work
PR #2547 publishes the prepared branch after the user's explicit authorization.
CI remains queued. Auto-merge was separately refused as outside publication
authorization; the PR remains open. No alternative merge route was attempted.

The original report and raw artifacts are preserved. The 23 passing software
tests and exact same-source replay are separate from this blind derivation.
No scientific state, hypothesis or leaderboard status is changed. Optimized
shifts, weighted-bound normalization, higher-rank GAPs, verified root extraction,
random-target relation rank/yield and matched full IC measurements remain open.
No verified IC improvement is established.

Full source: ../independent-review.md. Exact composition and source digest:
comparison.json. Context and evidence links: report.md and ../report.md.
""")
import typst
typst.compile(str(HERE/"report.typ"),output=str(HERE/"report.pdf"))
print("Rendered scoped independent-review addendum.")
