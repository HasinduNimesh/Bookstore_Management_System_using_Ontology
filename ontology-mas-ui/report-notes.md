# Report Notes: Ontology-Driven MAS with HMM Inference

## Overview

This document connects the theoretical concepts of **Multi-Agent Systems (MAS)**, **Hidden Markov Models (HMM)**, and **Ontologies** as implemented in the Ontology-Driven MAS Simulator.

## 1. Multi-Agent Systems (MAS)

### Definition
A Multi-Agent System consists of multiple interacting intelligent agents operating in a shared environment to achieve individual or collective goals.

### Implementation in Our System

#### Agent Types
1. **CustomerAgent**
   - **State**: Hidden emotional state (Happy, Neutral, Unhappy)
   - **Behavior**: Moves randomly on grid, emits observations based on hidden state
   - **Observations**: Purchase, Complaint, Silence
   - **Transition**: State evolves according to Markov transition matrix

2. **ServiceAgent**
   - **Role**: Observes customer behaviors and infers hidden states
   - **Inference**: Uses Viterbi algorithm (HMM) to decode observation sequences
   - **Action**: Provides insights for service optimization

#### Mesa Framework
- **RandomActivation**: Agents act in random order each step
- **MultiGrid**: 2D grid environment where agents can occupy overlapping cells
- **DataCollector**: Tracks metrics (purchases, complaints, state distributions)
- **Scheduler**: Coordinates agent activation and environment updates

### MAS Characteristics in Our Implementation
- **Autonomy**: Each agent decides its actions independently
- **Interaction**: Agents share environment, service agents observe customers
- **Emergent Behavior**: Aggregate metrics emerge from individual agent interactions
- **Distributed Problem-Solving**: No central controller; agents operate concurrently

## 2. Hidden Markov Models (HMM)

### Definition
An HMM models a system with:
- **Hidden States** (S): Not directly observable (e.g., customer emotions)
- **Observations** (O): Observable events (e.g., purchase, complaint)
- **Transition Probabilities** (A): P(next_state | current_state)
- **Emission Probabilities** (B): P(observation | state)
- **Initial State Distribution** (π): P(initial_state)

### Implementation in Our System

#### Model Parameters
```python
states = ['Happy', 'Neutral', 'Unhappy']
observations = ['Purchase', 'Complaint', 'Silence']

# Transition Matrix (A)
A = [
  [0.7, 0.2, 0.1],  # Happy → [Happy, Neutral, Unhappy]
  [0.3, 0.5, 0.2],  # Neutral → ...
  [0.1, 0.3, 0.6]   # Unhappy → ...
]

# Emission Matrix (B)
B = [
  [0.6, 0.1, 0.3],  # Happy → [Purchase, Complaint, Silence]
  [0.3, 0.2, 0.5],  # Neutral → ...
  [0.1, 0.6, 0.3]   # Unhappy → ...
]

# Initial Distribution (π)
pi = [0.4, 0.4, 0.2]  # Higher probability of starting Happy/Neutral
```

#### Viterbi Algorithm
The `HMMInference` class uses the Viterbi algorithm to find the most likely sequence of hidden states given a sequence of observations.

**Algorithm Steps**:
1. **Initialization**: Compute initial probabilities for each state
   ```
   δ[0][s] = π[s] × B[s][obs[0]]
   ```

2. **Recursion**: For each time step, compute:
   ```
   δ[t][s] = max_s' (δ[t-1][s'] × A[s'][s]) × B[s][obs[t]]
   ```

3. **Termination**: Find the most likely final state
   ```
   best_final_state = argmax(δ[T])
   ```

4. **Backtracking**: Trace back to reconstruct the full state sequence

**Output**: Most likely state sequence + log-probability score

### Why HMM for Customer Service?
- **Hidden States**: Customer satisfaction is internal and not directly observable
- **Observations**: Actions (purchases, complaints) provide indirect evidence
- **Temporal Dynamics**: Satisfaction evolves over time based on experiences
- **Inference**: Service agents can estimate satisfaction to optimize interactions

