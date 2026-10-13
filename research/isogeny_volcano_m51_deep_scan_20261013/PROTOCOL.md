# Frozen protocol: m=51 bottom-to-f=120871 endpoint discovery

Status: pre-outcome, freeze-ready harness. The admitted scientific scan has
not been run in this study directory.

## Question and claim boundary

The discovery question is whether endpoint-native rho cost changes across the
four conductor levels with `f_E` equal to 1, 271, 120871, and
`271*120871=32756041` in the ordinary Koblitz isogeny class over `GF(2^51)`.
This stage discovers 32 bottom/parent edges for a later fixed native benchmark.

The study constructs and certifies endpoint models only. It does not serialize
a general isogeny point evaluator or a dual, transport planted points, price a
transfer, or support a transfer-based ECDLP claim. A faster native endpoint is
evidence about that endpoint/action implementation; it is not evidence that a
challenge on another curve can be moved there cheaply.

## Frozen mathematical object

The base field is

`GF(2)[x]/(x^51+x^6+x^3+x+1)`

and the scanned models are `E_b: y^2+xy=x^3+b`, `b != 0`. The target group
order and trace are

```
N = 2251799852369764
t = 2^51 + 1 - N = -38684515.
```

The classifier recomputes the exact point count. It also checks

```
t^2 - 4*2^51 = -7 * 32756041^2,
32756041 = 271 * 120871,
```

the primality and coprimality of the two factors, the 271-adic discriminant
valuation 2, `gcd(45,271)=1`, and class number `h(-7)=1`. A sieve hit is never
treated as a cardinality or conductor certificate.

## Pre-outcome coefficient ordering

The fixed scientific ranks are `[0,3600000000)`, divided into 256 contiguous
shards of 14,062,500 ranks. Four workers are pinned to logical CPUs 0--3. The
entire range must be scanned and every sieve hit classified; reaching the
pair quota never stops the scan.

Rank is mapped to `b` by a 12-round alternating 26/25-bit Feistel permutation.
Its round function uses `mix64`, so this is called a **keyed modeled PRP**, not
a cryptographically proven PRP. Level-wide inclusion and quota probabilities
are conditional on the ideal-PRP/exchangeability model.

The root was generated exactly once before any admitted scientific scan
outcomes (the excluded feasibility pilot already existed):

```
UTC:              2026-10-13T08:55:02Z
command:          openssl rand -hex 32
OpenSSL:          OpenSSL 3.5.7 9 Jun 2026
exit status:      0
root key:         10456676ccd2e6bd1497bc8de889944eff4f72ebe81da37fbedb0a95b36853c6
```

Counter `c=0` was the first and only rekey trial. The derived key is
`SHA256("m51-deep-scan-prp/v1/rekey" || root || uint64_be(c))`:

```
c:                0
derived key:      c6ac26c5f692baa74a02c14f38de8e93bfe40c2d2ecbdcf7231ac6e79049d7b2
PRP^-1(0):        1143900985707342
```

The zero preimage is outside the scientific rank range. Therefore all
3.6 billion coefficients are unique and nonzero. Under the ideal-PRP model,
they are an ordered sample without replacement from the nonzero coefficients.
`verify_prp.py` independently rederives the key and round keys, checks forward
and inverse vectors, proves the zero condition by inversion, exhaustively
checks a reduced-width Feistel, and runs marginal/avalanche diagnostics under
a disjoint self-test key.

The separate `probe_root_seed=202610135201` affects only the three point-x
probes. It cannot change coefficient order.

## Sieve and independent controls

`search.c` reuses the audited m=51 carry-less GF core and Lopez--Dahab x-only
ladder. It emits a row only when all three deterministically generated points
are killed by `N`; this is only a fast random-point sieve.

The `reference-vectors` mode is incompatible with scientific output.
`test_sieve_reference.py` checks twelve fixed cases against an independent
pure-Python oracle using bit-polynomial arithmetic, polynomial-Euclid
inversion, Rabin irreducibility, half-trace affine lifting, and affine
add/double scalar multiplication. It also checks malformed inputs and
exclusive output creation.

