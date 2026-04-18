import json
import re
from typing import Any, Dict, List, Optional


class ResponseParser:
    """Extracts structured information from language-model responses."""

    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract the first JSON object found in text."""
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None

    @staticmethod
    def extract_code(text: str, language: Optional[str] = None) -> Optional[str]:
        """Extract code from a fenced code block."""
        if language:
            pattern = rf"```{re.escape(language)}\n(.*?)```"
        else:
            pattern = r"```(?:\w+)?\n(.*?)```"

        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else None

    @staticmethod
    def extract_security_findings(text: str) -> List[str]:
        """Extract likely security findings from text."""
        findings: List[str] = []
        keywords = [
            "vulnerability",
            "security issue",
            "weakness",
            "misconfiguration",
            "xss",
            "sql injection",
            "csrf",
            "exposed secret",
            "unsafe deserialization",
            "path traversal",
        ]

        for line in text.splitlines():
            normalized = line.strip().lower()
            if normalized and any(keyword in normalized for keyword in keywords):
                findings.append(line.strip())

        return findings

    @staticmethod
    def parse_decision(text: str) -> Dict[str, Any]:
        """Parse a defensive recommendation from text."""
        result: Dict[str, Any] = {
            "action": "review",
            "confidence": 0.0,
            "reasoning": text[:500].strip(),
        }

        lowered = text.lower()

        if "remediate" in lowered or "fix" in lowered:
            result["action"] = "remediate"
        elif "monitor" in lowered:
            result["action"] = "monitor"
        elif "contain" in lowered:
            result["action"] = "contain"
        elif "escalate" in lowered:
            result["action"] = "escalate"

        confidence_match = re.search(r"confidence[:\s]*(\d+(?:\.\d+)?)", lowered)
        if confidence_match:
            try:
                result["confidence"] = float(confidence_match.group(1))
            except ValueError:
                result["confidence"] = 0.0

        return result