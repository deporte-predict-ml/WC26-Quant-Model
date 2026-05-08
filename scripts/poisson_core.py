import json
import os
import numpy as np
from scipy.stats import poisson
from datetime import datetime

def cargar_datos():
    ruta = "data/wc2022_stats.json"
    if not os.path.exists(ruta):
        print("Ponte trucha, no encuentro el archivo. Primero corre el extractor.")
        return None
    with open(ruta, "r") as f:
        return json.load(f)

def calcular_promedios_con_peso(data):
    stats_equipos = {}
    hoy = datetime.now()
    
    partidos = data.get("response", [])
    for p in partidos:
        home = p["teams"]["home"]["name"]
        away = p["teams"]["away"]["name"]
        goles_h = p["goals"]["home"]
        goles_a = p["goals"]["away"]
        
        # Jalamos la fecha del partido desde la API
        fecha_str = p["fixture"]["date"] 
        
        if goles_h is None or goles_a is None: continue

        # Cortamos el timezone para que no haga bronca al convertir la fecha
        fecha_partido = datetime.fromisoformat(fecha_str.replace('Z', '+00:00')[:19])
        dias_pasados = (hoy - fecha_partido).days
        
        # El jale clave: Decaimiento exponencial
        # Ajustamos el 0.001 para que en 4 años el peso baje drásticamente
        peso = np.exp(-0.001 * dias_pasados)

        for equipo in [home, away]:
            if equipo not in stats_equipos:
                stats_equipos[equipo] = {"anotados_ponderados": 0, "partidos_ponderados": 0}
        
        # Multiplicamos los goles por el peso del partido
        stats_equipos[home]["anotados_ponderados"] += goles_h * peso
        stats_equipos[home]["partidos_ponderados"] += peso
        
        stats_equipos[away]["anotados_ponderados"] += goles_a * peso
        stats_equipos[away]["partidos_ponderados"] += peso

    return stats_equipos

def poisson_model(home_team, away_team, stats):
    if home_team not in stats or away_team not in stats:
        return "Faltan datos de esa selección, carnal"
    
    # Sacamos la media real tomando en cuenta el tiempo
    exp_home = stats[home_team]["anotados_ponderados"] / stats[home_team]["partidos_ponderados"]
    exp_away = stats[away_team]["anotados_ponderados"] / stats[away_team]["partidos_ponderados"]
    
    max_goles = 8
    prob_h = [poisson.pmf(i, exp_home) for i in range(max_goles)]
    prob_a = [poisson.pmf(i, exp_away) for i in range(max_goles)]
    
    matriz = np.outer(prob_h, prob_a)
    
    return {
        "Local": round(np.sum(np.tril(matriz, -1)) * 100, 2),
        "Empate": round(np.sum(np.diag(matriz)) * 100, 2),
        "Visitante": round(np.sum(np.triu(matriz, 1)) * 100, 2)
    }

# Ejecución principal
data = cargar_datos()
if data:
    stats = calcular_promedios_con_peso(data)
    res = poisson_model("Argentina", "France", stats)
    print(f"Predicción al tiro (con peso de tiempo): {res}")
