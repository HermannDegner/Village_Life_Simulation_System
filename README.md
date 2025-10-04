# 🏘️ VLSS (Village Life Simulation System) - クイックスタート

## 🚀 すぐに使う

### 👑 メインシステム実行
```bash
# メイン村シミュレーション
python integrated_village_simulation.py

# 100日間長期テスト  
python meaning_pressure_100_day_simulation.py
```

## 📁 現在のファイル構成

```
d:\GitHub\VLSS\
├── 🌟 メインシステム
│   ├── integrated_village_simulation.py      # 👑 メイン統合シミュレーション
│   └── meaning_pressure_100_day_simulation.py # ⏳ 100日間テスト
│
├── 🧠 コアエンジン
│   ├── village_ssd_adapter.py                # SSD Core Engine適用
│   └── village_meaning_pressure_system.py    # 意味圧学習理論
│
├── 🎯 統合活動システム
│   ├── hunting_system.py                     # 🏹 狩猟 (SSD+意味圧)
│   ├── relationship_care_system.py           # 💝 看護 (SSD+意味圧)
│   ├── cooking_integrated_village.py         # 🍳 料理 (SSD+意味圧)  
│   └── meaning_pressure_carpentry_system.py  # 🔨 大工 (SSD+意味圧)
│
├── 🔬 実験中
│   ├── rumor_system.py                       # 噂システム
│   ├── ssd_formal_alignment.py               # 形式的アライメント
│   └── village_ssd_formal_adapter.py         # 形式的SSD適用
│
├── 📦 整理済みフォルダ
│   ├── archive/                              # 古いファイル
│   └── tests_and_demos/                      # テスト・デモ
│
└── 📖 ドキュメント
    ├── README_ファイル整理.md                # 詳細ファイル構成  
    └── README.md                             # このファイル
```

## ✨ 統合システムの特徴

### 🧠 意味圧ベース学習 (W = p·j - ρj²)
- **意味圧**: 新規性・複雑さ・社会的影響による学習圧力
- **学習飽和**: 日常作業で学習効果が減少、緊急・革新時に急成長
- **自然な専門化**: 個人の特性に基づく自発的な役割分担

### 🏘️ SSD Core Engine効果
- **信頼関係**: 成功/失敗による動的な村人間信頼変化
- **アライメント慣性**: 継続活動による価値観・行動パターンの固定
- **領域管理**: 専門分野での縄張り・影響圏形成

### 🎯 統合された4つの活動
1. **🏹 狩猟**: 食料確保、リスク管理、チームワーク
2. **💝 看護**: 健康管理、緊急対応、共感能力
3. **🍳 料理**: 資源活用、創造性、コミュニティ形成
4. **🔨 大工**: 建築技術、インフラ整備、村発展

## 🎮 使用例

### 📊 基本シミュレーション
```bash
python integrated_village_simulation.py
# → 1日単位の詳細村生活シミュレーション
```

### 📈 長期分析
```bash  
python meaning_pressure_100_day_simulation.py
# → 100日間の村発展・専門化プロセス観測
```

### 🔧 個別システムテスト
```bash
# 大工システムのみ
python meaning_pressure_carpentry_system.py

# 意味圧システムのみ  
python meaning_pressure_village_test.py  # tests_and_demos/内
```

## 🎯 期待される結果

- **自然な職業分化**: 村人が得意分野で専門家に成長
- **学習飽和効果**: 慣れた作業の成長率低下
- **緊急時急成長**: 危機・革新時の急速なスキル向上
- **信頼関係進化**: 協力成功で信頼構築、失敗で悪化
- **村全体発展**: 個人成長が村全体の繁栄に寄与

---
**🏆 現在の統合状況**: 4つの主要活動システムが完全統合済み！