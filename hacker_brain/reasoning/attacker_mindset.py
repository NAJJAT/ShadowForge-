"""
Attacker Mindset - عقلية الهاكر المحترف
يُقلد سلسلة التفكير الفعلية للهاكر قبل كل قرار
"""

import logging
import random
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from core.config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def __init__(self):
    self.experience_level = settings.EXPERIENCE_LEVEL
    self.risk_threshold = settings.RISK_THRESHOLD
class RiskLevel(Enum):
    """مستويات المخاطر"""
    CRITICAL = "critical"      # خطر شديد - لا تنفذ
    HIGH = "high"              # خطر مرتفع - ابحث عن بديل
    MEDIUM = "medium"          # خطر متوسط - يمكن التنفيذ بحذر
    LOW = "low"                # خطر منخفض - آمن للتنفيذ
    NEGLIGIBLE = "negligible"  # خطر لا يُذكر


class ActionType(Enum):
    """أنواع الإجراءات"""
    RECON = "reconnaissance"      # استطلاع
    SCAN = "scanning"             # مسح
    EXPLOIT = "exploitation"      # استغلال
    PERSIST = "persistence"       # استمرارية
    PRIV_ESC = "privilege_escalation"  # رفع صلاحيات
    EXFIL = "exfiltration"        # تسريب بيانات
    CLEANUP = "cleanup"           # تنظيف الآثار


@dataclass
class ActionAnalysis:
    """تحليل إجراء قبل تنفيذه"""
    action: str
    action_type: ActionType
    efficiency_score: float  # 0-1 (أسرع طريقة؟)
    stealth_score: float     # 0-1 (احتمال عدم الاكتشاف)
    risk_level: RiskLevel
    alternatives: List[str]
    fallback_plan: str
    next_steps: List[str]
    estimated_time_seconds: int
    success_probability: float  # 0-1
    requires_privilege: bool = False
    requires_specific_os: Optional[str] = None


