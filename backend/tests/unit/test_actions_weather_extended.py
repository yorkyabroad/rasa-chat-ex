import pytest
import datetime
from unittest.mock import MagicMock, patch
from actions.actions_weather_extended import (
    ActionGetSevereWeatherAlerts,
    ActionGetPrecipitation,
    ActionGetWindConditions,
    ActionGetSunriseSunset,
    ActionGetWeatherComparison
)

# Test ActionGetWindConditions helper methods (lines 335-378)
class TestActionGetWindConditions:
    def setup_method(self):
        self.action = ActionGetWindConditions()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    def test_degree_to_direction(self):
        # Test cardinal directions
        assert self.action._degree_to_direction(0) == "North"
        assert self.action._degree_to_direction(90) == "East"
        assert self.action._degree_to_direction(180) == "South"
        assert self.action._degree_to_direction(270) == "West"
        assert self.action._degree_to_direction(360) == "North"
        
        # Test intermediate directions
        assert self.action._degree_to_direction(45) == "Northeast"
        assert self.action._degree_to_direction(135) == "Southeast"
        assert self.action._degree_to_direction(225) == "Southwest"
        assert self.action._degree_to_direction(315) == "Northwest"
    
    def test_ms_to_kmh(self):
        assert self.action._ms_to_kmh(1) == 3.6
        assert self.action._ms_to_kmh(10) == 36.0
        assert self.action._ms_to_kmh(27.78) == pytest.approx(100.008, abs=0.001)  # ~100 km/h
    
    def test_describe_wind(self):
        assert self.action._describe_wind(0.3) == "Calm"
        assert self.action._describe_wind(1.0) == "Light air"
        assert self.action._describe_wind(2.5) == "Light breeze"
        assert self.action._describe_wind(4.0) == "Gentle breeze"
        assert self.action._describe_wind(6.0) == "Moderate breeze"
        assert self.action._describe_wind(9.0) == "Fresh breeze"
        assert self.action._describe_wind(12.0) == "Strong breeze"
        assert self.action._describe_wind(15.0) == "High wind"
        assert self.action._describe_wind(19.0) == "Gale"
        assert self.action._describe_wind(22.0) == "Strong gale"
        assert self.action._describe_wind(26.0) == "Storm"
        assert self.action._describe_wind(30.0) == "Violent storm"
        assert self.action._describe_wind(33.0) == "Hurricane force"
    
    def test_outdoor_recommendation(self):
        assert "Perfect for most outdoor activities" in self.action._outdoor_recommendation(3.0)
        assert "Good for most activities" in self.action._outdoor_recommendation(8.0)
        assert "Challenging for cycling" in self.action._outdoor_recommendation(15.0)
        assert "Not recommended" in self.action._outdoor_recommendation(20.0)
        assert "Dangerous conditions" in self.action._outdoor_recommendation(30.0)
        
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_wind_conditions_today(self, mock_env_get, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock response for current wind conditions
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "wind": {
                "speed": 5.5,
                "deg": 90,
                "gust": 8.2
            }
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "Paris" if slot == "location" else "today"
        self.tracker.latest_message = {'text': 'What is the wind like in Paris today?'}
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that wind conditions were reported correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Current wind conditions in Paris" in call_args
        assert "Wind speed: 5.5 m/s (19.8 km/h)" in call_args
        assert "Wind direction: East (90°)" in call_args
        assert "Wind gusts up to: 8.2 m/s (29.5 km/h)" in call_args
        assert "Conditions: Moderate breeze" in call_args
        
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_wind_conditions_tomorrow(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (48.8566, 2.3522)  # Paris coordinates
        
        # Create mock response for tomorrow's forecast
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create tomorrow's date for filtering
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        mock_response.json.return_value = {
            "list": [
                {
                    "dt_txt": f"{tomorrow} 12:00:00",
                    "wind": {
                        "speed": 12.5,
                        "deg": 180,
                        "gust": 18.0
                    }
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "Paris" if slot == "location" else "tomorrow"
        self.tracker.latest_message = {'text': 'What will the wind be like in Paris tomorrow?'}
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that wind forecast was reported correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Wind forecast for Paris tomorrow" in call_args
        assert "Wind speed: 12.5 m/s (45.0 km/h)" in call_args
        assert "Wind direction: South (180°)" in call_args
        assert "Wind gusts up to: 18.0 m/s (64.8 km/h)" in call_args
        assert "Expected conditions: Strong breeze" in call_args

# Test ActionGetSunriseSunset message parsing (lines 549-584)
class TestActionGetSunriseSunset:
    def setup_method(self):
        self.action = ActionGetSunriseSunset()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.logger')
    def test_message_text_parsing(self, mock_logger):
        # Test sunrise detection
        self.tracker.latest_message = {'text': 'When is sunrise in London?'}
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "today"
        
        with patch('actions.actions_weather_extended.os.environ.get', return_value=None):
            self.action.run(self.dispatcher, self.tracker, self.domain)
            
        # Check that sunrise was detected in the message
        mock_logger.info.assert_any_call("Message text: when is sunrise in london?")
        
        # Test sunset detection
        self.tracker.latest_message = {'text': 'When is sunset in Paris?'}
        with patch('actions.actions_weather_extended.os.environ.get', return_value=None):
            self.action.run(self.dispatcher, self.tracker, self.domain)
            
        # Check that sunset was detected in the message
        mock_logger.info.assert_any_call("Message text: when is sunset in paris?")
        
        # Test tomorrow detection
        self.tracker.latest_message = {'text': 'When is sunrise in Tokyo tomorrow?'}
        with patch('actions.actions_weather_extended.os.environ.get', return_value=None):
            self.action.run(self.dispatcher, self.tracker, self.domain)
            
        # Check that tomorrow was detected and time_period was updated
        mock_logger.info.assert_any_call("Found 'tomorrow' in message text, setting time_period to: tomorrow")
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_sunrise_sunset_today(self, mock_env_get, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        
        # Create mock response for today's sunrise/sunset
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sys": {
                "sunrise": 1609570800,  # Example timestamp for sunrise
                "sunset": 1609599600    # Example timestamp for sunset
            },
            "timezone": 3600  # UTC+1
        }
        mock_requests_get.return_value = mock_response
        
        # Test for both sunrise and sunset - use a message that doesn't contain "sunrise" or "sunset"
        self.tracker.latest_message = {'text': 'What are the daylight hours in London today?'}
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "today"
        
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that both sunrise and sunset were reported
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Sunrise and sunset times for London today" in call_args
        assert "Sunrise: " in call_args
        assert "Sunset: " in call_args
        assert "Daylight hours: " in call_args
        
        # Test for sunrise only
        self.dispatcher.utter_message.reset_mock()
        self.tracker.latest_message = {'text': 'When is sunrise in London today?'}
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that only sunrise was reported
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Sunrise time for London today" in call_args
        
        # Test for sunset only
        self.dispatcher.utter_message.reset_mock()
        self.tracker.latest_message = {'text': 'When is sunset in London today?'}
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that only sunset was reported
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Sunset time for London today" in call_args

# Test ActionGetSevereWeatherAlerts extreme weather detection (lines 74-104)
class TestActionGetSevereWeatherAlerts:
    def setup_method(self):
        self.action = ActionGetSevereWeatherAlerts()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_extreme_weather_detection(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (40.7128, -74.0060)  # NYC coordinates
        
        # Create mock response with different weather conditions
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Test case 1: Thunderstorm (weather_id < 300)
        mock_response.json.return_value = {
            "list": [
                {
                    "weather": [{"id": 200, "description": "thunderstorm with light rain"}],
                    "wind": {"speed": 5.0}
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "New York"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that thunderstorm was detected
        self.dispatcher.utter_message.assert_called_with(
            text="Weather alerts for New York:\n\nALERT 1: Thunderstorm\n"
        )
        
        # Test case 2: Heavy rain (500 <= weather_id < 600 and weather_id >= 502)
        mock_response.json.return_value = {
            "list": [
                {
                    "weather": [{"id": 502, "description": "heavy intensity rain"}],
                    "wind": {"speed": 5.0}
                }
            ]
        }
        self.dispatcher.utter_message.reset_mock()
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that heavy rain was detected
        self.dispatcher.utter_message.assert_called_with(
            text="Weather alerts for New York:\n\nALERT 1: Heavy rain\n"
        )
        
        # Test case 3: Strong winds (weather_id == 800 and wind speed > 20)
        mock_response.json.return_value = {
            "list": [
                {
                    "weather": [{"id": 800, "description": "clear sky"}],
                    "wind": {"speed": 25.0}
                }
            ]
        }
        self.dispatcher.utter_message.reset_mock()
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that strong winds were detected
        self.dispatcher.utter_message.assert_called_with(
            text="Weather alerts for New York:\n\nALERT 1: Strong winds\n"
        )
        
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_no_extreme_weather(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (40.7128, -74.0060)  # NYC coordinates
        
        # Create mock response with normal weather conditions
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {
                    "weather": [{"id": 800, "description": "clear sky"}],
                    "wind": {"speed": 5.0}
                },
                {
                    "weather": [{"id": 801, "description": "few clouds"}],
                    "wind": {"speed": 4.0}
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "New York"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that no alerts were reported
        self.dispatcher.utter_message.assert_called_with(
            text="Good news! There are no weather alerts for New York at this time."
        )
        
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_multiple_extreme_weather_conditions(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (40.7128, -74.0060)  # NYC coordinates
        
        # Create mock response with multiple extreme weather conditions
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "list": [
                {
                    "weather": [{"id": 200, "description": "thunderstorm with light rain"}],
                    "wind": {"speed": 5.0}
                },
                {
                    "weather": [{"id": 502, "description": "heavy intensity rain"}],
                    "wind": {"speed": 5.0}
                },
                {
                    "weather": [{"id": 602, "description": "heavy snow"}],
                    "wind": {"speed": 5.0}
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.return_value = "New York"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that all three alerts were reported (unique conditions)
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Weather alerts for New York" in call_args
        assert "ALERT 1:" in call_args
        assert "ALERT 2:" in call_args
        assert "ALERT 3:" in call_args
        assert "Thunderstorm" in call_args
        assert "Heavy rain" in call_args
        assert "Heavy snow" in call_args

# Test ActionGetPrecipitation precipitation calculation (lines 154-227)
class TestActionGetPrecipitation:
    def setup_method(self):
        self.action = ActionGetPrecipitation()
        self.dispatcher = MagicMock()
        self.tracker = MagicMock()
        self.domain = {}
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_precipitation_calculation_today(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Create mock response with precipitation data for today
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create today's date for filtering
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Mock data with rain
        mock_response.json.return_value = {
            "list": [
                {
                    "dt_txt": f"{today} 12:00:00",
                    "pop": 0.8,  # 80% chance of precipitation
                    "rain": {"3h": 2.5}  # 2.5mm of rain in 3 hours
                },
                {
                    "dt_txt": f"{today} 15:00:00",
                    "pop": 0.6,  # 60% chance of precipitation
                    "rain": {"3h": 1.2}  # 1.2mm of rain in 3 hours
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "today"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that precipitation was calculated correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Precipitation forecast for London today" in call_args
        assert "Chance of precipitation: 80%" in call_args
        assert "Expected rainfall: 3.7 mm" in call_args
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_precipitation_calculation_today_no_rain(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Create mock response with no precipitation data for today
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create today's date for filtering
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Mock data with no rain
        mock_response.json.return_value = {
            "list": [
                {
                    "dt_txt": f"{today} 12:00:00",
                    "pop": 0.1  # 10% chance of precipitation, no rain data
                },
                {
                    "dt_txt": f"{today} 15:00:00",
                    "pop": 0.0  # 0% chance of precipitation
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "today"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that no precipitation was reported
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Precipitation forecast for London today" in call_args
        assert "Chance of precipitation: 10%" in call_args
        assert "No significant precipitation expected today" in call_args
        
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_precipitation_calculation_tomorrow(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Create mock response with precipitation data for tomorrow
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create tomorrow's date for filtering
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Mock data with snow
        mock_response.json.return_value = {
            "list": [
                {
                    "dt_txt": f"{tomorrow} 12:00:00",
                    "pop": 0.9,  # 90% chance of precipitation
                    "snow": {"3h": 1.5}  # 1.5mm of snow in 3 hours
                },
                {
                    "dt_txt": f"{tomorrow} 15:00:00",
                    "pop": 0.7,  # 70% chance of precipitation
                    "snow": {"3h": 2.0}  # 2.0mm of snow in 3 hours
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "tomorrow"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that precipitation was calculated correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Precipitation forecast for London tomorrow" in call_args
        assert "Chance of precipitation: 80%" in call_args  # Average of 90% and 70%
        assert "Expected snowfall: 3.5 mm" in call_args
        assert "Prepare for wet conditions" in call_args  # pop > 0.5
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_precipitation_calculation_tomorrow_moderate(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Create mock response with moderate precipitation data for tomorrow
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Create tomorrow's date for filtering
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Mock data with moderate rain
        mock_response.json.return_value = {
            "list": [
                {
                    "dt_txt": f"{tomorrow} 12:00:00",
                    "pop": 0.3,  # 30% chance of precipitation
                    "rain": {"3h": 0.5}  # 0.5mm of rain in 3 hours
                },
                {
                    "dt_txt": f"{tomorrow} 15:00:00",
                    "pop": 0.4,  # 40% chance of precipitation
                    "rain": {"3h": 0.8}  # 0.8mm of rain in 3 hours
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "tomorrow"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that precipitation was calculated correctly
        call_args = self.dispatcher.utter_message.call_args[1]['text']
        assert "Precipitation forecast for London tomorrow" in call_args
        assert "Chance of precipitation: 35%" in call_args  # Average of 30% and 40%
        assert "Expected rainfall: 1.3 mm" in call_args
        assert "Some precipitation possible" in call_args  # 0.2 < pop < 0.5
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_precipitation_calculation_invalid_time_period(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Create mock response with 200 status code to avoid the API error path
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"list": []}
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "next week"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the correct message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I can only provide precipitation forecasts for today or tomorrow."
        )
    
    @patch('actions.actions_weather_extended.requests.get')
    @patch('actions.actions_weather_extended.get_coordinates')
    @patch('actions.actions_weather_extended.os.environ.get')
    def test_precipitation_calculation_api_error(self, mock_env_get, mock_get_coords, mock_requests_get):
        # Setup mocks
        mock_env_get.return_value = "fake_api_key"
        mock_get_coords.return_value = (51.5074, -0.1278)  # London coordinates
        
        # Create mock response with error
        mock_response = MagicMock()
        mock_response.status_code = 401  # Unauthorized
        mock_requests_get.return_value = mock_response
        
        self.tracker.get_slot.side_effect = lambda slot: "London" if slot == "location" else "today"
        self.action.run(self.dispatcher, self.tracker, self.domain)
        
        # Check that the error message was sent
        self.dispatcher.utter_message.assert_called_with(
            text="I couldn't fetch precipitation data for that location. Try again."
        )