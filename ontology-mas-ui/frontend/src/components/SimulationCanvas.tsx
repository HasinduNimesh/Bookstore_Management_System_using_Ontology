// React not needed explicitly with TSX + Vite React plugin
import { useAppStore } from '../store/appStore'
import type { SimulationEvent } from '../store/appStore'

function renderEventBody(event: SimulationEvent) {
  switch (event.type) {
    case 'observation':
      return (
        <span className="text-gray-600">
          {event.agentId} observed <strong>{event.obs}</strong>
        </span>
      )
    case 'inference': {
      const formattedLog = typeof event.logprob === 'number' ? event.logprob.toFixed(2) : '—'
      return (
        <span className="text-gray-600">
          {event.agentId} inferred {event.custId} → <strong>{event.inferredState}</strong> ({formattedLog})
        </span>
      )
    }
    case 'inventory':
      return (
        <span className="text-gray-600">
          <span className="font-semibold capitalize">{event.category}</span> {event.title}
          {typeof event.delta === 'number' && event.delta !== 0 && (
            <span className="ml-1 font-mono">{event.delta > 0 ? `+${event.delta}` : event.delta}</span>
          )}
          <span className="ml-2 text-xs text-gray-500">on-hand: {event.remaining}</span>
        </span>
      )
    default:
      return <span className="text-gray-600">{JSON.stringify(event)}</span>
  }
}

export default function SimulationCanvas() {
  const { gridState, events, currentTick, pendingRestocks } = useAppStore()

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Grid visualization */}
      <div className="flex-1 p-2 lg:p-4 overflow-auto">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between mb-2 lg:mb-3 gap-2">
          <h2 className="text-sm lg:text-lg font-bold">Grid (Tick: {currentTick})</h2>
          <div className="flex flex-wrap gap-2 lg:gap-4 text-xs">
            <div className="flex items-center gap-1">
              <span className="w-4 h-4 bg-blue-500 rounded flex items-center justify-center text-white">👤</span>
              <span className="hidden lg:inline">Customer Agents (browsing & purchasing)</span>
              <span className="lg:hidden">Customers</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="w-4 h-4 bg-green-500 rounded flex items-center justify-center text-white">🛠️</span>
              <span className="hidden lg:inline">Service Agents (restocking inventory)</span>
              <span className="lg:hidden">Service</span>
            </div>
            {pendingRestocks && pendingRestocks.length > 0 && (
              <div className="flex items-center gap-1">
                <span className="w-4 h-4 bg-orange-500 rounded flex items-center justify-center text-white">🚚</span>
                <span className="text-orange-600 font-semibold text-xs">{pendingRestocks.length} <span className="hidden sm:inline">Restocks In Transit</span><span className="sm:hidden">Transit</span></span>
              </div>
            )}
          </div>
        </div>
        
        {gridState && (
          <div className="inline-block">
            <div 
              className="grid gap-1 bg-gray-100 p-2 rounded"
              style={{
                gridTemplateColumns: `repeat(${gridState.width}, 40px)`,
                gridTemplateRows: `repeat(${gridState.height}, 40px)`
              }}
            >
              {Array.from({ length: gridState.height }).map((_, y) => (
                Array.from({ length: gridState.width }).map((_, x) => {
                  // Find agents at this position (can be multiple)
                  const agentsHere = gridState.occupied.filter(
                    (item: any) => item.x === x && item.y === y
                  )
                  const hasAgents = agentsHere.length > 0
                  const hasService = agentsHere.some((a: any) => a.agentType === 'service')
                  const hasCustomer = agentsHere.some((a: any) => a.agentType === 'customer')
                  
                  // Determine display
                  let bgColor = 'bg-white hover:bg-gray-50'
                  let icon = ''
                  let tooltip = `Empty (${x}, ${y})`
                  
                  if (hasAgents) {
                    if (hasService && hasCustomer) {
                      bgColor = 'bg-purple-500 text-white hover:bg-purple-600'
                      icon = '🛍️' // Shopping - customer + service interaction
                    } else if (hasService) {
                      bgColor = 'bg-green-500 text-white hover:bg-green-600'
                      icon = '🛠️'
                    } else {
                      bgColor = 'bg-blue-500 text-white hover:bg-blue-600'
                      icon = '👤'
                    }
                    tooltip = agentsHere.map((a: any) => a.agentId).join(', ') + ` at (${x}, ${y})`
                  }
                  
                  return (
                    <div
                      key={`${x}-${y}`}
                      className={`w-10 h-10 border rounded flex items-center justify-center text-base transition-colors ${bgColor}`}
                      title={tooltip}
                    >
                      {icon}
                    </div>
                  )
                })
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Event console */}
      <div className="h-64 border-t border-gray-200 bg-gray-50 p-4 overflow-auto">
        <h3 className="font-semibold mb-2">Event Stream</h3>
        <div className="space-y-1 text-xs font-mono">
          {events.slice(-25).reverse().map((event, idx) => (
            <div key={idx} className="p-2 bg-white rounded border border-gray-100">
              <div className="flex items-center justify-between text-[10px] uppercase tracking-wide text-gray-400 mb-1">
                <span>{event.type}</span>
                {typeof event.tick === 'number' && <span>t{event.tick}</span>}
              </div>
              {renderEventBody(event)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
