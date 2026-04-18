"""
Pattern Recognizer - التعرف على الأنماط عبر التجارب المتعددة
"""

import logging
from typing import Dict, List, Any
from collections import Counter

logger = logging.getLogger(__name__)


class PatternRecognizer:
    """
    يتعرف على أنماط متكررة في الهجمات الناجحة والفاشلة
    """
    
    def __init__(self):
        self.patterns = []
        logger.info("PatternRecognizer initialized")
    
    def analyze_all_missions(self, missions: List[Dict]) -> List[Dict]:
        """
        تحليل جميع المهام واستخراج الأنماط
        """
        patterns = []
        
        # نمط 1: الخوادم التي تعمل IIS غالباً تعاني من Path Traversal
        iis_missions = [m for m in missions if "IIS" in str(m.get("target_profile", {}))]
        if iis_missions:
            success_rate = sum(1 for m in iis_missions if m.get("success_rate", 0) > 0.7) / len(iis_missions)
            patterns.append({
                "pattern": "IIS servers often vulnerable to path traversal",
                "confidence": success_rate,
                "actionable": "Always test path traversal first on IIS targets"
            })
        
        # نمط 2: إعادة استخدام كلمات المرور في الشركات الصغيرة
        small_companies = [m for m in missions if m.get("target_profile", {}).get("size") == "small"]
        if small_companies:
            spray_success = sum(1 for m in small_companies if "password_spray" in m.get("techniques_used", []))
            patterns.append({
                "pattern": "Small company admins reuse passwords",
                "confidence": spray_success / len(small_companies) if small_companies else 0,
                "actionable": "Password spraying should be the first technique"
            })
        
        # نمط 3: CrowdStrike ضعيف أمام .NET in-memory execution
        cs_missions = [m for m in missions if "CrowdStrike" in str(m.get("defenses_encountered", []))]
        if cs_missions:
            net_success = sum(1 for m in cs_missions if "execute-assembly" in str(m.get("techniques_used", [])))
            patterns.append({
                "pattern": "CrowdStrike weak against in-memory .NET execution",
                "confidence": net_success / len(cs_missions) if cs_missions else 0,
                "actionable": "Use execute-assembly for CrowdStrike environments"
            })
        
        # نمط 4: أوقات الذروة (ساعات العمل) أقل اكتشافاً
        working_hours_missions = [m for m in missions if 9 <= m.get("hour", 0) <= 17]
        if working_hours_missions:
            detection_rate = sum(1 for m in working_hours_missions if m.get("detected", False)) / len(working_hours_missions)
            patterns.append({
                "pattern": "Attacks during working hours have lower detection rate",
                "confidence": 1 - detection_rate,
                "actionable": "Schedule attacks between 9 AM - 5 PM"
            })
        
        return patterns
    
    def extract_common_failure_modes(self, failures: List[Dict]) -> Dict:
        """استخراج أكثر أسباب الفشل شيوعاً"""
        causes = Counter()
        for f in failures:
            cause = f.get("failure_reason", "unknown")
            causes[cause] += 1
        return dict(causes.most_common(5))
    
    def extract_success_factors(self, successes: List[Dict]) -> Dict:
        """استخراج عوامل النجاح المشتركة"""
        factors = Counter()
        for s in successes:
            for factor in s.get("success_factors", []):
                factors[factor] += 1
        return dict(factors.most_common(5))


# مثال
if __name__ == "__main__":
    recognizer = PatternRecognizer()
    
    missions = [
        {"target_profile": {"server": "IIS", "size": "small"}, "success_rate": 0.9, "techniques_used": ["path_traversal"]},
        {"target_profile": {"server": "IIS", "size": "medium"}, "success_rate": 0.8, "techniques_used": ["path_traversal"]},
        {"target_profile": {"server": "Apache"}, "success_rate": 0.3},
        {"defenses_encountered": ["CrowdStrike"], "techniques_used": ["execute-assembly"], "success_rate": 1.0},
    ]
    
    patterns = recognizer.analyze_all_missions(missions)
    for p in patterns:
        print(f"Pattern: {p['pattern']}")
        print(f"  Confidence: {p['confidence']:.2f}")
        print(f"  Actionable: {p['actionable']}")