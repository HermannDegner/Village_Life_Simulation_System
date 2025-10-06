"""
Village Life SSD Simulation - Relationship-Based Care System
村ライフSSDシミュレーション - 関係値による看病システム

職業要素を排除し、純粋に関係値による看病・食事持参・支援システム
"""

import random
import time
import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.village_ssd_adapter import VillageSSDAdapter, update_alignment_inertia, manage_territory_relationship

# 狩りシステムのインポート
from systems.hunting.hunting_system import HuntingSystem, PreySize, HuntResult, HuntingStyle

class CareAction(Enum):
    """看病行動"""
    VISIT_BEDSIDE = "visit_bedside"           # 枕元を訪問
    BRING_FOOD = "bring_food"                 # 食事を持参
    BRING_MEDICINE = "bring_medicine"         # 薬草を持参
    EMOTIONAL_SUPPORT = "emotional_support"   # 精神的支援
    PHYSICAL_CARE = "physical_care"           # 身体的介護
    STAY_OVERNIGHT = "stay_overnight"         # 徹夜看病
    PRAYER_HEALING = "prayer_healing"         # 祈りによる癒し
    STORYTELLING = "storytelling"             # 話し相手になる

@dataclass
class CareEvent:
    """看病イベント"""
    caregiver: str              # 看病者
    patient: str                # 患者
    action: CareAction          # 看病行動
    effectiveness: float        # 効果（0.0-1.0）
    relationship_before: float  # 看病前の関係値
    relationship_after: float   # 看病後の関係値
    timestamp: float            # 時刻
    emotional_impact: str       # 感情的影響の説明

@dataclass
class CareRequest:
    """看病依頼"""
    patient_name: str           # 患者名
    caregiver_preference: Optional[str] = None  # 希望看病者
    urgency_level: float = 0.5  # 緊急度 (0.0-1.0)
    care_complexity: float = 0.5  # 看病複雑さ (0.0-1.0)

