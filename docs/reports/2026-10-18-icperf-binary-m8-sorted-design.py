"""Rebuild the binary m8 design SVG and a Typst input for its PDF.

No scientific trial, solver call, or performance metric is run here.
Usage: python3 docs/reports/2026-10-18-icperf-binary-m8-sorted-design.py
Then: typst compile /private/tmp/icperf-binary-m8-sorted-design.typ \
  docs/reports/2026-10-18-icperf-binary-m8-sorted-design.pdf
Inspect the rendered PDF before archival custody is recorded.
"""

from pathlib import Path

HERE = Path(__file__).resolve().parent
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 565" role="img" aria-labelledby="title desc">
<title id="title">Ordinary-binary m8 sorted-summand successor gates</title>
<desc id="desc">Reviewed censored pilot feeds two prospective gates: exact gamma blind replay and sorted-summand input checks. A dashed conjectural edge connects sorted encoding to solver cost. No end-to-end result is shown.</desc>
<style>text{font-family:Arial,Helvetica,sans-serif;fill:#17233b}.head{font-size:25px;font-weight:700}.small{font-size:15px}.boxhead{font-size:18px;font-weight:700}.caption{font-size:14px}.blue{fill:#e8f1ff;stroke:#3971b5}.amber{fill:#fff4d8;stroke:#b48620}.pale{fill:#f1f3f7;stroke:#66748b}.red{fill:#fff0f0;stroke:#b84747}.edge{fill:none;stroke:#445a78;stroke-width:2.5;marker-end:url(#arrow)}.hyp{fill:none;stroke:#b84747;stroke-width:2.5;stroke-dasharray:8 6;marker-end:url(#arrow)}</style>
<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L9,5 L0,10" fill="none" stroke="#445a78" stroke-width="1.5"/></marker></defs>
<text x="34" y="43" class="head">Binary m=8: admission and solver instrument gates</text>
<text x="34" y="72" class="small">One GF(2^61) curve · prime r=576460752557211763 · two target-blind B=316 bases</text>
<rect x="34" y="111" width="270" height="116" rx="12" class="blue" stroke-width="2"/>
<text x="51" y="141" class="boxhead">Reviewed predecessor</text>
<text x="51" y="169" class="small">2 planted calls: 300 s censored</text>
<text x="51" y="193" class="small">64 natural calls: gated</text>
<text x="51" y="213" class="caption">EXP-ICPERF-018b0c / EV-54ac6b</text>
<rect x="361" y="104" width="265" height="129" rx="12" class="amber" stroke-width="2"/>
<text x="379" y="134" class="boxhead">Gamma-bound blind gate</text>
<text x="379" y="161" class="small">gamma = b^(1/4) = x([r]P)</text>
<text x="379" y="185" class="small">8 targets, 32 raw channels</text>
<text x="379" y="209" class="caption">independent replay pending</text>
<path d="M304 169 H352" class="edge"/>
<rect x="674" y="104" width="252" height="129" rx="12" class="amber" stroke-width="2"/>
<text x="691" y="134" class="boxhead">Sorted input checks</text>
<text x="691" y="160" class="small">t0 ≤ ... ≤ t7</text>
<text x="691" y="185" class="small">re-chain full signed points</text>
<text x="691" y="209" class="caption">CNF/XOR/point checks pending</text>
<path d="M626 169 H664" class="edge"/>
<rect x="361" y="293" width="265" height="107" rx="12" class="pale" stroke-width="2"/>
<text x="379" y="322" class="boxhead">Six-call U/S/U panel</text>
<text x="379" y="349" class="small">1200 s cap per call</text>
<text x="379" y="374" class="small">unsorted repeat = A/A spread</text>
<path d="M800 233 V275 H625" class="hyp"/>
<text x="700" y="260" class="caption" fill="#b84747">cost effect conjectural</text>
<path d="M494 233 V282" class="edge"/>
<rect x="34" y="466" width="892" height="64" rx="10" class="pale" stroke-width="1.5"/>
<text x="51" y="492" class="small">After positive certification: separately frozen natural panel and full cold-cost accounting</text>
<text x="51" y="516" class="small">No new natural yield, degree of regularity, rank, E2E S, or matched-rho result in this design.</text>
<text x="36" y="554" class="caption">Blue = reviewed observation · amber = open finite gate · dashed red = hypothesis · gray = future work</text>
</svg>
"""

TYPST = r'''#set page(paper: "us-letter", margin: 0.8in)
#set text(font: "Arial", size: 10pt)
= Gamma-bound binary m8 successor: sorted summands

*Design record, 2026-10-18.* EXP-ICPERF-554db4 is review_required; no scientific solver call is authorized.

The predecessor's two planted solver calls each reached their 300-second wall cap. Its 64 natural calls did not start. The successor first binds gamma as the unique fourth root of b=31 in GF(2^61), numeric 70364449406991, and requires an independent blind derivation of eight targets and 32 raw channels before comparison with archived manifests.

The proposed solver representation sorts eight 11-bit summand coordinates and re-chains six intermediate full-point sums. Group commutativity preserves a certified point relation under permutation, but finite XCNF fidelity and any runtime effect remain unverified. Two B=316 bases each receive an unsorted/sorted/unsorted planted-positive schedule. The identical unsorted repeat supplies an A/A timing spread. Every call has a 1200-second and sampled-8-GiB guard; six calls are the prospective maximum.

#image("__SVG_PATH__", width: 100%)

The sorted-to-cost edge is conjectural. The two planted targets differ, so no cross-base yield comparison is valid. Input and implementation controls, independent blind review, a complete preapproval packet, a new approval decision and normal run admission remain open. Natural relation yield, useful rank, degree of regularity, linear algebra, target work, complete end-to-end cost and matched rho are unmeasured by this design.

Sources: EXP-ICPERF-018b0c; RUN-ICPERF-712e85; EV-ICPERF-54ac6b; DEC-20261017-3b87bf; problems/icperf-k11-gamma-admission-unbound.md. Provenance: internal for archived observations, derived for the point-sum permutation argument. The complete mechanism and controls are in the accompanying Markdown report and prospective specification.
'''


def main() -> None:
    (HERE / "2026-10-18-icperf-binary-m8-sorted-design.svg").write_text(SVG)
    svg_path = HERE / "2026-10-18-icperf-binary-m8-sorted-design.svg"
    Path("/private/tmp/icperf-binary-m8-sorted-design.typ").write_text(
        TYPST.replace("__SVG_PATH__", svg_path.as_posix())
    )


if __name__ == "__main__":
    main()
