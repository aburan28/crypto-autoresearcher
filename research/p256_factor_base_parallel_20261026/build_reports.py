"""Render fresh second-pass reports using the retained inspected renderer.

Rendering is communication work, never an experiment or a checkpoint opt-out.
The source renderer remains unchanged and refuses to overwrite a prior PDF.
"""
import argparse
import importlib.util
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "p256_factor_base_parallel_20261025" / "build_reports.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+")
    parser.add_argument("--stem", default="report-preparation")
    parser.add_argument("--source", default="report.md")
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("p256_retained_report_renderer", SOURCE)
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    renderer.ROOT = ROOT
    original_document = renderer.document

    def document_without_duplicate_diagram(markdown, diagram):
        explicit = diagram and re.search(
            r"(?m)^!\[[^\]]*\]\(" + re.escape(diagram) + r"\)\s*$", markdown)
        return original_document(markdown, None if explicit else diagram)

    renderer.document = document_without_duplicate_diagram
    for name in args.directories:
        directory = (ROOT / name).resolve()
        if not directory.is_relative_to(ROOT):
            raise ValueError("Report directory escapes the second-pass study")
        renderer.build(directory, args.stem, args.source)


if __name__ == "__main__":
    main()
