import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'
import { useMemo } from 'react'
import { useAppStore } from '../store/appStore'

/**
 * Bookstore Metrics Dashboard
 * Displays real-time book inventory, purchases, restocks, and agent activity
 */
export default function HMMDashboard() {
  const { metrics, customerStates, inventory, events, pendingRestocks } = useAppStore()

  // Chart data for inventory levels
  const inventoryChartData = useMemo(() => 
    inventory.map(item => ({
      name: item.title?.substring(0, 15) + (item.title?.length > 15 ? '...' : ''),
      stock: item.onHand,
      threshold: item.threshold,
      price: item.price
    }))
  , [inventory])

  const statTiles = [
    { label: 'Purchases', value: metrics.purchases, tone: 'bg-blue-50 text-blue-700 border-blue-200' },
    { label: 'Restocks', value: metrics.restocks, tone: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    { label: 'Stockouts', value: metrics.stockouts, tone: 'bg-red-50 text-red-700 border-red-200' },
    { label: 'Revenue', value: `$${metrics.revenue.toFixed(2)}`, tone: 'bg-amber-50 text-amber-700 border-amber-200' }
  ]

  // Recent events (purchases, restocks) - last 10
  const recentEvents = useMemo(() => {
    return events
      .filter(e => e.type === 'inventory' || e.type === 'observation')
      .slice(-10)
      .reverse()
  }, [events])

  return (
    <div className="p-4 space-y-6">
      <div>
        <h2 className="text-lg font-bold mb-3">Bookstore Metrics & KPIs</h2>
        <div className="grid grid-cols-2 gap-3">
          {statTiles.map((tile) => (
            <div key={tile.label} className={`rounded border px-3 py-2 text-sm font-medium ${tile.tone}`}>
              <div className="text-xs uppercase tracking-wide opacity-80">{tile.label}</div>
              <div className="text-lg font-semibold">{tile.value}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-2 text-sm">Book Inventory Stock Levels</h3>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={inventoryChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} fontSize={11} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Legend wrapperStyle={{ fontSize: '12px' }} />
            <Bar dataKey="stock" fill="#3b82f6" name="Current Stock" radius={[4, 4, 0, 0]} />
            <Bar dataKey="threshold" fill="#ef4444" name="Restock Threshold" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h3 className="font-semibold mb-2 text-sm">Recent Events (Agent Activity)</h3>
        <div className="max-h-56 overflow-auto border rounded bg-gray-50">
          {recentEvents.length === 0 ? (
            <div className="px-4 py-8 text-center text-gray-500 text-sm">
              No events yet. Start the simulation to see purchases, restocks, and agent communications.
            </div>
          ) : (
            <div className="divide-y">
              {recentEvents.map((evt, idx) => (
                <div key={idx} className="px-3 py-2 text-xs">
                  {evt.type === 'inventory' && (
                    <>
                      {evt.category === 'purchase' && (
                        <div className="flex items-start gap-2">
                          <span className="text-blue-600 font-bold">📚 PURCHASE:</span>
                          <div className="flex-1">
                            <span className="font-medium">{evt.title || evt.sku}</span>
                            <span className="text-gray-600"> - Stock: {evt.remaining}</span>
                            {(() => {
                              const item = inventory.find(i => i.sku === evt.sku)
                              return item && evt.remaining <= item.threshold ? (
                                <span className="ml-2 text-red-600 font-semibold">⚠️ LOW</span>
                              ) : null
                            })()}
                          </div>
                          <span className="text-gray-400 text-[10px]">Tick {evt.tick}</span>
                        </div>
                      )}
                      {evt.category === 'restock' && (
                        <div className="flex items-start gap-2">
                          <span className="text-emerald-600 font-bold">📦 RESTOCK:</span>
                          <div className="flex-1">
                            <span className="font-medium">{evt.title || evt.sku}</span>
                            <span className="text-gray-600"> +{evt.delta} → {evt.remaining} units</span>
                          </div>
                          <span className="text-gray-400 text-[10px]">Tick {evt.tick}</span>
                        </div>
                      )}
                      {evt.category === 'restock_ordered' && (
                        <div className="flex items-start gap-2">
                          <span className="text-orange-600 font-bold">🚚 ORDER:</span>
                          <div className="flex-1">
                            <span className="font-medium">{evt.title || evt.sku}</span>
                            <span className="text-gray-600"> +{evt.delta} units ordered</span>
                            <span className="ml-2 text-orange-500 font-semibold">
                              ⏳ Arrives in {evt.ticksRemaining} ticks
                            </span>
                          </div>
                          <span className="text-gray-400 text-[10px]">Tick {evt.tick}</span>
                        </div>
                      )}
                      {evt.category === 'stockout' && (
                        <div className="flex items-start gap-2">
                          <span className="text-red-600 font-bold">❌ STOCKOUT:</span>
                          <div className="flex-1">
                            <span className="font-medium">{evt.title || evt.sku}</span>
                            <span className="text-gray-600"> - Out of stock!</span>
                          </div>
                          <span className="text-gray-400 text-[10px]">Tick {evt.tick}</span>
                        </div>
                      )}
                    </>
                  )}
                  {evt.type === 'observation' && (
                    <div className="flex items-start gap-2">
                      <span className="text-purple-600 font-bold">👤 CUSTOMER:</span>
                      <div className="flex-1">
                        <span className="font-medium">{evt.agentId}</span>
                        <span className="text-gray-600"> observed "{evt.obs}"</span>
                      </div>
                      <span className="text-gray-400 text-[10px]">Tick {evt.tick}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Pending Restocks Panel */}
      {pendingRestocks && pendingRestocks.length > 0 && (
        <div>
          <h3 className="font-semibold mb-2 text-sm flex items-center gap-2">
            <span>🚚 Pending Restocks (In Transit)</span>
            <span className="text-xs font-normal text-gray-500">— Delivery countdown</span>
          </h3>
          <div className="border rounded divide-y bg-orange-50">
            {pendingRestocks.map((restock) => (
              <div key={restock.sku} className="px-3 py-2.5 flex items-center gap-3">
                <div className="flex-shrink-0 w-12 h-12 bg-orange-200 rounded-full flex items-center justify-center text-2xl">
                  🚚
                </div>
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{restock.title}</div>
                  <div className="text-xs text-gray-600">
                    +{restock.amount} units ordered at tick {restock.orderedTick}
                  </div>
                </div>
                <div className="flex-shrink-0 text-right">
                  <div className="text-2xl font-bold text-orange-600">
                    {restock.ticksRemaining}
                  </div>
                  <div className="text-[10px] uppercase tracking-wide text-gray-500">
                    ticks left
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 className="font-semibold mb-2 text-sm">Inventory Snapshot</h3>
        <div className="max-h-48 overflow-auto border rounded">
          <table className="w-full text-xs">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left">Title</th>
                <th className="px-3 py-2 text-right">On Hand</th>
                <th className="px-3 py-2 text-right">Threshold</th>
                <th className="px-3 py-2 text-right">Restock</th>
              </tr>
            </thead>
            <tbody>
              {inventory.map((item) => (
                <tr key={item.sku} className="border-t">
                  <td className="px-3 py-2">
                    <div className="font-medium text-gray-900">{item.title}</div>
                    <div className="text-[10px] uppercase tracking-wide text-gray-500">{item.sku}</div>
                  </td>
                  <td className={`px-3 py-2 text-right font-mono ${item.onHand <= item.threshold ? 'text-red-600' : 'text-gray-800'}`}>
                    {item.onHand}
                  </td>
                  <td className="px-3 py-2 text-right text-gray-600">{item.threshold}</td>
                  <td className="px-3 py-2 text-right text-gray-600">+{item.restockAmount}</td>
                </tr>
              ))}
              {inventory.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-3 py-4 text-center text-gray-500">
                    <div className="space-y-1">
                      <div>📚 No inventory loaded yet</div>
                      <div className="text-xs">1. Click "Load Sample Ontology" 2. Click "Configure" 3. Start simulation</div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div>
        <h3 className="font-semibold mb-2 text-sm">Customer States (Inferred)</h3>
        <div className="max-h-60 overflow-auto border rounded">
          <table className="w-full text-xs">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left">Customer</th>
                <th className="px-3 py-2 text-left">State</th>
                <th className="px-3 py-2 text-right">Log Prob</th>
              </tr>
            </thead>
            <tbody>
              {customerStates.map((cs) => (
                <tr key={cs.custId} className="border-t">
                  <td className="px-3 py-2">{cs.custId}</td>
                  <td className="px-3 py-2">
                    <span className={`px-2 py-0.5 rounded text-xs ${
                      cs.inferredState === 'Happy' ? 'bg-green-100 text-green-800' :
                      cs.inferredState === 'Unhappy' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {cs.inferredState}
                    </span>
                  </td>
                  <td className="px-3 py-2 text-right font-mono">{cs.logprob.toFixed(2)}</td>
                </tr>
              ))}
              {customerStates.length === 0 && (
                <tr>
                  <td colSpan={3} className="px-3 py-4 text-center text-gray-500">No inferences yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="space-y-2">
        <h3 className="font-semibold text-sm">Export</h3>
        <button className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm">
          Download Logs (CSV)
        </button>
        <button className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm">
          Download Metrics (JSON)
        </button>
        <button className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded text-sm">
          Download Ontology (TTL)
        </button>
      </div>
    </div>
  )
}
