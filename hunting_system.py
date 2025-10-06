"""
Village Life SSD Simulation - Hunting System
村ライフSSDシミュレーション - 狩りシステム

大物獲物の出現、性格による対応、狩り成功時の分配システム
"""

import random
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from village_ssd_adapter import VillageSSDAdapter, update_alignment_inertia, manage_territory_relationship

class PreySize(Enum):
    """獲物サイズ"""
    SMALL = "small"           # 小動物（ウサギ、鳥など）
    MEDIUM = "medium"         # 中型動物（鹿、イノシシなど）
    LARGE = "large"           # 大型動物（熊、大鹿など）
    LEGENDARY = "legendary"   # 伝説級（古龍、幻獣など）

class HuntResult(Enum):
    """狩り結果"""
    CRITICAL_SUCCESS = "critical_success"  # 大成功
    SUCCESS = "success"                    # 成功
    PARTIAL_SUCCESS = "partial_success"    # 部分成功
    FAILURE = "failure"                    # 失敗
    INJURY = "injury"                      # 負傷
    DISASTER = "disaster"                  # 大失敗

class HuntingStyle(Enum):
    """狩りスタイル"""
    AGGRESSIVE = "aggressive"     # 積極的
    CAUTIOUS = "cautious"        # 慎重
    STRATEGIC = "strategic"      # 戦略的
    COOPERATIVE = "cooperative"  # 協力的
    SOLO = "solo"               # 単独
    AVOID = "avoid"             # 回避

@dataclass
class Prey:
    """獲物"""
    name: str                    # 名前
    size: PreySize              # サイズ
    difficulty: float           # 難易度 (0.0-1.0)
    meat_amount: float          # 肉量
    danger_level: float         # 危険度 (0.0-1.0)
    rarity: float              # 出現率 (0.0-1.0)
    special_effects: List[str] = field(default_factory=list)  # 特殊効果
    
    def get_nutrition_value(self) -> float:
        """栄養価計算"""
        base_nutrition = {
            PreySize.SMALL: 0.3,
            PreySize.MEDIUM: 0.8,
            PreySize.LARGE: 2.0,
            PreySize.LEGENDARY: 5.0
        }
        return base_nutrition.get(self.size, 0.5) * self.meat_amount

@dataclass
class HuntingSkill:
    """狩猟技能"""
    level: float = 1.0          # スキルレベル (0.0-10.0)
    experience: float = 0.0     # 経験値
    
    # 狩猟特性
    accuracy: float = 0.5       # 精度 (0.0-1.0)
    stealth: float = 0.5        # 隠密 (0.0-1.0)
    strength: float = 0.5       # 力 (0.0-1.0)
    courage: float = 0.5        # 勇気 (0.0-1.0)
    
    # 実績
    total_hunts: int = 0
    successful_hunts: int = 0
    large_prey_killed: int = 0
    legendary_encounters: int = 0
    times_injured: int = 0
    
    # 得意獲物
    preferred_prey_size: Optional[PreySize] = None
    
    def get_success_rate(self, prey: Prey, style: HuntingStyle) -> float:
        """獲物に対する成功率計算"""
        # 基本成功率（スキルレベル依存）
        base_rate = min(0.9, self.level / 10.0)
        
        # 難易度による修正
        difficulty_modifier = 1.0 - prey.difficulty * 0.7
        
        # 狩りスタイルによる修正
        style_modifiers = {
            HuntingStyle.AGGRESSIVE: self.courage + self.strength - prey.danger_level * 0.5,
            HuntingStyle.CAUTIOUS: self.stealth + self.accuracy - prey.difficulty * 0.3,
            HuntingStyle.STRATEGIC: (self.accuracy + self.stealth) / 2 + self.level * 0.05,
            HuntingStyle.COOPERATIVE: self.level * 0.1 + 0.2,  # 協力時はボーナス
            HuntingStyle.SOLO: (self.strength + self.courage) / 2,
            HuntingStyle.AVOID: 0.0  # 回避時は成功率0
        }
        
        style_bonus = style_modifiers.get(style, 0.0) * 0.3
        
        # 得意獲物ボーナス
        preferred_bonus = 0.2 if self.preferred_prey_size == prey.size else 0.0
        
        # 経験ボーナス
        exp_bonus = min(0.15, self.experience / 500.0)
        
        total_rate = base_rate * difficulty_modifier + style_bonus + preferred_bonus + exp_bonus
        return max(0.05, min(0.95, total_rate))
    
    def gain_experience(self, prey: Prey, result: HuntResult, was_group_hunt: bool = False):
        """経験値獲得"""
        # 基本経験値
        size_exp = {
            PreySize.SMALL: 5,
            PreySize.MEDIUM: 15,
            PreySize.LARGE: 40,
            PreySize.LEGENDARY: 100
        }
        
        base_exp = size_exp.get(prey.size, 10)
        
        # 結果による倍率
        result_multipliers = {
            HuntResult.CRITICAL_SUCCESS: 2.0,
            HuntResult.SUCCESS: 1.5,
            HuntResult.PARTIAL_SUCCESS: 1.0,
            HuntResult.FAILURE: 0.3,
            HuntResult.INJURY: 0.1,
            HuntResult.DISASTER: 0.05
        }
        
        exp_gain = base_exp * result_multipliers.get(result, 1.0)
        
        # グループ狩りの場合は経験値減少
        if was_group_hunt:
            exp_gain *= 0.7
        
        self.experience += exp_gain
        
        # レベルアップチェック
        new_level = math.log(self.experience / 20 + 1, 2)
        if new_level > self.level:
            self.level = min(10.0, new_level)
        
        # 統計更新
        self.total_hunts += 1
        
        if result in [HuntResult.SUCCESS, HuntResult.CRITICAL_SUCCESS, HuntResult.PARTIAL_SUCCESS]:
            self.successful_hunts += 1
            
            if prey.size in [PreySize.LARGE, PreySize.LEGENDARY]:
                self.large_prey_killed += 1
                
        if prey.size == PreySize.LEGENDARY:
            self.legendary_encounters += 1
            
        if result in [HuntResult.INJURY, HuntResult.DISASTER]:
            self.times_injured += 1

