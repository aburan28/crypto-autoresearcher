"""Certificate corruptions must fail without a scalar search or collector."""
import pytest
from certify_bases import check_weights
from certify_targets import isolated_certificate
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations


def test_exact_unit_certificate_and_corruptions():
    matrix=[[1,2],[0,1]];rhs=[3,4]
    check_weights(matrix,rhs,[1,0],2,[1,5],7)
    for unit,value,weights in [([0,1],2,[1,5]),([1,0],3,[1,5]),([1,0],2,[1]),([1,0],2,[1,4])]:
        with pytest.raises(ValueError):check_weights(matrix,rhs,unit,value,weights,7)


def test_isolated_target_certificate_retains_free_base_column():
    base=AffineRelations(7,2);base.add([1,0],3)
    certificate=isolated_certificate(base,[2,0],1,2,7)
    assert certificate['scalar']==6 and certificate['augmented_rank']==2
    assert certificate['remaining_base_nullity']==1
    assert isolated_certificate(base,[2,1],1,2,7) is None
