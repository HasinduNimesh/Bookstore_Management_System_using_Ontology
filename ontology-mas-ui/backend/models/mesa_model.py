"""Mesa-based multi-agent simulation model."""
from typing import Dict, List, Optional, Any
import random
import logging
from mesa import Agent, Model  # type: ignore[import-not-found]
from mesa.time import RandomActivation  # type: ignore[import-not-found]
from mesa.space import MultiGrid  # type: ignore[import-not-found]
from mesa.datacollection import DataCollector  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

class CustomerAgent(Agent):
    """Customer agent with hidden emotional state."""
    
    def __init__(self, unique_id: int, model: 'SimulationModel', hmm_config: dict):
        super().__init__(unique_id, model)
        self.hmm_states = hmm_config["states"]
        self.hmm_observations = hmm_config["observations"]
        
        # Initialize hidden state (true mood)
        self.hidden_state = random.choice(self.hmm_states)
        self.observation_history: List[str] = []
        self.inferred_state: Optional[str] = None
        self.inferred_logprob: float = 0.0
        
    def step(self):
        """Emit an observation based on hidden state."""
        # Sample observation from HMM emission
        m: Any = self.model
        obs = m.hmm.sample_observation(self.hidden_state)  # type: ignore[attr-defined]
        self.observation_history.append(obs)
        
        # Emit event
        m.add_event({  # type: ignore[attr-defined]
            "type": "observation",
            "agentId": f"cust_{self.unique_id}",
            "obs": obs,
            "trueState": self.hidden_state  # For debugging
        })
        
        # Simulate purchase request message (customers occasionally want to buy)
        if obs == "Purchase" and random.random() < 0.5:
            # Pick a random book from inventory
            if hasattr(m, 'inventory') and m.inventory:
                book_sku = random.choice(list(m.inventory.keys()))
                book_title = m.inventory[book_sku]["title"]
                
                m.add_event({
                    "type": "message",
                    "from": f"Customer_{self.unique_id}",
                    "to": "ServiceAgent",
                    "topic": "purchase_request",
                    "content": f"I want to buy '{book_title}'",
                    "sku": book_sku
                })
        
        # Possibly transition to new hidden state
        if random.random() < 0.3:  # 30% chance of state change per tick
            self.hidden_state = m.hmm.sample_next_state(self.hidden_state)  # type: ignore[attr-defined]
        
        # Update ontology if loaded
        if getattr(m, "graph_manager", None) and getattr(m.graph_manager, "graph", None):  # type: ignore[attr-defined]
            self._update_ontology(obs)
    
    def _update_ontology(self, obs: str):
        """Add observation to ontology."""
        customer_uri = f"ex:Customer_{self.unique_id}"
        m: Any = self.model
        obs_uri = f"ex:Obs_{self.unique_id}_{getattr(m, 'current_tick', 0)}"
        
        triples = [
            (customer_uri, "rdf:type", "ex:Customer", True),
            (obs_uri, "rdf:type", "ex:Observation", True),
            (obs_uri, "ex:observedBy", customer_uri, True),
            (obs_uri, "ex:observationType", obs, True),
            (obs_uri, "ex:atTick", str(getattr(m, 'current_tick', 0)), True),
        ]
        
        m.graph_manager.apply_updates(triples)  # type: ignore[attr-defined]

class ServiceAgent(Agent):
    """Service agent that infers customer states via HMM."""
    
    def __init__(self, unique_id: int, model: 'SimulationModel'):
        super().__init__(unique_id, model)
        self.inferences_made = 0
        
    def step(self):
        """Process observations and infer customer states."""
        m: Any = self.model
        for customer in getattr(getattr(m, 'schedule', None), 'agents', []):
            if not isinstance(customer, CustomerAgent):
                continue
            
            # Run Viterbi on customer's observation history
            if len(customer.observation_history) > 0:
                hmm = getattr(m, 'hmm', None)
                if hmm is None:
                    continue
                states, logprob = hmm.viterbi(customer.observation_history)
                
                if states:
                    inferred_state = states[-1]  # Most recent state
                    customer.inferred_state = inferred_state
                    customer.inferred_logprob = logprob
                    
                    self.inferences_made += 1
                    
                    # Emit inference event
                    m.add_event({  # type: ignore[attr-defined]
                        "type": "inference",
                        "agentId": f"svc_{self.unique_id}",
                        "custId": f"cust_{customer.unique_id}",
                        "inferredState": inferred_state,
                        "logprob": logprob
                    })
                    
                    # Service agent responds to customer
                    if inferred_state == "Happy" and random.random() < 0.3:
                        m.add_event({
                            "type": "message",
                            "from": f"ServiceAgent_{self.unique_id}",
                            "to": f"Customer_{customer.unique_id}",
                            "topic": "service_response",
                            "content": f"Customer seems {inferred_state}, providing recommendation"
                        })