class RelationshipCareSystem:
    """関係値による看病システム"""
    
    def __init__(self):
        self.hunting_system = HuntingSystem()
        self.npcs: Dict[str, Any] = {}
        self.care_history: List[CareEvent] = []
        self.day = 1
        
        # 看病設定
        self.care_threshold = 0.1      # 看病を始める最低関係値
        self.spontaneous_care_rate = 0.3  # 関係なくても看病する確率
        
    def create_npc(self, name: str, personality: str):
        """NPCを作成（職業要素なし）"""
        
        npc = {
            "name": name,
            "personality": personality,
            "hunger_level": random.uniform(0.6, 0.8),
            "happiness": random.uniform(0.5, 0.8),
            "energy": random.uniform(0.7, 0.9),
            "health": random.uniform(0.8, 1.0),
            "relationships": {},  # 他NPCとの関係値 (0.0-1.0)
            "is_injured": False,
            "injury_severity": 0.0,  # 負傷の重さ (0.0-1.0)
            "days_injured": 0,
            "received_care_today": [],  # 今日受けた看病
            "given_care_today": [],     # 今日与えた看病
            "food_items": random.randint(2, 5),  # 持っている食材
            "herbal_items": random.randint(0, 3)  # 持っている薬草
        }
        
        self.npcs[name] = npc
        
        # 狩りスキルを追加（性格のみに基づく）
        base_skill = random.uniform(1.0, 3.0)
        if personality in ["aggressive", "brave", "competitive"]:
            base_skill += 0.5
        elif personality in ["cautious", "gentle"]:
            base_skill += 0.2
        
        self.hunting_system.add_npc(name, base_skill, personality)
    
    def initialize_relationships(self):
        """初期関係値を設定"""
        
        npc_names = list(self.npcs.keys())
        
        for i, name1 in enumerate(npc_names):
            for name2 in npc_names[i+1:]:
                
                # 初期関係値（性格の相性を考慮）
                personality1 = self.npcs[name1]["personality"]
                personality2 = self.npcs[name2]["personality"]
                
                base_relationship = self._calculate_personality_compatibility(personality1, personality2)
                
                # 少しのランダム変動
                relationship = base_relationship + random.uniform(-0.2, 0.2)
                relationship = max(0.0, min(1.0, relationship))
                
                # 相互関係設定
                self.npcs[name1]["relationships"][name2] = relationship
                self.npcs[name2]["relationships"][name1] = relationship
    
    def _calculate_personality_compatibility(self, personality1: str, personality2: str) -> float:
        """性格の相性計算"""
        
        # 相性マトリックス
        compatibility_matrix = {
            "aggressive": {"aggressive": 0.2, "cautious": 0.1, "brave": 0.6, "cooperative": 0.4, "gentle": 0.1, "helpful": 0.3, "caring": 0.2, "social": 0.4, "competitive": 0.7},
            "cautious": {"aggressive": 0.1, "cautious": 0.8, "brave": 0.3, "cooperative": 0.7, "gentle": 0.9, "helpful": 0.6, "caring": 0.8, "social": 0.5, "competitive": 0.2},
            "brave": {"aggressive": 0.6, "cautious": 0.3, "brave": 0.8, "cooperative": 0.6, "gentle": 0.4, "helpful": 0.7, "caring": 0.5, "social": 0.6, "competitive": 0.5},
            "cooperative": {"aggressive": 0.4, "cautious": 0.7, "brave": 0.6, "cooperative": 0.9, "gentle": 0.8, "helpful": 0.9, "caring": 0.9, "social": 0.8, "competitive": 0.3},
            "gentle": {"aggressive": 0.1, "cautious": 0.9, "brave": 0.4, "cooperative": 0.8, "gentle": 0.9, "helpful": 0.8, "caring": 1.0, "social": 0.7, "competitive": 0.1},
            "helpful": {"aggressive": 0.3, "cautious": 0.6, "brave": 0.7, "cooperative": 0.9, "gentle": 0.8, "helpful": 0.8, "caring": 0.9, "social": 0.8, "competitive": 0.4},
            "caring": {"aggressive": 0.2, "cautious": 0.8, "brave": 0.5, "cooperative": 0.9, "gentle": 1.0, "helpful": 0.9, "caring": 0.9, "social": 0.7, "competitive": 0.2},
            "social": {"aggressive": 0.4, "cautious": 0.5, "brave": 0.6, "cooperative": 0.8, "gentle": 0.7, "helpful": 0.8, "caring": 0.7, "social": 0.9, "competitive": 0.6},
            "competitive": {"aggressive": 0.7, "cautious": 0.2, "brave": 0.5, "cooperative": 0.3, "gentle": 0.1, "helpful": 0.4, "caring": 0.2, "social": 0.6, "competitive": 0.8}
        }
        
        return compatibility_matrix.get(personality1, {}).get(personality2, 0.3)
    
    def process_hunting_injuries(self, hunt_event):
        """狩りによる負傷処理"""
        
        if hunt_event.injured_hunters:
            for injured_name in hunt_event.injured_hunters:
                injured_npc = self.npcs[injured_name]
                
                # 負傷状態設定
                injured_npc["is_injured"] = True
                injured_npc["injury_severity"] = random.uniform(0.3, 0.8)
                injured_npc["days_injured"] = 0
                
                # 健康状態悪化
                injured_npc["health"] -= injured_npc["injury_severity"] * 0.4
                injured_npc["energy"] -= injured_npc["injury_severity"] * 0.5
                injured_npc["happiness"] -= 0.3
                
                print(f"{injured_name}が負傷しました (重傷度: {injured_npc['injury_severity']:.1f})")
    
    def simulate_daily_care(self):
        """1日の看病シミュレーション"""
        
        print(f"\n第{self.day}日目 - 看病・支援の時間")
        
        # 負傷者リスト
        injured_npcs = [name for name, npc in self.npcs.items() if npc["is_injured"]]
        
        if not injured_npcs:
            print("  今日は負傷者がいません。平和な一日です。")
            return
        
        print(f"  🩹 負傷者: {', '.join(injured_npcs)}")
        
        # 各負傷者に対する看病処理
        for injured_name in injured_npcs:
            self._process_care_for_injured(injured_name)
        
        # 負傷回復処理
        self._process_injury_recovery()
    
    def _process_care_for_injured(self, injured_name: str):
        """特定の負傷者への看病処理"""
        
        injured_npc = self.npcs[injured_name]
        
        print(f"\n    💊 {injured_name}への看病:")
        
        # 看病候補者の選出
        potential_caregivers = []
        
        for caregiver_name, caregiver_npc in self.npcs.items():
            if caregiver_name == injured_name:
                continue
                
            if caregiver_npc["is_injured"]:
                continue  # 負傷者は看病できない
            
            # 看病意欲の計算
            willingness = self._calculate_care_willingness(caregiver_name, injured_name)
            
            if willingness > 0.2:  # 閾値を超えた場合
                potential_caregivers.append((caregiver_name, willingness))
        
        if not potential_caregivers:
            print(f"      😢 誰も{injured_name}の看病に来ませんでした...")
            return
        
        # 意欲順にソートして看病実行
        potential_caregivers.sort(key=lambda x: x[1], reverse=True)
        
        # 上位3名まで看病
        caregivers = potential_caregivers[:3]
        
        for caregiver_name, willingness in caregivers:
            self._execute_care_action(caregiver_name, injured_name, willingness)
    
    def _calculate_care_willingness(self, caregiver_name: str, injured_name: str) -> float:
        """看病意欲の計算"""
        
        caregiver = self.npcs[caregiver_name]
        injured = self.npcs[injured_name]
        
        # 基本意欲（関係値に基づく）
        relationship = caregiver["relationships"].get(injured_name, 0.0)
        base_willingness = relationship * 0.7
        
        # 性格による修正
        personality_bonus = {
            "caring": 0.4,
            "helpful": 0.35,
            "gentle": 0.3,
            "cooperative": 0.25,
            "social": 0.2,
            "brave": 0.15,
            "cautious": 0.1,
            "aggressive": 0.05,
            "competitive": 0.0
        }
        
        personality = caregiver["personality"]
        base_willingness += personality_bonus.get(personality, 0.1)
        
        # 負傷の重傷度による緊急性修正
        urgency_bonus = injured["injury_severity"] * 0.2
        base_willingness += urgency_bonus
        
        # 看病者自身の状態
        caregiver_condition = (caregiver["health"] + caregiver["energy"]) / 2
        base_willingness *= caregiver_condition
        
        # 自然発生的な同情心（関係が薄くても）
        if relationship < 0.2 and random.random() < self.spontaneous_care_rate:
            base_willingness += 0.3
        
        return min(1.0, base_willingness)
    
    def _execute_care_action(self, caregiver_name: str, injured_name: str, willingness: float):
        """看病行動の実行"""
        
        caregiver = self.npcs[caregiver_name]
        injured = self.npcs[injured_name]
        
        # 関係値に基づいて看病行動を選択
        relationship = caregiver["relationships"].get(injured_name, 0.0)
        
        action = self._choose_care_action(caregiver_name, injured_name, relationship, willingness)
        
        # 看病効果の計算
        effectiveness = self._calculate_care_effectiveness(action, willingness, relationship)
        
        # 看病の実行
        old_relationship = relationship
        
        # 健康状態への影響
        health_improvement = effectiveness * 0.3
        energy_improvement = effectiveness * 0.2
        happiness_improvement = effectiveness * 0.4
        
        injured["health"] = min(1.0, injured["health"] + health_improvement)
        injured["energy"] = min(1.0, injured["energy"] + energy_improvement)  
        injured["happiness"] = min(1.0, injured["happiness"] + happiness_improvement)
        
        # 関係値向上
        relationship_improvement = effectiveness * 0.2 + random.uniform(0.05, 0.15)
        new_relationship = min(1.0, old_relationship + relationship_improvement)
        
        # 相互関係更新
        caregiver["relationships"][injured_name] = new_relationship
        injured["relationships"][caregiver_name] = new_relationship
        
        # 看病記録
        care_event = CareEvent(
            caregiver=caregiver_name,
            patient=injured_name,
            action=action,
            effectiveness=effectiveness,
            relationship_before=old_relationship,
            relationship_after=new_relationship,
            timestamp=time.time(),
            emotional_impact=self._generate_emotional_description(action, effectiveness, old_relationship, new_relationship)
        )
        
        self.care_history.append(care_event)
        
        # 今日の看病記録
        injured["received_care_today"].append(caregiver_name)
        caregiver["given_care_today"].append(injured_name)
        
        # 結果表示
        self._display_care_result(care_event)
    
    def _choose_care_action(self, caregiver_name: str, injured_name: str, relationship: float, willingness: float) -> CareAction:
        """看病行動の選択"""
        
        caregiver = self.npcs[caregiver_name]
        injured = self.npcs[injured_name]
        
        # 関係値による行動選択
        if relationship > 0.8:
            # 非常に親しい関係
            return random.choice([CareAction.STAY_OVERNIGHT, CareAction.PHYSICAL_CARE, CareAction.EMOTIONAL_SUPPORT])
        
        elif relationship > 0.5:
            # 親しい関係
            return random.choice([CareAction.BRING_FOOD, CareAction.VISIT_BEDSIDE, CareAction.EMOTIONAL_SUPPORT, CareAction.STORYTELLING])
        
        elif relationship > 0.2:
            # 普通の関係
            return random.choice([CareAction.BRING_FOOD, CareAction.VISIT_BEDSIDE, CareAction.BRING_MEDICINE])
        
        else:
            # 薄い関係（でも看病する）
            return random.choice([CareAction.VISIT_BEDSIDE, CareAction.BRING_MEDICINE, CareAction.PRAYER_HEALING])
    
    def _calculate_care_effectiveness(self, action: CareAction, willingness: float, relationship: float) -> float:
        """看病効果の計算"""
        
        # アクション基本効果
        base_effectiveness = {
            CareAction.VISIT_BEDSIDE: 0.3,
            CareAction.BRING_FOOD: 0.5,
            CareAction.BRING_MEDICINE: 0.6,
            CareAction.EMOTIONAL_SUPPORT: 0.4,
            CareAction.PHYSICAL_CARE: 0.7,
            CareAction.STAY_OVERNIGHT: 0.9,
            CareAction.PRAYER_HEALING: 0.2,
            CareAction.STORYTELLING: 0.3
        }
        
        effectiveness = base_effectiveness.get(action, 0.3)
        
        # 意欲による修正
        effectiveness *= (0.5 + willingness * 0.5)
        
        # 関係値による修正（親しいほど効果的）
        effectiveness *= (0.7 + relationship * 0.3)
        
        return min(1.0, effectiveness)
    
    def _generate_emotional_description(self, action: CareAction, effectiveness: float, old_rel: float, new_rel: float) -> str:
        """感情的影響の説明生成"""
        
        action_descriptions = {
            CareAction.VISIT_BEDSIDE: "枕元を訪れ",
            CareAction.BRING_FOOD: "手作りの食事を持参し",
            CareAction.BRING_MEDICINE: "薬草を持ってきて",
            CareAction.EMOTIONAL_SUPPORT: "心の支えとなり",
            CareAction.PHYSICAL_CARE: "献身的に身の回りを世話し",
            CareAction.STAY_OVERNIGHT: "一晩中付き添い",
            CareAction.PRAYER_HEALING: "回復を祈り",
            CareAction.STORYTELLING: "楽しい話をして"
        }
        
        base_desc = action_descriptions.get(action, "看病し")
        
        if effectiveness > 0.8:
            return f"{base_desc}、大きな回復をもたらしました"
        elif effectiveness > 0.5:
            return f"{base_desc}、着実な回復を助けました"
        elif effectiveness > 0.3:
            return f"{base_desc}、少しずつ元気になりました"
        else:
            return f"{base_desc}、心の支えになりました"
    
    def _display_care_result(self, care_event: CareEvent):
        """看病結果の表示"""
        
        action_emojis = {
            CareAction.VISIT_BEDSIDE: "[訪問]",
            CareAction.BRING_FOOD: "🍲",
            CareAction.BRING_MEDICINE: "🌿",
            CareAction.EMOTIONAL_SUPPORT: "[情緒サポート]",
            CareAction.PHYSICAL_CARE: "🤲",
            CareAction.STAY_OVERNIGHT: "🌙",
            CareAction.PRAYER_HEALING: "🙏",
            CareAction.STORYTELLING: "📖"
        }
        
        emoji = action_emojis.get(care_event.action, "💊")
        
        print(f"      {emoji} {care_event.caregiver} → {care_event.patient}")
        print(f"         {care_event.emotional_impact}")
        print(f"         関係値: {care_event.relationship_before:.2f} → {care_event.relationship_after:.2f}")
        
        if care_event.effectiveness > 0.7:
            print(f"         ✨ 非常に効果的な看病でした！")
        elif care_event.effectiveness > 0.4:
            print(f"         😊 効果的な看病でした")
        else:
            print(f"         心温まる優しさでした")
    
    def _process_injury_recovery(self):
        """負傷回復処理"""
        
        recovered = []
        
        for name, npc in self.npcs.items():
            if npc["is_injured"]:
                npc["days_injured"] += 1
                
                # 回復判定
                recovery_rate = 0.1  # 基本回復率
                
                # 受けた看病による回復ボーナス
                care_count = len(npc["received_care_today"])
                recovery_rate += care_count * 0.15
                
                # 健康状態による回復修正
                recovery_rate *= npc["health"]
                
                # 回復処理
                if random.random() < recovery_rate or npc["days_injured"] >= 7:  # 1週間で強制回復
                    npc["is_injured"] = False
                    npc["injury_severity"] = 0.0
                    npc["days_injured"] = 0
                    recovered.append(name)
                    
                    # 完全回復
                    npc["health"] = min(1.0, npc["health"] + 0.3)
                    npc["energy"] = min(1.0, npc["energy"] + 0.4)
                    npc["happiness"] = min(1.0, npc["happiness"] + 0.2)
        
        if recovered:
            print(f"\n  🎉 回復した村人: {', '.join(recovered)}")
        
        # 今日の看病記録をクリア
        for npc in self.npcs.values():
            npc["received_care_today"] = []
            npc["given_care_today"] = []

