import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Message from './components/Message';
import Suggestions from './components/Suggestions';
import FlightCard from './components/FlightCard';

const API_BASE = 'http://localhost:8000';
const speechInputSupported =
  typeof window !== 'undefined' &&
  ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);
const speechOutputSupported =
  typeof window !== 'undefined' && 'speechSynthesis' in window;

const starterMessages = [
  {
    sender: 'bot',
    text: 'Hi! I can help with flights, baggage, flight status, and general travel questions.',
  },
];

function App() {
  const [messages, setMessages] = useState(starterMessages);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [flightInfo, setFlightInfo] = useState(null);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput((prev) => prev ? `${prev} ${transcript}` : transcript);
    };

    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => {
      setIsListening(false);
      setError('Microphone is unavailable or blocked.');
    };

    recognitionRef.current = recognition;
  }, []);

  const handleSend = async (textOverride) => {
    const messageText = (textOverride ?? input).trim();

    if (!messageText) {
      setError('Please type a message before sending.');
      return;
    }

    setError('');
    setInput('');

    const userMessage = { sender: 'user', text: messageText };
    const nextHistory = messages.map((msg) => ({
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.text,
    }));

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        message: messageText,
        history: nextHistory,
      });

      const botMessage = {
        sender: 'bot',
        text: response.data.response || 'I am not able to answer that right now.',
        provider: response.data.provider,
        dataSource: response.data.data_source,
      };

      setMessages((prev) => [...prev, botMessage]);

      if (response.data.data && response.data.tool_used) {
        setFlightInfo(response.data.data);
      } else {
        setFlightInfo(null);
      }
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
          'Cannot connect to the backend server. Please make sure the API is running.'
      );
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: 'I could not reach the airline service. Please try again in a moment.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceToggle = () => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      setError('Speech recognition is not supported in this browser.');
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
      return;
    }

    setIsListening(true);
    recognition.start();
  };

  const speakMessage = (text) => {
    if (!('speechSynthesis' in window)) {
      setError('Text-to-speech is not supported in this browser.');
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const handleClear = () => {
    setMessages(starterMessages);
    setInput('');
    setError('');
    setFlightInfo(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-6">
        <header className="mb-4 rounded-3xl border border-sky-400/20 bg-slate-900/80 px-5 py-4 shadow-soft backdrop-blur-md">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-sky-500/15 text-2xl">✈️</div>
              <div>
                <div className="text-xs uppercase tracking-[0.25em] text-sky-300">Airline AI</div>
                <h1 className="text-xl font-semibold">Customer Support Agent</h1>
              </div>
            </div>
            <button
              onClick={handleClear}
              className="rounded-full border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-slate-200 hover:border-red-400 hover:text-red-300"
            >
              Clear chat
            </button>
          </div>
        </header>

        <main className="flex flex-1 flex-col overflow-hidden rounded-3xl border border-slate-800 bg-slate-900/70 shadow-soft">
          <div className="border-b border-slate-800 p-4">
            <Suggestions onSelect={handleSend} />
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.map((message, index) => (
              <div key={`${message.sender}-${index}`}>
                <Message message={message} />
                {message.sender === 'bot' && message.text && (
                  <div className="ml-4 mb-4 flex justify-start">
                    <button
                      onClick={() => speakMessage(message.text)}
                      disabled={!speechOutputSupported}
                      title={speechOutputSupported ? 'Read response aloud' : 'Speech output is not supported'}
                      className="rounded-full border border-slate-600 bg-slate-800 px-2 py-1 text-xs text-slate-200 hover:border-sky-400 hover:text-sky-300"
                    >
                      🔊 Speak
                    </button>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl bg-slate-800 text-slate-200 px-4 py-3 border border-slate-700">
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-sky-400" />
                    <span className="h-2 w-2 animate-pulse rounded-full bg-sky-400 [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-pulse rounded-full bg-sky-400 [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}

            {flightInfo && <FlightCard flight={flightInfo} />}

            {error && (
              <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-200">
                {error}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-slate-800 bg-slate-950/60 p-4">
            <div className="flex items-center gap-3">
              <button
                onClick={handleVoiceToggle}
                disabled={!speechInputSupported}
                title={speechInputSupported ? 'Use voice input' : 'Speech recognition is not supported'}
                className={`flex h-12 w-12 items-center justify-center rounded-full border text-lg transition ${
                  isListening
                    ? 'border-red-400 bg-red-500/20 text-red-300'
                    : 'border-slate-600 bg-slate-800 text-slate-200 hover:border-sky-400 hover:text-sky-300 disabled:cursor-not-allowed disabled:opacity-40'
                }`}
                type="button"
                aria-label="Toggle microphone"
              >
                🎙️
              </button>

              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSend();
                }}
                placeholder="Ask about flights, baggage, or travel support..."
                className="flex-1 rounded-full border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none placeholder:text-slate-400 focus:border-sky-400"
              />

              <button
                onClick={() => handleSend()}
                disabled={loading}
                className="rounded-full bg-sky-500 px-5 py-3 font-medium text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
              >
                Send
              </button>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
