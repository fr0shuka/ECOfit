import urllib.parse
import feedparser
import streamlit as st


class GoogleNewsService:
    BASE_URL = "https://news.google.com/rss/search"

    @classmethod
    def pesquisar_eventos(cls, termo_pesquisa: str, limite: int = 6) -> list[dict]:
        """Transforma a pesquisa do utilizador numa procura direcionada a sites/agendas de eventos."""
        
        # Otimiza a query adicionando termos que apontam para o evento em si
        query_otimizada = f"{termo_pesquisa} (inscricoes OR programa OR 'site oficial' OR agenda)"
        query_encoded = urllib.parse.quote(query_otimizada)
        
        url = f"{cls.BASE_URL}?q={query_encoded}+when:30d&hl=pt-PT&gl=PT&ceid=PT:pt-150"

        try:
            feed = feedparser.parse(url)
            resultados = []

            for entry in feed.entries[:limite]:
                fonte = entry.source.title if hasattr(entry, "source") and hasattr(entry.source, "title") else "Evento"
                
                # Tratamento do Título: Remove o "- Nome do Jornal/Site" que o Google junta no fim
                titulo_limpo = entry.title.split(" - ")[0]
                
                # Trunca títulos longos para manter o cartão pequeno e limpo
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
    """Executa a pesquisa e desenha os cartões padronizados na horizontal."""
    
    # 1. Faz a pesquisa dinâmica
    eventos = EventosDesportoService.pesquisar_eventos(termo_pesquisa, limite=6)

    if not eventos:
        st.info("Nenhum evento ou página relevante encontrada para essa pesquisa.")
        return

    # 2. Gera os cartões com altura e largura estritamente FIXAS
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

    # 3. Contentor Flexbox com Scroll Horizontal
    galeria_html = f"""
    <div style="
        display: flex;
        gap: 12px;
        overflow-x: auto;
        padding-bottom: 8px;
        align-items: stretch;">
        {cards_html}
    </div>
    """

    st.components.v1.html(galeria_html, height=170, scrolling=False)


# ==========================================
# Exemplo de Utilização no Streamlit
# ==========================================

# Caixa de pesquisa dinâmica para o utilizador
termo = st.text_input("O que procuras?", "proximos eventos desportivos em Portugal")

if termo:
    renderizar_galeria_eventos(termo)