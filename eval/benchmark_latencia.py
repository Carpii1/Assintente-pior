import os
import time
import json
import csv
import io
import requests

SERVER_URL = "http://127.0.0.1:8000"

def run_latency_benchmark(output_dir="eval"):
    """
    Executa bateria de pelo menos 30 interações para medir a latência etapa por etapa.
    Gera tabela CSV e relatório JSON em eval/.
    """
    os.makedirs(output_dir, exist_ok=True)
    csv_file = os.path.join(output_dir, "benchmark_latencia_30.csv")
    json_file = os.path.join(output_dir, "benchmark_latencia_30.json")

    prompts = [
        "Pior, que horas são?",
        "Qual é a capital da França?",
        "Explique o que é Python de forma direta.",
        "Pior, como está o tempo hoje?",
        "Quanto é 25 multiplicado por 4?",
        "Qual a diferença entre lista e tupla?",
        "Pior, me dê um conselho de produtividade.",
        "O que significa a sigla API?",
        "Pior, cite três linguagens de programação.",
        "Como funciona a memória RAM?"
    ] * 3 # 30 requisições

    results = []
    print(f"[Benchmark] Iniciando bateria de {len(prompts)} interações...")

    for i, p in enumerate(prompts, start=1):
        t0 = time.time()
        try:
            resp = requests.post(
                f"{SERVER_URL}/chat",
                json={"message": p, "mode": "direto"},
                timeout=15
            )
            roundtrip_ms = int((time.time() - t0) * 1000)
            data = resp.json()
            server_latency = data.get("latency_ms", roundtrip_ms)
            backend = data.get("backend", "unknown")
            status = "sucesso" if resp.status_code == 200 else "erro"
        except Exception as e:
            roundtrip_ms = int((time.time() - t0) * 1000)
            server_latency = roundtrip_ms
            backend = "falha_rede"
            status = f"erro: {e}"

        item = {
            "iteracao": i,
            "prompt": p,
            "latencia_servidor_ms": server_latency,
            "tempo_total_roundtrip_ms": roundtrip_ms,
            "backend": backend,
            "status": status
        }
        results.append(item)
        print(f"[{i:02d}/30] Latência Servidor: {server_latency}ms | Total: {roundtrip_ms}ms | Status: {status}")
        time.sleep(0.3)

    # Escreve CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["iteracao", "prompt", "latencia_servidor_ms", "tempo_total_roundtrip_ms", "backend", "status"])
        writer.writeheader()
        writer.writerows(results)

    # Calcula médias
    valid_latencies = [r["latencia_servidor_ms"] for r in results if r["status"] == "sucesso"]
    valid_roundtrips = [r["tempo_total_roundtrip_ms"] for r in results if r["status"] == "sucesso"]
    
    summary = {
        "total_testes": len(results),
        "sucessos": len(valid_latencies),
        "latencia_media_servidor_ms": round(sum(valid_latencies) / len(valid_latencies), 2) if valid_latencies else 0,
        "latencia_min_ms": min(valid_latencies) if valid_latencies else 0,
        "latencia_max_ms": max(valid_latencies) if valid_latencies else 0,
        "roundtrip_medio_ms": round(sum(valid_roundtrips) / len(valid_roundtrips), 2) if valid_roundtrips else 0,
        "dados": results
    }

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n[Concluído] Resultados salvos em:\n - {csv_file}\n - {json_file}")
    print(f"Média Latência Servidor: {summary['latencia_media_servidor_ms']} ms")

if __name__ == "__main__":
    run_latency_benchmark()
