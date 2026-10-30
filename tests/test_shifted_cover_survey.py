"""Marked small-field controls for full survey coverage and refusals."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def survey(monkeypatch):
    old = ROOT/'research/prym_experiment_design_20261019/implementation'
    monkeypatch.syspath_prepend(str(old))
    for name in ('arithmetic','independent','relations','fixtures'):
        spec = importlib.util.spec_from_file_location(name,old/(name+'.py'))
        module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        monkeypatch.setitem(sys.modules,name,module)
    spec = importlib.util.spec_from_file_location('cover_survey_driver',ROOT/'research/prime_field_cover_survey_20261029/driver.py')
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    from fixtures import describe
    fixture,_ = describe(101,2,21,8)
    fixture.update(software_control=True,width_binding=dict(source_order=[1,2]),
                   ec1=dict(curve_uid='marked-small-software-curve'))
    return module,fixture


def test_complete_small_field_and_corruption_controls(survey):
    module,fixture = survey
    result = module.survey([fixture])
    check = module.check([fixture],result)
    assert check['checked'] and check['frames_checked']==101 and check['source_points_checked']==2
    cell = result['cells'][0]
    assert cell['rows'][0]['eligible'] and 0 in cell['eligible_h']
    assert cell['counters']['modular_pow_calls']==101*(8+2)
    assert all(row['base_square_mask'][i]=='1' for row in cell['rows']
               for i,bit in enumerate(row['base_zero_mask']) if bit=='1')
    mutations = [lambda v:v['cells'][0]['rows'].pop(),
                 lambda v:v['cells'][0]['rows'][0].update(c4=1),
                 lambda v:v['cells'][0]['rows'][0].update(base_square_mask='0'*8),
                 lambda v:v['cells'][0]['rows'][0].update(source_zero_mask='11'),
                 lambda v:v['cells'][0].update(eligible_h=[]),
                 lambda v:v['cells'][0]['source_points'].__setitem__(0,[0,0])]
    for mutate in mutations:
        corrupt=deepcopy(result);mutate(corrupt)
        with pytest.raises(ValueError):module.check([fixture],corrupt)


def test_no_unadmitted_scientific_survey(survey):
    module,fixture = survey
    fixture.pop('software_control')
    with pytest.raises(ValueError,match='admission'):module.survey([fixture])
