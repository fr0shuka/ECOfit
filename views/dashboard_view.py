import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from models.activity_model import ActivityModel
from services.weather_service import WeatherService


class DashboardView:
    @staticmethod
    def _injetar_estilos():
        st.markdown("""
            <style>
                .main .block-container {
                    padding-top: 1.5rem;
                    max-width: 1100px;
                }
                
                /* Cartão do st.metric */
                [data-testid="stMetric"] {
                    background-color: #1e222a !important;
                    border: 1px solid #2e3440 !important;
                    border-left: 4px solid #FF4B4B !important;
                    padding: 12px 14px !important;
                    border-radius: 6px !important;
                    transition: all 0.2s ease-in-out !important;
                }

                /* Efeito Hover nos Cartões */
                [data-testid="stMetric"]:hover {
                    background-color: #242933 !important;
                    border-color: #FF4B4B !important;
                    transform: translateY(-2px);
                }

                /* Título / Rótulo da Métrica */
                [data-testid="stMetricLabel"] {
                    font-size: 0.75rem !important;
                    color: #94a3b8 !important;
                    font-weight: 600 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                }

                /* Valor Numérico */
                [data-testid="stMetricValue"] {
                    font-size: 1.3rem !important;
                    font-weight: 700 !important;
                    color: #ffffff !important;
                }
            </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def renderizar_formulario():
        """Renderiza a zona de registo de atividade e o painel analítico completo."""
        DashboardView._injetar_estilos()
        temp_real = WeatherService.obter_temperatura_atual()
        
        # Obter modalidades da BD
        tipos_atividade = ActivityModel.obter_tipos_atividade()
        if not tipos_atividade:
            st.error("Nenhuma modalidade disponível na base de dados.")
            return

        mapa_modalidades = {t["nome"]: t for t in tipos_atividade}

        # --- ZONA 1: FORMULÁRIO DE REGISTO MANUAL ---
        st.markdown("### Registo de Atividade")
        st.caption("Insira os dados do treino e hábitos diários.")
        
        with st.form("form_atividade", clear_on_submit=True):
            col_mod, col_clima = st.columns(2)
            
            with col_mod:
                modalidade_nome = st.selectbox("Modalidade", list(mapa_modalidades.keys()))
                modalidade_obj = mapa_modalidades[modalidade_nome]
            
            with col_clima:
                condicao_clima = st.selectbox("Condição Atmosférica", ["Ensolarado", "Nublado", "Chuvoso", "Vento", "Frio"])

            col1, col2 = st.columns(2)
            
            with col1:
                distancia = st.number_input("Distância (km)", min_value=0.0, step=0.1)
                
                col_h, col_m = st.columns(2)
                with col_h:
                    horas = st.number_input("Horas", min_value=0, step=1, value=0)
                with col_m:
                    minutos_input = st.number_input("Minutos", min_value=0, max_value=59, step=1, value=0)
            
            with col2:
                copos = st.number_input("Copos de Água", min_value=0, step=1)
                fruta = st.number_input("Peças de Fruta", min_value=0, step=1)

            submetido = st.form_submit_button("Salvar Atividade", type="primary", use_container_width=True)
            
            if submetido:
                total_minutos = int((horas * 60) + minutos_input)
                
                if distancia == 0 and total_minutos == 0 and copos == 0 and fruta == 0:
                    st.warning("Preencha pelo menos um dos campos para registar a atividade.")
                else:
                    id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
                    
                    # Cálculo com o fator da modalidade
                    fator = float(modalidade_obj.get("fator_pontuacao", 1.0))
                    pontos_treino = (distancia * 10 + total_minutos * 1) * fator
                    pontos_habitos = (copos * 2) + (fruta * 5)
                    pontos_totais = int(pontos_treino + pontos_habitos)
                    
                    payload = {
                        "utilizador_id": id_utilizador,
                        "tipo_atividade_id": modalidade_obj["tipo_atividade_id"],
                        "data_registo": str(date.today()),
                        "distancia_km": distancia,
                        "minutos_treino": total_minutos,
                        "copos_agua": copos,
                        "pecas_fruta": fruta,
                        "pontos_ganhos": pontos_totais,
                        "tipo_insercao": "Manual",
                        "temperatura": float(temp_real) if temp_real else None,
                        "condicao_clima": condicao_clima
                    }
                    
                    if ActivityModel.salvar_atividade(payload):
                        st.toast(f"Atividade registada com sucesso (+{pontos_totais} pts).")
                        st.rerun()

        st.markdown("---")

        # --- ZONA 2: PAINEL ANALÍTICO ---
        DashboardView.renderizar_graficos_e_kpis()

    @staticmethod
    def renderizar_graficos_e_kpis():
        """Calcula métricas com Pandas e renderiza gráficos com Plotly."""
        st.markdown("##### Análise de Performance e Métricas")
        
        id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
        registos_brutos = ActivityModel.buscar_por_utilizador(id_utilizador)
        
        if not registos_brutos:
            st.info("Não existem atividades registadas para este utilizador.")
            return

        # Achatar a estrutura do JOIN para facilidade no Pandas
        dados_flat = []
        for reg in registos_brutos:
            item = dict(reg)
            info_modalidade = item.get("bd_tipos_atividade") or {}
            item["modalidade"] = info_modalidade.get("nome", "N/A")
            dados_flat.append(item)

        df = pd.DataFrame(dados_flat)
        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['distancia_km'] = pd.to_numeric(df.get('distancia_km', 0), errors='coerce').fillna(0)
        df['minutos_treino'] = pd.to_numeric(df.get('minutos_treino', 0), errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df.get('copos_agua', 0), errors='coerce').fillna(0)
        df['pecas_fruta'] = pd.to_numeric(df.get('pecas_fruta', 0), errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df.get('pontos_ganhos', 0), errors='coerce').fillna(0)
        df = df.sort_values(by='data_registo', ascending=True)

        # 1. Cálculo formatado do tempo
        total_minutos = int(df['minutos_treino'].sum())
        horas = total_minutos // 60
        minutos_resto = total_minutos % 60
        tempo_formatado = f"{horas}h {minutos_resto}m" if horas > 0 else f"{minutos_resto} min"

        # 2. Cartões KPI em Linha
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            label="Distância", 
            value=f"{df['distancia_km'].sum():.1f} km",
            help="Total de quilómetros percorridos acumulados."
        )

        col2.metric(
            label="Tempo", 
            value=tempo_formatado,
            help="Tempo acumulado gasto em sessões de treino."
        )

        col3.metric(
            label="Água", 
            value=f"{int(df['copos_agua'].sum())} copos",
            help="Quantidade total de copos de água ingeridos."
        )

        col4.metric(
            label="Fruta", 
            value=f"{int(df['pecas_fruta'].sum())} peças",
            help="Doses de fruta consumidas durante o período."
        )

        col5.metric(
            label="Pontos", 
            value=f"{int(df['pontos_ganhos'].sum())} pts",
            help="Pontuação total acumulada com base nas atividades e modalidades."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Chamar o Simulador Preditivo
        DashboardView.renderizar_previsao_pontucao(df)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # 4. Gráfico de Pontos por Data e Modalidade
        df_diario = df.groupby([df['data_registo'].dt.strftime('%Y-%m-%d'), 'modalidade'])['pontos_ganhos'].sum().reset_index()
        
        fig_bar = px.bar(
            df_diario,
            x='data_registo',
            y='pontos_ganhos',
            color='modalidade',
            title="Evolução Diária de Pontuações por Modalidade",
            labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos', 'modalidade': 'Modalidade'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(family="Inter, sans-serif", size=12, color="#94a3b8"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#2e3440")
        )
        
        with st.container(border=True):
            st.plotly_chart(fig_bar, use_container_width=True)

    @staticmethod
    def renderizar_previsao_pontucao(df_treinos):
        """
        Simulador de previsão de pontuação para o atleta com base no histórico 
        e regras de negócio do EcoFit (RVCC Nível 5 - Modelação Preditiva Simples).
        """
        st.markdown("---")
        st.markdown("##### 🎯 Simulador Preditivo de Metas e Pontuação")
        st.caption("Projeção analítica do impacto de novos treinos ou hábitos na pontuação total acumulada.")

        if df_treinos.empty:
            st.info("Registe atividades para ativar o simulador preditivo.")
            return

        # 1. Obter pontos atuais do utilizador
        pontos_totais_atuais = int(df_treinos['pontos_ganhos'].sum()) if 'pontos_ganhos' in df_treinos.columns else 0
        
        # 2. Calcular a média de pontos por quilómetro ou por sessão do utilizador (modelo base)
        df_fisico = df_treinos[(df_treinos['distancia_km'] > 0)]
        if not df_fisico.empty:
            media_pontos_por_treino = df_fisico['pontos_ganhos'].mean()
        else:
            media_pontos_por_treino = 60.0

        # Layout de colunas para o simulador interativo
        col_sim1, col_sim2 = st.columns(2)

        with col_sim1:
            st.markdown("###### 🏃‍♂️ Simular por Quilómetros Adicionais")
            km_extra = st.slider("Quantos km pretende percorrer na próxima meta?", min_value=1.0, max_value=50.0, value=10.0, step=1.0, key="slider_km_extra")
            
            min_estimados = km_extra * 6
            pontos_projetados_km = int((km_extra * 10) + (min_estimados * 1))
            novo_total_km = pontos_totais_atuais + pontos_projetados_km

            st.info(f"💡 Se realizar **{km_extra} km** (cerca de {int(min_estimados)} min de exercício), irá somar **+{pontos_projetados_km} pontos**, elevando o seu pecúlio para **{novo_total_km} pontos**.")

        with col_sim2:
            st.markdown("###### 💧🍎 Simular por Hábitos Saudáveis")
            dias_meta = st.slider("Manter hidratação e fruta rigorosa durante quantos dias?", min_value=1, max_value=30, value=7, step=1, key="slider_dias_habito")
            
            pontos_por_dia_habito = 40 
            pontos_projetados_habitos = dias_meta * pontos_por_dia_habito
            novo_total_habitos = pontos_totais_atuais + pontos_projetados_habitos

            st.success(f"🌱 Cumprindo os hábitos durante **{dias_meta} dias**, conquistará **+{pontos_projetados_habitos} pontos**, atingindo um total acumulado de **{novo_total_habitos} pontos**.")

        # Mensagem de objetivo / meta inteligente
        st.markdown("<br>", unsafe_allow_html=True)
        meta_alvo = st.number_input("Definir meta de pontuação:", min_value=100, max_value=10000, value=max(1000, pontos_totais_atuais + 500), step=50, key="input_meta_alvo")
        
        if meta_alvo > pontos_totais_atuais:
            pontos_em_falta = meta_alvo - pontos_totais_atuais
            treinos_necessarios = max(1, int(pontos_em_falta / max(1, media_pontos_por_treino)))
            
            st.warning(f"**Análise de Meta:** Faltam-lhe **{pontos_em_falta} pontos** para atingir o objetivo de **{meta_alvo} pontos**. Com base no seu ritmo histórico, precisará de realizar aproximadamente **{treinos_necessarios} sessões** semelhantes à sua média para lá chegar!")
        else:
            st.balloons()
            st.success("Parabéns! Já ultrapassou a meta de pontuação definida.")