import { create } from 'zustand'

export interface SimulationEvent {
  type: string
  agentId?: string
  obs?: string
  inferredState?: string
  logprob?: number
  [key: string]: any
}

export interface OccupiedPosition {
  x: number
  y: number
  agentId: string
  agentType: 'customer' | 'service'
}

export interface PendingRestock {
  sku: string
  title: string
  amount: number
  deliveryTick: number
  orderedTick: number
  ticksRemaining: number
}

export interface GridState {
  width: number
  height: number
  occupied: OccupiedPosition[]
  pendingRestocks?: PendingRestock[]
}

export interface CustomerState {
  custId: string
  inferredState: string
  logprob: number
  observationCount: number
}

export interface InventoryItem {
  sku: string
  title: string
  onHand: number
  threshold: number
  restockAmount: number
  price: number
}

export interface TickData {
  tick: number
  events: SimulationEvent[]
  grid: GridState
  metrics: {
    purchases: number
    complaints: number
    silence: number
    restocks: number
    stockouts: number
    revenue: number
  }
  customerStates?: CustomerState[]
  inventory?: InventoryItem[]
}

export interface OntologySummary {
  namespaces: Record<string, string>
  classCount: number
  instanceCount: number
  objectProperties: number
  dataProperties: number
  tripleCount: number
  topClasses: Record<string, number>
}

interface AppState {
  // WebSocket
  ws: WebSocket | null
  wsConnected: boolean
  
  // Simulation
  simulationRunning: boolean
  currentTick: number
  events: SimulationEvent[]
  gridState: GridState | null
  metrics: TickData['metrics']
  customerStates: CustomerState[]
  
  // Ontology
  ontologyLoaded: boolean
  ontologySummary: OntologySummary | null
  
  // Config
  config: any
  inventory: InventoryItem[]
  pendingRestocks: PendingRestock[]
  
  // Actions
  setWs: (ws: WebSocket | null) => void
  setWsConnected: (connected: boolean) => void
  setSimulationRunning: (running: boolean) => void
  updateTick: (data: TickData) => void
  setOntologyLoaded: (loaded: boolean) => void
  setOntologySummary: (summary: OntologySummary) => void
  setConfig: (config: any, inventory?: InventoryItem[]) => void
}

export const useAppStore = create<AppState>((set) => ({
  // Initial state
  ws: null,
  wsConnected: false,
  simulationRunning: false,
  currentTick: 0,
  events: [],
  gridState: null,
  metrics: {
    purchases: 0,
    complaints: 0,
    silence: 0,
    restocks: 0,
    stockouts: 0,
    revenue: 0
  },
  customerStates: [],
  ontologyLoaded: false,
  ontologySummary: null,
  config: null,
  inventory: [],
  pendingRestocks: [],
  
  // Actions
  setWs: (ws) => set({ ws }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  setSimulationRunning: (running) => set({ simulationRunning: running }),
  updateTick: (data) => set((state) => ({
    currentTick: data.tick,
    // Keep ALL events (no limit - we need them for end-of-simulation download)
    events: [...state.events, ...data.events],
    gridState: data.grid,
    metrics: { ...state.metrics, ...data.metrics },
    customerStates: data.customerStates || [],
    inventory: data.inventory || state.inventory,
    pendingRestocks: data.grid?.pendingRestocks || []
  })),
  setOntologyLoaded: (loaded) => set({ ontologyLoaded: loaded }),
  setOntologySummary: (summary) => set({ ontologySummary: summary }),
  setConfig: (config, inventory) => set({ config, inventory: inventory || [] })
}))
