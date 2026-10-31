# Independent fixed shared-chart software review

Task `TASK-20261030-0c09df`; reviewer `reviewer-prime-shared-chart`; session
`prime-shared-chart-independent-review-20261030`.

The five frozen implementation files pass this independently authored fixed
software review. One suite invocation returned exit code 0 with **50 passing
assertions and zero failures**: 15 chart cases, 8 projector cases, 26 mandated
corruption assertions, and one final source-hash assertion. The two impossible
chart cases and two invalid projector cases passed by rejecting their specified
obligations. All five supplied SHA256 values matched before and after execution.

| Owned joint | Verdict | Evidence and scope |
| --- | --- | --- |
| chart_correspondence | holds | All 15 fixed charts: independently checked group relation, exact residual polynomial, basis/pole shape, monic normalization, coefficient norm identity, target sign and five-slot identity padding. Two impossible charts rejected. Universal rational descent and completeness are not decided here. |
| quotient_membership | holds | Own polynomial arithmetic checks idempotence, interval nilpotence and square-or-zero support on valid charts/projector cases. Repeated-root, nonsquare-common-root and malformed late-entry controls behave as required. Prime modulus remains an input premise. |
| projector_recovery | holds | All 8 fixed projector cases, exact expected factor lists, independently multiplied factor products, wrapped labels and integer multiplicity 5 in characteristic 5. Trace-zero and altered multiplicity certificates reject. |
| signed_local_orders | holds | Independent Hasse series check every represented rational sign, including expected order zero, common factors, B=0, two-torsion, characteristic 5 and a target outside the interval. Wrong target subtraction, missing target support, sign collapse and common-factor loss reject. |
| fixed_execution | holds | Exactly the frozen 15/8 cases plus their required mutations; 1 of at most 4 suite invocations, 240-second worker watchdog, exit 0, no timeout. Raw stdout/stderr and all records retained. No source edit, fixture search, solver, census, benchmark or remote job. |
| claim_boundary | holds | Source audit distinguishes a constructor given a relation from recovery given idempotents. Conditional field-operation reasoning does not establish witness-search cost, measured advantage, solving degree, or universal chart theory. No gcd-support construction appears in these five files. |

These are software-scope verdicts. They do not prefill the Coordinator's native
independence gate or constitute an official scientific transition.

## Reproducible execution and custody

The invoked command, from `/home/ec2-user/crypto-prime-sat-ideas-20261029`, was:

```text
/home/ec2-user/prime-sat-research-venv/bin/python -B research/prime_sat_shared_signed_chart_20261030/TASK-20261030-0c09df/test_independent.py
```

The controller launches exactly one `--worker` child per suite invocation,
captures its complete stdout/stderr and return code, and applies a 240-second
timeout. Attempt 1 began `2026-10-31T00:07:34.323843+00:00` and finished
`2026-10-31T00:07:35.036855+00:00`. These timestamps establish execution custody;
they are not a benchmark. The observed interpreter was Python 3.12.8, Clang
19.1.6 build; platform
`Linux-6.18.54-121.166.amzn2023.x86_64-x86_64-with-glibc2.34`.
`independent-results.json` retains the command, environment, suite-source hash,
contract hash, source hashes before/after, raw stdout, empty stderr, parsed
assertion details, every constructed witness, output, and local-series row.

The source commit `1a944ab5677a4e0b1059d1afd965cdd1b87acdf6` was supplied by the
dispatcher. This reviewer verified content hashes, not Git reachability, branch
state, the dispatch claim, or publication. Those duties remain with the root.

| Source file under `research/prime_sat_shared_signed_chart_20261030/` | Verified SHA256 |
| --- | --- |
| quotient.py | `0a5ac4ef58ef1c4616f849af6bb3895ca927f241f53a05baf21ee028fda3a433` |
| charts.py | `c808c7d3a5a2a96316a0c13c9faafd848406ef44e960a1bcc52bde700e6a818b` |
| projectors.py | `1f27515ad569061ae5599e8988611d9a5722518a6fa23e537f0febcbf3f5b6af` |
| signed_recovery.py | `bf67fa02e1778b8de89f4305c2ecda338977ab17ce24941503bb8ce61d4c8bc3` |
| check_chart.py | `139ec0d1b2a13d0add5547b81a363bc402fe59af13d94965beb21a6f0725de65` |

