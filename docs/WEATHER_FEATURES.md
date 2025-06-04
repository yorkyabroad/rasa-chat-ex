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
- **Precipitation Details**: Get information about rainfall and snowfall forecasts, including probability
- **Wind Conditions**: Get information about wind speed, direction, and recommendations for outdoor activities
- **Sunrise/Sunset Times**: Get sunrise and sunset times, as well as daylight hours for a location
- **Weather Comparison**: Compare today's weather with yesterday's weather for a location

## Example Queries

### Severe Weather Alerts
- "Are there any weather alerts for London?"
- "Is there a storm warning in New York?"
- "Will there be any severe weather today in Tokyo?"

### Precipitation Details
- "What's the chance of rain in London tomorrow?"
- "Will it snow in New York this weekend?"
- "How much rainfall is expected in Tokyo today?"

### Wind Conditions
- "How windy will it be in London today?"
- "What's the wind direction in New York?"
- "Is it too windy for outdoor activities in Tokyo?"

### Sunrise/Sunset Times
- "When is sunrise in London today?"
- "What time does the sun set in New York?"
- "How many hours of daylight in Tokyo today?"

### Weather Comparison
- "Is today warmer than yesterday in London?"
- "How does today's weather compare to yesterday in New York?"
- "Is Tokyo colder today than yesterday?"

## Technical Implementation

The weather features are implemented using the OpenWeather API. The following endpoints are used:

- Current Weather: `/data/2.5/weather`
- Weather Forecast: `/data/2.5/forecast`
- One Call API: `/data/2.5/onecall`
- Air Pollution: `/data/2.5/air_pollution`
- UV Index: `/data/2.5/uvi`

Each feature is implemented as a custom action in the Rasa chatbot, which processes the user's request, calls the appropriate API endpoint, and formats the response in a user-friendly way.