# HTML 模板解耦合设计

## 现状

WinMaster 是一个基于 Flask + Jinja2 的 Windows 系统管理工具，HTML 模板只有两个文件：

| 文件 | 行数 | 问题 |
|------|------|------|
| `templates/base.html` | 52 | 合理，作为外层框架 |
| `templates/dashboard.html` | 851 | 包含所有 tab 内容 + 导航 + 模态框，文件过大，维护困难 |

静态资源（CSS / JS）已经按功能拆分，本次不涉及。

## 目标

将 `dashboard.html` 按功能域拆分为多个独立的 Jinja2 模板文件，通过 `{% include %}` 组合，保持服务端渲染方式和 DOM 结构完全不变。

## 新文件结构

```
templates/
├── base.html                  # 不变
├── dashboard.html             # 缩为约 30 行，仅包含 extends 和 include
├── _topnav.html               # 顶部导航栏（从 dashboard.html 抽出）
├── _modals.html               # 退出确认模态框
├── _tab_dashboard.html        # 仪表盘 — 概览/系统/硬件/网络/GPU/电池卡片
├── _tab_system_status.html    # 系统状态 — 负载/进程
├── _tab_network.html          # 网络设置 — 适配器/WiFi/DNS
├── _tab_power.html            # 电源选项 — 电源方案/快速启动
├── _tab_shutdown.html         # 定时关机
├── _tab_quick.html            # 快捷设置
├── _tab_speedtest.html        # 网站测速
├── _tab_activation.html       # 系统激活（三步向导）
├── _tab_app_uninstall.html    # 应用卸载
├── _tab_update.html           # 延迟更新
└── _tab_win11.html            # Win11 优化
```

## 拆分规则

1. 每个 `<div id="tab-xxx" class="tab-content">...</div>` 抽取为单独文件 `_tab_xxx.html`
2. 导航 `<nav class="topnav">` 抽取为 `_topnav.html`
3. 退出模态框 `<div id="exit-modal">` 抽取为 `_modals.html`
4. `dashboard.html` 只保留框架结构 + `{% include %}` 调用
5. 所有 DOM ID 和层级结构不变，JS 代码不需要修改
6. CSS/JS 加载方式不变，仍通过 `base.html` 中的 `<link>` 和 `<script>` 引入

## 执行顺序

按风险从小到大依次执行，每拆一个就验证页面正常：

1. 抽出 `_modals.html`（最小、无依赖）
2. 抽出 `_topnav.html`
3. 逐个抽出 tab 文件（按功能独立性排序）：
   - 快捷设置（最稳定，内容最少）
   - 应用卸载
   - 延迟更新
   - Win11 优化
   - 电源选项
   - 定时关机
   - 系统状态
   - 网站测速
   - 网络设置
   - 系统激活（最复杂，有向导逻辑）
   - 仪表盘（最大，200+ 行）
4. 清理 `dashboard.html`，收尾验证

## 核心原则

- **不动 JS** — 所有 JS 通过 ID 绑定 DOM，保持 ID 不变即零改动
- **不动 CSS** — 结构不变，class 不变
- **不动路由** — 仍由 `/` 路由渲染 `dashboard.html`，Flask 后端不变
- **不动构建** — `build.py` 已经将整个 `templates/` 目录打包，新增文件自动包含

## 回滚方案

- 每个拆分步骤独立成单独的 git commit
- 如果某步出错，git revert 该 commit 即可
