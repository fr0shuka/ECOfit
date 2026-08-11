import time
import streamlit as st
import pandas as pd
from controllers.file_controller import FileController


class UploadView:
    @staticmethod
    def renderizar_zona_upload():
        st.subheader("📥 Sincronizar Ficheiro de Atividades")
        
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador:
            return

        utilizador_id = utilizador['utilizador_id']

        # --- SEÇÃO 1: UPLOAD ---
        ficheiro = st.file_uploader(
            "Seleciona o ficheiro de atividades (CSV ou Excel)", 
            type=["csv", "xlsx"]
        )

        if ficheiro is not None:
            if st.button("🚀 Processar Ficheiro", type="primary", use_container_width=True):
                with st.spinner("A processar e a guardar os dados..."):
                    sucesso = FileController.processar_ficheiro(ficheiro, utilizador_id)

                if sucesso:
                    st.toast(f"Ficheiro '{ficheiro.name}' processado com sucesso!", icon="🎉")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("❌ Erro ao processar o ficheiro.")

        st.markdown("---")

        # --- SEÇÃO 2: TABELA DE HISTÓRICO DE DADOS SINCRONIZADOS ---
        st.markdown("### 📋 Atividades Sincronizadas via Ficheiro")

        df_historico = FileController.obter_historico_atividades_ficheiro(utilizador_id)

        if df_historico.empty:
            st.info("Ainda não existem atividades registadas via ficheiro.")
            return

        # Mapeamento para nomes amigáveis no ecrã
        colunas_exibir = {
            'data_registo': 'Data da Atividade',
            'km_corridos': 'Distância (Km)',
            'minutos_treino': 'Duração (min)',
            'pontos_ganhos': 'Pontos Obtidos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df_historico.columns]
        df_exibicao = df_historico[cols_presentes].copy()
        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao,
            use_container_width=True,
            hide_index=True
        )