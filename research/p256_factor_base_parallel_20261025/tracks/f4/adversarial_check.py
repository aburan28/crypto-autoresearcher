"""Fixed corruption controls for the independent certificate reader."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import independent_check

parser=argparse.ArgumentParser()
parser.add_argument('directory',type=Path)
parser.add_argument('--receipt',type=Path,required=True)
args=parser.parse_args()
controls=[]
for label,filename,mutation in [
    ('wrong_norm','pole4.json',lambda c:c['norm'].__setitem__(0,c['norm'][0]+1)),
    ('wrong_zero_multiplicity','tangent.json',lambda c:c['zeros'][0].__setitem__('multiplicity',c['zeros'][0]['multiplicity']+1)),
    ('wrong_signed_row','pole3.json',lambda c:c['row'].__setitem__(next(iter(c['row'])),99)),
    ('wrong_stitch_coefficient','graph_two_outside.json',lambda c:c['cancelled_rows'][0]['combination'].__setitem__(0,c['cancelled_rows'][0]['combination'][0]+1)),
    ('wrong_stitch_rank','graph_one_outside.json',lambda c:c.__setitem__('rank_after_cancellation',c['rank_after_cancellation']+1))]:
    with tempfile.TemporaryDirectory(prefix='f4-corrupt-') as scratch:
        dest=Path(scratch)
        for f in args.directory.glob('*.json'):shutil.copy2(f,dest/f.name)
        target=dest/filename
        c=json.loads(target.read_text()); mutation(c)
        target.write_text(json.dumps(c,sort_keys=True)+'\n')
        try:independent_check.check(dest)
        except AssertionError:
            controls.append({'mutation':label,'file':filename,'detected':True,
                'corrupt_sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        else:raise AssertionError('corruption accepted: '+label)
record={'status':'passed','scope':'implementation corruption controls, same author/session',
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'controls':controls}
args.receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
print(json.dumps(record,indent=2))
