import json,sys
lbl,st,s,e,raw=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
try: d=json.loads(raw)
except Exception: d={'parse_error':raw[:300],'status':'no_result_terminated_or_failed'}
d['label']=lbl; d['exit_status']=st; d['start_epoch']=s; d['end_epoch']=e; d['wall_s']=e-s
d['segment']=3; d['machine_conditions']='uncontended: 4 cores, no other producers (coordinator-confirmed load 0.24 at segment start)'
open('raw.jsonl','a').write(json.dumps(d)+"\n")
