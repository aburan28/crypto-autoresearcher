"""Exploratory exact-cubic links among already-verified accepted witnesses."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    connection=sqlite3.connect('file:'+str(args.database.resolve())+'?mode=ro',uri=True)
    connection.row_factory=sqlite3.Row
    old=list(connection.execute("SELECT e.*,o.base_sha256,o.execution_id FROM equations e JOIN observations o USING(observation_id) WHERE o.arm='historical_nonzero' ORDER BY observation_id,row_index"))
    new=list(connection.execute("SELECT e.*,o.base_sha256,o.execution_id FROM equations e JOIN observations o USING(observation_id) WHERE o.arm='completed_zero' AND e.constraint_zero=1 ORDER BY observation_id,row_index"))
    matches,unmatched=[],[]
    for row in new:
        witness=json.loads(row['witness_json']);match=None
        for candidate in old:
            if any(candidate[k]!=row[k] for k in ('base_sha256','execution_id','function_id','normalized_affine_json')):continue
            previous=json.loads(candidate['witness_json'])
            if all(previous[k]==witness[k] for k in ('source_scalar','v_coefficients','coefficients')):
                match=candidate;break
        pointer=dict(observation_id=row['observation_id'],row_index=row['row_index'])
        if match is None:unmatched.append(pointer);continue
        matches.append(dict(new=pointer,old=dict(observation_id=match['observation_id'],row_index=match['row_index']),
                            source_scalar=witness['source_scalar'],v_coefficients=witness['v_coefficients'],
                            native_coefficients=witness['coefficients'],normalized_affine_json=row['normalized_affine_json']))
    connection.close()
    result=dict(schema='prime-field-retained-reencodings/v1',analysis_scope='Exploratory retained-witness equality after frozen B1 collection; no new branch/target draw.',
                database_sha256=sha256(args.database.read_bytes()).hexdigest(),script_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                constraint_zero_witnesses=len(new),same_source_cubic_native_coefficients=len(matches),
                matches=matches,unmatched=unmatched,
                limitation='Equality links use source-verified public witnesses, not an independent scientific review or cache/speedup benchmark.')
    with args.out.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(json.dumps(dict(tested=len(new),matched=len(matches),unmatched=len(unmatched))))


if __name__=='__main__':main()
