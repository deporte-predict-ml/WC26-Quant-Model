# tests/test_poisson.py
"""
Tests unitarios para el núcleo Poisson
"""
import unittest
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.poisson_core import PoissonModel, TeamStats


class TestPoissonModel(unittest.TestCase):
    
    def setUp(self):
        self.model = PoissonModel(decay_lambda=0.001)
        self.sample_data = {
            "response": [
                {
                    "teams": {"home": {"name": "Mexico"}, "away": {"name": "USA"}},
                    "goals": {"home": 2, "away": 1},
                    "fixture": {"date": "2024-01-15T00:00:00+00:00"}
                },
                {
                    "teams": {"home": {"name": "Mexico"}, "away": {"name": "Canada"}},
                    "goals": {"home": 3, "away": 0},
                    "fixture": {"date": "2024-02-20T00:00:00+00:00"}
                },
                {
                    "teams": {"home": {"name": "USA"}, "away": {"name": "Mexico"}},
                    "goals": {"home": 1, "away": 1},
                    "fixture": {"date": "2024-03-10T00:00:00+00:00"}
                },
            ]
        }
    
    def test_calculate_weighted_stats(self):
        stats = self.model.calculate_weighted_stats(self.sample_data)
        self.assertIn("Mexico", stats)
        self.assertIn("USA", stats)
        self.assertGreater(stats["Mexico"].xg_average, 0)
    
    def test_predict_match(self):
        self.model.calculate_weighted_stats(self.sample_data)
        prediction = self.model.predict_match("Mexico", "USA")
        self.assertIsNotNone(prediction)
        self.assertAlmostEqual(
            prediction.prob_home + prediction.prob_draw + prediction.prob_away,
            100,
            places=0
        )
    
    def test_exact_scores_sum(self):
        exact = self.model.calculate_exact_scores(1.5, 1.2)
        total = sum(exact.values())
        self.assertGreater(total, 95)  # Debe sumar ~100%
    
    def test_empty_data(self):
        stats = self.model.calculate_weighted_stats({"response": []})
        self.assertEqual(len(stats), 0)


if __name__ == "__main__":
    unittest.main()
