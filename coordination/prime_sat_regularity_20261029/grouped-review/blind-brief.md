# Blind grouped-indicator problem

This is a fresh, blind-only theory review. Do not read producer notes or candidate bounds. No later unblinding occurs within this TASK. Read only this brief, its adjacent review-plan, your own handoff/inference declaration, AGENTS.md, and the allowed primary sources below. No scientific runs, numerical sweeps, solver calls or benchmark claims.

Start with an arbitrary Boolean polynomial system over a field k, using equations b_i^2-b_i=0. Partition the bits into groups of actual widths w_g>=1. For a group of width w, introduce one variable u_a for each nonzero binary word a of that width. Impose u_a^2-u_a=0 and u_a u_b=0 for distinct nonzero words a,b. The all-zero indicator vector is permitted. Project each bit b_j to the sum of u_a over words whose j-th bit is one, and replace the original system using this linear projection. Independently construct an inverse, determine all field restrictions, count variables/equations, prove or refute exact solution correspondence, and state the appropriate relationship between ideals in the different rings.

Derive the local highest-part quotient, its Hilbert series and its vanishing threshold, then infer only justified conclusions for the full substituted generating system. Analyze true shortened final groups and the specialization of two coordinates with s bits each grouped in pairs. Distinguish the local quotient from the full quotient and a bound from equality. Independently determine whether the full-system bound is sharp, proving nonvanishing if possible. Analyze the raw substituted S3 polynomial and a version reduced by local relations as distinct generating lists; do not assume equal affine ideals have equal generating-system regularity. Charge the representation cost if the group width grows.

For an elliptic comparison, let p>max(3,s), s>=2, and use a nonsingular y^2=x^3+A*x+B over F_p with a finite rational target R=(r,t), t!=0. Set x=h_x+sum_j alpha_j b_j and y=h_y+sum_j beta_j c_j with nonzero original weights, and substitute into

S3(x,y,r)=(x-y)^2*r^2-2*((x+y)*(x*y+A)+2*B)*r+(x*y-A)^2-4*B*(x+y).

Use explicit Boolean equations and this constraint as the original generating list; compare with the indicator substitution. Independently derive the original baseline threshold if possible, including both vanishing and nonvanishing sides. Do not assume a strict comparison if you cannot prove the baseline. The grouped construction must be analyzed independently of any special-curve or membership-table hypothesis.

Allowed primary sources:
- https://arxiv.org/html/2112.05579 : Definition1.4 and its distinctions between degree of regularity and other invariants.
- https://arxiv.org/html/2211.13548 : Theorem2.7 for the square-zero block algebra; verify hypotheses before any weighted or tensor application.
- https://arxiv.org/html/2304.13485 : Definition2.5 and Proposition3.10 in full. Independently derive any applicable solving-degree upper bound from your proved degree bound and the actual maximum input degree. Identify the exact mutant-closure/degree-compatible convention and whether any strict comparison with the original system is established.

Do not infer a runtime advantage, general ECDLP speedup, novelty, or efficient algorithm from a degree bound alone. Record widths, representation, reconstruction, matrix-size and circuit-encoding limitations. Follow every joint/control in the plan. No producer proof or previous reviewer output may be consulted.

Your task is TASK-20261029-9c92f8. Write `research/prime_sat_regularity_20261029/TASK-20261029-9c92f8/blind-review.md` and `research/prime_sat_regularity_20261029/TASK-20261029-9c92f8/attestation.yaml`. The latter must contain `review_attestation` with task_id, role reviewer, all assigned joints_owned, a verdicts mapping with honest holds/breaks/inconclusive entries, read_sibling_reports false, sources_read recording actual exact files/URLs, blind_from_respected true only if true, and actual session/runtime/model/effort. Do not fabricate a completion or prefill a verdict. Root archives the actual outputs before Coordinator synthesis; you do not read the producer even afterward under this task.
