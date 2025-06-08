# Weather Features

This document outlines the weather-related features available in the Rasa chatbot.

## Basic Weather Features

- **Current Weather**: Get the current weather conditions for a location
- **Weather Forecast**: Get a multi-day weather forecast for a location
- **Temperature Range**: Get minimum and maximum temperatures for a location
- **Humidity**: Get current humidity levels for a location

## Air Quality Features

- **Air Pollution**: Get current air quality information for a location
- **Air Pollution Forecast**: Get forecasted air quality information for a location
- **UV Index**: Get current UV index information for a location
- **UV Index Forecast**: Get forecasted UV index information for a location

## Extended Weather Features

- **Severe Weather Alerts**: Get information about weather warnings and alerts for a location
- **Precipitation Details**: Get information about rainfall and snowfall forecasts, including probability and volume
- **Wind Conditions**: Get information about wind speed, direction, gusts, and recommendations for outdoor activities
- **Sunrise/Sunset Times**: Get sunrise and sunset times, as well as daylight hours for a location
- **Weather Comparison**: Compare today's weather with yesterday's weather for a location

## Time and Location Features

- **Local Time**: Get the current local time for any location worldwide
- **Global Coverage**: Support for cities and locations around the world

## Example Queries

### Severe Weather Alerts
- "Are there any weather alerts for London?"
- "Is there a storm warning in New York?"
- "Will there be any severe weather today in Tokyo?"
- "Any weather warnings for Paris?"
- "Check for weather alerts in Sydney"

### Precipitation Details
- "What's the chance of rain in London tomorrow?"
- "Will it snow in New York this weekend?"
- "How much rainfall is expected in Tokyo today?"
- "Will it rain in Madrid tomorrow?"
- "What's the precipitation forecast for Berlin?"

### Wind Conditions
- "How windy will it be in London today?"
- "What's the wind direction in New York?"
- "Is it too windy for outdoor activities in Tokyo?"
- "What's the wind speed in Paris today?"
- "Wind forecast for Berlin tomorrow"
- "Is it safe to sail in Miami today?"

### Sunrise/Sunset Times
- "When is sunrise in London today?"
- "What time does the sun set in New York?"
- "How many hours of daylight in Tokyo today?"
- "Sunrise time for Paris today"
- "When will the sun rise tomorrow in Sydney?"
- "Tell me only the sunset time in Paris today"

### Weather Comparison
- "Is today warmer than yesterday in London?"
- "How does today's weather compare to yesterday in New York?"
- "Is Tokyo colder today than yesterday?"
- "Compare today and yesterday's weather in Paris"
- "How much has the temperature changed since yesterday in Chicago?"

### Local Time
- "What's the time in New York?"
- "What time is it in Moscow?"
- "Tell me the time in Los Angeles"
- "Current time in Rome"
- "What hour is it in Amsterdam?"

## Technical Implementation

The weather features are implemented using the OpenWeather API. The following endpoints are used:

- Current Weather: `/data/2.5/weather`
- Weather Forecast: `/data/2.5/forecast`
- One Call API: `/data/2.5/onecall`
- Air Pollution: `/data/2.5/air_pollution`
- UV Index: `/data/2.5/uvi`
- Historical Data: `/data/2.5/onecall/timemachine`

Each feature is implemented as a custom action in the Rasa chatbot, which processes the user's request, calls the appropriate API endpoint, and formats the response in a user-friendly way.

## Implementation Details

### Extended Weather Features

The extended weather features are implemented in `actions_weather_extended.py` and include:

- **Severe Weather Alerts**: Analyzes forecast data to detect extreme weather conditions and alerts
- **Precipitation Details**: Calculates precipitation probability and expected rainfall/snowfall volume
- **Wind Conditions**: Provides wind speed, direction, gusts, and outdoor activity recommendations based on the Beaufort scale
- **Sunrise/Sunset Times**: Calculates sunrise, sunset times and total daylight hours for any location
- **Weather Comparison**: Compares current weather with historical data from the previous day

### Air Quality Features

Air quality features are implemented in `actions_air_pollution.py` and `actions_air_pollution_forecast.py`:

- Provides real-time air quality index (AQI) values
- Includes detailed pollutant measurements (PM2.5, PM10, NO₂, O₃)
- Offers health recommendations based on air quality levels
- Forecasts future air quality conditions