Before any scientific shard, the runner requires a sealed 21-control GP batch:

- the crater and all 16 complete `f=271` orbit representatives must be
  excluded with their exact labels;
- the pilot bottom must be excluded in normal mode;
- control-only `m51-floor-o01` must exhibit order-`271^2` torsion and ascend
  to the crater;
- the pilot bottom must exhibit order-`271^2` torsion and recover its frozen
  parent; and
- the pilot parent must positively exhibit full rank `E[271]`.

Control modes are hard-bound to the exact known coefficients and emit
control-only statuses that scientific selection rejects.

## Exact classification and endpoint recovery

All globally sorted hits are processed in one GP process. This shares the
deterministic degree-2295 field and base-field embedding initialization. The
certificate serializes the extension modulus, embedding, seeds, attempts,
point witnesses, kernel, Velu sum, raw codomain, canonical endpoint, and exact
orders. Other-twist samples are expected and counted; `[271^2]R != O` after
using the selected-twist cofactor is a skip, not an error.

Both validation layers require every source and target base-field coefficient
to lie in nonzero `GF(2^51)`, every Frobenius-orbit size to be one of the
divisors `{1,3,17,51}`, and every exact curve order to lie in the integer
Hasse interval `q+1 +/- floor(2*sqrt(q))`. Thus even a sieve-false-positive
certificate must also have even order, because `x=0` supplies rational
2-torsion on every nonsingular scanned model. A benign status therefore cannot
suppress a row with impossible order or orbit metadata.

The selected group `G=2^(51*45)+1+t_45` is the quadratic twist over the
degree-45 extension. Because 45 is odd, twisting replaces Frobenius `pi` by
`-pi`; it does not change the endomorphism-order conductor or the
scalar-versus-nonscalar question modulo 271. The x-only cyclic kernel and its
q-stability therefore certify the corresponding base-field quotient, which is
twisted back and identified with the exact trace-`t` target model. This proves
the endpoint only up to the serialized target isomorphism/conjugacy data. The
normalizing y-translation is serialized, but no general isogeny point
evaluator, dual, or transfer certificate is present.

For a bottom source, the required positive evidence is:

1. exact source order `N` and a 51-element Frobenius orbit;
2. three x-only `Q` witnesses with `[271]Q != O` and `[271^2]Q=O`;
3. the order-271 point `T=[271]Q` and agreement of its Velu half-kernel sum
   across all witnesses;
4. `x(T)^q=x([u]T)` for a serialized `u` in 1--135, plus a q-fixed Velu sum;
5. the characteristic-two Velu quotient `[1,0,0,v,B+v]`, with serialized
   `v`, and the normalization `y -> y+v` to
   `[1,0,0,0,B+v+v^2]`; its nonzero normalized coefficient, minimal
   polynomial, conjugacy exponent, and canonical parent;
6. exact target order `N`; and
7. two target order-271 x-only points, with all 135 x-coordinates of the first
   cyclic subgroup enumerated and the second point proved absent.

The target full-rank certificate proves that 271 does not divide its conductor.
The target's noncrater orbit and `h(-7)=1` distinguish `f_E=120871` from the
maximal order. The q-stable kernel certifies that the actual degree-271 edge is
defined over the base field. Since 120871 is coprime to 271, it is preserved
across that edge; the order-`271^2` source witness then certifies
`f_E=271*120871`. The complete `f=271` census is retained as a hash-bound
corroborating exclusion, not the load-bearing step in this proof.

Two short scalar lemmas are checked by the emitted valuations and witnesses.
First, the selected twist group has total 271-adic order exactly `271^2`; an
actual point of order `271^2` is incompatible with scalar Frobenius modulo 271,
which would make the rank-two 271-torsion split and give exponent 271 at this
valuation. Thus the source Frobenius is nonscalar and 271 divides its
conductor. Second, two independent target order-271 points make
`(-pi)^45` scalar on target 271-torsion. Modulo 271 the characteristic
polynomial has a repeated nonzero eigenvalue. A nonscalar case is a Jordan
block `lambda I+N`; its 45th power retains the nonzero term
`45*lambda^44*N` because `gcd(45,271)=1`. Hence `pi` itself must be scalar and
271 does not divide the target conductor.

