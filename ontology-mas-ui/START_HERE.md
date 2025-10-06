# Quick Start Guide

## 🚀 Running the Ontology-Driven MAS Simulator

### Prerequisites
- ✅ Backend dependencies installed
- ✅ Frontend dependencies installed

### Start the Application (Two Terminals Required)

#### Terminal 1: Backend Server
```powershell
cd f:\BMS_Project_Ready_To_Run\ontology-mas-ui\backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Backend will be available at:**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws

#### Terminal 2: Frontend Dev Server
```powershell
cd f:\BMS_Project_Ready_To_Run\ontology-mas-ui\frontend
npm run dev
```

**Expected Output:**
```
VITE v5.0.8  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help
```

**Frontend will be available at:**
- UI: http://localhost:5173

### Open Your Browser
Navigate to: **http://localhost:5173**

---

## 📖 Usage Workflow

### Step 1: Load Ontology
1. Click **"Load Ontology"** button in the top bar
2. Choose **"Use Sample"** for demo ontology OR upload your own RDF/OWL/TTL file
3. See ontology summary appear in the left panel (classes, instances, triples)

### Step 2: Configure Simulation
1. Click **"Configure"** button
2. Set simulation parameters:
   - **Ticks**: Number of simulation steps (e.g., 50)
   - **Seed**: Random seed for reproducibility (e.g., 42)
   - **Customers**: Number of customer agents (e.g., 5)
   - **Service Agents**: Number of service agents (e.g., 2)
3. Configure HMM parameters:
   - **States**: Comma-separated (e.g., `Happy,Neutral,Unhappy`)
   - **Observations**: Comma-separated (e.g., `Purchase,Complaint,Silence`)
   - **Transition Matrix**: 3x3 matrix for state transitions
   - **Emission Matrix**: 3x3 matrix for observation probabilities
   - **Initial Distribution**: Starting probabilities
4. Click **"Save"**

### Step 3: Run Simulation
1. Click **"Start Simulation"** (green button)
2. Watch the simulation in real-time:
   - **Left Panel**: Ontology classes/instances update
   - **Center Panel**: Grid visualization with agent positions
   - **Center Console**: Event stream (observations)
   - **Right Panel**: HMM metrics and inferred customer states

### Step 4: Inspect Results
- **Observations Chart**: Bar chart showing Purchase, Complaint, Silence counts
- **Customer States Table**: Each customer's inferred emotional state with log-probability
- **Ontology Diff**: Real-time tracking of added/removed RDF triples
- **Event Log**: Chronological stream of agent actions

### Step 5: Export Data
Click export buttons in the right panel:
- **Download Logs (CSV)**: Event stream for analysis
- **Download Metrics (JSON)**: Simulation metrics and HMM inference results
- **Download Ontology (TTL)**: Updated RDF ontology with simulation data

---

## 🔧 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process by PID
taskkill /PID <PID> /F
```

**ModuleNotFoundError:**
```powershell
# Ensure venv is activated (you should see (venv) in prompt)
.\venv\Scripts\Activate.ps1
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Cannot connect to backend:**
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify `vite.config.ts` proxy settings

**Module not found errors:**
```powershell
# Delete node_modules and reinstall
rm -r node_modules
rm package-lock.json
npm install --legacy-peer-deps
```

**WebSocket connection failed:**
- Check that backend is running
- Verify WebSocket URL in `appStore.ts` matches backend

### General Issues

**Simulation not starting:**
- Load an ontology first
- Configure simulation parameters
- Check backend terminal for error messages

**No events appearing:**
- Ensure simulation is running (green "Stop" button visible)
- Check WebSocket connection status (top-right indicator)
- Refresh browser and reconnect

---

## 🎯 Quick Demo

**5-Minute Demo:**
1. Start backend + frontend (both terminals)
2. Open http://localhost:5173
3. Click "Load Ontology" → "Use Sample"
4. Click "Configure" → Keep defaults → "Save"
5. Click "Start Simulation"
6. Watch agents move, observe events, see HMM inference!

---

## 📚 Documentation

- **Full README**: `README.md`
- **Technical Report**: `report-notes.md`
- **API Documentation**: http://localhost:8000/docs (when backend running)

---

## 🐳 Docker Alternative (Optional)

If you have Docker installed:

```powershell
# Build and run both services
docker-compose up --build

# Access:
# - Frontend: http://localhost:5173
# - Backend: http://localhost:8000
```

---

## 🎓 Key Concepts

- **Multi-Agent System**: Autonomous agents (customers + service agents) interact on a grid
- **Hidden Markov Model**: Service agents infer customer emotions from observable behaviors
- **Ontology**: Formal knowledge representation (RDF/OWL) tracks agent states and relationships
- **Viterbi Algorithm**: Finds most likely sequence of hidden states given observations
- **WebSocket Streaming**: Real-time updates from backend to frontend

---

## 📞 Need Help?

- Check backend terminal for error logs
- Check browser console (F12) for frontend errors
- Review `report-notes.md` for architecture details
- Inspect API docs at http://localhost:8000/docs

---

**Happy Simulating! 🎉**
