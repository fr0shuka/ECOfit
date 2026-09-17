import sys
import os
import streamlit as st
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.user_controller import UserController


class UsersView:
    @staticmethod
    def renderizar():
        st.title("Classificação Geral")
        st.caption("Desempenho acumulado da comunidade EcoFit.")

        df_users = UserController.obter_dados_ranking()

        if df_users is None or df_users.empty:
            st.info("Não existem dados de utilizadores para apresentar.")
            return

        # Normalização de colunas de hábitos e métricas
        for col in ['agua', 'fruta', 'pontos', 'kms', 'minutos']:
            if col not in df_users.columns:
                df_users[col] = 0
            else:
                df_users[col] = pd.to_numeric(df_users[col], errors='coerce').fillna(0)

        if 'agua' in df_users.columns and 'fruta' in df_users.columns:
            df_users['agua_fruta'] = df_users['agua'] + df_users['fruta']

        # Normalização do nome do perfil relacional se existir
        if 'perfil_nome' not in df_users.columns:
            df_users['perfil_nome'] = df_users.get('perfil', 'Atleta')

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
            'perfil_nome': 'Perfil',
            'pontos': 'Pontos',
            'kms': 'Distância (km)',
            'agua': 'Água (copos)',
            'fruta': 'Fruta (doses)',
            'agua_fruta': 'Total Saúde'
        }
        
        cols_presentes = [c for c in colunas_exibir.keys() if c in df_users.columns]
        df_exibicao = df_users[cols_presentes].copy()
        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao.sort_values(by="Pontos", ascending=False),
            width="stretch",
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
                    st.markdown(f"**#{idx}**")
                with col_nome:
                    p_nome = row.get('perfil_nome', 'Atleta')
                    st.markdown(f"**{row['nome']}**  \n<span style='color: #94a3b8; font-size: 0.75rem;'>{p_nome}</span>", unsafe_allow_html=True)
                with col_val:
                    st.markdown(f"`{row[coluna_valor]}` {sufixo}")