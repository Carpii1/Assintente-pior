import os
import sys
import json
import base64
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_model_resolution():
    print("\n--- Teste 1: Resolução de Modelo ---")
    r = requests.get(f"{BASE_URL}/api/models")
    print("Status /api/models:", r.status_code)
    installed = [m.get("name") for m in r.json().get("models", [])]
    print("Modelos instalados:", installed)
    assert "pior-vl:8b" in installed, "pior-vl:8b deve estar instalado no Ollama"
    print("PASS: pior-vl:8b detectado com sucesso!")

def test_chat_text_portuguese():
    print("\n--- Teste 2: Pergunta Textual sem Markdown ---")
    payload = {
        "message": "Qual é a temperatura do sol?",
        "history": [],
        "mode": "direto"
    }
    r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=60)
    print("Status:", r.status_code)
    data = r.json()
    reply = data.get("reply", "")
    print("Resposta:", reply)
    print("Backend:", data.get("backend"))
    assert reply, "Resposta não pode ser vazia"
    assert "*" not in reply, "Resposta não deve conter asteriscos de markdown"
    print("PASS: Resposta fluida em português sem markdown!")

def test_email_interactive_flow():
    print("\n--- Teste 3: Fluxo Interativo de E-mail ---")
    # Turno 1: Usuário pede envio de email sem corpo
    p1 = {
        "message": "Envie um e-mail para o professor Carlos",
        "history": []
    }
    r1 = requests.post(f"{BASE_URL}/chat", json=p1)
    d1 = r1.json()
    print("Turno 1 - Pergunta ao usuário:", d1.get("reply"))
    assert "corpo" in d1.get("reply", "").lower() or "dizer" in d1.get("reply", "").lower(), "Deve perguntar o que dizer no corpo"

    # Turno 2: Usuário fornece a descrição simples
    p2 = {
        "message": "Avisa que terminei a implementação da visão da tela e vou enviar o relatório amanhã",
        "history": [
            {"role": "user", "content": "Envie um e-mail para o professor Carlos"},
            {"role": "assistant", "content": d1.get("reply")}
        ]
    }
    r2 = requests.post(f"{BASE_URL}/chat", json=p2, timeout=60)
    d2 = r2.json()
    print("Turno 2 - Resposta e Card:", d2.get("reply"))
    act = d2.get("action", {})
    print("Action type:", act.get("type"))
    print("Draft Body:", act.get("body"))
    print("Mailto URL:", act.get("mailto_url"))
    assert act.get("type") == "email_draft", "Deve gerar o rascunho de e-mail interativo"
    print("PASS: Fluxo de e-mail interativo multi-turno validado!")

def test_screen_frame_upload():
    print("\n--- Teste 4: Upload de Frames de Monitor em Alta Definição ---")
    # Cria uma imagem 100x100 em memória
    sample_b64 = "data:image/jpeg;base64," + base64.b64encode(b"dummy_test_bytes").decode("utf-8")
    payload = {
        "source": "unified_screen",
        "image": sample_b64,
        "frames": [sample_b64]
    }
    r = requests.post(f"{BASE_URL}/upload_frame", json=payload)
    print("Status upload_frame:", r.status_code, r.json())
    assert r.status_code == 200, "Upload de frame deve ser 200 OK"
    print("PASS: Upload de múltiplos monitores individuais validado!")

if __name__ == "__main__":
    try:
        test_model_resolution()
        test_chat_text_portuguese()
        test_email_interactive_flow()
        test_screen_frame_upload()
        print("\nTODOS OS TESTES DE VALIDAÇÃO PASSARAM!")
    except Exception as e:
        print(f"\nERRO NO TESTE: {e}")
        sys.exit(1)
