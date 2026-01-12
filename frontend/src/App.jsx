import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [initialized, setInitialized] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize chat with greeting on mount (only once)
  useEffect(() => {
    initializeChat()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Empty dependency array - run only once on mount

  const initializeChat = async () => {
    if (initialized) return // Prevent multiple initializations
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: '',
          session_id: sessionId || null
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.session_id) {
          setSessionId(data.session_id)
        }
        if (data.reply) {
          setMessages([{ type: 'ai', content: data.reply }])
        }
      }
    } catch (error) {
      console.error('Error initializing chat:', error)
      setMessages([{ 
        type: 'ai', 
        content: "Hello! I'm your AI food assistance helper. I'm here to help you get free food within 10 minutes. How can I assist you today?" 
      }])
    } finally {
      setInitialized(true)
    }
  }

  const sendMessage = async (e) => {
    e?.preventDefault()
    
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)

    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: userMessage }])

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId || null  // Always send session_id
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      // Always update session ID if provided (important for session continuity)
      if (data.session_id) {
        setSessionId(data.session_id)
      }

      // Add AI response to chat
      setMessages(prev => [...prev, { type: 'ai', content: data.reply }])
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { 
        type: 'ai', 
        content: "I'm sorry, I encountered an error. Please try again or contact support." 
      }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🍽️ Zero Hunger Platform</h1>
        <p>AI-Powered Food Assistance - Get free food within 10 minutes</p>
      </header>

      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              <div className="message-content">
                {msg.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="message ai">
              <div className="message-content">
                <span className="typing-indicator">AI is thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="chat-input-form" onSubmit={sendMessage}>
          <input
            type="text"
            className="chat-input"
            placeholder="Type your message here... (e.g., 'I need food urgently')"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={loading || !input.trim()}
          >
            Send
          </button>
        </form>
      </div>

      <footer className="app-footer">
        <p>No one should sleep hungry. We're here to help.</p>
      </footer>
    </div>
  )
}

export default App
