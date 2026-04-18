"""
Experience Memory - ذاكرة طويلة المدى لتجارب الهجوم
تخزن كل تجربة وتصنفها للاسترجاع المستقبلي
"""

import json
import time
import hashlib
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from core.config import settings

logger = logging.getLogger(__name__)

def __init__(self):
    self.db_path = settings.EXPERIENCE_DB_PATH
class ExperienceOutcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"


@dataclass
class Experience:
    """تجربة هجوم كاملة"""
    id: str
    timestamp: float
    target_profile: Dict
    techniques_used: List[str]
    successful_exploits: List[Dict]
    failed_attempts: List[Dict]
    defenses_encountered: List[str]
    bypass_methods: List[str]
    total_time: float
    detection_events: List[Dict]
    outcome: ExperienceOutcome
    lessons_learned: str
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "target_profile": self.target_profile,
            "techniques_used": self.techniques_used,
            "successful_exploits": self.successful_exploits[:5],
            "failed_attempts": self.failed_attempts[:5],
            "defenses_encountered": self.defenses_encountered,
            "bypass_methods": self.bypass_methods,
            "total_time": self.total_time,
            "detection_events": len(self.detection_events),
            "outcome": self.outcome.value,
            "lessons_learned": self.lessons_learned[:200],
        }


