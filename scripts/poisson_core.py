import numpy as np
from scipy.stats import poisson

def calcular_probabilidades_partido(home_expectancy, away_expectancy, max_goles=8):
    """
    Calcula la matriz de probabilidades para un partido.
    home_expectancy: xG del equipo local (o equipo A)
    away_expectancy: xG del equipo visitante (o equipo B)
    """
    # Creamos las distribuciones de probabilidad para cada equipo
    prob_home = [poisson.pmf(i, home_expectancy) for i in range(max_goles)]
    prob_away = [poisson.pmf(i, away_expectancy) for i in range(max_goles)]
    
    # Matriz de resultados exactos (Marcadores)
    matriz_resultados = np.outer(prob_home, prob_away)
    
    # Calculamos 1X2
    prob_empate = np.sum(np.diag(matriz_resultados))
    prob_local = np.sum(np.tril(matriz_resultados, -1))
    prob_visitante = np.sum(np.triu(matriz_resultados, 1))
    
    return {
        "Local": round(prob_local * 100, 2),
        "Empate": round(prob_empate * 100, 2),
        "Visitante": round(prob_visitante * 100, 2),
        "Over_2.5": round((1 - np.sum([matriz_resultados[i, j] for i in range(max_goles) for j in range(max_goles) if i+j <= 2])) * 100, 2)
    }

# Ejemplo de uso con datos de un partido top del mundial pasado
# Supongamos que basándonos en Qatar 2022, el xG de Francia es 2.1 y el de Marruecos es 0.8
proyeccion = calcular_probabilidades_partido(2.1, 0.8)

print(f"Probabilidades del encuentro:")
print(f"Ganar Local: {proyeccion['Local']}%")
print(f"Empate: {proyeccion['Empate']}%")
print(f"Ganar Visitante: {proyeccion['Visitante']}%")
print(f"Más de 2.5 goles: {proyeccion['Over_2.5']}%")
