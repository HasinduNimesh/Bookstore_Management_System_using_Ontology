"""FastAPI main application."""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException  # type: ignore[import-not-found]
from fastapi.middleware.cors import CORSMiddleware  # type: ignore[import-not-found]
from pydantic import BaseModel  # type: ignore[import-not-found]
from typing import Optional, List, Dict, Any, Tuple
from rdflib import Namespace, RDF, RDFS, Literal  # type: ignore[import-not-found]
import asyncio
import json
import logging

from models.ontology import GraphManager
from models.hmm import HMMInference
from models.mesa_model import SimulationModel
from services.bus import event_bus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ontology-Driven MAS Simulator")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
graph_manager = GraphManager()
simulation_model: Optional[SimulationModel] = None
simulation_config: Optional[Dict[str, Any]] = None
hmm_instance: Optional[HMMInference] = None
simulation_running = False
simulation_task: Optional[asyncio.Task] = None
websocket_clients: List[WebSocket] = []

# ============ Models ============

class OntologyLoadRequest(BaseModel):
    path: Optional[str] = None
    ttl: Optional[str] = None
    owl: Optional[str] = None

class InventoryItem(BaseModel):
    sku: Optional[str] = None
    title: Optional[str] = None
    price: float = 10.0
    onHand: int = 20
    threshold: int = 5
    restockAmount: int = 10


class SimulationConfigRequest(BaseModel):
    ticks: int = 100
    seed: int = 42
    numCustomers: int = 20
    numServiceAgents: int = 2
    gridWidth: int = 10
    gridHeight: int = 10
    hmm: Dict[str, Any]
    inventory: Optional[List[InventoryItem]] = None

class OntologyUpdateRequest(BaseModel):
    # Each triple: (subject, predicate, object, is_add)
    triples: List[Tuple[str, str, str, bool]]

# ============ Ontology Endpoints ============

@app.post("/ontology/load")
async def load_ontology(request: OntologyLoadRequest):
    """Load ontology from path or string."""
    try:
        result = graph_manager.load_graph(
            path=request.path,
            ttl=request.ttl,
            owl=request.owl
        )
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Failed to load ontology: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ontology/summary")
async def ontology_summary():
    """Get ontology summary."""
    return graph_manager.summary()

@app.get("/ontology/instances")
async def get_instances(class_name: str):
    """Get instances of a class."""
    instances = graph_manager.get_instances(class_name)
    return {"class": class_name, "instances": instances}

@app.post("/ontology/update")
async def update_ontology(request: OntologyUpdateRequest):
    """Apply triple updates."""
    try:
        result = graph_manager.apply_updates(request.triples)
        diff = graph_manager.diff()
        return {"status": "success", "result": result, "diff": diff}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/ontology/diff")
async def get_diff():
    """Get ontology diff since initial load."""
    return graph_manager.diff()

# ============ Simulation Endpoints ============

@app.post("/simulation/config")
async def set_simulation_config(config: SimulationConfigRequest):
    """Set simulation configuration."""
    global simulation_config, hmm_instance
    
    try:
        simulation_config = config.dict()
        
        # Initialize HMM
        hmm_instance = HMMInference(config.hmm)

        # If inventory not provided explicitly, derive it from the loaded ontology
        if not simulation_config.get("inventory"):
            derived_inventory = extract_inventory_from_ontology(graph_manager)
            if derived_inventory:
                simulation_config["inventory"] = derived_inventory
            else:
                raise HTTPException(status_code=400, detail="No inventory data found in ontology. Load an ontology with Inventory instances or provide inventory in the configuration.")
        
        return {"status": "success", "config": simulation_config}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set config: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/simulation/start")
async def start_simulation():
    """Start the simulation."""
    global simulation_model, simulation_running, simulation_task
    
    if not simulation_config or not hmm_instance:
        raise HTTPException(status_code=400, detail="Configuration not set")
    if not graph_manager.graph:
        raise HTTPException(status_code=400, detail="Ontology must be loaded before starting the simulation")
    
    if simulation_running:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    try:
        # Create model
        simulation_model = SimulationModel(simulation_config, graph_manager, hmm_instance)
        simulation_running = True
        
        # Start simulation loop in background
        simulation_task = asyncio.create_task(run_simulation())
        
        return {"status": "success", "message": "Simulation started"}
    except Exception as e:
        logger.error(f"Failed to start simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulation/stop")
async def stop_simulation():
    """Stop the simulation."""
    global simulation_running, simulation_task
    
    simulation_running = False
    
    if simulation_task:
        simulation_task.cancel()
        try:
            await simulation_task
        except asyncio.CancelledError:
            pass
    
    return {"status": "success", "message": "Simulation stopped"}

