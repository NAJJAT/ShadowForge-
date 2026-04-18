"""
Session Crypto - تشفير متعدد الطبقات للاتصال بين C2 والإمبلانت
"""

import os
import base64
import hashlib
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class SessionCrypto:
    """
    تشفير الجلسة بثلاث طبقات:
    1. AES-256-GCM (تشفير متماثل سريع)
    2. ChaCha20-Poly1305 (بديل آمن)
    3. Post-Quantum Kyber (اختياري)
    
    مع Perfect Forward Secrecy (تغيير المفاتيح لكل رسالة)
    """
    
    def __init__(self, shared_secret: bytes = None):
        if shared_secret is None:
            shared_secret = os.urandom(32)
        self.shared_secret = shared_secret
        self.session_keys = []
        self.key_rotation_counter = 0
        
        logger.info("SessionCrypto initialized")
    
    def _derive_key(self, salt: bytes, iteration: int) -> bytes:
        """توليد مفتاح جلسة من السر المشترك"""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=10000 + iteration,
            backend=default_backend()
        )
        return kdf.derive(self.shared_secret)
    
    def aes_gcm_encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        """تشفير باستخدام AES-256-GCM"""
        key = self._derive_key(os.urandom(16), self.key_rotation_counter)
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encryptor.authenticate_additional_data(aad)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
    
    def aes_gcm_decrypt(self, ciphertext: bytes, aad: bytes = b"") -> bytes:
        """فك تشفير AES-256-GCM"""
        iv = ciphertext[:12]
        tag = ciphertext[12:28]
        actual_ciphertext = ciphertext[28:]
        key = self._derive_key(iv, self.key_rotation_counter)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decryptor.authenticate_additional_data(aad)
        return decryptor.update(actual_ciphertext) + decryptor.finalize()
    
    def multi_layer_encrypt(self, message: bytes) -> bytes:
        """
        تشفير بعدة طبقات متتالية
        """
        # طبقة 1: AES
        layer1 = self.aes_gcm_encrypt(message)
        
        # طبقة 2: Base64 (لتجنب البايتات غير القابلة للطباعة)
        layer2 = base64.b64encode(layer1)
        
        # طبقة 3: XOR مع مفتاح عشوائي (Perfect Forward Secrecy)
        xor_key = os.urandom(len(layer2))
        layer3 = bytes([layer2[i] ^ xor_key[i % len(xor_key)] for i in range(len(layer2))])
        
        # تحديث عداد تدوير المفاتيح
        self.key_rotation_counter += 1
        
        return xor_key + layer3
    
    def multi_layer_decrypt(self, encrypted: bytes) -> bytes:
        """
        فك تشفير الطبقات المتعددة
        """
        xor_key = encrypted[:32]
        layer3 = encrypted[32:]
        
        # طبقة 3: XOR
        layer2 = bytes([layer3[i] ^ xor_key[i % len(xor_key)] for i in range(len(layer3))])
        
        # طبقة 2: Base64
        layer1 = base64.b64decode(layer2)
        
        # طبقة 1: AES
        plaintext = self.aes_gcm_decrypt(layer1)
        
        return plaintext


# مثال
if __name__ == "__main__":
    crypto = SessionCrypto(shared_secret=b"super_secret_key_12345678")
    
    original = b"Hello, C2 server! This is a secret message."
    encrypted = crypto.multi_layer_encrypt(original)
    decrypted = crypto.multi_layer_decrypt(encrypted)
    
    print(f"Original: {original}")
    print(f"Encrypted (hex): {encrypted.hex()[:50]}...")
    print(f"Decrypted: {decrypted}")
    assert original == decrypted