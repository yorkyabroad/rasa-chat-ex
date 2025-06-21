# tests/test_air_pollution_integration.py
import pytest
from unittest.mock import patch, MagicMock
import requests
from actions.actions_air_pollution import ActionGetAirPollution
from actions.actions_air_pollution_forecast import ActionGetAirPollutionForecast

class TestAirPollutionIntegration:
    """Integration tests for air pollution actions."""
    
    def test_air_pollution_different_aqi_levels(self):
        """Test air pollution action with different AQI levels."""
        action = ActionGetAirPollution()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Test with different AQI levels
            aqi_levels = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very Poor"
            }
            
            for aqi, expected_level in aqi_levels.items():
                # Reset mocks
                dispatcher.reset_mock()
                
                # Mock air pollution response with current AQI level
                air_response = MagicMock(status_code=200)
                air_response.json.return_value = {
                    "list": [
                        {
                            "main": {"aqi": aqi},
                            "components": {
                                "pm2_5": 5.0 * aqi,
                                "pm10": 10.0 * aqi,
                                "no2": 5.0 * aqi,
                                "o3": 30.0 * aqi
                            }
                        }
                    ]
                }
                
                # Set up the side effect to return different responses
                mock_requests_get.side_effect = [geo_response, air_response]
                
                # Set up tracker
                tracker.get_slot.return_value = "London"
                
                # Run the action
                action.run(dispatcher, tracker, domain)
                
                # Check that the message was sent with correct AQI level
                message = dispatcher.utter_message.call_args[1]['text']
                assert expected_level in message
    
    def test_air_pollution_forecast_integration(self):
        """Test integration between current and forecast air pollution actions."""
        # First test current air pollution
        current_action = ActionGetAirPollution()
        forecast_action = ActionGetAirPollutionForecast()
        dispatcher = MagicMock()
        tracker = MagicMock()
        domain = MagicMock()
        
        # Mock the API responses for current air pollution
        with patch('actions.actions_air_pollution.load_dotenv'), \
             patch('actions.actions_air_pollution.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution.requests.get') as mock_requests_get:
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Mock air pollution response
            air_response = MagicMock(status_code=200)
            air_response.json.return_value = {
                "list": [
                    {
                        "main": {"aqi": 2},
                        "components": {
                            "pm2_5": 4.5,
                            "pm10": 7.6,
                            "no2": 9.4,
                            "o3": 68.7
                        }
                    }
                ]
            }
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, air_response]
            
            # Set up tracker
            tracker.get_slot.return_value = "London"
            
            # Run the current action
            current_action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent with correct information
            current_message = dispatcher.utter_message.call_args[1]['text']
            assert "current air quality" in current_message.lower()
            assert "London" in current_message
            assert "Fair" in current_message  # AQI 2 = Fair
        
        # Now test forecast air pollution with the same setup
        with patch('actions.actions_air_pollution_forecast.load_dotenv'), \
             patch('actions.actions_air_pollution_forecast.os.environ.get') as mock_env_get, \
             patch('actions.actions_air_pollution_forecast.requests.get') as mock_requests_get, \
             patch('actions.actions_air_pollution_forecast.datetime') as mock_datetime:
            
            import datetime as dt
            
            # Set up datetime mock
            today = dt.datetime.now()
            tomorrow = today + dt.timedelta(days=1)
            mock_datetime.datetime.now.return_value = today
            mock_datetime.datetime.fromtimestamp.side_effect = lambda x: dt.datetime.fromtimestamp(x)
            mock_datetime.timedelta.side_effect = dt.timedelta
            
            mock_env_get.return_value = "fake_api_key"
            
            # Mock geo response
            geo_response = MagicMock(status_code=200)
            geo_response.json.return_value = {
                "coord": {"lat": 51.5074, "lon": -0.1278}
            }
            
            # Create forecast data for tomorrow
            tomorrow_timestamp = int(tomorrow.timestamp())
            
            # Mock air pollution forecast response
            forecast_response = MagicMock(status_code=200)
            forecast_response.json.return_value = {
                "list": [
                    {
                        "dt": tomorrow_timestamp,
                        "main": {"aqi": 3},  # Different from current
                        "components": {
                            "pm2_5": 8.5,
                            "pm10": 12.6,
                            "no2": 15.4,
                            "o3": 85.7
                        }
                    }
                ]
            }
            
            # Reset dispatcher
            dispatcher.reset_mock()
            
            # Set up the side effect to return different responses
            mock_requests_get.side_effect = [geo_response, forecast_response]
            
            # Run the forecast action
            forecast_action.run(dispatcher, tracker, domain)
            
            # Check that the message was sent with correct information
            forecast_message = dispatcher.utter_message.call_args[1]['text']
            assert "air quality forecast" in forecast_message.lower()
            assert "London" in forecast_message
            assert "tomorrow" in forecast_message.lower()
            assert "Moderate" in forecast_message  # AQI 3 = Moderate