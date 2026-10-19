#set page(paper: "us-letter", margin: (x: 0.7in, y: 0.6in))
#set text(font: "Arial", size: 9.4pt)
#set par(leading: 0.5em)

= Circuit input support of two binary eight-summand chains

*2026-10-17 · Structural input comparison on one GF(2^61) ordinary-binary fixture*

Seven three-point equations encode one planted eight-summand raw target. The selected torsion-coordinate base has 267 projected columns and 10 external bits per coordinate; the selected raw-x base has 265 columns and 9 bits. Both use six full-field intermediates. A fixed schoolbook GF(2^61) multiplier, linear squaring/constant multiplication, two-input XOR and AND gates, and common-subexpression reuse define the circuit encoding. Counts below include only gates reachable from all 427 output bits, across the seven equations; input bits are separate.

#table(
  columns: (auto, auto, auto, auto, auto),
  inset: 5pt,
  stroke: (bottom: 0.35pt + rgb("CCD8DE")),
  [*Arm*], [*Inputs*], [*AND*], [*XOR*], [*Live gates*],
  [Torsion φ, selected], [446], [25,093], [61,020], [86,113],
  [Raw x, selected], [438], [42,542], [94,764], [137,306],
  [Torsion φ, width control], [438], [24,582], [59,468], [84,050],
  [Raw x, width control], [446], [43,010], [95,246], [138,256],
)

#image("2026-10-17-binary-circuit-support.svg", width: 100%)

The circuit generator matched all seven archived field-equation values on eight seeded assignments per arm. The parent equations were independently replayed in Sage. The equal-width controls are symbolic only and have no matched realized point sets. The selected torsion form uses fewer circuit gates while its expanded ANF has more coefficient-bit terms than raw x (647,014 versus 121,546 in one middle equation). This reflects representation and shared products; it does not measure solver degree, runtime, relation yield or end-to-end cost.

*Boundary.* The encoding omits curve lifts, sign consistency, poles, three other torsion target channels, certificates, rank and linear algebra. A frozen solver comparison must measure these, equal realized-column controls, planted and unseen targets, full costs and matched rho. Source, exact record and links: `docs/reports/2026-10-17-binary-circuit-support.md`.
