"""Independent integer descriptors and exact fair-coin run reference."""
import numpy as np


def scores_from_packed(packed):
    values=np.unpackbits(np.asarray(packed,dtype=np.uint8),axis=-1,bitorder='little')
    flat=values.reshape(-1,256).astype(np.int16);size=len(flat)
    longest=np.ones(size,dtype=np.int32);run=longest.copy()
    for i in range(1,256):
        run=np.where(flat[:,i]==flat[:,i-1],run+1,1);longest=np.maximum(longest,run)
    parity=np.abs(np.sum(2*((flat[:,:-2]^flat[:,1:-1]^flat[:,2:]))-1,axis=1))
    motifs=8*flat[:,:-3]+4*flat[:,1:-2]+2*flat[:,2:-1]+flat[:,3:]
    counts=np.zeros((size,16),dtype=np.int32)
    for j in range(16):counts[:,j]=np.sum(motifs==j,axis=1)
    numerator=16*np.sum(counts.astype(np.int64)**2,axis=1)-253**2
    result=np.column_stack((longest,parity,numerator)).astype(np.uint32)
    return result.reshape(*values.shape[:-1],3)


def fair_coin_run_probability(length,threshold):
    if threshold<=1:return 1.0
    counts=[0]*(threshold-1);counts[0]=2
    for _ in range(1,length):counts=[sum(counts)]+counts[:-1]
    return (2**length-sum(counts))/2**length


def unscale(metric_index,value):
    return float(value) if metric_index==0 else float(value)/(254 if metric_index==1 else 15*253)
