# Validation report — TASK-20260913-25da8c

Blind re-derivation, then comparison, of `ledger/corrections/CORR-20260913-53739b.yaml`
(Semaev-2015 stage-1 figures under a yield charge; correction_1, correction_2, and
the claim that no conclusion changes).

- Role: validator (independent session; `requested_policy: review-adversarial`;
  `resolved_model_id: claude-fable-5-1-thinking-xhigh`, self-reported,
  `model_verified: false`, `reasoning_effort: xhigh`).
- Object validated: the committed snapshot `62bd331d4641d79c1e32526da5423b6bac9d6a50`
  (archived by `TASK-20260913-b03e25`; reachable from `HEAD`
  `d6a5313fbce1912cd417c0bee277c46502483c04` on `cursor/semaev-2015-audit-program-5b8b`).
  The correction and all three producer artifacts hash identically in that commit and in
  the working tree (hashes in §7). This is not a working-tree-only receipt.
- Nothing here is measured. No degree is measured or asserted (IMP-SEMBIN-ENGINE). No
  statement about the security of any curve is made or implied; every figure below is
  cost-model bookkeeping evaluated from published formulas at stated parameters.

## 1. Verdicts

| claim | verdict | one-line basis |
| --- | --- | --- |
| correction_1 | **holds** | Every authoritative figure re-derived blind and matched to all displayed digits (§3). Two wording defects, neither arithmetic: the linearisation-control bounds are stated as if over n ∈ [100, 1000] but hold only on the producer's six-point grid (§4.1); the "18 values of n, namely n in [281, 302]" is a set of 18 of the 22 integers in that interval, because the faithful-charge d_sat = 4 crossover is non-monotone (§4.2). |
| correction_2 | **holds** | c′, c, c − 1/c′, both collapse constants, every floor value and coefficient at n = 571 (ω = 3 and 2.376), and the route coefficient at n ∈ {571, 10⁴, 10⁶, 10¹⁰, 10²⁰} re-derived blind and matched (§3). One omission: the "n ≈ 3400" crossing figure carried by DEC-20260913-cb5ee2, EXP-SEMBIN-92724f, H-SEMBIN-c59e50 and IDEA-20260913-8138a0 is the m = 2 value (4.0126 at n = 3400); at the route those records name, the floor first reaches 4 at n = 11518 (ω = 3) (§5.3). |
| no_conclusion_changes | **holds** for every conclusion the correction names as safe, and the correction's scope lists are incomplete (§5). IDEA-20260913-191ed2's headline ("the threshold is the fragile part") is sharpened, not moved; EXP-SEMBIN-92724f's interpretation_limits holds under every m with more margin. But (a) IDEA-20260913-9c54f9 — named by the correction only in correction_4 — carries figures inside correction_1's `supersedes_in_scope` and a directional statement ("integer k moves the threshold 302 → 303") whose direction reverses under the faithful charge (302 → 281 first-n, 287 stable); (b) IDEA-191ed2's "+0.5 bits at n = 571 per extra degree" becomes +3.75 bits and the dominant stage-1 arm at d_sat = 5, ω = 3 flips from unsatisfiable to satisfiable — implied by the authoritative cells but nowhere stated; (c) the correction's "about five times larger" compares a superseded m!-only figure (4 in n) with a cross-charge shift (22 in n); under the faithful charge the same one-degree shift is 14 in n (first-n) or 8 (stable). None of these moves a hypothesis status. |

Overall `validation_report.verdict`: **passed** — the producer's receipt is admissible
evidence for the figures it states. Passed does not promote anything, does not support an
ECDLP claim, and does not authorize a status change; the scope omissions in §5 are findings
for the Coordinator, to be handled by a successor correction, never by editing this one.

## 2. Phase 1 — blind re-derivation

### 2.1 Ordering evidence

- `independent-figures.json` sha256
  `e63e898c8ef116390ef42f28f5b8eedee133056d1c7bb51ee95b03b05c84a6bf`;
  `written_at_utc: 2026-09-13T20:36:54Z` (script start); file mtime
  `2026-09-13 20:37:30.304 UTC`.
- The derivation source is embedded in that file (`derivation_source`, sha256
  `148d1ca4e0114837bff53410b4869ad74186524833750c37291a265e920bdfdc`). It imports only
  `json, math, statistics, hashlib, sys, datetime` and references no path under the
  blind_from directory; a reader can confirm this from the embedded text.
- The blind_from directory
  `coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/coordinator-rederivation-53739b/`
  was not opened, listed, grepped or imported before that file was on disk. This is
  attested by the validator; the filesystem is mounted `relatime`, so the producer files'
  atimes (17:06 UTC, at their creation) were not updated by my later reads and disk alone
  cannot prove the ordering. What disk does show: my derivation script and draft output
  (`/tmp/val25da8c/`, mtimes 20:35 UTC) predate the JSON, and the JSON predates every Phase 2
  artefact in this directory.

### 2.2 What was read, and the formulas as I read them (not as the correction quotes them)

`inputs/SEMAEV-2015-310/paper_fulltext.md`:

- eq. (11) (lines 400–427): P(q, m, t, |V|) = 1 − (1 − 1/q)^K with K ≈ |V|^t / t!;
  ≈ 1 − exp(−|V|^t/(q t!)); and when |V|^t/(q t!) = o(1), P ≈ |V|^t/(q t!).
