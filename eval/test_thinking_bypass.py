import requests
import time

def test_speed_prompt():
    payloads = [
        {
            "name": "Standard prompt",
            "prompt": "Diga oi de forma rápida e direta."
        },
        {
            "name": "Instruct no think",
            "system": "Você é um assistente direto. NUNCA pense antes de responder. Responda imediatamente em 1 palavra.",
            "prompt": "Diga oi."
        },
        {
            "name": "With stop token",
            "system": "Direto e rápido.",
            "prompt": "Diga oi.",
            "options": {"num_predict": 30, "temperature": 0.3}
        }
    ]

    for p in payloads:
        t0 = time.time()
        body = {
            "model": "qwen3:8b",
            "prompt": p["prompt"],
            "stream": False,
            "options": p.get("options", {"num_predict": 40})
        }
        if "system" in p:
            body["system"] = p["system"]
        r = requests.post("http://127.0.0.1:11434/api/generate", json=body, timeout=30)
        data = r.json()
        print(f"[{p['name']}] Elapsed: {time.time()-t0:.2f}s | Eval count: {data.get('eval_count')} | Response: {repr(data.get('response'))}")

if __name__ == "__main__":
    test_speed_prompt()
