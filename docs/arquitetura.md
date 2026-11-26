# Documentação Técnica e Arquitetura - PIOR

## 1. Visão Geral
O **PIOR** é um assistente multimodal desktop projetado para operar com inteligência artificial local de alta fidelidade (Ollama), eliminando dependências de nuvem para privacidade, rapidez e custo zero.

```
+-----------------------------------------------------------+
|                   Interface Web (HUD Neon)                |
|  - Web Speech API (Voz)    - Canvas / getDisplayMedia     |
+-----------------------------+-----------------------------+
                              | HTTP / JSON / Base64
                              v
+-----------------------------------------------------------+
|                   Backend FastAPI (src/)                  |
|  - main.py: Sensory Perception Hub                        |
|  - vision.py: OpenCV & captura multi-monitor              |
|  - actions.py: E-mails, Calendário (.ics), Arquivos       |
|  - web_search.py: Busca sob demanda e cupons (DDGS)       |
|  - ollama_manager.py: Telemetria de GPU/RAM e troca a quente|
+-----------------------------+-----------------------------+
                              | API REST local (Porta 11434)
                              v
+-----------------------------------------------------------+
|                Ollama Server Local (GPU VRAM)             |
|  - pior-vl:8b (Qwen3-VL 8B Instruct personalizado)        |
+-----------------------------------------------------------+
```

## 2. Componentes Principais
- **Sensory Perception Hub**: Gerencia buffers em memória de múltiplos monitores individuais em Full HD e câmera simultaneamente.
- **Actions Engine**: Suporta conversações de dois turnos para composição de e-mails, emissão de arquivos de calendário `.ics` e notas locais em `documentos_pior/`.
- **Modelfile**: Define hiperparâmetros de inferência (temperatura 0.25, top_p 0.9) e supressão de tokens de pensamento para respostas orais diretas.

## 3. Segurança e Privacidade
- Todos os frames visuais e gravações são processados exclusivamente na máquina do usuário (GPU local).
- Credenciais e segredos protegidos por arquivo `.env` ignorado no versionamento.
