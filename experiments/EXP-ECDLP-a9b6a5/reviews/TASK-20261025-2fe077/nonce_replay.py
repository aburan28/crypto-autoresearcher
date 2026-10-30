"""Post-publication nonce-selected witness replay for review-run compatibility.

The full descriptor census was already completed without sampling. This
additional audit records a fresh draw before verifying the selected witnesses.
"""
import hashlib
import json
import random
import secrets


def audit(reader,g,h):
    out='experiments/EXP-ECDLP-a9b6a5/reviews/TASK-20261025-2fe077'
    fixtures=json.loads(reader.read('research/prym_factor_base_width_20261025/fixtures.json'))['fixtures']
    raw=json.loads(reader.read('experiments/EXP-ECDLP-a9b6a5/export-inputs/RUN-ECDLP-967315/raw-result.json'))
    population=[(c,i) for c,cell in enumerate(raw['cells']) for i in range(len(cell['rows']))]
    nonce=secrets.token_hex(32)
    drawn=g['now']()
    selected=random.Random(nonce).sample(population,16)
    draw={'schema':'fresh-review-nonce-draw/v1','nonce':nonce,'drawn_at':drawn,
          'population':'164 accepted rows, each unit checks original and transported principal/E1/E2 witnesses',
          'population_size':len(population),'selection':'random.Random(actual_nonce).sample(population,16)',
          'selected':selected,
          'chronology':'Drawn after published release and after exhaustive full-stream validation; not used to claim a sampled origin for that earlier census.'}
    draw_artifact=h['save']('nonce-replay-draw.json',draw)
    checks=[]
    for c,i in selected:
        fixture,cell=fixtures[c],raw['cells'][c]
        row=cell['rows'][i]
        h['verify_row'](fixture,row,g)
        other,transported=h['transport'](fixture,row)
        h['verify_row'](other,transported,g)
        h['check'](h['digest'](transported)==cell['transported_witness_hashes'][i],'nonce selected transported hash differs')
        checks.append({'b':fixture['b'],'row_index':i,'original_sha256':h['digest'](row),'transported_sha256':h['digest'](transported),'identical':True})
    result={'schema':'fresh-review-nonce-replay/v1','generated_at':g['now'](),'status':'passed',
            'nonce':nonce,'drawn_at':drawn,'draw_artifact':draw_artifact,
            'unit':'one accepted row with original and transported principal/E1/E2 verification',
            'units_sampled':16,'identical':16,'mismatched':0,'checks':checks,
            'miss_probability':{str(f):(1-f)**16 for f in (0.01,0.05,0.1,0.2)},
            'miss_probability_scope':'Conservative (1-f)^16 sampling bound for corrupted accepted-witness units. Full descriptor census is independently checked separately, including all rejected statuses.',
            'no_new_scientific_arm':True}
    artifact=h['save']('nonce-replay.json',result)
    print(json.dumps({'nonce_replay':artifact,'actual_nonce':nonce,'drawn_at':drawn,'sample_units':16}),flush=True)
    return result