@app.post("/simulation/step")
async def step_simulation():
    """Step simulation once."""
    if not simulation_model:
        raise HTTPException(status_code=400, detail="Simulation not initialized")
    
    simulation_model.step()
    
    # Broadcast tick
    await broadcast_tick()
    
    return {"status": "success", "tick": simulation_model.current_tick}

@app.get("/simulation/metrics")
async def get_metrics():
    """Get cumulative metrics."""
    if not simulation_model:
        return {"metrics": {}}
    
    return {
        "metrics": simulation_model.metrics,
        "tick": simulation_model.current_tick
    }

@app.get("/simulation/logs")
async def get_logs():
    """Get simulation logs (placeholder)."""
    # TODO: Implement NDJSON log file
    return {"logs": []}

@app.get("/simulation/status")
async def get_status():
    """Get simulation status."""
    return {
        "running": simulation_running,
        "tick": simulation_model.current_tick if simulation_model else 0,
        "configured": simulation_config is not None
    }

# ============ WebSocket ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for live simulation updates."""
    await websocket.accept()
    websocket_clients.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(websocket_clients)}")
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle client messages if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(websocket_clients)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)

async def broadcast_tick():
    """Broadcast current tick state to all WebSocket clients."""
    if not simulation_model:
        return
    
    payload = {
        "tick": simulation_model.current_tick,
        "events": simulation_model.events,
        "grid": simulation_model.get_grid_state(),
        "metrics": simulation_model.metrics,
        "customerStates": simulation_model.get_customer_states(),
        "inventory": simulation_model.get_inventory_snapshot()
    }
    
    # Send to all connected clients
    disconnected = []
    for client in websocket_clients:
        try:
            await client.send_json(payload)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")
            disconnected.append(client)
    
    # Clean up disconnected clients
    for client in disconnected:
        if client in websocket_clients:
            websocket_clients.remove(client)

async def run_simulation():
    """Run simulation loop."""
    global simulation_running
    
    # Defensive guards for type checker and runtime
    if simulation_config is None or simulation_model is None:
        logger.warning("Simulation config or model missing; aborting run loop")
        return
    max_ticks = int(simulation_config.get("ticks", 100))
    
    try:
        while simulation_running and simulation_model.current_tick < max_ticks:
            simulation_model.step()
            
            # Broadcast tick
            await broadcast_tick()
            
            # Delay between ticks
            await asyncio.sleep(0.5)
        
        simulation_running = False
        logger.info("Simulation completed")
    except asyncio.CancelledError:
        logger.info("Simulation cancelled")
        simulation_running = False
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        simulation_running = False

@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "service": "Ontology-Driven MAS Simulator"}

def extract_inventory_from_ontology(manager: GraphManager) -> List[Dict[str, Any]]:
    """Translate Inventory individuals from the loaded ontology into simulation-ready items."""
    if not manager.graph:
        return []

    graph = manager.graph
    ex_prefix = manager.namespaces.get("ex", "http://example.org/bookstore#")
    EX = Namespace(ex_prefix)

    def literal_to_int(value: Any, default: int) -> int:
        if value is None:
            return default
        try:
            return int(float(value))
        except Exception:
            return default

    def literal_to_float(value: Any, default: float) -> float:
        if value is None:
            return default
        try:
            return float(value)
        except Exception:
            return default

    inventory_items: List[Dict[str, Any]] = []
    for inv in graph.subjects(RDF.type, EX.Inventory):
        book = next(graph.objects(inv, EX.hasBook), None)
        if book is None:
            continue

        title = next(graph.objects(book, EX.title), None)
        price = next(graph.objects(book, EX.price), None)
        available = next(graph.objects(inv, EX.availableQuantity), None)
        threshold = next(graph.objects(inv, EX.thresholdQuantity), None)
        restock = next(graph.objects(inv, EX.restockAmount), None)

        if title is None:
            # Try rdfs:label as fallback
            label = next(graph.objects(book, RDFS.label), None)
            title = label

        if title is None:
            continue

        short = manager._short_name(book)
        sku_value = short.split(":", 1)[-1] if ":" in short else short

        item = {
            "sku": sku_value,
            "title": str(title),
            "price": literal_to_float(price, 10.0),
            "onHand": literal_to_int(available, 10),
            "threshold": literal_to_int(threshold, 5),
            "restockAmount": literal_to_int(restock, 10)
        }
        inventory_items.append(item)

    return inventory_items


if __name__ == "__main__":
    import uvicorn  # type: ignore[import-not-found]
    uvicorn.run(app, host="0.0.0.0", port=8000)
