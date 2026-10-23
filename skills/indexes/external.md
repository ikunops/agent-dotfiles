# 外部本地依赖索引（Internal Node）

> 本页登记**不属于本仓库维护权**、但可能安装在本机的 skill。根入口为
> `../INDEX.md`；这些技能缺失不算仓库故障，重建方式必须可从本页追溯。
>
> 不要把外部件复制成仓库自有件，也不要直接改其 `SKILL.md`。需要定制时复制到
> 新目录、改名并作为自有 skill 登记。

## 外部 HyperFrames 视频族（本地依赖，不随仓库跟踪）

> **归属：上游开源件，不是本仓自有 skill。** 源 = [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)（Apache-2.0）；本机通过 WorkBuddy 安装。10 个 skill 协作，总入口必读。
> **约束：** 本目录被 `.gitignore` 排除，不提交、不改写；新机器需要时按上游方式安装，缺失不会导致仓库审计失败。

| skill | 一句话 | 什么时候用 |
|---|---|---|
| `hyperframes` | 总入口：任何做/改/渲染视频前先读，恢复项目状态、选工作流 | 视频/动画/动效素材的起点 |
| `hyperframes-core` | 合成契约：时序属性、轨道、子合成、确定性渲染 | 写合成 HTML 前必读 |
| `hyperframes-animation` | 动画知识库：原子运动、场景蓝图、转场 + 7 种运行时适配器 | 任何动画/运动设计 |
| `hyperframes-creative` | 非动画创意：配色、字体、旁白、节拍、frame 预设 | 风格/调性决策 |
| `hyperframes-cli` | CLI 开发环：init / render / publish / preview / doctor | 建站、渲染、发布 |
| `hyperframes-registry` | 检索并接入现成效果块（CRT、glitch、色差、胶片颗粒等） | 手写名状效果之前先查 |
| `hyperframes-keyframes` | 推拉镜头、Ken Burns、运镜、SVG morph | 镜头/关键帧 |
| `hyperframes-audio` | 混音：淡入淡出、ducking、人声压背景乐 | 音频已就位后 |
| `hyperframes-studio` | Studio 协作工作方式 | 人在回路的方案/变更讨论 |
| `media-use` | 媒体 OS：BGM/SFX/图标/配音/调色 LUT 解析与生成 | 素材就位 |

> 与 ⑧ 设计线的通用动画纪律互补：那条是跨框架纪律，这组是 HyperFrames 框架专用。
> 重建：用 WorkBuddy 重新安装 HyperFrames 插件/技能组；本仓不保存副本。

## 外部交付自检 skill（本地依赖，不随仓库跟踪）

| skill | 来源 | 说明 |
|---|---|---|
| `delivery-no-pseudoblock` | WorkBuddy 市场（`source=others`，`skillId=skill_2095070772061040640`） | 交付前 D1–D12 自检闸门。本机已安装，但**不是本仓自有**；`.gitignore` 排除，不进版本库。缺失不影响仓库审计。 |

> 重建：在 WorkBuddy 市场重新安装该 skill。若本仓需要自有交付门禁，应在本地自建并独立登记，不要直接改市场件。
