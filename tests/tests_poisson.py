"""Tests para el módulo PoissonModel"""
import pytest
import json
from datetime import datetime, timezone
from scripts.poisson_core import PoissonModel, MatchPrediction, TeamStats


class TestPoissonModel:
    """Tests de la clase PoissonModel"""
    
    @pytest.fixture
    def model(self):
        """Crea una instancia de PoissonModel para tests"""
        return PoissonModel()
    
    def test_model_initialization(self, model):
        """Verifica que PoissonModel se inicialice correctamente"""
        assert model.decay_lambda == 0.0015
        assert model.max_goals == 10
        assert model.min_matches == 3
        assert model.team_stats == {}
    
    def test_team_stats_creation(self):
        """Verifica la creación de estadísticas de equipo"""
        stats = TeamStats(
            name="Argentina",
            matches_weighted=15.5,
            goals_weighted=35.2,
            xg_average=2.27
        )
        assert stats.name == "Argentina"
        assert stats.xg_average == 2.27
    
    def test_match_prediction_creation(self):
        """Verifica la creación de predicciones de partido"""
        pred = MatchPrediction(
            home_team="Argentina",
            away_team="Brazil",
            prob_home=55.0,
            prob_draw=25.0,
            prob_away=20.0,
            xg_home=2.5,
            xg_away=1.8,
            exact_scores={"2-1": 15.5, "1-1": 12.3},
            over_under={"Over_2.5": 65.0},
            confidence=0.75,
            value_bet=True,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        assert pred.home_team == "Argentina"
        assert pred.value_bet is True
        assert pred.confidence == 0.75
