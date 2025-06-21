# tests/test_actions_air_pollution_forecast.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions_air_pollution_forecast import ActionGetAirPollutionForecast

class TestActionGetAirPollutionForecast:
    """Tests for ActionGetAirPollutionForecast class in actions_air_pollution_forecast.py."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionGetAirPollutionForecast()
    
    # Test for lines 71-73 (ActionGetAirPollutionForecast AQI level mapping)
    def test_aqi_level_mapping(self):
        """Test AQI level mapping in ActionGetAirPollutionForecast """
        # Test each AQI level
        assert self.action._get_aqi_level(1) == "Good"
        assert self.action._get_aqi_level(2) == "Fair"
        assert self.action._get_aqi_level(3) == "Moderate"
        assert self.action._get_aqi_level(4) == "Poor"
        assert self.action._get_aqi_level(5) == "Very Poor"
        assert self.action._get_aqi_level(6) == "Unknown"  # Invalid AQI
        assert self.action._get_aqi_level(0) == "Unknown"  # Invalid AQI
        assert self.action._get_aqi_level(-1) == "Unknown"  # Invalid AQI
    
    # Test for lines 115-120 (ActionGetAirPollutionForecast no forecast data handling)
    @patch('actions.actions_air_pollution_forecast.load_dotenv')
    @patch('actions.actions_air_pollution_forecast.os.environ.get')
    @patch('actions.actions_air_pollution_forecast.requests.get')
    def test_no_forecast_data_handling(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test handling of missing forecast data """
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock geo response
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        # Mock empty pollution response
        pollution_response = MagicMock(status_code=200)
        pollution_response.json.return_value = {"list": []}
        
        # Set up the side effect
        mock_get.side_effect = [geo_response, pollution_response]
        
        # Set up tracker
        self.tracker.get_slot.return_value = "London"
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "couldn't find air pollution forecast data" in message.lower()
    
    # Additional test for health implications
    def test_health_implications(self):
        """Test health implications in ActionGetAirPollutionForecast."""
        # Test each AQI level's health implications
        assert "satisfactory" in self.action._get_health_implications(1)
        assert "acceptable" in self.action._get_health_implications(2)
        assert "sensitive groups" in self.action._get_health_implications(3)
        assert "Everyone may begin to experience" in self.action._get_health_implications(4)
        assert "emergency conditions" in self.action._get_health_implications(5)
        assert "unknown" in self.action._get_health_implications(6)  # Invalid AQI
    
    # Test for successful forecast with valid data
    @patch('actions.actions_air_pollution_forecast.load_dotenv')
    @patch('actions.actions_air_pollution_forecast.os.environ.get')
    @patch('actions.actions_air_pollution_forecast.requests.get')
    @patch('actions.actions_air_pollution_forecast.datetime')
    def test_run_with_valid_forecast_data(self, mock_datetime, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetAirPollutionForecast run method with valid forecast data."""
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock current date
        today = datetime.datetime(2023, 7, 15)
        tomorrow = datetime.datetime(2023, 7, 16)
        mock_datetime.datetime.now.return_value = today
        mock_datetime.datetime.fromtimestamp.side_effect = lambda ts: datetime.datetime.fromtimestamp(ts)
        mock_datetime.timedelta.side_effect = datetime.timedelta
        
        # Mock geo response
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        # Mock pollution response
        pollution_response = MagicMock(status_code=200)
        pollution_response.json.return_value = {
            "list": [
                {
                    "dt": int(tomorrow.timestamp()),
                    "main": {"aqi": 2},  # Fair
                    "components": {
                        "co": 250.34,
                        "no2": 15.82,
                        "o3": 68.66,
                        "pm2_5": 8.5,
                        "pm10": 12.3
                    }
                }
            ]
        }
        
        # Set up the side effect
        mock_get.side_effect = [geo_response, pollution_response]
        
        # Set up tracker
        self.tracker.get_slot.return_value = "London"
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the message contains the expected level and description
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "Fair" in message
        assert "AQI: 2" in message
        assert "acceptable" in message.lower()
