# Deploying Kimi-K3 on AWS across multiple nodes

Reference architecture and runnable manifests for serving
[`moonshotai/Kimi-K3`](https://huggingface.co/moonshotai/Kimi-K3) (2.8T-parameter MoE,
1M context) on multi-node AWS GPU clusters.

> **Status / verification boundary.** Kimi-K3 open weights landed 2026-07-27 and
> engine support is very fresh: vLLM published a *preview* of production-scale K3
> support on 2026-07-22, and as of this writing there is **no** `Kimi-K3.md` in
> `vllm-project/recipes` (404). Everything in this directory that is derived from
> published Moonshot/vLLM/AWS facts is cited in [Sources](#sources). Everything that
> is a **template you must confirm against the shipped `config.json` and the engine
> recipe** is marked `CONFIRM:`. No launch flag here is presented as verified K3
> syntax unless it is cited. Do not paste these into production without step 0.

---

## 0. What the model forces on your topology

| Property | Value | Consequence for deployment |
|---|---|---|
| Total parameters | 2.8 T | ~1.5 TB of weights — no single AWS node holds it |
| Active parameters / token | 104 B | Compute per token is mid-size; **memory and all-to-all dominate** |
| Experts | 16 active of 896 | Expert parallelism is the primary sharding axis |
| Layers | 93 = **69 KDA** + **24 Gated MLA** | Only 24 layers grow KV with sequence length |
| Weights / activations | MXFP4 / MXFP8 | **Blackwell strongly preferred** (native FP4/FP8 tensor cores) |
| Context | 1 M tokens | Prefill will head-of-line block decode → PD disaggregation |

Three consequences drive every decision below.

**(a) ~1.5 TB of weights.** MXFP4 is 4-bit elements plus a shared 8-bit scale per
32-element block = 4.25 bits/parameter effective, so
`2.8e12 x 4.25 / 8 = 1.49e12 bytes ~= 1.5 TB`, before the non-expert tensors
(attention, embeddings, norms, router) that are typically held at higher precision.
Budget **1.5-1.6 TB aggregate HBM for weights alone**, then add KV cache,
activations, CUDA graphs, and NCCL/all-to-all buffers on top.

**(b) The hybrid attention stack is a gift.** 69 of 93 layers are KDA (linear
attention) and hold a *fixed-size recurrent state per sequence*, independent of
sequence length. Only the 24 Gated MLA layers hold a KV cache that grows with
tokens — and MLA caches a compressed latent, not full K/V. This is why a 1M context
is tractable at all. A naive "93 layers of MHA" estimate overstates KV memory by
roughly an order of magnitude. Compute the real number with
[`sizing.py`](#3-size-it-before-you-spend) once you have `config.json`.

**(c) 896 = 2^7 x 7.** Expert-parallel world sizes that divide the expert count
evenly are **8, 14, 16, 28, 32, 56, 64, 112, 128**. Note that **72 does not divide
896** — on a GB200 NVL72 UltraServer, run the serving group at **EP=64** (14 experts
per GPU) and use the remaining 8 GPUs for prefill or spare capacity. The alternative,
EP=72, is ragged: `896 = 72 x 12 + 32`, so 32 GPUs hold 13 experts and 40 hold 12,
and every all-to-all in every layer waits on the 32 stragglers.

---

## 1. Pick the instance shape

| Instance | GPUs / node | HBM / node | Interconnect | Native MXFP4 |
|---|---|---|---|---|
| `p5.48xlarge` | 8 x H100 80 GB | 640 GB | 3.2 Tbps EFAv2 | No |
| `p5e.48xlarge` | 8 x H200 141 GB | 1128 GB | 3.2 Tbps EFAv2 | No |
| `p5en.48xlarge` | 8 x H200 141 GB | 1128 GB | 3.2 Tbps EFAv3 | No |
| `p6-b200.48xlarge` | 8 x B200 180 GB | 1440 GB | 3.2 Tbps EFAv4 | **Yes** |
| `p6e-gb200.36xlarge` | 4 x GB200 Blackwell | ~744 GB | NVLink domain member | **Yes** |
| `u-p6e-gb200x72` UltraServer | **72** in one NVLink domain | **13.4 TB** | 28.8 Tbps EFAv4 | **Yes** |

### Recommendation

**First choice — one `u-p6e-gb200x72` UltraServer.** The entire model fits inside a
single 72-GPU NVLink domain with 13.4 TB of HBM3e. This matters far more for K3 than
raw FLOPs: a 896-expert MoE at EP scale is dominated by expert all-to-all traffic,
and inside an NVLink domain that traffic **never touches EFA**. Weights occupy ~11%
of HBM, leaving an enormous KV budget for 1M-context serving. Moonshot's own guidance
is a supernode of 64+ accelerators, which is exactly this shape.

**Second choice — 4 to 8 x `p6-b200.48xlarge`.** 8 nodes gives 64 GPUs (clean EP=64,
14 experts/GPU) and 11.5 TB HBM; 4 nodes gives 32 GPUs (clean EP=32, 28 experts/GPU,
~47 GB of weights per 180 GB card) which is a viable production config with ~130 GB
per GPU left for KV and activations. Here the expert all-to-all *does* cross EFA
between nodes, so EFA tuning (§5) is load-bearing rather than optional.

**Hopper (`p5`/`p5e`/`p5en`) — possible, but read this first.** H100/H200 have no
native FP4 tensor cores and no native MXFP8 path. The MXFP4 weights must be
dequantized (on the fly per block, to keep memory at ~4 bits) and computed in
BF16/FP8, so you pay a real throughput penalty and depend on the engine shipping a
Hopper-compatible dequant kernel for K3's SiTU-enabled MXFP4 MoE path. `CONFIRM:`
whether your engine build supports K3 on `sm90` at all before committing to a Hopper
fleet. If it does, budget 8 x `p5en.48xlarge` (64 GPUs, 9 TB) — 2 nodes is
arithmetically sufficient for weights but leaves no usable KV headroom.

---

## 2. Pick the parallelism strategy

For a sparse MoE with only 104B active parameters, **do not tensor-parallel the whole
model**. vLLM's guidance for large MoE is data-parallel attention combined with
expert parallelism ("DEP"), one `vllm serve` process per GPU:

```
--data-parallel-size   <total GPUs>
--tensor-parallel-size 1
--enable-expert-parallel
```

Why not TP: with 16 experts active per token, TP shards each expert's small GEMM
across GPUs and turns an already-narrow matmul into a latency-bound all-reduce.
DP-attention + EP keeps each expert whole on one GPU and moves *tokens* instead of
*activations*, which is the cheaper direction of travel at this sparsity.

Why not pipeline parallel: 93 layers do divide cleanly, but PP introduces bubbles
that hurt inter-token latency, and with EP you do not need PP to fit. Reach for PP
only if you are stuck on a small number of memory-poor nodes.

**Prefill/decode disaggregation is not optional at 1M context.** A single 1M-token
prefill is enormously compute-heavy and will stall every in-flight decode behind it.
Run two separate DP groups with distinct RPC ports and move KV between them with a KV
connector (Mooncake/NIXL over EFA). vLLM and Moonshot collaborated specifically on
Mooncake-based PD disaggregation for K3's hybrid attention. Note that prefill and
decode are **separate DP groups** — they need different `--data-parallel-rpc-port`
values or the coordinators collide.

See [`eks/lws-kimi-k3-ep64.yaml`](eks/lws-kimi-k3-ep64.yaml) for the aggregated
config and [`eks/lws-kimi-k3-pd-disagg.yaml`](eks/lws-kimi-k3-pd-disagg.yaml) for the
disaggregated one.

---

## 3. Size it before you spend

`sizing.py` computes aggregate HBM from real config values. It deliberately **refuses
to guess** dimensions it cannot read — pass `--assume` only for planning, and it will
label every derived number as an assumption.

```bash
# After the weights are staged:
python3 deploy/kimi-k3-aws/sizing.py \
    --config /fsx/models/Kimi-K3/config.json \
    --gpus 64 --gpu-hbm-gb 180 \
    --max-model-len 1000000 --max-seqs 32
```

It reports weight bytes at MXFP4, per-GPU expert shard size, MLA KV bytes per token
(24 layers only), KDA recurrent state per sequence (69 layers, length-independent),
and whether the configuration fits with headroom.

---

## 4. Stage 1.5 TB of weights without melting your cold start

Weight loading, not inference, is what makes the first deploy painful. 1.5 TB pulled
from Hugging Face once, then fanned out to N nodes, is the difference between a
20-minute and a 4-hour bring-up.

Use [`scripts/stage-weights.sh`](scripts/stage-weights.sh):

1. Download once to a staging host with `hf_transfer` enabled (parallel range GETs).
2. Push to S3 with `s5cmd` (concurrent multipart).
3. Expose to the cluster via **FSx for Lustre** with an S3 data repository
   association, so every node reads the same copy instead of holding 1.5 TB each.
4. Enable **GPUDirect Storage** on FSx for Lustre to load tensors straight into HBM,
   bypassing a bounce through host memory.

Node-local NVMe (`hostPath: /mnt/k8s-disks/0`, the pattern in `aws-samples`) is fine
for a pinned single-shape deployment, but it means 1.5 TB per node and a full re-pull
on every scale-out. FSx is the better default at this size.

With expert parallelism each GPU ultimately holds only its expert shard, but the
engine still reads the full safetensors set on each node during load — plan the
shared filesystem for **full-model read bandwidth x node count**, not shard size.

---

## 5. Networking: EFA is the whole ballgame

Between nodes, MoE all-to-all is the bottleneck. Non-negotiables:

- All nodes in a **single AZ** and a **cluster placement group**.
- EFA enabled on every interface (`p6-b200.48xlarge` exposes multiple EFA devices per
  node); on EKS install the `aws-efa-k8s-device-plugin`.
- Build the container with the **`aws-ofi-nccl`** plugin so NCCL uses EFA's libfabric
  provider rather than falling back to TCP. A silent TCP fallback looks like
  "inference is mysteriously 10x slow".
- Verify with `nccl-tests` **before** loading the model — see
  [`scripts/verify-efa.sh`](scripts/verify-efa.sh). If `all_to_all` bus bandwidth is
  not in the expected range for your instance, stop and fix it; every subsequent
  measurement is meaningless until it is.

Environment settings live in [`scripts/nccl-efa-env.sh`](scripts/nccl-efa-env.sh).

---

## 6. Orchestration: pick one

| Option | Use when | Reference |
|---|---|---|
| **EKS + LeaderWorkerSet** | Default. Kubernetes-native gang scheduling of a multi-node replica; scales the *group*, not the pod | `aws-samples/sample-llm-inference-on-eks` |
| **SageMaker HyperPod** | You want managed node auto-recovery, task governance, and P6e-GB200 UltraServer support; especially if you also fine-tune | AWS HyperPod UltraServer support |
| **AWS PCS / ParallelCluster** | Slurm shop, batch or offline inference; supports P6e-GB200/GB300 UltraServers | AWS PCS UltraServer support |
| **Plain EC2 + Ray** | Prototyping only. Simplest, least resilient — one node loss kills the deployment with no rescheduling | vLLM Ray multi-node docs |

LeaderWorkerSet is the right default: it models "one logical model replica spanning
N nodes" directly, restarts the whole group on a member failure (which is what you
want — a partial EP group is useless), and avoids standing up Ray as a second control
plane. Manifests in [`eks/`](eks/).

---

## 7. Runbook

```bash
# 1. Cluster with EFA-enabled Blackwell nodes
eksctl create cluster -f deploy/kimi-k3-aws/eks/cluster.yaml

# 2. Prerequisites: NVIDIA + EFA device plugins, LWS controller, FSx CSI, ConfigMap
./deploy/kimi-k3-aws/scripts/install-prereqs.sh

# 3. Stage weights to S3 + FSx (run once, off-cluster)
./deploy/kimi-k3-aws/scripts/stage-weights.sh s3://my-bucket/models/Kimi-K3

# 4. PROVE the fabric works before spending an hour loading 1.5 TB
kubectl apply -f deploy/kimi-k3-aws/eks/nccl-test.yaml
kubectl logs -f job/nccl-alltoall-test

# 5. Size the deployment against the real config.json
python3 deploy/kimi-k3-aws/sizing.py --config /fsx/models/Kimi-K3/config.json \
    --gpus 64 --gpu-hbm-gb 180 --max-model-len 1000000 --max-seqs 32

# 6. Deploy
kubectl apply -f deploy/kimi-k3-aws/eks/lws-kimi-k3-ep64.yaml
kubectl get pods -l app=kimi-k3 -w

# 7. Smoke test + benchmark
./deploy/kimi-k3-aws/scripts/smoke-test.sh
```

---

## 8. Cost reality check

A 64-GPU Blackwell deployment is on the order of **tens of dollars per hour per
node**, so 8 x `p6-b200.48xlarge` is a four-to-five-figure daily bill at on-demand
rates. Before committing:

- Price the Moonshot-hosted API at `platform.kimi.ai` against your actual token
  volume. Self-hosting K3 wins on data sovereignty, sustained high utilization, and
  latency control — not on casual usage.
- Capacity Blocks or reservations, not on-demand, for anything sustained.
- Scale-to-zero is impractical: a 1.5 TB cold start is minutes at best. Budget for a
  warm floor.

---

## 9. Open items to close when the ecosystem catches up

- [ ] `CONFIRM:` exact `config.json` field names for KDA state dims and MLA
      `kv_lora_rank` / `qk_rope_head_dim`; update `sizing.py` defaults.
- [ ] `CONFIRM:` the official `vllm-project/recipes/moonshotai/Kimi-K3.md` flags when
      published; reconcile against `eks/*.yaml`.
- [ ] `CONFIRM:` minimum vLLM version with FlashKDA + fused AttnRes + SiTU MXFP4 MoE.
- [ ] `CONFIRM:` SGLang and TokenSpeed equivalents; Moonshot lists all three.
- [ ] `CONFIRM:` whether `sm90` (Hopper) is supported at all for the MXFP4 path.
- [ ] Measure real all-to-all cost at EP=32 vs EP=64 on your fabric and pick the
      smaller world size if it is within latency SLO — fewer GPUs, less all-to-all.

---

## Sources

- [MoonshotAI/Kimi-K3 (GitHub)](https://github.com/MoonshotAI/Kimi-K3) — 2.8T total /
  104B active, 16 of 896 experts, 93 layers (69 KDA + 24 Gated MLA), MXFP4 weights +
  MXFP8 activations, 1M context, recommended engines vLLM / SGLang / TokenSpeed
- [moonshotai/Kimi-K3 (Hugging Face)](https://huggingface.co/moonshotai/Kimi-K3) — model card and weights
- [A Preview of Production-Scale Kimi K3 Support on vLLM](https://vllm.ai/blog/2026-07-22-kimi-k3-preview) —
  FlashKDA, fused KDA decode/projections, fused AttnRes, reimplemented MLA, SiTU MXFP4
  MoE path, Mooncake PD disaggregation
- [vLLM recipe: moonshotai/Kimi-K2.5](https://github.com/vllm-project/recipes/blob/main/moonshotai/Kimi-K2.5.md) —
  DEP-PD flag syntax (`--data-parallel-size`, `--enable-expert-parallel`,
  `--data-parallel-address`, `--data-parallel-rpc-port`), separate prefill/decode DP groups
- [vLLM: Parallelism and Scaling](https://docs.vllm.ai/en/stable/serving/parallelism_scaling/)
- [Amazon EC2 P6e and P6 instances](https://aws.amazon.com/ec2/instance-types/p6/) —
  P6e-GB200 UltraServers (72 GPUs, 13.4 TB HBM3e, 28.8 Tbps EFAv4), P6-B200 (8 GPUs, 1440 GB)
- [New Amazon EC2 P6e-GB200 UltraServers](https://aws.amazon.com/blogs/aws/new-amazon-ec2-p6e-gb200-ultraservers-powered-by-nvidia-grace-blackwell-gpus-for-the-highest-ai-performance)
- [SageMaker HyperPod support for P6e-GB200 UltraServers](https://aws.amazon.com/blogs/machine-learning/train-and-deploy-ai-models-at-trillion-parameter-scale-with-amazon-sagemaker-hyperpod-support-for-p6e-gb200-ultraservers/)
- [AWS PCS supports P6e-GB200 and P6e-GB300 UltraServers](https://aws.amazon.com/about-aws/whats-new/2026/06/aws-parallel-computing-service/)
- [aws-samples/sample-llm-inference-on-eks](https://github.com/aws-samples/sample-llm-inference-on-eks) —
  LeaderWorkerSet multi-node, NCCL over EFA RDMA, PD disaggregation manifests
- [Multi-Node Inference with vLLM — EKS Blueprints](https://aws-ia.github.io/terraform-aws-eks-blueprints/patterns/machine-learning/multi-node-vllm/)
- [Accelerate LLM model loading with GPUDirect on FSx for Lustre](https://aws.amazon.com/blogs/machine-learning/accelerate-llm-model-loading-and-increase-context-windows-with-gpudirect-on-amazon-fsx-for-lustre-and-turboquant/)
- [Amazon EC2 P5en instances (EFAv3)](https://aws.amazon.com/blogs/aws/new-amazon-ec2-p5en-instances-with-nvidia-h200-tensor-core-gpus-and-efav3-networking)