- §4.5.2 (lines 1064–1067): P(n, m, m, k) ≈ 2^{mk−n}/m! with k = ⌈n/m⌉.
- eq. (15) (lines 1074–1091): stage 1 = 2^k n^{4ω}/P(n, m, m, k) ≈ (m!/2^{mk−n}) 2^k n^{4ω};
  "for ω = 3 that is at most m! 2^{n/m} n^{12}". The "at most" is the paper's own
  acknowledgement that dropping 2^{mk−n} overstates the cost.
- eq. (16) (lines 1093–1101): stage 2 = 2^{kω′}, ω′ = 2.
- Table 3 (lines 1157–1234; `tables.yaml` `table_3`): columns 2^{n/2}, m, m! 2^{n/m} n^{12},
  2^{2n/m} at un-ceiled k. I recomputed all twelve rows from the un-ceiled formula: maximum
  relative error 0.7 % (n = 500 stage 2), consistent with 3-significant-figure rounding.

`ledger/proposals/IDEA-20260913-191ed2.yaml` (C3): stage1 = 2^k((1/P)·C(d_unsat) + C(d_sat)),
C(d) = n^{dω}, d_unsat = 4, ω = 3, k = ⌈n/m⌉.
`ledger/proposals/IDEA-20260913-8138a0.yaml` (C5): d(n, m) ≥ [c − 1/c′]·√(n ln n)/(ω log₂(n(m−1))),
c′ = √(2 ln 2), c = 2/c′.

Charges evaluated: **A** (m!-only) 1/P = m!; **B** (eq. (11) linearised) 1/P = m!·2^{n−mk};
**B\*** (eq. (11) unlinearised) P = 1 − exp(−2^{mk−n}/m!). Total = stage1 + stage2, in log₂
domain, m optimised over [2, n]. Crossover = smallest n ∈ [100, 1000] with re-optimised total
< n/2; I additionally record every n above that first value at which the method does *not*
beat n/2.

Reading of eq. (11) confirmed independently: at (n, m, k) = (571, 12, 48), mk − n = 5,
log₂ 12! = 28.8355, so log₂(1/P) is 28.8355 under A and 23.8355 under B (B\*: 23.83545528).
The faithful charge is B; A equals B iff mk = n. Since 0 ≤ mk − n ≤ m − 1 and m! ≥ 2^{m−1},
λ = 2^{mk−n}/m! ≤ 1 always under ceiled k, with equality only at m = 2 with slack 1.

### 2.3 Phase 1 figures (subset; full set in `independent-figures.json`)

Stage 1 at (571, 12, 48), bits, d_sat = 4/5/6/7:
A 186.7236 / 187.1973 / 212.8322 / 240.3043; B 181.7236 / 185.4718 / 212.8322 / 240.3043;
B\* identical to B at 4 decimals.

Re-optimised totals at n = 571, bits (m, k):
A 186.4241 (13, 44) / 186.4666 (13, 44) / 197.0768 (18, 32) / 216.4367 (24, 24);
B 175.1383 (15, 39) / 176.8749 (15, 39) / 192.8484 (21, 28) / 212.4107 (30, 20);
B\* identical to B.

Crossovers (first n beating 2^{n/2}), d_sat = 4/5/6/7: A 303 / 307 / 347 / 400;
B 281 / 295 / 337 / 393; B\* 281 / 295 / 337 / 393.
Under B at d_sat = 4 the method beats 2^{n/2} at n = 281, 282, fails at 283, 284, 285, 286,
and beats it at every n ≥ 287 up to 1000. All other (charge, d_sat) crossovers are monotone.
Disagreement set at d_sat = 4: {281, 282, 287, 288, …, 302}, 18 values, all with B beating
and A not.

Overcharge A − B at d_sat = 4, n ∈ [100, 1000], re-optimised: mean 9.1075, median 9.2854,
min 0.9995 (n = 160), max 15.0000 (n = 961), sample sd 2.9362 (population 2.9345); argmin m
differs at 863/901 n; at n = 571 (13, 44) → (15, 39); at n = 310 (10, 31) → (11, 29).
Bound check max ≤ m − 1: true.

Linearisation control over the whole range n ∈ [100, 1000] at the d_sat = 4 charge-B optimum:
max log₂ λ = **−2.9069 at n = 126** (m = 5, k = 26); log₂ λ = −10.4691 at n = 163 (m = 9,
k = 19); −36.2501 at n = 1000; 97 values of n have log₂ λ > −10.47; max |B\* − B| in the
re-optimised total = **0.0842 bits at n = 126**; 67 values of n exceed 0.001 bits; the
argmin m under B\* never differs from B; crossovers under B\* are identical to B.

ω′-invariance (A, d_sat = 6, n = 571): optimum (18, 32) at 197.0768 for every ω′ ∈ {1, 2,
2.376, 3}; m = 21 (k = 28) is 203.3588, i.e. 6.282 bits worse. Un-ceiled k: A and B agree to
0.0 bits at n = 283 (m = 9) and n = 571 (m = 13). Un-ceiled paper formula: first n with
min_m stage 1 < n/2 is 302.

