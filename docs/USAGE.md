# Usage Guide

## Getting Started

### Initial Setup

1. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your API credentials
```

2. **Training the Model**
```bash
rasa train
```

### Running the Chatbot

1. **Start the Action Server**
```bash
# Terminal 1
rasa run actions
```

2. **Start the Chatbot**
```bash
# Terminal 2
rasa shell
```

## Common Use Cases

### 1. Checking Current Weather

User: "What's the weather like in London?"
Bot: *Provides current weather information for London*

User: "How's the weather in San Francisco right now?"
Bot: *Provides current weather information for San Francisco*

User: "Tell me about the current conditions in Sydney"
Bot: *Provides current weather information for Sydney*

### 2. Weather Forecast

User: "Will it rain tomorrow in Paris?"
Bot: *Provides weather forecast for Paris*

User: "What's the weather going to be like this weekend in Berlin?"
Bot: *Provides weekend forecast for Berlin*

User: "Do I need an umbrella in Toronto on Friday?"
Bot: *Provides precipitation forecast for Toronto on Friday*

### 3. Specific Weather Attributes

User: "How's the humidity in Tokyo?"
Bot: *Provides humidity information for Tokyo*

User: "What's the UV index in Miami today?"
Bot: *Provides UV index information with safety recommendations for Miami*

User: "What's the wind speed in Chicago today?"
Bot: *Provides wind speed information for Chicago*

User: "How hot will it get in Dubai tomorrow?"
Bot: *Provides temperature forecast for Dubai*

User: "Do I need sunscreen in Los Angeles today?"
Bot: *Provides UV index information with protection advice for Los Angeles*

### 3.1 UV Index Information

User: "What's the UV index in Miami today?"
Bot: *Provides current UV index with protection recommendations*

User: "Will I need sunscreen in Barcelona tomorrow?"
Bot: *Provides UV index forecast with protection advice*

User: "What will the UV index be like in Sydney this weekend?"
Bot: *Provides UV index forecast for the weekend*

User: "Is the UV index dangerous in Phoenix today?"
Bot: *Provides UV risk level assessment and safety recommendations*

### 4. Time-Based Weather Queries

User: "What's the weather like in London at 3pm?"
Bot: *Provides weather forecast for London at 3pm*

User: "Will it be cold tonight in Montreal?"
Bot: *Provides evening temperature forecast for Montreal*

User: "What's the morning forecast for Singapore?"
Bot: *Provides morning weather forecast for Singapore*

### 5. Comparative Weather Queries

User: "Is it warmer in Miami or Los Angeles today?"
Bot: *Compares temperatures between Miami and Los Angeles*

User: "Which is rainier this week, Seattle or Portland?"
Bot: *Compares precipitation forecasts between Seattle and Portland*

## Conversation Examples

```
User: Hi
Bot: Hello! I can help you with weather information. What city would you like to know about?

User: What's the weather like in New York?
Bot: Let me check that for you. In New York, it's currently 72°F with partly cloudy skies.

User: How about tomorrow?
Bot: Tomorrow in New York, expect a high of 75°F with sunny conditions.
```

## Troubleshooting

### Common Issues

1. **API Connection Issues**
   - Check your internet connection
   - Verify API credentials in .env file
   - Ensure API service is available

2. **Model Training Issues**
   - Clear the models/ directory
   - Verify training data format
   - Check for conflicting training examples

3. **Action Server Problems**
   - Verify action server is running
   - Check port availability
   - Review action server logs

### Debug Mode

To run the bot in debug mode:
```bash
rasa shell --debug
```

## Advanced Usage

### Custom Configurations

Modify `config.yml` to adjust:
- NLU pipeline components
- Policy configuration
- Model architecture

### Adding New Training Data

1. Add intents to `data/nlu.yml`:
```yaml
- intent: new_intent
  examples: |
    - example 1
    - example 2
```

2. Add stories to `data/stories.yml`:
```yaml
- story: new story
  steps:
    - intent: new_intent
    - action: action_response
```

### Testing

1. **Run All Tests**
```bash
python -m pytest
```

2. **Test NLU Model**
```bash
rasa test nlu
```

3. **Test Stories**
```bash
rasa test core
```

## Best Practices

1. **Conversation Design**
   - Keep responses concise
   - Provide clear options to users
   - Handle edge cases gracefully

2. **Model Training**
   - Regular model updates
   - Balanced training data
   - Validate model performance

3. **Maintenance**
   - Monitor API usage
   - Review conversation logs
   - Update dependencies regularly