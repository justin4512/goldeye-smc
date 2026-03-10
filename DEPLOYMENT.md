# 🚀 GoldEye SMC GitHub 部署指南

本指南說明如何將 GoldEye 系統部署到雲端，解決 NAS 環境受限問題。

---

## 📋 部署選項總覽

| 方案 | 費用 | 難度 | 適合場景 |
|------|------|------|---------|
| **Hugging Face Spaces** | 免費 | ⭐ | 首選推薦 |
| **Railway** | $5/月 credit | ⭐⭐ | 穩定運行 |
| **Render** | 免費 750h/月 | ⭐⭐ | 備選方案 |
| **GitHub Actions** | 免費 2000min/月 | ⭐⭐⭐ | 定時掃描 |

---

## 方案一：Hugging Face Spaces（推薦）⭐

### 優點
- ✅ 完全免費
- ✅ 支持 Docker 容器
- ✅ 自動重啟
- ✅ 無需信用卡

### 部署步驟

#### 1. 創建 Hugging Face 賬戶
前往 https://huggingface.co/ 註冊賬戶

#### 2. 創建新的 Space
1. 點擊右上角頭像 → **New Space**
2. 填寫：
   - **Space name:** `goldeye-smc`
   - **License:** MIT
   - **Space SDK:** 選擇 **Docker**
   - **Visibility:** Private（建議）
3. 點擊 **Create Space**

#### 3. 推送代碼到 Hugging Face

```bash
# 安裝 huggingface-cli
pip install huggingface_hub

# 登錄（輸入你的 HF Token）
huggingface-cli login

# 初始化 Git 倉庫
cd /home/node/.openclaw/workspace/xauusd_smc
git init
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/goldeye-smc

# 添加所有文件
git add .
git commit -m "Initial commit: GoldEye SMC v2.0"

# 推送到 Hugging Face
git push -u origin main
```

#### 4. 配置環境變量
1. 進入你的 Space 頁面
2. 點擊 **Settings** → **Variables and secrets**
3. 添加：
   - `TELEGRAM_BOT_TOKEN` = 你的 Bot Token
   - `TELEGRAM_CHAT_ID` = 你的 Chat ID

#### 5. 等待部署完成
Hugging Face 會自動構建 Docker 鏡像並啟動，約 3-5 分鐘。

#### 6. 查看日誌
在 Space 頁面點擊 **Logs** 查看運行狀態。

---

## 方案二：Railway

### 優點
- ✅ $5/月 credit（足夠運行）
- ✅ 自動部署
- ✅ 內置數據庫

### 部署步驟

#### 1. 創建 Railway 賬戶
前往 https://railway.app/ 註冊（需 GitHub 賬戶）

#### 2. 創建新項目
1. 點擊 **New Project**
2. 選擇 **Deploy from GitHub repo**
3. 選擇你的 `goldeye-smc` 倉庫

#### 3. 配置環境變量
在 Railway 後台添加：
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

#### 4. 自動部署
Railway 會自動檢測 `Dockerfile` 並部署。

---

## 方案三：Render

### 優點
- ✅ 免費 750 小時/月
- ✅ 自動 HTTPS
- ✅ 內置 CI/CD

### 部署步驟

#### 1. 創建 Render 賬戶
前往 https://render.com/ 註冊

#### 2. 創建 Web Service
1. 點擊 **New** → **Web Service**
2. 連接 GitHub 倉庫
3. 配置：
   - **Name:** goldeye-smc
   - **Environment:** Docker
   - **Instance Type:** Free

#### 3. 配置環境變量
添加 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`

#### 4. 部署
點擊 **Create Web Service**，等待部署完成。

---

## 方案四：GitHub Actions（定時掃描）

### 優點
- ✅ 完全免費
- ✅ 與 GitHub 深度整合
- ❌ 不適合持續監控（有時間限制）

### 創建 Actions 工作流

創建文件 `.github/workflows/monitor.yml`:

```yaml
name: GoldEye 監控

on:
  schedule:
    - cron: '*/15 * * * *'  # 每 15 分鐘運行
  workflow_dispatch:  # 手動觸發

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 設置 Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: 安裝依賴
      run: |
        pip install -r requirements.txt
    
    - name: 運行監控
      env:
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      run: |
        python main.py
```

### 配置 Secrets
1. 進入 GitHub 倉庫 → **Settings**
2. **Secrets and variables** → **Actions**
3. 添加：
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`

---

## 📊 各方案對比

| 特性 | HF Spaces | Railway | Render | Actions |
|------|-----------|---------|--------|---------|
| 費用 | 免費 | $5 credit | 免費 | 免費 |
| 運行時間 | 24/7 | 24/7 | 750h/月 | 定時 |
| 設置難度 | 簡單 | 中等 | 中等 | 複雜 |
| 自動重啟 | ✅ | ✅ | ✅ | N/A |
| 日誌查看 | ✅ | ✅ | ✅ | ✅ |

---

## 🎯 推薦方案

**首選：Hugging Face Spaces**
- 完全免費
- 設置最簡單
- 支持 Docker
- 24/7 運行

**備選：Railway**
- 如果 HF Spaces 不穩定
- $5 credit 足夠運行數月

---

## ⚠️ 注意事項

1. **環境變量安全**
   - 永遠不要將 `.env` 文件提交到 Git
   - 使用 `.gitignore` 排除敏感文件
   - 在雲平台後台配置 secrets

2. **監控運行狀態**
   - 定期查看日誌
   - 設置 Telegram 心跳通知
   - 配置異常告警

3. **數據持久化**
   - 使用雲存儲保存交易記錄
   - 定期備份配置文件

---

## 🔧 故障排查

### Q: 部署後收不到 Telegram 通知？
A: 檢查環境變量是否正確設置，並在日誌中查看錯誤信息。

### Q: 容器不斷重啟？
A: 查看日誌，可能是：
- 缺少環境變量
- 依賴安裝失敗
- 代碼錯誤

### Q: Hugging Face 構建失敗？
A: 檢查 `Dockerfile` 語法，確保所有文件已正確提交。

---

## 📞 下一步

1. **選擇部署方案** - 推薦 Hugging Face Spaces
2. **推送代碼到 GitHub**
   ```bash
   cd /home/node/.openclaw/workspace/xauusd_smc
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/goldeye-smc.git
   git push -u origin main
   ```
3. **按照所選方案部署**
4. **測試 Telegram 通知**

---

**祝你部署成功！** 🎉
