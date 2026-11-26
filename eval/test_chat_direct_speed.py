import requests
import time

payload = {
    "model": "qwen3:8b",
    "messages": [
        {"role": "system", "content": "Você é o assistente PIOR. Responda em no máximo 1 a 2 frases curtas sem símbolos markdown."},
        {"role": "user", "content": "Que horas são?"}
    ],
    "stream": False,
    "think": False
}

t0 = time.time()
r = requests.post("http://127.0.0.1:11434/api/chat", json=payload, timeout=10)
data = r.json()
elapsed = time.time() - t0
print(f"Elapsed: {elapsed:.3f}s ({int(elapsed*1000)}ms)")
print("Response:", data.get("message", {}).get("content"))
print("Has thinking:", bool(data.get("message", {}).get("thinking")))
