# Period source recovery and the ell-199 lead

2026-10-27. Source review accompanying NIST-CLASSIFIER-CAPACITY-01. This is a documentary comparison with existing signed-action records, not another curve measurement or a reconstruction of the original caller.

## Sources actually read

1. J.-M. Couveignes, L. Dewaghe and F. Morain, *Isogeny cycles and the Schoof-Elkies-Atkin algorithm*, author PDF, first article page dated April 12, 1996. Retrieved from [Morain's archive](https://www.lix.polytechnique.fr/~morain/Articles/isog-cycles.pdf), SHA-256 `9b1b65c50fcb5da4c564078aa8b7da095664f21817b7170bb2815639a3122a38`, 350,836 bytes. Read the introductory algorithm sections and visually inspected the date and bibliography, printed pages 18-19. References 11-12 identify Dewaghe preprints dated December 1995 and January 1996; references 21-22 identify Müller's October 1994 work in preparation and 1995 thesis. The bibliography establishes dated references, not their exact contents or use by the NIST/ANSI selector. `SOURCE-RETRIEVAL.json` retains all three retrieval outcomes, including two failures.
2. Laurent Dewaghe, *Calcul du nombre de points sur une courbe elliptique dans un corps fini*, Lille thesis, defended December 12, 1996. Retrieved from the [university repository](https://pepite-depot.univ-lille.fr/LIBRE/Th_Num/1996/50376-1996-354.pdf), SHA-256 `9c8810460f646df5c70606721a6aa00f5242082da583fc12da806e389f40a82f`, 2,604,062 bytes. Read the introduction and chapter 2 sections 2.3-2.4; visually checked the sign formulas on printed pages 31, 32 and 38 (PDF pages 49, 50 and 56). The introduction identifies chapter 2 as *Remarks on the Schoof-Elkies-Atkin algorithm*, then submitted for publication. The December 1996 thesis itself contains the resultant sign formulas. The exact 1998 journal text has not been compared for revisions. The first urllib certificate failure is retained in `THESIS-RETRIEVAL.json`; the successful system-certificate curl receipt is `THESIS-RETRIEVAL-02.json`.

Provenance for these claims is retrieved primary text, verified by Codex T-5518 on 2026-10-27. Local OCR (`read_pdf.swift`) is a navigation aid; encoded/OCR text does not authenticate mathematical formulas. Third-party PDFs, extracted text and page images stay private and are excluded from Git and the calibration archive.

## What the 1996 thesis changes

Theorem 5, printed page 31, resolves an Elkies eigenvalue sign by a resultant and quadratic characters when ell is 3 modulo 4. Its kernel polynomial has degree (ell-1)/2, which is odd. Corollary 3, page 32, covers ell equal to 1 modulo 4 when the eigenvalue's order modulo sign is odd, using an odd-degree factor. This supplies actual pre-1997 mathematical text behind the sign refinements; the earlier bibliography alone supplied only a pointer. It still does not establish the original selector's implementation.

For Atkin primes, section 2.4.1 constructs a conjugate kernel factor of degree e*(ell-1)/2, where e is the projective Frobenius order. That factor need not be irreducible. Section 2.4.3 and Proposition 28, printed page 38, require e odd for their resultant sign shortcut. Thus the thesis does not turn our minimum irreducible-factor degree into a cap on every intermediate polynomial.

The recorded [ell-199 table](../ell199.csv) gives immediate counterexamples to an acceptance rule requiring that particular Atkin sign shortcut: published P-224 has e=20, whereas omitted P-224 positions 1485 and 5736 have e=25. The published nonsplit 239-bit examples have e=40; their conjugate factors would have degree 3960, although their smallest irreducible factors have degree 440. Therefore neither odd-e availability nor a literal 2048 cap on that intermediate factor explains the published choices. This is a source-condition comparison with existing exact records, not a native execution of the thesis algorithms.

The inspected sections give no requirement to validate at ell=199, cap a candidate list at 32, or cap the minimum irreducible factor at 2048. This statement is confined to the inspected material; it is not a claim about every historical implementation. List length, location of the correct comparison, minimum irreducible degree and largest intermediate degree remain different quantities.

## Müller source located, not yet read

A bibliographic directory led to the [Saarland dissertation record](https://publikationen.sulb.uni-saarland.de/handle/20.500.11880/25777), DOI [10.22028/D291-25721](https://doi.org/10.22028/D291-25721), Volker Müller, 1995, oral examination May 18, 1995, advisor Johannes Buchmann. Its linked file is `VolkerMueller_ProfDrJohannesBuchmann.pdf`. The browser search service exposes a cached but font-encoded extraction; direct PDF retrieval returned HTTP 403 with curl and a certificate error with urllib. No local PDF was obtained, no formulas were read from its corrupted extraction, and no algorithmic assertion here relies on that thesis. `MUELLER-POINTER.json` and `MUELLER-RETRIEVAL.json` retain the distinction. This is Volker Müller's thesis, not Jan Steffen Müller's later dissertation.

The 2001 Maurer-Müller paper remains a bibliographic pointer: DOI 10.1080/10586458.2001.10504448 and institutional record https://orbilu.uni.lu/handle/10993/2281. No copy request or other outgoing human message was sent.

## Remaining discriminating evidence

The narrow two-cap family's unique labeling warrants retaining the ell-199 pattern. To attribute it historically, recover a caller or dated implementation that supplies a reason for ell=199, the splitting-degree mode, both resource quantities, and the actual bounds. A source-based reconstruction must then explain all six streams and all 21 fixed identities without choosing different rules for exceptions. If the source uses an earlier stopping rule, compare its actual visitation sequence rather than assuming all candidate curves reached 199. The separate later counter replay already records that all eleven omission replays stopped before 199.

No local LMFDB query was needed in this round: it adds no catalog comparison or new curve arithmetic; the earlier documented index coverage excludes these cryptographic fields. No canonical attack/frontier graph changes: this review changes source provenance and classifier selectivity only. The selector problem and overall goal remain open.
