import pytest
from fastapi.testclient import TestClient
from src.main import app, clean_for_speech, build_system_prompt

client = TestClient(app)

def test_root_html_endpoint():
    """Verifica se a rota raiz entrega a interface HTML moderna com status 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "PIOR MULTIMODAL" in response.text
    assert "<canvas id=\"panoramicCanvas\"" in response.text

def test_logo_endpoint():
    """Verifica se o endpoint dinâmico de logo responde corretamente."""
    response = client.get("/logo")
    assert response.status_code in (200, 404)

def test_clean_for_speech_filter():
    """Garante que a higienização de voz remove asteriscos, cerquilhas e marcadores."""
    markdown_text = "**Olá**! Este é o # PIOR com *visão* e `código`:\n- Item 1\n* Item 2"
    cleaned = clean_for_speech(markdown_text)
    assert "*" not in cleaned
    assert "#" not in cleaned
    assert "`" not in cleaned
    assert "Olá! Este é o PIOR com visão e código: Item 1 Item 2" in cleaned

def test_system_prompt_mode_direto():
    """Garante que o modo direto inclui a instrução de brevidade."""
    prompt = build_system_prompt("direto")
    assert "MODO DIRETO (Ativo)" in prompt
    assert "1 a 3 frases" in prompt

def test_system_prompt_mode_detalhado():
    """Garante que o modo detalhado inclui a instrução de profundidade."""
    prompt = build_system_prompt("detalhado")
    assert "MODO DETALHADO (Ativo)" in prompt

def test_chat_empty_message_validation():
    """Testa validação de entrada vazia na API de chat."""
    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 400

def test_upload_frame_valid_and_invalid():
    """Testa o endpoint de sincronização de imagem."""
    # Inválido sem payload
    res_inv = client.post("/upload_frame", json={})
    assert res_inv.status_code == 400

    # Válido com base64 mínimo
    res_val = client.post("/upload_frame", json={
        "source": "webcam",
        "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
    })
    assert res_val.status_code == 200

def test_system_status_endpoint():
    """Testa se o endpoint de telemetria retorna estrutura com GPU, RAM e Ollama."""
    response = client.get("/api/system_status")
    assert response.status_code == 200
    data = response.json()
    assert "gpu" in data
    assert "ram" in data
    assert "ollama_running" in data
    assert "selected_model" in data
    # RAM deve ter total_gb e used_gb
    assert "total_gb" in data["ram"]
    assert "percent" in data["ram"]

def test_models_endpoint():
    """Testa se o endpoint de modelos retorna lista de modelos locais."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "active" in data

def test_unload_endpoint():
    """Testa endpoint de descarregamento da VRAM."""
    response = client.post("/api/model/unload")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "unloaded"

