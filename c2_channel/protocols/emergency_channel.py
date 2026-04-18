"""
Emergency Channel - قناة طوارئ عند فشل القنوات الرئيسية
"""

import logging
import random

logger = logging.getLogger(__name__)

class EmergencyChannel:
    """قناة اتصال بديلة عند اكتشاف أو فشل القنوات العادية"""
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.fallback_domains = [
            "google.com", "cloudflare.com", "microsoft.com", "github.com"
        ]
    
    def send(self, data: bytes) -> bool:
        domain = random.choice(self.fallback_domains)
        if self.simulation_mode:
            logger.info(f"[EMERGENCY] Would send {len(data)} bytes via {domain}")
        return True
    
    def receive(self) -> bytes:
        return b"emergency_response"