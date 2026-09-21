# Direct five-source TT red-team v1

## Handoff: frozen preflight v1 red-team

### Claim or task

Audit frozen `preflight-v1.md` at SHA256
`5db581dae9305fe43190f766ac3a450bd17830adeaab0c1118859988cb52c720`
for exactness, circularity, exceptional projective behavior, multiplicity,
relation yield, and displaced advice.

### Status

`REVISE`.

The equality scalar, finite-field indicator, final cut-rank theorem, and generic
entry-oracle obstruction are mathematically sound within their stated models.
Four repairs remain. No implementation is authorized.

### Assumptions

- A `GO` would approve only the paper preflight, not implementation or an
  ECDLP claim.
- Relation yield uses canonical signed factor-base variables, not ordered tuple
  multiplicity or duplicate labels.
- Fixed-curve online, amortized preprocessing, and single-instance comparisons
  are distinct claim tiers.

### Evidence so far

- `g_Q=e_X+omega*e_Y` is exact whenever every addition returns a valid nonzero
  representative on the stated cubic.
- A fixed polynomial addition circuit gives a `B`-independent pre-indicator
  CP-rank upper bound.
- The Fermat indicator is exact, while its Hadamard chain may have large
  intermediate ranks.
- `rho_k(Zcal_Q)=m_(k,Q)` is correct even with repeated indices and duplicate
  point representations.
- The entry-oracle argument correctly shows that low final rank does not reveal
  unknown sparse support.
- If any intermediate central rank is `Omega(B)`, standard dense TT cores
  already require `Omega(B^2)` words: `rho_2<=B*rho_1` gives
  `B*rho_1*rho_2>=rho_2^2`, and symmetrically at cut three. This is a
  representation gate for dense cores, not a universal circuit lower bound.

### Failure modes

1. **Complete addition remains an oracle in v1.** Bind an actual formula,
   coordinate convention, curve preconditions, and addition tree. Prove
   nonzero on-curve outputs for identity, inverse pairs, doubling, repeated
   IDs, and every intermediate identity. Until then label the construction
   assumption `UNTESTED`.
2. **Target multiplicity can create a false continuation signal.** Preregister
   uniform no-hit, one-canonical-witness, many-witness, `Q=O`, repetition, and
   duplicate-label classes. Define support
   `epsilon=|D5|/q`, canonical signed relation rows, and rank-increment yield
   `eta_r`. Ordered permutations and duplicate labels do not count as
   independent relations.
3. **Preprocessing work is ungated.** Report and gate preprocessing operations,
   writes, traffic, peak workspace, amortized target count, and crossover
   against an equal-advice D2+D3 comparator.
4. **Final storage shorthand is incomplete.** Require

   ```text
   rho_1+rho_1*rho_2+rho_2*rho_3
        +rho_3*rho_4+rho_4=o(B)
   ```

   for every target class, as well as cumulative intermediate gates.

No universal intermediate-rank lower bound has been established. Large ranks
are the likely fatal obstruction for the specified indicator chain, not a
theorem about every coordinate-specific compiler.

### Next concrete action

Create v2 with these four repairs and a gate-by-gate central-rank ledger for one
bound complete-formula indicator circuit; stop before source code if any
intermediate central rank reaches `Omega(B)` in the dense TT interface.

### Artifact paths

- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/preflight-v1.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/object-dimension-ledger.md`
- `experiments/EXP-ECDLP-TT-ZERO-LOCATOR-001/research-question.json`
