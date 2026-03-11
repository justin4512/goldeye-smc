# 🚀 GoldEye SMC 快速開始指南

## 1️⃣ 安裝依賴

```bash
cd /home/node/.openclaw/workspace/xauusd_smc

# 方法 1: 使用安裝腳本
chmod +x install.sh
./install.sh

# 方法 2: 手動安裝
pip3 install -r requirements.txt
```

## 2️⃣ 配置 Telegram Bot

### 步驟 1: 創建 Bot
1. 在 Telegram 搜尋 `@BotFather`
2. 發送 `/newbot`
3. 輸入 Bot 名稱（例如：GoldEye Alert Bot）
4. 輸入 Bot 用戶名（例如：goldeye_alert_bot）
5. 複製 Bot Token（格式：`123456:ABC-DEF1234...`）

### 步驟 2: 獲取 Chat ID
1. 在 Telegram 搜尋 `@userinfobot`
2. 發送任意消息
3. 複製 Chat ID（格式：`123456789`）

### 步驟 3: 配置 .env
```bash
# 複製配置範例
cp .env.example .env

# 編輯配置
nano .env
```

填入：
```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234...
TELEGRAM_CHAT_ID=123456789
```

### 步驟 4: 啟動 Bot
1. 在 Telegram 中搜尋你的 Bot 用戶名
2. 發送 `/start` 啟動 Bot

## 3️⃣ 測試系統

```bash
# 運行測試
python3 tests/test_system.py
```

預期輸出：
```
✅ 成功獲取 XXX 根 K 線
✅ 檢測到 X 個 Order Block
✅ 檢測到 X 個 FVG
✅ 測試完成
```

## 4️⃣ 啟動監控

```bash
# 啟動系統
python3 main.py
```

啟動後會：
1. 測試 Telegram 連接
2. 開始監控 XAUUSD 價格
3. 每 60 秒掃描一次信號
4. 檢測到合格信號時發送 Telegram 通知

## 5️⃣ 後台運行（可選）

```bash
# 使用 nohup 後台運行
nohup python3 main.py > logs/goldenee.log 2>&1 &

# 查看日誌
tail -f logs/goldenee.log

# 停止系統
pkill -f "python3 main.py"
```

## 6️⃣ 使用 Docker（可選）

創建 Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
```

運行：
```bash
docker build -t goldeye-smc .
docker run -d --name goldeye \
  -e TELEGRAM_BOT_TOKEN=your_token \
  -e TELEGRAM_CHAT_ID=your_chat_id \
  goldeye-smc
```

---

## ❓ 常見問題

### Q: 無法獲取 XAUUSD 數據？
A: Yahoo Finance 可能有時區限制，嘗試：
- 使用 VPN
- 改用 `GC=F`（黃金期貨）作為數據源

### Q: Telegram 收不到通知？
A: 檢查：
- Bot Token 和 Chat ID 是否正確
- 是否已在 Telegram 中啟動 Bot（發送 /start）
- 查看日誌錯誤信息

### Q: 信號太少？
A: 這是正常的！SMC 策略只在高質量機會時進場。可以：
- 降低 `min_confidence` 門檻（不建議）
- 監控更多時間框架
- 耐心等待真正的好機會

---

## 📞 支持

遇到問題請查看：
- 日誌文件：`logs/goldenee.log`
- 測試輸出：`python3 tests/test_system.py`
