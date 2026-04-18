"""
Policy Network - شبكة عصبية لاتخاذ القرارات باستخدام التعلم المعزز
"""

import numpy as np
import logging
from typing import List, Tuple, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# محاولة استيراد PyTorch (اختياري)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    logger.warning("PyTorch not installed. Using simple rule-based policy.")


class SimplePolicyNetwork:
    """شبكة سياسات بسيطة (بدون PyTorch)"""
    
    def __init__(self, action_space: int = 10, state_dim: int = 20):
        self.action_space = action_space
        self.state_dim = state_dim
        # مصفوفة وزن عشوائية
        self.weights = np.random.randn(state_dim, action_space) * 0.01
        logger.info("SimplePolicyNetwork initialized")
    
    def predict(self, state: np.ndarray) -> int:
        """اختيار أفضل إجراء للحالة"""
        scores = np.dot(state, self.weights)
        return int(np.argmax(scores))
    
    def update(self, state: np.ndarray, action: int, reward: float, learning_rate: float = 0.01):
        """تحديث الأوزان بناءً على المكافأة"""
        grad = np.zeros_like(self.weights)
        grad[:, action] = state
        self.weights += learning_rate * reward * grad


class PyTorchPolicyNetwork:
    """شبكة سياسات باستخدام PyTorch"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 64):
        if not HAS_TORCH:
            raise ImportError("PyTorch not installed")
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )
        self.optimizer = optim.Adam(self.network.parameters(), lr=0.001)
        logger.info("PyTorchPolicyNetwork initialized")
    
    def predict(self, state: np.ndarray) -> int:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        probs = self.network(state_tensor)
        action = torch.multinomial(probs, 1).item()
        return action
    
    def update(self, states, actions, rewards):
        # تنفيذ تحديث باستخدام REINFORCE أو PPO
        pass


class PolicyNetwork:
    """واجهة موحدة لشبكة السياسات"""
    
    def __init__(self, state_dim: int = 20, action_dim: int = 10, use_pytorch: bool = False):
        self.use_pytorch = use_pytorch and HAS_TORCH
        if self.use_pytorch:
            self.network = PyTorchPolicyNetwork(state_dim, action_dim)
        else:
            self.network = SimplePolicyNetwork(action_dim, state_dim)
        logger.info(f"PolicyNetwork initialized (using {type(self.network).__name__})")
    
    def get_action(self, state: List[float]) -> int:
        return self.network.predict(np.array(state))
    
    def update(self, state: List[float], action: int, reward: float):
        if not self.use_pytorch:
            self.network.update(np.array(state), action, reward)


class RewardShaping:
    """تشكيل المكافآت لتوجيه التعلم"""
    
    @staticmethod
    def get_reward(action_result: Dict) -> float:
        """حساب المكافأة بناءً على نتيجة الإجراء"""
        reward = 0.0
        
        if action_result.get("success", False):
            reward += 10.0
        else:
            reward -= 5.0
        
        if action_result.get("detected", False):
            reward -= 15.0
        
        if action_result.get("time_taken", 0) < 60:
            reward += 2.0
        elif action_result.get("time_taken", 0) > 300:
            reward -= 3.0
        
        if action_result.get("privilege_escalated", False):
            reward += 20.0
        
        if action_result.get("persistence_established", False):
            reward += 15.0
        
        return reward


class ContinuousTrainer:
    """مدرب مستمر باستخدام التعلم المعزز"""
    
    def __init__(self, policy_network: PolicyNetwork, replay_buffer_size: int = 10000):
        self.policy = policy_network
        self.replay_buffer = []
        self.buffer_size = replay_buffer_size
        self.episode_rewards = []
        logger.info("ContinuousTrainer initialized")
    
    def add_experience(self, state: List[float], action: int, reward: float, next_state: List[float], done: bool):
        """إضافة تجربة إلى المخزن"""
        self.replay_buffer.append((state, action, reward, next_state, done))
        if len(self.replay_buffer) > self.buffer_size:
            self.replay_buffer.pop(0)
    
    def train_step(self, batch_size: int = 32):
        """تدريب على دفعة من التجارب"""
        if len(self.replay_buffer) < batch_size:
            return
        
        import random
        batch = random.sample(self.replay_buffer, batch_size)
        
        for state, action, reward, next_state, done in batch:
            self.policy.update(state, action, reward)
    
    def evaluate_on_benchmark(self, benchmark_env) -> float:
        """تقييم الأداء على بيئة معيارية"""
        total_reward = 0.0
        for _ in range(10):
            state = benchmark_env.reset()
            done = False
            while not done:
                action = self.policy.get_action(state)
                next_state, reward, done = benchmark_env.step(action)
                total_reward += reward
                state = next_state
        return total_reward / 10


# مثال
if __name__ == "__main__":
    policy = PolicyNetwork(state_dim=10, action_dim=5, use_pytorch=False)
    trainer = ContinuousTrainer(policy)
    
    # محاكاة تدريب
    for episode in range(10):
        state = [np.random.random() for _ in range(10)]
        action = policy.get_action(state)
        # محاكاة مكافأة
        reward = 1.0 if np.random.random() > 0.5 else -0.5
        trainer.add_experience(state, action, reward, state, done=False)
        trainer.train_step(batch_size=4)
        print(f"Episode {episode}: action={action}, reward={reward}")