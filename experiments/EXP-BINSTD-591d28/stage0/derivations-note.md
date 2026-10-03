# Derivations note — EXP-BINSTD-591d28

Predicted spurious factor at RC-1: m! * 2^{sum_k dim V^{(k)} - m l} with dim V^{(k)} = min(k(l-1)+1, n).

At l=4,5,6 (m=3,n=17): [3072.0, 24576.0, 196608.0] (log2 ≈ [11.585, 14.585, 17.585]).

n=131 excess unknowns at balanced cells:
- (m,l)=(5,23): sum_dims=335 vs ml=115 (excess 220)
- (m,l)=(5,28): sum_dims=405 vs ml=140 (excess 265)
- (m,l)=(6,22): sum_dims=447 vs ml=132 (excess 315)
- (m,l)=(6,24): sum_dims=481 vs ml=144 (excess 337)
- (m,l)=(8,20): sum_dims=667 vs ml=160 (excess 507)

Amazon Bedrock: NOT SELECTED.
