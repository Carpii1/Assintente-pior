"""
Módulo de Pesquisa na Web em Tempo Real para o PIOR Assistente.
Permite à LLM consultar:
- Fatos recentes, álbuns, notícias e datas atualizadas.
- Cupons de desconto e ofertas para lojas online visíveis na tela ou mencionadas.
- Informações sobre papéis de parede (wallpapers), arte, jogos e animes.
"""
import re
from typing import List, Dict, Any

try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

def perform_web_search(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """
    Executa uma pesquisa na Web via DuckDuckGo em tempo real.
    Retorna uma lista de resultados contendo título, resumo (snippet) e link.
    """
    if not query or not query.strip():
        return []
    
    clean_query = query.strip()
    results = []
    
    if DDGS is not None:
        try:
            ddgs = DDGS()
            raw = list(ddgs.text(clean_query, max_results=max_results))
            for item in raw:
                title = item.get("title", "")
                snippet = item.get("body", "") or item.get("snippet", "")
                href = item.get("href", "")
                if title or snippet:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": href
                    })
            if results:
                return results
        except Exception as e:
            print(f"[WebSearch] Erro ao buscar via DDGS: {e}")

    # Fallback via duckduckgo html básico se DDGS falhar
    try:
        import urllib.request
        import urllib.parse
        
        encoded = urllib.parse.quote(clean_query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            for result in soup.select('.result'):
                title_elem = result.select_one('.result__title')
                snippet_elem = result.select_one('.result__snippet')
                if title_elem and snippet_elem:
                    results.append({
                        "title": title_elem.get_text(strip=True),
                        "snippet": snippet_elem.get_text(strip=True),
                        "url": ""
                    })
                if len(results) >= max_results:
                    break
        except ImportError:
            # Fallback simples regex se bs4 não estiver disponível
            matches = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
            for m in matches[:max_results]:
                clean_txt = re.sub(r'<[^>]+>', '', m).strip()
                if clean_txt:
                    results.append({"title": "Resultado Web", "snippet": clean_txt, "url": ""})
    except Exception as e:
        print(f"[WebSearch] Fallback também falhou: {e}")

    return results

def search_coupons(store_or_product: str) -> List[Dict[str, str]]:
    """Pesquisa cupons de desconto e promoções ativas para uma loja ou produto."""
    query = f"cupom de desconto {store_or_product} código promocional hoje 2024"
    return perform_web_search(query, max_results=3)

def format_search_context(results: List[Dict[str, str]]) -> str:
    """Formata os resultados da busca em um bloco limpo para injetar no contexto da LLM."""
    if not results:
        return ""
    lines = ["INFORMAÇÕES RECENTES COLETADAS NA WEB:"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}: {r['snippet']}")
    return "\n".join(lines)

def should_trigger_search(user_msg: str) -> bool:
    """Detecta se a pergunta do usuário pede explicitamente pesquisa factual na web, lançamentos, notícias ou cupons."""
    msg = user_msg.lower()
    
    # Se for uma pergunta visual direta de tela ou webcam, só faz busca se o usuário pedir explicitamente
    is_visual_query = any(w in msg for w in ["tela", "monitor", "wallpaper", "papel de parede", "fundo", "leia", "traduza", "webcam", "quadro", "olhe", "veja"])
    has_explicit_search = any(w in msg for w in ["pesquis", "busqu", "procur", "google", "googl", "lançado recentemente", "lancado recentemente", "último mês", "ultimo mes", "notícia", "noticia", "cupom", "cupons", "desconto", "preço", "preco"])

    if is_visual_query and not has_explicit_search:
        return False

    explicit_patterns = [
        r"\b(pesquis|busqu|procur|googl|investig|descubr)\b",
        r"\b(cupom|cupons|desconto|promocional|promoção|promocao|oferta|ofertas|mais barato)\b",
        r"\b(lançado|lancado|lançamento|lancamento|recente|recentemente|ultimo mes|último mês|este ano)\b",
        r"\b(notícia|noticia|informações recentes|cotação|cotacao)\b"
    ]
    for p in explicit_patterns:
        if re.search(p, msg):
            return True
    return False

def is_shopping_or_coupon_query(msg: str) -> bool:
    """Verifica se o usuário está falando sobre compras, loja virtual ou cupons."""
    m = msg.lower()
    return any(w in m for w in ["cupom", "cupons", "desconto", "comprar", "preço", "preco", "loja", "amazon", "mercado livre", "aliexpress", "kabum", "magalu", "shopee", "shein"])
