#set page(paper: "a4", margin: 1.6cm, numbering: "1")
#set text(font: "New Computer Modern", size: 9.5pt)
#set heading(numbering: "1.")
#show table: set text(size: 7.5pt)

= Run report: EXP-ECDLP-f49f75 (runs RUN-ECDLP-f49f75-01, -02, -03)

*Observations only.* This report records what ran and what was measured. It contains no verdict, support or weaken language: that belongs to the evidence review (`reports/review-DEC-20261015-a08389/`).

- *Experiment* EXP-ECDLP-f49f75 · *hypothesis* H-ECDLP-60de36 · *question* RQ-ECDLP-001 · *goal* GOAL-ECDLP-001
- *Launcher* `pkm_isogeny_fb.py`; *frozen plan* `trial-plan.json`; *amendments* AMD-01 (resume after host limit), AMD-02 (launcher int-overflow fix; invalidates RUN-01 m=2, L≥8 Gröbner cells, re-run as RUN-03).
- *Host* 4 vCPU, 15 GB, Linux 6.18, Python 3.13.16, Singular 4.3.2; 4 worker processes, one Singular process per solve.

== Runs

#table(columns: 6, stroke: 0.4pt,
[*run*],[*cells*],[*started (UTC)*],[*finished*],[*git HEAD*],[*end*],
[RUN-01],[m=2, L=3..11 (L≥8 Gröbner excluded, AMD-02)],[2026-10-15 04:59],[06:59],[378abed375],[killed by 7200 s host limit in m=2 L=12 (no rows)],
[RUN-02],[m=3, L=3..5],[06:59],[09:00],[b9ddeefe78],[killed by host limit in m=3 L=6 (no rows)],
[RUN-03],[m=2, L=8..11],[09:00],[10:21],[41a38de6c4],[exit 0],
)

Command (RUN-03): `python3 experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py --plan experiments/EXP-ECDLP-f49f75/amendments/trial-plan-run03.json --out …/RUN-ECDLP-f49f75-03/raw-result.jsonl --workers 4`. Seeds: sha256 of `EXP-ECDLP-f49f75/v1|m|L|instance`. Per cell: 4 planted + 2 random targets. Timeout 600 s per Singular process. All working trees were clean at launch except the run directory being written.

== Arms and controls

A: factor-base x-set $V = x(R + ⟨K⟩)$, $|V| = 2^L$, encoded by $L$ chained Vélu 2-isogeny equations per point ($m L$ variables). B: the same $V$ by its degree-$2^L$ minimal polynomial ($m$ variables). C: a uniformly random $2^L$-set, dense. E: meet-in-the-middle enumeration over $plus.minus$FB (counted group operations). Solvers: Singular `std` and `slimgb` (each followed by `std` and `fglm` to lex). Positive control: the planted decomposition must lie in the computed variety.

#figure(image("cost-vs-L.svg", width: 100%), caption: [Median time per decomposition (Gröbner: std+fglm ms; E: Python wall, below 0.1 ms resolution shown at floor) against $L$; bars min–max over $n = 6$ instances (5 where a planted target was degenerate). × marks cells where every instance hit the 600 s timeout. Measured; RUN-01 (m=2, L≤7), RUN-03 (m=2, L≥8), RUN-02 (m=3).])

== Per-cell measurements

Columns: completed/timeout/degenerate-target counts; Gröbner median total ms [min–max] (measured) or enumeration median group ops and median factor-base size; planted-in-variety (passed/checked); max degree in reduced basis; max Singular memory(2) MiB.

