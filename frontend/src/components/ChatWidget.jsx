import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Minus, Maximize2, Moon, Sun, Bot, User, Clock, ExternalLink, Mic, MicOff } from 'lucide-react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import axios from 'axios';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import botIcon from '../assets/bot-icon.png';

const API_URL = window.INKIE_API_URL || 'http://127.0.0.1:8000';

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const LANG_MAP = {
  en: 'en-US',
  de: 'de-DE',
  fr: 'fr-FR',
  es: 'es-ES',
  ar: 'ar-SA'
};

// Animated Icon Component
const BotMascot = ({ isActive, className }) => {
  return (
    <motion.div
      animate={isActive ? {
        y: [0, -5, 0],
        rotate: [0, 5, -5, 0],
        scale: [1, 1.05, 1]
      } : {
        y: 0,
        rotate: 0,
        scale: 1
      }}
      transition={isActive ? {
        duration: 2,
        repeat: Infinity,
        ease: "easeInOut"
      } : {
        duration: 0.5
      }}
      className={cn("relative flex items-center justify-center", className)}
    >
      <img src={botIcon} alt="Bot Mascot" className="w-full h-full object-contain rounded-full" />
      {isActive && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 border-2 border-white dark:border-slate-800 rounded-full"
        />
      )}
    </motion.div>
  );
};

