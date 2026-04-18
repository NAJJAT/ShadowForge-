"""
Failure Analyzer - تحليل أسباب فشل الهجوم وتقديم تحسينات
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FailureAnalysis:
    """تحليل فشل الهجوم"""
    root_cause: str
    confidence: float
    suggested_improvements: List[str]
    alternative_techniques: List[str]
    prevention_tips: List[str]


class FailureAnalyzer:
    """
    محلل الفشل - يحدد سبب فشل الهجوم ويقترح تحسينات
    
    أنواع الفشل المدعومة:
    - detected_by_av: اكتشفه برنامج مكافحة الفيروسات
    - wrong_technique: تقنية غير مناسبة للهدف
    - missing_prerequisite: نقص صلاحيات أو متطلبات
    - target_patched: الثغرة تم إصلاحها
    - opsec_failure: فشل في التخفي
    - timing_issue: توقيت غير مناسب
    """
    
    def __init__(self):
        self.failure_patterns = self._load_patterns()
        logger.info("FailureAnalyzer initialized")
    
    def _load_patterns(self) -> Dict:
        """تحميل أنماط الفشل"""
        return {
            "detected_by_av": {
                "indicators": ["detected", "quarantine", "virus", "malware", "antivirus", "blocked"],
                "improvements": [
                    "Use polymorphic encoding",
                    "Implement sleep obfuscation",
                    "Use fileless technique",
                    "Sign the payload with stolen certificate",
                ],
                "alternatives": ["PowerShell without disk", "Living-off-the-land binaries", "Macro-based attack"],
            },
            "wrong_technique": {
                "indicators": ["not vulnerable", "patched", "does not work", "failed"],
                "improvements": [
                    "Enumerate target thoroughly first",
                    "Use different exploitation technique",
                    "Check for alternative vectors",
                ],
                "alternatives": ["Try different vulnerability class", "Use social engineering instead"],
            },
            "missing_prerequisite": {
                "indicators": ["access denied", "permission", "requires admin", "insufficient privileges"],
                "improvements": [
                    "Perform privilege escalation first",
                    "Use different initial access method",
                    "Target different user account",
                ],
                "alternatives": ["Phishing for higher privileges", "Exploit misconfigured service"],
            },
            "target_patched": {
                "indicators": ["patch", "update", "fixed", "version"],
                "improvements": [
                    "Find newer vulnerability in same component",
                    "Try different attack surface",
                    "Downgrade attack (if possible)",
                ],
                "alternatives": ["0-day research", "Configuration issue exploitation"],
            },
            "opsec_failure": {
                "indicators": ["detected", "alert", "incident", "honeypot"],
                "improvements": [
                    "Increase stealth (more proxies, tor, VPN chain)",
                    "Reduce scanning speed",
                    "Use less known tools",
                    "Mimic legitimate traffic",
                ],
                "alternatives": ["Wait longer between actions", "Use different infrastructure"],
            },
            "timing_issue": {
                "indicators": ["timeout", "slow", "rate limit", "cooldown"],
                "improvements": [
                    "Increase delay between requests",
                    "Use distributed scanning",
                    "Schedule during off-hours",
                ],
                "alternatives": ["Use asynchronous techniques", "Lower request rate"],
            },
        }
    
    def analyze_failure(self, failed_attempt: Dict) -> FailureAnalysis:
        """
        تحليل محاولة فاشلة
        
        Args:
            failed_attempt: بيانات المحاولة الفاشلة
                {
                    "technique": "sql_injection",
                    "error": "detected by WAF",
                    "context": {...}
                }
        
        Returns:
            FailureAnalysis: تحليل الفشل
        """
        error_msg = failed_attempt.get("error", "").lower()
        technique = failed_attempt.get("technique", "")
        
        # تحديد السبب الجذري
        root_cause = "unknown"
        best_match = None
        best_score = 0
        
        for cause, pattern in self.failure_patterns.items():
            score = sum(1 for ind in pattern["indicators"] if ind in error_msg)
            if score > best_score:
                best_score = score
                best_match = cause
        
        if best_match:
            root_cause = best_match
            pattern = self.failure_patterns[best_match]
            improvements = pattern["improvements"]
            alternatives = pattern["alternatives"]
        else:
            # سبب غير معروف
            improvements = [
                "Gather more information about target",
                "Try basic troubleshooting",
                "Consult known techniques for similar targets",
            ]
            alternatives = ["Research new techniques", "Use different toolset"]
        
        # إضافة تحسينات خاصة بالتقنية
        if "sql" in technique.lower():
            improvements.append("Try different SQL injection technique (boolean/time-based)")
        elif "xss" in technique.lower():
            improvements.append("Use DOM-based XSS or different payload encoding")
        elif "edr" in error_msg:
            improvements.append("Use direct syscalls instead of API calls")
        
        return FailureAnalysis(
            root_cause=root_cause,
            confidence=min(0.9, best_score / 5) if best_score > 0 else 0.3,
            suggested_improvements=improvements[:5],
            alternative_techniques=alternatives[:3],
            prevention_tips=[
                "Always test in isolated lab first",
                "Keep techniques updated",
                "Monitor for detection signs",
            ],
        )
    
    def generate_new_hypothesis(self, failed_attempt: Dict, improvements: List[str]) -> str:
        """توليد فرضية جديدة بناءً على التحليل"""
        technique = failed_attempt.get("technique", "unknown")
        improvements_text = ", ".join(improvements[:2])
        return f"Modified {technique} with {improvements_text} should bypass the previous issue."


# مثال
if __name__ == "__main__":
    analyzer = FailureAnalyzer()
    
    # فشل بسبب اكتشاف AV
    failure = {
        "technique": "meterpreter_reverse_https",
        "error": "Payload detected by Windows Defender and quarantined",
        "context": {"target_os": "windows", "defenses": ["defender"]}
    }
    
    analysis = analyzer.analyze_failure(failure)
    print(f"Root cause: {analysis.root_cause}")
    print(f"Confidence: {analysis.confidence}")
    print(f"Improvements: {analysis.suggested_improvements[:3]}")
    
    # فشل بسبب نقص صلاحيات
    failure2 = {
        "technique": "registry_persistence",
        "error": "access denied writing to HKLM",
        "context": {"current_privileges": "user"}
    }
    analysis2 = analyzer.analyze_failure(failure2)
    print(f"\nRoot cause: {analysis2.root_cause}")
    print(f"Alternatives: {analysis2.alternative_techniques}")