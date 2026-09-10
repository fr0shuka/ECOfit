import sys
import os
import streamlit as st
import pandas as pd
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.admin_controller import AdminController
from models.user_model import UserModel


class AdminView:
    @staticmethod
    def _injetar_estilos_profissionais():
        """Injeta CSS minimalista para estilo corporativo sem emojis."""
        st.markdown("""
            <style>
                .main .block-container {
                    padding-top: 1.5rem;
                    max-width: 1100px;
                }
                
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

                .badge-approved {
                    background-color: rgba(34, 197, 94, 0.1);
                    color: #22c55e;
                    border: 1px solid rgba(34, 197, 94, 0.25);
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.72rem;
                    font-weight: 600;
                    letter-spacing: 0.05em;
                    text-transform: uppercase;
                }

                .text-secondary {
                    color: #94a3b8;
                    font-size: 0.875rem;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def renderizar_painel_admin():
        AdminView._injetar_estilos_profissionais()

        # 1. Controlo de Acesso
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador or str(utilizador.get('perfil', '')).lower() != 'admin':
            st.error("Acesso restrito a administradores.")
            return

        # Cabeçalho
        st.markdown("### Painel de Administração")
        st.caption("Gestão de acessos, validação de pendentes e controlo de perfis.")
        st.markdown("---")

        # Organização em Abas
        tab_pendentes, tab_gestao = st.tabs(["📋 Pedidos de Adesão", "👥 Gestão de Utilizadores"])

        #########
        # ABA 1: PEDIDOS PENDENTES
        #########
        with tab_pendentes:
            pendentes = AdminController.listar_pendentes()
            total_pendentes = len(pendentes) if pendentes else 0

            col_kpi, _ = st.columns([1, 3])
            with col_kpi:
                st.metric(label="Aprovações Pendentes", value=total_pendentes)

            st.markdown("##### Pedidos de Adesão em Espera")

            if not pendentes:
                st.info("Não existem utilizadores aguardando aprovação de momento.")
            else:
                for p in pendentes:
                    u_id = p.get('utilizador_id')
                    u_nome = p.get('nome', 'Sem Nome')
                    perfil_nome = p.get('perfil', 'Atleta')
                    estado_nome = p.get('estado', 'Pendente')

                    with st.container(border=True):
                        col_info, col_acoes = st.columns([3, 2], vertical_alignment="center")
                        
                        with col_info:
                            st.markdown(f"**{u_nome}**")
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
                                if st.button("Aprovar", key=f"app_{u_id}", type="primary", width="stretch"):
                                    if AdminController.processar_decisao(u_id, aprovado=True):
                                        st.toast(f"Utilizador {u_nome} aprovado.")
                                        time.sleep(0.6)
                                        st.rerun()
                                    else:
                                        st.error("Falha ao aprovar utilizador.")

                            with col_rejeitar:
                                if st.button("Rejeitar", key=f"rej_{u_id}", width="stretch"):
                                    if AdminController.processar_decisao(u_id, aprovado=False):
                                        st.toast(f"Pedido de {u_nome} rejeitado.")
                                        time.sleep(0.6)
                                        st.rerun()
                                    else:
                                        st.error("Falha ao rejeitar utilizador.")

        ##########
        # ABA 2: GESTÃO GERAL DE UTILIZADORES (ALTERAR PERFIL / ELIMINAR)
        ##########
        with tab_gestao:
            todos_utilizadores = UserModel.listar_todos()

            if not todos_utilizadores:
                st.warning("Nenhum utilizador registado na base de dados.")
                return

            df_users = pd.DataFrame(todos_utilizadores)

            # Métricas Gerais
            total_users = len(df_users)
            total_admins = len(df_users[df_users['perfil'].astype(str).str.lower() == 'admin']) if 'perfil' in df_users.columns else 0
            total_atletas = total_users - total_admins

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Registados", total_users)
            with m2:
                st.metric("Atletas", total_atletas)
            with m3:
                st.metric("Administradores", total_admins)

            st.markdown("---")
            st.markdown("##### Tabela Geral de Atletas e Admins")

            # Tratamento da Tabela de Exibição
            df_vis = df_users.copy()
            cols_map = {
                'utilizador_id': 'ID',
                'nome': 'Nome',
                'perfil': 'Perfil',
                'estado': 'Estado'
            }
            df_vis = df_vis.rename(columns={k: v for k, v in cols_map.items() if k in df_vis.columns})
            exibir_cols = [c for c in ['ID', 'Nome', 'Perfil', 'Estado'] if c in df_vis.columns]

            st.dataframe(df_vis[exibir_cols], width="stretch", hide_index=True)

            st.markdown("---")
            st.markdown("##### Alterar Perfil ou Remover Utilizador")

            for u in todos_utilizadores:
                u_id = u.get('utilizador_id')
                u_nome = u.get('nome', 'Sem Nome')
                u_perfil = str(u.get('perfil', 'Atleta')).capitalize()
                u_estado = str(u.get('estado', 'Pendente')).capitalize()

                with st.expander(f"ID #{u_id} — {u_nome} | Perfil: {u_perfil} | Estado: {u_estado}"):
                    c_perfil, c_delete = st.columns([2, 1], vertical_alignment="bottom")

                    with c_perfil:
                        opcoes_perfil = ["Atleta", "Admin"]
                        idx_selecionado = opcoes_perfil.index(u_perfil) if u_perfil in opcoes_perfil else 0
                        
                        novo_perfil = st.selectbox(
                            "Perfil de Acesso:",
                            opcoes_perfil,
                            index=idx_selecionado,
                            key=f"sel_perfil_{u_id}"
                        )

                        if st.button("Guardar Perfil", key=f"btn_save_perfil_{u_id}", type="primary"):
                            if novo_perfil != u_perfil:
                                if UserModel.atualizar_perfil(u_id, novo_perfil):
                                    st.toast(f"Perfil de {u_nome} alterado para {novo_perfil}!")
                                    time.sleep(0.6)
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar o perfil.")
                            else:
                                st.info("O perfil selecionado é igual ao atual.")

                    with c_delete:
                        if st.button("🗑️ Eliminar Utilizador", key=f"btn_del_usr_{u_id}", width="stretch"):
                            if UserModel.eliminar_utilizador(u_id):
                                st.toast(f"Utilizador {u_nome} eliminado com sucesso.")
                                time.sleep(0.6)
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar o utilizador.")