Correction 2: c′ = 1.177410, c = 1.698644, c − 1/c′ = 0.849322 = c/2. Collapse constants
(c ln 2)/(2ω): 0.19624 (ω = 3), 0.24777 (ω = 2.376); (c ln 2)/(4ω): 0.09812, 0.12389.
Floor at n = 571, ω = 3: m = 2 → 1.8612 (coeff 0.19624); m = 3 → 1.6780 (0.17692);
m = 12 → 1.3509 (0.14243); m = 62 → 1.1296 (0.11910); m = 571 → 0.9307 (0.09813);
interval over m ∈ [2, 571]: [0.9307, 1.8612]. ω = 2.376: m = 2 → 2.3500 (0.24777),
m = 571 → 1.1752 (0.12390). Route m = n/log₂ n coefficient: 0.11910 (571), 0.11415 (10⁴),
0.11003 (10⁶), 0.10620 (10¹⁰), 0.10280 (10²⁰). First n at which the floor reaches 4, ω = 3:
m = 2 → 3376; route → 11518; m = n → 16099 (ω = 2.376: 1979 / 6728 / 9555).

Degree price and margin (not in the correction; used in §5): at fixed (571, 12, 48) one extra
degree costs 0.4737 bits under A and 3.7482 under B; at fixed (310, 10, 31) it costs 3.2031
under both (slack 0). Dominant stage-1 term at (571, 12, 48), d_sat = 5, ω = 3: unsat under A,
sat under B; arm-switch threshold d_s − d_u: A 1.0496 / B 0.8676 (ω = 3), A 1.3253 / B 1.0955
(ω = 2.376). Re-optimised margin over n/2 at d_sat = 4: n = 310 → 2.8954 (A) / 10.4360 (B);
one-degree re-optimised cost 2.1314 (A) / 3.3556 (B).

## 3. Phase 2 — cell-by-cell comparison

Producer: `coordinator-rederivation-53739b/rederivation.txt` (sha256 `edaf3fa9…d6d0b`),
generated by `rederive.py` (sha256 `f3c0937f…348e2`); `rederivation.stderr.txt` is empty.
Re-running the producer's script from a copy in `/tmp` on Python 3.12.3 reproduces
`rederivation.txt` byte-for-byte (1.9 s, empty stderr) — the reproducibility pointer was
exercised, not asserted.

| cell | correction / producer | mine (Phase 1) | Δ |
| --- | --- | --- | --- |
| c′, c, c − 1/c′ | 1.177410, 1.698644, 0.849322 | 1.177410, 1.698644, 0.849322 | 0 |
| Semaev single-term stage 1 at (571, 12, 48) | 186.72 | 186.7236 | 0 |
| stage 1 A, d = 4/5/6/7 | 186.7 / 187.2 / 212.8 / 240.3 | 186.7236 / 187.1973 / 212.8322 / 240.3043 | 0 |
| stage 1 B, d = 4/5/6/7 | 181.7 / 185.5 / 212.8 / 240.3 | 181.7236 / 185.4718 / 212.8322 / 240.3043 | 0 |
| re-opt A, d = 4/5/6 | 186.4 (13, 44) / 186.5 (13, 44) / 197.1 (18, 32) | 186.4241 / 186.4666 / 197.0768, same (m, k) | 0 |
| re-opt B, d = 4/5/6 | 175.1 (15, 39) / 176.9 (15, 39) / 192.8 (21, 28) | 175.1383 / 176.8749 / 192.8484, same (m, k) | 0 |
| crossover A, d = 4/5/6/7 | 303 / 307 / 347 / 400 | 303 / 307 / 347 / 400 | 0 |
| crossover B, d = 4/5/6/7 | 281 / 295 / 337 / 393 | 281 / 295 / 337 / 393 | 0 |
| k shift at d = 6 | A 48 → 32 (16 bits); B 48 → 28 (20 bits) | 32 (16) ; 28 (20) | 0 |
| un-ceiled agreement, n = 283 / 571 | 147.649480 / 186.306952, diff 0.00e+00 | 0.0 bits diff at m = 9 / 13 | 0 |
| overcharge stats | mean 9.11, median 9.29, min 1.00, max 15.00, sd 2.93 | 9.1075, 9.2854, 0.9995, 15.0000, 2.9362 (sample) | 0 at displayed precision |
| argmin m differs | 863/901 | 863/901 | 0 |
| disagreement set d = 4 | "18 values of n: 281-302" | 18 values; set {281, 282, 287–302}; 22 integers in [281, 302] | count 0; **interval wording imprecise** |
| linearisation grid n = 163 | lin 117.6549 (m 9), exact 117.6554 (m 9), log₂ λ −10.47 | 117.6549, 117.6554, −10.47 | 0 |
| n = 233 | 132.6207 / 132.6208 / −16.25 | 132.6207 / 132.6208 / −16.25 | 0 |
| n = 283 | 141.5270 / 141.5270 / −14.79 | 141.5270 / 141.5270 / −14.79 | 0 |
| n = 409 | 156.9469 / 156.9469 / −17.84 | 156.9469 / 156.9469 / −17.84 | 0 |
| n = 571 | 175.1383 / 175.1383 / −26.25 | 175.1383 / 175.1383 / −26.25 | 0 |
| n = 1000 | 218.8396 / 218.8396 / −36.25 | 218.8396 / 218.8396 / −36.25 | 0 |
| correction text: "log₂ λ at most −10.47 … < 0.001 bits at every n tested … safe over the whole tested range" | (bound stated; grid = 6 points) | over [100, 1000]: max log₂ λ = **−2.91** (n = 126), max Δ = **0.084 bits** (n = 126), 67 n > 0.001 bits; argmin and crossovers unchanged | **largest disagreement — see §4.1** |
| ω′ invariance (A, d = 6) | (18, 32), 197.08 at ω′ ∈ {1, 2, 2.376, 3}; m = 21: 203.36 | same; 203.3588, +6.282 | 0 |
| flatness m = 17…21 | 198.85 / 197.08 / 198.01 / 199.99 / 203.36 | 198.85 / 197.08 / 198.01 / 199.99 / 203.36 | 0 |
| floor n = 571, ω = 3, m = 2/3/12/62/571 | 1.8612 / 1.6780 / 1.3509 / 1.1296 / 0.9307 | identical | 0 |
| implied coefficients | 0.19624 / 0.17692 / 0.14243 / 0.11910 / 0.09813 | identical | 0 |
| log₂(n(m−1))/log₂ n at route, n = 571 | 1.648 | 1.64765 | 0 |
| route coefficient n = 571 / 10⁴ / 10⁶ / 10¹⁰ / 10²⁰ | 0.11910 / 0.11415 / 0.11003 / 0.10620 / 0.10280 | 0.11910 / 0.11415 / 0.11003 / 0.10620 / 0.10280 | 0 |
| ω = 2.376: m = 2 / m = n | 2.3500 (0.24777) / 1.1752 (0.12390) | identical | 0 |

