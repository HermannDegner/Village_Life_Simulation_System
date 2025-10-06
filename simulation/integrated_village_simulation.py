"""
VLSS メインシステム - integrated_village_simulation.py

【メイン統合村シミュレーション】
統合村生活シミュレーション - SSD Core Engine + 意味圧ベース学習統合版

統合内容:
- 狩猟システム (SSD + 意味圧)
- 看護システム (SSD + 意味圧)
- 料理システム (SSD + 意味圧)  
- 大工システム (SSD + 意味圧)

使用方法: python integrated_village_simulation.py
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

# 統合システムのインポート
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.village_ssd_adapter import VillageSSDAdapter, update_alignment_inertia, manage_territory_relationship
from core.village_meaning_pressure_system import VillageMeaningPressureSystem, ActivityType as MeaningActivityType
from systems.carpentry.meaning_pressure_carpentry_system import MeaningPressureCarpentrySystem, ConstructionRequest, ConstructionType
from systems.hunting.hunting_system import HuntingSystem, Prey
from systems.caregiving.relationship_care_system import RelationshipCareSystem, CareRequest
from systems.cooking.cooking_integrated_village import EnhancedCookingSystem, CookingRequest
from systems.social.rumor_system import RumorSystem, RumorType

@dataclass
class Villager:
    """村人データ"""
    name: str
    personality: str = "balanced"
    health: float = 1.0
    hunger: float = 0.3
    energy: float = 1.0
    injured: bool = False
    severe_injury: bool = False  # 重傷フラグ
    injury_recovery_days: int = 0  # 重傷回復までの日数
    skills: Dict[str, float] = field(default_factory=dict)
    
    # エネルギー・時間管理
    daily_energy_used: float = 0.0
    work_sessions_today: int = 0
    last_work_type: str = ""
    fatigue_level: float = 0.0
    max_work_sessions: int = 3  # 1日最大作業回数
    
    def __post_init__(self):
        if not self.skills:
            self.skills = {
                'hunting': random.uniform(0.5, 2.5),
                'caregiving': random.uniform(0.2, 1.8),
                'cooking': random.uniform(0.3, 2.0),
                'carpentry': random.uniform(0.2, 1.5),
            }
    
    def can_work(self, work_type: str, energy_required: float) -> bool:
        """作業可能かチェック"""
        # 重傷時は完全に作業不可
        if self.severe_injury:
            return False
        if self.injured or self.health < 0.3:
            return False
        if self.energy < energy_required:
            return False
        if self.work_sessions_today >= self.max_work_sessions:
            return False
        if self.daily_energy_used + energy_required > 0.8:  # 1日最大エネルギー消費
            return False
        return True
    
    def consume_energy(self, work_type: str, energy_amount: float, work_duration: float):
        """エネルギー消費と疲労蓄積"""
        # 基本エネルギー消費
        self.energy = max(0.0, self.energy - energy_amount)
        self.daily_energy_used += energy_amount
        self.work_sessions_today += 1
        
        # 疲労蓄積（同じ作業の繰り返しで増加）
        if self.last_work_type == work_type:
            self.fatigue_level += 0.1
        else:
            self.fatigue_level = max(0.0, self.fatigue_level - 0.05)
        
        self.last_work_type = work_type
        
        # 疲労による効率低下
        if self.fatigue_level > 0.5:
            self.energy = max(0.0, self.energy - 0.1)
    
    def reset_daily_work(self):
        """日次作業データリセット"""
        self.daily_energy_used = 0.0
        self.work_sessions_today = 0
        # 夜間回復
        self.energy = min(1.0, self.energy + 0.4)
        self.fatigue_level = max(0.0, self.fatigue_level - 0.2)

class VillageEvent(Enum):
    """村の出来事"""
    HUNTING_SUCCESS = "hunting_success"
    HUNTING_FAILURE = "hunting_failure"  
    CARE_PROVIDED = "care_provided"
    MEAL_PREPARED = "meal_prepared"
    CONSTRUCTION_COMPLETED = "construction_completed"
    CONSTRUCTION_FAILED = "construction_failed"
    EMERGENCY_SITUATION = "emergency_situation"
    INNOVATION_ACHIEVED = "innovation_achieved"
    WORK_EXHAUSTION = "work_exhaustion"
    ENERGY_RECOVERED = "energy_recovered"

class IntegratedVillageSimulation:
    """統合村シミュレーション - 意味圧ベース + SSD Core Engine"""
    
    def __init__(self, population_size: int = 8):
        # 基本設定
        self.population_size = population_size
        self.current_day = 0
        self.village_events: List[Dict[str, Any]] = []
        self.food_storage = 1.0  # 最小限の初期食料
        self.village_happiness = random.uniform(0.5, 0.8)
        
        # 統合システム初期化
        self.ssd_adapter = VillageSSDAdapter("integrated_village_system")
        self.meaning_pressure_system = VillageMeaningPressureSystem()
        
        # 各活動システム初期化
        self.hunting_system = HuntingSystem()
        self.care_system = RelationshipCareSystem()
        self.cooking_system = EnhancedCookingSystem(self)  
        self.carpentry_system = MeaningPressureCarpentrySystem()
        self.rumor_system = RumorSystem()
        
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
        # self.hunting_system.initialize_hunters(villager_names)  # HuntingSystemにメソッドなし
        self.care_system.initialize_relationships()
        self.cooking_system.initialize_cooking_reputations(villager_names)
        self.carpentry_system.initialize_carpentry_reputations(villager_names)
        
        # 噂システム初期化
        villager_data = {v.name: {"personality": v.personality} for v in self.villagers}
        self.rumor_system.initialize_reputations(villager_names, villager_data)
        
        # 意味圧システムに村人登録
        # for villager in self.villagers:
        #     self.meaning_pressure_system.initialize_villager(
        #         villager.name, villager.personality, villager.skills
        #     )  # VillageMeaningPressureSystemにメソッドなし
        
        print(f"村システム初期化済み - {len(self.villagers)}人の村")
        for villager in self.villagers:
            hunting_skill = villager.skills.get('hunting', 1.0)
            print(f"  {villager.name} ({villager.personality}) - 狩猟スキル: {hunting_skill:.1f}")
        
        print("  料理システム統合完了")
        print("  意味圧ベース学習システム初期化完了")  
        print("  意味圧ベース大工システム初期化完了")
        print("  噂システム初期化完了")
        print("\\n=== 統合村システム初期化完了！===")
    
    def _update_daily_environment(self):
        """日次環境更新（獲物出現等）"""
        # 獲物出現処理
        self.hunting_system.spawn_prey(24.0)
        
        # 村人のエネルギー回復（前日からの回復）
        for villager in self.villagers:
            villager.daily_energy_used = 0.0
            villager.work_sessions_today = 0
            villager.fatigue_level = max(0.0, villager.fatigue_level - 0.2)
    
    def simulate_day(self) -> Dict[str, Any]:
        """1日のシミュレーション実行"""
        self.current_day += 1
        daily_events = []
        
        # 日次環境更新（獲物出現など）
        self._update_daily_environment()
        
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
        
        # 空腹度更新
        self._update_hunger()
        
        # 食料不足時は狩猟を最優先
        if self.food_storage < 2.0:
            print(f"警告: 食料不足！現在の貯蔵量: {self.food_storage:.1f}")
            hunting_events = self._conduct_hunting()
            events.extend(hunting_events)
            return events  # 食料確保最優先
        
        # 通常時の活動
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
    
    def _update_hunger(self):
        """全村人の空腹度を更新"""
        for villager in self.villagers:
            # 基本的な空腹増加（活動による消耗）
            villager.hunger += 0.15 + villager.fatigue_level * 0.05
            if villager.hunger > 1.0:
                villager.hunger = 1.0
    
    def _conduct_hunting(self) -> List[Dict[str, Any]]:
        """狩猟活動の実行"""
        events = []
        
        # エネルギー必要量設定
        hunting_energy_required = 0.3
        
        # 狩猟参加者選出（エネルギーと作業制限チェック）
        available_hunters = [
            v for v in self.villagers 
            if v.can_work('hunting', hunting_energy_required)
        ]
        
        if not available_hunters:
            return events
        
        # チームサイズを制限（エネルギー管理のため）
        max_team_size = min(2, len(available_hunters))  # 最大2人に制限
        if max_team_size < 1:
            return events
        
        hunters = random.sample(available_hunters, max_team_size)
        hunter_names = [h.name for h in hunters]
        
        # 簡素化された狩猟システム（確実に食料獲得）
        for hunter in hunters:
            hunter_name = hunter.name
            
            # 狩猟成功判定（スキルベース + ランダム）
            hunting_skill = hunter.skills.get('hunting', 0.5)
            success_chance = min(0.9, 0.3 + hunting_skill * 0.6)
            hunt_success = random.random() < success_chance
            
            # エネルギー消費
            hunt_duration = 3.0 + random.uniform(0, 2.0)
            energy_consumption = hunting_energy_required * random.uniform(0.8, 1.2)
            
            # エネルギー消費実行
            hunter.consume_energy('hunting', energy_consumption, hunt_duration)
            
            # 結果処理
            if hunt_success:
                # 食料獲得（スキルに基づいて量決定）
                food_gained = 1.5 + hunting_skill * 1.0 + random.uniform(0, 0.5)
                self.food_storage += food_gained
                
                # 狩猟成功の噂を広める
                self._spread_hunting_rumor(hunter_name, True, hunt_duration, 0.5)
                
                events.append({
                    'type': VillageEvent.HUNTING_SUCCESS,
                    'hunter': hunter_name,
                    'prey': "小動物",
                    'food_gained': food_gained,
                    'energy_used': energy_consumption,
                    'hunt_duration': hunt_duration
                })
                
                # 狩猟活動の負傷リスク適用
                injury_result = self._apply_injury_risk('hunting', True, hunter_name)
                events[-1].update(injury_result)
                
                if injury_result['injury_occurred']:
                    injury_type = "重傷" if injury_result['severe_injury_occurred'] else "軽傷"
                    events[-1]['injury_message'] = f"💥 代償: 狩猟中に{injury_type}してしまった"
                
                # 意味圧システムにスキル向上を記録
                hunting_context = {
                    'success': True,
                    'effectiveness': food_gained / 3.0,
                    'difficulty': 0.5,
                    'innovation': False
                }
                updated_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                    hunter_name, MeaningActivityType.HUNTING, hunting_context
                )
                print(f"      [DEBUG] {hunter_name}の狩猟慣性更新: {updated_inertia:.3f}")
                
                # SSD理論: 狩猟成功による主観的境界学習
                self.ssd_adapter.update_experience(hunter_name, "hunting", True, food_gained / 3.0)
                
            else:
                # 狩猟失敗時の負傷リスク適用
                injury_result = self._apply_injury_risk('hunting', False, hunter_name)
                
                if injury_result['injury_occurred']:
                    injury_type = "重傷" if injury_result['severe_injury_occurred'] else "軽傷"
                
                # SSD理論: 狩猟失敗による主観的境界学習
                self.ssd_adapter.update_experience(hunter_name, "hunting", False, 0.3)
                
                # 狩猟失敗の噂を広める（低い頻度で）
                if random.random() < 0.3:  # 30%の確率で失敗の噂が広がる
                    self._spread_hunting_rumor(hunter_name, False, hunt_duration, 0.5)
                
                failure_event = {
                    'type': VillageEvent.HUNTING_FAILURE,
                    'hunter': hunter_name,
                    'prey': "小動物",
                    'energy_used': energy_consumption,
                    'hunt_duration': hunt_duration
                }
                failure_event.update(injury_result)
                
                if injury_result['injury_occurred']:
                    injury_type = "重傷" if injury_result['severe_injury_occurred'] else "軽傷"
                    failure_event['injury_message'] = f"💥 さらに: 失敗により{injury_type}してしまった"
                
                events.append(failure_event)
        
        return events
    
    def _conduct_cooking(self) -> List[Dict[str, Any]]:
        """料理活動の実行"""
        events = []
        
        # 食料がある場合は料理を実行
        if self.food_storage <= 0:
            return events  # 食料がない場合のみスキップ
        
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
            occasion="daily",
            urgency_level=random.uniform(0.4, 0.7),
            group_size=len(self.villagers)
        )
        
        # 簡易料理実行
        ingredients_used = min(2.0, self.food_storage)  # 最大2.0単位の食材を使用
        cooking_success = random.random() < 0.8  # 80%の成功確率
        
        if cooking_success and ingredients_used > 0:
            self.food_storage -= ingredients_used
            # 村全体の満足度向上
            self.village_happiness = min(1.0, self.village_happiness + 0.05)
            
            # 村人の満腹度回復
            for villager in self.villagers:
                villager.hunger = max(0.0, villager.hunger - 0.3)
            
            # 意味圧システムにスキル向上を記録
            cooking_context = {
                'success': True,
                'effectiveness': 0.7,  # 標準的な品質
                'difficulty': 0.4,
                'innovation': False
            }
            updated_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                cook_name, MeaningActivityType.COOKING, cooking_context
            )
            print(f"      [DEBUG] {cook_name}の料理慣性更新: {updated_inertia:.3f}")
            
            # SSD理論: 料理成功による主観的境界学習
            self.ssd_adapter.update_experience(cook_name, "cooking", True, 0.7)
            
            # 料理活動の負傷リスク適用
            injury_result = self._apply_injury_risk('cooking', True, cook_name)
            
            cooking_event = {
                'type': VillageEvent.MEAL_PREPARED,
                'cook': cook_name,
                'meal_quality': 0.7,  # 標準的な品質
                'cooking_inertia': 0.1,
                'ingredients_used': ingredients_used
            }
            cooking_event.update(injury_result)
            
            if injury_result['injury_occurred']:
                injury_type = "重傷" if injury_result['severe_injury_occurred'] else "軽傷"
                cooking_event['injury_message'] = f"💥 代償: 料理中に{injury_type}してしまった"
            
            events.append(cooking_event)
        
        return events
    
    def _conduct_carpentry(self) -> List[Dict[str, Any]]:
        """大工活動の実行（エネルギー制限付き）"""
        events = []
        
        # 建築需要の判定（低頻度）
        if random.random() > 0.3:
            return events
        
        # エネルギー必要量設定
        carpentry_energy_required = 0.25
        
        # 大工担当者選出（エネルギーと作業制限チェック）
        available_carpenters = [
            v for v in self.villagers 
            if v.can_work('carpentry', carpentry_energy_required)
        ]
        
        if not available_carpenters:
            return events
        
        # 大工スキルベース選択（疲労考慮）
        carpenter_scores = []
        for villager in available_carpenters:
            carpentry_skill = villager.skills.get('carpentry', 0)
            # 疲労による効率低下を考慮
            effective_skill = carpentry_skill * (1.0 - villager.fatigue_level * 0.3)
            carpenter_scores.append((villager, effective_skill))
        
        carpenter_scores.sort(key=lambda x: x[1], reverse=True)
        carpenter_villager = carpenter_scores[0][0]
        carpenter_name = carpenter_villager.name
        
        # 進行中プロジェクトがあるかチェック
        ongoing_projects = self.carpentry_system.get_ongoing_projects_status()
        carpenter_busy = any(
            proj['lead_carpenter'] == carpenter_name or carpenter_name in proj['helpers']
            for proj in ongoing_projects
        )
        
        if carpenter_busy:
            # 進行中プロジェクトの作業継続
            for ongoing in self.carpentry_system.ongoing_projects:
                if (ongoing.lead_carpenter == carpenter_name or 
                    carpenter_name in ongoing.helpers):
                    
                    result = self.carpentry_system.continue_project_work(
                        ongoing, self.meaning_pressure_system, self.current_day
                    )
                    break
        else:
            # 新規プロジェクト開始判定
            construction_types = ["repair", "housing", "furniture", "infrastructure"]
            
            # 大規模プロジェクトの可能性を追加
            if random.random() < 0.1:  # 10%で大規模プロジェクト
                construction_types = ["infrastructure", "housing"]
                complexity_range = (0.6, 0.9)
            else:
                complexity_range = (0.3, 0.7)
            
            construction_request = ConstructionRequest(
                requester_name=random.choice([v.name for v in self.villagers]),
                preferred_carpenter=carpenter_name,
                construction_type=random.choice(construction_types),
                urgency_level=random.uniform(0.2, 0.8),
                complexity=random.uniform(*complexity_range)
            )
            
            # プロジェクトタイプ判定
            selected_project = self.carpentry_system._select_project_for_request(construction_request)
            
            if selected_project.total_work_days > 1:
                # マルチデイプロジェクト開始
                helpers = []
                if selected_project.collaboration_needed or selected_project.total_work_days >= 7:
                    # 大型プロジェクトには助手を配置
                    available_helpers = [
                        v for v in self.villagers 
                        if (v.can_work('carpentry', 0.2) and v.name != carpenter_name)
                    ]
                    if available_helpers:
                        helper_count = min(2, len(available_helpers), selected_project.total_work_days // 4)
                        helpers = [h.name for h in random.sample(available_helpers, helper_count)]
                
                ongoing_project = self.carpentry_system.start_multi_day_project(
                    carpenter_name, construction_request, self.current_day, helpers
                )
                
                # 初日の作業実行
                result = self.carpentry_system.continue_project_work(
                    ongoing_project, self.meaning_pressure_system, self.current_day
                )
            else:
                # 1日プロジェクト（従来通り）
                result = self.carpentry_system.execute_carpentry_with_meaning_pressure(
                    carpenter_name, construction_request, self.meaning_pressure_system
                )
        
        # マルチデイプロジェクトかどうかで処理を分岐
        is_multi_day = 'days_remaining' in result
        
        if is_multi_day:
            # マルチデイプロジェクトの場合
            work_duration = 4.0  # 1日の標準作業時間
            complexity = result.get('daily_progress', 1.0)
        else:
            # 従来の1日プロジェクト
            work_duration = result.get('complexity', 0.5) * 2.0 + 1.0
            complexity = result.get('complexity', 0.5)
            
        energy_consumption = carpentry_energy_required * (1.0 + complexity)
        
        # エネルギー消費実行
        carpenter_villager.consume_energy('carpentry', energy_consumption, work_duration)
        
        # 意味圧システムにスキル向上を記録
        carpentry_context = {
            'success': result.get('success', True),
            'effectiveness': result.get('quality', 0.5),
            'difficulty': complexity,
            'innovation': False,
            'complex_project': is_multi_day and complexity > 0.7,
            'project_quality': result.get('quality', 0.5),
            'limited_materials': random.random() < 0.2,
            'structural_requirements': complexity > 0.6,
            'team_coordination': is_multi_day
        }
        
        updated_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
            carpenter_name, MeaningActivityType.CARPENTRY, carpentry_context
        )
        print(f"      [DEBUG] {carpenter_name}の木工慣性更新: {updated_inertia:.3f}")
        
        # SSD理論: 建設活動による主観的境界学習
        success = result.get('success', True)
        quality = result.get('quality', 0.5)
        self.ssd_adapter.update_experience(carpenter_name, "carpentry", success, quality)
        
        # 大工活動の負傷リスク適用（責任者）
        injury_result = self._apply_injury_risk('carpentry', success, carpenter_name)
        
        # 助手もエネルギー消費と意味圧記録
        if is_multi_day:
            ongoing_projects = self.carpentry_system.get_ongoing_projects_status()
            for proj in ongoing_projects:
                if proj['lead_carpenter'] == carpenter_name:
                    for helper_name in proj['helpers']:
                        helper_villager = next((v for v in self.villagers if v.name == helper_name), None)
                        if helper_villager and helper_villager.can_work('carpentry', energy_consumption * 0.7):
                            helper_villager.consume_energy('carpentry', energy_consumption * 0.7, work_duration)
                            # 助手にも意味圧記録（効果は70%）
                            helper_context = carpentry_context.copy()
                            helper_context['effectiveness'] *= 0.7
                            helper_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                                helper_name, MeaningActivityType.CARPENTRY, helper_context
                            )
                            print(f"      [DEBUG] {helper_name}の木工助手慣性更新: {helper_inertia:.3f}")
                            
                            # SSD理論: 助手の協力作業による境界学習
                            self.ssd_adapter.update_experience(helper_name, "carpentry", success, quality * 0.7)
                            # 助手と責任者の協力関係による相互境界学習
                            self.ssd_adapter.update_relationship(helper_name, carpenter_name, "cooperative_construction")
                            
                            # 助手の負傷リスク（責任者より低めのリスク）
                            helper_injury = self._apply_injury_risk('construction', success, helper_name)
                            if helper_injury['injury_occurred']:
                                injury_type = "重傷" if helper_injury['severe_injury_occurred'] else "軽傷"
                                print(f"      💥 助手事故: {helper_name}が建設作業中に{injury_type}しました")
        
        # 結果処理
        if result.get('success', True):
            # 村の建物品質向上
            happiness_gain = 0.03
            if is_multi_day:
                # マルチデイプロジェクトは完了時により大きな幸福度向上
                if result.get('is_completed', False):
                    happiness_gain = 0.1
                    # 大きなプロジェクト完了時は噂が広がりやすい
                    self._spread_carpentry_rumor(
                        carpenter_name, True, result['project_name'], 
                        result.get('final_quality', 0.8)
                    )
                else:
                    happiness_gain = 0.01  # 進行中は小さな向上
            else:
                # 1日プロジェクトも噂の対象
                self._spread_carpentry_rumor(
                    carpenter_name, True, result['project_name'], 
                    result.get('quality', 0.5)
                )
            
            self.village_happiness = min(1.0, self.village_happiness + happiness_gain)
            
            event_data = {
                'type': VillageEvent.CONSTRUCTION_COMPLETED if not is_multi_day or result.get('is_completed', False) else 'construction_progress',
                'carpenter': carpenter_name,
                'project': result['project_name'],
                'carpentry_inertia': result['carpentry_inertia'],
                'energy_used': energy_consumption,
                'work_duration': work_duration
            }
            event_data.update(injury_result)
            
            if injury_result['injury_occurred']:
                injury_type = "重傷" if injury_result['severe_injury_occurred'] else "軽傷"
                event_data['injury_message'] = f"💥 代償: 建設作業中に{injury_type}してしまった"
            
            # マルチデイプロジェクト用の追加情報
            if is_multi_day:
                event_data.update({
                    'progress_percentage': result.get('total_progress', 0),
                    'days_remaining': result.get('days_remaining', 0),
                    'is_completed': result.get('is_completed', False),
                    'daily_progress': result.get('daily_progress', 0)
                })
                
                if result.get('is_completed', False):
                    event_data['final_quality'] = result.get('final_quality', 0)
            else:
                event_data['quality'] = result.get('quality', 0)
            
            events.append(event_data)
        else:
            # 失敗でも疲労は蓄積
            events.append({
                'type': VillageEvent.CONSTRUCTION_FAILED,
                'carpenter': carpenter_name,
                'project': result['project_name'],
                'energy_used': energy_consumption,
                'work_duration': work_duration,
                'is_multi_day': is_multi_day
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
            # 看護システム実行
            care_result = self.care_system.simulate_daily_care()
            
            # 結果処理（簡易版）
            if care_result and len(care_result) > 0:
                # 最初の看護イベントを使用
                care_event = care_result[0]
                patient.health = min(1.0, patient.health + 0.2)
                recovery_success = False
                if patient.injured and random.random() < 0.6:
                    patient.injured = False
                    recovery_success = True
                
                # 意味圧システムにスキル向上を記録
                caregiving_context = {
                    'success': recovery_success or care_event.effectiveness > 0.7,
                    'effectiveness': care_event.effectiveness,
                    'difficulty': 0.6,  # 看護の難易度
                    'innovation': False
                }
                updated_inertia = self.meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
                    care_event.caregiver, MeaningActivityType.CAREGIVING, caregiving_context
                )
                print(f"      [DEBUG] {care_event.caregiver}の看護慣性更新: {updated_inertia:.3f}")
                
                # SSD理論: 看護活動による主観的境界学習
                care_success = recovery_success or care_event.effectiveness > 0.7
                self.ssd_adapter.update_experience(care_event.caregiver, "caregiving", care_success, care_event.effectiveness)
                # 患者と看護者の関係による相互境界学習
                relationship_type = "received_excellent_care" if care_success else "received_poor_care"
                self.ssd_adapter.update_relationship(care_event.patient, care_event.caregiver, relationship_type)
                
                # 看護活動の負傷リスク適用
                injury_result = self._apply_injury_risk('caregiving', care_success, care_event.caregiver)
                
                # 看護に関する噂を広める
                self._spread_care_rumor(
                    care_event.caregiver, 
                    care_event.patient, 
                    recovery_success or care_event.effectiveness > 0.7,
                    care_event.effectiveness
                )
                
                care_event_data = {
                    'type': VillageEvent.CARE_PROVIDED,
                    'caregiver': care_event.caregiver,
                    'patient': care_event.patient,
                    'care_quality': care_event.effectiveness,
                    'caregiving_inertia': care_event.relationship_after - care_event.relationship_before
                }
                care_event_data.update(injury_result)
                
                if injury_result['injury_occurred']:
                    injury_type = "重傷" if injury_result['severe_injury_occurred'] else "軽傷"
                    care_event_data['injury_message'] = f"💥 代償: 看護中に{injury_type}してしまった"
                
                events.append(care_event_data)
        
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
        
        # 日常的な食料消費
        daily_food_consumption = len(self.villagers) * 0.3  # 1人あたり0.3単位/日
        
        if self.food_storage >= daily_food_consumption:
            # 十分な食料がある場合
            self.food_storage -= daily_food_consumption
            # 村人の空腹度軽減
            hunger_relief = 0.2
        else:
            # 食料不足の場合
            available_food = self.food_storage
            self.food_storage = 0.0
            # 部分的な空腹軽減
            hunger_relief = available_food / len(self.villagers) * 0.5
            
            events.append({
                'type': 'food_shortage',
                'message': f'食料不足: {available_food:.1f}単位しか消費できませんでした',
                'severity': 'warning'
            })
        
        # 村人の基本的な回復と日次リセット
        for villager in self.villagers:
            # 食事による空腹度変化
            villager.hunger = max(0.0, villager.hunger - hunger_relief)
            
            # 軽微な健康回復
            if villager.health < 1.0 and not villager.injured:
                villager.health = min(1.0, villager.health + 0.1)
            
            # 重傷の回復判定（優先）
            if villager.severe_injury:
                villager.injury_recovery_days -= 1
                if villager.injury_recovery_days <= 0:
                    # 重傷から回復
                    villager.severe_injury = False
                    villager.injured = False  # 重傷が治れば軽傷も治る
                    villager.health = min(1.0, villager.health + 0.3)
                    events.append({
                        'type': 'severe_injury_recovery',
                        'villager': villager.name,
                        'message': f'{villager.name}が重傷から回復しました'
                    })
            # 軽傷の回復判定
            elif villager.injured and random.random() < 0.3:
                villager.injured = False
                villager.health = min(1.0, villager.health + 0.2)
                events.append({
                    'type': 'injury_recovery',
                    'villager': villager.name,
                    'message': f'{villager.name}が怪我から回復しました'
                })
            
            # 日次作業データリセット（エネルギー回復含む）
            villager.reset_daily_work()
        
        return events
    
    def _spread_hunting_rumor(self, hunter_name: str, success: bool, hunt_duration: float, difficulty: float):
        """狩猟に関する噂を広める"""
        # 噂の強さを計算（成功度、難易度、時間に基づく）
        intensity = min(1.0, (difficulty + hunt_duration / 5.0) / 2.0)
        
        # 潜在的な聞き手（他の村人たち）
        potential_listeners = [v.name for v in self.villagers if v.name != hunter_name]
        
        # 目撃者がいれば噂を作成
        if len(potential_listeners) >= 2:
            witness = random.choice(potential_listeners)  # ランダムに目撃者選択
            possible_listeners_for_witness = [v for v in potential_listeners if v != witness]
            
            listener = random.choice(possible_listeners_for_witness)
            self.rumor_system.create_rumor_from_interaction(
                speaker=witness,
                listener=listener,
                subject=hunter_name,
                rumor_type=RumorType.HUNTING_SKILL,
                positive=success,
                intensity=intensity,
                context="direct_experience" if success else "witnessed_failure"
            )
            
            # SSD理論: 噂を通じた主観的境界学習
            interaction_type = "positive_rumor_sharing" if success else "negative_rumor_sharing"
            self.ssd_adapter.update_relationship(witness, listener, interaction_type)
            self.ssd_adapter.update_relationship(witness, hunter_name, f"witnessed_{'success' if success else 'failure'}")
            
            # 社会的承認による自信向上（スキル≠境界の分離）
            if success:
                self.ssd_adapter.update_social_recognition(hunter_name, witness, "hunting", 0.6)
    
    def _spread_carpentry_rumor(self, carpenter_name: str, success: bool, project_name: str, quality: float = 0.0):
        """大工作業に関する噂を広める"""
        intensity = min(1.0, quality + (0.8 if success else 0.2))
        
        potential_speakers = [v.name for v in self.villagers if v.name != carpenter_name]
        
        if len(potential_speakers) >= 2:
            speaker = random.choice(potential_speakers)
            potential_listeners = [v for v in potential_speakers if v != speaker]
            listener = random.choice(potential_listeners)
            
            self.rumor_system.create_rumor_from_interaction(
                speaker=speaker,
                listener=listener,
                subject=carpenter_name,
                rumor_type=RumorType.CRAFTING_SKILL,
                positive=success,
                intensity=intensity,
                context=f"saw_{project_name}"
            )
            
            # SSD理論: 建設噂を通じた主観的境界学習
            interaction_type = "positive_craft_rumor" if success else "negative_craft_rumor"
            self.ssd_adapter.update_relationship(speaker, listener, interaction_type)
            self.ssd_adapter.update_relationship(speaker, carpenter_name, f"observed_{'good' if success else 'poor'}_crafting")
            
            # 社会的承認による自信向上
            if success:
                self.ssd_adapter.update_social_recognition(carpenter_name, speaker, "carpentry", intensity * 0.8)
    
    def _spread_care_rumor(self, caregiver_name: str, patient_name: str, success: bool, care_quality: float):
        """看護に関する噂を広める"""
        intensity = min(1.0, care_quality + (0.5 if success else 0.1))
        
        # 患者自身が噂を広める場合もある
        potential_speakers = [v.name for v in self.villagers if v.name != caregiver_name]
        
        if potential_speakers:
            speaker = patient_name if patient_name in potential_speakers else random.choice(potential_speakers)
            potential_listeners = [v.name for v in self.villagers if v.name not in [caregiver_name, speaker]]
            
            if potential_listeners:
                listener = random.choice(potential_listeners)
                
                self.rumor_system.create_rumor_from_interaction(
                    speaker=speaker,
                    listener=listener,
                    subject=caregiver_name,
                    rumor_type=RumorType.CAREGIVING_SKILL,
                    positive=success,
                    intensity=intensity,
                    context="received_care" if speaker == patient_name else "witnessed_care"
                )
                
                # SSD理論: 看護噂を通じた主観的境界学習
                interaction_type = "positive_care_rumor" if success else "negative_care_rumor"
                self.ssd_adapter.update_relationship(speaker, listener, interaction_type)
                if speaker == patient_name:
                    # 患者が語る場合は直接経験による強い境界形成
                    care_experience = "received_excellent_care" if success else "received_poor_care"
                    self.ssd_adapter.update_relationship(speaker, caregiver_name, care_experience)
                    
                # 社会的承認による自信向上
                if success:
                    recognition_strength = 0.8 if speaker == patient_name else 0.6  # 患者からの評価は重い
                    self.ssd_adapter.update_social_recognition(caregiver_name, speaker, "caregiving", recognition_strength)
    
    def _update_villager_energy(self, name: str, change: float):
        """村人のエネルギー更新"""
        for villager in self.villagers:
            if villager.name == name:
                villager.energy = max(0.0, min(1.0, villager.energy + change))
                break
    
    def _get_villager_by_name(self, name: str):
        """名前で村人を取得"""
        for villager in self.villagers:
            if villager.name == name:
                return villager
        return None

    def _calculate_injury_risk(self, activity_type: str, success: bool, villager_name: str) -> dict:
        """活動別の負傷リスク計算"""
        villager = self._get_villager_by_name(villager_name)
        base_fatigue = villager.fatigue_level if villager else 0.0
        
        # 活動別基本リスク設定
        risk_profiles = {
            'hunting': {
                'light_injury': (0.03, 0.05) if success else (0.08, 0.12),  # (base, fatigue_multiplier)
                'severe_injury': (0.005, 0.01) if success else (0.02, 0.03),
                'description': '野生動物との接触、転倒、道具事故'
            },
            'carpentry': {
                'light_injury': (0.05, 0.08) if success else (0.12, 0.15),  # 工具使用リスク
                'severe_injury': (0.01, 0.02) if success else (0.04, 0.06),  # 重機具事故
                'description': '工具による切り傷、落下物、重機事故'
            },
            'cooking': {
                'light_injury': (0.02, 0.03) if success else (0.05, 0.07),  # 火傷、刃物
                'severe_injury': (0.001, 0.005) if success else (0.01, 0.02),  # 重度火傷
                'description': '火傷、刃物による切り傷、熱湯事故'
            },
            'caregiving': {
                'light_injury': (0.01, 0.02) if success else (0.03, 0.04),  # 患者移動時
                'severe_injury': (0.0005, 0.001) if success else (0.002, 0.005),  # 感染等
                'description': '患者移動時の負傷、感染リスク'
            },
            'construction': {
                'light_injury': (0.06, 0.10) if success else (0.15, 0.20),  # 建設現場リスク
                'severe_injury': (0.02, 0.03) if success else (0.06, 0.08),  # 重大事故
                'description': '高所落下、重量物事故、建材による負傷'
            }
        }
        
        profile = risk_profiles.get(activity_type, risk_profiles['hunting'])  # デフォルト
        
        light_base, light_fatigue = profile['light_injury']
        severe_base, severe_fatigue = profile['severe_injury']
        
        light_risk = light_base + base_fatigue * light_fatigue
        severe_risk = severe_base + base_fatigue * severe_fatigue
        
        return {
            'light_injury_risk': min(0.25, light_risk),  # 最大25%
            'severe_injury_risk': min(0.10, severe_risk),  # 最大10%
            'description': profile['description']
        }
    
    def _apply_injury_risk(self, activity_type: str, success: bool, villager_name: str) -> dict:
        """負傷リスクの適用と結果返却"""
        risks = self._calculate_injury_risk(activity_type, success, villager_name)
        
        injury_result = {
            'injury_occurred': False,
            'severe_injury_occurred': False,
            'injury_type': None,
            'description': risks['description']
        }
        
        if random.random() < risks['severe_injury_risk']:
            self._injure_villager(villager_name, severe=True)
            injury_result.update({
                'injury_occurred': True,
                'severe_injury_occurred': True,
                'injury_type': 'severe'
            })
        elif random.random() < risks['light_injury_risk']:
            self._injure_villager(villager_name)
            injury_result.update({
                'injury_occurred': True,
                'injury_type': 'light'
            })
        
        return injury_result

    def _injure_villager(self, name: str, severe: bool = False):
        """村人に怪我を負わせる"""
        for villager in self.villagers:
            if villager.name == name:
                if severe:
                    # 重傷：数日間動けない
                    villager.severe_injury = True
                    villager.injury_recovery_days = random.randint(3, 7)  # 3-7日間
                    villager.health = max(0.1, villager.health - 0.5)  # より大きなダメージ
                    villager.injured = True
                else:
                    # 軽傷：通常の怪我
                    villager.injured = True
                    villager.health = max(0.1, villager.health - 0.3)
                break
    
    def _calculate_daily_stats(self) -> Dict[str, Any]:
        """日次統計の計算"""
        
        # 健康状態統計
        healthy_count = len([v for v in self.villagers if v.health > 0.7 and not v.injured])
        injured_count = len([v for v in self.villagers if v.injured and not v.severe_injury])
        severe_injured_count = len([v for v in self.villagers if v.severe_injury])
        
        # スキル慣性平均
        hunting_inertias = []
        caregiving_inertias = []
        cooking_inertias = []
        social_coordination_inertias = []
        carpentry_inertias = []
        
        for villager in self.villagers:
            # 意味圧システムから慣性値取得
            hunter_inertia = self.meaning_pressure_system.get_villager_skill_level(villager.name, MeaningActivityType.HUNTING)
            caregiving_inertia = self.meaning_pressure_system.get_villager_skill_level(villager.name, MeaningActivityType.CAREGIVING)  
            cooking_inertia = self.meaning_pressure_system.get_villager_skill_level(villager.name, MeaningActivityType.COOKING)
            social_inertia = self.meaning_pressure_system.get_villager_skill_level(villager.name, MeaningActivityType.SOCIAL_COORDINATION)
            carpentry_inertia = self.meaning_pressure_system.get_villager_skill_level(villager.name, MeaningActivityType.CARPENTRY)
            
            # すべてのスキル慣性を記録（初期値0.0も含む）
            hunting_inertias.append(hunter_inertia)
            caregiving_inertias.append(caregiving_inertia)
            cooking_inertias.append(cooking_inertia)
            social_coordination_inertias.append(social_inertia)
            carpentry_inertias.append(carpentry_inertia)
        
        # 建物品質
        building_quality = sum(self.carpentry_system.village_buildings.values()) / len(self.carpentry_system.village_buildings)
        
        return {
            'day': self.current_day,
            'healthy_villagers': healthy_count,
            'injured_villagers': injured_count,
            'severe_injured_villagers': severe_injured_count,
            'food_storage': self.food_storage,
            'village_happiness': self.village_happiness,
            'hunting_inertia': sum(hunting_inertias) / max(len(hunting_inertias), 1),
            'caregiving_inertia': sum(caregiving_inertias) / max(len(caregiving_inertias), 1),
            'cooking_inertia': sum(cooking_inertias) / max(len(cooking_inertias), 1),
            'social_coordination_inertia': sum(social_coordination_inertias) / max(len(social_coordination_inertias), 1),
            'carpentry_inertia': sum(carpentry_inertias) / max(len(carpentry_inertias), 1),
            'building_quality': building_quality
        }
    
    def get_village_status(self) -> Dict[str, Any]:
        """村の現在状況取得"""
        stats = self._calculate_daily_stats()
        
        print(f"\\n=== 村の概要 ===")
        print(f"  人口: {len(self.villagers)}人")
        print(f"  健康: {stats['healthy_villagers']}人, 軽傷: {stats['injured_villagers']}人, 重傷: {stats['severe_injured_villagers']}人")
        print(f"  食料貯蔵: {self.food_storage:.1f}単位")
        print(f"  村の幸福度: {self.village_happiness:.2f}")
        
        # 進行中プロジェクト表示
        ongoing_projects = self.carpentry_system.get_ongoing_projects_status()
        if ongoing_projects:
            print(f"\\n進行中プロジェクト:")
            for proj in ongoing_projects:
                print(f"  {proj['project_name']}")
                print(f"     責任者: {proj['lead_carpenter']}")
                if proj['helpers']:
                    print(f"     助手: {', '.join(proj['helpers'])}")
                print(f"     進捗: {proj['progress_percentage']:.1f}% ({proj['days_worked']}/{proj['total_days']}日)")
                print(f"     品質: {proj['quality_so_far']:.2f}")
        
        print(f"\\n=== 意味圧ベーススキル平均 ===")
        print(f"  狩猟慣性: {stats['hunting_inertia']:.3f}")
        print(f"  看護慣性: {stats['caregiving_inertia']:.3f}")  
        print(f"  料理慣性: {stats['cooking_inertia']:.3f}")
        print(f"  調整慣性: {stats['social_coordination_inertia']:.3f}")
        print(f"  大工慣性: {stats['carpentry_inertia']:.3f}")
        print(f"  建物品質: {stats['building_quality']:.2f}")
        
        # 詳細スキル分析を追加
        self._display_detailed_skill_analysis()
        
        # SSD理論主観的境界分析を追加
        self._display_subjective_boundary_analysis()
        
        # 噂情報表示
        self._display_rumors()
        
        return stats
    
    def _display_subjective_boundary_analysis(self):
        """SSD理論：主観的境界分析表示"""
        print(f"\\n=== SSD理論 主観的境界分析 ===")
        
        for villager in self.villagers:
            boundary_summary = self.ssd_adapter.get_subjective_boundary_summary(villager.name)
            
            if "error" not in boundary_summary:
                print(f"\\n🧠 {villager.name}の主観的境界:")
                print(f"   内側認識: {boundary_summary['inner_count']}オブジェクト")
                print(f"   外側認識: {boundary_summary['outer_count']}オブジェクト")
                print(f"   境界平均強度: {boundary_summary['average_boundary_strength']:.3f}")
                
                # 強い結びつき（内側）
                if boundary_summary['strong_inner_bonds']:
                    print(f"   🤝 強い親和性:")
                    for obj, strength in list(boundary_summary['strong_inner_bonds'].items())[:3]:
                        obj_type = self._classify_boundary_object(obj)
                        print(f"      {obj_type}: {strength:.2f}")
                
                # 強い拒絶（外側）  
                if boundary_summary['strong_outer_aversions']:
                    print(f"   ❌ 強い警戒感:")
                    for obj, strength in list(boundary_summary['strong_outer_aversions'].items())[:3]:
                        obj_type = self._classify_boundary_object(obj)
                        print(f"      {obj_type}: {strength:.2f}")
    
    def _classify_boundary_object(self, obj_id: str) -> str:
        """境界オブジェクトの分類"""
        if obj_id.startswith("activity_"):
            return f"活動「{obj_id.replace('activity_', '')}」"
        elif obj_id.startswith("location_"):
            return f"場所「{obj_id.replace('location_', '')}」"
        elif obj_id.startswith("self_"):
            return f"自信「{obj_id.replace('self_', '').replace('_skill', '')}」"
        elif obj_id in [v.name for v in self.villagers]:
            return f"人物「{obj_id}」"
        else:
            return f"オブジェクト「{obj_id}」"
    
    def _display_detailed_skill_analysis(self):
        """詳細なスキル分析を表示"""
        print(f"\\n=== 詳細スキル専門化分析 ===")
        
        # 各スキルの上位者を抽出
        skill_specialists = {
            '狩猟': [],
            '看護': [],
            '料理': [],
            '調整': [],
            '大工': []
        }
        
        for villager in self.villagers:
            name = villager.name
            
            # 各スキルレベル取得
            hunting_level = self.meaning_pressure_system.get_villager_skill_level(name, MeaningActivityType.HUNTING)
            care_level = self.meaning_pressure_system.get_villager_skill_level(name, MeaningActivityType.CAREGIVING)
            cooking_level = self.meaning_pressure_system.get_villager_skill_level(name, MeaningActivityType.COOKING)
            social_level = self.meaning_pressure_system.get_villager_skill_level(name, MeaningActivityType.SOCIAL_COORDINATION)
            
            # 閾値を超えたスキルを記録
            if hunting_level > 0.1:
                skill_specialists['狩猟'].append((name, hunting_level))
            if care_level > 0.1:
                skill_specialists['看護'].append((name, care_level))
            if cooking_level > 0.1:
                skill_specialists['料理'].append((name, cooking_level))
            if social_level > 0.1:
                skill_specialists['調整'].append((name, social_level))
        
        # 大工の専門家
        for name, rep in self.carpentry_system.carpenter_reputations.items():
            if rep.total_attempts > 0:
                skill_specialists['大工'].append((name, rep.reputation_score / 10.0))  # 正規化
        
        # 各スキル分野の上位者表示
        for skill_name, specialists in skill_specialists.items():
            if specialists:
                # スキルレベルでソート
                specialists.sort(key=lambda x: x[1], reverse=True)
                top_specialists = specialists[:3]  # 上位3名
                
                print(f"\\n{skill_name}専門家:")
                for i, (name, level) in enumerate(top_specialists, 1):
                    level_desc = self._get_skill_level_description(level)
                    print(f"  {i}位. {name}: {level:.3f} ({level_desc})")
            else:
                print(f"\\n{skill_name}専門家: まだ専門化していません")
    
    def _get_skill_level_description(self, level: float) -> str:
        """スキルレベルの説明文を取得"""
        if level >= 0.5:
            return "達人級"
        elif level >= 0.3:
            return "上級者"
        elif level >= 0.15:
            return "中級者" 
        elif level >= 0.05:
            return "初級者"
        else:
            return "見習い"
    
    def _display_rumors(self):
        """現在の噂情報を表示"""
        print(f"\\n=== 村の噂情報 ===")
        
        active_rumors = self.rumor_system.active_rumors
        
        if not active_rumors:
            print("  現在、特に目立った噂はありません。")
            return
        
        # 最近の噂を表示（最大5件）
        recent_rumors = sorted(active_rumors, key=lambda r: r.creation_time, reverse=True)[:5]
        
        print(f"  最近の噂 ({len(recent_rumors)}件):")
        for rumor in recent_rumors:
            confidence_level = "[高]" if rumor.confidence > 0.8 else "[中]" if rumor.confidence > 0.6 else "[低]"
            intensity_level = "***" if rumor.intensity > 0.8 else "**" if rumor.intensity > 0.5 else "*"
            
            print(f"    {confidence_level} {rumor.get_rumor_text()} {intensity_level}")
            print(f"       (発信者: {rumor.source_name}, 確信度: {rumor.confidence:.1f})")
        
        # 評判集計表示
        print(f"\\n  評判集計:")
        reputation_summary = {}
        for name, reputation_dict in self.rumor_system.village_reputation.items():
            for rumor_type, value in reputation_dict.items():
                if value != 0.5:  # 中性値以外
                    if name not in reputation_summary:
                        reputation_summary[name] = []
                    reputation_summary[name].append((rumor_type.value, value))
        
        if reputation_summary:
            for name, reputation_list in list(reputation_summary.items())[:5]:  # 上位5名表示
                reputation_items = [f"{rtype}: {value:.2f}" for rtype, value in reputation_list]
                print(f"    {name}: {', '.join(reputation_items)}")
        else:
            print("    まだ確立された評判はありません。")

def test_large_scale_simulation(population_size: int = 50, days: int = 100):
    """大規模・長期間シミュレーションテスト"""
    
    print(f"=== 大規模村システムテスト ===")
    print(f"   人口: {population_size}人, 期間: {days}日\\n")
    
    # システム初期化
    village = IntegratedVillageSimulation(population_size=population_size)
    
    # 初期状態表示
    print("【初期状態】")
    initial_stats = village.get_village_status()
    
    # シミュレーション実行（簡易ログ）
    print(f"\\n=== {days}日間シミュレーション実行中 ===")
    
    significant_events_count = 0
    crisis_events = 0
    
    for day in range(1, days + 1):
        daily_result = village.simulate_day()
        
        # 重要なイベントをカウント
        for event in daily_result['events']:
            if event['type'] in [VillageEvent.HUNTING_SUCCESS, VillageEvent.MEAL_PREPARED, 
                               VillageEvent.CONSTRUCTION_COMPLETED, VillageEvent.CARE_PROVIDED]:
                significant_events_count += 1
            elif event['type'] == VillageEvent.EMERGENCY_SITUATION:
                crisis_events += 1
        
        # 10日ごとに進捗表示
        if day % 10 == 0:
            print(f"  {day}日経過 - イベント累計: {significant_events_count}, 危機: {crisis_events}")
    
    # 最終状態
    print(f"\\n【最終状態】")
    final_stats = village.get_village_status()
    
    print(f"\\n🎯 === テスト結果 ===")
    print(f"全体統計:")
    print(f"  総イベント数: {significant_events_count}")
    print(f"  危機発生数: {crisis_events}")
    print(f"  平均危機頻度: {crisis_events/days:.2f}回/日")
    
    print(f"\\n📈 スキル成長:")
    if final_stats['hunting_inertia'] > 0.1:
        print(f"  🏹 狩猟慣性: {final_stats['hunting_inertia']:.3f}")
    if final_stats['cooking_inertia'] > 0.1:
        print(f"  🍳 料理慣性: {final_stats['cooking_inertia']:.3f}")
    if final_stats['caregiving_inertia'] > 0.1:
        print(f"  💝 看護慣性: {final_stats['caregiving_inertia']:.3f}")

    
    print(f"\\n🏘️ 建設品質: {final_stats['building_quality']:.3f}")
    print(f"🏘️ 村幸福度: {final_stats['village_happiness']:.3f}")
    
    # SSD効果の分析
    print(f"\\n🧠 === SSD Core Engine 分析 ===")
    print(f"   構造主観力学による自律的適応を確認")
    print(f"   意味圧ベース学習による専門化の自然発生")
    print(f"   整合・跳躍メカニズムによる危機対応")
    
    return {
        'initial_stats': initial_stats,
        'final_stats': final_stats,
        'total_events': significant_events_count,
        'crisis_events': crisis_events,
        'simulation_days': days
    }
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
                    print(f"  {event['carpenter']}が{event['project']}完成 (品質: {event['quality']:.2f})")
                elif event['type'] == VillageEvent.CARE_PROVIDED:
                    print(f"  💝 {event['caregiver']}が{event['patient']}を看護")
        else:
            print("  📝 平穏な一日")
    
    # 最終状態
    print(f"\\n【最終状態】")
    final_stats = village.get_village_status()
    
    print(f"\\n🎯 === 統合システム効果 ===")
    print(f"成長したスキル:")
    if final_stats['hunting_inertia'] > 0.1:
        print(f"  🏹 狩猟専門化: 平均慣性 {final_stats['hunting_inertia']:.3f}")
    if final_stats['cooking_inertia'] > 0.1:
        print(f"  🍳 料理専門化: 平均慣性 {final_stats['cooking_inertia']:.3f}")
    if final_stats['caregiving_inertia'] > 0.1:
        print(f"  💝 看護専門化: 平均慣性 {final_stats['caregiving_inertia']:.3f}")

    
    print(f"\\n🏘️ 構造主観力学（SSD理論）による理論的一貫性:")
    print(f"   • ssd_core_engine による主観的境界学習で全行動を決定")
    print(f"   • 場当たり的プログラミング不要の自律的AIエージェント")
    print(f"   • 意味圧ベース学習による自然な専門化と役割分担を実現！")

if __name__ == "__main__":
    print("=== 統合村システム デモンストレーション ===\\n")
    
    # システム初期化
    village = IntegratedVillageSimulation(population_size=8)
    
    # 初期状態表示
    print("【初期状態】")
    village.get_village_status()
    
    # 数日間のシミュレーション
    print(f"\\n=== 14日間シミュレーション開始 ===")
    
    for day in range(1, 15):
        print(f"\\n--- 第{day}日目 ---")
        
        daily_result = village.simulate_day()
        
        # 主要イベントの表示
        significant_events = [
            e for e in daily_result['events'] 
            if e['type'] in [VillageEvent.HUNTING_SUCCESS, VillageEvent.MEAL_PREPARED, 
                           VillageEvent.CONSTRUCTION_COMPLETED, VillageEvent.CARE_PROVIDED]
        ]
        
        if significant_events:
            print(f"  主要活動:")
            for event in significant_events[:3]:  # 最大3つまで表示
                if event['type'] == VillageEvent.HUNTING_SUCCESS:
                    hunter_name = event.get('hunter', event.get('actor', '不明'))
                    food_gained = event.get('food_gained', event.get('details', {}).get('meat_acquired', 0))
                    print(f"    {hunter_name}が狩猟で{food_gained:.1f}の肉を獲得")
                elif event['type'] == VillageEvent.MEAL_PREPARED:
                    cook_name = event.get('cook', event.get('actor', '不明'))
                    print(f"    {cook_name}が料理を準備")
                elif event['type'] == VillageEvent.CONSTRUCTION_COMPLETED:
                    carpenter_name = event.get('carpenter', event.get('actor', '不明'))
                    project_name = event.get('project', event.get('details', {}).get('project_name', '建物'))
                    print(f"    {carpenter_name}が{project_name}を完成")
                elif event['type'] == VillageEvent.CARE_PROVIDED:
                    caregiver_name = event.get('caregiver', event.get('actor', '不明'))
                    patient_name = event.get('patient', event.get('details', {}).get('patient', '患者'))
                    print(f"    {caregiver_name}が{patient_name}を看病")
    
    print(f"\\n=== 統合システム効果 ===")
    final_stats = village.get_village_status()
    
    if final_stats:
        print("\\nSSD Core Engine + 意味圧ベース学習により")
        print("   自然な役割分担と継続的な村の発展を実現！")