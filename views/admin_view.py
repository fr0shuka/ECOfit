import sys
import os
import streamlit as st
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.admin_controller import AdminController


class AdminView:
    @staticmethod
    def _injetar_estilos_profissionais():
        """Injeta CSS minimalista para estilo corporativo sem emojis."""
        st.markdown("""
            <style>
                /* Tipografia e estrutura */
                .main .block-container {
                    padding-top: 1.5rem;
                    max-width: 1100px;
                }
                
                /* Badges de estado discretos */
                .badge-pending {
                    background-color: rgba(234, 179, 8, 0.1);
                    color: #eab308;
                    border: 1px solid rgba(234, 179, 8, 0.25);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.72rem;
                    font-weight: 600;
                    letter-spacing: 0.05em;
                    text-transform: uppercase;
                }
                
                .badge-profile {
                    background-color: rgba(148, 163, 184, 0.1);
                    color: #94a3b8;
                    border: 1px solid rgba(148, 163, 184, 0.25);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.72rem;
                    font-weight: 600;
                    letter-spacing: 0.05em;
                    text-transform: uppercase;
                }

                /* Subtítulo e descrições */
                .text-secondary {
                    color: #94a3b8;
                    font-size: 0.875rem;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def renderizar_painel_admin():
        # Aplicar estilos minimalistas
        AdminView._injetar_estilos_profissionais()

        # 1. Controlo de Acesso (Apenas Admins)
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador or utilizador.get('perfil') != 'Admin':
            st.error("Acesso restrito a administradores.")
            return

        # Cabeçalho Limpo
        st.title("Painel de Administração")
        st.caption("Gestão de acessos e validação de pendentes.")
        st.markdown("---")

        # 2. Obter Utilizadores Pendentes
        pendentes = AdminController.listar_pendentes()
        total_pendentes = len(pendentes) if pendentes else 0

        # Métrica de Resumo
        col_kpi, _ = st.columns([1, 3])
        with col_kpi:
            st.metric(label="Aprovações Pendentes", value=total_pendentes)

        st.markdown("##### Pedidos de Adesão")

        if not pendentes:
            st.info("Não existem utilizadores aguardando aprovação de momento.")
            return

        # 3. Listagem com design corporativo
        for p in pendentes:
            with st.container(border=True):
                col_info, col_acoes = st.columns([3, 2], vertical_alignment="center")
                
                with col_info:
                    st.markdown(f"**{p['nome']}**")
                    
                    perfil_nome = p.get('perfil', 'Utilizador')
                    estado_nome = p.get('estado', 'Pendente')
                    
                    st.markdown(
                        f"""
                        <div style="display: flex; gap: 6px; align-items: center; margin-top: 4px;">
                            <span class="badge-profile">{perfil_nome}</span>
                            <span class="badge-pending">{estado_nome}</span>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                with col_acoes:
                    col_aprovar, col_rejeitar = st.columns(2)
                    
                    with col_aprovar:
                        if st.button("Aprovar", key=f"app_{p['utilizador_id']}", type="primary", use_container_width=True):
                            if AdminController.processar_decisao(p['utilizador_id'], aprovado=True):
                                st.toast(f"Utilizador {p['nome']} aprovado.", icon=None)
                                time.sleep(0.8)
                                st.rerun()
                            else:
                                st.error("Falha ao aprovar utilizador.")

                    with col_rejeitar:
                        if st.button("Rejeitar", key=f"rej_{p['utilizador_id']}", use_container_width=True):
                            if AdminController.processar_decisao(p['utilizador_id'], aprovado=False):
                                st.toast(f"Pedido de {p['nome']} rejeitado.", icon=None)
                                time.sleep(0.8)
                                st.rerun()
                            else:
                                st.error("Falha ao rejeitar utilizador.")