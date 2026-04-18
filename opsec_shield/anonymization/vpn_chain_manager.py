"""
VPN Chain Manager - يدير سلسلة VPNs متعددة الطبقات مع تدوير تلقائي
"""

import random
import time
import threading
import subprocess
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VPNProvider(Enum):
    """مزودو VPN المدعومون"""
    PROTONVPN = "protonvpn"
    MULLVAD = "mullvad"
    IVPN = "ivpn"
    WINDSCRIBE = "windscribe"
    AIRVPN = "airvpn"
    
    @property
    def cli_name(self) -> str:
        """اسم CLI لكل مزود"""
        mapping = {
            VPNProvider.PROTONVPN: "protonvpn-cli",
            VPNProvider.MULLVAD: "mullvad",
            VPNProvider.IVPN: "ivpn",
            VPNProvider.WINDSCRIBE: "windscribe",
            VPNProvider.AIRVPN: "airvpn",
        }
        return mapping.get(self, "unknown")


@dataclass
class VPNHop:
    """طبقة واحدة في سلسلة VPN"""
    provider: VPNProvider
    country: str
    city: str = ""
    entry_ip: str = ""
    exit_ip: str = ""
    connected_at: float = field(default_factory=time.time)
    bytes_sent: int = 0
    bytes_recv: int = 0
    connection_id: str = ""
    
    def __post_init__(self):
        if not self.connection_id:
            self.connection_id = hashlib.md5(
                f"{self.provider.value}{self.country}{self.connected_at}".encode()
            ).hexdigest()[:8]
    
    def to_dict(self) -> dict:
        return {
            "provider": self.provider.value,
            "country": self.country,
            "city": self.city,
            "entry_ip": self.entry_ip,
            "exit_ip": self.exit_ip,
            "connected_at": self.connected_at,
            "connection_id": self.connection_id,
        }
    
    def __str__(self) -> str:
        return f"[{self.connection_id}] {self.provider.value} → {self.country} ({self.exit_ip})"


class VPNConnectionError(Exception):
    """خطأ في اتصال VPN"""
    pass


