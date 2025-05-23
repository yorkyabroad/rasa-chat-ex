# Weather Chatbot with Rasa

A conversational AI chatbot built with Rasa framework that provides weather information to users.

## Features

- Real-time weather information retrieval
- Natural language understanding for weather-related queries
- Support for multiple conversation flows
- Automated testing and continuous integration

## Prerequisites

- Python 3.10 or higher
- Rasa framework
- Weather API credentials (see `.env.example`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rasa-chat
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

## Project Structure

```
├── actions/              # Custom action code
├── data/                # Training data
│   ├── nlu.yml         # Natural Language Understanding data
│   ├── rules.yml       # Conversation rules
│   └── stories.yml     # Conversation stories/flows
├── models/              # Trained model files
├── tests/              # Test files
└── config.yml          # Model configuration
```

## Running the Chatbot

1. Start the actions server:
```bash
rasa run actions
```

2. In a new terminal, start the Rasa shell:
```bash
rasa shell
```

## Development

### Training the Model

To train a new model:
```bash
rasa train
```

### Testing

Run the test suite:
```bash
python -m pytest tests/
```

For NLU testing:
```bash
rasa shell nlu
```

### Code Quality

The project uses:
- Pytest for testing
- GitHub Actions for CI/CD
- Code coverage reporting

## API Documentation

### Custom Actions

The chatbot implements custom actions in `actions/actions.py`:
- Weather information retrieval
- Input validation
- Response formatting

### Configuration

- `config.yml`: Model pipeline and policies configuration
- `domain.yml`: Bot responses, actions, and entities
- `endpoints.yml`: Service endpoint configurations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

See LICENSE file

## Acknowledgments

- Rasa framework team
- Weather API provider