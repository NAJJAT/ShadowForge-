"""
Key Manager - إدارة المفاتيح التشفيرية (نسخة مبسطة باستخدام hashlib)
"""

import os
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)


class KeyManager:
    """
    يدير المفاتيح التشفيرية:
    - توليد مفاتيح عشوائية
    - استخلاص مفاتيح من كلمة مرور (باستخدام PBKDF2 من hashlib)
    - تدوير المفاتيح
    - تخزين آمن مؤقت
    """
    
    def __init__(self, master_password: bytes = None, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.master_key = None
        self.session_keys = []
        
        if master_password:
            self.master_key = self.derive_key(master_password, salt=b'fixed_salt_16bytes')
        
        logger.info("KeyManager initialized (using hashlib)")
    
    def generate_key(self, length: int = 32) -> bytes:
        """توليد مفتاح عشوائي"""
        return os.urandom(length)
    
    def derive_key(self, password: bytes, salt: bytes, iterations: int = 100000) -> bytes:
        """استخلاص مفتاح من كلمة مرور باستخدام hashlib.pbkdf2_hmac"""
        return hashlib.pbkdf2_hmac('sha256', password, salt, iterations, dklen=32)
    
    def fernet_key(self) -> bytes:
        """توليد مفتاح صالح لـ Fernet (base64 URL-safe)"""
        return base64.urlsafe_b64encode(os.urandom(32))
    
    def rotate_session_key(self) -> bytes:
        """تدوير مفتاح الجلسة (Perfect Forward Secrecy)"""
        new_key = self.generate_key(32)
        self.session_keys.append(new_key)
        if len(self.session_keys) > 10:
            self.session_keys.pop(0)
        logger.debug("Session key rotated")
        return new_key
    
    def get_current_session_key(self) -> bytes:
        """الحصول على مفتاح الجلسة الحالي"""
        if not self.session_keys:
            return self.rotate_session_key()
        return self.session_keys[-1]
    
    def clear_keys(self):
        """مسح جميع المفاتيح من الذاكرة"""
        self.master_key = None
        for i in range(len(self.session_keys)):
            self.session_keys[i] = b'\x00' * len(self.session_keys[i])
        self.session_keys.clear()
        logger.info("All keys cleared from memory")


if __name__ == "__main__":
    km = KeyManager(simulation_mode=True)
    key = km.generate_key()
    print(f"Generated key: {key.hex()[:20]}...")
    km.clear_keys()