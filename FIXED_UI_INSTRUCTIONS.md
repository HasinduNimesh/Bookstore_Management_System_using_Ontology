# ✅ UI Dashboard Fixed - Correct Usage Steps

## What Was Wrong

The inventory data wasn't showing because:
1. **Backend extracts inventory from the loaded ontology** during configuration
2. **Frontend wasn't capturing the inventory** from the config response
3. You needed to click **"Configure"** button after loading the ontology

## ✅ What I Fixed

1. **`appStore.ts`**: Modified `setConfig` to accept and store inventory array
2. **`TopBar.tsx`**: Extract inventory from backend response and pass to store
3. **`HMMDashboard.tsx`**: Improved empty state message with clear instructions

## 🎯 Correct Usage Steps (IMPORTANT!)

### Step 1: Open Web UI
```powershell
# Navigate to http://localhost:5173
```

### Step 2: Load Sample Ontology
Click **"Load Sample Ontology"** button (top right, blue)
- This loads the bookstore ontology with 12 books
- You'll see "ex:Book (4)" and "ex:Inventory (4)" in the Ontology Inspector

### Step 3: Configure Simulation ⚠️ **CRITICAL STEP**
Click **"Configure"** button (top right, gray)
- Fill in the form:
  - Ticks: 20
  - Seed: 42
  - Customers: 5
  - Service Agents: 1
- Click **"Apply"**
- You should see: **"Configuration set! Loaded 12 books from ontology."**

### Step 4: Start Simulation
Click **"Start"** button (now enabled)
- Simulation will run for 20 ticks
- **Inventory chart will now show all 12 books** 📊
- **Recent Events will show purchases, restocks, stockouts** 📚📦❌
- **Inventory table will display book details** with stock levels

## 📊 What You Should See Now

### Bookstore Metrics & KPIs Panel (Right Side):
- **PURCHASES**: Real-time purchase count
- **RESTOCKS**: Employee restocking events
- **STOCKOUTS**: Out-of-stock incidents
- **REVENUE**: Total sales revenue

### Book Inventory Stock Levels (Bar Chart):
- Blue bars: Current stock
- Red bars: Restock threshold
- All 12 books displayed (Pride and Prejudice, 1984, etc.)

### Recent Events (Agent Activity):
- 📚 **Purchase**: "Customer X purchased 'Book Title'"
- 📦 **Restock**: "Restocked 'Book Title' (+10 units)"
- ❌ **Stockout**: "'Book Title' is out of stock!"

### Inventory Snapshot (Table):
| Title | On Hand | Threshold | Restock |
|-------|---------|-----------|---------|
| Pride and Prejudice | 15 | 5 | 10 |
| 1984 | 12 | 5 | 10 |
| ... | ... | ... | ... |

## 🔧 Troubleshooting

### If inventory still doesn't show:
1. **Stop simulation** if running
2. **Click "Load Sample Ontology"** again
3. **Click "Configure"** again (this is the critical step!)
4. **Start simulation**

### If backend needs restart:
```powershell
# In backend terminal (Ctrl+C to stop)
cd ontology-mas-ui\backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🎥 Ready for Video Recording

Now that the UI is working correctly, you can record your video showing:
1. ✅ Loading the ontology (see classes and instances)
2. ✅ Configuring the simulation (loads 12 books)
3. ✅ Running the simulation (see agent interactions)
4. ✅ Real-time inventory updates (bar chart animating)
5. ✅ Purchase/restock events (scrolling feed)
6. ✅ Customer state inference (HMM predictions)

## 📝 Technical Details

### Backend Flow:
```python
# main.py /simulation/config endpoint
1. Receives config from frontend
2. Calls extract_inventory_from_ontology(graph_manager)
3. Queries all ex:Inventory individuals from loaded ontology
4. Returns: {"status": "success", "config": {..., "inventory": [12 books]}}
```

### Frontend Flow:
```typescript
// TopBar.tsx onSubmitConfig
1. api.setConfig(config) → backend
2. response.config.inventory → 12 books array
3. setConfig(backendConfig, inventory) → store
4. HMMDashboard reads inventory from store → renders chart + table
```

## ✨ Summary

**The key was:** You MUST click **"Configure"** after loading the ontology!

This step:
- Extracts the 12 books from the ontology
- Sends them to the simulation model
- Stores them in the frontend state
- Enables the inventory visualization

Without this step, the simulation has no book data to display!