Independent corroboration (not blind; recorded only as corroboration):
`experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/reproduction.json`, group
`CORR_53739b_authoritative_eq11`, reproduces 181.7236 / 185.4718 / 212.8322 / 240.3043 and
175.1383 at (15, 39) — a third implementation agreeing with mine to every shown digit.

Implementation differences between the two named implementations (none changes any displayed
figure): producer uses `lgamma(m+1)/ln 2` for log₂ m!, mine uses exact `math.factorial`;
producer guards the unlinearised charge at log₂ λ < −30, mine at −50; both define crossover as
first-n and scan m ∈ [2, n]; producer's linearisation control evaluates 6 values of n, mine
evaluates all 901.

## 4. Disagreements (localised, not reconciled)

### 4.1 Linearisation control — scope of the stated bounds (largest disagreement)

The correction's `control_the_linearisation` states that the unlinearised charge "changes the
re-optimised total by less than 0.001 bits at every n tested, and log₂(λ) is at most −10.47
(n = 163) … The linearisation is safe over the whole tested range." Read beside
`measured_size_of_the_overcharge.scope` ("every integer n in [100, 1000]"), a reader will take
the bounds to cover [100, 1000]. They do not: the producer's script (`rederive.py` lines
123–132) evaluates n ∈ {163, 233, 283, 409, 571, 1000} only, and on those six points my
figures agree exactly. Over [100, 1000] the maximum log₂ λ at the charge-B optimum is −2.91
(n = 126, where the optimum sits at m = 5, k = 26 with slack 4 and 1/P = 7.5), and the
unlinearised charge changes the re-optimised total by up to 0.084 bits (n = 126), with 67
values of n above 0.001 bits — all below n = 163, i.e. in the region where the method does
not beat 2^{n/2} under either charge. The *conclusion* of the control survives on the full
range: B\* never changes the argmin m and never changes a crossover. The *stated bounds* are
grid-specific and should be re-scoped in a successor record ("on the six tested n" or the
full-range figures above). This localises to the producer's grid choice, not to either
implementation's arithmetic.

### 4.2 Crossover non-monotonicity at d_sat = 4 under the faithful charge

Both implementations define n\* as the first n at which the re-optimised total drops below
n/2, and both get 281. Neither the correction nor the producer's output reports that the
faithful charge then *loses* to 2^{n/2} at n = 283, 284, 285, 286 (totals 141.527, 142.588,
143.649, 144.169 against 141.5, 142.0, 142.5, 143.0) before beating it at every n ≥ 287. The
count "18 values of n" is correct; the phrase "namely n in [281, 302]" names an interval of
22 integers of which 4 are not in the set. A reader taking n\* = 281 as a threshold would be
wrong at 283–286. This is bookkeeping about a cost model at integer k; it says nothing about
any curve.

### 4.3 Nothing else disagrees

Every other cell agrees to the displayed precision of the producer's output.

## 5. Attack on "no conclusion changes"