class VPNChainManager:
    """
    مدير سلسلة VPNs المتعددة
    
    الوظائف:
    - بناء سلسلة عشوائية من VPNs
    - تدوير تلقائي كل X ساعة
    - تغيير كامل للهوية عند التدوير
    - مراقبة جودة الاتصال
    - تجاوز الفشل التلقائي
    """
    
    def __init__(self, simulation_mode: bool = True, config: dict = None):
        self.simulation_mode = simulation_mode
        self.config = config or {}
        
        # حالة النظام
        self.current_chain: List[VPNHop] = []
        self.rotation_timer: Optional[threading.Timer] = None
        self.is_running: bool = False
        self._stop_rotation = False
        
        # إحصائيات
        self.total_bytes_sent: int = 0
        self.total_bytes_recv: int = 0
        self.rotations_count: int = 0
        self.failures_count: int = 0
        
        # قواعد البيانات المحاكاة
        self.country_database = self._load_country_database()
        self.provider_servers = self._load_provider_servers()
        
        logger.info(f"VPNChainManager initialized (simulation_mode={simulation_mode})")
    
    def _load_country_database(self) -> dict:
        """تحميل قاعدة بيانات الدول المتاحة"""
        return {
            "CH": {"name": "Switzerland", "jurisdiction": "friendly", "latency_ms": 50},
            "IS": {"name": "Iceland", "jurisdiction": "friendly", "latency_ms": 80},
            "SE": {"name": "Sweden", "jurisdiction": "friendly", "latency_ms": 60},
            "NL": {"name": "Netherlands", "jurisdiction": "friendly", "latency_ms": 40},
            "RO": {"name": "Romania", "jurisdiction": "friendly", "latency_ms": 70},
            "DE": {"name": "Germany", "jurisdiction": "friendly", "latency_ms": 45},
            "NO": {"name": "Norway", "jurisdiction": "friendly", "latency_ms": 85},
            "FI": {"name": "Finland", "jurisdiction": "friendly", "latency_ms": 90},
        }
    
    def _load_provider_servers(self) -> dict:
        """تحميل معلومات سيرفرات المزودين"""
        return {
            VPNProvider.PROTONVPN: {
                "CH": ["10.2.1.1", "10.2.1.2", "10.2.1.3"],
                "IS": ["10.2.2.1", "10.2.2.2"],
                "SE": ["10.2.3.1", "10.2.3.2"],
                "NL": ["10.2.4.1", "10.2.4.2"],
            },
            VPNProvider.MULLVAD: {
                "DE": ["10.3.1.1", "10.3.1.2"],
                "NL": ["10.3.2.1", "10.3.2.2"],
                "CH": ["10.3.3.1"],
            },
            VPNProvider.IVPN: {
                "CH": ["10.4.1.1"],
                "IS": ["10.4.2.1"],
                "SE": ["10.4.3.1"],
                "NL": ["10.4.4.1"],
            },
        }
    
    def build_chain(self, length: int = 3, avoid_countries: List[str] = None) -> List[VPNHop]:
        """
        بناء سلسلة VPN عشوائية جديدة
        
        Args:
            length: عدد طبقات VPN (1-5)
            avoid_countries: قائمة دول لتجنبها
        
        Returns:
            List[VPNHop]: السلسلة الجديدة
        """
        if avoid_countries is None:
            avoid_countries = ["US", "UK", "AU", "CA", "NZ", "CN", "RU"]
        
        # تحديد الطول الفعلي
        length = min(max(length, 1), 5)
        
        chain = []
        used_providers = set()
        used_countries = set()
        
        for i in range(length):
            # 1. اختيار مزود VPN لم يُستخدم
            available_providers = [p for p in VPNProvider if p not in used_providers]
            if not available_providers:
                available_providers = list(VPNProvider)
            
            provider = random.choice(available_providers)
            used_providers.add(provider)
            
            # 2. اختيار دولة مناسبة
            available_countries = list(self.provider_servers.get(provider, {}).keys())
            available_countries = [c for c in available_countries 
                                  if c not in avoid_countries 
                                  and c not in used_countries]
            
            if not available_countries:
                available_countries = [c for c in list(self.country_database.keys()) 
                                      if c not in avoid_countries]
            
            country = random.choice(available_countries) if available_countries else "CH"
            used_countries.add(country)
            
            # 3. اختيار IP دخول وخروج
            servers = self.provider_servers.get(provider, {}).get(country, ["127.0.0.1"])
            entry_ip = random.choice(servers) if servers else f"10.0.{i}.1"
            exit_ip = random.choice(servers) if len(servers) > 1 else f"10.0.{i}.2"
            
            # 4. إنشاء الـ hop
            hop = VPNHop(
                provider=provider,
                country=country,
                city=self.country_database.get(country, {}).get("name", ""),
                entry_ip=entry_ip,
                exit_ip=exit_ip,
            )
            chain.append(hop)
            
            logger.info(f"Built hop {i+1}: {hop}")
        
        # 5. التحقق من عدم وجود تكرار في الدول (للحصول على أقصى إخفاء)
        unique_countries = set(h.country for h in chain)
        if len(unique_countries) < length:
            logger.warning(f"Chain has duplicate countries: {unique_countries}")
        
        return chain
    
    def connect_chain(self, chain: List[VPNHop] = None) -> bool:
        """
        الاتصال بسلسلة VPN
        
        Args:
            chain: السلسلة للاتصال (إذا لم تُعطَ، يُبنى واحد جديد)
        
        Returns:
            bool: نجاح الاتصال
        """
        if chain is None:
            chain = self.build_chain()
        
        logger.info(f"Connecting VPN chain with {len(chain)} hops...")
        
        for i, hop in enumerate(chain):
            logger.info(f"  Connecting hop {i+1}: {hop.provider.value} → {hop.country}")
            
            if self.simulation_mode:
                # وضع المحاكاة - نجاح وهمي
                time.sleep(0.5)  # محاكاة وقت الاتصال
                hop.connected_at = time.time()
                logger.info(f"  ✓ Connected to {hop} (simulated)")
            else:
                # اتصال حقيقي - يتطلب تثبيت VPN CLIs
                success = self._real_connect(hop)
                if not success:
                    logger.error(f"  ✗ Failed to connect {hop}")
                    self.disconnect_chain()
                    return False
            
            # تحديث الإحصائيات
            self.total_bytes_sent += hop.bytes_sent
            self.total_bytes_recv += hop.bytes_recv
        
        self.current_chain = chain
        self.is_running = True
        logger.info(f"✓ VPN chain connected successfully! Chain ID: {self._get_chain_id()}")
        
        # بدء مؤقت التدوير
        self._start_rotation_timer()
        
        return True
    
    def _real_connect(self, hop: VPNHop) -> bool:
        """اتصال حقيقي بـ VPN (يتطلب CLI مثبت)"""
        try:
            cmd = [hop.provider.cli_name, "connect", hop.country.lower()]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # الحصول على IP المعين
                ip_result = subprocess.run(["curl", "-s", "ifconfig.me"], 
                                          capture_output=True, text=True, timeout=10)
                hop.exit_ip = ip_result.stdout.strip()
                return True
            return False
        except Exception as e:
            logger.error(f"VPN connection error: {e}")
            return False
    
    def disconnect_chain(self) -> bool:
        """قطع اتصال السلسلة الحالية"""
        if not self.current_chain:
            return True
        
        logger.info("Disconnecting VPN chain...")
        
        # قطع الاتصال بالعكس (من آخر hop إلى أول hop)
        for hop in reversed(self.current_chain):
            if self.simulation_mode:
                logger.info(f"  Disconnected {hop}")
            else:
                self._real_disconnect(hop)
        
        self.current_chain = []
        self.is_running = False
        self._stop_rotation_timer()
        
        logger.info("✓ VPN chain disconnected")
        return True
    
    def _real_disconnect(self, hop: VPNHop) -> bool:
        """قطع اتصال حقيقي"""
        try:
            cmd = [hop.provider.cli_name, "disconnect"]
            subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return True
        except Exception:
            return False
    
    def rotate_chain(self) -> bool:
        """
        تدوير السلسلة بالكامل وتغيير الهوية
        """
        logger.info("🔄 Rotating VPN chain and identity...")
        self.rotations_count += 1
        
        # 1. قطع الاتصال الحالي
        self.disconnect_chain()
        
        # 2. بناء سلسلة جديدة
        new_chain = self.build_chain()
        
        # 3. الاتصال بالسلسلة الجديدة
        success = self.connect_chain(new_chain)
        
        if success:
            logger.info(f"✓ Rotation complete (#{self.rotations_count})")
        else:
            logger.error("✗ Rotation failed!")
            self.failures_count += 1
        
        return success
    
    def _start_rotation_timer(self):
        """بدء مؤقت التدوير التلقائي"""
        if self.rotation_timer:
            self.rotation_timer.cancel()
        
        interval = self.config.get("rotation_interval", 3600)
        self.rotation_timer = threading.Timer(interval, self._auto_rotate)
        self.rotation_timer.daemon = True
        self.rotation_timer.start()
        logger.debug(f"Rotation timer set for {interval} seconds")
    
    def _stop_rotation_timer(self):
        """إيقاف مؤقت التدوير"""
        if self.rotation_timer:
            self.rotation_timer.cancel()
            self.rotation_timer = None
    
    def _auto_rotate(self):
        """تدوير تلقائي (يُستدعى بواسطة المؤقت)"""
        if not self._stop_rotation and self.is_running:
            self.rotate_chain()
            self._start_rotation_timer()  # إعادة جدولة
    
    def get_current_exit_ip(self) -> Optional[str]:
        """الحصول على IP الخروج الحالي"""
        if self.current_chain:
            return self.current_chain[-1].exit_ip
        return None
    
    def get_chain_status(self) -> dict:
        """الحصول على حالة السلسلة"""
        return {
            "is_connected": self.is_running,
            "chain_length": len(self.current_chain),
            "hops": [h.to_dict() for h in self.current_chain],
            "exit_ip": self.get_current_exit_ip(),
            "rotations_count": self.rotations_count,
            "failures_count": self.failures_count,
            "total_bytes": self.total_bytes_sent + self.total_bytes_recv,
        }
    
    def _get_chain_id(self) -> str:
        """معرف فريد للسلسلة الحالية"""
        if not self.current_chain:
            return "none"
        combined = "|".join([f"{h.provider.value}:{h.country}" for h in self.current_chain])
        return hashlib.md5(combined.encode()).hexdigest()[:8]
    
    def test_leak(self) -> dict:
        """
        اختبار تسرب DNS و IP
        
        Returns:
            dict: نتائج الاختبار
        """
        results = {
            "ip": self.get_current_exit_ip(),
            "dns_leak": False,
            "ipv6_leak": False,
            "webrtc_leak": False,
        }
        
        if self.simulation_mode:
            results["dns_leak"] = False
            results["ipv6_leak"] = False
            results["webrtc_leak"] = False
            results["message"] = "Simulation mode - no leaks detected"
        else:
            # اختبارات حقيقية
            import requests
            try:
                # اختبار IP
                resp = requests.get("https://api.ipify.org", timeout=10)
                results["ip"] = resp.text
                
                # اختبار DNS leak
                dns_test = requests.get("https://dnsleaktest.com/json", timeout=10)
                if dns_test.status_code == 200:
                    data = dns_test.json()
                    results["dns_leak"] = len(data.get("ip", [])) > 1
            except Exception as e:
                results["error"] = str(e)
        
        return results
    
    def __enter__(self):
        """دعم context manager"""
        self.connect_chain()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """دعم context manager"""
        self.disconnect_chain()


# مثال الاستخدام
if __name__ == "__main__":
    # اختبار في وضع المحاكاة
    with VPNChainManager(simulation_mode=True) as vpn:
        print("\n" + "="*50)
        print("VPN Chain Status:")
        print("="*50)
        status = vpn.get_chain_status()
        print(f"Connected: {status['is_connected']}")
        print(f"Exit IP: {status['exit_ip']}")
        print(f"Chain ID: {vpn._get_chain_id()}")
        
        print("\n" + "="*50)
        print("Leak Test:")
        print("="*50)
        leak_test = vpn.test_leak()
        for k, v in leak_test.items():
            print(f"{k}: {v}")