#!/usr/bin/env python3
"""Bind the recovered 1997 draft to exact example seeds and prior curve checks."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


EXPECTED_PDF_SHA256 = "0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e"
EXPECTED_SEEDS = {
    "prime192v1/P-192": "3045AE6FC8422F64ED579528D38120EAE12196D5",
    "prime192v2": "31A92EE2029FD10D901B113E990710F0D21AC6B6",
    "prime192v3": "C469684435DEB378C4B65CA9591E2A5763059A2E",
    "prime239v1": "E43BB460F0B80CC0C0B075798E948060F8321B7D",
    "prime239v2": "E8B4011604095303CA3B8099982BE09FCB9AE616",
    "prime239v3": "7D7374168FFE3471B60A857686A19475D3BFA2FF",
    "prime256v1/P-256": "C49D360886E704936A6678E1139D26B7819F7E90",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    pdf_hash = hashlib.sha256(args.pdf.read_bytes()).hexdigest()
    assert pdf_hash == EXPECTED_PDF_SHA256, pdf_hash
    pages = subprocess.check_output(["pdftotext", "-layout", str(args.pdf), "-"], text=True).split("\f")
    assert len(pages) - 1 == 103, len(pages) - 1
    assert "November 17, 1997" in pages[0]
    assert "F.3.2. Selecting an Appropriate Curve and Point" in pages[62]
    assert "H.5. Sample Elliptic Curves over the Field" in pages[96]
    section = "\n".join(pages[96:101])
    found = {"".join(bits) for bits in re.findall(
        r"seed\s*=\s*((?:[0-9A-F]{8}\s+){4}[0-9A-F]{8})", section
    ) for bits in [re.findall(r"[0-9A-F]{8}", bits)]}
    seed_checks = {name: seed in found for name, seed in EXPECTED_SEEDS.items()}
    assert all(seed_checks.values()), seed_checks
    assert len(found) == 7, found

    prior = repo / "research/nist_seed_selection_workflow_20261023/check.json"
    prior_hash = hashlib.sha256(prior.read_bytes()).hexdigest()
    rows = json.loads(prior.read_text())["rows"]
    assert len(rows) == 21
    assert sum(row["class"] == "omitted" for row in rows) == 11
    assert sum(row["class"] == "published" for row in rows) == 10
    required = ("cofactor_one", "mov_B100", "n_gt_2pow160", "nonanomalous")
    assert all(all(row["gates"][gate] for gate in required) for row in rows)
    result = {
        "source_pdf_url": "https://archive.org/download/x962-11-17-97/x962-11-17-97.pdf",
        "source_pdf_sha256": pdf_hash,
        "source_pdf_bytes": args.pdf.stat().st_size,
        "source_pdf_pages": 103,
        "dated_cover": "1997-11-17",
        "sample_table_pdf_pages_one_based": [97, 98, 99, 100, 101],
        "procedure_pdf_page_one_based": 63,
        "sample_seed_checks": seed_checks,
        "sample_seed_count": len(found),
        "prior_gate_record": str(prior.relative_to(repo)),
        "prior_gate_record_sha256": prior_hash,
        "prior_rows": {"omitted": 11, "published": 10},
        "prior_gates_all_true": list(required),
        "qualification": "Prior gate matrix reused; this check does not prove the historical program used those gates.",
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"source_verified": True, "sample_seeds": len(found), "prior_rows": len(rows)}))


if __name__ == "__main__":
    main()
