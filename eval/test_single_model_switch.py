import requests
import json

base = "http://127.0.0.1:8000"

print("--- Testing Model Switch to qwen3:14b ---")
r = requests.post(f"{base}/api/model/load", json={"model": "qwen3:14b"}, timeout=120)
print("Load response:", r.json())

# Check Ollama PS via backend
st = requests.get(f"{base}/api/system_status", timeout=5).json()
print("Active Model in system status:", st.get("active_model"))
print("GPU VRAM used (GB):", st.get("gpu", {}).get("used_vram_gb"))

# Check direct Ollama api/ps to verify ONLY 1 model exists
ps = requests.get("http://127.0.0.1:11434/api/ps").json()
loaded_models = ps.get("models", [])
print(f"Total models loaded in Ollama VRAM: {len(loaded_models)}")
for m in loaded_models:
    print(f" -> {m.get('name')} (VRAM: {m.get('size_vram') / (1024**3):.2f} GB)")

assert len(loaded_models) == 1, f"Expected 1 model, got {len(loaded_models)}"
print("CONFIRMED: Exactly ONE model active in GPU VRAM!")
