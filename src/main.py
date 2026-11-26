import os
import cv2
import numpy as np
import io
import base64
import asyncio
import glob
import time
import threading
import re
import urllib.parse
import traceback
from typing import Generator, List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
from PIL import Image

from dotenv import load_dotenv
import requests

from src import ollama_manager, vision, web_search, actions

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ---------- Sensory Perception Hub (Unified Panoramic Screen + Webcam + Multi-Monitor) ----------
class SensoryPerceptionHub:
    def __init__(self):
        self.lock = threading.Lock()
        self.latest_webcam_jpeg = None
        self.unified_screen_jpeg = None
        self.screen_frames = []

    def update_webcam(self, jpeg_bytes: bytes):
        with self.lock:
            self.latest_webcam_jpeg = jpeg_bytes

    def update_unified_screen(self, jpeg_bytes: bytes, individual_frames: Optional[List[bytes]] = None):
        with self.lock:
            self.unified_screen_jpeg = jpeg_bytes
            if individual_frames and len(individual_frames) > 0:
                self.screen_frames = individual_frames
            elif jpeg_bytes:
                self.screen_frames = [jpeg_bytes]

    def get_webcam(self) -> bytes:
        with self.lock:
            if self.latest_webcam_jpeg:
                return self.latest_webcam_jpeg
        # Fallback OpenCV direto se o hub estiver sem quadro
        try:
            for idx in (0, 1):
                cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, frame = cap.read()
                    cap.release()
                    if ret and frame is not None:
                        ret2, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
                        if ret2:
                            b = buf.tobytes()
                            self.latest_webcam_jpeg = b
                            return b
        except Exception:
            pass
        return None

    def get_unified_screen(self) -> bytes:
        with self.lock:
            return self.unified_screen_jpeg

    def get_screen_frames(self) -> List[bytes]:
        """Retorna os frames individuais dos monitores em alta fidelidade."""
        with self.lock:
            if self.screen_frames:
                return list(self.screen_frames)
            if self.unified_screen_jpeg:
                return [self.unified_screen_jpeg]
            return []

hub = SensoryPerceptionHub()

@asynccontextmanager
async def lifespan(app: FastAPI):
    def startup_worker():
        ollama_manager.ensure_ollama_server()
        try:
            ollama_manager.load_single_model("qwen3-vl:8b")
        except Exception as e:
            print(f"[Lifespan] Erro ao pré-carregar qwen3-vl:8b: {e}")

    threading.Thread(target=startup_worker, daemon=True).start()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(vision.router)
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# ---------- System Persona Prompt com Suporte a Tela, OCR, Cupons e SO ----------
def build_system_prompt(detail_mode: str = "direto") -> str:
    conciseness_instruction = (
        "- MODO DIRETO (Ativo): Responda em no máximo 1 a 3 frases curtas e objetivas, vá direto ao ponto sem enrolação."
        if detail_mode == "direto" else
        "- MODO DETALHADO (Ativo): Forneça explicações completas, didáticas e detalhadas, aprofundando o assunto com clareza."
    )

    return f"""/no_think
Você é o PIOR, um assistente inteligente multimodal de voz para desktop, com visão em tempo real (webcam e tela compartilhada), pesquisa na web e integração com o computador.

DIRETRIZES DE FALA E PERSONALIDADE:
1. IDENTIDADE:
   - Seu nome oficial é PIOR. Seja amigável, direto, seguro e proativo.
   - SEMPRE responda em Português do Brasil. NUNCA responda em inglês ou monólogo de pensamento.

2. COMUNICAÇÃO VOICE-FIRST (SEM MARKDOWN):
   - NUNCA use formatação markdown: NÃO use asteriscos, hashtags, traços de lista, crases ou tabelas.
   - Fale apenas texto corrido e pontuação natural de conversa falada, como em um podcast ou assistente ao vivo.

3. VISÃO DE TELA E WEBCAM EM TEMPO REAL:
   - Leitura de tela e OCR: Quando o usuário compartilhar a tela, leia exatamente o que está escrito, realize traduções e resuma conteúdos.
   - Identificação de Wallpaper: Se o usuário perguntar sobre o wallpaper ou plano de fundo da área de trabalho, analise a arte, personagem, jogo, anime, filme ou paisagem do desktop.
   - Lojas e Cupons: Se houver um site de compras ou o usuário mencionar compras/produtos, aponte promoções, preços e cupons de desconto ativos.
   - Webcam: Identifique objetos, quadros de parede, álbuns de música, roupas e o ambiente físico.

4. AÇÕES NO COMPUTADOR (PROATIVIDADE):
   - E-mails: Ajude a redigir e estruturar e-mails claros prontos para envio.
   - Calendário: Auxilie na marcação de reuniões e compromissos.
   - Arquivos: Ajude a criar e organizar notas e arquivos de texto.

5. EXTENSÃO:
   {conciseness_instruction}
   - Mantenha sempre a memória da conversa para responder com continuidade.
"""

