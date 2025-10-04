"""
🏘️ VLSS メインシステム - integrated_village_simulation.py

【👑 メイン統合村シミュレーション】
統合村生活シミュレーション - SSD Core Engine + 意味圧ベース学習統合版

統合内容:
- 🏹 狩猟システム (SSD + 意味圧)
- 💝 看護システム (SSD + 意味圧)
- 🍳 料理システム (SSD + 意味圧)  
- 🔨 大工システム (SSD + 意味圧)

使用方法: python integrated_village_simulation.py
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# 統合システムのインポート
from village_ssd_adapter import VillageSSDAdapter, update_alignment_inertia, manage_territory_relationship
from village_meaning_pressure_system import VillageMeaningPressureSystem, ActivityType as MeaningActivityType
from meaning_pressure_carpentry_system import MeaningPressureCarpentrySystem, ConstructionRequest, ConstructionType
from hunting_system import HuntingSystem, Prey
from relationship_care_system import RelationshipCareSystem, CareRequest
from cooking_integrated_village import IntegratedCookingSystem, CookingRequest

@dataclass
class Villager:
    """村人データ"""
    name: str
    personality: str = "balanced"
    health: float = 1.0
    hunger: float = 0.3
    energy: float = 1.0
    injured: bool = False
    skills: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.skills:
            self.skills = {
                'hunting': random.uniform(0.5, 2.5),
                'caregiving': random.uniform(0.2, 1.8),
                'cooking': random.uniform(0.3, 2.0),
                'carpentry': random.uniform(0.2, 1.5),
            }

class VillageEvent(Enum):
    """村の出来事"""
    HUNTING_SUCCESS = "hunting_success"
    HUNTING_FAILURE = "hunting_failure"  
    CARE_PROVIDED = "care_provided"
    MEAL_PREPARED = "meal_prepared"
    CONSTRUCTION_COMPLETED = "construction_completed"
    EMERGENCY_SITUATION = "emergency_situation"
    INNOVATION_ACHIEVED = "innovation_achieved"

class IntegratedVillageSimulation:
    """統合村シミュレーション - 意味圧ベース + SSD Core Engine"""
    
    def __init__(self, population_size: int = 8):
        # 基本設定
        self.population_size = population_size
        self.current_day = 0
        self.village_events: List[Dict[str, Any]] = []
        self.food_storage = 0.0
        self.village_happiness = random.uniform(0.5, 0.8)
        
        # 統合システム初期化
        self.ssd_adapter = VillageSSDAdapter("integrated_village_system")
        self.meaning_pressure_system = VillageMeaningPressureSystem()
        
        # 各活動システム初期化
        self.hunting_system = HuntingSystem()
        self.care_system = RelationshipCareSystem()
        self.cooking_system = IntegratedCookingSystem()  
        self.carpentry_system = MeaningPressureCarpentrySystem()
        
        # 村人生成
        self.villagers = self._generate_villagers()
        
        # システム初期化
        self._initialize_systems()
    
    def _generate_villagers(self) -> List[Villager]:
        """多様な性格の村人を生成"""
        personalities = ["aggressive", "brave", "competitive", "caring", "gentle", "helpful", "social", "cooperative"]
        names = ["アキラ", "タケシ", "ユウ", "アカネ", "ハナ", "タロウ", "サクラ", "ケン"]
        
        villagers = []
        for i in range(self.population_size):
            villager = Villager(
                name=names[i % len(names)],
                personality=personalities[i % len(personalities)]
            )
            villagers.append(villager)
        
        return villagers
    
    def _initialize_systems(self):
        """各システムの初期化"""
        villager_names = [v.name for v in self.villagers]
        
        # 各システムに村人を登録
        self.hunting_system.initialize_hunters(villager_names)
        self.care_system.initialize_caregivers(villager_names)
        self.cooking_system.initialize_cooks(villager_names)
        self.carpentry_system.initialize_carpentry_reputations(villager_names)
        
        # 意味圧システムに村人登録
        for villager in self.villagers:
            self.meaning_pressure_system.initialize_villager(
                villager.name, villager.personality, villager.skills
            )
        
        print(f"🏘️ 統合村システム初期化 - {len(self.villagers)}人の村")
        for villager in self.villagers:
            hunting_skill = villager.skills.get('hunting', 1.0)
            print(f"  {villager.name} ({villager.personality}) - 狩猟スキル: {hunting_skill:.1f}")
        
        print("  🍳 料理システム統合完了")
        print("  🧠 意味圧ベース学習システム初期化完了")  
        print("  🔨 意味圧ベース大工システム初期化完了")
        print("\\n🌟 統合村システム初期化完了！")
    
    def simulate_day(self) -> Dict[str, Any]:
        """1日のシミュレーション実行"""
        self.current_day += 1
        daily_events = []
        
        # 朝の活動（生産活動）
        morning_events = self._morning_production_activities()
        daily_events.extend(morning_events)
        
        # 午後の活動（社会活動・緊急対応）
        afternoon_events = self._afternoon_social_activities()
        daily_events.extend(afternoon_events)
        
        # 夜の活動（休息・回復）
        evening_events = self._evening_recovery()
        daily_events.extend(evening_events)
        
        # 日次統計計算
        daily_stats = self._calculate_daily_stats()
        
        # イベント記録
        self.village_events.extend(daily_events)
        
        return {
            'day': self.current_day,
            'events': daily_events,
            'stats': daily_stats,
            'villagers': len(self.villagers),
            'food_storage': self.food_storage,
            'happiness': self.village_happiness
        }
    
    def _morning_production_activities(self) -> List[Dict[str, Any]]:
        """朝の生産活動"""
        events = []
        
        # 狩猟活動
        hunting_events = self._conduct_hunting()
        events.extend(hunting_events)
        
        # 料理活動
        cooking_events = self._conduct_cooking()
        events.extend(cooking_events)
        
        # 大工活動
        carpentry_events = self._conduct_carpentry()
        events.extend(carpentry_events)
        
        return events
    
    def _conduct_hunting(self) -> List[Dict[str, Any]]:
        """狩猟活動の実行"""
        events = []
        
        # 狩猟参加者選出（エネルギーがある村人）
        available_hunters = [
            v.name for v in self.villagers 
            if v.energy > 0.4 and not v.injured and v.skills.get('hunting', 0) > 0.5
        ]
        
        if not available_hunters:
            return events
        
        # 2-3人のチームで狩猟
        team_size = min(3, len(available_hunters))
        hunters = random.sample(available_hunters, team_size)
        
        # 獲物選択
        available_prey = [p for p in self.hunting_system.available_prey.values() if p.base_quantity > 0]
        if not available_prey:
            return events
        
        prey = random.choice(available_prey)
        
        # 狩猟実行
        for hunter_name in hunters:
            result = self.hunting_system.execute_hunt_with_meaning_pressure(
                hunter_name, prey, self.meaning_pressure_system
            )
            
            # 結果処理
            if result['success']:
                self.food_storage += result['food_gained']
                self._update_villager_energy(hunter_name, -0.2)
                
                events.append({
                    'type': VillageEvent.HUNTING_SUCCESS,
                    'hunter': hunter_name,
                    'prey': prey.name,
                    'food_gained': result['food_gained'],
                    'hunting_inertia': result['hunting_inertia']
                })
            else:
                self._update_villager_energy(hunter_name, -0.3)
                # 失敗時怪我のリスク
                if random.random() < 0.1:
                    self._injure_villager(hunter_name)
                
                events.append({
                    'type': VillageEvent.HUNTING_FAILURE,
                    'hunter': hunter_name,
                    'prey': prey.name
                })
        
        return events
    
    def _conduct_cooking(self) -> List[Dict[str, Any]]:
        """料理活動の実行"""
        events = []
        
        # 料理需要の判定
        if self.food_storage < 2.0 or random.random() < 0.6:
            return events
        
        # 料理担当者選出
        available_cooks = [
            v.name for v in self.villagers 
            if v.energy > 0.3 and not v.injured
        ]
        
        if not available_cooks:
            return events
        
        # 料理担当者（スキルベース選択）
        cook_scores = []
        for name in available_cooks:
            cooking_skill = next(v.skills.get('cooking', 0) for v in self.villagers if v.name == name)
            cook_scores.append((name, cooking_skill))
        
        cook_scores.sort(key=lambda x: x[1], reverse=True)
        cook_name = cook_scores[0][0]
        
        # 料理リクエスト生成
        cooking_request = CookingRequest(
            requester_name=cook_name,
            preferred_cook=cook_name,
            meal_type="daily_meal",
            complexity=random.uniform(0.3, 0.8),
            ingredients_available=min(self.food_storage, 3.0)
        )
        
        # 料理実行
        result = self.cooking_system.execute_cooking_with_meaning_pressure(
            cook_name, cooking_request, self.meaning_pressure_system
        )
        
        # 結果処理
        if result['success']:
            self.food_storage -= result['ingredients_used']
            # 村全体の満足度向上
            self.village_happiness = min(1.0, self.village_happiness + 0.05)
            
            # 村人の満腹度回復
            for villager in self.villagers:
                villager.hunger = max(0.0, villager.hunger - 0.3)
            
            events.append({
                'type': VillageEvent.MEAL_PREPARED,
                'cook': cook_name,
                'meal_quality': result['meal_quality'],
                'cooking_inertia': result['cooking_inertia'],
                'ingredients_used': result['ingredients_used']
            })
        
        return events
    
    def _conduct_carpentry(self) -> List[Dict[str, Any]]:
        """大工活動の実行"""
        events = []
        
        # 建築需要の判定（低頻度）
        if random.random() > 0.3:
            return events
        
        # 大工担当者選出
        available_carpenters = [
            v.name for v in self.villagers 
            if v.energy > 0.4 and not v.injured
        ]
        
        if not available_carpenters:
            return events
        
        # 大工スキルベース選択
        carpenter_scores = []
        for name in available_carpenters:
            carpentry_skill = next(v.skills.get('carpentry', 0) for v in self.villagers if v.name == name)
            carpenter_scores.append((name, carpentry_skill))
        
        carpenter_scores.sort(key=lambda x: x[1], reverse=True)
        carpenter_name = carpenter_scores[0][0]
        
        # 建築リクエスト生成
        construction_types = ["repair", "housing", "furniture"]
        construction_request = ConstructionRequest(
            requester_name=random.choice([v.name for v in self.villagers]),
            preferred_carpenter=carpenter_name,
            construction_type=random.choice(construction_types),
            urgency_level=random.uniform(0.2, 0.8),
            complexity=random.uniform(0.3, 0.7)
        )
        
        # 大工作業実行
        result = self.carpentry_system.execute_carpentry_with_meaning_pressure(
            carpenter_name, construction_request, self.meaning_pressure_system
        )
        
        # 結果処理
        if result['success']:
            # 村の建物品質向上
            self.village_happiness = min(1.0, self.village_happiness + 0.03)
            
            events.append({
                'type': VillageEvent.CONSTRUCTION_COMPLETED,
                'carpenter': carpenter_name,
                'project': result['project_name'],
                'quality': result['quality'],
                'carpentry_inertia': result['carpentry_inertia']
            })
        
        return events
    
    def _afternoon_social_activities(self) -> List[Dict[str, Any]]:
        """午後の社会活動"""
        events = []
        
        # 看護・介護活動
        care_events = self._conduct_caregiving()
        events.extend(care_events)
        
        # 緊急事態発生（低頻度）
        if random.random() < 0.05:
            emergency_events = self._handle_emergency()
            events.extend(emergency_events)
        
        return events
    
    def _conduct_caregiving(self) -> List[Dict[str, Any]]:
        """看護・介護活動"""
        events = []
        
        # 怪我人・病人のチェック
        patients = [v for v in self.villagers if v.injured or v.health < 0.7]
        
        if not patients:
            return events
        
        # 看護担当者選出
        available_caregivers = [
            v.name for v in self.villagers 
            if not v.injured and v.energy > 0.3 and v.health > 0.7
        ]
        
        if not available_caregivers:
            return events
        
        # 看護スキルベース選択
        caregiver_scores = []
        for name in available_caregivers:
            caregiving_skill = next(v.skills.get('caregiving', 0) for v in self.villagers if v.name == name)
            caregiver_scores.append((name, caregiving_skill))
        
        caregiver_scores.sort(key=lambda x: x[1], reverse=True)
        caregiver_name = caregiver_scores[0][0]
        
        # 患者への看護
        for patient in patients[:2]:  # 最大2人まで
            care_request = CareRequest(
                patient_name=patient.name,
                caregiver_preference=caregiver_name,
                urgency_level=0.8 if patient.injured else 0.5,
                care_complexity=0.7 if patient.injured else 0.4
            )
            
            result = self.care_system.execute_care_with_meaning_pressure(
                caregiver_name, care_request, self.meaning_pressure_system
            )
            
            # 結果処理
            if result['success']:
                # 患者の回復
                patient.health = min(1.0, patient.health + 0.3)
                if patient.injured and random.random() < 0.7:
                    patient.injured = False
                
                events.append({
                    'type': VillageEvent.CARE_PROVIDED,
                    'caregiver': caregiver_name,
                    'patient': patient.name,
                    'care_quality': result['care_quality'],
                    'caregiving_inertia': result['caregiving_inertia']
                })
        
        return events
    
    def _handle_emergency(self) -> List[Dict[str, Any]]:
        """緊急事態対応"""
        events = []
        
        emergency_types = ["accident", "illness", "disaster"]
        emergency_type = random.choice(emergency_types)
        
        if emergency_type == "accident":
            # 事故で村人が怪我
            victim = random.choice(self.villagers)
            self._injure_villager(victim.name)
            
            events.append({
                'type': VillageEvent.EMERGENCY_SITUATION,
                'emergency_type': 'accident',
                'affected': victim.name
            })
        
        elif emergency_type == "illness":
            # 病気で健康度低下
            victim = random.choice(self.villagers)
            victim.health = max(0.2, victim.health - 0.4)
            
            events.append({
                'type': VillageEvent.EMERGENCY_SITUATION, 
                'emergency_type': 'illness',
                'affected': victim.name
            })
        
        return events
    
    def _evening_recovery(self) -> List[Dict[str, Any]]:
        """夜の回復活動"""
        events = []
        
        # 村人の基本的な回復
        for villager in self.villagers:
            # エネルギー回復
            villager.energy = min(1.0, villager.energy + 0.4)
            
            # 空腹度上昇
            villager.hunger = min(1.0, villager.hunger + 0.1)
            
            # 軽微な健康回復
            if villager.health < 1.0 and not villager.injured:
                villager.health = min(1.0, villager.health + 0.1)
        
        return events
    
    def _update_villager_energy(self, name: str, change: float):
        """村人のエネルギー更新"""
        for villager in self.villagers:
            if villager.name == name:
                villager.energy = max(0.0, min(1.0, villager.energy + change))
                break
    
    def _injure_villager(self, name: str):
        """村人に怪我を負わせる"""
        for villager in self.villagers:
            if villager.name == name:
                villager.injured = True
                villager.health = max(0.1, villager.health - 0.3)
                break
    
    def _calculate_daily_stats(self) -> Dict[str, Any]:
        """日次統計の計算"""
        
        # 健康状態統計
        healthy_count = len([v for v in self.villagers if v.health > 0.7 and not v.injured])
        injured_count = len([v for v in self.villagers if v.injured])
        
        # スキル慣性平均
        hunting_inertias = []
        caregiving_inertias = []
        cooking_inertias = []
        social_coordination_inertias = []
        
        for villager in self.villagers:
            # 意味圧システムから慣性値取得
            hunter_inertia = self.meaning_pressure_system.get_alignment_inertia(villager.name, MeaningActivityType.HUNTING)
            caregiving_inertia = self.meaning_pressure_system.get_alignment_inertia(villager.name, MeaningActivityType.CAREGIVING)  
            cooking_inertia = self.meaning_pressure_system.get_alignment_inertia(villager.name, MeaningActivityType.COOKING)
            social_inertia = self.meaning_pressure_system.get_alignment_inertia(villager.name, MeaningActivityType.SOCIAL_COORDINATION)
            
            if hunter_inertia > 0:
                hunting_inertias.append(hunter_inertia)
            if caregiving_inertia > 0:
                caregiving_inertias.append(caregiving_inertia)
            if cooking_inertia > 0:
                cooking_inertias.append(cooking_inertia)
            if social_inertia > 0:
                social_coordination_inertias.append(social_inertia)
        
        # 熟練大工数
        skilled_carpenters = len([
            name for name, rep in self.carpentry_system.carpenter_reputations.items()
            if rep.specialization_known
        ])
        
        # 建物品質
        building_quality = sum(self.carpentry_system.village_buildings.values()) / len(self.carpentry_system.village_buildings)
        
        return {
            'day': self.current_day,
            'healthy_villagers': healthy_count,
            'injured_villagers': injured_count,
            'food_storage': self.food_storage,
            'village_happiness': self.village_happiness,
            'hunting_inertia': sum(hunting_inertias) / max(len(hunting_inertias), 1),
            'caregiving_inertia': sum(caregiving_inertias) / max(len(caregiving_inertias), 1),
            'cooking_inertia': sum(cooking_inertias) / max(len(cooking_inertias), 1),
            'social_coordination_inertia': sum(social_coordination_inertias) / max(len(social_coordination_inertias), 1),
            'skilled_carpenters': skilled_carpenters,
            'building_quality': building_quality
        }
    
    def get_village_status(self) -> Dict[str, Any]:
        """村の現在状況取得"""
        stats = self._calculate_daily_stats()
        
        print(f"\\n📊 村の概要:")
        print(f"  人口: {len(self.villagers)}人")
        print(f"  健康: {stats['healthy_villagers']}人, 負傷: {stats['injured_villagers']}人")
        print(f"  食料貯蔵: {self.food_storage:.1f}単位")
        print(f"  村の幸福度: {self.village_happiness:.2f}")
        
        print(f"\\n🧠 意味圧ベーススキル平均:")
        print(f"  🏹 狩猟慣性: {stats['hunting_inertia']:.3f}")
        print(f"  💝 看護慣性: {stats['caregiving_inertia']:.3f}")  
        print(f"  🍳 料理慣性: {stats['cooking_inertia']:.3f}")
        print(f"  🤝 調整慣性: {stats['social_coordination_inertia']:.3f}")
        print(f"  🔨 熟練大工: {stats['skilled_carpenters']}名")
        print(f"  🏠 建物品質: {stats['building_quality']:.2f}")
        
        return stats

def demonstrate_integrated_simulation():
    """統合シミュレーションデモ"""
    
    print("🏘️ === 統合村システム デモンストレーション ===\\n")
    
    # システム初期化
    village = IntegratedVillageSimulation(population_size=8)
    
    # 初期状態表示
    print("【初期状態】")
    village.get_village_status()
    
    # 数日間のシミュレーション
    print(f"\\n🗓️ === 7日間シミュレーション開始 ===")
    
    for day in range(1, 8):
        print(f"\\n--- 第{day}日目 ---")
        
        daily_result = village.simulate_day()
        
        # 主要イベントの表示
        significant_events = [
            e for e in daily_result['events'] 
            if e['type'] in [VillageEvent.HUNTING_SUCCESS, VillageEvent.MEAL_PREPARED, 
                           VillageEvent.CONSTRUCTION_COMPLETED, VillageEvent.CARE_PROVIDED]
        ]
        
        if significant_events:
            for event in significant_events[:3]:  # 上位3イベント表示
                if event['type'] == VillageEvent.HUNTING_SUCCESS:
                    print(f"  🏹 {event['hunter']}が{event['prey']}を狩猟成功 (+{event['food_gained']:.1f}食料)")
                elif event['type'] == VillageEvent.MEAL_PREPARED:
                    print(f"  🍳 {event['cook']}が食事準備 (品質: {event['meal_quality']:.2f})")
                elif event['type'] == VillageEvent.CONSTRUCTION_COMPLETED:
                    print(f"  🔨 {event['carpenter']}が{event['project']}完成 (品質: {event['quality']:.2f})")
                elif event['type'] == VillageEvent.CARE_PROVIDED:
                    print(f"  💝 {event['caregiver']}が{event['patient']}を看護")
        else:
            print("  📝 平穏な一日")
    
    # 最終状態
    print(f"\\n【最終状態】")
    final_stats = village.get_village_status()
    
    print(f"\\n🎯 === 統合システム効果 ===")
    print(f"📈 成長したスキル:")
    if final_stats['hunting_inertia'] > 0.1:
        print(f"  🏹 狩猟専門化: 平均慣性 {final_stats['hunting_inertia']:.3f}")
    if final_stats['cooking_inertia'] > 0.1:
        print(f"  🍳 料理専門化: 平均慣性 {final_stats['cooking_inertia']:.3f}")
    if final_stats['caregiving_inertia'] > 0.1:
        print(f"  💝 看護専門化: 平均慣性 {final_stats['caregiving_inertia']:.3f}")
    if final_stats['skilled_carpenters'] > 0:
        print(f"  🔨 大工専門化: {final_stats['skilled_carpenters']}名の熟練工")
    
    print(f"\\n🏘️ SSD Core Engine + 意味圧ベース学習により")
    print(f"   自然な役割分担と継続的な村の発展を実現！")

if __name__ == "__main__":
    demonstrate_integrated_simulation()