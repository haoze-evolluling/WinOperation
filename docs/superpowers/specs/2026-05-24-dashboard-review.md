# 概览仪表盘 — 代码审查记录

审查日期: 2026-05-24
涉及范围: dashboard.js, tab-dashboard-overview.css, _tab_dashboard.html, gpu_info.py, main.py

---

## 待修复问题

### P1 — Wi-Fi 子卡片被隐藏 + 网格留空

**文件**: `static/js/dashboard.js` — `loadDashboardWifiDetail()`

当无 Wi-Fi 连接时，`wifiSection.style.display = "none"` 隐藏了整个 Wi-Fi 子卡片。用户要求"不要隐藏卡片"。

**连锁影响**: `.net-grid` 列定义为 `42fr 29fr 29fr`，Wi-Fi 卡片隐藏后第二个 `29fr` 轨道变为空白，不会自动合并为 2 列。

**修复方向**: 移除 `display: none`，Wi-Fi 不连接时仅保持 `-` 占位值不变。

---

### P2 — API 失败时模板 `-` 占位符残留

**文件**: `templates/_tab_dashboard.html`

HTML 模板所有字段默认值写死 `-`。当 API 请求失败或超时，JS 不更新这些元素，导致 `-` 永远留在界面上。涉及字段：

| API 端点 | 影响字段 |
|---|---|
| `/api/network/status` | `dash-ip`, `dash-dns`, `dash-adapter`, `dash-online` |
| `/api/system/public-ip` | `dash-public-ip` |
| `/api/system/latency` | `dash-latency`, `dash-packet-loss` |
| `/api/system/gateway-delay` | `dash-gateway-delay` |
| `/api/system/battery` | `dash-battery-pct`, `dash-battery-status` |
| `/api/system/wifi-detail` | `dash-ssid`, `dash-signal-text` |

**修复方向**: 方案 A) 模板默认值改为空字符串；方案 B) 在 `fetchAll()` 完成后对所有未更新的字段清空。方案 A 更简单但首次加载闪白；方案 B 更稳妥。

---

### P3 — GPU 详情温度没有色阶标识

**文件**: `static/js/dashboard.js` — `loadDashboardGpuDetail()`

GPU 详情卡片中的温度以纯文本显示，不区分温度高低。CSS 已定义：

```css
.temp-value { color: var(--text); }
.temp-value.warm { color: var(--warning); }   /* >50°C */
.temp-value.hot { color: var(--deep-red); }   /* >70°C */
```

但 GPU 详情卡片中温度输出用的是普通 `gpu-stat-value` 类，未使用 `temp-value` 类及其变体。

对照：`loadDashboardTemps()` 中的 CPU/GPU 温度是有颜色的。

**修复方向**: 在温度单元格的 `<div class="gpu-stat-value">` 上根据 `g.temperature` 添加 `warm`/`hot` 类。

---

### P4 — GPU 2 列网格在移动端不折叠

**文件**: `static/css/tab-dashboard-overview.css`

`@media (max-width: 768px)` 中没有将 `.gpu-stat-grid` 切换为单列。小屏幕上 2 列格子（利用率、温度、显存等）拥挤难以阅读。

**修复方向**: 在 `@media (max-width: 768px)` 中添加：

```css
.gpu-stat-grid { grid-template-columns: 1fr; }
```

---

### P5 — GPU 无数据时卡片内容完全空白

**文件**: `static/js/dashboard.js` — `loadDashboardGpuDetail()`

当 `gpus.length === 0` 时，JS 设置 `body.textContent = ""`，卡片头"GPU 详情"保留但内容完全空白。用户可能困惑。

对比：API 失败（`!data.success`）时显示"无法获取 GPU 数据"。

**修复方向**: 无数据时显示一行浅色提示文字（如"未检测到 GPU"）。

---

## 已确认无问题的设计

### GPU 显存分离渲染
`vram_used` 和 `vram_total` 拆分为独立的两行。Intel WMI 只返回 total（不返回 used）时，仅渲染"总显存"行，"占用显存"行不渲染。这是用户明确要求的行为。

### 后端 gpu_info.py
- 降级链完整: GPUtil → nvidia-smi → WMI + typeperf
- 去重逻辑: 将已检测到的 NVIDIA GPU 名集合传入 `_wmi_non_nvidia_gpus()` 避免重复
- 异常捕获完备: 每个检测函数独立 try/except，任一失败自动降级
- 4GB cap 已在注释中标明

### 宽度填充修复
`.gpu-card-item { width: 100%; }` 已添加，解决了 `.card-body { align-items: flex-start }` 导致的内容左偏问题。

### 增量更新优化
`resourcesChanged()` 函数对比前后数据，CPU/内存/磁盘/进程无变化时跳过 DOM 更新，减少不必要的重排。

### 缓存系统
`saveDashboardCache()` / `renderDashboardCache()` 覆盖 texts/htmls/bars/props，localStorage 持久化。页面加载时先渲染缓存再请求新数据，减少白屏等待。

---

## 修改优先级建议

1. **P1 + P2** — 违反用户明确要求的行为，用户感知最强
2. **P3** — 小改动，提升温度信息的可读性
3. **P4** — 移动端适配，重要但非紧急
4. **P5** — 边际情况，体验优化