## 3. Ontologies

### Definition
An ontology is a formal representation of knowledge as a set of concepts (classes), relationships (properties), and individuals (instances) within a domain.

### Implementation in Our System

#### Ontology Components
1. **Classes**
   - `Customer`: Represents customer agents
   - `ServiceAgent`: Represents service agents
   - `Observation`: Represents observable events
   - `State`: Represents hidden emotional states
   - `Seat`: Represents grid positions

2. **Properties**
   - **Object Properties**: Links between individuals (e.g., `hasState`, `observedBy`)
   - **Data Properties**: Attribute values (e.g., `hasName`, `timestamp`, `logProb`)

3. **Instances**
   - Created dynamically during simulation (e.g., `Customer_0`, `Observation_42`)

#### RDF/OWL Format
```turtle
@prefix : <http://example.org/mas#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Customer rdf:type rdfs:Class .
:ServiceAgent rdf:type rdfs:Class .
:Observation rdf:type rdfs:Class .
:State rdf:type rdfs:Class .

:hasState rdf:type rdf:Property ;
  rdfs:domain :Customer ;
  rdfs:range :State .

:Customer_0 rdf:type :Customer ;
  :hasState :Happy ;
  :position "5,7" .
```

#### GraphManager Operations
- **Load**: Parse RDF/OWL files into RDFlib graph
- **Query**: Execute SPARQL queries to retrieve instances/properties
- **Update**: Add new triples during simulation
- **Diff**: Track changes between snapshots for validation
- **Serialize**: Export ontology in TTL/XML/JSON-LD formats

