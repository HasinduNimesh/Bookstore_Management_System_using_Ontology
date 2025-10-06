const API_BASE = '/api'

export const api = {
  // Ontology
  loadOntology: async (data: { path?: string; ttl?: string; owl?: string }) => {
    const response = await fetch(`${API_BASE}/ontology/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    return response.json()
  },
  
  getOntologySummary: async () => {
    const response = await fetch(`${API_BASE}/ontology/summary`)
    return response.json()
  },
  
  getInstances: async (className: string) => {
    // Backend expects 'class_name' query param
    const response = await fetch(`${API_BASE}/ontology/instances?class_name=${encodeURIComponent(className)}`)
    return response.json()
  },
  
  getDiff: async () => {
    const response = await fetch(`${API_BASE}/ontology/diff`)
    return response.json()
  },
  
  // Simulation
  setConfig: async (config: any) => {
    const response = await fetch(`${API_BASE}/simulation/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })
    return response.json()
  },
  
  startSimulation: async () => {
    const response = await fetch(`${API_BASE}/simulation/start`, {
      method: 'POST'
    })
    return response.json()
  },
  
  stopSimulation: async () => {
    const response = await fetch(`${API_BASE}/simulation/stop`, {
      method: 'POST'
    })
    return response.json()
  },
  
  stepSimulation: async () => {
    const response = await fetch(`${API_BASE}/simulation/step`, {
      method: 'POST'
    })
    return response.json()
  },
  
  getMetrics: async () => {
    const response = await fetch(`${API_BASE}/simulation/metrics`)
    return response.json()
  },
  
  getStatus: async () => {
    const response = await fetch(`${API_BASE}/simulation/status`)
    return response.json()
  }
}
