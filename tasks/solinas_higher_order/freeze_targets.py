#!/usr/bin/env python3
"""Prepare only public coordinates; no outcome-driven target selection."""
import json
from pathlib import Path
from oracle import sqrt_mod, multiply

HERE = Path(__file__).resolve().parent


def make_targets(inputs, config):
    targets = []
    for anchor in inputs['anchors']:
        p = anchor['p']
        centers = {'zero': 0, 'two64': 1 << 64, 'two96': 1 << 96,
                   'p_minus_two64': p-(1 << 64), 'p_minus_one': p-1}
        for region in config['target_regions']:
            selected = []
            for offset in range(config['target_search_limit']):
                # Search backward for centers near p, forward otherwise.
                x = centers[region]-offset if region.startswith('p_') else centers[region]+offset
                if not 0 <= x < p: continue
                y = sqrt_mod((x*x*x+anchor['A']*x+anchor['B']) % p, p)
                if y is None: continue
                if multiply(anchor, (x, y), anchor['N']) is not None:
                    raise ValueError('Target is not in the certified prime-order group')
                selected.append({'case': anchor['case'], 'region': region, 'index': len(selected),
                                 'offset': offset, 'G': [x, y]})
                if len(selected) == config['targets_per_region']: break
            if len(selected) != config['targets_per_region']:
                raise ValueError('Bounded target search did not fill the frozen cohort')
            targets.extend(selected)
    return {'schema': 1, 'selection': 'First 32 liftable x in each predefined interval; smaller y root only; both signs are not independent draws',
            'targets': targets}


if __name__ == '__main__':
    result = make_targets(json.loads((HERE/'inputs.json').read_text()), json.loads((HERE/'config.json').read_text()))
    path = HERE/'targets.json'
    data = json.dumps(result, sort_keys=True, indent=2).encode()+b'\n'
    if path.exists() and path.read_bytes() != data:
        raise ValueError('Existing target preparation differs')
    path.write_bytes(data)
    print(json.dumps({'targets': len(result['targets']), 'path': str(path)}))
