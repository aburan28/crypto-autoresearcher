"""Exploratory membership-only candidates from a completed cover archive."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--database',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    c=sqlite3.connect('file:'+str(args.database.resolve())+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
    candidates=[]
    for base in c.execute('SELECT * FROM bases ORDER BY fixture_uid').fetchall():
        maximum=c.execute("SELECT MAX(atoms_with_lifts) FROM cover_admissibility WHERE base_sha256=? AND h!='0'",(base['base_sha256'],)).fetchone()[0]
        for row in c.execute('''SELECT a.*,f.base_square_mask FROM cover_admissibility a JOIN cover_frames f USING(execution_id,base_sha256,h)
                WHERE a.base_sha256=? AND a.h!='0' AND a.atoms_with_lifts=? ORDER BY CAST(a.h AS INTEGER)''',(base['base_sha256'],maximum)).fetchall():
            candidates.append(dict(row,missing_native_atom_indices=[i for i,bit in enumerate(row['base_square_mask']) if bit=='0']))
    c.close()
    value=dict(schema='prime-field-exploratory-cover-subsets/v1',database_sha256=sha256(args.database.read_bytes()).hexdigest(),
               script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
               selection='All nonzero shifts tied for maximum original-atom lift count on each fixed base; source counts retained, not used to discard ties. Selection uses no relation yield.',
               frozen_primary_metric=False,new_collection_attempts=0,candidates=candidates,
               next_test='Separately freeze h0 versus h on each same admissible E-atom subset, original unknown columns and public sources; complete checked collectors and score new old-kernel information per charged cost.')
    with args.out.open('x') as s:json.dump(value,s,indent=2);s.write('\n')
    print(json.dumps(dict(candidates=len(candidates))))


if __name__=='__main__':main()