Certificates contain enough exact data for a later independent arithmetic
replay. The present runner independently checks byte hashes and strict schema
and runs pinned positive controls, but it does not claim that every future
scientific certificate has already been replayed by a second arithmetic
implementation.

A direct `f=120871` hit is skipped only after positive full-rank evidence:
the classifier finds two nonzero order-271 x-only points, enumerates the 135
x-coordinates of the first cyclic subgroup, and proves that the second is not
in it. Exhausting a bounded witness search is `UNKNOWN_*`, never a conductor
label.

The complete `f=271` CSV is bound to revision
`f0bdf9f739462766a9060532c59f9bfed69d00b1`, source SHA256
`a73ef01d0cb78be9f1c3df131c5598eae394541ce85a55fab5b33efaeca8d91b`,
and normalized CSV SHA256
`bb4b64d5e8d53b323cd7493af435c738198b90b0ba8696316bb36e8709150fbe`.

## Pilot exclusion, population, and selection

The feasibility pilot is never eligible:

```
raw pilot b:       675235026289400
bottom orbit min:  99224513745505
parent orbit min:  7746411922983
```

The exclusion is the entire parent fiber, not only the observed child. Every
hit is retained, but after ascent any bottom whose parent orbit equals
`7746411922983` receives `EXCLUDED_PILOT_ORBIT`. This removes 272 bottom-child
orbits.

The resulting modeled eligible population contains 2,369 parents, 644,368
bottom orbits, and 32,862,768 models. For the fixed 3.6-billion range the
exact expectation is 52.53840242858134 eligible bottom hits and
51.96014232199414 distinct parents. Using each parent's exact
without-replacement marginal hit probability but approximating the parent-hit
indicators as independent gives a binomial-occupancy planning probability
0.998926642220153 of at least 32 distinct parents. `planning_stats.py`
reproduces these values and labels the tail as an approximation, not an exact
finite-population probability. These are PRP-model planning quantities, not
observed results.

The selected sample is the first 32 eligible distinct parent orbits in global
rank order, retaining the first bottom child for each. Duplicate siblings,
duplicate parent orbits, exclusions, direct parents, false positives, and all
failures remain serialized. Selection is never "first 32 successful pairs."
An admitted/unresolved failure at or before the provisional 32nd eligible rank
invalidates the run and permits no backfill. If fewer than 32 are recovered,
any admitted failure invalidates it. Later failures remain in the fixed-range
record but do not alter the already determined selected-32 sample.

"Eligible" describes the underlying fully certified object; bounded
classification or construction failure does not redefine a possibly eligible
rank as ineligible. Such a failure before the provisional cutoff makes the
sample unresolved and invalid, which is why no later success can replace it.

Every eligible parent fiber has the same 272 bottom-child orbits and every
orbit has 51 models. Under the modeled PRP ordering, parent-first selection
therefore does not require unequal-fiber weights, and the first child within a
selected parent is exchangeable within that fiber. Only one child is retained
per parent, however, so this discovery cannot estimate within-parent child
heterogeneity; a later whole-bottom-level claim must state that limitation.

## Output, checkpoint, and failure rules

`run_scan.py` requires a clean committed worktree and requires
`FROZEN.sha256` to name exactly the frozen input set (no omitted or extra
import-shadowing files) before copying a regular-file, read-only run-local
input snapshot. It
rechecks that snapshot against the frozen hashes before and after every
external build, control, scan, and classification phase and immediately
before terminal sealing. GP runtime receipts bind the classifier and census
hashes to the manifest entries, not merely to whatever bytes are present. The
runner also re-hashes the GP executable, `ldd`, and every resolved shared
object and rechecks the link mapping before and after controls and
classification, on resume, and immediately before sealing. The statically
linked scanner and its sealed build tree are likewise rechecked before and
after scanning and before sealing. It then:

