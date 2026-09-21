import subprocess
import sys
import shutil

def convert():
    free_gb = shutil.disk_usage(".").free / (1024**3)
    if free_gb < 60:
        print(f"Need ~60GB free, have {free_gb:.1f}GB")
        return False
    
    cmd = [
        "mlx_lm.convert",
        "--hf-path", "Qwen/Qwen3-27B",
        "--mlx-path", "qwen3-27b-4bit",
        "-q", "--q-bits", "4"
    ]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0

if __name__ == "__main__":
    convert()