#!/bin/bash
# 用法: ./collect_and_push.sh <folder_name>

set -e

if [ -z "$1" ]; then
  echo "❌ 请提供文件夹名作为参数"
  echo "用法: ./collect_and_push.sh <folder_name>"
  exit 1
fi

FOLDER_NAME=$1
TARGET_DIR="/workspace/Code-Web-Agent/oh_ui_sessions/$FOLDER_NAME"

echo "📂 创建目录: $TARGET_DIR"
mkdir -p "$TARGET_DIR"

echo "📄 复制文件到 $TARGET_DIR"
cp -f /workspace/*.py "$TARGET_DIR" 2>/dev/null || true
cp -f /workspace/*.md "$TARGET_DIR" 2>/dev/null || true
cp -f /workspace/*.json "$TARGET_DIR" 2>/dev/null || true
cp -r /workspace/.browser_screenshots "$TARGET_DIR" 2>/dev/null || true

echo "✅ 文件复制完成"

cd /workspace/Code-Web-Agent

echo "📤 推送到 GitHub..."
git add "oh_ui_sessions/$FOLDER_NAME"
git commit -m "Add session files for $FOLDER_NAME"
git push origin main

echo "🎉 已推送到仓库: $FOLDER_NAME"
