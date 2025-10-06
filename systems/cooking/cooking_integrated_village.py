"""
Village Life SSD Simulation - Enhanced Cooking Reputation System
村ライフSSDシミュレーション - 料理評判システム統合版

料理が得意になると村人から依頼される料理人システム
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from core.village_ssd_adapter import VillageSSDAdapter, update_alignment_inertia, manage_territory_relationship

# 既存システムのインポート
# from integrated_village_simulation import IntegratedVillageSystem, VillageEvent, VillageStatus  # 循環インポート回避のためコメントアウト
# ActivityTypeは現在はvillage_meaning_pressure_systemからインポート
from core.village_meaning_pressure_system import ActivityType
from systems.social.rumor_system import RumorSystem, RumorType

class VillageEvent(Enum):
    """村の出来事"""
    HUNTING_SUCCESS = "hunting_success"
    HUNTING_FAILURE = "hunting_failure"  
    CARE_PROVIDED = "care_provided"
    MEAL_PREPARED = "meal_prepared"
    CONSTRUCTION_COMPLETED = "construction_completed"
    EMERGENCY_SITUATION = "emergency_situation"
    INNOVATION_ACHIEVED = "innovation_achieved"
    FEAST_CELEBRATION = "feast_celebration"
    NATURAL_CAREGIVER_EMERGED = "natural_caregiver_emerged"

@dataclass
class CookingReputation:
    """料理評判データ"""
    cook_name: str
    success_count: int = 0           # 成功回数
    total_attempts: int = 0          # 総試行回数
    taste_score_sum: float = 0.0     # 美味しさスコア合計
    reputation_score: float = 0.0    # 評判スコア
    cooking_requests: int = 0        # 依頼された回数
    specialization_known: bool = False  # 料理人として認知されているか
    signature_dishes: List[str] = field(default_factory=list)  # 得意料理

@dataclass
class CookingRequest:
    """料理依頼"""
    requester_name: str              # 依頼者
    preferred_cook: Optional[str] = None  # 指名希望料理人
    occasion: str = "daily"          # 機会（daily, celebration, recovery）
    urgency_level: float = 0.5       # 緊急度
    group_size: int = 1              # 対象人数

class CookingStyle(Enum):
    """料理スタイル"""
    SIMPLE = "simple"                # シンプル料理
    HEARTY = "hearty"               # ボリューム重視
    REFINED = "refined"             # 洗練された料理
    COMFORT = "comfort"             # 癒し系料理
    FESTIVE = "festive"             # 祝祭料理

@dataclass
class Dish:
    """料理データ"""
    name: str
    cooking_style: CookingStyle
    difficulty: float               # 難易度 (0.1-1.0)
    base_taste: float              # 基本美味しさ
    preparation_time: float        # 調理時間
    meat_required: float           # 必要な肉量
    happiness_bonus: float         # 幸福度ボーナス

class EnhancedCookingSystem:
    """拡張料理システム"""
    
    def __init__(self, base_village):  # 循環インポート回避のため型ヒントを削除
        self.base_village = base_village
        self.cook_reputations: Dict[str, CookingReputation] = {}
        self.cooking_requests: List[CookingRequest] = []
        
        # SSD Core Engine の初期化
        self.ssd_adapter = VillageSSDAdapter("enhanced_cooking_system")
        self.ssd_engine = self.ssd_adapter.engine
        
        # 噂システムの統合（base_villageから取得）
        if hasattr(base_village, 'rumor_system'):
            self.rumor_system = base_village.rumor_system
        else:
            # フォールバック：独自の噂システム
            self.rumor_system = RumorSystem()
            villager_names = [v.name for v in base_village.villagers] if hasattr(base_village, 'villagers') else []
            self.rumor_system.initialize_reputations(villager_names, {})
        
        # 料理データベース
        self.dish_database = {
            # シンプル料理
            "焼き肉": Dish("焼き肉", CookingStyle.SIMPLE, 0.2, 0.6, 0.3, 0.5, 0.1),
            "肉スープ": Dish("肉スープ", CookingStyle.SIMPLE, 0.3, 0.7, 0.4, 0.3, 0.15),
            
            # ボリューム重視
            "肉団子": Dish("肉団子", CookingStyle.HEARTY, 0.4, 0.7, 0.5, 0.8, 0.2),
            "煮込み料理": Dish("煮込み料理", CookingStyle.HEARTY, 0.5, 0.8, 0.8, 0.6, 0.25),
            
            # 洗練された料理
            "香草焼き": Dish("香草焼き", CookingStyle.REFINED, 0.6, 0.9, 0.7, 0.4, 0.3),
            "薄切り刺身": Dish("薄切り刺身", CookingStyle.REFINED, 0.7, 0.85, 0.6, 0.2, 0.35),
            
            # 癒し系料理
            "お粥": Dish("お粥", CookingStyle.COMFORT, 0.3, 0.6, 0.4, 0.2, 0.4),
            "温かいスープ": Dish("温かいスープ", CookingStyle.COMFORT, 0.4, 0.75, 0.5, 0.3, 0.35),
            
            # 祝祭料理
            "大皿焼肉": Dish("大皿焼肉", CookingStyle.FESTIVE, 0.5, 0.8, 1.0, 2.0, 0.4),
            "特製シチュー": Dish("特製シチュー", CookingStyle.FESTIVE, 0.8, 0.95, 1.2, 1.5, 0.5),
        }
        
        # 料理評判閾値
        self.reputation_thresholds = {
            "known_cook": 5,           # 料理人として知られる
            "skilled_cook": 15,        # 腕の良い料理人
            "master_chef": 30,         # 料理の達人
        }
        
        # 依頼発生率
        self.request_rates = {
            "daily_cooking": 0.7,      # 日常料理依頼率
            "special_occasion": 0.3,   # 特別な機会
            "recovery_meal": 0.8,      # 回復食依頼率
        }
    
    def initialize_cooking_reputations(self, villager_names: List[str] = None):
        """料理評判初期化"""
        
        if villager_names is None:
            # base_village から取得を試みる
            if hasattr(self.base_village, 'villagers'):
                villager_names = [v.name for v in self.base_village.villagers]
            else:
                villager_names = []
        
        for name in villager_names:
            if name not in self.cook_reputations:
                self.cook_reputations[name] = CookingReputation(cook_name=name)
    
    def generate_cooking_requests(self) -> List[CookingRequest]:
        """料理依頼生成"""
        
        requests = []
        
        # 負傷者向け回復食依頼
        injured_npcs = [name for name, npc in self.base_village.base_system.npcs.items() 
                       if npc["is_injured"]]
        
        for injured_name in injured_npcs:
            if random.random() < self.request_rates["recovery_meal"]:
                requester = self._find_requester_for_patient(injured_name)
                skilled_cooks = self._find_skilled_cooks()
                
                request = CookingRequest(
                    requester_name=requester,
                    preferred_cook=skilled_cooks[0] if skilled_cooks else None,
                    occasion="recovery",
                    urgency_level=0.8,
                    group_size=1
                )
                requests.append(request)
        
        # 日常料理依頼
        if random.random() < self.request_rates["daily_cooking"]:
            # 村の誰かが料理を依頼
            potential_requesters = list(self.base_village.base_system.npcs.keys())
            requester = random.choice(potential_requesters)
            
            skilled_cooks = self._find_skilled_cooks()
            
            request = CookingRequest(
                requester_name=requester,
                preferred_cook=skilled_cooks[0] if skilled_cooks else None,
                occasion="daily",
                urgency_level=random.uniform(0.3, 0.6),
                group_size=random.randint(2, 5)
            )
            requests.append(request)
        
        # 特別な機会（祝宴など）
        recent_celebrations = [event for day, event, details in self.base_village.village_events 
                             if event == VillageEvent.FEAST_CELEBRATION and 
                             day == self.base_village.village_status.day]
        
        if recent_celebrations or random.random() < self.request_rates["special_occasion"]:
            requester = self._find_social_coordinator_or_random()
            skilled_cooks = self._find_skilled_cooks()
            
            request = CookingRequest(
                requester_name=requester,
                preferred_cook=skilled_cooks[0] if skilled_cooks else None,
                occasion="celebration",
                urgency_level=0.6,
                group_size=len(self.base_village.base_system.npcs)
            )
            requests.append(request)
        
        return requests
    
    def process_cooking_requests(self, requests: List[CookingRequest]) -> List[Tuple[str, CookingRequest]]:
        """料理依頼処理"""
        
        assignments = []
        
        for request in requests:
            print(f"    料理依頼: {request.requester_name}が{request.occasion}料理を依頼")
            
            # 指名料理人がいる場合
            if request.preferred_cook:
                cook = self.base_village.base_system.npcs.get(request.preferred_cook)
                
                if (cook and 
                    not cook["is_injured"] and 
                    cook["daily_energy_used"] < 0.8):
                    
                    assignments.append((request.preferred_cook, request))
                    print(f"      {request.preferred_cook}が指名で料理を担当")
                    
                    # 依頼回数記録
                    if request.preferred_cook in self.cook_reputations:
                        self.cook_reputations[request.preferred_cook].cooking_requests += 1
                    
                    continue
            
            # 通常の料理人選択
            available_cooks = self._find_available_cooks()
            
            if available_cooks:
                selected_cook = self._select_cook_by_reputation(available_cooks, request)
                assignments.append((selected_cook, request))
                print(f"      {selected_cook}が料理を担当")
            else:
                print(f"      利用可能な料理人がいません")
        
        return assignments
    
    def execute_cooking_assignment(self, cook_name: str, request: CookingRequest):
        """料理実行"""
        
        cook = self.base_village.base_system.npcs[cook_name]
        
        # 料理選択（機会と技術レベルに応じて）
        dish = self._select_appropriate_dish(cook_name, request)
        
        # 料理スキル計算
        cooking_experience = self.base_village.base_system.specialization_levels[cook_name][ActivityType.COOKING]
        cooking_skill = min(1.0, 0.3 + cooking_experience * 0.01)  # 経験値に基づくスキル
        
        # 性格による料理スタイル修正
        personality = cook["personality"]
        style_bonus = self._get_personality_cooking_bonus(personality, dish.cooking_style)
        
        # 料理成功判定
        success_probability = min(0.95, cooking_skill * 0.6 + (1.0 - dish.difficulty) * 0.3 + style_bonus * 0.1)
        success = random.random() < success_probability
        
        # 美味しさ計算
        if success:
            taste_score = min(1.0, dish.base_taste * cooking_skill * (1.0 + style_bonus * 0.5))
            result_text = "成功"
        else:
            taste_score = dish.base_taste * 0.4 * cooking_skill
            result_text = "失敗"
        
        # 肉消費
        meat_used = dish.meat_required * request.group_size
        if self.base_village.meat_storage >= meat_used:
            self.base_village.meat_storage -= meat_used
        else:
            # 肉不足の場合、品質低下
            taste_score *= 0.6
            print(f"        材料不足により品質低下")
        
        print(f"      {cook_name}が{dish.name}を調理 (美味しさ:{taste_score:.2f}) {result_text}")
        
        # 効果適用
        self._apply_cooking_effects(cook_name, request, dish, taste_score, success)
        
        # 評判更新
        self._update_cooking_reputation(cook_name, taste_score, success, dish)
        
        # 経験値蓄積
        exp_gain = (taste_score * 10 + dish.difficulty * 5) if success else (taste_score * 3)
        self.base_village.base_system.specialization_levels[cook_name][ActivityType.COOKING] += exp_gain
        
        # 料理傾向向上
        if success and taste_score > 0.7:
            current_pref = self.base_village.base_system.activity_preferences[cook_name][ActivityType.COOKING]
            self.base_village.base_system.activity_preferences[cook_name][ActivityType.COOKING] = min(1.0, current_pref + 0.03)
        
        # 噂生成（食べた人が体験を語る）
        self._generate_rumor_from_cooking(cook_name, request.requester_name, success, taste_score, dish)
        
        # エネルギー消費
        cook["daily_energy_used"] += dish.preparation_time * request.group_size * 0.1
        
        return taste_score, success
    
    def _find_skilled_cooks(self) -> List[str]:
        """腕の良い料理人を見つける"""
        
        skilled = []
        
        for name, reputation in self.cook_reputations.items():
            if (reputation.specialization_known and 
                reputation.reputation_score > 0.6 and
                not self.base_village.base_system.npcs[name]["is_injured"]):
                
                skilled.append(name)
        
        # 評判スコア順にソート
        skilled.sort(key=lambda x: self.cook_reputations[x].reputation_score, reverse=True)
        
        return skilled
    
    def _find_available_cooks(self) -> List[str]:
        """利用可能な料理人を見つける"""
        
        available = []
        
        for name, npc in self.base_village.base_system.npcs.items():
            if (not npc["is_injured"] and 
                npc["daily_energy_used"] < 0.8):
                
                available.append(name)
        
        return available
    
    def _select_cook_by_reputation(self, available_cooks: List[str], request: CookingRequest) -> str:
        """評判による料理人選択"""
        
        scored_cooks = []
        
        for cook_name in available_cooks:
            cook = self.base_village.base_system.npcs[cook_name]
            
            # 基本スコア
            base_score = 0.5
            
            # 評判ボーナス
            if cook_name in self.cook_reputations:
                reputation = self.cook_reputations[cook_name]
                reputation_bonus = reputation.reputation_score * 0.5
                base_score += reputation_bonus
                
                # 特技認知ボーナス
                if reputation.specialization_known:
                    base_score += 0.3
            
            # 料理経験ボーナス
            cooking_exp = self.base_village.base_system.specialization_levels[cook_name][ActivityType.COOKING]
            experience_bonus = min(0.3, cooking_exp * 0.003)
            base_score += experience_bonus
            
            # 性格による機会適性
            personality = cook["personality"]
            occasion_bonus = self._get_occasion_personality_bonus(personality, request.occasion)
            base_score += occasion_bonus * 0.2
            
            scored_cooks.append((cook_name, base_score))
        
        # スコア順にソート
        scored_cooks.sort(key=lambda x: x[1], reverse=True)
        
        return scored_cooks[0][0] if scored_cooks else available_cooks[0]
    
    def _select_appropriate_dish(self, cook_name: str, request: CookingRequest) -> Dish:
        """適切な料理選択"""
        
        # 機会に応じた料理スタイル決定
        if request.occasion == "recovery":
            preferred_styles = [CookingStyle.COMFORT, CookingStyle.SIMPLE]
        elif request.occasion == "celebration":
            preferred_styles = [CookingStyle.FESTIVE, CookingStyle.REFINED]
        else:  # daily
            preferred_styles = [CookingStyle.SIMPLE, CookingStyle.HEARTY]
        
        # 料理人のスキルレベル
        cooking_exp = self.base_village.base_system.specialization_levels[cook_name][ActivityType.COOKING]
        skill_level = min(1.0, cooking_exp * 0.01)
        
        # 適切な料理を選択
        suitable_dishes = []
        
        for dish_name, dish in self.dish_database.items():
            if (dish.cooking_style in preferred_styles and 
                dish.difficulty <= skill_level + 0.3):  # スキルより少し上まで挑戦可能
                
                suitable_dishes.append(dish)
        
        if not suitable_dishes:
            # 適切な料理がない場合は最も簡単な料理
            suitable_dishes = [dish for dish in self.dish_database.values() 
                             if dish.difficulty <= 0.4]
        
        return random.choice(suitable_dishes) if suitable_dishes else list(self.dish_database.values())[0]
    
    def _get_personality_cooking_bonus(self, personality: str, cooking_style: CookingStyle) -> float:
        """性格と料理スタイルの相性ボーナス"""
        
        compatibility_matrix = {
            "creative": {CookingStyle.REFINED: 0.3, CookingStyle.FESTIVE: 0.2},
            "caring": {CookingStyle.COMFORT: 0.3, CookingStyle.SIMPLE: 0.2},
            "social": {CookingStyle.FESTIVE: 0.3, CookingStyle.HEARTY: 0.2},
            "patient": {CookingStyle.REFINED: 0.2, CookingStyle.COMFORT: 0.2},
            "helpful": {CookingStyle.HEARTY: 0.2, CookingStyle.SIMPLE: 0.2},
        }
        
        return compatibility_matrix.get(personality, {}).get(cooking_style, 0.0)
    
    def _get_occasion_personality_bonus(self, personality: str, occasion: str) -> float:
        """性格と機会の適性ボーナス"""
        
        occasion_matrix = {
            "caring": {"recovery": 0.3, "daily": 0.2},
            "social": {"celebration": 0.3, "daily": 0.1},
            "helpful": {"daily": 0.3, "recovery": 0.2},
            "creative": {"celebration": 0.2, "daily": 0.1},
        }
        
        return occasion_matrix.get(personality, {}).get(occasion, 0.0)
    
    def _apply_cooking_effects(self, cook_name: str, request: CookingRequest, dish: Dish, taste_score: float, success: bool):
        """料理効果適用"""
        
        # 対象者特定
        if request.occasion == "recovery":
            # 負傷者への回復食
            injured_npcs = [name for name, npc in self.base_village.base_system.npcs.items() if npc["is_injured"]]
            target_npcs = injured_npcs[:request.group_size]
        elif request.occasion == "celebration":
            # 全村民対象
            target_npcs = list(self.base_village.base_system.npcs.keys())
        else:
            # 日常料理：ランダムに対象選択
            all_npcs = list(self.base_village.base_system.npcs.keys())
            target_npcs = random.sample(all_npcs, min(request.group_size, len(all_npcs)))
        
        # 効果適用
        for target_name in target_npcs:
            target = self.base_village.base_system.npcs[target_name]
            
            # 基本幸福度向上
            happiness_gain = dish.happiness_bonus * taste_score
            if success:
                happiness_gain *= 1.5
            
            target["happiness"] = min(1.0, target["happiness"] + happiness_gain)
            
            # 回復食の場合、追加効果
            if request.occasion == "recovery" and target["is_injured"]:
                health_recovery = taste_score * 0.15
                target["health"] = min(1.0, target["health"] + health_recovery)
                
                if taste_score > 0.8:  # 特に美味しい場合
                    print(f"        🌟 {target_name}の体調が著しく改善！")
            
            # 満腹感向上
            hunger_gain = min(0.3, taste_score * 0.4)
            target["hunger_level"] = min(1.0, target["hunger_level"] + hunger_gain)
        
        # 料理人への関係値向上（SSD Core Engine使用）
        cook = self.base_village.base_system.npcs[cook_name]
        for target_name in target_npcs:
            if target_name != cook_name:
                # SSD Core Engineによる領域ベース信頼更新
                self._apply_ssd_cooking_effects(cook_name, target_name, success, taste_score, dish, request)
                
                # 従来の関係値も更新（互換性のため）
                old_rel = cook["relationships"].get(target_name, 0.3)
                relationship_gain = taste_score * 0.1 if success else taste_score * 0.05
                new_rel = min(1.0, old_rel + relationship_gain)
                
                cook["relationships"][target_name] = new_rel
                self.base_village.base_system.npcs[target_name]["relationships"][cook_name] = new_rel
    
    def _update_cooking_reputation(self, cook_name: str, taste_score: float, success: bool, dish: Dish):
        """料理評判更新"""
        
        if cook_name not in self.cook_reputations:
            self.cook_reputations[cook_name] = CookingReputation(cook_name=cook_name)
        
        reputation = self.cook_reputations[cook_name]
        
        # 基本統計更新
        reputation.total_attempts += 1
        reputation.taste_score_sum += taste_score
        
        if success:
            reputation.success_count += 1
        
        # 得意料理記録
        if success and taste_score > 0.8:
            if dish.name not in reputation.signature_dishes:
                reputation.signature_dishes.append(dish.name)
                if len(reputation.signature_dishes) == 1:
                    print(f"        ⭐ {cook_name}の得意料理：{dish.name}")
        
        # 評判スコア計算
        if reputation.total_attempts > 0:
            avg_taste = reputation.taste_score_sum / reputation.total_attempts
            success_rate = reputation.success_count / reputation.total_attempts
            experience_modifier = min(1.5, 1.0 + reputation.total_attempts * 0.02)
            
            reputation.reputation_score = avg_taste * success_rate * experience_modifier
        
        # 特技認知判定
        if (reputation.success_count >= self.reputation_thresholds["known_cook"] and
            not reputation.specialization_known):
            
            reputation.specialization_known = True
            self.base_village.base_system.npcs[cook_name]["natural_cook"] = True  # フラグ追加
            print(f"    {cook_name}が料理人として村で知られるようになりました！")
    
    def _generate_rumor_from_cooking(self, cook_name: str, eater_name: str, success: bool, taste_score: float, dish):
        """料理結果から噂を生成（食べた人が体験を語る）"""
        
        # 食べた人が他の村人に料理の体験を話す
        all_villagers = list(self.base_village.base_system.npcs.keys())
        potential_listeners = [name for name in all_villagers if name not in [cook_name, eater_name]]
        
        # 味の強度を噂の強度に変換
        intensity = min(1.0, taste_score + random.uniform(0.1, 0.3))
        
        # 食べた人が料理体験を話す（性格によって広めるか決定）
        if hasattr(self, 'rumor_system') and self.rumor_system:
            eater_rumors = self.rumor_system.create_rumor_from_experience(
                experiencer=eater_name,
                target=cook_name,
                rumor_type=RumorType.CRAFTING_SKILL,  # 料理は工芸スキルとして扱う
                positive=success and taste_score > 0.5,
                intensity=intensity,
                potential_listeners=potential_listeners
            )
            
            # 特に美味しい場合、目撃者（同席者）からも噂が出る可能性
            if success and taste_score > 0.8 and potential_listeners and random.random() < 0.3:
                witness = random.choice(potential_listeners)
                self.rumor_system.create_rumor_from_experience(
                    experiencer=witness,
                    target=cook_name,
                    rumor_type=RumorType.CRAFTING_SKILL,
                    positive=True,
                    intensity=intensity * 0.8,  # 間接体験なので少し弱める
                    potential_listeners=[name for name in potential_listeners if name != witness]
                )
    
    def _apply_ssd_cooking_effects(self, cook_name: str, target_name: str, success: bool, 
                                  taste_score: float, dish, request: CookingRequest):
        """SSD Core Engineを使用した料理効果適用"""
        
        # 料理の種類と成功度に基づく領域決定
        domain_mapping = {
            "recovery": "social_care",           # 回復食は看護的
            "celebration": "social_coordination", # 祝祭料理は社交的
            "daily": "resource_creation"         # 日常料理は資源創造
        }
        
        primary_domain = domain_mapping.get(request.occasion, "resource_creation")
        
        # SSDによる信頼関係更新
        effect_strength = taste_score * (1.5 if success else 0.7)
        
        # 料理成功時の信頼向上
        if success and taste_score > 0.6:
            self.ssd_adapter.update_trust_through_interaction(
                cook_name, target_name, primary_domain, 
                positive=True, effect_strength=effect_strength
            )
            
            # 特に美味しい料理の場合、追加効果
            if taste_score > 0.8:
                # 優しさ・配慮の領域でも信頼向上
                self.ssd_adapter.update_trust_through_interaction(
                    cook_name, target_name, "social_care",
                    positive=True, effect_strength=effect_strength * 0.7
                )
        
        # 料理失敗時の影響
        elif not success and taste_score < 0.4:
            self.ssd_adapter.update_trust_through_interaction(
                cook_name, target_name, primary_domain,
                positive=False, effect_strength=effect_strength * 0.5
            )
        
        # アライメント慣性効果（継続的な料理提供による信頼安定化）
        cook_reputation = self.cook_reputations.get(cook_name)
        if cook_reputation and cook_reputation.success_count > 3:
            # 経験豊富な料理人は信頼が安定する
            update_alignment_inertia(
                self.ssd_engine,
                cook_name, 
                target_name,
                primary_domain,
                inertia_change=0.1  # 信頼の安定性向上
            )
        
        # 料理を通じた領域関係管理
        # 回復食は看護者としての評価、祝祭料理は社交者としての評価
        if request.occasion == "recovery" and success:
            manage_territory_relationship(
                self.ssd_engine,
                cook_name,
                "caregiving_territory",
                relationship_change=0.2
            )
        elif request.occasion == "celebration" and success:
            manage_territory_relationship(
                self.ssd_engine,
                cook_name,
                "social_coordination_territory", 
                relationship_change=0.2
            )
    
    def _find_requester_for_patient(self, patient_name: str) -> str:
        """患者のための依頼者を見つける"""
        
        patient = self.base_village.base_system.npcs[patient_name]
        
        # 関係値が高い人から選ぶ
        potential_requesters = []
        
        for name, npc in self.base_village.base_system.npcs.items():
            if name != patient_name and not npc["is_injured"]:
                relationship = patient["relationships"].get(name, 0.3)
                if relationship > 0.4:
                    potential_requesters.append((name, relationship))
        
        if potential_requesters:
            potential_requesters.sort(key=lambda x: x[1], reverse=True)
            return potential_requesters[0][0]
        else:
            return patient_name
    
    def _find_social_coordinator_or_random(self) -> str:
        """社交コーディネーターまたはランダム選択"""
        
        # 社交コーディネーターを優先
        coordinators = [name for name, npc in self.base_village.base_system.npcs.items() 
                       if npc.get("social_coordinator", False)]
        
        if coordinators:
            return random.choice(coordinators)
        else:
            return random.choice(list(self.base_village.base_system.npcs.keys()))
    
    def display_cooking_reputation_status(self):
        """料理評判状況表示"""
        
        print(f"\n  料理評判状況:")
        
        # 評判でソート
        reputation_list = []
        
        for name, reputation in self.cook_reputations.items():
            if reputation.total_attempts > 0:
                reputation_list.append((name, reputation))
        
        if not reputation_list:
            print("    まだ料理評判データがありません")
            return
        
        reputation_list.sort(key=lambda x: x[1].reputation_score, reverse=True)
        
        for name, reputation in reputation_list:
            status_icons = []
            
            if reputation.specialization_known:
                status_icons.append("⭐")
            
            if reputation.success_count >= self.reputation_thresholds["skilled_cook"]:
                status_icons.append("🏆")
            
            if reputation.success_count >= self.reputation_thresholds["master_chef"]:
                status_icons.append("[王冠]")
            
            status_str = "".join(status_icons) if status_icons else ""
            
            success_rate = (reputation.success_count / reputation.total_attempts * 100) if reputation.total_attempts > 0 else 0
            avg_taste = (reputation.taste_score_sum / reputation.total_attempts) if reputation.total_attempts > 0 else 0
            
            print(f"    {name} {status_str}")
            print(f"      評判スコア: {reputation.reputation_score:.2f}")
            print(f"      成功率: {success_rate:.0f}% ({reputation.success_count}/{reputation.total_attempts})")
            print(f"      平均美味しさ: {avg_taste:.2f}")
            print(f"      依頼回数: {reputation.cooking_requests}")
            
            if reputation.signature_dishes:
                print(f"      得意料理: {', '.join(reputation.signature_dishes)}")

class EnhancedVillageWithCooking:  # 循環インポート回避のため継承を一時的に削除
    """料理システム統合村"""
    
    def __init__(self):
        # 循環インポート回避のため遅延インポート
        from simulation.integrated_village_simulation import IntegratedVillageSimulation
        IntegratedVillageSimulation.__init__(self)
        self.cooking_system = None  # 後で初期化
    
    def initialize_integrated_village(self, village_size: int = 10):
        """料理システム統合初期化"""
        
        # ベースシステム初期化 (遅延インポート)
        from simulation.integrated_village_simulation import IntegratedVillageSimulation
        IntegratedVillageSimulation.initialize_integrated_village(self, village_size)
        
        # 料理システム初期化
        self.cooking_system = EnhancedCookingSystem(self)
        self.cooking_system.initialize_cooking_reputations()
        
        # 料理フラグをNPCに追加
        for name in self.base_system.npcs.keys():
            self.base_system.npcs[name]["natural_cook"] = False
    
    def _evening_social_activities(self):
        """夕方の社交・食事活動（料理システム統合版）"""
        
        print(f"  🌆 夕方の社交・料理・食事活動")
        
        # 料理依頼生成と処理
        cooking_requests = self.cooking_system.generate_cooking_requests()
        
        if cooking_requests:
            print(f"    料理依頼: {len(cooking_requests)}件")
            assignments = self.cooking_system.process_cooking_requests(cooking_requests)
            
            # 料理実行
            for cook_name, request in assignments:
                taste_score, success = self.cooking_system.execute_cooking_assignment(cook_name, request)
        
        # 通常の食事処理
        self._process_daily_meals()
        
        # 社交集会
        if random.random() < self.event_rates["social_gathering"]:
            socializers = self._select_activity_participants(ActivityType.SOCIALIZING, max_participants=6)
            if socializers:
                print(f"    🎉 社交集会: {', '.join(socializers)}")
                
                # 社交活動の効果
                for socializer in socializers:
                    # 幸福度向上
                    self.base_system.npcs[socializer]["happiness"] = min(1.0, 
                        self.base_system.npcs[socializer]["happiness"] + random.uniform(0.05, 0.15))
                    
                    # 経験値獲得
                    exp_gain = random.uniform(8, 15)
                    self.base_system.specialization_levels[socializer][ActivityType.SOCIALIZING] += exp_gain
                    
                    # エネルギー消費（軽微）
                    self.base_system.npcs[socializer]["daily_energy_used"] += random.uniform(0.1, 0.2)
                
                # 全体的な関係値向上
                for i, name1 in enumerate(socializers):
                    for name2 in socializers[i+1:]:
                        npc1 = self.base_system.npcs[name1]
                        npc2 = self.base_system.npcs[name2]
                        
                        # 相互関係値向上
                        old_rel = npc1["relationships"].get(name2, 0.3)
                        new_rel = min(1.0, old_rel + random.uniform(0.02, 0.08))
                        npc1["relationships"][name2] = new_rel
                        npc2["relationships"][name1] = new_rel
        
        # 社交コーディネーター＆料理人認定チェック
        self._check_social_coordinator_emergence()
        self._check_natural_cook_emergence()
    
    def _check_natural_cook_emergence(self):
        """自然な料理人認定チェック"""
        
        for name, npc in self.base_system.npcs.items():
            cooking_exp = self.base_system.specialization_levels[name][ActivityType.COOKING]
            cooking_pref = self.base_system.activity_preferences[name][ActivityType.COOKING]
            
            if (cooking_exp > 35 and 
                cooking_pref > 0.75 and 
                not npc.get("natural_cook", False) and
                name in self.cooking_system.cook_reputations):
                
                reputation = self.cooking_system.cook_reputations[name]
                if reputation.specialization_known:
                    npc["natural_cook"] = True
                    print(f"    {name}が自然な料理人として認められました！")
                    self.village_events.append((self.village_status.day, VillageEvent.NATURAL_CAREGIVER_EMERGED, f"料理人:{name}"))  # イベント流用
    
    def _display_periodic_report(self, day: int):
        """定期レポート表示（料理システム統合版）"""
        
        print(f"\n" + "=" * 60)
        print(f"第{day}日目 - 定期レポート")
        print(f"=" * 60)
        
        # 村ステータス
        self._display_village_overview()
        
        # 役割分担状況
        natural_cooks = sum(1 for npc in self.base_system.npcs.values() if npc.get("natural_cook", False))
        
        print(f"\n🎭 役割分担状況:")
        print(f"  自然なハンター: {self.village_status.natural_hunters}名")
        print(f"  自然な看護師: {self.village_status.natural_caregivers}名")  
        print(f"  自然な料理人: {natural_cooks}名")
        print(f"  社交コーディネーター: {self.village_status.social_coordinators}名")
        
        # 看護評判状況
        if hasattr(self.reputation_system, 'display_reputation_status'):
            self.reputation_system.display_reputation_status()
        
        # 料理評判状況
        self.cooking_system.display_cooking_reputation_status()
        
        # 最近のイベント
        recent_events = [(event_day, event_type, details) for event_day, event_type, details in self.village_events if event_day > day - 5]
        if recent_events:
            print(f"\n📰 最近の出来事({len(recent_events)}件):")
            for event_day, event_type, details in self.village_events[-5:]:
                icon = self._get_event_icon(event_type)
                print(f"  {icon} 第{event_day}日目: {details}")
    
    def _display_final_comprehensive_report(self):
        """最終総合レポート表示（料理システム統合版）"""
        
        print(f"\n" + "=" * 80)
        print(f"🏆 料理統合村シミュレーション最終総合レポート")
        print(f"=" * 80)
        
        # 最終村ステータス
        self._display_village_overview()
        
        # 個人別専門化状況
        print(f"\n👥 個人別専門化状況:")
        
        for name, npc in self.base_system.npcs.items():
            specializations = []
            
            if npc["natural_hunter"]:
                hunt_stats = self.base_system.hunting_system.get_npc_hunting_status(name)
                specializations.append(f"ハンター(Lv.{hunt_stats['level']:.1f})")
            
            if npc["natural_caregiver"]:
                care_exp = self.base_system.specialization_levels[name][ActivityType.CAREGIVING]
                if name in self.reputation_system.caregiver_reputations:
                    reputation = self.reputation_system.caregiver_reputations[name]
                    specializations.append(f"🏥看護師(経験値{care_exp:.0f}, 評判{reputation.reputation_score:.2f})")
                else:
                    specializations.append(f"🏥看護師(経験値{care_exp:.0f})")
            
            if npc.get("natural_cook", False):
                cooking_exp = self.base_system.specialization_levels[name][ActivityType.COOKING]
                if name in self.cooking_system.cook_reputations:
                    reputation = self.cooking_system.cook_reputations[name]
                    signature = f", 得意:{', '.join(reputation.signature_dishes[:2])}" if reputation.signature_dishes else ""
                    specializations.append(f"料理人(経験値{cooking_exp:.0f}, 評判{reputation.reputation_score:.2f}{signature})")
                else:
                    specializations.append(f"料理人(経験値{cooking_exp:.0f})")
            
            if npc["social_coordinator"]:
                social_exp = self.base_system.specialization_levels[name][ActivityType.SOCIALIZING]
                specializations.append(f"🎭社交(経験値{social_exp:.0f})")
            
            if not specializations:
                # 最も経験値の高い活動を表示
                max_exp = 0
                max_activity = None
                for activity, exp in self.base_system.specialization_levels[name].items():
                    if exp > max_exp:
                        max_exp = exp
                        max_activity = activity
                
                if max_exp > 10:
                    activity_names = {
                        ActivityType.GATHERING: "🌿採取",
                        ActivityType.CRAFTING: "工作",
                        ActivityType.RESTING: "😴休息"
                    }
                    activity_name = activity_names.get(max_activity, str(max_activity.value))
                    specializations.append(f"{activity_name}(経験値{max_exp:.0f})")
                else:
                    specializations.append("汎用作業者")
            
            status_text = ", ".join(specializations)
            health_status = "負傷" if npc["is_injured"] else "健康"
            
            print(f"  {name} ({npc['personality']}): {status_text} [{health_status}, 幸福度{npc['happiness']:.2f}]")
        
        # 料理評判最終状況
        print(f"\n料理評判最終状況:")
        self.cooking_system.display_cooking_reputation_status()
        
        # 統計サマリー
        natural_cooks = sum(1 for npc in self.base_system.npcs.values() if npc.get("natural_cook", False))
        total_specialists = (self.village_status.natural_hunters + 
                           self.village_status.natural_caregivers + 
                           natural_cooks + 
                           self.village_status.social_coordinators)
        
        print(f"\n統計サマリー:")
        print(f"  シミュレーション日数: {self.village_status.day}日")
        print(f"  総イベント数: {len(self.village_events)}件")
        print(f"  最終食料貯蔵量: {self.village_status.total_meat_stored:.1f}単位")
        print(f"  最終村幸福度: {self.village_status.village_happiness:.2f}")
        print(f"  総合役割分担達成率: {total_specialists / self.village_status.total_population * 100:.1f}%")
        print(f"    - ハンター: {self.village_status.natural_hunters}名")
        print(f"    - 看護師: {self.village_status.natural_caregivers}名")
        print(f"    - 料理人: {natural_cooks}名")
        print(f"    - 社交コーディネーター: {self.village_status.social_coordinators}名")
        
        print(f"\n🎉 料理統合村シミュレーション完了！")
        print("狩猟・看護・料理の自然な役割分担により、より豊かな村社会が形成されました。")

def demonstrate_cooking_integrated_village():
    """料理統合村システムデモ実行"""
    
    print("=" * 100)
    print("🍳 村ライフSSD料理統合システム - 料理人自然発生デモ")
    print("=" * 100)
    
    # 料理統合システム初期化
    village = EnhancedVillageWithCooking()
    village.initialize_integrated_village(village_size=10)
    
    # 20日間シミュレーション実行
    village.simulate_village_days(num_days=20)

if __name__ == "__main__":
    demonstrate_cooking_integrated_village()