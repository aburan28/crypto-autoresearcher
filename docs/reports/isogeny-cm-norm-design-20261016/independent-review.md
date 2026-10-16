# Independent pre-implementation review of the compact CM norm construction

Task: `TASK-20261016-3b4ca9`.

Native agent identity: `/root/frontier_coordinator_resume/cm_norm_independent_review`.

Review date: 2026-10-16, America/Los_Angeles.

The construction is mathematically sound under the explicit hypotheses below. Native implementation may proceed after incorporating this acceptance contract. Concrete-instance acceptance remains incomplete until a separately authorized, frozen execution produces and independently replays the arithmetic and evaluation receipts. This review does not promote official research state or admit a result to an existing full-map challenge.

This is an ordinary pre-implementation review of four assigned mathematical and verification-contract joints. I worked from the supplied definitions and retrieved mathematical sources, without reading a producer implementation, producer proof, or sibling review. No Lucas–Lehmer, Cornacchia, elliptic-curve evaluation, benchmark, or other scientific computation was executed. Repository access was read-only; this report was written only to the authorized temporary path for Coordinator archival.

The requested inference policy was `review-adversarial` with `xhigh` effort. The actual served model, actual served effort, and native runtime session UUID are not exposed to this reviewer. Those properties are unverified. No API call, alternate inference provider, model substitution, or fallback was used.

## 1. Geometric relation, dual, and degree

Fix the exact curve and field

\[
p=2^{256}-2^{32}-977,\qquad
E/\mathbf F_p:\ y^2=x^3+7,
\]

including its smooth projective completion and identity point \(O\). The verifier must establish that the field characteristic is prime, that \(p>3\), and that the discriminant is nonzero. For this model the discriminant is \(-16\cdot27\cdot7^2\), which is nonzero modulo the specified \(p\). The exact curve equation and full domain parameters must be bound to the certificate; a curve nickname is insufficient.

Let the supplied field element \(\beta\) satisfy

\[
0\le\beta<p,\qquad \beta^3=1\pmod p,\qquad \beta\ne1.
\]

Then \(\phi(x,y)=(\beta x,y)\), extended by \(\phi(O)=O\), is an automorphism of this curve fixing \(O\). It preserves the equation because \(\beta^3=1\); an automorphism fixing \(O\) is a group automorphism. It has \(\phi^3=1\) and \(\phi\ne1\).

