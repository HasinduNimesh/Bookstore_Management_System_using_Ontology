import { useAppStore } from '../store/appStore'

export default function MessageLog() {
  const { events, currentTick } = useAppStore()
  
  // Keep ALL message events (no slicing), just filter and reverse
  const messageEvents = events
    .filter(e => e.type === 'message')
    .reverse() // Most recent first (but keep all of them)
  
  // Debug log
  console.log('MessageLog - Total events:', events.length, 'Message events:', messageEvents.length)
  
  const getMessageIcon = (topic: string) => {
    switch (topic) {
      case 'purchase_request':
        return '🛒'
      case 'service_response':
        return '💬'
      case 'restock_request':
        return '📦'
      case 'restock_done':
        return '✅'
      default:
        return '📨'
    }
  }
  
  const getMessageColor = (topic: string) => {
    switch (topic) {
      case 'purchase_request':
        return 'bg-blue-50 border-blue-200'
      case 'service_response':
        return 'bg-green-50 border-green-200'
      case 'restock_request':
        return 'bg-orange-50 border-orange-200'
      case 'restock_done':
        return 'bg-emerald-50 border-emerald-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }
  
  if (messageEvents.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <span className="text-2xl">💬</span>
          Agent Messages
        </h2>
        <div className="text-center py-8 text-gray-400">
          <p className="text-sm">No messages yet. Start the simulation to see agent communications.</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="bg-white rounded-lg shadow-lg p-2 lg:p-4 border-2 border-blue-300 h-full flex flex-col">
      <div className="flex items-center justify-between mb-2 bg-blue-50 p-2 rounded">
        <h2 className="text-sm lg:text-lg font-bold text-blue-900 flex items-center gap-1 lg:gap-2">
          <span className="text-lg lg:text-2xl">💬</span>
          <span className="hidden sm:inline">Agent Messages</span>
          <span className="sm:hidden">Messages</span>
          <span className="text-xs font-normal text-blue-600 ml-1 bg-blue-200 px-2 py-1 rounded-full">
            {messageEvents.length} total
          </span>
        </h2>
        <div className="text-xs lg:text-sm text-gray-700 font-semibold">
          Tick: <span className="font-mono bg-yellow-100 px-2 py-1 rounded">{currentTick}</span>
        </div>
      </div>
      
      <div className="space-y-2 flex-1 overflow-y-auto pr-2" style={{scrollBehavior: 'smooth'}}>
        {messageEvents.length === 0 ? (
          <div className="text-center py-4 lg:py-8 text-gray-400">
            <p className="text-xs lg:text-sm">No messages yet...</p>
            <p className="text-xs mt-1 hidden lg:block">Messages will appear when agents communicate</p>
          </div>
        ) : (
          messageEvents.map((event, idx) => (
            <div
              key={idx}
              className={`p-2 lg:p-3 rounded border ${getMessageColor(event.topic || '')}`}
            >
              <div className="flex items-start gap-2">
                <span className="text-lg lg:text-xl flex-shrink-0">
                  {getMessageIcon(event.topic || '')}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1 lg:gap-2 mb-1">
                    <span className="text-xs font-semibold text-gray-700 truncate">
                      {event.from}
                    </span>
                    <span className="text-xs text-gray-400">→</span>
                    <span className="text-xs font-semibold text-gray-700 truncate">
                      {event.to}
                    </span>
                    <span className="text-xs text-gray-400 ml-auto flex-shrink-0">
                      T{event.tick || currentTick}
                    </span>
                  </div>
                  <div className="text-xs lg:text-sm text-gray-800">
                    {event.content}
                  </div>
                  {event.sku && (
                    <div className="text-xs text-gray-500 mt-1">
                      SKU: {event.sku}
                      {event.quantity && ` | Qty: ${event.quantity}`}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
      
      <div className="mt-2 pt-2 border-t border-gray-200 flex-shrink-0">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-1 lg:gap-2 text-xs">
          <div className="flex items-center gap-1">
            <span className="text-sm">🛒</span>
            <span className="text-gray-600 text-xs">Requests</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm">💬</span>
            <span className="text-gray-600 text-xs">Responses</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm">📦</span>
            <span className="text-gray-600 text-xs">Restock</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-sm">✅</span>
            <span className="text-gray-600 text-xs">Delivery</span>
          </div>
        </div>
      </div>
    </div>
  )
}
