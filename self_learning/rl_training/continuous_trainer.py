"""
Continuous Trainer - تدريب مستمر باستخدام RL
"""

import logging
from typing import List, Dict
from .policy_network import PolicyNetwork
from .reward_shaping import RewardShaping

logger = logging.getLogger(__name__)

class ContinuousTrainer:
    """يدرب الشبكة باستمرار على التجارب الجديدة"""
    
    def __init__(self, policy_network: PolicyNetwork):
        self.policy = policy_network
        self.reward_shaper = RewardShaping()
        self.experience_buffer = []
    
    def add_experience(self, state, action, reward, next_state):
        self.experience_buffer.append((state, action, reward, next_state))
        if len(self.experience_buffer) > 10000:
            self.experience_buffer.pop(0)
    
    def train_step(self, batch_size: int = 32):
        if len(self.experience_buffer) < batch_size:
            return
        import random
        batch = random.sample(self.experience_buffer, batch_size)
        for state, action, reward, next_state in batch:
            self.policy.update(state, action, reward)