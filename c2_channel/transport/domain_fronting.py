"""
Domain Fronting - استخدام CDN كواجهة أمامية
"""

import requests
import logging

logger = logging.getLogger(__name__)

class DomainFronting:
    """يستخدم CDN لإخفاء الوجهة الحقيقية"""
    
    def __init__(self, front_domain: str, real_host: str):
        self.front_domain = front_domain
        self.real_host = real_host
    
    def send(self, data: bytes) -> requests.Response:
        headers = {"Host": self.real_host}
        url = f"https://{self.front_domain}/"
        return requests.post(url, headers=headers, data=data, verify=False)