"""
الإعدادات الرئيسية لطبقة OPSEC Shield
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class Environment(Enum):
    """بيئات التشغيل"""
    LAB = "lab"              # بيئة مختبر معزولة
    SIMULATION = "sim"       # وضع المحاكاة
    PRODUCTION = "prod"      # إنتاجي (لاختبار الشركة فقط)


@dataclass
class OPSECConfig:
    """الإعدادات الرئيسية"""
    
    # === إعدادات البيئة ===
    environment: Environment = Environment.LAB
    simulation_mode: bool = True
    lab_mode: bool = True
    
    # === إعدادات VPN Chain ===
    vpn_providers: List[str] = field(default_factory=lambda: ["protonvpn", "mullvad", "ivpn"])
    excluded_countries: List[str] = field(default_factory=lambda: ["US", "UK", "AU", "CA", "NZ"])
    preferred_countries: List[str] = field(default_factory=lambda: ["CH", "IS", "SE", "NL", "RO", "DE"])
    chain_length: int = 3
    rotation_interval_seconds: int = 3600  # ساعة
    vpn_connection_timeout: int = 30
    
    # === إعدادات Tor ===
    tor_enabled: bool = True
    tor_socks_port: int = 9050
    tor_control_port: int = 9051
    tor_password: str = ""
    obfs4_enabled: bool = True
    use_bridges: bool = True
    
    # === إعدادات Traffic Obfuscation ===
    obfuscation_method: str = "obfs4"  # obfs4, meek, snowflake
    mimic_protocol: str = "https"      # https, dns, webrtc
    packet_padding: bool = True
    timing_jitter: float = 0.3  # 30% jitter
    
    # === إعدادات Dead Man's Switch ===
    dms_enabled: bool = True
    inactivity_timeout_hours: int = 72
    auto_wipe_on_detection: bool = True
    wipe_passes: int = 7
    alert_channel: str = "signal"  # signal, telegram, email
    
    # === إعدادات التشفير ===
    encryption_layers: int = 3
    use_post_quantum: bool = False
    key_rotation_minutes: int = 15
    session_key_length: int = 32  # 256 bit
    
    # === إعدادات الهوية الاصطناعية ===
    identity_rotation_hours: int = 24
    browser_fingerprint_rotation: bool = True
    timezone_spoofing: bool = True
    
    # === مسارات التخزين ===
    data_dir: Path = Path("./data/opsec")
    logs_dir: Path = Path("./logs")
    temp_dir: Path = Path("./temp")
    
    def __post_init__(self):
        """إنشاء المسارات اللازمة"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # التحقق من الأمان
        if self.environment == Environment.PRODUCTION:
            assert not self.simulation_mode, "Production mode requires simulation_mode=False"
            assert not self.lab_mode, "Production mode requires lab_mode=False"
            print("⚠️ تحذير: التشغيل في وضع الإنتاج - تأكد من وجود تفويض كتابي!")


# إنشاء الإعدادات الافتراضية
config = OPSECConfig()