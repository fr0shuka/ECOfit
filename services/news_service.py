import urllib.parse
import feedparser
import streamlit as st


class EventosDesportoService:
    BASE_URL = "https://news.google.com/rss/search"

    @classmethod
    def pesquisar_eventos(cls, termo_pesquisa: str, limite: int = 6) -> list[dict]:
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
    """Renderiza a galeria de notícias fixada no rodapé da página."""
    eventos = EventosDesportoService.pesquisar_eventos(termo_pesquisa, limite=6)

    if not eventos:
        return

    # Gera os cartões em formato compacto para o rodapé
    cards_html = ""
    for ev in eventos:
        cards_html += f"""
        <div style="
            flex: 0 0 190px;
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

    # Estrutura HTML/CSS fixada na base da janela (rodapé)
    footer_html = f"""
    <style>
        /* Cria margem no fundo do Streamlit para o conteúdo não ser tapado pelo rodapé */
        body {{
            margin-bottom: 160px !important;
        }}
        .no-scrollbar::-webkit-scrollbar {{
            display: none;
        }}
        .no-scrollbar {{
            -ms-overflow-style: none;
            scrollbar-width: none;
        }}
        .footer-news-container {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100vw;
            background-color: #121212;
            border-top: 1px solid #333;
            padding: 8px 16px;
            z-index: 99999;
            box-shadow: 0px -4px 10px rgba(0,0,0,0.5);
            box-sizing: border-box;
        }}
        .nav-btn {{
            background-color: #2b2b2b;
            color: #fff;
            border: 1px solid #444;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            cursor: pointer;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            user-select: none;
        }}
        .nav-btn:hover {{
            background-color: #ff4b4b;
            border-color: #ff4b4b;
        }}
    </style>

    <div class="footer-news-container">
        <div style="font-size: 0.75em; color: #888; margin-bottom: 4px; font-weight: bold;">
             Próximos Eventos Desportivos
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
            <button class="nav-btn" onclick="document.getElementById('gallery-footer').scrollBy({{left: -200, behavior: 'smooth'}})">❮</button>
            
            <div id="gallery-footer" class="no-scrollbar" style="
                display: flex;
                gap: 10px;
                overflow-x: auto;
                scroll-behavior: smooth;
                align-items: stretch;
                width: 100%;">
                {cards_html}
            </div>

            <button class="nav-btn" onclick="document.getElementById('gallery-footer').scrollBy({{left: 200, behavior: 'smooth'}})">❯</button>
        </div>
    </div>
    """

    st.components.v1.html(footer_html, height=150, scrolling=False)