"""
Decision Engine - محرك اتخاذ القرارات
"""

import logging
from typing import Dict, Any, List
from .attacker_mindset import AttackerMindset, RiskLevel

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    محرك القرارات يقرر الإجراء التالي بناءً على التحليل
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.mindset = AttackerMindset(simulation_mode)
        self.decision_history: List[Dict] = []
    
    def decide_next_action(self, context: Dict) -> Dict:
        """
        اتخاذ القرار التالي
        """
        # تحليل الوضع الحالي
        analysis = self.mindset.think_before_act("next_action", context)
        
        decision = {
            "action": "proceed" if analysis.success_probability > 0.6 else "reconsider",
            "risk_level": analysis.risk_level.value,
            "confidence": analysis.success_probability,
            "suggested_alternative": analysis.alternatives[0] if analysis.alternatives else None,
            "fallback": analysis.fallback_plan,
            "reasoning": f"Efficiency={analysis.efficiency_score:.2f}, Stealth={analysis.stealth_score:.2f}"
        }
        
        self.decision_history.append(decision)
        logger.info(f"Decision: {decision['action']} (risk={decision['risk_level']})")
        return decision
    
    def get_history(self) -> List[Dict]:
        return self.decision_history