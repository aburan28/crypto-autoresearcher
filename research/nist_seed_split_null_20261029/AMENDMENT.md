# Post-run amendment to PROTOCOL.md (count typo; no change to the test)

Written 2026-10-29 UTC after `heldout.py` ran. PROTOCOL.md says the held-out
population has "48 in the 192/224/239/256-bit fields". The label definition it
gives (`order_too_wide_only` or `opposite_root_only` in
`nist_seed_1997_acceptance_20261024/analysis.json`) selects **42** positions in
those fields (21 + 8 + 9 + 4) and 6 in P-384; 48 is the total including
P-384. The protocol's pair count, 21x3 + 8x1 + 9x3 + 4x1 = 102, is computed
from the correct 42 and matches the run. The population, statistic,
cutoff, null, permutation scheme, seed and decision rule are unchanged.
