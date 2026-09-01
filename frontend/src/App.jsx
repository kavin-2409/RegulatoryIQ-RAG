import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import ChatMessage from './components/ChatMessage'
import ChatInput from './components/ChatInput'

const API = ''  // empty = same origin (proxied by Vite to localhost:8000)

const WELCOME = {
  role: 'assistant',
  content: {
    answer: "Hello! I'm RegulatorIQ, your AI assistant for Indian financial regulations.\n\nI can answer questions about SEBI and RBI circulars, regulations, and guidelines. Try asking something like:\n• \"What are the SEBI rules on cybersecurity incident reporting?\"\n• \"What are RBI directions on Cash Reserve Ratio for commercial banks?\"\n• \"What is the IT Resilience Index for Market Infrastructure Institutions?\"",
    citations: [],
    confidence: 'high',
    grounded: true,
    retrieved_chunks: 0,
  }
}

export default function App() {
  const [messages, setMessages]     = useState([WELCOME])
  const [loading, setLoading]       = useState(false)
  const [regulator, setRegulator]   = useState(null)   // null = all sources
  const [docCount, setDocCount]     = useState(0)
  const [status, setStatus]         = useState({ api: false, qdrant: false, ollama: false })
  const bottomRef = useRef(null)

  // Check health on mount
  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(data => {
        setStatus({ api: true, qdrant: data.qdrant, ollama: data.ollama })
        setDocCount(data.documents_indexed)
      })
      .catch(() => setStatus({ api: false, qdrant: false, ollama: false }))
  }, [])

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend(question) {
    // Add user message immediately
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setLoading(true)

    try {
      const res = await fetch(`${API}/api/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, regulator, top_k: 3 }),
      })

      if (!res.ok) throw new Error(`Server error ${res.status}`)
      const data = await res.json()

      setMessages(prev => [...prev, { role: 'assistant', content: data }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: {
          answer: `Error: ${err.message}. Make sure the FastAPI backend is running on port 8000.`,
          citations: [],
          confidence: 'low',
          grounded: false,
          retrieved_chunks: 0,
        }
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        regulator={regulator}
        onRegulatorChange={setRegulator}
        docCount={docCount}
        status={status}
      />

      {/* Main chat area */}
      <div className="flex flex-col flex-1 overflow-hidden">
        {/* Header */}
        <header className="bg-slate-900 border-b border-slate-700 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-white font-semibold">
              {regulator ? `${regulator} Regulations` : 'All Regulations'}
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Powered by SEBI · RBI · phi3 · Qdrant
            </p>
          </div>
          {loading && (
            <div className="flex items-center gap-2 text-sm text-blue-400">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              Thinking...
            </div>
          )}
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {messages.map((msg, i) => (
            <ChatMessage key={i} message={msg} />
          ))}
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-5 py-4">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <ChatInput onSend={handleSend} loading={loading} />
      </div>
    </div>
  )
}
