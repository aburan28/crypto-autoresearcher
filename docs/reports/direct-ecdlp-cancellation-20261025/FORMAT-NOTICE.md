# Compact PDF derivatives, 25 October 2026

The four PDFs listed in `compact-export-manifest.json` are new formatting derivatives of unsealed report exports. Their Markdown, mathematics, tables, captions, citation links and figure data are unchanged. No scientific measurement was repeated and no sealed run, frozen log or historical raster/hash record was edited.

The reexports use one embedded CFF text face at 10 pt, retaining embedded mathematical fonts. Headings retain their sizes; pagination and text weight change. Two Unicode script characters have explicit TeX mappings, and the planning export permits inline-code line breaks. This also restores a source commit-reference suffix (`e31,`) that the original overfull PDF clipped. The programme diagram retains its original labels and uses the standard PDF Base14 Times-Roman font. A lossless content-string representation change and ordinary object/Flate compression complete the export. No coordinate reconstruction, missing custom font, remote upload or artifact-policy exception is involved.

All 29 unique exported pages were visually inspected. The historical programme derivative is byte-identical to the current programme derivative, so these cover all 41 exported pages. Every extracted text bounding box lies within its page. After accounting for pagination, discretionary hyphenation, repeated table headers and Unicode normalization, programme and pilot text agree with their originals; planning differs only by the restored source-reference suffix. Every unique page renders pixel-identically before and after the lossless packing step.

The manifest records original and compact SHA-256 hashes, byte/page counts, and immutable links to the originals at commit `fee743bb37fe9eb74e6fc00fb82179494c17bd50`. In particular, `programme/executions/20261025T040202Z/rebuilt-programme.pdf` is now a compact derivative. Its old run's logs and raster/hash checks describe the original linked PDF, not this derivative.

Rebuild the same formatting from unchanged report sources with:

```sh
python3 compact-export.py --repo-root /path/to/crypto-autoresearcher --out-dir /tmp/fresh-compact-exports
```

The helper writes only its requested output directory. Copy the four resulting PDFs to their corresponding report-export paths after review. Current report `build.sh` scripts call this helper after their initial typesetting to produce the compact exports. PDF creation metadata can change byte hashes by a few bytes across rebuilds; the published manifest binds the actual reviewed files. This is same-session document verification, not an independent scientific review.

The three current native `build.sh` scripts finish with this compact export step. It reads the existing report-source Markdown and figures for all three report directories and copies the relevant compact PDF into place; it does not invoke the measurement harness. All those source directories must be present.
