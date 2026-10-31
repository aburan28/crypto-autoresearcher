# J1 review: archived equations and source-to-Lean representation

**Task:** Conductor T-1060, lease epoch 1. **Joint:** J1 only. **Disposition:** the archived draw, S3 component equations, Boolean parity row construction, and literal Lean source bridge pass the checks below for this one finite witness. This is a source and representation finding, not a Lean theorem or generic first-fall verdict.

## Frozen inputs and method

I read the review plan and input bindings from published merge `a1f3d0fde48d8a09301d65f8b8056f3cf42fc307`, then used an isolated worktree at source commit `ad91212179e737d829076ca593d608261590ba89`. All 14 bound files matched their declared byte counts and SHA-256 digests. The archive `draws.json` hashes to `f2c0bd08739c56f0dc24a3a67e4ab367319944c7a7868aef8c67508ac1ef13b2`. There is exactly one record for `(n,nprime,draw,seed,xR,basis)=(4,4,1,32201,1,[9,3,2,12])`. Its four ordered component lists serialize with compact JSON to SHA-256 `89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb`.

The paper's characteristic-two formula is `S3(x1,x2,x3)=(x1*x2+x1*x3+x2*x3)^2+x1*x2*x3+a6` (full text, lines 181–185). With `x3=1`, `a6=1`, `F2[X]/(X^4+X+1)`, and the archived basis, I evaluated all 256 assignments, then used a Möbius transform to derive each Boolean ANF. The four **ordered** monomial lists equal the archived lists, and the archived lists equal the literal `equations` in `BooleanParityFiniteCertificate.lean`. All 15 nonzero field elements have inverses under the reviewed multiplier. The curve record has `a2=a6=1`; `a2` does not occur in this S3 formula.

I independently regenerated compatible monomial multiples in the Lean source order: equation index first, multiplier mask `0..255` second; Boolean multiplication uses monomial-mask OR and coefficient XOR. This gave 28 degree-two and 80 degree-three rows, with binary ranks 11 and 53. `comboMask=1321682796735964` selects 23 row indices: `2,3,4,6,7,8,10,11,13,14,15,17,19,20,23,24,30,36,41,44,45,47,50`. Their XOR is the literal Lean `witnessNat=6277101735386703064921270320751746415339343215057222047510`. Its nonzero monomial masks are `1,2,4,8,9,10,12,16,18,20,32,40,48,64,65,128,144,192`; each has degree at most two. The coefficient functional `c80+c192` vanishes on every degree-two row and equals one on this vector. Adjoining it raises the degree-two rank from 11 to 12.

## Controls

- Mutating the archive's first component monomial `0` to `3` in a disposable copy made the source-binding checker exit 1 at its equation-hash assertion. The mutated source was discarded after saving [the control receipt](raw/mutation-control.json).
- The archived set-product operation, substituted for XOR parity on equation 0 times monomial mask 1, retains three extra masks: `1,17,129`. The regenerated XOR row differs, as required.
- The producer's source-binding checker was rerun with Python 3.11 and its [output](raw/source-binding-rerun.json) was byte identical to the committed receipt. The independent [J1 audit](raw/j1-audit.json) includes the ordered equations, selected rows, hash checks, and both controls.

## Scope and limits

This review covers the archived draw identity, the paper-to-ANF arithmetic for the stated field/basis, the literal finite Lean equation list, the source order and parity semantics of compatible rows, and the particular selected-row witness. I read no J2/J3 report or receipt. I launched no Lean, Lake, Cargo, scientific trial, or cloud resource. The fresh exact-source Lean build, transitive axiom audit, and theorem semantic boundary belong to J2. Blind discovery of an independent low-degree class belongs to J3. This report supports only the one-draw source bridge; the Coordinator composes the joint verdict after all reports are frozen.

The worktree was created with no checkout and only bound source paths were materialized. The exact read inventory is in [the audit JSON](raw/j1-audit.json); the [attestation](ATTESTATION.json) binds this review and its raw outputs.
