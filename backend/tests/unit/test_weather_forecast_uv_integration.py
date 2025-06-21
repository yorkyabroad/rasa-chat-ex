# tests/test_weather_forecast_uv_integration.py
import pytest
from unittest.mock import patch, MagicMock
import datetime
from actions.actions import ActionFetchWeatherForecast

class TestWeatherForecastUVIntegration:
    """Tests specifically for the UV data integration in ActionFetchWeatherForecast."""
    
    def test_uv_data_processing(self):
        """Test the processing of UV data in weather forecasts."""
        action = ActionFetchWeatherForecast()
        
        # Test the UV level classification method
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
    
    def test_uv_data_integration_in_forecast(self):
        """Test the integration of UV data into the forecast message."""
        action = ActionFetchWeatherForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        with patch('actions.actions.load_dotenv'), \
             patch('actions.actions.os.environ.get') as mock_env_get, \
             patch('actions.actions.requests.get') as mock_requests_get, \
             patch('actions.actions.datetime') as mock_datetime:
            
            # Set up datetime mock
            today = datetime.datetime(2023, 6, 15, 12, 0, 0)
            tomorrow = today + datetime.timedelta(days=1)
            mock_datetime.datetime.now.return_value = today
            mock_datetime.datetime.fromtimestamp.side_effect = lambda x: datetime.datetime.fromtimestamp(x)
            mock_datetime.timedelta.side_effect = datetime.timedelta
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock forecast response with today and tomorrow at noon
            today_timestamp = int(today.timestamp())
            tomorrow_timestamp = int(tomorrow.timestamp())
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {
                "list": [
                    {
                        "dt": today_timestamp,
                        "main": {"temp": 22.5},
                        "weather": [{"description": "clear sky"}]
                    },
                    {
                        "dt": tomorrow_timestamp,
                        "main": {"temp": 24.0},
                        "weather": [{"description": "scattered clouds"}]
                    }
                ]
            }
            
            # Mock UV response with different UV levels for today and tomorrow
            uv_response = MagicMock(status_code=200)
            uv_response.json.return_value = [
                {
                    "date": today_timestamp,
                    "value": 2.5  # Low
                },
                {
                    "date": tomorrow_timestamp,
                    "value": 7.5  # High
                }
            ]
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response, uv_response]
            
            # Set up tracker
            tracker.get_slot.side_effect = lambda name: "London" if name == "location" else 2
            
            # Run the action
            action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent with correct UV information
            dispatcher.utter_message.assert_called_once()
            message = dispatcher.utter_message.call_args[1]['text']
            
            # Check for today's UV info
            assert "Today" in message
            assert "UV index: 2.5 (Low)" in message
            
            # Check for tomorrow's UV info
            assert "scattered clouds" in message
            assert "UV index: 7.5 (High)" in message