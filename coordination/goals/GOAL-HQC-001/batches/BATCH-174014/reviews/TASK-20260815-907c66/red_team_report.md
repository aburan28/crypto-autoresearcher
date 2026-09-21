# Red-team report — completing the four-shard single-shard-only exponent table plus IVW pooling check (TASK-20260815-e61cca)

**Task** `TASK-20260815-907c66` (red team) · **Batch** `BATCH-174014` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`63b5607d3c1c71e35d98ea20c315ef7460b2b319` (task `TASK-20260815-7c6951`) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/{design.md,shard_8001_8002_discard_prefix.py,shard_8001_8002_discard_prefix_results.json,ivw_pooling_check.py,ivw_pooling_check_results.json,four_shard_exponent_report.md,run_manifest.yaml,stdout.log,stderr.log}`.
Also read, in full: `coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/reviews/TASK-20260814-a49f1c/red_team_report.md`
(my own prior report from a different session), `ledger/decisions/DEC-20260814-3f429d.yaml`,
`ledger/evidence/EV-HQC-469c08.yaml`, `ledger/handoffs/TASK-20260815-907c66.yaml`,
the dispatch queue, `AGENTS.md`, `agents/red-team.md`, `matched_pair.py`
(TASK-20260809-a79e4f), `stage_a.py` (`CTRStream`, `_t_shard`, `run_arm`,
`sha_key`, `fixed_weight_support`, `hist_of`, `batch_hists`, `evaluable_k`),
and `measure.py` (`log2_A_from_hists`, `comb_matrix`), all read-only. This is
a different session from the concurrent Validator's review; I have not read
`TASK-20260815-dbb70b`'s output.

**What I did beyond reading the artifacts.** I independently recomputed, from
`TASK-20260809-a79e4f`'s committed `matched_pair_results.json` (not from the
executor's own reported numbers), the IVW `diff_ivw`/`se_ivw` and the
`se_ivw/se_pooled_concatenated` ratio at k=17 for both shard pairs, in a
from-scratch Python snippet reading only the source JSON — this reproduces
the executor's numbers exactly (see §3). I pulled the full k=2..26 ratio
series from `ivw_pooling_check_results.json` and checked it against the
report's own prose summary (§3). I directly traced `CTRStream`'s
construction in `stage_a.py` (lines 158–204) to test the specific mechanism
the design names as the adapted disjointness proof's residual risk (§2). I
computed, from the four committed single-shard local exponents plus their
own committed trial-count/batch-size context, the batch-size/trial-count
transition each pair was actually tested at (§4) — this is the sharpest
finding in this report and, to my knowledge, has not been surfaced by any
prior artifact in this family. I did not re-run either script myself
end-to-end (both the disjointness proof and the F-invariant check are
independently checkable by direct inspection of the committed JSON's
per-field pass/fail counts, which I did, rather than by re-executing
`_t_shard`, given this task's records-only budget and this batch's own
already-thin remaining wall-clock authorization).

I do not contest any reported number. Every value I independently
recomputed — the IVW `diff_ivw`/`se_ivw`/ratio at k=17 for both pairs, the
0-mismatch counts on the disjointness proof and the F-invariant check —
matches the committed record exactly. My objections are about whether this
batch's own framing of what the four-shard table shows is defensible, and
about a confound in the underlying design that neither this task nor
`DEC-20260814-3f429d` noticed.

---

## 1. Does the completed table turn the directional lean into confound-free evidence — or does it show the diagnostic itself is too noisy to mean anything, regardless of direction?

**The second reading is correct, and it is the dominant finding of this
review.** `DEC-20260814-3f429d`'s own limitation (rationale item 3,
carried forward from my own prior report) already said the two-shard
directional lean "rests on exactly two shards with two data points each"
and is "not confound-free evidence." Completing the table to four shards
does not fix this — it makes the problem worse, not better, because the
four values now **actively contradict a single monotone story in either
direction**:

| shard | single-shard-only local exponent | sign |
|---|---:|---|
| 5000 | +2.836 | + |
| 6000 | +1.402 | + |
| 8001 | −0.268 | − |
| 8002 | −0.866 | − |

A 2-point log-log slope has **zero internal degrees of freedom**: it is a
deterministic function of exactly two noisy `se_paired` point estimates,
with no way to compute a standard error, confidence interval, or
significance test from the two points alone. Treating four such draws as
"evidence leaning toward general estimator/shard heterogeneity" (as
`DEC-20260814-3f429d` did for the two-shard case, and as this batch's own
framing implicitly invites for the four-shard case) implicitly assumes the
diagnostic itself is low-noise enough that its sign and rough magnitude are
informative. The data available *from this very batch* argue against that
assumption. Treating the four exponents as four i.i.d. draws of some
common-or-heterogeneous quantity (a crude, informal calculation — not a
rigorous model of a 2-point log-log slope's true sampling distribution, and
I flag it as exactly that):

```
values = [2.836, 1.402, -0.268, -0.866]
mean = 0.776, sample SD = 1.6755 (ddof=1), SE of mean = 0.8377
naive t(df=3) 95% CI on the mean: [-1.890, 3.442]
```

This interval comfortably contains **both** 0 (no scaling at all) **and**
the pre-registered [0.4, 0.6] band **and** values far above 1 — i.e., taken
at face value as a sample, the four numbers cannot even reject "the true
common exponent is 0.5 and everything else is sampling noise in a very
noisy 2-point statistic," which is the opposite of what a "directional lean
toward general heterogeneity" reading requires. **I state this plainly per
the handoff's own instruction: having four wildly different, sign-flipping
single-shard exponents does not sharpen the shard-specific-vs-general
question — it undermines the premise that the single-shard-only local
exponent, computed from exactly two points with no internal error bar, is a
diagnostic capable of adjudicating that question at all**, independent of
which way any individual draw happens to point. My own prior report named
this exact quantity as "the sharpest available discriminator" (§3b,
`TASK-20260814-a49f1c`) when it had two data points that happened to agree
in sign; with two more data points that disagree in sign, the honest
correction is to say the sharpness claim does not survive its own
completion. The cheapest control that would settle this directly — not
computed in this batch — is a genuine null-object control: run the *same*
2-point discard-prefix local-exponent procedure repeatedly on data where the
true scaling law is *known* (e.g., a NULL-M/NULL-P-style parametric object
under the same matched-pair machinery, `measure.py`'s "A_k = 1 is a
THEOREM" construction, adapted to the paired-SE estimator) and check whether
it *also* produces sign-flipping, order-of-magnitude-scattered local
exponents purely from sampling noise. If it does, that is a controlled
demonstration that the diagnostic itself — not shard identity, not general
heterogeneity — is the source of the scatter. See §5 for why I rank this
above further single-shard data collection of the same kind.

## 2. Attacking the adapted disjointness proof: can it pass while not proving genuine disjointness, in a way the direct 5000/6000 check would not be vulnerable to?

**I traced the actual code (`shard_8001_8002_discard_prefix.py` lines
280–520, plus `stage_a.py`'s `CTRStream`/`_t_shard`/`run_arm`), not merely
the design document's argument, per the handoff's instruction.**

**First, the design's own named example of the residual risk does not
survive a code trace, and I say so plainly.** `design.md` §3 names, as the
concrete mechanism by which the two-step check could pass while true
correspondence is broken: "a numpy RNG version or platform difference
changing `CTRStream`'s output while leaving its internal determinism
intact." I read `CTRStream`'s constructor and `_refill` directly
(`stage_a.py` lines 171–204): it is a pure SHA-256 counter-mode
construction (`hashlib.sha256(self.key + self.dom + self.ctr.to_bytes(8,
"little")).digest()`), with **no dependency on `numpy.random`, `PCG64`, or
any seeded `Generator` anywhere in the trial-generating path**
(`fixed_weight_support`, `support_to_int`, `ring_mul_sparse` are all pure
Python/bytes arithmetic over `CTRStream` output). SHA-256 is a fixed,
platform- and library-version-independent primitive; there is no "numpy RNG
version" that could perturb it. This specific named risk is not
mechanistically live. I raise this not to congratulate the design but
because it means the design's own limitation section, while directionally
honest ("weaker, not equivalent"), mischaracterizes *where* the real gap
is — which matters for whether a future reviewer trusts the stated
limitation as a complete account.

**The genuine, more precise gap is structural, not RNG-related: Step 2
compares two calls made inside the SAME process, where Step 1 (and
`TASK-20260814-8bbdd2`'s direct check) compares against an artifact
persisted by a genuinely SEPARATE process/session/commit.** A same-process
comparison is vulnerable to a class of bug a cross-process, git-committed
raw-array diff is structurally immune to: accidental aliasing of a mutable
buffer, a stale cached object, or any other same-interpreter state leak that
could make two "independent" calls agree without either being what it
claims to be. I checked the actual code for exactly this: `_t_shard`
allocates a fresh `F_all = np.zeros((n_trials, n_e), ...)` on every
invocation (`stage_a.py` line 487, no module-level cache), and `run_arm`
mutates the shared `sa.decode_blocks` global only for the duration of its
own call and restores `original_decode_blocks` immediately after (lines
322–325 of `matched_pair.py`) — I found **no evidence of a same-process
aliasing or caching bug** in the reused, sha256-pinned code. So while the
structural vulnerability is real and correctly disclosed in spirit (if more
sharply expressible than the design's own example), I found nothing live
exploiting it here.

**A separate observation that does NOT differentiate the two checks, though
it looks at first like it might.** One could argue: "a systematic bug
shared between the original stage-2 run and this task's verification call
(both reached via the same sha256-pinned `run_arm`/`_t_shard`) would
reproduce identically in both and neither step would catch it." This is
true, but it applies **symmetrically** to `TASK-20260814-8bbdd2`'s direct
check as well — that check's "committed raw array" comparator was itself
generated via the same sha256-pinned `matched_pair.py` `run_arm` mechanism
this task reuses. So this is a standing limitation of the whole task
family's determinism-checking methodology (it verifies self-consistency of
a fixed deterministic function, not that the function correctly implements
its documented trial-indexing contract against an independent ground
truth), not a way in which the adapted substitute is specifically weaker
than the direct check. I flag it as scope, not as differentiating evidence.

**Step 1's own robustness is underrated by the design's framing.** Matching
`se_paired`/`diff`/`z_paired` etc. to full float64 bit-identity at **25**
independent evaluable-k cells, where `se_paired` is a leave-one-batch-out
jackknife over 200 sequentially-partitioned batches (order-sensitive, not
just an aggregate-histogram statistic), is a very high-dimensional exact
match. A genuinely different raw draw producing the same aggregate H would
not, in general, also reproduce the same batch-by-batch partition and hence
the same `se_paired` at all 25 k values by coincidence — this is for
practical purposes as strong as the derived-statistics comparator can be
made without the missing raw array.

**Position: the adapted proof is not proven unsound, and I found no
exploited gap, but it is honestly weaker in one precise, disclosed way (same-process
Step 2 vs. cross-process persisted comparator), not in the way the design
itself names.** This is a real, if narrow, loss of independently-auditable
evidence (a future reviewer can no longer re-diff a frozen raw array without
trusting this task's own process), and I recommend the design's §3 be
corrected to name the structural (same-process-vs-cross-process) risk rather
than the SHA-256-immune RNG-version risk, the next time this pattern is
reused — a low-priority, disclosed, non-blocking correction, in the same
spirit as the O10 documentation-accuracy finding this family has already
handled once.

## 3. Does the IVW check refute, confirm, or fail to address the pooling-convention-asymmetry-as-bias hypothesis (O8)?

**It informs a related but narrower question than O8 asked, and conflating
the two would misstate what this batch shows — this distinction is not
made explicit anywhere in the committed artifacts, and I make it explicit
here.**

Independently recomputed from `matched_pair_results.json` directly (not
from the executor's script output):

```
IVW(5000,6000)@T=5000-each, k=17: diff_ivw=0.064435, se_ivw=0.096049
  vs. concatenated pooled (stage_1, T=10,000):        se=0.096781
  ratio = 0.9924  [independently reproduced exactly]

