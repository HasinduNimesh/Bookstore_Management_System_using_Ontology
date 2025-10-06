import { useAppStore } from '../store/appStore'

export default function MessageLog() {
  const { events, currentTick } = useAppStore()
  
  // Filter only message events from recent ticks (last 20)
  const messageEvents = events
    .filter(e => e.type === 'message')
    .slice(-20) // Keep last 20 messages
    .reverse() // Most recent first
  
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
    <div className="bg-white rounded-lg shadow p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-2xl">💬</span>
          Agent Messages
          <span className="text-xs font-normal text-gray-500 ml-2">
            (Last 20)
          </span>
        </h2>
        <div className="text-sm text-gray-600">
          Tick: <span className="font-mono font-semibold">{currentTick}</span>
        </div>
      </div>
      
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {messageEvents.map((event, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-lg border ${getMessageColor(event.topic || '')}`}
          >
            <div className="flex items-start gap-3">
              <span className="text-2xl flex-shrink-0">
                {getMessageIcon(event.topic || '')}
              </span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-semibold text-gray-700">
                    {event.from}
                  </span>
                  <span className="text-xs text-gray-400">→</span>
                  <span className="text-xs font-semibold text-gray-700">
                    {event.to}
                  </span>
                  <span className="text-xs text-gray-400 ml-auto">
                    Tick {event.tick || currentTick}
                  </span>
                </div>
                <div className="text-sm text-gray-800 font-medium">
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
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-lg">🛒</span>
            <span className="text-gray-600">Customer requests</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">💬</span>
            <span className="text-gray-600">Service responses</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">📦</span>
            <span className="text-gray-600">Restock orders</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-lg">✅</span>
            <span className="text-gray-600">Deliveries</span>
          </div>
        </div>
      </div>
    </div>
  )
}
