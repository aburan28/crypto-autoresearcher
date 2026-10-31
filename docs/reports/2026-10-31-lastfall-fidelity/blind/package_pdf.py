"""Repackage the original T-1107 PDF and check text, streams, and every page.

Dependencies: pikepdf==10.17.0, zopfli==0.4.3, Pillow==13.0.0; Poppler CLI.
Usage: python package_pdf.py ORIGINAL.pdf OUTPUT.pdf RECORD.json SCRATCH_DIR
SCRATCH_DIR must not already exist. The source is bound by SHA-256 below.
"""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys

from PIL import Image
import pikepdf
import zopfli
import zopfli.zlib


ORIGINAL_SHA256 = "67a1313db72ae569005f40ebc4bb065c3e3af1a18330568a54d41385e9742666"
PEER_COMMIT = "574df8c7f45c81118a33637d528424eeb6eb1a11"
INTEGRATION_BASE = "44f54fc8fb794f29a5d518edd33c8c02331f9741"


def digest(data):
    return sha256(data).hexdigest()


def stream_payloads(path):
    with pikepdf.Pdf.open(path) as pdf:
        return Counter(
            digest(obj.read_bytes())
            for obj in pdf.objects
            if isinstance(obj, pikepdf.Stream)
            and obj.get("/Type") not in (pikepdf.Name.ObjStm, pikepdf.Name.XRef)
        )


def main():
    source, output, record_path, scratch = map(Path, sys.argv[1:])
    source_data = source.read_bytes()
    assert digest(source_data) == ORIGINAL_SHA256
    scratch.mkdir(parents=True, exist_ok=False)
    record = {
        "task_id": "T-1110",
        "original_peer_commit": PEER_COMMIT,
        "integration_base": INTEGRATION_BASE,
        "input_sha256": ORIGINAL_SHA256,
        "input_bytes": len(source_data),
        "versions": {
            "pikepdf": pikepdf.__version__,
            "libqpdf": pikepdf.__libqpdf_version__,
            "zopfli": zopfli.__version__,
        },
        "compression_stages": [],
    }
    pikepdf.settings.set_flate_compression_level(9)
    previous = scratch / "object-streams.pdf"
    with pikepdf.Pdf.open(source) as pdf:
        pdf.save(previous, object_stream_mode=pikepdf.ObjectStreamMode.generate,
                 compress_streams=True, recompress_flate=True,
                 deterministic_id=True, fix_metadata_version=False)
    record["compression_stages"].append({"kind": "qpdf_objects", "bytes": previous.stat().st_size})
    for iterations in (15, 100, 500):
        current = scratch / f"zopfli-{iterations}.pdf"
        with pikepdf.Pdf.open(previous) as pdf:
            for obj in pdf.objects:
                if not isinstance(obj, pikepdf.Stream):
                    continue
                if obj.get("/Filter") != pikepdf.Name.FlateDecode:
                    continue
                if obj.get("/Type") in (pikepdf.Name.ObjStm, pikepdf.Name.XRef):
                    continue
                packed = zopfli.zlib.compress(obj.read_bytes(), numiterations=iterations)
                if len(packed) < len(obj.read_raw_bytes()):
                    obj.write(packed, filter=pikepdf.Name.FlateDecode)
            pdf.save(current, object_stream_mode=pikepdf.ObjectStreamMode.generate,
                     compress_streams=True, recompress_flate=False,
                     deterministic_id=True, fix_metadata_version=False)
        record["compression_stages"].append({"zopfli_iterations": iterations, "bytes": current.stat().st_size})
        previous = current
    final_data = previous.read_bytes()
    assert len(final_data) <= 65536, len(final_data)
    assert stream_payloads(source) == stream_payloads(previous)
    record["all_decoded_content_streams_identical"] = True
    with pikepdf.Pdf.open(source) as original, pikepdf.Pdf.open(previous) as final:
        assert len(original.pages) == len(final.pages)
        assert original.Root.Metadata.read_bytes() == final.Root.Metadata.read_bytes()
        assert str(original.docinfo) == str(final.docinfo)
        assert set(original.Root.keys()) == set(final.Root.keys())
        assert not final.check_pdf_syntax()
        record["page_count"] = len(final.pages)
        record["metadata_xml_identical"] = True
        record["document_info_identical"] = True
        record["catalog_keys_identical"] = True
        record["pdf_syntax_warnings"] = []
    record["text_extraction"] = []
    for mode in ([], ["-layout"], ["-raw"]):
        extracted = []
        for path in (source, previous):
            result = subprocess.run(["pdftotext", "-enc", "UTF-8", *mode, str(path), "-"], check=True, capture_output=True)
            result.stdout.decode("utf-8")
            extracted.append(result.stdout)
        assert extracted[0] == extracted[1]
        record["text_extraction"].append({"mode": mode or ["default"], "bytes": len(extracted[0]), "sha256": digest(extracted[0]), "byte_identical": True})
    record["rendered_pages"] = []
    for label, path in (("original", source), ("packed", previous)):
        subprocess.run(["pdftoppm", "-r", "120", "-png", str(path), str(scratch / label)], check=True, capture_output=True)
    for page in range(1, record["page_count"] + 1):
        with Image.open(scratch / f"original-{page}.png") as left, Image.open(scratch / f"packed-{page}.png") as right:
            assert left.size == right.size and left.mode == right.mode
            pixels = left.tobytes()
            assert pixels == right.tobytes()
            record["rendered_pages"].append({"page": page, "dpi": 120, "dimensions": list(left.size), "pixel_sha256": digest(pixels), "pixel_identical": True})
    record["output_bytes"] = len(final_data)
    record["output_sha256"] = digest(final_data)
    record["limit_bytes"] = 65536
    record["headroom_bytes"] = 65536 - len(final_data)
    output.write_bytes(final_data)
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps({"output_bytes": len(final_data), "output_sha256": digest(final_data), "checks_passed": True}))


if __name__ == "__main__":
    main()
