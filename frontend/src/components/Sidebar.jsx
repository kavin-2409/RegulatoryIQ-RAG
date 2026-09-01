export default function Sidebar({ regulator, onRegulatorChange, docCount, status }) {
  const filters = [
    { value: null,   label: 'All Sources' },
    { value: 'SEBI', label: 'SEBI Only' },
    { value: 'RBI',  label: 'RBI Only' },
  ]

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-700 flex flex-col">
      {/* Logo */}
      <div className="p-5 border-b border-slate-700">
        <h1 className="text-xl font-bold text-white">RegulatorIQ</h1>
        <p className="text-xs text-slate-400 mt-1">Indian Financial Regulations AI</p>
      </div>

      {/* Source filter */}
      <div className="p-4 border-b border-slate-700">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Filter by Source
        </p>
        <div className="space-y-1">
          {filters.map(f => (
            <button
              key={String(f.value)}
              onClick={() => onRegulatorChange(f.value)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                regulator === f.value
                  ? 'bg-blue-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="p-4 border-b border-slate-700">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          System Status
        </p>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-400">Documents</span>
            <span className="text-white font-medium">{docCount}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Backend</span>
            <span className={status.api ? 'text-green-400' : 'text-red-400'}>
              {status.api ? 'Online' : 'Offline'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Qdrant</span>
            <span className={status.qdrant ? 'text-green-400' : 'text-red-400'}>
              {status.qdrant ? 'Online' : 'Offline'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Ollama</span>
            <span className={status.ollama ? 'text-green-400' : 'text-red-400'}>
              {status.ollama ? 'Online' : 'Offline'}
            </span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-auto p-4">
        <p className="text-xs text-slate-500 text-center">
          Sources: SEBI · RBI
        </p>
      </div>
    </aside>
  )
}