The correction's safety claims are: (i) IDEA-191ed2's headline "the published threshold is
the fragile part of the claim" survives and is sharpened (correction_1
`consequence_for_the_records_headline_claim`); (ii) EXP-SEMBIN-92724f's interpretation_limits
statement holds under every reading of the coefficient (correction_2 `no_conclusion_changes`);
(iii) EXP-SEMBIN-92724f's frozen contract needs no amendment; (iv) "Nothing in this record
moves a hypothesis, closes a lane, or supports a claim" (limitations). Records the correction
names: IDEA-20260913-191ed2, IDEA-20260913-8138a0, IDEA-20260913-c94e52 (`corrects`);
EXP-SEMBIN-92724f, DEC-20260913-cb5ee2 (correction_2); IDEA-20260913-9c54f9,
IDEA-20260913-449d2b, IDEA-20260913-9ba7fc (correction_4); KN-LIT-fa346d (citation).

### 5.1 IDEA-20260913-191ed2 — headline survives; three figures move that the correction does not restate

- Headline (lines 65–68): sharpened, as the correction says. Under B the crossovers are lower
  and the one-degree shift larger (281 → 295 = 14 in n first-n; 287 → 295 = 8 stable) than the
  record's 303 → 307 = 4. **Holds.**
- "+0.5 bits at n = 571" per extra degree (lines 60–61, 168): computed at fixed (12, 48) under
  A (0.4737). Under B it is **3.7482 bits**. This figure is inside `supersedes_in_scope`
  generically but the correction gives no replacement, and its consequence paragraph still
  quotes the record's "4 in n" as if it were the faithful-charge value when comparing it with
  the 22-in-n cross-charge shift ("about five times larger" mixes charges).
- Arm dominance at d_sat = 5, ω = 3, (571, 12, 48): unsat-term 138.72 vs sat-term 137.36 under
  A (unsat dominates, hence +0.5 bits); 133.72 vs 137.36 under B (**sat dominates**). The
  record's stated arm-separation threshold d_s − d_u = log_n(m!)/ω = 1.33 at ω = 2.376 (line
  392) becomes log_n(m!·2^{n−mk})/ω = 1.0955 under B — still > 1, so its ω = 2.376 sentence
  ("safe for one extra degree and not for two") survives, thinner. At ω = 3 the threshold is
  1.0496 (A) / **0.8676 (B)**: under the faithful charge the single-term form is not safe for
  even one extra degree at the record's own ω. This is a qualitative change in the mechanism's
  bookkeeping that the authoritative cells (185.5 vs 181.7) imply but the correction never
  states.
- "+3.2 bits at n = 310" and "margin 2.9 bits" (lines 61–63, 409): at (10, 31) the slack is 0,
  so both charges give 3.2031; the 2.9-bit margin is Table 3's own. Unchanged by the
  correction. (Re-optimised, the margin is 2.8954 under A and 10.4360 under B, and one degree
  costs 2.1314 / 3.3556 — under neither charge is the re-optimised margin smaller than the
  re-optimised one-degree cost; the record's sentence compares fixed-m figures and is
  internally consistent as written.)
- `minimum_effect` "n\* ≥ 307 if d_sat = 5" (line 233) → 295 under B; covered by the
  correction's crossovers.

No hypothesis status moves; IDEA-191ed2 is `proposed`.

### 5.2 IDEA-20260913-9c54f9 — named by the correction, carries superseded figures, not in `corrects`

`target_complexity.time_exponent` (lines 476–482) states "2^{181.7} at m = 12 integer k;
2^{175.1} with m re-optimised" — these are **charge-B** figures — and in the same sentence
"Crossover with 2^{n/2}: 302 (paper's formula), 303 (integer k, m re-optimised), … 347
(satisfiable arm at degree 6), 400 (degree 7)" — these are **charge-A** crossovers. Under B
they are 281 (first-n; 287 stable) / 337 / 393. `sota_delta` (line 524) and `dominated_by`
(line 515) repeat "302-303" and "303-400". The directional statement that integer k moves the
paper's threshold from 302 to 303 reverses under the faithful charge: integer k with the
yield collected moves it from 302 down to 281/287. These figures fall inside correction_1's
`supersedes_in_scope` description ("every figure … computed under 1/P ~ m! at integer k")
but IDEA-9c54f9 is not in `corrects`, and correction_4 names it only for a citation
provenance point. This is a scope omission in the correction, and the moved statement is a
quantitative figure in a `proposed` record, not a hypothesis status or a lane closure.

### 5.3 IDEA-20260913-8138a0, EXP-SEMBIN-92724f, DEC-20260913-cb5ee2, H-SEMBIN-c59e50 — the "n ≈ 3400" figure carries the same missing m-label

- EXP-SEMBIN-92724f `interpretation_limits` ("evaluates to 1.86 at n = 571, below Assumption
  1's 4"): 1.8612 at m = 2 is the **maximum** of the floor over m ≥ 2 (the floor is decreasing
  in m because log₂(n(m−1)) increases), so the statement holds at every m and with more
  margin at every m > 2. **Holds**, as the correction says.
- DEC-20260913-cb5ee2 line 171 ("the floor reaches 4 at n ~ 3400 (4.012 at n = 3400)") and
  line 293; EXP-SEMBIN-92724f line 341 ("the n ~ 3400 crossing"); H-SEMBIN-c59e50 line 635
  and IDEA-8138a0 line 810 ("exceeds 4 only near/around n ~ 3400 at ω = 3"): 4.0126 at
  n = 3400 is the **m = 2** value. At the route m = n/log₂ n that IDEA-8138a0 names, the floor
  at n = 3400 is 2.3648 and first reaches 4 at **n = 11518** (m = n: 16099). Read as an
  envelope over m ("no m gives a floor ≥ 4 below n ≈ 3376"), the sentence is correct; read at
  the named route it is off by a factor 3.4 in n. This is exactly the defect correction_2
  diagnoses in the collapsed constant, propagated into a hypothesis record and an approval
  decision the correction does not name. No conclusion moves — every reading leaves the floor
  below 4 at n = 571 — but the successor record should label the 3400 with its m.
