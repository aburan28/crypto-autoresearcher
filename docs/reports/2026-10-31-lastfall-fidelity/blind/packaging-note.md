# T-1110: preserve PDF content below the artifact limit

The four-page blind review PDF is now **65,408 bytes**, below the 65,536-byte artifact limit with 128 bytes of headroom. Complete Unicode text extraction is byte-identical to the original in default, layout, and raw modes. Every page renders to identical pixels at 120 dpi. The scientific report, conclusions, original attestation, Typst source, and SVG are unchanged.

## Provenance

- Original peer commit: `574df8c7f45c81118a33637d528424eeb6eb1a11`.
- Integration base for this packaging task: `44f54fc8fb794f29a5d518edd33c8c02331f9741` (PR #2824 head supplied by the coordinator).
- Artifact path: `docs/reports/2026-10-31-lastfall-fidelity/blind/report.pdf`.
- Original PDF: 101,156 bytes; SHA-256 `67a1313db72ae569005f40ebc4bb065c3e3af1a18330568a54d41385e9742666`.
- Packaged PDF: 65,408 bytes; SHA-256 `3adfbcecf2b50b12568efe9ab1c41c1e04795fc34793075d2e86b2260ad6cbbe`.

The original PDF remains retrievable from the named immutable commits. This task replaces its packaging in the current tree; it does not duplicate the oversized binary in another tracked path. Earlier validation records describe the original artifact and remain intact. `packaging-validation.json` records the new artifact's checks, and `SHA256SUMS` binds the current report and packaging files.

## Transformation and checks

`package_pdf.py` groups PDF objects into compressed object streams, then applies lossless Zopfli Flate compression to existing compressed streams. Each stream is replaced only when its encoded bytes get shorter. The transformation preserves every decoded stream payload, including page contents, embedded fonts, Unicode character maps, and XMP metadata. Document-info entries and catalog keys also match the original. Page graphics, accessibility structures, document navigation, and metadata are not removed. Ghostscript was not used.

The successful packaging stages were 68,175 bytes after object-stream compression, then 65,493, 65,438, and 65,408 bytes with the recorded Zopfli passes. Versions: pikepdf 10.17.0, libqpdf 12.4.2, zopfli 0.4.3, Pillow 13.0.0, CPython 3.12.15, and Poppler 24.08.0.

The following checks passed against the complete original PDF:

| Check | Result |
| --- | --- |
| File size | 65,408 ≤ 65,536 bytes |
| Decoded stream payloads, including duplicate counts | Exact multiset equality |
| XMP metadata and document-info entries | Identical |
| PDF syntax check | No warnings from pikepdf |
| UTF-8 text, default `pdftotext` mode | Identical 10,281 bytes |
| UTF-8 text, `pdftotext -layout` | Identical 12,528 bytes |
| UTF-8 text, `pdftotext -raw` | Identical 10,180 bytes |
| Pages 1–4 at 120 dpi | Identical pixels, each 993 × 1,404 |
| Visual inspection | All four packaged pages opened and inspected |

The record retains the full extracted-text hashes and a pixel hash for every page. There are no extracted-text differences to justify. No scientific claim was reassessed during packaging; the coordinator's separate convention clarification remains outside this task.

An initial verification attempt correctly stopped before replacing `report.pdf`: pikepdf's default metadata-version update had reformatted the XMP XML despite leaving its values unchanged. Setting `fix_metadata_version=False` in every save retained the original metadata bytes and made the full stream-payload check pass. Intermediate candidates above the size limit were not committed. An exploratory metadata-compression attempt did not retain a metadata filter and was discarded. The successful script uses ordinary PDF metadata preservation and changes only encoding and object organization.

## Reproduction

Extract the original blob from its named commit, then invoke the included script with a fresh scratch directory. The script checks the input hash, the size limit, complete text equality, decoded stream equality, and all page pixels before writing the output PDF or validation record.

```sh
git show 44f54fc8fb794f29a5d518edd33c8c02331f9741:docs/reports/2026-10-31-lastfall-fidelity/blind/report.pdf > /tmp/lastfall-original.pdf
uv run --no-project --with pikepdf==10.17.0 --with zopfli==0.4.3 --with Pillow==13.0.0 \
  python package_pdf.py /tmp/lastfall-original.pdf report.pdf packaging-validation.json /tmp/lastfall-pack-fresh
```

Run the second command from this report directory; `/tmp/lastfall-pack-fresh` must not already exist. Poppler's `pdftotext` and `pdftoppm` must be on `PATH`. The executed validation used the same script with `/tmp/lastfall-pdf-pack-20261031/original.pdf` as input and `/tmp/lastfall-pdf-pack-20261031/reproduce-v2` as scratch.

T-1110 was claimed at epoch 1. The advisory scope check reported T-1110's own matching reservation as a conflict; the holder task and current claim were the same. The base was kept at the coordinator's supplied PR head; the pre-archive fetch observed `origin/main` at `1a0afc68c2`. Integration remains with the coordinator.
