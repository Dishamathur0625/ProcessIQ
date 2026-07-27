import uuid
from typing import Dict, Any, List
from datetime import datetime

class DatasetVersionNode:
    """
    Represents a specific state of the dataset in the version graph.
    """
    def __init__(self, fingerprint: str, quality_scores: Dict[str, float]):
        self.version_id = str(uuid.uuid4())
        self.fingerprint = fingerprint
        self.quality_scores = quality_scores
        self.timestamp = datetime.utcnow().isoformat() + "Z"

class DatasetVersionEdge:
    """
    Represents an operation that transitions the dataset from one version to the next.
    """
    def __init__(self, source_version_id: str, target_version_id: str, operation_name: str, audit_hash: str):
        self.source_version_id = source_version_id
        self.target_version_id = target_version_id
        self.operation_name = operation_name
        self.audit_hash = audit_hash
        self.timestamp = datetime.utcnow().isoformat() + "Z"

class DatasetVersionGraph:
    """
    Maintains the exact lineage (V1 -> Op -> V2) for reproducibility and auditing.
    """
    def __init__(self):
        self.nodes: Dict[str, DatasetVersionNode] = {}
        self.edges: List[DatasetVersionEdge] = []
        self.current_version_id: str = None
        
    def add_initial_version(self, fingerprint: str, quality_scores: Dict[str, float]) -> str:
        node = DatasetVersionNode(fingerprint, quality_scores)
        self.nodes[node.version_id] = node
        self.current_version_id = node.version_id
        return node.version_id
        
    def record_transition(self, new_fingerprint: str, new_quality_scores: Dict[str, float], operation_name: str, audit_hash: str) -> str:
        if not self.current_version_id:
            raise ValueError("Graph has no initial version. Call add_initial_version first.")
            
        new_node = DatasetVersionNode(new_fingerprint, new_quality_scores)
        self.nodes[new_node.version_id] = new_node
        
        edge = DatasetVersionEdge(
            source_version_id=self.current_version_id,
            target_version_id=new_node.version_id,
            operation_name=operation_name,
            audit_hash=audit_hash
        )
        self.edges.append(edge)
        
        self.current_version_id = new_node.version_id
        return new_node.version_id
        
    def get_lineage(self) -> List[Dict[str, Any]]:
        lineage = []
        for edge in self.edges:
            lineage.append({
                "from_version": edge.source_version_id,
                "to_version": edge.target_version_id,
                "operation": edge.operation_name,
                "audit_hash": edge.audit_hash,
                "timestamp": edge.timestamp
            })
        return lineage
