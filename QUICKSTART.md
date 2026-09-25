# OpenCode 快速入门

## 你已经拥有了什么

- 23个 Skills（数据库、DevOps、开发流程等）
- 3个 Plugins（superpowers、skill-creator 等）
- 2个 MCP 服务器（92个基础设施工具 + 500+应用集成）

## 如何使用

### 日常使用

直接提问就行，LLM 会自动选择工具：

```
检查系统资源
Docker 容器状态
项目有没有安全漏洞
```

### 查看已安装的 Skills

在 OpenCode 中输入：

```
/skills
```

### 查看 MCP 工具

在终端运行：

```powershell
opencode mcp list
```

## 其他机器同步

```powershell
# 一键同步（需要先装 Node.js 和 OpenCode）
git clone https://github.com/ikunops/opencode-dotfiles.git $env:TEMP\oc-bootstrap
powershell -ExecutionPolicy Bypass -File $env:TEMP\oc-bootstrap\setup.ps1
```

脚本会把仓库**持久克隆到 `~/opencode-dotfiles`**，并把各 AI 客户端的 skills 目录都建成链接指向它
（物理上只有一份文件，改一处所有客户端生效）。

## 更新配置

```powershell
cd ~/opencode-dotfiles
git add .
git commit -m "更新xxx"
git push
```

## 常见问题

**Q: MCP 工具怎么用？**
A: 直接提问，LLM 自动调用。比如"检查系统内存"。

**Q: 怎么知道 MCP 加载成功了？**
A: 终端运行 `opencode mcp list`。

**Q: Skills 怎么用？**
A: LLM 会根据问题自动匹配，或在提问时加"用 xxx skill"。

**Q: Composio 怎么登录？**
A: 首次使用时浏览器会弹出 OAuth 认证页面。
