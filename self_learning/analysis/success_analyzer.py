"""
Success Analyzer - تحليل أسباب نجاح الهجوم لتعزيز التقنيات الناجحة
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SuccessAnalysis:
    """تحليل نجاح الهجوم"""
    key_factors: List[str]
    technique_effectiveness: float
    recommendations: List[str]
    reusable_patterns: List[str]


class SuccessAnalyzer:
    """
    محلل النجاح - يستخرج الدروس المستفادة من الهجمات الناجحة
    """
    
    def __init__(self):
        self.success_patterns = []
        logger.info("SuccessAnalyzer initialized")
    
    def analyze_success(self, successful_attempt: Dict) -> SuccessAnalysis:
        """
        تحليل محاولة ناجحة
        
        Args:
            successful_attempt: بيانات المحاولة الناجحة
        """
        technique = successful_attempt.get("technique", "")
        context = successful_attempt.get("context", {})
        result = successful_attempt.get("result", {})
        
        key_factors = []
        recommendations = []
        reusable_patterns = []
        
        # تحديد عوامل النجاح
        if "bypassed" in str(result):
            key_factors.append("Bypassed security controls")
            reusable_patterns.append("Bypass technique can be reused on similar targets")
        
        if "admin" in str(result) or "root" in str(result):
            key_factors.append("Achieved elevated privileges")
            reusable_patterns.append("Privilege escalation chain is effective")
        
        if "persistence" in str(result):
            key_factors.append("Established persistent access")
            reusable_patterns.append("Persistence method works on this OS version")
        
        if context.get("defenses"):
            key_factors.append(f"Successfully evaded {len(context['defenses'])} defenses")
        
        # تقييم فعالية التقنية
        effectiveness = 0.8  # افتراضي
        if "time" in result:
            effectiveness = min(1.0, effectiveness + 0.1)
        if "detected" in str(result):
            effectiveness = max(0.3, effectiveness - 0.2)
        
        # توصيات
        recommendations = [
            f"Use {technique} as primary attack vector for similar targets",
            "Document the exact steps for future reference",
            "Automate this technique for faster execution",
        ]
        
        if "bypass" in technique.lower():
            recommendations.append("Combine with other bypasses for layered evasion")
        
        return SuccessAnalysis(
            key_factors=key_factors,
            technique_effectiveness=effectiveness,
            recommendations=recommendations,
            reusable_patterns=reusable_patterns,
        )
    
    def extract_best_practices(self, successes: List[Dict]) -> List[str]:
        """استخراج أفضل الممارسات من عدة نجاحات"""
        practices = set()
        for success in successes:
            analysis = self.analyze_success(success)
            for pattern in analysis.reusable_patterns:
                practices.add(pattern)
        return list(practices)


# مثال
if __name__ == "__main__":
    analyzer = SuccessAnalyzer()
    
    success = {
        "technique": "process_hollowing",
        "context": {"defenses": ["CrowdStrike"]},
        "result": {"status": "success", "bypassed": True, "privilege": "system"}
    }
    
    analysis = analyzer.analyze_success(success)
    print(f"Key factors: {analysis.key_factors}")
    print(f"Effectiveness: {analysis.technique_effectiveness}")
    print(f"Reusable patterns: {analysis.reusable_patterns}")