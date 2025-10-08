import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { useAppStore } from '../store/appStore'
import { api } from '../services/api'

type ConfigFormValues = {
  ticks: number
  seed: number
  numCustomers: number
  numServiceAgents: number
}

export default function TopBar() {
  const { simulationRunning, ontologyLoaded, config, setSimulationRunning, setOntologyLoaded, setOntologySummary, setConfig } = useAppStore()
  const [showConfig, setShowConfig] = useState(false)
  const { register, handleSubmit, reset } = useForm<ConfigFormValues>({
    defaultValues: {
      ticks: 100,
      seed: 42,
      numCustomers: 20,
      numServiceAgents: 2
    }
  })

  // Auto-load bookstore ontology on mount
  useEffect(() => {
    const loadBookstoreOntology = async () => {
      if (!ontologyLoaded) {
        try {
          const result = await api.loadOntology({ path: 'data/bookstore_sample.ttl' })
          setOntologyLoaded(true)
          setOntologySummary(result.data)
          console.log('Bookstore ontology loaded automatically')
        } catch (e) {
          console.error('Failed to auto-load bookstore ontology:', e)
        }
      }
    }
    loadBookstoreOntology()
  }, [])

  const handleStartStop = async () => {
    if (simulationRunning) {
      await api.stopSimulation()
      setSimulationRunning(false)
    } else {
      if (!ontologyLoaded) {
        alert('Load an ontology before starting the simulation so we have book data to work with.')
        return
      }
      if (!config) {
        alert('Apply a configuration first, then start the simulation.')
        return
      }
      await api.startSimulation()
      setSimulationRunning(true)
    }
  }

  const onSubmitConfig = async (data: ConfigFormValues) => {
    const config = {
      ticks: Number(data.ticks),
      seed: Number(data.seed),
      numCustomers: Number(data.numCustomers),
      numServiceAgents: Number(data.numServiceAgents),
      gridWidth: 10,
      gridHeight: 10,
      hmm: {
        states: ['Happy', 'Neutral', 'Unhappy'],
        observations: ['Purchase', 'Complaint', 'Silence'],
        start: [0.5, 0.3, 0.2],
        transition: [
          [0.6, 0.3, 0.1],
          [0.2, 0.6, 0.2],
          [0.2, 0.3, 0.5]
        ],
        emission: [
          [0.7, 0.1, 0.2],
          [0.2, 0.6, 0.2],
          [0.1, 0.6, 0.3]
        ]
      }
    }

    try {
      const response = await api.setConfig(config)
      // Backend returns { status, config } where config includes inventory array
      const backendConfig = response.config || config
      const inventory = backendConfig.inventory || []
      setConfig(backendConfig, inventory)
      setShowConfig(false)
      reset({
        ticks: config.ticks,
        seed: config.seed,
        numCustomers: config.numCustomers,
        numServiceAgents: config.numServiceAgents
      })
      alert(`Configuration set! Loaded ${inventory.length} books from ontology.`)
    } catch (e) {
      alert('Failed to set configuration')
    }
  }

  return (
    <div className="bg-white border-b border-gray-200 px-2 lg:px-6 py-2 lg:py-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <h1 className="text-lg lg:text-2xl font-bold text-gray-900">Ontology-Driven MAS Simulator</h1>
        
        <div className="flex gap-2">
          <button
            onClick={() => setShowConfig(!showConfig)}
            className="px-3 lg:px-4 py-1 lg:py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 text-sm lg:text-base"
          >
            Configure
          </button>
          
          <button
            onClick={handleStartStop}
            className={`px-3 lg:px-4 py-1 lg:py-2 rounded-lg text-sm lg:text-base ${
              simulationRunning 
                ? 'bg-red-600 hover:bg-red-700' 
                : (ontologyLoaded && config ? 'bg-green-600 hover:bg-green-700' : 'bg-green-300 cursor-not-allowed')
            } text-white`}
            disabled={!simulationRunning && (!ontologyLoaded || !config)}
          >
            {simulationRunning ? 'Stop' : 'Start'}
          </button>
        </div>
      </div>

      {showConfig && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-gray-800">Simulation Settings</h2>
            <p className="text-sm text-gray-600">Update the run length and agent counts before starting a new simulation.</p>
          </div>
          <form onSubmit={handleSubmit(onSubmitConfig)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <label className="flex flex-col text-sm font-medium text-gray-700">
                Total Ticks
                <input
                  {...register('ticks', { valueAsNumber: true, min: 1 })}
                  type="number"
                  className="mt-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-blue-200"
                  aria-describedby="ticks-helper"
                  min={1}
                />
                <span id="ticks-helper" className="mt-1 text-xs font-normal text-gray-500">How many steps the simulation should run.</span>
              </label>
              <label className="flex flex-col text-sm font-medium text-gray-700">
                Random Seed
                <input
                  {...register('seed', { valueAsNumber: true })}
                  type="number"
                  className="mt-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-blue-200"
                  aria-describedby="seed-helper"
                />
                <span id="seed-helper" className="mt-1 text-xs font-normal text-gray-500">Use the same seed to reproduce a run.</span>
              </label>
              <label className="flex flex-col text-sm font-medium text-gray-700">
                Customer Agents
                <input
                  {...register('numCustomers', { valueAsNumber: true, min: 1 })}
                  type="number"
                  className="mt-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-blue-200"
                  aria-describedby="customers-helper"
                  min={1}
                />
                <span id="customers-helper" className="mt-1 text-xs font-normal text-gray-500">Number of customer agents to spawn.</span>
              </label>
              <label className="flex flex-col text-sm font-medium text-gray-700">
                Service Agents (Restock)
                <input
                  {...register('numServiceAgents', { valueAsNumber: true, min: 1 })}
                  type="number"
                  className="mt-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring focus:ring-blue-200"
                  aria-describedby="service-helper"
                  min={1}
                />
                <span id="service-helper" className="mt-1 text-xs font-normal text-gray-500">Agents that monitor inventory and handle restocking.</span>
              </label>
            </div>
            <div className="flex flex-wrap gap-3 justify-end">
              <button
                type="button"
                onClick={() => reset()}
                className="px-4 py-2 rounded border border-gray-300 text-gray-700 bg-white hover:bg-gray-100"
              >
                Reset to Defaults
              </button>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Apply Settings
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
