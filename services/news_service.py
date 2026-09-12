import urllib.parse
import feedparser
import streamlit as st
import streamlit.components.v1 as components


class EventosDesportoService:
    BASE_URL = "https://news.google.com/rss/search"

    @classmethod
    def pesquisar_eventos(cls, termo_pesquisa: str, limite: int = 12) -> list[dict]:
        query_otimizada = f"{termo_pesquisa} (inscricoes OR programa OR 'site oficial' OR agenda)"
        query_encoded = urllib.parse.quote(query_otimizada)
        
        url = f"{cls.BASE_URL}?q={query_encoded}+when:30d&hl=pt-PT&gl=PT&ceid=PT:pt-150"

        try:
            feed = feedparser.parse(url)
            resultados = []

            for entry in feed.entries[:limite]:
                fonte = entry.source.title if hasattr(entry, "source") and hasattr(entry.source, "title") else "Evento"
                
                titulo_limpo = entry.title.split(" - ")[0]
                if len(titulo_limpo) > 40:
                    titulo_limpo = titulo_limpo[:37] + "..."

                resultados.append({
                    "titulo": titulo_limpo,
                    "link": entry.link,
                    "fonte": fonte
                })
            return resultados
        except Exception as e:
            print(f"⚠️ Erro na pesquisa: {e}")
            return []


def renderizar_galeria_eventos(termo_pesquisa: str):
    """Galeria de notícias em formato carrossel perfeitamente alinhada e funcional."""
    eventos = EventosDesportoService.pesquisar_eventos(termo_pesquisa, limite=12)

    if not eventos:
        return

    # Construção dos cartões
    cards_html = ""
    for ev in eventos:
        cards_html += f"""
        <div class="card">
            <div>
                <span class="fonte">{ev['fonte']}</span>
                <p class="titulo">{ev['titulo']}</p>
            </div>
            <a href="{ev['link']}" target="_blank" class="link">🔗 Ver Evento →</a>
        </div>
        """

    # HTML + CSS + JS encapsulado via Componente Nativo do Streamlit
    componente_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            background-color: transparent;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            overflow: hidden;
        }}
        .embedded-news-container {{
            width: 100%;
            background-color: #121212;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 12px 16px;
        }}
        .header-title {{
            font-size: 0.75em;
            color: #888;
            margin-bottom: 8px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .carousel-wrapper {{
            display: flex;
            align-items: center;
            gap: 10px;
            width: 100%;
        }}
        .no-scrollbar {{
            display: flex;
            gap: 12px;
            overflow-x: auto;
            scroll-behavior: smooth;
            width: 100%;
            padding: 4px 0;
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        .no-scrollbar::-webkit-scrollbar {{
            display: none;
        }}
        .card {{
            flex: 0 0 240px;
            min-width: 240px;
            height: 110px;
            background-color: #1e1e1e;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #333;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .fonte {{
            color: #4da6ff;
            font-size: 0.65em;
            font-weight: bold;
            text-transform: uppercase;
            display: block;
        }}
        .titulo {{
            color: #fff;
            font-size: 0.80em;
            font-weight: 600;
            line-height: 1.3;
            margin-top: 4px;
        }}
        .link {{
            color: #ff4b4b;
            text-decoration: none;
            font-weight: bold;
            font-size: 0.72em;
        }}
        .nav-btn {{
            background-color: #2b2b2b;
            color: #fff;
            border: 1px solid #444;
            border-radius: 50%;
            min-width: 34px;
            height: 34px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
            flex-shrink: 0;
            transition: background-color 0.2s;
        }}
        .nav-btn:hover {{
            background-color: #ff4b4b;
            border-color: #ff4b4b;
        }}
    </style>
    </head>
    <body>

    <div class="embedded-news-container">
        <div class="header-title">Próximos Eventos Desportivos</div>
        <div class="carousel-wrapper">
            <button class="nav-btn" onclick="document.getElementById('track').scrollBy({{left: -300, behavior: 'smooth'}})">❮</button>
            
            <div id="track" class="no-scrollbar">
                {cards_html}
            </div>

            <button class="nav-btn" onclick="document.getElementById('track').scrollBy({{left: 300, behavior: 'smooth'}})">❯</button>
        </div>
    </div>

    </body>
    </html>
    """

    # Renderiza através do componente de iframe para garantir isolamento de JS e largura total
    components.html(componente_html, height=170)