import requests
import json

payload = {
    "model": "qwen3:8b",
    "prompt": "Diga oi de forma rápida e direta.",
    "stream": False
}
r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=30)
data = r.json()
print("Raw response:", repr(data.get("response")))
print("Total duration (s):", data.get("total_duration", 0) / 1e9)
print("Eval duration (s):", data.get("eval_duration", 0) / 1e9)
print("Eval count:", data.get("eval_count", 0))
