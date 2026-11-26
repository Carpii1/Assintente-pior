import requests
import time

tests = [
    {"name": "think=False in root", "payload": {"model": "qwen3:8b", "messages": [{"role": "user", "content": "Diga oi"}], "stream": False, "think": False}},
    {"name": "think=False in options", "payload": {"model": "qwen3:8b", "messages": [{"role": "user", "content": "Diga oi"}], "stream": False, "options": {"think": False}}},
    {"name": "system prompt strict no thinking", "payload": {"model": "qwen3:8b", "messages": [{"role": "system", "content": "/no_think"}, {"role": "user", "content": "Diga oi"}], "stream": False}},
    {"name": "system prompt /think=off", "payload": {"model": "qwen3:8b", "messages": [{"role": "system", "content": "Respond without thinking process."}, {"role": "user", "content": "Diga oi"}], "stream": False}}
]

for t in tests:
    t0 = time.time()
    try:
        r = requests.post("http://127.0.0.1:11434/api/chat", json=t["payload"], timeout=20)
        res = r.json()
        print(f"[{t['name']}] Elapsed: {time.time()-t0:.2f}s | Has thinking: {bool(res.get('message', {}).get('thinking'))} | Content: {repr(res.get('message', {}).get('content'))}")
    except Exception as e:
        print(f"[{t['name']}] Error: {e}")
