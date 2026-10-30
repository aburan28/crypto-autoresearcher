"""Losslessly encode closed new outputs; never alter committed run bytes."""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import secrets
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    args=parser.parse_args();raw=args.run/'raw';records=[]
    for verification in sorted(raw.glob('*.verification.json')):
        try:checked=json.loads(verification.read_text()).get('checked')
        except json.JSONDecodeError:continue  # A concurrently emitted marker is not closed yet.
        if checked is not True:continue
        stem=verification.name.removesuffix('.verification.json')
        for name in (stem+'.json',stem+'.events.jsonl'):
            path=raw/name
            if not path.is_file() or path.stat().st_size<1048576:continue
            relative=str(path.resolve().relative_to(ROOT))
            tracked=subprocess.run(['git','ls-files','--error-unmatch','--',relative],cwd=ROOT,capture_output=True)
            if tracked.returncode==0:raise ValueError('committed raw file must remain immutable: '+relative)
            data=path.read_bytes();compressed=gzip.compress(data,compresslevel=6,mtime=0);out=Path(str(path)+'.gz')
            with out.open('xb') as stream:stream.write(compressed)
            if gzip.decompress(out.read_bytes())!=data:raise ValueError('lossless archival check failed')
            records.append(dict(original_path=str(path.relative_to(args.run)),original_bytes=len(data),
                                original_sha256=sha256(data).hexdigest(),archive_path=str(out.relative_to(args.run)),
                                archive_bytes=len(compressed),archive_sha256=sha256(compressed).hexdigest(),
                                encoding='gzip level6 mtime0; verified lossless; only closed separately checked cell files'))
            path.unlink()
    if records:
        directory=args.run/'archive-encodings';directory.mkdir(exist_ok=True)
        with (directory/('part-'+secrets.token_hex(3)+'.json')).open('x') as stream:json.dump(records,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(archived_files=len(records),store_paths=[str(args.run/r['archive_path']) for r in records if r['archive_bytes']>65536])))


if __name__=='__main__':main()
