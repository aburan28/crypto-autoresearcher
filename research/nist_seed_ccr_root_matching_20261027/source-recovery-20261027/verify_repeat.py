"""Replay exact repeat/export bindings; no historical-source redistribution."""
import collections,hashlib,json,sys
from pathlib import Path
import verify
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
verify.main()
cross=json.loads((P/'CROSS-REPEAT.json').read_text());assert cross['status']=='PASS' and cross['byte_identical'] and cross['repeat_observations_sha256']==cross['first_observations_sha256']==sha(P/'observations.jsonl')
assert json.loads((P/'EXPORT-CHECK.json').read_text())['returncode']==0
exp=json.loads((P/'export.json').read_text());protocol=json.loads((P/'experiment.protocol.json').read_text());obs=[json.loads(x) for x in (P/'observations.jsonl').read_text().splitlines()]
assert protocol['protocol_id']=='ATKIN-NATIVE-GETALL-02' and exp['protocol']['sha256']==protocol['freeze']['protocol_sha256'] and protocol['freeze']['filed_before_affected_data']
assert len(exp['runs'])==666 and protocol['sample_size']['instances']==333 and len(protocol['arms'])==2
seen=set();arms=collections.Counter();kinds=collections.Counter()
for r in exp['runs']:
    line=int(r['backend_ref'].split(':')[-1]);assert line not in seen;seen.add(line);z=obs[line-1];kinds[z['kind']]+=1
    assert 'arithmetic' in z and r['arm']==f'radix{z["bits"]}' and r['status']=='succeeded' and r['verification']['status']=='verified'
    assert r['measurements']['counted']['source_calls']==int(z['kind']!='derivative_control') and r['measurements']['counted']['zero_divisions']==z['arithmetic']['zero_divisions'] and not r['measurements']['wall_valid'];arms[r['arm']]+=1
assert arms=={'radix26':333,'radix30':333} and kinds=={'cohort':598,'derivative_control':60,'regular_control':4,'exception_control':2,'AA_control':2}
assert exp['host']['sha256']==sha(P/exp['host']['path'])
for f in exp['files']+exp['analysis']['outputs']+[exp['analysis']['script']]:assert sha(P/f['path'])==f['sha256'] and (P/f['path']).stat().st_size==f['bytes']
print(json.dumps({'repeat_bindings':'PASS','formal_export':'PASS','rows':666,'per_width':dict(arms),'byte_identical_to_first':True}))
