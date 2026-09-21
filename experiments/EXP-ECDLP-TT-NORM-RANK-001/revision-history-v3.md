# Revision history v3

V3 preserves v1 and v2. It changes only the rank-traffic model and bound:

1. Defines `P=c*r`, `E=c*r*(r-1)/2`, and `N=E+P` for each oriented unfolding.
2. Freezes materialization `2P`, monotone pivot scans `P`, elimination updates
   `3E`, normalization `2P`, and certificate reads `P`.
3. Replaces invalid v2 traffic `3N` with `T=3E+6P`.
4. Records aggregate `F_p` traffic 495573756 words and `F_p2` traffic 46024308
   words, giving 587622372 base-field-word equivalents per baseline path.
5. Charges pointer, pivot-index, JSON, timing, and process metadata separately.
6. Invalidates row copying or nonmonotone scans under this access model.

All mathematical, execution-matrix cross-product, mutation, comparator,
cohort, and interpretation decisions from v2 remain unchanged.

