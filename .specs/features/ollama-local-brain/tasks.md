# Tasks: Cérebro Local Ollama, Seleção de Modelos e Telemetria

- [x] Task 1: Implementar módulo `src/ollama_manager.py` com ciclo de vida do Ollama (F:\IA\Ollama\Models), carregamento exclusivo (1 modelo por vez), telemetria nvidia-smi e psutil.
- [x] Task 2: Integrar rotas no `src/main.py` (`/api/system_status`, `/api/models`, `/api/model/load`, `/api/model/unload`, `/chat` com Ollama local).
- [x] Task 3: Atualizar `requirements.txt` adicionando `psutil>=6.0.0`.
- [x] Task 4: Atualizar interface web `src/static/index.html` com controles do cérebro (botão Ligar Cérebro, Desligar, seletor de modelos) e telemetria visual em tempo real (GPU VRAM, GPU Util, RAM, Modelo Ativo).
- [x] Task 5: Criar testes automatizados em `tests/test_ollama_manager.py` e rodar bateria de testes via `pytest`.
- [x] Task 6: Executar servidor localmente, verificar carregamento do modelo `qwen3:8b`, telemetria de GPU/RAM e resposta no chat.
