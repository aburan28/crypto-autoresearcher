# TASK-20260812-2d7288 independent validation notes

## Outcome

Verdict: **invalid**.

The archived arithmetic mechanically reproduces the producer's
`continuity_scoped` branch, but that data-bearing branch is not admissible.
Every primary meter is constant over all 32 vertical/horizontal curve objects,
three meters are exactly zero everywhere, the driver's `0/0 -> 1.0` convention
turns all ratios into one, KS is therefore exactly zero, and every permutation
"winner" is an eight-way tie. The instrument has no demonstrated ability to
distinguish continuity from a discontinuity that its measurement map collapses.

Independently, the mandatory horizontal same-level control was not performed as
frozen. None of the eight horizontal records recomputes the conductor on either
endpoint. Each substitutes `gcd(ell,q)=1` for the five candidate conductor
primes. That establishes only that the listed q-adic parts cannot change across
an ell-isogeny; it says nothing about the ell-adic conductor valuation, which is
the part an ell-isogeny can change. All eight horizontal edges use `ell=3`, so a
3-volcano ascending or descending edge remains compatible with every recorded
gcd fact. The KS comparator is consequently not certified horizontal/same-level.

This is instrument and evidence integrity, not negative evidence about
H-ECTD-19017a. No scientific status change is made or recommended by this
Validator artifact.

## Evidence boundary and provenance

- Independent fresh session: yes. I did not produce, execute, edit, or snapshot
  EXP-ECTD-9e4248.
- Requested policy: `review-adversarial`; reasoning effort: `xhigh`.
- Actual runtime/model: OpenAI native Codex, `gpt-5.6-sol`.
- Fallback: false. Degradation: false. Bedrock selected/configured/probed/
  contacted/used: false.
- `model_verified: false`: no exact canonical task-scoped adapter probe receipt
  was obtained. The read-only preflight passed generated bindings, role bindings,
  Python, and dependencies, but its harness doctor reported no usable API backend
  because API credentials were absent. I used the authenticated native Codex
  session and did not represent it as a canonical adapter probe.
- Reviewed frozen specification: `experiments/EXP-ECTD-9e4248/specification.yaml`
  v2, approved by `DEC-20260806-160175`.
- Reviewed hypothesis: `ledger/hypotheses/H-ECTD-19017a.yaml`.
- Reviewed content-first snapshot task: `TASK-20260812-7a3fab`, commit
  `9641644622e34ccca428fa36db4e08ebc554e1ba`.

## Snapshot and run-package integrity

The content-first binding is complete over the source set frozen by the v2
queue:

- The snapshot commit is reachable from `HEAD`.
- Its first parent is
  `c480116ba1b48c7a574685c143064fb0129e9ace`, exactly as declared.
- Its message contains the archive task, goal, batch, experiment, and producer
  task IDs.
- Independent SHA-256 recomputation matches 18/18 queue entries: 17 producer
  paths plus the self-neutral receipt.
- The receipt's 17 non-null internal producer hashes all match, its internal
  `commit_sha` and self-hash are deliberately null, and the queue carries the
  actual reachable receipt commit.
- `tools/research_dispatch.py` exited 0 and independently reported explicit
  `content_first`, `paths_verified: 18`, no generated skips, and all ten gates
  passing.

Exactly two planned terminal run records are bound: the one-edge implementation
smoke and the eight-edge screen. A prior first attempt with the decision-threshold
bug remains openly preserved under
`RUN-ECTD-9e4248-impl-INVALID-decision-threshold-bug`; it is outside this
17-path package and was neither hidden nor counted as one of the two planned
terminal runs.

Strict parsing succeeded for 12 JSON-bearing files and both duplicate-key-
rejecting YAML manifests. The six screen ancillary JSON files compare exactly
to independent projections from `screen/raw-result.json`. Both run summaries
agree with raw data, stdout, and environment files. The recorded `run.yaml`
files match their archived source manifests except for the disclosed additive
`run.yaml` artifact-list entry.

## Independent recomputation

### Seeds and scale

The screen master seeds are exactly 301 through 308, unique and complete. Each
has one successful attempt record; no undocumented replacement seed exists.

For seeds 301 through 308 respectively, the raw `(target_bits, achieved_bits)`
pairs are:

```text
(43,44), (44,45), (40,40), (41,42),
(41,41), (43,43), (44,45), (41,42)
```

