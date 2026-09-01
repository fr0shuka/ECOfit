import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.user_controller import UserController


class UsersView:
    @staticmethod
    def _injetar_estilos():
        st.markdown("""
            <style>
                button[data-baseweb="tab"] {
                    color: #94a3b8 !important;
                }
                button[data-baseweb="tab"][aria-selected="true"] {
                    color: #10b981 !important;
                    border-bottom-color: #10b981 !important;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def renderizar():
        UsersView._injetar_estilos()
        st.title("Classificação Geral")
        st.caption("Desempenho acumulado da comunidade EcoFit.")

        df_users = UserController.obter_dados_ranking()

        if df_users is None or df_users.empty:
            st.info("Não existem dados de utilizadores para apresentar.")
            return

        if 'agua' in df_users.columns and 'fruta' in df_users.columns:
            df_users['agua_fruta'] = df_users['agua'] + df_users['fruta']

        # --- SECÇÃO TOP 5 ---
        st.markdown("##### Líderes por Categoria")

        tab_pontos, tab_kms, tab_saude = st.tabs([
            "Pontuação Total",
            "Distância Percorrida",
            "Hábitos Saudáveis (Água + Fruta)"
        ])

        with tab_pontos:
            UsersView._renderizar_podio(
                df=df_users,
                coluna_ordem="pontos",
                coluna_valor="pontos",
                sufixo="pts",
                titulo="Maior Pontuação Acumulada"
            )

        with tab_kms:
            UsersView._renderizar_podio(
                df=df_users,
                coluna_ordem="kms",
                coluna_valor="kms",
                sufixo="km",
                titulo="Maiores Distâncias Percorridas"
            )

        with tab_saude:
            UsersView._renderizar_podio(
                df=df_users,
                coluna_ordem="agua_fruta",
                coluna_valor="agua_fruta",
                sufixo="doses",
                titulo="Hábitos Saudáveis Acumulados"
            )

        st.markdown("---")

        # --- SECÇÃO TABELA GERAL ---
        st.markdown("##### Tabela Geral de Utilizadores")

        colunas_exibir = {
            'nome': 'Nome',
            'pontos': 'Pontos',
            'kms': 'Distância (km)',
            'agua': 'Água (L)',
            'fruta': 'Fruta (doses)',
            'agua_fruta': 'Total Saúde'
        }
        
        cols_presentes = [c for c in colunas_exibir.keys() if c in df_users.columns]
        df_exibicao = df_users[cols_presentes].copy()
        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao.sort_values(by="Pontos", ascending=False),
            use_container_width=True,
            hide_index=True
        )

    @staticmethod
    def _renderizar_podio(df: pd.DataFrame, coluna_ordem: str, coluna_valor: str, sufixo: str, titulo: str):
        st.caption(titulo)
        top_5 = df.sort_values(by=coluna_ordem, ascending=False).head(5)

        for idx, (_, row) in enumerate(top_5.iterrows(), start=1):
            with st.container(border=True):
                col_pos, col_nome, col_val = st.columns([1, 4, 2], vertical_alignment="center")

                with col_pos:
                    st.markdown(f"<span style='color:#10b981; font-weight:bold;'>#{idx}</span>", unsafe_allow_html=True)
                with col_nome:
                    st.markdown(f"**{row['nome']}**")
                with col_val:
                    st.markdown(f"`{row[coluna_valor]}` {sufixo}")