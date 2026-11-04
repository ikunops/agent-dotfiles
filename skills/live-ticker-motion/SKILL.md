---
name: live-ticker-motion
description: 实时金钱/计数器跳动的唯一实现路线——"亚秒级精度 + rAF 逐帧驱动"（Sub-second Precision + rAF Frame-Driven Ticker）。当需求里出现「数字一直在跳」「别一跳一跳的」「要像计价器/油表那样连续滚动」「秒表/工资/余额/收益实时增长」「第 N 位小数在动」时使用。含反模式（setInterval 一秒一跳）、精度根因、Web/Flutter/Android 三端实现骨架、断流时段的零重建处理。
---

# 实时数字跳动：亚秒级精度 + rAF 逐帧驱动

> **一句话**：数字看起来「在跳」还是「在闪」，只由两件事决定——**时间精度**和**渲染帧率**。
> 缺一个就失败：精度不够 = 一秒一跳；帧率不够 = 卡顿/停顿感。

## 名字与触发词

| 形式 | 说法 |
|---|---|
| 中文正式名 | **亚秒级精度 + rAF 逐帧驱动** |
| 英文正式名 | **Sub-second Precision + rAF Frame-Driven Ticker** |
| 也常被叫 | 毫秒级连续计价、live ticker、odometer ticker、油表式跳动 |
| 触发词 | 「数字一直在跳」「别一跳一跳」「连续滚动」「计价器」「油表」「实时增长」「第 4 位小数在动」「不要有停顿感」「金钱跳动」 |

**AI 读到名字后的固定实现路线**（不许自创）：
1. 时间源必须带**毫秒小数**（亚秒级）
2. 渲染必须由**逐帧回调**驱动（rAF / Ticker），不是定时器
3. 金额 = 速率 × 带小数的累计秒数
4. 只让**数字那一个叶子节点**重建，页面其余部分低频刷新

## 根因：为什么一秒一跳

```js
// ❌ 反模式：setInterval 1000ms + 整数秒
setInterval(() => { earned += perSecond; render(earned); }, 1000);
```
- 时间精度被截断成整秒 → 每 1 秒才变一次
- 视觉是「闪一下」，不是「滚动」
- 用户原话就是「你不觉得这样很怪吗」

```js
// ✅ 正确：亚秒精度 + rAF
const perSecond = 0.01323;
const t0 = performance.now();
const startSec = 24356;           // 已累计的秒（可含小数）
function frame(now) {
  const secs = startSec + (now - t0) / 1000;   // 带毫秒小数
  el.textContent = (perSecond * secs).toFixed(4);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```
每帧（~16.7ms）金额增长 `0.01323 × 0.0167 ≈ 0.00022`，第 4 位小数每帧都变 → 连续滚动。

## 精度：秒数必须带小数

**Web / Dart / Kotlin 同一条公式**：

```
secOfDay = hour*3600 + minute*60 + second + millisecond/1000
```

⚠️ 最高频的移植 bug：把 `secOfDay` 或「已计薪秒数」**截断成整数**。
一旦 `toInt()` / `Math.floor()`，即使帧率 60fps，金额也只会一秒跳一下——
此时你会误以为是帧率问题，其实是精度问题。**两个都要查。**

## 三端实现骨架

### Web
```js
requestAnimationFrame(frame)          // 驱动
performance.now()                     // 时间源（不要用 Date.now 的秒级）
el.textContent = ...                  // 只写文本节点，不重排 DOM
```
- 数字节点用 `font-variant-numeric: tabular-nums`，否则字宽变化会让整行抖动
- 不要每帧 `innerHTML`，不要每帧读写 `offsetHeight` 等触发强制同步布局的属性

### Flutter
```dart
// ✅ 用 Ticker（vsync 驱动），不要 Timer.periodic(100ms)
Ticker((_) => tick())..start();

// ✅ 金额单独用 ValueListenableBuilder，只重建那一小块
final heroValue = ValueNotifier<double>(0);
ValueListenableBuilder<double>(
  valueListenable: heroValue,
  builder: (_, v, __) => Text(fmtMoney(v, 4)),
)
```
**关键架构约束（血的教训）**：
- ❌ Ticker 每帧 `notifyListeners()` → 整页重建 → 模拟器/低端机掉帧 → 用户说「有停顿感」
- ✅ Ticker 只更新 `ValueNotifier<double>`；页面其余部分（时钟/徽标/进度条）**降到 4Hz 或事件驱动**
- ValueNotifier 在值不变时自动跳过通知，非计薪时段（下班/休息日）自动零重建

### Android 原生（通知 / Widget）
- 通知：系统限制，最低刷新间隔约 1 分钟（`Handler.postDelayed(60_000)`）。**做不到逐秒**
- Widget：`updatePeriodMillis` 最低 30 分钟；用 `AlarmManager` 可压到 1 分钟，**仍做不到秒级**
- 结论：**秒级跳动只能发生在应用内**。通知/小组件只能做「分钟级 + 亮屏/进桌面时立即刷新」的近似
- 若必须让 widget 看起来在动：只能做「渐变/呼吸」等 CSS 式动画（RemoteViews 支持有限），不能改数字

## 其它必须一起做对的事

| 项 | 要求 | 原因 |
|---|---|---|
| 数字字体 | `tabular-nums` / `FontFeature.tabularFigures()` | 等宽，否则每帧宽度变化导致抖动 |
| 重建范围 | 只重建数字叶子节点 | 全树重建必然掉帧 |
| 后台行为 | 切后台停帧（Ticker 自动停；rAF 浏览器自动停） | 省电，且避免累计时间错乱 |
| 累计跳变 | 两次采样间隔 > 60s 视为异常，跳过累加 | 休眠/切后台回来时不要一次补一大笔 |
| 精度展示 | 小数位可配（0/2/3/4），默认 4 | 4 位才能看出「连续滚动」；0 位时本来就只能一跳一跳 |
| 冻结态 | 非计薪时段值不变 → 不推送 | 省电、避免无意义重建 |

## 自检清单（交付前必过）

- [ ] 画面里的数字，**同一位小数在 1 秒内至少变化 3 次**？（4 位小数应每帧都变）
- [ ] 代码里没有 `setInterval(..., 1000)` 驱动金额？
- [ ] 秒数计算里没有 `toInt()` / `Math.floor()` 截断？
- [ ] Flutter 侧：Ticker 没有触发整页 `notifyListeners()`？
- [ ] 数字节点用了 tabular figures？
- [ ] 切后台再回来，金额没有暴涨？

## 反例库（真实踩过）

1. **Flutter 首版**：`Timer.periodic(100ms)` + 整页 rebuild → 用户「数字有停顿感」
2. **Flutter 二版**：改成 60fps Ticker 但整页重建 → 仍然停顿（重建量太大）
3. **Flutter 三版**：Ticker + 金额独立 ValueNotifier + 页面 4Hz → 流畅
4. **精度 bug**：移植时把 `secOfDay` 截成整数 → 一秒一跳，用户说「不是这个效果」
5. **预览稿 bug**：设计稿里用 `setInterval(1000)` → 用户一眼看出「数字滚动效果怎么变了」
