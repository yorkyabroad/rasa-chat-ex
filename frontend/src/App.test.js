import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock scrollIntoView
Element.prototype.scrollIntoView = jest.fn();

describe('Weather Assistant App', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders weather assistant title', () => {
    render(<App />);
    expect(screen.getByText('Weather Assistant')).toBeInTheDocument();
  });

  test('renders initial welcome message', () => {
    render(<App />);
    expect(screen.getByText(/Hello! I am your weather assistant/)).toBeInTheDocument();
  });

  test('renders chat input', () => {
    render(<App />);
    expect(screen.getByPlaceholderText('Ask about the weather...')).toBeInTheDocument();
  });

  test('renders quick action buttons', () => {
    render(<App />);
    expect(screen.getByText('London')).toBeInTheDocument();
    expect(screen.getByText('Current weather')).toBeInTheDocument();
  });

  test('allows user to type in input field', async () => {
    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask about the weather...');
    await userEvent.type(input, 'What is the weather in London?');
    
    expect(input).toHaveValue('What is the weather in London?');
  });

  test('sends message when send button is clicked', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ text: 'The weather in London is sunny.' }]
    });

    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask about the weather...');
    await userEvent.type(input, 'Weather in London');
    
    const buttons = screen.getAllByRole('button');
    const sendButton = buttons[buttons.length - 1]; // Last button is the send button
    await userEvent.click(sendButton);
    
    expect(fetch).toHaveBeenCalledWith('http://localhost:5005/webhooks/rest/webhook', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sender: 'user_id_123', message: 'Weather in London' })
    });
  });

  test('displays user message after sending', async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ text: 'Bot response' }]
    });

    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask about the weather...');
    await userEvent.type(input, 'Test message');
    
    const buttons = screen.getAllByRole('button');
    const sendButton = buttons[buttons.length - 1];
    await userEvent.click(sendButton);
    
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));

    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask about the weather...');
    await userEvent.type(input, 'Test message');
    
    const buttons = screen.getAllByRole('button');
    const sendButton = buttons[buttons.length - 1];
    await userEvent.click(sendButton);
    
    await waitFor(() => {
      expect(screen.getByText(/Could not connect to the chatbot/)).toBeInTheDocument();
    });
  });

  test('quick action selection works', async () => {
    render(<App />);
    
    await userEvent.click(screen.getByText('London'));
    await userEvent.click(screen.getByText('Current weather'));
    
    expect(screen.getByText('Ask: Current weather in London')).toBeInTheDocument();
  });
});