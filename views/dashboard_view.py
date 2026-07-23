import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date
from models.activity_model import ActivityModel

class DashboardView:
    @staticmethod
    def renderizar_formulario():
        """Renderiza a zona de registo de atividade e o painel analítico completo."""
        
        # --- ZONA 1: FORMULÁRIO DE REGISTO MANUAL ---
        st.markdown("### 🚀 Registar Atividade")
        
        with st.form("form_atividade", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                km = st.number_input("Quilómetros Corridos (km)", min_value=0.0, step=0.1)
                
                # ⏱️ Divisão de Tempo: Horas e Minutos
                
                col_h, col_m = st.columns(2)
                with col_h:
                    horas = st.number_input("Horas", min_value=0, step=1, value=0)
                with col_m:
                    minutos_input = st.number_input("Minutos", min_value=0, max_value=59, step=1, value=0)
            
            with col2:
                copos = st.number_input("Copos de Água", min_value=0, step=1)
                fruta = st.number_input("Peças de Fruta", min_value=0, step=1)
            
            submetido = st.form_submit_button("Salvar Atividade", use_container_width=True)
            
            if submetido:
                # 🧹 LIMPEZA E CONVERSÃO: Transforma Horas + Minutos no Total de Minutos para a BD
                total_minutos = int((horas * 60) + minutos_input)
                
                if km == 0 and total_minutos == 0 and copos == 0 and fruta == 0:
                    st.warning("⚠️ Preenche pelo menos um dos campos para registar a atividade.")
                else:
                    id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
                    
                    # Cálculo de pontos com o tempo limpo/convertido
                    pontos = int((km * 10) + (total_minutos * 1) + (copos * 2) + (fruta * 5))
                    
                    payload = {
                        "utilizador_id": id_utilizador,
                        "data_registo": str(date.today()),
                        "km_corridos": km,
                        "minutos_treino": total_minutos, # Envia o total limpo em minutos
                        "copos_agua": copos,
                        "pecas_fruta": fruta,
                        "pontos_ganhos": pontos,
                        "tipo_insercao": "Manual",
                        "temperatura": 20.0,
                        "condicao_clima": "Manual"
                    }
                    
                    if ActivityModel.salvar_atividade(payload):
                        st.success(f"🎯 Atividade registada com sucesso! Ganhaste +{pontos} pontos ({total_minutos} min acumulados).")
                        st.rerun()

        st.markdown("---")

        # --- ZONA 2: PAINEL ANALÍTICO (KPIs + GRÁFICO PLOTLY) ---
        DashboardView.renderizar_graficos_e_kpis()

    @staticmethod
    def renderizar_graficos_e_kpis():
        """Calcula métricas com Pandas e renderiza os gráficos do Plotly."""
        st.markdown("### 📊 Análise de Performance e Métricas")
        
        id_utilizador = st.session_state['utilizador_logado']['utilizador_id']
        registos_brutos = ActivityModel.buscar_por_utilizador(id_utilizador)
        
        if not registos_brutos:
            st.info("🌱 Ainda não tens atividades registadas. Insere o teu primeiro treino acima!")
            return

        # 1. Tratamento e Estruturação dos Dados com Pandas
        df = pd.DataFrame(registos_brutos)
        df['data_registo'] = pd.to_datetime(df['data_registo'])
        df['km_corridos'] = pd.to_numeric(df['km_corridos'], errors='coerce').fillna(0)
        df['minutos_treino'] = pd.to_numeric(df['minutos_treino'], errors='coerce').fillna(0)
        df['copos_agua'] = pd.to_numeric(df['copos_agua'], errors='coerce').fillna(0)
        df['pontos_ganhos'] = pd.to_numeric(df['pontos_ganhos'], errors='coerce').fillna(0)
        df = df.sort_values(by='data_registo', ascending=True)

        # 2. Exibição dos Cartões KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏃 Distância", f"{df['km_corridos'].sum():.1f} km")
        col2.metric("⏱️ Tempo Total", f"{int(df['minutos_treino'].sum())} min")
        col3.metric("💧 Hidratação", f"{int(df['copos_agua'].sum())} copos")
        col4.metric("🌱 Pontos", f"{int(df['pontos_ganhos'].sum())} pts")

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Geração do Gráfico Interativo com Plotly
        df_diario = df.groupby(df['data_registo'].dt.strftime('%Y-%m-%d'))['pontos_ganhos'].sum().reset_index()
        
        fig_bar = px.bar(
            df_diario,
            x='data_registo',
            y='pontos_ganhos',
            title="📈 Evolução Diária de Pontuações",
            labels={'data_registo': 'Data', 'pontos_ganhos': 'Pontos'},
            color_discrete_sequence=['#2E7D32']
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        
        st.plotly_chart(fig_bar, use_container_width=True)