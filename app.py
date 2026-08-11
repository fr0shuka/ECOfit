import streamlit as st
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.admin_view import AdminView
from views.upload_view import UploadView
from views.users_view import UsersView
from views.components import renderizar_meteo_sidebar
from services.news_service import GoogleNewsService

# Configuração centrada e aplicação do Logotipo no separador do navegador
st.set_page_config(
    page_title="EcoFIT", 
    page_icon="🌱", 
    layout="centered"             # Força o layout a ficar centrado e compacto
)

# Fluxo de navegação baseado no estado da sessão
if 'utilizador_logado' not in st.session_state:
    LoginView.renderizar_ecran()
else:
    utilizador = st.session_state['utilizador_logado']
    
    # Barra Lateral
    with st.sidebar:
        st.markdown(f"### Olá, **{utilizador['nome']}**")
        st.caption(f"Perfil: {utilizador['perfil']} | Estado: {utilizador['estado']}")
        st.markdown("---")

        # Renderiza o widget do tempo no fundo do menu esquerdo
        renderizar_meteo_sidebar()


        if st.button("Terminar Sessão (Logout)", use_container_width=True):
            from controllers.auth_controller import AuthController
            AuthController.logout()
            st.rerun()



    st.title("💪 Painel de Performance EcoFit")
    
    if utilizador['perfil'] == 'Admin':
        # Admin vê 4 abas agora
        aba_app, aba_upload, aba_user, aba_admin = st.tabs(["🚀 Inserir Atividade", "📥 Sincronizar Ficheiro", "🏆 Ranking & Utilizadores", "🛡️ Gerir Pedidos Pendentes"])
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_upload:
            UploadView.renderizar_zona_upload()
        with aba_user:
            UsersView.renderizar()
        with aba_admin:
            AdminView.renderizar_painel_admin()
    else:
        # Atleta normal vê 3 abas
        aba_app, aba_upload, aba_user = st.tabs(["🚀 Inserir Atividade", "📥 Sincronizar Ficheiro", "🏆 Ranking & Utilizadores"])
        with aba_app:
            DashboardView.renderizar_formulario()
        with aba_upload:
            UploadView.renderizar_zona_upload()
        with aba_user:
            UsersView.renderizar()  


    noticias = GoogleNewsService.obter_eventos_desporto_pt(limite=5)

    if noticias:
        for item in noticias:
            with st.container():
                st.subheader(item["titulo"])
                st.caption(f"Fonte: {item['fonte']} | Data: {item['publicado']}")
                st.markdown(f"[Ler artigo completo]({item['link']})")
                st.divider()
        else:
            st.info("Nenhuma notícia encontrada de momento.")