"""
Mission Planner - تخطيط المهام الهجومية
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MissionPhase(Enum):
    """مراحل المهمة"""
    RECONNAISSANCE = "reconnaissance"
    SCANNING = "scanning"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    PERSISTENCE = "persistence"
    CLEANUP = "cleanup"
    REPORTING = "reporting"


class MissionStatus(Enum):
    """حالة المهمة"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class MissionTask:
    """مهمة فرعية"""
    id: str
    name: str
    description: str
    phase: MissionPhase
    dependencies: List[str] = field(default_factory=list)
    estimated_time_seconds: int = 300
    status: MissionStatus = MissionStatus.PLANNED
    result: Any = None
    error: str = None
    started_at: float = None
    completed_at: float = None
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "phase": self.phase.value,
            "status": self.status.value,
            "estimated_time": self.estimated_time_seconds,
            "result": str(self.result) if self.result else None,
        }


@dataclass
class Mission:
    """مهمة كاملة"""
    id: str
    name: str
    target: str
    scope: List[str]
    tasks: List[MissionTask]
    status: MissionStatus = MissionStatus.PLANNED
    created_at: float = field(default_factory=time.time)
    started_at: float = None
    completed_at: float = None
    notes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "target": self.target,
            "scope": self.scope,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
        }


class MissionPlanner:
    """
    مخطط المهام - يخطط وينسق الهجمات
    """
    
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.missions: List[Mission] = []
        self.current_mission: Optional[Mission] = None
        self.task_execution_log: List[Dict] = []
        
        logger.info(f"MissionPlanner initialized")
    
    def create_mission(self, name: str, target: str, scope: List[str]) -> Mission:
        """
        إنشاء مهمة جديدة
        """
        mission_id = f"mission_{int(time.time())}"
        
        # إنشاء المهام تلقائياً حسب النطاق
        tasks = self._generate_tasks(scope, target)
        
        mission = Mission(
            id=mission_id,
            name=name,
            target=target,
            scope=scope,
            tasks=tasks,
        )
        
        self.missions.append(mission)
        logger.info(f"Mission created: {name} (ID: {mission_id})")
        
        return mission
    
    def _generate_tasks(self, scope: List[str], target: str) -> List[MissionTask]:
        """
        توليد المهام بناءً على النطاق
        """
        tasks = []
        task_id = 1
        
        # المرحلة 1: الاستطلاع
        if "recon" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Passive Reconnaissance",
                description="Gather information without touching target",
                phase=MissionPhase.RECONNAISSANCE,
                estimated_time_seconds=600,
            ))
            task_id += 1
            
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Active Reconnaissance",
                description="Active probing of target",
                phase=MissionPhase.RECONNAISSANCE,
                dependencies=["task_1"],
                estimated_time_seconds=900,
            ))
            task_id += 1
        
        # المرحلة 2: المسح
        if "scan" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Port Scanning",
                description="Scan for open ports",
                phase=MissionPhase.SCANNING,
                estimated_time_seconds=300,
            ))
            task_id += 1
            
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Service Detection",
                description="Identify running services",
                phase=MissionPhase.SCANNING,
                dependencies=[f"task_{task_id-1}"],
                estimated_time_seconds=600,
            ))
            task_id += 1
        
        # المرحلة 3: اكتشاف الثغرات
        if "vuln" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Vulnerability Scanning",
                description="Automated vulnerability scan",
                phase=MissionPhase.VULNERABILITY_ASSESSMENT,
                estimated_time_seconds=1200,
            ))
            task_id += 1
            
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Manual Vulnerability Verification",
                description="Verify and exploit vulnerabilities",
                phase=MissionPhase.VULNERABILITY_ASSESSMENT,
                dependencies=[f"task_{task_id-1}"],
                estimated_time_seconds=1800,
            ))
            task_id += 1
        
        # المرحلة 4: الاستغلال
        if "exploit" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Initial Exploitation",
                description="Gain initial access",
                phase=MissionPhase.EXPLOITATION,
                estimated_time_seconds=600,
            ))
            task_id += 1
            
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Privilege Escalation",
                description="Escalate to higher privileges",
                phase=MissionPhase.EXPLOITATION,
                dependencies=[f"task_{task_id-1}"],
                estimated_time_seconds=900,
            ))
            task_id += 1
        
        # المرحلة 5: ما بعد الاستغلال
        if "post" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Data Collection",
                description="Collect sensitive data",
                phase=MissionPhase.POST_EXPLOITATION,
                estimated_time_seconds=600,
            ))
            task_id += 1
            
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Lateral Movement",
                description="Move to other systems",
                phase=MissionPhase.POST_EXPLOITATION,
                dependencies=[f"task_{task_id-1}"],
                estimated_time_seconds=1200,
            ))
            task_id += 1
        
        # المرحلة 6: الاستمرارية
        if "persist" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Establish Persistence",
                description="Install backdoors",
                phase=MissionPhase.PERSISTENCE,
                estimated_time_seconds=300,
            ))
            task_id += 1
        
        # المرحلة 7: التنظيف
        if "cleanup" in scope or "all" in scope:
            tasks.append(MissionTask(
                id=f"task_{task_id}",
                name="Clean Traces",
                description="Remove evidence",
                phase=MissionPhase.CLEANUP,
                estimated_time_seconds=300,
            ))
            task_id += 1
        
        return tasks
    
    def start_mission(self, mission_id: str) -> bool:
        """
        بدء تنفيذ مهمة
        """
        for mission in self.missions:
            if mission.id == mission_id:
                self.current_mission = mission
                mission.status = MissionStatus.IN_PROGRESS
                mission.started_at = time.time()
                logger.info(f"Mission started: {mission.name}")
                return True
        
        logger.error(f"Mission {mission_id} not found")
        return False
    
    def execute_task(self, task_id: str, executor_func=None) -> Dict:
        """
        تنفيذ مهمة فرعية
        """
        if not self.current_mission:
            return {"error": "No active mission"}
        
        # البحث عن المهمة
        task = None
        for t in self.current_mission.tasks:
            if t.id == task_id:
                task = t
                break
        
        if not task:
            return {"error": f"Task {task_id} not found"}
        
        # التحقق من التبعيات
        for dep_id in task.dependencies:
            dep_task = None
            for t in self.current_mission.tasks:
                if t.id == dep_id:
                    dep_task = t
                    break
            if dep_task and dep_task.status != MissionStatus.COMPLETED:
                return {"error": f"Dependency not met: {dep_id}"}
        
        logger.info(f"Executing task: {task.name}")
        task.started_at = time.time()
        task.status = MissionStatus.IN_PROGRESS
        
        # تنفيذ المهمة
        if executor_func:
            try:
                result = executor_func(task)
                task.result = result
                task.status = MissionStatus.COMPLETED
                task.completed_at = time.time()
                
                self.task_execution_log.append({
                    "task_id": task_id,
                    "task_name": task.name,
                    "started": task.started_at,
                    "completed": task.completed_at,
                    "duration": task.completed_at - task.started_at,
                    "result": str(result)[:200],
                })
                
                logger.info(f"Task completed: {task.name}")
                return {"success": True, "result": result}
                
            except Exception as e:
                task.error = str(e)
                task.status = MissionStatus.FAILED
                logger.error(f"Task failed: {task.name} - {e}")
                return {"error": str(e)}
        else:
            # وضع المحاكاة
            import random
            time.sleep(random.uniform(1, 3))
            task.status = MissionStatus.COMPLETED
            task.completed_at = time.time()
            task.result = f"Simulated result for {task.name}"
            
            return {"success": True, "result": task.result, "simulated": True}
    
    def get_mission_status(self) -> Dict:
        """
        الحصول على حالة المهمة الحالية
        """
        if not self.current_mission:
            return {"error": "No active mission"}
        
        total = len(self.current_mission.tasks)
        completed = sum(1 for t in self.current_mission.tasks if t.status == MissionStatus.COMPLETED)
        failed = sum(1 for t in self.current_mission.tasks if t.status == MissionStatus.FAILED)
        in_progress = sum(1 for t in self.current_mission.tasks if t.status == MissionStatus.IN_PROGRESS)
        
        return {
            "mission_id": self.current_mission.id,
            "mission_name": self.current_mission.name,
            "target": self.current_mission.target,
            "status": self.current_mission.status.value,
            "progress": {
                "total": total,
                "completed": completed,
                "failed": failed,
                "in_progress": in_progress,
                "percentage": (completed / total * 100) if total > 0 else 0,
            },
            "elapsed_time": time.time() - self.current_mission.started_at if self.current_mission.started_at else 0,
        }
    
    def pause_mission(self) -> bool:
        """إيقاف المهمة مؤقتاً"""
        if self.current_mission:
            self.current_mission.status = MissionStatus.PAUSED
            logger.info(f"Mission paused: {self.current_mission.name}")
            return True
        return False
    
    def resume_mission(self) -> bool:
        """استئناف المهمة"""
        if self.current_mission and self.current_mission.status == MissionStatus.PAUSED:
            self.current_mission.status = MissionStatus.IN_PROGRESS
            logger.info(f"Mission resumed: {self.current_mission.name}")
            return True
        return False
    
    def complete_mission(self) -> Dict:
        """إنهاء المهمة"""
        if not self.current_mission:
            return {"error": "No active mission"}
        
        self.current_mission.status = MissionStatus.COMPLETED
        self.current_mission.completed_at = time.time()
        
        # إنشاء تقرير
        report = self.generate_report()
        
        logger.info(f"Mission completed: {self.current_mission.name}")
        
        return report
    
    def abort_mission(self, reason: str) -> bool:
        """إلغاء المهمة"""
        if self.current_mission:
            self.current_mission.status = MissionStatus.ABORTED
            self.current_mission.notes.append(f"Aborted: {reason}")
            logger.warning(f"Mission aborted: {self.current_mission.name} - {reason}")
            return True
        return False
    
    def generate_report(self) -> Dict:
        """توليد تقرير المهمة"""
        if not self.current_mission:
            return {"error": "No mission"}
        
        completed_tasks = [t for t in self.current_mission.tasks if t.status == MissionStatus.COMPLETED]
        
        return {
            "mission_name": self.current_mission.name,
            "target": self.current_mission.target,
            "status": self.current_mission.status.value,
            "started_at": self.current_mission.started_at,
            "completed_at": self.current_mission.completed_at,
            "duration_seconds": (self.current_mission.completed_at or time.time()) - (self.current_mission.started_at or time.time()),
            "tasks_completed": len(completed_tasks),
            "tasks_total": len(self.current_mission.tasks),
            "task_log": self.task_execution_log[-10:],  # آخر 10 مهام
            "notes": self.current_mission.notes,
        }
    
    def list_missions(self) -> List[Dict]:
        """عرض جميع المهام"""
        return [m.to_dict() for m in self.missions]


# مثال الاستخدام
if __name__ == "__main__":
    planner = MissionPlanner(simulation_mode=True)
    
    # إنشاء مهمة
    mission = planner.create_mission(
        name="Internal Network Assessment",
        target="192.168.1.0/24",
        scope=["recon", "scan", "vuln"]
    )
    
    print("\n" + "="*60)
    print("Mission Created")
    print("="*60)
    print(json.dumps(mission.to_dict(), indent=2))
    
    # بدء المهمة
    planner.start_mission(mission.id)
    
    # تنفيذ المهام
    for task in mission.tasks:
        print(f"\nExecuting: {task.name}")
        result = planner.execute_task(task.id)
        print(f"  Result: {result}")
    
    # عرض الحالة
    print("\n" + "="*60)
    print("Mission Status")
    print("="*60)
    status = planner.get_mission_status()
    print(json.dumps(status, indent=2))
    
    # إنهاء المهمة
    report = planner.complete_mission()
    print("\n" + "="*60)
    print("Mission Report")
    print("="*60)
    print(json.dumps(report, indent=2))