class AttackerMindset:
    """
    عقلية الهاكر - قبل كل إجراء، يسأل 5 أسئلة:
    1. هل هذه أسرع طريقة؟
    2. ما احتمال اكتشافي؟
    3. هل هناك طريقة أذكى؟
    4. ما الخطة البديلة لو فشل؟
    5. ماذا سأفعل بعد النتيجة؟
    """
    
    def __init__(self, simulation_mode: bool = True, experience_level: str = "expert"):
        self.simulation_mode = simulation_mode
        self.experience_level = experience_level  # novice, intermediate, expert, elite
        
        # سجل التفكير (Chain of Thought)
        self.thought_log: List[Dict] = []
        
        # المعرفة المتراكمة
        self.knowledge_base = self._load_knowledge_base()
        
        # إحصائيات
        self.decisions_made = 0
        self.successful_decisions = 0
        
        logger.info(f"AttackerMindset initialized (level={experience_level}, simulation={simulation_mode})")
    
    def _load_knowledge_base(self) -> Dict:
        """تحميل قاعدة المعرفة"""
        return {
            "recon_techniques": {
                "passive": ["dns_recon", "whois", "shodan", "crt_sh"],
                "active": ["port_scan", "service_scan", "vuln_scan"],
                "stealth": ["slow_scan", "decoy_scan", "fragmented_scan"],
            },
            "common_defenses": {
                "waf": ["Cloudflare", "AWS WAF", "ModSecurity", "F5"],
                "edr": ["CrowdStrike", "SentinelOne", "CarbonBlack", "Defender"],
                "ids": ["Snort", "Suricata", "Zeek"],
            },
            "bypass_techniques": {
                "waf": ["sql_injection_evasion", "xss_evasion", "encoding_chaining"],
                "edr": ["direct_syscalls", "unhook_ntdll", "sleep_obfuscation"],
                "av": ["polymorphic_code", "encrypted_payloads", "process_injection"],
            },
            "os_weaknesses": {
                "windows": ["eternalblue", "zerologon", "petitpotam"],
                "linux": ["dirty_pipe", "pwnkit", "dirty_cow"],
                "macos": ["shrootless", "mrt_exploit", "powerdir"],
            }
        }
    
    def think_before_act(self, proposed_action: str, context: Dict) -> ActionAnalysis:
        """
        التفكير قبل تنفيذ أي إجراء
        
        Args:
            proposed_action: الإجراء المقترح
            context: سياق الهجوم (الهدف، الصلاحيات، الدفاعات المكتشفة)
        
        Returns:
            ActionAnalysis: التحليل الكامل
        """
        logger.info(f"🤔 Thinking about: {proposed_action}")
        
        # تسجيل بداية التفكير
        thought_start = {
            "timestamp": time.time(),
            "action": proposed_action,
            "context": context,
            "thought_chain": []
        }
        
        # السؤال 1: هل هذه أسرع طريقة؟
        efficiency = self._evaluate_efficiency(proposed_action, context)
        thought_start["thought_chain"].append(f"Efficiency: {efficiency:.2f}")
        
        # السؤال 2: ما احتمال اكتشافي؟
        stealth, risk_level = self._evaluate_stealth(proposed_action, context)
        thought_start["thought_chain"].append(f"Stealth: {stealth:.2f}, Risk: {risk_level.value}")
        
        # السؤال 3: هل هناك طريقة أذكى؟
        alternatives = self._find_alternatives(proposed_action, context)
        thought_start["thought_chain"].append(f"Alternatives found: {len(alternatives)}")
        
        # السؤال 4: ما الخطة البديلة لو فشل؟
        fallback = self._plan_fallback(proposed_action, context)
        thought_start["thought_chain"].append(f"Fallback: {fallback[:50]}...")
        
        # السؤال 5: ماذا سأفعل بالنتيجة؟
        next_steps = self._plan_next_steps(proposed_action, context)
        thought_start["thought_chain"].append(f"Next steps: {len(next_steps)} planned")
        
        # حساب احتمال النجاح
        success_probability = self._calculate_success_probability(efficiency, stealth, context)
        
        # تحديد نوع الإجراء
        action_type = self._classify_action(proposed_action)
        
        # بناء التحليل النهائي
        analysis = ActionAnalysis(
            action=proposed_action,
            action_type=action_type,
            efficiency_score=efficiency,
            stealth_score=stealth,
            risk_level=risk_level,
            alternatives=alternatives,
            fallback_plan=fallback,
            next_steps=next_steps,
            estimated_time_seconds=self._estimate_time(proposed_action),
            success_probability=success_probability,
            requires_privilege=context.get("requires_admin", False),
            requires_specific_os=context.get("target_os")
        )
        
        # تسجيل التفكير
        thought_start["analysis"] = {
            "efficiency": efficiency,
            "stealth": stealth,
            "risk_level": risk_level.value,
            "success_probability": success_probability,
        }
        self.thought_log.append(thought_start)
        self.decisions_made += 1
        
        # اتخاذ القرار النهائي
        should_proceed = self._decide(analysis)
        
        if should_proceed:
            logger.info(f"✅ Decision: PROCEED with {proposed_action} (risk={risk_level.value})")
            self.successful_decisions += 1
        else:
            logger.warning(f"❌ Decision: ABORT {proposed_action} (risk too high)")
        
        analysis.success_probability = success_probability if should_proceed else 0
        
        return analysis
    
    def _evaluate_efficiency(self, action: str, context: Dict) -> float:
        """
        تقييم كفاءة الإجراء (هل هي أسرع طريقة؟)
        
        Returns:
            float: درجة الكفاءة (0-1، 1 = أسرع طريقة ممكنة)
        """
        # عوامل تؤثر على الكفاءة
        factors = {
            "complexity": 1.0,   # مدى تعقيد الإجراء
            "automation": 0.5,   # هل يمكن أتمتته؟
            "parallelizable": 0.5,  # هل يمكن تنفيذه بالتوازي؟
            "dependencies": 1.0,    # هل يعتمد على إجراءات أخرى؟
        }
        
        # تحليل الإجراء
        if "scan" in action.lower():
            factors["automation"] = 0.9
            factors["parallelizable"] = 0.9
        elif "exploit" in action.lower():
            factors["complexity"] = 0.7
            factors["dependencies"] = 0.6
        elif "bruteforce" in action.lower():
            factors["parallelizable"] = 0.8
            factors["efficiency"] = 0.5
        
        # حسب مستوى الخبرة
        experience_multipliers = {
            "novice": 0.6,
            "intermediate": 0.8,
            "expert": 1.0,
            "elite": 1.2,
        }
        exp_mult = experience_multipliers.get(self.experience_level, 1.0)
        
        # حساب الكفاءة
        efficiency = sum(factors.values()) / len(factors) * exp_mult
        return min(1.0, max(0.0, efficiency))
    
    def _evaluate_stealth(self, action: str, context: Dict) -> Tuple[float, RiskLevel]:
        """
        تقييم احتمالية الاكتشاف
        
        Returns:
            Tuple[float, RiskLevel]: (درجة التخفي, مستوى الخطر)
        """
        # البدء بدرجة تخفي عالية
        stealth = 1.0
        
        # عوامل تقلل التخفي
        detection_factors = {
            "noise_level": 1.0,      # كمية الضجيج الناتج
            "signature_detection": 1.0,  # قابلية الكشف بالتوقيعات
            "behavioral_anomaly": 1.0,   # هل السلوك غير طبيعي؟
            "requires_admin": 1.0,       # هل يحتاج صلاحيات عليا؟
            "touches_disk": 1.0,         # هل يكتب على القرص؟
            "uses_network": 1.0,         # هل يستخدم الشبكة؟
        }
        
        # تحليل الإجراء
        if "scan" in action.lower():
            if "slow" in action.lower():
                detection_factors["noise_level"] = 0.3
                detection_factors["signature_detection"] = 0.4
            else:
                detection_factors["noise_level"] = 0.8
                detection_factors["signature_detection"] = 0.7
        
        if "exploit" in action.lower():
            detection_factors["behavioral_anomaly"] = 0.9
            detection_factors["signature_detection"] = 0.8
        
        if "persistence" in action.lower():
            detection_factors["touches_disk"] = 0.9
            detection_factors["behavioral_anomaly"] = 0.7
        
        if "mimikatz" in action.lower():
            detection_factors["signature_detection"] = 0.95
        
        # الدفاعات الموجودة في الهدف
        defenses = context.get("detected_defenses", [])
        for defense in defenses:
            if defense.lower() in ["crowdstrike", "sentinelone", "carbonblack"]:
                detection_factors["signature_detection"] *= 1.2
                detection_factors["behavioral_anomaly"] *= 1.3
        
        # حساب درجة التخفي
        for factor, value in detection_factors.items():
            stealth *= (1 - value * 0.3)
        
        stealth = max(0.0, min(1.0, stealth))
        
        # تحديد مستوى الخطر
        if stealth < 0.2:
            risk = RiskLevel.CRITICAL
        elif stealth < 0.4:
            risk = RiskLevel.HIGH
        elif stealth < 0.7:
            risk = RiskLevel.MEDIUM
        elif stealth < 0.9:
            risk = RiskLevel.LOW
        else:
            risk = RiskLevel.NEGLIGIBLE
        
        return stealth, risk
    
    def _find_alternatives(self, action: str, context: Dict) -> List[str]:
        """
        إيجاد طرق بديلة أذكى
        
        Returns:
            List[str]: قائمة بالبدائل
        """
        alternatives = []
        
        # حسب نوع الإجراء
        if "scan" in action.lower():
            alternatives.extend([
                "use_passive_recon_instead",
                "scan_through_proxy_chain",
                "use_decoy_scanning",
                "scan_during_off_hours"
            ])
        
        if "bruteforce" in action.lower():
            alternatives.extend([
                "try_password_spraying",
                "check_default_credentials_first",
                "use_credential_stuffing",
                "try_phishing_instead"
            ])
        
        if "exploit" in action.lower():
            vuln_type = context.get("vulnerability_type", "")
            if "sqli" in vuln_type.lower():
                alternatives.append("try_time_based_blind_instead")
                alternatives.append("use_dns_exfiltration")
            elif "xss" in vuln_type.lower():
                alternatives.append("try_dom_based_xss")
                alternatives.append("use_cookie_stealing")
        
        # إضافة بدائل عامة
        alternatives.extend([
            "wait_for_better_opportunity",
            "escalate_privileges_first",
            "use_different_payload",
            "target_different_endpoint"
        ])
        
        # حسب مستوى الخبرة
        if self.experience_level in ["expert", "elite"]:
            alternatives.extend([
                "use_0day_instead",
                "bypass_defense_with_new_technique",
                "leverage_trusted_relationship"
            ])
        
        return list(set(alternatives))[:5]  # إرجاع 5 بدائل فريدة
    
    def _plan_fallback(self, action: str, context: Dict) -> str:
        """
        وضع خطة بديلة لو فشل الإجراء الحالي
        
        Returns:
            str: خطة الطوارئ
        """
        fallback_templates = {
            "scan": "If scan fails, switch to passive recon using OSINT sources",
            "exploit": "If exploit fails, try alternative vulnerability or use social engineering",
            "bruteforce": "If bruteforce fails, try credential harvesting from previous breaches",
            "persistence": "If persistence fails, use scheduled tasks instead of registry",
            "default": "Rollback to last stable state and reassess target"
        }
        
        template_key = "default"
        for key in fallback_templates:
            if key in action.lower():
                template_key = key
                break
        
        fallback = fallback_templates[template_key]
        
        # إضافة تفاصيل حسب السياق
        if context.get("detected_defenses"):
            fallback += f" considering detected defenses: {context['detected_defenses']}"
        
        return fallback
    
    def _plan_next_steps(self, action: str, context: Dict) -> List[str]:
        """
        تخطيط الخطوات التالية بعد الإجراء
        
        Returns:
            List[str]: قائمة بالخطوات التالية
        """
        next_steps = []
        
        if "scan" in action.lower():
            next_steps = [
                "analyze_scan_results",
                "identify_vulnerable_services",
                "prioritize_targets_by_criticality",
                "prepare_exploit_plan"
            ]
        elif "exploit" in action.lower():
            next_steps = [
                "verify_successful_exploitation",
                "establish_persistence",
                "dump_credentials",
                "lateral_movement_planning"
            ]
        elif "privilege_escalation" in action.lower():
            next_steps = [
                "verify_new_privileges",
                "disable_defense_mechanisms",
                "access_restricted_data",
                "create_hidden_admin_account"
            ]
        else:
            next_steps = [
                "document_findings",
                "update_knowledge_base",
                "clean_traces",
                "prepare_for_next_phase"
            ]
        
        return next_steps
    
    def _classify_action(self, action: str) -> ActionType:
        """تصنيف نوع الإجراء"""
        action_lower = action.lower()
        
        if any(x in action_lower for x in ["recon", "osint", "whois", "dns"]):
            return ActionType.RECON
        elif any(x in action_lower for x in ["scan", "nmap", "port"]):
            return ActionType.SCAN
        elif any(x in action_lower for x in ["exploit", "inject", "payload"]):
            return ActionType.EXPLOIT
        elif any(x in action_lower for x in ["persist", "backdoor", "implant"]):
            return ActionType.PERSIST
        elif any(x in action_lower for x in ["privilege", "escalate", "bypass"]):
            return ActionType.PRIV_ESC
        elif any(x in action_lower for x in ["exfil", "download", "steal"]):
            return ActionType.EXFIL
        else:
            return ActionType.CLEANUP
    
    def _estimate_time(self, action: str) -> int:
        """تقدير الوقت اللازم بالثواني"""
        time_estimates = {
            "fast_scan": 60,
            "full_scan": 600,
            "simple_exploit": 30,
            "complex_exploit": 300,
            "bruteforce": 3600,
            "password_spray": 300,
            "persistence": 120,
        }
        
        for key, estimate in time_estimates.items():
            if key in action.lower():
                return estimate
        
        return 180  # افتراضي 3 دقائق
    
    def _calculate_success_probability(self, efficiency: float, stealth: float, context: Dict) -> float:
        """حساب احتمالية النجاح"""
        base_prob = (efficiency + stealth) / 2
        
        # تعديل حسب السياق
        if context.get("detected_defenses"):
            base_prob *= 0.7
        
        if context.get("previous_success"):
            base_prob *= 1.2
        
        # حسب مستوى الخبرة
        experience_bonus = {
            "novice": 0.8,
            "intermediate": 0.9,
            "expert": 1.0,
            "elite": 1.1,
        }
        base_prob *= experience_bonus.get(self.experience_level, 1.0)
        
        return min(1.0, max(0.0, base_prob))
    
    def _decide(self, analysis: ActionAnalysis) -> bool:
        """
        اتخاذ القرار النهائي
        
        القاعدة: إذا كان الخطر HIGH أو CRITICAL، لا تنفذ
        """
        if analysis.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            return False
        
        if analysis.success_probability < 0.4:
            return False
        
        return True
    
    def reconsider(self, analysis: Dict) -> ActionAnalysis:
        """
        إعادة التفكير عندما يكون خطر الاكتشاف مرتفعاً
        """
        logger.info("🔄 Reconsidering due to high detection risk...")
        
        # بناء إجراء بديل
        original_action = analysis.get("action", "unknown")
        alternative_action = f"stealthy_{original_action}"
        
        context = {
            "detected_defenses": ["avoiding previous detection vectors"],
            "requires_stealth": True,
        }
        
        return self.think_before_act(alternative_action, context)
    
    def get_thought_log(self, last_n: int = None) -> List[Dict]:
        """الحصول على سجل التفكير"""
        if last_n:
            return self.thought_log[-last_n:]
        return self.thought_log
    
    def export_thought_log(self, format: str = "json") -> str:
        """تصدير سجل التفكير"""
        if format == "json":
            return json.dumps(self.thought_log, indent=2, default=str)
        
        text = "="*60 + "\n"
        text += "ATTACKER MINDSET - THOUGHT LOG\n"
        text += "="*60 + "\n\n"
        
        for i, thought in enumerate(self.thought_log):
            text += f"[THOUGHT {i+1}] {thought['action']}\n"
            text += f"  Time: {time.ctime(thought['timestamp'])}\n"
            for chain in thought.get('thought_chain', []):
                text += f"  → {chain}\n"
            text += "\n"
        
        return text
    
    def get_stats(self) -> dict:
        """إحصائيات العقل المدبر"""
        return {
            "decisions_made": self.decisions_made,
            "successful_decisions": self.successful_decisions,
            "success_rate": self.successful_decisions / self.decisions_made if self.decisions_made > 0 else 0,
            "experience_level": self.experience_level,
            "thought_log_entries": len(self.thought_log),
        }


