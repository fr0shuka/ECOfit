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
                if len(titulo_limpo) > 45:
                    titulo_limpo = titulo_limpo[:42] + "..."

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
        """Módulo visual para desenhar a galeria com setas de navegação no Streamlit."""
        eventos = EventosDesportoService.pesquisar_eventos(termo_pesquisa, limite=6)

        if not eventos:
            st.info("Nenhum evento encontrado de momento.")
            return

        # Gera os cartões
        cards_html = ""
        for ev in eventos:
            cards_html += f"""
            <div style="
                flex: 0 0 210px;
                height: 150px;
                background-color: #1e1e1e;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #333;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-sizing: border-box;">
                <div>
                    <span style="color: #4da6ff; font-size: 0.70em; font-weight: bold; text-transform: uppercase;">{ev['fonte']}</span>
                    <p style="color: #fff; font-size: 0.82em; font-weight: 600; line-height: 1.25; margin: 6px 0 0 0;">{ev['titulo']}</p>
                </div>
                <a href="{ev['link']}" target="_blank" style="
                    color: #ff4b4b;
                    text-decoration: none;
                    font-weight: bold;
                    font-size: 0.75em;">🔗 Aceder ao Evento →</a>
            </div>
            """

        # Galeria com botões laterais + CSS para esconder a scrollbar
        galeria_html = f"""
        <style>
            /* Esconde a barra de scroll nos navegadores */
            .no-scrollbar::-webkit-scrollbar {{
                display: none;
            }}
            .no-scrollbar {{
                -ms-overflow-style: none;  /* IE/Edge */
                scrollbar-width: none;  /* Firefox */
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
                transition: background-color 0.2s;
            }}
            .nav-btn:hover {{
                background-color: #ff4b4b;
                border-color: #ff4b4b;
            }}
        </style>

        <div style="display: flex; align-items: center; gap: 8px;">
            <button class="nav-btn" onclick="document.getElementById('gallery-container').scrollBy({{left: -230, behavior: 'smooth'}})">❮</button>
            
            <div id="gallery-container" class="no-scrollbar" style="
                display: flex;
                gap: 12px;
                overflow-x: auto;
                scroll-behavior: smooth;
                padding: 4px 0;
                align-items: stretch;
                width: 100%;">
                {cards_html}
            </div>

            <button class="nav-btn" onclick="document.getElementById('gallery-container').scrollBy({{left: 230, behavior: 'smooth'}})">❯</button>
        </div>
        """

        st.components.v1.html(galeria_html, height=170, scrolling=False)