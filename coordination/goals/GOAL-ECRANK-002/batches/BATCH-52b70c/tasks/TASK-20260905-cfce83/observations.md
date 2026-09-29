# TASK-20260905-cfce83 — OBSERVATIONS (EXECUTOR, OBSERVATIONS ONLY)

GOAL-ECRANK-002 / BATCH-52b70c / N1 of DEC-20260822-7d356e.
Executed 2026-09-05 ~22:52–22:58 UTC. Network permission: DEC-20260905-9e5bfa
(recorded on the handoff). This file contains **observations only**: no rank
assertion, no C1 ruling, no statement about anyone's rank.

## 1. What was fetched (11 files, every byte archived unedited in `fetched/`, see `fetched_manifest.json`)

Primary targets located and archived:

- **ICARM leaderboard curve #302 entry** — `https://elliptic-rank.icarm.cloud/curve/302`
  (HTML, 10,096 B, HTTP 200) and its machine-readable record
  `https://elliptic-rank.icarm.cloud/curve/302.json` (5,486 B, HTTP 200).
  The leaderboard is the "Elliptic Curve Rank Leaderboard" maintained by the
  NSF Institute for Computer-Aided Reasoning in Mathematics (ICARM); its stated
  scope (verbatim from the page footer/index): "A leaderboard of certified
  Mordell-Weil rank lower bounds, ordered by naive height, Faltings height, and
  conductor."
- **Dujella rank-history table** — `https://dujella.github.io/tors/rankhist.html`
  ("History of elliptic curves rank records", 11,440 B, HTTP 200). The legacy URL
  `https://web.math.pmf.unizg.hr/~dujella/highrank.html` returned HTTP 404 and
  that 308-byte body is archived as well.
- Supporting pages: leaderboard index (`https://elliptic-rank.icarm.cloud/`,
  374,487 B), source repository page (`https://github.com/icarm/elliptic-rank`,
  259,299 B), commentary-history page for curve #302 (3,094 B), Wolfram MathWorld
  `EllipticCurveRank` page (71,296 B), two DuckDuckGo search-result pages that
  located the targets (34,022 B and 34,683 B), and one Bing search page that
  returned a bot-challenge with no organic results (117,891 B, archived as
  fetched, labelled as such).

## 2. The records' own claims, quoted VERBATIM from the fetched bytes

