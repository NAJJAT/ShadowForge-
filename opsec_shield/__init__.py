"""
OPSEC Shield - طبقة الإخفاء وحماية الهوية
للأغراض الأكاديمية واختبار الأمان الداخلي للشركة فقط
"""

from .anonymization.vpn_chain_manager import VPNChainManager, VPNHop, VPNProvider
from .anonymization.tor_controller import TorController
from .anonymization.traffic_obfuscator import TrafficObfuscator
from .anonymization.identity_rotator import IdentityRotator
from .encryption.triple_layer_crypto import TripleLayerEncryption
from .encryption.key_manager import KeyManager
from .anti_forensics.dead_mans_switch import DeadMansSwitch
from .anti_forensics.secure_wipe import SecureWipe
from .synthetic_identity.identity_generator import SyntheticIdentity

__version__ = "1.0.0"
__all__ = [
    "VPNChainManager",
    "VPNHop", 
    "VPNProvider",
    "TorController",
    "TrafficObfuscator",
    "IdentityRotator",
    "TripleLayerEncryption",
    "KeyManager",
    "DeadMansSwitch",
    "SecureWipe",
    "SyntheticIdentity",
]