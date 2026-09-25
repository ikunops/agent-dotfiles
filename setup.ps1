# OpenCode 配置一键同步脚本（跨平台）
# 用法: 在新机器上运行此脚本

$repo = "https://github.com/ikunops/opencode-dotfiles.git"

# 检测操作系统
if ($IsLinux -or $IsMacOS) {
    $target = "$env:HOME/.config/opencode"
    $platform = "linux"
} else {
    $target = "$env:USERPROFILE\.config\opencode"
    $platform = "windows"
}

# 持久保存（不再放 TEMP、也不再删除）—— sync-skills-links.py 需要一份常驻副本当权威来源，
# 各客户端的 skills 目录链接都指向它。删掉它 = 所有客户端失去技能。
$temp = "$env:USERPROFILE/opencode-dotfiles"

Write-Host "🔄 开始同步 OpenCode 配置..." -ForegroundColor Cyan
Write-Host "📌 检测到平台: $platform" -ForegroundColor Yellow

# 检查 Node.js
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 请先安装 Node.js >= 18.0.0" -ForegroundColor Red
    Write-Host "   安装: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# 检查 OpenCode
if (-not (Get-Command opencode -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 请先安装 OpenCode" -ForegroundColor Red
    Write-Host "   安装: npm install -g opencode-ai" -ForegroundColor Yellow
    exit 1
}

# 克隆或更新配置
if (Test-Path $temp) {
    Write-Host "📥 更新配置..." -ForegroundColor Yellow
    git -C $temp pull
} else {
    Write-Host "📥 克隆配置..." -ForegroundColor Yellow
    git clone $repo $temp
}

# 安装依赖（包括 infra-ops-mcp）
Write-Host "📦 安装依赖..." -ForegroundColor Yellow
npm install --prefix $temp

# 创建目标目录
if (-not (Test-Path $target)) {
    New-Item -ItemType Directory -Path $target -Force | Out-Null
}

# 读取基础配置
$baseConfig = Get-Content "$temp/opencode.base.jsonc" | ConvertFrom-Json

# 读取平台特定配置
$platformConfig = Get-Content "$temp/platforms/$platform.jsonc" | ConvertFrom-Json

# 合并配置
$finalConfig = $baseConfig
$finalConfig.shell = $platformConfig.shell

# 保存最终配置
$finalConfig | ConvertTo-Json -Depth 10 | Set-Content "$target/opencode.jsonc"

# 复制其他文件
Copy-Item -Path "$temp/tui.jsonc" -Destination $target -Force -ErrorAction SilentlyContinue
Copy-Item -Path "$temp/package.json" -Destination $target -Force
Copy-Item -Path "$temp/package-lock.json" -Destination $target -Force

# 复制目录
# 已存在就跳过 —— Copy-Item 在「目标已存在」时会把源塞进目标里（skills/skills、plugin/plugin），
# 而 $target 本身可能就是指回本仓库的链接（那种情况下目标与源是同一份）。
# skills 的最终形态由末尾的 sync-skills-links.py 统一成链接；这里只在缺失时兜底复制。
if (Test-Path "$target/skills") {
    Write-Host "⏭  skills 已存在，跳过复制（末尾会统一成链接）" -ForegroundColor DarkGray
} else {
    Copy-Item -Path "$temp/skills" -Destination "$target/skills" -Recurse -Force
}
if (Test-Path "$target/plugin") {
    Write-Host "⏭  plugin 已存在，跳过复制" -ForegroundColor DarkGray
} else {
    Copy-Item -Path "$temp/plugin" -Destination "$target/plugin" -Recurse -Force
}

Copy-Item -Path "$temp/AGENTS.md" -Destination "$target/AGENTS.md" -Force
Copy-Item -Path "$temp/setup-vision.ps1" -Destination "$target/setup-vision.ps1" -Force

# Install vision toolkit CLIs (glance/ground/detect/trace/crop), idempotent
powershell -ExecutionPolicy Bypass -File "$target/setup-vision.ps1"

# 让各 AI 客户端共用同一份 skills（一份物理文件、多入口）
# 脚本自带保护：遇到真实目录先备份、遇到「独有 skill」默认跳过，不会丢东西。
$syncScript = "$temp/scripts/sync-skills-links.py"
if (Test-Path $syncScript) {
    $pyExe = (Get-Command python -ErrorAction SilentlyContinue).Source
    if (-not $pyExe) { $pyExe = (Get-Command py -ErrorAction SilentlyContinue).Source }
    if ($pyExe) {
        Write-Host "🔗 统一各客户端 skills 指向..." -ForegroundColor Yellow
        & $pyExe $syncScript --apply
        if ($LASTEXITCODE -ne 0) {
            Write-Host "⚠️  skills 指向未全部完成（exit $LASTEXITCODE），可稍后手动重跑：" -ForegroundColor Yellow
            Write-Host "    python `"$syncScript`" --apply"
        }
    } else {
        Write-Host "⚠️  未找到 python，跳过 skills 指向统一（可手动跑 scripts/sync-skills-links.py）" -ForegroundColor Yellow
    }
}

Write-Host "✅ 配置同步完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📌 当前配置:" -ForegroundColor Cyan
Write-Host "   Shell: $($finalConfig.shell)"
Write-Host "   MCP: infra-ops + composio"
Write-Host ""
Write-Host "📌 启动 OpenCode:" -ForegroundColor Cyan
Write-Host "   opencode"
Write-Host ""
Write-Host "📌 首次使用 Composio 时会弹出浏览器认证" -ForegroundColor Yellow
