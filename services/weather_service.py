import requests


class WeatherService:
    # Coordenadas predefinidas
    ESPINHO = {"lat": 41.0072, "lon": -8.6410, "nome": "Espinho"}
    GAIA = {"lat": 41.1336, "lon": -8.6174, "nome": "Vila Nova de Gaia"}

    @staticmethod
    def obter_meteo(lat: float = None, lon: float = None) -> dict:
        """
        Obtém a temperatura atual.
        1. Se lat/lon forem fornecidos, usa a geolocalização.
        2. Se não forem, tenta Espinho.
        3. Se falhar, usa Vila Nova de Gaia como fallback.
        """
        if lat is not None and lon is not None:
            alvo_lat, alvo_lon, local_nome = lat, lon, "Localização Atual"
        else:
            alvo_lat, alvo_lon, local_nome = WeatherService.ESPINHO["lat"], WeatherService.ESPINHO["lon"], WeatherService.ESPINHO["nome"]

        # Primeira tentativa (Geolocalização do utilizador ou Espinho)
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={alvo_lat}&longitude={alvo_lon}&current_weather=true"
            response = requests.get(url, timeout=4).json()
            
            if "current_weather" in response:
                return {
                    "temp": response["current_weather"]["temperature"],
                    "wind": response["current_weather"]["windspeed"],
                    "local": local_nome
                }
        except Exception as e:
            print(f"⚠️ Erro ao obter meteo para {local_nome}: {e}. A tentar fallback (VN Gaia)...")

        # Fallback secundário (Vila Nova de Gaia)
        try:
            url_fallback = f"https://api.open-meteo.com/v1/forecast?latitude={WeatherService.GAIA['lat']}&longitude={WeatherService.GAIA['lon']}&current_weather=true"
            response = requests.get(url_fallback, timeout=4).json()
            
            if "current_weather" in response:
                return {
                    "temp": response["current_weather"]["temperature"],
                    "wind": response["current_weather"]["windspeed"],
                    "local": WeatherService.GAIA["nome"]
                }
        except Exception as e:
            print(f"❌ Erro no fallback de VN Gaia: {e}")

        return None