def clean_for_speech(text: str) -> str:
    cleaned = re.sub(r'[*_~`#>]', '', text)
    cleaned = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'^\s*[-*+]\s+', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def extract_reply(response_data: dict) -> str:
    """Extrai a resposta real do Ollama. NUNCA utiliza o campo 'thinking'."""
    msg = response_data.get("message", {})
    content = msg.get("content", "").strip()
    if content:
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        if content:
            return content
    return ""

async def call_ollama(messages: list, model: str, num_predict: int, timeout: int = 60) -> str:
    """Chama a API do Ollama sem streaming e sem thinking."""
    actual_model = ollama_manager.resolve_model_name(model)
    payload = {
        "model": actual_model,
        "messages": messages,
        "stream": False,
        "think": False,
        "options": {
            "num_predict": num_predict,
            "temperature": 0.5,
            "top_p": 0.9
        }
    }
    try:
        res = await asyncio.to_thread(
            requests.post,
            "http://127.0.0.1:11434/api/chat",
            json=payload,
            timeout=timeout
        )
        reply = extract_reply(res.json())
        if reply:
            return reply
    except Exception as e:
        print(f"[OllamaCall] Erro na chamada: {e}")

    # Fallback caso venha vazio
    msgs2 = [m.copy() for m in messages]
    for i in reversed(range(len(msgs2))):
        if msgs2[i]["role"] == "user":
            msgs2[i]["content"] = msgs2[i]["content"] + "\n\n[Responda agora diretamente em português falado em uma frase.]"
            break
    payload2 = {**payload, "messages": msgs2, "options": {**payload["options"], "num_predict": num_predict + 80}}
    try:
        res2 = await asyncio.to_thread(
            requests.post,
            "http://127.0.0.1:11434/api/chat",
            json=payload2,
            timeout=timeout
        )
        return extract_reply(res2.json()) or "Desculpe, não consegui obter a resposta no momento."
    except Exception as e:
        return f"Ocorreu uma instabilidade na geração: {e}"

@app.get("/logo")
async def get_logo():
    # Procura logo padronizado em assets ou na raiz
    assets_logo = os.path.join(PROJECT_ROOT, "assets", "logo_pior.png")
    if os.path.exists(assets_logo):
        return FileResponse(assets_logo)
    pattern = os.path.join(PROJECT_ROOT, "*Logo Pior com Robô Neon Multimodal*.*")
    matches = glob.glob(pattern)
    if matches:
        return FileResponse(matches[0])
    fallback = os.path.join(os.path.dirname(__file__), "static", "logo.png")
    if os.path.exists(fallback):
        return FileResponse(fallback)
    return JSONResponse(status_code=404, content={"error": "Logo not found"})

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    async with aiofiles.open(html_path, "r", encoding="utf-8") as f:
        content = await f.read()
    return HTMLResponse(content)

# ---------- Local Ollama Brain & Hardware Telemetry APIs ----------

@app.get("/api/system_status")
async def get_system_status():
    status = await asyncio.to_thread(ollama_manager.get_full_system_status)
    return JSONResponse(content=status)

@app.get("/api/models")
async def get_models():
    models = await asyncio.to_thread(ollama_manager.list_installed_models)
    return JSONResponse(content={"models": models, "active": ollama_manager.get_current_model()})

@app.post("/api/models/ensure")
async def ensure_model(request: Request):
    data = await request.json()
    model_name = data.get("model", "qwen3-vl:8b")
    result = await asyncio.to_thread(ollama_manager.load_single_model, model_name)
    models = await asyncio.to_thread(ollama_manager.list_installed_models)
    return JSONResponse(content={"ensure": result, "models": models, "active": ollama_manager.get_current_model()})