class SimulationModel(Model):
    """Main simulation model."""
    
    def __init__(self, config: Dict[str, Any], graph_manager, hmm):
        super().__init__()
        
        self.config = config
        self.graph_manager = graph_manager
        self.hmm = hmm
        
        self.num_customers = config.get("numCustomers", 20)
        self.num_service_agents = config.get("numServiceAgents", 2)
        self.grid_width = config.get("gridWidth", 10)
        self.grid_height = config.get("gridHeight", 10)
        self.seed = config.get("seed", 42)
        
        random.seed(self.seed)
        
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        
        self.current_tick = 0
        self.events: List[Dict[str, Any]] = []
        self.metrics = {
            "purchases": 0,
            "complaints": 0,
            "silence": 0,
            "restocks": 0,
            "stockouts": 0,
            "revenue": 0.0
        }

        self.inventory: Dict[str, Dict[str, Any]] = self._init_inventory()
        
        # Track pending restock orders with delivery tick
        self.pending_restocks: Dict[str, Dict[str, Any]] = {}
        # Format: {sku: {"amount": int, "delivery_tick": int, "ordered_tick": int}}
        
        # Create agents
        self._create_agents()
        
        # Data collector
        self.datacollector = DataCollector(
            model_reporters={
                "purchases": lambda m: m.metrics["purchases"],
                "complaints": lambda m: m.metrics["complaints"],
                "silence": lambda m: m.metrics["silence"],
                "restocks": lambda m: m.metrics["restocks"],
                "stockouts": lambda m: m.metrics["stockouts"],
                "revenue": lambda m: m.metrics["revenue"],
            }
        )
    
    def _create_agents(self):
        """Create customer and service agents."""
        # Create customers
        for i in range(self.num_customers):
            agent = CustomerAgent(i, self, self.config.get("hmm", {}))
            self.schedule.add(agent)
            
            # Place on grid
            x = random.randrange(self.grid_width)
            y = random.randrange(self.grid_height)
            self.grid.place_agent(agent, (x, y))
        
        # Create service agents
        for i in range(self.num_service_agents):
            agent = ServiceAgent(self.num_customers + i, self)
            self.schedule.add(agent)
            
            x = random.randrange(self.grid_width)
            y = random.randrange(self.grid_height)
            self.grid.place_agent(agent, (x, y))
    
    def step(self):
        """Advance simulation by one tick."""
        self.events = []  # Clear events
        self.current_tick += 1
        
        # Process pending restock deliveries FIRST (before agent actions)
        self._process_pending_restocks()
        
        self.datacollector.collect(self)
        self.schedule.step()
        
        # Update metrics from events (work on a snapshot so appended events don't re-trigger)
        for event in list(self.events):
            if event.get("type") == "observation":
                obs = event.get("obs", "")
                if obs == "Purchase":
                    self._handle_purchase_event(event)
                elif obs == "Complaint":
                    self.metrics["complaints"] += 1
                elif obs == "Silence":
                    self.metrics["silence"] += 1
    
    def add_event(self, event: Dict[str, Any]):
        """Add event to current tick's event log."""
        event.setdefault("tick", self.current_tick)
        self.events.append(event)
    
    def get_grid_state(self) -> Dict[str, Any]:
        """Return current grid state with agent information."""
        occupied = []
        # coord_iter returns (content, (x, y)) tuples
        for content, (x, y) in self.grid.coord_iter():
            if content:
                # Content is a list of agents at this position (MultiGrid allows multiple)
                agents_at_pos = content if isinstance(content, list) else [content]
                for agent in agents_at_pos:
                    agent_type = "service" if isinstance(agent, ServiceAgent) else "customer"
                    agent_id = f"{agent_type}_{agent.unique_id}"
                    occupied.append({
                        "x": x,
                        "y": y,
                        "agentId": agent_id,
                        "agentType": agent_type
                    })
        
        return {
            "width": self.grid_width,
            "height": self.grid_height,
            "occupied": occupied,
            "pendingRestocks": [
                {
                    "sku": sku,
                    "title": self.inventory[sku]["title"],
                    "amount": order["amount"],
                    "deliveryTick": order["delivery_tick"],
                    "orderedTick": order["ordered_tick"],
                    "ticksRemaining": order["delivery_tick"] - self.current_tick
                }
                for sku, order in self.pending_restocks.items()
            ]
        }
    
    def get_customer_states(self) -> List[Dict[str, Any]]:
        """Return current inferred states for all customers."""
        states = []
        for agent in self.schedule.agents:
            if isinstance(agent, CustomerAgent):
                states.append({
                    "custId": f"cust_{agent.unique_id}",
                    "inferredState": agent.inferred_state or "Unknown",
                    "logprob": agent.inferred_logprob,
                    "observationCount": len(agent.observation_history)
                })
        return states

    def get_inventory_snapshot(self) -> List[Dict[str, Any]]:
        """Return lightweight inventory summary for UI."""
        return [
            {
                "sku": sku,
                "title": data["title"],
                "onHand": data["onHand"],
                "threshold": data["threshold"],
                "restockAmount": data["restockAmount"],
                "price": data["price"]
            }
            for sku, data in self.inventory.items()
        ]

    # ---------------------
    # Internal helpers
    # ---------------------

    def _init_inventory(self) -> Dict[str, Dict[str, Any]]:
        """Seed inventory from configuration payload (must be provided)."""
        config_inventory = self.config.get("inventory")
        if not config_inventory:
            raise ValueError("Inventory configuration missing. Ensure ontology provides Inventory data or pass it explicitly.")

        inventory: Dict[str, Dict[str, Any]] = {}
        for idx, item in enumerate(config_inventory):
            sku = str(item.get("sku") or f"SKU-{idx + 1:03d}")
            inventory[sku] = {
                "sku": sku,
                "title": item.get("title", sku),
                "price": float(item.get("price", 10.0)),
                "onHand": int(item.get("onHand", 20)),
                "threshold": int(item.get("threshold", 5)),
                "restockAmount": int(item.get("restockAmount", 10))
            }
        return inventory

    def _choose_inventory_item(self) -> Optional[Dict[str, Any]]:
        """Select an inventory item, weighted by current availability."""
        if not self.inventory:
            return None
        items = list(self.inventory.values())
        weights = [max(item["onHand"], 1) for item in items]
        pick = random.choices(items, weights=weights, k=1)[0]
        return pick

    def _process_pending_restocks(self):
        """Process pending restock deliveries that have arrived."""
        delivered = []
        for sku, order in self.pending_restocks.items():
            if self.current_tick >= order["delivery_tick"]:
                # Restock has arrived!
                item = self.inventory[sku]
                item["onHand"] += order["amount"]
                self.metrics["restocks"] += 1
                
                self.add_event({
                    "type": "inventory",
                    "category": "restock",
                    "sku": sku,
                    "title": item["title"],
                    "delta": order["amount"],
                    "remaining": item["onHand"],
                    "orderedTick": order["ordered_tick"]
                })
                
                # Supplier confirms delivery
                self.add_event({
                    "type": "message",
                    "from": "Supplier",
                    "to": "EmployeeAgent",
                    "topic": "restock_done",
                    "content": f"Delivered {order['amount']} units of '{item['title']}'",
                    "sku": sku,
                    "quantity": order["amount"]
                })
                
                delivered.append(sku)
        
        # Remove delivered restocks
        for sku in delivered:
            del self.pending_restocks[sku]
    
    def _handle_purchase_event(self, event: Dict[str, Any]):
        """Handle purchase observation: update inventory + metrics."""
        item = self._choose_inventory_item()
        if item is None:
            logger.debug("No inventory configured; skipping purchase handling")
            self.metrics["purchases"] += 1
            return

        sku = item["sku"]
        before = item["onHand"]

        if before > 0:
            item["onHand"] -= 1
            self.metrics["purchases"] += 1
            self.metrics["revenue"] = round(self.metrics["revenue"] + item["price"], 2)

            self.add_event({
                "type": "inventory",
                "category": "purchase",
                "sku": sku,
                "title": item["title"],
                "delta": -1,
                "remaining": item["onHand"]
            })

            # Check if restock needed and not already pending
            if item["onHand"] <= item["threshold"] and sku not in self.pending_restocks:
                restock_qty = item["restockAmount"]
                delivery_delay = 3  # Restocks take 3 ticks to arrive
                delivery_tick = self.current_tick + delivery_delay
                
                # Place restock order (won't arrive until delivery_tick)
                self.pending_restocks[sku] = {
                    "amount": restock_qty,
                    "delivery_tick": delivery_tick,
                    "ordered_tick": self.current_tick
                }
                
                self.add_event({
                    "type": "inventory",
                    "category": "restock_ordered",
                    "sku": sku,
                    "title": item["title"],
                    "delta": restock_qty,
                    "deliveryTick": delivery_tick,
                    "ticksRemaining": delivery_delay
                })
                
                # Employee sends restock order message to supplier
                self.add_event({
                    "type": "message",
                    "from": "EmployeeAgent",
                    "to": "Supplier",
                    "topic": "restock_request",
                    "content": f"Order {restock_qty} units of '{item['title']}'",
                    "sku": sku,
                    "quantity": restock_qty
                })
        else:
            self.metrics["stockouts"] += 1
            self.add_event({
                "type": "inventory",
                "category": "stockout",
                "sku": sku,
                "title": item["title"],
                "remaining": before
            })
