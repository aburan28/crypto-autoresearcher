# Source provenance

Read by `/root/labelled_relations`, 2026-10-25, provenance `retrieved`.

- APS, *On the discrete logarithm problem for prime-field elliptic curves*,
  accepted manuscript, https://pure.tue.nl/ws/files/91158650/609.pdf . Read
  section 3 and adjacent summation-polynomial definition. Retrieved PDF SHA-256:
  `970e425f7c50ca741ca3822c4f22d5e90a90b37e8b381eb53bddbf82198f45fb`.
  `aps2018.txt` is local pdftotext output (38,484 bytes); PDF is 506,451 bytes.
  The downloaded full-text PDF is retained losslessly as nine parts of at most
  60 KiB in `aps2018.pdf.parts/`, bound by `aps2018.pdf.manifest.json`.
  `python3 sources/reassemble.py` verifies all parts without writing the PDF;
  append a new output path to reconstitute its exact bytes for pdftotext replay.
  Coordinator should handle source redistribution
  under the source's terms; this report cites the public URL.
- Kudo et al., CANS 2018 chapter DOI 10.1007/978-3-030-00434-7_19.
  https://link.springer.com/chapter/10.1007/978-3-030-00434-7_19 . Read publisher
  abstract, access notice, references and author metadata. Full text is
  subscription content, not retrieved. Thus exact chapter limitation claims
  are not verified. Independent derivations in report.md are labelled as such.
- Kudo author publication list:
  https://sites.google.com/view/m-kudo-official-website/english/papers . It links
  the CANS chapter DOI but supplied no full chapter PDF. Search queries:
  `"Acceleration of Index Calculus" filetype:pdf` and
  `"Kudo" "Yokota" "2018" "hybrid" ECDLP limitation` did not produce a full-text
  primary chapter source. Absence in those results is not proof of unavailability.
- P-256 constants are imported from the committed study baseline/parameters.py;
  standard generator coordinates are from SEC 2 v2 section 2.4.2 (provenance
  `recalled` for that external pointer, checked against the actual curve/order
  independently in Sage). No unsupported new curve trait is inferred.

No knowledge-index tool was exposed by `ALL_TOOLS`; that access gap was not
treated as evidence about prior experiments. No scientific authority is claimed.
