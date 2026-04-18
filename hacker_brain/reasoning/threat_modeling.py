"""
Threat Modeling - نمذجة التهديدات
"""

from typing import Dict, List, Optional

class ThreatModel:
    """يمثل نموذج تهديد للهدف"""
    def __init__(self, target: str, assets: List[str], threats: List[str]):
        self.target = target
        self.assets = assets
        self.threats = threats
        self.mitigations = []

class ThreatModeling:
    """يبني نماذج تهديد للأهداف"""
    
    @staticmethod
    def for_web_app(url: str, tech_stack: List[str]) -> ThreatModel:
        threats = ["SQL Injection", "XSS", "CSRF", "IDOR", "SSRF"]
        assets = ["Database", "User PII", "Session Tokens", "Admin Panel"]
        model = ThreatModel(url, assets, threats)
        model.mitigations = ["WAF", "Input Validation", "CSP", "Rate Limiting"]
        return model
    
    @staticmethod
    def for_network(ip_range: str) -> ThreatModel:
        threats = ["Port Scan", "Service Exploit", "MITM", "DoS"]
        assets = ["Sensitive Data", "Credentials", "Internal Services"]
        return ThreatModel(ip_range, assets, threats)