"""
🏘️ VLSS 統合システム (簡易版) - integrated_village_simulation_simple.py

【👑 シンプル統合村シミュレーション】
現在利用可能なシ        print(f"統合村システム初期化 - {len(self.villagers)}人の村")テムを使っ        print("  SSD Core Engine統合完了")        print("\n統合村システム初期化完了！")合シミュレーション

統合内容:
- 🧠 意味圧ベース学習システム
- 🔨 大工システム (SSD + 意味圧)
- 🏘️ SSD Core Engine

使用方法: python integrated_village_simulation_simple.py
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# 利用可能なシステムのインポート
from village_ssd_adapter import VillageSSDAdapter
from village_meaning_pressure_system import VillageMeaningPressureSystem, ActivityType as MeaningActivityType
from meaning_pressure_carpentry_system import MeaningPressureCarpentrySystem, ConstructionRequest

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
                'hunting': random.uniform(0.8, 2.5),
                'caregiving': random.uniform(0.5, 1.8),
                'cooking': random.uniform(0.6, 2.0),
                'carpentry': random.uniform(0.4, 1.5),
                'social': random.uniform(0.3, 1.2),
            }

class VillageEvent(Enum):
    """村の出来事"""
    HUNTING_ACTIVITY = "hunting_activity"
    CARE_ACTIVITY = "care_activity"  
    COOKING_ACTIVITY = "cooking_activity"
    CONSTRUCTION_COMPLETED = "construction_completed"
    SOCIAL_INTERACTION = "social_interaction"
    EMERGENCY_SITUATION = "emergency_situation"

class SimpleIntegratedVillage:
    """シンプル統合村シミュレーション"""
    
    def __init__(self, population_size: int = 8):
        # 基本設定
        self.population_size = population_size
        self.current_day = 0
        self.village_events: List[Dict[str, Any]] = []
        self.food_storage = 5.0
        self.village_happiness = random.uniform(0.6, 0.8)
        
        # 統合システム初期化
        self.ssd_adapter = VillageSSDAdapter("simple_integrated_village")
        self.meaning_pressure_system = VillageMeaningPressureSystem()
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
        
        # 大工システムに村人を登録
        self.carpentry_system.initialize_carpentry_reputations(villager_names)
        
        # 意味圧システムに村人を初期化（自動的に管理される）
        # VillageMeaningPressureSystemは使用時に自動的に村人を追加
        
        print(f"🏘️ 統合村システム初期化 - {len(self.villagers)}人の村")
        for villager in self.villagers:
            print(f"  {villager.name} ({villager.personality}) - スキル平均: {sum(villager.skills.values())/len(villager.skills):.1f}")
        
        print("  🧠 意味圧ベース学習システム初期化完了")  
        print("  意味圧ベース大工システム初期化完了")
        print("  🏘️ SSD Core Engine統合完了")
        print("\\n🌟 統合村システム初期化完了！")
    
    def simulate_day(self) -> Dict[str, Any]:
        """1日のシミュレーション実行"""
        self.current_day += 1
        daily_events = []
        
        # 朝の活動（生産活動）
        morning_events = self._morning_activities()
        daily_events.extend(morning_events)
        
        # 午後の活動（社会活動・大工活動）
        afternoon_events = self._afternoon_activities()
        daily_events.extend(afternoon_events)
        
        # 夜の活動（回復）
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
    
    def _morning_activities(self) -> List[Dict[str, Any]]:
        """朝の活動（食料確保・料理）"""
        events = []
        
        # 狩猟活動シミュレーション
        hunting_events = self._simulate_hunting()
        events.extend(hunting_events)
        
        # 料理活動シミュレーション
        cooking_events = self._simulate_cooking()
        events.extend(cooking_events)
        
        return events
    
    def _simulate_hunting(self) -> List[Dict[str, Any]]:
        """狩猟活動シミュレーション"""
        events = []
        
        # 狩猟参加者選出
        available_hunters = [
            v for v in self.villagers 
            if v.energy > 0.4 and not v.injured and v.skills.get('hunting', 0) > 0.8
        ]
        
        if not available_hunters:
            return events
        
        # 上位スキル保持者を選出
        available_hunters.sort(key=lambda x: x.skills['hunting'], reverse=True)
        hunters = available_hunters[:3]  # 最大3人
        
        for hunter in hunters:
            # 意味圧ベース狩猟シミュレーション
            success_rate = min(0.9, hunter.skills['hunting'] * 0.3)
            success = random.random() < success_rate
            
            # 意味圧文脈作成
            hunting_context = {
                'success': success,
                'effectiveness': random.uniform(0.4, 0.9) if success else random.uniform(0.1, 0.4),
                'difficulty': random.uniform(0.3, 0.8),
                'innovation': False,
                'collaboration': len(hunters) > 1,
                'emergency': False,
                'village_wide_impact': False,
                'people_affected': 1,
                'creativity_required': random.random() < 0.2,
                'time_pressure': random.random() < 0.3,
                'resource_scarcity': self.food_storage < 2.0,
                'new_technique': False,
                'high_stakes': random.random() < 0.1,
                'mentor_present': random.random() < 0.2
            }
            
            # 意味圧ベース学習適用
            hunting_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                hunter.name, MeaningActivityType.HUNTING, hunting_context
            )
            
            # 結果処理
            if success:
                food_gained = random.uniform(1.0, 3.0)
                self.food_storage += food_gained
                hunter.energy -= 0.2
                
                events.append({
                    'type': VillageEvent.HUNTING_ACTIVITY,
                    'hunter': hunter.name,
                    'success': True,
                    'food_gained': food_gained,
                    'hunting_inertia': hunting_inertia
                })
            else:
                hunter.energy -= 0.3
                # 怪我のリスク
                if random.random() < 0.1:
                    hunter.injured = True
                    hunter.health -= 0.2
                
                events.append({
                    'type': VillageEvent.HUNTING_ACTIVITY,
                    'hunter': hunter.name,
                    'success': False,
                    'hunting_inertia': hunting_inertia
                })
        
        return events
    
    def _simulate_cooking(self) -> List[Dict[str, Any]]:
        """料理活動シミュレーション"""
        events = []
        
        # 料理需要判定
        if self.food_storage < 1.0 or random.random() > 0.6:
            return events
        
        # 料理担当者選出
        available_cooks = [
            v for v in self.villagers 
            if v.energy > 0.3 and not v.injured
        ]
        
        if not available_cooks:
            return events
        
        # 料理スキル上位者選択
        available_cooks.sort(key=lambda x: x.skills.get('cooking', 0), reverse=True)
        cook = available_cooks[0]
        
        # 料理成功判定
        success_rate = min(0.9, cook.skills['cooking'] * 0.4)
        success = random.random() < success_rate
        
        # 意味圧文脈作成
        cooking_context = {
            'success': success,
            'effectiveness': random.uniform(0.5, 0.9) if success else random.uniform(0.2, 0.5),
            'difficulty': random.uniform(0.2, 0.6),
            'innovation': random.random() < 0.3,
            'collaboration': False,
            'emergency': False,
            'village_wide_impact': True,  # 料理は村全体に影響
            'people_affected': len(self.villagers),
            'creativity_required': random.random() < 0.4,
            'time_pressure': random.random() < 0.2,
            'resource_scarcity': self.food_storage < 3.0,
            'new_technique': random.random() < 0.2 and success,
            'high_stakes': False,
            'mentor_present': random.random() < 0.1
        }
        
        # 意味圧ベース学習適用
        cooking_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
            cook.name, MeaningActivityType.COOKING, cooking_context
        )
        
        if success:
            ingredients_used = min(self.food_storage, random.uniform(1.0, 2.5))
            self.food_storage -= ingredients_used
            
            # 村全体の満足度向上
            self.village_happiness = min(1.0, self.village_happiness + 0.05)
            
            # 村人の満腹度回復
            for villager in self.villagers:
                villager.hunger = max(0.0, villager.hunger - 0.3)
            
            events.append({
                'type': VillageEvent.COOKING_ACTIVITY,
                'cook': cook.name,
                'success': True,
                'meal_quality': random.uniform(0.6, 0.9),
                'cooking_inertia': cooking_inertia,
                'ingredients_used': ingredients_used
            })
        
        return events
    
    def _afternoon_activities(self) -> List[Dict[str, Any]]:
        """午後の活動（大工・社会活動）"""
        events = []
        
        # 大工活動
        carpentry_events = self._conduct_carpentry()
        events.extend(carpentry_events)
        
        # 社会活動・看護
        social_events = self._simulate_social_care()
        events.extend(social_events)
        
        return events
    
    def _conduct_carpentry(self) -> List[Dict[str, Any]]:
        """大工活動の実行"""
        events = []
        
        # 建築需要の判定（低頻度）
        if random.random() > 0.3:
            return events
        
        # 大工担当者選出
        available_carpenters = [
            v for v in self.villagers 
            if v.energy > 0.4 and not v.injured
        ]
        
        if not available_carpenters:
            return events
        
        # 大工スキル上位者選択
        available_carpenters.sort(key=lambda x: x.skills.get('carpentry', 0), reverse=True)
        carpenter = available_carpenters[0]
        
        # 建築リクエスト生成
        construction_types = ["repair", "housing", "furniture"]
        construction_request = ConstructionRequest(
            requester_name=random.choice([v.name for v in self.villagers]),
            preferred_carpenter=carpenter.name,
            construction_type=random.choice(construction_types),
            urgency_level=random.uniform(0.2, 0.8),
            complexity=random.uniform(0.3, 0.7)
        )
        
        # 大工作業実行
        result = self.carpentry_system.execute_carpentry_with_meaning_pressure(
            carpenter.name, construction_request, self.meaning_pressure_system
        )
        
        # 結果処理
        if result['success']:
            # 村の品質向上
            self.village_happiness = min(1.0, self.village_happiness + 0.03)
            carpenter.energy -= 0.25
            
            events.append({
                'type': VillageEvent.CONSTRUCTION_COMPLETED,
                'carpenter': carpenter.name,
                'project': result['project_name'],
                'quality': result['quality'],
                'carpentry_inertia': result['carpentry_inertia']
            })
        
        return events
    
    def _simulate_social_care(self) -> List[Dict[str, Any]]:
        """社会活動・看護シミュレーション"""
        events = []
        
        # 怪我人・病人チェック
        patients = [v for v in self.villagers if v.injured or v.health < 0.7]
        
        if patients:
            # 看護担当者選出
            available_caregivers = [
                v for v in self.villagers 
                if not v.injured and v.energy > 0.3 and v.health > 0.7
            ]
            
            if available_caregivers:
                # 看護スキル上位者選択
                available_caregivers.sort(key=lambda x: x.skills.get('caregiving', 0), reverse=True)
                caregiver = available_caregivers[0]
                patient = patients[0]
                
                # 看護成功判定
                success_rate = min(0.9, caregiver.skills['caregiving'] * 0.5)
                success = random.random() < success_rate
                
                # 意味圧文脈作成
                care_context = {
                    'success': success,
                    'effectiveness': random.uniform(0.5, 0.9) if success else random.uniform(0.2, 0.5),
                    'difficulty': 0.8 if patient.injured else 0.5,
                    'innovation': False,
                    'collaboration': False,
                    'emergency': patient.injured,
                    'village_wide_impact': False,
                    'people_affected': 1,
                    'creativity_required': False,
                    'time_pressure': patient.injured,
                    'resource_scarcity': False,
                    'new_technique': False,
                    'high_stakes': patient.health < 0.3,
                    'mentor_present': False
                }
                
                # 意味圧ベース学習適用
                caregiving_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                    caregiver.name, MeaningActivityType.CAREGIVING, care_context
                )
                
                if success:
                    # 患者回復
                    patient.health = min(1.0, patient.health + 0.3)
                    if patient.injured and random.random() < 0.7:
                        patient.injured = False
                    
                    caregiver.energy -= 0.2
                    
                    events.append({
                        'type': VillageEvent.CARE_ACTIVITY,
                        'caregiver': caregiver.name,
                        'patient': patient.name,
                        'success': True,
                        'caregiving_inertia': caregiving_inertia
                    })
        
        # 社会的交流
        if random.random() < 0.4:
            # ランダムな社会活動
            social_participants = random.sample(self.villagers, min(3, len(self.villagers)))
            
            for participant in social_participants:
                social_context = {
                    'success': True,
                    'effectiveness': random.uniform(0.4, 0.8),
                    'difficulty': random.uniform(0.1, 0.4),
                    'innovation': False,
                    'collaboration': True,
                    'emergency': False,
                    'village_wide_impact': False,
                    'people_affected': len(social_participants),
                    'creativity_required': random.random() < 0.3,
                    'time_pressure': False,
                    'resource_scarcity': False,
                    'new_technique': False,
                    'high_stakes': False,
                    'mentor_present': False
                }
                
                social_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                    participant.name, MeaningActivityType.SOCIAL_COORDINATION, social_context
                )
                
                participant.energy -= 0.1
                self.village_happiness = min(1.0, self.village_happiness + 0.02)
            
            events.append({
                'type': VillageEvent.SOCIAL_INTERACTION,
                'participants': [p.name for p in social_participants],
                'social_benefit': 0.02 * len(social_participants)
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
            hunter_inertia = self.meaning_pressure_system.alignment_inertia[villager.name][MeaningActivityType.HUNTING]
            caregiving_inertia = self.meaning_pressure_system.alignment_inertia[villager.name][MeaningActivityType.CAREGIVING]  
            cooking_inertia = self.meaning_pressure_system.alignment_inertia[villager.name][MeaningActivityType.COOKING]
            social_inertia = self.meaning_pressure_system.alignment_inertia[villager.name][MeaningActivityType.SOCIAL_COORDINATION]
            
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
        print(f"  狩猟慣性: {stats['hunting_inertia']:.3f}")
        print(f"  💝 看護慣性: {stats['caregiving_inertia']:.3f}")  
        print(f"  🍳 料理慣性: {stats['cooking_inertia']:.3f}")
        print(f"  🤝 調整慣性: {stats['social_coordination_inertia']:.3f}")
        print(f"  熟練大工: {stats['skilled_carpenters']}名")
        print(f"  🏠 建物品質: {stats['building_quality']:.2f}")
        
        return stats

def demonstrate_simple_integrated_simulation():
    """シンプル統合シミュレーションデモ"""
    
    print("🏘️ === シンプル統合村システム デモンストレーション ===\\n")
    
    # システム初期化
    village = SimpleIntegratedVillage(population_size=8)
    
    # 初期状態表示
    print("【初期状態】")
    village.get_village_status()
    
    # 数日間のシミュレーション
    print(f"\\n🗓️ === 10日間シミュレーション開始 ===")
    
    for day in range(1, 11):
        print(f"\\n--- 第{day}日目 ---")
        
        daily_result = village.simulate_day()
        
        # 主要イベントの表示
        significant_events = [
            e for e in daily_result['events'] 
            if e['type'] in [VillageEvent.HUNTING_ACTIVITY, VillageEvent.COOKING_ACTIVITY, 
                           VillageEvent.CONSTRUCTION_COMPLETED, VillageEvent.CARE_ACTIVITY]
        ]
        
        if significant_events:
            for event in significant_events[:3]:  # 上位3イベント表示
                if event['type'] == VillageEvent.HUNTING_ACTIVITY:
                    result_text = "成功" if event['success'] else "失敗"
                    print(f"  {event['hunter']}の狩猟: {result_text}")
                elif event['type'] == VillageEvent.COOKING_ACTIVITY:
                    print(f"  🍳 {event['cook']}が料理 (品質: {event['meal_quality']:.2f})")
                elif event['type'] == VillageEvent.CONSTRUCTION_COMPLETED:
                    print(f"  {event['carpenter']}が{event['project']}完成")
                elif event['type'] == VillageEvent.CARE_ACTIVITY:
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
    if final_stats['social_coordination_inertia'] > 0.1:
        print(f"  🤝 社会調整: 平均慣性 {final_stats['social_coordination_inertia']:.3f}")
    
    print(f"\\n🏘️ 意味圧ベース学習 + SSD Core Engine により")
    print(f"   自然な役割分担と継続的な村の発展を実現！")

if __name__ == "__main__":
    demonstrate_simple_integrated_simulation()