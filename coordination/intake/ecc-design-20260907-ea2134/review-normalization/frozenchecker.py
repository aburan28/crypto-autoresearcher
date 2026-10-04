import os, sys, json, hashlib, pathlib, subprocess, collections, itertools, time, resource, datetime, traceback
from functools import lru_cache
ROOT=pathlib.Path.cwd()
REL=pathlib.Path("experiments/EXP-FROB-b8cf21/runs/TASK-20260907-ee1e3c")
ADM=pathlib.Path("coordination/intake/ecc-design-20260907-ea2134/admission/DEC-20260909-24ab46")
SNAP="922ab8ddec16200363ae1f2d97682866b36efaa3"
started=datetime.datetime.now(datetime.timezone.utc).isoformat()
t0=time.monotonic(); c0=time.process_time()
counts=collections.Counter(); failures=[]; sources=set(); stages=[]; detail={}
def rss(): return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)*(1 if sys.platform=="darwin" else 1024)
def ck(value,label,context=None):
    counts[label]+=1
    if not value: failures.append({"check":label,"context":context})
    if rss()>8*1024**3: raise MemoryError("Independent review RSS exceeded 8 GiB")
def data(path):
    path=str(path); sources.add(path)
    return (ROOT/path).read_bytes()
def js(path): return json.loads(data(path))
def sh(path): return hashlib.sha256(data(path)).hexdigest()
def git(*args): return subprocess.check_output(["git",*args],cwd=ROOT)
def mark(label):
    item={"stage":label,"wall_seconds":time.monotonic()-t0,"cpu_seconds":time.process_time()-c0,"peak_rss_bytes":rss(),"failure_count":len(failures)}
    stages.append(item); print(json.dumps(item),flush=True)