def demonstrate_care_system():
    """関係値看病システムのデモンストレーション"""
    
    print("=" * 80)
    print("関係値による看病システム デモ")
    print("=" * 80)
    
    # システム初期化
    care_system = RelationshipCareSystem()
    
    # NPCs作成（職業なし、性格のみ）
    villagers = [
        ("愛情深いアカネ", "caring"),
        ("親切なタロウ", "helpful"), 
        ("穏やかなハナ", "gentle"),
        ("協力的なケン", "cooperative"),
        ("社交的なサクラ", "social"),
        ("勇敢なアキラ", "brave"),
        ("慎重なミドリ", "cautious"),
        ("積極的なユウ", "aggressive"),
        ("競争好きなシン", "competitive")
    ]
    
    print(f"🏘️ 村の設立 - {len(villagers)}人の村人（職業なし）")
    
    for name, personality in villagers:
        care_system.create_npc(name, personality)
        print(f"  {name} ({personality})")
    
    # 初期関係値設定
    care_system.initialize_relationships()
    
    print(f"\n初期関係値（抜粋）:")
    sample_relationships = []
    for name, npc in care_system.npcs.items():
        for friend, relationship in list(npc["relationships"].items())[:2]:
            sample_relationships.append((name, friend, relationship))
    
    for person1, person2, rel in sample_relationships[:5]:
        print(f"  {person1} ⟷ {person2}: {rel:.2f}")
    
    # 7日間のシミュレーション
    print(f"\n" + "=" * 60)
    print(f"7日間看病システムシミュレーション")
    print(f"=" * 60)
    
    for day in range(1, 8):
        print(f"\n🌅 第{day}日目開始")
        care_system.day = day
        
        # 狩りによる負傷発生（ランダム）
        if day == 2 or day == 4 or day == 6:
            # 狩りシミュレーション（簡易版）
            hunters = random.sample(list(care_system.npcs.keys()), random.randint(2, 4))
            print(f"🏹 {', '.join(hunters)}が狩りに出かけました")
            
            # 負傷判定
            if random.random() < 0.4:  # 40%の確率で負傷
                injured = random.sample(hunters, random.randint(1, 2))
                
                # 疑似hunt_eventを作成
                class MockHuntEvent:
                    def __init__(self, injured_hunters):
                        self.injured_hunters = injured_hunters
                
                mock_event = MockHuntEvent(injured)
                care_system.process_hunting_injuries(mock_event)
        
        # 看病シミュレーション
        care_system.simulate_daily_care()
        
        # 2日ごとに村の状況表示
        if day % 2 == 0:
            print(f"\n📊 第{day}日目終了時の村の状況:")
            
            # 負傷者状況
            injured_count = sum(1 for npc in care_system.npcs.values() if npc["is_injured"])
            print(f"   🩹 負傷者数: {injured_count}人")
            
            # 関係値変化（上位5組）
            all_relationships = []
            for name, npc in care_system.npcs.items():
                for friend, relationship in npc["relationships"].items():
                    if name < friend:  # 重複を避ける
                        all_relationships.append((name, friend, relationship))
            
            all_relationships.sort(key=lambda x: x[2], reverse=True)
            
            print(f"   最も親しい関係（上位3組）:")
            for i, (person1, person2, rel) in enumerate(all_relationships[:3], 1):
                print(f"     {i}. {person1} ⟷ {person2}: {rel:.2f}")
    
    # 最終分析
    print(f"\n" + "=" * 60)
    print(f"📊 7日間看病システム最終分析")
    print(f"=" * 60)
    
    # 看病統計
    total_care_events = len(care_system.care_history)
    print(f"\n💊 看病統計:")
    print(f"  総看病回数: {total_care_events}回")
    
    # 看病者ランキング
    caregiver_counts = {}
    for event in care_system.care_history:
        caregiver_counts[event.caregiver] = caregiver_counts.get(event.caregiver, 0) + 1
    
    caregiver_ranking = sorted(caregiver_counts.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n最も献身的な看病者（上位5名）:")
    for i, (name, count) in enumerate(caregiver_ranking[:5], 1):
        personality = care_system.npcs[name]["personality"]
        print(f"  {i}位. {name} ({personality}): {count}回")
    
    # 行動別統計
    action_counts = {}
    for event in care_system.care_history:
        action = event.action.value
        action_counts[action] = action_counts.get(action, 0) + 1
    
    print(f"\n🎭 看病行動別統計:")
    action_names = {
        "visit_bedside": "枕元訪問",
        "bring_food": "食事持参",
        "bring_medicine": "薬草持参", 
        "emotional_support": "精神的支援",
        "physical_care": "身体介護",
        "stay_overnight": "徹夜看病",
        "prayer_healing": "祈りの癒し",
        "storytelling": "話し相手"
    }
    
    for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
        action_name = action_names.get(action, action)
        print(f"  {action_name}: {count}回")
    
    # 関係値変化分析
    print(f"\n関係値変化分析:")
    
    # 最も成長した関係
    relationship_growth = []
    for event in care_system.care_history:
        growth = event.relationship_after - event.relationship_before
        relationship_growth.append((event.caregiver, event.patient, growth, event.relationship_after))
    
    relationship_growth.sort(key=lambda x: x[2], reverse=True)
    
    print(f"  最も深まった絆（上位3組）:")
    for i, (caregiver, patient, growth, final_rel) in enumerate(relationship_growth[:3], 1):
        print(f"    {i}. {caregiver} → {patient}: +{growth:.2f} (最終: {final_rel:.2f})")
    
    # 最終関係値ランキング
    final_relationships = []
    for name, npc in care_system.npcs.items():
        for friend, relationship in npc["relationships"].items():
            if name < friend:
                final_relationships.append((name, friend, relationship))
    
    final_relationships.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n🏆 最終関係値ランキング（上位5組）:")
    for i, (person1, person2, rel) in enumerate(final_relationships[:5], 1):
        print(f"  {i}位. {person1} ⟷ {person2}: {rel:.2f}")
    
    # 性格別看病傾向
    print(f"\n🧠 性格別看病傾向:")
    personality_care_counts = {}
    
    for event in care_system.care_history:
        caregiver_personality = care_system.npcs[event.caregiver]["personality"]
        if caregiver_personality not in personality_care_counts:
            personality_care_counts[caregiver_personality] = 0
        personality_care_counts[caregiver_personality] += 1
    
    for personality, count in sorted(personality_care_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {personality}: {count}回")
    
    print(f"\n✨ 関係値による看病システムデモ完了!")
    print("職業に関係なく、純粋な人間関係による支え合いが実現されました。")

if __name__ == "__main__":
    demonstrate_care_system()