#!/usr/bin/env python3
"""Fixed developer controls only; no confirmation cohort inputs are opened."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile


def add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x,y=P;u,v=Q
    if x==u and (y+v)%p==0:
        return None
    slope=((3*x*x+a)*pow(2*y,-1,p) if P==Q else (v-y)*pow(u-x,-1,p))%p
    w=(slope*slope-x-u)%p
    return w,(slope*(x-w)-y)%p


def scalar(P,k,p,a):
    out=None
    while k:
        if k&1:
            out=add(out,P,p,a)
        k>>=1
        if k:
            P=add(P,P,p,a)
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,required=True)
    args=parser.parse_args()
    checks=0
    def require(x, reason):
        nonlocal checks
        checks+=1
        if not x:
            raise AssertionError(reason)
    with tempfile.TemporaryDirectory(prefix='cli-dev-',dir=Path(__file__).resolve().parent) as folder:
        base=Path(folder);fixtures=base/'fixtures.tsv';targets=base/'targets.tsv';out=base/'rows.jsonl'
        fixture_text='id\tstratum\tp\ta\tb\tPx\tPy\tr\tN\tseed\nunit\tordinary\t17\t2\t2\t5\t1\t19\t19\t10517\nunit5\tpower5\t61\t1\t4\t41\t55\t19\t57\t8453\n'
        public={'zero':('unit',None),'seven':('unit',scalar((5,1),7,17,2)),'five-seven':('unit5',scalar((41,55),7,61,1))}
        target_text='fixture_id\ttarget_id\tQx\tQy\tQinf\n'+''.join(f'{f}\t{tid}\t{0 if q is None else q[0]}\t{0 if q is None else q[1]}\t{int(q is None)}\n' for tid,(f,q) in public.items())
        fixtures.write_text(fixture_text);targets.write_text(target_text)
        def run(output=out):
            return subprocess.run([str(args.binary.resolve()),'--run',str(fixtures),str(targets),str(output)],capture_output=True,text=True)
        result=run();require(result.returncode==0,result.stderr)
        summary=json.loads(result.stdout);require(summary['truth_labels_read'] is False,'truth separation flag')
        lines=out.read_text().splitlines();rows=[json.loads(line) for line in lines]
        require(len(rows)==48,'complete fixed developer serialization coverage')
        kernel_rows=[r for r in rows if r['row_kind']=='kernel'];target_rows=[r for r in rows if r['row_kind']=='target']
        require(len(kernel_rows)==7 and len(target_rows)==40,'kernel and target row counts')
        for row in target_rows:
            fixture=row['fixture'];p,a,P=(17,2,(5,1)) if fixture=='unit' else (61,1,(41,55))
            Q=public[row['target_id']][1]
            actual=[k for k in row['candidates'] if scalar(P,k,p,a)==Q]
            require(len(row['candidates'])==row['beam_width'],'full beam width retained')
            require(len(set(row['candidates']))==len(row['candidates']),'unique candidates')
            require(all(0<=k<19 for k in row['candidates']),'canonical candidates')
            require(row['verified_scalar']==(actual[0] if actual else None),'independent public scalar equation')
            require(row['candidate_verification_hits']==len(actual),'verification flags')
            require(row['inference_and_verification_counters']=={key:row['inference_counters'][key]+row['verification_counters'][key] for key in row['inference_counters']},'split operation vector reconciles')
            require(row['verification_counters']['candidate_verifications']==row['beam_width'],'failed candidates charged')
            require(row['inference_wall_seconds']>=0 and row['verification_wall_seconds']>=0 and row['inference_cpu_seconds']>=0 and row['verification_cpu_seconds']>=0 and row['shared_view_cpu_seconds']>=0,'actual stage timing signs')
        original=out.read_bytes();result=run();require(result.returncode!=0,'overwrite refused');require(out.read_bytes()==original,'old output unchanged')
        malformed=[('scalar-column',target_text.replace('unit\tseven\t','unit\tseven\t').replace('\nunit5', '\t7\nunit5')),
                   ('duplicate-id',target_text+target_text.splitlines()[1]+'\n'),
                   ('unknown-fixture',target_text.replace('unit\tseven','missing\tseven')),
                   ('noncanonical-infinity',target_text.replace('unit\tzero\t0\t0\t1','unit\tzero\t1\t0\t1')),
                   ('off-curve',target_text.replace('unit\tseven\t'+str(public['seven'][1][0])+'\t'+str(public['seven'][1][1])+'\t0','unit\tseven\t1\t1\t0'))]
        for name,text in malformed:
            targets.write_text(text);require(run(base/(name+'.jsonl')).returncode!=0,name+' rejected')
        targets.write_text(target_text)
        fixtures.write_text(fixture_text+fixture_text.splitlines()[1]+'\n');require(run(base/'duplicate-fixture.jsonl').returncode!=0,'duplicate fixture rejected')
        fixtures.write_text(fixture_text.replace('unit\tordinary\t17','unit\tordinary\t1048583'));require(run(base/'field-guard.jsonl').returncode!=0,'field guard rejected before arithmetic')
        output={'kind':'fixed_development_cli_controls','scientific_run':False,'confirmation_inputs_opened':False,'checks':checks,'rows':len(rows),'kernels':len(kernel_rows),'target_cases':len(target_rows),'maximum_serialized_target_bytes':max(len(line.encode())+1 for line,row in zip(lines,rows) if row['row_kind']=='target'),'maximum_serialized_kernel_bytes':max(len(line.encode())+1 for line,row in zip(lines,rows) if row['row_kind']=='kernel'),'all_returned_candidates_checked_with_independent_python_arithmetic':True,'temporary_rows_removed':True}
        print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