def pt(p): return None if p is None else tuple(p)
try:
    lock=js(ADM/"review-lock-TASK-20260909-e40ef6.json")
    queue=js("coordination/intake/ecc-design-20260907-ea2134/dispatch_queue.json")
    archive=next(t for t in queue["tasks"] if t["id"]=="TASK-20260907-cc56aa")["archive"]
    receipt=js("coordination/intake/ecc-design-20260907-ea2134/archives/TASK-20260907-cc56aa/snapshot.md")
    ck(lock["snapshot_commit"]==SNAP==archive["commit_sha"],"snapshot_identity")
    changed=set(git("diff-tree","--no-commit-id","--name-only","-r",SNAP).decode().splitlines())
    ck(changed==set(archive["path_sha256"]),"snapshot_exact_paths")
    ck(git("rev-parse",SNAP+"^").decode().strip()==archive["parent_sha"],"snapshot_parent")
    ck(subprocess.run(["git","merge-base","--is-ancestor",SNAP,"HEAD"]).returncode==0,"snapshot_reachable")
    for p,h in archive["path_sha256"].items():
        ck(sh(p)==h==lock["snapshot_path_sha256"][p],"current_archive_hash",p)
        ck(hashlib.sha256(git("show",SNAP+":"+p)).hexdigest()==h,"git_archive_blob",p)
    fx=js(REL/"fixtures.json"); met=js(REL/"metrics.json"); cert=js(REL/"certificates.json")
    run=js(REL/"manifest.yaml")["run"]; res=js(REL/"raw-result.json"); env=js(REL/"environment.json")
    spec=js("experiments/EXP-FROB-b8cf21/specification.yaml")["experiment"]
    exlock=js(ADM/"execution-lock.json")
    ck(run["result"]==res and res["metrics"]==met and run["environment"]==env,"companion_equality")
    ck(run["resources"]==res["costs"],"cost_companion_equality")
    ck(data(REL/"command.txt").decode().strip()==run["code"]["command"]==exlock["command"],"command_binding")
    ck(sh(ADM/"execution-lock.json")==run["code"]["execution_lock_sha256"]==env["execution_lock_sha256"],"execution_lock_binding")
    ck(env["native_runtime_lock"]==exlock,"environment_native_lock")
    for p,h in {**exlock["input_sha256"],**exlock["source_sha256"]}.items():
        ck(sh(p)==h,"execution_source_input_hash",p)
    for name,a in run["artifacts"].items():
        ck(sh(a["path"])==a["sha256"] and len(data(a["path"]))==a["bytes"],"manifest_artifact_hash_size",name)
    ck(sum(a["bytes"] for a in run["artifacts"].values())==run["artifact_stored_bytes_excluding_manifest"],"artifact_bytes")
    ck(run["inputs"]["specification_sha256"]==sh("experiments/EXP-FROB-b8cf21/specification.yaml"),"specification_hash")
    ck(run["inputs"]["seed"]==[2026090701,2026090702],"seeds")
    ck(run["inputs"]["parameters"]["planned_cell_ids"]==spec["inputs"]["cell_ids"]+spec["inputs"]["null_cell_ids"],"planned_ids")
    logs=[json.loads(s) for s in data(REL/"stdout.log").splitlines()]
    ck(logs[0]["head"]==run["code"]["commit"] and logs[0]["timestamp"]==run["timing"]["started_at"],"start_log_binding")
    ck(logs[-1]["status"]==run["status"]==res["status"] and logs[-1]["error"]==res["invalid_reason"],"terminal_log_binding")
    ck(not data(REL/"stderr.log"),"empty_stderr")
    ck(bool(env["git_status_at_start"].strip())==run["code"]["dirty"],"dirty_flag")
    ck(git("show",run["code"]["commit"]+":"+str(ADM/"execution-lock.json"))==data(ADM/"execution-lock.json"),"executing_revision_lock")
    admit=js(ADM/"admission.json")
    ck(sh(admit["validator"]["log_path"])==admit["validator"]["log_sha256"],"admission_log_hash")
    post=receipt["postrun_validation"]
    lines=[x for x in post["raw_log_text"].splitlines() if x.startswith("  - ")]
    ck(lines==admit["validator"]["error_identities"] and len(lines)==67,"ordered_ledger_errors")
    ck(post["absolute_result"]=="FAIL" and post["exit_code"]==1,"absolute_ledger_failure_preserved")
    for p,h in post["comparison"]["affected_path_sha256"].items(): ck(sh(p)==h,"unchanged_external_debt",p)
    ck(receipt["prior_coordinator_policy_provenance"]["prior_turn_policy_compliance_verified"] is False,"unresolved_prior_policy_preserved")
    old=__import__("base64").b64decode(receipt["rejected_preparation"]["original_bytes_base64"])
    ck(hashlib.sha256(old).hexdigest()==receipt["rejected_preparation"]["original_sha256"],"rejected_draft_custody")
    # Canonical receipt schema check, separate from certificate verification.
    sys.path.insert(0,str(ROOT/"tools"))
    import validate_ledger as vl
    cx=vl.Ctx(set())
    vl.check_run(str(ROOT/REL/"manifest.yaml"),cx)
    detail["canonical_check_run"]={"errors":cx.errors,"status":"PASS" if not cx.errors else "FAIL"}
    ck(not cx.errors,"canonical_check_run")
    sources.add("tools/validate_ledger.py")
    mark("archive_and_receipt_bindings")
    import sage.all as S
    from sage.env import SAGE_VERSION
    ck(SAGE_VERSION=="10.9","sage_version")
    FIELDS={}; POLYS={}
    def enc(v,q): return sum(int(a)*q**i for i,a in enumerate(v.polynomial().list()))
    def decode(k,F,q,n): return F([(k//q**i)%q for i in range(n)])
    for f in fx["fields"]:
        q,n=f["q"],f["n"]; P=S.PolynomialRing(S.GF(q),"v"); modulus=P(f["modulus"])
        ck(modulus.is_irreducible(),"field_irreducible",(q,n))
        F=S.GF(q**n,name="v",modulus=modulus); FIELDS[q,n]=F; POLYS[q,n]=P
        # Fixed compatibility panel: four values per field, in this one comparison invocation.
        for compatibility_label, compatibility_value in (("zero",F(0)),("one",F(1)),("generator",F.gen()),("highest_basis",F.gen()**(n-1))):
            compatibility_coefficients=[compatibility_value.polynomial()[j] for j in range(n)]
            ck(len(compatibility_coefficients)==n,"field_coefficient_vector_length",(q,n,compatibility_label))
            ck(sum((F(compatibility_coefficients[j])*F.gen()**j for j in range(n)),F(0))==compatibility_value,"field_coefficient_reconstruction",(q,n,compatibility_label))
        cols=[[(F.gen()**(i*q)).polynomial()[j] for j in range(n)] for i in range(n)]
        M=S.matrix(S.GF(q),cols).transpose()
        ck([list(map(int,r)) for r in M.rows()]==f["frobenius_matrix"],"frobenius_matrix",(q,n))
        ck(M**n==S.identity_matrix(S.GF(q),n),"frobenius_period",(q,n))
        factors=[g for g,e in (P.gen()**n-1).factor()]
        ck(sorted(tuple(map(int,g.list())) for g in factors)==sorted(map(tuple,f["factors"])),"frobenius_factorization")
        hs=[]
        for r in range(1,len(factors)+1):
            for subset in itertools.combinations(factors,r):
                h=S.prod(subset)
                if h.degree() in (1,2): hs.append(tuple(map(int,h.list())))
        hs.sort(key=lambda h:(len(h),h))
        ck(hs==[tuple(x["h"]) for x in f["modules"]],"module_list_complete")
        for m in f["modules"]:
            H=sum((int(a)*M**i for i,a in enumerate(m["h"])),S.zero_matrix(S.GF(q),n))
            K=S.matrix(S.GF(q),m["kernel_basis"])
            ck(H.right_nullity()==m["dimension"]==m["degree"]==len(m["h"])-1,"module_dimension")
            ck(K.rank()==m["dimension"] and (H*K.transpose()).is_zero() and (H*M*K.transpose()).is_zero(),"module_kernel_and_invariance")
    mark("field_module_certificates")
    # Read all rows once; retain selection/calibration records and index pair streams independently.
    events=collections.defaultdict(list); kinds=collections.Counter()
    sources.add(str(REL/"raw.jsonl"))
    with (ROOT/REL/"raw.jsonl").open() as stream:
        for line in stream:
            e=json.loads(line); kinds[e["kind"]]+=1
            if e["kind"]!="pair_attempt": events[e["kind"]].append(e)
    for q,n in FIELDS:
        rows=[e for e in events["field_polynomial_candidate"] if (e["q"],e["n"])==(q,n)]
        expected=itertools.product(range(q),repeat=n)
        for e in rows:
            ck(e["coefficients"]==list(next(expected))+[1],"polynomial_scan_order")
            ck(bool(POLYS[q,n](e["coefficients"]).is_irreducible())==e["irreducible"],"polynomial_scan_result")
        ck(sum(e["irreducible"] for e in rows)==1 and rows[-1]["irreducible"],"first_irreducible_selection")
    @lru_cache(None)
    def curve(q,n,A,B): return S.EllipticCurve(FIELDS[q,n],[decode(A,FIELDS[q,n],q,n),decode(B,FIELDS[q,n],q,n)])
    def ep(P,q): return None if P.is_zero() else (enc(P[0],q),enc(P[1],q))
    def sp(Q,E,q,n): return E(0) if Q is None else E(decode(Q[0],E.base_field(),q,n),decode(Q[1],E.base_field(),q,n))
    order_events={e["tag"]:e for kind in ("object_curve_order","null_curve_order") for e in events[kind]}
    chosen={e["tag"]:e for e in events["object_curve_selected"]}
    object_by_id={c["id"]:c for c in fx["cells"] if c.get("arm")=="object"}
    tags={}; group_cache={}
    for tag,e in order_events.items():
        if e["kind"]=="object_curve_order":
            q,n,A,B=e["q"],e["n"],e["A"],e["B"]
            base=1+sum(1 if (rhs:=(x**3+A*x+B)%q)==0 else 2 if pow(rhs,(q-1)//2,q)==1 else 0 for x in range(q))
            t=q+1-base; s0,s1=2,t
            for k in range(2,n+1): s0,s1=s1,t*s1-q*s0
            order=q**n+1-s1
            ck(base==e["base_order"],"object_base_count",tag)
            primes=sorted([int(p) for p,z in S.factor(order) if z==1 and p>=17 and base%p],reverse=True)
        else:
            o=object_by_id[e["object"]]; q,n=o["q"],o["n"]; A=q+e["a"];B=q+e["b"]
            order=int(curve(q,n,A,B).cardinality())
            union={tuple(p) for b in o["bases"] for p in b["points"]}
            primes=sorted([int(p) for p,z in S.factor(order) if z==1 and o["N"]<=2*p<=4*o["N"] and p-1>=len(union)],reverse=True)
            E=curve(q,n,A,B)
            ck(E.j_invariant()**q!=E.j_invariant(),"null_non_subfield_j",tag)
        ck(order==e["order"],"curve_order_record",tag)
        ck([[int(p),int(z)] for p,z in S.factor(order)]==e["factorization"],"factorization_record",tag)
        ck(primes==e["eligible_primes"],"prime_selection_record",tag)
        tags[tag]=(q,n,A,B,order)
    for tag,scans in itertools.groupby(sorted(events["generator_candidate"],key=lambda e:(e["tag"],e["scan_index"])),key=lambda e:e["tag"]):
        scans=list(scans);q,n,A,B,order=tags[tag]; E=curve(q,n,A,B);F=FIELDS[q,n];N=scans[0]["prime"]
        ck(N==order_events[tag]["eligible_primes"][0],"largest_prime_choice",tag)
        want=[]
        xint=0
        while len(want)<len(scans):
            x=decode(xint,F,q,n); rhs=x**3+E.a4()*x+E.a6()
            ys=sorted((enc(y,q) for y in rhs.sqrt(all=True))) if rhs.is_square() else []
            want.extend((xint,y) for y in ys)
            xint+=1
        for i,e in enumerate(scans):
            Q=pt(e["point"]); out=ep((order//N)*sp(Q,E,q,n),q)
            ck(e["scan_index"]==i and Q==want[i],"generator_scan_order",tag)
            ck(out==pt(e["cofactor_image"]),"generator_cofactor_image",tag)
            ck((out is not None)==(i==len(scans)-1),"first_nonzero_generator",tag)
        P=sp(pt(scans[-1]["cofactor_image"]),E,q,n)
        ck(S.is_prime(N) and N*P==E(0),"generator_order",tag)
        cachekey=(q,n,A,B,N,ep(P,q))
        if cachekey not in group_cache:
            G=[];Q=E(0)
            for i in range(N): G.append(ep(Q,q));Q=Q+P
            ck(Q==E(0) and len(set(G))==N,"subgroup_recurrence",tag)
            group_cache[cachekey]=G
        tags[tag]=(q,n,A,B,order,N,ep(P,q),group_cache[cachekey])
    # Exact complete module membership for each selection candidate that reached that gate.
    modules_by_tag=collections.defaultdict(list)
    for e in events["module_candidate"]: modules_by_tag[e["tag"]].append(e)
    structures={}
    for tag,records in modules_by_tag.items():
        q,n,A,B,order,N,P,G=tags[tag]; F=FIELDS[q,n]
        expected_modules=next(f["modules"] for f in fx["fields"] if (f["q"],f["n"])==(q,n))
        ck([e["module"] for e in records]==expected_modules,"candidate_modules_complete",tag)
        distinct=[]; seen=set()
        for e in records:
            h=e["module"]["h"]; selected=[]
            for Q in G[1:]:
                x=decode(Q[0],F,q,n)
                if sum((int(a)*x**(q**i) for i,a in enumerate(h)),F(0))==0: selected.append(Q)
            selected.sort()
            ck(selected==[pt(Q) for Q in e["points"]],"candidate_membership",tag)
            key=tuple(selected)
            ck(e["duplicate"]==(key in seen),"candidate_duplicate",tag)
            if key not in seen: distinct.append(key);seen.add(key)
        union=set().union(*(set(b) for b in distinct))
        E=curve(q,n,A,B)
        reps=set()
        for Q in union:
            X=sp(Q,E,q,n)
            reps.add(min(ep(eps*E(X[0]**(q**i),X[1]**(q**i)),q) for i in range(n) for eps in (1,-1)))
        structures[tag]=(sum(len(b)>=2*n for b in distinct),len(union),len(reps))
        for e in records:
            ck(e["module"]["dimension"]==e["module"]["degree"],"candidate_dimension_record")
    for q,n in FIELDS:
        terminals=[e for linekind in ("object_curve_rejected","object_curve_selected") for e in events[linekind] if (e["q"],e["n"])==(q,n)]
        terminals.sort(key=lambda e:(e["A"],e["B"]))
        expected=list(itertools.product(range(q),repeat=2))
        ck([(e["A"],e["B"]) for e in terminals]==expected[:len(terminals)],"object_scan_complete_prefix",(q,n))
        seen_j=set(); selected_count=0
        for e in terminals:
            A,B,tag=e["A"],e["B"],e["tag"]
            if (4*A**3+27*B**2)%q==0: reason="singular"
            else:
                base=int(S.EllipticCurve(S.GF(q),[A,B]).cardinality())
                j=int(S.EllipticCurve(S.GF(q),[A,B]).j_invariant())
                if (q+1-base)%q==0: reason="supersingular"
                elif j in seen_j: reason="already_selected_j"
                elif not order_events[tag]["eligible_primes"]: reason="no_eligible_prime"
                else:
                    size,un,orbs=structures[tag]
                    reason=None if size>=2 and orbs>=2 else "candidate_structure"
            ck(e.get("reason")==reason,"object_selection_reason",tag)
            if reason is None:
                seen_j.add(j);selected_count+=1
                ck(e["id"]==f"FROB-q{q}-n{n}-object{selected_count:02d}","selected_object_id")
        ck(selected_count==2 or len(terminals)==q*q,"object_scan_stop",(q,n))
    # Selected fixtures: match verified subgroup sequence, direct Frobenius and quotient weights.
    cells={}; maps={}; coverinfo={}
    for c in fx["cells"]:
        if c["status"]!="selected": continue
        cid=c["id"];q,n,N=c["q"],c["n"],c["N"];E=curve(q,n,c["A"],c["B"])
        key=(q,n,c["A"],c["B"],N,pt(c["generator"]))
        G=group_cache[key];ck(G==[pt(p) for p in c["group"]],"fixture_group",cid)
        logs={p:i for i,p in enumerate(G)}
        ck(enc(E.j_invariant(),q)==c["j"] and int(E.cardinality())==c["order"],"selected_curve_parameters",cid)
        if c["arm"]=="object":
            ck(pow(c["mu"],n,N)==1 and all(pow(c["mu"],k,N)!=1 for k in range(1,n)),"mu_order",cid)
            for i,Q in enumerate(G[1:],1):
                X=sp(Q,E,q,n);x,y=X[0],X[1]
                ck(ep(E(x**q,y**q),q)==G[(i*c["mu"])%N],"mu_action",cid)
            tag=f"q{q}-n{n}-A{c['A']}-B{c['B']}"
            candidate_sets={}
            for e in modules_by_tag[tag]:
                k=tuple(map(pt,e["points"]))
                candidate_sets.setdefault(k,[]).append(e["module"]["h"])
            ck([{"points":[list(p) for p in pts],"labels":labs} for pts,labs in candidate_sets.items()]==c["bases"],"fixture_bases_complete",cid)
        bases=[set(map(pt,b["points"])) for b in c["bases"]];union=set().union(*bases)
        ck(all(B<=set(G[1:]) and all(G[-logs[p]%N] in B for p in B) for B in bases),"base_negation_closure",cid)
        neg=lambda Q:G[-logs[Q]%N]
        if c["arm"]=="null":
            parent=cells[c["object_id"]]; oc,og,ol,ob,ou=parent
            opairs=sorted({min(p,og[-ol[p]%oc["N"]]) for p in ou})
            npairs=sorted({min(p,neg(p)) for p in G[1:]},key=lambda p:(hashlib.sha256(f"{c['seed']}:{p[0]},{p[1]}".encode("ascii")).digest(),p))
            transport={}
            for p,r in zip(opairs,npairs): transport[p]=r;transport[og[-ol[p]%oc["N"]]]=neg(r)
            ck(transport=={pt(e["object"]):pt(e["null"]) for e in c["membership_transport"]},"null_transport",cid)
            ck([set(transport[p] for p in B) for B in ob]==bases,"null_membership_shape",cid)
        expected_maps={}
        for name,entries in c["quotient_maps"].items():
            options={}
            for Q in sorted(union):
                powers=range(n) if name=="frobenius_negation" else range(1)
                alternatives=[]
                for k in powers:
                    mul=pow(c["mu"],k,N) if name=="frobenius_negation" else 1
                    for sign in (1,-1): alternatives.append((G[(sign*mul*logs[Q])%N],pow(sign*mul%N,-1,N)))
                options[Q]=min(alternatives,key=lambda v:v[0])
            columns=sorted({v[0] for v in options.values()})
            expected=[{"point":list(Q),"representative":list(p),"column":columns.index(p),"weight":w} for Q,(p,w) in sorted(options.items())]
            ck(expected==entries,"quotient_minimum_and_multiplier",cid+":"+name)
            expected_maps[name]={Q:(columns.index(p),w) for Q,(p,w) in options.items()}
        ck(set(expected_maps)==({"negation","frobenius_negation"} if c["arm"]=="object" else {"negation"}),"presentation_scope",cid)
        cells[cid]=(c,G,logs,bases,union);maps[cid]=expected_maps
        for t in (1,2,3):
            for subset in itertools.combinations([i for i,B in enumerate(bases) if B],t):
                cover=",".join(map(str,subset));u=sorted(set().union(*(bases[i] for i in subset)))
                local={}
                for name,wm in expected_maps.items():
                    cols=sorted({wm[p][0] for p in u});local[name]={p:(cols.index(wm[p][0]),wm[p][1]) for p in u}
                coverinfo[cid,cover]={"subset":subset,"union":u,"uset":set(u),"maps":local,"rows":{name:{} for name in local},"attempts":0,"accepted":0,"same":0}
    for o in object_by_id.values():
        orders=[e for e in events["null_curve_order"] if e["object"]==o["id"]]
        ck([(e["a"],e["b"]) for e in orders]==list(itertools.product(range(o["q"]),repeat=2))[:len(orders)],"null_scan_prefix",o["id"])
        ck(all(not e["eligible_primes"] for e in orders[:-1]) and bool(orders[-1]["eligible_primes"]),"first_eligible_null",o["id"])
        for c,G,logs,bases,union in cells.values():
            if c.get("object_id")==o["id"]:
                last=orders[-1]
                ck(c["A"]==o["q"]+last["a"] and c["B"]==o["q"]+last["b"] and c["N"]==last["eligible_primes"][0],"null_selected_parameters",c["id"])
    for r in fx["structural_rejections"]:
        size,un,orb=structures[r["tag"]]
        ck((size,un,orb)==(r["distinct_sets_size_at_least_2n"],r["full_union_size"],r["frobenius_negation_orbits"]),"structural_rejection_counts",r["tag"])
    rawfx=[{k:v for k,v in e.items() if k!="kind"} for e in events["cell_fixture"]]
    ck(rawfx==[c for c in fx["cells"] if c["status"]=="selected"],"raw_fixture_equality")
    rawmet=[{k:v for k,v in e.items() if k!="kind"} for e in events["cover_summary"]]
    ck(rawmet==met["covers"],"raw_cover_summary_equality")
    mark("selection_groups_membership_and_quotients")
    # Independent pair verification uses the full group recurrence verified above; producer arithmetic is never imported.
    with (ROOT/REL/"raw.jsonl").open() as stream:
        for line in stream:
            e=json.loads(line)
            if e["kind"]!="pair_attempt": continue
            key=e["cell"],e["cover"];d=coverinfo[key];c,G,logs,bases,union=cells[e["cell"]];N=c["N"]
            idx=d["attempts"];u=d["union"];Q1=u[idx//len(u)];Q2=u[idx%len(u)];Q3=G[-(logs[Q1]+logs[Q2])%N]
            accept=Q3 is not None and Q3 in d["uset"]
            same=accept and any(all(p in bases[j] for p in (Q1,Q2,Q3)) for j in d["subset"])
            ck(e["index"]==idx and e["base_indices"]==list(d["subset"]) and pt(e["Q1"])==Q1 and pt(e["Q2"])==Q2,"raw_pair_index")
            ck(pt(e["Q3"])==Q3 and e["accepted"]==accept and e["same_base"]==same,"raw_pair_identity_classification")
            d["attempts"]+=1
            if accept:
                d["accepted"]+=1;d["same"]+=int(same)
                for name,wm in d["maps"].items():
                    coeff=collections.Counter()
                    for p in (Q1,Q2,Q3):j,w=wm[p];coeff[j]=(coeff[j]+w)%N
                    row=tuple(sorted((j,v) for j,v in coeff.items() if v))
                    d["rows"][name][row]=d["rows"][name].get(row,False) or same
    expected_metrics={(c["cell"],c["cover"]):c for c in met["covers"]}
    ck(len(expected_metrics)==len(met["covers"]) and set(expected_metrics)==set(coverinfo),"all_cover_keys")
    pivots={p["tag"]:p for p in cert["pivots"]};stats=[];unique_rows=0
    def mat(rows,U,N):return S.matrix(S.GF(N),len(rows),U,{(i,j):v for i,r in enumerate(rows) for j,v in r})
    def normalized_pivot_check(source,stored,pivot,basis_rows,N):
        # Pure modular elimination against the span's echelon rows, followed by monic normalization.
        residual=[int(a)%N for a in source]
        stored=[int(a)%N for a in stored]
        width=len(residual)
        if len(stored)!=width or not 0<=pivot<width: return False
        echelon=[]
        for basis_row in basis_rows:
            row=[int(a)%N for a in basis_row]
            if len(row)!=width: return False
            lead=next((j for j,a in enumerate(row) if a),None)
            if lead is not None: echelon.append((lead,row))
        echelon.sort(key=lambda item:item[0])
        for lead,row in echelon:
            scale=residual[lead]*pow(row[lead],-1,N)%N
            residual=[(a-scale*b)%N for a,b in zip(residual,row)]
        lead=next((j for j,a in enumerate(residual) if a),None)
        if lead is None: return False
        inverse=pow(residual[lead],-1,N)
        normalized=[a*inverse%N for a in residual]
        return pivot==lead and stored==normalized
    normalization_controls=[
        ([],[2],[1],0,True),
        ([],[1],[1],0,True),
        ([],[2,4],[1,2],0,True),
        ([[1,1,0]],[2,0,2],[0,1,4],1,True),
        ([],[2,4],[1,3],0,False),
        ([],[2,4],[2,4],0,False),
        ([],[2,4],[1,2],1,False),
        ([[1,1]],[2,2],[1,0],0,False),
    ]
    detail["normalization_controls"]=[]
    for control_index,(basis_rows,source,stored,pivot,expected) in enumerate(normalization_controls):
        observed=normalized_pivot_check(source,stored,pivot,basis_rows,5)
        ck(observed==expected,"normalized_pivot_control",control_index)
        detail["normalization_controls"].append({"index":control_index,"modulus":5,"basis_rows":basis_rows,"source":source,"stored":stored,"pivot":pivot,"expected":expected,"observed":observed})
    for key,d in coverinfo.items():
        c,G,logs,bases,union=cells[key[0]];N=c["N"];m=expected_metrics[key];u=d["union"]
        fields={"ordered_pairs":len(u)**2,"union_size":len(u),"t":len(d["subset"]),"accepted_pairs":d["accepted"],"same_base_accepted_pairs":d["same"],"mixed_accepted_pairs":d["accepted"]-d["same"],"unique_single_base_pairs":len(set().union(*(set(itertools.product(bases[i],repeat=2)) for i in d["subset"])))}
        ck(d["attempts"]==len(u)**2,"raw_cover_exhaustion",key)
        for k,v in fields.items():ck(m[k]==v,"cover_metric_"+k,key)
        for name,rows in d["rows"].items():
            rr=sorted(rows);ss=[r for r in rr if rows[r]];U=len({i for i,w in d["maps"][name].values()})
            ma=mat(rr,U,N);ms=mat(ss,U,N);ar=int(ma.rank());sr=int(ms.rank());delta=ar-sr
            target=m["presentations"][name]
            wanted={"U":U,"all_rank":ar,"same_rank":sr,"Delta_rank":delta,"rank_deficit":U-ar,"unique_rows":len(rr),"matrix_nonzero_entries":sum(len(r) for r in rr),"maximum_coefficient_bits":max((v.bit_length() for r in rr for j,v in r),default=0),"added_pivot_witnesses":delta,"denominator_zero":delta==0,"ordered_pairs_per_Delta_rank_exact":None if delta==0 else {"numerator":len(u)**2,"denominator":delta}}
            ck(wanted==target,"all_presentation_metrics",(*key,name))
            if len(d["subset"])==1:ck(delta==0 and all(rows.values()),"single_base_control",(*key,name))
            tag=key[0]+":"+key[1]+":"+name;p=pivots[tag]
            ck(p["same_rank"]==sr and p["all_rank"]==ar and len(p["added"])==delta,"pivot_count",tag)
            span=ms.row_space()
            for w in p["added"]:
                row=tuple(map(tuple,w["source_row"]));r=S.vector(S.GF(N),U)
                v=S.vector(S.GF(N),U)
                for j,a in row:r[j]=a
                for j,a in w["residual"]["row"]:v[j]=a
                ck(row in rows and normalized_pivot_check(r,v,w["residual"]["pivot"],span.basis(),N),"pivot_witness",tag)
                span=span+S.span([r],S.GF(N))
            ck(span.dimension()==ar,"pivot_span_completion",tag)
            for r in rr:
                mu=c["mu"] if c["mu"] is not None else 1
                scaled=[tuple((j,v*pow(mu,k,N)%N) for j,v in r if v*pow(mu,k,N)%N) for k in range(c["n"])]
                ck(mat(scaled,U,N).rank()==int(bool(r)),"scalar_multiple_control")
            unique_rows+=len(rr);stats.append({"cell":key[0],"cover":key[1],"presentation":name,"same_rank":sr,"all_rank":ar,"Delta_rank":delta})
    mark("all_raw_pairs_metrics_and_pivots")
    # Check every recorded coefficient/relabel control against independently reconstructed rows.
    for control in cert["controls"]:
        kind=control["kind"]
        if kind.startswith("synthetic_generator"):
            c,G,logs,bases,un=cells[control["cell"]]
            ck(pt(c["generator"]) is not None and control["rejected"] is True,"synthetic_rejection_control")
        elif kind=="altered_point_coefficient":
            c,G,logs,bases,un=cells[control["cell"]];triple=list(map(pt,control["triple"]))
            coeff=control["coefficients"]
            valid=sum(a*logs[p] for a,p in zip(coeff,triple))%c["N"]==0
            ck(control["accidentally_valid"]==valid and control["rejected"]==(not valid),"altered_coefficient_control")
        elif kind=="generic_relabel":
            key=control["cell"],control["cover"];d=coverinfo[key];c,G,logs,bases,un=cells[key[0]]
            seed=control["seed"];ordered=sorted(G[1:],key=lambda p:(hashlib.sha256(f"{seed}:{p[0]},{p[1]}".encode("ascii")).digest(),p))
            labels={p:i+1 for i,p in enumerate(ordered)};labels[None]=0
            decode_labels={i:p for p,i in labels.items()}
            ck(len(labels)==len(decode_labels)==len(G)==control["table_entries"],"generic_injective_labels")
            target=expected_metrics[key]["presentations"][control["presentation"]]
            ck(control["same_rank"]==target["same_rank"] and control["all_rank"]==target["all_rank"] and control["incidence_rows_weights_identical"],"generic_control_metric_binding")
            # Deterministic transported addition is isomorphic on each cover's complete pair domain.
            for p,r in itertools.product(d["union"],repeat=2):
                third=G[-(logs[decode_labels[labels[p]]]+logs[decode_labels[labels[r]]])%c["N"]]
                ck(decode_labels[labels[third]]==third,"generic_transported_pair")
        elif kind=="t1_precompute":
            rows=[e for e in events["calibration_pair"] if e["tag"]==control["tag"] and e["presentation"]==control["presentation"]]
            base=next(e["points"] for e in events["calibration_start"] if e["tag"]==control["tag"]);base=list(map(pt,base))
            tag=control["tag"].removesuffix(":precompute");q,n,A,B,order,N,P,G=tags[tag];L={p:i for i,p in enumerate(G)}
            ck(len(rows)==len(base)**2 and control["Delta_rank"]==0 and control["nonempty_base_size"]==len(base)>0,"precompute_nonempty_baseline")
            for i,e in enumerate(rows):
                p,r=base[i//len(base)],base[i%len(base)];third=G[-(L[p]+L[r])%N]
                ck(e["index"]==i and pt(e["Q1"])==p and pt(e["Q2"])==r and pt(e["Q3"])==third and e["accepted"]==(third is not None and third in base),"precompute_pair")
        else: ck(False,"unknown_control",kind)
    counts_record=run["resources"]["counts"]
    for k,event in [("raw_records",None),("ordered_pairs_including_failures","pair_attempt"),("calibration_ordered_pairs","calibration_pair"),("irreducible_polynomials_tested","field_polynomial_candidate"),("null_curve_candidates","null_curve_order")]:
        ck(counts_record[k]==(sum(kinds.values()) if event is None else kinds[event]),"cost_event_count",k)
    ck(counts_record["generic_relabel_attempt_checks"]==2*kinds["pair_attempt"],"generic_cost_count")
    ck(counts_record["independent_relation_checks"]==sum(c["accepted_pairs"] for c in met["covers"]),"accepted_relation_count")
    ck(counts_record["scalar_rank_null_rows_checked"]==unique_rows+sum(c["unique_rows"] for c in cert["controls"] if c["kind"]=="t1_precompute"),"scalar_null_count")
    ck(counts_record["sage_matrix_rank_calls"]==2*len(cert["pivots"]),"rank_call_count")
    planned=set(spec["inputs"]["cell_ids"]+spec["inputs"]["null_cell_ids"])
    ck({c["id"] for c in met["cells"]}==planned and len(met["cells"])==len(fx["cells"])==12,"panel_all_terminal_cells")
    ck(sum(c["status"]=="completed" for c in met["cells"])==9 and res["panel_complete"] is False,"incomplete_panel_truth")
    norm={(v["cell"],v["cover"],v["presentation"]):v for v in res["normalization"]}
    for s in stats:
        k=s["cell"],s["cover"],s["presentation"];d=s["Delta_rank"];r=norm[k]
        ck(r["Delta_rank"]==d and r["denominator_zero"]==(d==0) and r["total_aggregate_instrument_cpu_per_Delta_rank"]==(None if d==0 else run["timing"]["cpu_seconds"]/d),"normalization_binding",k)
    elapsed=(datetime.datetime.fromisoformat(run["timing"]["finished_at"])-datetime.datetime.fromisoformat(run["timing"]["started_at"])).total_seconds()
    ck(abs(elapsed-run["timing"]["wall_seconds"])<0.1,"wall_timestamp_consistency")
    ck(run["finalization_boundary"]["cpu_seconds_through_pre_manifest"]>=run["timing"]["cpu_seconds"] and run["finalization_boundary"]["wall_seconds_through_pre_manifest"]>=run["timing"]["wall_seconds"],"finalization_separate_boundary")
    for c in met["cells"]:
        if c["status"]=="completed": ck(c["cover_count"]==sum(k[0]==c["id"] for k in coverinfo),"cell_cover_count")
    detail.update({"event_counts":dict(kinds),"cover_count":len(coverinfo),"presentation_count":len(stats),"rank_results":stats,"cell_statuses":met["cells"],"producer_checker_checks_not_reused":cert["package_checker"]["checks"],"producer_costs":{"cpu_seconds":run["timing"]["cpu_seconds"],"wall_seconds":run["timing"]["wall_seconds"],"peak_rss_bytes":run["resources"]["peak_rss_bytes"],"finalization":run["finalization_boundary"]}})
    mark("controls_costs_and_panel_binding")
except BaseException as error:
    failures.append({"check":"review_execution_exception","exception":repr(error),"traceback":traceback.format_exc()})
    traceback.print_exc()
finally:
    print(json.dumps({"review_finished":True,"started_at":started,"finished_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),"review_wall_seconds":time.monotonic()-t0,"review_cpu_seconds":time.process_time()-c0,"review_peak_rss_bytes":rss(),"check_counts":dict(counts),"failure_count":len(failures),"failures":failures[:200],"all_failures_retained":len(failures)<=200,"stages":stages,"details":detail,"sources_read":sorted(sources)},sort_keys=True),flush=True)