The standard endomorphism-ring facts used here are: \(\operatorname{End}(E)\) has no zero divisors; the integer multiplication morphisms embed \(\mathbf Z\) injectively; duality is additive and fixes integer multiplication; and \(\gamma\widehat\gamma=[\deg\gamma]\). These facts hold in positive characteristic. They are stated in [Sutherland, 18.783 Fall 2023, Lecture 12, opening facts and §12.1](https://math.mit.edu/classes/18.783/2023/LectureNotes12.pdf).

Applying those facts independently gives

\[
(\phi-1)(\phi^2+\phi+1)=0,
\qquad\therefore\qquad \phi^2+\phi+1=0.
\]

Since \(\phi\) is an automorphism, \(\deg\phi=1\), so

\[
\widehat\phi=\phi^{-1}=\phi^2.
\]

For unreduced signed integers \(a,b\), define the endomorphism

\[
\alpha=[a]+[b]\phi.
\]

Its dual is

\[
\widehat\alpha=[a]+[b]\phi^2=[a-b]-[b]\phi.
\]

Hence

\[
\begin{aligned}
\alpha\widehat\alpha
&=([a]+[b]\phi)([a]+[b]\phi^2)\\
&=[a^2]+[ab](\phi+\phi^2)+[b^2]\phi^3\\
&=[a^2-ab+b^2].
\end{aligned}
\]

Comparison with the dual identity and injectivity of the integer multiplication morphisms proves

\[
\boxed{\deg\alpha=a^2-ab+b^2}.
\]

In characteristic \(p\), the morphism \([p]\) is nonzero and has degree \(p^2\). Thus characteristic \(p\) does not justify reducing these integer coefficients modulo \(p\). Rational subgroup order \(n\) likewise does not justify reducing them modulo \(n\) when identifying the geometric map or its degree.

The quadratic polynomial \(T^2+T+1\) is irreducible over \(\mathbf Q\), so the nontrivial automorphism has that minimal relation in the endomorphism algebra. No determination of the full endomorphism ring, ordinary/supersingular classification, or conductor is required for this particular degree argument.

Joint verdict: **holds**, for the exact geometric endomorphism expression and hypotheses above.

## 2. Exact symbolic certificate and its mathematical interpretation

The required integer polynomial identity is

\[
(a+bt)(a-b-bt)
=a^2-ab+b^2-b^2(t^2+t+1).
\]

Both sides expand over \(\mathbf Z\) to

\[
a^2-ab-b^2t-b^2t^2.
\]

The checker must verify exact equality of the integer coefficient maps, with explicit variable order and encoding. It then specializes \(t=\phi\) using the separately reviewed geometric endomorphism relation. The integer polynomial checker establishes the algebraic identity; the reviewed theorem supplies the interpretation of the specialized product as geometric degree.

An `identity.certificate/v1` evaluated over the field of order \(2^{61}-1\), including any `IDC1` evaluated evidence, is supplementary. It is not a proof of an identity over \(\mathbf Z\) and does not independently prove geometric degree. Even equality as polynomials after reduction modulo that field characteristic would miss an erroneous coefficient differing by a multiple of the characteristic.

Required controls are an altered sign or coefficient and an altered coefficient by \(2^{61}-1\). The exact integer identity check must reject both, including the latter when finite-field evaluations agree. Freeze the symbolic statement, input coefficients, exact checker source, and theorem reference in the map-certificate provenance.

## 3. Prime degree, separability, and rational subgroup action

On invariant differentials,

\[
\omega=\frac{dx}{2y},\qquad
\phi^*\omega=\beta\omega,\qquad
\alpha^*\omega=(a+b\beta)\omega.
\]

The final equality follows from additivity of the differential of a sum of group homomorphisms and the differential of signed integer multiplication. For nonzero \(\alpha\), the derivative multiplier is

\[
c=(a+b\beta)\bmod p,
\]

and separability is equivalent to \(c\ne0\). Independently verify

\[
(a+b\beta)(a+b\beta^2)\equiv a^2-ab+b^2\pmod p.
\]

Once the norm is proved equal to a prime \(\ell\ne p\), the right side is nonzero, so both derivative factors are nonzero. Alternatively, a nontrivial inseparable degree is a positive power of the characteristic and cannot divide such \(\ell\). The geometric kernel then has exactly \(\ell\) elements and is cyclic because its order is prime. These uses of inseparable degree and kernel cardinality are supported by [Sutherland, Lecture 5, Corollary 5.4 and Theorem 5.8](https://math.mit.edu/classes/18.783/2023/LectureNotes5.pdf).

For the target \(\ell=2^{8191}-1\), its 8,191-bit length exceeds the 256-bit characteristic. After primality has been established, \(\ell\ne p\) follows. Record the actual derivative multiplier and its modular product check as explicit receipts rather than relying only on this implication.

The rational subgroup obligations must be stated separately. Freeze the entire secp256k1 tuple \(p,E,G,n,h\), where

\[
n=\mathtt{FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141},
\qquad h=1.
\]

The exact standardized tuple is given in [SEC 2 v2, §2.4.1](https://www.secg.org/sec2-v2.pdf). A trusted standardized-parameter basis must be declared explicitly if used. If the deliverable instead claims self-contained arithmetic certification, it must carry independently checkable primality certificates for both \(p\) and \(n\), not only for \(\ell\).

A sufficient independently certified route to the full rational group order is:

1. Establish primality of \(p\) and \(n\).
2. Verify the exact \(G\) is on the specified curve, is not \(O\), and satisfies \([n]G=O\).
3. Verify by exact integer inequalities that the Hasse interval contains exactly one multiple of \(n\), namely \(n\).

Then \(G\) has order \(n\) and \(\#E(\mathbf F_p)=n\). Hasse's bound and the unique-multiple argument are given in [Sutherland, Lecture 7, Theorem 7.3 and §7.5](https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf).

If a scalar eigenvalue \(\lambda\) is declared, require

\[
0\le\lambda<n,\qquad
\lambda^2+\lambda+1\equiv0\pmod n,\qquad
[\lambda]G=\phi(G).
\]

The final equality must compare full points, including \(y\) and infinity handling. The quadratic congruence alone leaves two roots and does not pair one with the selected \(\beta\). Either nontrivial cube root \(\beta\) is valid, but its declared \(\lambda\) must match its action on \(G\).

After these checks, the restriction of \(\alpha\) to the rational subgroup is multiplication by

\[
k=(a+b\lambda)\bmod n.
\]

Require \(k\ne0\) and record an inverse modulo \(n\). Independently verify

\[
(a+b\lambda)(a+b\lambda^2)\equiv\ell\pmod n.
\]

When \(\ell\) is prime and \(\ell>n\), this is nonzero modulo prime \(n\), proving that the subgroup restriction is invertible. Field definition of the geometric map guarantees Frobenius stability of its kernel, not rationality of each kernel point. In this instance the rational kernel is trivial while the geometric kernel has \(\ell\) elements.

Joint verdict: **holds**, as a conditional mathematical statement with these source, primality, pairing, derivative, and subgroup hypotheses. The numerical receipts have not been executed or checked in this review.

## 4. Lucas–Lehmer and Cornacchia acceptance contract

Use distinct field names for characteristic \(p\), exponent \(e\), and geometric degree \(\ell\). Reconstruct the target from the exact exponent:

\[
e=8191,\qquad \ell=2^e-1.
\]

The degree must not be accepted merely because a supplied decimal or hexadecimal integer has the expected bit length.

Certify primality of exponent 8191 by exact deterministic trial division through \(\lfloor\sqrt{8191}\rfloor=90\); trial division by all integers from 2 through 90 is sufficient. Verify the square-root bound itself with integer inequalities. For Lucas–Lehmer, independently recompute

\[
s_0=4,\qquad s_{i+1}=(s_i^2-2)\bmod\ell
\]

for exactly \(e-2=8189\) transitions and require \(s_{8189}=0\). The selected acceptance theorem is [Keith Conrad, The Lucas–Lehmer Test, Theorem 2.2](https://kconrad.math.uconn.edu/blurbs/ugradnumthy/lucas-lehmer-test.pdf): for an odd prime exponent, this final zero is equivalent to primality of its Mersenne number. I retrieved and read that theorem and its proof directly. Once the odd-prime-exponent precondition and complete recurrence replay are established, intermediate GCD checks are not required by this selected theorem.

The earlier suggestion to require \(\gcd(s_i,\ell)=1\) for \(0\le i\le8188\) was conditional on using the particular formulation in [Gross, An elliptic curve test for Mersenne primes, §1, Proposition 1.3](https://people.math.harvard.edu/~gross/preprints/Mersenne.pdf). Under the now-selected Conrad theorem those 8,189 GCD checks are optional diagnostics, not an acceptance requirement or missing evidence. The implementation and frozen contract should cite Conrad's exact theorem and its preconditions consistently.

A certificate containing a reported final zero or digest is insufficient unless the verifier recomputes the recurrence. Full states or deterministic checkpoints may be retained for localization, but the replay must cover every transition and exact iteration count. Hashes bind artifacts and do not replace arithmetic verification.

Required LL controls:

- \(e=3\), \(M_3=7\): positive control accepted.
- \(e=11\), \(M_{11}=2047=23\cdot89\): prime-exponent precondition passes; LL primality acceptance fails. Exponent 11 is not a composite-exponent control.
- \(e=9\): reject the composite exponent before prime-exponent LL acceptance.
- An altered degree, recurrence value, terminal residue, or iteration count: reject.
- \(e=2\): either support explicitly as \(M_2=3\), or reject as outside a documented \(e\ge3\) implementation.

For Cornacchia, use \(d=3,m=\ell\). Verify the supplied root \(r^2\equiv-3\pmod\ell\), normalize it to \(\min(r,\ell-r)\), and replay the Euclidean chain until the first remainder \(x\) with \(x^2<\ell\). Every quotient and remainder must satisfy its exact division equation and remainder bounds. Check that \((\ell-x^2)/3\) is a nonnegative integer and an exact square \(y^2\). The algorithm and this stopping rule appear in [MIT 18.783 Fall 2025, Problem Set 2, Problem 1](https://math.mit.edu/classes/18.783/2025/ProblemSet2.pdf).

Acceptance requires

\[
x^2+3y^2=\ell,
\qquad a=x+y,\qquad b=2y,
\]

and an independent exact integer expansion of

\[
(x+y)^2-(x+y)(2y)+(2y)^2=x^2+3y^2=\ell.
\]

The canonical construction receipt may use \(x,y\ge0\), while the general endomorphism schema must preserve signed integer coefficients. For this target, if the primality and representation checks pass, \(x,y>0\) and \(\gcd(x,y)=1\). The congruence \(\ell\equiv7\pmod{12}\) further implies that \(x\) is even and \(y\) is odd; these are useful supplementary checks.

Reject wrong square roots, broken remainder equations, premature or late stopping, rounded square roots, nondivisible \(\ell-x^2\), and altered \(x,y,a,b\). A null return or resource failure is a construction failure in the recorded scope, not a mathematical nonexistence certificate.

The independent arithmetic verifier should use generic exact integer operations and its own recurrence/remainder replay rather than importing producer methods. If production uses a specialized Mersenne reduction, the independent verifier should use a distinct general modular reduction implementation. A fixed M8191 run must have its own frozen execution contract and native run receipt.

Joint verdict: **inconclusive** for the concrete target instance, because no LL or Cornacchia certificate was supplied or executed here. The proposed corrected verification contract is mathematically suitable to implement.

## 5. Independent point evaluation and the degree-alias control

Expose two distinct evaluator semantics:

1. A geometric-expression evaluator accepts the serialized unreduced signed integers and computes \([a]P+[b]\phi(P)\) using signed integer multiplication, with no subgroup-order reduction in its definition.
2. A rational-subgroup evaluator may compute \([k]P\), where \(k=(a+b\lambda)\bmod n\), only after establishing that the point lies in the stated subgroup.

The second is a subgroup optimization. Its scalar must never replace \((a,b)\) in the geometric map identity or degree certificate. Even when both implementations return identical rational-point outputs, their serialized objects and proof obligations differ.

Independent evaluation must use separately implemented group arithmetic or materially different formulas, without importing the producer's scalar-reduction or point-evaluation helpers. Include \(O\), \(G\), \(-G\), deterministic public known-scalar points, and negative and zero coefficient fixtures. Compare complete points. Verify curve membership of inputs and outputs, both compositions with the declared dual, group-law compatibility on the fixed check set, and signed-coefficient behavior. Invalid encodings and off-curve inputs must be rejected.

For the decisive control, define

\[
\alpha'=[a+n]+[b]\phi.
\]

Once \(\#E(\mathbf F_p)=n\) is certified, every rational point satisfies

\[
\alpha'(P)=\alpha(P).
\]

However,

\[
\deg\alpha'-\deg\alpha=n(2a-b+n).
\]

For canonical Cornacchia coefficients \(a=x+y,b=2y\), this becomes

\[
\boxed{\deg\alpha'-\deg\alpha=n(2x+n)>0}.
\]

The expected control outcome is therefore: rational-point comparisons pass, while a certificate pairing \((a+n,b)\) with the original degree \(\ell\) fails exact norm equality. A general expression checker may accept \(\alpha'\) with its recomputed degree; admission to a prime-degree category requires separate primality certification of that new degree.

For arbitrary signed coefficients, this particular shift can have zero degree difference when \(2a-b=-n\). A generic alias-control implementation must check that the chosen shift changes the norm, or choose another nonzero multiple of \(n\). The canonical Cornacchia control above avoids that corner case by its strict positive difference.

No number of comparisons on \(E(\mathbf F_p)\) distinguishes these two geometric maps. Similarly, full rational-point agreement of dual compositions is supplementary evidence and cannot replace the exact norm proof.

Joint verdict: **holds** for the mathematical evaluation contract and alias argument. No implementation-level evaluation or control pass is asserted.

## 6. Additional controls with required interpretations

| Control | Required acceptance or rejection rule |
|---|---|
| \(\beta=1\) | Reject the primitive-cube-root hypothesis. Here \(\phi=1\), and the actual degree is \((a+b)^2\). The CM norm formula cannot be applied. |
| Replace \(\beta\) by the other nontrivial cube root | Accept as a valid alternative expression after checking its declared eigenvalue pairing. A root choice alone is not a defect. |
| Keep \(\beta\), declare the other \(\lambda\) | Reject if \([\lambda]G\ne\phi(G)\), even though the quadratic congruence passes. |
| Alter \(\ell\) while keeping \(a,b\) | Reject exact norm equality regardless of point-test results. |
| Reduce \(a,b\) modulo \(n\) before computing geometric degree | Reject geometric-certificate semantics. |
| Alter an integer identity coefficient by \(2^{61}-1\) | Exact coefficient checker rejects even if evaluated finite-field evidence agrees. |
| Pure Frobenius \(\pi(x,y)=(x^p,y^p)\) | Its degree is prime \(p\), its derivative is zero, and its rational-point action is the identity. Reject a separability claim. |
| \(1-\pi\) | Its degree is \(n\), derivative is one, and rational-point action is zero. Reject subgroup invertibility; this map is separable. |

Frobenius and \(1-\pi\) exercise different errors. In particular, \(1-\pi\) is not an inseparability counterexample or an example of degree equal to the characteristic on this curve. The identities \(\ker(1-\pi)=E(\mathbf F_p)\), separability of \(1-\pi\), and \(\deg(1-\pi)=\#E(\mathbf F_p)\) are established in [Sutherland, Lecture 7, §§7.1–7.2](https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf).

If the implementation accepts only the compact CM expression schema, a Frobenius test must be represented through a separately certified expression in that schema, or explicitly recorded as a theorem-level control outside the executable schema. Do not claim an executable Frobenius control passed when the input type cannot represent it.

## 7. Concrete implementation and archival recommendation

Proceed with native implementation under the corrected contract. Require separately reported verdicts for:

- Exact domain and subgroup parameters, including the declared primality trust basis or replayable certificates.
- Exponent primality and complete Lucas–Lehmer replay.
- Cornacchia root, Euclidean replay, square test, and exact coefficient transformation.
- Exact integer polynomial identity and its reviewed geometric specialization.
- Geometric norm computed from the original signed integers.
- Derivative multiplier and separability.
- Beta/lambda pairing, subgroup action, and invertibility.
- Independently implemented point evaluation and dual checks.
- Each positive, negative, and alias control with its expected outcome.

Bind these receipts to the exact input serialization, unreduced coefficients, source revisions, commands, implementation identities, source and artifact hashes, environment, complete stdout/stderr, and measured resource records where execution occurs. Missing evidence remains incomplete. The pre-implementation review does not substitute for the subsequently frozen native `/run` of M8191 or its independent replay.

After all required receipts pass, the admissible mathematical deliverable is a compact known-endomorphism self-map representation with certified geometric prime degree. Its representation category and acceptance contract must remain separate from an existing challenge requiring expanded rational-map coefficients or a full kernel-polynomial artifact. A degree shared with that challenge does not establish artifact equivalence.

This construction does not establish a new algorithm, a worldwide record, a finite global maximum, a performance advantage, or a deployed-curve-security result. Any bounded comparison must name its frozen candidate set and representation category. Evaluation cost and construction cost need their own measurements if later claimed.

The Coordinator should archive this report with the task handoff and the required research diagram and PDF, then schedule the implementation and frozen execution as separate work. This reviewer did not generate those derivative archival artifacts, commit changes, open a PR, or alter official state; the assignment explicitly reserved repository writes and archival work to the Coordinator.

## 8. Provenance and machine-readable attestation

The load-bearing external references above were retrieved and read directly by this reviewer. Repository instructions and the review-attestation template were read. The review checker was read during preparation of this artifact to verify its verdict schema. In particular, a reviewer owning multiple joints should provide a mapping with one verdict per joint, and each value must be `holds`, `breaks`, or `inconclusive`.

The memory registry was consulted earlier for orientation about geometric degree versus rational subgroup behavior and historical artifact distinctions. No historical result is used as proof of the present construction or as a current status assertion. No rollout summary or producer mathematical artifact was opened. The path `agents/reviewer.md` was attempted but does not exist in the instructed checkout; the extant `agents/validator.md` supplied the reviewer responsibilities used here.

The checker `tools/check_review_independence.py` reads YAML documents, not Markdown fences. For mechanical archive checking, extract the following YAML block into the Coordinator-owned archived attestation YAML. This report does not assert that a plan/report composition check has already run or passed. The joint names below are the descriptive names used in the review assignment; the Coordinator must preserve an explicit mapping if the committed plan uses different identifiers rather than imply this reviewer read an unseen plan.

```yaml
review_attestation:
  task_id: TASK-20261016-3b4ca9
  native_agent_identity: /root/frontier_coordinator_resume/cm_norm_independent_review
  native_agent_session_id: unverified_not_exposed
  review_kind: pre_implementation_mathematics_and_verification_contract
  joints_owned:
    - phi_relation_dual_and_geometric_degree
    - prime_degree_separability_source_and_subgroup
    - lucas_lehmer_cornacchia_and_arithmetic_certificates
    - independent_point_evaluation_and_degree_alias_control
  verdicts:
    phi_relation_dual_and_geometric_degree: holds
    prime_degree_separability_source_and_subgroup: holds
    lucas_lehmer_cornacchia_and_arithmetic_certificates: inconclusive
    independent_point_evaluation_and_degree_alias_control: holds
  verdict_scope:
    phi_relation_dual_and_geometric_degree: Exact geometric expression with the stated hypotheses.
    prime_degree_separability_source_and_subgroup: Conditional theorem; numerical receipts remain unverified.
    lucas_lehmer_cornacchia_and_arithmetic_certificates: Corrected contract is suitable; concrete arithmetic instance has not been replayed.
    independent_point_evaluation_and_degree_alias_control: Mathematical contract and alias argument only; implementation execution is unverified.
  sources_read:
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/AGENTS.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/agents/validator.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/templates/research-records.md
    - /Volumes/SSD990-2/crypto-autoresearcher-isogeny-frontier-20261015/tools/check_review_independence.py
    - /Volumes/SSD990/.codex/memories/MEMORY.md
    - https://math.mit.edu/classes/18.783/2023/LectureNotes12.pdf
    - https://math.mit.edu/classes/18.783/2023/LectureNotes5.pdf
    - https://math.mit.edu/classes/18.783/2023/LectureNotes7.pdf
    - https://math.mit.edu/classes/18.783/2025/ProblemSet2.pdf
    - https://people.math.harvard.edu/~gross/preprints/Mersenne.pdf
    - https://kconrad.math.uconn.edu/blurbs/ugradnumthy/lucas-lehmer-test.pdf
    - https://www.secg.org/sec2-v2.pdf
  sources_read_scope:
    templates/research-records.md: Review-attestation section.
    tools/check_review_independence.py: Opening definitions, verdict extraction, YAML loading, and report collection; relevant symbol search.
    memory_registry: Orientation excerpts only; no current status reliance or load-bearing proof use.
    web_search_results: Discovery metadata and snippets were visible; mathematical support is the directly read primary sources listed above.
  source_provenance:
    mathematical_sources: retrieved
    verified_by: /root/frontier_coordinator_resume/cm_norm_independent_review
  read_sibling_reports: false
  blind_from_respected: true
  blindness_scope: No producer implementation, producer proof, or sibling report was read; definitions and Coordinator assignment and clarifications were supplied.
  producer_implementation_or_proof_read: false
  requested_policy: review-adversarial
  requested_effort: xhigh
  actual_served_model: unverified_not_exposed
  actual_served_effort: unverified_not_exposed
  provider_substitution_used: false
  scientific_runs_launched: false
  selected_ll_theorem: Keith Conrad, The Lucas-Lehmer Test, Theorem 2.2
  intermediate_ll_gcd_checks: optional_diagnostics_not_required_by_selected_theorem
  repository_modified: false
  recommendation: proceed_with_native_implementation_under_the_stated_corrections
  concrete_instance_acceptance: incomplete_pending_frozen_execution_and_independent_replay
  official_state_transition: none
```