No suite failed, was retried, or was corrected. A preliminary navigation command
(`pwd && rg --files -g AGENTS.md -g '!research/**' -g '!knowledge/**'
/home/ec2-user/crypto-prime-sat-ideas-20261029 /home/ec2-user 2>/dev/null | head -60`)
was interrupted with Ctrl-C after yielding only `/home/ec2-user`; its exit status
was 130. It discovered no fixture or protected artifact and was not a software
suite invocation. Subsequent reads named exact assigned paths.

## Independent arithmetic and local-order reasoning

The oracle in `test_independent.py` implements its own polynomial multiplication,
monic division, binary modular powers, group accumulation and local series. It
does not use the producer's valuations for expected orders, and it derives
expected recovered multisets directly from the frozen point tuples. For every
valid chart it checks the product of linear factors against U, the norm equation
coefficient by coefficient, and the expected divisor on both rational signs.

At a point with ordinate beta nonzero, z=x-alpha is a local parameter and
`2*beta` is invertible. The oracle obtains the coefficients of f(alpha+z) with
integer binomial coefficients reduced modulo p, then solves y(z)^2=f(alpha+z)
coefficient by coefficient. This requires division only by `2*beta`, including
when the requested order is at least p. At a two-torsion point, nonsingularity
gives f'(alpha) nonzero. With z=y and w=x-alpha, the oracle instead solves

```text
f'(alpha)*w + 3*alpha*w^2 + w^3 = z^2.
```

It then substitutes x(z), y(z) into A+B*y using power expansion. The producer
checker uses Horner composition; the independent oracle uses a different
composition structure and the explicit cubic recurrence at two-torsion.

The valuation formulas also withstand direct local reasoning. Away from
two-torsion, removing g=min(v(A),v(B)) contributes g on each sign. If the remaining
norm order is positive, the reduced B(alpha) cannot vanish: that would force
reduced A(alpha)=0 too, contradicting removal of the common factor. Thus exactly
one sign has a zero, beta=-A(alpha)/B(alpha), and the norm's remaining order lies
there. If no norm order remains, both signs have order g and a verified square
root is still necessary. At two-torsion, x-alpha has order 2 and y has order 1;
the candidate orders `2*v(A)` and `2*v(B)+1` have opposite parity, so they cannot
cancel. The zero polynomial has infinite valuation; this covers B=0 and leaves
the minimum finite for a normalized nonzero chart.

At infinity, x and y have poles 2 and 3. Even d therefore normalizes the unique
highest term of A, while odd d normalizes the unique highest term of B. The norm
has leading coefficient +1 and -1 respectively, explaining the required c.
The local derivation supports the source audit; it is not a blind derivation of
all global rational principal-divisor, descent, auxiliary-fiber or chart
completeness claims.

| Fixed exceptional case | Observed independent orders and consequence |
| --- | --- |
| finite_four | A=4X, B=X over F5: orders 4 at (0,1), 1 at (0,4); the nonzero common factor contributes on both signs. |
| finite_five_characteristic5 | A=X^3+2, B=3: order 6 at (0,1), 0 at (0,4); subtracting -R leaves five copies. No factorial inversion. |
| identity_five_two_torsion | A=3+6X, B=4+X over F7: orders 3 at (0,1), 0 at (0,6), 2 at (3,0). |
| wrapped_five_balanced | A=X^3+X^2, B=0 over F5: orders 2 on each sign above 0 and 1 on each sign above 4; signed subtraction leaves the prescribed five points. |
| target_outside_interval | A=4+2X, B=1 over F5: orders 2 at (0,1), 0 at (0,4), 0 at (4,2), 1 at (4,3). The last point is -R outside the interval. |
| finite_two_torsion | h=X-3 over F7 has order 2 at the single point (3,0); subtracting the target once leaves one point. |

The fixed case named `finite_three_common` has B=0 in the actual normalized
witness. The `finite_four` case supplies the separate nonzero-A/nonzero-B common
factor check; neither fact is inferred from the fixture name.

For quotient membership, idempotents give binary labels on each residue field.
The nilpotent equation forces x to equal the corresponding interval label in
each residue field, while preserving repeated-root components. The permitted
interval length is less than p, so the labels are injective even when wrapped.
The rationality polynomial vanishes precisely at square-or-zero f-values in
the named prime fields. Its kth power removes nilpotent residue terms; dropping
this condition admits the mandated nonsquare example.

