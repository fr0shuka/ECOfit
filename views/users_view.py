import sys
import os
import streamlit as st
import pandas as pd

# Assegura a resolução da raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controllers.user_controller import UserController


class UsersView:
    @staticmethod
    def renderizar():
        st.title("🏆 Tabela de Classificação & Utilizadores")
        st.write("Acompanha os líderes e o desempenho da comunidade **EcoFit**!")

        # 1. Obter os dados de todos os utilizadores aprovados através do Controller
        df_users = UserController.obter_dados_ranking()

        if df_users is None or df_users.empty:
            st.info("Ainda não existem dados de utilizadores registados/aprovados para apresentar.")
            return

        # Garantir que a coluna combinada Água + Fruta existe
        if 'agua' in df_users.columns and 'fruta' in df_users.columns:
            df_users['agua_fruta'] = df_users['agua'] + df_users['fruta']

        # --- SEÇÃO TOP 5 ---
        st.subheader("🌟 Top 5 EcoFit")

        tab_pontos, tab_kms, tab_saude = st.tabs([
            "🥇 Top 5 Pontos",
            "🏃 Top 5 Distância (Kms)",
            "🍎💧 Top 5 Água & Fruta"
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
                sufixo="unidades/doses",
                titulo="Campeões de Hábitos Saudáveis (Água + Fruta)"
            )

        st.divider()

        # --- SEÇÃO TABELA GERAL ---
        st.subheader("👥 Lista Geral de Utilizadores")

        # Seleção e renomeação de colunas para exibição limpa
        colunas_exibir = {
            'nome': 'Nome',
            'pontos': 'Pontos',
            'kms': 'Distância (Km)',
            'agua': 'Água (L)',
            'fruta': 'Fruta (doses)',
            'agua_fruta': 'Total Saúde (Água+Fruta)'
        }
        
        # Filtrar apenas as colunas existentes no DataFrame
        cols_presentes = [c for c in colunas_exibir.keys() if c in df_users.columns]
        df_exibicao = df_users[cols_presentes].copy()
        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        # Apresentar tabela ordenada por Pontos por omissão
        st.dataframe(
            df_exibicao.sort_values(by="Pontos", ascending=False),
            width="stretch",
            hide_index=True
        )

    @staticmethod
    def _renderizar_podio(df: pd.DataFrame, coluna_ordem: str, coluna_valor: str, sufixo: str, titulo: str):
        """Método auxiliar para desenhar o Top 5 formatado com medalhas."""
        st.markdown(f"#### {titulo}")
        
        # Ordena e seleciona os 5 primeiros
        top_5 = df.sort_values(by=coluna_ordem, ascending=False).head(5)

        medals = ["🥇 1º", "🥈 2º", "🥉 3º", "4º", "5º"]

        for idx, (_, row) in enumerate(top_5.iterrows()):
            posicao = medals[idx] if idx < len(medals) else f"{idx+1}º"
            
            with st.container():
                col_pos, col_nome, col_val = st.columns([1, 3, 2])

                with col_pos:
                    st.write(f"**{posicao}**")
                with col_nome:
                    st.write(f"👤 **{row['nome']}**")
                with col_val:
                    valor = row[coluna_valor]
                    st.write(f"`{valor}` {sufixo}")
            st.divider()