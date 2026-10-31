#set document(title: "L(1,chi) test for prime239v1", date: datetime(year: 2026, month: 10, day: 30))
#set page(paper: "a4", margin: (x: 2cm, y: 1.8cm))
#set text(size: 9.5pt)
#set par(justify: true)
#show heading: set text(weight: "regular", size: 12.5pt)
#show strong: it => underline(it.body)

= prime239v1's L(1, χ) proxy stays extreme, but only through primes already seen

*Study* `research/nist_seed_l1chi_20261030`, run 2026-10-30 UTC. The run followed the frozen protocol `PROTOCOL.md` / `protocol.json` (sha256 `039665e8…`), merged in PR \#2763 before any target was evaluated. The checkpoint gate passed before each run, and the records are in `runs/`.

*Consolidated.* An independent study, `research/nist_seed_lvalue_20261030` (x = $10^8$, exact $D_K$; canonical), gives the same result. On the 61 shared curves, log L at $10^6$ agrees to $2.9 dot 10^(-14)$, and prime239v1 is at the 0.247th percentile there. See `CROSSCHECK.md`.

*Measured.*

- *Positive control passes.* For secp256k1, log $P_"DK" = -0.503074$ against the exact $log(pi\/(3 sqrt(3))) = -0.503189$, within the calibrated tolerance $tau = 8.65 dot 10^(-4)$. The calibration used 2,000 fundamental discriminants in $[-10^13, -10^12]$, h from PARI `quadclassunit` (GRH), with mean error $-2 dot 10^(-6)$.
- *Decisive result.* prime239v1 has log $P_Delta = -1.4020$ over all primes $ell <= 10^6$. That is at the *0.246th percentile* of the prime-order null, below the 1% threshold, so the frozen verdict is *`extreme_persists`*. The author's recorded prediction, `not_extreme`, failed. It is the lowest of the 69 eligible curves; next come two unpublished curves (1.31%, 1.53%) and published P-384 (1.69%).

#figure(image("fig_null.svg", width: 100%), caption: [Null density of log $P_Delta$ per field (grey), drawn with the frozen null and seed, with each eligible curve marked. Source: `runs/results.json`, `figures.py`.])

*Post-hoc, descriptive, not preregistered.*

- *Where the extreme comes from.* The decisive scope was the never-seen terms $5003 < ell <= 10^6$. They are ordinary: z = $-0.26$, about the 40th percentile. All terms above $ell = 1000$ sit near the 72nd percentile. The extreme comes entirely from small primes already seen in the split-count study. The run confirms that signal; it adds no new evidence for it.
- *My prediction failed* because it extrapolated the unweighted split-count percentile (11% at B = 5003). The $1\/ell$-weighted product is dominated by small $ell$.
- *Selection.* prime239v1 was chosen for being the minimum of 61 curves seen earlier. Among 69 null draws, a minimum at or below 0.246% has probability $1-(1-0.00246)^69 approx 0.16$.
- *Class number.* $D_K = Delta$: the conductor is 1, the endomorphism ring is maximal, and $|D_K| approx 2^241$. With $L(1, chi) approx 0.246$, $h approx sqrt(|D_K|) L \/ pi approx 2^116.8$, against about $2^118.8$ at $L = 1$. That is about 4 times smaller than typical and astronomically far from the tiny class numbers a CM-method generator produces.
- *Published versus unpublished (in-sample).* Unpublished curves exceed published ones in 0.699 of 133 within-field pairs (one-sided permutation p = 0.045). The 59 unpublished percentiles fit uniform: KS D = 0.118 against a 5% critical value of 0.177.

*Interpretation.* The frozen rule reopens only the CM-field question, and the class-number estimate answers it at once: prime239v1's CM field is not small in any generation-relevant sense. No known ECDLP attack depends on L(1, χ) or h at this scale. The selection-rule problem stays open; no hypothesis status changes.
