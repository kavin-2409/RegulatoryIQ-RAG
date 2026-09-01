import { useState } from 'react'

export default function ChatInput({ onSend, loading }) {
  const [text, setText] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const q = text.trim()
    if (!q || loading) return
    onSend(q)
    setText('')
  }

  function handleKeyDown(e) {
    // Submit on Enter, new line on Shift+Enter
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-slate-700 bg-slate-900">
      <div className="flex items-end gap-3 bg-slate-800 border border-slate-600 rounded-xl px-4 py-3 focus-within:border-blue-500 transition-colors">
        <textarea
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about SEBI or RBI regulations..."
          rows={1}
          disabled={loading}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm resize-none outline-none min-h-[24px] max-h-32"
          style={{ height: 'auto' }}
          onInput={e => {
            e.target.style.height = 'auto'
            e.target.style.height = e.target.scrollHeight + 'px'
          }}
        />
        <button
          type="submit"
          disabled={!text.trim() || loading}
          className="shrink-0 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
        >
          {loading ? '...' : 'Ask'}
        </button>
      </div>
      <p className="text-xs text-slate-600 mt-2 text-center">
        Press Enter to send · Shift+Enter for new line
      </p>
    </form>
  )
}
