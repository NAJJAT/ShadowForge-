"""
Reward Shaping - تشكيل المكافآت لتوجيه التعلم
"""

class RewardShaping:
    """يحسب المكافآت بناءً على نتائج الإجراءات"""
    
    @staticmethod
    def calculate(action_result: dict) -> float:
        reward = 0.0
        if action_result.get("success"):
            reward += 10.0
        if action_result.get("efficiency", 0) > 0.8:
            reward += 5.0
        if action_result.get("detected"):
            reward -= 20.0
        if action_result.get("time_taken", 0) < 60:
            reward += 2.0
        return reward