# مثال الاستخدام
if __name__ == "__main__":
    mindset = AttackerMindset(simulation_mode=True, experience_level="expert")
    
    # سيناريو 1: فحص منفذ
    print("\n" + "="*60)
    print("Scenario 1: Port Scan")
    print("="*60)
    
    context = {
        "target": "192.168.1.100",
        "detected_defenses": ["basic_firewall"],
        "requires_admin": False,
    }
    
    analysis = mindset.think_before_act("nmap_full_port_scan", context)
    print(f"Decision: {'PROCEED' if analysis.success_probability > 0 else 'ABORT'}")
    print(f"Risk Level: {analysis.risk_level.value}")
    print(f"Success Probability: {analysis.success_probability:.2f}")
    print(f"Alternatives: {analysis.alternatives[:2]}")
    
    # سيناريو 2: استغلال في بيئة محمية
    print("\n" + "="*60)
    print("Scenario 2: Exploit with EDR Present")
    print("="*60)
    
    context = {
        "target": "10.0.0.50",
        "detected_defenses": ["CrowdStrike", "Windows Defender"],
        "vulnerability_type": "eternalblue",
        "requires_admin": True,
    }
    
    analysis = mindset.think_before_act("eternalblue_exploit", context)
    print(f"Decision: {'PROCEED' if analysis.success_probability > 0 else 'ABORT'}")
    print(f"Risk Level: {analysis.risk_level.value}")
    print(f"Stealth Score: {analysis.stealth_score:.2f}")
    print(f"Alternatives: {analysis.alternatives[:3]}")
    
    # عرض الإحصائيات
    print("\n" + "="*60)
    print("Statistics")
    print("="*60)
    stats = mindset.get_stats()
    for k, v in stats.items():
        print(f"{k}: {v}")
    
    # تصدير سجل التفكير
    print("\n" + mindset.export_thought_log())