# tests/test_uv_index_forecast_utils.py
import pytest
from actions.actions import ActionGetUVIndexForecast

class TestUVIndexForecastUtils:
    """Tests for the utility methods in ActionGetUVIndexForecast."""
    
    def test_get_uv_level(self):
        """Test the _get_uv_level method with different UV values."""
        action = ActionGetUVIndexForecast()
        
        # Test all UV level boundaries
        test_cases = [
            (0, "Low"),
            (2.9, "Low"),
            (3, "Moderate"),
            (5.9, "Moderate"),
            (6, "High"),
            (7.9, "High"),
            (8, "Very High"),
            (10.9, "Very High"),
            (11, "Extreme"),
            (15, "Extreme")
        ]
        
        for uv_value, expected_level in test_cases:
            level = action._get_uv_level(uv_value)
            assert level == expected_level, f"UV value {uv_value} should be '{expected_level}', got '{level}'"
    
    def test_get_protection_advice(self):
        """Test the _get_protection_advice method with different UV values."""
        action = ActionGetUVIndexForecast()
        
        # Test all protection advice boundaries
        test_cases = [
            (0, "No protection required for most people."),
            (2.9, "No protection required for most people."),
            (3, "Wear sunscreen, a hat, and sunglasses. Seek shade during midday hours."),
            (5.9, "Wear sunscreen, a hat, and sunglasses. Seek shade during midday hours."),
            (6, "Wear sunscreen SPF 30+, protective clothing, a hat, and sunglasses. Reduce time in the sun between 10 AM and 4 PM."),
            (7.9, "Wear sunscreen SPF 30+, protective clothing, a hat, and sunglasses. Reduce time in the sun between 10 AM and 4 PM."),
            (8, "Wear SPF 30+ sunscreen, protective clothing, a wide-brim hat, and UV-blocking sunglasses. Try to avoid sun exposure between 10 AM and 4 PM."),
            (10.9, "Wear SPF 30+ sunscreen, protective clothing, a wide-brim hat, and UV-blocking sunglasses. Try to avoid sun exposure between 10 AM and 4 PM."),
            (11, "Take all precautions: SPF 30+ sunscreen, protective clothing, wide-brim hat, and UV-blocking sunglasses. Avoid sun exposure as much as possible."),
            (15, "Take all precautions: SPF 30+ sunscreen, protective clothing, wide-brim hat, and UV-blocking sunglasses. Avoid sun exposure as much as possible.")
        ]
        
        for uv_value, expected_advice in test_cases:
            advice = action._get_protection_advice(uv_value)
            assert advice == expected_advice, f"UV value {uv_value} should give advice '{expected_advice}', got '{advice}'"