Thus the reported achieved list `[44,45,40,42,41,43,45,42]` is accurate and
contains six widths. This fixes the earlier all-one-width behavior. It does not,
however, satisfy the frozen v2 requirement to draw target widths from
`{40,...,60}`: both runs use only `[40,41,42,43,44]`, explicitly disclosed as a
protocol deviation but not authorized by a pre-run amendment. The honest tested
scope is toy 40-45-bit N, not a 40-60 sweep.

### Primary meters, ratios, KS, and permutations

The 32 objects are the eight floor curves, eight crater curves, and sixteen
horizontal endpoints. Their primary values have the following unique sets:

| meter | unique values over 32 objects | zero count |
|---|---:|---:|
| `semaev_m3_relation_density` | `{0.0}` | 32 |
| `semaev_m4_relation_density` | `{0.0}` | 32 |
| `fb_decomposition_probability` | `{0.0}` | 32 |
| `groebner_solving_degree_d_reg` | `{14}` | 0 |
| `macaulay_rank_defect_at_first_fall` | `{2}` | 0 |

The driver defines a symmetric ratio of the larger to the smaller value and
special-cases `(0,0)` to `1.0`. Applying that exact convention produces 40
vertical ones and 40 horizontal ones. Every edge has `delta_d_reg=0` and
`max_ratio=1.0`.

The independently recomputed two-sample statistic is:

```text
D = 0.0
n = m = 40
d_crit = 1.36 * sqrt((40+40)/(40*40))
       = 0.30410524493997143
rejects at alpha=0.05 = false
```

For all five meters, the permutation record's `true_winners` is
`[0,1,2,3,4,5,6,7]`, and every trial recovers all eight. `stable=true` is the
correct boolean for preservation of this tie set, but it is not evidence that a
distinguished discontinuous edge survives relabelling.

### Five-branch table

The raw mechanical inputs and branch results are:

| predicate/branch | recomputation |
|---|---|
| vertical end-ring failures > 1 | false (`0`) |
| GLV expected move failed | false |
| fewer than 8 vertical or driver-labelled horizontal records | false |
| KS rejects | false |
| any ratio >=100 or `delta_d_reg >=2` | false |
| all ratios in `[0.1,10]` | true |
| `discontinuity_nominates_endpoint` | false |
| `continuity_scoped` | mechanically true, scientifically inadmissible |
| `moderate_effect_unresolved` | false |
| narrow coded `instrument_void` predicate | false |
| `resource_incomplete` | false |

Accordingly the producer token is mechanically reproduced without trusting its
summary. The Validator disposition is nevertheless instrument-void/invalid,
with no admissible data-bearing branch. The frozen table does not contain a
predicate for a missing mandatory horizontal certificate or a constant,
non-discriminating meter; validation gates cannot be bypassed merely because
the table's narrower coded booleans select a token.

### Vertical construction and certificates

For each seed I independently checked:

- `p` and `N` are prime;
- `N = p + 1 - t`;
- `t^2 - 4p = q^2 D_K`;
- `gcd(q,N)=1`;
- crater and floor equations are nonsingular;
- the crater j-invariant recomputes to the known CM value;
- recorded kernel representative count is `(q-1)/2`.

I then deterministically reconstructed kernel sets on every archived crater and
floor. The crater counts were `30,18,32,18,24,24,24,24`, exactly `q+1`; every
floor count was one; and every archived floor equation occurs among the
corresponding crater's q-Velu codomains. No vertical certificate failure was
found.

### Rho/BSGS certificates

All eight floor-curve baseline records contain both rho and BSGS certificates.
Using independently written short-Weierstrass addition and multiplication, I
checked all 16 witnesses: every `G` and `Q` is on its recorded curve, `N*G` is
the identity, and `k_found*G=Q`. Rho and BSGS agree with each other and the
bookkeeping k in every edge. These baseline receipts are valid; they do not
repair the meter/control failures.

### GLV isolation

The GLV receipt's algebraic facts recompute: p and the subgroup order are prime,
`N_full = cofactor * N_prime_subgroup`, the curve is j=0/D=-3, `zeta3` is a
nontrivial cube root modulo p, and `lambda` satisfies
`lambda^2+lambda+1=0` modulo the subgroup order. The cost channel is separate,
and the GLV Semaev meter object never enters `decision.build_ratio_samples`.

The receipt does not serialize the base point used for
`phi(P)=lambda*P`, so the two recorded point-dependent booleans cannot be
independently replayed from the receipt alone. This is a bounded receipt
limitation; no evidence indicates GLV was mixed into the primary sample.

### Other controls

- Coordinate null: all three coefficient transformations recompute correctly,
  and all primary meters match. A constant instrument necessarily passes this
  check, so it confirms invariance but not sensitivity.
- No-class-invariant endpoint: structurally N/A because no discontinuity branch
  nominated an endpoint. The invalid verdict independently licenses none.
- Tail exceedance: no exceedance; both distributions are the same point mass at
  one.
- Claim ceiling: no trapdoor, path-hardness, isogeny-evaluation-hardness,
  crypto-scale, ECDLP exponent, closure, completion, or breakthrough claim is
  present. The only `asymptotic` text is the disclosed KS critical-value
  approximation.

## Why D-2 is blocking

The specification does not ask merely whether a horizontal ell-edge preserves
the vertical experiment's chosen q-part. It expressly requires conductor
recomputation from both horizontal endpoint curves and whole-conductor equality.
The package provides neither endpoint conductor. Its proof obligation and its
implemented argument are therefore different:

```text
required:  conductor(E1) == conductor(E2)
provided:  v_q(conductor(E1)) == v_q(conductor(E2))
           for q in {17,19,23,29,31}, because gcd(ell,q)=1
missing:   v_ell(conductor(E1)) == v_ell(conductor(E2))
```

For every archived pair, `ell=3`. It is precisely `v_3` that a 3-isogeny can
change. Hence the provided facts are compatible with a misclassified vertical
3-edge and cannot certify the null comparator's same-level property.

## Why zero dynamic range is blocking

The package contains null/invariance checks, but no positive sensitivity check
showing that the frozen meter recognizes a known conductor-dependent change.
With the observed mapping, distinct curve equations, vertical endpoints, and
horizontal endpoints all produce `(0,0,0,14,2)`. Consequently:

```text
continuity at the target -> observed (0,0,0,14,2)
discontinuity erased by saturation/sampling -> observed (0,0,0,14,2)
```

Both ground truths are observationally compatible. This is the inventor
protocol's observation-collision/artifact shape. KS, ratios, coordinate nulls,
and permutation stability only process the already-collapsed observable and
cannot recover what it discarded. A `continuity_scoped` scientific reading is
therefore not identifiable from these data.

## Exact commands

These are the material read-only commands used. The embedded Python snippets
are shown in reproducible consolidated form; no producer file was written and no
experiment entry point was run.

```sh
python3 plugins/crypto-autoresearcher-harness/scripts/preflight.py \
  --repo /private/tmp/wt-ectd-rebind.DAKT0m --runtime codex --doctor

python3 tools/agent_bus.py inbox --as validator

python3 tools/research_dispatch.py \
  coordination/goals/GOAL-ECTD-001/batches/BATCH-33b207/dispatch_queue.v2.json \
  --output /dev/stdout --report /dev/stderr \
  --repo-root /private/tmp/wt-ectd-rebind.DAKT0m

git merge-base --is-ancestor \
  9641644622e34ccca428fa36db4e08ebc554e1ba HEAD
git log -1 --format='%H%n%P%n%B' \
  9641644622e34ccca428fa36db4e08ebc554e1ba
git diff-tree --no-commit-id --name-status -r \
  9641644622e34ccca428fa36db4e08ebc554e1ba
```

Hash and receipt binding:

```sh
python3 - <<'PY'
import hashlib, json, subprocess
from pathlib import Path
q = json.loads(Path('coordination/goals/GOAL-ECTD-001/batches/BATCH-33b207/dispatch_queue.v2.json').read_text())
t = next(x for x in q['tasks'] if x['id'] == 'TASK-20260812-7a3fab')
a = t['archive']
rec = json.loads(Path(t['artifact_paths'][0]).read_text())
actual = {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in a['path_sha256']}
assert actual == a['path_sha256']
assert sum(h is not None for h in rec['path_sha256'].values()) == 17
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == h
           for p, h in rec['path_sha256'].items() if h is not None)
assert rec['commit_sha'] is None
assert rec['path_sha256'][t['artifact_paths'][0]] is None
assert subprocess.run(['git','merge-base','--is-ancestor',a['commit_sha'],'HEAD']).returncode == 0
assert subprocess.check_output(['git','show','-s','--format=%P',a['commit_sha']], text=True).split()[0] == a['parent_sha']
PY
```

Raw samples, KS, and mechanical decision branch:

