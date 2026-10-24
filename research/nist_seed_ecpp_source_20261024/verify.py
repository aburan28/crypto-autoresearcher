#!/usr/bin/env python3
"""Check the static receipt using separate archive/table extraction."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    out = HERE / 'verification.json'
    assert not out.exists()
    raw = (HERE / 'source_audit.json').read_bytes()
    result = json.loads(raw)
    objects = result['objects']
    payloads = [Path(o['local_path']).read_bytes() for o in objects]
    assert payloads[0] == payloads[1]
    for obj, payload in zip(objects, payloads):
        assert hashlib.sha256(payload).hexdigest() == obj['sha256']
    archive = objects[0]['local_path']
    files = {name: subprocess.check_output(['tar', '-xOf', archive, 'ECPP/' + name]) for name in result['selected_files_sha256']}
    assert {name: hashlib.sha256(b).hexdigest() for name, b in files.items()} == result['selected_files_sha256']
    lines = files['Ecpp/Data/ecpp.DfD'].decode().splitlines()
    assert len(lines) == 1684 == len(result['catalog_rows'])
    for i, (line, row) in enumerate(zip(lines, result['catalog_rows'])):
        values = [int(x) for x in re.findall(r'-?\d+', line)]
        assert values[:-2] == row['factor_entries']
        assert values[-2:] == [row['D'], row['signed_h_entry']]
        assert row['zero_based_row'] == i
    assert max(r['D'] for r in result['catalog_rows']) == 58507
    assert re.search(rb'RGDMAX\s+1685', files['Ecpp/C/h/ecpp.h'])
    params = [[int(v) for v in line.split()] for line in files['Ecpp/Data/spmax.data'].decode().splitlines() if line.strip()]
    assert len(params) == 14
    assert [r['sieve_bound'] for r in result['factoring_parameters']] == [p[1] for p in params]
    # Text-presence checks complement the report's manual branch walk;
    # they are not a compiler CFG proof or a false-negative prime example.
    assert all(result['source_guards'].values())
    e = files['Ecpp/C/c/ecpp.c'].decode()
    f = files['Ecpp/C/c/findd.c'].decode()
    c = files['Ecpp/C/c/runecpp.c'].decode()
    assert 'if(gasp)\n\t\treturn(0);' in e
    assert 'if(!findD(&l, sqrtd, file_of_DfD))\n\t    return(0);' in e
    assert 'if(rgd[depth] == RGDMAX) return(0);' in f
    assert 'printf("This number is composite\\n");' in c
    check = {'status': 'passed', 'scope': 'same-session archive and static-text replay; no execution of legacy ECPP and no candidate classification', 'mirror_payloads': 2, 'source_files': len(files), 'catalog_rows': len(lines), 'parameter_rows': len(params), 'source_audit_sha256': hashlib.sha256(raw).hexdigest(), 'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    out.write_text(json.dumps(check, indent=2, sort_keys=True) + '\n')
    print(json.dumps(check, sort_keys=True))


if __name__ == '__main__':
    main()
