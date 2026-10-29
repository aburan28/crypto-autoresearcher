"""Software identities for target reuse; no timing or P-256 query."""
from collections import Counter
import importlib.util
from pathlib import Path
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]
F1=ROOT/'research/p256_factor_base_parallel_20261026/tracks/f1'


@pytest.fixture
def family(monkeypatch):
    pytest.importorskip('flint')
    monkeypatch.syspath_prepend(str(F1))
    for name in ('core','exterior'):
        spec=importlib.util.spec_from_file_location(name,F1/(name+'.py'))
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        monkeypatch.setitem(sys.modules,name,module)
    path=ROOT/'research/prime_field_symmetries_20261029/operator_family.py'
    spec=importlib.util.spec_from_file_location('software_operator_family',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('name,slots',[('distinct',(0,1,2)),('twoequal',(0,0,1)),('allequal',(0,0,0))])
def test_every_software_target_matches_frozen_operator(family,name,slots):
    from flint import fmpz_mod_ctx
    parameters=dict(p=19,a=2,b=3)
    cached=family.OperatorFamily(parameters,2,0,name)
    assert cached.degree==4
    assert len(cached.operators)==5 and cached.setup_counters['operators_constructed']==5
    scalar=family.exterior.scalar_columns(2,0,19)
    for target_x in range(19):
        polynomial,_=family.core.relation_polynomial(parameters,target_x,slots)
        expected,basis=family.exterior.tensor_operator(polynomial,max(slots)+1,name=='distinct',
                                                       scalar,fmpz_mod_ctx(19),19,Counter())
        assert cached.basis==basis
        assert cached.evaluate(target_x)==expected
    assert cached.evaluate(3)==cached.evaluate(3+19)


def test_family_guard_precedes_allocation_and_coefficients_are_restricted(family,monkeypatch):
    monkeypatch.setattr(family.exterior,'tensor_operator',lambda *a:pytest.fail('allocated after guard'))
    with pytest.raises(family.core.ExtractionUnknown,match='dimension'):
        family.OperatorFamily(dict(p=19,a=2,b=3),5,0,'distinct')
    for expression in ["__import__('os')",'t/2','t**-1','z+1']:
        with pytest.raises(ValueError):
            family.target_degree(expression)
