# 🏦 GoldEye SMC 交易系統 v2.0

> **機構級 Smart Money Concept 交易系統**  
> 基於 Python + yfinance + SMC 邏輯，透過 Telegram 發送進出信號

---

## 📋 功能特色

### 核心功能
- ✅ **Order Block 檢測** - 自動識別機構訂單區
- ✅ **Fair Value Gap** - 檢測價格空白區作為目標
- ✅ **市場結構分析** - BOS/CHoCH 趨勢判斷
- ✅ **流動性掃描** - 識別 BSL/SSL 止損聚集區
- ✅ **多時間框架分析** - Top-Down Analysis (1D/4H/1H/15m)
- ✅ **Telegram 通知** - 即時推送交易信號
- ✅ **風險管理** - 動態 Position Sizing

### 機構級功能
- 📊 **多資產數據** - XAUUSD + GLD + DXY + VIX 相關性分析
- 🏦 **COT 報告整合** - 追蹤機構持倉動向
- 📈 **ETF 資金流** - 監控 GLD 持倉變化
- 📉 **宏觀因子** - 實際利率、美元相關性

---

## 🚀 快速開始

### 選項 A：本地運行

#### 1. 安裝依賴

```bash
cd xauusd_smc
pip install -r requirements.txt
```

#### 2. 配置 Telegram Bot

```bash
# 複製環境配置範例
cp .env.example .env

# 編輯 .env 文件，填入你的 Telegram Bot Token 和 Chat ID
nano .env
```

**獲取 Telegram Bot Token:**
1. 在 Telegram 搜尋 `@BotFather`
2. 發送 `/newbot` 創建新 Bot
3. 複製 Bot Token

**獲取 Chat ID:**
1. 在 Telegram 搜尋 `@userinfobot`
2. 發送任意消息
3. 它會回覆你的 Chat ID

### 3. 運行系統

```bash
# 測試運行
python main.py
```

### 選項 B：部署到 GitHub + 雲端（推薦 NAS 用戶）⭐

詳細步驟請查看 [DEPLOYMENT.md](DEPLOYMENT.md)

```bash
# 一鍵部署到 GitHub
chmod +x deploy-to-github.sh
./deploy-to-github.sh

# 然後在 GitHub 配置 Secrets，選擇雲端平台部署
```

**推薦雲端平台：**
- 🥇 **Hugging Face Spaces** - 完全免費，支持 Docker
- 🥈 **Railway** - $5/月 credit
- 🥉 **Render** - 免費 750 小時/月

---

## 📁 項目結構

```
xauusd_smc/
├── config/
│   └── config.yaml          # 主配置文件
├── src/
│   ├── data/
│   │   └── fetcher.py       # yfinance 數據獲取
│   ├── smc/
│   │   ├── order_block.py   # Order Block 檢測
│   │   ├── fvg.py           # Fair Value Gap 檢測
│   │   └── structure.py     # 市場結構分析 (BOS/CHoCH)
│   ├── signal/
│   │   └── generator.py     # 信號生成器
│   └── utils/
│       └── notifier.py      # Telegram 通知
├── tests/                    # 測試文件
├── notebooks/                # Jupyter 分析筆記本
├── main.py                   # 主程序入口
├── requirements.txt          # Python 依賴
└── README.md                 # 本文件
```

---

## 📱 Telegram 通知範例

### 進場信號
```
🏦 GoldEye SMC 信號

📊 方向：做多
💯 信心度：78%
⏰ 時間框架：4H/15m

📍 進場區間：$2,348 ~ $2,352
🛑 止損：$2,335 (-0.55%)
🎯 目標 1：$2,368 (R:R = 1:1.5)
🎯 目標 2：$2,385 (R:R = 1:2.8)

🔍 SMC 邏輯：
- 結構：4H Bullish BOS 確認
- OB：回測 $2,345-2,350 Bullish OB (未測試)
- FVG：上方 $2,365-2,370 未填補 FVG
```

---

## ⚙️ 配置說明

### config.yaml 主要配置項

```yaml
# SMC 參數
smc:
  order_block:
    min_body_atr_multiplier: 1.5  # 最小 K 線實體倍率
    max_test_count: 3              # 最大測試次數
  
  signal:
    min_confidence: 70            # 最低信心度 (%)
    min_rr_ratio: 1.5             # 最低風險報酬比

# 風險管理
risk:
  capital: 100000                 # 總資本 (USD)
  risk_per_trade: 0.01            # 單筆風險 (1%)
  max_total_exposure: 0.05        # 總風險敞口 (5%)
```

---

## 🧪 測試

```bash
# 運行單元測試
pytest tests/

# 測試 Order Block 檢測
python -m src.smc.order_block

# 測試 Telegram 通知
python -m src.utils.notifier
```

---

## 📊 回測（開發中）

```bash
# 運行回測
python -m src.backtest.engine --start-date 2020-01-01 --end-date 2026-03-10
```

---

## ⚠️ 風險提示

1. **本系統僅供學習研究** - 不構成投資建議
2. **紙上交易優先** - 建議先紙上交易 30 天驗證策略
3. **漸進式實盤** - 從 10% 頭寸開始，逐步增加
4. **風險控制** - 單筆風險不超過 1%，總風險不超過 5%
5. **市場風險** - 極端行情下所有技術分析可能失效

---

## 📝 待辦事項

- [ ] 完善回測引擎
- [ ] 整合 COT 報告分析
- [ ] 整合 ETF 資金流分析
- [ ] 添加 Web 控制面板
- [ ] 支持更多交易標的

---

## 📄 許可證

MIT License

---

## 🙏 致謝

- Smart Money Concept 社區
- yfinance 維護者
- Telegram Bot API

---

**最後更新：** 2026-03-10  
**版本：** v2.0.0
