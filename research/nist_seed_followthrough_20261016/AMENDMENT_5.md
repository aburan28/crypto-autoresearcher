# Separate FreeLIP base-point positive controls

Recorded before the replay. The user-supplied Anthropic article provides a
complete FreeLIP `zrandom` recipe and six May 1997 examples. Independently
recompute those six x-coordinates using state modulo `2^107-1`, multiplier
`3^121`, seven discarded 26-bit outputs, and one more 26-bit limb than the
field width requires. At each candidate x, reduce modulo the published field
and accept the first x whose curve right-hand side is a nonzero quadratic
residue. Use the published fields and coefficients in the frozen target file.
The six fixed FreeLIP seeds are 20000, 20420, 20507, 20509, 20512, and
20517 for P-192, prime239v1–v3, prime192v2, and prime192v3 respectively.
Require exact x-coordinate and try-count agreement with the six published
examples and a changed x for each seed increased by one; keep a mismatch as a
failed control. Stop after 1000 candidate
coordinates per case. This validates the distinct positive-control generator
only; it does not identify the origin of the later four base points or add an
acceptance rule for the curve-seed stream.
