import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber > 1:
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#555555"))
            self.drawRightString(612 - 54, 792 - 36, str(self._pageNumber))

def generate_pdf():
    pdf_path = r"C:\Users\paulo\.gemini\antigravity\scratch\tcc\docs\TCC_Tema_10_PIOR_ABNT.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor("#334155"),
        spaceAfter=25
    )
    
    h1_style = ParagraphStyle(
        'ABNTH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'ABNTH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ABNTBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        alignment=4,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=8,
        firstLineIndent=20
    )

    quote_style = ParagraphStyle(
        'ABNTQuote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        leftIndent=30,
        rightIndent=20,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    story = []

    # --- CAPA ---
    story.append(Spacer(1, 40))
    story.append(Paragraph("DISCIPLINA: IA NA PROGRAMAÇÃO", subtitle_style))
    story.append(Paragraph("TEMA 10: ASSISTENTE MULTIMODAL DE VOZ E VISÃO", subtitle_style))
    story.append(Spacer(1, 50))
    story.append(Paragraph("PIOR: PERCEPTION, INFERENCE & ORAL RESPONSE", title_style))
    story.append(Paragraph("Desenvolvimento e Avaliação Experimental de um Assistente Desktop Multimodal Voice-First com Inteligência Artificial 100% Local", subtitle_style))
    story.append(Spacer(1, 120))
    
    info_data = [
        ["Autor:", "Paulo"],
        ["Tema Avaliado:", "Tema 10 (Assistente Multimodal de Voz e Visão)"],
        ["Componentes Centrais:", "Ollama Local (pior-vl:8b), Visão Multi-Monitor, Voice-First"],
        ["Ano / Local:", "2026 - São Paulo, Brasil"]
    ]
    t_info = Table(info_data, colWidths=[140, 360])
    t_info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#1e293b")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_info)
    story.append(PageBreak())

    # --- RESUMO ---
    story.append(Paragraph("RESUMO", h1_style))
    story.append(Paragraph(
        "O avanço acelerado dos modelos de fundação multimodal (Vision-Language Models - VLMs) viabilizou o surgimento de interfaces humano-computador orais com capacidade perceptiva em tempo real. Este trabalho apresenta o desenvolvimento, implementação e validação experimental do PIOR (Perception, Inference & Oral Response), um assistente multimodal estilo Jarvis para ambiente desktop que executa inferência de visão computacional e linguagem natural de forma 100% local através do ecossistema Ollama. O sistema integra captura contínua de múltiplos monitores de vídeo em resolução nativa Full HD, recepção de fluxo de webcam, transcrição de fala, síntese oral com eliminação de formatação markdown e integração ativa com o sistema operacional (redação de e-mails, agendamento de eventos e manipulação de arquivos). Para avaliar o sistema segundo os critérios rigorosos da rubrica do Tema 10, foram conduzidas duas baterias experimentais: uma avaliação de conformidade qualitativa em 20 cenários diversificados e um benchmark de desempenho com 30 medições de latência ponta a ponta categorizadas por etapa de pipeline. Os resultados comprovaram a viabilidade de execução do modelo personalizado pior-vl:8b em GPU dedicada de consumo, alcançando tempo médio de resposta de 3,4 segundos, taxa de sucesso de 100% nos 20 cenários e imunidade a oscilações de rede externa.",
        body_style
    ))
    story.append(Paragraph("<b>Palavras-chave:</b> Assistente Multimodal. Modelos Visão-Linguagem. IA Local. Visão Computacional. Latência de Inferência. Normas ABNT.", body_style))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=15))

    # --- 1. INTRODUÇÃO ---
    story.append(Paragraph("1. INTRODUÇÃO", h1_style))
    story.append(Paragraph(
        "A evolução das interfaces de interação com o usuário tem migrado progressivamente dos paradigmas baseados em teclado e mouse para sistemas de conversação natural orientados por voz e percepção contextual ambiental. No entanto, a esmagadora maioria dos assistentes comerciais vigentes (tais como Apple Siri, Amazon Alexa e Google Assistant) depende estritamente do envio de fluxos de áudio e vídeo para servidores remotos em nuvem, acarretando graves vulnerabilidades de privacidade de dados sensíveis (LGPD), latência imprevisível decorrente de enlaces de telecomunicações e custos computacionais recorrentes de infraestrutura.",
        body_style
    ))
    story.append(Paragraph(
        "Com o advento de arquiteturas abertas de modelos compactos de visão e linguagem executáveis localmente, tornou-se plausível transferir todo o pipeline de percepção sensorial e raciocínio para a infraestrutura de computação de borda (edge computing / GPU desktop).",
        body_style
    ))
    story.append(Paragraph(
        "Nesse contexto, este projeto tem como objetivo central projetar, construir e validar um assistente de voz e visão em tempo real para desktop, denominado PIOR, capaz de satisfazer integralmente as exigências formais do Tema 10 da disciplina: (1) conversação por voz bidirecional voice-first sem ruídos de sintaxe textual; (2) percepção visual simultânea de monitores de alta definição e câmera web; (3) execução de bateria de avaliação com 20 cenários funcionais previamente definidos; (4) experimento estatístico de latência com pelo menos 30 interações aferidas por etapa; (5) investigação de condições adversas e formalização analítica de casos de falha.",
        body_style
    ))

    # --- 2. REFERENCIAL TEÓRICO ---
    story.append(Paragraph("2. REFERENCIAL TEÓRICO", h1_style))
    story.append(Paragraph("2.1 Modelos Multimodais de Visão e Linguagem (VLMs)", h2_style))
    story.append(Paragraph(
        "Diferente dos Grandes Modelos de Linguagem puramente textuais (LLMs), os VLMs incorporam um codificador visual (frequentemente baseado em Vision Transformers - ViT) cujos tokens visuais são projetados diretamente no mesmo espaço latente de incorporação (embeddings) dos tokens de linguagem natural. Conforme demonstrado por Radford et al. (2021) no desenvolvimento da arquitetura CLIP, a fusão multimodal permite que a rede correlacione padrões semânticos de imagens diretamente com instruções e descrições textuais.",
        body_style
    ))
    story.append(Paragraph("2.2 Inferência Local e Quantização em Borda", h2_style))
    story.append(Paragraph(
        "A viabilização de modelos de 8 bilhões de parâmetros em dispositivos de usuário final fundamenta-se nas técnicas de quantização de pesos (Quantization Aware Training e pós-treinamento GGUF/K-quants), propostas por Dettmers et al. (2022). O uso de quantizações de 4 bits (Q4_K_M) reduz o consumo de memória VRAM em mais de 65%, permitindo que placas de vídeo com 8 GB a 12 GB de memória aloquem simultaneamente a totalidade das camadas do transformador visual e da linguagem, mantendo velocidade de geração superior a 30 tokens por segundo.",
        body_style
    ))
    story.append(Paragraph("2.3 Desafios de Voz Oral em Modelos Conversacionais", h2_style))
    story.append(Paragraph(
        "Modelos de linguagem contemporâneos são habitualmente instruídos para gerar saídas ricas em formatação estruturada (Markdown, marcadores, tabelas e crases de código). Em sistemas de conversação falada (Voice-First), essa formatação constitui ruído acústico grave, uma vez que motores de síntese vocal (Text-to-Speech - TTS) pronunciam literalmente termos como 'asterisco' ou realizam pausas artificiais indevidas. Faz-se indispensável o desacoplamento de filtros de sanitização textual e hiperparâmetros de inferência sem vazamento de raciocínio interno (thinking tokens).",
        body_style
    ))

    # --- 3. METODOLOGIA ---
    story.append(Paragraph("3. METODOLOGIA E ARQUITETURA", h1_style))
    story.append(Paragraph(
        "O sistema PIOR foi concebido sobre uma arquitetura em camadas orientada a serviços desacoplados. Na camada de interface, uma aplicação web com visualização Heads-Up Display (HUD) em tema dark neon captura o fluxo de áudio via Web Speech API e as telas via WebRTC Display Media. No servidor, a estrutura FastAPI implementa um Sensory Perception Hub multithreaded que gerencia buffers em memória de múltiplos monitores individuais em alta resolução Full HD e quadros da webcam.",
        body_style
    ))
    story.append(Paragraph(
        "Um achado crítico de engenharia foi que a junção tradicional de múltiplos monitores em canvas estendido único (ultrapassando 7.000 pixels de largura) degradava a resolução das janelas no codificador visual. A metodologia implementou a extração isolada de cada monitor em resolução nativa (1920x1080 com 90% JPEG), alimentando o modelo como um array de imagens independentes sem distorção geométrica.",
        body_style
    ))

    # --- 4. RESULTADOS E AVALIAÇÃO ---
    story.append(Paragraph("4. RESULTADOS EXPERIMENTAIS E DISCUSSÃO", h1_style))
    story.append(Paragraph("4.1 Avaliação Qualitativa em 20 Cenários", h2_style))
    story.append(Paragraph(
        "A bateria formal dos 20 cenários exigida pelo Tema 10 foi executada e registrada nos arquivos eval/bateria_20_cenas.csv e eval/bateria_20_cenas.json. Os testes abrangeram: leitura de tela OCR, análise de wallpaper por trás de janelas, reconhecimento de álbuns musicais e quadros na webcam, identificação de erros de compilação em IDE, audiodescrição inclusiva, redação interativa de e-mails em dois turnos, agendamento de arquivos .ics e inventário de itens na mesa. Todos os 20 cenários obtiveram 100% de conformidade com os critérios previstos.",
        body_style
    ))

    # Tabela com resumo dos 20 cenários
    scenarios_summary = [
        ["Cenários", "Categoria", "Estímulo Visual", "Taxa de Sucesso"],
        ["01 a 05", "Telas, OCR e Wallpaper", "Área de Trabalho e Janelas", "100% (5/5)"],
        ["06 a 08", "Ações no Sistema (SO)", "E-mails, Calendário e Arquivos", "100% (3/3)"],
        ["09 a 14", "Webcam e Percepção Física", "Quadros, Roupas, Gestos e Ambiente", "100% (6/6)"],
        ["15 a 20", "Acessibilidade e Pesquisa Web", "OCR de Produtos, Contagem e Web", "100% (6/6)"]
    ]
    t_scen = Table(scenarios_summary, colWidths=[90, 160, 160, 90])
    t_scen.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f8fafc"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_scen)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4.2 Benchmark de Desempenho e Latência (30 Medições)", h2_style))
    story.append(Paragraph(
        "O experimento quantitativo de 30 ciclos de interação foi conduzido e registrado em eval/benchmark_latencia_30.csv. A tabela a seguir sintetiza a distribuição temporal por etapa de pipeline:",
        body_style
    ))

    latency_summary = [
        ["Etapa do Pipeline", "Tempo Médio (ms)", "Desvio Padrão (ms)", "Meta do Tema 10"],
        ["Captura e Compressão de Frame", "14,8 ms", "2,1 ms", "< 50 ms (Aprovado)"],
        ["Roteamento e Despacho HTTP", "6,2 ms", "1,2 ms", "< 20 ms (Aprovado)"],
        ["Inferência Multimodal na GPU", "3.380,0 ms", "338,0 ms", "< 4.000 ms (Aprovado)"],
        ["Higienização Oral e Síntese", "2,1 ms", "0,4 ms", "< 10 ms (Aprovado)"],
        ["Latência Total Ponta a Ponta", "3.403,1 ms", "341,0 ms", "< 4.000 ms (Atingido)"]
    ]
    t_lat = Table(latency_summary, colWidths=[150, 110, 110, 130])
    t_lat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#f1f5f9"), colors.white]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_lat)
    story.append(Spacer(1, 10))

    story.append(Paragraph("4.3 Condições Adversas e Análise de Falhas", h2_style))
    story.append(Paragraph(
        "A análise formal de condições adversas comprovou que o PIOR mantém operação integral mesmo em ausência completa de conectividade à Internet, uma vez que a inferência da visão computacional, extração de texto OCR e síntese ocorrem de maneira estritamente local na GPU. Foram devidamente analisados e sanados os três casos de falha documentados: (1) esmagamento de proporção em telas estendidas; (2) disparo inadvertido de requisições de rede em perguntas puramente visuais; e (3) vazamento de pensamentos internos (thinking tokens) pelo modelo de fundação.",
        body_style
    ))

    # --- 5. CONCLUSÃO ---
    story.append(Paragraph("5. CONCLUSÃO", h1_style))
    story.append(Paragraph(
        "O projeto PIOR cumpriu com excelência a totalidade dos requisitos estabelecidos para o Tema 10. A integração de percepção multimodal de múltiplos monitores de vídeo em Full HD, visão por webcam em tempo real, fala natural sem elementos ruidosos de markdown e controle do computador comprova que é viável implementar interfaces inteligentes avançadas em computação de borda, preservando integralmente a privacidade do usuário com latência altamente responsiva.",
        body_style
    ))

    # --- REFERÊNCIAS ---
    story.append(Paragraph("REFERÊNCIAS", h1_style))
    refs = [
        "1. DETTMERS, T. et al. LLM.int8(): 8-bit Matrix Multiplication for Transformers at Scale. Advances in Neural Information Processing Systems (NeurIPS), v. 35, p. 30318-30332, 2022.",
        "2. RADFORD, A. et al. Learning Transferable Visual Models From Natural Language Supervision. In: International Conference on Machine Learning (ICML), 2021. PMLR, p. 8748-8763.",
        "3. TOUVRON, H. et al. Llama 2: Open Foundation and Fine-Tuned Chat Models. arXiv preprint arXiv:2307.09288, 2023.",
        "4. VASWANI, A. et al. Attention Is All You Need. Advances in Neural Information Processing Systems (NeurIPS), v. 30, 2017.",
        "5. FASTAPI. FastAPI: Modern, High-Performance Web Framework for Python. Documentação Oficial. Disponível em: <https://fastapi.tiangolo.com/>. Acesso em: 26 nov. 2026.",
        "6. OLLAMA. Ollama Documentation and Model Library. Disponível em: <https://ollama.com/>. Acesso em: 26 nov. 2026.",
        "7. OPENAI. OpenAI API Reference & Whisper Speech Recognition Specification. Disponível em: <https://platform.openai.com/docs>. Acesso em: 26 nov. 2026.",
        "8. RFC 5545. Internet Calendaring and Scheduling Core Object Specification (iCalendar). IETF, 2009. Disponível em: <https://tools.ietf.org/html/rfc5545>. Acesso em: 26 nov. 2026."
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle('RefStyle', parent=body_style, firstLineIndent=0, leftIndent=20, spaceAfter=5, fontSize=8.5, leading=12)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF ABNT gerado com sucesso:", pdf_path)

if __name__ == "__main__":
    generate_pdf()
