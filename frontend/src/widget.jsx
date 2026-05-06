import React from 'react';
import ReactDOM from 'react-dom/client';
import ChatWidget from './components/ChatWidget';
import './index.css';

// This script will automatically create a container and mount the chatbot
const initChatbot = () => {
  const containerId = 'inkit-chatbot-root';
  let container = document.getElementById(containerId);

  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    document.body.appendChild(container);
  }

  const root = ReactDOM.createRoot(container);
  
  // Default to light mode for the widget unless specified or detected
  const isDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  root.render(
    <React.StrictMode>
      <ChatWidget isDark={isDark} toggleTheme={() => {}} />
    </React.StrictMode>
  );
};

if (document.readyState === 'complete') {
  initChatbot();
} else {
  window.addEventListener('load', initChatbot);
}
