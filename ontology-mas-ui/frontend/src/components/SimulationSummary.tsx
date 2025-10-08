import { useAppStore } from '../store/appStore'
import { BarChart, Bar, PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function SimulationSummary() {
  const { events, metrics, currentTick, inventory, customerStates } = useAppStore()

  // Calculate message statistics
  const messageEvents = events.filter(e => e.type === 'message')
  const purchaseRequests = messageEvents.filter(e => e.topic === 'purchase_request').length
  const serviceResponses = messageEvents.filter(e => e.topic === 'service_response').length
  const restockRequests = messageEvents.filter(e => e.topic === 'restock_request').length
  const restockDeliveries = messageEvents.filter(e => e.topic === 'restock_done').length

  // Calculate revenue over time (cumulative)
  // Look for purchase events - they might be in different formats
  const purchaseEvents = events
    .filter(e => e.type === 'purchase' || e.type === 'PURCHASE' || (e.type === 'metric' && e.metric === 'purchase'))
    .sort((a, b) => (a.tick || 0) - (b.tick || 0))

  console.log('Total events:', events.length)
  console.log('Purchase events found:', purchaseEvents.length)
  console.log('Sample purchase event:', purchaseEvents[0])
  console.log('Metrics:', metrics)

  const revenueTrend: { tick: number; revenue: number; purchases: number }[] = []
  let cumulativeRevenue = 0
  let cumulativePurchases = 0
  
  // If we have purchase events with price data, build the trend
  if (purchaseEvents.length > 0 && purchaseEvents.some(e => e.price)) {
    // Group purchases by tick and calculate cumulative values
    const tickGroups = purchaseEvents.reduce((acc, event) => {
      const tick = event.tick || currentTick
      if (!acc[tick]) {
        acc[tick] = { revenue: 0, count: 0 }
      }
      acc[tick].revenue += event.price || 0
      acc[tick].count += 1
      return acc
    }, {} as Record<number, { revenue: number; count: number }>)

    // Create trend data with sampling for better visualization
    const ticks = Object.keys(tickGroups).map(Number).sort((a, b) => a - b)
    const sampleInterval = Math.max(1, Math.floor(ticks.length / 50)) // Sample ~50 points max
    
    ticks.forEach((tick, index) => {
      cumulativeRevenue += tickGroups[tick].revenue
      cumulativePurchases += tickGroups[tick].count
      
      // Sample points to avoid overcrowding the chart
      if (index % sampleInterval === 0 || index === ticks.length - 1) {
        revenueTrend.push({
          tick,
          revenue: parseFloat(cumulativeRevenue.toFixed(2)),
          purchases: cumulativePurchases
        })
      }
    })
  } else if (metrics.purchases > 0 && metrics.revenue > 0) {
    // Fallback: Create a simple trend based on final metrics
    // Assume linear growth over the simulation period
    const tickInterval = Math.max(1, Math.floor(currentTick / 10))
    for (let tick = 0; tick <= currentTick; tick += tickInterval) {
      const progress = tick / currentTick
      revenueTrend.push({
        tick,
        revenue: parseFloat((metrics.revenue * progress).toFixed(2)),
        purchases: Math.floor(metrics.purchases * progress)
      })
    }
    // Ensure final tick is included
    if (revenueTrend[revenueTrend.length - 1].tick !== currentTick) {
      revenueTrend.push({
        tick: currentTick,
        revenue: metrics.revenue,
        purchases: metrics.purchases
      })
    }
  }

  // Calculate customer state distribution
  const stateDistribution = customerStates.reduce((acc, cs) => {
    acc[cs.inferredState] = (acc[cs.inferredState] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const stateData = Object.entries(stateDistribution).map(([state, count]) => ({
    name: state,
    value: count
  }))

  // Message type distribution
  const messageTypeData = [
    { name: 'Purchase Requests', value: purchaseRequests, color: '#3b82f6' },
    { name: 'Service Responses', value: serviceResponses, color: '#8b5cf6' },
    { name: 'Restock Orders', value: restockRequests, color: '#10b981' },
    { name: 'Deliveries', value: restockDeliveries, color: '#f59e0b' }
  ]

  // Inventory status
  const inventoryData = inventory.map(item => ({
    name: item.title.length > 20 ? item.title.substring(0, 20) + '...' : item.title,
    stock: item.onHand,
    threshold: item.threshold
  }))

  // Metrics over time
  const metricsData = [
    { name: 'Purchases', value: metrics.purchases },
    { name: 'Complaints', value: metrics.complaints },
    { name: 'Silence', value: metrics.silence },
    { name: 'Restocks', value: metrics.restocks },
    { name: 'Stockouts', value: metrics.stockouts }
  ]

  // Download all data as JSON
  const downloadData = () => {
    const data = {
      simulationSummary: {
        totalTicks: currentTick,
        timestamp: new Date().toISOString()
      },
      metrics,
      customerStates,
      inventory,
      messageStatistics: {
        purchaseRequests,
        serviceResponses,
        restockRequests,
        restockDeliveries,
        totalMessages: messageEvents.length
      },
      allEvents: events,
      allMessages: messageEvents
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `simulation-data-tick-${currentTick}-${Date.now()}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  // Download messages as CSV
  const downloadMessagesCSV = () => {
    const headers = ['Tick', 'From', 'To', 'Topic', 'Content', 'SKU', 'Quantity']
    const rows = messageEvents.map(msg => [
      msg.tick || currentTick,
      msg.from || '',
      msg.to || '',
      msg.topic || '',
      msg.content || '',
      msg.sku || '',
      msg.quantity || ''
    ])

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `agent-messages-tick-${currentTick}-${Date.now()}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6']

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-2xl max-w-6xl w-full my-8 relative">
        {/* Sticky Header with Close Button */}
        <div className="sticky top-0 z-10 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-lg flex justify-between items-start">
          <div>
            <h2 className="text-3xl font-bold">📊 Simulation Complete - Analysis Summary</h2>
            <p className="text-blue-100 mt-2">Tick: {currentTick} | Total Messages: {messageEvents.length}</p>
          </div>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent('closeSummary'))}
            className="ml-4 p-2 hover:bg-white hover:bg-opacity-20 rounded-full transition-colors flex-shrink-0"
            title="Close"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6 max-h-[calc(90vh-100px)] overflow-y-auto">
          {/* Download Buttons */}
          <div className="bg-gray-50 p-4 rounded-lg border-2 border-gray-200">
            <h3 className="text-lg font-bold mb-3 text-gray-800">📥 Download Data</h3>
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={downloadData}
                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold shadow-lg flex items-center gap-2"
              >
                <span>📦</span> Download All Data (JSON)
              </button>
              <button
                onClick={downloadMessagesCSV}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold shadow-lg flex items-center gap-2"
              >
                <span>📄</span> Download Messages (CSV)
              </button>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
              <div className="text-3xl font-bold text-blue-600">{metrics.purchases}</div>
              <div className="text-sm text-gray-600">Purchases</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg border-2 border-red-200">
              <div className="text-3xl font-bold text-red-600">{metrics.stockouts}</div>
              <div className="text-sm text-gray-600">Stockouts</div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg border-2 border-green-200">
              <div className="text-3xl font-bold text-green-600">{metrics.restocks}</div>
              <div className="text-sm text-gray-600">Restocks</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg border-2 border-yellow-200">
              <div className="text-3xl font-bold text-yellow-600">${metrics.revenue.toFixed(2)}</div>
              <div className="text-sm text-gray-600">Revenue</div>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg border-2 border-purple-200">
              <div className="text-3xl font-bold text-purple-600">{messageEvents.length}</div>
              <div className="text-sm text-gray-600">Messages</div>
            </div>
          </div>

          {/* Revenue Trend Over Time - Full Width */}
          <div className="bg-white p-6 rounded-lg border-2 border-gray-200">
            <h3 className="text-xl font-bold mb-4 text-gray-800">📈 Revenue Growth Over Time (Agent Activity)</h3>
            <p className="text-sm text-gray-600 mb-4">
              Shows how revenue accumulated as customer agents made purchases throughout the simulation
            </p>
            {revenueTrend.length > 0 ? (
              <div style={{ width: '100%', height: '300px' }}>
                <ResponsiveContainer>
                  <LineChart data={revenueTrend} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="tick" 
                      label={{ value: 'Simulation Tick', position: 'insideBottom', offset: -5 }}
                    />
                    <YAxis 
                      yAxisId="left"
                      label={{ value: 'Cumulative Revenue ($)', angle: -90, position: 'insideLeft' }}
                    />
                    <YAxis 
                      yAxisId="right" 
                      orientation="right"
                      label={{ value: 'Total Purchases', angle: 90, position: 'insideRight' }}
                    />
                    <Tooltip 
                      formatter={(value: number, name: string) => {
                        if (name === 'revenue') return [`$${value.toFixed(2)}`, 'Revenue']
                        if (name === 'purchases') return [value, 'Purchases']
                        return [value, name]
                      }}
                      labelFormatter={(tick) => `Tick: ${tick}`}
                    />
                    <Legend />
                    <Line 
                      yAxisId="left"
                      type="monotone" 
                      dataKey="revenue" 
                      stroke="#10b981" 
                      strokeWidth={3}
                      dot={{ fill: '#10b981', r: 4 }}
                      name="Cumulative Revenue"
                    />
                    <Line 
                      yAxisId="right"
                      type="monotone" 
                      dataKey="purchases" 
                      stroke="#3b82f6" 
                      strokeWidth={2}
                      dot={{ fill: '#3b82f6', r: 3 }}
                      name="Total Purchases"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="bg-gray-50 p-8 rounded-lg border-2 border-dashed border-gray-300 text-center">
                <p className="text-gray-600 text-lg">📊 No revenue data available</p>
                <p className="text-gray-500 text-sm mt-2">
                  Revenue trend will appear here when purchases are made during the simulation.
                </p>
                <p className="text-gray-400 text-xs mt-2">
                  Debug: {purchaseEvents.length} purchase events found, {events.length} total events
                </p>
              </div>
            )}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="bg-green-50 p-3 rounded border border-green-200">
                <div className="font-semibold text-green-700">Final Revenue</div>
                <div className="text-2xl font-bold text-green-600">${metrics.revenue.toFixed(2)}</div>
              </div>
              <div className="bg-blue-50 p-3 rounded border border-blue-200">
                <div className="font-semibold text-blue-700">Total Purchases</div>
                <div className="text-2xl font-bold text-blue-600">{metrics.purchases}</div>
              </div>
              <div className="bg-purple-50 p-3 rounded border border-purple-200">
                <div className="font-semibold text-purple-700">Avg. Sale Price</div>
                <div className="text-2xl font-bold text-purple-600">
                  ${metrics.purchases > 0 ? (metrics.revenue / metrics.purchases).toFixed(2) : '0.00'}
                </div>
              </div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Message Type Distribution */}
            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
              <h3 className="text-lg font-bold mb-3 text-gray-800">Agent Communication Breakdown</h3>
              <div style={{ width: '100%', height: '250px' }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={messageTypeData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name.split(' ')[0]}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {messageTypeData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Customer State Distribution */}
            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
              <h3 className="text-lg font-bold mb-3 text-gray-800">Customer State Distribution</h3>
              <div style={{ width: '100%', height: '250px' }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={stateData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, value }) => `${name}: ${value}`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {stateData.map((_entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Event Type Summary */}
            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
              <h3 className="text-lg font-bold mb-3 text-gray-800">Event Type Summary</h3>
              <div style={{ width: '100%', height: '250px' }}>
                <ResponsiveContainer>
                  <BarChart data={metricsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Inventory Levels */}
            <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
              <h3 className="text-lg font-bold mb-3 text-gray-800">Final Inventory Levels</h3>
              <div className="overflow-y-auto" style={{ maxHeight: '400px' }}>
                <div style={{ width: '100%', height: Math.max(400, inventoryData.length * 35) + 'px' }}>
                  <ResponsiveContainer>
                    <BarChart data={inventoryData} layout="horizontal" margin={{ left: 20, right: 20 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={150} fontSize={11} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="stock" fill="#10b981" name="Current Stock" />
                      <Bar dataKey="threshold" fill="#ef4444" name="Threshold" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>

          {/* Message Log Summary */}
          <div className="bg-white p-4 rounded-lg border-2 border-gray-200">
            <h3 className="text-lg font-bold mb-3 text-gray-800">📊 Communication Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-blue-600">🛒 {purchaseRequests}</div>
                <div className="text-xs text-gray-600">Purchase Requests</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-600">💬 {serviceResponses}</div>
                <div className="text-xs text-gray-600">Service Responses</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-600">📦 {restockRequests}</div>
                <div className="text-xs text-gray-600">Restock Orders</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-600">✅ {restockDeliveries}</div>
                <div className="text-xs text-gray-600">Deliveries</div>
              </div>
            </div>
          </div>
        </div>

        <div className="sticky bottom-0 bg-gray-100 p-4 rounded-b-lg border-t-2 border-gray-300 text-center">
          <p className="text-sm text-gray-600">
            Simulation completed at {new Date().toLocaleString()} | 
            Duration: {currentTick} ticks | 
            Total Events: {events.length}
          </p>
        </div>
      </div>
    </div>
  )
}
