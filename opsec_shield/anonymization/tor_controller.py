"""
Tor Controller - إدارة اتصال Tor مع obfs4 bridges
"""

import subprocess
import socket
import socks
import requests
import time
import threading
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class TorStatus:
    """حالة اتصال Tor"""
    is_running: bool = False
    circuit_id: str = ""
    exit_node: str = ""
    entry_node: str = ""
    bandwidth: int = 0
    uptime_seconds: int = 0


class TorController:
    """
    مدير اتصال Tor
    
    الميزات:
    - تشغيل/إيقاف Tor
    - استخدام obfs4 bridges لتجنب الكشف
    - تدوير الـ circuit تلقائياً
    - مراقبة الجودة
    """
    
    def __init__(self, simulation_mode: bool = True, config: dict = None):
        self.simulation_mode = simulation_mode
        self.config = config or {}
        
        self.socks_port = self.config.get("socks_port", 9050)
        self.control_port = self.config.get("control_port", 9051)
        self.control_password = self.config.get("control_password", "")
        
        self.process: Optional[subprocess.Popen] = None
        self.status = TorStatus()
        self._running = False
        self._circuit_rotation_timer: Optional[threading.Timer] = None
        
        # Bridges مخفية (للأغراض الأكاديمية فقط)
        self.obfs4_bridges = [
            "obfs4 192.95.36.142:443 C6A5B4E5F0C8B6A4D9F2E1A3B5C7D9E2F1A3B5C7",
            "obfs4 45.145.95.6:27015 E8D4B2F9A1C5E7B3D6F0A2C4E8B1D3F5A7C9E1B3",
            "obfs4 38.229.1.78:80 C7E5B3D1F9A7C5E3B1D9F7A5C3E1B9F7D5B3F1A9",
        ]
        
        logger.info(f"TorController initialized (simulation_mode={simulation_mode})")
    
    def start(self) -> bool:
        """تشغيل خدمة Tor"""
        if self._running:
            logger.warning("Tor already running")
            return True
        
        logger.info("Starting Tor service...")
        
        if self.simulation_mode:
            # وضع المحاكاة
            self._running = True
            self.status.is_running = True
            self.status.exit_node = "simulated_exit_node.tor"
            self.status.entry_node = "simulated_entry_node.tor"
            logger.info("✓ Tor started (simulation mode)")
            self._start_circuit_rotation()
            return True
        
        # وضع حقيقي - يتطلب تثبيت Tor
        try:
            cmd = ["tor", "--SocksPort", str(self.socks_port), 
                   "--ControlPort", str(self.control_port),
                   "--RunAsDaemon", "1"]
            
            if self.config.get("use_bridges", True):
                bridge_lines = [f"Bridge {b}" for b in self.obfs4_bridges[:2]]
                with open("/tmp/torrc", "w") as f:
                    f.write("\n".join(bridge_lines))
                    f.write("\nUseBridges 1\n")
                cmd.extend(["-f", "/tmp/torrc"])
            
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)  # انتظار بدء التشغيل
            
            if self._check_connection():
                self._running = True
                self.status.is_running = True
                self._update_status()
                self._start_circuit_rotation()
                logger.info("✓ Tor started successfully")
                return True
            else:
                logger.error("✗ Tor failed to start")
                return False
                
        except Exception as e:
            logger.error(f"Tor start error: {e}")
            return False
    
    def stop(self) -> bool:
        """إيقاف خدمة Tor"""
        logger.info("Stopping Tor service...")
        
        self._stop_circuit_rotation()
        
        if self.simulation_mode:
            self._running = False
            self.status.is_running = False
            logger.info("✓ Tor stopped (simulation mode)")
            return True
        
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=10)
            else:
                subprocess.run(["pkill", "tor"], capture_output=True)
            
            self._running = False
            self.status.is_running = False
            logger.info("✓ Tor stopped")
            return True
        except Exception as e:
            logger.error(f"Tor stop error: {e}")
            return False
    
    def _check_connection(self) -> bool:
        """فحص اتصال Tor"""
        try:
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", self.socks_port)
            socket.socket = socks.socksocket
            
            response = requests.get("https://check.torproject.org/api/ip", timeout=10)
            return response.json().get("IsTor", False)
        except Exception:
            return False
    
    def _update_status(self):
        """تحديث حالة Tor"""
        if self.simulation_mode:
            return
        
        try:
            import stem
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                
                # الحصول على معلومات الـ circuit
                circuits = controller.get_circuits()
                for circuit in circuits:
                    if circuit.status == "BUILT":
                        self.status.circuit_id = str(circuit.id)
                        if len(circuit.path) > 0:
                            self.status.exit_node = circuit.path[-1]
                            self.status.entry_node = circuit.path[0]
                        break
                
                self.status.uptime_seconds = int(controller.get_info("uptime"))
                self.status.bandwidth = int(controller.get_info("traffic/read")) // 1024
                
        except Exception as e:
            logger.debug(f"Status update failed: {e}")
    
    def rotate_circuit(self) -> bool:
        """
        تدوير الـ circuit (الحصول على هوية خروج جديدة)
        """
        logger.info("Rotating Tor circuit...")
        
        if self.simulation_mode:
            # في وضع المحاكاة، نغير البيانات الوهمية
            import random
            self.status.exit_node = f"simulated_exit_{random.randint(1,999)}.tor"
            logger.info("✓ Circuit rotated (simulation mode)")
            return True
        
        try:
            import stem
            from stem.control import Controller
            
            with Controller.from_port(port=self.control_port) as controller:
                controller.authenticate()
                controller.signal(stem.Signal.NEWNYM)
                time.sleep(2)
                self._update_status()
                logger.info(f"✓ Circuit rotated. New exit node: {self.status.exit_node}")
                return True
        except Exception as e:
            logger.error(f"Circuit rotation failed: {e}")
            return False
    
    def _start_circuit_rotation(self):
        """بدء التدوير التلقائي للـ circuit"""
        interval = self.config.get("circuit_rotation_minutes", 10) * 60
        self._circuit_rotation_timer = threading.Timer(interval, self._auto_rotate_circuit)
        self._circuit_rotation_timer.daemon = True
        self._circuit_rotation_timer.start()
    
    def _stop_circuit_rotation(self):
        """إيقاف التدوير التلقائي"""
        if self._circuit_rotation_timer:
            self._circuit_rotation_timer.cancel()
            self._circuit_rotation_timer = None
    
    def _auto_rotate_circuit(self):
        """تدوير تلقائي للـ circuit"""
        if self._running:
            self.rotate_circuit()
            self._start_circuit_rotation()  # إعادة جدولة
    
    def get_proxy(self) -> Tuple[str, int]:
        """الحصول على إعدادات الوكيل"""
        return ("127.0.0.1", self.socks_port)
    
    def get_status(self) -> dict:
        """الحصول على حالة Tor"""
        self._update_status()
        return {
            "is_running": self._running,
            "exit_node": self.status.exit_node,
            "entry_node": self.status.entry_node,
            "uptime_seconds": self.status.uptime_seconds,
            "circuit_id": self.status.circuit_id,
        }
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


# مثال الاستخدام
if __name__ == "__main__":
    with TorController(simulation_mode=True) as tor:
        print("\n" + "="*50)
        print("Tor Status:")
        print("="*50)
        status = tor.get_status()
        for k, v in status.items():
            print(f"{k}: {v}")