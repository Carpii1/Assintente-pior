import os
import base64
import requests

BASE_URL = "http://127.0.0.1:8000"

# Usa a imagem existente da interface que contém opções de modelo
img_path = r"C:\Users\paulo\.gemini\antigravity\brain\71576207-fbc7-4a43-af49-0a30c762d1fa\.user_uploaded\media_1794863346042_a9aee78b.png"
with open(img_path, "rb") as f:
    b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

# 1. Faz upload como tela compartilhada
r_up = requests.post(f"{BASE_URL}/upload_frame", json={
    "source": "unified_screen",
    "image": b64,
    "frames": [b64]
})
print("Upload Tela:", r_up.status_code, r_up.json())

# 2. Pergunta sobre o que está na tela (Leitura e OCR)
payload = {
    "message": "O que você está vendo na minha tela? Leia as opções abertas.",
    "history": [],
    "mode": "direto"
}
r_chat = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
print("\nResposta do PIOR sobre a tela:")
data = r_chat.json()
print("Backend:", data.get("backend"))
print("Reply:", data.get("reply"))
print("Latency:", data.get("latency_ms"), "ms")
