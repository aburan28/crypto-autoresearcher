"""Dataset split construction and disjointness verification.

Two split modes, both operating on the SET of logarithms k in [0, N):
  - random_by_logarithm: k's shuffled (seeded) then cut into train / early-stop / heldout.
  - contiguous_block_by_logarithm: k's cut into contiguous integer-value blocks.

Splits are constructed once per (curve, split_mode) and are independent of
architecture, capacity, presentation and training seed -- required so that
the held-out set is identical across every matched cell within that
(curve, split_mode) pair.
"""
import json
import random

TRAIN_FRAC = 0.6
EARLYSTOP_FRAC = 0.1
HELDOUT_FRAC = 0.3
SPLIT_SEED = 777  # fixed, independent of training seeds; documented, not secret

def make_split(N, split_mode):
    n_train = int(N * TRAIN_FRAC)
    n_es = int(N * EARLYSTOP_FRAC)
    if split_mode == "random_by_logarithm":
        ks = list(range(N))
        rng = random.Random(SPLIT_SEED)
        rng.shuffle(ks)
        train = sorted(ks[:n_train])
        es = sorted(ks[n_train:n_train + n_es])
        ho = sorted(ks[n_train + n_es:])
    elif split_mode == "contiguous_block_by_logarithm":
        ks = list(range(N))
        train = ks[:n_train]
        es = ks[n_train:n_train + n_es]
        ho = ks[n_train + n_es:]
    else:
        raise ValueError(split_mode)
    return train, es, ho

def verify_disjoint(train, es, ho, N):
    st, ses, sho = set(train), set(es), set(ho)
    assert len(st) == len(train) and len(ses) == len(es) and len(sho) == len(ho), "duplicates within a split"
    assert st.isdisjoint(ses), "train/earlystop overlap"
    assert st.isdisjoint(sho), "train/heldout overlap"
    assert ses.isdisjoint(sho), "earlystop/heldout overlap"
    assert st | ses | sho == set(range(N)), "splits do not cover [0,N)"
    return True

def split_manifest(curve_name, N, split_mode):
    train, es, ho = make_split(N, split_mode)
    verify_disjoint(train, es, ho, N)
    return {
        "curve": curve_name, "N": N, "split_mode": split_mode,
        "split_seed": SPLIT_SEED,
        "n_train": len(train), "n_earlystop": len(es), "n_heldout": len(ho),
        "disjoint_verified": True,
        "train_ids": train, "earlystop_ids": es, "heldout_ids": ho,
    }
