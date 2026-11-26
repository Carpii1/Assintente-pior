import os
import subprocess
import time
import requests
import psutil
from typing import Dict, Any, List, Optional

OLLAMA_EXE = os.path.join(os.environ.get("LOCALAPPDATA", r"C:\Users\paulo\AppData\Local"), r"Programs\Ollama\ollama.exe")
if not os.path.exists(OLLAMA_EXE):
    OLLAMA_EXE = "ollama"

OLLAMA_MODELS_PATH = os.environ.get("OLLAMA_MODELS", r"F:\IA\Ollama\Models")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")

# Track current selected model in memory (Multimodal 8B default com sintonia PIOR)
_CURRENT_MODEL = "pior-vl:8b"

def is_ollama_running() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def ensure_ollama_server() -> bool:
    if is_ollama_running():
        return True

    env = os.environ.copy()
    env["OLLAMA_MODELS"] = OLLAMA_MODELS_PATH
    
    creationflags = 0
    if hasattr(subprocess, "DETACHED_PROCESS") and hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP

    try:
        subprocess.Popen(
            [OLLAMA_EXE, "serve"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags
        )
    except Exception as e:
        print(f"[OllamaManager] Failed to launch Ollama serve: {e}")
        return False

    # Wait for service up to 10 seconds
    for _ in range(10):
        time.sleep(1)
        if is_ollama_running():
            print("[OllamaManager] Ollama server is up and running.")
            return True

    return False

def list_installed_models() -> List[Dict[str, Any]]:
    ensure_ollama_server()
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        if r.status_code == 200:
            data = r.json()
            models = []
            for m in data.get("models", []):
                name = m.get("name", "")
                param_size = m.get("details", {}).get("parameter_size", "")
                quant = m.get("details", {}).get("quantization_level", "")
                size_gb = round(m.get("size", 0) / (1024 ** 3), 2)
                models.append({
                    "name": name,
                    "parameter_size": param_size,
                    "quantization": quant,
                    "size_gb": size_gb,
                    "digest": m.get("digest", "")
                })
            return models
    except Exception as e:
        print(f"[OllamaManager] Error listing models: {e}")
    return []

def get_loaded_models() -> List[Dict[str, Any]]:
    if not is_ollama_running():
        return []
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/ps", timeout=2)
        if r.status_code == 200:
            data = r.json()
            loaded = []
            for m in data.get("models", []):
                name = m.get("name", "")
                vram_gb = round(m.get("size_vram", 0) / (1024 ** 3), 2)
                total_size_gb = round(m.get("size", 0) / (1024 ** 3), 2)
                param_size = m.get("details", {}).get("parameter_size", "")
                loaded.append({
                    "name": name,
                    "param_size": param_size,
                    "vram_gb": vram_gb,
                    "size_gb": total_size_gb,
                    "expires_at": m.get("expires_at", "")
                })
            return loaded
    except Exception as e:
        print(f"[OllamaManager] Error checking api/ps: {e}")
    return []

def unload_all_models() -> bool:
    """Unloads all models to ensure strictly zero or one model in VRAM."""
    loaded = get_loaded_models()
    for m in loaded:
        name = m.get("name")
        if name:
            try:
                requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={"model": name, "keep_alive": 0},
                    timeout=5
                )
            except Exception as e:
                print(f"[OllamaManager] Error unloading {name}: {e}")
    return True

def resolve_model_name(name: str) -> str:
    """Mapeia nomes de modelo para as versões ideais instaladas (prioriza o modelo treinado pior-vl:8b)."""
    installed = [m.get("name") for m in list_installed_models()]
    if name in ("qwen3-vl:8b", "qwen3-vl:8b-instruct", "pior-vl:8b"):
        if "pior-vl:8b" in installed:
            return "pior-vl:8b"
        if "qwen3-vl:8b-instruct" in installed:
            return "qwen3-vl:8b-instruct"
        return "qwen3-vl:8b"
    return name

def load_single_model(model_name: str) -> Dict[str, Any]:
    """Ensures only ONE model is loaded by unloading others first, then loading model_name."""
    global _CURRENT_MODEL
    ensure_ollama_server()

    actual_model = resolve_model_name(model_name)

    # Unload any model that isn't the requested one
    loaded = get_loaded_models()
    for m in loaded:
        if m.get("name") != actual_model:
            try:
                requests.post(
                    f"{OLLAMA_BASE_URL}/api/generate",
                    json={"model": m.get("name"), "keep_alive": 0},
                    timeout=5
                )
            except Exception:
                pass

    # Load requested model with 60m keep-alive
    t0 = time.time()
    try:
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={"model": actual_model, "keep_alive": "60m"},
            timeout=120
        )
        elapsed = round(time.time() - t0, 2)
        if r.status_code == 200:
            _CURRENT_MODEL = model_name  # Mantém o nome público escolhido
            # Fetch active status
            loaded = get_loaded_models()
            vram_gb = 0.0
            for m in loaded:
                if m.get("name") == actual_model:
                    vram_gb = m.get("vram_gb", 0.0)
            return {
                "success": True,
                "model": model_name,
                "actual_model": actual_model,
                "load_time_s": elapsed,
                "vram_gb": vram_gb,
                "status": "loaded"
            }
        else:
            return {"success": False, "error": f"Ollama HTTP {r.status_code}: {r.text}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_current_model() -> str:
    global _CURRENT_MODEL
    return _CURRENT_MODEL

def set_current_model(model_name: str):
    global _CURRENT_MODEL
    _CURRENT_MODEL = model_name

def get_gpu_telemetry() -> Dict[str, Any]:
    """Queries nvidia-smi for VRAM, GPU utilization and temperature."""
    try:
        output = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
            encoding="utf-8",
            timeout=2
        ).strip()
        parts = [p.strip() for p in output.split(",")]
        if len(parts) >= 6:
            total_mb = float(parts[1])
            used_mb = float(parts[2])
            free_mb = float(parts[3])
            util_pct = int(parts[4])
            temp_c = int(parts[5])
            vram_pct = round((used_mb / total_mb) * 100, 1) if total_mb > 0 else 0
            return {
                "available": True,
                "name": parts[0],
                "total_vram_gb": round(total_mb / 1024, 2),
                "used_vram_gb": round(used_mb / 1024, 2),
                "free_vram_gb": round(free_mb / 1024, 2),
                "vram_percent": vram_pct,
                "gpu_util_percent": util_pct,
                "temperature_c": temp_c
            }
    except Exception as e:
        pass
    return {
        "available": False,
        "name": "N/A",
        "total_vram_gb": 0,
        "used_vram_gb": 0,
        "free_vram_gb": 0,
        "vram_percent": 0,
        "gpu_util_percent": 0,
        "temperature_c": 0
    }

def get_ram_telemetry() -> Dict[str, Any]:
    try:
        v = psutil.virtual_memory()
        return {
            "total_gb": round(v.total / (1024 ** 3), 2),
            "used_gb": round(v.used / (1024 ** 3), 2),
            "free_gb": round(v.available / (1024 ** 3), 2),
            "percent": v.percent
        }
    except Exception:
        return {"total_gb": 0, "used_gb": 0, "free_gb": 0, "percent": 0}

def get_full_system_status() -> Dict[str, Any]:
    gpu = get_gpu_telemetry()
    ram = get_ram_telemetry()
    loaded = get_loaded_models()
    active_model = loaded[0] if loaded else None
    
    return {
        "gpu": gpu,
        "ram": ram,
        "ollama_running": is_ollama_running(),
        "active_model": active_model,
        "selected_model": get_current_model()
    }
