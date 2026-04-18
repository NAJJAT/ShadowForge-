"""
Environment Awareness - الوعي بالبيئة
"""

import os
import platform

class EnvironmentAwareness:
    """يجمع معلومات عن البيئة الحالية"""
    
    @staticmethod
    def get_os_info() -> dict:
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        }
    
    @staticmethod
    def is_vm() -> bool:
        indicators = ["vbox", "vmware", "qemu", "xen", "kvm"]
        system = platform.system().lower()
        for ind in indicators:
            if ind in system:
                return True
        return False
    
    @staticmethod
    def get_username() -> str:
        return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))