@app.post("/api/model/load")
async def load_model_endpoint(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}
    model_name = data.get("model", "qwen3-vl:8b")
    result = await asyncio.to_thread(ollama_manager.load_single_model, model_name)
    return JSONResponse(content=result)

@app.post("/api/model/unload")
async def unload_model_endpoint():
    success = await asyncio.to_thread(ollama_manager.unload_all_models)
    return JSONResponse(content={"success": success, "status": "unloaded"})

@app.post("/upload_frame")
async def upload_frame(request: Request):
    data = await request.json()
    source = data.get("source")
    b64_img = data.get("image")
    b64_frames = data.get("frames", [])

    try:
        if source == "webcam" and b64_img:
            img_bytes = base64.b64decode(b64_img.split(",")[-1])
            hub.update_webcam(img_bytes)
            return JSONResponse({"status": "ok"})
        elif source in ("screen", "unified_screen"):
            main_bytes = base64.b64decode(b64_img.split(",")[-1]) if b64_img else None
            ind_bytes = []
            for f in b64_frames:
                if f:
                    ind_bytes.append(base64.b64decode(f.split(",")[-1]))
            hub.update_unified_screen(main_bytes, ind_bytes)
            return JSONResponse({"status": "ok", "screens_count": len(ind_bytes) or (1 if main_bytes else 0)})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return JSONResponse({"error": "No image"}, status_code=400)

