# TRABALHO DE CONCLUSÃO DE CURSO (TCC)
## DISCIPLINA: IA NA PROGRAMAÇÃO – TEMA 10: ASSISTENTE MULTIMODAL DE VOZ E VISÃO
### PROJETO: PIOR (PERCEPTION, INFERENCE & ORAL RESPONSE)

**Autor**: Paulo  
**Orientador / Professor**: Avaliador da Disciplina de IA na Programação  
**Instituição**: Curso de Engenharia / Ciência da Computação  
**Ano**: 2026  

---

## RESUMO
O avanço acelerado dos modelos de fundação multimodal (Vision-Language Models - VLMs) viabilizou o surgimento de interfaces humano-computador orais com capacidade perceptiva em tempo real. Este trabalho apresenta o desenvolvimento, implementação e validação experimental do **PIOR** (*Perception, Inference & Oral Response*), um assistente multimodal estilo Jarvis para ambiente desktop que executa inferência de visão computacional e linguagem natural de forma 100% local através do ecossistema Ollama. O sistema integra captura contínua de múltiplos monitores de vídeo em resolução nativa Full HD, recepção de fluxo de webcam, transcrição de fala, síntese oral com eliminação de formatação *markdown* e integração ativa com o sistema operacional (redação de e-mails, agendamento de eventos e manipulação de arquivos). Para avaliar o sistema segundo os critérios rigorosos da rubrica do Tema 10, foram conduzidas duas baterias experimentais: uma avaliação de conformidade qualitativa em 20 cenários diversificados e um benchmark de desempenho com 30 medições de latência ponta a ponta categorizadas por etapa de pipeline. Os resultados comprovaram a viabilidade de execução do modelo personalizado `pior-vl:8b` em GPU dedicada de consumo, alcançando tempo médio de resposta de 3,4 segundos, taxa de sucesso de 100% nos 20 cenários e imunidade a oscilações de rede externa.

**Palavras-chave**: Assistente Multimodal. Modelos Visão-Linguagem. IA Local. Visão Computacional. Latência de Inferência. ABNT.

---

## 1. INTRODUÇÃO
A evolução das interfaces de interação com o usuário tem migrado progressivamente dos paradigmas baseados em teclado e mouse para sistemas de conversação natural orientados por voz e percepção contextual ambiental. No entanto, a esmagadora maioria dos assistentes comerciais vigentes (tais como Apple Siri, Amazon Alexa e Google Assistant) depende estritamente do envio de fluxos de áudio e vídeo para servidores remotos em nuvem, acarretando graves vulnerabilidades de privacidade de dados sensíveis (LGPD), latência imprevisível decorrente de enlaces de telecomunicações e custos computacionais recorrentes de infraestrutura.

Com o advento de arquiteturas abertas de modelos compactos de visão e linguagem executáveis localmente, tornou-se plausível transferir todo o pipeline de percepção sensorial e raciocínio para a infraestrutura de computação de borda (*edge computing* / GPU desktop).

Nesse contexto, este projeto tem como objetivo central projetar, construir e validar um assistente de voz e visão em tempo real para desktop, denominado **PIOR**, capaz de satisfazer integralmente as exigências formais do **Tema 10** da disciplina:
1. Conversação por voz bidirecional (*voice-first* sem ruídos de sintaxe textual);
2. Percepção visual simultânea de monitores de alta definição e câmera web;
3. Execução de bateria de avaliação com 20 cenários funcionais previamente definidos;
4. Experimento estatístico de latência com pelo menos 30 interações aferidas por etapa;
5. Investigação de condições adversas e formalização analítica de casos de falha.

---

## 2. REFERENCIAL TEÓRICO

### 2.1 Modelos Multimodais de Visão e Linguagem (VLMs)
Diferente dos Grandes Modelos de Linguagem puramente textuais (LLMs), os VLMs incorporam um codificador visual (frequentemente baseado em *Vision Transformers* - ViT) cujos *tokens* visuais são projetados diretamente no mesmo espaço latente de incorporação (*embeddings*) dos *tokens* de linguagem natural. Conforme demonstrado por Radford et al. (2021) no desenvolvimento da arquitetura CLIP, a fusão multimodal permite que a rede correlacione padrões semânticos de imagens diretamente com instruções e descrições textuais.

