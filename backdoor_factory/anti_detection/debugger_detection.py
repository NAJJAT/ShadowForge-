"""
Debugger Detection - كشف وجود مصحح أخطاء
"""

import sys
import ctypes

class DebuggerDetection:
    """يكتشف إذا كان البرنامج يعمل تحت debugger"""
    
    @staticmethod
    def is_debugger_present() -> bool:
        if sys.platform == "win32":
            try:
                return ctypes.windll.kernel32.IsDebuggerPresent() != 0
            except:
                pass
        return False
    
    @staticmethod
    def check_ptrace() -> bool:
        """فحص ptrace على Linux"""
        if sys.platform == "linux":
            try:
                import ptrace
                return ptrace.traceme() != 0
            except:
                pass
        return False