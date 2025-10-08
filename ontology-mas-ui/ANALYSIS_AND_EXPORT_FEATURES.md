# Simulation Analysis & Data Export Features

## Overview
Enhanced the application with comprehensive analysis tools and data export capabilities to provide full transparency into simulation results.

## New Features

### 1. **Complete Message Log** 📝
- **Keeps ALL messages** from the entire simulation (no more limit of 20)
- Messages never "disappear" during simulation
- Better visual styling with:
  - Blue border and header for visibility
  - Count badge showing total messages
  - Smooth scrolling
  - Larger spacing between messages

**Location**: Bottom-center panel in the main UI

### 2. **Simulation Summary Dashboard** 📊
- **Auto-shows** when simulation completes (1 second delay)
- **Manual access** via "📊 View Analysis" button (bottom-left corner)
- Provides comprehensive analysis with:
  - Key metrics (purchases, stockouts, restocks, revenue, messages)
  - Multiple interactive charts
  - Customer state distribution
  - Inventory levels
  - Communication statistics

### 3. **Data Export Capabilities** 💾

#### Download All Data (JSON)
Downloads a complete JSON file containing:
- Simulation summary (ticks, timestamp)
- All metrics
- Customer states with HMM probabilities
- Final inventory levels
- Message statistics
- **All events** (every single event that occurred)
- **All messages** (complete communication log)

**Format**: `simulation-data-tick-[N]-[timestamp].json`

#### Download Messages (CSV)
Downloads agent messages in CSV format with columns:
- Tick
- From (sender agent)
- To (receiver agent)
- Topic (purchase_request, service_response, restock_request, restock_done)
- Content (message text)
- SKU (book identifier)
- Quantity

**Format**: `agent-messages-tick-[N]-[timestamp].csv`
**Use case**: Import into Excel, Google Sheets, or data analysis tools

### 4. **Interactive Charts** 📈

#### Revenue Growth Over Time (Line Chart) 💰 **NEW!**
- **Shows how revenue accumulated** as customer agents made purchases
- **Dual Y-axis visualization**:
  - Left axis: Cumulative revenue in dollars (green line)
  - Right axis: Total number of purchases (blue line)
- **Demonstrates agent impact**: See exactly when purchases happened and how they drove revenue
- **Key metrics displayed**:
  - Final Revenue: Total money earned
  - Total Purchases: Number of successful transactions
  - Average Sale Price: Revenue per transaction
- **Interactive hover**: Click points to see exact values at each simulation tick
- **Business insights**: Identify periods of high activity or revenue plateaus

#### Agent Communication Breakdown (Pie Chart)
- Shows distribution of message types:
  - 🛒 Purchase Requests (blue)
  - 💬 Service Responses (purple)
  - 📦 Restock Orders (green)
  - ✅ Deliveries (orange)

#### Customer State Distribution (Pie Chart)
- Shows HMM-inferred emotional states:
  - Happy (green)
  - Neutral (blue)
  - Unhappy (red)

#### Event Type Summary (Bar Chart)
- Visual comparison of:
  - Purchases
  - Complaints
  - Silence observations
  - Restocks
  - Stockouts

#### Final Inventory Levels (Horizontal Bar Chart)
- Shows for each book:
  - Current stock (green)
  - Restock threshold (red)
- Helps identify which books sold well

### 5. **Communication Statistics** 📊
Detailed breakdown showing:
- 🛒 Total purchase requests
- 💬 Total service responses
- 📦 Total restock orders
- ✅ Total deliveries confirmed

## How to Use

### During Simulation
1. **Watch messages appear** in the bottom-center panel
2. Messages are color-coded by type
3. Scroll to see older messages (they never disappear!)
4. Total count shows in header badge

### After Simulation
1. **Automatic**: Summary pops up 1 second after simulation stops
2. **Manual**: Click "📊 View Analysis" button anytime
3. **Review charts** to understand simulation behavior
4. **Download data**:
   - Click "📦 Download All Data (JSON)" for complete dataset
   - Click "💬 Download Messages (CSV)" for message log

### Analyzing Downloaded Data

#### JSON File Contents
```json
{
  "simulationSummary": {
    "totalTicks": 50,
    "timestamp": "2025-10-07T..."
  },
  "metrics": {
    "purchases": 45,
    "stockouts": 12,
    "restocks": 8,
    "revenue": 678.45,
    ...
  },
  "customerStates": [
    {
      "custId": "cust_5",
      "inferredState": "Happy",
      "logprob": -42.48,
      ...
    }
  ],
  "allMessages": [
    {
      "type": "message",
      "from": "Customer_5",
      "to": "ServiceAgent",
      "topic": "purchase_request",
      "content": "I want to buy 'Dune'",
      "tick": 12,
      ...
    }
  ]
}
```

#### CSV File Structure
```csv
Tick,From,To,Topic,Content,SKU,Quantity
12,"Customer_5","ServiceAgent","purchase_request","I want to buy 'Dune'","Book_Dune",""
13,"ServiceAgent_2","Customer_5","service_response","Customer seems Happy",,"
14,"EmployeeAgent","Supplier","restock_request","Order 15 units of 'Harry Potter'","Book_HarryPotter","15"
```

## Technical Details

### Performance Considerations
- **All events are kept** in memory during simulation
- For very long simulations (1000+ ticks), this may use more RAM
- The UI remains responsive due to virtual scrolling
- Download operations are handled client-side (no server overhead)

### Data Persistence
- Events are stored in Zustand state management
- Data is NOT persisted between page refreshes
- **Important**: Download data before closing browser!

### Browser Compatibility
- Works in all modern browsers (Chrome, Firefox, Safari, Edge)
- File downloads use standard Blob API
- Charts rendered using Recharts library

## Use Cases

### Academic Research
- Export all data for statistical analysis
- Import CSV into R, Python pandas, or SPSS
- Analyze agent behavior patterns
- Study HMM inference accuracy

### Debugging
- Review complete message log to understand agent interactions
- Check if restocks are arriving on time
- Verify customer state transitions
- Identify bottlenecks in the system

### Presentations
- Use charts directly from summary dashboard
- Export data for custom visualizations
- Show message log to demonstrate agent communication
- Prove system is working correctly (real data, not mock!)

### Comparison Studies
- Run multiple simulations with different parameters
- Download data from each run
- Compare results side-by-side
- Identify optimal configuration

## Tips

1. **Run shorter simulations first** (50-100 ticks) to get familiar with data structure
2. **Check message count** in real-time to ensure agents are communicating
3. **Download immediately** after simulation completes
4. **Open JSON in a viewer** (like https://jsonviewer.stack.hu) for better readability
5. **Use CSV** for quick analysis in Excel or Google Sheets

## Future Enhancements
- [ ] Save simulation history to local storage
- [ ] Compare multiple simulation runs side-by-side
- [ ] Export charts as images (PNG/SVG)
- [ ] Time-series charts showing metrics over ticks
- [ ] Filter messages by agent or topic
- [ ] Search functionality in message log
