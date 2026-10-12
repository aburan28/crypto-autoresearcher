"""One-time repository import. The resulting input file makes the runner portable."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = REPO / 'experiments/EXP-ECDLP-5184f7/runs/RUN-ECDLP-d0e449/preparation'


def main():
    anchors_path = SOURCE / 'standard-anchors.json'
    anchors = json.loads(anchors_path.read_text())
    hashes = {str(anchors_path.relative_to(REPO)): hashlib.sha256(anchors_path.read_bytes()).hexdigest()}
    fields = []
    for path in sorted((SOURCE / 'curves').glob('*/curves.json')):
        data = json.loads(path.read_text())
        hashes[str(path.relative_to(REPO))] = hashlib.sha256(path.read_bytes()).hexdigest()
        curves = [{k: c[k] for k in ('index', 'p', 'A', 'B', 'N')} for c in data['curves']]
        fields.append({'id': data['modulus']['id'], 'case': data['modulus']['case'],
                       'arm': data['modulus']['arm'], 'curves': curves})
    result = {'schema': 1, 'anchors': anchors, 'fields': fields, 'source_sha256': hashes,
              'provenance': 'Internal immutable RUN-ECDLP-d0e449 public inputs; exact PARI counts and certified primes. R matches bits and ±1% of standard p; C also matches p mod 12. Random nonsingular A,B; no order selection. These are reused fields, not newly sampled fields.'}
    with (HERE / 'inputs.json').open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
