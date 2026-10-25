#set page(paper: "a4", margin: 1.8cm, numbering: "1")
#set text(font: "New Computer Modern", size: 10pt)
#set heading(numbering: "1.")
#show table: set text(size: 8.5pt)

= Does P-256's group order let the PKM coset factor base touch P-256's addition?

*Date* 2026-10-16 · *goal* GOAL-ECDLP-001 · *question* RQ-ECDLP-001 · *hypothesis* H-ECDLP-60de36 · *related* EXP-ECDLP-f49f75, -502ae2, -20a588 · *problem record* `problems/pkm-isogeny-chain-factor-base-no-fast-decomposition.md`

*Answer.* No. This is pen-and-paper work plus exact integer checks (`check_p256_structure.py`, output in `output.json`); it uses no solver and no timing. Labels: *derived* (proved below), *computed* (exact check on the published P-256 parameters, mine only), *recalled* (textbook fact, a pointer not support).

#figure(image("diagram.svg", width: 100%), caption: [Where the group structure lives. Left: the auxiliary curve, whose cyclic 2-power subgroup the chain uses. Right: P-256. Nothing relates the two group laws.])

== Setting

The proposal takes $p = 2^256 - 2^224 + 2^192 + 2^96 - 1$ (P-256's field prime), notes $v_2(p+1) = 96$ (*computed*: 96), builds the chain $Phi$ of 44 Vélu 2-isogenies on $E_0: y^2 = x^3 + x$ (where $\#E_0(F_p) = p+1$ since $p equiv 3 mod 4$), and sets $V = x(R + ⟨K⟩) subset F_p$, $|V| = 2^44$. It then uses $V$ as a set of $x$-coordinates on $E_P$ (P-256) and asks for $T = P_1 + dots + P_6$ with $x(P_i) in V$.

== Facts about P-256 (computed)

- The published $G$ lies on the curve and $n G = O$ (so the constants are right); $p$ and $n$ are prime and $n$ is odd.
- The trace $t = p + 1 - n$ has 127 bits and is odd; $t != 0$, so $E_P$ is *ordinary*. $E_0$ is *supersingular* ($t = 0$).
- $x^3 - 3x + b$ is irreducible over $F_p$ (the Frobenius orbit of $x$ modulo it has size 3). So $E_P$ has no point of order 2 over $F_p$ and no $F_p$-rational 2-isogeny.
- For an odd prime $l$, an $F_p$-stable line in $E_P[l]$ (hence an $F_p$-rational $l$-isogeny) exists iff $t^2 - 4p$ is a square mod $l$ (*recalled* criterion: Frobenius has characteristic polynomial $x^2 - t x + p$ on $E[l]$). It holds for $l = 3, 5, 11, 13, 17, 23, dots$ and fails for $l = 7, 19, 31, dots$ (full list in `output.json`).

== Result 1: no map between the two group laws (derived)

An isogeny preserves supersingularity over $overline(F)_p$, and every non-constant morphism of elliptic curves taking $O$ to $O$ is an isogeny (*recalled*). $E_0$ is supersingular and $E_P$ is ordinary, so there is no non-constant morphism $E_0 -> E_P$ or back, over $F_p$ or any extension. The cyclic subgroup $⟨K⟩ subset E_0(F_p)$ therefore cannot be transported to $E_P$, and $E_0$'s addition says nothing about $E_P$'s.

== Result 2: a kernel coset cannot sit inside $E_P(F_p)$ (derived)

*Lemma.* Let $\#E(F_p) = n$ be prime and let $K subset E(overline(F)_p)$ be a finite subgroup of order coprime to $n$. Then $K inter E(F_p) = {O}$, so for every $R$, $|(R + K) inter E(F_p)| <= 1$.

_Proof._ If $R, R + k in E(F_p)$ with $k in K$, then $k = (R + k) - R in E(F_p)$, so the order of $k$ divides both $|K|$ and $n$, hence $k = O$. $square$

So even on $E_P$ itself, a factor base made of an isogeny-kernel coset has at most one $F_p$-rational point, whatever isogeny degree is used. The $F_p$-rational $l$-isogenies for $l = 3, 5, 11, dots$ are real, but their kernel points live over extension fields. What survives of the proposal is only the *coordinate trick*: a subset $V subset F_p$ chosen via $E_0$, whose elements are then used as $x$-values on $E_P$.

== What this does and does not settle

- *Settled (derived + computed):* the 2-power torsion that makes $p+1$ special is a property of $E_0$ only. P-256's group order $n$ is prime and unrelated to $p+1$ beyond Hasse; nothing in $n$, $t$ or $p$ gives a structured $F_p$-subset of $E_P$ that mirrors the chain.
- *Not settled:* whether the coordinate-defined set $V$ could still make $S_(m+1)$ restricted to $V^m$ unusually easy. That is the empirical question the toy experiments address; they found no advantage in the encoding and, under block order, a roughly constant factor loss.
- *Not claimed:* anything about security beyond the toy scale; absence of an attack here is not security.

== Next checks this suggests

+ State the "why is the chain slower, can it be fixed" question in the problem record (done in the same change) with the degree observation as the starting point.
+ If a new factor-base idea is proposed, apply the Lemma first: any construction that needs a rational *coset* inside $E_P(F_p)$ is ruled out before any experiment.
