import React, { useState, useEffect } from 'react'
import ChatWidget from './components/ChatWidget'

function App() {
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)
  })

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [isDark])

  const toggleTheme = () => setIsDark(!isDark)

  return (
    <div className="min-h-screen bg-transparent">
      {/* Chatbot Widget */}
      <ChatWidget isDark={isDark} toggleTheme={toggleTheme} />
    </div>
  )
}

export default App
