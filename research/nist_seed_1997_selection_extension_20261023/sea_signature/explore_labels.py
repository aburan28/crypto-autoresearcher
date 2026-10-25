#!/usr/bin/env python3
"""Post-result descriptive label reallocation; no historical randomization model."""
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path


def main():
    assert len(sys.argv) == 3
    raw_path, out_path = map(Path, sys.argv[1:])
    assert not out_path.exists()
    raw = json.loads(raw_path.read_text())
    groups = []
    actual = 0
    for bits in [192, 224, 239, 256]:
        vals = [r['cutoff_ell'] for r in raw['rows'] if r['field_bits'] == bits]
        labels = [r['label'] for r in raw['rows'] if r['field_bits'] == bits]
        n_p = labels.count('published')
        assert n_p in [1, 3]
        options = []
        for pub_indices in itertools.combinations(range(len(vals)), n_p):
            indices = set(pub_indices)
            score = sum(vals[o] < vals[p] for o in range(len(vals)) for p in range(len(vals))
                        if o not in indices and p in indices)
            options.append(score)
        groups.append(options)
        actual += sum(vals[o] < vals[p] for o in range(len(vals)) for p in range(len(vals))
                      if labels[o] == 'omitted' and labels[p] == 'published')
    distribution = Counter(sum(x) for x in itertools.product(*groups))
    total = sum(distribution.values())
    assert total == 4480 and actual == 24
    out = {'classification': 'post-result descriptive reallocation, no random-label historical model',
           'raw_sha256': hashlib.sha256(raw_path.read_bytes()).hexdigest(),
           'actual_omitted_lower_pair_score': actual, 'total_pair_score': 25,
           'label_allocations': total,
           'allocations_scoring_at_least_actual': sum(n for score,n in distribution.items() if score >= actual),
           'distribution': dict(sorted(distribution.items()))}
    out_path.write_text(json.dumps(out, sort_keys=True, indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='distribution'},sort_keys=True))


if __name__ == '__main__':
    main()
