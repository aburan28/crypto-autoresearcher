#!/usr/bin/env python3
"""Pin two contemporary source documents and inherited prime-order controls."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCES = (
    ('draft_1997', '0c231d5176fcf0b239b44732213d281b518a0e16cc6f13f7bd4039ec99807b6e', 62,
     ['F.2.3. A Deterministic Primality Test', 'Goldwasser-Kilian-Atkin (GKA)',
      'If a deterministic primality test is', 'shall be used']),
    ('text_1998', '6cb44495bf816008afc11cc6cf65124b484654b2d260559dab6dde55e2609da7', 39,
     ['The probabilistic and deterministic primality tests to appear',
      'may be used instead of the test described in this section.',
      'If n is a probable prime']),
)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--draft-1997', required=True, type=Path)
    ap.add_argument('--text-1998', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    args = ap.parse_args()
    result = {'source_checks': [], 'prior_checks': []}
    for (key, expected, page, fragments), path in zip(SOURCES, (args.draft_1997, args.text_1998)):
        content = path.read_bytes()
        assert hashlib.sha256(content).hexdigest() == expected, key
        text = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page), '-layout', str(path), '-'],
                              capture_output=True, text=True, check=True).stdout
        assert all(fragment in text for fragment in fragments), key
        result['source_checks'].append({'id': key, 'sha256': expected, 'pdf_page_one_based': page,
                                        'fragments_present': len(fragments), 'bytes': len(content)})
    expected_prior = ROOT / 'research/nist_seed_selection_workflow_20261023/check.json'
    workflow = json.loads(expected_prior.read_text())
    assert len(workflow['rows']) == 21
    result['prior_checks'].append({'path': str(expected_prior.relative_to(ROOT)),
                                    'sha256': hashlib.sha256(expected_prior.read_bytes()).hexdigest(),
                                    'rows': len(workflow['rows'])})
    order = ROOT / 'research/nist_seed_order_certificate_20261023/analysis.json'
    data = json.loads(order.read_text())
    assert len(data['rows']) == 38 and data['all_19_n_minus_one_F_1m_fail_pocklington_size']
    result['prior_checks'].append({'path': str(order.relative_to(ROOT)),
                                   'sha256': hashlib.sha256(order.read_bytes()).hexdigest(),
                                   'rows': len(data['rows']), 'n_minus_one_rows': sum(r['direction'] == 'minus' for r in data['rows'])})
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')

if __name__ == '__main__':
    main()
