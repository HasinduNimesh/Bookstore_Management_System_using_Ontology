import { useState, useEffect } from 'react'
import { useAppStore } from '../store/appStore'
import { api } from '../services/api'

export default function OntologyInspector() {
  const { ontologySummary, ontologyLoaded } = useAppStore()
  const [selectedClass, setSelectedClass] = useState<string>('')
  const [instances, setInstances] = useState<any[]>([])
  const [diff, setDiff] = useState<any>(null)

  useEffect(() => {
    const fetchDiff = async () => {
      if (ontologyLoaded) {
        const result = await api.getDiff()
        setDiff(result)
      }
    }
    
    const interval = setInterval(fetchDiff, 2000)
    return () => clearInterval(interval)
  }, [ontologyLoaded])

  const handleClassClick = async (className: string) => {
    setSelectedClass(className)
    const result = await api.getInstances(className)
    setInstances(result.instances || [])
  }

  if (!ontologyLoaded || !ontologySummary) {
    return (
      <div className="p-4">
        <h2 className="text-lg font-bold mb-3">Ontology Inspector</h2>
        <p className="text-gray-500">No ontology loaded</p>
      </div>
    )
  }

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold mb-3">Ontology Inspector</h2>
      
      {/* Summary */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg text-sm">
        <div>Classes: {ontologySummary.classCount}</div>
        <div>Instances: {ontologySummary.instanceCount}</div>
        <div>Triples: {ontologySummary.tripleCount}</div>
      </div>

      {/* Top Classes */}
      <div className="mb-4">
        <h3 className="font-semibold mb-2">Classes</h3>
        <div className="space-y-1">
          {Object.entries(ontologySummary.topClasses).map(([name, count]) => (
            <button
              key={name}
              onClick={() => handleClassClick(name)}
              className={`w-full text-left px-3 py-2 rounded text-sm ${
                selectedClass === name ? 'bg-blue-100' : 'bg-gray-50 hover:bg-gray-100'
              }`}
            >
              {name} ({count as number})
            </button>
          ))}
        </div>
      </div>

      {/* Instances */}
      {selectedClass && (
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Instances of {selectedClass}</h3>
          <div className="space-y-2">
            {instances.map((inst, idx) => (
              <div key={idx} className="p-2 bg-gray-50 rounded text-xs">
                <div className="font-medium">{inst.name}</div>
                {Object.entries(inst.properties).map(([prop, values]: [string, any]) => (
                  <div key={prop} className="text-gray-600 ml-2">
                    {prop}: {Array.isArray(values) ? values.join(', ') : values}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Diff */}
      {diff && (
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Diff Since Start</h3>
          <div className="text-xs">
            <div className="text-green-600">Added: {diff.added?.length || 0}</div>
            <div className="text-red-600">Removed: {diff.removed?.length || 0}</div>
            {diff.added && diff.added.slice(0, 5).map((triple: any, idx: number) => (
              <div key={idx} className="text-green-700 ml-2 truncate">
                + {triple.join(' ')}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
