#!/bin/bash
# OpenCode 配置一键同步脚本（Linux/macOS）
# 用法: bash setup.sh

REPO="https://github.com/ikunops/opencode-dotfiles.git"
TARGET="$HOME/.config/opencode"
# 持久保存（不再放 /tmp、也不再删除）—— sync-skills-links.py 需要一份常驻副本当权威来源，
# 各客户端的 skills 目录链接都指向它。删掉它 = 所有客户端失去技能。
TEMP="$HOME/opencode-dotfiles"

echo "🔄 开始同步 OpenCode 配置..."

# 检测操作系统
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="linux"
    echo "📌 检测到平台: macOS"
else
    PLATFORM="linux"
    echo "📌 检测到平台: Linux"
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 请先安装 Node.js >= 18.0.0"
    echo "   安装: https://nodejs.org/"
    exit 1
fi

# 检查 OpenCode
if ! command -v opencode &> /dev/null; then
    echo "❌ 请先安装 OpenCode"
    echo "   安装: npm install -g opencode-ai"
    exit 1
fi

# 克隆或更新配置
if [ -d "$TEMP" ]; then
    echo "📥 更新配置..."
    git -C "$TEMP" pull
else
    echo "📥 克隆配置..."
    git clone "$REPO" "$TEMP"
fi

# 安装依赖（包括 infra-ops-mcp）
echo "📦 安装依赖..."
cd "$TEMP" && npm install

# 创建目标目录
mkdir -p "$TARGET"

# 读取基础配置和平台配置，合并生成最终配置
# 这里简化处理，直接复制基础配置并修改 shell
cp "$TEMP/opencode.base.jsonc" "$TARGET/opencode.jsonc"

# 用 sed 修改 shell 配置
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' 's/"powershell"/"bash"/g' "$TARGET/opencode.jsonc"
else
    sed -i 's/"powershell"/"bash"/g' "$TARGET/opencode.jsonc"
fi

# 复制其他文件
cp "$TEMP/tui.jsonc" "$TARGET/" 2>/dev/null || true
cp "$TEMP/package.json" "$TARGET/"
cp "$TEMP/package-lock.json" "$TARGET/"

# 复制目录
# 已存在就跳过 —— cp -r 在「目标已存在」时会把源塞进目标里（skills/skills、plugin/plugin），
# 而 $TARGET 本身可能就是指回本仓库的链接（那种情况下目标与源是同一份）。
# skills 的最终形态由末尾的 sync-skills-links.py 统一成链接；这里只在缺失时兜底复制。
if [ -e "$TARGET/skills" ]; then
    echo "⏭  skills 已存在，跳过复制（末尾会统一成链接）"
else
    cp -r "$TEMP/skills" "$TARGET/"
fi
if [ -e "$TARGET/plugin" ]; then
    echo "⏭  plugin 已存在，跳过复制"
else
    # 注：原写成 plugins/，仓库里实际是 plugin/ —— 顺手改正
    cp -r "$TEMP/plugin" "$TARGET/"
fi

# 让各 AI 客户端共用同一份 skills（一份物理文件、多入口）
# 脚本自带保护：遇到真实目录先备份、遇到「独有 skill」默认跳过，不会丢东西。
SYNC="$TEMP/scripts/sync-skills-links.py"
if [ -f "$SYNC" ]; then
    PY="$(command -v python3 || command -v python)"
    if [ -n "$PY" ]; then
        echo "🔗 统一各客户端 skills 指向..."
        "$PY" "$SYNC" --apply || echo "⚠️  skills 指向未全部完成，可稍后重跑: $PY $SYNC --apply"
    else
        echo "⚠️  未找到 python，跳过 skills 指向统一（可手动跑 scripts/sync-skills-links.py）"
    fi
fi

echo "✅ 配置同步完成！"
echo ""
echo "📌 当前配置:"
echo "   Shell: bash"
echo "   MCP: infra-ops + composio"
echo ""
echo "📌 启动 OpenCode:"
echo "   opencode"
echo ""
echo "📌 首次使用 Composio 时会弹出浏览器认证"
