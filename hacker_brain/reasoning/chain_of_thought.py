"""
Chain of Thought - سلسلة التفكير أثناء الاستغلال
تسجيل وتحليل كل خطوة تفكيرية أثناء اكتشاف واستغلال الثغرات
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ThoughtType(Enum):
    """أنواع الأفكار"""
    OBSERVATION = "observation"      # ملاحظة
    ANALYSIS = "analysis"            # تحليل
    HYPOTHESIS = "hypothesis"        # فرضية
    TEST = "test"                    # اختبار
    RESULT = "result"                # نتيجة
    CONCLUSION = "conclusion"        # استنتاج
    INSIGHT = "insight"              # بصيرة
    CREATIVE = "creative"            # فكرة إبداعية
    NEXT_STEP = "next_step"          # خطوة تالية


@dataclass
class Thought:
    """فكرة واحدة في سلسلة التفكير"""
    type: ThoughtType
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "type": self.type.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "metadata": self.metadata,
        }


class ChainOfThought:
    """
    سلسلة التفكير - ReAct (Reasoning + Acting)
    
    مثال:
    [OBSERVATION] وجدت endpoint: /api/users/profile?id=123
    [ANALYSIS] هذا يُوحي بـ IDOR محتمل
    [HYPOTHESIS] جرب id=124 - ممكن أرى بيانات مستخدم آخر
    [TEST] أرسل: GET /api/users/profile?id=124
    [RESULT] 200 OK - بيانات مستخدم آخر ظهرت!
    [CONCLUSION] IDOR مؤكد. الآن السؤال: هل هو admin؟
    [NEXT] جرب id=1 (عادة admin)
    """
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"cot_{int(time.time())}"
        self.thoughts: List[Thought] = []
        self.current_hypothesis: Optional[str] = None
        self.finding_confidence: float = 0.0
        self.analysis_depth: int = 0
        
        logger.info(f"ChainOfThought initialized: {self.session_id}")
    
    def add_observation(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة ملاحظة"""
        return self._add_thought(ThoughtType.OBSERVATION, content, metadata)
    
    def add_analysis(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة تحليل"""
        self.analysis_depth += 1
        return self._add_thought(ThoughtType.ANALYSIS, content, metadata)
    
    def add_hypothesis(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة فرضية"""
        self.current_hypothesis = content
        return self._add_thought(ThoughtType.HYPOTHESIS, content, metadata)
    
    def add_test(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة اختبار"""
        return self._add_thought(ThoughtType.TEST, content, metadata)
    
    def add_result(self, content: str, success: bool = None, metadata: Dict = None) -> 'Thought':
        """إضافة نتيجة"""
        if success is not None:
            metadata = metadata or {}
            metadata["success"] = success
            if success:
                self.finding_confidence = min(1.0, self.finding_confidence + 0.2)
            else:
                self.finding_confidence = max(0.0, self.finding_confidence - 0.1)
        return self._add_thought(ThoughtType.RESULT, content, metadata)
    
    def add_conclusion(self, content: str, confidence: float = None, metadata: Dict = None) -> 'Thought':
        """إضافة استنتاج"""
        if confidence is not None:
            metadata = metadata or {}
            metadata["confidence"] = confidence
            self.finding_confidence = confidence
        return self._add_thought(ThoughtType.CONCLUSION, content, metadata)
    
    def add_insight(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة بصيرة (اكتشاف مهم)"""
        return self._add_thought(ThoughtType.INSIGHT, content, metadata)
    
    def add_creative_idea(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة فكرة إبداعية"""
        return self._add_thought(ThoughtType.CREATIVE, content, metadata)
    
    def add_next_step(self, content: str, metadata: Dict = None) -> 'Thought':
        """إضافة خطوة تالية"""
        return self._add_thought(ThoughtType.NEXT_STEP, content, metadata)
    
    def _add_thought(self, thought_type: ThoughtType, content: str, metadata: Dict = None) -> Thought:
        """إضافة فكرة إلى السلسلة"""
        thought = Thought(
            type=thought_type,
            content=content,
            metadata=metadata or {}
        )
        self.thoughts.append(thought)
        
        # تسجيل بالفورمات المطلوب
        log_msg = f"[{thought_type.value.upper()}] {content}"
        if metadata:
            log_msg += f" {metadata}"
        logger.info(log_msg)
        
        return thought
    
    def start_vulnerability_analysis(self, endpoint: str, initial_observation: str = None) -> 'Thought':
        """بدء تحليل ثغرة جديد"""
        obs = self.add_observation(
            f"Analyzing endpoint: {endpoint}",
            {"endpoint": endpoint}
        )
        
        if initial_observation:
            self.add_observation(initial_observation)
        
        return obs
    
    def analyze_potential_vulnerability(self, vuln_type: str, evidence: Dict) -> Dict:
        """
        تحليل ثغرة محتملة باستخدام سلسلة التفكير
        
        Returns:
            Dict: نتائج التحليل
        """
        self.add_analysis(f"Potential {vuln_type} vulnerability detected")
        
        # تحليل الأدلة
        for key, value in evidence.items():
            self.add_observation(f"Evidence: {key}={value}")
        
        # توليد فرضيات
        hypotheses = self._generate_hypotheses(vuln_type, evidence)
        
        for hypo in hypotheses:
            self.add_hypothesis(hypo)
        
        return {
            "vulnerability_type": vuln_type,
            "hypotheses": hypotheses,
            "confidence": self.finding_confidence,
        }
    
    def _generate_hypotheses(self, vuln_type: str, evidence: Dict) -> List[str]:
        """توليد فرضيات بناءً على نوع الثغرة"""
        hypotheses = []
        
        if vuln_type.lower() == "idor":
            hypotheses = [
                "Changing ID parameter may reveal other users' data",
                "Admin users might have ID=1 or other predictable values",
                "ID parameter might be vulnerable to IDOR in PUT/DELETE methods too"
            ]
        elif vuln_type.lower() == "sqli":
            hypotheses = [
                "Adding single quote might break SQL query",
                "Union-based injection could extract data",
                "Time-based blind injection may work if errors are hidden"
            ]
        elif vuln_type.lower() == "xss":
            hypotheses = [
                "Input might be reflected without sanitization",
                "Event handlers like onerror might bypass filters",
                "DOM-based XSS could be present in JavaScript"
            ]
        elif vuln_type.lower() == "ssrf":
            hypotheses = [
                "Can access internal metadata endpoints",
                "Localhost services might be reachable",
                "Internal network scanning could be possible"
            ]
        
        return hypotheses
    
    def record_exploit_chain(self, steps: List[Dict]) -> Dict:
        """
        تسجيل سلسلة الاستغلال الكاملة
        """
        self.add_insight("Starting exploit chain recording")
        
        for step in steps:
            self.add_test(
                step.get("description", "Executing step"),
                {"step_data": step.get("data")}
            )
            
            if step.get("result"):
                self.add_result(
                    step.get("result_description", "Step completed"),
                    success=step.get("success", True)
                )
        
        return {
            "total_steps": len(steps),
            "successful": sum(1 for s in steps if s.get("success", False)),
            "chain_complete": all(s.get("success", False) for s in steps),
        }
    
    def get_thought_chain(self) -> List[Dict]:
        """الحصول على سلسلة التفكير كاملة"""
        return [t.to_dict() for t in self.thoughts]
    
    def get_reasoning_summary(self) -> str:
        """الحصول على ملخص الاستدلال"""
        summary = []
        
        for thought in self.thoughts:
            if thought.type in [ThoughtType.CONCLUSION, ThoughtType.INSIGHT]:
                summary.append(f"• {thought.content}")
        
        return "\n".join(summary)
    
    def export_to_markdown(self) -> str:
        """تصدير سلسلة التفكير بصيغة Markdown"""
        md = f"# Chain of Thought Report\n"
        md += f"**Session ID:** {self.session_id}\n"
        md += f"**Created:** {datetime.fromtimestamp(self.thoughts[0].timestamp).isoformat() if self.thoughts else 'N/A'}\n"
        md += f"**Total Thoughts:** {len(self.thoughts)}\n"
        md += f"**Confidence:** {self.finding_confidence:.2f}\n\n"
        
        md += "## Thought Chain\n\n"
        md += "| # | Type | Timestamp | Content |\n"
        md += "|---|------|-----------|---------|\n"
        
        for i, thought in enumerate(self.thoughts):
            time_str = datetime.fromtimestamp(thought.timestamp).strftime("%H:%M:%S")
            md += f"| {i+1} | {thought.type.value} | {time_str} | {thought.content[:80]} |\n"
        
        md += "\n## Summary of Findings\n\n"
        md += self.get_reasoning_summary()
        
        return md
    
    def export_to_json(self) -> str:
        """تصدير بصيغة JSON"""
        return json.dumps({
            "session_id": self.session_id,
            "created_at": self.thoughts[0].timestamp if self.thoughts else None,
            "total_thoughts": len(self.thoughts),
            "confidence": self.finding_confidence,
            "thoughts": self.get_thought_chain(),
        }, indent=2)
    
    def clear(self):
        """مسح سلسلة التفكير"""
        self.thoughts = []
        self.current_hypothesis = None
        self.finding_confidence = 0.0
        self.analysis_depth = 0


# مثال استخدام - IDOR اكتشاف
if __name__ == "__main__":
    cot = ChainOfThought(session_id="idor_analysis_2024")
    
    print("\n" + "="*60)
    print("IDOR Vulnerability Analysis - Chain of Thought")
    print("="*60)
    
    # بدء التحليل
    cot.start_vulnerability_analysis("/api/users/profile?id=123")
    
    # الملاحظة الأولى
    cot.add_observation("Parameter 'id' is numeric and sequential")
    
    # التحليل
    cot.add_analysis("Sequential IDs often indicate IDOR vulnerability")
    
    # فرضية
    cot.add_hypothesis("Changing id=124 may show another user's profile")
    
    # اختبار
    cot.add_test("Sending GET /api/users/profile?id=124")
    
    # نتيجة
    cot.add_result("200 OK - Retrieved another user's data", success=True)
    
    # استنتاج مؤقت
    cot.add_conclusion("IDOR confirmed for regular users", confidence=0.8)
    
    # بصيرة
    cot.add_insight("Session token is not tied to user ID - IDOR may affect all users")
    
    # فكرة إبداعية
    cot.add_creative_idea("What if we try PUT instead of GET? Could modify admin data")
    
    # اختبار إضافي
    cot.add_test("PUT /api/users/profile?id=1 with new password")
    
    # نتيجة
    cot.add_result("200 OK - Admin password changed!", success=True)
    
    # استنتاج نهائي
    cot.add_conclusion("CRITICAL: Full account takeover possible", confidence=0.95)
    
    # خطوات تالية
    cot.add_next_step("Extract all user data using IDOR")
    cot.add_next_step("Check for similar patterns in other endpoints")
    
    # عرض النتيجة
    print("\n" + cot.export_to_markdown())
    
    print("\n" + "="*60)
    print("Reasoning Summary:")
    print("="*60)
    print(cot.get_reasoning_summary())