1. records compiler, host, CPU feature, GP image/binary, `ldd`, and shared
   library hashes;
2. builds with warning-as-error flags and runs C plus differential self-tests;
3. runs and seals the 21 controls;
4. scans all 256 immutable chunks with four workers and per-chunk receipts;
5. constructs one sealed, globally sorted `hits.csv`;
6. classifies every row in a single shared-initialization GP batch;
7. independently checks hit, record, certificate byte hash, and endpoint
   bindings, reconstructs the exact GP batch driver, and requires exact
   certificate/partial/payload inventories; and
8. writes the global selection and terminal tree manifest.

Certificate paths embedded in root `selection.json` or `TERMINAL.json` are
relative to their explicit `certificate_base` value,
`classification/payload`; pipeline-local JSON paths remain relative to their
own payload directory.

Partial attempts are never promoted over complete outputs. Existing sealed
chunks are verified on resume. A nonblocking advisory lock serializes every
mutation of one output root, immutable publication uses atomic no-replace,
and terminal trees are SHA256-manifested and immediately reverified. The
terminal session schema and fixed-range invariants are checked both before
sealing and on sealed resume. No mutable artifact write occurs after the root
manifest is published; final JSON presentation happens outside the sealed
mutation and exception-recovery scope.

GP stderr, stdout, or a nonzero exit is a retryable process-level failure and
cannot enter selection; the failed attempt retains bound diagnostic
artifacts. Candidate-local GP exceptions are contained inside the batch, so a
missing or partial certificate is converted into an admitted `GP_ERROR` at
that exact rank while later rows continue. With an otherwise clean batch, an
incomplete, duplicate, mismatched, or invalid per-candidate certificate also
becomes an admitted failure at that fixed rank and triggers the no-backfill
rule. An unknown or arithmetically inconsistent benign label fails closed.
The global GP watchdog is seven days; it is only a hang guard, not an
outcome-driven choice.

The Linux runner must become a child subreaper before launching any admitted
process. Every direct-child completion, timeout, or cancellation probes the
whole child process group, escalates TERM to KILL when necessary, reaps
adopted descendants by PGID, and only then performs a bounded stdout/stderr
drain. A surviving group or held pipe is a failed attempt. This covers the
direct-leader-exits/GP-survives zombie path as well as normal watchdog exits.

The integrity model detects persistent corruption and concurrent admitted
runners; it does not claim protection from a privileged or same-UID adversary
that can rewrite and restore files between checks or coherently replace a run
and its self-contained receipts. The admitted run therefore requires an
isolated host with no concurrent writer to the study snapshot, output root,
GP executable, or linked libraries. This operational premise is recorded
rather than overstated as cryptographic tamper resistance.

Mock mode uses four tiny shards of explicitly tagged singular `b=0` fixtures,
does not invoke GP, and is schema-incompatible with scientific input.

No `FROZEN.sha256` is created until independent protocol, math, schema, and
code review is complete. No admitted scan may start before that freeze.

## Non-frozen downstream endpoint-native blueprint

Nothing in this section admits a benchmark estimator, test family, schedule,
seed, or performance claim. It is planning context only. A separate rho
protocol must freeze all of those items after discovery and before any endpoint
timing. The current blueprint is:

- 32 edge-pair strata and 96 four-arm target blocks per pair (3,072 blocks);
- native negation walks on `f=1`, `f=271`, `f=120871`, and bottom endpoints;
- all 16 `f=271` orbit representatives crossed within every deep pair, with
  six inferential and two held-out blocks per representative;
- within each deep pair, the 96 P/B assignments use one random/permuted
  schedule of conjugates 0--50 and then 45 duplicated conjugates; P and B use
  the same conjugate within a block so the certified edge is preserved;
- `f=271` conjugates are near-balanced over pair-by-six-assignment cells, and
  analysis calibrates cell means to equal model weight;
- one planted scalar shared within each four-arm block, with `P,Q` constructed
  independently on each endpoint; setup/target namespaces are common where
  appropriate, while walk seeds are arm/domain separated; and
