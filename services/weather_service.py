import requests


class WeatherService:
    ESPINHO = {"lat": 41.0072, "lon": -8.6410, "nome": "Espinho"}
    GAIA = {"lat": 41.1336, "lon": -8.6174, "nome": "Vila Nova de Gaia"}

    @staticmethod
    def _obter_nome_localidade(lat: float, lon: float) -> str:
        """Converte coordenadas GPS no nome da cidade/freguesia."""
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/reverse?latitude={lat}&longitude={lon}&limit=1"
            res = requests.get(url, timeout=3).json()
            if "results" in res and len(res["results"]) > 0:
                item = res["results"][0]
                # Tenta devolver o nome da localidade, concelho ou região
                return item.get("name") or item.get("admin2") or item.get("admin1") or "Localização Atual"
        except Exception:
            pass
        return "Localização Atual"

    @staticmethod
    def obter_meteo(lat: float = None, lon: float = None) -> dict:
        """Obtém a temperatura e o nome real do local."""
        if lat is not None and lon is not None:
            alvo_lat, alvo_lon = lat, lon
            local_nome = WeatherService._obter_nome_localidade(lat, lon)
        else:
            alvo_lat, alvo_lon = WeatherService.ESPINHO["lat"], WeatherService.ESPINHO["lon"]
            local_nome = WeatherService.ESPINHO["nome"]

        # 1. Tentativa principal (Geolocalização ou Espinho)
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
            print(f"⚠️ Erro no pedido principal de meteo ({local_nome}): {e}")

        # 2. Fallback (VN Gaia)
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