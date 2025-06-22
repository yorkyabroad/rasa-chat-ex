import React, { useState, useEffect, useRef } from 'react';

// Main App component for the Rasa Chatbot UI
const App = () => {
    // State to store chat messages with initial welcome message
    const [messages, setMessages] = useState([
        { text: 'Hello! I am your weather assistant. How can I help you today?', sender: 'bot' },
        { text: '', sender: 'spacer' }
    ]);
    // State to store the current user input
    const [userInput, setUserInput] = useState('');
    const [selectedLocation, setSelectedLocation] = useState('');
    const [selectedRequest, setSelectedRequest] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    // Ref to automatically scroll to the latest message
    const messagesEndRef = useRef(null);

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

    const RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook';

    useEffect(() => {
        console.log("Rasa API URL configured:", RASA_API_URL);
    }, [RASA_API_URL]);

    useEffect(() => {
        if (messagesEndRef.current) {
            messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    const addMessage = (text, sender) => {
        setMessages((prevMessages) => [...prevMessages, { text, sender, timestamp: new Date() }]);
    };

    const sendMessage = async () => {
        const message = userInput.trim();
        if (!message) return;

        addMessage(message, 'user');
        setUserInput('');
        setIsLoading(true);

        try {
            const response = await fetch(RASA_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sender: 'user_id_123',
                    message: message,
                }),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
            }

            const data = await response.json();

            if (data && Array.isArray(data)) {
                data.forEach((botResponse) => {
                    if (botResponse.text) {
                        addMessage(botResponse.text, 'bot');
                    }
                });
            } else {
                addMessage('No valid response from bot.', 'bot');
            }

        } catch (error) {
            console.error('Error sending message to Rasa:', error);
            addMessage(
                `Oops! Could not connect to the chatbot. Please ensure the Rasa server is running and accessible at "${RASA_API_URL}". Check your browser's console (F12) and network tab for more details.`,
                'bot'
            );
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    return (
        <div style={{minHeight: '100vh', background: 'linear-gradient(135deg, #87CEEB 0%, #98D8E8 25%, #B0E0E6 50%, #E0F6FF 75%, #F0F8FF 100%)', padding: '16px'}}>
            <h1 className="text-4xl font-bold text-gray-800 text-center mb-6" style={{width: '100%', textAlign: 'center'}}>Weather Assistant</h1>
            <div style={{display: 'flex', justifyContent: 'center', width: '100%'}}>
                <div style={{display: 'flex', flexDirection: window.innerWidth < 1024 ? 'column' : 'row', gap: '24px', width: 'fit-content', alignItems: window.innerWidth < 1024 ? 'center' : 'flex-start'}}>
                {/* Chat Interface */}
                <div style={{flex: '1', maxWidth: '600px', display: 'flex', flexDirection: 'column', gap: '16px'}}>
                    {/* Chat Messages Display Area */}
                    <div style={{backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', height: '350px', border: '4px solid #8b5cf6', overflow: 'hidden'}}>
                        <div style={{flex: 1, padding: '24px 32px 24px 32px', overflowY: 'auto', background: 'linear-gradient(to bottom, #f9fafb, white)', height: '100%', scrollBehavior: 'smooth'}}>
                            {messages.map((msg, index) => (
                                <div key={index}>
                                    {msg.sender === 'spacer' ? (
                                        <div style={{height: '32px'}}></div>
                                    ) : (
                                        <div
                                            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn group`}
                                            style={{marginBottom: index === messages.length - 1 ? '0px' : (msg.sender === 'bot' && messages[index + 1]?.sender === 'user' ? '32px' : '4px')}}
                                        >
                                            <div
                                                className={`max-w-[85%] p-4 rounded-2xl shadow-lg backdrop-blur-sm transition-all duration-200 hover:shadow-xl break-words ${
                                                    msg.sender === 'user'
                                                        ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-br-md'
                                                        : 'bg-white text-gray-800 rounded-bl-md border-l-4 border-purple-400'
                                                }`}
                                            >
                                                <div className={`leading-7 whitespace-pre-line break-words ${msg.sender === 'user' ? 'text-sm' : 'text-base'}`}>
                                                    {msg.text}
                                                </div>
                                                {msg.timestamp && (
                                                    <div style={{fontSize: '10px', opacity: 0.7, marginTop: '4px', textAlign: msg.sender === 'user' ? 'right' : 'left'}}>
                                                        {formatTime(msg.timestamp)}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ))}
                            {isLoading && (
                                <div className="flex justify-start animate-fadeIn">
                                    <div className="bg-white text-gray-800 rounded-bl-md border-l-4 border-purple-400 p-4 rounded-2xl shadow-lg">
                                        <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                                            <div style={{display: 'flex', gap: '4px'}}>
                                                <div style={{width: '8px', height: '8px', backgroundColor: '#8b5cf6', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out'}}></div>
                                                <div style={{width: '8px', height: '8px', backgroundColor: '#8b5cf6', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out 0.16s'}}></div>
                                                <div style={{width: '8px', height: '8px', backgroundColor: '#8b5cf6', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out 0.32s'}}></div>
                                            </div>
                                            <span style={{fontSize: '14px', color: '#6b7280'}}>Bot is typing...</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>
                    </div>

                    {/* Quick Action Buttons */}
                    <div style={{backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', padding: '16px', border: '4px solid #8b5cf6', marginBottom: '16px'}}>
                        <div style={{marginBottom: '12px', textAlign: 'center', fontSize: '14px', fontWeight: 'bold', color: '#6b7280'}}>Quick Actions</div>
                        
                        <div style={{marginBottom: '16px'}}>
                            <div style={{marginBottom: '8px', fontSize: '12px', fontWeight: 'bold', color: '#374151'}}>Locations:</div>
                            <div style={{display: 'flex', flexWrap: 'wrap', gap: '6px'}}>
                                {['London', 'New York', 'Tokyo', 'Sydney', 'Paris', 'Stockholm', 'Leeds', 'Härnösand', 'Brighton', 'Boden', 'Bordeaux'].map((location, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setSelectedLocation(location)}
                                        style={{
                                            padding: '6px 12px',
                                            backgroundColor: selectedLocation === location ? '#8b5cf6' : '#f3f4f6',
                                            color: selectedLocation === location ? 'white' : '#374151',
                                            border: '2px solid ' + (selectedLocation === location ? '#8b5cf6' : '#e5e7eb'),
                                            borderRadius: '16px',
                                            fontSize: '12px',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        {location}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div style={{marginBottom: '16px'}}>
                            <div style={{marginBottom: '8px', fontSize: '12px', fontWeight: 'bold', color: '#374151'}}>Weather Requests:</div>
                            <div style={{display: 'flex', flexWrap: 'wrap', gap: '6px'}}>
                                {['Current weather', 'Tomorrow forecast', 'UV index', 'Wind conditions'].map((request, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setSelectedRequest(request)}
                                        style={{
                                            padding: '6px 12px',
                                            backgroundColor: selectedRequest === request ? '#8b5cf6' : '#f3f4f6',
                                            color: selectedRequest === request ? 'white' : '#374151',
                                            border: '2px solid ' + (selectedRequest === request ? '#8b5cf6' : '#e5e7eb'),
                                            borderRadius: '16px',
                                            fontSize: '12px',
                                            cursor: 'pointer',
                                            transition: 'all 0.2s',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '4px'
                                        }}
                                    >
                                        <span>{getWeatherIcon(request)}</span>
                                        {request}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <button
                            onClick={async () => {
                                if (!selectedLocation || !selectedRequest) return;
                                const query = `${selectedRequest} in ${selectedLocation}`;
                                addMessage(query, 'user');
                                setIsLoading(true);
                                
                                try {
                                    const response = await fetch(RASA_API_URL, {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json',
                                        },
                                        body: JSON.stringify({
                                            sender: 'user_id_123',
                                            message: query,
                                        }),
                                    });

                                    if (!response.ok) {
                                        const errorText = await response.text();
                                        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
                                    }

                                    const data = await response.json();

                                    if (data && Array.isArray(data)) {
                                        data.forEach((botResponse) => {
                                            if (botResponse.text) {
                                                addMessage(botResponse.text, 'bot');
                                            }
                                        });
                                    } else {
                                        addMessage('No valid response from bot.', 'bot');
                                    }
                                } catch (error) {
                                    console.error('Error sending message to Rasa:', error);
                                    addMessage(
                                        `Oops! Could not connect to the chatbot. Please ensure the Rasa server is running and accessible at "${RASA_API_URL}". Check your browser's console (F12) and network tab for more details.`,
                                        'bot'
                                    );
                                } finally {
                                    setIsLoading(false);
                                }
                                setSelectedLocation('');
                                setSelectedRequest('');
                            }}
                            disabled={!selectedLocation || !selectedRequest}
                            style={{
                                width: '100%',
                                padding: '12px',
                                backgroundColor: (!selectedLocation || !selectedRequest) ? '#d1d5db' : '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: '12px',
                                fontSize: '14px',
                                fontWeight: 'bold',
                                cursor: (!selectedLocation || !selectedRequest) ? 'not-allowed' : 'pointer',
                                transition: 'all 0.2s'
                            }}
                        >
                            {selectedLocation && selectedRequest ? `Ask: ${selectedRequest} in ${selectedLocation}` : 'Select location and request'}
                        </button>
                    </div>

                    {/* Chat Input Area */}
                    <div style={{backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', padding: '16px', border: '4px solid #8b5cf6', display: 'flex', alignItems: 'end', gap: '12px'}}>
                        <textarea
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask about the weather..."
                            className="flex-1 p-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400 focus:border-transparent resize-none min-h-[52px] max-h-32 overflow-y-auto bg-white/90 backdrop-blur-sm shadow-sm transition-all duration-200 placeholder-gray-500"
                            rows="1"
                            style={{
                                height: 'auto',
                                minHeight: '52px'
                            }}
                            onInput={(e) => {
                                e.target.style.height = 'auto';
                                e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px';
                            }}
                        />
                        <button
                            onClick={sendMessage}
                            className="p-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-xl shadow-lg hover:from-purple-600 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-purple-400 transition-all duration-200 transform hover:scale-105 active:scale-95 flex-shrink-0"
                        >
                            <svg
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                strokeWidth={2}
                                stroke="currentColor"
                                className="w-6 h-6"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
                                />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Information Panel */}
                <div style={{flex: '1', maxWidth: '600px', display: window.innerWidth < 1024 ? 'none' : 'block'}}>
                    <div style={{backgroundColor: 'white', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)', padding: '24px', overflowY: 'auto', height: '350px', border: '4px solid #8b5cf6'}}>
                        <div className="text-gray-800">
                            <h2 className="text-2xl font-bold text-purple-600 mb-4">Weather Chatbot</h2>
                            <p className="text-sm text-gray-600 mb-6">A Rasa-powered chatbot that provides weather information and forecasts using the OpenWeather API.</p>
                            
                            <h3 className="text-lg font-semibold text-purple-600 mb-3">Features</h3>
                            <ul className="text-sm space-y-2 text-gray-700">
                                <li>Get current weather for any location</li>
                                <li>Get weather forecasts for up to 3 days</li>
                                <li>Get UV index information and safety recommendations</li>
                                <li>Get UV index forecasts for future days</li>
                                <li>Get temperature ranges, minimums, and maximums for today and tomorrow</li>
                                <li>Get air pollution data and health recommendations</li>
                                <li>Get air pollution forecasts for tomorrow</li>
                                <li>Compare weather conditions with historical averages</li>
                                <li>Get humidity information</li>
                                <li>Get local time for any location</li>
                                <li>Get precipitation details (rain/snow forecasts)</li>
                                <li>Get wind conditions (speed, direction, recommendations)</li>
                                <li>Get sunrise and sunset times</li>
                                <li>Get severe weather alerts and warnings</li>
                                <li>Compare today's weather with yesterday's weather</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
            </div>
        </div>
    );
};

export default App;