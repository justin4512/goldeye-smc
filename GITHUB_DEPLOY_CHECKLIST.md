# 📦 GitHub 部署完整清單

**日期：** 2026-03-10  
**狀態：** ✅ 所有部署文件已準備完成

---

## ✅ 已創建的部署文件

| 文件 | 用途 | 狀態 |
|------|------|------|
| `Dockerfile` | Docker 容器配置 | ✅ 完成 |
| `docker-compose.yml` | Docker Compose 配置 | ✅ 完成 |
| `.gitignore` | Git 忽略文件 | ✅ 完成 |
| `.github/workflows/monitor.yml` | GitHub Actions 定時任務 | ✅ 完成 |
| `DEPLOYMENT.md` | 完整部署指南 | ✅ 完成 |
| `deploy-to-github.sh` | 一鍵部署腳本 | ✅ 完成 |

---

## 🚀 快速部署流程

### 步驟 1: 推送到 GitHub

```bash
cd /home/node/.openclaw/workspace/xauusd_smc

# 方法 1: 使用部署腳本
chmod +x deploy-to-github.sh
./deploy-to-github.sh

# 方法 2: 手動推送
git init
git add .
git commit -m "GoldEye SMC v2.0"
git remote add origin https://github.com/YOUR_USERNAME/goldeye-smc.git
git push -u origin main
```

### 步驟 2: 配置 GitHub Secrets

1. 進入你的 GitHub 倉庫
2. 點擊 **Settings** → **Secrets and variables** → **Actions**
3. 添加以下 Secrets：

| Secret Name | 值 |
|-------------|---|
| `TELEGRAM_BOT_TOKEN` | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | `123456789` |

### 步驟 3: 選擇雲端平台部署

#### 選項 A: Hugging Face Spaces（推薦）⭐

```bash
# 安裝 Hugging Face CLI
pip install huggingface_hub

# 登錄
huggingface-cli login

# 推送代碼
git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/goldeye-smc
git push -u origin main
```

然後在 Hugging Face Space 後台配置環境變量。

#### 選項 B: Railway

1. 前往 https://railway.app/
2. 點擊 **New Project** → **Deploy from GitHub**
3. 選擇 `goldeye-smc` 倉庫
4. 配置環境變量
5. 自動部署

#### 選項 C: Render

1. 前往 https://render.com/
2. 點擊 **New** → **Web Service**
3. 連接 GitHub 倉庫
4. 選擇 **Docker** 環境
5. 配置環境變量
6. 部署

---

## 📊 部署方案對比

| 方案 | 費用 | 運行時間 | 難度 | 推薦度 |
|------|------|---------|------|--------|
| **Hugging Face Spaces** | 免費 | 24/7 | ⭐ | ⭐⭐⭐⭐⭐ |
| **Railway** | $5 credit | 24/7 | ⭐⭐ | ⭐⭐⭐⭐ |
| **Render** | 免費 750h | 24/7 | ⭐⭐ | ⭐⭐⭐⭐ |
| **GitHub Actions** | 免費 | 定時 | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 推薦給 NAS 用戶

由於你的 NAS 環境受限，**強烈推薦使用 Hugging Face Spaces**：

### 為什麼選擇 Hugging Face Spaces？

✅ **完全免費** - 無需信用卡  
✅ **24/7 運行** - 持續監控 XAUUSD  
✅ **Docker 支持** - 使用現有的 Dockerfile  
✅ **自動重啟** - 崩潰後自動恢復  
✅ **內置日誌** - 方便調試  
✅ **環境變量** - 安全存儲 Telegram Token  

### 部署時間

- **首次部署：** 約 10 分鐘
- **後續更新：** 自動部署（連接 GitHub）

---

## ⚠️ 重要提醒

### 1. 不要提交的敏感文件

以下文件已加入 `.gitignore`，**切勿手動提交**：

- `.env` - 包含 Telegram Token
- `config/secrets.yaml` - 敏感配置
- `logs/` - 日誌文件
- `*.db` - 數據庫文件

### 2. 使用環境變量

所有敏感配置都應該通過雲端平台的 **環境變量/Secrets** 功能設置，而不是寫入代碼。

### 3. 監控運行狀態

部署後定期檢查：
- 雲端平台的日誌
- Telegram 是否收到心跳消息
- GitHub Actions 運行記錄（如果使用）

---

## 🔧 故障排查

### Q1: GitHub 推送失敗？

```bash
# 檢查 Git 配置
git config --global user.email "your@email.com"
git config --global user.name "Your Name"

# 重新推送
git push -u origin main
```

### Q2: Hugging Face 構建失敗？

查看 Space 的 **Logs** 標籤頁，常見問題：
- `requirements.txt` 格式錯誤
- `Dockerfile` 語法問題
- 缺少必要文件

### Q3: 收不到 Telegram 通知？

檢查：
1. 環境變量是否正確設置
2. Bot Token 是否有效
3. Chat ID 是否正確
4. 是否已在 Telegram 中啟動 Bot

---

## 📞 支持資源

| 資源 | 連結 |
|------|------|
| Hugging Face 文檔 | https://huggingface.co/docs/hub/spaces |
| Railway 文檔 | https://docs.railway.app/ |
| Render 文檔 | https://render.com/docs |
| GitHub Actions 文檔 | https://docs.github.com/en/actions |

---

## ✅ 部署檢查清單

部署前請確認：

- [ ] 已創建 GitHub 賬戶
- [ ] 已創建 Telegram Bot
- [ ] 已獲取 Bot Token 和 Chat ID
- [ ] 已閱讀 DEPLOYMENT.md
- [ ] 已選擇雲端平台

部署後請確認：

- [ ] 代碼已成功推送到 GitHub
- [ ] 雲端平台已正確配置環境變量
- [ ] 容器/服務已成功啟動
- [ ] Telegram 收到測試消息
- [ ] 日誌顯示正常運行

---

**準備就緒！開始部署吧！** 🚀

參考 `DEPLOYMENT.md` 獲取詳細步驟。
