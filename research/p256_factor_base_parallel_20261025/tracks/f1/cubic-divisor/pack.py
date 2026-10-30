"""Losslessly compress native JSON payloads exceeding 64 KiB; retain raw hashes."""
import gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
    records=[]
    for path in sorted(ROOT.rglob('*.json')):
        if path.stat().st_size<65536:continue
        raw=path.read_bytes();json.loads(raw);compressed=gzip.compress(raw,mtime=0)
        dest=path.with_suffix(path.suffix+'.gz');assert not dest.exists()
        dest.write_bytes(compressed);assert gzip.decompress(dest.read_bytes())==raw
        records.append({'logical_path':str(path.relative_to(ROOT)),
            'stored_path':str(dest.relative_to(ROOT)),'encoding':'gzip',
            'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),
            'stored_sha256':hashlib.sha256(compressed).hexdigest(),'stored_bytes':len(compressed)})
        path.unlink() # Raw bytes retained exactly in the gzip payload, never discarded.
    (ROOT/'packed-artifacts.json').write_text(json.dumps({'status':'PASS','artifacts':records},indent=2)+'\n')
    print(json.dumps({'status':'PASS','losslessly_packed':records}),flush=True)

if __name__=='__main__':main()
