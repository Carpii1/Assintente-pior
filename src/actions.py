"""
Módulo de Ações e Interação com o Sistema do Assistente PIOR.
Implementa:
1. Redação e Gestão Interativa de E-mails com preview em tempo real.
2. Criação de Arquivos locais no computador.
3. Agendamento de Eventos no Calendário (geração de arquivo .ics para Windows Calendar / Outlook / Google).
"""
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

USER_DESKTOP = os.path.join(os.environ.get("USERPROFILE", r"C:\Users\paulo"), "Desktop")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "documentos_pior")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Estado em memória para fluxo interativo de e-mail (por sessão simples)
_EMAIL_FLOW_STATE = {
    "waiting_body": False,
    "recipient": "",
    "subject": ""
}

def check_email_intent(user_msg: str, conversation_history: list) -> Dict[str, Any]:
    """
    Verifica se a mensagem faz parte do fluxo de redação de e-mail.
    Suporta:
    - Início: 'envie um email para fulano', 'redija email para x'
    - Resposta ao corpo: 'o que quer dizer no corpo do email?' -> usuário responde o conteúdo
    """
    global _EMAIL_FLOW_STATE
    msg = user_msg.strip()
    msg_lower = msg.lower()

    # Se estamos aguardando o corpo do e-mail
    if _EMAIL_FLOW_STATE["waiting_body"]:
        recipient = _EMAIL_FLOW_STATE["recipient"]
        subject = _EMAIL_FLOW_STATE["subject"] or "Mensagem importante"
        body_description = msg
        
        # Reseta o estado
        _EMAIL_FLOW_STATE["waiting_body"] = False
        _EMAIL_FLOW_STATE["recipient"] = ""
        _EMAIL_FLOW_STATE["subject"] = ""
        
        return {
            "is_email_action": True,
            "stage": "complete",
            "recipient": recipient,
            "subject": subject,
            "body_description": body_description
        }

    # Verifica se o usuário está iniciando um pedido de e-mail
    email_start_patterns = [
        r"\b(envi|mand|redij|escrev|cri).*(email|e-mail)\b.*(para|a|ao)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-ZÀ-ÿ\s]+)",
        r"\b(email|e-mail)\s+(para|a|ao)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-zA-ZÀ-ÿ\s]+)"
    ]

    for p in email_start_patterns:
        match = re.search(p, msg, re.IGNORECASE)
        if match:
            # Extrai o destinatário
            recipient_candidate = match.group(match.lastindex).strip()
            # Limpa palavras comuns no fim
            recipient_candidate = re.sub(r'[\.\,\?\!]', '', recipient_candidate).strip()
            
            # Verifica se já tem o que dizer no corpo na mesma frase
            body_match = re.search(r"(dizendo que|falando que|com o texto|sobre)\s+(.+)", msg, re.IGNORECASE)
            if body_match:
                return {
                    "is_email_action": True,
                    "stage": "complete",
                    "recipient": recipient_candidate,
                    "subject": f"Assunto: {body_match.group(2)[:30]}...",
                    "body_description": body_match.group(2)
                }

            # Se não disse o corpo, entra no modo de espera
            _EMAIL_FLOW_STATE["waiting_body"] = True
            _EMAIL_FLOW_STATE["recipient"] = recipient_candidate
            _EMAIL_FLOW_STATE["subject"] = f"Contato com {recipient_candidate}"

            return {
                "is_email_action": True,
                "stage": "ask_body",
                "recipient": recipient_candidate
            }

    return {"is_email_action": False}

def create_local_file(filename: str, content: str) -> Dict[str, Any]:
    """Cria um arquivo no computador dentro da pasta de documentos do PIOR."""
    try:
        # Sanitiza nome do arquivo
        clean_name = re.sub(r'[\\/*?:"<>|]', '', filename).strip()
        if not clean_name:
            clean_name = f"documento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        elif not clean_name.endswith(('.txt', '.md', '.py', '.json', '.csv', '.html')):
            clean_name += ".txt"

        filepath = os.path.join(OUTPUT_DIR, clean_name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": True,
            "filename": clean_name,
            "filepath": filepath,
            "size_bytes": len(content.encode("utf-8")),
            "message": f"Arquivo {clean_name} criado com sucesso na pasta documentos."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_calendar_event(title: str, date_str: str = "", time_str: str = "", description: str = "") -> Dict[str, Any]:
    """
    Gera um arquivo de evento .ics universal (compatível com Calendário do Windows, Outlook e Google Calendar).
    """
    try:
        now = datetime.now()
        event_title = title.strip() or "Compromisso Agendado"
        clean_name = re.sub(r'[\\/*?:"<>|]', '_', event_title).strip()[:25]
        filename = f"evento_{clean_name}_{now.strftime('%Y%m%d_%H%M')}.ics"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Horário do evento (padrão: amanhã ou horário especificado)
        start_dt = now + timedelta(days=1)
        if time_str:
            time_match = re.search(r"(\d{1,2})[h:]?(\d{2})?", time_str)
            if time_match:
                hr = int(time_match.group(1))
                mn = int(time_match.group(2)) if time_match.group(2) else 0
                start_dt = start_dt.replace(hour=hr, minute=mn, second=0)

        end_dt = start_dt + timedelta(hours=1)

        dt_format = "%Y%m%dT%H%M%S"
        dt_stamp = now.strftime(dt_format)
        dt_start = start_dt.strftime(dt_format)
        dt_end = end_dt.strftime(dt_format)

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PIOR AI Assistant//Desktop//PT
BEGIN:VEVENT
UID:{now.strftime('%Y%m%d%H%M%S')}@pior.desktop
DTSTAMP:{dt_stamp}
DTSTART:{dt_start}
DTEND:{dt_end}
SUMMARY:{event_title}
DESCRIPTION:{description or 'Evento criado pelo assistente PIOR'}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(ics_content)

        return {
            "success": True,
            "title": event_title,
            "filename": filename,
            "filepath": filepath,
            "start_time": start_dt.strftime("%d/%m/%Y às %H:%M"),
            "message": f"Evento '{event_title}' agendado para {start_dt.strftime('%d/%m/%Y às %H:%M')} e salvo em {filename}."
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_file_creation_intent(msg: str) -> Optional[Dict[str, str]]:
    """Detecta se o usuário pediu criação ou salvamento de arquivo."""
    patterns = [
        r"\b(crie|criar|gere|gerar|salve|salvar|faça|escreva).*(um arquivo|o arquivo|num arquivo|em um arquivo|texto)\b.*(chamado|com o nome|de nome)?\s*([a-zA-Z0-9_\-\.]+)?",
        r"\b(crie um arquivo|salve em arquivo)\b"
    ]
    for p in patterns:
        m = re.search(p, msg, re.IGNORECASE)
        if m:
            filename = m.group(m.lastindex) if m.lastindex and m.group(m.lastindex) else "anotacoes.txt"
            return {"requested": True, "filename": filename}
    return None

def check_calendar_intent(msg: str) -> Optional[Dict[str, str]]:
    """Detecta pedidos de agendamento ou lembretes no calendário."""
    patterns = [
        r"\b(agend|marqu|adicion|cri).*(calendário|calendario|agenda|evento|compromisso|reunião|reuniao)\b",
        r"\b(lembre-me|me lembre|lembrete)\b"
    ]
    for p in patterns:
        if re.search(p, msg, re.IGNORECASE):
            # Extrai título aproximado
            title = re.sub(r'^(agende|marque|crie|adicione|um evento|uma reunião|no calendário|na agenda|para)\s*', '', msg, flags=re.IGNORECASE).strip()
            return {"requested": True, "title": title}
    return None