IVW(8001,8002)@T=10000-each, k=17: diff_ivw=0.010616, se_ivw=0.016411
  vs. concatenated pooled (stage_2, T=20,000):         se=0.017905
  ratio = 0.9165  [independently reproduced exactly]
```

Both ratios are close to 1, exactly as reported.

**What "close to 1" tells you:** at k=17, combining two shards' point
estimates by inverse-variance-weighting gives almost the same SE as
combining the *same underlying data* by concatenating histograms. This is
evidence **against** the narrow claim that concatenation is materially
compressing SE relative to a heterogeneity-respecting combination, at this
cell, for these two pairs, **when the two combination methods are applied
to the same trial count**.

**What it does NOT tell you, and what O8 actually flagged:** O8's stated
asymmetry (`EV-HQC-469c08` O8, restated in `DEC-20260814-3f429d` rationale
item 4) is between the T=5,000 fit point — the **arithmetic mean of the two
shards' separately-computed SEs** (0.137502 = (0.125106+0.149899)/2, a
"typical single-shard SE" statistic) — and the T=10,000/T=20,000 fit points,
which are **SEs of a jointly pooled multi-shard dataset**. This task's Part
B never computes the arithmetic-mean-of-SEs statistic, and never compares
it to anything. What it computes instead is IVW-of-two-shards vs.
concatenated-pooling-of-two-shards, **both of which are multi-shard-combined
statistics on the same underlying trial count** — the T=5,000 fit point's
actual comparator (single-shard-representative average) is a third,
untouched quantity. IVW-at-T=5,000-each landing close to
pooled-at-T=10,000 (ratio 0.9924) is therefore not surprising and not
informative about O8's asymmetry: IVW-of-N=5,000-each-shard and
pooled-concatenation-of-N=5,000-each-shard are both, structurally, "what you
get from combining 10,000 total trials across two shards" — they should
agree closely regardless of whether O8's actual concern (mixing a
single-shard-average statistic with a multi-shard-pooled statistic on the
same log-log line) is a real bias or not. **The specific pooling-convention
asymmetry O8 named remains untested by this batch — neither confirmed nor
refuted.** The ledger archive should not read the close-to-1 ratios as
having addressed O8; it addresses a different, adjacent question (does
concatenation ≈ IVW on the same data) that happens to have a reassuring
answer.

**One further, minor but concrete finding:** `four_shard_exponent_report.md`
§6(b) states the ratio is "consistently at or below 1... at every k in
2..26" for the 8001/8002 pair. I pulled the full k=2..26 series from
`ivw_pooling_check_results.json` directly: at k=2–7 the ratio is
**1.0005–1.0018**, marginally *above* 1, not at-or-below. This is a small,
non-material overstatement in the report's prose (the data themselves are
correct and I reproduced them exactly), worth a one-line correction, not a
validity concern. The ratio also shows real k-structure, not a flat "close
to 1 everywhere": it dips to its minimum (~0.907–0.910) specifically around
k=17–20 for the 8001/8002 pair, i.e. the divergence between the two pooling
conventions is largest exactly at and near the pre-registered load-bearing
cell, not spread uniformly across the k range — worth noting for anyone who
later wants to actually test O8's real asymmetry, since it suggests the
load-bearing cell is not a representative "typical" cell for this
comparison either.

## 4. A more parsimonious explanation for the whole four-shard pattern: shard identity and trial-count/batch-size regime are perfectly confounded

**This is the sharpest finding in this review, and it directly answers the
question posed.** Every `se_paired` in this family is a leave-one-batch-out
jackknife over a **fixed** `N_JACK_BATCHES = sa.N_JACK_BATCHES = 200`
(confirmed by direct read of `stage_a.py` line 89 and its use in both
`matched_pair.py.matched_pair_stats`/`arm_hists` and this task's own
driver). Batch size is therefore `T / 200`, which **doubles at every T-point
in this family**, and I laid out each pair's actual (T, batch-size)
trajectory using values I independently confirmed against the committed
records:

| pair | T (baseline point) | batch size (T/200) | T (new point) | batch size | SE direction | local exponent |
|---|---:|---:|---:|---:|---|---:|
| 5000 alone | 5,000 | 25 | 10,000 | 50 | **decrease** | +2.836 |
| 6000 alone | 5,000 | 25 | 10,000 | 50 | **decrease** | +1.402 |
| 8001 alone | 10,000 | 50 | 20,000 | 100 | **increase** | −0.268 |
| 8002 alone | 10,000 | 50 | 20,000 | 100 | **increase** | −0.866 |

**Every shard ever tested at the 25→50-trials-per-batch transition (5000,
6000) shows a positive exponent (SE decreased); every shard ever tested at
the 50→100-trials-per-batch transition (8001, 8002) shows a negative
exponent (SE increased).** Shard identity (original vs. fresh) is **100%
collinear** with which absolute trial-count/batch-size transition was
tested, in this dataset, because `TASK-20260809-a79e4f` stage 1 used
T=5,000/shard for 5000/6000 (`N_TRIALS_STAGE1 = 5_000`, confirmed directly
in `matched_pair.py` line 82) while stage 2 used T=10,000/shard for
8001/8002 (`STAGE2_T_FLOOR = 20_000` total, i.e. 10,000/shard, confirmed at
line 102), and every subsequent single-shard-only measurement in this
family has extended each shard from its own historically-fixed starting
point rather than from a common one.

This is a substantially more parsimonious candidate explanation than either
"shard-specific to 8001/8002" or "general shard-to-shard estimator
heterogeneity," because it requires no appeal to *shard identity* at all —
only to which two absolute (T, batch-size) points were sampled, a variable
that has never been varied independently of shard identity anywhere in this
task family. It is directly falsifiable and cheap to test: run the same
discard-prefix technique on shard 5000 or 6000 using a **fresh, disjoint**
T=10,000-per-shard baseline → T=20,000-per-shard new-tail transition
(mirroring 8001/8002's regime), and separately on shard 8001 or 8002 using a
fresh, disjoint T=5,000 → T=10,000 transition (mirroring 5000/6000's
regime) — genuinely disjoint from every trial range already consumed on
each shard. If the sign of the local exponent tracks the *transition
regime* rather than the *shard*, that directly falsifies both of
`DEC-20260809-186c86`'s named categories in favor of a third, previously
unconsidered mechanism (a batch-size- or absolute-T-dependent property of
the 200-batch jackknife estimator itself, structurally unrelated to any
defect-detection question this campaign otherwise cares about). This design
is authorized, in spirit, by the same next_actions pattern
`DEC-20260814-3f429d` already used to authorize this batch, and it is
strictly more informative than a fifth or sixth single-shard exponent
computed at whichever transition each shard happens to have a historical
starting point for.

## 5. What should the actual next step be?

**Not diminishing returns as a whole, but diminishing returns for more of
the SAME design.** Collecting a fifth or sixth single-shard exponent using
the existing pattern (extend whatever shard's own historical starting
point) would add another confounded, noisy 2-point draw to a diagnostic
already shown (§1) to be too scattered to adjudicate anything on its own,
and would not touch the shard-identity/regime confound (§4) at all —
recognizing that honestly is not premature closure, it is scoping the
existing design's information content correctly. Declaring the whole line
of inquiry saturated would be premature closure in the sense
`docs/inventor-protocol.md` §4 and this campaign's own standing rules
forbid: I have just named a concrete, cheap, previously-unconsidered
experimental design (§4) that would break the confound this batch's own new
data reveals, plus a genuine null-object control (§1) that would settle
whether the diagnostic itself is trustworthy at all — neither has been run,
and both are cheap relative to this batch's own measured 94 core-seconds
against a 500 core-second authorization. My concrete recommendation, in
priority order: (1) the confound-breaking design in §4 (mirror-transition
single-shard exponents, at least one shard from each existing pair, tested
at the OTHER pair's regime); (2) the null-object control in §1 (repeat the
2-point local-exponent procedure on a known-flat object, or repeat it
multiple times on the SAME shard at the SAME transition with genuinely
disjoint fresh trial ranges, to get an empirical handle on the diagnostic's
own sampling variance) — these can be sequenced together or the second
folded into the first's replication. Only *after* one or both of these is
run would I consider the shard-specific-vs-general question meaningfully
sharpened rather than merely re-measured with more scatter.

## 6. Standing objections, carried forward

Branch A (positive detection) has still never fired anywhere in this
campaign. This task's own new per-shard z-values at k=17 — shard 8001
z_paired = −0.8431, shard 8002 z_paired = 1.0552 — join shard 5000's −1.2256
and shard 6000's 0.6760 (`EV-HQC-469c08` O3): all four |z| < 1.96. My
`BATCH-2ecaa1` standing objection is not retired by this batch either.

## 7. Scope

Toy-scale, PS-R3-only, single defect class (V3), single injection point
(`decode_blocks`, block `n_e-1`). Part A: shards 8001 and 8002 only, trial
indices [10000,30000) retained per shard, [0,10000) discarded-but-computed.
Part B: reads only already-committed T=5,000-each (5000/6000) and
T=10,000-each (8001/8002) per-shard points; no new sampling. Nothing here is
a statement about HQC's IND-CCA security, its decoding-failure rate,
assumption A17/A5, or any standardized parameter set. Pollard-rho/BSGS
baseline comparison is not applicable to this HQC decode-path instrument
task; the relevant baseline remains the campaign's own between-shard design,
unaffected by this batch. This batch's measured spend (94.171 core-seconds /
94.020 wall-seconds, per `run_manifest.yaml`) is far under its 500/1,800
authorization; I did not independently re-run the sampling calls myself and
report this figure as read, not re-measured.

---

```yaml
red_team_report:
  id: RT-20260815-907c66
  task_id: TASK-20260815-907c66
  claim_under_review: >-
    four_shard_exponent_report.md (TASK-20260815-e61cca, snapshot
    63b5607d3c1c71e35d98ea20c315ef7460b2b319) reports a completed four-shard
    single-shard-only local-exponent table (5000=+2.836, 6000=+1.402 cited;
    8001=-0.268, 8002=-0.866 newly computed) via an adapted, disclosed-weaker
    two-step disjointness proof, plus an IVW pooling combination vs. the
    concatenated-histogram pooled estimate at k=17 (ratios 0.9924 and 0.9165),
    with no conclusion drawn about DEC-20260809-186c86's framing or about
    shard-specific-vs-general.
  objections:
    - "Having four single-shard-only local exponents that span a full sign
      flip (+2.836, +1.402, -0.268, -0.866), none within [0.4,0.6], does not
      sharpen the shard-specific-vs-general question into confound-free
      evidence -- it undermines the premise that a 2-point, zero-degree-of-
      freedom log-log slope is a diagnostic capable of adjudicating that
      question at all, in either direction. A crude n=4 mean/SD treatment of
      the four values (mean 0.776, sample SD 1.6755, naive t(df=3) 95% CI
      [-1.890, 3.442]) cannot even reject 'true exponent 0.5, rest is noise
      in a very noisy statistic' -- the opposite of what a directional lean
      toward general heterogeneity requires. This is stated plainly, per the
      handoff's instruction, as the primary finding of this review."
    - "design.md Section 3's own named example of the adapted disjointness
      proof's residual risk (a numpy RNG version or platform difference
      changing CTRStream's output) does not survive a direct code trace:
      CTRStream (stage_a.py lines 171-204) is a pure SHA-256 counter-mode
      construction with zero dependency on numpy.random/PCG64/Generator
      anywhere in the trial-generating path. The design's stated limitation
      is directionally honest but names an implausible mechanism; the
      genuine, more precise gap is structural (Step 2 compares two calls
      made in the SAME process, unlike the direct check's cross-process,
      git-committed comparator), not RNG-version drift. I checked the
      reused code for the concrete same-process failure class this implies
      (aliasing, caching) and found none (F_all is freshly zero-allocated
      every call; sa.decode_blocks is correctly saved/restored)."
    - "The IVW check (Part B) answers a narrower question than EV-HQC-469c08
      O8 actually flagged. O8's asymmetry is between the T=5,000 fit point
      (arithmetic MEAN of two separate per-shard SEs, 0.137502) and the
      T=10,000/20,000 points (SE of a JOINTLY POOLED dataset). Part B never
      computes or compares against the arithmetic-mean-of-SEs statistic; it
      compares IVW-of-two-shards to concatenated-pooling-of-two-shards, BOTH
      multi-shard-combined statistics on the SAME trial count -- so finding
      them close (ratio 0.9924, 0.9165) is unsurprising and does not confirm
      or refute O8's actual named asymmetry, which remains completely
      untested. Separately, four_shard_exponent_report.md Section 6(b)
      slightly overstates its own data: the 8001/8002 ratio is marginally
      ABOVE 1 at k=2-7 (1.0005-1.0018), not 'consistently at or below 1...
      at every k' as stated -- a minor, non-material prose inaccuracy,
      independently caught by pulling the full k=2..26 series."
    - "A more parsimonious explanation for the whole four-shard pattern than
      either named category: shard identity is 100% collinear with which
      absolute trial-count/batch-size transition was tested. N_JACK_BATCHES
      is fixed at 200 throughout this family, so batch size = T/200 doubles
      at every point. Shards 5000/6000 were both tested at the 25-to-50-
      trials-per-batch transition (T=5,000->10,000) and BOTH show SE
      decrease (positive exponent); shards 8001/8002 were both tested at
      the 50-to-100-trials-per-batch transition (T=10,000->20,000) and BOTH
      show SE increase (negative exponent). No shard has ever been tested
      at the OTHER pair's transition regime. This confound has never been
      broken anywhere in this task family and is a live, cheap, previously
      unnamed alternative to both 'shard-specific' and 'general estimator
      heterogeneity.'"
    - "Branch A (positive detection) has still never fired. This task's new
      z_paired values (shard 8001: -0.8431, shard 8002: 1.0552) join shards
      5000/6000's (-1.2256, 0.6760): all four |z| < 1.96. My BATCH-2ecaa1
      standing objection is not retired by this batch."
  required_controls:
    - "Break the shard-identity/regime confound directly: run the same
      discard-prefix technique on at least one of shards 5000/6000 at a
      fresh, disjoint T=10,000-per-shard baseline -> T=20,000-per-shard new
      tail (mirroring 8001/8002's regime), and on at least one of shards
      8001/8002 at a fresh, disjoint T=5,000 -> T=10,000 transition
      (mirroring 5000/6000's regime). If exponent sign tracks the transition
      regime rather than shard identity, this falsifies both of
      DEC-20260809-186c86's named categories in favor of a third,
      batch-size/absolute-T-dependent estimator mechanism -- named in this
      report's Section 4."
    - "Run a null-object control on the local-exponent diagnostic itself:
      apply the same 2-point discard-prefix procedure to an object with a
      KNOWN scaling law (e.g. a NULL-M/NULL-P-style parametric construction
      where A_k=1 is a theorem, adapted to the paired-SE estimator), or
      repeat the SAME (shard, transition) measurement multiple times with
      genuinely disjoint fresh trial ranges, to obtain an empirical estimate
      of the local exponent's own sampling variance. Without this, no single
      2-point draw's sign or magnitude can be trusted as informative."
    - "Correct design.md Section 3's stated example of the adapted
      disjointness proof's residual risk: CTRStream has no numpy-RNG
      dependency (pure SHA-256 counter mode, verified by direct code trace),
      so the named 'numpy RNG version' mechanism is not mechanistically
      live. State the genuine risk precisely: Step 2 is a same-process,
      not cross-process, comparison, and is therefore structurally (not
      currently, on the evidence I found) more vulnerable to same-process
      state-leak bugs than a persisted-raw-array comparison would be."
    - "Correct four_shard_exponent_report.md Section 6(b)'s minor
      overstatement: the 8001/8002 se_ivw/se_pooled ratio is marginally
      above 1 at k=2-7 (up to 1.0018), not 'at or below 1... at every k.'"
  counterexample_or_mutation: >-
    Cheapest discriminating experiment, already derivable from this batch's
    own committed data without new sampling: lay out each shard's actual
    (T_baseline, batch_size_baseline) -> (T_new, batch_size_new) transition
    next to its local exponent's sign. Shards 5000/6000 (batch 25->50) are
    BOTH positive; shards 8001/8002 (batch 50->100) are BOTH negative -- a
    perfect confound between shard identity and transition regime that
    neither DEC-20260814-3f429d nor this task's own design surfaces. The
    genuinely discriminating NEW experiment (not yet run) is to test at
    least one shard from each existing pair at the OTHER pair's transition
    regime, on a fresh disjoint trial range; if sign tracks regime rather
    than shard, this directly falsifies the shard-specific-vs-general
    framing this whole batch was designed to inform, in favor of a third
    mechanism this campaign has not yet considered.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS sense (this is an HQC decode-path
    instrument measurement, not an ECDLP claim). The relevant specialized
    baseline is the campaign's own between-shard design, unaffected by this
    batch's measured 94.171 core-seconds / 94.020 wall-seconds (read from
    run_manifest.yaml, not independently re-measured by this review), well
    inside the 500/1,800 authorization.
  heuristic_challenges: []
  cost_model_challenges:
    - "Spend is read from run_manifest.yaml and both results JSON files'
      own budget blocks, internally consistent (93.839+0.332=94.171
      core-seconds, matching the reported total exactly). I did not
      independently re-run either script to corroborate the timing figure
      this time, unlike my prior review of this family; no objection to the
      accounting itself, only a disclosed limitation on how it was checked."
  reduction_and_scope_challenges:
    - "Claim tier correctly stays TOY throughout design.md, both results
      JSON files, four_shard_exponent_report.md, and run_manifest.yaml;
      PS-R3-only, V3-only, decode_blocks-only, shards 8001/8002-only (Part
      A) scope is stated repeatedly and accurately. I found no HQC-security,
      decoding-failure-rate, A17/A5, or standardized-parameter-set claim
      latent anywhere in the executor's artifacts."
    - "H-HQC-18d1b4 is correctly left untouched by this task's own
      artifacts, as instructed; any movement of that hypothesis is the
      ledger archive task's responsibility, not this task's, and is outside
      what I am reviewing here."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The disjoint-trial-range, single-shard-only design for shards 8001/8002
    was implemented as pre-registered: the adapted two-step disjointness
    proof and the F[:, 0:n_e-1] structural invariant both PASS (0 mismatches
    on 25 evaluable-k matched_pair_stats comparisons per shard, 0/1,100,000
    F-invariant elements per shard, independently confirmed by direct
    inspection of the committed JSON's own pass/fail fields), and the
    reported se_paired/diff/local-exponent values and the IVW diff_ivw/
    se_ivw/ratio at k=17 for both pairs are exactly reproducible from the
    committed matched_pair_results.json by an independent from-scratch
    computation. The adapted disjointness proof is honestly disclosed as
    weaker than the direct raw-array check, though its own named example of
    the residual risk (numpy RNG/platform drift) is not mechanistically
    plausible given CTRStream's pure-SHA-256 construction; the genuine gap
    is the same-process (not cross-process) nature of Step 2, for which I
    found no evidence of an actual exploited bug. The completed four-shard
    table does NOT constitute confound-free evidence for either
    'shard-specific' or 'general shard-to-shard estimator heterogeneity':
    the four single-shard-only local exponents span a full sign flip and,
    treated even crudely as a four-point sample, cannot statistically
    distinguish either reading from pure sampling noise around the naive
    1/sqrt(T) value. A more parsimonious, previously unnamed, and directly
    falsifiable third explanation exists and has never been tested in this
    family: shard identity is perfectly confounded with which absolute
    trial-count/batch-size transition (25->50 batch trials for 5000/6000,
    50->100 for 8001/8002, since N_JACK_BATCHES=200 is fixed throughout) was
    sampled. The IVW combination (Part B) is correctly computed and matches
    independent recomputation exactly, but it tests a narrower question
    (concatenated-pooling vs. IVW-pooling on the SAME trial count) than the
    pooling-convention asymmetry EV-HQC-469c08 O8 actually named (average-
    of-separate-SEs vs. SE-of-pooled-data across DIFFERENT fit points), which
    remains untested. Branch A has still never fired anywhere in this
    campaign.
  next_concrete_action: >-
    Before any further ledger interpretation treats the shard-specific-vs-
    general question as sharpened by this batch: run the confound-breaking
    design named in Section 4/required_controls -- at least one shard from
    each existing pair (5000 or 6000; 8001 or 8002), tested at the OTHER
    pair's trial-count/batch-size transition, on a fresh disjoint trial
    range -- to determine whether local-exponent sign tracks shard identity
    or transition regime. In parallel or as a follow-up, run a null-object
    control on the 2-point local-exponent diagnostic itself (a known-flat
    parametric object, or repeated disjoint draws at the same (shard,
    transition)) to obtain an empirical handle on how much of the observed
    four-shard scatter is simply the diagnostic's own sampling noise. Until
    at least one of these runs, further single-shard exponents computed at
    each shard's own historical (confounded) transition are diminishing
    returns; these two designs are not.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/ivw_pooling_check.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/ivw_pooling_check_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/four_shard_exponent_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/archives/TASK-20260815-7c6951/snapshot-receipt.json
    - ledger/decisions/DEC-20260814-3f429d.yaml
    - ledger/evidence/EV-HQC-469c08.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/reviews/TASK-20260814-a49f1c/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement,
formed by tracing the actual reused code (`CTRStream`, `_t_shard`,
`run_arm`) rather than accepting the design document's own account of its
risk, and by independently recomputing the IVW combination and the
four-shard trial-count/batch-size trajectory from the committed
`matched_pair_results.json` rather than accepting the executor's reported
arithmetic on faith.*
