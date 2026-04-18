"""
Local LLM Integration - دمج نموذج لغوي محلي للتفكير المتقدم
يستخدم Ollama لتشغيل نماذج LLM محلياً (بدون إنترنت)
"""

import json
import logging
import subprocess
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from core.config import settings

logger = logging.getLogger(__name__)

def __init__(self):
    self.llm_enabled = settings.LLM_ENABLED
    self.model = settings.LLM_MODEL
    self.ollama_url = settings.LLM_OLLAMA_URL
    self.temperature = settings.LLM_TEMPERATURE
class LLMModel(Enum):
    """نماذج LLM المدعومة"""
    LLAMA3 = "llama3"
    MISTRAL = "mistral"
    PHI = "phi"
    CODGEMMA = "codgemma"
    DEEPSEEK_CODER = "deepseek-coder"


@dataclass
class LLMResponse:
    """استجابة من نموذج LLM"""
    content: str
    model: str
    response_time_ms: float
    tokens_generated: int
    raw_response: Dict = None


class LocalLLM:
    """
    دمج نموذج لغوي محلي (Ollama)
    
    يستخدم لـ:
    - تحليل الثغرات المعقدة
    - توليد استغلالات مخصصة
    - اتخاذ قرارات استراتيجية
    - فهم الكود المصدري
    """
    
    def __init__(self, model: str = "llama3", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
        self.is_available = self._check_availability()
        
        if self.is_available:
            logger.info(f"LocalLLM initialized: {model}")
        else:
            logger.warning(f"LocalLLM not available (Ollama not running). Install Ollama from https://ollama.ai")
    
    def _check_availability(self) -> bool:
        """فحص توفر Ollama"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def _ensure_model(self) -> bool:
        """التأكد من وجود النموذج"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                for m in models:
                    if m.get("name", "").startswith(self.model):
                        return True
            
            # تحميل النموذج إذا لم يكن موجوداً
            logger.info(f"Pulling model {self.model}...")
            subprocess.run(["ollama", "pull", self.model], check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to ensure model: {e}")
            return False
    
    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> LLMResponse:
        """
        توليد نص من النموذج
        
        Args:
            prompt: النص المُدخل
            system_prompt: تعليمات النظام
            temperature: درجة العشوائية (0-1)
        
        Returns:
            LLMResponse: استجابة النموذج
        """
        if not self.is_available:
            return LLMResponse(
                content="[LLM not available - install Ollama]",
                model=self.model,
                response_time_ms=0,
                tokens_generated=0
            )
        
        import time
        start_time = time.time()
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                return LLMResponse(
                    content=data.get("response", ""),
                    model=self.model,
                    response_time_ms=elapsed_ms,
                    tokens_generated=data.get("eval_count", 0),
                    raw_response=data
                )
            else:
                logger.error(f"LLM error: {response.status_code}")
                return LLMResponse(
                    content=f"Error: {response.status_code}",
                    model=self.model,
                    response_time_ms=elapsed_ms,
                    tokens_generated=0
                )
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=self.model,
                response_time_ms=0,
                tokens_generated=0
            )
    
    def analyze_vulnerability(self, vuln_description: str, code_context: str = None) -> Dict:
        """
        تحليل ثغرة باستخدام LLM
        
        Returns:
            Dict: تحليل الثغرة
        """
        prompt = f"""
        Analyze this vulnerability and provide:
        1. Vulnerability type
        2. Severity (Critical/High/Medium/Low)
        3. Exploitation difficulty (1-10)
        4. Potential impact
        5. Recommended fix
        
        Vulnerability: {vuln_description}
        """
        
        if code_context:
            prompt += f"\n\nCode context:\n{code_context}"
        
        response = self.generate(prompt, system_prompt="You are a cybersecurity expert. Respond in JSON format.")
        
        try:
            # محاولة استخراج JSON من الاستجابة
            content = response.content
            # البحث عن JSON في النص
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            "analysis": response.content,
            "model": self.model,
            "confidence": 0.7,
        }
    
    def generate_exploit_suggestion(self, vuln_type: str, target_details: Dict) -> str:
        """
        توليد اقتراح استغلال لثغرة محددة
        """
        prompt = f"""
        Generate a step-by-step exploitation plan for:
        Vulnerability Type: {vuln_type}
        Target Details: {json.dumps(target_details, indent=2)}
        
        Include:
        1. Prerequisites
        2. Step-by-step instructions
        3. Potential pitfalls
        4. Alternative approaches
        """
        
        response = self.generate(prompt, system_prompt="You are a red team expert. Provide practical, actionable advice.")
        return response.content
    
    def understand_code(self, code: str, language: str, question: str) -> str:
        """
        فهم وتحليل كود مصدري
        """
        prompt = f"""
        Language: {language}
        
        Code: