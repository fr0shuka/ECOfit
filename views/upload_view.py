import time
import streamlit as st
import pandas as pd
from controllers.file_controller import FileController
from models.activity_model import ActivityModel


class UploadView:
    @staticmethod
    def renderizar_zona_upload():
        st.markdown("### Sincronização de Ficheiro")
        st.caption("Importação com pré-visualização e validação de dados de atividade")
        
        utilizador = st.session_state.get('utilizador_logado')
        if not utilizador:
            st.error("Utilizador não autenticado.")
            return

        utilizador_id = utilizador.get('utilizador_id') or utilizador.get('id')

        tipos_disponiveis = ActivityModel.obter_tipos_atividade()
        mapa_tipos = {t['nome']: t['tipo_atividade_id'] for t in tipos_disponiveis} if tipos_disponiveis else {"Corrida": 1}
        nomes_opcoes = list(mapa_tipos.keys())

        with st.container(border=True):
            ficheiro = st.file_uploader(
                "Selecione o ficheiro de atividades (GPX, TCX, CSV, etc.)", 
                type=["csv", "xlsx", "xls", "json", "gpx", "fit", "txt", "xml", "tcx"]
            )

            if ficheiro is not None:
                # Obter pré-visualização inteligente
                info_preview = FileController.pre_visualizar_ficheiro(ficheiro)

                if info_preview and info_preview.get("sucesso"):
                    st.success("✅ Ficheiro lido com sucesso! Valide os dados detetados abaixo:")
                    
                    with st.form(key="form_preview_upload"):
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            prev_km = st.number_input("Distância (km)", min_value=0.0, value=float(info_preview.get("km", 0.0)), step=0.1)
                        with c2:
                            prev_min = st.number_input("Duração (min)", min_value=1, value=int(info_preview.get("minutos", 1)), step=1)
                        with c3:
                            st.text_input("Data Detetada", value=str(info_preview.get("data_real", "Hoje")), disabled=True)

                        # Detetar modalidade sugerida pelo ficheiro (ex: cycling -> Ciclismo)
                        sugestao_id = info_preview.get("tipo_sugerido_id")
                        idx_sugerido = 0
                        for nome, tid in mapa_tipos.items():
                            if tid == sugestao_id:
                                idx_sugerido = nomes_opcoes.index(nome)
                                break

                        modalidade_escolhida = st.selectbox(
                            "Modalidade Detetada / Confirmada:",
                            options=nomes_opcoes,
                            index=idx_sugerido
                        )

                        btn_confirmar = st.form_submit_button("Confirmar e Inserir na Base de Dados", type="primary", width="stretch")

                        if btn_confirmar:
                            tipo_id_final = mapa_tipos[modalidade_escolhida]
                            sucesso_gravacao = FileController.gravar_atividade_com_dados_ajustados(
                                utilizador_id=utilizador_id,
                                km=prev_km,
                                minutos=prev_min,
                                tipo_atividade_id=tipo_id_final,
                                nome_fonte=ficheiro.name,
                                data_real=info_preview.get("data_real")
                            )

                            if sucesso_gravacao:
                                st.toast("Atividade sincronizada e guardada com sucesso!")
                                time.sleep(0.8)
                                st.rerun()
                            else:
                                st.error("Erro ao guardar a atividade na base de dados.")
                else:
                    st.error("❌ Não foi possível extrair métricas válidas deste ficheiro.")

        st.markdown("---")

        # --- SECÇÃO 2: HISTÓRICO ---
        st.markdown("##### Histórico de Ficheiros Sincronizados")
        df_historico = FileController.obter_historico_atividades_ficheiro(utilizador_id)

        if df_historico is None or df_historico.empty:
            st.info("Não existem atividades registadas via ficheiro de momento.")
            return

        if 'distancia_km' not in df_historico.columns and 'km_corridos' in df_historico.columns:
            df_historico['distancia_km'] = df_historico['km_corridos']

        colunas_exibir = {
            'data_registo': 'Data da Atividade',
            'modalidade': 'Modalidade',
            'distancia_km': 'Distância (km)',
            'minutos_treino': 'Duração (min)',
            'pontos_ganhos': 'Pontos Obtidos'
        }

        cols_presentes = [c for c in colunas_exibir.keys() if c in df_historico.columns]
        df_exibicao = df_historico[cols_presentes].copy()
        
        if 'data_registo' in df_exibicao.columns:
            df_exibicao['data_registo'] = pd.to_datetime(df_exibicao['data_registo'], errors='coerce').dt.strftime('%Y-%m-%d %H:%M')

        df_exibicao.rename(columns=colunas_exibir, inplace=True)

        st.dataframe(
            df_exibicao,
            width="stretch",
            hide_index=True
        )