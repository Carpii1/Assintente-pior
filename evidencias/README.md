# Índice de Evidências Experimentais - TCC Tema 10 (PIOR)

Este diretório reúne as evidências obrigatórias exigidas pela rubrica de avaliação do projeto.

---

## 1. Avaliação Experimental (20 Cenários)
- **Arquivo CSV**: [`eval/bateria_20_cenas.csv`](../eval/bateria_20_cenas.csv)
- **Arquivo JSON**: [`eval/bateria_20_cenas.json`](../eval/bateria_20_cenas.json)
- **Script de Execução**: [`eval/bateria_20_cenas.py`](../eval/bateria_20_cenas.py)
- **Resumo**: 20 casos de testes executados abrangendo OCR, wallpapers, webcam, álbuns de música, lojas e ações no sistema. Taxa de sucesso: **100%**.

---

## 2. Experimento de Latência (30 Medições)
- **Arquivo CSV**: [`eval/benchmark_latencia_30.csv`](../eval/benchmark_latencia_30.csv)
- **Arquivo JSON**: [`eval/benchmark_latencia_30.json`](../eval/benchmark_latencia_30.json)
- **Script de Benchmark**: [`eval/benchmark_latencia.py`](../eval/benchmark_latencia.py)
- **Etapas Medidas**:
  1. Captura e codificação do frame (tela/webcam): ~15ms
  2. Pré-processamento e despacho HTTP: ~8ms
  3. Inferência do modelo local (`pior-vl:8b` na GPU): ~1800ms - 3800ms
  4. Pós-processamento e higienização de voz: ~2ms
  5. Latência total ponta a ponta: **Meta < 4000ms atingida**.

---

## 3. Teste em Condições Adversas
- **Ruído de Fundo**: Documentado o comportamento do sintetizador e do reconhecimento sob ruído acústico ambiente.
- **Rede Lenta**: Como o cérebro principal roda 100% local no Ollama (offline), a latência do assistente é imune a oscilações de rede externa, exceto quando a busca de cupons DuckDuckGo é acionada.

---

## 4. Análise dos Casos de Falha
1. **Falha 1 - Distorção Panorâmica de Monitores**: Aspect ratio de múltiplos monitores (6420x1080) esmagava textos. *Solução*: Envio de telas individuais em Full HD nativo (0.90 JPEG).
2. **Falha 2 - Disparo Inadvertido de Busca Web**: Perguntas de tela acionavam DuckDuckGo desnecessariamente. *Solução*: Desacoplamento da busca web para perguntas puramente visuais.
3. **Falha 3 - Thinking Leak no Modelo**: O modelo emitia pensamentos internos em inglês. *Solução*: Criação do `pior-vl:8b` via `Modelfile` com parâmetros de parada `<think>` e temperatura 0.25.

---

## 5. Demonstração em Vídeo
- Roteiro e vídeo de 3 a 5 minutos demonstrando a inicialização com Docker/Local, comando por voz, leitura de tela, cupons e a bateria dos 20 cenários.
