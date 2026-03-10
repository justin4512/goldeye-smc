#!/bin/bash
# GoldEye SMC 系統安裝腳本

echo "🏦 GoldEye SMC 交易系統安裝"
echo "================================"

# 檢查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤：未找到 Python 3"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 創建虛擬環境（可選但推薦）
read -p "是否創建虛擬環境？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 創建虛擬環境..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 安裝依賴
echo "📦 安裝依賴包..."
pip3 install -r requirements.txt

# 複製環境配置
if [ ! -f .env ]; then
    echo "📝 複製環境配置..."
    cp .env.example .env
    echo "⚠️  請編輯 .env 文件，填寫 Telegram Bot Token 和 Chat ID"
fi

echo ""
echo "✅ 安裝完成！"
echo ""
echo "🚀 下一步:"
echo "   1. 編輯 .env 文件，填寫 Telegram 配置"
echo "   2. 運行測試：python3 tests/test_system.py"
echo "   3. 啟動系統：python3 main.py"
echo ""
