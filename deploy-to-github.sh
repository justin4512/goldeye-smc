#!/bin/bash
# GoldEye SMC GitHub 部署腳本

echo "🚀 GoldEye SMC GitHub 部署"
echo "================================"

# 檢查 Git
if ! command -v git &> /dev/null; then
    echo "❌ 錯誤：未找到 Git"
    exit 1
fi

# 獲取用戶輸入
read -p "請輸入你的 GitHub 用戶名：" GITHUB_USER
read -p "倉庫名稱 (預設：goldeye-smc): " REPO_NAME
REPO_NAME=${REPO_NAME:-goldeye-smc}

echo ""
echo "📁 將部署到：https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""

# 初始化 Git
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 倉庫..."
    git init
fi

# 添加所有文件
echo "📝 添加文件..."
git add .

# 提交
echo "💾 提交更改..."
git commit -m "GoldEye SMC v2.0 - Initial commit"

# 添加遠程（如果不存在）
if ! git remote | grep -q "^origin$"; then
    echo "🔗 添加 GitHub 遠程..."
    git remote add origin https://github.com/${GITHUB_USER}/${REPO_NAME}.git
fi

# 推送
echo "🚀 推送到 GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 推送完成！"
echo ""
echo "📋 下一步:"
echo "   1. 前往 https://github.com/${GITHUB_USER}/${REPO_NAME}/settings/secrets/actions"
echo "   2. 添加 Secrets:"
echo "      - TELEGRAM_BOT_TOKEN"
echo "      - TELEGRAM_CHAT_ID"
echo ""
echo "📖 詳細部署指南請查看：DEPLOYMENT.md"
echo ""
