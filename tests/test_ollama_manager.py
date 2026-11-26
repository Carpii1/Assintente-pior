import pytest
from src import ollama_manager

def test_ram_telemetry():
    ram = ollama_manager.get_ram_telemetry()
    assert isinstance(ram, dict)
    assert ram["total_gb"] > 0
    assert ram["used_gb"] > 0
    assert 0 <= ram["percent"] <= 100

def test_gpu_telemetry_structure():
    gpu = ollama_manager.get_gpu_telemetry()
    assert isinstance(gpu, dict)
    assert "available" in gpu
    assert "total_vram_gb" in gpu
    assert "used_vram_gb" in gpu
    assert "gpu_util_percent" in gpu
    assert "temperature_c" in gpu

def test_current_model_selection():
    ollama_manager.set_current_model("qwen3:8b")
    assert ollama_manager.get_current_model() == "qwen3:8b"
    ollama_manager.set_current_model("qwen3:14b")
    assert ollama_manager.get_current_model() == "qwen3:14b"
    # Reset
    ollama_manager.set_current_model("qwen3:8b")

def test_full_system_status_structure():
    status = ollama_manager.get_full_system_status()
    assert "gpu" in status
    assert "ram" in status
    assert "ollama_running" in status
    assert "selected_model" in status
