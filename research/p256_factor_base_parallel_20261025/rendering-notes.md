# Publication rendering

The final per-track PDFs are `report-delivery.pdf`; they retain vector graphics and embedded subset fonts and fit the repository’s 64 KiB data-file limit. Each compact PDF was checked against the Typst render by comparing extracted text with whitespace ignored. Earlier local rendering drafts are excluded from Git; none is scientific evidence.

Initial DejaVu-based Ghostscript compaction lost glyph mappings and was rejected. Liberation Sans with ligatures disabled passes the text-preservation check. F1, F2 and F7 use the editable `publication-diagram.svg` summaries to avoid mixed SVG font issues; full original diagrams remain beside them. F3 has a separate `diagram-render.svg` applying `fill:none` to arrow paths; the initial diagram’s default fill produced black polygons. No recorded mathematical output was changed.

Rebuild a PDF to a fresh stem with the Typst wheel installed:

```sh
python3 build_reports.py --stem report-rebuild tracks/f1
```

The script calls Ghostscript, requires exact text preservation after whitespace normalization, and refuses oversized output or an existing destination. All PDF previews are local communication artifacts.
