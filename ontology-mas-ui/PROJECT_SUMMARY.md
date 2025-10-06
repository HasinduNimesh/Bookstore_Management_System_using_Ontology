# 🎉 Project Complete: Ontology-Driven MAS Simulator

## ✅ What Was Built

A **full-stack web application** for simulating multi-agent systems with:
- **Ontology Management** (RDF/OWL)
- **Multi-Agent Simulation** (Mesa framework)
- **Hidden Markov Model Inference** (Viterbi algorithm)
- **Real-Time Visualization** (React + WebSocket)

---

## 📁 Project Structure

```
ontology-mas-ui/
├── backend/                      # Python FastAPI Backend
│   ├── main.py                  # FastAPI app with REST + WebSocket endpoints
│   ├── requirements.txt         # Python dependencies
│   ├── venv/                    # ✅ Virtual environment (created & configured)
│   ├── models/
│   │   ├── ontology.py         # GraphManager (RDFlib for ontology operations)
│   │   ├── hmm.py              # HMMInference (Viterbi algorithm)
│   │   └── mesa_model.py       # SimulationModel, CustomerAgent, ServiceAgent
│   ├── services/
│   │   └── bus.py              # EventBus for WebSocket pub/sub
│   └── data/
│       └── sample_ontology.ttl # Demo RDF ontology
│
├── frontend/                     # React + TypeScript Frontend
│   ├── src/
│   │   ├── main.tsx            # Entry point
│   │   ├── App.tsx             # Main layout with WebSocket
│   │   ├── index.css           # Tailwind imports
│   │   ├── store/
│   │   │   └── appStore.ts     # Zustand global state management
│   │   ├── services/
│   │   │   └── api.ts          # API client functions
│   │   └── components/
│   │       ├── TopBar.tsx      # Control bar + config modal
│   │       ├── OntologyInspector.tsx  # Left panel: classes/instances/diff
│   │       ├── SimulationCanvas.tsx   # Center: grid + event console
│   │       └── HMMDashboard.tsx       # Right panel: charts + customer states
│   ├── package.json            # ✅ Dependencies installed
│   ├── node_modules/           # ✅ Installed with --legacy-peer-deps
│   ├── vite.config.ts          # Vite config with proxy
│   ├── tailwind.config.js      # Tailwind CSS config
│   ├── postcss.config.js       # PostCSS config
│   └── tsconfig.json           # TypeScript config
│
├── index.html                   # HTML entry point
├── docker-compose.yml           # Docker orchestration
├── README.md                    # Full documentation
├── START_HERE.md               # Quick start guide
└── report-notes.md             # Technical report (MAS + HMM + Ontology)
```

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.109.0 | REST API + WebSocket server |
| Uvicorn | 0.27.0 | ASGI server with hot reload |
| RDFlib | 7.0.0 | RDF/OWL ontology parsing & SPARQL |
| Owlready2 | 0.46 | Python ontology library |
| Mesa | 2.3.3 | Multi-agent simulation framework |
| hmmlearn | 0.3.2 | HMM inference (Viterbi) |
| NumPy | 1.26.3 | Numerical operations |
| scikit-learn | 1.4.0 | ML utilities |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.2.0 | UI framework |
| TypeScript | 5.2.2 | Type-safe JavaScript |
| Vite | 5.0.8 | Build tool with HMR |
| Tailwind CSS | 3.4.0 | Utility-first styling |
| Zustand | 4.5.0 | State management |
| Recharts | 2.10.3 | Data visualization |
| react-hook-form | 7.49.3 | Form management |

---

## 🎯 Key Features

### 1. Ontology Management
- **Load**: Upload RDF/OWL/TTL files or use sample ontology
- **Inspect**: View classes, instances, properties in hierarchical tree
- **Query**: SPARQL queries to retrieve specific instances
- **Update**: Apply new RDF triples during simulation
- **Diff**: Real-time tracking of added/removed triples
- **Export**: Download updated ontology in TTL format

### 2. Multi-Agent Simulation
- **CustomerAgent**: Autonomous agents with hidden emotional states
  - Move randomly on 10×10 grid
  - Emit observations (Purchase, Complaint, Silence)
  - State transitions follow Markov chain
- **ServiceAgent**: Intelligent agents that infer customer states
  - Use HMM inference (Viterbi algorithm)
  - Compute log-probability confidence scores
  - Provide insights for service optimization

### 3. HMM Inference
- **Viterbi Algorithm**: Find most likely state sequence
- **Configurable Parameters**:
  - States (e.g., Happy, Neutral, Unhappy)
  - Observations (e.g., Purchase, Complaint, Silence)
  - Transition matrix (state-to-state probabilities)
  - Emission matrix (state-to-observation probabilities)
  - Initial distribution
- **Output**: Inferred states with log-probability scores

### 4. Real-Time Visualization
- **Grid Canvas**: 10×10 grid showing agent positions
- **Event Stream**: Live console with color-coded event badges
- **Observation Charts**: Bar chart of observation counts
- **State Table**: Customer emotional states with confidence scores
- **Ontology Diff**: Added/removed triples in real-time

### 5. WebSocket Streaming
- **Bidirectional Communication**: Backend ↔ Frontend
- **Event Types**:
  - `tick`: Simulation step completed
  - `observation`: Agent emitted observation
  - `inference`: HMM inference completed
  - `metrics`: Aggregate statistics updated
- **Connection Status**: Visual indicator in UI

### 6. Export Capabilities
- **Logs (CSV)**: Event stream with timestamps
- **Metrics (JSON)**: Simulation statistics + HMM results
- **Ontology (TTL)**: Updated RDF ontology

