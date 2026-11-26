import cv2
import ollama

MODEL = "qwen3-vl:8b"

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():
    raise RuntimeError("Não foi possível abrir a webcam.")

try:
    ok, frame = camera.read()

    if not ok or frame is None:
        raise RuntimeError("A webcam não retornou uma imagem.")

    ok, encoded = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, 85]
    )

    if not ok:
        raise RuntimeError("Não foi possível codificar a imagem.")

    image_bytes = encoded.tobytes()

finally:
    camera.release()

print("Imagem capturada. Enviando ao Qwen3-VL...")

response = ollama.chat(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": (
                "Descreva objetivamente o que aparece nesta imagem. "
                "Responda em português."
            ),
            "images": [image_bytes]
        }
    ]
)

print("\nRESPOSTA DO MODELO:")
print(response.message.content)