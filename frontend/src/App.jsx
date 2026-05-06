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
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
      <div className="flex flex-col items-center justify-center min-h-screen p-4 text-center">
        <h1 className="text-4xl md:text-6xl font-bold text-slate-900 dark:text-white mb-6">
          INK IT SOLUTIONS
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mb-8">
          Enterprise IT Consulting & Digital Transformation Experts.
        </p>
        <button 
          onClick={toggleTheme}
          className="px-6 py-2 rounded-full bg-primary text-white hover:bg-primary-dark transition-colors"
        >
          Toggle {isDark ? 'Light' : 'Dark'} Mode
        </button>
      </div>
      
      {/* Chatbot Widget */}
      <ChatWidget isDark={isDark} toggleTheme={toggleTheme} />
    </div>
  )
}

export default App
