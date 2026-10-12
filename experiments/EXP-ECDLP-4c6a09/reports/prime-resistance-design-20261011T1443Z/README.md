# Controlled Solinas-prime comparison — design only

The user requested a controlled experiment design for the hypothesis that Solinas primes make elliptic-curve discrete logarithms harder. No new prime catalog, curve pool or ECDLP trial has been generated or run. EXP-ECDLP-5184f7 is a proposed identifier, not an official approved executable record.

Read [the PDF overview](report.pdf) or [the detailed protocol](protocol.md). The planned main sample is 36 sparse-prime blocks, each with nearby random and residue-matched random controls: 108 moduli at 24/28/32 bits. Six historical primes have their own case-study controls. The study separates curve-generation outcomes, normalized attack work, and arithmetic speed.

The complete initial [plan](plan.json) is accompanied by an authoritative [measurement-boundary clarification](measurement-boundary.json): common normalized horizon 20 and integer search cap ceil(20√ell). Read both together. No sample or observation changed.

Editable [report builder](build_design_report.py), [Typst source](report.typ), two SVG figures, [control inventory](controls.csv), [source provenance](design-provenance.json), and six copied exact curve identities are included. The historical chart is prior measured context, not a random-prime result. The native [design validator](validate_design.py) checks syntax, counts, links, copied evidence and preservation of earlier reports; it does not execute attacks.

The PDF was rendered with Python 3.12.14, Matplotlib and Typst 0.15.0. Run the builder with `--out` pointing to this directory in an environment containing Matplotlib and Typst; run the validator with `--repo` pointing to the original checkout and `--out` to this directory. Internal run links in protocol.md resolve in that checkout; the downloadable design archive contains the copied six-group chart data and hashes, not all earlier raw campaigns.

The broader ECDLP-resistance claim requires a validated structure-dependent attack on the random-prime controls that the sparse cases avoid. Increased Pollard-rho work alone is attack-specific. The frozen protocol specifies controls, uncertainty, censoring, failures and the boundary for subsequent implementation and execution.
