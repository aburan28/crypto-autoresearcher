"""Single matched training run for EXP-REPL-1d1287 (pilot scale).

Emits a JSON result to stdout (captured by the orchestrator into
raw-result.json) with: heldout advantage + CI, training-set accuracy,
early-stop-slice disjointness confirmation, parameter count / S in bits
(raw and gzip-compressed), timing, and per-example heldout predictions
(as compact int arrays, sufficient for independent recomputation).
"""
import argparse, gzip, io, json, random, sys, time
import numpy as np
import torch
import torch.nn as nn

from ec import load_curves
from splits import make_split, verify_disjoint, SPLIT_SEED
from models import build_model

DATA_KEY = {
    "affine_xy_limbs": "affine",
    "x_only_limbs": "x_only",
    "projective_jacobian_limbs": "projective",
    "scrambled_labels": "scrambled",
    "planted_leaky": "planted",
}

def get_arrays(curve_name, presentation, shuffle_labels, shuffle_seed):
    d = np.load(f"cache/{curve_name}.npz")
    key = DATA_KEY[presentation]
    X = d[key]
    y = d["msb"].copy()
    if shuffle_labels:
        rng = np.random.RandomState(shuffle_seed)
        perm = rng.permutation(len(y))
        y = y[perm]
    return X, y

def run(args):
    t0 = time.time()
    curves = load_curves()
    curve = curves[args.curve]
    train_ids, es_ids, ho_ids = make_split(curve.N, args.split_mode)
    verify_disjoint(train_ids, es_ids, ho_ids, curve.N)

    X, y = get_arrays(args.curve, args.presentation, args.shuffle_labels, args.seed)
    n_limbs = X.shape[1]

    train_ids_capped = train_ids
    if args.max_train is not None and len(train_ids) > args.max_train:
        rng = random.Random(SPLIT_SEED)
        train_ids_capped = sorted(rng.sample(train_ids, args.max_train))

    def to_tensors(ids):
        idx = np.array(ids, dtype=np.int64)
        return torch.from_numpy(X[idx]).long(), torch.from_numpy(y[idx]).float()

    Xtr, ytr = to_tensors(train_ids_capped)
    Xes, yes = to_tensors(es_ids)
    Xho, yho = to_tensors(ho_ids)

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)

    model, n_params, cap_cfg = build_model(args.architecture, args.capacity_id, n_limbs, args.seed)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.BCEWithLogitsLoss()

    best_es_loss = float("inf")
    best_state = None
    patience_left = args.patience
    bs = args.batch_size
    n = len(Xtr)

    epochs_run = 0
    for epoch in range(args.epochs):
        epochs_run = epoch + 1
        model.train()
        perm = torch.randperm(n)
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            xb, yb = Xtr[idx], ytr[idx]
            opt.zero_grad()
            out = model(xb)
            loss = lossf(out, yb)
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            es_out = model(Xes)
            es_loss = lossf(es_out, yes).item()
        if es_loss < best_es_loss - 1e-6:
            best_es_loss = es_loss
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            patience_left = args.patience
        else:
            patience_left -= 1
            if patience_left <= 0:
                break

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()

    def eval_acc(Xs, ys):
        with torch.no_grad():
            out = model(Xs)
            pred = (torch.sigmoid(out) >= 0.5).float()
            correct = (pred == ys).numpy().astype(int)
            acc = float(correct.mean())
        return acc, pred.numpy().astype(int).tolist()

    train_acc, _ = eval_acc(Xtr, ytr)
    ho_acc, ho_pred = eval_acc(Xho, yho)
    n_ho = len(yho)
    se_binom = float(np.sqrt(max(ho_acc * (1 - ho_acc), 1e-9) / n_ho))

    buf = io.BytesIO()
    torch.save(model.state_dict(), buf)
    raw_bytes = buf.getvalue()
    compressed_bytes = gzip.compress(raw_bytes, compresslevel=9)

    wall = time.time() - t0

    result = {
        "curve": args.curve, "N": curve.N, "split_mode": args.split_mode,
        "presentation": args.presentation, "shuffle_labels": args.shuffle_labels,
        "architecture": args.architecture, "capacity_id": args.capacity_id,
        "capacity_cfg": cap_cfg, "n_params": n_params,
        "S_bits_raw": n_params * 32,
        "S_bits_compressed": len(compressed_bytes) * 8,
        "seed": args.seed, "epochs_run": epochs_run, "epochs_cap": args.epochs,
        "n_train_used": len(train_ids_capped), "n_train_full": len(train_ids),
        "n_earlystop": len(es_ids), "n_heldout": n_ho,
        "train_accuracy": train_acc,
        "heldout_accuracy": ho_acc,
        "heldout_advantage": ho_acc - 0.5,
        "heldout_se_binomial": se_binom,
        "best_earlystop_loss": best_es_loss,
        "wall_clock_seconds": wall,
        "budget_limited": epochs_run >= args.epochs and patience_left > 0,
        "heldout_ids": ho_ids,
        "heldout_predictions": ho_pred,
        "split_disjoint_verified": True,
    }
    return result

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--curve", required=True)
    ap.add_argument("--split_mode", required=True)
    ap.add_argument("--presentation", required=True)
    ap.add_argument("--shuffle_labels", action="store_true")
    ap.add_argument("--architecture", required=True)
    ap.add_argument("--capacity_id", type=int, required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--patience", type=int, default=5)
    ap.add_argument("--batch_size", type=int, default=128)
    ap.add_argument("--max_train", type=int, default=None)
    args = ap.parse_args()
    print(json.dumps(run(args)))
