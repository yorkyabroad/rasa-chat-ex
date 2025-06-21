# Architecture Documentation

## Overview

The Weather Chatbot is built using the Rasa framework, which provides a modular architecture for building conversational AI applications. The system consists of several key components that work together to process user inputs, understand intent, and generate appropriate responses.

## System Components

### 1. Natural Language Understanding (NLU)

The NLU component processes user input to:
- Identify user intent (e.g., asking for weather)
- Extract entities (e.g., location, time)
- Classify the overall meaning of the message

**Key files:**
- `data/nlu.yml`: Training examples for intent recognition
- `config.yml`: NLU pipeline configuration

### 2. Dialogue Management

The dialogue management system:
- Tracks conversation state
- Determines appropriate next actions
- Manages the flow of conversation

**Key files:**
- `data/stories.yml`: Conversation flow examples
- `data/rules.yml`: Specific conversation rules
- `domain.yml`: Defines the universe of the bot

### 3. Custom Actions and Utilities

Custom actions extend the bot's capabilities by:
- Connecting to external APIs (weather service)
- Processing and formatting responses
- Handling complex logic

**Key files:**
- `actions/actions.py`: Implementation of custom actions
- `actions/weather_utils.py`: Weather API integration utilities and helper functions

The weather utilities module provides:
- API endpoint configuration
- Retry logic for API calls
- Structured data classes for responses
- Helper functions for UV index interpretation
- Error handling and logging

## Data Flow

1. **User Input** → The user sends a message to the chatbot
2. **NLU Processing** → The message is processed to determine intent and extract entities
3. **Dialogue Management** → The system determines the next action based on the current state
4. **Action Execution** → If required, a custom action is executed
5. **Response Generation** → A response is generated and sent back to the user

```
User Input → NLU → Dialogue Management → Action Execution → Response Generation
```

## Integration Points

### External Services

- **Weather API**: Provides real-time weather data
  - Connection managed through `actions/weather_utils.py`
  - Configured via environment variables
  - Endpoints used:
    - Current weather data
    - Weather forecast
    - Current UV index data
    - UV index forecast data
    - Air pollution data
    - Air pollution forecast data
    - Geolocation data

### Deployment Architecture

```
                   ┌─────────────────┐
                   │                 │
                   │  Weather API    │
                   │                 │
                   └────────┬────────┘
                            │
                            ▼
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│             │     │                 │     │                 │
│  User       │◄────┤  Rasa Server    │◄────┤  Action Server  │
│             │     │                 │     │                 │
└─────────────┘     └─────────────────┘     └─────────────────┘
```

## Security Considerations

1. **API Key Management**: Weather API keys are stored as environment variables
2. **Input Validation**: All user inputs are validated before processing
3. **Rate Limiting**: API calls are rate-limited to prevent abuse

## Testing Strategy

The project implements a comprehensive testing strategy:

1. **Unit Tests**: Test individual components in isolation
2. **Integration Tests**: Test the interaction between components
3. **End-to-End Tests**: Test the complete conversation flow
4. **NLU Tests**: Specifically test the NLU model's accuracy

## Performance Considerations

- **Caching**: Frequently requested weather data is cached
- **Asynchronous Processing**: Long-running operations are handled asynchronously
- **Model Optimization**: NLU models are optimized for performance

### Weather Data Processing

The system processes various types of weather data:

- **Current Weather**: Temperature, weather conditions, humidity
- **Weather Forecasts**: Multi-day predictions of weather conditions
- **Temperature Ranges**: Min/max temperatures for today and tomorrow
- **UV Index**: Current and forecasted UV levels with safety recommendations
- **Weather Comparisons**: Comparing current conditions to historical averages

Each data type is handled by a specialized action class that:
1. Retrieves the necessary data from the appropriate API endpoint
2. Processes and formats the data for user consumption
3. Provides contextually relevant information based on the data
