"""
意味圧ベース大工システム - 統合村システム対応版

狩猟・看護・料理システムと同様に、意味圧ベース学習飽和メカニズムを採用した大工システム
統合村システムに完全対応
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from village_meaning_pressure_system import VillageMeaningPressureSystem, ActivityType as MeaningActivityType
from village_ssd_adapter import VillageSSDAdapter, update_alignment_inertia, manage_territory_relationship

@dataclass
class CarpentryReputation:
    """大工評判データ"""
    carpenter_name: str
    success_count: int = 0           # 成功回数
    total_attempts: int = 0          # 総試行回数
    quality_score_sum: float = 0.0   # 品質スコア合計
    reputation_score: float = 0.0    # 評判スコア
    construction_requests: int = 0   # 依頼された回数
    specialization_known: bool = False  # 大工として認知されているか
    signature_works: List[str] = field(default_factory=list)  # 得意作品

@dataclass
class ConstructionRequest:
    """建築依頼"""
    requester_name: str              # 依頼者
    preferred_carpenter: Optional[str] = None  # 指名希望大工
    construction_type: str = "repair"  # 建築タイプ
    urgency_level: float = 0.5       # 緊急度
    complexity: float = 0.5          # 複雑さ
    village_wide_impact: bool = False  # 村全体への影響

class ConstructionType(Enum):
    """建築タイプ"""
    REPAIR = "repair"                # 修理
    HOUSING = "housing"             # 住居建築
    FURNITURE = "furniture"         # 家具製作
    INFRASTRUCTURE = "infrastructure"  # インフラ整備
    TOOL_MAKING = "tool_making"     # 道具作り
    EMERGENCY_REPAIR = "emergency_repair"  # 緊急修理

@dataclass
class ConstructionProject:
    """建築プロジェクト"""
    name: str
    construction_type: ConstructionType
    difficulty: float               # 難易度 (0.1-1.0)
    base_quality: float            # 基本品質
    work_time: float               # 作業時間
    materials_required: float      # 必要材料量
    village_benefit: float         # 村への恩恵
    innovation_potential: float = 0.0  # 革新的要素
    collaboration_needed: bool = False  # 協力が必要か

class MeaningPressureCarpentrySystem:
    """意味圧ベース大工システム（SSD Core Engine統合版）"""
    
    def __init__(self):
        self.carpenter_reputations: Dict[str, CarpentryReputation] = {}
        self.construction_requests: List[ConstructionRequest] = []
        
        # SSD Core Engine の初期化
        self.ssd_adapter = VillageSSDAdapter("meaning_pressure_carpentry_system")
        self.ssd_engine = self.ssd_adapter.engine
        
        self.village_buildings: Dict[str, float] = {
            "住居": 0.6,      # 住居品質
            "作業場": 0.4,    # 作業場品質
            "倉庫": 0.3,      # 倉庫品質
            "集会所": 0.2,    # 集会所品質
        }
        
        # 建築プロジェクトデータベース（意味圧考慮版）
        self.project_database = {
            # 日常修理（低意味圧）
            "壁補修": ConstructionProject(
                "壁補修", ConstructionType.REPAIR, 0.2, 0.5, 0.3, 0.1, 0.1, 0.0, False
            ),
            "屋根修理": ConstructionProject(
                "屋根修理", ConstructionType.REPAIR, 0.3, 0.6, 0.4, 0.2, 0.15, 0.1, False
            ),
            
            # 緊急修理（高意味圧）
            "緊急屋根修理": ConstructionProject(
                "緊急屋根修理", ConstructionType.EMERGENCY_REPAIR, 0.8, 0.7, 0.6, 0.3, 0.4, 0.0, True
            ),
            "災害復旧": ConstructionProject(
                "災害復旧", ConstructionType.EMERGENCY_REPAIR, 0.9, 0.8, 1.0, 0.5, 0.6, 0.2, True
            ),
            
            # 創造的建築（高意味圧）
            "革新的住居": ConstructionProject(
                "革新的住居", ConstructionType.HOUSING, 0.8, 0.9, 1.5, 1.2, 0.5, 0.7, True
            ),
            "多目的作業場": ConstructionProject(
                "多目的作業場", ConstructionType.HOUSING, 0.7, 0.8, 1.2, 1.0, 0.4, 0.6, True
            ),
            
            # 村全体インフラ（最高意味圧）
            "村の大橋": ConstructionProject(
                "村の大橋", ConstructionType.INFRASTRUCTURE, 0.9, 0.9, 2.0, 1.5, 0.8, 0.8, True
            ),
            "共同作業場": ConstructionProject(
                "共同作業場", ConstructionType.INFRASTRUCTURE, 0.8, 0.8, 1.8, 1.2, 0.7, 0.7, True
            ),
            
            # 日常家具（低-中意味圧）
            "木製椅子": ConstructionProject(
                "木製椅子", ConstructionType.FURNITURE, 0.3, 0.6, 0.3, 0.2, 0.1, 0.1, False
            ),
            "芸術的家具": ConstructionProject(
                "芸術的家具", ConstructionType.FURNITURE, 0.6, 0.8, 0.8, 0.4, 0.3, 0.5, False
            ),
            
            # 特殊道具（中-高意味圧）
            "精密狩猟道具": ConstructionProject(
                "精密狩猟道具", ConstructionType.TOOL_MAKING, 0.7, 0.9, 0.8, 0.3, 0.4, 0.6, False
            ),
            "革新農具": ConstructionProject(
                "革新農具", ConstructionType.TOOL_MAKING, 0.6, 0.8, 0.6, 0.2, 0.3, 0.5, False
            ),
        }
        
        # 大工評判閾値
        self.reputation_thresholds = {
            "known_carpenter": 3,      # 大工として知られる
            "skilled_carpenter": 10,   # 腕の良い大工
            "master_craftsman": 20,    # 職人の達人
        }
        
        # 依頼発生率
        self.request_rates = {
            "daily_maintenance": 0.4,   # 日常メンテナンス依頼率
            "new_construction": 0.2,    # 新築依頼率
            "infrastructure": 0.15,     # インフラ依頼率
            "urgent_repair": 0.3,       # 緊急修理率
            "innovation_project": 0.1,  # 革新プロジェクト率
        }
        
        # 村の材料ストック
        self.material_storage = 5.0  # 木材等の材料
    
    def initialize_carpentry_reputations(self, villager_names: List[str]):
        """大工評判初期化"""
        
        for name in villager_names:
            if name not in self.carpenter_reputations:
                self.carpenter_reputations[name] = CarpentryReputation(carpenter_name=name)
    
    def generate_construction_requests(self, village_context: Dict[str, Any]) -> List[ConstructionRequest]:
        """建築依頼生成（村の状況を考慮）"""
        
        requests = []
        villager_names = village_context.get('villager_names', [])
        village_happiness = village_context.get('village_happiness', 0.5)
        food_crisis = village_context.get('food_crisis', False)
        
        if not villager_names:
            return requests
        
        # 緊急修理依頼（食料危機時は確率上昇）
        emergency_rate = self.request_rates["urgent_repair"]
        if food_crisis:
            emergency_rate *= 2.0
            
        if random.random() < emergency_rate:
            requester = random.choice(villager_names)
            skilled_carpenters = self._find_skilled_carpenters()
            
            request = ConstructionRequest(
                requester_name=requester,
                preferred_carpenter=skilled_carpenters[0] if skilled_carpenters else None,
                construction_type="emergency_repair",
                urgency_level=random.uniform(0.8, 1.0),
                complexity=random.uniform(0.6, 0.9),
                village_wide_impact=random.random() < 0.4
            )
            requests.append(request)
        
        # 革新プロジェクト（幸福度が高い時）
        if (village_happiness > 0.7 and 
            len(self._find_skilled_carpenters()) > 0 and
            random.random() < self.request_rates["innovation_project"]):
            
            requester = random.choice(villager_names)
            
            request = ConstructionRequest(
                requester_name=requester,
                preferred_carpenter=None,  # 最適な大工を自動選択
                construction_type="infrastructure",
                urgency_level=random.uniform(0.5, 0.8),
                complexity=random.uniform(0.7, 1.0),
                village_wide_impact=True
            )
            requests.append(request)
        
        # 日常メンテナンス依頼
        if random.random() < self.request_rates["daily_maintenance"]:
            requester = random.choice(villager_names)
            
            request = ConstructionRequest(
                requester_name=requester,
                preferred_carpenter=None,
                construction_type="repair",
                urgency_level=random.uniform(0.2, 0.5),
                complexity=random.uniform(0.2, 0.4),
                village_wide_impact=False
            )
            requests.append(request)
        
        # 新築依頼（村の発展に応じて）
        if (village_happiness > 0.6 and 
            random.random() < self.request_rates["new_construction"]):
            
            requester = random.choice(villager_names)
            
            request = ConstructionRequest(
                requester_name=requester,
                preferred_carpenter=None,
                construction_type="housing",
                urgency_level=random.uniform(0.4, 0.7),
                complexity=random.uniform(0.5, 0.8),
                village_wide_impact=random.random() < 0.3
            )
            requests.append(request)
        
        return requests
    
    def execute_carpentry_with_meaning_pressure(self, carpenter_name: str, request: ConstructionRequest, 
                                              meaning_pressure_system: VillageMeaningPressureSystem) -> Dict[str, Any]:
        """意味圧ベース大工作業実行"""
        
        # 適切なプロジェクト選択
        project = self._select_project_for_request(request)
        
        # 大工の現在スキル（意味圧ベース慣性値）
        current_skill = meaning_pressure_system.get_villager_skill_level(carpenter_name, MeaningActivityType.SOCIAL_COORDINATION)
        
        # 基本成功率計算
        skill_modifier = min(current_skill * 0.3, 1.0)
        base_success_rate = 0.4 + skill_modifier
        
        # 複雑さによる調整
        complexity_penalty = request.complexity * 0.3
        final_success_rate = max(0.1, base_success_rate - complexity_penalty)
        
        # 成功判定
        success = random.random() < final_success_rate
        
        # 品質計算
        if success:
            quality = min(1.0, project.base_quality + skill_modifier + random.uniform(0.0, 0.2))
            effectiveness = quality
        else:
            quality = max(0.1, project.base_quality - random.uniform(0.2, 0.5))
            effectiveness = quality * 0.5
        
        # 材料消費
        materials_used = project.materials_required * (1.2 if not success else 1.0)
        self.material_storage = max(0, self.material_storage - materials_used)
        
        # 評判更新
        reputation = self.carpenter_reputations.get(carpenter_name)
        if reputation:
            reputation.total_attempts += 1
            if success:
                reputation.success_count += 1
                reputation.quality_score_sum += quality
            
            # 評判スコア計算
            reputation.reputation_score = (
                reputation.success_count * 2.0 +
                (reputation.quality_score_sum / max(1, reputation.total_attempts)) * 3.0
            )
            
            # 大工として認知されるか
            if not reputation.specialization_known and reputation.reputation_score > self.reputation_thresholds["known_carpenter"]:
                reputation.specialization_known = True
        
        # 意味圧文脈の作成
        carpentry_context = self._create_carpentry_meaning_context(request, project, success, effectiveness, quality)
        
        # 意味圧ベース学習効果適用
        carpentry_inertia = meaning_pressure_system.update_alignment_inertia_with_meaning_pressure(
            carpenter_name, MeaningActivityType.SOCIAL_COORDINATION, carpentry_context
        )
        
        # SSD Core Engine効果適用
        self._apply_ssd_carpentry_effects(carpenter_name, request, project, success, effectiveness)
        
        # 結果データ
        result = {
            'success': success,
            'effectiveness': effectiveness,
            'quality': quality,
            'project_name': project.name,
            'materials_used': materials_used,
            'village_benefit': project.village_benefit if success else 0,
            'carpentry_inertia': carpentry_inertia,
            'reputation_gained': success
        }
        
        return result
    
    def _create_carpentry_meaning_context(self, request: ConstructionRequest, project: ConstructionProject,
                                        success: bool, effectiveness: float, quality: float) -> Dict[str, Any]:
        """大工作業の意味圧文脈を作成"""
        
        context = {
            'success': success,
            'effectiveness': effectiveness,
            'difficulty': request.complexity,
            'innovation': project.innovation_potential > 0.3,
            'collaboration': project.collaboration_needed,
            'emergency': request.construction_type == "emergency_repair",
            'village_wide_impact': request.village_wide_impact,
            'people_affected': 1 if not request.village_wide_impact else random.randint(3, 8),
            'creativity_required': project.innovation_potential > 0.4,
            'time_pressure': request.urgency_level > 0.7,
            'resource_scarcity': self.material_storage < 2.0,
            'new_technique': project.innovation_potential > 0.6 and success,
            'high_stakes': request.urgency_level > 0.8 or request.village_wide_impact,
            'mentor_present': random.random() < 0.2  # 他の大工からの指導
        }
        
        return context
    
    def _apply_ssd_carpentry_effects(self, carpenter_name: str, request: ConstructionRequest, 
                                   project: ConstructionProject, success: bool, effectiveness: float):
        """大工作業のSSD Core Engine効果適用"""
        
        # 大工の成功度に基づく領域決定
        if project.construction_type == ConstructionType.INFRASTRUCTURE:
            primary_domain = "infrastructure_creation"
        elif project.construction_type == ConstructionType.HOUSING:
            primary_domain = "housing_construction"
        elif project.construction_type in [ConstructionType.EMERGENCY_REPAIR, ConstructionType.REPAIR]:
            primary_domain = "repair_expertise"
        else:
            primary_domain = "crafting_skill"
        
        # SSDによる信頼関係更新
        effect_strength = effectiveness * (1.5 if success else 0.7)
        
        # 依頼者との信頼関係
        if success and effectiveness > 0.6:
            self.ssd_adapter.update_trust_through_interaction(
                carpenter_name, request.requester_name, primary_domain,
                success=True, effectiveness=effect_strength
            )
            
            # 特に高品質な場合、技術領域でも信頼向上
            if effectiveness > 0.8:
                self.ssd_adapter.update_trust_through_interaction(
                    carpenter_name, request.requester_name, "technical_skill",
                    success=True, effectiveness=effect_strength * 0.8
                )
        
        # 失敗時の影響
        elif not success and effectiveness < 0.4:
            self.ssd_adapter.update_trust_through_interaction(
                carpenter_name, request.requester_name, primary_domain,
                success=False, effectiveness=effect_strength * 0.5
            )
        
        # 村全体への影響（インフラプロジェクトの場合）
        if request.village_wide_impact and success:
            # 村人たちとの信頼関係向上
            beneficiaries = [request.requester_name]  # 実際の村人リストは引数で取得する必要がある
            
            for beneficiary in beneficiaries[:3]:  # 上位3名に影響
                self.ssd_adapter.update_trust_through_interaction(
                    carpenter_name, beneficiary, "community_contribution",
                    success=True, effectiveness=effect_strength * 0.6
                )
        
        # アライメント慣性効果（経験豊富な大工）
        carpenter_reputation = self.carpenter_reputations.get(carpenter_name)
        if carpenter_reputation and carpenter_reputation.total_attempts > 5:
            update_alignment_inertia(
                self.ssd_engine, carpenter_name, "craftsmanship",
                increment=0.2 if success else 0.08
            )
        
        # 領域関係管理（大工領域での評価）
        if success:
            territory_type = "carpentry_workshop" if project.construction_type != ConstructionType.INFRASTRUCTURE else "village_infrastructure"
            manage_territory_relationship(
                self.ssd_engine, carpenter_name, territory_type, "successful_construction"
            )
    
    def _select_project_for_request(self, request: ConstructionRequest) -> ConstructionProject:
        """依頼に適したプロジェクトを選択"""
        
        suitable_projects = []
        
        for project in self.project_database.values():
            # 建築タイプが一致するもの
            if request.construction_type == "emergency_repair":
                if project.construction_type == ConstructionType.EMERGENCY_REPAIR:
                    suitable_projects.append(project)
            elif request.construction_type == "repair":
                if project.construction_type in [ConstructionType.REPAIR, ConstructionType.EMERGENCY_REPAIR]:
                    suitable_projects.append(project)
            elif request.construction_type == "housing":
                if project.construction_type == ConstructionType.HOUSING:
                    suitable_projects.append(project)
            elif request.construction_type == "infrastructure":
                if project.construction_type == ConstructionType.INFRASTRUCTURE:
                    suitable_projects.append(project)
            elif request.construction_type == "furniture":
                if project.construction_type == ConstructionType.FURNITURE:
                    suitable_projects.append(project)
        
        if suitable_projects:
            # 複雑さに応じてプロジェクト選択
            if request.complexity > 0.7:
                # 高複雑度の場合、革新的なプロジェクトを優先
                innovative_projects = [p for p in suitable_projects if p.innovation_potential > 0.3]
                return random.choice(innovative_projects if innovative_projects else suitable_projects)
            else:
                # 低複雑度の場合、基本プロジェクト
                basic_projects = [p for p in suitable_projects if p.innovation_potential <= 0.3]
                return random.choice(basic_projects if basic_projects else suitable_projects)
        
        # フォールバック：基本的な壁補修
        return self.project_database["壁補修"]
    
    def _find_skilled_carpenters(self) -> List[str]:
        """熟練大工を見つける"""
        
        skilled = []
        for name, reputation in self.carpenter_reputations.items():
            if reputation.reputation_score > self.reputation_thresholds["skilled_carpenter"]:
                skilled.append(name)
        
        # 評判スコアでソート
        skilled.sort(key=lambda name: self.carpenter_reputations[name].reputation_score, reverse=True)
        return skilled
    
    def display_carpentry_status(self):
        """大工システム状況表示"""
        
        print(f"\n🔨 === 大工システム状況 ===")
        print(f"材料ストック: {self.material_storage:.1f}単位")
        print(f"建築依頼数: {len(self.construction_requests)}")
        
        # 大工評判表示
        skilled_carpenters = [(name, rep) for name, rep in self.carpenter_reputations.items() 
                            if rep.reputation_score > 1.0]
        
        if skilled_carpenters:
            print(f"\n【認知された大工】")
            skilled_carpenters.sort(key=lambda x: x[1].reputation_score, reverse=True)
            
            for name, reputation in skilled_carpenters[:5]:  # 上位5名
                success_rate = reputation.success_count / max(1, reputation.total_attempts)
                avg_quality = reputation.quality_score_sum / max(1, reputation.success_count)
                
                level = "見習い"
                if reputation.reputation_score > self.reputation_thresholds["master_craftsman"]:
                    level = "達人"
                elif reputation.reputation_score > self.reputation_thresholds["skilled_carpenter"]:
                    level = "熟練工"
                elif reputation.reputation_score > self.reputation_thresholds["known_carpenter"]:
                    level = "大工"
                
                print(f"  🔨 {name} ({level}): 評判{reputation.reputation_score:.1f}, 成功率{success_rate:.1%}, 品質{avg_quality:.2f}")


def demonstrate_meaning_pressure_carpentry_with_ssd():
    """意味圧ベース大工システムのデモンストレーション"""
    
    print("🔨 === 意味圧ベース大工システム + SSD Core Engine デモ ===\n")
    
    # システム初期化（SSD Core Engine + 意味圧ベース）
    carpentry_system = MeaningPressureCarpentrySystem()
    meaning_pressure_system = VillageMeaningPressureSystem()
    
    print("🏠 SSD Core Engine統合完了")
    
    villagers = ["大工タカシ", "見習いハルト", "多才なサキ", "新人ケンタ"]
    carpentry_system.initialize_carpentry_reputations(villagers)
    
    print("【初期状態】")
    carpentry_system.display_carpentry_status()
    
    # シナリオ1: 日常的な修理作業の繰り返し
    print(f"\n【シナリオ1: 日常修理の繰り返し（学習飽和テスト）】")
    
    for day in range(1, 6):
        print(f"\n--- 第{day}日目: 日常修理 ---")
        
        # 簡単な修理依頼
        request = ConstructionRequest(
            requester_name="村人A",
            construction_type="repair",
            urgency_level=0.3,
            complexity=0.2
        )
        
        result = carpentry_system.execute_carpentry_with_meaning_pressure(
            "大工タカシ", request, meaning_pressure_system
        )
        
        carpentry_inertia = meaning_pressure_system.get_villager_skill_level("大工タカシ", MeaningActivityType.SOCIAL_COORDINATION)
        print(f"  🔨 {result['project_name']}: {'成功' if result['success'] else '失敗'}")
        print(f"  📈 大工慣性: {carpentry_inertia:.3f}")
    
    print(f"\n【シナリオ2: 緊急・革新的プロジェクト（意味圧上昇テスト）】")
    
    # 緊急修理
    emergency_request = ConstructionRequest(
        requester_name="村長",
        construction_type="emergency_repair",
        urgency_level=0.9,
        complexity=0.8,
        village_wide_impact=True
    )
    
    result = carpentry_system.execute_carpentry_with_meaning_pressure(
        "大工タカシ", emergency_request, meaning_pressure_system
    )
    
    carpentry_inertia = meaning_pressure_system.get_villager_skill_level("大工タカシ", MeaningActivityType.SOCIAL_COORDINATION)
    print(f"\n🚨 緊急修理: {result['project_name']}")
    print(f"  結果: {'成功' if result['success'] else '失敗'} (品質: {result['quality']:.2f})")
    print(f"  📈 大工慣性: {carpentry_inertia:.3f}")
    
    # 革新的インフラプロジェクト
    innovation_request = ConstructionRequest(
        requester_name="村議会",
        construction_type="infrastructure",
        urgency_level=0.6,
        complexity=0.9,
        village_wide_impact=True
    )
    
    result = carpentry_system.execute_carpentry_with_meaning_pressure(
        "大工タカシ", innovation_request, meaning_pressure_system
    )
    
    final_inertia = meaning_pressure_system.get_villager_skill_level("大工タカシ", MeaningActivityType.SOCIAL_COORDINATION)
    print(f"\n🏗️ 革新プロジェクト: {result['project_name']}")
    print(f"  結果: {'成功' if result['success'] else '失敗'} (品質: {result['quality']:.2f})")
    print(f"  📈 最終大工慣性: {final_inertia:.3f}")
    
    print(f"\n【最終状況】")
    carpentry_system.display_carpentry_status()
    
    # 意味圧ベース分析
    print(f"\n🧠 【意味圧ベース + SSD Core Engine 統合分析】")
    print(f"大工タカシの慣性成長:")
    print(f"  初期: 0.000 → 最終: {final_inertia:.3f}")
    print(f"  特徴: 日常作業で飽和 → 緊急・革新プロジェクトで急成長")
    
    print(f"\n🏠 【SSD Core Engine統合の効果】")
    print(f"  1. 依頼者との信頼関係: 成功時に構築、失敗時に悪化")
    print(f"  2. アライメント慣性: 職人気質の発達と固定")
    print(f"  3. 領域管理: 大工工房・インフラ領域の形成")
    print(f"  4. 意味圧ベースとの相乗効果: 自然な職人成長プロセス")
    
    print(f"\n🏠 【SSD Core Engine効果】")
    print(f"  ・依頼者との信頼関係構築")
    print(f"  ・村全体への貢献でコミュニティ信頼向上")
    print(f"  ・アライメント慣性で職人気質発達")
    print(f"  ・大工工房領域の形成と管理")


if __name__ == "__main__":
    demonstrate_meaning_pressure_carpentry_with_ssd()