function ConfidenceBadge({ confidence }) {
  const colors = {
    high:   'bg-green-900 text-green-300 border-green-700',
    medium: 'bg-yellow-900 text-yellow-300 border-yellow-700',
    low:    'bg-red-900 text-red-300 border-red-700',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${colors[confidence] || colors.low}`}>
      {confidence} confidence
    </span>
  )
}

function GroundedBadge({ grounded }) {
  return grounded ? (
    <span className="text-xs px-2 py-0.5 rounded-full border bg-emerald-900 text-emerald-300 border-emerald-700 font-medium">
      ✓ grounded
    </span>
  ) : (
    <span className="text-xs px-2 py-0.5 rounded-full border bg-orange-900 text-orange-300 border-orange-700 font-medium">
      ⚠ verify sources
    </span>
  )
}

export default function ChatMessage({ message }) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end mb-4">
        <div className="bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-xl text-sm">
          {message.content}
        </div>
      </div>
    )
  }

  // Assistant message
  const { answer, citations, confidence, grounded, retrieved_chunks } = message.content

  return (
    <div className="flex justify-start mb-6">
      <div className="max-w-2xl w-full">
        {/* Answer bubble */}
        <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-5 py-4">
          <p className="text-slate-100 text-sm leading-relaxed whitespace-pre-wrap">{answer}</p>

          {/* Badges */}
          <div className="flex items-center gap-2 mt-3 flex-wrap">
            <ConfidenceBadge confidence={confidence} />
            <GroundedBadge grounded={grounded} />
            <span className="text-xs text-slate-500">{retrieved_chunks} chunks retrieved</span>
          </div>
        </div>

        {/* Citations */}
        {citations && citations.length > 0 && (
          <div className="mt-2 pl-1">
            <p className="text-xs text-slate-500 mb-1 font-medium uppercase tracking-wider">Sources</p>
            <div className="space-y-1">
              {citations.map((c, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-400">
                  <span className="text-blue-400 font-medium shrink-0">[{i + 1}]</span>
                  <div>
                    <span className="text-slate-300">{c.source}</span>
                    {c.url && (
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="ml-2 text-blue-400 hover:text-blue-300 underline"
                      >
                        View circular ↗
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
