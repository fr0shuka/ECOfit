import urllib.parse
import feedparser


class GoogleNewsService:
    BASE_URL = "https://news.google.com/rss/search"

    @classmethod
    def obter_eventos_desporto_pt(cls, modalidade: str = None, limite: int = 5) -> list[dict]:
        """Obtém as últimas notícias de eventos desportivos em Portugal via Google News RSS."""
        
        # Query simplificada e eficaz para o Google News
        if modalidade:
            termos = f"{modalidade} desporto portugal"
        else:
            termos = "eventos desporto portugal"

        query_encoded = urllib.parse.quote(termos)
        
        # URL com ordenação por data recente (when:7d força os últimos 7 dias)
        url = f"{cls.BASE_URL}?q={query_encoded}+when:7d&hl=pt-PT&gl=PT&ceid=PT:pt-150"

        try:
            feed = feedparser.parse(url)
            noticias = []

            for entry in feed.entries[:limite]:
                # Extrai a fonte original se disponível
                fonte_nome = entry.source.title if hasattr(entry, "source") and hasattr(entry.source, "title") else "Google News"
                
                noticias.append({
                    "titulo": entry.title,
                    "link": entry.link,
                    "publicado": getattr(entry, "published", "N/D"),
                    "fonte": fonte_nome
                })
            return noticias
        except Exception as e:
            print(f"⚠️ Erro ao consultar o Google News RSS: {e}")
            return []


# Teste rápido de verificação
if __name__ == "__main__":
    noticias = GoogleNewsService.obter_eventos_desporto_pt(limite=5)
    print(f"Total encontradas: {len(noticias)}\n")
    for n in noticias:
        print(f"• [{n['fonte']}] {n['titulo']}")
        print(f"  {n['link']}\n")