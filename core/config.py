"""
Configuration Management - قراءة الإعدادات من .env باستخدام Pydantic
"""

from typing import List, Optional, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    إعدادات النظام المركزية - تقرأ من ملف .env
    جميع القيم الافتراضية آمنة (simulation mode)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # ==================== System Mode ====================
    SIMULATION_MODE: bool = Field(default=True, description="Safe mode – no real connections")
    PRODUCTION_MODE: bool = Field(default=False, description="Real execution – requires authorization")
    LAB_MODE: bool = Field(default=True, description="Restrict to lab domains only")
    DEBUG: bool = Field(default=False, description="Verbose logging")
    PROFILE: bool = Field(default=False, description="Enable performance profiling")

    # ==================== Authorization (Legal) ====================
    AUTHORIZED_ENGAGEMENT: bool = Field(default=False, description="Must be True for production mode")
    AUTHORIZATION_TOKEN: Optional[str] = Field(default=None, description="JWT or API token for authorization")
    CONTRACT_ID: Optional[str] = Field(default=None, description="Red team contract identifier")
    CLIENT_NAME: Optional[str] = Field(default=None, description="Authorized client name")

    @field_validator("PRODUCTION_MODE")
    @classmethod
    def validate_production_mode(cls, v: bool, info) -> bool:
        if v and not info.data.get("AUTHORIZED_ENGAGEMENT", False):
            raise ValueError("PRODUCTION_MODE requires AUTHORIZED_ENGAGEMENT=True")
        return v

    # ==================== Logging & Monitoring ====================
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(default="INFO")
    LOG_FORMAT: Literal["json", "console"] = Field(default="json")
    LOG_FILE: str = Field(default="./logs/redteam.log")
    METRICS_ENABLED: bool = Field(default=False)
    METRICS_PORT: int = Field(default=9090)

    # ==================== OPSEC Shield ====================
    # VPN Chain
    VPN_ENABLED: bool = Field(default=False)
    VPN_PROVIDERS: List[str] = Field(default=["protonvpn", "mullvad"])
    VPN_EXCLUDED_COUNTRIES: List[str] = Field(default=["US", "UK", "AU", "CA", "NZ"])
    VPN_CHAIN_LENGTH: int = Field(default=3, ge=1, le=5)
    VPN_ROTATION_INTERVAL_SECONDS: int = Field(default=3600, ge=60)

    # ProtonVPN
    PROTONVPN_USERNAME: Optional[str] = None
    PROTONVPN_PASSWORD: Optional[str] = None
    PROTONVPN_PLAN: Literal["free", "basic", "plus"] = "free"

    # Mullvad
    MULLVAD_ACCOUNT: Optional[str] = None

    # Tor
    TOR_ENABLED: bool = Field(default=False)
    TOR_SOCKS_PORT: int = Field(default=9050)
    TOR_CONTROL_PORT: int = Field(default=9051)
    TOR_PASSWORD: Optional[str] = None
    TOR_USE_BRIDGES: bool = Field(default=True)
    TOR_BRIDGES: str = Field(default="obfs4 192.95.36.142:443 C6A5B4E5...,obfs4 45.145.95.6:27015 E8D4B2F9...")

    # Traffic Obfuscation
    OBFUSCATION_METHOD: Literal["obfs4", "meek", "snowflake"] = Field(default="obfs4")
    MIMIC_PROTOCOL: Literal["https", "dns", "webrtc"] = Field(default="https")

    # Dead Man's Switch
    DMS_ENABLED: bool = Field(default=True)
    DMS_INACTIVITY_TIMEOUT_HOURS: int = Field(default=72)
    DMS_AUTO_WIPE: bool = Field(default=True)
    DMS_ALERT_CHANNEL: Literal["signal", "telegram", "email"] = Field(default="signal")
    SIGNAL_PHONE_NUMBER: Optional[str] = None
    SIGNAL_RECEIVER: Optional[str] = None

    # ==================== Hacker Brain ====================
    LLM_ENABLED: bool = Field(default=False)
    LLM_MODEL: str = Field(default="llama3")
    LLM_OLLAMA_URL: str = Field(default="http://localhost:11434")
    LLM_TEMPERATURE: float = Field(default=0.7, ge=0.0, le=1.0)

    EXPERIENCE_LEVEL: Literal["novice", "intermediate", "expert", "elite"] = Field(default="expert")
    RISK_THRESHOLD: float = Field(default=0.6, ge=0.0, le=1.0)

    # ==================== Vulnerability Hunter ====================
    SCANNER_CONCURRENT_REQUESTS: int = Field(default=10, ge=1, le=100)
    SCANNER_REQUEST_TIMEOUT: int = Field(default=30, ge=1)
    SCANNER_RATE_LIMIT: float = Field(default=0.0, description="0 = unlimited")
    SCANNER_RANDOM_DELAY_MIN: float = Field(default=0.1, ge=0.0)
    SCANNER_RANDOM_DELAY_MAX: float = Field(default=1.0, ge=0.0)

    SAFE_DOMAINS: List[str] = Field(default=[
        "localhost", "127.0.0.1", "192.168.", "10.0.", "172.16.",
        "test.", "example.com", "dvwa", "metasploitable"
    ])

    # ==================== Exploit Developer ====================
    ALLOW_EXPLOIT_EXECUTION: bool = Field(default=False, description="Really execute exploits on target")
    REVERSE_SHELL_IP: str = Field(default="127.0.0.1")
    REVERSE_SHELL_PORT: int = Field(default=4444, ge=1, le=65535)
    MSFVENOM_PATH: str = Field(default="msfvenom")

    # ==================== Backdoor Factory ====================
    PERSISTENCE_HIDE_FROM_USER: bool = Field(default=True)
    PERSISTENCE_USE_LEGITIMATE_NAMES: bool = Field(default=True)

    IMPLANT_BEACON_INTERVAL: int = Field(default=60, ge=5)
    IMPLANT_JITTER: float = Field(default=0.3, ge=0.0, le=1.0)
    IMPLANT_SLEEP_PATTERN: Literal["jittered", "fixed", "random"] = Field(default="jittered")
    IMPLANT_FILELESS: bool = Field(default=True)

    # ==================== C2 Channel ====================
    C2_ENABLED: bool = Field(default=False)
    C2_SERVER_HOST: str = Field(default="0.0.0.0")
    C2_SERVER_PORT: int = Field(default=8000)
    C2_SERVER_URL: str = Field(default="https://c2.internal.local")

    C2_FRONT_DOMAIN: str = Field(default="cloudflare.com")
    C2_REAL_DOMAIN: str = Field(default="your-c2-domain.com")

    DNS_TUNNEL_DOMAIN: str = Field(default="your-dns-domain.com")
    DNS_SERVER: str = Field(default="8.8.8.8")

    STEGANOGRAPHY_SOCIAL_ACCOUNT: str = Field(default="twitter@your_account")

    # ==================== Self-Learning ====================
    EXPERIENCE_DB_PATH: str = Field(default="./data/experiences.json")
    VECTOR_STORE_PATH: str = Field(default="./data/chroma_db")
    KNOWLEDGE_GRAPH_URI: str = Field(default="bolt://localhost:7687")
    KNOWLEDGE_GRAPH_USER: str = Field(default="neo4j")
    KNOWLEDGE_GRAPH_PASSWORD: str = Field(default="password")

    RL_ENABLED: bool = Field(default=False)
    RL_POLICY_NETWORK: Literal["simple", "pytorch"] = Field(default="simple")
    RL_REPLAY_BUFFER_SIZE: int = Field(default=10000)

    # ==================== Helper methods ====================
    @property
    def is_production_ready(self) -> bool:
        """Check if system is allowed to run in production mode."""
        return self.PRODUCTION_MODE and self.AUTHORIZED_ENGAGEMENT

    @property
    def vpn_provider_list(self) -> List[str]:
        """Parse comma-separated VPN providers."""
        if isinstance(self.VPN_PROVIDERS, str):
            return [p.strip() for p in self.VPN_PROVIDERS.split(",")]
        return self.VPN_PROVIDERS

    @property
    def safe_domains_list(self) -> List[str]:
        if isinstance(self.SAFE_DOMAINS, str):
            return [d.strip() for d in self.SAFE_DOMAINS.split(",")]
        return self.SAFE_DOMAINS

    @property
    def tor_bridges_list(self) -> List[str]:
        if not self.TOR_BRIDGES:
            return []
        return [b.strip() for b in self.TOR_BRIDGES.split(",")]


# إنشاء كائن الإعدادات لاستيراده في باقي الملفات
settings = Settings()