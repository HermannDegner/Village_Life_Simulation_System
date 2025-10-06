"""
Village Social System - 社会活動と噂システム
"""

import random
from typing import Dict, List, Any
from village_core import Villager, VillageEvent

class VillageSocialSystem:
    """村の社会システム"""
    
    def __init__(self, villagers: List[Villager], rumor_system=None):
        self.villagers = {v.name: v for v in villagers}
        self.rumor_system = rumor_system
    
    def conduct_social_activities(self) -> List[Dict[str, Any]]:
        """社会活動の実行"""
        events = []
        
        # 噂の伝播（確率的）
        if self.rumor_system and random.random() < 0.3:
            rumor_events = self._spread_rumors()
            events.extend(rumor_events)
        
        return events
    
    def _spread_rumors(self) -> List[Dict[str, Any]]:
        """噂の伝播"""
        events = []
        
        # ランダムな村人間で噂を伝播
        speakers = list(self.villagers.keys())
        for _ in range(random.randint(0, 2)):
            if len(speakers) >= 2:
                speaker = random.choice(speakers)
                possible_listeners = [v for v in speakers if v != speaker]
                if possible_listeners:  # 聞き手がいることを確認
                    listener = random.choice(possible_listeners)
                    
                    # 既存の噂から適当なものを選んで伝播
                    if self.rumor_system.active_rumors:
                        rumor = random.choice(self.rumor_system.active_rumors)
                        rumor_content = rumor.get_rumor_text()
                        events.append({
                            'type': VillageEvent.RUMOR_SPREAD,
                            'speaker': speaker,
                            'listener': listener,
                            'content': rumor_content
                        })
        
        return events
    
    def spread_hunting_rumor(self, hunter_name: str, success: bool, hunt_duration: float, difficulty: float):
        """狩猟に関する噂を広める"""
        if not self.rumor_system:
            return
        
        speaker = random.choice(list(self.villagers.keys()))
        
        if success:
            if hunt_duration < 3.0:
                rumor_templates = [
                    f"{hunter_name}は狩りが上手いらしい",
                    f"{hunter_name}は獲物を確実に仕留めるらしい",
                    f"{hunter_name}は狩猟の腕前がすごいらしい"
                ]
            else:
                rumor_templates = [
                    f"{hunter_name}は狩りに時間がかかるらしい"
                ]
        else:
            rumor_templates = [
                f"{hunter_name}は狩りが下手らしい",
                f"{hunter_name}はよく獲物を逃すらしい",
                f"{hunter_name}は狩猟が苦手らしい"
            ]
        
        rumor_content = random.choice(rumor_templates)
        confidence = random.uniform(0.6, 1.0)
        
        # 噂システムに登録
        if hasattr(self.rumor_system, 'add_rumor'):
            self.rumor_system.add_rumor(speaker, hunter_name, rumor_content, confidence)
    
    def spread_carpentry_rumor(self, carpenter_name: str, success: bool, project_name: str, quality: float = 0.0):
        """大工に関する噂を広める"""
        if not self.rumor_system:
            return
        
        speaker = random.choice(list(self.villagers.keys()))
        
        if success:
            if quality > 0.8:
                rumor_templates = [
                    f"{carpenter_name}の{project_name}は素晴らしい出来らしい",
                    f"{carpenter_name}は腕の良い職人らしい"
                ]
            else:
                rumor_templates = [
                    f"{carpenter_name}が{project_name}を完成させたらしい"
                ]
        else:
            rumor_templates = [
                f"{carpenter_name}の{project_name}は失敗したらしい"
            ]
        
        rumor_content = random.choice(rumor_templates)
        confidence = random.uniform(0.5, 0.9)
        
        if hasattr(self.rumor_system, 'add_rumor'):
            self.rumor_system.add_rumor(speaker, carpenter_name, rumor_content, confidence)
    
    def spread_care_rumor(self, caregiver_name: str, patient_name: str, success: bool, care_quality: float):
        """看病に関する噂を広める"""
        if not self.rumor_system:
            return
        
        speaker = random.choice(list(self.villagers.keys()))
        
        if success and care_quality > 0.7:
            rumor_templates = [
                f"{caregiver_name}は看病が上手らしい",
                f"{caregiver_name}は優しい人らしい",
                f"{caregiver_name}のおかげで{patient_name}が回復したらしい"
            ]
            rumor_content = random.choice(rumor_templates)
            confidence = random.uniform(0.6, 1.0)
            
            if hasattr(self.rumor_system, 'add_rumor'):
                self.rumor_system.add_rumor(speaker, caregiver_name, rumor_content, confidence)