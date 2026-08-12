# Briefing: Teske trapdoor systems and a prime-field ECDLP research target

**Source:** Secondary analysis (ChatGPT Pro, 2026-07-31) of Edlyn Teske, “An Elliptic Curve Trapdoor System,” plus related literature.  
**Status:** Unverified synthesis. Every paper claim below must be checked against primary sources before experiment design.  
**Goal binding:** `GOAL-ECTD-001` / `RQ-ECTD-001`.

## Anchor construction (Teske)

Teske’s trapdoor is a secret, efficiently evaluable isogeny connecting a public curve \(E_{\mathrm{pub}}\) to a curve \(E_s\) on which the GHS Weil-descent attack converts ECDLP into a feasible hyperelliptic-Jacobian DLP. The published construction works over \(\mathbb{F}_{2^{161}}\), not a generic prime field.

## Closest literature (to verify and file as KN-LIT)

Approach-adjacent:

1. Gaudry–Hess–Smart — constructive/destructive Weil descent (GHS engine).
2. Galbraith–Hess–Smart — extending GHS via isogenies to a GHS-weak curve in the same class (closest attack architecture to Teske).
3. Galbraith — constructing isogenies between elliptic curves over finite fields (ordinary \(\mathbb{F}_p\) translation; hard when endomorphism-ring index contains a large prime).
4. Jao–Miller–Venkatesan — GRH expander evidence that ECDLP difficulty is nearly uniform across an endomorphism-ring level; weakness must be sparse / cross-level.
5. De Feo — modern weak-class / MITM path-to-weak-curve description (\(\approx O(\#E^{1/4})\) threat model for trapdoor secrecy).

Hidden-capability / trapdoor analogues:

6. Dent–Galbraith — hidden pairings and trapdoor DDH groups (hide an extra representation/operation).
7. Kutas–Petit–Silva — trapdoor DDH from pairings and isogenies (weaker than full trapdoor ECDLP; nearer existing constructions).
8. Fried–Gaudry–Heninger–Thomé — kilobit hidden-SNFS discrete log (parameter-level trapdoor gold standard: ordinary-looking public params, hidden algebraic representation, private precomputation, cheap individual logs, no obvious detector).
9. Jacobson–Kushwaha — removable weak keys (key-level, not curve-universal, baseline).

Already partially present in this corpus:

- `KN-LIT-007` Gaudry–Hess–Smart
- `KN-LIT-3748` Extending the GHS Weil Descent Attack
- `KN-LIT-7261` Teske “Trapdooring with Isogenies” (title-only stub; local `downloads/teske.pdf` missing as of 2026-07-31)
- `KN-LIT-5102` New Constructions and Applications of Trapdoor DDH Groups (Seurin; cites Dent–Galbraith)

## Why Teske does not directly transfer to generic \(\mathbb{F}_p\)

Within one ordinary isogeny class over the same \(\mathbb{F}_p\):

- trace and group order are identical → smooth-order, anomalous, and MOV/Frey–Rück embedding degree are class invariants;
- \(\mathbb{F}_p\) has no proper subfields → GHS-style descent to a smaller base field is unavailable;
- a secret isogeny therefore cannot move a secure-order prime-field curve to a secretly anomalous / low-embedding / smooth-order curve;
- endomorphism rings differ by conductor within one imaginary quadratic field; a secret endomorphism can give GLV-style constant-factor rho speedups, not a qualitative sub-\(\sqrt{r}\) trapdoor by itself.

## Promising research target (hypothesis shape, not a result)

Most faithful Teske analogue:

\[
\mathrm{Gen}(1^\lambda) \mapsto (p, E_s, E_{\mathrm{pub}}, \phi, \tau_{\mathrm{solver}})
\]

where \(E_s/\mathbb{F}_p\) has an unusually efficient endpoint-specific ECDLP solver, \(E_{\mathrm{pub}}\) has the same order and looks generic, \(\phi: E_s \to E_{\mathrm{pub}}\) is a long composition of small-degree isogenies (degree coprime to the large subgroup order), and recovering an equivalent public path is harder than Pollard rho.

Missing ingredient: a prime-field weakness that varies dramatically between isogenous curves (not a class invariant).

### Candidate endpoint weaknesses (priority order)

1. **Secret isogeny-aligned factor bases** — \(E_s\) + structured \(B_s\) with anomalously dense Semaev relations / lower Gröbner complexity; trapdoor is \((E_s, \hat\phi, B_s, \) relation precomputation\()\), not a transparently weak public equation.
2. **Large-conductor vertical trapdoor** — \(E_{\mathrm{pub}}\) and \(E_s\) at different volcano levels with large prime in the endomorphism-ring index (Galbraith’s incomplete-equivalence boundary); needs more than GLV at the maximal-order endpoint.
3. **Hidden correspondence** to another algebraic group (Jacobian, disguised restriction of scalars, torus, privately evaluable CM module) — Dent–Galbraith model.
4. **Trapdoor DDH first** — private DDH/pairing oracle + Brown–Gallant/Cheon-style auxiliary-input acceleration; weaker than universal ECDLP trapdoor but closer to existing constructions.

### Deprioritize

- Hiding anomalous / low embedding degree / smooth order / supersingular endpoint behind an \(\mathbb{F}_p\)-isogeny (public class invariants).
- Secret GLV/CM endomorphism alone (plausible \(2\times\)–\(4\times\), not Teske-class).

## Concrete experimental program (toy, ~40–80 bits)

1. Generate ordinary prime-field isogeny classes with several conductor structures, especially when \([\mathcal{O}_K:\mathbb{Z}[\pi]]\) has a moderately large prime factor.
2. Enumerate horizontal/vertical neighborhoods for \(\ell \in \{2,3,5,7,11,13\}\); retain full path information.
3. Per curve measure: End/conductor; Semaev relation density \(m=3,\ldots,8\); FB decomposition probability; Gröbner \(d_{\mathrm{reg}}\); elimination / first-fall; Macaulay rank defects / syzygies; maps to low-genus curves; cost of evaluable endomorphisms.
4. Search for **heavy-tailed outliers**, not small average improvements. Meaningful endpoints should be orders of magnitude easier than neighbors.
5. Hide candidates behind longer isogeny walks; red-team: random-walk search, public-invariant classifiers, End-ring recovery, generation-family reconstruction, MITM path recovery.
6. Reject fixed-factor-only advantages. Signal of interest: empirical complexity exponent \(< 1/2\), or precomputation / individual-log separation analogous to hidden SNFS.

## Relation to existing ledger work

- `GOAL-ECDLP-001` / `RQ-ECDLP-002` — broad charged breakthrough search; complementary, not a substitute.
- `IDEA-20260731-008` — isogeny-transfer **cost gate** for public special-curve families (attacker view); this goal asks the dual (designer) question: can a *secret* endpoint weakness be planted and hidden.
- `H-ISO-001` (`rejected_scoped`) — short \(\ell\)-neighbor Semaev \(d_{\mathrm{reg}}\) / yield audit found no advantage; does **not** close heavy-tail search across full classes, conductor barriers, or private factor bases.
- `IDEA-20260726-009` — min-height / weak-model reachability in the class (representation-sensitive, order-invariant).

## Standing open target (one sentence)

Find a rare, curve-equation-dependent algebraic weakness within an ordinary prime-field isogeny class—preferably across a hard conductor barrier—and show that a stored isogeny chain gives private access while public path search and public detection remain rho-hard.
