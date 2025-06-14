# tests/test_actions_air_pollution.py
import pytest
from unittest.mock import patch, MagicMock
import requests
from actions.actions_air_pollution import ActionGetAirPollution

class TestActionGetAirPollution:
    """Tests for ActionGetAirPollution class in actions_air_pollution.py."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
        self.action = ActionGetAirPollution()
    
    # Test for line 15 (ActionGetAirPollution name method)
    def test_action_get_air_pollution_name(self):
        """Test ActionGetAirPollution name method """
        assert self.action.name() == "action_get_air_pollution"
    
    # Test for lines 80-85 (ActionGetAirPollution AQI level mapping)
    def test_aqi_level_mapping(self):
        """Test AQI level mapping in ActionGetAirPollution """
        # Test each AQI level
        assert self.action._get_aqi_level(1) == "Good"
        assert self.action._get_aqi_level(2) == "Fair"
        assert self.action._get_aqi_level(3) == "Moderate"
        assert self.action._get_aqi_level(4) == "Poor"
        assert self.action._get_aqi_level(5) == "Very Poor"
        assert self.action._get_aqi_level(6) == "Unknown"  # Invalid AQI
        assert self.action._get_aqi_level(0) == "Unknown"  # Invalid AQI
        assert self.action._get_aqi_level(-1) == "Unknown"  # Invalid AQI
    
    # Test for lines 80-85 (ActionGetAirPollution health implications)
    def test_health_implications(self):
        """Test health implications in ActionGetAirPollution (lines 80-85)."""
        # Test each AQI level's health implications
        assert "satisfactory" in self.action._get_health_implications(1)
        assert "acceptable" in self.action._get_health_implications(2)
        assert "sensitive groups" in self.action._get_health_implications(3)
        assert "Everyone may begin to experience" in self.action._get_health_implications(4)
        assert "emergency conditions" in self.action._get_health_implications(5)
        assert "unknown" in self.action._get_health_implications(6)  # Invalid AQI
    
    @patch('actions.actions_air_pollution.load_dotenv')
    @patch('actions.actions_air_pollution.os.environ.get')
    @patch('actions.actions_air_pollution.requests.get')
    def test_run_with_valid_data(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetAirPollution run method with valid data."""
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock geo response
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        # Mock air pollution response
        pollution_response = MagicMock(status_code=200)
        pollution_response.json.return_value = {
            "list": [
                {
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
    
    @patch('actions.actions_air_pollution.load_dotenv')
    @patch('actions.actions_air_pollution.os.environ.get')
    @patch('actions.actions_air_pollution.requests.get')
    def test_run_with_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetAirPollution run method with API error."""
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Set up tracker
        self.tracker.get_slot.return_value = "London"
        
        # Run the action
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "sorry" in message.lower()
        assert "error" in message.lower()