const ChatWidget = ({ isDark, toggleTheme }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [userName, setUserName] = useState(null);
  const [userCountry, setUserCountry] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [backendStatus, setBackendStatus] = useState('checking'); // 'online', 'offline', 'checking'

  const [lastDocUrl, setLastDocUrl] = useState(null);
  const [chatStage, setChatStage] = useState('ask_name');

  const [isBotActive, setIsBotActive] = useState(false);
  const [speechState, setSpeechState] = useState('idle');
  const [speechError, setSpeechError] = useState(null);

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
    isMicrophoneAvailable
  } = useSpeechRecognition();

  const activityTimeoutRef = useRef(null);

  const [messages, setMessages] = useState([{
    id: 1,
    text: "Hello! I'm Inkie, your virtual assistant from INK IT Solutions.\nMay I please know your name so I can assist you better?",
    sender: 'bot',
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    suggestions: []
  }]);

  // Reset session when widget is opened
  useEffect(() => {
    if (isOpen) {
      setUserName(null);
      setUserCountry(null);
      setSelectedLanguage('en');
      setChatStage('ask_name');
      setLastDocUrl(null);
      setMessages([{
        id: Date.now(),
        text: "Hello! I'm Inkie, your virtual assistant from INK IT Solutions.\nMay I please know your name so I can assist you better?",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestions: []
      }]);
    }
  }, [isOpen]);

  const resetSession = () => {
    setUserName(null);
    setUserCountry(null);
    setSelectedLanguage('en');
    setChatStage('ask_name');
    setLastDocUrl(null);
    setMessages([{
      id: Date.now(),
      text: "Hello! I'm Inkie, your virtual assistant from INK IT Solutions.\nMay I please know your name so I can assist you better?",
      sender: 'bot',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestions: []
    }]);
  };
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  // Handle incoming transcript when listening stops
  useEffect(() => {
    if (!listening && transcript) {
      const finalTranscript = transcript.trim();
      if (finalTranscript.length > 1) {
        setInput(finalTranscript);
        handleSend(finalTranscript);
        resetTranscript();
      }
      setSpeechState('idle');
    }
  }, [listening, transcript]);

  // Update speech state based on library listening state
  useEffect(() => {
    if (listening) {
      setSpeechState('listening');
    } else if (speechState === 'listening') {
      setSpeechState('idle');
    }
  }, [listening]);

  // Diagnostics for speech recognition support
  useEffect(() => {
    if (isOpen) {
      const nativeSupport = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
      console.log('[Inkie] Speech Diagnostics:', {
        librarySupported: browserSupportsSpeechRecognition,
        nativeSupport: nativeSupport,
        micAvailable: isMicrophoneAvailable,
        secureContext: window.isSecureContext,
        protocol: window.location.protocol,
        hostname: window.location.hostname
      });

      if (!window.isSecureContext && window.location.hostname !== 'localhost') {
        console.warn("[Inkie] Speech recognition is DISABLED because this site is not using HTTPS. Browsers block microphone access on non-secure sites.");
      }
    }
  }, [isOpen, browserSupportsSpeechRecognition, isMicrophoneAvailable]);

  // Backend Health Check
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await axios.get(`${API_URL}/`);
        if (response.data.status === 'online') {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (err) {
        console.error("[Inkie] Backend health check failed:", err);
        setBackendStatus('offline');
      }
    };

    checkHealth();
    // Check every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleVoiceInput = () => {
    const nativeSupport = !!(window.SpeechRecognition || window.webkitSpeechRecognition);

    if (!window.isSecureContext && window.location.hostname !== 'localhost') {
      setSpeechError("Speech recognition requires a secure connection (HTTPS). Please serve your site over HTTPS.");
      setSpeechState('error');
      return;
    }

    if (!browserSupportsSpeechRecognition && !nativeSupport) {
      setSpeechError("Your browser doesn't support speech recognition. Please use Chrome, Edge, or Safari.");
      setSpeechState('error');
      return;
    }

    if (!isMicrophoneAvailable) {
      setSpeechError("Microphone access is denied. Please enable it in browser settings.");
      setSpeechState('error');
      return;
    }

    if (listening) {
      SpeechRecognition.stopListening();
    } else {
      setSpeechError(null);
      resetTranscript();
      try {
        SpeechRecognition.startListening({
          continuous: false,
          language: LANG_MAP[selectedLanguage] || 'en-US',
          interimResults: true
        });
      } catch (err) {
        console.error("[Inkie] Speech start error:", err);
        setSpeechError("Could not start speech recognition. Try again.");
        setSpeechState('error');
      }
    }
  };

  // Trigger activity and reset idle timer
  const triggerActivity = () => {
    setIsBotActive(true);
    if (activityTimeoutRef.current) clearTimeout(activityTimeoutRef.current);
    activityTimeoutRef.current = setTimeout(() => {
      setIsBotActive(false);
    }, 60000); // 60 seconds idle time
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (text = input) => {
    if (!text.trim()) return;

    triggerActivity();

    const userMessage = {
      id: Date.now(),
      text,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: text,
        user_name: userName,
        user_country: userCountry,
        last_doc_url: lastDocUrl,
        language: selectedLanguage,
        stage: chatStage
      });

      const { response: botText, suggestions, updated_name, updated_country, updated_language, updated_stage, link, last_doc_url } = response.data;

      // Update session info if returned
      if (updated_name) setUserName(updated_name);
      if (updated_country) setUserCountry(updated_country);
      if (updated_language) setSelectedLanguage(updated_language);
      if (updated_stage) setChatStage(updated_stage);
      if (last_doc_url) setLastDocUrl(last_doc_url);

      setTimeout(() => {
        const botMessage = {
          id: Date.now() + 1,
          text: botText,
          sender: 'bot',
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          suggestions: suggestions,
          link: link
        };
        setMessages(prev => [...prev, botMessage]);
        setIsTyping(false);
      }, 800);
    } catch (error) {
      console.error('Chat error:', error);
      setIsTyping(false);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting to my brain right now. 🧠 Please make sure the backend is running and try again!",
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        isError: true
      }]);
    }
  };

  return (
    <div className={cn("fixed bottom-6 right-6 z-50 font-sans", isDark && "dark")}>
      <AnimatePresence mode="wait">
        {!isOpen ? (
          <motion.button
            key="launcher"
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={() => setIsOpen(true)}
            className="w-20 h-20 rounded-full bg-primary text-white shadow-2xl flex items-center justify-center hover:bg-primary-dark transition-all duration-300 group overflow-hidden"
          >
            <BotMascot isActive={false} className="w-14 h-14 group-hover:scale-110 transition-transform" />
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute top-3 right-3 w-4 h-4 bg-red-500 border-2 border-white rounded-full shadow-sm"
            />
          </motion.button>
        ) : (
          <motion.div
            key="chat-window"
            initial={{ scale: 0.8, opacity: 0, y: 100, x: 100 }}
            animate={{ scale: 1, opacity: 1, y: 0, x: 0 }}
            exit={{ scale: 0.8, opacity: 0, y: 100, x: 100 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="w-[450px] max-w-[95vw] h-[650px] max-h-[90vh] flex flex-col glass rounded-3xl shadow-2xl overflow-hidden border border-slate-200/50 dark:border-slate-800/50"
          >
            {/* Header */}
            <div className="p-4 bg-primary text-white flex items-center justify-between shadow-lg">
              <div className="flex items-center gap-4">
                <BotMascot isActive={isBotActive || speechState === 'listening'} className="w-14 h-14 border-2 border-white/20 rounded-full p-0.5 bg-white/10" />
                <div>
                  <h3 className="font-bold text-xl leading-tight">Inkie</h3>
                  <div className="flex items-center gap-2">
                    <span className={cn(
                      "w-2.5 h-2.5 rounded-full",
                      backendStatus === 'online' ? "bg-green-400 animate-pulse" :
                        backendStatus === 'offline' ? "bg-red-500" : "bg-slate-400"
                    )} />
                    <span className="text-sm text-white/80">
                      {backendStatus === 'online' ? 'Online' :
                        backendStatus === 'offline' ? 'Offline' : 'Checking...'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2 relative z-10">
                {/* Language Selector Dropdown */}
                <select
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg px-2 py-1 text-xs text-white focus:outline-none hover:bg-white/20 transition-all cursor-pointer"
                >
                  <option value="en" className="bg-slate-800 text-white">English</option>
                  <option value="de" className="bg-slate-800 text-white">German</option>
                  <option value="fr" className="bg-slate-800 text-white">French</option>
                  <option value="es" className="bg-slate-800 text-white">Spanish</option>
                  <option value="ar" className="bg-slate-800 text-white">Arabic</option>
                </select>

                <motion.button
                  whileHover={{ scale: 1.1, rotate: 180 }}
                  onClick={toggleTheme}
                  title="Toggle Theme"
                  className="p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  {isDark ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  onClick={resetSession}
                  title="Reset Conversation"
                  className="p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  <Clock className="w-6 h-6" />
                </motion.button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div
              ref={scrollRef}
              className="flex-1 overflow-y-auto p-4 space-y-6 bg-slate-50 dark:bg-slate-950"
            >
              {speechError && (
                <div className="sticky top-0 z-10 text-center py-2 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-xs font-medium rounded-lg shadow-sm mb-4 animate-in fade-in slide-in-from-top-2">
                  {speechError}
                </div>
              )}
              {messages.map((msg) => (
                <MessageItem key={msg.id} msg={msg} onSuggestionClick={handleSend} isBotActive={isBotActive} />
              ))}
              {isTyping && (
                <div className="flex gap-3">
                  <BotMascot isActive={true} className="w-10 h-10 opacity-70" />
                  <div className="bg-white dark:bg-slate-900 p-3 rounded-2xl rounded-tl-none shadow-sm flex gap-1 items-center">
                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '400ms' }} />
                  </div>
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white dark:bg-slate-950 border-t border-slate-100 dark:border-slate-800">
              <form
                onSubmit={(e) => { e.preventDefault(); handleSend(); }}
                className="flex items-center gap-2 bg-slate-100 dark:bg-slate-900 p-3 rounded-2xl border border-transparent focus-within:border-primary/30 focus-within:bg-white dark:focus-within:bg-slate-950 transition-all duration-300"
              >
                <input
                  value={listening ? (transcript || 'Listening...') : input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything..."
                  disabled={listening}
                  className="flex-1 bg-transparent border-none focus:ring-0 text-slate-900 dark:text-white px-2 py-1 placeholder:text-slate-400 text-base disabled:opacity-50"
                />

                {/* Voice Input Button */}
                <button
                  type="button"
                  onClick={toggleVoiceInput}
                  aria-label="Start voice input"
                  className={cn(
                    "p-2.5 rounded-full transition-all duration-300 relative overflow-hidden",
                    listening
                      ? "bg-red-500 text-white shadow-lg scale-110"
                      : "text-primary hover:bg-primary/10"
                  )}
                >
                  {listening ? (
                    <>
                      <Mic className="w-6 h-6 animate-pulse" />
                      <motion.div
                        initial={{ scale: 0.8, opacity: 0.5 }}
                        animate={{ scale: 2, opacity: 0 }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="absolute inset-0 bg-red-400 rounded-full"
                      />
                    </>
                  ) : (
                    <Mic className="w-6 h-6" />
                  )}
                </button>

                <button
                  disabled={!input.trim() || speechState === 'listening'}
                  type="submit"
                  className={cn(
                    "p-2.5 rounded-xl transition-all duration-300",
                    (input.trim() && speechState !== 'listening')
                      ? "bg-primary text-white shadow-md hover:scale-105 active:scale-95"
                      : "text-slate-400"
                  )}
                >
                  <Send className="w-6 h-6" />
                </button>
              </form>
              <p className="text-[10px] text-center mt-2 text-slate-400 uppercase tracking-widest font-medium">
                Powered by INK IT SOLUTIONS
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const MessageItem = ({ msg, onSuggestionClick, isBotActive }) => {
  const isBot = msg.sender === 'bot';

  const formatText = (text) => {
    if (!text) return null;

    return text.split('\n').map((line, i) => {
      const trimmedLine = line.trim();

      // Handle Bullet Points (supports -, *, •)
      if (trimmedLine.startsWith('-') || trimmedLine.startsWith('*') || trimmedLine.startsWith('•')) {
        const content = trimmedLine.replace(/^[-*•]\s*/, '');
        return (
          <div key={i} className="flex gap-2 ml-2 my-1 items-start">
            <span className="text-primary mt-1.5 w-1.5 h-1.5 rounded-full bg-primary shrink-0" />
            <span className="flex-1">
              {content.split('**').map((part, j) =>
                j % 2 === 1 ? <strong key={j} className="text-secondary dark:text-primary-light font-bold">{part}</strong> : part
              )}
            </span>
          </div>
        );
      }

      // Handle Regular Lines with Bolding
      return (
        <span key={i} className="block mb-1">
          {line.split('**').map((part, j) =>
            j % 2 === 1 ? <strong key={j} className="text-secondary dark:text-primary-light font-bold">{part}</strong> : part
          )}
        </span>
      );
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, x: isBot ? -10 : 10 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      className={cn("flex gap-4", !isBot && "flex-row-reverse")}
    >
      {isBot ? (
        <BotMascot isActive={isBotActive} className="w-12 h-12 flex-shrink-0" />
      ) : (
        <div className="w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-white">
          <User className="w-6 h-6" />
        </div>
      )}

      <div className={cn("max-w-[85%] flex flex-col gap-1", !isBot && "items-end")}>
        <div className={cn(
          "p-4 rounded-2xl shadow-sm text-base leading-relaxed",
          isBot
            ? "bg-white dark:bg-slate-900 rounded-tl-none text-slate-700 dark:text-slate-200 border border-slate-100 dark:border-slate-800"
            : "bg-primary text-white rounded-tr-none"
        )}>
          {formatText(msg.text)}

          {isBot && msg.link && (
            <motion.a
              href={msg.link}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center justify-center gap-2 w-full py-2.5 bg-primary text-white rounded-xl font-bold hover:bg-primary-dark transition-all transform hover:scale-[1.02]"
            >
              <ExternalLink className="w-4 h-4" />
              Visit Official Page
            </motion.a>
          )}
        </div>

        <div className="flex items-center gap-1 text-[10px] text-slate-400 px-1">
          <Clock className="w-3 h-3" />
          {msg.timestamp}
        </div>

        {isBot && msg.suggestions && msg.suggestions.length > 0 && (
          <motion.div
            initial="hidden"
            animate="visible"
            variants={{
              visible: {
                transition: {
                  staggerChildren: 0.1
                }
              }
            }}
            className="flex flex-wrap gap-2 mt-2"
          >
            {msg.suggestions.map((s, i) => (
              <motion.button
                key={i}
                variants={{
                  hidden: { opacity: 0, scale: 0.8 },
                  visible: { opacity: 1, scale: 1 }
                }}
                whileHover={{ scale: 1.05, backgroundColor: 'var(--color-primary-dark)', color: 'white' }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onSuggestionClick(s)}
                className="text-xs py-2 px-4 rounded-full border border-primary/30 text-primary transition-all duration-300 bg-white dark:bg-slate-900 backdrop-blur-sm font-medium"
              >
                {s}
              </motion.button>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default ChatWidget;
