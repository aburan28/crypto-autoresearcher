#!/usr/bin/env python3
"""Replay payload bindings, source-body comparisons and integer call bounds."""
import base64
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def function(text, declaration):
    # Independent brace-count extraction, rather than the producer's end markers.
    text = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
    start = text.index(declaration)
    brace = text.index('{', start)
    depth = 0
    for end in range(brace, len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if depth == 0:
            return re.sub(r'\s+', '', text[start:end + 1])
    raise AssertionError('unterminated function')


def main():
    output = HERE / 'verification.json'
    assert not output.exists()
    raw = (HERE / 'analysis.json').read_bytes()
    data = json.loads(raw)
    cdx = json.loads((HERE / 'cdx.json').read_text())
    records = [dict(zip(cdx[0], row)) for row in cdx[1:]]
    bodies = []
    for obj in data['objects']:
        payload = Path(obj['local_path']).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == obj['sha256']
        entry = next(r for r in records if r['timestamp'] == obj['capture_timestamp'] and r['original'] == obj['original_url'])
        assert base64.b32encode(hashlib.sha1(payload).digest()).decode().rstrip('=') == entry['digest'] == obj['cdx_sha1_base32']
        if not obj['label'].endswith('archive'):
            continue
        files = {n: subprocess.check_output(['tar', '-xOf', obj['local_path'], n]) for n in ('ZZ.c', 'ZZ.h', 'lip.c')}
        assert {n: hashlib.sha256(v).hexdigest() for n, v in files.items()} == obj['source_files_sha256']
        zz, header, lip = (files[n].decode('latin1') for n in ('ZZ.c', 'ZZ.h', 'lip.c'))
        prob = function(zz, 'long ProbPrime(const ZZ& n, long NumTrials)')
        root = function(zz, 'void SqrRootMod(ZZ& x, const ZZ& aa, const ZZ& nn)')
        assert re.search(r'ProbPrime\(const ZZ& n, long NumTrials\s*=\s*10\)', header)
        assert prob.count('w=RandomLen(ZZ_NBITS);') == 1
        assert 'for(i=0;i<NumTrials;i++){RandomBnd(W,n);' in prob
        assert 'dummy[i]=zrandom(ZZ_RADIX);' in function(lip, 'void zrandomb(')
        assert 'for(;i>0;i--)' in function(lip, 'void zrandomb(')
        assert 'zsetlength(&dummy,i=bnd[0]+1);' in function(lip, 'void zrandomb(')
        bodies.append((prob, root))
    assert bodies[0] == bodies[1]
    assert data['function_bodies_equal']
    traits = json.loads((ROOT / 'research/nist_seed_skipped_curves_20261016/traits.json').read_text())['published_controls']
    assert len(data['rows']) == 12
    keys = set()
    for row in data['rows']:
        key = row['name'], row['argument']
        assert key not in keys
        keys.add(key)
        control = traits[row['name']]
        assert row['curve_uid'] == control['identity']['curve_uid']
        v = int(control[row['argument'] + '_hex'], 16)
        assert v == int(row['argument_value'])
        limbs = 0
        while v:
            limbs += 1
            v //= 2 ** 26
        assert limbs == row['input_limbs']
        bound = 1 + sum(limbs + 1 for _ in range(10))
        assert bound == row['minimum_rng_advances']
        assert row['limb_bits'] == 26 and row['observed_prefix'] == 7
        assert bound in (91, 111) and bound > 7
    result = {'status': 'passed', 'scope': 'static source and integer replay; no NTL executable or historical generator replay', 'payloads': 4, 'archive_pairs': 1, 'input_rows': 12, 'minimum_advances': [91, 111], 'analysis_sha256': hashlib.sha256(raw).hexdigest(), 'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
