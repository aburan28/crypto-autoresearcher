# E3 projective section preparation

Engineering preparation for `IDEA-20261009-581f5d` / `H-ECDLP-af796a`. This is not an approved scientific trial, a rank certificate, a blind solver, or a speed claim. The existing frozen stage-0 implementation and its records are unchanged.

For a supplied short Weierstrass model with `deg A <= 4 chi`, `deg B <= 6 chi`, the encoder uses

```
Y(t)^2 = X(t)^3 + A(t) X(t) Z(t)^4 + B(t) Z(t)^6
x = X / Z^2,   y = Y / Z^3
deg X <= 2(D + chi),   deg Y <= 3(D + chi),   deg Z = e <= D.
```

Each chart makes `Z` monic. The search must include every `e = 0,...,D` and every `D` up to the encoding bound. The zero section is excluded from these charts; it cannot count as a kernel relation. Bezout equations `X U + Z V = 1` enforce finite primitivity, with `deg U < e` and `deg V < 2(D+chi)`. For `e < D`, an extra inverse witness enforces a nonzero leading coefficient of `X`, preventing a common weighted factor at base infinity. These auxiliary variables are part of the solver system and its cost.

At a smooth finite fibre, an affine target imposes `X(t0)=x_R Z(t0)^2`, `Y(t0)=y_R Z(t0)^3` and an inverse witness for `Z(t0)`. An identity target imposes `Z(t0)=0`. At infinity, the local coordinates are the top coefficients for degrees `2(D+chi)`, `3(D+chi)`, and `D`; the encoder distinguishes affine and identity charts there too.

**D is an encoding degree.** Interpreting it as the intersection degree with the zero section needs the stated global Weierstrass-model hypotheses. This component does not certify model minimality, the supplied `chi`, local height corrections, canonical height, or a height-to-D conversion. It makes no uniqueness assertion. Primary coefficient count is `5(D+chi)+e+2`; saturation witnesses and target conditions add to that count. The exact equation-degree list is available in `system.metadata` for a future matched control.

`kernel_recovery.py` separately checks supplied integer coordinates, every relation's image, full integer rank, **index exactly ell**, quotient calibration, and final scalar recovery in a certified cyclic prime-order toy subgroup. It rejects a full-rank proper sublattice. This is a verifier for supplied vectors: it does not find sections, recover their MW coordinates, certify a MW basis, or find a full kernel cheaply.

The 13 deterministic software fixtures include a rational section obtained by doubling `(1,t)` on `y^2=x^3+t*x+t^2-t-1` over `F_31(t)`, its identity specialization, a base inversion with identity specialization at infinity, and a known-answer `F_17` group of order 19. Sage's group law checks the section formula. All fixture scalars are public inputs. `fixture-checks.json` records source hashes, commands and literal outcomes; it is not independent scientific review.

Development failures are retained: the first direct Python import lacked a writable Sage cache; the second lacked the activated Singular environment; the third correctly rejected an inadvertently chosen singular target fibre at `t=1`. The final fixtures use the smooth target `t=2`. These logs are development history, not failed mathematical hypotheses or benchmark measurements; their earlier source revisions were not separately archived.

Recheck the unchanged fixtures through the locked environment (from this directory):

```sh
PIXI_HOME=/workspace/snfs-toolchains/pixi-home \
PIXI_CACHE_DIR=/workspace/snfs-toolchains/pixi-cache \
XDG_CACHE_HOME=/workspace/snfs-toolchains/cache \
XDG_CONFIG_HOME=/workspace/snfs-toolchains/config \
DOT_SAGE=/workspace/snfs-toolchains/sage-state \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
/workspace/snfs-toolchains/bin/pixi run \
  --manifest-path /workspace/snfs-toolchains/sage-pixi/pixi.toml \
  python -m unittest -v test_section_encoding test_kernel_recovery
```

Next scientific protocol: freeze the surface before target selection; specify every denominator chart and saturation variable; separate random targets from planted/oracle inputs; include coefficient-system construction, solver failures, section verification, integer-coordinate recovery, kernel index and final scalar verification in the complete-operation boundary. Certify the height convention and specialization coverage before selecting sizes from E4. The component does not authorize that protocol.
