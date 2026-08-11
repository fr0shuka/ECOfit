import urllib.parse
import feedparser


class GoogleNewsService:
    BASE_URL = "https://news.google.com/rss/search"

    @classmethod
    def obter_proximos_eventos_desporto_pt(cls, modalidade: str = None, limite: int = 6) -> list[dict]:
        """Procura notícias sobre PRÓXIMOS eventos e calendários desportivos em Portugal."""
        
        # Query focada em intenção futura/agendamento de eventos
        if modalidade:
            termos = f'"{modalidade}" (agenda OR calendario OR "proximos eventos" OR "datas") portugal'
        else:
            termos = '(agenda OR calendario OR "proximos eventos" OR "guia de eventos") desporto portugal'

        query_encoded = urllib.parse.quote(termos)
        
        # Pesquisa nos últimos 7 dias para garantir atualidade
        url = f"{cls.BASE_URL}?q={query_encoded}+when:7d&hl=pt-PT&gl=PT&ceid=PT:pt-150"

        try:
            feed = feedparser.parse(url)
            noticias = []

            for entry in feed.entries[:limite]:
                fonte_nome = entry.source.title if hasattr(entry, "source") and hasattr(entry.source, "title") else "Google News"
                
                noticias.append({
                    "titulo": entry.title,
                    "link": entry.link,
                    "publicado": getattr(entry, "published", "N/D")[:16],  # Trunca a data para ficar limpa
                    "fonte": fonte_nome
                })
            return noticias
        except Exception as e:
            print(f"⚠️ Erro ao consultar o Google News RSS: {e}")
            return []