### Why Ontologies for MAS?
- **Shared Vocabulary**: Agents understand common concepts
- **Semantic Reasoning**: Infer implicit relationships (e.g., if Customer_0 hasState Happy, then Customer_0 is Satisfied)
- **Interoperability**: Standard formats (RDF/OWL) enable integration with other systems
- **Validation**: Check consistency (e.g., a Customer can't have two states simultaneously)
- **Provenance**: Track how agent states and observations evolved

## 4. System Integration

### How MAS + HMM + Ontology Work Together

#### Simulation Loop (Each Tick)
1. **Agent Activation** (MAS)
   - CustomerAgent: Select next hidden state (sample from transition matrix)
   - CustomerAgent: Emit observation (sample from emission matrix)
   - ServiceAgent: Collect observations from nearby customers

2. **HMM Inference**
   - ServiceAgent: Run Viterbi on observation sequence
   - ServiceAgent: Infer most likely hidden state sequence
   - ServiceAgent: Compute log-probability confidence score

3. **Ontology Update**
   - Create RDF triples for new observations:
     ```turtle
     :Observation_42 rdf:type :Observation ;
       :agent :Customer_0 ;
       :type "Purchase" ;
       :timestamp "12" .
     ```
   - Update customer state triples:
     ```turtle
     :Customer_0 :hasState :Happy ;
       :inferredLogProb "-2.34" .
     ```
   - Store in RDFlib graph for SPARQL queries

4. **Event Broadcasting** (WebSocket)
   - EventBus publishes events: `{"type": "observation", "agent": 0, "obs": "Purchase"}`
   - Frontend receives real-time updates for visualization

5. **Metrics Collection**
   - DataCollector aggregates: total purchases, complaints, state distributions
   - Stored in JSON for export

### Data Flow Diagram
```
┌─────────────┐
│ Ontology    │ ← Load RDF/OWL file
│ (RDFlib)    │
└──────┬──────┘
       │
       │ Provides classes/properties
       ▼
┌─────────────┐     ┌─────────────┐
│ CustomerAgent│────►│ Observations│ (Purchase, Complaint, Silence)
│ (Mesa)      │     └──────┬──────┘
└─────────────┘            │
       │                   │ Feed into HMM
       │ Hidden state      ▼
       │              ┌─────────────┐
       └─────────────►│ HMM (Viterbi│
                      │  Algorithm) │
                      └──────┬──────┘
                             │ Inferred states + log-prob
                             ▼
                      ┌─────────────┐
                      │ Ontology    │
                      │ Update      │ ← Add triples
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │ WebSocket   │
                      │ (EventBus)  │
                      └──────┬──────┘
                             │
                             ▼
                      ┌─────────────┐
                      │ React UI    │ (Grid, Charts, Logs)
                      └─────────────┘
```

## 5. Research Significance

### Novel Contributions
1. **Ontology-Driven MAS**: Agents use formal ontologies for shared understanding
2. **HMM Integration**: Probabilistic state inference in agent reasoning
3. **Real-Time Visualization**: WebSocket streaming of agent states and ontology updates
4. **Validation Framework**: Diff tracking for ontology consistency checks

### Potential Applications
- **Customer Service**: Infer satisfaction from behavior, optimize support
- **Healthcare**: Monitor patient states from observable symptoms
- **Smart Cities**: Track citizen sentiment from interactions with urban systems
- **E-commerce**: Predict user intent from browsing/purchase patterns

### Evaluation Metrics
- **HMM Accuracy**: Compare inferred vs. true hidden states (if ground truth available)
- **Ontology Consistency**: Check for logical contradictions (OWL reasoner)
- **System Performance**: Simulation speed, WebSocket latency, memory usage
- **Emergent Behavior**: Analyze aggregate patterns (e.g., complaint clusters)

## 6. Implementation Highlights

### Key Code Patterns

#### Agent Definition (Mesa)
```python
class CustomerAgent(Agent):
    def __init__(self, unique_id, model, state, hmm):
        super().__init__(unique_id, model)
        self.hidden_state = state
        self.hmm = hmm
    
    def step(self):
        # Transition to next state
        self.hidden_state = self.hmm.sample_next_state(self.hidden_state)
        # Emit observation
        obs = self.hmm.sample_observation(self.hidden_state)
        # Broadcast event
        self.model.events.append({'agent': self.unique_id, 'obs': obs})
```

#### HMM Inference
```python
class HMMInference:
    def viterbi(self, observations):
        V = [{}]  # Viterbi matrix
        path = {}  # Backpointers
        
        # Initialization
        for s in self.states:
            V[0][s] = self.pi[s] * self.B[s][observations[0]]
        
        # Recursion
        for t in range(1, len(observations)):
            V.append({})
            for s in self.states:
                max_prob = max(V[t-1][s0] * self.A[s0][s] for s0 in self.states)
                V[t][s] = max_prob * self.B[s][observations[t]]
        
        # Termination + backtracking
        best_path = self._backtrack(V, path)
        return best_path, max(V[-1].values())
```

#### Ontology Update
```python
class GraphManager:
    def apply_updates(self, triples):
        for subj, pred, obj in triples:
            self.graph.add((URIRef(subj), URIRef(pred), Literal(obj)))
    
    def diff(self):
        added = self.graph - self.previous_snapshot
        removed = self.previous_snapshot - self.graph
        return list(added), list(removed)
```

## 7. Future Enhancements

### Potential Extensions
1. **SWRL Rules**: Define logical rules for automatic state inference
   ```
   Customer(?c) ∧ hasObservation(?c, "Complaint") → hasState(?c, "Unhappy")
   ```

2. **Reinforcement Learning**: Train service agents to optimize actions (e.g., offer discount)

3. **Multi-Modal Observations**: Combine behavior, sentiment analysis, context

4. **Distributed Simulation**: Scale to thousands of agents with distributed computing

5. **Explainable AI**: Provide natural language justifications for inferred states

6. **Active Learning**: Service agents query customers when uncertain (high entropy)

## 8. Conclusion

This system demonstrates a **principled integration** of:
- **MAS** for modeling autonomous interacting agents
- **HMM** for probabilistic reasoning under uncertainty
- **Ontologies** for semantic knowledge representation and interoperability

The result is a flexible, extensible platform for researching agent-based systems with formal knowledge structures and statistical inference capabilities.

---

**Document Version**: 1.0  
**Last Updated**: 2025  
**Authors**: BMS Project Team  
**License**: MIT