@dataclass
class HuntingEvent:
    """狩猟イベント"""
    hunters: List[str]          # 狩猟者たち
    prey: Prey                  # 獲物
    hunting_styles: Dict[str, HuntingStyle]  # 各ハンターのスタイル
    result: HuntResult          # 結果
    meat_obtained: float        # 獲得肉量
    injured_hunters: List[str]  # 負傷者
    timestamp: float            # 時刻
    was_group_hunt: bool = False  # グループ狩りかどうか
    distribution_plan: Dict[str, float] = field(default_factory=dict)  # 分配計画

class HuntingSystem:
    """狩りシステム"""
    
    def __init__(self):
        # NPC狩猟スキル管理
        self.hunting_skills: Dict[str, HuntingSkill] = {}
        
        # 狩猟履歴
        self.hunting_history: List[HuntingEvent] = []
        
        # 獲物データベース
        self.prey_database = self._initialize_prey_database()
        
        # 現在出現している獲物
        self.active_prey: List[Prey] = []
        
        # SSD Core Engine の初期化
        self.ssd_adapter = VillageSSDAdapter("hunting_system")
        self.ssd_engine = self.ssd_adapter.engine
        
        # システム設定
        self.large_prey_spawn_rate = 0.1    # 大物出現率（1日あたり）
        self.legendary_spawn_rate = 0.02    # 伝説級出現率（1日あたり）
        
    def _initialize_prey_database(self) -> Dict[str, Prey]:
        """獲物データベース初期化"""
        prey_list = [
            # 小動物
            Prey("ウサギ", PreySize.SMALL, 0.1, 1.0, 0.0, 0.8),
            Prey("キツネ", PreySize.SMALL, 0.2, 1.2, 0.1, 0.6),
            Prey("野鳥", PreySize.SMALL, 0.3, 0.8, 0.0, 0.7),
            Prey("リス", PreySize.SMALL, 0.15, 0.6, 0.0, 0.9),
            
            # 中型動物
            Prey("鹿", PreySize.MEDIUM, 0.4, 3.0, 0.1, 0.5),
            Prey("イノシシ", PreySize.MEDIUM, 0.6, 4.0, 0.4, 0.3),
            Prey("オオカミ", PreySize.MEDIUM, 0.7, 2.5, 0.6, 0.2),
            Prey("野生牛", PreySize.MEDIUM, 0.5, 5.0, 0.3, 0.25),
            
            # 大型動物
            Prey("熊", PreySize.LARGE, 0.8, 8.0, 0.8, 0.1, ["強靭な毛皮"]),
            Prey("大鹿", PreySize.LARGE, 0.6, 6.0, 0.2, 0.15, ["立派な角"]),
            Prey("巨大イノシシ", PreySize.LARGE, 0.9, 10.0, 0.7, 0.08, ["頑丈な牙"]),
            Prey("山の王者", PreySize.LARGE, 0.85, 12.0, 0.6, 0.05, ["王者の威厳"]),
            
            # 伝説級
            Prey("古き森の守護者", PreySize.LEGENDARY, 0.95, 20.0, 0.9, 0.01, ["古代の力", "森の祝福"]),
            Prey("銀狼王", PreySize.LEGENDARY, 0.9, 15.0, 0.95, 0.005, ["銀の毛皮", "月光の加護"]),
            Prey("幻の白鹿", PreySize.LEGENDARY, 0.8, 18.0, 0.3, 0.008, ["幻想の角", "純白の恵み"]),
            Prey("雷鳴の熊王", PreySize.LEGENDARY, 1.0, 25.0, 1.0, 0.003, ["雷の力", "王者の証"])
        ]
        
        return {prey.name: prey for prey in prey_list}
    
    def add_npc(self, npc_name: str, initial_skill: float = 1.0, personality: str = "neutral"):
        """NPCを狩猟システムに追加"""
        
        # 性格による基本特性設定
        personality_traits = {
            "aggressive": {"accuracy": 0.6, "stealth": 0.4, "strength": 0.8, "courage": 0.9},
            "cautious": {"accuracy": 0.8, "stealth": 0.9, "strength": 0.5, "courage": 0.4},
            "brave": {"accuracy": 0.7, "stealth": 0.5, "strength": 0.7, "courage": 0.9},
            "strategic": {"accuracy": 0.9, "stealth": 0.8, "strength": 0.6, "courage": 0.6},
            "cooperative": {"accuracy": 0.7, "stealth": 0.7, "strength": 0.7, "courage": 0.7},
            "competitive": {"accuracy": 0.8, "stealth": 0.6, "strength": 0.8, "courage": 0.8},
            "gentle": {"accuracy": 0.5, "stealth": 0.6, "strength": 0.4, "courage": 0.3},
            "neutral": {"accuracy": 0.6, "stealth": 0.6, "strength": 0.6, "courage": 0.6}
        }
        
        traits = personality_traits.get(personality, personality_traits["neutral"])
        
        # 少しのランダム変動を追加
        for key in traits:
            traits[key] = max(0.1, min(1.0, traits[key] + random.uniform(-0.2, 0.2)))
        
        # 得意獲物をランダムに決定（30%の確率）
        preferred_prey = None
        if random.random() < 0.3:
            preferred_prey = random.choice(list(PreySize))
        
        self.hunting_skills[npc_name] = HuntingSkill(
            level=initial_skill,
            accuracy=traits["accuracy"],
            stealth=traits["stealth"],
            strength=traits["strength"],
            courage=traits["courage"],
            preferred_prey_size=preferred_prey
        )
    
    def spawn_prey(self, hours_passed: float = 24.0):
        """獲物出現処理"""
        
        # 既存の獲物が逃走する可能性
        self.active_prey = [prey for prey in self.active_prey if random.random() > 0.3]
        
        # 新しい獲物の出現
        spawn_chances = hours_passed / 24.0  # 1日基準の出現確率
        
        # 小動物・中型動物の通常出現
        for prey_name, prey in self.prey_database.items():
            if prey.size in [PreySize.SMALL, PreySize.MEDIUM]:
                if random.random() < prey.rarity * spawn_chances * 2:  # 通常出現率
                    if prey not in self.active_prey:  # 重複回避
                        self.active_prey.append(prey)
        
        # 大型動物の特別出現
        if random.random() < self.large_prey_spawn_rate * spawn_chances:
            large_prey = [p for p in self.prey_database.values() if p.size == PreySize.LARGE]
            if large_prey:
                selected = random.choice(large_prey)
                if selected not in self.active_prey:
                    self.active_prey.append(selected)
        
        # 伝説級の超稀少出現
        if random.random() < self.legendary_spawn_rate * spawn_chances:
            legendary_prey = [p for p in self.prey_database.values() if p.size == PreySize.LEGENDARY]
            if legendary_prey:
                selected = random.choice(legendary_prey)
                if selected not in self.active_prey:
                    self.active_prey.append(selected)
    
    def determine_hunting_style(self, hunter: str, prey: Prey, personality: str) -> HuntingStyle:
        """性格による狩りスタイル決定"""
        
        skill = self.hunting_skills[hunter]
        
        # 性格による基本スタイル傾向
        personality_styles = {
            "aggressive": [HuntingStyle.AGGRESSIVE, HuntingStyle.SOLO],
            "cautious": [HuntingStyle.CAUTIOUS, HuntingStyle.AVOID],
            "brave": [HuntingStyle.AGGRESSIVE, HuntingStyle.STRATEGIC],
            "strategic": [HuntingStyle.STRATEGIC, HuntingStyle.CAUTIOUS],
            "cooperative": [HuntingStyle.COOPERATIVE, HuntingStyle.STRATEGIC],
            "competitive": [HuntingStyle.SOLO, HuntingStyle.AGGRESSIVE],
            "gentle": [HuntingStyle.AVOID, HuntingStyle.CAUTIOUS],
            "helpful": [HuntingStyle.COOPERATIVE, HuntingStyle.STRATEGIC],
            "caring": [HuntingStyle.COOPERATIVE, HuntingStyle.CAUTIOUS],
            "independent": [HuntingStyle.SOLO, HuntingStyle.STRATEGIC],
            "social": [HuntingStyle.COOPERATIVE, HuntingStyle.STRATEGIC],
            "creative": [HuntingStyle.STRATEGIC, HuntingStyle.COOPERATIVE],
            "practical": [HuntingStyle.CAUTIOUS, HuntingStyle.STRATEGIC],
            "energetic": [HuntingStyle.AGGRESSIVE, HuntingStyle.COOPERATIVE]
        }
        
        possible_styles = personality_styles.get(personality, [HuntingStyle.CAUTIOUS])
        
        # 獲物の危険度による修正
        if prey.danger_level > 0.7:  # 非常に危険
            if personality in ["gentle", "cautious"]:
                return HuntingStyle.AVOID
            elif personality not in ["aggressive", "brave"]:
                # 危険な獲物には慎重になる
                if HuntingStyle.CAUTIOUS not in possible_styles:
                    possible_styles.append(HuntingStyle.CAUTIOUS)
        
        # 獲物のサイズによる修正
        if prey.size in [PreySize.LARGE, PreySize.LEGENDARY]:
            if personality in ["cooperative", "helpful", "social"]:
                # 大物にはグループで挑む傾向
                return HuntingStyle.COOPERATIVE
        
        # スキルレベルによる修正
        if skill.level < 2.0 and prey.size in [PreySize.LARGE, PreySize.LEGENDARY]:
            # 低スキルでは大物を避ける傾向
            if personality not in ["aggressive", "brave", "competitive"]:
                return HuntingStyle.AVOID
        
        # 最終的なスタイル決定
        return random.choice(possible_styles)
    
    def execute_hunt(self, hunters: List[str], prey: Prey, personalities: Dict[str, str]) -> HuntingEvent:
        """狩りの実行"""
        
        # 各ハンターのスタイル決定
        hunting_styles = {}
        participating_hunters = []
        
        for hunter in hunters:
            personality = personalities.get(hunter, "neutral")
            style = self.determine_hunting_style(hunter, prey, personality)
            hunting_styles[hunter] = style
            
            if style != HuntingStyle.AVOID:
                participating_hunters.append(hunter)
        
        if not participating_hunters:
            # 全員回避の場合
            return HuntingEvent(
                hunters=hunters,
                prey=prey,
                hunting_styles=hunting_styles,
                result=HuntResult.FAILURE,
                meat_obtained=0.0,
                injured_hunters=[],
                timestamp=time.time(),
                was_group_hunt=len(hunters) > 1
            )
        
        # グループ狩りかどうか
        is_group_hunt = len(participating_hunters) > 1
        
        # 成功率計算
        if is_group_hunt:
            # グループ狩りの場合：協力ボーナス
            total_success_rate = 0
            cooperation_bonus = 0.0
            
            for hunter in participating_hunters:
                skill = self.hunting_skills[hunter]
                style = hunting_styles[hunter]
                base_rate = skill.get_success_rate(prey, style)
                total_success_rate += base_rate
                
                if style == HuntingStyle.COOPERATIVE:
                    cooperation_bonus += 0.15
            
            # グループ効果：平均成功率 + 協力ボーナス + 人数ボーナス
            group_success_rate = (total_success_rate / len(participating_hunters) + 
                                cooperation_bonus + 
                                min(0.2, len(participating_hunters) * 0.05))
            
            final_success_rate = min(0.95, group_success_rate)
        else:
            # 単独狩りの場合
            hunter = participating_hunters[0]
            skill = self.hunting_skills[hunter]
            style = hunting_styles[hunter]
            final_success_rate = skill.get_success_rate(prey, style)
        
        # 結果判定
        roll = random.random()
        
        if roll <= final_success_rate * 0.1:  # 10%の確率で大成功
            result = HuntResult.CRITICAL_SUCCESS
        elif roll <= final_success_rate:
            result = HuntResult.SUCCESS
        elif roll <= final_success_rate + 0.2:
            result = HuntResult.PARTIAL_SUCCESS
        elif roll <= 0.7:
            result = HuntResult.FAILURE
        elif roll <= 0.9:
            result = HuntResult.INJURY
        else:
            result = HuntResult.DISASTER
        
        # 肉量と負傷者の決定
        meat_obtained = 0.0
        injured_hunters = []
        
        if result == HuntResult.CRITICAL_SUCCESS:
            meat_obtained = prey.meat_amount * random.uniform(1.2, 1.5)
        elif result == HuntResult.SUCCESS:
            meat_obtained = prey.meat_amount * random.uniform(0.8, 1.2)
        elif result == HuntResult.PARTIAL_SUCCESS:
            meat_obtained = prey.meat_amount * random.uniform(0.3, 0.7)
        
        # 負傷処理
        if result in [HuntResult.INJURY, HuntResult.DISASTER]:
            injury_count = 1 if result == HuntResult.INJURY else random.randint(1, len(participating_hunters))
            injured_hunters = random.sample(participating_hunters, min(injury_count, len(participating_hunters)))
        
        # 経験値獲得
        for hunter in participating_hunters:
            skill = self.hunting_skills[hunter]
            skill.gain_experience(prey, result, is_group_hunt)
        
        # 狩猟イベント作成
        hunting_event = HuntingEvent(
            hunters=hunters,
            prey=prey,
            hunting_styles=hunting_styles,
            result=result,
            meat_obtained=meat_obtained,
            injured_hunters=injured_hunters,
            timestamp=time.time(),
            was_group_hunt=is_group_hunt
        )
        
        # 分配計画作成（成功時）
        if meat_obtained > 0:
            hunting_event.distribution_plan = self._create_distribution_plan(
                participating_hunters, meat_obtained, prey, personalities
            )
        
        # 履歴に記録
        self.hunting_history.append(hunting_event)
        
        # 獲物を除去（成功時）
        if result in [HuntResult.SUCCESS, HuntResult.CRITICAL_SUCCESS]:
            if prey in self.active_prey:
                self.active_prey.remove(prey)
        
        return hunting_event
    
    def _create_distribution_plan(self, hunters: List[str], total_meat: float, 
                                prey: Prey, personalities: Dict[str, str]) -> Dict[str, float]:
        """分配計画作成"""
        
        if not hunters or total_meat <= 0:
            return {}
        
        # 基本分配（均等分割）
        base_share = total_meat * 0.6 / len(hunters)  # 60%を狩猟者に
        
        distribution = {}
        for hunter in hunters:
            distribution[hunter] = base_share
        
        # 残り40%は村全体への貢献として算出
        community_share = total_meat * 0.4
        
        # リーダー的な人物により多く分配（性格考慮）
        leadership_bonus = 0.0
        for hunter in hunters:
            personality = personalities.get(hunter, "neutral")
            if personality in ["helpful", "caring", "cooperative", "social"]:
                leadership_bonus += community_share * 0.1
                distribution[hunter] += community_share * 0.1
        
        # 残りを均等分配
        remaining = community_share - leadership_bonus
        if remaining > 0:
            per_hunter_bonus = remaining / len(hunters)
            for hunter in hunters:
                distribution[hunter] += per_hunter_bonus
        
        return distribution
    
    def distribute_hunt_rewards(self, event: HuntingEvent, all_npcs: List[str], 
                              personalities: Dict[str, str]) -> Dict[str, Any]:
        """狩り成果の分配実行"""
        
        if event.meat_obtained <= 0:
            return {"distributed": False, "reason": "no_meat"}
        
        distribution_log = {
            "distributed": True,
            "total_meat": event.meat_obtained,
            "hunter_shares": {},
            "community_shares": {},
            "distribution_method": "equal" if len(event.hunters) == 1 else "cooperative"
        }
        
        # ハンター自身への分配
        for hunter, amount in event.distribution_plan.items():
            distribution_log["hunter_shares"][hunter] = amount
        
        # 村全体への分配（大物の場合）
        if event.prey.size in [PreySize.LARGE, PreySize.LEGENDARY]:
            
            # 分配対象を選定（hungry NPCs + 支援的な関係の人々）
            distribution_targets = []
            
            # 寛大な性格のハンターが主導
            generous_hunters = [h for h in event.hunters 
                              if personalities.get(h, "neutral") in ["caring", "helpful", "cooperative"]]
            
            if generous_hunters or event.prey.size == PreySize.LEGENDARY:
                # 村人への分配実行
                community_meat = event.meat_obtained * 0.3  # 30%を村へ
                
                # 分配対象選定（最大10人）
                eligible_npcs = [npc for npc in all_npcs if npc not in event.hunters]
                distribution_targets = random.sample(eligible_npcs, 
                                                   min(10, len(eligible_npcs)))
                
                if distribution_targets:
                    meat_per_person = community_meat / len(distribution_targets)
                    
                    for target in distribution_targets:
                        distribution_log["community_shares"][target] = meat_per_person
        
        return distribution_log
    
    def get_npc_hunting_status(self, npc_name: str) -> Dict[str, Any]:
        """NPC狩猟状況取得"""
        
        if npc_name not in self.hunting_skills:
            return {}
        
        skill = self.hunting_skills[npc_name]
        
        # レベルによる称号
        if skill.level >= 8.0:
            title = "伝説のハンター"
        elif skill.level >= 6.0:
            title = "ベテランハンター"
        elif skill.level >= 4.0:
            title = "熟練ハンター"
        elif skill.level >= 2.0:
            title = "駆け出しハンター"
        else:
            title = "狩猟初心者"
        
        # 最近の狩猟結果
        recent_hunts = [event for event in self.hunting_history[-20:] 
                       if npc_name in event.hunters]
        
        return {
            "npc_name": npc_name,
            "level": skill.level,
            "title": title,
            "experience": skill.experience,
            "accuracy": skill.accuracy,
            "stealth": skill.stealth,
            "strength": skill.strength,
            "courage": skill.courage,
            "total_hunts": skill.total_hunts,
            "successful_hunts": skill.successful_hunts,
            "success_rate": skill.successful_hunts / max(1, skill.total_hunts),
            "large_prey_killed": skill.large_prey_killed,
            "legendary_encounters": skill.legendary_encounters,
            "times_injured": skill.times_injured,
            "preferred_prey": skill.preferred_prey_size.value if skill.preferred_prey_size else None,
            "recent_hunt_count": len(recent_hunts)
        }
    
    def get_available_prey(self) -> List[Dict[str, Any]]:
        """利用可能な獲物リスト"""
        
        prey_info = []
        for prey in self.active_prey:
            prey_info.append({
                "name": prey.name,
                "size": prey.size.value,
                "difficulty": prey.difficulty,
                "danger_level": prey.danger_level,
                "estimated_meat": prey.meat_amount,
                "nutrition_value": prey.get_nutrition_value(),
                "special_effects": prey.special_effects,
                "rarity_indicator": "⭐" * min(5, int(prey.difficulty * 5 + 1))
            })
        
        return sorted(prey_info, key=lambda x: x["difficulty"], reverse=True)