From `fetched/icarm_curve302.html` / `.json` (curve #302):

- Curve (a-invariants, verbatim from the JSON `ainvs`):
  `[1, 1, 1, -1284727764113567728281797636015784768866707681415849262157224232063, 560368321454261339256859338901915312332769858684945406858043869199456710681989058863306170127006181]`
  i.e. `y^2 + xy + y = x^3 + x^2 + a4*x + a6` (general Weierstrass form).
- Field "rank (lower bound)": `≥ 31`; "torsion subgroup": `trivial`.
- "**Witness: 31 independent points**" — 31 (x, y) pairs listed on the page,
  several with large fractional coordinates (largest denominator 26650518803);
  the page list matches the JSON `points` array **exactly, string for string,
  31/31** (mechanical comparison, recorded in run_record.yaml).
- Credit and timestamps (verbatim): "submitted by Ava Howell", "submitted at
  2026-08-23 20:02:58 UTC", "last updated 2026-08-23 20:16:24 UTC".
- **Conditioning language, VERBATIM** (commentary field of both HTML and JSON,
  and the single edit in the commentary-history page, "Ava Howell · 2026-08-23
  20:02:58 UTC"):

  > "BSD + GRH certified to rank 31, found by Claude, Levent Alpöge, and Ava Howell."

  This is the BSD+GRH mention the red-team record (control C-02) flagged. The
  page states no further qualification of the witness list itself.
- Other stated quantities (verbatim fields): conductor (209 digits),
  discriminant (204 digits), "regulator
  5520367374821893536678475926502746956624.072603230810343324240227195436655202216427344786535970988197",
  naive height 468.277091963089, Faltings height 36.74250427555862, 20 primes
  of bad reduction, "★ record for rank ≥ 31" markers on naive height, Faltings
  height, conductor and discriminant.

From `fetched/dujella_rankhist.html` (rank-history table rows, verbatim):

> `    rank >=         year                 Author(s)`
> `     |30|		    2026            Alpöge - Howell`
> `     |31|		    2026            Alpöge - Howell`

(the `|N|` markers are the page's own link wrappers around rank values; the
table lists rank 30 and rank 31, both 2026, Alpöge–Howell, exactly as the
committed red-team record C-02 states). The page also states: "The highest rank
of an elliptic curve which is (unconditionally) known exactly (not only a lower
bound for rank)" — with Elkies rank = 19 listed there — distinguishing exact
ranks from lower bounds.

Search-snippet corroboration archived in `fetched/ddg_icarm_leaderboard.html`
(MathWorld snippet, verbatim): "As of Aug. 29, 2026, the largest known lower
bound for the rank of an elliptic curve over [Q] is 31. The record elliptic
curve, submitted to the ICARM Elliptic Curve Rank Leaderboard on Aug. 23, 2026
and attributed there to Claude, L. Alpöge, and A. Howell, is …".

## 3. Identity / provenance observations (mechanical)

- The curve #302 page DOES state the curve equation explicitly (a-invariants,
  section 2) and the credit "found by Claude, Levent Alpöge, and Ava Howell"
  matches the leaderboard credit recorded in the committed red-team report
  C-02; the submission timestamp on the page (2026-08-23 20:02:58 UTC) matches
  C-02's recorded timestamp exactly. Submitter of record: Ava Howell.
- The JSON `curve_key` field's two components equal, digit for digit, the
  numerators of the pre-scaling short-model invariants A and B computed from
  the page's `ainvs` in the input-preparation step (section 4):
  `61666932677451250957526286528757668905601968707960764583546763139025` and
  `484158229736481797117926468811255292357508238788175012972498868670847390044003856563630907590456883225`.
- The page's `discriminant` field equals exactly the discriminant recomputed
  from the page's own `ainvs` by the standard general-Weierstrass formula
  (checked exactly in `src/prepare_certificate.py`).
- The witness-point list on the HTML page and in the JSON are byte-identical
  after whitespace normalization (31/31 exact string match).

## 4. Input prepared for the committed verifiers (preparation only; no verifier edited, no point constructed)

The committed verifiers accept only short Weierstrass `y^2 = x^3 + A x + B`
with **integer** A, B (`verify_certificate.py` line 78: `int(cert['base_curve']['A'])`);
the published curve is in general form with (a1,a2,a3) = (1,1,1). An exact
birational change of variables over Q was therefore applied as INPUT
PREPARATION (`src/prepare_certificate.py`, full derivation in its docstring and
in run_record.yaml):

- W = (2y + x + 1)/2; x = X − b2/12 with b2 = 5; scale by u = 1/12
  (X = Xs/144, W = Ws/1728), giving the integer short model
  `A' = -26640114916658940413651355780423312967220050481839050300092201676058800`,
  `B' = 1673250841969281090839553876211698290387548473251932844832956090126448579992077328283908416632618988425600`,
  and the point map (x, y) ↦ (144x + 60, 864(2y + x + 1)).
- Exact checks performed during preparation (all with Fraction/integer
  arithmetic, output in `logs_prepare.txt`): all 31 fetched points lie exactly
  on the published GENERAL model (31/31); all 31 transformed points lie exactly
  on the transformed SHORT model (31/31); c4, c6 and discriminant scale exactly
  by u^-4, u^-6, u^-12 (all True); page discriminant equals the general-model
  discriminant (True).
- Certificate written: `certificate_k0_icarm302.json` — k = 0 configuration
  (V = [1], k = 0, single twist d = 1 carrying all 31 points), exactly the
  shape C1 specifies. NO point was constructed, completed or repaired; every
  coordinate descends from the archived JSON bytes by exact rational
  arithmetic. An isomorphism over Q preserves the group structure, non-torsion
  and independence, and the Néron–Tate height pairing is isomorphism-invariant.

## 5. Committed-verifier outputs (scripts run UNCHANGED; sha256 recorded in run_record.yaml)

`verify_certificate.py certificate_k0_icarm302.json` — exit code **0**, stdout
(verbatim):

```
base curve   E : y^2 = x^3 + (-26640114916658940413651355780423312967220050481839050300092201676058800) x + (1673250841969281090839553876211698290387548473251932844832956090126448579992077328283908416632618988425600)
field        K = Q(sqrt d : d in V),  |V| = 2^0, [K:Q] = 1
twist classes with a verified non-torsion rational point: 1
CERTIFIED    rank E(K) >= 1
errors: 0
```

Observation: errors = 0 means every one of the 31 points passed the exact
on-curve check and the exact Mazur non-torsion check (no point hit any
torsion multiple m ∈ {1,…,10,12}). The "CERTIFIED rank E(K) >= 1" line is the
eigenspace mechanism's own count of verified twist CLASSES, which at k = 0 is
necessarily 1; it is not the count of verified independent points, and the
script's own docstring states the multi-point-per-class case is delegated to
the height argument.

`regulator_check.py certificate_k0_icarm302.json` — exit code **0**, stdout
(verbatim):

```
classes with >1 point : 1
   d=1        m=31  det=5.52037e+39
singular regulators   : 0
TOTAL independent points (eigenspace + regulator) = 31
```

Observation: the single 31-point class has a NON-SINGULAR height-regulator
determinant (5.52037e+39, far above the script's 1e-20 threshold), and the
script's total independent-point count is 31.

Numerical coincidence worth recording (observation only, NOT interpreted):
the committed check's determinant 5.52037e+39 and the page's stated
"regulator" 5.5203673748218935…e49 agree in all printed significant digits
modulo an exact factor of 10^10. The scripts and the page may use different
normalizations/conventions; this task does not rule on why. Both quantities
are non-zero by many orders of magnitude.

Re-runs for resource measurement produced byte-identical stdout for both
verifiers (diff empty; files `stdout_verify_rss.txt`, `stdout_regulator_rss.txt`).

## 6. Unconditionality observation (mechanical, NOT a ruling)

As a mechanical observation about the artifact classes involved, per the
handoff's instruction: within this program's own certificate semantics, a
lower bound supported by (i) exact on-curve checks, (ii) exact Mazur
non-torsion checks and (iii) a non-singular Néron–Tate height regulator is a
finite verification of exhibited data and invokes no conjecture — the
verifiers' code paths consult no BSD conjecture and no GRH. All three outputs
above were obtained on the fetched bytes (transformed exactly). The page's own
commentary nevertheless carries the conditioning language "BSD + GRH certified
to rank 31" (quoted verbatim in section 2); whether that language concerns an
upper bound, the exact rank, or something else is NOT ruled on here. Whether
these observations CLOSE C1 is a Coordinator ruling and is not made in this file.

## 7. Outcome class

**FULL_LIST_OBTAINED_AND_VERIFIED**: 31/31 exhibited points obtained from the
ICARM curve #302 record; both committed verifiers ran unchanged and exited 0
(errors: 0; singular regulators: 0; TOTAL independent points = 31).

## 8. Prohibited-action compliance

No existing file modified (`git status` over the verifier sources: clean;
verifier sha256s recorded). No git commit. Zero search compute (no Mestre
scan, no descent, no new search — only fetch + committed verification + exact
input-preparation arithmetic). No Amazon Bedrock provider, endpoint or model
identifier selected, requested or probed for any inference or fetch. Fetch
failures encountered (one 404, one bot-challenge page) are recorded as
infrastructure outcomes and assert nothing about anyone's rank.
