"""
Village Meaning Pressure Growth System
村の意味圧ベース成長システム

狩り・看護・料理すべての活動に意味圧ベースの学習飽和メカニズムを適用
"""

import math
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque

class ActivityType(Enum):
    """活動タイプ"""
    HUNTING = "hunting"
    CAREGIVING = "caregiving" 
    COOKING = "cooking"
    SOCIAL_COORDINATION = "social_coordination"
    CARPENTRY = "carpentry"

class MeaningLevel(Enum):
    """経験の意味レベル"""
    TRIVIAL = 1      # 些細な経験（日常的な失敗）
    ROUTINE = 2      # 日常的な成功
    MEANINGFUL = 3   # 意味のある経験（困難な成功）
    PROFOUND = 4     # 深い影響のある経験（危機救済、革新）

class VillageMeaningPressureSystem:
    """村全体の意味圧ベース成長システム"""
    
    def __init__(self):
        # 各村人の慣性値 {person_id: {activity_type: inertia_value}}
        self.alignment_inertia = defaultdict(lambda: defaultdict(float))
        
        # 経験履歴の追跡
        self.experience_history = defaultdict(lambda: defaultdict(list))
        
        # 繰り返し回数の追跡
        self.repetition_counter = defaultdict(lambda: defaultdict(int))
        
        # 活動別の抵抗係数（ρ値）
        self.activity_resistance = {
            ActivityType.HUNTING: 0.4,      # 中程度（体力消耗）
            ActivityType.CAREGIVING: 0.2,   # 低め（社会的活動）
            ActivityType.COOKING: 0.3,      # 中程度（技術と創造性）
            ActivityType.SOCIAL_COORDINATION: 0.5,  # 高め（複雑な調整）
            ActivityType.CARPENTRY: 0.6     # 最高（技術・体力・創造性）
        }
        
        # 活動別の基本整合係数
        self.base_alignment = {
            ActivityType.HUNTING: 0.25,
            ActivityType.CAREGIVING: 0.30,
            ActivityType.COOKING: 0.35,
            ActivityType.SOCIAL_COORDINATION: 0.20,
            ActivityType.CARPENTRY: 0.40    # 高め（技術習得による成長）
        }
    
    def calculate_meaning_pressure(self, person_id: str, activity: ActivityType, 
                                 context: Dict[str, Any]) -> float:
        """活動の意味圧を計算"""
        
        # 基本的な意味レベル判定
        meaning_level = self._assess_meaning_level(person_id, activity, context)
        
        # 繰り返し度合いによる減衰
        repetition_factor = self._calculate_repetition_decay(person_id, activity)
        
        # 活動の複雑性評価
        complexity_factor = self._assess_activity_complexity(activity, context)
        
        # 社会的インパクト
        social_impact = self._calculate_social_impact(activity, context)
        
        # 意味圧の基本値
        base_pressure = {
            MeaningLevel.TRIVIAL: 0.2,
            MeaningLevel.ROUTINE: 0.5,
            MeaningLevel.MEANINGFUL: 1.0,
            MeaningLevel.PROFOUND: 2.0
        }[meaning_level]
        
        # 最終的な意味圧
        meaning_pressure = base_pressure * complexity_factor * repetition_factor * social_impact
        
        return max(0.05, meaning_pressure)
    
    def _assess_meaning_level(self, person_id: str, activity: ActivityType, 
                            context: Dict[str, Any]) -> MeaningLevel:
        """経験の意味レベルを評価"""
        
        success = context.get('success', False)
        effectiveness = context.get('effectiveness', 0.5)
        difficulty = context.get('difficulty', 0.5)
        emergency = context.get('emergency', False)
        innovation = context.get('innovation', False)
        
        # 活動別の特別評価
        if activity == ActivityType.HUNTING:
            large_prey = context.get('large_prey', False)
            danger_level = context.get('danger_level', 0)
            
            if emergency and success:  # 食料危機を救った
                return MeaningLevel.PROFOUND
            elif large_prey and success and danger_level > 0.7:
                return MeaningLevel.MEANINGFUL
            elif success and effectiveness > 0.6:
                return MeaningLevel.ROUTINE
            else:
                return MeaningLevel.TRIVIAL
                
        elif activity == ActivityType.CAREGIVING:
            life_threatening = context.get('life_threatening', False)
            patient_recovery = context.get('patient_recovery', False)
            
            if life_threatening and success and patient_recovery:
                return MeaningLevel.PROFOUND
            elif success and effectiveness > 0.7:
                return MeaningLevel.MEANINGFUL
            elif success:
                return MeaningLevel.ROUTINE
            else:
                return MeaningLevel.TRIVIAL
                
        elif activity == ActivityType.COOKING:
            feast_preparation = context.get('feast_preparation', False)
            new_recipe = context.get('new_recipe', False)
            food_crisis = context.get('food_crisis', False)
            
            if (feast_preparation or food_crisis) and success:
                return MeaningLevel.PROFOUND
            elif new_recipe and success:
                return MeaningLevel.MEANINGFUL
            elif success and effectiveness > 0.6:
                return MeaningLevel.ROUTINE
            else:
                return MeaningLevel.TRIVIAL
                
        elif activity == ActivityType.CARPENTRY:
            complex_project = context.get('complex_project', False)
            new_technique = context.get('new_technique', False) 
            emergency_construction = context.get('emergency_construction', False)
            project_quality = context.get('project_quality', 0.5)
            
            if (complex_project or emergency_construction) and success and project_quality > 0.8:
                return MeaningLevel.PROFOUND
            elif new_technique and success:
                return MeaningLevel.MEANINGFUL
            elif success and project_quality > 0.6:
                return MeaningLevel.ROUTINE
            else:
                return MeaningLevel.TRIVIAL
        
        # デフォルト評価
        if innovation and success:
            return MeaningLevel.PROFOUND
        elif success and effectiveness > 0.7 and difficulty > 0.6:
            return MeaningLevel.MEANINGFUL
        elif success:
            return MeaningLevel.ROUTINE
        else:
            return MeaningLevel.TRIVIAL
    
    def _calculate_repetition_decay(self, person_id: str, activity: ActivityType) -> float:
        """繰り返しによる減衰係数"""
        
        count = self.repetition_counter[person_id][activity]
        self.repetition_counter[person_id][activity] += 1
        
        # 活動別の減衰特性
        if activity == ActivityType.HUNTING:
            # 狩猟は繰り返しでも技術向上の余地あり
            decay_rate = 0.05
        elif activity == ActivityType.CAREGIVING:
            # 看護は人それぞれで新鮮さ維持
            decay_rate = 0.03
        elif activity == ActivityType.COOKING:
            # 料理は創造性で繰り返し回避可能
            decay_rate = 0.04
        elif activity == ActivityType.CARPENTRY:
            # 大工は技術習得で長期成長可能
            decay_rate = 0.02
        else:
            decay_rate = 0.08
        
        decay_factor = math.exp(-count * decay_rate)
        return max(0.3, decay_factor)  # 最低30%は維持
    
    def _assess_activity_complexity(self, activity: ActivityType, context: Dict[str, Any]) -> float:
        """活動の複雑性を評価"""
        
        complexity = 1.0  # ベース値
        
        # 共通の複雑性要因
        if context.get('collaboration', False):
            complexity += 0.3
        if context.get('time_pressure', False):
            complexity += 0.2
        if context.get('resource_scarcity', False):
            complexity += 0.4
        
        # 活動別の特殊要因
        if activity == ActivityType.HUNTING:
            if context.get('weather_bad', False):
                complexity += 0.3
            if context.get('group_coordination', False):
                complexity += 0.4
                
        elif activity == ActivityType.CAREGIVING:
            if context.get('multiple_patients', False):
                complexity += 0.5
            if context.get('diagnosis_difficulty', False):
                complexity += 0.6
                
        elif activity == ActivityType.COOKING:
            if context.get('limited_ingredients', False):
                complexity += 0.4
            if context.get('large_group', False):
                complexity += 0.3
                
        elif activity == ActivityType.CARPENTRY:
            if context.get('limited_materials', False):
                complexity += 0.5
            if context.get('structural_requirements', False):
                complexity += 0.6
            if context.get('team_coordination', False):
                complexity += 0.4
        
        return min(2.5, complexity)  # 最大2.5倍
    
    def _calculate_social_impact(self, activity: ActivityType, context: Dict[str, Any]) -> float:
        """社会的インパクトを計算"""
        
        impact = 1.0
        
        # 人数による影響
        people_affected = context.get('people_affected', 1)
        impact *= (1 + math.log(people_affected) * 0.2)
        
        # 緊急度
        if context.get('emergency', False):
            impact *= 1.5
        
        # 村全体への影響
        if context.get('village_wide_impact', False):
            impact *= 1.8
        
        return min(3.0, impact)
    
    def update_alignment_inertia_with_meaning_pressure(self, person_id: str, 
                                                      activity: ActivityType,
                                                      context: Dict[str, Any],
                                                      time_decay: float = 0.98) -> float:
        """意味圧ベースでアライメント慣性を更新"""
        
        # 現在の慣性値を取得
        current_inertia = self.alignment_inertia[person_id][activity]
        
        # 意味圧を計算
        meaning_pressure = self.calculate_meaning_pressure(person_id, activity, context)
        
        # 活動の整合仕事を計算
        G0 = self.base_alignment[activity]
        g = 0.3  # 慣性結合係数
        rho = self.activity_resistance[activity]
        
        # 整合流: j = (G0 + g * κ) * p
        j = (G0 + g * current_inertia) * meaning_pressure
        
        # 整合仕事: W = p·j - ρj²
        alignment_work = meaning_pressure * j - rho * (j ** 2)
        
        # 時間減衰を適用
        decayed_inertia = current_inertia * time_decay
        
        # 仕事量による慣性更新
        learning_rate = self._get_learning_rate(activity, context)
        
        if alignment_work > 0:
            # 正の仕事は慣性を強化
            new_inertia = decayed_inertia + learning_rate * alignment_work
        else:
            # 負の仕事は軽微な減少
            new_inertia = decayed_inertia + learning_rate * alignment_work * 0.2
        
        # 慣性の範囲制限
        new_inertia = max(0.05, min(new_inertia, 10.0))
        
        self.alignment_inertia[person_id][activity] = new_inertia
        
        # 経験履歴を更新
        self._update_experience_history(person_id, activity, context, alignment_work)
        
        return new_inertia
    
    def _get_learning_rate(self, activity: ActivityType, context: Dict[str, Any]) -> float:
        """活動別の学習率を取得"""
        
        base_rates = {
            ActivityType.HUNTING: 0.12,
            ActivityType.CAREGIVING: 0.15,
            ActivityType.COOKING: 0.18,
            ActivityType.SOCIAL_COORDINATION: 0.10,
            ActivityType.CARPENTRY: 0.14
        }
        
        learning_rate = base_rates[activity]
        
        # 文脈による調整
        if context.get('mentor_present', False):
            learning_rate *= 1.3
        if context.get('high_stakes', False):
            learning_rate *= 1.2
        
        return learning_rate
    
    def _update_experience_history(self, person_id: str, activity: ActivityType, 
                                 context: Dict[str, Any], alignment_work: float):
        """経験履歴を更新"""
        
        experience = {
            'context': context.copy(),
            'alignment_work': alignment_work,
            'meaning_pressure': self.calculate_meaning_pressure(person_id, activity, context)
        }
        
        self.experience_history[person_id][activity].append(experience)
        
        # 履歴のサイズ制限
        if len(self.experience_history[person_id][activity]) > 30:
            self.experience_history[person_id][activity] = \
                self.experience_history[person_id][activity][-20:]
    
    def get_villager_skill_level(self, person_id: str, activity: ActivityType) -> float:
        """村人のスキルレベルを取得"""
        return self.alignment_inertia[person_id][activity]
    
    def get_village_expertise_distribution(self) -> Dict[str, Dict[str, float]]:
        """村全体の専門性分布を取得"""
        
        distribution = {}
        for person_id in self.alignment_inertia:
            distribution[person_id] = {}
            for activity in ActivityType:
                distribution[person_id][activity.value] = \
                    self.alignment_inertia[person_id][activity]
        
        return distribution
    
    def calculate_village_learning_efficiency(self) -> Dict[str, float]:
        """村全体の学習効率を計算"""
        
        efficiency = {}
        
        for activity in ActivityType:
            total_inertia = 0
            person_count = 0
            
            for person_id in self.alignment_inertia:
                if activity in self.alignment_inertia[person_id]:
                    total_inertia += self.alignment_inertia[person_id][activity]
                    person_count += 1
            
            if person_count > 0:
                efficiency[activity.value] = total_inertia / person_count
            else:
                efficiency[activity.value] = 0.0
        
        return efficiency


