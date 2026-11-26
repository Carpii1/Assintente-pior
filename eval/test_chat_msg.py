import requests

payload = {
    "model": "qwen3:8b",
    "messages": [
        {"role": "user", "content": "Diga oi"}
    ],
    "stream": False
}
r = requests.post("http://127.0.0.1:11434/api/chat", json=payload, timeout=30)
print(r.json())
