"""GraphManager: RDF/OWL ontology loading, querying, and diff utilities."""
from typing import Dict, List, Optional, Set, Tuple, Any
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal  # type: ignore[import-not-found]
from rdflib.namespace import FOAF  # type: ignore[import-not-found]
import logging

logger = logging.getLogger(__name__)

class GraphManager:
    def __init__(self):
        self.graph: Optional[Graph] = None
        self.initial_graph: Optional[Graph] = None
        self.namespaces: Dict[str, str] = {}
        
    def load_graph(self, path: Optional[str] = None, ttl: Optional[str] = None, 
                   owl: Optional[str] = None) -> Dict[str, Any]:
        """Load ontology from file path or string content."""
        self.graph = Graph()
        # Narrow Optional for type checker
        assert self.graph is not None
        graph: Graph = self.graph
        
        try:
            if path:
                graph.parse(path)
                logger.info(f"Loaded ontology from {path}")
            elif ttl:
                graph.parse(data=ttl, format="turtle")
                logger.info("Loaded ontology from TTL string")
            elif owl:
                graph.parse(data=owl, format="xml")
                logger.info("Loaded ontology from OWL string")
            else:
                raise ValueError("Must provide path, ttl, or owl")
            
            # Store initial state for diff
            self.initial_graph = Graph()
            assert self.initial_graph is not None
            initial_graph: Graph = self.initial_graph
            for triple in graph:
                initial_graph.add(triple)
            
            # Extract namespaces
            self.namespaces = {prefix: str(ns) for prefix, ns in graph.namespaces()}
            
            return self.summary()
        except Exception as e:
            logger.error(f"Failed to load graph: {e}")
            raise
    
    def summary(self) -> Dict[str, Any]:
        """Return graph statistics."""
        if not self.graph:
            return {"error": "No graph loaded"}
        # Narrow Optional
        assert self.graph is not None
        graph: Graph = self.graph
        
        # Count classes and instances
        classes = list(graph.subjects(RDF.type, OWL.Class)) + \
                  list(graph.subjects(RDF.type, RDFS.Class))
        class_count = len(set(classes))
        
        # Count instances (things that are typed)
        instances = set()
        for s, p, o in graph.triples((None, RDF.type, None)):
            if o not in [OWL.Class, RDFS.Class, OWL.ObjectProperty, OWL.DatatypeProperty]:
                instances.add(s)
        instance_count = len(instances)
        
        # Count properties
        obj_props = list(graph.subjects(RDF.type, OWL.ObjectProperty))
        data_props = list(graph.subjects(RDF.type, OWL.DatatypeProperty))
        
        # Top classes by instance count
        class_instances: Dict[str, int] = {}
        for cls in classes:
            count = len(list(graph.subjects(RDF.type, cls)))
            if count > 0:
                class_instances[self._short_name(cls)] = count
        
        top_classes = sorted(class_instances.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "namespaces": self.namespaces,
            "classCount": class_count,
            "instanceCount": instance_count,
            "objectProperties": len(obj_props),
            "dataProperties": len(data_props),
            "tripleCount": len(graph),
            "topClasses": dict(top_classes)
        }
    
    def query(self, sparql: str) -> List[Dict[str, Any]]:
        """Execute SPARQL query."""
        if not self.graph:
            return []
        assert self.graph is not None
        graph: Graph = self.graph
        
        try:
            results = graph.query(sparql)
            # Use row.asdict() to avoid indexing by Variable for type checker
            return [{str(k): str(v) for k, v in getattr(row, "asdict")().items()} for row in results]
        except Exception as e:
            logger.error(f"SPARQL query failed: {e}")
            return []
    
    def get_instances(self, class_name: str) -> List[Dict[str, Any]]:
        """Get all instances of a class with their properties."""
        if not self.graph:
            return []
        assert self.graph is not None
        graph: Graph = self.graph
        
        # Try to resolve class URI
        class_uri = self._resolve_uri(class_name)
        
        instances = []
        for subj in graph.subjects(RDF.type, class_uri):
            props = {}
            for pred, obj in graph.predicate_objects(subj):
                pred_name = self._short_name(pred)
                if pred_name not in props:
                    props[pred_name] = []
                props[pred_name].append(str(obj))
            
            instances.append({
                "uri": str(subj),
                "name": self._short_name(subj),
                "properties": props
            })
        
        return instances
    
    def apply_updates(self, triples: List[Tuple[str, str, str, bool]]) -> Dict[str, int]:
        """Apply triple updates (add/remove).
        
        Args:
            triples: List of (subject, predicate, object, is_add)
        """
        if not self.graph:
            return {"added": 0, "removed": 0}
        assert self.graph is not None
        graph: Graph = self.graph
        
        added = 0
        removed = 0
        
        for subj_str, pred_str, obj_str, is_add in triples:
            try:
                subj = self._resolve_uri(subj_str)
                pred = self._resolve_uri(pred_str)
                
                # Try to parse object as URI or literal
                try:
                    obj = self._resolve_uri(obj_str)
                except:
                    obj = Literal(obj_str)
                
                if is_add:
                    graph.add((subj, pred, obj))
                    added += 1
                else:
                    graph.remove((subj, pred, obj))
                    removed += 1
            except Exception as e:
                logger.error(f"Failed to apply triple update: {e}")
        
        return {"added": added, "removed": removed}
    
    def diff(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Compute diff between current graph and initial graph."""
        if not self.graph or not self.initial_graph:
            return {"added": [], "removed": []}
        assert self.graph is not None and self.initial_graph is not None
        graph: Graph = self.graph
        initial_graph: Graph = self.initial_graph
        
        current_triples = set(graph)
        initial_triples = set(initial_graph)
        
        added = [
            (str(s), str(p), str(o))
            for s, p, o in (current_triples - initial_triples)
        ]
        removed = [
            (str(s), str(p), str(o))
            for s, p, o in (initial_triples - current_triples)
        ]
        
        return {"added": added, "removed": removed}
    
    def serialize(self, format: str = "turtle") -> str:
        """Serialize graph to string."""
        if not self.graph:
            return ""
        assert self.graph is not None
        graph: Graph = self.graph
        return graph.serialize(format=format)
    
    def _resolve_uri(self, name: str) -> URIRef:
        """Resolve a short name or full URI to URIRef."""
        if name.startswith("http://") or name.startswith("https://"):
            return URIRef(name)
        
        # Try with namespaces
        if ":" in name:
            prefix, local = name.split(":", 1)
            if prefix in self.namespaces:
                return URIRef(self.namespaces[prefix] + local)
        
        # Default to first namespace or create new
        if self.namespaces:
            default_ns = list(self.namespaces.values())[0]
            return URIRef(default_ns + name)
        
        return URIRef(f"http://example.org/{name}")
    
    def _short_name(self, uri: Any) -> str:
        """Convert URI to short name using namespaces."""
        uri_str = str(uri)
        
        for prefix, ns in self.namespaces.items():
            if uri_str.startswith(ns):
                return f"{prefix}:{uri_str[len(ns):]}"
        
        # Return last part of URI
        if "#" in uri_str:
            return uri_str.split("#")[-1]
        elif "/" in uri_str:
            return uri_str.split("/")[-1]
        
        return uri_str
