import os
import json
import csv
import time
import requests

SERVER_URL = "http://127.0.0.1:8000"

BENCHMARK_SCENES = [
    {"id": 1, "tipo": "conhecimento_geral", "pergunta": "Qual é a capital do Brasil?", "resposta_esperada": "brasília"},
    {"id": 2, "tipo": "matematica", "pergunta": "Quanto é 15 somado com 27?", "resposta_esperada": "42"},
    {"id": 3, "tipo": "programacao", "pergunta": "Qual função em Python imprime texto na tela?", "resposta_esperada": "print"},
    {"id": 4, "tipo": "ciencia", "pergunta": "Qual é a fórmula da água?", "resposta_esperada": "h2o"},
    {"id": 5, "tipo": "nome_proprio", "pergunta": "Pior, qual é o seu nome oficial?", "resposta_esperada": "pior"},
    {"id": 6, "tipo": "distincao_adjetivo", "pergunta": "Qual é o pior erro de sintaxe do Python?", "resposta_esperada": "syntaxerror"},
    {"id": 7, "tipo": "logica", "pergunta": "Se um triângulo tem três lados, quantos tem um quadrado?", "resposta_esperada": "quatro"},
    {"id": 8, "tipo": "conhecimento_geral", "pergunta": "Em qual continente fica o Japão?", "resposta_esperada": "ásia"},
    {"id": 9, "tipo": "hardware", "pergunta": "O que significa a sigla CPU?", "resposta_esperada": "processamento"},
    {"id": 10, "tipo": "idioma", "pergunta": "Em que língua nós estamos conversando agora?", "resposta_esperada": "português"},
    {"id": 11, "tipo": "matematica", "pergunta": "Quanto é 100 dividido por 4?", "resposta_esperada": "25"},
    {"id": 12, "tipo": "programacao", "pergunta": "Python é uma linguagem compilada ou interpretada?", "resposta_esperada": "interpretada"},
    {"id": 13, "tipo": "sistema", "pergunta": "O que significa o termo SO em computação?", "resposta_esperada": "sistema operacional"},
    {"id": 14, "tipo": "web", "pergunta": "Qual protocolo seguro é usado na web, HTTP ou HTTPS?", "resposta_esperada": "https"},
    {"id": 15, "tipo": "visão_demanda", "pergunta": "Pior, o que tem na tela?", "resposta_esperada": "tela"},
    {"id": 16, "tipo": "conversacao", "pergunta": "Pior, você pode me ajudar?", "resposta_esperada": "ajudar"},
    {"id": 17, "tipo": "tempo", "pergunta": "Quantos minutos tem uma hora?", "resposta_esperada": "60"},
    {"id": 18, "tipo": "ciencia", "pergunta": "Qual planeta é conhecido como o planeta vermelho?", "resposta_esperada": "marte"},
    {"id": 19, "tipo": "logica", "pergunta": "O gelo é água em qual estado físico?", "resposta_esperada": "sólido"},
    {"id": 20, "tipo": "rede", "pergunta": "Qual porta padrão é usada pelo HTTP comum?", "resposta_esperada": "80"}
]

def run_accuracy_benchmark(output_dir="eval"):
    """
    Executa a bateria obrigatória de 20 perguntas/cenas para calcular
    a taxa de respostas corretas (Accuracy Rate).
    Gera CSV e JSON de auditoria.
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, "bateria_20_cenas.csv")
    json_file = os.path.join(output_dir, "bateria_20_cenas.json")

    results = []
    acertos = 0

    print(f"[Benchmark 20 Cenas] Iniciando avaliação de acurácia...")

    for item in BENCHMARK_SCENES:
        t0 = time.time()
        try:
            resp = requests.post(
                f"{SERVER_URL}/chat",
                json={"message": item["pergunta"], "mode": "direto"},
                timeout=15
            )
            data = resp.json()
            reply = data.get("reply", "").lower()
            esperado = item["resposta_esperada"].lower()

            # Checa se o termo-chave da resposta esperada está presente
            correto = esperado in reply
            if correto:
                acertos += 1
            status = "ACERTO" if correto else "ERRO_OU_DIVERGENCIA"
            raw_reply = data.get("reply", "")
        except Exception as e:
            correto = False
            status = f"FALHA_CONEXAO: {e}"
            raw_reply = ""

        duration_ms = int((time.time() - t0) * 1000)

        row = {
            "id": item["id"],
            "tipo": item["tipo"],
            "pergunta": item["pergunta"],
            "palavra_chave_esperada": item["resposta_esperada"],
            "resultado": status,
            "correto": correto,
            "duracao_ms": duration_ms,
            "resposta_obtida": raw_reply
        }
        results.append(row)
        print(f"[{item['id']:02d}/20] {status} - Pergunta: {item['pergunta'][:30]}...")
        time.sleep(0.3)

    accuracy_rate = round((acertos / len(BENCHMARK_SCENES)) * 100, 2)

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "tipo", "pergunta", "palavra_chave_esperada", "resultado", "correto", "duracao_ms", "resposta_obtida"])
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "total_cenas": len(BENCHMARK_SCENES),
        "acertos": acertos,
        "erros": len(BENCHMARK_SCENES) - acertos,
        "taxa_acerto_pct": accuracy_rate,
        "detalhes": results
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[Concluído] Bateria de 20 cenas finalizada!")
    print(f"Taxa de Acerto: {accuracy_rate}% ({acertos}/{len(BENCHMARK_SCENES)})")

if __name__ == "__main__":
    run_accuracy_benchmark()
