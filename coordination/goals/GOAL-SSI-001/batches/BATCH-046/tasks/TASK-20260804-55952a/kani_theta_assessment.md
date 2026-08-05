# Kani/Theta Assessment for Pure Path-Finding

**Verdict**: NO — does not offer sub-p^{1/3} for pure supersingular path-finding  
**Named obstruction**: Torsion-image input-dependence barrier

## Core argument

Kani's reducibility criterion converts action-on-torsion constraints into
computable product decompositions. Pure path-finding provides NO torsion data.
Without it, applying Kani introduces a higher-dimensional search space with no
new constraints, and search cost ≥ the original problem.

## Why the SIDH break doesn't transfer

- SIDH break: torsion images SELECT the kernel K from an exponential space
- Pure path-finding: no torsion images → no kernel selection → exponential search
- Every constructive use of Kani requires torsion images OR the endomorphism ring

## Search cost analysis (without torsion)

For product isogenies (E₁ × E') → (E₂ × E''):
- Valid kernels yielding E₂ as first factor: ~N² out of ~N⁴ total
- Search cost: ~N² isogeny computations
- For Wesolowski-scale N ~ p^{1/3}: cost ~p^{2/3} (worse than p^{1/3})

## Conclusion

Kani/theta is a REPRESENTATION tool (manipulating known algebraic structure),
not a DISCOVERY tool (finding unknown isogenies). It becomes constructive only
when external data resolves the existential quantifier in Kani's theorem.
The pure path-finding problem provides no such data.

This closes the Kani/theta angle for GOAL-SSI-001.
