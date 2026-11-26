from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import base64
import asyncio
import cv2
import mss
import numpy as np

router = APIRouter(prefix="/vision", tags=["Vision"])

def get_hub():
    from src.main import hub
    return hub

async def capture_webcam_frame() -> bytes:
    """
    Captura um frame da webcam com estratégia híbrida:
    1. Tenta recuperar o frame mais recente enviado pelo navegador ao Hub (evita conflito de câmera no Windows).
    2. Se não houver, tenta capturar diretamente via OpenCV (DirectShow).
    """
    # 1. Tenta pegar do Hub em memória
    hub_bytes = get_hub().latest_webcam_jpeg
    if hub_bytes:
        return hub_bytes

    # 2. Tenta abrir via OpenCV
    def _capture():
        for idx in (0, 1):
            try:
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        ret2, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                        if ret2:
                            return buf.tobytes()
            except Exception:
                pass
        return None

    frame = await asyncio.to_thread(_capture)
    if frame:
        get_hub().update_webcam(frame)
    return frame

async def capture_unified_screen() -> bytes:
    """Captura a tela unificada (todos os monitores juntos) usando mss."""
    # Primeiro verifica se o navegador já enviou o frame panorâmico
    hub_screen = get_hub().unified_screen_jpeg
    if hub_screen:
        return hub_screen

    def _capture():
        try:
            with mss.mss() as sct:
                mon = sct.monitors[0]  # Todos os monitores combinados
                sct_img = sct.grab(mon)
                img = np.array(sct_img)
                img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                ret, buf = cv2.imencode('.jpg', img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                return buf.tobytes() if ret else None
        except Exception as e:
            print(f"[Vision] Erro captura tela: {e}")
            return None

    return await asyncio.to_thread(_capture)

@router.post("/webcam")
async def webcam_capture(request: Request):
    """Captura um frame da webcam e retorna em base64 JPEG."""
    img_bytes = await capture_webcam_frame()
    if img_bytes is None:
        return JSONResponse({"error": "Webcam não disponível no momento."}, status_code=503)
    b64 = base64.b64encode(img_bytes).decode('utf-8')
    get_hub().update_webcam(img_bytes)
    return JSONResponse({"source": "webcam", "image": f"data:image/jpeg;base64,{b64}"})

@router.post("/screen")
async def screen_capture(request: Request):
    """Captura a tela panorâmica unificada e retorna em base64 JPEG."""
    img_bytes = await capture_unified_screen()
    if img_bytes is None:
        return JSONResponse({"error": "Falha ao capturar a tela."}, status_code=503)
    b64 = base64.b64encode(img_bytes).decode('utf-8')
    get_hub().update_unified_screen(img_bytes)
    return JSONResponse({"source": "unified_screen", "image": f"data:image/jpeg;base64,{b64}"})

@router.post("/model/select")
async def select_model(request: Request):
    data = await request.json()
    model_name = data.get("model", "qwen3-vl:8b")
    from src import ollama_manager
    result = await asyncio.to_thread(ollama_manager.load_single_model, model_name)
    return JSONResponse(result)

@router.get("/status")
async def vision_status():
    from src import ollama_manager
    gpu = await asyncio.to_thread(ollama_manager.get_gpu_telemetry)
    current = ollama_manager.get_current_model()
    return JSONResponse({"gpu": gpu, "active_model": current})
