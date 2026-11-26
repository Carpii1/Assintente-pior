# Spec: Cérebro Local Ollama com Seleção de Modelos (8b, 14b, 32b) e Telemetria GPU/RAM

## 1. Visão Geral
Migração completa do assistente PIOR do uso de APIs externas (Groq) para inferência 100% local executada via Ollama com modelos armazenados no disco `F:\IA\Ollama\Models`. Inclusão de controle de ciclo de vida do modelo ("Ligar o Cérebro"), seletor de modelos (8b, 14b e 32b com garantia de apenas um modelo ativo por vez) e painel em tempo real de telemetria de VRAM/GPU (nvidia-smi) e RAM do sistema.

## 2. Requisitos em Notação EARS

- **REQ-01 (Ubiquitous - Motor Local):**
  O sistema SHALL utilizar a instância local do Ollama (`http://127.0.0.1:11434`) com a variável de ambiente `OLLAMA_MODELS=F:\IA\Ollama\Models` para todas as inferências conversacionais do PIOR, sem dependência de chaves ou chamadas de API externas da Groq.

- **REQ-02 (State-driven - Modelo Padrão no Início):**
  WHILE o botão "Ligar o Cérebro" for acionado pela primeira vez, o sistema SHALL carregar na memória o modelo de menor contagem de parâmetros (`qwen3:8b`).

- **REQ-03 (Event-driven - Troca de Modelos com Unload Exclusivo):**
  WHEN o usuário selecionar um modelo diferente (`qwen3:8b`, `qwen3:14b` ou `qwen3-vl:32b`), o sistema SHALL descarregar imediatamente da memória o modelo anterior (`keep_alive: 0`) e pré-carregar na VRAM exclusivamente o modelo selecionado (`keep_alive: "60m"`), garantindo que apenas um modelo permaneça ativo na GPU por vez.

- **REQ-04 (Ubiquitous - Telemetria em Tempo Real):**
  O sistema SHALL fornecer um endpoint `/api/system_status` que retorne dados consolidados de:
  - `nvidia-smi`: Nome da GPU, VRAM Total (MB), VRAM Usada (MB), VRAM Livre (MB), Utilização da GPU (%) e Temperatura (°C).
  - RAM do Sistema: RAM Total (GB), RAM Usada (GB) e Porcentagem de Uso (%).
  - `ollama ps`: Modelo atualmente carregado na VRAM, tamanho em VRAM e expiração.

- **REQ-05 (Event-driven - Desligamento do Cérebro):**
  WHEN o usuário clicar em "Desligar Cérebro", o sistema SHALL descarregar todos os modelos da VRAM (`keep_alive: 0`) e atualizar o status para descarregado/ocioso.

- **REQ-06 (Ubiquitous - Interface Visual):**
  A interface web SHALL exibir os seletores de modelo (8B, 14B, 32B), os botões de controle de inicialização do cérebro, e os medidores visuais de VRAM e RAM atualizados a cada 2 a 3 segundos.

- **REQ-07 (Unwanted - Tratamento de Erros e Ollama Inativo):**
  IF o serviço Ollama não estiver em execução ao solicitar uma operação, THEN o backend SHALL automaticamente tentar inicializar o processo do Ollama com `OLLAMA_MODELS=F:\IA\Ollama\Models` e aguardar sua prontidão antes de falhar com mensagem amigável.

## 3. Critérios de Aceitação e Verificação
1. Inicialização do Ollama apontando para `F:\IA\Ollama\Models` detecta `qwen3:8b`, `qwen3:14b` e `qwen3-vl:32b`.
2. Endpoint `/api/models` lista os modelos instalados no disco F:.
3. Endpoint `/api/model/load` carrega um modelo por vez e descarrega os demais.
4. Endpoint `/api/model/unload` descarrega o modelo ativo.
5. Endpoint `/api/system_status` retorna métricas de `nvidia-smi` e memória RAM.
6. Endpoint `/chat` responde usando a LLM local em execução sem chamar Groq.
