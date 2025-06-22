// Unit tests for weather utility functions
describe('Weather Utils', () => {
  const getWeatherIcon = (request) => {
    if (request.includes('Current weather')) return '☀️';
    if (request.includes('forecast') || request.includes('Tomorrow')) return '🌤️';
    if (request.includes('UV')) return '🌞';
    if (request.includes('Wind')) return '💨';
    return '🌡️';
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  test('getWeatherIcon returns correct icons', () => {
    expect(getWeatherIcon('Current weather')).toBe('☀️');
    expect(getWeatherIcon('Tomorrow forecast')).toBe('🌤️');
    expect(getWeatherIcon('UV index')).toBe('🌞');
    expect(getWeatherIcon('Wind conditions')).toBe('💨');
    expect(getWeatherIcon('Temperature')).toBe('🌡️');
  });

  test('formatTime formats date correctly', () => {
    const testDate = new Date('2023-01-01T14:30:00');
    const formatted = formatTime(testDate);
    expect(formatted).toMatch(/\d{1,2}:\d{2}/);
  });
});