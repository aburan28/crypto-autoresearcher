# Arithmetic-validated prefix transcript adapter

`adapter.py` accepts the unchanged prefix transcript emitted by
`research/prime_sat_followup_20261029/encoding.py`. It checks every restricted
polynomial identity, returned model and supported domain before using the
existing sparse prefix trie to check projected-model completeness. It has no
expected-model census argument and invokes no SAT or polynomial search.

```python
verify_transcript(p, n, projected_bits, polynomials, domain_cnf, answer,
                  aux_bound=None)
verify_encoding_search(cell, arm, answer)
```

The generic API checks identities in `(Z/p)[b]/(b_i**2-b_i)`, for integer
`p >= 2`. It does not certify primality. Sparse monomial masks are canonical
nonnegative Python integers or decimal JSON strings; nonzero coefficients
must be canonical residues. Alias keys, malformed records, unsupported domain
clauses and duplicate model projections are rejected with `ValueError`.
Already decoded mappings cannot reveal duplicate identical textual JSON keys;
raw JSON parser integrity is outside this interface.

A learned cylinder is usable only after its multiplier identity equals one.
A returned model licenses a cylinder of its projected coordinates: this proves
coverage of projected solutions, not that every auxiliary assignment in that
cylinder is a root. The domain must be the full Boolean cube or the exact
legacy CNF excluding every auxiliary integer at or above `aux_bound` once.
The adapter validates clause shape, distinct values and cardinality without
enumerating omitted assignments. Arbitrary CNF is unsupported.

`valid` means all submitted records passed. `cover_complete` reports actual
coverage. `projected_model_set_complete` additionally requires declared status
`complete`; a censored transcript remains censored even if coverage closes.
An uncovered assignment is a coverage gap and need not be a polynomial root.

The EC wrapper rebuilds the named frozen encoding and reconstructs/checks
point witnesses. Its prime-field interpretation assumes mathematical
primality. It supports quartic, membership, quadratic and reversed quadratic
arms, retaining the target/non-singularity/domain conditions. Construction and
witness counters are separate from parsing, restriction, identity arithmetic,
model evaluation, domain validation and coverage counters. Historical solver
telemetry in the transcript is not authenticated.

Only the completeness phase removes the old explicit `2**n` exhaustion loop.
Certificate size, large range CNFs, membership truth tables, input/output bit
costs and witness reconstruction still matter. There is no measured speedup,
new degree bound, formal proof, scalar recovery or general ECDLP result here.

The prospective software contract fixes eight generic fixtures and one
`p=5,a=b=1,s=2,R=(0,1)` cell in all four arms. Only the test harness may
enumerate their tiny domains and compare directly with the old exhaustive
checker. It constructs leaf certificates without invoking any solver. Run:

```text
/home/ec2-user/prime-sat-research-venv/bin/python -B research/prime_sat_prefix_adapter_20261030/test_adapter.py --receipt research/prime_sat_prefix_adapter_20261030/producer-results.json
```

Actual attempts, outcomes and source hashes belong to `producer-results.json`;
independent acceptance requires the separate review task. The fixed n=256
constant-refutation case is a software fixture, not a 256-bit ECDLP attack.
Prior PNEXT status and artifacts remain unchanged.

Source and applicability notes are in
`coordination/prime_sat_prefix_adapter_20261030/source-notes.md`. The
[Saccomani et al. author paper](https://hanielbarbosa.com/papers/2026fmcad-ffproofs.pdf)
separates algebraic proof checking from branch completeness; the adapter uses
that standard distinction without claiming to implement or benchmark their
SMT system. Future arbitrary-trail propagation needs its own proof interface.