- The frozen contract's preregistered 0.196 / 0.248 and approval_basis 0.19624 / 0.24777 /
  1.861 are the m = 2 values and mutually consistent; the correction's statement that the
  contract is not amended is correct and I do not propose amending it.

### 5.4 IDEA-20260913-c94e52 (correction_3), IDEA-449d2b, IDEA-9ba7fc, KN-LIT-fa346d

Correction_3's arithmetic check (52480/39424 = 1.33117, 1.331³ = 2.3579, 91648/52480 =
1.74634) recomputes exactly. The in-place-edit finding is a process finding outside the
three claims I was asked to judge; I did not audit the git history for it. IDEA-449d2b and
IDEA-9ba7fc are named only for how their copies differ and carry no yield-charge figure
that I evaluated. KN-LIT-fa346d is the literature note for the paper; I read the paper
directly instead.

### 5.5 Records that cite the correction (downstream consumers, not named by it)

`rg -l CORR-20260913-53739b` finds consumers EXP-SEMBIN-db9bc3 (reproduction gate),
DEC-20260913-d02263, IDEA-20260913-352163, IDEA-20260913-41c4f0, IDEA-20260913-cedd2f
(untracked in the working tree), TASK-20260913-495fcc and H-SEMBIN-4a80f3. They take the
correction's figures as inputs; those figures hold. Whether any of them also inherits the
linearisation-bound wording of §4.1 is outside the three verdicts here and was not audited.

### 5.6 Verdict on the claim

No conclusion the correction names as safe moves. The claim **holds**. The correction's
`corrects` and `supersedes_in_scope` lists are incomplete (IDEA-9c54f9; the m-label on
"n ≈ 3400" in DEC-cb5ee2 and H-c59e50), and three superseded figures in IDEA-191ed2 have no
stated replacement. These are findings for a successor correction, not grounds to call the
present one broken.

## 6. What I could not evaluate, and why

- Whether the (C5) inequality itself is right. The correction names it as unreviewed; I
  evaluated only the collapse, as tasked.
- Whether any solving degree has the values used (d_unsat = 4, d_sat ∈ {4, …, 7}). No degree
  was measured; no algebra engine is installed (IMP-SEMBIN-ENGINE). Every figure is
  conditional on those inputs.
- The direction of the eq. (11) linearisation error's effect on the paper's *own* Table 3 is
  moot there (un-ceiled k, slack 0) and was not pursued.
- Correction_3's in-place-edit history (commit c441f43ea) — not audited; outside the three
  claims.
- The ordering of Phase 1 before Phase 2 cannot be proven from disk (relatime); it rests on
  this attestation plus the file timestamps and embedded source in §2.1.
- The model identifier is self-reported; no adapter probe ran (`model_verified: false`).

## 7. validation_report

