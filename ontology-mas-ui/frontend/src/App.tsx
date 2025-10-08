import { useEffect, useRef, useState } from 'react'
import { useAppStore } from './store/appStore'
import TopBar from './components/TopBar'
import OntologyInspector from './components/OntologyInspector'
import SimulationCanvas from './components/SimulationCanvas'
import HMMDashboard from './components/HMMDashboard'
import MessageLog from './components/MessageLog'
import SimulationSummary from './components/SimulationSummary'
import './index.css'

function App() {
  const { setWs, setWsConnected, updateTick, wsConnected, simulationRunning } = useAppStore()
  const reconnectTimeoutRef = useRef<number | null>(null)
  const backoffRef = useRef(1000) // start with 1s, cap at 10s
  const [showSummary, setShowSummary] = useState(false)
  const prevRunningRef = useRef(simulationRunning)

  useEffect(() => {
    // Build WS URL using current host so Vite proxy can route /ws -> backend in dev
    const buildWsUrl = () => {
      const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
      // Use same host:port as the frontend, then rely on Vite proxy for /ws
      return `${proto}://${window.location.host}/ws`
    }

    const connectWs = () => {
      const url = buildWsUrl()
      const ws = new WebSocket(url)
      
      ws.onopen = () => {
        // eslint-disable-next-line no-console
        console.log('WebSocket connected')
        setWsConnected(true)
        backoffRef.current = 1000 // reset backoff on success
      }
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          updateTick(data)
        } catch (e) {
          // eslint-disable-next-line no-console
          console.debug('WS message parse skipped (non-JSON?)')
        }
      }
      
      ws.onclose = () => {
        // eslint-disable-next-line no-console
        console.log('WebSocket disconnected')
        setWsConnected(false)
        // Reconnect with exponential backoff (max 10s)
        const delay = Math.min(backoffRef.current, 10000)
        if (reconnectTimeoutRef.current) window.clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = window.setTimeout(connectWs, delay)
        backoffRef.current = Math.min(delay * 2, 10000)
      }
      
      ws.onerror = () => {
        // Quiet error logging to avoid noisy console during backend restarts/HMR
        // eslint-disable-next-line no-console
        console.debug('WebSocket transient error, will retry')
      }

      // Heartbeat: keep connection alive
      const heartbeat = window.setInterval(() => {
        try {
          ws.readyState === WebSocket.OPEN && ws.send('ping')
        } catch {}
      }, 15000)
      
      setWs(ws)
      // Clean heartbeat when socket closes
      ws.addEventListener('close', () => window.clearInterval(heartbeat))
    }
    
    connectWs()
    
    return () => {
      const ws = useAppStore.getState().ws
      if (ws) {
        ws.close()
      }
      if (reconnectTimeoutRef.current) window.clearTimeout(reconnectTimeoutRef.current)
    }
  }, [])

  // Detect when simulation stops to potentially show summary
  useEffect(() => {
    if (prevRunningRef.current && !simulationRunning) {
      // Simulation just stopped
      // Auto-show summary after a short delay
      setTimeout(() => {
        setShowSummary(true)
      }, 1000)
    }
    prevRunningRef.current = simulationRunning
  }, [simulationRunning])

  // Handle close summary event
  useEffect(() => {
    const handleCloseSummary = () => setShowSummary(false)
    window.addEventListener('closeSummary', handleCloseSummary)
    return () => window.removeEventListener('closeSummary', handleCloseSummary)
  }, [])

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <TopBar />
      
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left: Ontology Inspector */}
        <div className="w-full lg:w-1/4 h-1/4 lg:h-full border-b lg:border-b-0 lg:border-r border-gray-200 overflow-y-auto bg-white">
          <OntologyInspector />
        </div>
        
        {/* Center: Simulation Canvas & Message Log */}
        <div className="flex-1 flex flex-col overflow-hidden min-h-0">
          <div className="flex-1 min-h-0">
            <SimulationCanvas />
          </div>
          <div className="h-48 lg:h-64 border-t border-gray-200 overflow-y-auto p-2 lg:p-4 bg-gray-50 flex-shrink-0">
            <MessageLog />
          </div>
        </div>
        
        {/* Right: HMM & KPIs */}
        <div className="w-full lg:w-1/4 h-1/4 lg:h-full border-t lg:border-t-0 lg:border-l border-gray-200 overflow-y-auto bg-white">
          <HMMDashboard />
        </div>
      </div>
      
      {/* View Summary Button (always available) */}
      <div className="fixed bottom-4 left-4">
        <button
          onClick={() => setShowSummary(true)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 shadow-lg font-semibold flex items-center gap-2"
        >
          <span>📊</span> View Analysis
        </button>
      </div>

      {/* Connection status */}
      <div className="fixed bottom-4 right-4">
        <div className={`px-3 py-1 rounded-full text-sm ${
          wsConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {wsConnected ? '● Connected' : '○ Disconnected'}
        </div>
      </div>

      {/* Simulation Summary Modal */}
      {showSummary && (
        <SimulationSummary />
      )}
    </div>
  )
}

export default App
