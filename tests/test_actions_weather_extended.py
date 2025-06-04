import pytest
from unittest.mock import patch, MagicMock
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from actions.actions_weather_extended import (
    ActionGetSevereWeatherAlerts,
    ActionGetPrecipitation,
    ActionGetWindConditions,
    ActionGetSunriseSunset,
    ActionGetWeatherComparison
)

class TestActionsWeatherExtended:
    
    @pytest.fixture
    def dispatcher(self):
        return MagicMock(spec=CollectingDispatcher)
    
    @pytest.fixture
    def tracker(self):
        tracker = MagicMock(spec=Tracker)
        tracker.get_slot.return_value = "London"
        return tracker
    
    @pytest.fixture
    def domain(self):
        return {}
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_severe_weather_alerts_no_alerts(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Mock response with no alerts
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "alerts": []
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSevereWeatherAlerts()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "no weather alerts" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_severe_weather_alerts_with_alerts(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Mock response with alerts
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "alerts": [
                {
                    "sender_name": "Met Office",
                    "event": "Severe Thunderstorm Warning",
                    "start": 1609459200,  # Example timestamp
                    "end": 1609545600,    # Example timestamp
                    "description": "Severe thunderstorms expected with potential for lightning and flash flooding."
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSevereWeatherAlerts()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "weather alerts for london" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "severe thunderstorm warning" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_severe_weather_alerts_api_error(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSevereWeatherAlerts()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "couldn't fetch weather alerts" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_precipitation_today(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        tracker.get_slot.side_effect = lambda name: "today" if name == "time_period" else "London"
        
        # Mock response with precipitation data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "hourly": [
                {"dt": 1609459200, "temp": 5, "pop": 0.5},
                {"dt": 1609462800, "temp": 6, "pop": 0.7, "rain": {"1h": 1.2}}
            ],
            "daily": [
                {"dt": 1609459200, "temp": {"day": 5}, "pop": 0.2},
                {"dt": 1609545600, "temp": {"day": 6}, "pop": 0.6, "rain": 2.5}
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetPrecipitation()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "precipitation forecast" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_precipitation_tomorrow(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        tracker.get_slot.side_effect = lambda name: "tomorrow" if name == "time_period" else "London"
        
        # Mock response with precipitation data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 51.5074,
            "lon": -0.1278,
            "timezone": "Europe/London",
            "hourly": [],
            "daily": [
                {"dt": 1609459200, "temp": {"day": 5}, "pop": 0.2},
                {"dt": 1609545600, "temp": {"day": 6}, "pop": 0.6, "rain": 2.5, "snow": 0}
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetPrecipitation()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "precipitation forecast for london tomorrow" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "expected rainfall: 2.5" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_wind_conditions_today(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        tracker.get_slot.side_effect = lambda name: "today" if name == "time_period" else "London"
        
        # Mock response with wind data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "wind": {
                "speed": 5.2,
                "deg": 180
            }
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetWindConditions()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "wind conditions in london" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "wind speed: 5.2" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "wind direction: south" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_wind_conditions_tomorrow(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        tracker.get_slot.side_effect = lambda name: "tomorrow" if name == "time_period" else "London"
        
        # Mock response with wind forecast data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "daily": [
                {},  # Today
                {    # Tomorrow
                    "wind_speed": 6.7,
                    "wind_deg": 90,
                    "wind_gust": 10.2
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetWindConditions()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "wind forecast for london tomorrow" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "wind speed: 6.7" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "wind direction: east" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    def test_wind_conditions_helper_methods(self):
        action = ActionGetWindConditions()
        
        # Test degree to direction conversion
        assert action._degree_to_direction(0) == "North"
        assert action._degree_to_direction(90) == "East"
        assert action._degree_to_direction(180) == "South"
        assert action._degree_to_direction(270) == "West"
        
        # Test m/s to km/h conversion
        assert action._ms_to_kmh(1) == 3.6
        
        # Test wind description
        assert action._describe_wind(0.3) == "Calm"
        assert action._describe_wind(4.0) == "Gentle breeze"
        assert action._describe_wind(15.0) == "High wind"
        assert action._describe_wind(35.0) == "Hurricane force"
        
        # Test outdoor recommendation
        assert "perfect" in action._outdoor_recommendation(3.0).lower()
        assert "challenging" in action._outdoor_recommendation(15.0).lower()
        assert "dangerous" in action._outdoor_recommendation(30.0).lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_sunrise_sunset_today(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        tracker.get_slot.side_effect = lambda name: "today" if name == "time_period" else "London"
        
        # Mock response with sunrise/sunset data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "London",
            "sys": {
                "sunrise": 1609484400,  # Example timestamp
                "sunset": 1609513200    # Example timestamp
            },
            "timezone": 0
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSunriseSunset()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "sunrise and sunset times for london today" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "sunrise:" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "sunset:" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "daylight hours:" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_sunrise_sunset_tomorrow(self, mock_env_get, mock_requests_get, mock_get_coords, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        tracker.get_slot.side_effect = lambda name: "tomorrow" if name == "time_period" else "London"
        
        # Mock response with sunrise/sunset forecast data
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "timezone_offset": 0,
            "daily": [
                {},  # Today
                {    # Tomorrow
                    "sunrise": 1609570800,  # Example timestamp
                    "sunset": 1609599600    # Example timestamp
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Execute action
        action = ActionGetSunriseSunset()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "sunrise and sunset times for london tomorrow" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "sunrise:" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "sunset:" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_weather_comparison(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response for current weather
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "name": "London",
            "main": {"temp": 10.5},
            "weather": [{"description": "cloudy"}],
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        # Mock response for historical weather
        hist_response = MagicMock()
        hist_response.status_code = 200
        hist_response.json.return_value = {
            "data": [
                {
                    "temp": 8.5,
                    "weather": [{"description": "rainy"}]
                }
            ]
        }
        
        # Configure mock to return different responses
        mock_requests_get.side_effect = [current_response, hist_response]
        
        # Execute action
        action = ActionGetWeatherComparison()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "weather comparison for london" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "today: cloudy, 10.5°c" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "yesterday: rainy, 8.5°c" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "2.0°c warmer than" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_get_weather_comparison_historical_error(self, mock_env_get, mock_requests_get, dispatcher, tracker, domain):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Mock response for current weather
        current_response = MagicMock()
        current_response.status_code = 200
        current_response.json.return_value = {
            "name": "London",
            "main": {"temp": 10.5},
            "weather": [{"description": "cloudy"}],
            "coord": {"lat": 51.5074, "lon": -0.1278}
        }
        
        # Mock error response for historical weather
        hist_response = MagicMock()
        hist_response.status_code = 404
        
        # Configure mock to return different responses
        mock_requests_get.side_effect = [current_response, hist_response]
        
        # Execute action
        action = ActionGetWeatherComparison()
        action.run(dispatcher, tracker, domain)
        
        # Verify
        dispatcher.utter_message.assert_called_once()
        assert "could only get today's weather" in dispatcher.utter_message.call_args[1]['text'].lower()
        assert "cloudy, 10.5°c" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_missing_api_key(self, mock_env_get, dispatcher, tracker, domain):
        # Setup mock to return None for API key
        mock_env_get.return_value = None
        
        # Test all actions
        actions = [
            ActionGetSevereWeatherAlerts(),
            ActionGetPrecipitation(),
            ActionGetWindConditions(),
            ActionGetSunriseSunset(),
            ActionGetWeatherComparison()
        ]
        
        for action in actions:
            # Reset mock
            dispatcher.reset_mock()
            
            # Execute action
            action.run(dispatcher, tracker, domain)
            
            # Verify
            dispatcher.utter_message.assert_called_once()
            assert "unavailable" in dispatcher.utter_message.call_args[1]['text'].lower()
    
    def test_missing_location(self, dispatcher, domain):
        # Setup tracker to return None for location
        tracker = MagicMock(spec=Tracker)
        tracker.get_slot.return_value = None
        
        # Test all actions
        actions = [
            ActionGetSevereWeatherAlerts(),
            ActionGetPrecipitation(),
            ActionGetWindConditions(),
            ActionGetSunriseSunset(),
            ActionGetWeatherComparison()
        ]
        
        for action in actions:
            # Reset mock
            dispatcher.reset_mock()
            
            # Execute action
            action.run(dispatcher, tracker, domain)
            
            # Verify
            dispatcher.utter_message.assert_called_once()
            assert "couldn't find the location" in dispatcher.utter_message.call_args[1]['text'].lower()