- a disjoint 32-block-per-pair A/A design, for 4,096 solves in each of two
  independent walk-seed replications.

This is 12,288 inference solves plus 8,192 A/A solves, or 20,480 total. The
primary metric is the bit difference of arithmetic mean `walk_ops`. Labeling
the arms `C=f1`, `A=f271`, `P=f120871`, and `B=bottom`, the four adjacent
volcano-lattice contrasts are C-A, C-P, A-B, and P-B. P-A is not adjacent.
A candidate benchmark plan would report all six pairwise contrasts with
Bonferroni 99.1667% marginal intervals for 95% family coverage. The separate
benchmark freeze must decide whether that six-contrast family or a larger
family including factorial summaries is primary.

Here "adjacent" means an association between adjacent conductor-order levels,
not that every compared endpoint pair comes with a matched map. This discovery
certifies only each sampled P-B degree-271 edge. The crossed C-P and A-B arms
are not supplied as explicit matched isogeny edges (nor are transfer costs
available), so the later protocol must not describe those contrasts as
matched-edge transfer measurements.
Under that candidate plan, equivalence would be asserted only when the
complete interval lies inside +/-0.10 bit. The proposed A/A gate would be a
99% interval inside +/-0.15 bit.

Two estimands must remain distinct:

1. **Selected-32 mean.** Hold the 32 pair strata fixed and resample the 96
   four-arm target blocks within pair. This supports only the selected pairs.
2. **Whole-level mean.** Conditional on the modeled-PRP/exchangeability
   sampling model, resample the 32 sampled edge-pair PSUs and then blocks
   within pair. Any resulting level claim is restricted to the pilot-excluded
   population of 2,369 parents and 644,368 bottom orbits; it is never a claim
   about the complete named levels. The 16 `f=271` orbits are a census and the
   crater is fixed.

Prior near-zero pairing correlations are not credited in power. The planning
calculation's approximate six-way half-width of 0.0511 bit and approximate
93% joint equivalence success at true zero are planning statements only; the
frozen estimators and observed intervals govern the result.

Before that benchmark starts, its separate freeze must define the full
inference family (including any interaction contrasts and studentization), and
serialize the exact
0--50 permutations, the 45 duplicate choices per pair, `f=271` conjugate
assignments, scalar/setup/target/walk namespaces, and analysis weights. The
present discovery protocol fixes the constraints, not those as-yet uncreated
schedules.

## Invocation after freeze

The extracted pinned GP route is:

```
python3 -I -S -B run_scan.py \
  --out /absolute/write-once/run-directory \
  --gp-bin /tmp/m51-pari-runtime/gp-2.15
```

The runner invokes that absolute binary as `gp -q -f -s 2G`; `-f` suppresses
all user startup files. The GP child environment is exactly `LANG=C`,
`LC_ALL=C`, and `TZ=UTC`, with no `HOME`, `GPRC`, `LD_PRELOAD`, or
`LD_LIBRARY_PATH`. Other compiler, scanner, and Python children use the fixed
environment serialized in `spec.json` and every process receipt. The runner
itself and every Python child require isolated, no-site, no-bytecode mode
(`-I -S -B`), excluding user/system site customization, `PYTHONPATH`, and
`.pyc` inputs. The C
scanner is linked with `-static`; the runner parses its ELF program headers
and rejects any `PT_INTERP` or `PT_DYNAMIC` segment before executing it.

`--gp-image` is deliberately rejected for an admitted run. Killing a Docker
CLI does not guarantee that its daemon-side container stops, so a timeout or
interrupt could otherwise leave a GP process mutating a failed attempt. The
image remains the rebuild/provenance source and can be used for separately
supervised certificate replay; the long discovery run is frozen to the exact
extracted binary and records all host-linked libraries. The mock route is
Docker- and GP-free:

```
python3 -I -S -B run_scan.py --mock --out /absolute/write-once/mock-directory
```

Neither command is part of this pre-freeze implementation change.
