# CUDA kernels for crypto_autoresearcher.gf2

| file | role |
| --- | --- |
| `tail_update.cu` | Trailing update (`tail_chunk`) — Gray-table and direct forms |
| `__init__.py` | CuPy/NVRTC loader + numpy CPU reference for differential tests |

No GPU is required to import the package: `available()` reports why, and the
CPU OpenMP column pass is unchanged. Install `.[gf2-gpu]` and run on a CUDA
host (or via `tools/gf2_runpod.py`) to exercise the device path.
