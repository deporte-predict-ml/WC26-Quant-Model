import os
import json
import requests

# Jalamos el token directo desde los secretos de GitHub
API_KEY = os.getenv("API_SPORTS_KEY")

def fetch_wc22_data():
    # Endpoint de ejemplo (ajustar según tu API, esto es estilo API-football)
    url = "https://v3.football.api-sports.io/fixtures"
    
    # El Mundial suele ser la liga ID 1 en varias APIs, temporada 2022
    querystring = {"league": "1", "season": "2022"}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "v3.football.api-sports.io"
    }

    try:
        print("Jalando la info del mundial pasado...")
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status() # Nos avisa si la API nos batea
        data = response.json()
        
        # Nos aseguramos de que la carpeta exista y guardamos el archivo
        os.makedirs("data", exist_ok=True)
        with open("data/wc2022_stats.json", "w") as f:
            json.dump(data, f, indent=4)
            
        print("Datos guardados al tiro en data/wc2022_stats.json")
        
    except Exception as e:
        print(f"Hubo un pedo al conectar con la API: {e}")

if __name__ == "__main__":
    if not API_KEY:
        print("¡Ojo! No se encontró la API Key. Revisa los Secrets en GitHub.")
    else:
        fetch_wc22_data()
