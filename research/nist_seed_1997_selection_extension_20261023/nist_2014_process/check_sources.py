#!/usr/bin/env python3
"""Bind the NIST 2014 retrospective source statements to exact PDFs/pages."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

EXPECTED = {
    'vcat': {
        'sha256': 'd22e14c8a668e2c806483e3b002f6d9d7cd71657c111f445a475cc470280ec4e',
        'page': 22,
        'phrases': ['NIST could not say how', 'many seeds were attempted',
                    'NIST has verified that this is how the parameters'],
    },
    'briefing': {
        'sha256': 'da87c4202058c715904706ac1dc8abdfdaac78a31408c619916ee8a98094ab47',
        'page': 11,
        'phrases': ['Curve Selection', 'Check if curve is secure against known attacks',
                    'Very likely need to choose many seeds'],
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vcat', required=True, type=Path)
    parser.add_argument('--briefing', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists')
    out = {}
    for name in ('vcat', 'briefing'):
        path = getattr(args, name)
        spec = EXPECTED[name]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest == spec['sha256'], (name, digest)
        page = spec['page']
        result = subprocess.run(['pdftotext', '-f', str(page), '-l', str(page),
                                 '-layout', str(path), '-'], check=True,
                                capture_output=True, text=True)
        normalized = ' '.join(result.stdout.split())
        assert all(phrase in normalized for phrase in spec['phrases']), name
        out[name] = {'sha256': digest, 'pdf_page_one_based': page,
                     'checked_phrases': spec['phrases']}
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + '\n')
    print('checked both NIST PDFs and cited pages')


if __name__ == '__main__':
    main()
