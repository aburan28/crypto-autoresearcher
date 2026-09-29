#!/usr/bin/env python3
"""V1 cold re-run comparison: archived raw-result.json vs fresh re-run."""
import json
import sys

runs = [
    ('RUN-MDFIVE-b6-primary-md4-prod', 'md4', 'primary'),
    ('RUN-MDFIVE-b6-primary-md5-prod', 'md5', 'primary'),
    ('RUN-MDFIVE-b6-null-md4-prod', 'md4', 'null'),
    ('RUN-MDFIVE-b6-null-md5-prod', 'md5', 'null'),
]

archived_root = 'coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/tasks/TASK-20260822-767bb1/runs'
fresh_root = 'coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/reviews/TASK-20260822-7f5ed3/runs'

total_compared = 0
total_matched = 0
all_mismatches = []
per_run_results = []

for run_id, prim, obj in runs:
    archived_path = f'{archived_root}/{run_id}/raw-result.json'
    fresh_path = f'{fresh_root}/{run_id}-v1check/raw-result.json'

    with open(archived_path) as f:
        archived = json.load(f)
    with open(fresh_path) as f:
        fresh = json.load(f)

    run_mismatches = []
    run_compared = 0
    run_matched = 0

    for i in range(100):
        a_seed = archived['per_seed'][i]
        f_seed = fresh['per_seed'][i]

        assert a_seed['seed'] == f_seed['seed'], (
            f"Seed mismatch at index {i}: {a_seed['seed']} vs {f_seed['seed']}"
        )

        # Compare direction_A_rows (fwd distinct counts)
        for j, (a_row, f_row) in enumerate(
            zip(a_seed['direction_A_rows'], f_seed['direction_A_rows'])
        ):
            for field in ['distinct_fwd_32bit', 'distinct_fwd_12bit']:
                run_compared += 1
                if a_row[field] == f_row[field]:
                    run_matched += 1
                else:
                    run_mismatches.append({
                        'seed': a_seed['seed'],
                        'field': f'direction_A_row{j}.{field}',
                        'archived': a_row[field],
                        'fresh': f_row[field]
                    })

            # For primary object, also compare values_32bit
            if 'values_32bit' in a_row:
                run_compared += 1
                if a_row['values_32bit'] == f_row['values_32bit']:
                    run_matched += 1
                else:
                    run_mismatches.append({
                        'seed': a_seed['seed'],
                        'field': f'direction_A_row{j}.values_32bit',
                        'archived_first4': a_row['values_32bit'][:4],
                        'fresh_first4': f_row['values_32bit'][:4]
                    })

        # Compare direction_B_rows (bwd distinct counts)
        for j, (a_row, f_row) in enumerate(
            zip(a_seed['direction_B_rows'], f_seed['direction_B_rows'])
        ):
            for field in ['distinct_bwd_32bit', 'distinct_bwd_12bit']:
                run_compared += 1
                if a_row[field] == f_row[field]:
                    run_matched += 1
                else:
                    run_mismatches.append({
                        'seed': a_seed['seed'],
                        'field': f'direction_B_row{j}.{field}',
                        'archived': a_row[field],
                        'fresh': f_row[field]
                    })

        # Compare CTL-PO5 raw_candidate_count
        run_compared += 1
        a_count = a_seed['ctl_po5_k1_k2_6']['raw_candidate_count']
        f_count = f_seed['ctl_po5_k1_k2_6']['raw_candidate_count']
        if a_count == f_count:
            run_matched += 1
        else:
            run_mismatches.append({
                'seed': a_seed['seed'],
                'field': 'ctl_po5_k1_k2_6.raw_candidate_count',
                'archived': a_count,
                'fresh': f_count
            })

    total_compared += run_compared
    total_matched += run_matched
    all_mismatches.extend(run_mismatches)
    per_run_results.append({
        'run_id': run_id,
        'compared': run_compared,
        'matched': run_matched,
        'mismatches': len(run_mismatches)
    })
    print(f'{run_id}: {run_matched}/{run_compared} matched, '
          f'{len(run_mismatches)} mismatches')

print(f'\nTOTAL: {total_matched}/{total_compared} matched, '
      f'{len(all_mismatches)} mismatches')

if all_mismatches:
    print('MISMATCHES (first 20):')
    for m in all_mismatches[:20]:
        print(f'  {m}')

# Output structured result for the report
result = {
    'total_compared': total_compared,
    'total_matched': total_matched,
    'total_mismatches': len(all_mismatches),
    'per_run': per_run_results,
    'mismatches': all_mismatches,
}
with open(
    'coordination/goals/GOAL-MD5-001/batches/BATCH-ebac02/reviews/'
    'TASK-20260822-7f5ed3/comparison-result.json', 'w'
) as f:
    json.dump(result, f, indent=2)
print('\nWrote comparison-result.json')
