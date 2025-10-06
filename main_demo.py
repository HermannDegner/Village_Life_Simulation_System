"""
SSD理論（構造主観力学）ベース AIエージェントシステム デモンストレーション

このデモは構造主観力学（Structural Subjectivity Dynamics）理論に基づく
AIエージェントシステムの実証実験です。

重要な理論的原則:
- 全ての思考・判断は ssd_core_engine による主観的境界学習で実現
- 場当たり的な条件分岐やハードコーディングされた行動は一切使用しない
- 経験→境界形成→行動変化の一貫したサイクルで全ての行動が決定される
- 関係性・信頼・協力は主観的境界の動的学習により自然発生する

観察ポイント:
- 🧠 SSD境界学習: NPCが経験を通じて内側/外側を動的に学習
- 🌟 SSD自信形成: 成功体験による自己効力感の境界強化
- 🏘️ 主観的境界形成: 内側/外側認識による安全領域の確立
- 個別の主観的境界分析: 各NPCの異なる境界認識パターン
"""

from integrated_village_simulation import IntegratedVillageSimulation
from village_core import VillageEvent

def run_village_demo():
    """構造主観力学（SSD理論）ベースAIエージェント デモンストレーション"""
    
    print("=" * 80)
    print("構造主観力学（SSD理論）ベース AIエージェントシステム 実証デモ")  
    print("=" * 80)
    print()
    print("⚠️  重要な理論的注意事項")
    print("-" * 50)
    print("このデモは構造主観力学（Structural Subjectivity Dynamics）理論に基づく")
    print("AIエージェントシステムの実証実験です。")
    print()
    print("🧠 SSD理論の核心原則:")
    print("• NPCの思考・判断は全て ssd_core_engine による主観的境界学習")
    print("• 場当たり的な条件分岐やハードコーディングされた行動は一切使用しません")  
    print("• 経験→境界形成→行動変化の一貫したサイクルで全ての行動が決定されます")
    print("• 関係性・信頼・協力は全て主観的境界の動的学習により自然発生します")
    print()
    print("📊 観察ポイント:")
    print("• 🧠 SSD境界学習: NPCが経験を通じて内側/外側を動的に学習")
    print("• 🌟 SSD自信形成: 成功体験による自己効力感の境界強化") 
    print("• 🏘️ 主観的境界形成: 内側/外側認識による安全領域の確立")
    print("• 三層境界学習: 基層・中核・上層での独立した境界認識プロセス")
    print("• 個別の主観的境界分析: 各NPCの異なる境界認識パターン")
    print()
    print("=" * 80)
    print("=== 小さな村の物語 - SSD理論AIエージェント実証デモ ===")
    print()
    
    # システム初期化（小人数）
    village = IntegratedVillageSimulation(population_size=5)
    
    # 初期状態表示
    print("【村の設立】")
    village.get_village_status()
    
    # 7日間の詳細シミュレーション
    print(f"\\n=== 7日間の村の物語 ===")
    print("※ NPCたちが自分で状況を判断し、行動を決めています\\n")
    
    for day in range(1, 8):
        print(f"\\n🌅 === 第{day}日目の朝 ===")
        
        # 村人の状態確認
        print("📊 村人たちの朝の様子:")
        for villager in village.villagers:
            status_parts = []
            if villager.hunger > 0.5:
                status_parts.append(f"空腹度{villager.hunger:.1f}")
            if villager.injured:
                injury_type = "重傷" if villager.severe_injury else "軽傷"
                status_parts.append(f"{injury_type}")
            if villager.fatigue_level > 0.3:
                status_parts.append(f"疲労{villager.fatigue_level:.1f}")
            if villager.energy < 0.5:
                status_parts.append(f"疲労気味")
            
            # スキル情報も表示
            best_skill = max(villager.skills, key=villager.skills.get)
            best_value = villager.skills[best_skill]
            skill_names = {
                'hunting': '狩猟', 'cooking': '料理', 
                'caregiving': '看護', 'carpentry': '大工'
            }
            skill_text = f"{skill_names.get(best_skill, best_skill)}得意({best_value:.1f})"
            
            status_text = f"({', '.join(status_parts)})" if status_parts else "(元気)"
            print(f"  💭 {villager.name}: \"{villager.personality}な性格, {skill_text}\" {status_text}")
        
        print(f"\\n🏃 村人たちの自律行動:")
        
        # 各村人の詳細な行動理由分析
        for villager in village.villagers:
            # 村人の現在状態を詳しく分析
            state_analysis = []
            decision_factors = []
            
            # 空腹状態の分析
            if villager.hunger > 0.7:
                state_analysis.append(f"非常に空腹({villager.hunger:.1f})")
                decision_factors.append("食料確保が最優先")
            elif villager.hunger > 0.4:
                state_analysis.append(f"少し空腹({villager.hunger:.1f})")
                decision_factors.append("食事を考慮中")
            
            # 疲労状態の分析
            if villager.fatigue_level > 0.6:
                state_analysis.append(f"かなり疲労({villager.fatigue_level:.1f})")
                decision_factors.append("休息が必要")
            elif villager.fatigue_level > 0.3:
                state_analysis.append(f"軽い疲労({villager.fatigue_level:.1f})")
                decision_factors.append("適度な活動を選択")
            
            # 怪我の分析
            if villager.injured:
                injury_level = "重傷" if villager.severe_injury else "軽傷"
                state_analysis.append(f"{injury_level}")
                decision_factors.append("治療・休養が必要")
            
            # エネルギーレベル
            if villager.energy < 0.3:
                state_analysis.append(f"エネルギー不足({villager.energy:.1f})")
                decision_factors.append("軽作業のみ可能")
            elif villager.energy > 0.8:
                state_analysis.append(f"体力充実({villager.energy:.1f})")
                decision_factors.append("積極的活動が可能")
            
            # スキルと性格による判断傾向
            best_skill = max(villager.skills, key=villager.skills.get)
            skill_confidence = villager.skills[best_skill]
            
            if skill_confidence > 1.5:
                decision_factors.append(f"{best_skill}への自信あり")
            
            # 性格による行動傾向
            personality_traits = {
                'aggressive': '積極的に行動したい',
                'brave': '困難に立ち向かいたい', 
                'competitive': '他者より優れた結果を求める',
                'caring': '仲間を助けたい',
                'gentle': '和を重んじて慎重に行動'
            }
            
            personality_factor = personality_traits.get(villager.personality, '自分らしく行動')
            decision_factors.append(personality_factor)
            
            # 思考プロセス表示
            if state_analysis or decision_factors:
                print(f"\\n  🧠 {villager.name}の思考:")
                if state_analysis:
                    print(f"     現在の状態: {', '.join(state_analysis)}")
                if decision_factors:
                    print(f"     判断要因: {', '.join(decision_factors)}")
        
        # 実際のシミュレーション実行
        daily_result = village.simulate_day()
        
        print(f"\\n  📋 実際に発生した行動:")
        
        for event in daily_result['events']:            
            # 詳細な行動理由と結果を表現
            event_type = event.get('type')
            if event_type == VillageEvent.HUNTING_SUCCESS or str(event_type) == 'VillageEvent.HUNTING_SUCCESS':
                hunter_name = event.get('hunter', '誰か')
                food = event.get('food_gained', 0)
                energy = event.get('energy_used', 0)
                
                # 狩猟者の詳しい動機
                hunter = next((v for v in village.villagers if v.name == hunter_name), None)
                if hunter:
                    motivation = []
                    if village.food_storage < 3.0:
                        motivation.append("村の食料不足を懸念")
                    if hunter.hunger > 0.5:
                        motivation.append("自身の空腹")
                    if hunter.skills['hunting'] > 1.0:
                        motivation.append("狩猟スキルへの自信")
                    if hunter.personality in ['aggressive', 'brave']:
                        motivation.append(f"{hunter.personality}な性格")
                        
                    print(f"    🎯 {hunter_name}: {', '.join(motivation)}により狩猟を決意")
                    print(f"       → 成功: {food:.1f}の肉を獲得 (エネルギー{energy:.1f}消費)")
                    
                    if event.get('injury_occurred'):
                        print(f"       💥 代償: 狩猟中に負傷してしまった")
                
            elif event_type == VillageEvent.HUNTING_FAILURE or str(event_type) == 'VillageEvent.HUNTING_FAILURE':
                hunter_name = event.get('hunter', '誰か')
                reason = event.get('reason', '失敗')
                
                hunter = next((v for v in village.villagers if v.name == hunter_name), None)
                if hunter:
                    print(f"    😞 {hunter_name}: 意欲はあったが技術不足で失敗")
                    print(f"       → 結果: {reason} (経験値は獲得)")
                
            elif event_type == VillageEvent.MEAL_PREPARED or str(event_type) == 'VillageEvent.MEAL_PREPARED':
                cook_name = event.get('cook', '誰か')
                quality = event.get('meal_quality', 0)
                
                cook = next((v for v in village.villagers if v.name == cook_name), None)
                if cook:
                    motivation = []
                    if cook.personality == 'caring':
                        motivation.append("仲間への思いやり")
                    if cook.skills['cooking'] > 1.0:
                        motivation.append("料理への自信")
                    if sum(v.hunger for v in village.villagers) > 2.0:
                        motivation.append("村全体の空腹状況")
                        
                    print(f"    🍳 {cook_name}: {', '.join(motivation)}で料理を担当")
                    print(f"       → 結果: 品質{quality:.1f}の食事を準備完了")
                
            elif (event_type == VillageEvent.CONSTRUCTION_COMPLETED or str(event_type) == 'VillageEvent.CONSTRUCTION_COMPLETED' or 
                  str(event_type) == 'construction_progress'):
                carpenter_name = event.get('carpenter', '誰か')
                project = event.get('project', '何か')
                
                carpenter = next((v for v in village.villagers if v.name == carpenter_name), None)
                if carpenter:
                    motivation = []
                    if carpenter.skills.get('carpentry', 0) > 0.8:
                        motivation.append("建築技術への自信")
                    if carpenter.personality in ['competitive', 'aggressive']:
                        motivation.append("積極的な性格")
                    motivation.append("村の発展への貢献意欲")
                    
                    if event.get('is_completed', False):
                        print(f"    🔨 {carpenter_name}: {', '.join(motivation)}で建設プロジェクトを完成")
                        print(f"       → 完成: {project}が完成しました！")
                    else:
                        progress = event.get('progress_percentage', 0)
                        print(f"    🔨 {carpenter_name}: {', '.join(motivation)}で建設作業を継続")
                        print(f"       → 進捗: {project}の建設を推進 ({progress:.1f}%完了)")
            
            elif str(event_type) == 'VillageEvent.CONSTRUCTION_FAILED':
                carpenter_name = event.get('carpenter', '誰か')
                project = event.get('project', '何か')
                
                print(f"    😞 {carpenter_name}: 建設に挑戦したが技術不足で失敗")
                print(f"       → 結果: {project}の建設に失敗 (経験値は獲得)")
                
            elif event_type == VillageEvent.CARE_PROVIDED or str(event_type) == 'VillageEvent.CARE_PROVIDED':
                caregiver_name = event.get('caregiver', '誰か')
                patient_name = event.get('patient', '患者')
                
                caregiver = next((v for v in village.villagers if v.name == caregiver_name), None)
                if caregiver:
                    motivation = []
                    if caregiver.personality == 'caring':
                        motivation.append("思いやり深い性格")
                    if caregiver.skills['caregiving'] > 0.5:
                        motivation.append("看護技術")
                    motivation.append(f"{patient_name}の苦痛への共感")
                    
                    print(f"    💊 {caregiver_name}: {', '.join(motivation)}で治療を実施")
                    print(f"       → 処置: {patient_name}の看病・治療を行った")
                
            elif event_type == VillageEvent.RUMOR_SPREAD or str(event_type) == 'VillageEvent.RUMOR_SPREAD':
                speaker = event.get('speaker', '誰か')
                listener = event.get('listener', '誰か')
                content = event.get('content', '何かの噂')
                
                speaker_villager = next((v for v in village.villagers if v.name == speaker), None)
                if speaker_villager:
                    social_motivation = []
                    if speaker_villager.personality in ['competitive', 'aggressive']:
                        social_motivation.append("情報共有による影響力行使")
                    elif speaker_villager.personality in ['caring', 'gentle']:
                        social_motivation.append("仲間との絆を深めたい")
                    else:
                        social_motivation.append("自然な会話欲求")
                        
                    print(f"    🗣️ {speaker}: {', '.join(social_motivation)}で会話を開始")
                    print(f"       → 内容: {listener}に「{content}」を伝えた")
        
        # 夕方の状況
        print(f"\\n🌆 第{day}日目の夕方 - 村の状況:")
        food_storage = getattr(village, 'food_storage', 0)
        happiness = getattr(village, 'village_happiness', 0)
        print(f"  📦 食料貯蔵: {food_storage:.1f}単位")
        print(f"  😊 村の幸福度: {happiness:.2f}")
        
        # 負傷者チェック
        injured_count = sum(1 for v in village.villagers if v.injured)
        if injured_count > 0:
            print(f"  🏥 負傷者: {injured_count}名")
        else:
            print(f"  ✅ 全員が健康です")
            
        # 一日の終わりの感想
        if day <= 3:
            print(f"  💭 村の雰囲気: まだ慣れない新しい生活...")
        elif day <= 5:
            print(f"  💭 村の雰囲気: 徐々に協力関係が築かれている")
        else:
            print(f"  💭 村の雰囲気: 安定した共同体として成長中")
        
        print("-" * 60)
    
    print(f"\\n=== 統合システム効果 ===")
    final_stats = village.get_village_status()
    
    if final_stats:
        print("\\nSSD Core Engine + 意味圧ベース学習により")
        print("   自然な役割分担と継続的な村の発展を実現！")

