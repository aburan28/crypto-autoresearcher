#!/usr/bin/env python3
"""Create a smaller derived PDF of the same complete report text.

Requires typst and PyMuPDF. The original rendering and source are untouched.
Only the display font and PDF container representation change. Structural
accessibility tags are omitted from this compact view. Vector artwork remains.
"""
import hashlib
import json
from pathlib import Path
import sys
import tempfile

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv[1])
import fitz
import typst

p = Path(__file__).resolve().parent
for name in ['report-compact.typ', 'report-compact.pdf', 'compact-check.json']:
    if (p / name).exists():
        raise SystemExit(f'Refusing to replace {name}')
original = (p / 'report.typ').read_text()
variant = original.replace('font: "DejaVu Sans"', 'font: "Nimbus Roman"')
with (p / 'report-compact.typ').open('x') as f:
    f.write(variant)
with tempfile.TemporaryDirectory() as td:
    uncompressed = Path(td) / 'nimbus.pdf'
    typst.compile(str(p / 'report-compact.typ'), output=str(uncompressed))
    doc = fitz.open(uncompressed)
    before = [hashlib.sha256(page.get_pixmap().samples).hexdigest() for page in doc]
    doc.xref_set_key(doc.pdf_catalog(), 'StructTreeRoot', 'null')
    doc.xref_set_key(doc.pdf_catalog(), 'MarkInfo', 'null')
    doc.save(p / 'report-compact.pdf', garbage=4, deflate=True, deflate_fonts=True,
             use_objstms=1, compression_effort=100)
    compressed = fitz.open(p / 'report-compact.pdf')
    after = [hashlib.sha256(page.get_pixmap().samples).hexdigest() for page in compressed]
    assert before == after, 'Container optimization changed rendered pixels'
    size = (p / 'report-compact.pdf').stat().st_size
    assert size <= 65536, 'PDF exceeds artifact-policy threshold'
    result = {'source_text_unchanged': variant.replace('font: "Nimbus Roman"',
              'font: "DejaVu Sans"') == original, 'display_font': 'Nimbus Roman',
              'structural_accessibility_tags': False, 'vector_artwork': True,
              'container_optimization_pixels_identical': True,
              'page_pixel_sha256': after, 'pages': len(after), 'bytes': size,
              'pdf_sha256': hashlib.sha256((p / 'report-compact.pdf').read_bytes()).hexdigest()}
    (p / 'compact-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
