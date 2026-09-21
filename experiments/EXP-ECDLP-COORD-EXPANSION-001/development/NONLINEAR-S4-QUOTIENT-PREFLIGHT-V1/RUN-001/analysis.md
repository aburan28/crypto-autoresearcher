# Nonlinear S4 Quotient Preflight V1: RUN-001

## Result

`SCOPED NEGATIVE`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The run built exact source-tagged nondecreasing `D2` and `D3` states for all
four registered coordinate families on three generated ordinary prime-field
curves. It compared each candidate with the same-curve `random_x` control in
216 degree/rank rows. The independent verifier replayed 12 cells and all 216
comparisons exactly; all five mutations were rejected.

No quotient signal passed the preregistered gate. Across every family and
curve, the `D3` feature-rank curve was the same:

`1, 3, 6, 9, 12, 15, 18, 21, 24` for degrees `0..8`.

The candidate support varied slightly, but no row combined at least 80% of
control support with a rank ratio at most 80%. This means the tested
low-degree affine coordinate spaces exhibit the expected algebraic growth,
not a family-specific nonlinear quotient.

## Accounting

- state levels: 24;
- point-add calls: 5,348;
- field inversions: 3,424;
- counted field multiplications: 13,696;
- producer wall time: 1.98 seconds;
- producer peak RSS: 27,279,360 bytes;
- verifier wall time: 2.08 seconds;
- verifier peak RSS: 27,181,056 bytes.

Every retained state includes the lexicographically first nondecreasing
source witness. The state and witness digests are part of the raw result and
are replayed independently.

## Interpretation

This is a negative result for the tested low-degree coordinate-state quotient,
not for all nonlinear composition towers. It does not test target-conditioned
complement lookup, higher-degree implicit resultants, elliptic-net divisors,
or batch-specific state compression. It also does not establish a generic
lower bound or say that prime-field ECDLP cannot improve.

The next useful branch is a target-conditioned nonlinear operator: take the
exact source-tagged D2/D3 state and test whether a quotient retains a cheap
complement lookup and complete witness lift. The strict gate must include
state construction, target work, memory, relation rank, and descent.

## Evidence hashes

- contract: `04a0cbece5fefc95195875e4641b7fb1d6ed90f2515f60b4b1f3ea4ef2fb1575`
- producer: `d4874122d343309dcc2c795d551df620e49a9b9edb8bdaa0f087004dbfe0916d`
- verifier: `ed8cd66913796af8ec45c9b7be65daf7187e4a8229de86e2f1929bb26ba2568f`
- immutable input: `c7476f8aeff640ea2690c70218252186a8c657bf1d6db76baa01c55e2289fa3c`
- raw result: `db9bcdc0b67af70ab4e4c0917da3fc99e47d2d5ed00fac3f1e0b4e53653b7a36`
- verification: `9d5ccffe44d83df14ee3390d8564a8fc5f2d625caba3956d0e379ecded188189`
- producer stderr: `cc4924dd44b9061628f315c58017dabbd2542aa9ba064b8f62df43299107dd1a`
- verifier stderr: `2b4e33818a1c5c898d149925dd5dbb5cf960ff4358e8d0472978b8c4288c225f`
