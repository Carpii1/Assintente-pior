import requests
import time

def benchmark():
    t0 = time.time()
    payload = {
        "model": "qwen3:8b",
        "prompt": "Responda em 1 frase curta: quem é você?",
        "stream": False,
        "options": {
            "num_predict": 40,
            "temperature": 0.6,
            "top_p": 0.9,
            "num_thread": 8
        }
    }
    r = requests.post("http://127.0.0.1:11434/api/generate", json=payload, timeout=30)
    data = r.json()
    elapsed = time.time() - t0
    eval_count = data.get("eval_count", 0)
    eval_dur = data.get("eval_duration", 1) / 1e9
    tok_sec = eval_count / eval_dur if eval_dur > 0 else 0
    print(f"Total time: {elapsed:.2f}s")
    print(f"Eval count: {eval_count} tokens in {eval_dur:.2f}s ({tok_sec:.1f} tokens/s)")
    print(f"Prompt eval: {data.get('prompt_eval_count')} tokens in {data.get('prompt_eval_duration',0)/1e9:.2f}s")
    print("Response:", data.get("response"))

if __name__ == "__main__":
    benchmark()
