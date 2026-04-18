"""
Pattern Extractor - استخراج الأنماط من البيانات
"""

import re
from collections import Counter
from typing import List, Dict

class PatternExtractor:
    """يستخرج أنماطاً متكررة من السجلات"""
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        pattern = r'https?://[^\s]+'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_ips(text: str) -> List[str]:
        pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_common_errors(errors: List[str]) -> Dict:
        return dict(Counter(errors).most_common(5))