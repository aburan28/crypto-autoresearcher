# Independent Theory Review: Asymmetric Layers V1

## Handoff: `2A+3R` theory boundary

### Claim or task

Verify the typed optimization, support, fitted exponents, rho boundary, rank,
and obligations for a coordinate `3R` compiler.

### Status

`REVISE`.

Review pinned to commit
`10214c603a8b7d6869c0b457c2f96b9235456982`. Recorded hashes, tables,
regressions, and deterministic replay match. No files were edited by the
reviewer.

### Evidence

For fixed occupancy `lambda`, minimizing `a+r` subject to

`(2a-1)*binomial(r+2,3) >= lambda*q`

gives

- `a=(lambda*q/9)^(1/4)+O(1)`;
- `r=(9*lambda*q)^(1/4)+O(1)`;
- `r/a -> 3`;
- `a+r=4*(lambda*q/9)^(1/4)+O(1)`.

The optimizer is globally correct for all eight tested cells. Median exact
coverage `0.405–0.464` is consistent with random occupancy. Reported fits
reproduce exactly, but `D2` and scan slopes are staircase-sensitive; `1/4`
is a derived design exponent, not an empirically established asymptotic.

Explicit materialization has setup/storage `q^(3/4)`, relation collection
`q^(1/2)`, and ordinary sparse linear algebra `q^(1/2)`. It is therefore not
a rho improvement.

Every row contains exactly two A coefficients and three R coefficients, so

`(3*1_A, -2*1_R)`

is an exact right-kernel vector. Rank is at most `a+r-1`. A successor must
quotient the gauge, anchor a log, treat A as known-log scaffolding, or add a
second relation type.

### Strongest valid conclusion

`OBSERVATION`: the scalar cyclic construction preserves constant five-term
coverage while reducing the split scan to the designed `q^(1/4)`.

`RESTRICTED THEOREM`: explicit materialization does not improve rho in the
charged table model, and the typed row matrix has the stated kernel.

### Next concrete action

Use a point-only coordinate successor with exact witnesses, quotient rank,
held-out descent, and complete build/advice accounting. Call the design a
structural candidate conditional on a rank fix and compressed compiler, not
a viable attack.

