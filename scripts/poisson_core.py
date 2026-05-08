# scripts/poisson_core.py
"""
Núcleo del modelo Poisson Bivariado para predicción de partidos
Implementa decaimiento exponencial y cálculo de xG
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import numpy as np
from scipy.stats import poisson
from dataclasses import dataclass, asdict

# Configuración
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Config

# Setup logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(f"{Config.LOGS_DIR}/poisson_core.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TeamStats:
    """Estructura para estadísticas de equipo"""
    name: str
    matches_weighted: float
    goals_weighted: float
    xg_average: float
    last_match_date: Optional[str] = None


@dataclass
class MatchPrediction:
    """Estructura para predicción de partido"""
    home_team: str
    away_team: str
    prob_home: float
    prob_draw: float
    prob_away: float
    xg_home: float
    xg_away: float
    exact_scores: Dict[str, float]
    over_under: Dict[str, float]
    confidence: float
    value_bet: bool
    timestamp: str


class PoissonModel:
    """Modelo Poisson Bivariado para predicción deportiva"""
    
    def __init__(self, decay_lambda: float = None):
        self.decay_lambda = decay_lambda or Config.DECAY_LAMBDA
        self.max_goals = Config.MAX_GOALS_PROJECTION
        self.min_matches = Config.MIN_MATCHES_REQUIRED
        self.team_stats: Dict[str, TeamStats] = {}
    
    def load_data(self, filepath: str = None) -> Optional[Dict]:
        """
        Carga datos históricos desde JSON
        
        Args:
            filepath: Ruta al archivo JSON
            
        Returns:
            Datos cargados o None
        """
        if filepath is None:
            filepath = os.path.join(Config.DATA_DIR, Config.HISTORICAL_DATA_FILE)
        
        if not os.path.exists(filepath):
            logger.error(f"❌ Archivo no encontrado: {filepath}")
            return None
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"✅ {len(data.get('response', []))} partidos cargados")
            return data
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parseando JSON: {e}")
            return None
    
    def calculate_weighted_stats(self, data: Dict) -> Dict[str, TeamStats]:
        """
        Calcula estadísticas ponderadas por tiempo
        
        Args:
            data: Datos de partidos
            
        Returns:
            Diccionario de estadísticas por equipo
        """
        stats = {}
        today = datetime.now(timezone.utc)
        matches = data.get("response", [])
        
        for match in matches:
            try:
                home = match["teams"]["home"]["name"]
                away = match["teams"]["away"]["name"]
                goals_h = match["goals"]["home"]
                goals_a = match["goals"]["away"]
                date_str = match["fixture"]["date"]
                
                # Parsear fecha
                date_str = date_str.replace('Z', '+00:00')
                match_date = datetime.fromisoformat(date_str)
                days_ago = (today - match_date).days
                
                # Calcular peso exponencial
                weight = np.exp(-self.decay_lambda * days_ago)
                
                # Inicializar equipos si no existen
                for team in [home, away]:
                    if team not in stats:
                        stats[team] = {
                            "goals_weighted": 0.0,
                            "matches_weighted": 0.0,
                            "last_match": match_date
                        }
                
                # Acumular estadísticas
                stats[home]["goals_weighted"] += goals_h * weight
                stats[home]["matches_weighted"] += weight
                stats[home]["last_match"] = max(stats[home]["last_match"], match_date)
                
                stats[away]["goals_weighted"] += goals_a * weight
                stats[away]["matches_weighted"] += weight
                stats[away]["last_match"] = max(stats[away]["last_match"], match_date)
                
            except (KeyError, ValueError) as e:
                logger.warning(f"Partido inválido saltado: {e}")
                continue
        
        # Convertir a TeamStats y calcular xG
        self.team_stats = {}
        for team, data_team in stats.items():
            if data_team["matches_weighted"] >= self.min_matches:
                xg = data_team["goals_weighted"] / data_team["matches_weighted"]
                self.team_stats[team] = TeamStats(
                    name=team,
                    matches_weighted=round(data_team["matches_weighted"], 2),
                    goals_weighted=round(data_team["goals_weighted"], 2),
                    xg_average=round(xg, 3),
                    last_match_date=data_team["last_match"].isoformat()
                )
        
        logger.info(f"✅ {len(self.team_stats)} equipos con estadísticas válidas")
        return self.team_stats
    
    def calculate_exact_scores(self, xg_home: float, xg_away: float) -> Dict[str, float]:
        """
        Calcula probabilidades de marcadores exactos
        
        Args:
            xg_home: Expected Goals local
            xg_away: Expected Goals visitante
            
        Returns:
            Diccionario de probabilidades por marcador
        """
        prob_h = [poisson.pmf(i, xg_home) for i in range(self.max_goals + 1)]
        prob_a = [poisson.pmf(i, xg_away) for i in range(self.max_goals + 1)]
        
        exact_scores = {}
        for h in range(self.max_goals + 1):
            for a in range(self.max_goals + 1):
                score_key = f"{h}-{a}"
                exact_scores[score_key] = round(prob_h[h] * prob_a[a] * 100, 3)
        
        return exact_scores
    
    def calculate_over_under(self, xg_home: float, xg_away: float) -> Dict[str, float]:
        """
        Calcula probabilidades Over/Under
        
        Args:
            xg_home: Expected Goals local
            xg_away: Expected Goals visitante
            
        Returns:
            Diccionario de probabilidades O/U
        """
        prob_h = [poisson.pmf(i, xg_home) for i in range(self.max_goals + 1)]
        prob_a = [poisson.pmf(i, xg_away) for i in range(self.max_goals + 1)]
        matriz = np.outer(prob_h, prob_a)
        
        total_goals_prob = {}
        for total in range(self.max_goals * 2):
            prob = 0
            for h in range(self.max_goals + 1):
                a = total - h
                if 0 <= a <= self.max_goals:
                    prob += matriz[h, a]
            total_goals_prob[total] = prob
        
        over_under = {
            "Over_1.5": round((1 - total_goals_prob.get(0, 0) - total_goals_prob.get(1, 0)) * 100, 2),
            "Over_2.5": round((1 - sum(total_goals_prob.get(i, 0) for i in range(3))) * 100, 2),
            "Over_3.5": round((1 - sum(total_goals_prob.get(i, 0) for i in range(4))) * 100, 2),
            "Under_2.5": round(sum(total_goals_prob.get(i, 0) for i in range(3)) * 100, 2),
        }
        
        return over_under
    
    def predict_match(self, home_team: str, away_team: str) -> Optional[MatchPrediction]:
        """
        Genera predicción completa para un partido
        
        Args:
            home_team: Nombre del equipo local
            away_team: Nombre del equipo visitante
            
        Returns:
            MatchPrediction o None si faltan datos
        """
        if home_team not in self.team_stats:
            logger.warning(f"⚠️ Sin datos para {home_team}")
            return None
        if away_team not in self.team_stats:
            logger.warning(f"⚠️ Sin datos para {away_team}")
            return None
        
        # Expected Goals
        xg_home = self.team_stats[home_team].xg_average
        xg_away = self.team_stats[away_team].xg_average
        
        # Probabilidades 1X2
        prob_h = [poisson.pmf(i, xg_home) for i in range(self.max_goals + 1)]
        prob_a = [poisson.pmf(i, xg_away) for i in range(self.max_goals + 1)]
        matriz = np.outer(prob_h, prob_a)
        
        prob_home = np.sum(np.tril(matriz, -1)) * 100
        prob_draw = np.sum(np.diag(matriz)) * 100
        prob_away = np.sum(np.triu(matriz, 1)) * 100
        
        # Marcadores exactos (top 5)
        exact_scores = self.calculate_exact_scores(xg_home, xg_away)
        top_scores = dict(sorted(exact_scores.items(), key=lambda x: x[1], reverse=True)[:5])
        
        # Over/Under
        over_under = self.calculate_over_under(xg_home, xg_away)
        
        # Confianza (basada en partidos ponderados)
        confidence = min(
            (self.team_stats[home_team].matches_weighted + 
             self.team_stats[away_team].matches_weighted) / 20,  # Normalizado
            1.0
        )
        
        # Value Bet (si prob > 65% y confianza alta)
        max_prob = max(prob_home, prob_draw, prob_away)
        value_bet = max_prob > 65 and confidence > Config.CONFIDENCE_THRESHOLD
        
        return MatchPrediction(
            home_team=home_team,
            away_team=away_team,
            prob_home=round(prob_home, 2),
            prob_draw=round(prob_draw, 2),
            prob_away=round(prob_away, 2),
            xg_home=round(xg_home, 2),
            xg_away=round(xg_away, 2),
            exact_scores=top_scores,
            over_under=over_under,
            confidence=round(confidence, 2),
            value_bet=value_bet,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    def predict_multiple_matches(self, matches: List[Tuple[str, str]]) -> List[MatchPrediction]:
        """
        Predice múltiples partidos
        
        Args:
            matches: Lista de tuplas (home, away)
            
        Returns:
            Lista de predicciones
        """
        predictions = []
        for home, away in matches:
            pred = self.predict_match(home, away)
            if pred:
                predictions.append(pred)
        
        # Ordenar por value bet y confianza
        predictions.sort(key=lambda x: (x.value_bet, x.confidence), reverse=True)
        return predictions
    
    def export_predictions(self, predictions: List[MatchPrediction], filepath: str = None) -> str:
        """
        Exporta predicciones a JSON
        
        Args:
            predictions: Lista de predicciones
            filepath: Ruta de salida
            
        Returns:
            Ruta del archivo
        """
        if filepath is None:
            filepath = os.path.join(Config.DATA_DIR, Config.PREDICTIONS_FILE)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_predictions": len(predictions),
            "value_bets": sum(1 for p in predictions if p.value_bet),
            "predictions": [asdict(p) for p in predictions]
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Predicciones exportadas a {filepath}")
        return filepath


def main():
    """Ejecución principal del modelo"""
    logger.info("🚀 Iniciando PoissonModel de QuantBet WC26")
    
    model = PoissonModel()
    data = model.load_data()
    
    if not data:
        logger.error("❌ No hay datos para procesar")
        return
    
    model.calculate_weighted_stats(data)
    
    # Partidos de prueba
    test_matches = [
        ("Mexico", "USA"),
        ("Argentina", "Brazil"),
        ("Spain", "Germany"),
        ("France", "England"),
    ]
    
    predictions = model.predict_multiple_matches(test_matches)
    
    for pred in predictions:
        logger.info(f"⚽ {pred.home_team} vs {pred.away_team}")
        logger.info(f"   1: {pred.prob_home}% | X: {pred.prob_draw}% | 2: {pred.prob_away}%")
        logger.info(f"   xG: {pred.xg_home} - {pred.xg_away} | Value: {pred.value_bet}")
    
    model.export_predictions(predictions)
    logger.info("✅ Proceso completado")


if __name__ == "__main__":
    main()