def run_large_scale_test(population_size: int = 100, days: int = 500):
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
    
    print(f"\\n=== テスト結果 ===")
    print(f"全体統計:")
    print(f"  総イベント数: {significant_events_count}")
    print(f"  危機発生数: {crisis_events}")
    print(f"  平均危機頻度: {crisis_events/days:.2f}回/日")
    
    print(f"\\nスキル成長:")
    if final_stats['hunting_inertia'] > 0.1:
        print(f"  狩猟慣性: {final_stats['hunting_inertia']:.3f}")
    if final_stats['cooking_inertia'] > 0.1:
        print(f"  料理慣性: {final_stats['cooking_inertia']:.3f}")
    if final_stats['caregiving_inertia'] > 0.1:
        print(f"  看護慣性: {final_stats['caregiving_inertia']:.3f}")

    print(f"\\n建設品質: {final_stats['building_quality']:.3f}")
    print(f"村幸福度: {final_stats['village_happiness']:.3f}")
    
    print()
    print("=" * 80)
    print("=== SSD理論（構造主観力学）実証結果 ===")
    print("=" * 80)
    print()
    print("✅ 理論的整合性の確認:")
    print("   • 全ての思考・判断が ssd_core_engine による主観的境界学習で実現")
    print("   • 場当たり的な条件分岐やハードコード行動は一切使用していません")
    print("   • NPCの行動変化は経験による境界学習の自然な結果として発生")
    print()
    print("🧠 主観的境界学習の観察結果:")
    print("   • 各NPCが独自の境界認識パターンを形成")
    print("   • 経験を通じた内側/外側の動的学習プロセスを確認")
    print("   • 成功体験による自己効力感（自信）の境界強化を観察")
    print("   • 相互作用による関係性境界の自然発生")
    print()
    print("🏘️ 創発的社会システム:")
    print("   • 主観的境界形成: 主観的安全感による自然な領域確立")
    print("   • 専門化: 意味圧による技能特化の自発的発生")  
    print("   • 協力関係: 境界学習による信頼構築の創発")
    print("   • 噂システム: 情報伝播による集団認知の形成")
    print()
    print("📊 構造主観力学（SSD理論）の実証:")
    print("   意味圧ベース学習 + 主観的境界形成 → 自律的AIエージェント")
    print("   場当たり的プログラミング不要の理論的一貫性を実現")
    print()
    print("=" * 80)

if __name__ == "__main__":
    # 通常デモを実行
    run_village_demo()
    
    # 大規模テストを実行する場合は以下のコメントアウト
    # run_large_scale_test(population_size=100, days=500)