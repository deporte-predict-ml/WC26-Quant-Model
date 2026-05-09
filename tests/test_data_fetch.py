"""Tests para el módulo DataFetcher"""
import pytest
import json
from unittest.mock import Mock, patch
from scripts.data_fetch import DataFetcher


class TestDataFetcher:
    """Tests de la clase DataFetcher"""
    
    @pytest.fixture
    def fetcher(self):
        """Crea una instancia de DataFetcher para tests"""
        return DataFetcher(api_key="test_key")
    
    def test_fetcher_initialization(self, fetcher):
        """Verifica que DataFetcher se inicialice correctamente"""
        assert fetcher.api_key == "test_key"
        assert fetcher.base_url == "https://v3.football.api-sports.io"
        assert fetcher.endpoint == "/fixtures"
        assert fetcher.all_matches == []
    
    def test_validate_match_with_valid_data(self, fetcher):
        """Verifica que validate_match acepta datos válidos"""
        valid_match = {
            "fixture": {"date": "2026-05-09T20:00:00Z"},
            "teams": {"home": {"name": "Argentina"}, "away": {"name": "Brazil"}},
            "goals": {"home": 2, "away": 1},
            "league": {"id": 1},
            "season": 2026
        }
        assert fetcher.validate_match(valid_match) is True
    
    def test_validate_match_with_missing_fields(self, fetcher):
        """Verifica que validate_match rechaza datos incompletos"""
        invalid_match = {
            "fixture": {"date": "2026-05-09T20:00:00Z"},
            "teams": {"home": {"name": "Argentina"}}
        }
        assert fetcher.validate_match(invalid_match) is False
    
    def test_validate_match_with_none_goals(self, fetcher):
        """Verifica que validate_match rechaza partidos sin goles definidos"""
        invalid_match = {
            "fixture": {"date": "2026-05-09T20:00:00Z"},
            "teams": {"home": {"name": "Argentina"}, "away": {"name": "Brazil"}},
            "goals": {"home": None, "away": 1},
            "league": {"id": 1},
            "season": 2026
        }
        assert fetcher.validate_match(invalid_match) is False
