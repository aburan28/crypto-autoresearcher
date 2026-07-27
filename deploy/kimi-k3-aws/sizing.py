#!/usr/bin/env python3
"""HBM sizing for multi-node Kimi-K3 serving on AWS.

Computes aggregate and per-GPU memory for a data-parallel-attention +
expert-parallel deployment, accounting for K3's hybrid attention stack: only the
Gated MLA layers hold a KV cache that grows with sequence length, while the KDA
layers hold a fixed-size recurrent state per sequence.

Design rule: this script does not invent model dimensions. Values it cannot read
from config.json are reported as missing unless --assume is passed, and every
assumed value is labelled in the output. Numbers derived from assumptions are not
a substitute for measuring against the real weights.

Usage:
    python3 sizing.py --config /fsx/models/Kimi-K3/config.json \
        --gpus 64 --gpu-hbm-gb 180 --max-model-len 1000000 --max-seqs 32
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field

GB = 1024**3
TB = 1024**4

# Published Kimi-K3 facts (github.com/MoonshotAI/Kimi-K3). Used only with --assume
# for the fields that are architectural constants rather than tensor dimensions.
PUBLISHED = {
    "total_params": 2.8e12,
    "active_params": 104e9,
    "num_experts": 896,
    "num_experts_per_tok": 16,
    "num_layers": 93,
    "num_kda_layers": 69,
    "num_mla_layers": 24,
}

# Placeholder tensor dimensions. NOT published as of 2026-07-27 -- these are
# order-of-magnitude anchors borrowed from comparable MLA / gated-linear-attention
# models so that planning can proceed. Replace from the shipped config.json.
PLACEHOLDER = {
    "kv_lora_rank": 512,          # DeepSeek-style MLA compressed latent dim
    "qk_rope_head_dim": 64,       # decoupled RoPE dim carried alongside the latent
    "kda_num_heads": 64,          # KDA heads per layer
    "kda_head_k_dim": 128,        # recurrent state is [heads, k_dim, v_dim]
    "kda_head_v_dim": 128,
}

# Candidate config.json key names, in priority order. Kimi-K3 introduces new
# architecture components (KDA, AttnRes, Stable LatentMoE) whose config field names
# are not yet documented publicly, so we probe several conventions.
KEY_ALIASES = {
    "num_layers": ["num_hidden_layers", "n_layers", "num_layers"],
    "num_experts": ["n_routed_experts", "num_experts", "moe_num_experts"],
    "num_experts_per_tok": ["num_experts_per_tok", "moe_top_k", "top_k"],
    "kv_lora_rank": ["kv_lora_rank"],
    "qk_rope_head_dim": ["qk_rope_head_dim", "rope_head_dim"],
    "kda_num_heads": ["kda_num_heads", "linear_num_heads", "num_attention_heads"],
    "kda_head_k_dim": ["kda_head_k_dim", "linear_key_head_dim", "head_dim"],
    "kda_head_v_dim": ["kda_head_v_dim", "linear_value_head_dim", "head_dim"],
    "num_kda_layers": ["num_kda_layers", "num_linear_layers"],
    "num_mla_layers": ["num_mla_layers", "num_full_attention_layers"],
}


@dataclass
class Resolved:
    """A model dimension plus where it came from."""

    values: dict = field(default_factory=dict)
    sources: dict = field(default_factory=dict)
    missing: list = field(default_factory=list)

    def get(self, name: str) -> float | None:
        return self.values.get(name)

    def note(self, name: str) -> str:
        src = self.sources.get(name, "missing")
        return "" if src == "config.json" else f"  [{src}]"


def resolve(cfg: dict, assume: bool) -> Resolved:
    r = Resolved()
    for name, aliases in KEY_ALIASES.items():
        for key in aliases:
            if key in cfg:
                r.values[name] = cfg[key]
                r.sources[name] = "config.json"
                break
        else:
            if assume and name in PUBLISHED:
                r.values[name] = PUBLISHED[name]
                r.sources[name] = "published"
            elif assume and name in PLACEHOLDER:
                r.values[name] = PLACEHOLDER[name]
                r.sources[name] = "PLACEHOLDER -- verify"
            else:
                r.missing.append(name)

    # Layer split: derive whichever half is absent if the total and one half exist.
    n, kda, mla = (r.get("num_layers"), r.get("num_kda_layers"), r.get("num_mla_layers"))
    if n and kda and not mla:
        r.values["num_mla_layers"], r.sources["num_mla_layers"] = n - kda, "derived"
    elif n and mla and not kda:
        r.values["num_kda_layers"], r.sources["num_kda_layers"] = n - mla, "derived"

    # Total parameter count is rarely in config.json; fall back to the published figure.
    if "total_params" not in r.values:
        if assume:
            r.values["total_params"] = PUBLISHED["total_params"]
            r.sources["total_params"] = "published"
        else:
            r.missing.append("total_params")

    r.missing = [m for m in r.missing if m not in r.values]
    return r


def mxfp4_bits_per_param(block: int = 32) -> float:
    """MXFP4: 4-bit element + one shared 8-bit scale per block of `block` elements."""
    return 4.0 + 8.0 / block


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", help="path to the model's config.json")
    p.add_argument("--assume", action="store_true",
                   help="fill unreadable fields from published facts and PLACEHOLDER dims")
    p.add_argument("--gpus", type=int, required=True, help="total GPUs in the serving group")
    p.add_argument("--gpu-hbm-gb", type=float, required=True, help="HBM per GPU in GB")
    p.add_argument("--max-model-len", type=int, default=1_000_000)
    p.add_argument("--max-seqs", type=int, default=32, help="concurrent sequences at max length")
    p.add_argument("--kv-dtype-bytes", type=float, default=1.0,
                   help="bytes per KV element (1.0 = FP8 cache, 2.0 = BF16)")
    p.add_argument("--overhead-frac", type=float, default=0.15,
                   help="fraction of HBM reserved for activations, CUDA graphs, NCCL buffers")
    p.add_argument("--mxfp4-block", type=int, default=32)
    args = p.parse_args()

    cfg = {}
    if args.config:
        try:
            with open(args.config) as fh:
                cfg = json.load(fh)
        except OSError as exc:
            print(f"warning: could not read {args.config}: {exc}\n", file=sys.stderr)

    r = resolve(cfg, args.assume)
    if r.missing:
        print("Cannot size: these values were not found in config.json:", file=sys.stderr)
        for m in sorted(set(r.missing)):
            print(f"  - {m}  (tried: {', '.join(KEY_ALIASES.get(m, ['n/a']))})", file=sys.stderr)
        print("\nRe-run with --assume to use published/placeholder values for planning.",
              file=sys.stderr)
        return 1

    assumed = {k: v for k, v in r.sources.items() if v != "config.json"}

    # --- Weights -----------------------------------------------------------
    bits = mxfp4_bits_per_param(args.mxfp4_block)
    total_params = r.get("total_params")
    weight_bytes = total_params * bits / 8.0

    # Under EP the routed-expert weights shard across GPUs; the dense remainder
    # (attention, embeddings, norms, router) is replicated per DP rank. Active-param
    # count gives a usable split: experts dominate the total, dense dominates active.
    dense_params = PUBLISHED["active_params"] - (
        (total_params / r.get("num_experts")) * r.get("num_experts_per_tok")
    )
    dense_params = max(dense_params, 0.0)
    expert_params = total_params - dense_params
    per_gpu_expert_bytes = (expert_params * bits / 8.0) / args.gpus
    per_gpu_dense_bytes = dense_params * bits / 8.0  # replicated
    per_gpu_weight_bytes = per_gpu_expert_bytes + per_gpu_dense_bytes

    # --- KV cache: only the MLA layers grow with sequence length -----------
    mla_layers = r.get("num_mla_layers")
    kda_layers = r.get("num_kda_layers")
    kv_per_token = mla_layers * (r.get("kv_lora_rank") + r.get("qk_rope_head_dim")) * args.kv_dtype_bytes
    kv_total = kv_per_token * args.max_model_len * args.max_seqs

    # KDA recurrent state: fixed per sequence, independent of sequence length.
    kda_state_per_seq = (
        kda_layers * r.get("kda_num_heads") * r.get("kda_head_k_dim")
        * r.get("kda_head_v_dim") * args.kv_dtype_bytes
    )
    kda_total = kda_state_per_seq * args.max_seqs

    # --- Budget ------------------------------------------------------------
    hbm_total = args.gpus * args.gpu_hbm_gb * GB
    overhead = hbm_total * args.overhead_frac
    used = weight_bytes + kv_total + kda_total + overhead
    free = hbm_total - used

    ep_ok = r.get("num_experts") % args.gpus == 0

    print("=" * 70)
    print("Kimi-K3 multi-node sizing")
    print("=" * 70)
    if assumed:
        print("\n!! NOT fully derived from config.json. Assumed values:")
        for k, v in sorted(assumed.items()):
            print(f"     {k:24s} = {r.get(k):<12} [{v}]")
        print("   Treat the totals below as planning estimates, not measurements.")

    print(f"\nTopology: {args.gpus} GPUs x {args.gpu_hbm_gb:.0f} GB = {hbm_total/TB:.2f} TB HBM")
    print(f"Layers:   {kda_layers:.0f} KDA (length-independent state)"
          f" + {mla_layers:.0f} MLA (growing KV){r.note('num_kda_layers')}")
    print(f"Experts:  {r.get('num_experts'):.0f} total, {r.get('num_experts_per_tok'):.0f} active/token")

    if ep_ok:
        print(f"          EP={args.gpus} divides evenly -> "
              f"{r.get('num_experts')/args.gpus:.0f} experts/GPU")
    else:
        rem = r.get("num_experts") % args.gpus
        print(f"          !! EP={args.gpus} does NOT divide {r.get('num_experts'):.0f} "
              f"(remainder {rem:.0f}).")
        print(f"             {rem:.0f} GPUs carry an extra expert and will straggle every "
              f"all-to-all.")
        print(f"             Prefer a world size dividing {r.get('num_experts'):.0f}: "
              f"{', '.join(str(d) for d in divisors(int(r.get('num_experts'))) if 8 <= d <= 256)}")

    print(f"\n{'Weights (MXFP4, %.2f bits/param)' % bits:<44s} {weight_bytes/TB:>8.2f} TB")
    print(f"{'  per GPU: expert shard':<44s} {per_gpu_expert_bytes/GB:>8.1f} GB")
    print(f"{'  per GPU: replicated dense':<44s} {per_gpu_dense_bytes/GB:>8.1f} GB")
    print(f"{'  per GPU: total':<44s} {per_gpu_weight_bytes/GB:>8.1f} GB")
    print(f"\n{'MLA KV per token (24 layers only)':<44s} {kv_per_token:>8.0f} B")
    print(f"{'MLA KV @ %d seqs x %d tokens' % (args.max_seqs, args.max_model_len):<44s} "
          f"{kv_total/TB:>8.2f} TB")
    print(f"{'KDA state per sequence':<44s} {kda_state_per_seq/GB:>8.2f} GB")
    print(f"{'KDA state @ %d seqs' % args.max_seqs:<44s} {kda_total/GB:>8.1f} GB")
    print(f"{'Runtime overhead (%.0f%%)' % (args.overhead_frac*100):<44s} {overhead/TB:>8.2f} TB")
    print("-" * 70)
    print(f"{'TOTAL':<44s} {used/TB:>8.2f} TB")
    print(f"{'AVAILABLE':<44s} {hbm_total/TB:>8.2f} TB")
    print(f"{'HEADROOM':<44s} {free/TB:>8.2f} TB")

    if free < 0:
        need = -free / (args.gpu_hbm_gb * GB)
        print(f"\nDOES NOT FIT. Add ~{need:.0f} more GPUs, reduce --max-seqs, "
              f"or reduce --max-model-len.")
        return 2
    if free / hbm_total < 0.10:
        print("\nFits, but under 10% headroom -- expect OOM under fragmentation. "
              "Add a node.")
    else:
        print(f"\nFits with {100*free/hbm_total:.0f}% headroom.")
    return 0


def divisors(n: int) -> list[int]:
    out = set()
    i = 1
    while i * i <= n:
        if n % i == 0:
            out.add(i)
            out.add(n // i)
        i += 1
    return sorted(out)


if __name__ == "__main__":
    sys.exit(main())
