# superpowers 路由回归测试

三个脚本，验证技能路由链路的每一环。改 `plugin/superpowers.js` 或
`setup.ps1` 之后应当全部重跑。

```bash
node scripts/tests/test_bootstrap.js      # bootstrap 是否真的注入
node scripts/tests/test_portability.js    # 4 种目录布局是否都能解析
node scripts/tests/test_freshmachine.js   # 新机器模拟（复制到全新路径）
node scripts/tests/test_sync_classify.js  # 链接/系统目录分类（sync 脚本）
```

## 为什么需要这些测试

原 `superpowers.js` 用 `path.resolve(__dirname, '../../skills')` 猜路径。
plugin 在 `~/.config/opencode/plugin/`，上两级是 `~/.config/skills` ——
不存在。于是 `getBootstrapContent()` 每次返回 null，那段"你有技能库、动手前
先查"的路由提示**从未注入过**，模型的技能使用率因此一直偏低。

这个 bug 不会报错、不会打日志、不会让任何功能失败 —— 它只是让一个提示消失。
所以只能靠测试断言"bootstrap 不为 null"来守住。

## 各脚本断言什么

| 脚本 | 断言 |
|---|---|
| `test_bootstrap.js` | 解析出一个含路由技能的目录；内容同时出现 "skill" 与路由/L0-L1-L2/invoke 字样；打印模型实际收到的前几行 |
| `test_portability.js` | 4 种布局各自解析正确：`<configDir>/skills`、`~/.agents/skills`、`OPENCODE_SKILLS_DIR` 覆盖、全空时返回 null 而不抛异常。另有一条反向断言：旧逻辑在这些场景必然失败 |
| `test_freshmachine.js` | 把仓库复制到全新路径 + 全新用户名 + 新建 junction，解析正确、技能可读、路由技能可读 |

## 注意

`test_freshmachine.js` 会往 `%TEMP%` 写一份仓库副本，跑完可以删。
它不碰真实的 `~/.config` 和真实仓库。

三份脚本里的 resolver 是**故意复制**的，不是 import —— 这样测试能独立运行，
不依赖 plugin 的模块格式（ESM）。代价是改 plugin 的解析逻辑时要同步这三处。
