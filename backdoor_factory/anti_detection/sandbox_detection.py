"""
Sandbox Detection - كشف بيئات التحليل (VMs, sandboxes, debuggers)
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class SandboxDetector:
    """
    يكتشف ما إذا كان الكود يعمل داخل بيئة تحليل (sandbox)
    
    المؤشرات:
    - عمليات غير معتادة
    - أجهزة افتراضية
    - أدوات تحليل
    - سلوك غير طبيعي
    """
    
    def __init__(self):
        self.suspicion_score = 0
        self.detections = []
    
    def detect(self) -> Tuple[bool, Dict]:
        """
        إجراء جميع الفحوصات
        Returns: (is_sandbox, details)
        """
        self.suspicion_score = 0
        self.detections = []
        
        self._check_processes()
        self._check_vm_artifacts()
        self._check_hardware()
        self._check_network()
        self._check_time()
        
        is_sandbox = self.suspicion_score >= 3
        return is_sandbox, {
            "score": self.suspicion_score,
            "detections": self.detections,
            "is_sandbox": is_sandbox,
        }
    
    def _check_processes(self):
        """فحص العمليات المشبوهة"""
        suspicious = [
            "vboxservice", "vboxtray", "vmtoolsd", "vmwaretray",
            "xenserver", "procmon", "wireshark", "tcpdump",
            "ollydbg", "x64dbg", "ida", "immunity",
        ]
        try:
            if sys.platform == "win32":
                result = subprocess.run(["tasklist"], capture_output=True, text=True)
                for proc in suspicious:
                    if proc.lower() in result.stdout.lower():
                        self.suspicion_score += 1
                        self.detections.append(f"Suspicious process: {proc}")
            else:
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
                for proc in suspicious:
                    if proc.lower() in result.stdout.lower():
                        self.suspicion_score += 1
                        self.detections.append(f"Suspicious process: {proc}")
        except:
            pass
    
    def _check_vm_artifacts(self):
        """فحص آثار VM"""
        artifacts = [
            "/proc/vz/veinfo",
            "/proc/xen",
            "/.dockerenv",
            "/var/log/vboxadd-install.log",
            "C:\\Program Files\\Oracle\\VirtualBox Guest Additions",
            "C:\\Program Files\\VMware\\VMware Tools",
        ]
        for art in artifacts:
            if os.path.exists(art):
                self.suspicion_score += 1
                self.detections.append(f"VM artifact: {art}")
    
    def _check_hardware(self):
        """فحص العتاد"""
        # عدد الأنوية (sandboxes غالباً قليل)
        cpu_count = os.cpu_count() or 1
        if cpu_count <= 2:
            self.suspicion_score += 1
            self.detections.append(f"Low CPU cores: {cpu_count}")
        
        # حجم RAM (sandboxes غالباً صغير)
        try:
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                mem = ctypes.c_ulonglong()
                kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(mem))
                ram_gb = mem.value / (1024 * 1024)
                if ram_gb < 4:
                    self.suspicion_score += 1
                    self.detections.append(f"Low RAM: {ram_gb:.1f} GB")
        except:
            pass
    
    def _check_network(self):
        """فحص الشبكة"""
        # sandboxes غالباً لا تحتوي اتصال إنترنت حقيقي
        try:
            import socket
            socket.gethostbyname("www.google.com")
        except:
            self.suspicion_score += 1
            self.detections.append("No internet connectivity")
    
    def _check_time(self):
        """فحص الوقت (sandboxes غالباً تعيد ضبط الوقت)"""
        # محاكاة: يمكن فحص فرق الوقت بين الاستعلامات
        pass


# مثال
if __name__ == "__main__":
    detector = SandboxDetector()
    is_sandbox, details = detector.detect()
    print(f"Is sandbox: {is_sandbox}")
    print(f"Details: {details}")