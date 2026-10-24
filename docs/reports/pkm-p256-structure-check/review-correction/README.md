# Qualification of the P-256 kernel-coset conclusion

This PR review correction qualifies the conclusion following Result 2 and the final suggested check in the [original report](../report.typ). The original source, PDF, diagram, arithmetic checker and output remain byte-identical; [original-artifacts.json](original-artifacts.json) binds those bytes to the reviewed commit. This correction makes no scientific status transition and authorizes no experiment.

For an elliptic curve E over F_p with prime rational group order n and a finite geometric subgroup K, any nonempty intersection (R + K) ∩ E(F_p) is a coset of K ∩ E(F_p). Indeed, choosing a rational point P in the intersection identifies it with P + (K ∩ E(F_p)) by subtraction. Its size therefore divides both |K| and n. If gcd(|K|, n) = 1, the intersection has at most one point. More generally, its size is either 0, 1 or n because n is prime.

The coprimality condition is essential. Take K = E(F_p): it has order n and is fixed by Frobenius, so the quotient E → E/K is a separable isogeny defined over F_p with kernel K. Its kernel coset K itself contains n rational points. The finite-subgroup quotient theorem and its field-of-definition statement are given in [Sutherland, Isogeny kernels and division polynomials, Theorem 6.11 and its following field-of-definition discussion](https://math.mit.edu/classes/18.783/2019/LectureNotes6.pdf). This supplies a mathematical counterexample to the unrestricted conclusion; it supplies no efficient decomposition algorithm or cost advantage.

The original conclusion remains valid for a kernel whose order is coprime to P-256's prime group order, including the proposed 2-power kernel and the listed small prime degrees. Supersingularity of the auxiliary curve and ordinarity of P-256 also continue to exclude an isogeny between those two curves. Coordinate-defined subsets of P-256 require separate analysis: the coset lemma does not classify them or settle their solver complexity.

The mutable problem note also separates a solution-count heuristic from a bound. The relation |V|^m ≈ p alone does not prove that restricting a summation polynomial to V^m yields O(2^m) rational solutions. Such an estimate requires a stated distribution model or an independent counting argument; that estimate is unresolved for an arbitrary structured V.

The [PR evidence-scope note](pr2424-evidence-scope.md) records statistical wording, degenerate-target counts and unavailable original crash-input files.

The author independently added [QUALIFICATION-20261019](../QUALIFICATION-20261019.typ) in commit `6954374bf1f2a488a3a8c471b6e347fa7eb0b4ce`. That qualification and its PDF/diagram are preserved; this review adds the explicit intersection proof, primary source and evidence-scope notes.
