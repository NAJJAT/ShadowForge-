from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

app = FastAPI(title="RedTeam AI API", description="API for security testing")

class ScanRequest(BaseModel):
    url: str
    params: Optional[dict] = {}
    depth: int = 1

class ExploitRequest(BaseModel):
    vuln_type: str
    target: str
    parameter: str
    os_type: str = "linux"

@app.post("/api/v1/scan")
async def scan_target(request: ScanRequest):
    """مسح هدف معين"""
    from vulnerability_hunter.pattern_matching.web_vuln_scanner import WebVulnerabilityScanner
    
    scanner = WebVulnerabilityScanner()
    vulnerabilities = await scanner.scan_url(request.url, request.params)
    return {"vulnerabilities": [v.to_dict() for v in vulnerabilities]}

@app.post("/api/v1/exploit/build")
async def build_exploit(request: ExploitRequest):
    """بناء استغلال مخصص"""
    from exploit_developer.exploit_builder.from_vulnerability import ExploitBuilder
    
    builder = ExploitBuilder(simulation_mode=True)
    vuln_info = {
        "type": request.vuln_type,
        "url": request.target,
        "parameter": request.parameter,
        "os_type": request.os_type,
    }
    exploit = builder.build_from_vulnerability(vuln_info)
    return exploit.to_dict()

@app.get("/api/v1/status")
async def system_status():
    """حالة النظام"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "modules": ["opsec", "hunter", "exploit", "persistence", "c2", "learning"],
        "simulation_mode": True,
    }

@app.get("/api/v1/learning/stats")
async def learning_stats():
    """إحصائيات نظام التعلم الذاتي"""
    from self_learning.memory.experience_memory import ExperienceMemory
    
    memory = ExperienceMemory()
    return memory.get_statistics()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)