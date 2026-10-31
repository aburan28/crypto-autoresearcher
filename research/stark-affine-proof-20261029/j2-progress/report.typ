#set page(paper: "us-letter", margin: 0.55in)
#set text(size: 10pt)
#set par(leading: 0.5em)
= Affine STARK proof: J2 findings and repair
T-781 / TASK-20261029-4cdb4c · 2026-10-29 · PR #2681

#image("proof-boundary.svg", width: 100%)

== Observations
The independent J2 reviewer compared six numbered propositions with their archived native Lean types at producer snapshot `d4f1279102709518247f5a7d1926de354fe5929a`. All six correspondences hold within their ring-valued scope. All 29 independently authored binding checks passed. The review and attestation are archived without edits under `reviewers/TASK-20261029-55585f/`.

The historical native evidence is run 40818135384, attempt 1, formal job 123264478731, synthetic merge `5e78a55ab310a98090fdc0592112f3e554a803f0`. Its source predates the current controls and seventh theorem. Passing that run does not certify the changed module.

== Finding and candidate correction
J2-F1: the Rust comment rules out agreement with multiplication at four designated points. The original exported theorem rules out agreement everywhere. Its proof uses those four points, but its type does not export the stronger finite-point assertion.

The proposed seventh declaration, `multiplication_not_affine_on_four_probes`, explicitly negates the conjunction of agreement at (0,0), (1,0), (0,1), and (1,1), for every coefficient triple over a nontrivial commutative ring. Its candidate proof forces c, a, b to zero and contradicts 0 ≠ 1. A second negative application over ZMod 1 must fail specifically because Nontrivial cannot be synthesized.

J2-F2: the original input manifest binds historical bytes. It is preserved; `inputs-v2.json` binds the successor source and plan. Old receipts are not relabeled current.

== Current verdict and next checks
Current module: *not_verified*. Claim 7 fidelity: *not_reviewed*. Complete-packet outcome: *inconclusive*. Collect the new native build, all seven explicit types and axiom outputs, and both negative-control diagnostics. Obtain the updated J2 comparison and independent J3 boundary review before completing the packet.

== Limitations and graph scope
No Rust arithmetic refinement, byte encoding or fingerprint injectivity, complete AIR identity, STARK soundness, historical execution or performance result is established by these identities. This diagram records proof obligations; no canonical performance graph changes are justified. Exact source and review hashes are recorded beside this report.
