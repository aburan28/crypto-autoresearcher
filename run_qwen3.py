import os
import mlx.core as mx
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler

MODEL_PATH = "/Volumes/SSD990/qwen3-27b-mlx"
MEMORY_LIMIT_GB = 36
CPU_THREADS = 8
MAX_TOKENS = 512
TEMPERATURE = 0.7

def main():
    os.environ["MLX_CPU_THREADS"] = str(CPU_THREADS)
    mx.set_memory_limit(MEMORY_LIMIT_GB * 1024**3)
    
    print(f"Loading {MODEL_PATH}...")
    print(f"Memory limit: {MEMORY_LIMIT_GB}GB, CPU threads: {CPU_THREADS}")
    
    model, tokenizer = load(MODEL_PATH)
    print("Model loaded. Type 'quit' to exit.\n")
    
    sampler = make_sampler(temp=TEMPERATURE)
    
    while True:
        prompt = input(">>> ").strip()
        if prompt.lower() in ("quit", "exit", "q"):
            break
        if not prompt:
            continue
        
        print("Generating...")
        response = generate(
            model, tokenizer,
            prompt=prompt,
            max_tokens=MAX_TOKENS,
            sampler=sampler,
            verbose=False
        )
        print(f"\n{response}\n")

if __name__ == "__main__":
    main()