For projector recovery, multiplication by an idempotent is a projection.
Splitting V into images of E and I-E preserves the direct-sum dimension, and
commuting multiplication operators preserve the earlier label splits. The
retained integer dimension is the multiplicity; field trace does not retain
that integer in characteristic p. The independent exact factor product is the
final certificate. Under naive dense field arithmetic, forming a multiplication
matrix and processing all subspace columns at one bit costs O(k^3): the column
counts across the disjoint spaces sum to k. This gives the conditional
O((s+1)k^3) recovery bound after supplied valid witnesses, with streamed matrices.
It does not count how unknown idempotents are found. The code's event dictionary
contains descriptive algorithm events, not measured field-operation totals or
an end-to-end cost comparison.

## Corruption evidence

The raw result records name every mutation and its exact rejection obligation.
The required controls include:

| Corruption | Observed signature |
| --- | --- |
| Replace n^k=0 by n=0 | For U=(X-1)^2, n=X-1 is nonzero and n^2=0; the incorrect predicate rejects the valid repeated fixture. |
| Replace integer multiplicity 5 by trace 0 | `positive integer multiplicity` rejects the zero factor multiplicity. |
| Omit r=4 outside the interval | An in-memory patch of `norm_support` triggers `complete signed degree`; source files stay unchanged. |
| Remove R instead of -R | Wrong output is (0,4) instead of (0,1); own group sum disagrees and checker rejects `checker exact signed local order`. |
| Collapse inverse signs / remove common contribution | Each rejects `checker exact signed local order`. |
| Count two-torsion as two signs | Duplicated signed contribution yields the wrong affine count and rejects `canonical multiset and padding`. |
| Drop rationality at a common root | U=(X-1)^2, t=0, s=1, e=1 passes the interval condition; f(1)=3 over F5 rejects `rational ordinate support`. |
| Alter idempotent / norm / leading U / factor multiplicity | Respectively rejects `idempotence`, `checker norm identity`, `monic quotient modulus`, `independent factor product`. |
| Alter target ordinate | Opposite valid sign rejects the exact local order; off-curve ordinate rejects `checker point on curve`. |
| Append late malformed field or mask entries | Booleans, strings, negative integers and elements at p reject `canonical field element`. |
| Other canonical corruptions | Trailing polynomial zero, tuple mask, boolean bit count and boolean multiplicity reject their specific representation/integer obligations. |

No new field, curve, support or point-tuple search was used to obtain these
controls. All are the fixed fixtures or mutations explicitly required by the
contract. The proves-too-much control against promoting fixed tests to a universal
theorem is enforced by the verdict scopes above; no theorem acceptance is claimed.

## Independence, runtime and handoff

This was a fresh review session with an initial task dispatch and no substantive
post-dispatch consultation. No sibling reviewer report, parent conversation,
producer test, producer result, producer proof, producer README, source-note
derivation or snapshot receipt was read. The frozen API, contract and review
plan were the prospective sources; the five implementation files were the audit
targets. This is independent arithmetic/local-order software review with visible
implementation, not a claim of blindness to that implementation.

The role request was `review-adversarial`, `xhigh`. The runtime identifies itself
as Codex/GPT-6 in instructions, but this session did not authenticate an exact
serving model, the actual reasoning setting, capacity, fallback route or backend.
Those values remain unknown/unverified under the supplied inference amendment.
No `doctor --probe` was performed. Independence is reported as an observed
session/read boundary; unverified runtime properties are not silently filled in.

Administrative reads included repository AGENTS.md, the literature/communication/
retrieval sections of docs/agent-contract-extended.md, the review-evidence skill,
and tools/check_review_independence.py for the attestation schema. The fresh
software review uses the prospective SOURCE-API as its primary specification;
no external literature conclusion or novelty claim is made. Protected source
notes and prior-run memory were not consulted. The Coordinator retains the
broader literature/proof-fidelity work, visual report publication, native gate,
Git/archive and official decision responsibilities. The four-path write scope
was preserved; no standalone graph/PDF was written by this reviewer.

The native independence gate was **not run by this reviewer** and acceptance is
not prefilled. After sealing the four assigned artifacts, this reviewer stops
writing. Any later correction requires an additive review record under the
Coordinator's procedure.