#table(columns: 10, stroke: 0.3pt,
[*m*],[*L*],[*p bits*],[*run*],[*arm*],[*ok/to/deg*],[*median ms [min–max] or ops*],[*planted*],[*maxdeg*],[*MiB*],
[2],[3],[7],[R01],[A],[5/0/1],[2 [1–2]],[3/3],[2],[2],
[2],[3],[7],[R01],[A:slimgb],[5/0/0],[1 [1–2]],[3/3],[2],[2],
[2],[3],[7],[R01],[B],[5/0/1],[0 [0–1]],[3/3],[4],[2],
[2],[3],[7],[R01],[B:slimgb],[5/0/0],[1 [0–1]],[3/3],[4],[2],
[2],[3],[7],[R01],[C],[5/0/1],[0 [0–1]],[3/3],[3],[2],
[2],[3],[7],[R01],[C:slimgb],[5/0/0],[0 [0–1]],[3/3],[3],[2],
[2],[3],[7],[R01],[E],[5/0/1],[8 ops / FB 4],[—],[—],[—],
[2],[4],[9],[R01],[A],[6/0/0],[9.5 [9–15]],[4/4],[2],[2],
[2],[4],[9],[R01],[A:slimgb],[6/0/0],[5.5 [5–6]],[4/4],[2],[2],
[2],[4],[9],[R01],[B],[6/0/0],[1 [1–1]],[4/4],[3],[2],
[2],[4],[9],[R01],[B:slimgb],[6/0/0],[1 [1–1]],[4/4],[3],[2],
[2],[4],[9],[R01],[C],[5/0/1],[1 [1–1]],[3/3],[3],[2],
[2],[4],[9],[R01],[C:slimgb],[5/0/0],[1 [1–1]],[3/3],[3],[2],
[2],[4],[9],[R01],[E],[6/0/0],[17 ops / FB 8.5],[—],[—],[—],
[2],[5],[11],[R01],[A],[6/0/0],[68.5 [65–78]],[4/4],[2],[2],
[2],[5],[11],[R01],[A:slimgb],[6/0/0],[26.5 [26–30]],[4/4],[2],[2],
[2],[5],[11],[R01],[B],[6/0/0],[2 [2–2]],[4/4],[3],[2],
[2],[5],[11],[R01],[B:slimgb],[6/0/0],[4 [4–4]],[4/4],[3],[2],
[2],[5],[11],[R01],[C],[6/0/0],[2 [2–2]],[4/4],[3],[2],
[2],[5],[11],[R01],[C:slimgb],[6/0/0],[4 [4–4]],[4/4],[3],[2],
[2],[5],[11],[R01],[E],[6/0/0],[27 ops / FB 13.5],[—],[—],[—],
[2],[6],[13],[R01],[A],[6/0/0],[774 [706–802]],[4/4],[2],[4],
[2],[6],[13],[R01],[A:slimgb],[6/0/0],[229.5 [223–240]],[4/4],[2],[11],
[2],[6],[13],[R01],[B],[6/0/0],[7.5 [7–8]],[4/4],[3],[2],
[2],[6],[13],[R01],[B:slimgb],[6/0/0],[17.5 [17–19]],[4/4],[3],[2],
[2],[6],[13],[R01],[C],[6/0/0],[7 [7–8]],[4/4],[2],[2],
[2],[6],[13],[R01],[C:slimgb],[6/0/0],[17 [17–18]],[4/4],[2],[2],
[2],[6],[13],[R01],[E],[6/0/0],[65 ops / FB 32.5],[—],[—],[—],
[2],[7],[15],[R01],[A],[6/0/0],[13,344 [12,193–13,819]],[4/4],[2],[17],
[2],[7],[15],[R01],[A:slimgb],[6/0/0],[3,138.5 [2,547–3,796]],[4/4],[2],[58],
[2],[7],[15],[R01],[B],[6/0/0],[46.5 [35–71]],[4/4],[4],[4],
[2],[7],[15],[R01],[B:slimgb],[6/0/0],[95.5 [92–200]],[4/4],[4],[6],
[2],[7],[15],[R01],[C],[6/0/0],[36.5 [34–58]],[4/4],[5],[4],
[2],[7],[15],[R01],[C:slimgb],[6/0/0],[99.5 [92–120]],[4/4],[5],[6],
[2],[7],[15],[R01],[E],[6/0/0],[124 ops / FB 62],[—],[—],[—],
[2],[8],[17],[R03],[A],[6/0/0],[153,435 [144,479–158,329]],[4/4],[2],[59],
[2],[8],[17],[R03],[A:slimgb],[6/0/0],[77,357 [71,380–78,300]],[4/4],[2],[90],
[2],[8],[17],[R03],[B],[6/0/0],[234.5 [228–250]],[4/4],[3],[14],
[2],[8],[17],[R03],[B:slimgb],[6/0/0],[529.5 [480–697]],[4/4],[3],[16],
[2],[8],[17],[R03],[C],[6/0/0],[225.5 [215–284]],[4/4],[2],[14],
[2],[8],[17],[R03],[C:slimgb],[6/0/0],[549.5 [496–568]],[4/4],[2],[16],
[2],[8],[17],[R03],[E],[6/0/0],[273 ops / FB 136.5],[—],[—],[—],
[2],[9],[19],[R03],[A],[0/6/0],[—],[—],[—],[—],
[2],[9],[19],[R03],[A:slimgb],[0/6/0],[—],[—],[—],[—],
[2],[9],[19],[R03],[B],[6/0/0],[1,743 [1,596–1,820]],[4/4],[3],[50],
[2],[9],[19],[R03],[B:slimgb],[6/0/0],[3,855 [3,646–4,341]],[4/4],[3],[64],
[2],[9],[19],[R03],[C],[6/0/0],[1,678 [1,530–2,067]],[4/4],[3],[50],
[2],[9],[19],[R03],[C:slimgb],[6/0/0],[3,658.5 [3,494–3,894]],[4/4],[3],[64],
[2],[9],[19],[R03],[E],[6/0/0],[514 ops / FB 257],[—],[—],[—],
[2],[10],[21],[R03],[B],[6/0/0],[13,604.5 [12,681–14,261]],[4/4],[3],[196],
[2],[10],[21],[R03],[B:slimgb],[6/0/0],[34,144.5 [32,964–34,620]],[4/4],[3],[255],
[2],[10],[21],[R03],[C],[6/0/0],[12,801.5 [12,660–13,429]],[4/4],[4],[196],
[2],[10],[21],[R03],[C:slimgb],[6/0/0],[34,614.5 [33,650–35,094]],[4/4],[4],[255],
[2],[10],[21],[R03],[E],[6/0/0],[1,045 ops / FB 522.5],[—],[—],[—],
[2],[11],[23],[R03],[B],[6/0/0],[107,962.5 [101,522–110,205]],[4/4],[3],[783],
[2],[11],[23],[R03],[B:slimgb],[6/0/0],[353,720.5 [345,233–355,022]],[4/4],[3],[1013],
[2],[11],[23],[R03],[C],[6/0/0],[99,491 [98,921–99,982]],[4/4],[3],[783],
[2],[11],[23],[R03],[C:slimgb],[6/0/0],[345,917.5 [338,619–351,202]],[4/4],[3],[1013],
[2],[11],[23],[R03],[E],[6/0/0],[2,028 ops / FB 1,014],[—],[—],[—],
[3],[3],[10],[R02],[A],[6/0/0],[437.5 [390–535]],[4/4],[3],[8],
[3],[3],[10],[R02],[A:slimgb],[6/0/0],[635.5 [601–729]],[4/4],[3],[29],
[3],[3],[10],[R02],[B],[6/0/0],[78.5 [75–102]],[4/4],[8],[4],
[3],[3],[10],[R02],[B:slimgb],[6/0/0],[35.5 [32–44]],[4/4],[8],[4],
[3],[3],[10],[R02],[C],[6/0/0],[84 [78–92]],[4/4],[3],[4],
[3],[3],[10],[R02],[C:slimgb],[6/0/0],[37 [31–40]],[4/4],[3],[4],
[3],[3],[10],[R02],[E],[6/0/0],[54.5 ops / FB 4.5],[—],[—],[—],
[3],[4],[13],[R02],[A],[6/0/0],[176,155 [168,125–179,709]],[4/4],[2],[235],
[3],[4],[13],[R02],[A:slimgb],[6/0/0],[48,804 [45,650–50,569]],[4/4],[2],[746],
[3],[4],[13],[R02],[B],[6/0/0],[5,049 [4,703–5,363]],[4/4],[3],[40],
[3],[4],[13],[R02],[B:slimgb],[6/0/0],[1,439.5 [1,337–1,515]],[4/4],[3],[39],
[3],[4],[13],[R02],[C],[6/0/0],[4,882.5 [4,783–5,088]],[4/4],[16],[40],
[3],[4],[13],[R02],[C:slimgb],[6/0/0],[1,548.5 [1,332–1,631]],[4/4],[16],[39],
[3],[4],[13],[R02],[E],[6/0/0],[152 ops / FB 8],[—],[—],[—],
[3],[5],[16],[R02],[A],[0/6/0],[—],[—],[—],[—],
[3],[5],[16],[R02],[A:slimgb],[0/6/0],[—],[—],[—],[—],
[3],[5],[16],[R02],[B],[6/0/0],[344,179.5 [333,653–348,474]],[4/4],[3],[615],
[3],[5],[16],[R02],[B:slimgb],[6/0/0],[70,800.5 [67,665–72,581]],[4/4],[3],[459],
[3],[5],[16],[R02],[C],[6/0/0],[337,273.5 [334,025–339,216]],[4/4],[4],[615],
[3],[5],[16],[R02],[C:slimgb],[6/0/0],[73,460.5 [65,149–76,113]],[4/4],[4],[459],
[3],[5],[16],[R02],[E],[6/0/0],[629 ops / FB 17],[—],[—],[—]
)

== Operational notes (facts, not findings)

- 24 RUN-01 rows (m=2, L=8..11) are excluded under AMD-02: their Singular input evaluated $x(T)^2$ in 32-bit integer arithmetic for $p > 46340$; the planted control fell to 2/4, 1/4, 0/4, 0/4 there. RUN-03 re-ran these cells with the fixed launcher; every planted check passed.
- RUN-02 workers were forked before the AMD-02 launcher fix and therefore ran launcher commit b9ddeefe78; the m=3 input never squares a bare integer and all its planted checks passed.
- Four AMD-02 fix-verification solves (07:15–07:20 UTC) shared the host with RUN-02's m=3, L=3 cell; its timings may be inflated.
- Degenerate targets (planted sum = point at infinity): 1 per affected cell, recorded as such.
- Arm A retired by the frozen stopping rule at m=2, L=9 and at m=3, L=5. m=2, L=12 and m=3, L=6 were not executed (host limit; AMD-01).