def demonstrate_hunting_system():
    """狩りシステムのデモンストレーション"""
    
    print("=" * 80)
    print("村ライフSSD - 狩りシステム デモ")
    print("=" * 80)
    
    # システム初期化
    hunting_system = HuntingSystem()
    
    # NPCs追加（異なる性格と狩猟スキル）
    npcs = {
        "田中太郎": {"skill": 2.0, "personality": "aggressive"},
        "佐藤花子": {"skill": 1.5, "personality": "cautious"},
        "山田健一": {"skill": 3.0, "personality": "brave"},
        "鈴木美咲": {"skill": 1.8, "personality": "cooperative"},
        "高橋みどり": {"skill": 2.5, "personality": "strategic"},
        "中村勇": {"skill": 4.0, "personality": "competitive"},
        "渡辺あい": {"skill": 1.0, "personality": "gentle"},
        "伊藤博": {"skill": 3.5, "personality": "helpful"}
    }
    
    personalities = {}
    for name, config in npcs.items():
        hunting_system.add_npc(name, config["skill"], config["personality"])
        personalities[name] = config["personality"]
    
    print(f"👥 8人のNPCによる狩りシステムデモ開始")
    
    # 初期ハンター状況
    print(f"\n📊 初期ハンター状況:")
    for name, config in npcs.items():
        status = hunting_system.get_npc_hunting_status(name)
        print(f"  {name} ({config['personality']}): {status['title']} Lv.{status['level']:.1f}")
        print(f"    精度:{status['accuracy']:.1f} 隠密:{status['stealth']:.1f} "
              f"力:{status['strength']:.1f} 勇気:{status['courage']:.1f}")
    
    # 7日間の狩猟シミュレーション
    print(f"\n7日間狩猟シミュレーション:")
    
    for day in range(1, 8):
        print(f"\n--- {day}日目 ---")
        
        # 獲物出現
        hunting_system.spawn_prey(24.0)
        
        # 利用可能な獲物表示
        available_prey = hunting_system.get_available_prey()
        if available_prey:
            print(f"出現している獲物:")
            for prey_info in available_prey[:3]:  # 上位3つを表示
                size_emoji = {"small": "[小]", "medium": "[中]", "large": "[大]", "legendary": "[伝説]"}
                emoji = size_emoji.get(prey_info["size"], "[中]")
                danger = "[危険]" * min(3, int(prey_info["danger_level"] * 3 + 1))
                
                print(f"  {emoji} {prey_info['name']} {prey_info['rarity_indicator']} {danger}")
                print(f"     肉量: {prey_info['estimated_meat']:.1f}, 栄養価: {prey_info['nutrition_value']:.1f}")
        
        # 狩猟実行（1-3回）
        hunt_count = random.randint(1, 3)
        
        for hunt_num in range(hunt_count):
            if not hunting_system.active_prey:
                break
            
            # 対象獲物選択
            target_prey = random.choice(hunting_system.active_prey)
            
            # ハンター選出（1-4人）
            num_hunters = random.randint(1, 4)
            selected_hunters = random.sample(list(npcs.keys()), num_hunters)
            
            print(f"\n狩猟{hunt_num + 1}: {target_prey.name}")
            print(f"   ハンター: {', '.join(selected_hunters)}")
            
            # 各ハンターのスタイル予測表示
            styles_preview = []
            for hunter in selected_hunters:
                personality = personalities[hunter]
                style = hunting_system.determine_hunting_style(hunter, target_prey, personality)
                styles_preview.append(f"{hunter}({style.value})")
            print(f"   スタイル: {', '.join(styles_preview)}")
            
            # 狩猟実行
            hunt_event = hunting_system.execute_hunt(selected_hunters, target_prey, personalities)
            
            # 結果表示
            result_emojis = {
                HuntResult.CRITICAL_SUCCESS: "🌟",
                HuntResult.SUCCESS: "✅",
                HuntResult.PARTIAL_SUCCESS: "🔸",
                HuntResult.FAILURE: "❌",
                HuntResult.INJURY: "🩹",
                HuntResult.DISASTER: "💥"
            }
            
            emoji = result_emojis.get(hunt_event.result, "❓")
            print(f"   結果: {emoji} {hunt_event.result.value}")
            
            if hunt_event.meat_obtained > 0:
                print(f"   獲得肉量: {hunt_event.meat_obtained:.1f}")
                
                # 分配実行
                distribution = hunting_system.distribute_hunt_rewards(
                    hunt_event, list(npcs.keys()), personalities
                )
                
                if distribution["distributed"]:
                    print(f"   肉の分配:")
                    for hunter, amount in distribution["hunter_shares"].items():
                        print(f"     {hunter}: {amount:.1f}")
                    
                    if distribution["community_shares"]:
                        community_total = sum(distribution["community_shares"].values())
                        community_count = len(distribution["community_shares"])
                        print(f"     村への分配: {community_total:.1f} ({community_count}人)")
            
            if hunt_event.injured_hunters:
                print(f"   🩹 負傷者: {', '.join(hunt_event.injured_hunters)}")
        
        # 一日の終わりの状況更新
        if day % 2 == 0:  # 2日ごとに状況表示
            print(f"\n📈 {day}日目終了時点でのトップハンター:")
            
            # ハンターランキング
            hunter_scores = []
            for name in npcs.keys():
                status = hunting_system.get_npc_hunting_status(name)
                score = (status['level'] * 10 + 
                        status['large_prey_killed'] * 20 + 
                        status['legendary_encounters'] * 50)
                hunter_scores.append((name, score, status))
            
            hunter_scores.sort(key=lambda x: x[1], reverse=True)
            
            for i, (name, score, status) in enumerate(hunter_scores[:3], 1):
                print(f"  {i}位. {name}: {status['title']} (スコア: {score:.0f})")
                if status['large_prey_killed'] > 0:
                    print(f"      大物討伐: {status['large_prey_killed']}回")
                if status['legendary_encounters'] > 0:
                    print(f"      伝説遭遇: {status['legendary_encounters']}回")
    
    # 最終分析
    print(f"\n" + "=" * 50)
    print(f"📊 7日間狩猟システム最終分析")
    print(f"=" * 50)
    
    # 全体統計
    total_hunts = len(hunting_system.hunting_history)
    successful_hunts = len([h for h in hunting_system.hunting_history 
                          if h.result in [HuntResult.SUCCESS, HuntResult.CRITICAL_SUCCESS, HuntResult.PARTIAL_SUCCESS]])
    
    print(f"\n全体統計:")
    print(f"  総狩猟回数: {total_hunts}回")
    print(f"  成功率: {successful_hunts/max(1, total_hunts)*100:.1f}%")
    
    # 獲物別統計
    prey_stats = {}
    total_meat = 0
    
    for hunt in hunting_system.hunting_history:
        prey_name = hunt.prey.name
        if prey_name not in prey_stats:
            prey_stats[prey_name] = {"attempts": 0, "successes": 0, "meat": 0}
        
        prey_stats[prey_name]["attempts"] += 1
        if hunt.result in [HuntResult.SUCCESS, HuntResult.CRITICAL_SUCCESS, HuntResult.PARTIAL_SUCCESS]:
            prey_stats[prey_name]["successes"] += 1
            prey_stats[prey_name]["meat"] += hunt.meat_obtained
            total_meat += hunt.meat_obtained
    
    print(f"\n獲物別成績:")
    for prey_name, stats in sorted(prey_stats.items(), key=lambda x: x[1]["meat"], reverse=True):
        if stats["attempts"] > 0:
            success_rate = stats["successes"] / stats["attempts"] * 100
            print(f"  {prey_name}: {stats['successes']}/{stats['attempts']} "
                  f"({success_rate:.0f}%), 肉量: {stats['meat']:.1f}")
    
    print(f"\n総獲得肉量: {total_meat:.1f}")
    
    # 最終ハンターランキング
    print(f"\n最終ハンターランキング:")
    final_ranking = []
    
    for name in npcs.keys():
        status = hunting_system.get_npc_hunting_status(name)
        final_ranking.append((name, status))
    
    # 複合スコアでソート
    final_ranking.sort(key=lambda x: (x[1]['level'] + x[1]['large_prey_killed'] * 2), reverse=True)
    
    for i, (name, status) in enumerate(final_ranking, 1):
        personality = personalities[name]
        print(f"  {i}位. {name} ({personality}): {status['title']}")
        print(f"      Lv.{status['level']:.1f}, 成功率: {status['success_rate']*100:.0f}%, "
              f"狩猟回数: {status['total_hunts']}")
        
        if status['large_prey_killed'] > 0:
            print(f"      🐻 大物討伐: {status['large_prey_killed']}回")
        if status['legendary_encounters'] > 0:
            print(f"      🐉 伝説遭遇: {status['legendary_encounters']}回")
        if status['times_injured'] > 0:
            print(f"      🩹 負傷回数: {status['times_injured']}回")
    
    # 性格別傾向分析
    print(f"\n🧠 性格別狩猟傾向:")
    personality_analysis = {}
    
    for hunt in hunting_system.hunting_history:
        for hunter in hunt.hunters:
            personality = personalities[hunter]
            style = hunt.hunting_styles.get(hunter, HuntingStyle.CAUTIOUS)
            
            if personality not in personality_analysis:
                personality_analysis[personality] = {}
            if style not in personality_analysis[personality]:
                personality_analysis[personality][style] = 0
            
            personality_analysis[personality][style] += 1
    
    for personality, style_counts in personality_analysis.items():
        most_common_style = max(style_counts.items(), key=lambda x: x[1])
        total_hunts = sum(style_counts.values())
        
        print(f"  {personality}: 最多スタイル = {most_common_style[0].value} "
              f"({most_common_style[1]}/{total_hunts}回)")
    
    print(f"\n✨ 狩りシステムデモ完了!")
    print("大物出現、性格による対応差、成功時の分配システムを体験しました。")

if __name__ == "__main__":
    demonstrate_hunting_system()