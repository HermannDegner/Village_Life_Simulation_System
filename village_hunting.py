"""
Village Hunting System - 狩猟システム
"""

import random
from typing import Dict, List, Any
from village_core import Villager, VillageEvent

class VillageHuntingSystem:
    """村の狩猟システム"""
    
    def __init__(self, villagers: List[Villager]):
        self.villagers = {v.name: v for v in villagers}
    
    def conduct_hunting(self, food_storage: float, meaning_pressure_system=None) -> List[Dict[str, Any]]:
        """狩猟活動の実行（エネルギー制限付き）"""
        events = []
        
        # 狩猟需要の判定
        if food_storage > 5.0:
            return events
        
        # エネルギー必要量設定
        energy_per_hunt = 2.5
        
        # 狩猟可能な村人を特定
        potential_hunters = []
        for name, villager in self.villagers.items():
            if villager.can_work('hunting', energy_per_hunt):
                hunting_skill = villager.base_hunting_skill
                potential_hunters.append((name, hunting_skill))
        
        if not potential_hunters:
            return events
        
        # スキルでソートし、上位の村人を選択
        potential_hunters.sort(key=lambda x: x[1], reverse=True)
        selected_hunters = potential_hunters[:min(3, len(potential_hunters))]
        
        for hunter_name, hunting_skill in selected_hunters:
            hunter = self.villagers[hunter_name]
            
            # 狩猟実行
            hunt_duration = random.uniform(2.0, 4.0)
            success_probability = min(0.9, hunting_skill / 3.0 + 0.3)
            
            if random.random() < success_probability:
                # 成功
                base_food = random.uniform(2.0, 4.0)
                skill_bonus = hunting_skill * 0.3
                food_gained = base_food + skill_bonus
                energy_consumption = energy_per_hunt * random.uniform(0.8, 1.2)
                
                hunter.consume_energy('hunting', energy_consumption, hunt_duration)
                
                events.append({
                    'type': VillageEvent.HUNTING_SUCCESS,
                    'hunter': hunter_name,
                    'prey': "小動物",
                    'food_gained': food_gained,
                    'energy_used': energy_consumption,
                    'hunt_duration': hunt_duration
                })
                
                # 成功時でも軽い怪我のリスク
                success_injury_risk = 0.03 + hunter.fatigue_level * 0.05
                severe_injury_risk = 0.005 + hunter.fatigue_level * 0.01
                
                if random.random() < severe_injury_risk:
                    self._injure_villager(hunter_name, severe=True)
                    events[-1]['severe_injury_occurred'] = True
                elif random.random() < success_injury_risk:
                    self._injure_villager(hunter_name)
                    events[-1]['injury_occurred'] = True
                
                # 意味圧システム更新
                if meaning_pressure_system:
                    hunting_context = {
                        'success': True,
                        'effectiveness': food_gained / 3.0,
                        'difficulty': 0.5,
                        'innovation': False
                    }
                    meaning_pressure_system.calculate_meaning_pressure(
                        hunter_name, 'HUNTING', hunting_context
                    )
            else:
                # 失敗
                energy_consumption = energy_per_hunt * random.uniform(1.0, 1.5)
                hunter.consume_energy('hunting', energy_consumption, hunt_duration)
                
                # 失敗時は怪我リスクが高い
                failure_injury_risk = 0.15 + hunter.fatigue_level * 0.1
                severe_injury_risk = 0.02 + hunter.fatigue_level * 0.03
                
                if random.random() < severe_injury_risk:
                    self._injure_villager(hunter_name, severe=True)
                elif random.random() < failure_injury_risk:
                    self._injure_villager(hunter_name)
                
                events.append({
                    'type': VillageEvent.HUNTING_FAILURE,
                    'hunter': hunter_name,
                    'reason': "獲物を逃した",
                    'energy_used': energy_consumption,
                    'hunt_duration': hunt_duration
                })
        
        return events
    
    def _injure_villager(self, villager_name: str, severe: bool = False):
        """村人を負傷させる"""
        villager = self.villagers[villager_name]
        
        if severe:
            villager.severe_injury = True
            villager.injury_severity = random.uniform(0.7, 1.0)
            villager.injury_days_remaining = random.randint(3, 7)
        else:
            villager.injury_severity = random.uniform(0.3, 0.7)
            villager.injury_days_remaining = random.randint(1, 3)