```sh
python3 - <<'PY'
import json, math
from pathlib import Path
r = json.loads(Path('experiments/EXP-ECTD-9e4248/runs/RUN-ECTD-9e4248-screen/raw-result.json').read_text())
meters = ['semaev_m3_relation_density','semaev_m4_relation_density',
          'fb_decomposition_probability','groebner_solving_degree_d_reg',
          'macaulay_rank_defect_at_first_fall']
assert r['master_seeds'] == list(range(301,309))
assert len(set(r['master_seeds'])) == 8
assert [(e['target_bits'],e['achieved_bits']) for e in r['completed_edges_detail']] == \
       [(43,44),(44,45),(40,40),(41,42),(41,41),(43,43),(44,45),(41,42)]
objects = []
for e in r['completed_edges_detail']:
    objects += [e['meters_floor'], e['meters_crater'],
                e['horizontal']['meters1'], e['horizontal']['meters2']]
assert len(objects) == 32
assert {tuple(o[m] for m in meters) for o in objects} == {(0.0,0.0,0.0,14,2)}
v = [e['ratios'][m] for e in r['completed_edges_detail'] for m in meters]
h = [e['horizontal']['ratios'][m] for e in r['completed_edges_detail'] for m in meters]
assert v == [1.0] * 40 and h == [1.0] * 40
vals = sorted(set(v+h))
D = max(abs(sum(y <= x for y in v)/len(v) - sum(y <= x for y in h)/len(h)) for x in vals)
dcrit = 1.36 * math.sqrt((len(v)+len(h))/(len(v)*len(h)))
reject = D > dcrit
extreme = any(any(math.isinf(x) or x >= 100 for x in e['ratios'].values())
              or e['delta_d_reg'] >= 2 for e in r['completed_edges_detail'])
band = all(all(not math.isinf(x) and 0.1 <= x <= 10 for x in e['ratios'].values())
           for e in r['completed_edges_detail'])
branch = ('discontinuity_nominates_endpoint' if reject and extreme else
          'continuity_scoped' if band and not reject else
          'moderate_effect_unresolved')
assert (D, dcrit, reject, extreme, band, branch) == \
       (0.0, 0.30410524493997143, False, False, True, 'continuity_scoped')
PY
```

Strict parsing and raw/ancillary agreement:

```sh
python3 - <<'PY'
import json, yaml
from pathlib import Path
class StrictLoader(yaml.SafeLoader): pass
def no_dupes(loader, node, deep=False):
    out = {}
    for kn, vn in node.value:
        key = loader.construct_object(kn, deep=deep)
        if key in out: raise ValueError('duplicate YAML key: %r' % key)
        out[key] = loader.construct_object(vn, deep=deep)
    return out
StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, no_dupes)
base = Path('experiments/EXP-ECTD-9e4248/runs/RUN-ECTD-9e4248-screen')
r = json.loads((base/'raw-result.json').read_text())
assert json.loads((base/'glv_instrument_receipt.json').read_text()) == r['glv_instrument']
assert json.loads((base/'coordinate_null_receipts.json').read_text()) == r['coordinate_null_receipts']
assert json.loads((base/'permutation_stability_table.json').read_text()) == r['permutation_results']
for run in ('RUN-ECTD-9e4248-impl','RUN-ECTD-9e4248-screen'):
    p = Path('experiments/EXP-ECTD-9e4248/runs')/run
    yaml.load((p/'run.yaml').read_text(), Loader=StrictLoader)
    json.loads((p/'raw-result.json').read_text())
    json.loads((p/'environment.json').read_text())
    json.loads((p/'stdout.log').read_text())
PY
```

The vertical kernel/codomain reconstruction used the archived driver primitives,
not either experiment entry point:

```sh
python3 - <<'PY'
import json, random, sys
sys.path.insert(0, 'experiments/EXP-ECTD-9e4248')
from driver import vertical_isogeny as vi
edges = json.load(open('experiments/EXP-ECTD-9e4248/runs/RUN-ECTD-9e4248-screen/raw-result.json'))['completed_edges_detail']
for e in edges:
    q, p = e['q'], e['p']
    ac, bc = e['crater']['a'], e['crater']['b']
    af, bf = e['floor']['a'], e['floor']['b']
    ck = vi.kernel_representative_sets_q(q, ac, bc, p, random.Random(900000+e['seed']))
    fk = vi.kernel_representative_sets_q(q, af, bf, p, random.Random(910000+e['seed']))
    assert len(ck) == q+1 and len(fk) == 1
    assert (af,bf) in {vi.velu_codomain(ac,bc,p,rep,q) for rep in ck}
PY
```

## Final boundary

The trustworthy observations are that the frozen bytes are intact; the raw and
summarized arithmetic agrees; eight vertical constructions and sixteen DLP
baseline witnesses pass the checks described above; and this meter/control
package cannot adjudicate the hypothesis. It is not trustworthy to interpret
the mechanically selected `continuity_scoped` token as scientific continuity.
