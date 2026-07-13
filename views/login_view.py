import re
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.admin_controller import AdminController

class LoginView:
    @staticmethod
    def renderizar_ecran():
        """Desenha a interface de autenticação customizada em tons de cinza e verde."""
        
        # 🎨 Injeção de CSS Customizado para controlo estrito da palete de cores
        st.markdown("""
            <style>
                /* Estilização global dos botões do Streamlit nesta página */
                div.stButton > button {
                    background-color: #2E7D32 !important; /* Verde Eco */
                    color: white !important;
                    border: none !important;
                    border-radius: 6px !important;
                    padding: 0.6rem 1rem !important;
                    font-weight: 600 !important;
                    transition: background-color 0.3s ease !important;
                }
                
                /* Efeito Hover nos botões (Passar o rato) */
                div.stButton > button:hover {
                    background-color: #1B5E20 !important; /* Verde mais escuro */
                    color: white !important;
                }
                
                /* Customização das Abas (Tabs) */
                button[data-baseweb="tab"] {
                    color: #555555 !important; /* Cinza Escuro */
                    font-size: 16px !important;
                }
                button[data-baseweb="tab"][aria-selected="true"] {
                    color: #2E7D32 !important; /* Destaque em Verde */
                    border-bottom-color: #2E7D32 !important;
                    font-weight: bold !important;
                }
                
                #MainMenu, footer {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)

        # 🎯 Apresentação Centrada do Logotipo e do Título
        col_logo_esq, col_logo_centro, col_logo_dir = st.columns([1, 2, 1])
        with col_logo_centro:
            # Apresenta o logotipo na página inicial centrado
            st.image("🌱", use_container_width=True)
            
        st.markdown("<h2 style='text-align: center; color: #333333; margin-bottom: 25px;'>🌱 EcoFIT</h2>", unsafe_html=True)
        
        # Abas para separar o login do pedido de novo registo
        aba_login, aba_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Novo Registo"])
        
        with aba_login:
            st.subheader("Acesso à Plataforma")
            nome_login = st.text_input("Nome do Atleta", placeholder="Ex: MiguelBorges", key="input_login")
            
            if st.button("Entrar", use_container_width=True, key="btn_login"):
                if AuthController.login(nome_login):
                    st.rerun()
                    
        with aba_registo:
            st.subheader("Solicitar conta de atleta")
            st.caption("O teu acesso ficará pendente de validação por parte do Administrador.")
            nome_input = st.text_input("O teu Nome", placeholder="Ex: AnaSilva", key="input_registo")
            
            nome_valido = False
            
            if nome_input:
                sucesso_validacao, mensagem = AdminController.validar_nome_registo(nome_input)
                if not sucesso_validacao:
                    st.error(mensagem)
                else:
                    st.success(mensagem)
                    nome_valido = True

            if st.button("Submeter Pedido de Acesso", use_container_width=True, key="btn_registo"):
                if nome_valido:
                    AdminController.solicitar_registo(nome_input)
                    st.rerun()
                else:
                    st.error("❌ Não é possível submeter. Resolva os avisos no nome antes de avançar.")