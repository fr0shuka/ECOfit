import urllib.parse
import feedparser


class GoogleNewsService:
    BASE_URL = "https://news.google.com/rss/search"

    @classmethod
    def obter_eventos_desporto_pt(cls, modalidade: str = None, limite: int = 5) -> list[dict]:
        """Obtém as últimas notícias de eventos desportivos em Portugal via Google News RSS."""
        
        # Constrói a pesquisa com base no desporto geral ou modalidade específica
        if modalidade:
            termos = f'"{modalidade}" eventos OR campeonato OR liga Portugal'
        else:
            termos = 'desporto eventos OR "calendário desportivo" OR "liga portugal"'

        query_encoded = urllib.parse.quote(termos)
        
        # URL parametrizado para o contexto de Portugal (hl=pt-PT, gl=PT, ceid=PT:pt-150)
        url = f"{cls.BASE_URL}?q={query_encoded}&hl=pt-PT&gl=PT&ceid=PT:pt-150"

        try:
            feed = feedparser.parse(url)
            noticias = []

            for entry in feed.entries[:limite]:
                noticias.append({
                    "titulo": entry.title,
                    "link": entry.link,
                    "publicado": getattr(entry, "published", "N/D"),
                    "fonte": entry.source.title if hasattr(entry, "source") else "Google News"
                })
            return noticias
        except Exception as e:
            print(f"⚠️ Erro ao consultar o Google News RSS: {e}")
            return []


# Exemplo de teste/chamada direta no próprio ficheiro:
if __name__ == "__main__":
    # Teste 1: Geral
    print("--- Notícias Gerais de Desporto ---")
    lista = GoogleNewsService.obter_eventos_desporto_pt(limite=3)
    for n in lista:
        print(f"[{n['fonte']}] {n['titulo']}\nLink: {n['link']}\n")

    # Teste 2: Modalidade Específica (ex: Ciclismo)
    print("--- Notícias de Ciclismo ---")
    lista_ciclismo = GoogleNewsService.obter_eventos_desporto_pt(modalidade="ciclismo", limite=2)
    for n in lista_ciclismo:
        print(f"[{n['fonte']}] {n['titulo']}\nLink: {n['link']}\n")