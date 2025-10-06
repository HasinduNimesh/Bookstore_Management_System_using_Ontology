# Ontology-Driven Multi-Agent System Simulator

A full-stack web application for simulating multi-agent systems with ontology management, Hidden Markov Model (HMM) inference, and real-time visualization.

## Features

- **Ontology Management**: Load, inspect, and update RDF/OWL ontologies with real-time diff tracking
- **Multi-Agent Simulation**: Mesa-based grid simulation with customer and service agents
- **HMM Inference**: Viterbi algorithm for inferring hidden states from observations
- **Real-Time Visualization**: Live grid updates and event streaming via WebSocket
- **Interactive Dashboard**: Charts, metrics, customer state inspection, and inventory KPIs pulled from the ontology
- **Export Capabilities**: Download logs (CSV), metrics (JSON), and ontology snapshots (TTL)

## Architecture

### Backend
- **FastAPI**: REST API + WebSocket server
- **Mesa 2.3.3**: Multi-agent simulation framework
- **RDFlib & Owlready2**: Ontology loading and SPARQL queries
- **hmmlearn**: HMM inference (Viterbi algorithm)
- **EventBus**: Pub/sub for WebSocket broadcasting

### Frontend
- **React 18 + Vite**: Fast SPA with hot module replacement
- **TypeScript**: Type-safe component development
- **Tailwind CSS**: Utility-first styling
- **Zustand**: Global state management
- **Recharts**: Data visualization

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Frontend Setup

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Running the Application

You'll need **two terminal windows**.

### Terminal 1: Backend Server

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- WebSocket: `ws://localhost:8000/ws`

### Terminal 2: Frontend Dev Server

```powershell
cd frontend
npm run dev
```

The frontend will start at `http://localhost:5173`

Open your browser and navigate to `http://localhost:5173`

## Usage

### 1. Load Ontology
- Click **"Load Ontology"** in the top bar
- Choose **"Upload File"** (RDF/OWL/TTL) or **"Use Sample"** — the bundled sample `data/bookstore_sample.ttl` includes books & inventory quantities
- The ontology summary appears in the left panel

### 2. Configure Simulation
- Click **"Configure"** to set:
  - Number of simulation ticks
  - Random seed
  - Number of customers
  - Number of service agents
  - HMM parameters (states, observations, transition matrix, emission matrix)

### 3. Run Simulation
- Click **"Start Simulation"** (button stays disabled until the sample ontology is loaded and configuration is applied)
- Watch the grid visualization update in real-time
- Observe events streaming in the center console
- Monitor HMM inference results in the right panel

### 4. Inspect Results
- **Left Panel**: View ontology classes, instances, and real-time diffs
- **Center Panel**: Grid visualization and event log
- **Right Panel**: Observation charts, inferred customer states, and inventory KPIs

### 5. Export Data
- **Download Logs (CSV)**: Event stream with timestamps
- **Download Metrics (JSON)**: Aggregated simulation metrics
- **Download Ontology (TTL)**: Updated ontology with simulation results

## API Endpoints

### Ontology Management
- `POST /ontology/load`: Load RDF/OWL ontology (file or text)
- `GET /ontology/summary`: Get class/instance/triple counts
- `GET /ontology/instances?class_name=Customer`: List instances of a class
- `POST /ontology/update`: Apply RDF triples to ontology
- `GET /ontology/diff`: Get added/removed triples since last check

### Simulation Control
- `POST /simulation/config`: Set simulation parameters
- `POST /simulation/start`: Start simulation (runs async)
- `POST /simulation/stop`: Stop simulation
- `POST /simulation/step`: Run a single step
- `GET /simulation/metrics`: Get current metrics
- `GET /simulation/status`: Get simulation state

### WebSocket
- `WS /ws`: Real-time event streaming (connect from frontend)

## Project Structure

```
ontology-mas-ui/
├── backend/
│   ├── main.py                  # FastAPI app + routes
│   ├── requirements.txt         # Python dependencies
│   ├── models/
│   │   ├── ontology.py         # GraphManager (RDFlib)
│   │   ├── hmm.py              # HMMInference (Viterbi)
│   │   └── mesa_model.py       # SimulationModel + Agents
│   ├── services/
│   │   └── bus.py              # EventBus (pub/sub)
│   └── data/
│       └── sample_ontology.ttl # Demo RDF ontology
├── frontend/
│   ├── src/
│   │   ├── App.tsx             # Main layout
│   │   ├── main.tsx            # Entry point
│   │   ├── store/
│   │   │   └── appStore.ts     # Zustand state
│   │   ├── services/
│   │   │   └── api.ts          # API client
│   │   └── components/
│   │       ├── TopBar.tsx      # Controls + config
│   │       ├── OntologyInspector.tsx
│   │       ├── SimulationCanvas.tsx
│   │       └── HMMDashboard.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
└── index.html
```

## Technologies

- **Python**: FastAPI, Mesa, RDFlib, Owlready2, hmmlearn, NumPy
- **JavaScript**: React, Vite, TypeScript, Zustand, Tailwind, Recharts
- **Protocols**: REST, WebSocket, SPARQL
- **Formats**: RDF, OWL, TTL, JSON, CSV

## Development

### Backend
```powershell
# Run with auto-reload
uvicorn main:app --reload

# Run tests (if available)
pytest tests/
```

### Frontend
```powershell
# Dev server with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Docker (Optional)

```yaml
# docker-compose.yml (to be added)
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
```

## Troubleshooting

### Backend Issues
- **ModuleNotFoundError**: Ensure virtual environment is activated and dependencies installed
- **Port 8000 in use**: Change port in uvicorn command or kill existing process
- **Java not found**: Pellet reasoner is disabled by default; uses Python inference

### Frontend Issues
- **Module not found**: Run `npm install` in frontend directory
- **WebSocket connection failed**: Ensure backend is running on port 8000
- **CORS errors**: Check `CORS(app)` configuration in `backend/main.py`

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Authors

- Initial development: BMS Project Team
- Extended for ontology-driven MAS with HMM inference

## Acknowledgments

- Mesa framework for agent-based modeling
- RDFlib and Owlready2 for ontology management
- hmmlearn for HMM implementation
- React and Vite teams for excellent developer experience
