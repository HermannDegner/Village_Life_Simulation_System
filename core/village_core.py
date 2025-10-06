"""
Village Core - 村システムの基本クラスと定数定義
"""

import random
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

@dataclass
class Villager:
    """村人データ"""
    name: str
    personality: str = "balanced"
    hunger: float = 0.0
    injury_severity: float = 0.0
    injury_days_remaining: int = 0
    severe_injury: bool = False
    daily_energy_limit: float = 8.0
    current_energy: float = 8.0
    fatigue_level: float = 0.0
    daily_work_log: Dict[str, float] = field(default_factory=dict)
    base_hunting_skill: float = field(default_factory=lambda: random.uniform(0.5, 2.5))

    def __post_init__(self):
        """初期化後の処理"""
        if not self.daily_work_log:
            self.daily_work_log = {
                'hunting': 0.0,
                'cooking': 0.0,
                'carpentry': 0.0,
                'caregiving': 0.0
            }

    def can_work(self, work_type: str, energy_required: float) -> bool:
        """作業可能かチェック"""
        if self.severe_injury:
            return False
        
        if self.injury_severity > 0.5 and work_type in ['hunting', 'carpentry']:
            return False
        
        return self.current_energy >= energy_required

    def consume_energy(self, work_type: str, energy_amount: float, work_duration: float):
        """エネルギー消費と疲労蓄積"""
        self.current_energy = max(0, self.current_energy - energy_amount)
        
        # 作業時間を記録
        if work_type in self.daily_work_log:
            self.daily_work_log[work_type] += work_duration
        
        # 疲労レベル更新（1日の作業時間に基づく）
        total_work_time = sum(self.daily_work_log.values())
        if total_work_time > 6.0:
            self.fatigue_level = min(1.0, (total_work_time - 6.0) / 4.0)
        else:
            self.fatigue_level = max(0.0, self.fatigue_level - 0.1)

    def reset_daily_work(self):
        """日次リセット"""
        self.current_energy = self.daily_energy_limit
        self.daily_work_log = {
            'hunting': 0.0,
            'cooking': 0.0, 
            'carpentry': 0.0,
            'caregiving': 0.0
        }

class VillageEvent(Enum):
    """村イベント種別"""
    HUNTING_SUCCESS = "hunting_success"
    HUNTING_FAILURE = "hunting_failure"
    MEAL_PREPARED = "meal_prepared"
    CONSTRUCTION_COMPLETED = "construction_completed"
    CARE_PROVIDED = "care_provided"
    RUMOR_SPREAD = "rumor_spread"
    EMERGENCY_SITUATION = "emergency_situation"
    SOCIAL_GATHERING = "social_gathering"