---

## 🚀 Quick Start

### 1. Start Backend (Terminal 1)
```powershell
cd f:\BMS_Project_Ready_To_Run\ontology-mas-ui\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend (Terminal 2)
```powershell
cd f:\BMS_Project_Ready_To_Run\ontology-mas-ui\frontend
npm run dev
```

### 3. Open Browser
Navigate to: **http://localhost:5173**

---

## 📊 API Endpoints

### Ontology
- `POST /ontology/load` - Load RDF/OWL ontology
- `GET /ontology/summary` - Get class/instance/triple counts
- `GET /ontology/instances?class_name=Customer` - List instances
- `POST /ontology/update` - Apply RDF triples
- `GET /ontology/diff` - Get added/removed triples

### Simulation
- `POST /simulation/config` - Set parameters
- `POST /simulation/start` - Start simulation
- `POST /simulation/stop` - Stop simulation
- `POST /simulation/step` - Run single step
- `GET /simulation/metrics` - Get metrics
- `GET /simulation/status` - Get status

### WebSocket
- `WS /ws` - Real-time event streaming

**Full API docs**: http://localhost:8000/docs

---

## 🎓 Research Concepts

### Multi-Agent Systems (MAS)
- **Autonomy**: Agents make independent decisions
- **Interaction**: Agents share environment and influence each other
- **Emergence**: Complex behavior arises from simple agent rules

### Hidden Markov Models (HMM)
- **Hidden States**: Unobservable emotional states (Happy/Neutral/Unhappy)
- **Observations**: Observable behaviors (Purchase/Complaint/Silence)
- **Inference**: Viterbi algorithm decodes hidden state sequence
- **Application**: Service optimization based on inferred satisfaction

### Ontologies
- **Formal Representation**: Classes, properties, instances
- **Semantic Reasoning**: Infer implicit relationships
- **Interoperability**: Standard formats (RDF/OWL)
- **Validation**: Check consistency and constraints

---

## 📈 Use Cases

1. **Customer Service**: Infer satisfaction from behavior, optimize support
2. **Healthcare**: Monitor patient states from observable symptoms
3. **Smart Cities**: Track citizen sentiment from urban interactions
4. **E-commerce**: Predict user intent from browsing patterns
5. **Education**: Assess student engagement from participation

---

## 🔄 Workflow Example

```
1. Load Ontology
   → RDFlib parses ontology
   → Classes/instances displayed

2. Configure Simulation
   → Set # agents, HMM parameters
   → Backend stores config

3. Start Simulation
   → Mesa activates agents
   → Customers emit observations
   → Service agents run Viterbi

4. Real-Time Updates
   → Events broadcast via WebSocket
   → Frontend updates grid/charts
   → Ontology tracks changes

5. Export Results
   → Download logs, metrics, ontology
   → Analyze offline or share
```

---

## 📝 Documentation Files

| File | Purpose |
|------|---------|
| `START_HERE.md` | Quick start guide (this file) |
| `README.md` | Comprehensive documentation |
| `report-notes.md` | Technical report on MAS/HMM/Ontology integration |
| Backend API docs | http://localhost:8000/docs (interactive Swagger) |

---

## ✅ Installation Status

- ✅ **Backend**: Virtual environment created, all dependencies installed
- ✅ **Frontend**: Node modules installed (--legacy-peer-deps)
- ✅ **Files**: All source code, configs, and docs created
- ✅ **Docker**: Dockerfile + docker-compose.yml ready (optional)

---

## 🎉 Next Steps

### To Run the Application:
1. Follow instructions in `START_HERE.md`
2. Start backend in Terminal 1
3. Start frontend in Terminal 2
4. Open http://localhost:5173 in browser
5. Load ontology → Configure → Start simulation!

### To Extend the Application:
- **Add New Agent Types**: Edit `backend/models/mesa_model.py`
- **Custom Ontologies**: Create your own RDF/OWL files
- **New Visualizations**: Add components in `frontend/src/components/`
- **Advanced HMM**: Implement POMCP, particle filters, etc.
- **SWRL Rules**: Add logical inference rules to ontology

### To Deploy:
```powershell
# Docker deployment
docker-compose up --build

# Or deploy to cloud (Azure, AWS, etc.)
# - Backend: Deploy as container or serverless function
# - Frontend: Build and host static files (npm run build)
```

---

## 🏆 Achievements

✨ **Full-Stack Application**: FastAPI backend + React frontend  
✨ **Real-Time Streaming**: WebSocket integration  
✨ **AI/ML Integration**: HMM inference with Viterbi algorithm  
✨ **Semantic Web**: RDF/OWL ontology management  
✨ **Agent-Based Modeling**: Mesa multi-agent simulation  
✨ **Modern Tech Stack**: TypeScript, Tailwind, Zustand, Recharts  
✨ **Production-Ready**: Docker, API docs, comprehensive error handling  
✨ **Well-Documented**: README, quick start, technical report  

---

## 📞 Support

- **Backend Issues**: Check `f:\BMS_Project_Ready_To_Run\ontology-mas-ui\backend` terminal
- **Frontend Issues**: Check browser console (F12)
- **API Testing**: Use http://localhost:8000/docs (Swagger UI)
- **Architecture**: Read `report-notes.md` for technical deep-dive

---

**🎊 Project Successfully Completed! 🎊**

Everything is ready to run. Follow the Quick Start instructions and enjoy your Ontology-Driven MAS Simulator!