```yaml
validation_report:
  id: VAL-20260913-353848
  task_id: TASK-20260913-25da8c
  role: validator
  kind: blind_rederivation_then_comparison
  object:
    record: CORR-20260913-53739b
    record_path: ledger/corrections/CORR-20260913-53739b.yaml
    committed_snapshot: 62bd331d4641d79c1e32526da5423b6bac9d6a50
    archived_by: TASK-20260913-b03e25
    head_at_validation: d6a5313fbce1912cd417c0bee277c46502483c04
    branch: cursor/semaev-2015-audit-program-5b8b
    snapshot_reachable_from_head: true
    working_tree_only: false
  inference:
    requested_policy: review-adversarial
    resolved_model_id: claude-fable-5-1-thinking-xhigh
    model_verified: false
    reasoning_effort: xhigh
    fallback_used: false
    independent_session: true
  run_ids: []   # no experiment run; the object is a coordinator re-derivation, nothing measured
  artifact_checks:
    - path: ledger/corrections/CORR-20260913-53739b.yaml
      sha256: 4e43a973d3fabc29a9f502007f9ef054f833608000383c349f870fba23f13ec7
      matches_commit_62bd331d4: true
    - path: coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/coordinator-rederivation-53739b/rederive.py
      sha256: f3c0937fac9a74a589c229339249aa5c4c101e5845e90ce86c5d7ba282c348e2
      matches_commit_62bd331d4: true
      imports: [math, statistics]
      m_range: "[2, n]"
      crossover_definition: first n in [50, 900) with re-optimised total < n/2
    - path: coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/coordinator-rederivation-53739b/rederivation.txt
      sha256: edaf3fa90d82948c2f2e12a7a796285e3ef3a19ce2ebae0eef1b6a26421d6d0b
      matches_commit_62bd331d4: true
      reproduced_byte_identical_by_rerun: true
      rerun_environment: "Python 3.12.3, copy of rederive.py executed in /tmp, 1.9 s wall, empty stderr"
    - path: coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/coordinator-rederivation-53739b/rederivation.stderr.txt
      sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
      empty: true
    - note: >-
        No run manifest, environment record, or command line is retained beside rederive.py;
        the artifact is a deterministic script whose output re-runs byte-identically, so
        reproducibility was exercised rather than read from a manifest.
  metric_recomputations:
    - name: stage1_at_571_12_48_bits
      producer: {A: [186.7, 187.2, 212.8, 240.3], B: [181.7, 185.5, 212.8, 240.3]}
      mine: {A: [186.7236, 187.1973, 212.8322, 240.3043], B: [181.7236, 185.4718, 212.8322, 240.3043]}
      agree: true
    - name: reoptimised_totals_at_571
      producer: {A: [[186.4, 13, 44], [186.5, 13, 44], [197.1, 18, 32]], B: [[175.1, 15, 39], [176.9, 15, 39], [192.8, 21, 28]]}
      mine: {A: [[186.4241, 13, 44], [186.4666, 13, 44], [197.0768, 18, 32]], B: [[175.1383, 15, 39], [176.8749, 15, 39], [192.8484, 21, 28]]}
      agree: true
    - name: crossover_first_n_beating_2_pow_n_half
      producer: {A: [303, 307, 347, 400], B: [281, 295, 337, 393]}
      mine: {A: [303, 307, 347, 400], B: [281, 295, 337, 393], Bstar: [281, 295, 337, 393]}
      agree: true
      addendum: "B at d_sat=4 is non-monotone: beats at 281,282; fails at 283-286; beats at every n in [287,1000]"
    - name: overcharge_A_minus_B_bits_d4_n_100_1000
      producer: {mean: 9.11, median: 9.29, min: 1.00, max: 15.00, sd: 2.93, argmin_m_differs: "863/901", disagreement_count: 18}
      mine: {mean: 9.1075, median: 9.2854, min: 0.9995, max: 15.0, sd_sample: 2.9362, argmin_m_differs: "863/901", disagreement_count: 18, disagreement_set: "{281,282,287..302}"}
      agree: true
    - name: linearisation_control_grid
      producer_grid_n: [163, 233, 283, 409, 571, 1000]
      producer_log2_lambda: [-10.47, -16.25, -14.79, -17.84, -26.25, -36.25]
      mine_on_same_grid: [-10.47, -16.25, -14.79, -17.84, -26.25, -36.25]
      agree_on_grid: true
      mine_full_range_100_1000: {max_log2_lambda: -2.9069, n_at_max: 126, max_abs_bits_Bstar_minus_B: 0.084242, n_at_max_diff: 126, count_n_gt_0_001_bits: 67, argmin_m_changes: 0, crossover_changes: 0}
      correction_wording_holds_over_100_1000: false
      control_conclusion_holds_over_100_1000: true
    - name: omega_prime_invariance_A_d6_571
      producer: {optimum: [18, 32, 197.08], m21: 203.36, omega_prime_set: [1, 2, 2.376, 3]}
      mine: {optimum: [18, 32, 197.0768], m21: 203.3588, delta: 6.282}
      agree: true
    - name: unceiled_k_coincidence
      producer: {n283: 0.0, n571: 0.0}
      mine: {n283: 0.0, n571: 0.0}
      agree: true
    - name: correction_2_constants_and_floors
      producer: {c_prime: 1.177410, c: 1.698644, bracket: 0.849322, floor_571_omega3_by_m: {2: 1.8612, 3: 1.6780, 12: 1.3509, 62: 1.1296, 571: 0.9307}, route_coeff: {571: 0.11910, 1e4: 0.11415, 1e6: 0.11003, 1e10: 0.10620, 1e20: 0.10280}, omega2376: {m2: 2.3500, m_n: 1.1752}}
      mine: identical to every displayed digit
      agree: true
      addendum: {first_n_floor_reaches_4_omega3: {m2: 3376, route: 11518, m_eq_n: 16099}, floor_at_3400: {m2: 4.0126, route_m290: 2.3648}}
    - name: table3_baseline_unceiled
      mine: {max_abs_rel_err_vs_paper: 0.007, first_n_min_m_stage1_lt_rho: 302}
      note: "consistency check of my reading of eq. (15)/(16) against the paper's own table; not a producer cell"
  control_checks:
    - name: eq11_reading_verified_against_primary_source
      result: "P = 2^(mk-n)/m! at |V|=2^k, q=2^n, t=m; 1/P = m! 2^(n-mk); equals m! iff mk=n; lambda <= 1 always under ceiled k"
      passed: true
    - name: unlinearised_charge_null_control
      result: "Bstar never changes argmin m or any crossover on [100,1000]; max effect 0.084 bits at n=126"
      passed: true
    - name: unceiled_k_agreement_control
      result: "charges A and B coincide to 0.0 bits at un-ceiled k (n=283, 571)"
      passed: true
    - name: producer_script_rerun
      result: "byte-identical stdout, empty stderr"
      passed: true
    - name: third_implementation_corroboration
      source: experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/reproduction.json (group CORR_53739b_authoritative_eq11)
      result: "181.7236 / 185.4718 / 212.8322 / 240.3043 / 175.1383 (15,39) — agrees with mine to every shown digit; not blind, corroboration only"
  heuristic_validation_checks:
    - name: not_applicable
      note: "no heuristic is validated by sampling here; every quantity is an exact evaluation of a published formula at stated parameters (omega=3, omega'=2, d_unsat=4, d_sat in 4..7, k=ceil(n/m))"
  cost_model_checks:
    - name: cost_bookkeeping_per_attempt_times_inverse_success
      result: "stage1 = 2^k((1/P) n^(4w) + n^(d_sat w)) with 1/P from eq. (11), never with success assumed certain; verified in both implementations"
      passed: true
    - name: unit_declared
      result: "bits of log2 cost in field-operation units per the paper's Table 3 convention (n^omega per row operation, omega=3); memory as k = log2 |V|"
      passed: true
    - name: memory_beside_time
      result: "k shift 48->28 (B) / 48->32 (A) at d_sat=6 reported; re-optimised (m,k) reported for every total"
      passed: true
    - name: optimistic_assumptions_flagged
      result: "omega=3 and the block-solver n^(4 omega) cost are the paper's own; d_unsat=4 is Assumption 1; none is measured. Flagged in the correction's limitations and here."
      passed: true
  proof_architecture_checks:
    - name: not_applicable
      note: "no theorem or asymptotic claim is proposed by the correction; it corrects bookkeeping in two proposed records"
  claim_verdicts:
    correction_1: holds
    correction_2: holds
    no_conclusion_changes: holds
  largest_cellwise_disagreement:
    where: control_the_linearisation (correction_1) — stated bounds "log2 lambda at most -10.47" and "< 0.001 bits at every n tested" read as covering n in [100,1000]
    producer_value: {max_log2_lambda: -10.47, max_bits: "<0.001", grid: 6 points}
    mine_full_range: {max_log2_lambda: -2.9069, max_bits: 0.084242, n: 126}
    localises_to: producer's six-point grid choice; arithmetic agrees on every shared cell
    changes_any_figure_or_conclusion: false
  downstream_conclusions_moved: none among those the correction names as safe
  scope_omissions_found:
    - IDEA-20260913-9c54f9 mixes eq.(11) stage-1 figures (181.7, 175.1) with m!-only crossovers (303/347/400; "302-303"); its "integer k moves threshold 302->303" reverses direction under the faithful charge (302->281 first-n / 287 stable); not in corrects
    - IDEA-20260913-191ed2 "+0.5 bits at n=571 per extra degree" becomes 3.7482 bits at fixed (12,48) under eq.(11); dominant arm at d_sat=5, omega=3 flips unsat->sat; arm-switch threshold 1.0496->0.8676 (omega=3), 1.3253->1.0955 (omega=2.376); no replacement stated
    - >-
      The "n ~ 3400" floor-reaches-4 figure in DEC-20260913-cb5ee2 (lines 171, 293),
      EXP-SEMBIN-92724f (line 341), H-SEMBIN-c59e50 (line 635), IDEA-20260913-8138a0
      (line 810) is the m=2 value (4.0126); at the named route m=n/log2 n it is n=11518;
      correct as an envelope over m, unlabeled
    - >-
      correction_1 "about five times larger" compares the record's m!-only 4-in-n with a
      cross-charge 22-in-n; the faithful-charge one-degree shift is 14 (first-n) or 8 (stable)
  verdict: passed
  verdict_meaning: >-
    The producer's receipt is admissible evidence for the figures it states. Passed does
    not promote a figure to knowledge, does not support any ECDLP claim, demonstrates no
    speedup, and authorizes no status change. The scope omissions above are for a
    successor correction; CORR-20260913-53739b itself is not to be edited.
  limitations:
    - No degree measured or asserted (IMP-SEMBIN-ENGINE); every figure is conditional on d_unsat=4 and the stated d_sat.
    - No statement about the security of any curve is made; n values are cost-model inputs only.
    - Phase-1-before-Phase-2 ordering is attested and supported by file timestamps and the embedded derivation source; it is not provable from disk (relatime).
    - resolved_model_id is self-reported; model_verified false; no adapter probe ran.
    - The (C5) inequality's own derivation is unaudited here, as in the correction.
    - Correction_3's git-history finding was not audited (outside the three claims).
    - Consumers citing the correction (EXP-SEMBIN-db9bc3, DEC-20260913-d02263, IDEA-20260913-352163, IDEA-20260913-41c4f0, IDEA-20260913-cedd2f, TASK-20260913-495fcc, H-SEMBIN-4a80f3) were not audited for inherited wording.
    - The working tree carries uncommitted modifications by other sessions outside my write scope (dispatch_queue.json, GOAL-SEMBIN-5078bc.yaml, claim/release files); I did not touch them.
  artifact_paths:
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/review-25da8c/independent-figures.json
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/review-25da8c/report.md
    - coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/review-25da8c/attestation.yaml
  independent_figures_sha256: e63e898c8ef116390ef42f28f5b8eedee133056d1c7bb51ee95b03b05c84a6bf
  derivation_source_sha256: 148d1ca4e0114837bff53410b4869ad74186524833750c37291a265e920bdfdc
  handed_to: coordinator ledger-archive task (the Coordinator commits; this session ran no git write command)
```
