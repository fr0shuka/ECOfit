import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.admin_controller import AdminController


class AdminView:
    @staticmethod
    def renderizar_painel_admin():
        # 1. Controlo de Acesso (Apenas Admins)
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador or utilizador.get('tipo_utilizador') != 'Admin':
            st.error("⛔ Acesso restrito a administradores.")
            return

        st.title("🛡️ Painel de Administração")
        st.subheader("Gestão de Novas Contas")

        # 2. Obter Utilizadores Pendentes
        pendentes = AdminController.listar_pendentes()

        if not pendentes:
            st.info("🎉 Não existem utilizadores aguardando aprovação no momento.")
            return

        st.warning(f"Existem **{len(pendentes)}** pedidos de adesão pendentes.")

        # 3. Listagem em Formato Card com Ações
        for p in pendentes:
            with st.container(border=True):
                col_info, col_acoes = st.columns([3, 2])
                
                with col_info:
                    st.markdown(f"**Nome:** {p['nome']}")
                    st.caption(f"📧 {p['email']} | 📅 Registado em: {p.get('data_registo', 'N/D')}")
                
                with col_acoes:
                    col_aprovar, col_rejeitar = st.columns(2)
                    
                    with col_aprovar:
                        if st.button("✅ Aprovar", key=f"app_{p['utilizador_id']}", use_container_width=True):
                            if AdminController.processar_decisao(p['utilizador_id'], aprovado=True):
                                st.toast(f"Utilizador {p['nome']} aprovado!", icon="✅")
                                st.rerun()
                            else:
                                st.error("Erro ao aprovar utilizador.")

                    with col_rejeitar:
                        if st.button("❌ Rejeitar", key=f"rej_{p['utilizador_id']}", use_container_width=True):
                            if AdminController.processar_decisao(p['utilizador_id'], aprovado=False):
                                st.toast(f"Pedido de {p['nome']} rejeitado.", icon="ℹ️")
                                st.rerun()
                            else:
                                st.error("Erro ao rejeitar utilizador.")