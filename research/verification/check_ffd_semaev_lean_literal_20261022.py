"""Check that the finite Lean certificate transcribes the archived draw exactly."""

from hashlib import sha256
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'docs/reports/2026-10-22-semaev-first-fall-replay'
LEAN = ROOT / 'formal/CryptoResearch/Semaev/BooleanParityFiniteCertificate.lean'
TARGET = ROOT / 'formal/targets/semaev-s3-boolean-parity-finite-20261022.yaml'


def main():
    record = json.loads((REPORT / 'evidence/draws.json').read_text())
    receipt = json.loads((REPORT / 'evidence/lean-certificate.json').read_text())
    cases = [row for row in record['draws']
             if (row['n'], row['nprime'], row['draw'], row['xR']) == (4, 4, 1, 1)]
    assert len(cases) == 1
    case = cases[0]
    assert case['basis'] == [9, 3, 2, 12]
    assert case['equations_sha256'] == (
        '89ab8e668c510572bbf9307f105b2eaf46858ad900f0b6b4a2fce8803e0ba6eb')

    source = LEAN.read_text()
    match = re.search(r'def equations\s*:\s*List \(List Nat\) :=\s*'
                      r'(\[\[.*?\]\])\s*\n\n/--', source, re.S)
    assert match, 'Lean equation literal not found uniquely'
    assert json.loads(match.group(1)) == case['equations']
    assert sha256(LEAN.read_bytes()).hexdigest() == receipt['lean_source_sha256']
    assert receipt['case_equations_sha256'] == case['equations_sha256']
    assert 'BooleanParityFiniteCertificate.exact_first_fall_at_three' in TARGET.read_text()
    print(json.dumps({
        'source_commit': record['source_commit'],
        'case': {'n': 4, 'nprime': 4, 'draw': 1, 'xR': 1},
        'equation_count': len(case['equations']),
        'equations_sha256': case['equations_sha256'],
        'lean_source_sha256': receipt['lean_source_sha256'],
        'literal_equal': True,
        'target_registered': True,
    }, indent=2))


if __name__ == '__main__':
    main()
