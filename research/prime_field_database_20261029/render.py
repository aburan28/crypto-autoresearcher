"""Render descriptive B1/database reports from retained values only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import subprocess

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run',type=Path,required=True)
    p.add_argument('--database',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    analysis = json.loads((args.run/'analysis.json').read_text())
    execution = json.loads((args.run/'execution.json').read_text())
    host = json.loads((args.run/'host.json').read_text())
    export = json.loads((args.run/'export.json').read_text())
    fixtures = json.loads((ROOT/'research/prym_factor_base_width_20261025/fixtures.json').read_text())['fixtures']
    fixture_map = {f['uid']:f for f in fixtures}
    cells = analysis['cells']
    data = [{key:cell.get(key) for key in ('arm','curve_uid','witnesses','unique_equations','rank',
            'nullity','new_distinct_equations','span_rank_gain','source_zero_witnesses',
            'constraint_zero_witnesses','nonzero_old_kernel_syndromes')} for cell in cells]
    (args.out/'plotted-data.json').write_text(json.dumps(data,indent=2)+'\n')
    plt.rcParams.update({'font.size':9,'svg.fonttype':'none'})
    fig,axes = plt.subplots(1,3,figsize=(9.4,2.4))
    arms = ('historical_nonzero','completed_zero')
    colors = ('#2166ac','#c85e18')
    for axis,metric,title in zip(axes,('witnesses','unique_equations','rank'),('Accepted witnesses','Distinct affine equations','Projected rank / 15')):
        for j,arm in enumerate(arms):
            values = [next(c[metric] for c in cells if c['curve_uid']==f['uid'] and c['arm']==arm) for f in fixtures]
            axis.bar([i+(j-.5)*.35 for i in range(len(fixtures))],[v or 0 for v in values],width=.33,
                     color=colors[j],label='Historical' if j==0 else 'Completed zero')
            for i,value in enumerate(values):
                axis.annotate('unknown' if value is None else str(value),(i+(j-.5)*.35,value or 0),
                              xytext=(0,3),textcoords='offset points',ha='center',fontsize=8)
        axis.set_xticks(range(len(fixtures)),[f"b={f['b']}" for f in fixtures])
        axis.set_title(title);axis.set_ylabel('objects');axis.set_ylim(0,max(1,axis.get_ylim()[1])*1.16)
        axis.spines[['top','right']].set_visible(False)
    axes[0].legend(loc='upper left',fontsize=7)
    fig.suptitle(f"{args.run.name}: two fixed curves over F4099; one full census per arm",fontsize=10)
    fig.tight_layout();fig.savefig(args.out/'observations.svg');plt.close(fig)
    svg=args.out/'observations.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    diagram = '''digraph archive {
      rankdir=LR; ranksep=0.18; nodesep=0.15; graph [bgcolor="transparent",fontname="Helvetica"];
      node [shape=box,style="rounded,filled",fillcolor="#edf3f8",fontname="Helvetica",fontsize=10];
      inputs [label="Frozen inputs\n16 atoms; 64 sources"];
      collect [label="Full collection\ntwo arms"];
      replay [label="Separate replay\ncomplete stream"];
      analysis [label="Old-kernel test\nnew equations"];
      database [label="SQLite archive\nsource hashes"];
      functions [label="Cubic groups\ncache unmeasured"];
      shifted [label="Shifted algebra\nsurvey unrun",fillcolor="#fff1d9"];
      inputs -> collect -> replay -> analysis -> database -> functions;
      analysis -> shifted [style=dashed,label="proposed",fontsize=9];
    }'''
    (args.out/'pipeline.dot').write_text(diagram+'\n')
    subprocess.run(['dot','-Tsvg',str(args.out/'pipeline.dot'),'-o',str(args.out/'pipeline.svg')],check=True)
    connection = sqlite3.connect('file:'+str(args.database.resolve())+'?mode=ro',uri=True)
    connection.row_factory = sqlite3.Row
    reuse = [dict(row) for row in connection.execute('SELECT o.arm,b.fixture_uid,c.b,s.witnesses,s.cubic_orbits,s.distinct_equations FROM cubic_reuse_summary s JOIN observations o USING(observation_id) JOIN bases b USING(base_sha256) JOIN curves c USING(curve_uid) ORDER BY CAST(c.b AS INTEGER),o.arm')]
    tables = {table:connection.execute('SELECT COUNT(*) FROM '+table).fetchone()[0] for table in
              ('curves','bases','atoms','actions','observations','equations','principal_functions','sources')}
    connection.close()
    (args.out/'database-counts.json').write_text(json.dumps(dict(tables=tables,cubic_reuse=reuse),indent=2)+'\n')
    def t(value):
        return json.dumps('unknown' if value is None else str(value))
    table_rows = '\n'.join(','.join('['+str(v)+']' for v in
        (fixture_map[c['curve_uid']]['b'],'historical' if c['arm']==arms[0] else 'completed',c['status'],
         c['witnesses'],c['unique_equations'],c['rank'],c['nullity']))+',' for c in cells)
    differences = '\n'.join(f"- b={fixture_map[c['curve_uid']]['b']}: {c.get('new_distinct_equations')} new distinct equations; rank increment {c.get('span_rank_gain')}; {c.get('nonzero_old_kernel_syndromes')} witness rows with nonzero old-kernel syndrome. Source-zero witnesses {c.get('source_zero_witnesses')}; constraint-zero witnesses {c.get('constraint_zero_witnesses')}." for c in cells if c['arm']==arms[1])
    phase_text = '\n'.join(f"- b={fixture_map[p['curve_uid']]['b']}, {p['arm']}, {p['phase']}: {p['status']}; CPU {p['cpu_seconds']:.3f}s, wall {p['wall_seconds']:.3f}s." for p in export['backend_record']['phase_records'])
    reuse_text = '\n'.join(f"- b={r['b']}, {r['arm']}: {r['witnesses']} accepted witnesses, {r['cubic_orbits']} cubic orbits, {r['distinct_equations']} distinct affine equations." for r in reuse)
    reencoding_path=args.database.parent/'reencodings.json'
    reencoding_note=''
    if reencoding_path.is_file():
        links=json.loads(reencoding_path.read_text())
        reencoding_note=f"Exploratory exact re-encoding check: {links['same_source_cubic_native_coefficients']} of {links['constraint_zero_witnesses']} constraint-zero witnesses share the same public source, full cubic and native coefficient vector with a historical witness. Original-row links are in database/reencodings.json. This is stronger than matching a coarse orbit key, within these accepted rows only."
    protocol_hash = export['protocol']['sha256']
    source = f'''#set page(paper: "a4", margin: 16mm)
#set text(size: 9pt)
#set par(justify: false)
= Fixed Prym x=0 completion and prime-field archive
Observations only. This report records one physical paired panel and a derived archive import. It promotes no scientific status or performance claim.

Run: #raw({t(args.run.name)}). Curves: p=4099, a=2; b=13, r=4021, P=(0,264), and b=16, r=4111, P=(0,4). Both original bases have sixteen atoms, with fifteen unknown signed columns after public anchors. The exact curve/base identities and source arrays remain in the frozen inputs.

== Observed coverage
Panel complete: {analysis['panel_complete']}. Collection branches: {analysis['collection_attempts_observed']}; separate replay branches: {analysis['verification_attempts_observed']}. Unknown cells: {analysis['unknown_cells']}. No rank-based stop or substituted inputs. A/A and statistical null arms are inapplicable to this deterministic complete census; marked-small software positives and corruption controls preceded the freeze. Separate full replay checks actual finite outputs; it is not independent scientific review.

#table(columns: (auto,auto,auto,auto,auto,auto,auto), inset: 4pt,
  [b],[arm],[status],[witnesses],[equations],[rank],[nullity],
  {table_rows}
)
#image("observations.svg",width: 100%)
Counts are exact within the two fixed inputs; no population interval or extrapolation is implied. Distinct equations are normalized affine rows, including the public-anchor-adjusted right side.

{differences}

== Diagnostic resources and retained failures
Exit {execution['returncode']}, timeout {execution['timeout']}, source unchanged after {execution['source_unchanged_after']}. Wall {execution['diagnostic_wall_seconds']:.3f}s, user CPU {execution['cpu_user_seconds']:.3f}s, system CPU {execution['cpu_sys_seconds']:.3f}s, peak RSS {execution['max_rss_bytes']} bytes. Host {host['cpu_model']}; kernel {host['kernel']}. These shared-host clocks have wall_valid=false. Collection operation vectors exclude replay, complete elimination/serialization/storage accounting and full S; no rate or speedup is inferred.

{phase_text}

#pagebreak()
== Reproducibility and provenance
Frozen protocol canonical SHA256: #raw({t(protocol_hash)}). Exact source commit: #raw({t(execution['source_commit'])}). Source/release/input/interpreter/package locks, actual S3 gate, owner/PIDs, host facts, stdout/stderr, every source status string/digest, accepted witness and phase record are retained in the run directory. The full analysis was frozen before data; compressed records preserve original-byte hashes in archive-encoding.json. Data were published before this report. Administrative failures are retained separately and do not count as failed mathematical trials.

#image("pipeline.svg",width: 100%)

== Derived database and an exploratory symmetry lead
Coverage: {tables['curves']} curves, {tables['bases']} exact bases, {tables['atoms']} projected atoms, {tables['actions']} action audits, {tables['observations']} observation cells, {tables['equations']} witnessed rows. Exact field/group integers use decimal TEXT. The archive binds {tables['sources']} source files by bytes/hash and stores process resources once. Retained historical observations have NULL attempt counts where unavailable. Hash import reports the source's verification scope and confers no independent proof.

On the even sextic, the existing deck/negation action transforms a cubic to sign * v(deck * X). These are accepted-witness grouping counts derived after collection, separate from the frozen primary analysis:

{reuse_text}

{reencoding_note}

An equal cubic key does not erase source-specific obligations or certify reuse of a residual computation. Rejected candidates are not covered by these counts. The next caching study must preserve all branches, charge interpolation/setup, compare identical outputs and separately measure validation. B1 itself has no cache enabled.

== Limits and next measurements
The paired finite result concerns only the exact two retained curves, bases, source order and cubic law. More witnesses, more equations and more information are different quantities. Full rank is not required by the separate natural-target criterion vN=0. Eight independent natural targets remain ungenerated in this panel; D1, natural partial relations and native many-target operator reuse remain separate measurements. Original C1/Prym reports and their historical graphs remain unchanged.

== Shifted-cover algebra: implemented, not collected
The new ShiftedCover software interface keeps the same E and uses C_h: y²=f(x²+h), with coefficients c4=3h, c2=3h²+a, c0=f(h). The maps (x,y) to (x²+h,y) and, for nonzero x, (c0/x²,c0*y/x³), satisfy their quotient equations by substitution. The latter auxiliary curve has coefficients (c2,c4*c0,c0²), including the term absent at h=0. The software rejects a singular base or f(h)=0 and deduplicates the x=0 lift. Fixed p101 software controls exercise h=0,1,2,3; there is no shift search on the retained p4099 curves here.

A prospective common-atom survey would retain only h for which every original atom coordinate u has u-h square or zero, freezing selection before relation yields. A later collector must preserve original E/base/log columns, source schedule, poles and signs. This is a genus-two cover interface; no elliptic isogeny, subgroup eigenvalue, Jacobian certificate or advantage is asserted. See shifted-covers.md for the derived identities and exact successor boundary.

Sources (internal/retrieved): original Context/Census and fixed inputs; B1 literature.md and frozen protocol; database schema.sql/build.py and source-bound generation receipt; Petit, Kosters, Messeng, PKC2016, sections 3.1-3.2, primary PDF SHA256 a53030a6cde720c354aebfb65b1eb01e07766ce2d26e543d77f2516c0a49ef5b. Solver and linear-algebra costs stay charged. No novelty, complete ECDLP recovery or asymptotic claim.
'''
    (args.out/'report.typ').write_text(source)
    typst.compile(str(args.out/'report.typ'),output=str(args.out/'report.pdf'),root=str(args.out.resolve()))
    print(json.dumps(dict(report=str(args.out/'report.pdf'),sha256=sha256((args.out/'report.pdf').read_bytes()).hexdigest(),tables=tables)))


if __name__ == '__main__':
    main()
