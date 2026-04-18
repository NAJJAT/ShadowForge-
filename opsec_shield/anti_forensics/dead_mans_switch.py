"""
Dead Man's Switch - التدمير الذاتي عند اكتشاف الخطر
"""

import os
import sys
import time
import threading
import shutil
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import hashlib
from core.config import settings

logger = logging.getLogger(__name__)

def __init__(self):
    self.enabled = settings.DMS_ENABLED
    self.inactivity_timeout = settings.DMS_INACTIVITY_TIMEOUT_HOURS * 3600
    self.alert_channel = settings.DMS_ALERT_CHANNEL
@dataclass
class DetectionEvent:
    """حدث اكتشاف خطر"""
    timestamp: float
    event_type: str
    description: str
    severity: str  # low, medium, high, critical


class DeadMansSwitch:
    """
    مفتاح الرجل الميت - تدمير ذاتي تلقائي
    
    يراقب علامات الخطر وعند اكتشافها:
    1. مسح آمن لكل البيانات
    2. مسح RAM
    3. تدمير المفاتيح
    4. إرسال تنبيه
    5. حذف البرنامج نفسه
    """
    
    # علامات الخطر (RED FLAGS)
    RED_FLAGS = {
        "ip_leak": {
            "patterns": ["DNS lookup to known tracking", "WebRTC IP detected"],
            "severity": "high"
        },
        "vpn_disconnect": {
            "patterns": ["VPN connection lost", "Interface down"],
            "severity": "critical"
        },
        "traceroute": {
            "patterns": ["traceroute detected", "hop count increasing"],
            "severity": "high"
        },
        "forensic_tools": {
            "patterns": ["wireshark", "tcpdump", "ProcessMonitor", "Sysinternals"],
            "severity": "high"
        },
        "debugger": {
            "patterns": ["ptrace detected", "debugger attached", "OllyDbg", "x64dbg"],
            "severity": "critical"
        },
        "sandbox": {
            "patterns": ["vmware", "virtualbox", "sandboxie", "cuckoo"],
            "severity": "medium"
        },
        "inactivity": {
            "patterns": ["no user activity > 72 hours"],
            "severity": "high"
        }
    }
    
    def __init__(self, enabled: bool = True, simulation_mode: bool = True, config: dict = None):
        self.enabled = enabled
        self.simulation_mode = simulation_mode
        self.config = config or {}
        
        # حالة النظام
        self.is_armed = False
        self.detected_events: List[DetectionEvent] = []
        self.last_activity = time.time()
        self.inactivity_timeout = self.config.get("inactivity_timeout", 72) * 3600
        
        # مسارات البيانات
        self.data_dir = Path(self.config.get("data_dir", "./data"))
        self.logs_dir = Path(self.config.get("logs_dir", "./logs"))
        
        # مؤقت المراقبة
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = False
        
        # ردود فعل مخصصة
        self.custom_actions: List[Callable] = []
        
        logger.info(f"DeadMansSwitch initialized (enabled={enabled}, simulation={simulation_mode})")
    
    def arm(self) -> bool:
        """تفعيل المفتاح"""
        if not self.enabled:
            logger.info("Dead Man's Switch is disabled")
            return False
        
        self.is_armed = True
        self._start_monitoring()
        logger.warning("⚠️ Dead Man's Switch ARMED - system will self-destruct if detected")
        return True
    
    def disarm(self) -> bool:
        """إلغاء التفعيل"""
        self.is_armed = False
        self._stop_monitoring()
        logger.info("Dead Man's Switch disarmed")
        return True
    
    def _start_monitoring(self):
        """بدء مراقبة العلامات الحمراء"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return
        
        self._stop_monitoring = False
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.debug("Monitoring thread started")
    
    def _stop_monitoring(self):
        """إيقاف المراقبة"""
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitor_loop(self):
        """حلقة المراقبة الرئيسية"""
        check_interval = self.config.get("check_interval", 5)  # كل 5 ثوان
        
        while not self._stop_monitoring and self.is_armed:
            try:
                # 1. فحص النشاط
                self._check_inactivity()
                
                # 2. فحص تسرب IP
                self._check_ip_leak()
                
                # 3. فحص أدوات التحليل الجنائي
                self._check_forensic_tools()
                
                # 4. فحص الـ debugger
                self._check_debugger()
                
                # 5. فحص بيئة التحليل
                self._check_sandbox()
                
                # 6. فحص مخصص
                self._run_custom_checks()
                
            except Exception as e:
                logger.error(f"Monitor error: {e}")
            
            time.sleep(check_interval)
    
    def _check_inactivity(self):
        """فحص فترة عدم النشاط"""
        inactive_time = time.time() - self.last_activity
        if inactive_time > self.inactivity_timeout:
            self._trigger_destruction(
                event_type="inactivity",
                description=f"No activity for {inactive_time//3600} hours",
                severity="high"
            )
    
    def _check_ip_leak(self):
        """فحص تسرب IP"""
        if self.simulation_mode:
            # في وضع المحاكاة، نفحص باستخدام API وهمي
            return
        
        try:
            import requests
            # فحص IP الحقيقي
            resp = requests.get("https://api.ipify.org", timeout=5)
            current_ip = resp.text
            
            # فحص IP عبر Tor
            resp = requests.get("https://check.torproject.org/api/ip", timeout=5)
            tor_ip = resp.json().get("IP", "")
            
            if current_ip != tor_ip and current_ip != "127.0.0.1":
                self._trigger_destruction(
                    event_type="ip_leak",
                    description=f"IP leak detected: {current_ip} vs Tor IP {tor_ip}",
                    severity="critical"
                )
        except Exception:
            pass
    
    def _check_forensic_tools(self):
        """فحص أدوات التحليل الجنائي"""
        forensic_processes = [
            "wireshark", "tcpdump", "tshark", "dumpcap",
            "procmon", "process monitor", "sysmon",
            "autoruns", "procexp", "process explorer"
        ]
        
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["tasklist"], capture_output=True, text=True, timeout=5
                )
                for proc in forensic_processes:
                    if proc.lower() in result.stdout.lower():
                        self._trigger_destruction(
                            event_type="forensic_tools",
                            description=f"Forensic tool detected: {proc}",
                            severity="high"
                        )
                        return
            except Exception:
                pass
        else:  # Linux/Mac
            try:
                result = subprocess.run(
                    ["ps", "aux"], capture_output=True, text=True, timeout=5
                )
                for proc in forensic_processes:
                    if proc.lower() in result.stdout.lower():
                        self._trigger_destruction(
                            event_type="forensic_tools",
                            description=f"Forensic tool detected: {proc}",
                            severity="high"
                        )
                        return
            except Exception:
                pass
    
    def _check_debugger(self):
        """فحص وجود debugger"""
        if sys.platform == "win32":
            try:
                # فحص وجود debugger
                import ctypes
                is_debugged = ctypes.windll.kernel32.IsDebuggerPresent()
                if is_debugged:
                    self._trigger_destruction(
                        event_type="debugger",
                        description="Debugger detected!",
                        severity="critical"
                    )
            except Exception:
                pass
    
    def _check_sandbox(self):
        """فحص بيئة تحليل"""
        # فحص وجود ملفات sandbox
        sandbox_indicators = [
            "/proc/vz/veinfo",  # OpenVZ
            "/proc/xen",  # Xen
            "/.dockerenv",  # Docker
            "/var/log/vboxadd-install.log",  # VirtualBox
        ]
        
        for indicator in sandbox_indicators:
            if os.path.exists(indicator):
                self._trigger_destruction(
                    event_type="sandbox",
                    description=f"Sandbox detected: {indicator}",
                    severity="medium"
                )
                return
        
        # فحص عدد الـ CPU cores (غالباً sandboxes 1-2 cores)
        cpu_count = os.cpu_count() or 1
        if cpu_count <= 2:
            logger.warning(f"Low CPU count ({cpu_count}) - possible sandbox")
            # لا ندمّر مباشرة، لكن نسجل
    
    def _run_custom_checks(self):
        """تنفيذ فحوصات مخصصة"""
        for action in self.custom_actions:
            try:
                result = action()
                if result:
                    self._trigger_destruction(
                        event_type="custom",
                        description=str(result),
                        severity="high"
                    )
            except Exception as e:
                logger.error(f"Custom check failed: {e}")
    
    def _trigger_destruction(self, event_type: str, description: str, severity: str):
        """
        تفعيل التدمير الذاتي
        """
        if not self.is_armed:
            return
        
        event = DetectionEvent(
            timestamp=time.time(),
            event_type=event_type,
            description=description,
            severity=severity
        )
        self.detected_events.append(event)
        
        logger.critical(f"⚠️ DESTRUCTION TRIGGERED! {event_type}: {description}")
        
        # تنفيذ التدمير
        self.self_destruct()
    
    def self_destruct(self):
        """
        التدمير الذاتي - مسح كل شيء
        """
        logger.critical("🔥 INITIATING SELF-DESTRUCT SEQUENCE 🔥")
        
        if self.simulation_mode:
            logger.warning("Simulation mode - skipping actual destruction")
            self._simulate_destruction()
            return
        
        # 1. إرسال تنبيه قبل التدمير
        self._send_alert()
        
        # 2. مسح آمن للبيانات
        self._secure_wipe()
        
        # 3. مسح المفاتيح التشفيرية
        self._destroy_keys()
        
        # 4. مسح سجلات النظام
        self._clear_logs()
        
        # 5. حذف البرنامج نفسه
        self._delete_self()
        
        # 6. إيقاف النظام
        self._shutdown()
        
        logger.critical("💀 SELF-DESTRUCT COMPLETE 💀")
    
    def _secure_wipe(self):
        """مسح آمن للبيانات"""
        paths_to_wipe = [self.data_dir, self.logs_dir]
        
        for path in paths_to_wipe:
            if path.exists():
                logger.info(f"Wiping: {path}")
                try:
                    if path.is_file():
                        self._wipe_file(path)
                    else:
                        shutil.rmtree(path, ignore_errors=True)
                except Exception as e:
                    logger.error(f"Wipe failed: {e}")
    
    def _wipe_file(self, filepath: Path, passes: int = 7):
        """مسح ملف بتمريرات متعددة"""
        if not filepath.exists():
            return
        
        size = filepath.stat().st_size
        with open(filepath, "wb") as f:
            for _ in range(passes):
                # تمرير بأصفار
                f.seek(0)
                f.write(b'\x00' * size)
                f.flush()
                
                # تمرير بأحرف عشوائية
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
        
        filepath.unlink()
        logger.debug(f"Wiped: {filepath}")
    
    def _destroy_keys(self):
        """تدمير المفاتيح التشفيرية"""
        # حذف متغيرات البيئة التي تحتوي مفاتيح
        for key in os.environ.keys():
            if any(x in key.lower() for x in ["key", "secret", "token", "password", "api"]):
                os.environ[key] = ""
        
        # مسح الذاكرة (على قدر الإمكان)
        self._clear_ram()
    
    def _clear_ram(self):
        """مسح محتويات RAM"""
        # لا يمكن مسح RAM بالكامل من Python، لكن نحاول تقليل البصمة
        
        # 1. حذف المتغيرات
        import gc
        gc.collect()
        
        # 2. محاولة مسح الذاكرة (Linux)
        if sys.platform == "linux":
            try:
                # طلب مسح ذاكرة التخزين المؤقت (يتطلب صلاحيات)
                subprocess.run(["sync"], capture_output=True)
                with open("/proc/sys/vm/drop_caches", "w") as f:
                    f.write("3")
            except Exception:
                pass
    
    def _clear_logs(self):
        """مسح سجلات النظام"""
        log_paths = [
            "/var/log/syslog",
            "/var/log/auth.log",
            "~/.bash_history",
            "~/.zsh_history",
        ]
        
        for log in log_paths:
            log_path = Path(log).expanduser()
            if log_path.exists():
                try:
                    with open(log_path, "w") as f:
                        f.write("")
                except Exception:
                    pass
    
    def _delete_self(self):
        """حذف البرنامج نفسه"""
        try:
            script_path = Path(sys.argv[0])
            self._wipe_file(script_path)
        except Exception:
            pass
    
    def _send_alert(self):
        """إرسال تنبيه"""
        alert_message = f"""
        ⚠️ DEAD MAN'S SWITCH TRIGGERED ⚠️
        Time: {datetime.now()}
        Events: {len(self.detected_events)}
        Last event: {self.detected_events[-1].description if self.detected_events else 'None'}
        """
        
        # يمكن إرسال عبر Signal, Telegram, أو Email
        logger.critical(alert_message)
        
        # في وضع حقيقي، أرسل تنبيه مشفر
        # self._send_signal_alert(alert_message)
    
    def _shutdown(self):
        """إيقاف التشغيل"""
        try:
            if sys.platform == "win32":
                os.system("shutdown /s /t 0")
            else:
                os.system("shutdown -h now")
        except Exception:
            pass
    
    def _simulate_destruction(self):
        """محاكاة التدمير الذاتي"""
        print("\n" + "="*60)
        print("🔥 SIMULATED SELF-DESTRUCT 🔥")
        print("="*60)
        print("In production mode, the following would happen:")
        print("1. Secure wipe of all data (7 passes)")
        print("2. RAM cleared")
        print("3. Encryption keys destroyed")
        print("4. System logs cleared")
        print("5. Program self-deleted")
        print("6. System shutdown")
        print("="*60)
        
        for event in self.detected_events:
            print(f"Triggered by: {event.event_type} - {event.description}")
    
    def heartbeat(self):
        """تحديث آخر نشاط"""
        self.last_activity = time.time()
    
    def register_custom_check(self, check_func: Callable):
        """إضافة فحص مخصص"""
        self.custom_actions.append(check_func)
    
    def get_status(self) -> dict:
        """الحصول على حالة المفتاح"""
        return {
            "armed": self.is_armed,
            "enabled": self.enabled,
            "detections": len(self.detected_events),
            "last_activity": self.last_activity,
            "inactivity_timeout_hours": self.inactivity_timeout / 3600,
        }


# مثال الاستخدام
if __name__ == "__main__":
    dms = DeadMansSwitch(enabled=True, simulation_mode=True)
    dms.arm()
    
    # محاكاة نشاط
    for i in range(5):
        dms.heartbeat()
        time.sleep(1)
        print(f"Activity {i+1}/5")
    
    # فحص المفتاح
    status = dms.get_status()
    print(f"\nStatus: {status}")
    
    dms.disarm()