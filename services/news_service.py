import urllib.parse
import feedparser
import streamlit as st


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
    """Galeria de notícias incorporada no fundo da página com scroll forçado."""
    eventos = EventosDesportoService.pesquisar_eventos(termo_pesquisa, limite=12)

    if not eventos:
        return

    # Gera os cartões garantindo largura fixa (flex-shrink: 0 e min-width)
    cards_html = ""
    for ev in eventos:
        cards_html += f"""
        <div style="
            flex: 0 0 220px;
            min-width: 220px;
            height: 110px;
            background-color: #1e1e1e;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #333;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;">
            <div>
                <span style="color: #4da6ff; font-size: 0.65em; font-weight: bold; text-transform: uppercase;">{ev['fonte']}</span>
                <p style="color: #fff; font-size: 0.78em; font-weight: 600; line-height: 1.2; margin: 4px 0 0 0;">{ev['titulo']}</p>
            </div>
            <a href="{ev['link']}" target="_blank" style="
                color: #ff4b4b;
                text-decoration: none;
                font-weight: bold;
                font-size: 0.70em;">🔗 Ver Evento →</a>
        </div>
        """

    footer_html = f"""
    <style>
        .no-scrollbar::-webkit-scrollbar {{
            display: none;
        }}
        .no-scrollbar {{
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        .embedded-news-container {{
            width: 80%;
            margin: 40px auto 20px auto;
            background-color: #121212;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 12px 16px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            box-sizing: border-box;
        }}
        .nav-btn {{
            background-color: #2b2b2b;
            color: #fff;
            border: 1px solid #444;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
            flex-shrink: 0;
        }}
        .nav-btn:hover {{
            background-color: #ff4b4b;
            border-color: #ff4b4b;
        }}
    </style>

    <div class="embedded-news-container">
        <div style="font-size: 0.75em; color: #888; margin-bottom: 6px; font-weight: bold;">
             Próximos Eventos Desportivos
        </div>
        <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
            <button class="nav-btn" onclick="this.nextElementSibling.scrollBy({{left: -250, behavior: 'smooth'}})">❮</button>
            
            <div class="no-scrollbar" style="
                display: flex;
                flex-wrap: nowrap;
                gap: 10px;
                overflow-x: auto;
                scroll-behavior: smooth;
                align-items: stretch;
                width: 100%;
                min-width: 0;">
                {cards_html}
            </div>

            <button class="nav-btn" onclick="this.previousElementSibling.scrollBy({{left: 250, behavior: 'smooth'}})">❯</button>
        </div>
    </div>
    """

    st.html(footer_html)