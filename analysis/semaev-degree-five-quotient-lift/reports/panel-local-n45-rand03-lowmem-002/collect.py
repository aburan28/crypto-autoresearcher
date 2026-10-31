"""Render the verified n45 random03 low-memory panel result and export."""
from pathlib import Path

source = Path('analysis/semaev-degree-five-quotient-lift/reports/panel-local-n45-rand00-001/collect.py').read_text()
source = source.replace('rand00', 'rand03').replace('rand-00', 'rand-03').replace('random00', 'random03')
source = source.replace('rref-local01', 'rref-lowmem01')
source = source.replace('panel-local-n45-rand03-final-001', 'panel-local-n45-rand03-lowmem-final-001')
source = source.replace('panel-local-n45-rand03-001', 'panel-local-n45-rand03-lowmem-002')
source = source.replace('panel-local-n45-rand03-protocol-001', 'panel-local-n45-rand03-lowmem-protocol-002')
source = source.replace('panel-local-n45-rand03-plan-001', 'panel-local-n45-rand03-lowmem-plan-002')
source = source.replace('local008', 'local011')
source = source.replace("result['exact_solutions'] == 2", "result['exact_solutions'] == 0")
source = source.replace("'exact_solutions': 2", "'exact_solutions': 0")
source = source.replace('found **2** solutions', 'found **0** solutions')
source = source.replace('found *2* solutions', 'found *0* solutions')
source = source.replace('solutions = 2', 'solutions = 0')
source = source.replace('46,472 &gt; 2', '46,472 &gt; 0')
source = source.replace('count 2', 'count 0')
source = source.replace("== 28 and inventory['certified_lfd_at_least5'] == 21", "== 31 and inventory['certified_lfd_at_least5'] == 24")
source = source.replace('28 terminal inputs', '31 terminal inputs').replace('21 certified lower bounds', '24 certified lower bounds')
source = source.replace('four remaining original', 'one remaining original')
source = source.replace('28 terminal, 21 certified LFD-at-least-five, and four remaining', '31 terminal, 24 certified LFD-at-least-five, and one remaining')
source = source.replace('one remaining original n45 random-subspace inputs', 'one remaining original n45 random-subspace input')
source = source.replace('and one remaining inputs', 'and one remaining input')
source = source.replace('40 GiB child cap', '24 GiB child cap')
source = source.replace('SEMAEV-PANEL-LOCAL-N45-RAND00-001', 'SEMAEV-PANEL-LOCAL-N45-RAND03-LOWMEM-001')
source = source.replace('The separate n47 random02 D5 search is running from a verified checkpoint; it has no degree-five certificate yet.',
                        'The separate n47 random03 D5 cloud Job failed without a degree-five certificate; the n48 poly04 local D5 attempt is frozen and queued after this terminal panel result.')
assert 'rand00' not in source and 'rand-00' not in source and 'random00' not in source
assert '40 GiB child cap' not in source and '28 terminal inputs' not in source
exec(compile(source, __file__, 'exec'))
