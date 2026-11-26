# Plano do Projeto Pior

## Visão geral
Este plano descreve as atividades, marcos e entregas para o desenvolvimento do **assistente multimodal "Pior"**, inspirado no conceito de Jarvis. Como o grupo será composto por um único integrante (você), todas as responsabilidades (dados, backend, IA e produto) permanecem com o mesmo desenvolvedor.

## Cronograma (adaptado dos marcos da disciplina)
| Data | Marco | Atividade principal |
|------|-------|----------------------|
| **17/10** | Início | Criação do repositório, definição da arquitetura e do escopo do assistente. |
| **24/10** | Marco 1 | **Proposta técnica** (1‑2 páginas) – descrição do problema, arquitetura proposta, métricas de sucesso. Configuração inicial do CI (GitHub Actions) e commit inicial. |
| **07/11** | Marco 2 | **Protótipo funcional** – API FastAPI com endpoints básicos, integração do modelo de voz (Whisper) e de reconhecimento de imagem (Moondream2). Dockerfile e `docker-compose.yml` funcionando. |
| **14/11** | Marco 3 | **MVP completo** – implementação das funcionalidades de controle de computador (abrir programas, ler arquivos), interface web (Streamlit ou React simples) e documentação preliminar (README ampliado, `docs/`). |
| **21/11** | Marco 4 | **Avaliação experimental** – scripts de benchmark (latência, acurácia), geração de relatórios em `eval/`, coleta de evidências (vídeo, logs). Finalização da documentação técnica e início do trabalho de pesquisa (ABNT). |
| **28/11** | Demonstração | Apresentação rápida em aula, ajustes finais com base no feedback. |
| **30/11 – 02/12** | Entrega final | Tag `v1.0`, público ou privado com professor como colaborador, entrega de todos os artefatos (código, evidências, documentação, trabalho de pesquisa). |

## Papéis (único desenvolvedor)
- **Dados e Qualidade** – Curadoria de datasets sintéticos, criação de testes automatizados.
- **Backend e Infraestrutura** – API FastAPI, Docker, CI/CD.
- **IA e Avaliação** – Integração dos modelos locais (Whisper, Moondream2, Piper), definição de métricas e scripts de avaliação.
- **Produto e Interface** – UI web (Streamlit), documentação, vídeo demo.

## Próximas tarefas imediatas
1. **Inicializar o repositório** – execute `init_repo.bat`.
2. **Escrever a proposta técnica** (arquivo `Proposta_Tecnica.md`).
3. **Implementar o endpoint `/health`** (já disponível) e iniciar a integração do modelo Whisper.
4. **Adicionar testes** em `tests/` para cobrir os novos endpoints.

> **Observação:** Todos os arquivos do projeto encontram‑se em `C:\Users\paulo\.gemini\antigravity\scratch\tcc`.
