"""
Village Life SSD Adapter - SSD Core Engine Adapter
村ライフSSDアダプター - SSD Core Engine統合用アダプター

実際のSSD Core Engineを村ライフシミュレーションで使用するためのアダプター関数
"""

from typing import Dict, Any, Optional
from ssd_core_engine.ssd_core_engine import SSDCoreEngine, create_ssd_engine, setup_basic_structure
from ssd_core_engine.ssd_core_engine.ssd_territory import TerritoryProcessor
from ssd_core_engine.ssd_core_engine.ssd_types import LayerType

class VillageSSDAdapter:
    """村ライフシミュレーション用SSDアダプター"""
    
    def __init__(self, engine_name: str):
        self.engine = create_ssd_engine(engine_name)
        setup_basic_structure(self.engine)
        self.territory_processor = TerritoryProcessor()
        self.villager_positions = {}  # 村人の位置情報
        
    def add_villager(self, villager_name: str, personality: str, position: tuple = (0.0, 0.0)):
        """村人をSSDシステムに追加"""
        # 村人を構造要素として追加
        self.engine.add_structural_element(LayerType.BASE, f"villager_{villager_name}")
        
        # 縄張りシステムで初期化
        self.territory_processor.initialize_npc_boundaries(villager_name)
        
        # 位置情報を記録
        self.villager_positions[villager_name] = position
        
    def decide_action(self, villager_name: str, available_actions: list) -> str:
        """村人の行動決定"""
        if not available_actions:
            return "rest"
        
        # 簡単な重み付けによる行動選択
        action_weights = {}
        
        for action in available_actions:
            # 基本重み
            weight = 1.0
            
            # 縄張り状態の影響を考慮
            territorial_state = self.territory_processor.get_territorial_state(villager_name)
            if 'territories' in territorial_state:
                # 縄張りを持つ村人は積極的に行動
                weight += len(territorial_state['territories']) * 0.1
            
            action_weights[action] = weight
        
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
        """村人の経験を更新"""
        # 縄張りプロセッサーで経験を記録
        pos = self.villager_positions.get(villager_name, (0.0, 0.0))
        valence = intensity if success else -0.3
        
        self.territory_processor.process_territorial_experience(
            villager_name, pos, f"{activity}_experience", valence
        )
    
    def update_relationship(self, villager_name: str, target_name: str, interaction_type: str):
        """村人間の関係を更新"""
        # 両方の村人の位置を取得
        pos_a = self.villager_positions.get(villager_name, (0.0, 0.0))
        pos_b = self.villager_positions.get(target_name, (1.0, 1.0))
        
        # 縄張りプロセッサーで相互作用を処理
        valence = 0.5 if any(word in interaction_type.lower() for word in ["positive", "help", "care"]) else -0.5
        
        self.territory_processor.process_territorial_experience(
            villager_name, pos_b, interaction_type, valence
        )
        
        self.territory_processor.process_territorial_experience(
            target_name, pos_a, interaction_type, valence
        )
    
    def calculate_trust_level(self, evaluator: str, target: str, domain: str = "general") -> float:
        """縄張りシステムの整合慣性を使った信頼度計算"""
        # 縄張りシステムから関係状態を取得
        evaluator_state = self.territory_processor.get_territorial_state(evaluator)
        
        # 領域内の親密度と安心感を考慮
        trust_base = 0.5  # ベース信頼値
        
        # 縄張り情報から信頼度を算出
        if 'territories' in evaluator_state:
            for territory_id, territory_info in evaluator_state['territories'].items():
                if target in territory_info.get('members', set()):
                    # 同じ縄張り内のメンバーは高信頼
                    trust_base += 0.3
        
        # 0.0-1.0の範囲に正規化
        return max(0.0, min(1.0, trust_base))
    
    def update_trust_through_interaction(self, actor: str, target: str, interaction_type: str, 
                                       success: bool, effectiveness: float = 0.5):
        """相互作用を通じた信頼度更新"""
        # 成功/失敗に基づいた縄張り関係更新
        interaction_valence = effectiveness if success else -0.3
        
        # 縄張りシステムで相互作用を記録
        actor_pos = self.villager_positions.get(actor, (0.0, 0.0))
        target_pos = self.villager_positions.get(target, (1.0, 1.0))
        
        self.territory_processor.process_territorial_experience(
            actor, target_pos, f"{interaction_type}_{'success' if success else 'failure'}", interaction_valence
        )
    
    def get_reputation_from_ssd(self, villager_name: str, domain: str = "caregiving") -> Dict[str, float]:
        """縄張りシステムから評判情報を取得"""
        territorial_state = self.territory_processor.get_territorial_state(villager_name)
        
        reputation_data = {
            "trust_level": 0.5,
            "domain_expertise": 0.0,
            "community_standing": 0.0
        }
        
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
    """縄張り関係管理の互換性関数"""
    # 簡易的な実装：縄張りプロセッサーがある場合は使用
    if hasattr(engine, 'territory_processor'):
        pos_a = (0.0, 0.0)  # デフォルト位置
        pos_b = (1.0, 1.0)  # デフォルト位置
        
        valence = 0.5 if any(word in interaction.lower() for word in ["positive", "help", "care"]) else -0.5
        
        engine.territory_processor.process_territorial_experience(
            entity_a, pos_b, interaction, valence
        )