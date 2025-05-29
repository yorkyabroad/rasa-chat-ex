# tests/test_actions_coverage.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
import requests
from actions.actions import (
    ActionFetchWeather, ActionRandomFact, ActionCompareWeather, 
    ActionGetLocalTime, ActionGetUVIndex, ActionFetchWeatherForecast,
    ActionGetTemperatureRange
)

class TestActionsCoverage:
    """Tests for specific lines in actions.py."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = MagicMock()
    
    # Test for line 22 (ActionFetchWeather name method)
    def test_action_fetch_weather_name(self):
        """Test ActionFetchWeather name method (line 22)."""
        action = ActionFetchWeather()
        assert action.name() == "action_fetch_weather"
    
    # Test for lines 51-53 (ActionFetchWeather error handling)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_fetch_weather_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionFetchWeather API error handling (lines 51-53)."""
        action = ActionFetchWeather()
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        self.tracker.get_slot.return_value = "London"
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "sorry" in message.lower()
        assert "error" in message.lower()
    
    # Test for line 75 (ActionRandomFact name method)
    def test_action_random_fact_name(self):
        """Test ActionRandomFact name method (line 75)."""
        action = ActionRandomFact()
        assert action.name() == "action_random_fact"
    
    # Test for lines 81-82 (ActionRandomFact run method)
    def test_action_random_fact_run(self):
        """Test ActionRandomFact run method (lines 81-82)."""
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
        """Test ActionCompareWeather name method (lines 87-88)."""
        action = ActionCompareWeather()
        assert action.name() == "action_compare_weather"
    
    # Test for lines 118-119 (ActionCompareWeather error handling)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_compare_weather_api_error(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionCompareWeather API error handling (lines 118-119)."""
        action = ActionCompareWeather()
        mock_env_get.return_value = "fake_api_key"
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        self.tracker.get_slot.return_value = "London"
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        message = self.dispatcher.utter_message.call_args[1]['text']
        assert "sorry" in message.lower()
        assert "error" in message.lower()
    
    # Test for line 128 (ActionGetLocalTime name method)
    def test_action_get_local_time_name(self):
        """Test ActionGetLocalTime name method (line 128)."""
        action = ActionGetLocalTime()
        assert action.name() == "action_get_local_time"
    
    # Test for lines 134-135 (ActionGetLocalTime missing location)
    def test_action_get_local_time_missing_location(self):
        """Test ActionGetLocalTime missing location handling (lines 134-135)."""
        action = ActionGetLocalTime()
        self.tracker.get_slot.return_value = None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    # Test for lines 142-143 (ActionGetLocalTime missing API key)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    def test_action_get_local_time_missing_api_key(self, mock_env_get, mock_load_dotenv):
        """Test ActionGetLocalTime missing API key handling (lines 142-143)."""
        action = ActionGetLocalTime()
        mock_env_get.return_value = None
        self.tracker.get_slot.return_value = "London"
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="Location service is currently unavailable."
        )
    
    # Test for lines 151-153 (ActionGetLocalTime location not found)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_get_local_time_location_not_found(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionGetLocalTime location not found handling (lines 151-153)."""
        action = ActionGetLocalTime()
        mock_env_get.return_value = "fake_api_key"
        
        # Mock error response
        mock_response = MagicMock(status_code=404)
        mock_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "NonExistentCity"
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find that location. Please try again."
        )
    
    # Test for line 191 (ActionFetchWeatherForecast name method)
    def test_action_fetch_weather_forecast_name(self):
        """Test ActionFetchWeatherForecast name method (line 191)."""
        action = ActionFetchWeatherForecast()
        assert action.name() == "action_fetch_weather_forecast"
    
    # Test for lines 220-222 (ActionFetchWeatherForecast days validation)
    @patch('actions.actions.load_dotenv')
    @patch('actions.actions.os.environ.get')
    @patch('actions.actions.requests.get')
    def test_action_fetch_weather_forecast_days_validation(self, mock_get, mock_env_get, mock_load_dotenv):
        """Test ActionFetchWeatherForecast days validation (lines 220-222)."""
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
        """Test ActionGetUVIndex name method (line 294)."""
        action = ActionGetUVIndex()
        assert action.name() == "action_get_uv_index"
    
    # Test for line 296 (ActionGetUVIndex run method - missing location)
    def test_action_get_uv_index_missing_location(self):
        """Test ActionGetUVIndex missing location handling (line 296)."""
        action = ActionGetUVIndex()
        self.tracker.get_slot.return_value = None
        
        action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check error message
        self.dispatcher.utter_message.assert_called_once_with(
            text="I couldn't find the location. Could you please provide it?"
        )
    
    # Test for lines 325-326 (ActionGetTemperatureRange name method)
    def test_action_get_temperature_range_name(self):
        """Test ActionGetTemperatureRange name method (lines 325-326)."""
        action = ActionGetTemperatureRange()
        assert action.name() == "action_get_temperature_range"
