import sys
import os
import re
import streamlit as st
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.auth_controller import AuthController
from controllers.admin_controller import AdminController

class LoginView:
    @staticmethod
    def renderizar_ecran():
        """Desenha a interface de autenticação centrada com emoji e tons de cinza/verde."""
        
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

        # 🎯 Apresentação Centrada do Emoji e Título
        st.markdown("<h1 style='text-align: center; font-size: 80px; margin-bottom: 0px;'>🌱</h1>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center; color: #99c33a; margin-top: 0px; margin-bottom: 25px;'>EcoFIT</h2>", unsafe_allow_html=True)
        
        # Abas para separar o login do pedido de novo registo
        aba_login, aba_registo = st.tabs(["🔑 Iniciar Sessão", "📝 Novo Registo"])
        
        with aba_login:
            st.subheader("Acesso à Plataforma")
            
            with st.form(key="form_login_atleta", clear_on_submit=False):
                nome_login = st.text_input("Nome do Atleta", placeholder="Ex: MiguelBorges", key="input_login")
                passe_login = st.text_input("Palavra-passe", type="password", placeholder="••••••••", key="input_login_pass")
                
                btn_login = st.form_submit_button("Entrar", type="primary", use_container_width=True)
                
                if btn_login:
                    if AuthController.login(nome_login, passe_login):
                        st.rerun()
                    
        with aba_registo:
            st.subheader("Solicitar conta de atleta")
            st.caption("O teu acesso ficará pendente de validação por parte do Administrador.")
            
            nome_input = st.text_input("O teu Nome", placeholder="Ex: AnaSilva", key="input_registo")
            passe_input = st.text_input("Define a tua Palavra-passe", type="password", placeholder="Mínimo 4 carateres", key="input_registo_pass")
            
            nome_valido = False
            
            if nome_input:
                sucesso_validacao, mensagem = AdminController.validar_nome_registo(nome_input)
                if not sucesso_validacao:
                    st.error(mensagem)
                else:
                    st.success(mensagem)
                    nome_valido = True

            if st.button("Submeter Pedido de Acesso", use_container_width=True, key="btn_registo"):
                if not nome_valido:
                    st.error("❌ Resolva os avisos no nome antes de avançar.")
                elif not passe_input or len(passe_input.strip()) < 4:
                    st.error("❌ A palavra-passe deve ter pelo menos 4 carateres.")
                else:
                    if AuthController.solicitar_registo(nome_input, passe_input):
                        st.rerun()