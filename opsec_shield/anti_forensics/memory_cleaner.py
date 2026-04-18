"""
Memory Cleaner - مسح محتويات الذاكرة (RAM)
"""

import sys
import gc
import logging
from typing import List

logger = logging.getLogger(__name__)


class MemoryCleaner:
    """
    يقوم بمسح البيانات الحساسة من الذاكرة:
    - محو المتغيرات
    - جمع القمامة
    - مسح المخازن المؤقتة
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        logger.info("MemoryCleaner initialized")
    
    def clear_variable(self, var):
        """مسح متغير بشكل آمن"""
        try:
            if isinstance(var, (bytes, bytearray)):
                for i in range(len(var)):
                    var[i] = 0
            elif isinstance(var, str):
                # السلاسل غير قابلة للتغيير، نحتاج إلى استبدال المرجع
                var = '\x00' * len(var)
            elif isinstance(var, dict):
                var.clear()
            elif isinstance(var, list):
                var.clear()
            elif isinstance(var, set):
                var.clear()
        except Exception as e:
            logger.debug(f"Could not clear variable: {e}")
    
    def clear_globals(self, sensitive_keys: List[str] = None):
        """مسح المتغيرات العامة الحساسة"""
        if sensitive_keys is None:
            sensitive_keys = ['password', 'key', 'secret', 'token', 'credential']
        
        for key in list(globals().keys()):
            if any(s in key.lower() for s in sensitive_keys):
                try:
                    globals()[key] = None
                except:
                    pass
    
    def force_garbage_collection(self):
        """强制执行 جمع القمامة"""
        gc.collect()
        if self.simulation_mode:
            logger.debug("[SIM] Garbage collection forced")
        else:
            logger.debug("Garbage collection forced")
    
    def clear_recent_memory(self):
        """مسح الذاكرة الحديثة (محاكاة)"""
        # في الواقع، يمكن استخدام ctypes لمسح الذاكرة
        # لكن هذا قد يكون غير مستقر عبر المنصات
        if self.simulation_mode:
            logger.info("[SIM] Recent memory cleared")
        else:
            # محاولة استخدام ctypes (اختياري)
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except:
                pass
    
    def wipe(self):
        """مسح شامل للذاكرة"""
        self.clear_globals()
        self.force_garbage_collection()
        self.clear_recent_memory()
        logger.info("Memory wipe completed")


if __name__ == "__main__":
    cleaner = MemoryCleaner(simulation_mode=True)
    cleaner.wipe()
    print("Memory cleaned")