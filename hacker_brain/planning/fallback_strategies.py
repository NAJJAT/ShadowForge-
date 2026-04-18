"""
Fallback Strategies - خطط بديلة عند فشل الهجوم
"""

from typing import Dict, List, Optional

class FallbackStrategies:
    """يدير الخطط البديلة لكل مرحلة هجوم"""
    
    STRATEGIES = {
        "reconnaissance": [
            "Switch to passive OSINT",
            "Use different scanning tool",
            "Scan from different source IP",
            "Increase scan delay"
        ],
        "exploitation": [
            "Try alternative vulnerability",
            "Use different payload encoding",
            "Switch to client-side attack",
            "Attempt privilege escalation first"
        ],
        "persistence": [
            "Use different persistence method",
            "Install backup backdoor",
            "Use fileless technique",
            "Schedule delayed execution"
        ],
        "exfiltration": [
            "Use steganography",
            "Split data across multiple channels",
            "Encrypt and upload to cloud",
            "Use DNS tunneling"
        ]
    }
    
    @classmethod
    def get_fallback(cls, phase: str, attempt: int = 1) -> Optional[str]:
        """الحصول على خطة بديلة بناءً على عدد المحاولات"""
        strategies = cls.STRATEGIES.get(phase, cls.STRATEGIES["exploitation"])
        idx = min(attempt - 1, len(strategies) - 1)
        return strategies[idx] if strategies else None
    
    @classmethod
    def all_fallbacks(cls, phase: str) -> List[str]:
        return cls.STRATEGIES.get(phase, [])