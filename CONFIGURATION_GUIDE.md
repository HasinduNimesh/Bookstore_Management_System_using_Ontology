# 🎛️ Configuration Guide

## Simulation Settings

When you click **"Configure"** in the top bar, you can adjust these settings:

### 1️⃣ Total Ticks
**Default:** 100  
**Range:** 1 - unlimited  
**What it does:** How many simulation steps to run before stopping automatically.

**Recommendations:**
- **Quick test:** 10-20 ticks
- **Normal run:** 50-100 ticks  
- **Long analysis:** 200+ ticks

---

### 2️⃣ Random Seed
**Default:** 42  
**Range:** Any integer  
**What it does:** Controls randomness. Same seed = same results (reproducible simulations).

**Use cases:**
- Keep at `42` for consistent testing
- Change to get different random behaviors
- Document your seed for reproducible research

---

### 3️⃣ Customer Agents
**Default:** 20  
**Range:** 1 - unlimited  
**What it does:** Number of customer agents browsing and buying books.

**Recommendations:**
- **Low traffic:** 5-10 customers (easier to track)
- **Normal traffic:** 15-25 customers (balanced)
- **High traffic:** 30-50 customers (stress test)

**Impact:**
- More customers = more purchases = more stockouts
- More customers = slower simulation
- Grid size is 10×10, so 100 is the visual maximum

---

### 4️⃣ Service Agents (Restock)
**Default:** 2  
**Range:** 1 - unlimited  
**What it does:** Number of service agents monitoring inventory and placing restock orders.

**Recommendations:**
- **Minimal:** 1 agent (may miss some restocks)
- **Balanced:** 2-3 agents (good coverage)
- **High capacity:** 4-5 agents (catches everything)

**Impact:**
- More agents = better inventory monitoring
- More agents = faster restock order placement
- However, **restock delay is 3 ticks** regardless of agent count
- More agents don't speed up deliveries, just detection

---

## How Service Agents Handle Restocking

### Process Flow:
```
Tick 1:  Customer buys → Stock drops to threshold
         ↓
Tick 1:  Service Agent detects low stock
         ↓
Tick 1:  🚚 Restock order placed (50 units ordered)
         ↓
Tick 2:  ⏳ In transit... (2 ticks remaining)
         ↓
Tick 3:  ⏳ In transit... (1 tick remaining)
         ↓
Tick 4:  ✅ Delivery arrives! (+50 units added)
```

### Multiple Service Agents:
- **1 Agent:** Processes customers sequentially, might miss some
- **2-3 Agents:** Better coverage, parallel processing
- **4+ Agents:** Redundant for small inventories, but useful for scale

---

## Example Configurations

### 🎯 Quick Demo (Fast)
- **Ticks:** 20
- **Seed:** 42
- **Customers:** 10
- **Service Agents:** 2
- **Result:** Quick 20-second demo showing basic mechanics

---

### 📊 Standard Analysis (Balanced)
- **Ticks:** 100
- **Seed:** 42
- **Customers:** 20
- **Service Agents:** 2-3
- **Result:** Good data for metrics, see full restock cycles

---

### 🔥 Stress Test (Heavy)
- **Ticks:** 200
- **Seed:** Any
- **Customers:** 40-50
- **Service Agents:** 4-5
- **Result:** High stockout rate, lots of restock activity

---

### 🧪 Scientific (Reproducible)
- **Ticks:** 100
- **Seed:** 12345 (document this!)
- **Customers:** 25
- **Service Agents:** 3
- **Result:** Reproducible for research papers

---

## Tips

1. **Start small** - Use 20 ticks and 10 customers for first run
2. **Watch the grid** - See agents moving and interacting
3. **Check Message Log** - See internal agent communications
4. **Monitor metrics** - Purchases, Restocks, Stockouts
5. **Adjust agents** - If too many stockouts, add service agents
6. **Compare runs** - Use same seed to test changes

---

## Current Settings (Default)
```json
{
  "ticks": 100,
  "seed": 42,
  "numCustomers": 20,
  "numServiceAgents": 2
}
```

These defaults provide a **balanced simulation** that:
- ✅ Runs long enough to see patterns (100 ticks)
- ✅ Has enough activity to be interesting (20 customers)
- ✅ Has adequate inventory monitoring (2 service agents)
- ✅ Shows restock delays clearly (3-tick delivery)
- ✅ Produces meaningful metrics

**Refresh browser → Click Configure → Adjust settings → Apply → Start!** 🚀
