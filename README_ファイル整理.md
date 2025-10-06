# 🏘️ VLSS (Village Life Simulation System) ファイル整理ガイド

## 📁 現在使用中のメインシステム

### 🧠 コアシステム
| ファイル名 | 役割 | 説明 |
|-----------|------|------|
| `village_ssd_adapter.py` | SSD Core Engine適用 | SSD効果を村システムに適用 |
| `village_meaning_pressure_system.py` | 意味圧学習システム | W = p·j - ρj² 学習飽和理論 |

### 🏹 活動システム（統合済み）
| ファイル名 | 活動 | 統合状況 |
|-----------|------|----------|
| `hunting_system.py` | 狩猟 | ✅ SSD + 意味圧統合済み |
| `relationship_care_system.py` | 看護 | ✅ SSD + 意味圧統合済み |
| `cooking_integrated_village.py` | 料理 | ✅ SSD + 意味圧統合済み |
| `meaning_pressure_carpentry_system.py` | 大工 | ✅ SSD + 意味圧統合済み |

### 🌟 統合メインシステム
| ファイル名 | 役割 | 説明 |
|-----------|------|------|
| `integrated_village_simulation.py` | **メインシステム** | 4つの活動を統合した村シミュレーション |
| `meaning_pressure_100_day_simulation.py` | **長期テスト** | 100日間の統合システムテスト |

## 📊 テスト・デモ・検証ファイル

### 🧪 テスト系
| ファイル名 | 用途 | 状態 |
|-----------|------|------|
| `carpentry_integration_test.py` | 大工システム統合テスト | 使用中 |
| `meaning_pressure_village_test.py` | 意味圧システムテスト | 使用中 |
| `ssd_learning_saturation_demo.py` | SSD学習飽和デモ | 参考用 |

### 🎯 デモ系  
| ファイル名 | 用途 | 状態 |
|-----------|------|------|
| `hunting_specialization_demo.py` | 狩猟専門化デモ | 参考用 |
| `natural_role_evolution.py` | 自然役割進化デモ | 参考用 |

## 🗂️ 古いファイル（アーカイブ候補）

### 🕰️ 統合前システム
| ファイル名 | 旧システム | 状況 |
|-----------|-----------|------|
| `caregiving_reputation_system.py` | 旧看護システム | ❌ 古い（統合済み） |
| `comprehensive_village_system.py` | 旧統合システム | ❌ 古い（新版あり） |
| `objective_relationship_system.py` | 旧関係システム | ❌ 古い |
| `integrated_100_day_simulation.py` | 旧100日テスト | ❌ 古い（新版あり） |
| `long_term_simulation.py` | 旧長期シミュ | ❌ 古い |

### 🔬 実験・試作系
| ファイル名 | 用途 | 状況 |
|-----------|------|------|
| `rumor_system.py` | 噂システム実装 | 🔄 実験中 |
| `rumor_system_clean.py` | 噂システム改良版 | 🔄 実験中 |
| `ssd_formal_alignment.py` | 形式的アライメント | 🔄 実験中 |
| `village_ssd_formal_adapter.py` | 形式的SSD適用 | 🔄 実験中 |
| `meaning_pressure_alignment.py` | 意味圧アライメント | 🔄 実験中 |

## 🎯 推奨開発フロー

### 👑 メインファイル（普段使い）
1. **`integrated_village_simulation.py`** - メイン村シミュレーション
2. **`meaning_pressure_100_day_simulation.py`** - 長期テスト

### 🔧 システム修正時
1. `village_meaning_pressure_system.py` - 学習システム調整
2. `village_ssd_adapter.py` - SSD効果調整
3. 各活動システム - 個別活動の調整

### 🧪 新機能テスト時
1. `tests_and_demos/` フォルダー内でテスト
2. 完成したら `current_systems/` に移動

## 🚀 次回開発時の開始手順

1. **現在状況確認**: `integrated_village_simulation.py` を実行
2. **長期テスト**: `meaning_pressure_100_day_simulation.py` で100日テスト
3. **新機能開発**: 個別システムファイルを修正
4. **統合テスト**: メインシステムで動作確認

---

**🎯 現在の統合状況**: 狩猟・看護・料理・大工の4システムがSSD Core Engine + 意味圧ベース学習で完全統合済み！