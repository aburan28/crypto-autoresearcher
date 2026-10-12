#!/usr/bin/env python3
"""Index completed batches in SQLite, without pooling dependent point samples."""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from research import canonical


def catalog(root,output):
    output=Path(output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(output) as database:
        database.executescript('''
        CREATE TABLE IF NOT EXISTS batches (
          design_sha256 TEXT PRIMARY KEY, path TEXT NOT NULL, seed TEXT NOT NULL,
          config_json TEXT NOT NULL, verification_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS blocks (
          design_sha256 TEXT NOT NULL, job_id TEXT NOT NULL, case_name TEXT NOT NULL,
          mode TEXT NOT NULL, cohort TEXT NOT NULL, arm TEXT NOT NULL,
          field_id TEXT NOT NULL, model_uid TEXT NOT NULL, generator_uid TEXT,
          points INTEGER NOT NULL, raw_sha256 TEXT NOT NULL, raw_path TEXT NOT NULL,
          x_lag1 REAL, bit64_lag1 REAL, bit96_lag1 REAL,
          x_bin_dispersion REAL, xy_correlation REAL,
          PRIMARY KEY (design_sha256, job_id)
        );
        CREATE INDEX IF NOT EXISTS block_population ON blocks(case_name,mode,cohort,arm);
        ''')
        batches=0;rows=0
        for design_path in sorted(Path(root).resolve().rglob('design.json')):
            folder=design_path.parent
            if not (folder/'receipt.json').exists() or not (folder/'verification.json').exists():continue
            verification=json.loads((folder/'verification.json').read_text())
            if verification['status']!='passed':continue
            design=json.loads(design_path.read_text());sha=hashlib.sha256(canonical(design)).hexdigest()
            database.execute('INSERT OR IGNORE INTO batches VALUES (?,?,?,?,?)',
                             (sha,str(folder),str(design['config']['seed']),json.dumps(design['config'],sort_keys=True),json.dumps(verification,sort_keys=True)))
            for record_path in sorted((folder/'records').glob('*.json')):
                record=json.loads(record_path.read_text());job=record['job'];features=record['features'];raw=record['raw']
                if record['design_sha256']!=sha:raise ValueError('Catalog record belongs to another design')
                previous=database.execute('SELECT raw_sha256 FROM blocks WHERE design_sha256=? AND job_id=?',(sha,job['id'])).fetchone()
                if previous and previous[0]!=raw['sha256']:raise ValueError('Identical design/seed has different data')
                values=(sha,job['id'],job['case'],job['mode'],job['cohort'],job['arm'],job['field_id'],record['model_uid'],
                        record['generator_identity']['curve_uid'] if record['generator_identity'] else None,
                        features['points'],raw['sha256'],str(folder/raw['path']),
                        *[features[k] for k in ('x_lag1','bit64_lag1','bit96_lag1','x_bin_dispersion','xy_correlation')])
                database.execute('INSERT OR IGNORE INTO blocks VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',values)
                rows+=1
            batches+=1
        total_batches=database.execute('SELECT COUNT(*) FROM batches').fetchone()[0]
        total_blocks=database.execute('SELECT COUNT(*) FROM blocks').fetchone()[0]
    print(json.dumps({'scanned_complete_batches':batches,'scanned_records':rows,'unique_batches':total_batches,
                      'unique_blocks':total_blocks,'database':str(output),
                      'inference_note':'Index only. Repeated seeds/designs deduplicate; field/model IDs remain available for clustered analysis. No pooled significance claim.'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();catalog(args.root,args.output)
