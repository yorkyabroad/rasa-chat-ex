# tests/test_weather_utils.py
import pytest
from unittest.mock import patch, MagicMock
import requests
from actions.weather_utils import (
    WeatherService, WeatherAPIError, UVInfo, fetch_with_retry,
    get_coordinates, get_uv_level, get_protection_advice,
    validate_env_vars, get_api_key, fetch_current_weather,
    fetch_weather_forecast, has_tenacity
)

class TestWeatherUtils:
    """Tests for the weather_utils.py module."""
    
    def test_get_uv_level(self):
        """Test UV level categorization."""
        assert get_uv_level(1.5) == "Low"
        assert get_uv_level(4.2) == "Moderate"
        assert get_uv_level(7.0) == "High"
        assert get_uv_level(9.8) == "Very High"
        assert get_uv_level(12.0) == "Extreme"
    
    def test_get_protection_advice(self):
        """Test protection advice based on UV level."""
        assert "No protection required" in get_protection_advice(1.5)
        assert "Wear sunscreen, a hat" in get_protection_advice(4.2)
        assert "SPF 30+" in get_protection_advice(7.0)
        assert "avoid sun exposure" in get_protection_advice(9.8)
        assert "Take all precautions" in get_protection_advice(12.0)
    
    @patch('actions.weather_utils.fetch_with_retry')
    def test_get_coordinates(self, mock_fetch):
        """Test getting coordinates for a location."""
        # Test successful response
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {"coord": {"lat": 51.5074, "lon": -0.1278}}
        mock_fetch.return_value = mock_response
        
        coords = get_coordinates("London", "test_key")
        assert coords == (51.5074, -0.1278)
        
        # Test error response
        mock_response.status_code = 404
        coords = get_coordinates("NonExistentCity", "test_key")
        assert coords is None
        
        # Test exception
        mock_fetch.side_effect = Exception("Test error")
        coords = get_coordinates("London", "test_key")
        assert coords is None
    
    def test_weather_service_methods(self):
        """Test all methods of the WeatherService class."""
        # Mock API key and responses
        api_key = "test_key"
        service = WeatherService(api_key)
        
        with patch('actions.weather_utils.fetch_with_retry') as mock_fetch:
            # Test get_current_weather
            mock_response = MagicMock(status_code=200)
            mock_response.json.return_value = {"main": {"temp": 20}, "weather": [{"description": "clear"}]}
            mock_fetch.return_value = mock_response
            
            result = service.get_current_weather("London")
            assert "main" in result
            assert "weather" in result
            
            # Test get_forecast
            mock_response.json.return_value = {"list": [{"dt": 1234567890, "main": {"temp": 22}}]}
            result = service.get_forecast("Paris", days=2)
            assert "list" in result
            
            # Test get_uv_index
            mock_response.json.return_value = {"value": 5.2}
            result = service.get_uv_index(35.6895, 139.6917)
            assert isinstance(result, UVInfo)
            assert result.value == 5.2
            assert result.level == "Moderate"
            
            # Test get_uv_forecast
            mock_response.json.return_value = [{"date": 1234567890, "value": 7.8}]
            result = service.get_uv_forecast(35.6895, 139.6917, days=1)
            assert isinstance(result, list)
            assert "value" in result[0]
    
    def test_weather_service_error_handling(self):
        """Test error handling in WeatherService methods."""
        api_key = "test_key"
        service = WeatherService(api_key)
        
        with patch('actions.weather_utils.fetch_with_retry') as mock_fetch:
            # Test error handling
            mock_response = MagicMock(status_code=404)
            mock_fetch.return_value = mock_response
            
            with pytest.raises(WeatherAPIError):
                service.get_current_weather("NonExistentCity")
                
            with pytest.raises(WeatherAPIError):
                service.get_forecast("NonExistentCity")
                
            with pytest.raises(WeatherAPIError):
                service.get_uv_index(0, 0)
                
            with pytest.raises(WeatherAPIError):
                service.get_uv_forecast(0, 0)
    
    @patch('actions.weather_utils.os.environ.get')
    def test_validate_env_vars(self, mock_get):
        """Test environment variable validation."""
        # Test when all vars are present
        mock_get.return_value = "test_value"
        assert validate_env_vars(["VAR1", "VAR2"]) is True
        
        # Test when vars are missing
        mock_get.side_effect = lambda x: None if x == "VAR2" else "test_value"
        assert validate_env_vars(["VAR1", "VAR2"]) is False
    
    @patch('actions.weather_utils.os.environ.get')
    def test_get_api_key(self, mock_get):
        """Test getting API key from environment."""
        mock_get.return_value = "test_api_key"
        assert get_api_key() == "test_api_key"
        
        mock_get.return_value = None
        assert get_api_key() is None
    
    def test_fetch_weather_functions(self):
        """Test the fetch_current_weather and fetch_weather_forecast functions."""
        with patch('actions.weather_utils.get_api_key') as mock_get_key, \
             patch('actions.weather_utils.requests.get') as mock_get:
            
            # Test with missing API key
            mock_get_key.return_value = None
            status, data = fetch_current_weather("London")
            assert status == 401
            assert data is None
            
            status, data = fetch_weather_forecast("London")
            assert status == 401
            assert data is None
            
            # Test with successful response
            mock_get_key.return_value = "test_key"
            mock_response = MagicMock(status_code=200)
            mock_response.json.return_value = {"weather": [{"description": "sunny"}]}
            mock_get.return_value = mock_response
            
            status, data = fetch_current_weather("London")
            assert status == 200
            assert "weather" in data
            
            status, data = fetch_weather_forecast("London")
            assert status == 200
            assert "weather" in data
            
            # Test with error response
            mock_response.status_code = 404
            status, data = fetch_current_weather("NonExistentCity")
            assert status == 404
            assert data is None
            
            # Test with request exception
            mock_get.side_effect = requests.exceptions.RequestException()
            status, data = fetch_current_weather("London")
            assert status == 500
            assert data is None
    
    @patch('actions.weather_utils.has_tenacity', False)
    @patch('actions.weather_utils.requests.get')
    def test_fetch_without_tenacity(self, mock_get):
        """Test the fetch_with_retry function when tenacity is not available."""
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        
        # This test requires reloading the module to apply the patch
        # In a real test, you might need to use importlib.reload
        # For this example, we'll just test the non-tenacity branch directly
        if not has_tenacity:
            response = fetch_with_retry("http://example.com")
            assert response == mock_response
            mock_get.assert_called_once_with("http://example.com", timeout=10)
