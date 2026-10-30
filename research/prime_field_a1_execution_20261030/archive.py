"""Losslessly archive closed checked A1 snapshots, never committed run files."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import secrets
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);a=p.parse_args();records=[]
    for marker in sorted((a.run/'raw').glob('*.verification.json')):
        try:checked=json.loads(marker.read_text()).get('checked')
        except json.JSONDecodeError:continue
        if checked is not True:continue
        stem=marker.name.removesuffix('.verification.json')
        for suffix in ('.json','.collection.json','.events.jsonl'):
            path=marker.parent/(stem+suffix)
            if not path.is_file() or path.stat().st_size<1048576:continue
            relative=str(path.resolve().relative_to(ROOT))
            if subprocess.run(['git','ls-files','--error-unmatch','--',relative],cwd=ROOT,capture_output=True).returncode==0:raise ValueError('committed raw bytes must remain unchanged')
            data=path.read_bytes();out=Path(str(path)+'.gz')
            with out.open('xb') as f:f.write(gzip.compress(data,compresslevel=6,mtime=0))
            if gzip.decompress(out.read_bytes())!=data:raise ValueError('gzip round-trip differs')
            records.append(dict(original_path=str(path.relative_to(a.run)),original_bytes=len(data),original_sha256=sha256(data).hexdigest(),
                archive_path=str(out.relative_to(a.run)),archive_bytes=out.stat().st_size,archive_sha256=sha256(out.read_bytes()).hexdigest(),encoding='gzip level6 mtime0; verified lossless'))
            path.unlink()
    if records:
        directory=a.run/'archive-encodings';directory.mkdir(exist_ok=True)
        with (directory/('part-'+secrets.token_hex(3)+'.json')).open('x') as f:json.dump(records,f,indent=2);f.write('\n')
    print(json.dumps(dict(archived_files=len(records),store_paths=[str(a.run/r['archive_path']) for r in records if r['archive_bytes']>65536])))


if __name__=='__main__':main()
