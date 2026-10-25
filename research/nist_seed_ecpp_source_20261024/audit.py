#!/usr/bin/env python3
"""Inspect external archive bytes without extracting or running bundled code."""
import gzip
import hashlib
import io
import json
import re
import subprocess
import tarfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCES = [
    ('funet', '/private/tmp/nist-ecpp.V3.4.1.tar.Z', 'https://mirrors.nic.funet.fi/pub/crypt/math/ecpp.V3.4.1.tar.Z'),
    ('gwdg', '/private/tmp/nist-ecpp.V3.4.1-gwdg.tar.Z', 'https://ftp3.gwdg.de/pub/misc/crypt/math/ecpp.V3.4.1.tar.Z'),
]
EXPECTED = '0387e7d180e570d0cf1ff957ed281a46711fb20d50ae0b0669a01a3464d9160f'
FILES = ['VERSION.ecpp', 'README', 'README.ecpp', 'Ecpp/C/c/ecpp.c', 'Ecpp/C/c/findd.c', 'Ecpp/C/c/factorm.c', 'Ecpp/C/c/tactics.c', 'Ecpp/C/c/runecpp.c', 'Ecpp/C/h/ecpp.h', 'Ecpp/C/Makefile', 'Ecpp/Data/ecpp.DfD', 'Ecpp/Data/spmax.data']


def sha(b):
    return hashlib.sha256(b).hexdigest()


def without_comments(s):
    return re.sub(r'\s+', '', re.sub(r'/\*.*?\*/|//[^\n]*', '', s, flags=re.S))


def main():
    output = HERE / 'source_audit.json'
    assert not output.exists()
    objects = []
    for label, path, url in SOURCES:
        b = Path(path).read_bytes()
        assert sha(b) == EXPECTED
        objects.append({'label': label, 'local_path': path, 'url': url, 'bytes': len(b), 'sha256': sha(b)})
    # gzip -dc handles the historical compress format; tar members are read only.
    payload = subprocess.check_output(['gzip', '-dc', SOURCES[0][1]])
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        inventory = [{'name': m.name, 'bytes': m.size, 'type': m.type.decode('ascii', errors='backslashreplace')} for m in archive.getmembers()]
        files = {name: archive.extractfile('ECPP/' + name).read() for name in FILES}
    text = {k: v.decode('latin1') for k, v in files.items()}
    compact = {k: without_comments(v) for k, v in text.items()}
    ecpp = compact['Ecpp/C/c/ecpp.c']
    find = compact['Ecpp/C/c/findd.c']
    caller = compact['Ecpp/C/c/runecpp.c']
    guards = {
        'nextD_has_finite_rank_stop': 'if(rgd[depth]==RGDMAX)return(0);' in find,
        'findD_propagates_no_next_D': 'if(!nextD(&D,fD,&h,&g,file_of_DfD)){printf("%%!%%NonextD\\n");return(0);}' in find,
        'findm_propagates_findD_failure': 'if(!findD(&l,sqrtd,file_of_DfD))return(0);' in ecpp,
        'buildchain_retries_once_then_returns_zero': 'if(gasp)return(0);else{' in ecpp and 'gasp=1;' in ecpp,
        'ecpp_propagates_buildchain_failure': 'if(!buildchain(tabcertif,n,nl,smallp)){depth--;ecppclose();return(0);}' in ecpp,
        'caller_labels_zero_composite': 'printf("Thisnumberiscomposite\\n");' in caller,
        'proof_phase_exists': 'ok=proveall(tabcertif,n,nl,smallp);' in ecpp,
        'noproof_default_zero': 'intverbose=1,noproof=0,' in ecpp,
    }
    assert all(guards.values()), guards
    records = []
    for rank, line in enumerate(text['Ecpp/Data/ecpp.DfD'].splitlines()):
        match = re.fullmatch(r'\(\(([^)]*)\)\s*(\d+)\s*(-?\d+)\)', line.strip())
        assert match, (rank, line)
        factors, D, h = match.groups()
        factors = [int(x) for x in factors.split()]
        product = 1
        for f in factors:
            product *= f
        assert product == int(D)
        records.append({'zero_based_row': rank, 'D': int(D), 'factor_entries': factors, 'signed_h_entry': int(h)})
    assert len(records) == 1684
    guard = int(re.search(r'#define\s+RGDMAX\s+(\d+)', text['Ecpp/C/h/ecpp.h']).group(1))
    params = [dict(zip(['length_threshold', 'sieve_bound', 'rho_iterations', 'gcd_batch', 'pollard_B1', 'pollard_B2'], map(int, line.split()))) for line in text['Ecpp/Data/spmax.data'].splitlines() if line.strip()]
    thesis = Path('/private/tmp/nist-chabaud-1996.pdf')
    assert sha(thesis.read_bytes()) == '4b2c43b1ee5a516a27be0a385c9edbaef5c6a53329cd69edc726c2e04e87d950'
    pages = subprocess.check_output(['pdftotext', '-layout', str(thesis), '-']).decode('utf8').split('\f')
    assert '22 octobre 1996' in pages[0]
    assert 'ecpp.V3.4.1.tar.Z' in pages[135]
    result = {'method': 'retrospective static source audit; no curve-order trial or bundled executable run', 'recorded_utc': datetime.now(timezone.utc).isoformat(), 'objects': objects, 'mirrors_equal': Path(SOURCES[0][1]).read_bytes() == Path(SOURCES[1][1]).read_bytes(), 'version_text': text['VERSION.ecpp'].strip(), 'thesis': {'url': 'https://www.di.ens.fr/reports/1996/liens-96-14.A4.pdf', 'sha256': sha(thesis.read_bytes()), 'bytes': thesis.stat().st_size, 'cover_pdf_page': 1, 'reference_pdf_page': 136}, 'historical_byte_authentication': 'not established; the 1996 filename reference supplies no payload digest', 'selected_files_sha256': {k: sha(v) for k, v in files.items()}, 'source_guards': guards, 'declared_rank_stop': guard, 'catalog_rows': records, 'catalog_max_D': max(r['D'] for r in records), 'factoring_parameters': params, 'archive_inventory': inventory, 'code_sha256': sha(Path(__file__).read_bytes()), 'scope_sha256': sha((HERE / 'SCOPE.md').read_bytes()), 'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'dirty': subprocess.check_output(['git', 'status', '--porcelain'], text=True)}
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'mirrors_equal': result['mirrors_equal'], 'catalog_rows': len(records), 'rank_guard': guard, 'max_D': result['catalog_max_D'], 'source_guards': guards}, sort_keys=True))


if __name__ == '__main__':
    main()
