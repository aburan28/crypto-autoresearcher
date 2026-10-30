#!/usr/bin/env python3
"""Read-only retained-seed profile; reproduce the frozen native allocation gate."""
import argparse
import datetime
import json
from pathlib import Path
from capacity_profile import digest, profile


def envelope(columns, old, nq, work, chunk):
    stride = ((work + 63) // 64 + 2) * 8
    seedstride = ((nq + 63) // 64 + 2) * 8
    terms = {
        'map_and_export': columns * stride * 2,
        'seed': old * seedstride,
        'relations_actions_workspace': (3 * work + 4 * chunk + nq) * stride,
        'low_workspace': (nq + chunk) * seedstride,
        'indices': columns * 40,
    }
    payload = sum(terms.values())
    return dict(terms=terms, payload_bytes=payload,
                envelope_bytes=payload * 135 // 100 + (64 << 20))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    plan = json.loads(args.plan.read_text())
    for name, expected in plan['source_hashes'].items():
        if digest(Path(__file__).parent / name) != expected:
            raise ValueError('source hash mismatch: ' + name)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    value = profile(Path(plan['certificate']), plan['certificate_sha256'])
    value['native_envelopes'] = {
        str(chunk): envelope(value['next_degree_columns'], value['seed_columns'],
                            value['seed_codimension'], value['working_coordinates'], chunk)
        for chunk in plan['chunk_rows']
    }
    value.update(plan_sha256=digest(args.plan), source_sha256=digest(Path(__file__)),
                 started_at=started, status='completed', wall_valid=False,
                 scope='Exact allocation formula for this representation; not measured RSS, minimum memory, admission on a host, or an LFD conclusion.')
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x') as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps(value), flush=True)


if __name__ == '__main__':
    main()
