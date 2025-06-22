# Weather Assistant Frontend

A React-based frontend for the Rasa Weather Chatbot that provides an intuitive chat interface for weather inquiries.

## Overview

This frontend application connects to a Rasa chatbot backend to provide weather information through a conversational interface. Users can ask about current weather, forecasts, UV index, air quality, and more for any location worldwide.

## Features

- **Interactive Chat Interface**: Clean, modern chat UI with message history
- **Quick Actions**: Pre-configured buttons for common weather requests and popular locations
- **Real-time Communication**: Direct integration with Rasa webhook API
- **Responsive Design**: Works on desktop and mobile devices
- **Weather Icons**: Visual indicators for different weather request types
- **Loading States**: Visual feedback during API calls

## Weather Capabilities

- Current weather conditions
- Weather forecasts (up to 3 days)
- UV index and safety recommendations
- Air pollution data and health advice
- Temperature ranges and extremes
- Wind conditions and recommendations
- Precipitation forecasts
- Sunrise/sunset times
- Severe weather alerts
- Historical weather comparisons

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Running Rasa server on `http://localhost:5005`

## Installation

```bash
npm install
```

## Available Scripts

### `npm start`

Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

### `npm test`

Launches the test runner in interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

## Configuration

The frontend is configured to connect to the Rasa server at `http://localhost:5005/webhooks/rest/webhook`. Ensure your Rasa server is running before starting the frontend.

### Environment Variables

Create a `.env` file in the frontend directory to customize quick-action buttons:

```bash
# Additional locations (up to 10)
REACT_APP_ADDITIONAL_LOCATIONS=Sydney,Paris,Berlin,Madrid,Rome

# Additional weather requests (up to 5)  
REACT_APP_ADDITIONAL_REQUESTS=Sunset time,Chance of rain,Weather alerts,Air quality,Current time
```

See `.env.example` for reference configuration.

## Usage

1. Start the Rasa server (see backend README)
2. Run `npm start` to launch the frontend
3. Open [http://localhost:3000](http://localhost:3000)
4. Start chatting about weather!

## Quick Actions

The interface includes configurable quick action buttons:

### Default Locations
- New York, London, Tokyo, Stockholm (always available)

### Default Weather Requests  
- Current weather, Tomorrow forecast, UV index, Wind conditions (always available)

### Additional Configuration
Customize additional buttons via environment variables:
- **REACT_APP_ADDITIONAL_LOCATIONS**: Up to 10 additional cities
- **REACT_APP_ADDITIONAL_REQUESTS**: Up to 5 additional weather request types

Select a location and request type, then click "Ask" to send the query automatically.

## Testing

### Unit Tests

Run unit tests with Jest and React Testing Library:

```bash
# Run tests once
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm test -- --watch
```

### E2E Tests

Run end-to-end tests with Playwright:

```bash
# Install E2E dependencies
npm install

# Run E2E tests
npm run test:e2e

# Run E2E tests with UI mode
npm run test:e2e:ui
```

### Test Coverage

The test suite covers:
- **Component rendering**: UI elements display correctly
- **User interactions**: Typing, clicking, form submission
- **API integration**: Message sending and response handling
- **Error handling**: Network failures and API errors
- **Quick actions**: Location and request selection
- **Responsive design**: Mobile and desktop layouts
- **Accessibility**: Keyboard navigation and screen readers
