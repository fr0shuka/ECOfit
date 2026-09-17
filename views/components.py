import streamlit as st
from services.weather_service import WeatherService

try:
    from streamlit_js_eval import get_geolocation
    HAS_GEO = True
except ImportError:
    HAS_GEO = False


def renderizar_meteo_sidebar():
    """Renderiza o widget meteorológico no menu lateral dentro de um cartão estilizado."""
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 🌡️ Meteorologia")

    loc = None
    if HAS_GEO:
        try:
            loc = get_geolocation()
        except Exception:
            loc = None

    try:
        if loc and isinstance(loc, dict) and 'coords' in loc:
            meteo = WeatherService.obter_meteo(
                lat=loc['coords']['latitude'], 
                lon=loc['coords']['longitude']
            )
        else:
            meteo = WeatherService.obter_meteo()
    except Exception as e:
        meteo = None

    if meteo and isinstance(meteo, dict) and 'temp' in meteo:
        st.sidebar.markdown(
            """
            <style>
                div[data-testid="stSidebar"] [data-testid="stMetric"] {
                    background-color: #1e222a !important;
                    border: 1px solid #2e3440 !important;
                    border-left: 4px solid #FF4B4B !important;
                    padding: 12px 14px !important;
                    border-radius: 6px !important;
                    transition: all 0.2s ease-in-out !important;
                }

                div[data-testid="stSidebar"] [data-testid="stMetric"]:hover {
                    background-color: #242933 !important;
                    border-color: #FF4B4B !important;
                    transform: translateY(-2px);
                }

                div[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
                    font-size: 0.75rem !important;
                    color: #94a3b8 !important;
                    font-weight: 600 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                }
                
                div[data-testid="stSidebar"] [data-testid="stMetricValue"] {
                    font-size: 1.3rem !important;
                    font-weight: 700 !important;
                    color: #ffffff !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        with st.sidebar:
            local_nome = str(meteo.get('local', 'Localidade')).upper()
            temp_val = float(meteo.get('temp', 0.0))
            wind_val = float(meteo.get('wind', 0.0))

            st.metric(
                label=local_nome, 
                value=f"{temp_val:.1f} °C", 
                delta=f"{wind_val:.1f} km/h vento",
                delta_color="normal",
                help=f"Condições meteorológicas obtidas em tempo real para {local_nome}."
            )
    else:
        st.sidebar.caption("Sem dados meteorológicos de momento.")