@app.post("/chat")
async def chat_endpoint(request: Request):
    start_time = time.time()
    data = await request.json()
    raw_user_msg = data.get("message", "").strip()
    history = data.get("history", [])
    detail_mode = data.get("mode", "direto")

    if not raw_user_msg:
        return JSONResponse(content={"error": "Mensagem vazia."}, status_code=400)

    cleaned_user_msg = re.sub(r'^(ei\s+|olá\s+|ola\s+|oi\s+)?pior[\s,.:;!?]*', '', raw_user_msg, flags=re.IGNORECASE).strip()
    user_msg = cleaned_user_msg if cleaned_user_msg else raw_user_msg
    msg_lower = user_msg.lower()

    # -------------------------------------------------------------
    # 1. FLUXO DE AÇÕES DO SISTEMA: E-MAIL
    # -------------------------------------------------------------
    email_check = actions.check_email_intent(user_msg, history)
    if email_check.get("is_email_action"):
        stage = email_check.get("stage")
        if stage == "ask_body":
            recipient = email_check.get("recipient", "destinatário")
            reply = f"Com certeza! O que você quer dizer no corpo do e-mail para {recipient}?"
            return JSONResponse(content={
                "reply": reply,
                "backend": "PIOR Ações (E-mail Interativo)",
                "latency_ms": int((time.time() - start_time) * 1000),
                "action": {
                    "type": "email_waiting_body",
                    "recipient": recipient
                }
            })
        elif stage == "complete":
            recipient = email_check.get("recipient", "")
            subject = email_check.get("subject", "Contato")
            body_desc = email_check.get("body_description", "")
            
            # Pede à LLM para redigir o corpo profissional e fluido
            draft_prompt = [
                {"role": "system", "content": "Você é um assistente executivo. Redija um e-mail claro, profissional e cordial em português com base na descrição. Responda APENAS o corpo do e-mail em texto puro."},
                {"role": "user", "content": f"Para: {recipient}\nAssunto: {subject}\nConteúdo desejado: {body_desc}"}
            ]
            active_model = ollama_manager.get_current_model()
            body_draft = await call_ollama(draft_prompt, active_model, num_predict=220, timeout=30)
            body_draft = clean_for_speech(body_draft).strip()

            encoded_sub = urllib.parse.quote(subject)
            encoded_body = urllib.parse.quote(body_draft)
            mailto_url = f"mailto:{recipient}?subject={encoded_sub}&body={encoded_body}"

            reply = f"Criei o rascunho do e-mail para {recipient} com o assunto {subject}. Veja na tela para conferir ou enviar agora mesmo."
            return JSONResponse(content={
                "reply": reply,
                "backend": "PIOR Ações (E-mail Criado)",
                "latency_ms": int((time.time() - start_time) * 1000),
                "action": {
                    "type": "email_draft",
                    "recipient": recipient,
                    "subject": subject,
                    "body": body_draft,
                    "mailto_url": mailto_url
                }
            })

    # -------------------------------------------------------------
    # 2. FLUXO DE AÇÕES DO SISTEMA: CALENDÁRIO / EVENTOS
    # -------------------------------------------------------------
    cal_check = actions.check_calendar_intent(user_msg)
    if cal_check and cal_check.get("requested"):
        cal_res = actions.create_calendar_event(cal_check.get("title", "Compromisso"))
        if cal_res.get("success"):
            reply = f"Agendei o evento {cal_res.get('title')} para {cal_res.get('start_time')}. Salvei o arquivo de calendário no seu computador."
            return JSONResponse(content={
                "reply": reply,
                "backend": "PIOR Ações (Calendário)",
                "latency_ms": int((time.time() - start_time) * 1000),
                "action": {
                    "type": "calendar_event",
                    "title": cal_res.get("title"),
                    "start_time": cal_res.get("start_time"),
                    "filename": cal_res.get("filename"),
                    "filepath": cal_res.get("filepath")
                }
            })

    # -------------------------------------------------------------
    # 3. FLUXO DE AÇÕES DO SISTEMA: CRIAR ARQUIVO
    # -------------------------------------------------------------
    file_check = actions.check_file_creation_intent(user_msg)
    if file_check and file_check.get("requested"):
        filename = file_check.get("filename", "anotacao.txt")
        # Gera o conteúdo com a LLM
        file_prompt = [
            {"role": "system", "content": "Gere o conteúdo em texto puro para o arquivo solicitado pelo usuário."},
            {"role": "user", "content": user_msg}
        ]
        active_model = ollama_manager.get_current_model()
        file_content = await call_ollama(file_prompt, active_model, num_predict=300, timeout=30)
        file_res = actions.create_local_file(filename, file_content)
        if file_res.get("success"):
            reply = f"Criei o arquivo {file_res.get('filename')} com sucesso na pasta de documentos."
            return JSONResponse(content={
                "reply": reply,
                "backend": "PIOR Ações (Arquivo Criado)",
                "latency_ms": int((time.time() - start_time) * 1000),
                "action": {
                    "type": "file_created",
                    "filename": file_res.get("filename"),
                    "filepath": file_res.get("filepath"),
                    "content": file_content[:500]
                }
            })

    # -------------------------------------------------------------
    # 4. DETECÇÃO INTELIGENTE DE VISÃO (TELA & WEBCAM)
    # -------------------------------------------------------------
    need_screen = False
    need_webcam = False

    screen_patterns = [
        r"\b(tela|telas|monitor|monitores|janela|janelas|display|computador|desktop|área de trabalho|area de trabalho)\b",
        r"\b(wallpaper|papel de parede|fundo de tela|plano de fundo)\b",
        r"\b(leia|leitura|o que está escrito|oq tá escrito|traduz|traduza|tradução|pesquise sobre isso)\b.*(tela|monitor|aqui|página|pagina|site)",
        r"\b(site|loja|comprar|compras|cupom|cupons|desconto|preço|preco|oferta|ofertas|carrinho)\b",
        r"\b(veja|olhe|mostre|analise).*(tela|monitor|janela|wallpaper|site|página|pagina)\b",
        r"\b(o que|oq).*(na tela|nos monitores|aberto|no meu wallpaper|no meu papel de parede)\b"
    ]
    webcam_patterns = [
        r"\b(webcam|câmera|camera|vídeo|video)\b",
        r"\b(olhe|veja|mostre|diga|identif|reconhec|analis|leia|consegue ver|pode ver)\b.*(mim|eu|rosto|cara|mão|mao|segurando|atrás|atras|parede|fundo|ambiente|quadro|álbum|album|camisa|roupa|cor|objeto|livro|marca|embalagem)",
        r"\b(quadro|poster|pôster|álbum|album|capa|livro|garrafa|caneca|embalagem)\b",
        r"\b(atrás de mim|atras de mim|ao meu redor|minha sala|meu quarto|na parede|na minha mão|na minha mao)\b",
        r"\b(o que tem|o que há|o que esta|quem é|qual é).*(atrás|atras|ao fundo|na parede|em cima|no fundo)\b",
        r"\b(o que estou|o que tenho|o que você vê|o que voce ve)\b"
    ]

    for p in screen_patterns:
        if re.search(p, msg_lower):
            need_screen = True
            break

    for p in webcam_patterns:
        if re.search(p, msg_lower):
            need_webcam = True
            break

    active_model = ollama_manager.get_current_model()
    is_vl_model = "vl" in active_model.lower() or "vision" in active_model.lower()

    # Se o modelo for multimodal e o usuário fizer pergunta visual geral
    if is_vl_model and not need_screen and not need_webcam:
        if any(w in msg_lower for w in ["wallpaper", "papel de parede", "leia", "traduza", "site", "cupom", "tela"]):
            need_screen = True
        elif any(w in msg_lower for w in ["veja", "olhe", "identifique", "qual", "quem", "o que é", "o que e", "cor", "quadro", "album"]):
            need_webcam = True

    await asyncio.to_thread(ollama_manager.ensure_ollama_server)

    loaded = await asyncio.to_thread(ollama_manager.get_loaded_models)
    actual_current = ollama_manager.resolve_model_name(active_model)
    if not any(m.get("name") == actual_current for m in loaded):
        await asyncio.to_thread(ollama_manager.load_single_model, active_model)

    system_prompt = build_system_prompt(detail_mode)
    num_predict = 220 if detail_mode == "direto" else 500

    try:
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for turn in history[-6:]:
            role = turn.get("role")
            content = turn.get("content", "")
            if role in ("user", "assistant") and content:
                formatted_messages.append({"role": role, "content": content})

        # Processamento Multimodal (Tela Panorâmica e/ou Webcam)
        if need_screen or need_webcam:
            if not is_vl_model:
                await asyncio.to_thread(ollama_manager.load_single_model, "qwen3-vl:8b")
                active_model = ollama_manager.get_current_model()
                is_vl_model = True

            images_b64 = []
            sources_used = []

            if need_screen:
                screen_frames = hub.get_screen_frames()
                if not screen_frames:
                    try:
                        fallback_screen = await vision.capture_unified_screen()
                        if fallback_screen:
                            screen_frames = [fallback_screen]
                    except Exception:
                        screen_frames = []
                for sf in screen_frames:
                    if sf:
                        images_b64.append(base64.b64encode(sf).decode("utf-8"))
                if screen_frames:
                    sources_used.append(f"{len(screen_frames)} tela(s) em alta definição")

            if need_webcam:
                w_bytes = hub.get_webcam()
                if not w_bytes:
                    try:
                        w_bytes = await vision.capture_webcam_frame()
                    except Exception as cam_err:
                        print(f"[CHAT] Erro webcam: {cam_err}")
                        w_bytes = None
                if w_bytes:
                    images_b64.append(base64.b64encode(w_bytes).decode("utf-8"))
                    sources_used.append("webcam")

            # Pesquisa Web / Cupons / Notícias Integradas (só roda se explicitamente necessário)
            search_context_text = ""
            user_wants_search = web_search.should_trigger_search(user_msg)
            is_shopping = web_search.is_shopping_or_coupon_query(user_msg)

            if user_wants_search or is_shopping:
                search_query = user_msg
                # Se for compras/cupons e temos tela, identificamos a loja na tela
                if is_shopping and images_b64:
                    try:
                        store_prompt = [
                            {"role": "system", "content": "Identifique em até 3 palavras qual loja online ou produto está visível na tela (ex: Amazon, Kabum, Mercado Livre, Shopee). Responda apenas o nome da loja/produto."},
                            {"role": "user", "content": "Qual loja ou produto está aqui?", "images": [images_b64[0]]}
                        ]
                        store_name = await call_ollama(store_prompt, active_model, num_predict=25, timeout=30)
                        clean_store = clean_for_speech(store_name).strip()
                        coupon_results = await asyncio.to_thread(web_search.search_coupons, clean_store or "loja online")
                        if coupon_results:
                            search_context_text = web_search.format_search_context(coupon_results)
                            sources_used.append("cupons web")
                    except Exception as e:
                        print(f"[CHAT] Erro busca cupons: {e}")

                elif user_wants_search:
                    try:
                        search_results = await asyncio.to_thread(web_search.perform_web_search, search_query, 4)
                        if search_results:
                            search_context_text = web_search.format_search_context(search_results)
                            sources_used.append("pesquisa web")
                    except Exception as e:
                        print(f"[CHAT] Erro busca web: {e}")

            # Monta o prompt final com diretrizes de visão de alta precisão
            final_user_content = user_msg
            if any(w in msg_lower for w in ["wallpaper", "papel de parede", "fundo", "desktop", "área de trabalho", "area de trabalho"]):
                final_user_content += (
                    "\n\n[DIRETRIZ DE VISÃO - WALLPAPER / PLANO DE FUNDO]:\n"
                    "O usuário está perguntando sobre o papel de parede (wallpaper/desktop) do computador dele. "
                    "Ignore ou olhe por trás das janelas abertas e foque diretamente na imagem de fundo da área de trabalho. "
                    "Identifique com precisão: o tema, personagens presentes, franquia (jogo, anime, filme, HQ ou arte digital), paisagem e paleta de cores. "
                    "Responda diretamente sem markdown."
                )

            if any(w in msg_lower for w in ["leia", "traduza", "traduz", "o que está escrito", "oq tá escrito", "leitura", "ler", "texto", "código", "codigo"]):
                final_user_content += (
                    "\n\n[DIRETRIZ DE VISÃO - LEITURA E OCR DE TELA]:\n"
                    "Transcreva com fidelidade rigorosa os textos visíveis nas telas (títulos de abas, janelas, menus, mensagens de erro ou código). "
                    "Se foi pedido tradução, traduza fielmente para o Português do Brasil com clareza."
                )

            if search_context_text:
                final_user_content += f"\n\n[DADOS ATUALIZADOS DA WEB EM TEMPO REAL]:\n{search_context_text}\n(Use estas informações para complementar a resposta com cupons, datas ou fatos recentes)."

            # Validação: se o usuário pediu especificamente para ver a tela mas não há imagem de tela no buffer
            if need_screen and not any("tela" in s for s in sources_used):
                reply = "Não consegui capturar sua tela neste momento. Por favor, clique no botão '+ Adicionar Monitor à Caixa' no topo da página para compartilhar seu monitor ou janela comigo, e eu poderei analisar seu wallpaper e ler tudo o que estiver na tela."
                return JSONResponse(content={
                    "reply": reply,
                    "backend": "PIOR Percepção (Aguardando Compartilhamento de Tela)",
                    "latency_ms": int((time.time() - start_time) * 1000),
                    "status": "aguardando_tela"
                })

            if images_b64:
                formatted_messages.append({"role": "user", "content": final_user_content, "images": images_b64})
                reply = await call_ollama(
                    formatted_messages,
                    active_model,
                    num_predict=320 if detail_mode == "direto" else 600,
                    timeout=180
                )
                clean_reply = clean_for_speech(reply)
                latency_ms = int((time.time() - start_time) * 1000)
                return JSONResponse(content={
                    "reply": clean_reply,
                    "backend": f"Ollama Local ({active_model}) - visão ({'+'.join(sources_used)})",
                    "latency_ms": latency_ms,
                    "status": "recebido_e_respondido"
                })
            else:
                formatted_messages.append({"role": "user", "content": final_user_content})

        else:
            # Fluxo puramente textual com busca se necessária
            if web_search.should_trigger_search(user_msg):
                search_results = await asyncio.to_thread(web_search.perform_web_search, user_msg, 4)
                if search_results:
                    context = web_search.format_search_context(search_results)
                    user_msg += f"\n\n[DADOS DA PESQUISA WEB]:\n{context}"

            formatted_messages.append({"role": "user", "content": user_msg})

        reply = await call_ollama(formatted_messages, active_model, num_predict=num_predict, timeout=60)
        clean_reply = clean_for_speech(reply)
        latency_ms = int((time.time() - start_time) * 1000)

        return JSONResponse(content={
            "reply": clean_reply,
            "backend": f"Ollama Local ({active_model})",
            "latency_ms": latency_ms,
            "status": "recebido_e_respondido"
        })

    except Exception as e:
        traceback.print_exc()
        latency_ms = int((time.time() - start_time) * 1000)
        return JSONResponse(content={"error": str(e), "latency_ms": latency_ms}, status_code=500)
