"""
Jittered Communications - اتصالات ذات تشويش زمني
"""

import time
import random
import logging

logger = logging.getLogger(__name__)

class JitteredComms:
    """يضيف تشويشاً زمنياً لتجنب اكتشاف الأنماط"""
    
    def __init__(self, base_delay: float = 1.0, jitter: float = 0.3):
        self.base_delay = base_delay
        self.jitter = jitter
    
    def delay(self):
        actual = self.base_delay * (1 + random.uniform(-self.jitter, self.jitter))
        time.sleep(actual)
        return actual