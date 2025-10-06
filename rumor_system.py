"""
Village Life SSD Simulation - Rumor System
村ライフSSDシミュレーション - 噂システム

「○○は狩りが上手いらしい」「看護が上手いらしい」という噂が村に広がり、
評判が形成されていくシステム
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from village_ssd_adapter import VillageSSDAdapter

class RumorType(Enum):
    """噂の種類"""
    HUNTING_SKILL = "hunting_skill"      # 狩猟の腕前
    CAREGIVING_SKILL = "caregiving_skill" # 看護の腕前
    SOCIAL_SKILL = "social_skill"        # 社交の上手さ
    CRAFTING_SKILL = "crafting_skill"    # 工芸の腕前
    LEADERSHIP = "leadership"            # 指導力
    KINDNESS = "kindness"                # 優しさ

@dataclass 
class Rumor:
    """噂データ構造"""
    target_name: str                     # 噂の対象者
    rumor_type: RumorType               # 噂の種類  
    content: str                        # 噂の内容
    positive: bool                      # ポジティブかネガティブか
    intensity: float                    # 噂の強さ (0.0-1.0)
    source_name: str                    # 噂の発信者
    confidence: float                   # 確信度 (0.0-1.0)
    witnesses: List[str] = field(default_factory=list)  # 目撃者リスト
    creation_time: int = 0              # 作成時刻
    
    def get_rumor_text(self) -> str:
        """噂のテキスト表現を生成"""
        if self.positive:
            return f"{self.target_name}は{self.content}らしい"
        else:
            return f"{self.target_name}は{self.content}らしい"

# 性格による噂の拡散傾向
personality_gossip_tendency = {
    "social": 0.8,       # 社交的：よく話す
    "aggressive": 0.6,   # 攻撃的：批判的な噂を広めやすい
    "competitive": 0.7,  # 競争的：他人の評価を語る
    "brave": 0.4,        # 勇敢：あまり噂話はしない
    "cautious": 0.1,     # 慎重：噂を広めたがらない
    "caring": 0.5,       # 思いやり：必要な時だけ
    "gentle": 0.3,       # 穏やか：悪い噂は避ける
    "helpful": 0.4,      # 協力的：建設的な内容のみ
    "analytical": 0.2,   # 分析的：根拠のない噂は避ける
    "creative": 0.6,     # 創造的：面白い話として広める
    "emotional": 0.7,    # 感情的：感動した話を伝える
    "practical": 0.3     # 実用的：実益のある情報のみ
}

class RumorSystem:
    """噂システム"""
    
    def __init__(self):
        self.active_rumors: List[Rumor] = []
        self.rumor_history: List[Rumor] = []
        self.village_reputation: Dict[str, Dict[RumorType, float]] = {}
        self.villager_personalities: Dict[str, str] = {}
        
        # SSD Core Engine 統合
        self.ssd_adapter = VillageSSDAdapter("rumor_system")
        
    def initialize_reputations(self, villager_names: List[str], villager_data: Dict[str, Dict[str, Any]] = None):
        """村人の評判を初期化"""
        for name in villager_names:
            # 評判値を中性（0.5）で初期化
            self.village_reputation[name] = {
                rumor_type: 0.5 for rumor_type in RumorType
            }
            
            # 性格情報を保存
            if villager_data and name in villager_data:
                self.villager_personalities[name] = villager_data[name].get("personality", "gentle")
            else:
                self.villager_personalities[name] = "gentle"
    
    def create_rumor_from_interaction(self, speaker: str, listener: str, subject: str,
                                    rumor_type: RumorType, positive: bool, intensity: float,
                                    context: str = "") -> Optional[Rumor]:
        """人同士の相互作用から噂を生成"""
        
        # 話し手の性格による噂拡散確率チェック
        speaker_personality = self.villager_personalities.get(speaker, "gentle")
        gossip_chance = personality_gossip_tendency.get(speaker_personality, 0.3)
        
        if random.random() > gossip_chance:
            return None  # この人は噂を広めない性格
            
        # 信頼度計算（関係性やコンテキストに基づく）
        confidence = random.uniform(0.4, 0.9)
        if context == "direct_experience":
            confidence += 0.2  # 直接体験は信頼度が高い
            
        # 噂内容生成
        content_templates = {
            RumorType.HUNTING_SKILL: {
                True: ["狩りが上手い", "獲物を確実に仕留める", "狩猟の腕前がすごい"],
                False: ["狩りが下手", "よく獲物を逃す", "狩猟が苦手"]
            },
            RumorType.CAREGIVING_SKILL: {
                True: ["看護が上手い", "病人の世話が得意", "治療に長けている"],
                False: ["看護が下手", "治療に失敗する", "病人の世話が苦手"]
            }
        }
        
        templates = content_templates.get(rumor_type, {True: ["上手い"], False: ["下手"]})
        content = random.choice(templates[positive])
        
        # 噂作成
        rumor = Rumor(
            target_name=subject,
            rumor_type=rumor_type,
            content=content,
            positive=positive,
            intensity=min(intensity, 1.0),
            source_name=speaker,
            confidence=confidence,
            witnesses=[listener],  # 聞き手が目撃者
            creation_time=len(self.rumor_history)
        )
        
        # デバッグ出力（簡素化） - 新しい噂の作成
        print(f"    >> {speaker}が{listener}に話す: 「{rumor.get_rumor_text()}」")
        
        self.active_rumors.append(rumor)
        self.rumor_history.append(rumor)
        
        # SSD Coreを通じた信頼関係への影響
        self._apply_ssd_effects(rumor)
        
        return rumor
    
    def create_rumor_from_experience(self, experiencer: str, target: str, 
                                   rumor_type: RumorType, positive: bool, 
                                   intensity: float, potential_listeners: List[str]) -> List[Rumor]:
        """体験者（患者、目撃者）が噂を広める"""
        created_rumors = []
        
        # 体験者が各潜在的な聞き手に噂を伝える可能性を判定
        for listener in potential_listeners:
            if listener == experiencer or listener == target:
                continue
                
            rumor = self.create_rumor_from_interaction(
                speaker=experiencer,
                listener=listener,
                subject=target,
                rumor_type=rumor_type,
                positive=positive,
                intensity=intensity,
                context="direct_experience"
            )
            
            if rumor:
                created_rumors.append(rumor)
                
        return created_rumors
    
    def spread_rumors_through_interactions(self, villager_names: List[str], 
                                         relationships: Dict[str, Dict[str, float]]):
        """人同士の相互作用を通じて噂を拡散"""
        print("  -- 噂の拡散 --")
        
        # アクティブな噂から拡散対象をランダム選択
        if not self.active_rumors:
            print("    拡散する噂がありません")
            return
            
        spread_rumors = random.sample(self.active_rumors, min(3, len(self.active_rumors)))
        
        for spread_rumor in spread_rumors:
            # 噂を知っている人をランダム選択
            possible_knowers = [r.source_name for r in self.active_rumors if r == spread_rumor] + spread_rumor.witnesses
            knower = random.choice(possible_knowers)
            
            # 聞き手をランダム選択（関係値を考慮）
            possible_listeners = [name for name in villager_names 
                                if name != knower and name != spread_rumor.target_name]
            
            if possible_listeners:
                # 関係値で重み付け
                weights = [relationships.get(knower, {}).get(listener, 0.5) for listener in possible_listeners]
                listener = random.choices(possible_listeners, weights=weights)[0]
                
                # 拡散の可能性をチェック
                if self._should_spread_rumor(knower, listener, spread_rumor):
                    # 新しい噂を作成（少し劣化）
                    new_rumor = self.create_rumor_from_interaction(
                        speaker=knower,
                        listener=listener, 
                        subject=spread_rumor.target_name,
                        rumor_type=spread_rumor.rumor_type,
                        positive=spread_rumor.positive,
                        intensity=spread_rumor.intensity * 0.9,  # 少し弱くなる
                        context="rumor_spread"
                    )
                    
                    if new_rumor:
                        print(f"    >> {knower}が{listener}に伝える: 「{spread_rumor.get_rumor_text()}」")
    
    def _should_spread_rumor(self, speaker: str, listener: str, rumor: Rumor) -> bool:
        """噂を拡散すべきかどうかの判定"""
        speaker_personality = self.villager_personalities.get(speaker, "gentle")
        base_chance = personality_gossip_tendency.get(speaker_personality, 0.3)
        
        # 噂の強さも考慮
        chance = base_chance * rumor.intensity
        
        return random.random() < chance
    
    def _apply_ssd_effects(self, rumor: Rumor):
        """SSD Coreエンジンを通じた効果適用"""
        # 噂の種類に応じた領域マッピング
        domain_mapping = {
            RumorType.HUNTING_SKILL: "survival_competence",
            RumorType.CAREGIVING_SKILL: "social_care",
            RumorType.SOCIAL_SKILL: "social_coordination",
            RumorType.CRAFTING_SKILL: "resource_creation",
            RumorType.LEADERSHIP: "group_coordination",
            RumorType.KINDNESS: "social_care"
        }
        
        domain = domain_mapping.get(rumor.rumor_type, "general_competence")
        effect_strength = rumor.intensity * rumor.confidence
        
        # SSDによる信頼関係更新
        self.ssd_adapter.update_trust_through_interaction(
            rumor.source_name, 
            rumor.target_name,
            domain,
            rumor.positive,
            effect_strength * 0.3  # 噂による間接的な影響
        )
    
    def update_reputation_from_rumors(self):
        """噂から評判を更新"""
        # 各人の各分野での評判を計算
        for name in self.village_reputation:
            for rumor_type in RumorType:
                relevant_rumors = [r for r in self.active_rumors 
                                 if r.target_name == name and r.rumor_type == rumor_type]
                
                if relevant_rumors:
                    # 重み付き平均で評判を計算
                    total_weight = 0
                    weighted_sum = 0
                    
                    for rumor in relevant_rumors:
                        weight = rumor.intensity * rumor.confidence
                        value = 0.8 if rumor.positive else 0.2
                        
                        weighted_sum += value * weight
                        total_weight += weight
                    
                    if total_weight > 0:
                        new_reputation = weighted_sum / total_weight
                        # 既存の評判と合成（噂の影響は徐々に）
                        old_reputation = self.village_reputation[name][rumor_type]
                        self.village_reputation[name][rumor_type] = (
                            old_reputation * 0.7 + new_reputation * 0.3
                        )
    
    def display_current_rumors(self):
        """現在の噂状況表示"""
        
        print(f"\n  ■ 村の噂 ({len(self.active_rumors)}件)")
        
        # 強さでソート
        sorted_rumors = sorted(self.active_rumors, key=lambda r: r.intensity * r.confidence, reverse=True)
        
        for i, rumor in enumerate(sorted_rumors[:5]):  # 上位5件表示
            strength_icon = "[強]" if rumor.intensity > 0.7 else "[中]" if rumor.intensity > 0.4 else "[弱]"
            print(f"    {strength_icon} {rumor.get_rumor_text()}")
            print(f"      (発信: {rumor.source_name}, 強さ: {rumor.intensity:.1f}, 確信: {rumor.confidence:.1f})")
    
    def get_reputation_summary(self, name: str) -> Dict[str, float]:
        """指定した人の評判サマリー取得"""
        if name not in self.village_reputation:
            return {}
        
        summary = {}
        for rumor_type, value in self.village_reputation[name].items():
            if abs(value - 0.5) > 0.1:  # 中性から離れている場合のみ
                type_name = {
                    RumorType.HUNTING_SKILL: "狩猟",
                    RumorType.CAREGIVING_SKILL: "看護", 
                    RumorType.SOCIAL_SKILL: "社交",
                    RumorType.CRAFTING_SKILL: "工芸",
                    RumorType.LEADERSHIP: "指導力",
                    RumorType.KINDNESS: "優しさ"
                }[rumor_type]
                summary[type_name] = value
        return summary
    
    def display_village_reputation(self, villager_names: List[str]):
        """村全体の評判状況表示"""
        print(f"\n  ★ 村での評判状況")
        
        for name in villager_names:
            reputation_summary = self.get_reputation_summary(name)
            if reputation_summary:
                print(f"    {name}:")
                for skill, value in reputation_summary.items():
                    if value > 0.7:
                        icon = "[★]"
                        level = "高評価"
                    elif value > 0.6:
                        icon = "[+]"
                        level = "好評"
                    elif value < 0.3:
                        icon = "[-]"
                        level = "低評価"
                    elif value < 0.4:
                        icon = "[?]"
                        level = "やや不評"
                    else:
                        continue
                    
                    print(f"      {icon} {skill}: {level} ({value:.2f})")

def demonstrate_rumor_system():
    """噂システムデモンストレーション"""
    
    print("=" * 80)
    print("村の噂システムデモ - 噂が評判を作る")
    print("=" * 80)
    
    # 初期設定
    villager_names = ["アキラ", "タケシ", "ユウ", "アカネ", "ハナ", "タロウ", "サクラ"]
    
    # 簡易的な村人データ（性格情報を含む）
    villager_data = {
        "アキラ": {"personality": "aggressive"},
        "タケシ": {"personality": "brave"}, 
        "ユウ": {"personality": "competitive"},
        "アカネ": {"personality": "caring"},
        "ハナ": {"personality": "gentle"},
        "タロウ": {"personality": "helpful"},
        "サクラ": {"personality": "social"}
    }
    
    rumor_system = RumorSystem()
    rumor_system.initialize_reputations(villager_names, villager_data)
    
    # 関係値データ（簡易）
    relationships = {}
    for name in villager_names:
        relationships[name] = {}
        for other_name in villager_names:
            if name != other_name:
                relationships[name][other_name] = random.uniform(0.3, 0.8)
    
    print(f"\n自然な人間関係による噂の広がり")
    
    # 体験からの噂生成をデモンストレーション
    print("\n=== 狩りの体験 ===")
    
    # アキラが大きな獲物を捕獲（ユウとタケシが目撃）
    rumors = rumor_system.create_rumor_from_experience(
        experiencer="ユウ", target="アキラ", rumor_type=RumorType.HUNTING_SKILL,
        positive=True, intensity=0.9, potential_listeners=["タケシ", "サクラ"]
    )
    print(f"アキラの狩猟成功について {len(rumors)}件の噂が生成されました")
    
    # タケシが狩りに失敗（サクラが目撃）
    rumors = rumor_system.create_rumor_from_experience(
        experiencer="サクラ", target="タケシ", rumor_type=RumorType.HUNTING_SKILL,
        positive=False, intensity=0.6, potential_listeners=["ユウ", "ハナ"]
    )
    print(f"タケシの狩猟失敗について {len(rumors)}件の噂が生成されました")
    
    # 看護の体験
    print("\n=== 看護の体験 ===")
    
    # ハナが病人を治療（患者はタロウ、アカネが見ていた）
    rumors = rumor_system.create_rumor_from_experience(
        experiencer="タロウ", target="ハナ", rumor_type=RumorType.CAREGIVING_SKILL,
        positive=True, intensity=0.8, potential_listeners=["アカネ", "アキラ"]
    )
    print(f"ハナの看護成功について {len(rumors)}件の噂が生成されました")
    
    # アカネが治療に失敗（患者はユウ）
    rumors = rumor_system.create_rumor_from_experience(
        experiencer="ユウ", target="アカネ", rumor_type=RumorType.CAREGIVING_SKILL,
        positive=False, intensity=0.4, potential_listeners=["ハナ", "タロウ"]
    )
    print(f"アカネの看護失敗について {len(rumors)}件の噂が生成されました")
    
    # 数回の相互作用をシミュレーション
    for interaction in range(5):
        print(f"\n--- 相互作用 {interaction + 1} ---")
        rumor_system.spread_rumors_through_interactions(villager_names, relationships)
        
        # 評判更新
        rumor_system.update_reputation_from_rumors()
        
    # 最終状況表示
    rumor_system.display_current_rumors()
    rumor_system.display_village_reputation(villager_names)
    
    print(f"★ 最終噂・評判状況")
    rumor_system.display_current_rumors()
    rumor_system.display_village_reputation(villager_names)

def long_term_simulation():
    """長期間シミュレーション（30日間）"""
    
    print("=" * 80)
    print("村の噂システム - 長期間シミュレーション（30日間）")
    print("=" * 80)
    
    # 初期設定
    villager_names = ["アキラ", "タケシ", "ユウ", "アカネ", "ハナ", "タロウ", "サクラ", "ミズキ", "ヒロシ", "マリコ"]
    
    # より詳細な村人データ
    villager_data = {
        "アキラ": {"personality": "aggressive", "skills": ["hunting"]},
        "タケシ": {"personality": "brave", "skills": ["hunting"]}, 
        "ユウ": {"personality": "competitive", "skills": ["hunting", "crafting"]},
        "アカネ": {"personality": "caring", "skills": ["caregiving"]},
        "ハナ": {"personality": "gentle", "skills": ["caregiving"]},
        "タロウ": {"personality": "helpful", "skills": ["crafting"]},
        "サクラ": {"personality": "social", "skills": ["social"]},
        "ミズキ": {"personality": "creative", "skills": ["crafting", "caregiving"]},
        "ヒロシ": {"personality": "analytical", "skills": ["hunting", "leadership"]},
        "マリコ": {"personality": "emotional", "skills": ["social", "caregiving"]}
    }
    
    rumor_system = RumorSystem()
    rumor_system.initialize_reputations(villager_names, villager_data)
    
    # より複雑な関係値設定
    relationships = {}
    for name in villager_names:
        relationships[name] = {}
        for other_name in villager_names:
            if name != other_name:
                # 性格による関係値傾向
                base_relation = random.uniform(0.3, 0.8)
                # 同じスキルを持つ人は少し親密度が高い
                if villager_data[name].get("skills") and villager_data[other_name].get("skills"):
                    common_skills = set(villager_data[name]["skills"]) & set(villager_data[other_name]["skills"])
                    if common_skills:
                        base_relation += 0.1
                relationships[name][other_name] = min(base_relation, 1.0)
    
    print(f"\n=== 30日間の村生活シミュレーション ===")
    
    # 各日のイベント設定
    daily_events = [
        # 狩猟イベント
        ("hunting_success", 0.4),
        ("hunting_failure", 0.2), 
        # 看護イベント
        ("caregiving_success", 0.3),
        ("caregiving_failure", 0.15),
        # 社交イベント
        ("social_coordination", 0.25),
        ("social_conflict", 0.1),
        # 工芸イベント
        ("crafting_success", 0.2),
        ("kindness_act", 0.3)
    ]
    
    # 30日間のシミュレーション
    for day in range(1, 31):
        print(f"\n--- 第{day}日目 ---")
        
        # 1日に1-3回のイベントが発生
        daily_event_count = random.randint(1, 3)
        
        for event_num in range(daily_event_count):
            # イベントタイプをランダム選択
            event_type, base_probability = random.choice(daily_events)
            
            if random.random() < base_probability:
                # 参加者選択（スキルに基づく）
                if "hunting" in event_type:
                    possible_participants = [name for name in villager_names 
                                          if "hunting" in villager_data[name].get("skills", [])]
                elif "caregiving" in event_type:
                    possible_participants = [name for name in villager_names 
                                          if "caregiving" in villager_data[name].get("skills", [])]
                elif "social" in event_type:
                    possible_participants = [name for name in villager_names 
                                          if "social" in villager_data[name].get("skills", [])]
                elif "crafting" in event_type:
                    possible_participants = [name for name in villager_names 
                                          if "crafting" in villager_data[name].get("skills", [])]
                else:  # kindness_act
                    possible_participants = villager_names
                
                if not possible_participants:
                    possible_participants = villager_names
                
                participant = random.choice(possible_participants)
                
                # 目撃者/関係者選択
                witnesses = random.sample([n for n in villager_names if n != participant], 
                                        random.randint(1, 3))
                
                # 成功/失敗判定
                success = "success" in event_type or random.random() > 0.3
                intensity = random.uniform(0.3, 0.9)
                
                # 噂タイプ決定
                rumor_type_map = {
                    "hunting": RumorType.HUNTING_SKILL,
                    "caregiving": RumorType.CAREGIVING_SKILL,
                    "social": RumorType.SOCIAL_SKILL,
                    "crafting": RumorType.CRAFTING_SKILL,
                    "kindness": RumorType.KINDNESS
                }
                
                for key, rumor_type in rumor_type_map.items():
                    if key in event_type:
                        break
                else:
                    rumor_type = RumorType.KINDNESS
                
                # 体験者からの噂生成
                experiencer = random.choice(witnesses)
                other_listeners = [w for w in witnesses if w != experiencer]
                
                rumors = rumor_system.create_rumor_from_experience(
                    experiencer=experiencer,
                    target=participant,
                    rumor_type=rumor_type,
                    positive=success,
                    intensity=intensity,
                    potential_listeners=other_listeners + random.sample(villager_names, 2)
                )
                
                print(f"  {event_type}: {participant} -> {len(rumors)}件の噂")
        
        # 毎日の噂拡散（2-4回の相互作用）
        daily_interactions = random.randint(2, 4)
        for _ in range(daily_interactions):
            rumor_system.spread_rumors_through_interactions(villager_names, relationships)
        
        # 評判更新
        rumor_system.update_reputation_from_rumors()
        
        # 古い噂の自然減衰（7日以上経過した噂は弱くなる）
        current_time = len(rumor_system.rumor_history)
        for rumor in rumor_system.active_rumors[:]:
            if current_time - rumor.creation_time > 7:
                rumor.intensity *= 0.9  # 徐々に弱くなる
                if rumor.intensity < 0.2:
                    rumor_system.active_rumors.remove(rumor)
        
        # 週ごとの状況報告
        if day % 7 == 0:
            print(f"\n=== 第{day}日目（{day//7}週目）の状況 ===")
            rumor_system.display_current_rumors()
            rumor_system.display_village_reputation(villager_names)
            print(f"アクティブな噂の数: {len(rumor_system.active_rumors)}")
            print(f"総噂履歴数: {len(rumor_system.rumor_history)}")
    
    # 最終結果
    print("\n" + "=" * 80)
    print("30日間シミュレーション完了 - 最終結果")
    print("=" * 80)
    
    rumor_system.display_current_rumors()
    rumor_system.display_village_reputation(villager_names)
    
    print(f"\n=== 統計情報 ===")
    print(f"総噂数: {len(rumor_system.rumor_history)}")
    print(f"現在アクティブな噂: {len(rumor_system.active_rumors)}")
    
    # 最も噂になった人
    rumor_counts = {}
    for rumor in rumor_system.rumor_history:
        rumor_counts[rumor.target_name] = rumor_counts.get(rumor.target_name, 0) + 1
    
    most_rumored = max(rumor_counts.items(), key=lambda x: x[1])
    print(f"最も噂になった人: {most_rumored[0]} ({most_rumored[1]}回)")
    
    # 最も噂を広めた人
    source_counts = {}
    for rumor in rumor_system.rumor_history:
        source_counts[rumor.source_name] = source_counts.get(rumor.source_name, 0) + 1
    
    most_gossiper = max(source_counts.items(), key=lambda x: x[1])
    print(f"最も噂を広めた人: {most_gossiper[0]} ({most_gossiper[1]}回)")

if __name__ == "__main__":
    print("1. 短期デモ")
    print("2. 長期シミュレーション（30日）")
    choice = input("選択してください (1/2): ")
    
    if choice == "2":
        long_term_simulation()
    else:
        demonstrate_rumor_system()