class ExperienceMemory:
    """
    ذاكرة التجارب - تخزن وتستعيد التجارب السابقة
    
    الميزات:
    - تخزين تجارب الهجوم بنجاح/فشل
    - بحث عن تجارب مشابهة للوضع الحالي
    - تحليل الأنماط عبر التجارب المتعددة
    """
    
    def __init__(self, storage_path: str = "./data/experiences.json", simulation_mode: bool = True):
        self.storage_path = storage_path
        self.simulation_mode = simulation_mode
        self.experiences: List[Experience] = []
        self._load_experiences()
        
        logger.info(f"ExperienceMemory initialized with {len(self.experiences)} experiences")
    
    def _load_experiences(self):
        """تحميل التجارب من ملف"""
        import os
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for exp_data in data:
                        exp = Experience(
                            id=exp_data["id"],
                            timestamp=exp_data["timestamp"],
                            target_profile=exp_data["target_profile"],
                            techniques_used=exp_data["techniques_used"],
                            successful_exploits=exp_data["successful_exploits"],
                            failed_attempts=exp_data["failed_attempts"],
                            defenses_encountered=exp_data["defenses_encountered"],
                            bypass_methods=exp_data["bypass_methods"],
                            total_time=exp_data["total_time"],
                            detection_events=exp_data["detection_events"],
                            outcome=ExperienceOutcome(exp_data["outcome"]),
                            lessons_learned=exp_data["lessons_learned"],
                        )
                        self.experiences.append(exp)
            except Exception as e:
                logger.error(f"Failed to load experiences: {e}")
    
    def _save_experiences(self):
        """حفظ التجارب إلى ملف"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump([e.to_dict() for e in self.experiences], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save experiences: {e}")
    
    def record_experience(self, mission_data: Dict) -> Experience:
        """
        تسجيل تجربة جديدة بعد كل مهمة
        
        Args:
            mission_data: بيانات المهمة (من Mission Planner)
        
        Returns:
            Experience: التجربة المسجلة
        """
        # تحديد النتيجة
        if mission_data.get("success_rate", 0) >= 0.8:
            outcome = ExperienceOutcome.SUCCESS
        elif mission_data.get("success_rate", 0) >= 0.3:
            outcome = ExperienceOutcome.PARTIAL
        else:
            outcome = ExperienceOutcome.FAILURE
        
        # إنشاء تجربة
        exp_id = hashlib.md5(f"{mission_data.get('mission_id')}{time.time()}".encode()).hexdigest()[:12]
        
        experience = Experience(
            id=exp_id,
            timestamp=time.time(),
            target_profile=mission_data.get("target_profile", {}),
            techniques_used=mission_data.get("techniques_used", []),
            successful_exploits=mission_data.get("successful_exploits", []),
            failed_attempts=mission_data.get("failed_attempts", []),
            defenses_encountered=mission_data.get("defenses_encountered", []),
            bypass_methods=mission_data.get("bypass_methods", []),
            total_time=mission_data.get("total_time", 0),
            detection_events=mission_data.get("detection_events", []),
            outcome=outcome,
            lessons_learned=mission_data.get("lessons_learned", ""),
        )
        
        self.experiences.append(experience)
        self._save_experiences()
        
        logger.info(f"Recorded experience {exp_id} with outcome {outcome.value}")
        return experience
    
    def recall_similar(self, current_situation: Dict, k: int = 5) -> List[Experience]:
        """
        استرجاع تجارب مشابهة للوضع الحالي
        
        Args:
            current_situation: الوضع الحالي (هدف، دفاعات، إلخ)
            k: عدد التجارب المطلوبة
        
        Returns:
            List[Experience]: التجارب الأكثر تشابهاً
        """
        if not self.experiences:
            return []
        
        # حساب التشابه لكل تجربة
        scored = []
        for exp in self.experiences:
            score = self._calculate_similarity(exp, current_situation)
            scored.append((score, exp))
        
        # ترتيب حسب التشابه
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # إرجاع أفضل k تجربة
        return [exp for _, exp in scored[:k]]
    
    def _calculate_similarity(self, exp: Experience, situation: Dict) -> float:
        """
        حساب درجة التشابه بين تجربة ووضع حالي
        """
        score = 0.0
        weight = 0
        
        # 1. تشابه الهدف
        target_type = situation.get("target_type", "")
        if target_type and target_type in str(exp.target_profile):
            score += 1
        weight += 1
        
        # 2. تشابه الدفاعات
        defenses = set(situation.get("defenses", []))
        exp_defenses = set(exp.defenses_encountered)
        if defenses and exp_defenses:
            intersection = len(defenses & exp_defenses)
            union = len(defenses | exp_defenses)
            if union > 0:
                score += intersection / union
        weight += 1
        
        # 3. نجاح التجربة (التجارب الناجحة لها وزن أكبر)
        if exp.outcome == ExperienceOutcome.SUCCESS:
            score += 0.5
        elif exp.outcome == ExperienceOutcome.FAILURE:
            score -= 0.2
        weight += 0.5
        
        # 4. حداثة التجربة (التجارب الأحدث لها وزن أكبر)
        age_days = (time.time() - exp.timestamp) / 86400
        recency = max(0, 1 - age_days / 30)  # آخر 30 يوم
        score += recency * 0.3
        weight += 0.3
        
        return score / weight if weight > 0 else 0
    
    def get_statistics(self) -> Dict:
        """إحصائيات التجارب"""
        total = len(self.experiences)
        if total == 0:
            return {"total": 0}
        
        successes = sum(1 for e in self.experiences if e.outcome == ExperienceOutcome.SUCCESS)
        failures = sum(1 for e in self.experiences if e.outcome == ExperienceOutcome.FAILURE)
        partial = total - successes - failures
        
        # أكثر التقنيات نجاحاً
        tech_success = {}
        for exp in self.experiences:
            for tech in exp.techniques_used:
                if tech not in tech_success:
                    tech_success[tech] = {"success": 0, "total": 0}
                tech_success[tech]["total"] += 1
                if exp.outcome == ExperienceOutcome.SUCCESS:
                    tech_success[tech]["success"] += 1
        
        top_techniques = sorted(
            [(t, d["success"]/d["total"] if d["total"]>0 else 0) for t, d in tech_success.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "total": total,
            "successes": successes,
            "failures": failures,
            "partial": partial,
            "success_rate": successes / total if total > 0 else 0,
            "top_techniques": top_techniques,
        }
    
    def clear(self):
        """مسح جميع التجارب"""
        self.experiences = []
        self._save_experiences()
        logger.info("All experiences cleared")


# مثال
if __name__ == "__main__":
    memory = ExperienceMemory(simulation_mode=True)
    
    # تسجيل تجربة وهمية
    test_mission = {
        "mission_id": "test_001",
        "target_profile": {"type": "web_app", "framework": "php"},
        "techniques_used": ["sql_injection", "xss"],
        "successful_exploits": [{"type": "sql_injection", "impact": "data_leak"}],
        "failed_attempts": [],
        "defenses_encountered": ["waf"],
        "bypass_methods": ["encoding"],
        "total_time": 3600,
        "detection_events": [],
        "lessons_learned": "Use union-based injection for faster extraction",
        "success_rate": 0.9,
    }
    
    exp = memory.record_experience(test_mission)
    print(f"Recorded: {exp.id}")
    
    # استرجاع تجارب مشابهة
    situation = {"target_type": "web_app", "defenses": ["waf"]}
    similar = memory.recall_similar(situation, k=3)
    print(f"Found {len(similar)} similar experiences")
    
    print(f"Statistics: {memory.get_statistics()}")