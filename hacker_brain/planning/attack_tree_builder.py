"""
Attack Tree Builder - بناء شجرة هجوم
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class AttackNode:
    """عقدة في شجرة الهجوم"""
    name: str
    children: List['AttackNode'] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

class AttackTreeBuilder:
    """يبني شجرة هجوم من وصف الهدف"""
    
    def build_for_target(self, target_type: str, defenses: List[str]) -> AttackNode:
        """بناء شجرة هجوم مخصصة للهدف"""
        root = AttackNode(name=f"Compromise {target_type}")
        
        if target_type == "web_application":
            root.children = self._web_app_attacks(defenses)
        elif target_type == "network":
            root.children = self._network_attacks(defenses)
        elif target_type == "endpoint":
            root.children = self._endpoint_attacks(defenses)
        else:
            root.children = self._generic_attacks()
        
        return root
    
    def _web_app_attacks(self, defenses: List[str]) -> List[AttackNode]:
        nodes = []
        nodes.append(AttackNode("SQL Injection"))
        nodes.append(AttackNode("XSS"))
        nodes.append(AttackNode("CSRF"))
        nodes.append(AttackNode("Path Traversal"))
        if "WAF" in defenses:
            nodes.append(AttackNode("WAF Bypass", children=[
                AttackNode("Encoding"),
                AttackNode("SQLi with Comments")
            ]))
        return nodes
    
    def _network_attacks(self, defenses: List[str]) -> List[AttackNode]:
        return [AttackNode("Port Scan"), AttackNode("Service Exploit"), AttackNode("MITM")]
    
    def _endpoint_attacks(self, defenses: List[str]) -> List[AttackNode]:
        return [AttackNode("Phishing"), AttackNode("Drive-by Download"), AttackNode("USB Drop")]
    
    def _generic_attacks(self) -> List[AttackNode]:
        return [AttackNode("Brute Force"), AttackNode("Social Engineering"), AttackNode("0-day")]