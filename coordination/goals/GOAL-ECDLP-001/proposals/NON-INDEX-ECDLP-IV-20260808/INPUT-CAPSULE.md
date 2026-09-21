# Prime-field non-generic hardness census

## Research question

`RQ-ECDLP-165d4b` asks whether ordinary prime-field ECDLP instances can carry
public, efficiently usable structure that survives matched controls and lowers
the charged cost of solving a large prime subgroup.

## Prior evidence used as a boundary, not as a conclusion

- `L4_endo_transfer_validation.json` tested forward/inverse transfer with an
  overhead-inclusive toy-field model. It did not test Pollard-rho orbit
  quotienting by a subgroup automorphism.
- `L6_special_structure_scan.json` reports `control_matching_preserved: false`,
  so its repeated-j observation is not admissible closure of the special-j
  question.
- `L6_endo_chain_stability_scan.json` records coarse automorphism and torsion
  counts but not field-of-definition, subgroup eigenvalue, or quotient-rho
  collision cost.

These artifacts motivate the successor design; none is reinterpreted here as
positive or negative evidence outside its declared scope.

## Fixed comparison object

For every primary instance, the solver receives `(E, F_p, P, Q, ell)` with
`Q = xP`, where `ell` is prime and all certificates are independently checked.
The random scalar `x` is uniform and never exposed to the solver. Every
candidate algorithm must return a certificate that recomputes `Q = xP`.

## Two arms

### Arm A — automorphism-quotiented rho

Compare ordinary rho, rho modulo negation, and rho modulo the maximal verified
`F_p`-defined automorphism subgroup. Record the quotient orbit size, eigenvalue
action on `P`, fruitless cycles, collision recovery, and all automorphism costs.

### Arm B — isogeny-class transfer

Search only bounded-degree, explicitly computable `F_p`-rational neighbors. Map
`P` and `Q`, solve on the target using the Arm-A quotient policy, map the answer
back, and charge construction, forward, inverse, serialization, and failed-path
costs. Include a null map of the same degree/representation shape and a
same-order random target control.

## Scale ceiling

The first runs are toy/medium calibration only. They may validate code,
controls, and scaling diagnostics; they cannot support a cryptographic-scale
ECDLP claim. Any slope estimate must use held-out sizes and be reported with
the finite-size caveat.
