"""
Strategy Optimizer - تحسين الاستراتيجيات بناءً على التحليل التلوي
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class StrategyOptimizer:
    """
    يحسن الاستراتيجيات العامة بناءً على الأنماط المستخرجة
    """
    
    def __init__(self):
        self.strategies = {}
        logger.info("StrategyOptimizer initialized")
    
    def update_strategy(self, pattern: Dict):
        """تحديث استراتيجية بناءً على نمط جديد"""
        strategy_name = pattern.get("actionable", "").split()[0] if pattern.get("actionable") else "general"
        if strategy_name not in self.strategies:
            self.strategies[strategy_name] = []
        self.strategies[strategy_name].append(pattern)
        logger.info(f"Updated strategy: {strategy_name}")
    
    def get_best_strategy(self, context: Dict) -> List[str]:
        """الحصول على أفضل استراتيجية للسياق الحالي"""
        recommendations = []
        
        # بناءً على نوع الخادم
        if "IIS" in str(context):
            recommendations.append("Test path traversal first")
            recommendations.append("Check for .NET misconfigurations")
        
        if "CrowdStrike" in str(context):
            recommendations.append("Use in-memory .NET execution")
            recommendations.append("Avoid PowerShell")
        
        if context.get("target_size") == "small":
            recommendations.append("Password spraying")
            recommendations.append("Default credentials check")
        
        return recommendations
    
    def optimize_workflow(self, historical_data: List[Dict]) -> Dict:
        """تحسين سير العمل بناءً على البيانات التاريخية"""
        # تحليل المدة الزمنية للمهام
        durations = [m.get("duration", 0) for m in historical_data if m.get("duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # تحليل معدل النجاح لكل تقنية
        tech_success = {}
        for m in historical_data:
            for tech in m.get("techniques_used", []):
                if tech not in tech_success:
                    tech_success[tech] = {"success": 0, "total": 0}
                tech_success[tech]["total"] += 1
                if m.get("success_rate", 0) > 0.7:
                    tech_success[tech]["success"] += 1
        
        # ترتيب التقنيات حسب معدل النجاح
        ranked = sorted(
            [(t, d["success"]/d["total"] if d["total"]>0 else 0) for t, d in tech_success.items()],
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "average_mission_duration": avg_duration,
            "top_techniques": ranked[:5],
            "recommended_parallelism": 3 if avg_duration > 600 else 1,
        }


# مثال
if __name__ == "__main__":
    optimizer = StrategyOptimizer()
    
    pattern = {
        "pattern": "IIS servers often vulnerable to path traversal",
        "confidence": 0.87,
        "actionable": "Always test path traversal first on IIS targets"
    }
    optimizer.update_strategy(pattern)
    
    context = {"target_server": "IIS", "defenses": ["CrowdStrike"]}
    best = optimizer.get_best_strategy(context)
    print(f"Recommended strategies: {best}")