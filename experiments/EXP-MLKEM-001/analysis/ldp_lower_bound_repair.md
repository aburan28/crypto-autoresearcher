# LDP lower-bound repair (EXP-MLKEM-001)

## Gap

ePrint 2026/1022 Theorem 1 uses a product polydisc centered at \(R u\). For
fixed radius-\(\varepsilon\) complex coordinates, the Euclidean neighborhood of
direction \(u\) is not eventually contained in that polydisc: a point near
\(R u\) can sit outside some coordinate slabs when \(\varepsilon\) is fixed.

## Repair

Replace the center by \((R+C)u\) with \(C > \sqrt{d}\,\varepsilon\) (complex
dimension \(d\)). Then any point within Euclidean distance \(\varepsilon\sqrt{d}\)
of \(R u\) lies inside the shifted product polydisc for large \(R\), after the
usual approximation of \(u\) by directions with no zero coordinates.

## Rate

The large-deviation speed-\(R\) cost of the center shift is an additive \(O(1)\)
in the exponent. The leading rate remains

\[
I(u)=c\bigl(\lVert u\rVert_1-1\bigr).
\]

Finite sanity checks at \(d\in\{2,8\}\) confirm \(C>\sqrt{d}\,\varepsilon\).
This repair is local to the Gaussian LDP lower bound and does not by itself
transfer to ML-KEM CBD/compression rates.
