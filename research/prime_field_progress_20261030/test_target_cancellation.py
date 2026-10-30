"""A new outside variable alone must never count as base information."""
from copy import deepcopy
import pytest
from cancel_targets import dense_gain,verify_cancellation
from crypto_autoresearcher.index_calculus.relation_quality import AffineRelations,cancel_outside


def test_one_outside_column_and_corrupt_cancellation():
    base=AffineRelations(7,2);base.add([1,0],3)
    B=[[0,1],[0,0]];U=[[1],[1]];rhs=[2,5]
    oracle=dense_gain(base,B,U);assert oracle==dict(stacked_rank=3,outside_rank=1,base_rank=1,delta=1)
    result=cancel_outside(base,B,U,rhs);assert result['rank_gain']==oracle['delta']
    for certificate in result['cancellations']:
        verify_cancellation(B,U,rhs,certificate,7)
        bad=deepcopy(certificate);bad['partial_row_weights'][0]+=1
        with pytest.raises(ValueError):verify_cancellation(B,U,rhs,bad,7)
    assert dense_gain(base,B[:1],U[:1])['delta']==0
    assert cancel_outside(base,B[:1],U[:1],rhs[:1])['rank_gain']==0
