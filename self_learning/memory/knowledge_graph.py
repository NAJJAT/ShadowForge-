"""
Knowledge Graph - رسم بياني للمعرفة يربط بين التقنيات والثغرات والدفاعات
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# محاولة استيراد Neo4j (اختياري)
try:
    from neo4j import GraphDatabase
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    logger.warning("Neo4j not installed. Using in-memory graph.")


@dataclass
class Node:
    """عقدة في الرسم البياني"""
    id: str
    type: str  # technique, vulnerability, defense, target
    properties: Dict = field(default_factory=dict)


@dataclass
class Edge:
    """علاقة بين عقدتين"""
    source: str
    target: str
    relationship: str  # bypasses, mitigates, targets, etc.
    weight: float = 1.0


class SimpleKnowledgeGraph:
    """رسم بياني بسيط في الذاكرة"""
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        logger.info("SimpleKnowledgeGraph initialized")
    
    def add_node(self, node_id: str, node_type: str, properties: Dict = None) -> Node:
        node = Node(id=node_id, type=node_type, properties=properties or {})
        self.nodes[node_id] = node
        return node
    
    def add_edge(self, source: str, target: str, relationship: str, weight: float = 1.0) -> Edge:
        edge = Edge(source=source, target=target, relationship=relationship, weight=weight)
        self.edges.append(edge)
        return edge
    
    def get_related(self, node_id: str, relationship: str = None) -> List[Node]:
        """الحصول على العقد المرتبطة بعقدة معينة"""
        related = []
        for edge in self.edges:
            if edge.source == node_id:
                if relationship is None or edge.relationship == relationship:
                    if edge.target in self.nodes:
                        related.append(self.nodes[edge.target])
        return related
    
    def get_path(self, start: str, end: str, max_depth: int = 3) -> Optional[List[str]]:
        """البحث عن مسار بين عقدتين (BFS)"""
        from collections import deque
        queue = deque([(start, [start])])
        visited = set()
        
        while queue:
            node, path = queue.popleft()
            if node == end:
                return path
            if len(path) > max_depth:
                continue
            visited.add(node)
            for edge in self.edges:
                if edge.source == node and edge.target not in visited:
                    queue.append((edge.target, path + [edge.target]))
        return None
    
    def to_dict(self) -> Dict:
        return {
            "nodes": {nid: {"type": n.type, "props": n.properties} for nid, n in self.nodes.items()},
            "edges": [(e.source, e.target, e.relationship) for e in self.edges],
        }


class Neo4jGraph:
    """رسم بياني باستخدام Neo4j (للتخزين الدائم)"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        if not HAS_NEO4J:
            raise ImportError("Neo4j driver not installed. Install with: pip install neo4j")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info("Neo4jGraph initialized")
    
    def close(self):
        self.driver.close()
    
    def add_node(self, node_id: str, node_type: str, properties: Dict = None):
        with self.driver.session() as session:
            props = properties or {}
            props["id"] = node_id
            props["type"] = node_type
            session.run(
                f"MERGE (n:{node_type} {{id: $id}}) SET n = $props",
                id=node_id, props=props
            )
    
    def add_edge(self, source: str, target: str, relationship: str, weight: float = 1.0):
        with self.driver.session() as session:
            session.run(
                f"MATCH (a {{id: $source}}), (b {{id: $target}}) MERGE (a)-[r:{relationship}]->(b) SET r.weight = $weight",
                source=source, target=target, weight=weight
            )


class KnowledgeGraph:
    """واجهة موحدة لرسم المعرفة"""
    
    def __init__(self, use_neo4j: bool = False, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.use_neo4j = use_neo4j and HAS_NEO4J and not simulation_mode
        
        if self.use_neo4j:
            self.graph = Neo4jGraph()
        else:
            self.graph = SimpleKnowledgeGraph()
        
        # تهيئة بعض العقد الأساسية
        self._init_base_nodes()
        
        logger.info(f"KnowledgeGraph initialized (using {type(self.graph).__name__})")
    
    def _init_base_nodes(self):
        """إضافة عقد أساسية للمعرفة"""
        self.graph.add_node("sql_injection", "vulnerability", {"cwe": "CWE-89", "severity": "critical"})
        self.graph.add_node("xss", "vulnerability", {"cwe": "CWE-79", "severity": "medium"})
        self.graph.add_node("lfi", "vulnerability", {"cwe": "CWE-98", "severity": "high"})
        self.graph.add_node("command_injection", "vulnerability", {"cwe": "CWE-78", "severity": "critical"})
        
        self.graph.add_node("waf", "defense", {"type": "web_application_firewall"})
        self.graph.add_node("edr", "defense", {"type": "endpoint_detection"})
        self.graph.add_node("csp", "defense", {"type": "content_security_policy"})
        
        self.graph.add_node("union_sqli", "technique", {"type": "exploit"})
        self.graph.add_node("time_sqli", "technique", {"type": "exploit"})
        self.graph.add_node("dom_xss", "technique", {"type": "exploit"})
        
        # إضافة علاقات
        self.graph.add_edge("union_sqli", "sql_injection", "exploits")
        self.graph.add_edge("time_sqli", "sql_injection", "exploits")
        self.graph.add_edge("dom_xss", "xss", "exploits")
        self.graph.add_edge("sql_injection", "waf", "bypassed_by", weight=0.6)
        self.graph.add_edge("xss", "csp", "mitigated_by", weight=0.8)
    
    def add_experience(self, exp: Dict):
        """إضافة تجربة إلى الرسم البياني"""
        exp_id = exp.get("id", "unknown")
        self.graph.add_node(exp_id, "experience", {
            "outcome": exp.get("outcome", "unknown"),
            "timestamp": exp.get("timestamp", 0)
        })
        
        for technique in exp.get("techniques_used", []):
            self.graph.add_node(technique, "technique")
            self.graph.add_edge(exp_id, technique, "used")
        
        for defense in exp.get("defenses_encountered", []):
            self.graph.add_node(defense, "defense")
            self.graph.add_edge(exp_id, defense, "encountered")
        
        for exploit in exp.get("successful_exploits", []):
            vuln_type = exploit.get("type")
            if vuln_type:
                self.graph.add_edge(exp_id, vuln_type, "successfully_exploited")
    
    def get_recommendations(self, current_defenses: List[str]) -> List[str]:
        """توصية بتقنيات لتجاوز دفاعات معينة"""
        recommendations = []
        for defense in current_defenses:
            # البحث عن تقنيات تتجاوز هذا الدفاع
            related = self.graph.get_related(defense, "bypassed_by") if hasattr(self.graph, 'get_related') else []
            for node in related:
                if node.type == "technique" or node.id in ["union_sqli", "time_sqli", "dom_xss"]:
                    recommendations.append(node.id)
        return list(set(recommendations))


# مثال
if __name__ == "__main__":
    kg = KnowledgeGraph(use_neo4j=False, simulation_mode=True)
    
    # إضافة تجربة
    exp = {
        "id": "exp_001",
        "outcome": "success",
        "techniques_used": ["union_sqli", "time_sqli"],
        "defenses_encountered": ["waf"],
        "successful_exploits": [{"type": "sql_injection"}],
    }
    kg.add_experience(exp)
    
    # توصيات
    recs = kg.get_recommendations(["waf", "csp"])
    print(f"Recommendations: {recs}")