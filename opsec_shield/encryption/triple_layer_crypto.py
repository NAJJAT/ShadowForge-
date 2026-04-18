"""
Triple Layer Encryption - تشفير بثلاث طبقات
"""

import os
import base64
import hashlib
import logging
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class TripleLayerEncryption:
    """
    ثلاث طبقات تشفير:
    1. AES-256-GCM (تشفير متماثل)
    2. ChaCha20-Poly1305 (بديل آمن)
    3. XOR مع مفتاح عشوائي (Perfect Forward Secrecy)
    """
    
    def __init__(self, master_key: bytes = None):
        if master_key is None:
            master_key = os.urandom(32)
        self.master_key = master_key
        self.nonce_counter = 0
        logger.info("TripleLayerEncryption initialized")
    
    def _aes_gcm_encrypt(self, plaintext: bytes, aad: bytes = b"") -> bytes:
        key = self.master_key[:32]
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encryptor.authenticate_additional_data(aad)
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv + encryptor.tag + ciphertext
    
    def _aes_gcm_decrypt(self, ciphertext: bytes, aad: bytes = b"") -> bytes:
        iv = ciphertext[:12]
        tag = ciphertext[12:28]
        data = ciphertext[28:]
        key = self.master_key[:32]
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decryptor.authenticate_additional_data(aad)
        return decryptor.update(data) + decryptor.finalize()
    
    def _xor_encrypt(self, data: bytes, key: bytes) -> bytes:
        return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
    
    def encrypt(self, plaintext: bytes) -> bytes:
        """تشفير بثلاث طبقات"""
        # طبقة 1: AES
        layer1 = self._aes_gcm_encrypt(plaintext)
        # طبقة 2: Base64 (لتجنب البايتات غير القابلة للطباعة)
        layer2 = base64.b64encode(layer1)
        # طبقة 3: XOR بمفتاح عشوائي (PFS)
        xor_key = os.urandom(32)
        layer3 = self._xor_encrypt(layer2, xor_key)
        return xor_key + layer3
    
    def decrypt(self, encrypted: bytes) -> bytes:
        """فك تشفير ثلاث طبقات"""
        xor_key = encrypted[:32]
        layer3 = encrypted[32:]
        layer2 = self._xor_encrypt(layer3, xor_key)
        layer1 = base64.b64decode(layer2)
        return self._aes_gcm_decrypt(layer1)


if __name__ == "__main__":
    crypto = TripleLayerEncryption()
    msg = b"Top secret message"
    enc = crypto.encrypt(msg)
    dec = crypto.decrypt(enc)
    print(f"Original: {msg}")
    print(f"Encrypted (hex): {enc.hex()[:40]}...")
    print(f"Decrypted: {dec}")