def demonstrate_village_meaning_pressure():
    """村の意味圧システムのデモンストレーション"""
    
    print("=== 村の意味圧ベース成長システム デモ ===\n")
    
    village_system = VillageMeaningPressureSystem()
    
    # 村人たち
    villagers = ["狩人アキラ", "看護師ユミ", "料理人タロウ", "調整役サクラ"]
    
    # シナリオ1: 日常的な活動
    print("【シナリオ1: 日常的な活動の繰り返し】")
    for day in range(1, 6):
        print(f"\n--- 第{day}日目 ---")
        
        # 狩人アキラ：日常的な狩り
        context = {
            'success': True,
            'effectiveness': 0.6,
            'difficulty': 0.4,
            'large_prey': False,
            'people_affected': 3
        }
        
        hunting_inertia = village_system.update_alignment_inertia_with_meaning_pressure(
            "狩人アキラ", ActivityType.HUNTING, context
        )
        print(f"狩人アキラの狩猟慣性: {hunting_inertia:.3f}")
        
        # 看護師ユミ：日常的な看護
        context = {
            'success': True,
            'effectiveness': 0.7,
            'life_threatening': False,
            'people_affected': 2
        }
        
        care_inertia = village_system.update_alignment_inertia_with_meaning_pressure(
            "看護師ユミ", ActivityType.CAREGIVING, context
        )
        print(f"看護師ユミの看護慣性: {care_inertia:.3f}")
    
    print("\n" + "="*50)
    
    # シナリオ2: 危機的状況
    print("【シナリオ2: 危機的状況での活動】")
    
    # 食料危機での狩猟
    crisis_context = {
        'success': True,
        'effectiveness': 0.8,
        'difficulty': 0.9,
        'emergency': True,
        'large_prey': True,
        'danger_level': 0.8,
        'people_affected': 15,
        'village_wide_impact': True
    }
    
    crisis_hunting = village_system.update_alignment_inertia_with_meaning_pressure(
        "狩人アキラ", ActivityType.HUNTING, crisis_context
    )
    print(f"危機時の狩猟後 - アキラの慣性: {crisis_hunting:.3f}")
    
    # 生命に関わる看護
    emergency_care_context = {
        'success': True,
        'effectiveness': 0.9,
        'life_threatening': True,
        'patient_recovery': True,
        'emergency': True,
        'people_affected': 1,
        'high_stakes': True
    }
    
    emergency_care = village_system.update_alignment_inertia_with_meaning_pressure(
        "看護師ユミ", ActivityType.CAREGIVING, emergency_care_context
    )
    print(f"緊急看護後 - ユミの慣性: {emergency_care:.3f}")
    
    # 祭りの料理
    feast_context = {
        'success': True,
        'effectiveness': 0.95,
        'feast_preparation': True,
        'new_recipe': True,
        'collaboration': True,
        'people_affected': 20,
        'village_wide_impact': True
    }
    
    feast_cooking = village_system.update_alignment_inertia_with_meaning_pressure(
        "料理人タロウ", ActivityType.COOKING, feast_context
    )
    print(f"祭り料理後 - タロウの慣性: {feast_cooking:.3f}")
    
    print("\n" + "="*50)
    
    # 最終統計
    print("【村全体の専門性分布】")
    distribution = village_system.get_village_expertise_distribution()
    
    for person_id, skills in distribution.items():
        print(f"\n{person_id}:")
        for activity, level in skills.items():
            if level > 0.05:
                print(f"  {activity}: {level:.3f}")
    
    print(f"\n【村全体の学習効率】")
    efficiency = village_system.calculate_village_learning_efficiency()
    for activity, eff in efficiency.items():
        print(f"{activity}: {eff:.3f}")


if __name__ == "__main__":
    demonstrate_village_meaning_pressure()