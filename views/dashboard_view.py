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
                
                /* Cartão do st.metric com cinza executivo e destaque lateral verde */
                [data-testid="stMetric"] {
                    background-color: #1e222a !important;
                    border: 1px solid #2e3440 !important;
                    border-left: 4px solid #10b981 !important; /* Verde EcoFit */
                    padding: 12px 14px !important;
                    border-radius: 6px !important;
                    transition: all 0.2s ease-in-out !important;
                }

                /* Efeito Hover nos Cartões */
                [data-testid="stMetric"]:hover {
                    background-color: #242933 !important;
                    border-color: #10b981 !important;
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
        
        # --- ZONA 1: FORMULÁRIO DE REGISTO MANUAL ---
        st.markdown("Registo de Atividade")
        st.caption("Insira os dados do treino e hábitos diários.")
        
        with st.form("form_atividade", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                km = st.number_input("Quilómetros Corridos (km)", min_value=0.0, step=0.1)
                
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
                
                if km == 0 and total_minutos == 0 and copos == 0 and fruta == 0:
                    st.warning("Preencha pelo menos um dos campos para registar a atividade.")
                else:
                    id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
                    pontos = int((km * 10) + (total_minutos * 1) + (copos * 2) + (fruta * 5))
                    
                    payload = {
                        "utilizador_id": id_utilizador,
                        "data_registo": str(date.today()),
                        "km_corridos": km,
                        "minutos_treino": total_minutos,
                        "copos_agua": copos,
                        "pecas_fruta": fruta,
                        "pontos_ganhos": pontos,
                        "tipo_insercao": "Manual",
                        "temperatura": float(temp_real),
                        "condicao_clima": "Manual"
                    }
                    
                    if ActivityModel.salvar_atividade(payload):
                        st.toast(f"Atividade registada com sucesso (+{pontos} pts).", icon=None)
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

        df = pd.DataFrame(registos_brutos)
        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['km_corridos'] = pd.to_numeric(df['km_corridos'], errors='coerce').fillna(0)
        df['minutos_treino'] = pd.to_numeric(df['minutos_treino'], errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df['copos_agua'], errors='coerce').fillna(0)
        df['pecas_fruta'] = pd.to_numeric(df.get('pecas_fruta', 0), errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df['pontos_ganhos'], errors='coerce').fillna(0)
        df = df.sort_values(by='data_registo', ascending=True)

       # Cartões KPI Em Linha (Com Tooltips nativos e nomes otimizados)
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            label="Distância", 
            value=f"{df['km_corridos'].sum():.1f} km",
            help="Total de quilómetros percorridos em corridas e caminhadas."
        )

        col2.metric(
            label="Tempo", 
            value=f"{int(df['minutos_treino'].sum())} min",
            help="Tempo acumulado gasto em sessões de treino."
        )

        col3.metric(
            label="Hidratação", 
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
            help="Pontuação total acumulada com base nas atividades registadas."
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico Executivo com Plotly
        df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()
        
        fig_bar = px.bar(
            df_diario,
            x='data_registo',
            y='pontos_ganhos',
            title="Evolução Diária de Pontuações",
            labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos'},
            color_discrete_sequence=['#4da6ff']
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