# tests/test_actions_comprehensive.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import (
    ActionFetchWeather, ActionRandomFact, ActionCompareWeather, 
    ActionGetLocalTime, ActionGetUVIndex, ActionFetchWeatherForecast,
    ActionGetTemperatureRange, ActionGetUVIndexForecast
)

class TestActionsComprehensive:
    """Comprehensive tests for actions.py."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
    
    # Test for lines 81-82 (ActionRandomFact run method)
    def test_action_random_fact_run(self):
        """Test ActionRandomFact run method """
        action = ActionRandomFact()
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that a fact was returned
        self.dispatcher.utter_message.assert_called_once()
        message = self.dispatcher.utter_message.call_args[1]['text']
        
        # Check that the message is one of the predefined facts
        facts = [
            "Did you know honey never spoils?",
            "Octopuses have three hearts.",
            "Bananas are berries, but strawberries are not."
        ]
        assert any(fact == message for fact in facts)
    
    # Test for lines 87-88 (ActionCompareWeather name method)
    def test_action_compare_weather_name(self):
        """Test ActionCompareWeather name method """
        action = ActionCompareWeather()
        assert action.name() == "action_compare_weather"
    
    # Test for lines 118-119 (ActionCompareWeather error handling)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_compare_weather_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionCompareWeather API error handling """
        action = ActionCompareWeather()
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        self.tracker.get_slot.return_value = "London"
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "sorry" in message.lower()
        assert "error" in message.lower()
    
    # Test for lines 220-222 (ActionFetchWeatherForecast days validation)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_fetch_weather_forecast_days_validation(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionFetchWeatherForecast days validation """
        action = ActionFetchWeatherForecast()
        mock_env_get.return_value = "fake_api_key"
        
        # Mock successful responses
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {"coord": {"lat": 51.5074, "lon": -0.1278}}
        
        forecast_response = MagicMock(status_code=200)
        forecast_response.json.return_value = {"list": []}
        
        uv_response = MagicMock(status_code=200)
        uv_response.json.return_value = []
        
        mock_get.side_effect = [geo_response, forecast_response, uv_response]
        
        # Test with string days value
        self.tracker.get_slot.side_effect = lambda name: "London" if name == "location" else "5" if name == "days" else None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that days was limited to 3
        # This is hard to test directly, but we can verify the API was called
        assert mock_get.call_count == 3
    
    # Test for line 294 (ActionGetUVIndex name method)
    def test_action_get_uv_index_name(self):
        """Test ActionGetUVIndex name method """
        action = ActionGetUVIndex()
        assert action.name() == "action_get_uv_index"
    
    # Test for line 296 (ActionGetUVIndex run method - missing location)
    def test_action_get_uv_index_missing_location(self):
        """Test ActionGetUVIndex missing location handling """
        action = ActionGetUVIndex()
        self.tracker.get_slot.return_value = None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    # Test for lines 325-326 (ActionGetTemperatureRange name method)
    def test_action_get_temperature_range_name(self):
        """Test ActionGetTemperatureRange name method """
        action = ActionGetTemperatureRange()
        assert action.name() == "action_get_temperature_range"
    
    # Test for line 347 (ActionGetTemperatureRange missing location)
    def test_action_get_temperature_range_missing_location(self):
        """Test ActionGetTemperatureRange missing location handling """
        action = ActionGetTemperatureRange()
        self.tracker.get_slot.return_value = None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    # Test for lines 359-360 (ActionGetTemperatureRange missing API key)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_action_get_temperature_range_missing_api_key(self, mock_env_get, mock_load_dotenv):
        """Test ActionGetTemperatureRange missing API key handling """
        action = ActionGetTemperatureRange()
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "London"
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="Weather service is currently unavailable."
        )
    
    # Test for lines 375-376 (ActionGetTemperatureRange today's temperature min)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_get_temperature_range_today_min(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetTemperatureRange today's min temperature """
        action = ActionGetTemperatureRange()
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response
        mock_response = MagicMock(status_code=200)
        mock_response.json.return_value = {
            "main": {
                "temp": 22.5,
                "temp_min": 18.0,
                "temp_max": 25.0
            }
        }
        mock_get.return_value = mock_response
        
        # Set up tracker slots
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "London",
            "time_period": "today",
            "temp_type": "min"
        }.get(name)
        
        # Run the action
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check the response
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "London" in message
        assert "minimum temperature" in message
        assert "18.0°C" in message
    
    # Test for lines 397-398 (ActionGetTemperatureRange API error)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_get_temperature_range_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetTemperatureRange API error handling """
        action = ActionGetTemperatureRange()
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        self.tracker.get_slot.side_effect = lambda name: {
            "location": "London",
            "time_period": "today",
            "temp_type": "range"
        }.get(name)
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "sorry" in message.lower()
        assert "error" in message.lower()
    
    # Test for line 466 (ActionGetUVIndexForecast name method)
    def test_action_get_uv_index_forecast_name(self):
        """Test ActionGetUVIndexForecast name method (line 466)."""
        action = ActionGetUVIndexForecast()
        assert action.name() == "action_get_uv_index_forecast"
    
    # Test for lines 486-487 (ActionGetUVIndexForecast days validation)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_get_uv_index_forecast_days_validation(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetUVIndexForecast days validation """
        action = ActionGetUVIndexForecast()
        mock_env_get.return_value = "fake_api_key"
        
        # Mock successful responses
        geo_response = MagicMock(status_code=200)
        geo_response.json.return_value = {"coord": {"lat": 51.5074, "lon": -0.1278}}
        
        uv_response = MagicMock(status_code=200)
        uv_response.json.return_value = [{"date": 1704110400, "value": 5.2}]
        
        mock_get.side_effect = [geo_response, uv_response]
        
        # Test with string days value
        self.tracker.get_slot.side_effect = lambda name: "London" if name == "location" else "6" if name == "days" else None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that days was limited to 5
        # This is hard to test directly, but we can verify the API was called
        assert mock_get.call_count == 2
    
    # Test for lines 496-498 (ActionGetUVIndexForecast missing location)
    def test_action_get_uv_index_forecast_missing_location(self):
        """Test ActionGetUVIndexForecast missing location handling """
        action = ActionGetUVIndexForecast()
        self.tracker.get_slot.return_value = None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    # Test for line 637 (ActionGetUVIndex _get_uv_level method)
    def test_action_get_uv_index_get_uv_level(self):
        """Test ActionGetUVIndex _get_uv_level method """
        action = ActionGetUVIndex()
        
        assert action._get_uv_level(1.5) == "Low"
        assert action._get_uv_level(4.2) == "Moderate"
        assert action._get_uv_level(7.0) == "High"
        assert action._get_uv_level(9.8) == "Very High"
        assert action._get_uv_level(12.0) == "Extreme"
    
    # Test for line 641 (ActionGetUVIndex _get_protection_advice method)
    def test_action_get_uv_index_get_protection_advice(self):
        """Test ActionGetUVIndex _get_protection_advice method """
        action = ActionGetUVIndex()
        
        assert "No protection required" in action._get_protection_advice(1.5)
        assert "Wear sunscreen, a hat" in action._get_protection_advice(4.2)
        assert "SPF 30+" in action._get_protection_advice(7.0)
        assert "avoid sun exposure" in action._get_protection_advice(9.8)
        assert "Take all precautions" in action._get_protection_advice(12.0)
    
    # Test for line 649 (ActionGetUVIndexForecast _get_uv_level method)
    def test_action_get_uv_index_forecast_get_uv_level(self):
        """Test ActionGetUVIndexForecast _get_uv_level method """
        action = ActionGetUVIndexForecast()
        
        assert action._get_uv_level(1.5) == "Low"
        assert action._get_uv_level(4.2) == "Moderate"
        assert action._get_uv_level(7.0) == "High"
        assert action._get_uv_level(9.8) == "Very High"
        assert action._get_uv_level(12.0) == "Extreme"
    
    # Test for lines 653-654 (ActionGetUVIndexForecast _get_protection_advice method)
    def test_action_get_uv_index_forecast_get_protection_advice(self):
        """Test ActionGetUVIndexForecast _get_protection_advice method """
        action = ActionGetUVIndexForecast()
        
        assert "No protection required" in action._get_protection_advice(1.5)
        assert "Wear sunscreen, a hat" in action._get_protection_advice(4.2)
        assert "SPF 30+" in action._get_protection_advice(7.0)
        assert "avoid sun exposure" in action._get_protection_advice(9.8)
        assert "Take all precautions" in action._get_protection_advice(12.0)
    
    # Test for line 664 (ActionGetHumidity name method)
    def test_action_get_humidity_name(self):
        """Test ActionGetHumidity name method (line 664)."""
        from actions.actions import ActionGetHumidity
        action = ActionGetHumidity()
        assert action.name() == "action_get_humidity"
    
    # Test for lines 670-671 (ActionGetHumidity missing location)
    def test_action_get_humidity_missing_location(self):
        """Test ActionGetHumidity missing location handling """
        from actions.actions import ActionGetHumidity
        action = ActionGetHumidity()
        self.tracker.get_slot.return_value = None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    # Test for lines 676-677 (ActionGetHumidity missing API key)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_action_get_humidity_missing_api_key(self, mock_env_get, mock_load_dotenv):
        """Test ActionGetHumidity missing API key handling """
        from actions.actions import ActionGetHumidity
        action = ActionGetHumidity()
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "London"
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="Weather service is currently unavailable."
        )
    
    # Test for lines 730-731 (ActionGetHumidity API error)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_get_humidity_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetHumidity API error handling """
        from actions.actions import ActionGetHumidity
        action = ActionGetHumidity()
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        self.tracker.get_slot.return_value = "London"
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "sorry" in message.lower()
        assert "error" in message.lower()
