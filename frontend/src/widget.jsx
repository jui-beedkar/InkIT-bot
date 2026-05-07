import React from 'react';
import ReactDOM from 'react-dom/client';
import ChatWidget from './components/ChatWidget';
import './index.css';

// This script will automatically create a container and mount the chatbot
const WidgetWrapper = () => {
  const [isDark, setIsDark] = React.useState(
    window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  const toggleTheme = () => {
    setIsDark(prev => !prev);
  };

  return <ChatWidget isDark={isDark} toggleTheme={toggleTheme} />;
};

const initChatbot = () => {
  const containerId = 'inkit-chatbot-root';
  let container = document.getElementById(containerId);

  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    document.body.appendChild(container);
  }

  const root = ReactDOM.createRoot(container);
  
  root.render(
    <React.StrictMode>
      <WidgetWrapper />
    </React.StrictMode>
  );
};

if (document.readyState === 'complete') {
  initChatbot();
} else {
  window.addEventListener('load', initChatbot);
}