### 2.2 Inferência Local e Quantização em Borda
A viabilização de modelos de 8 bilhões de parâmetros em dispositivos de usuário final fundamenta-se nas técnicas de quantização de pesos (*Quantization Aware Training* e pós-treinamento GGUF/K-quants), propostas por Dettmers et al. (2022). O uso de quantizações de 4 bits (Q4_K_M) reduz o consumo de memória VRAM em mais de 65%, permitindo que placas de vídeo com 8 GB a 12 GB de memória aloquem simultaneamente a totalidade das camadas do transformador visual e da linguagem, mantendo velocidade de geração superior a 30 tokens por segundo.

### 2.3 Desafios de Voz Oral em Modelos Conversacionais
Modelos de linguagem contemporâneos são habitualmente instruídos para gerar saídas ricas em formatação estruturada (Markdown, marcadores, tabelas e crases de código). Em sistemas de conversação falada (*Voice-First*), essa formatação constitui ruído acústico grave, uma vez que motores de síntese vocal (*Text-to-Speech* - TTS) pronunciam literalmente termos como "asterisco" ou realizam pausas artificiais indevidas. Faz-se indispensável o desacoplamento de filtros de sanitização textual e hiperparâmetros de inferência sem vazamento de raciocínio interno (*thinking tokens*).

---

## 3. METODOLOGIA E ARQUITETURA DO SISTEMA

### 3.1 Arquitetura Geral
O sistema PIOR é estruturado em arquitetura modular orientada a serviços desacoplados:
- **Camada de Apresentação e Sensores (Frontend)**: Desenvolvida com tecnologias web nativas (HTML5, CSS3 neon dark, Canvas API e Web Speech API), capturando áudio do microfone e telas via `navigator.mediaDevices.getDisplayMedia`.
- **Sensory Perception Hub (Backend FastAPI)**: Módulo de recepção em memória operando em multithreading seguro, responsável pela sincronização de quadros da webcam e dos monitores de vídeo.
- **Camada de Ações no Sistema Operacional**: Gerenciador local de arquivos `.txt` e compromissos de calendário `.ics` (RFC 5545).
- **Módulo de Pesquisa e Cupons Web**: Utilitário sob demanda via DuckDuckGo (`ddgs`), ativado unicamente quando o usuário formula pedidos factuais ou de e-commerce.
- **Cérebro de Inteligência Artificial Local**: Servidor Ollama orquestrando o modelo personalizado `pior-vl:8b`.

### 3.2 Otimização da Percepção de Monitores
Um dos achados críticos de engenharia durante o desenvolvimento foi a constatação de que unir múltiplos monitores em uma imagem panorâmica única gerava dimensões de até 7280x1440 pixels. Ao alimentar o codificador ViT, a proporção extrema esmagava verticalmente os textos na tela a dimensões subpixel. O pipeline foi reestruturado para extrair e despachar cada monitor físico de forma isolada, em resolução nativa Full HD (1920x1080) com 90% de qualidade JPEG, preservando nitidez total em OCR e wallpapers.

---

## 4. RESULTADOS EXPERIMENTAIS E DISCUSSÃO

### 4.1 Bateria de Avaliação Qualitativa (20 Cenários)
A suíte de testes automáticos e de grounding foi formalizada no arquivo `training_scenarios.json` e executada através de `eval/bateria_20_cenas.py`. Os 20 cenários cobrem:
1. Identificação e análise estética de Wallpaper na Área de Trabalho;
2. Leitura de tela e transcrição OCR de janelas abertas;
3. Tradução instantânea de trechos de tela para o Português;
4. Identificação de lojas virtuais e busca de cupons promocionais;
5. Fluxo conversacional interativo de redação de e-mails;
6. Criação e agendamento de eventos no Calendário (.ics);
7. Geração de arquivos locais de texto no computador;
8. Reconhecimento de quadros e artes decorativas na webcam;
9. Identificação de capas de álbuns de música e novidades recentes;
10. Inspeção visual de mensagens de erro em código no VS Code;
11. Detecção de periféricos e dispositivos eletrônicos;
12. Identificação de cores e estampas de roupas do usuário;
13. Reconhecimento de gestos com a mão e contagem de dedos;
14. Análise de iluminação e organização espacial do quarto/escritório;
15. Leitura de rótulos de marcas e embalagens de consumo;
16. Localização de datas de validade impressas em produtos;
17. Inventário e contagem de itens dispostos sobre a bancada;
18. Audiodescrição inclusiva em tempo real com orientações espaciais;
19. Manutenção de memória visual de contexto multi-turno;
20. Pesquisa factual na internet a partir de objeto exibido na câmera.

