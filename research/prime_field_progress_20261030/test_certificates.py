"""Certificate corruptions must fail without a scalar search or collector."""
import pytest
from certify_bases import check_weights


def test_exact_unit_certificate_and_corruptions():
    matrix=[[1,2],[0,1]];rhs=[3,4]
    check_weights(matrix,rhs,[1,0],2,[1,5],7)
    for unit,value,weights in [([0,1],2,[1,5]),([1,0],3,[1,5]),([1,0],2,[1]),([1,0],2,[1,4])]:
        with pytest.raises(ValueError):check_weights(matrix,rhs,unit,value,weights,7)
