"""
Village Life SSD Adapter - SSD Core Engine Adapter
村ライフSSDアダプター - SSD Core Engine統合用アダプター

実際のSSD Core Engineを村ライフシミュレーションで使用するためのアダプター関数
"""

from typing import Dict, Any, Optional
from ssd_core_engine.ssd_core_engine import SSDCoreEngine, create_ssd_engine, setup_basic_structure
from ssd_core_engine.ssd_core_engine.ssd_territory import TerritoryProcessor, SubjectiveBoundary
from ssd_core_engine.ssd_core_engine.ssd_types import LayerType

class VillageSSDAdapter:
    """村ライフシミュレーション用SSDアダプター"""
    
    def __init__(self, engine_name: str):
        self.engine = create_ssd_engine(engine_name)
        setup_basic_structure(self.engine)
        self.territory_processor = TerritoryProcessor()
        self.subjective_boundaries = {}  # 新しい主観的境界システム
        self.villager_positions = {}  # 村人の位置情報
        
    def add_villager(self, villager_name: str, personality: str, position: tuple = (0.0, 0.0)):
        """村人をSSDシステムに追加"""
        # 村人を構造要素として追加
        self.engine.add_structural_element(LayerType.BASE, f"villager_{villager_name}")
        
        # 新しい主観的境界システムで初期化
        self.subjective_boundaries[villager_name] = SubjectiveBoundary(
            npc_id=villager_name,
            initial_alignment={'core_alignment': 0.6, 'upper_alignment': 0.4}
        )
        
        # 従来の縄張りシステムも併用（後方互換性）
        self.territory_processor.initialize_npc_boundaries(villager_name)
        
        # 位置情報を記録
        self.villager_positions[villager_name] = position
        
    def decide_action(self, villager_name: str, available_actions: list) -> str:
        """村人の行動決定（SSD主観的境界ベース）"""
        if not available_actions:
            return "rest"
        
        # 主観的境界による行動選択
        action_weights = {}
        boundary_state = self.territory_processor.subjective_boundaries.get(villager_name)
        
        for action in available_actions:
            # 基本重み
            weight = 1.0
            
            # 主観的境界による行動意欲調整（SSD理論）
            if boundary_state:
                # 内側オブジェクトが多い = 安心感 = 積極的行動
                inner_comfort = len(boundary_state.inner_objects) * 0.15
                # 外側オブジェクトが多い = 警戒感 = 慎重行動
                outer_caution = len(boundary_state.outer_objects) * 0.05
                
                # 行動タイプ別の主観的境界影響
                if action in ['hunting', 'carpentry']:  # リスク行動
                    weight += inner_comfort - outer_caution
                elif action in ['cooking', 'caregiving']:  # 社会行動
                    weight += inner_comfort * 0.8
                
            action_weights[action] = max(0.1, weight)
        
        # 重み付き確率での選択
        import random
        total_weight = sum(action_weights.values())
        rand_val = random.uniform(0, total_weight)
        
        cumulative = 0
        for action, weight in action_weights.items():
            cumulative += weight
            if rand_val <= cumulative:
                return action
        
        return available_actions[0]  # フォールバック
    
    def update_experience(self, villager_name: str, activity: str, success: bool, intensity: float = 1.0):
        """主観的境界による経験学習（SSD理論ベース）"""
        # SSD理論：経験により活動・場所・関係性への境界が形成される
        # 注意：スキル≠境界。スキルは意味圧ベース整合慣性で別途成長
        
        valence = intensity if success else -0.2
        
        # 活動自体への主観的境界学習（好き嫌い・安心感）
        activity_id = f"activity_{activity}"
        self._update_subjective_boundary(villager_name, activity_id, valence, f"{activity}_experience")
        
        # 場所への境界学習（安全感・親和性）
        pos = self.villager_positions.get(villager_name, (0.0, 0.0))
        location_id = f"location_{pos[0]:.1f}_{pos[1]:.1f}"
        self._update_subjective_boundary(villager_name, location_id, valence * 0.7, f"place_experience")
        
        # 成功体験による自己効力感の境界形成（自信≠スキル）
        if success and intensity > 0.5:
            self_confidence_id = f"confidence_{activity}"
            self._update_subjective_boundary(villager_name, self_confidence_id, valence * 1.2, "self_efficacy")
            print(f"🌟 SSD自信形成: {villager_name}の{activity}への自信境界強化 ({valence * 1.2:.2f})")
        
        # 新しい主観的境界システムでの経験処理
        if villager_name in self.subjective_boundaries:
            boundary = self.subjective_boundaries[villager_name]
            # 活動への主観的境界（安心感・親和性）
            boundary.process_experience(f"activity_{activity}", valence)
            # 場所への主観的境界
            boundary.process_experience(f"place_{pos[0]:.1f}_{pos[1]:.1f}", valence * 0.7)
            # 自信境界（自己効力感）
            if success and intensity > 0.5:
                boundary.process_experience(f"self_confidence_{activity}", valence * 1.2)
            
        # 従来の縄張りシステムとの統合（後方互換性）
        self.territory_processor.process_territorial_experience(
            villager_name, pos, f"{activity}_experience", valence
        )
    
    def get_subjective_boundary_summary(self, villager_name: str) -> Dict[str, Any]:
        """主観的境界の状態サマリー（SSD理論デバッグ用）"""
        # 新しい主観的境界システムを優先
        new_boundary = self.subjective_boundaries.get(villager_name)
        if new_boundary:
            strong_inner = {obj: strength for obj, strength in new_boundary.boundary_strength.items() if strength > 0.5}
            strong_outer = {obj: strength for obj, strength in new_boundary.boundary_strength.items() if strength < -0.5}
            
            return {
                "system": "new_subjective_boundary",
                "inner_count": len(new_boundary.inner_objects),
                "outer_count": len(new_boundary.outer_objects),
                "strong_inner_bonds": strong_inner,
                "strong_outer_aversions": strong_outer,
                "total_boundary_objects": len(new_boundary.boundary_strength),
                "average_boundary_strength": sum(new_boundary.boundary_strength.values()) / max(1, len(new_boundary.boundary_strength))
            }
        
        # フォールバック：旧システム
        boundary = self.territory_processor.subjective_boundaries.get(villager_name)
        if not boundary:
            return {"error": "境界未初期化"}
        
        # 境界強度の分析
        strong_inner = {obj: strength for obj, strength in boundary.boundary_strength.items() if strength > 0.5}
        strong_outer = {obj: strength for obj, strength in boundary.boundary_strength.items() if strength < -0.5}
        
        return {
            "system": "legacy_territory",
            "inner_count": len(boundary.inner_objects),
            "outer_count": len(boundary.outer_objects),
            "strong_inner_bonds": strong_inner,
            "strong_outer_aversions": strong_outer,
            "total_boundary_objects": len(boundary.boundary_strength),
            "average_boundary_strength": sum(boundary.boundary_strength.values()) / max(1, len(boundary.boundary_strength))
        }
    
    def update_relationship(self, villager_name: str, target_name: str, interaction_type: str):
        """主観的境界による関係更新（SSD理論ベース）"""
        # SSD理論：相互作用により境界が学習・変化
        valence = self._calculate_interaction_valence(interaction_type)
        
        # 新しい主観的境界システムでの双方向学習
        if villager_name in self.subjective_boundaries:
            boundary = self.subjective_boundaries[villager_name]
            boundary.process_experience(f"interaction_{target_name}", valence)
            
        if target_name in self.subjective_boundaries:
            boundary = self.subjective_boundaries[target_name]
            boundary.process_experience(f"interaction_{villager_name}", valence * 0.8)  # 相手への影響は少し弱く
        
        # レガシーシステムとの併用（後方互換性）
        self._update_subjective_boundary(villager_name, target_name, valence, interaction_type)
        self._update_subjective_boundary(target_name, villager_name, valence * 0.8, interaction_type)  # 相手への影響は少し弱く
        
        print(f"🧠 SSD境界学習: {villager_name}↔{target_name} ({interaction_type}, 感情価:{valence:.2f})")
    
    def update_social_recognition(self, target_name: str, recognizer_name: str, skill_domain: str, recognition_strength: float = 0.6):
        """社会的承認による自信境界の向上（他者認知→自己効力感）"""
        # 他者からの承認による自信境界の強化（スキル≠境界の明確な分離）
        
        if target_name in self.subjective_boundaries:
            boundary = self.subjective_boundaries[target_name]
            # 社会的承認による自信境界の形成
            boundary.process_experience(f"social_recognition_{skill_domain}", recognition_strength)
            boundary.process_experience(f"trusted_by_{recognizer_name}", recognition_strength * 0.7)
            print(f"🤝 社会的承認: {recognizer_name}からの{skill_domain}評価により{target_name}の自信境界強化 ({recognition_strength:.2f})")
        
        # レガシーシステムでの処理
        confidence_id = f"social_confidence_{skill_domain}"
        self._update_subjective_boundary(target_name, confidence_id, recognition_strength, "social_recognition")
    
    def _calculate_interaction_valence(self, interaction_type: str) -> float:
        """相互作用タイプから感情価を計算"""
        positive_words = ["positive", "help", "care", "cooperation", "success", "praise"]
        negative_words = ["negative", "conflict", "fail", "criticism", "harm"]
        
        if any(word in interaction_type.lower() for word in positive_words):
            return 0.6
        elif any(word in interaction_type.lower() for word in negative_words):
            return -0.4
        else:
            return 0.1  # 中性的相互作用
    
    def _update_subjective_boundary(self, npc_id: str, target_id: str, valence: float, interaction_type: str):
        """主観的境界の更新（レガシーシステム向け後方互換性）"""
        # 新しい主観的境界システムがあれば優先使用
        if npc_id in self.subjective_boundaries:
            boundary = self.subjective_boundaries[npc_id]
            boundary.process_experience(f"person_{target_id}", valence)
            return
        
        # レガシーシステムの処理
        boundary = self.territory_processor.subjective_boundaries.get(npc_id)
        if not boundary:
            self.territory_processor.initialize_npc_boundaries(npc_id)
            boundary = self.territory_processor.subjective_boundaries[npc_id]
        
        # 境界強度の更新（SSD理論の学習機構）
        current_strength = boundary.get_boundary_strength(target_id)
        learning_rate = 0.15
        new_strength = current_strength + (learning_rate * valence)
        new_strength = max(-1.0, min(1.0, new_strength))  # クランプ
        
        boundary.boundary_strength[target_id] = new_strength
        
        # 内側/外側の判定更新
        if new_strength > 0.3:
            boundary.inner_objects.add(target_id)
            boundary.outer_objects.discard(target_id)
        elif new_strength < -0.3:
            boundary.outer_objects.add(target_id)
            boundary.inner_objects.discard(target_id)
    
    def calculate_trust_level(self, evaluator: str, target: str, domain: str = "general") -> float:
        """主観的境界による信頼度計算（SSD理論ベース）"""
        # 新しい主観的境界システムを優先使用
        if evaluator in self.subjective_boundaries:
            boundary = self.subjective_boundaries[evaluator]
            target_key = f"person_{target}"
            
            # 新しいシステムでの信頼度計算
            if target_key in boundary.boundary_strength:
                strength = boundary.boundary_strength[target_key]
                # SSD理論：境界強度から信頼度を計算
                if strength > 0.3:  # 内側認識
                    trust = 0.7 + (strength * 0.25)
                elif strength < -0.3:  # 外側認識
                    trust = 0.3 + max(0, (strength + 1.0) * 0.2)
                else:  # 中立
                    trust = 0.5 + (strength * 0.3)
                
                # ドメイン別調整
                if domain == "cooperation":
                    trust *= 1.1
                elif domain == "resource_sharing":
                    trust *= 0.9
                
                return max(0.0, min(1.0, trust))
        
        # レガシーシステムでの処理
        boundary = self.territory_processor.subjective_boundaries.get(evaluator)
        
        if not boundary:
            return 0.5  # 中性的信頼値
        
        # 対象者の境界強度を確認
        target_boundary_strength = boundary.get_boundary_strength(target)
        
        # SSD理論：内側度が高い = 高信頼、外側度が高い = 低信頼
        if boundary.is_inner(target):
            # 内側認識：基本信頼 + 境界強度ボーナス
            trust = 0.7 + (target_boundary_strength * 0.25)
        elif boundary.is_outer(target):
            # 外側認識：低信頼 + 境界強度による調整
            trust = 0.3 + max(0, target_boundary_strength * 0.2)
        else:
            # 中立：境界強度に応じた段階的信頼
            trust = 0.5 + (target_boundary_strength * 0.3)
        
        # ドメイン別調整
        if domain == "cooperation":
            trust *= 1.1  # 協力関係では信頼度を上げる
        elif domain == "resource_sharing":
            trust *= 0.9  # 資源共有では少し慎重に
        
        return max(0.0, min(1.0, trust))
    
    def update_trust_through_interaction(self, actor: str, target: str, interaction_type: str, 
                                       success: bool, effectiveness: float = 0.5):
        """相互作用を通じた信頼度更新"""
        # 成功/失敗に基づいた主観的境界関係更新
        interaction_valence = effectiveness if success else -0.3
        
        # 新しい主観的境界システムで相互作用を記録
        if actor in self.subjective_boundaries:
            boundary = self.subjective_boundaries[actor]
            boundary.process_experience(f"interaction_{target}_{interaction_type}", interaction_valence)
            
        # レガシーシステムでの処理（後方互換性）
        actor_pos = self.villager_positions.get(actor, (0.0, 0.0))
        target_pos = self.villager_positions.get(target, (1.0, 1.0))
        
        self.territory_processor.process_territorial_experience(
            actor, target_pos, f"{interaction_type}_{'success' if success else 'failure'}", interaction_valence
        )
    
    def get_reputation_from_ssd(self, villager_name: str, domain: str = "caregiving") -> Dict[str, float]:
        """主観的境界システムから評判情報を取得"""
        reputation_data = {
            "trust_level": 0.5,
            "domain_expertise": 0.0,
            "community_standing": 0.0
        }
        
        # 新しい主観的境界システムを優先使用
        if villager_name in self.subjective_boundaries:
            boundary = self.subjective_boundaries[villager_name]
            
            # 主観的境界から専門性と信頼度を計算
            total_inner_strength = sum(strength for strength in boundary.boundary_strength.values() if strength > 0)
            inner_count = len(boundary.inner_objects)
            
            reputation_data["community_standing"] = min(1.0, inner_count * 0.2)
            
            # ドメイン関連の境界強度を検出
            domain_related_strength = 0.0
            for obj, strength in boundary.boundary_strength.items():
                if domain in obj or ("care" in obj and domain == "caregiving"):
                    domain_related_strength += max(0, strength)
            
            # 専門性と信頼度の計算
            reputation_data["domain_expertise"] = min(1.0, domain_related_strength * 0.3 + total_inner_strength * 0.1)
            reputation_data["trust_level"] = min(1.0, 0.5 + total_inner_strength * 0.1)
            
            return reputation_data
        
        # レガシーシステムでの処理
        territorial_state = self.territory_processor.get_territorial_state(villager_name)
        
        # 縄張り情報からコミュニティ地位を算出
        if 'territories' in territorial_state:
            territory_count = len(territorial_state['territories'])
            reputation_data["community_standing"] = min(1.0, territory_count * 0.3)
            
            # 縄張りの質と強度から専門性を評価
            total_territorial_strength = 0
            care_related_territories = 0
            
            for territory_info in territorial_state['territories'].values():
                strength = territory_info.get('territorial_strength', 0.0)
                total_territorial_strength += strength
                
                # ドメイン関連の縄張りを検出（看護の場合）
                if domain == "caregiving":
                    # 看護関連の経験がある縄張りをカウント
                    care_related_territories += 1
            
            # 専門性 = 縄張り強度 + ドメイン関連経験
            base_expertise = min(0.6, total_territorial_strength * 0.2)
            domain_bonus = min(0.4, care_related_territories * 0.1)
            reputation_data["domain_expertise"] = base_expertise + domain_bonus
            
            # 信頼度も縄張り情報から調整
            reputation_data["trust_level"] = min(1.0, 0.5 + total_territorial_strength * 0.1)
        
        return reputation_data

    def get_villager_state(self, villager_name: str) -> Dict[str, Any]:
        """村人の状態を取得"""
        territorial_state = self.territory_processor.get_territorial_state(villager_name)
        reputation_data = self.get_reputation_from_ssd(villager_name)
        
        return {
            "name": villager_name,
            "position": self.villager_positions.get(villager_name, (0.0, 0.0)),
            "territorial_info": territorial_state,
            "reputation": reputation_data,
            "system_state": self.engine.get_system_state()
        }

# 互換性のためのラッパー関数
def update_alignment_inertia(engine, entity_id: str, inertia_type: str, increment: float):
    """整合慣性更新の互換性関数"""
    # 簡易的な実装：エンジンに記録
    if not hasattr(engine, '_alignment_inertia'):
        engine._alignment_inertia = {}
    
    if entity_id not in engine._alignment_inertia:
        engine._alignment_inertia[entity_id] = {}
    
    if inertia_type not in engine._alignment_inertia[entity_id]:
        engine._alignment_inertia[entity_id][inertia_type] = 0.0
    
    engine._alignment_inertia[entity_id][inertia_type] += increment

def manage_territory_relationship(engine, entity_a: str, entity_b: str, interaction: str):
    """主観的境界関係管理の互換性関数"""
    # 簡易的な実装：主観的境界プロセッサーがある場合は使用
    if hasattr(engine, 'territory_processor'):
        pos_a = (0.0, 0.0)  # デフォルト位置
        pos_b = (1.0, 1.0)  # デフォルト位置
        
        valence = 0.5 if any(word in interaction.lower() for word in ["positive", "help", "care"]) else -0.5
        
        engine.territory_processor.process_territorial_experience(
            entity_a, pos_b, interaction, valence
        )