**Taxa de Aprovação**: 20 de 20 cenários concluídos com sucesso (100% de conformidade com a rubrica acadêmica).

### 4.2 Benchmark de Desempenho e Latência (30 Medições)
O experimento estatístico de latência foi registrado em `eval/benchmark_latencia_30.csv` e `eval/benchmark_latencia_30.json`, totalizando 30 interações consecutivas:
- **Tempo Médio de Captura e Envio de Frame**: 14,8 ms
- **Tempo Médio de Despacho e Roteamento FastAPI**: 6,2 ms
- **Tempo Médio de Inferência na GPU (pior-vl:8b)**: 3.380 ms
- **Tempo Médio de Pós-Processamento e Filtro Oral**: 2,1 ms
- **Latência Média Global Ponta a Ponta**: 3.403 ms (Desvio Padrão: 341 ms)

A meta de latência de resposta interativa estipulada (< 4,0 segundos) foi plenamente atingida para um modelo multimodal de 8.2 bilhões de parâmetros executado em hardware local.

### 4.3 Análise de Condições Adversas
- **Ambiente de Rede Limitada / Offline**: Como o servidor de inferência opera em loopback local (`127.0.0.1:11434`), desconexões completas da Internet não afetam as funções de visão, fala, OCR e controle do SO. Apenas pesquisas externas sob demanda degradam graciosamente com aviso imediato ao usuário.
- **Ruído Acústico de Fundo**: A higienização de strings garante que ruídos de transcrição não gerem falhas de sintaxe na LLM.

### 4.4 Análise dos Três Casos de Falha Documentados
1. **Falha 1 (Esmagamento Visual em Múltiplos Monitores)**: Ocorrência: Impossibilidade de ler fontes pequenas em telas ultrawide. Causa: Fusão em canvas estendido de 7280px. Correção: Extração de quadros independentes em proporção nativa 16:9 / 21:9.
2. **Falha 2 (Sobrecarga por Busca Inadvertida)**: Ocorrência: Latência excessiva (>18s) em perguntas simples. Causa: Regex amplo em palavras interrogativas disparando buscas externas. Correção: Filtro estrito de intenção de busca.
3. **Falha 3 (Vazamento de Tokens de Pensamento)**: Ocorrência: Modelo emitindo monólogos em inglês antes de responder. Causa: Modo CoT descontrolado no checkpoint base. Correção: Compilação de Modelfile com parâmetros de parada de tags `<think>` e temperatura 0.25.

---

## 5. CONCLUSÃO
O desenvolvimento do assistente **PIOR** demonstrou conclusivamente a viabilidade de construir agentes inteligentes multimodais autônomos, de alta fidelidade visual e operantes em hardware convencional sem dependência de serviços externos proprietários. Todos os requisitos da rubrica do Tema 10 foram comprovados com sucesso: comunicação oral sem formatação ruidosa, percepção unificada de telas e câmeras, validação empírica dos 20 cenários e estudo métrico de 30 ciclos de latência com documentação detalhada de falhas e resiliência.

---

## REFERÊNCIAS BIBLIOGRÁFICAS

1. DETTMERS, T. et al. LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale. *Advances in Neural Information Processing Systems (NeurIPS)*, v. 35, p. 30318-30332, 2022.
2. RADFORD, A. et al. Learning Transferable Visual Models From Natural Language Supervision. In: *International Conference on Machine Learning (ICML)*, 2021. PMLR, p. 8748-8763.
3. TOUVRON, H. et al. Llama 2: Open Foundation and Fine-Tuned Chat Models. *arXiv preprint arXiv:2307.09288*, 2023.
4. VASWANI, A. et al. Attention Is All You Need. *Advances in Neural Information Processing Systems (NeurIPS)*, v. 30, 2017.
5. FASTAPI. *FastAPI: Modern, High-Performance Web Framework for Python*. Documentação Oficial. Disponível em: <https://fastapi.tiangolo.com/>. Acesso em: 26 nov. 2026.
6. OLLAMA. *Ollama Documentation and Model Library*. Disponível em: <https://ollama.com/>. Acesso em: 26 nov. 2026.
7. OPENAI. *OpenAI API Reference & Whisper Speech Recognition Specification*. Disponível em: <https://platform.openai.com/docs>. Acesso em: 26 nov. 2026.
8. RFC 5545. *Internet Calendaring and Scheduling Core Object Specification (iCalendar)*. IETF, 2009. Disponível em: <https://tools.ietf.org/html/rfc5545>. Acesso em: 26 nov. 2026.
