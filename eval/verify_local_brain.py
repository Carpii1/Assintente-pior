import requests
import json
import time

def verify_all():
    base = "http://127.0.0.1:8000"
    
    print("\n--- 1. Testing GET /api/system_status ---")
    r1 = requests.get(f"{base}/api/system_status", timeout=5)
    print("Status code:", r1.status_code)
    status_data = r1.json()
    print("GPU:", json.dumps(status_data.get("gpu", {}), indent=2))
    print("RAM:", json.dumps(status_data.get("ram", {}), indent=2))
    print("Ollama running:", status_data.get("ollama_running"))
    print("Active model:", status_data.get("active_model"))

    print("\n--- 2. Testing GET /api/models ---")
    r2 = requests.get(f"{base}/api/models", timeout=5)
    print("Status code:", r2.status_code)
    models_data = r2.json()
    print("Installed models:", [m["name"] for m in models_data.get("models", [])])

    print("\n--- 3. Testing POST /api/model/load (qwen3:8b) ---")
    t0 = time.time()
    r3 = requests.post(f"{base}/api/model/load", json={"model": "qwen3:8b"}, timeout=120)
    print(f"Loaded in {time.time()-t0:.2f}s, status: {r3.status_code}, result: {r3.json()}")

    print("\n--- 4. Testing POST /chat with local Ollama ---")
    t1 = time.time()
    chat_payload = {
        "message": "Olá Pior, confirme que você está usando o modelo local qwen3 8b.",
        "history": [],
        "mode": "direto"
    }
    r4 = requests.post(f"{base}/chat", json=chat_payload, timeout=60)
    print(f"Chat status: {r4.status_code} in {time.time()-t1:.2f}s")
    print("Chat response JSON:", json.dumps(r4.json(), indent=2, ensure_ascii=False))

    print("\n--- 5. Verifying telemetry after load ---")
    r5 = requests.get(f"{base}/api/system_status", timeout=5)
    status_after = r5.json()
    print("GPU VRAM used (GB):", status_after.get("gpu", {}).get("used_vram_gb"))
    print("Active Model in VRAM:", status_after.get("active_model"))

if __name__ == "__main__":
    verify_all()
