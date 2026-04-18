"""
Behavioral Mimic - محاكاة السلوك البشري
"""

import time
import random
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class BehavioralMimic:
    """
    يولد سلوكاً بشرياً طبيعياً:
    - نمط الكتابة (سرعة، أخطاء)
    - حركة الماوس
    - أوقات النشاط
    - أنماط التصفح
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.typing_speed_wpm = random.randint(40, 80)
        self.typing_accuracy = random.uniform(0.95, 0.99)
        self.active_hours = (9, 17)  # 9AM - 5PM
        logger.info("BehavioralMimic initialized")
    
    def generate_typing_pattern(self, text: str) -> List[float]:
        """
        محاكاة كتابة بشرية: تأخيرات عشوائية بين الحروف
        """
        delays = []
        for i, char in enumerate(text):
            # سرعة الكتابة تعطي تأخير أساسي
            base_delay = 60.0 / (self.typing_speed_wpm * 5)  # ثانية لكل حرف
            # إضافة تشويش
            jitter = random.uniform(0.7, 1.3)
            delay = base_delay * jitter
            # أخطاء كتابية نادرة (محاكاة)
            if random.random() > self.typing_accuracy:
                delay *= 2  # تأخير إضافي للتصحيح
            delays.append(delay)
        return delays
    
    def simulate_mouse_movement(self, start_x: int, start_y: int, end_x: int, end_y: int) -> List[tuple]:
        """
        محاكاة حركة ماوس غير خطية
        """
        steps = []
        duration = random.uniform(0.3, 1.0)  # ثانية
        num_steps = int(duration * 60)  # 60 نقطة في الثانية
        
        for i in range(num_steps):
            t = i / num_steps
            # حركة غير خطية (منحنى)
            x = start_x + (end_x - start_x) * t + random.uniform(-5, 5)
            y = start_y + (end_y - start_y) * t + random.uniform(-5, 5)
            steps.append((int(x), int(y)))
            time.sleep(duration / num_steps)
        return steps
    
    def is_active_hours(self) -> bool:
        """هل الوقت الحالي ضمن ساعات النشاط؟"""
        current_hour = time.localtime().tm_hour
        return self.active_hours[0] <= current_hour <= self.active_hours[1]
    
    def get_behavioral_profile(self) -> Dict:
        """الحصول على ملف سلوكي كامل"""
        return {
            "typing_speed_wpm": self.typing_speed_wpm,
            "typing_accuracy": self.typing_accuracy,
            "active_hours": self.active_hours,
            "mouse_trajectory": "nonlinear",
            "reading_speed": random.randint(200, 400),  # كلمة في الدقيقة
            "scroll_behavior": random.choice(["smooth", "jumpy", "steady"]),
        }


if __name__ == "__main__":
    mimic = BehavioralMimic()
    delays = mimic.generate_typing_pattern("Hello, world!")
    print(f"Typing delays: {[round(d,3) for d in delays[:5]]}...")
    print(f"Profile: {mimic.get_behavioral_profile()}")