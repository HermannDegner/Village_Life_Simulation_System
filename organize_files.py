"""
🏘️ VLSS ファイル整理スクリプト

古いファイルをアーカイブに移動し、現在のシステムを整理します
"""

import os
import shutil
from pathlib import Path

def organize_vlss_files():
    """VLSSファイルを整理"""
    
    # ベースディレクトリ
    base_dir = Path("d:/GitHub/VLSS")
    archive_dir = base_dir / "archive"
    current_dir = base_dir / "current_systems" 
    tests_dir = base_dir / "tests_and_demos"
    
    print("🏘️ === VLSS ファイル整理開始 ===")
    
    # アーカイブ対象（古いファイル）
    archive_files = [
        "caregiving_reputation_system.py",
        "comprehensive_village_system.py", 
        "objective_relationship_system.py",
        "integrated_100_day_simulation.py",
        "long_term_simulation.py",
    ]
    
    # テスト・デモ対象
    test_files = [
        "carpentry_integration_test.py",
        "meaning_pressure_village_test.py",
        "ssd_learning_saturation_demo.py",
        "hunting_specialization_demo.py",
        "natural_role_evolution.py",
    ]
    
    # 現在使用中のシステム（移動しない）
    current_files = [
        "village_ssd_adapter.py",
        "village_meaning_pressure_system.py", 
        "hunting_system.py",
        "relationship_care_system.py",
        "cooking_integrated_village.py",
        "meaning_pressure_carpentry_system.py",
        "integrated_village_simulation.py",
        "meaning_pressure_100_day_simulation.py",
    ]
    
    # 実験系（移動しない、現在開発中）
    experimental_files = [
        "rumor_system.py",
        "rumor_system_clean.py", 
        "ssd_formal_alignment.py",
        "village_ssd_formal_adapter.py",
        "meaning_pressure_alignment.py",
    ]
    
    # アーカイブ移動
    print("\\n📦 古いファイルをアーカイブに移動中...")
    for filename in archive_files:
        src = base_dir / filename
        if src.exists():
            dst = archive_dir / filename
            try:
                shutil.move(str(src), str(dst))
                print(f"  ✅ {filename} → archive/")
            except Exception as e:
                print(f"  ❌ {filename} 移動失敗: {e}")
        else:
            print(f"  ⚠️ {filename} が見つかりません")
    
    # テスト・デモ移動
    print("\\n🧪 テスト・デモファイルを移動中...")
    for filename in test_files:
        src = base_dir / filename  
        if src.exists():
            dst = tests_dir / filename
            try:
                shutil.move(str(src), str(dst))
                print(f"  ✅ {filename} → tests_and_demos/")
            except Exception as e:
                print(f"  ❌ {filename} 移動失敗: {e}")
        else:
            print(f"  ⚠️ {filename} が見つかりません")
    
    # 現在のシステム状況表示
    print("\\n🌟 現在使用中のメインシステム:")
    for filename in current_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} (見つからない)")
    
    # 実験系ファイル状況
    print("\\n🔬 実験・開発中ファイル:")
    for filename in experimental_files:
        filepath = base_dir / filename
        if filepath.exists():
            print(f"  🧪 {filename}")
        else:
            print(f"  ❌ {filename} (見つからない)")
    
    print("\\n✅ ファイル整理完了！")
    print("\\n📖 詳細は README_ファイル整理.md を参照してください")

if __name__ == "__main__":
    organize_vlss_files()