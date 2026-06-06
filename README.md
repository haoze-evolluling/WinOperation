<div align="center">

# 🖥️ WinOperation — 本地系统管理工具

<img src="static/logo.png" width="120" alt="WinOperation Logo" />

**一站式 Windows 系统监控、优化与配置管理平台**

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite)
![PyInstaller](https://img.shields.io/badge/Build-PyInstaller-green)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)

</div>

---

## 📋 目录

- [项目简介](#-项目简介)
- [功能总览](#-功能总览)
- [界面预览](#-界面预览)
- [技术架构](#-技术架构)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
- [构建与打包](#-构建与打包)
- [认证系统](#-认证系统)
- [API 概览](#-api-概览)
- [常见问题](#-常见问题)
- [更新日志](#-更新日志)

---

## 📖 项目简介

**WinOperation** 是一款面向 Windows 系统的本地 Web 管理工具，采用 **Python Flask** 构建后端，通过浏览器提供图形化管理界面，实现对 Windows 系统的全方位监控与配置管理。

**核心理念：** 无需安装繁琐的管理软件，打开浏览器即可完成此前需要多个系统工具才能完成的操作——从硬件监控、网络诊断到系统激活、更新管理，一切尽在掌握。

**适用场景：**
- IT 运维人员的日常系统巡检与维护
- 个人用户的系统深度优化与个性化配置
- Windows 11 系统调优与兼容性设置
- 批量网站延迟测试与网络质量评估

> ⚠️ **权限说明：** WinOperation 需要管理员权限运行，以执行系统级别的操作（如修改注册表、电源方案切换、系统激活等）。程序启动时会自动请求提权。

---

### 核心特性一览

| 特性 | 说明 |
|------|------|
| **零依赖安装** | Python Flask 轻量后端，单页 Web 界面，浏览器即可访问 |
| **全栈 PowerShell 驱动** | 通过 WMI/CIM、注册表、系统命令实现对 Windows 的深度操控 |
| **本地优先** | 绑定 `127.0.0.1`，仅本地访问，不依赖外网服务 |
| **深色/浅色双主题** | CSS Custom Properties 驱动的「清爽浅色」与「暗夜科技」双主题 |
| **Glassmorphism 设计** | 毛玻璃效果卡片、模糊背景、平滑动画 |
| **响应式布局** | 适配桌面与移动端，侧边栏在窄屏自动折叠为横向滚动 |
| **数据缓存** | 仪表盘数据缓存至 localStorage，切换页面不重复加载 |
| **智能 DOM 更新** | 仅在数据发生变化时刷新界面，减少不必要的渲染 |
| **并发数据加载** | 使用 `Promise.allSettled` 并行获取多个 API 数据 |
| **管理员自动提权** | 启动时检测权限，非管理员状态自动通过 UAC 提权 |
| **单文件打包** | 支持 PyInstaller 打包为独立 EXE，免 Python 环境运行 |

---

## ✨ 功能总览

### 🏠 首页

- **实时数字时钟** — 动态显示当前时间，每秒刷新，支持时/分/秒、年/月/日/星期的完整时间展示
- **功能快捷搜索** — 首页正中提供搜索框，输入关键词即可快速搜索和跳转到全部 12 个功能模块
  - 支持中文名称、英文名称、功能关键词多维度匹配
  - 键盘上下键导航 + Enter 跳转
  - 点击外部区域或 Escape 键关闭

### 📊 仪表盘

- **系统信息** — 操作系统版本、计算机名、运行时长、启动时间、登录用户、系统架构
- **硬件信息** — 处理器型号、显卡列表、内存容量与使用率、存储空间与使用率
- **网络信息** — 内网 IP、公网 IP（通过 ipify / ip.sb 获取）、联网状态、WiFi SSID 与信号强度、网络延迟与丢包率
- **GPU 详情** — NVIDIA GPU 利用率、显存使用量、温度、驱动版本（通过 `nvidia-smi`）
- **电池信息** — 电池剩余电量、充电状态（笔记本）
- **温度监控** — CPU/GPU 温度（需安装 [OpenHardwareMonitor](https://openhardwaremonitor.org/)）
- **刷新按钮** — 点击刷新按钮（带旋转动画）手动重新拉取所有数据
- **智能数据缓存** — 8 个 API 的数据通过 `Promise.allSettled` 并发拉取，结果缓存到 localStorage，再次进入仪表盘时优先展示缓存内容
- **变更检测** — 数据对比机制：仅当 CPU/内存/磁盘/进程数据发生有意义的变化时才更新 DOM，减少不必要的重渲染

### 📈 系统状态（实时监控）

- **系统负载** — CPU、内存、虚拟内存、存储使用率的实时进度条（带颜色分级：<50% 绿色 / 50-80% 橙色 / >80% 红色）
- **进程监控** — Top 5 CPU 占用进程列表（进程名 + PID + CPU 占用率 + 内存占用），每 5 秒自动刷新
  - 每个进程附带 CPU 和内存的迷你进度条，直观展示资源占用
  - 数据变更检测：仅在有意义的变化时才更新表格，避免闪烁

### 🌐 网络设置

- **网络适配器** — 通过 `Get-NetAdapter` / `Get-NetIPConfiguration` 查看所有网卡状态、IP 地址、网关、DNS 服务器
  - 加载时带有**自适应进度条动画**（基于 `0.65^t` 衰减曲线模拟加载进度，最少展示 1.5 秒）
  - 选择不同适配器可查看其详细信息和状态
- **WiFi 控制** — 一键启用/禁用无线网卡（通过 `Enable-NetAdapter` / `Disable-NetAdapter`）
- **DNS 配置** — 完整的 DNS 管理功能：
  - 支持 **IPv4/IPv6 协议切换**，切换时自动匹配对应协议的 DNS 预设
  - 内置国内外主流 DNS 提供商一键填充：

  | DNS 提供商 | IPv4 | IPv6 |
  |-----------|------|------|
  | 🇨🇳 阿里 DNS | 223.5.5.5 / 223.6.6.6 | 2400:3200::1 / 2400:3200:baba::1 |
  | 🇨🇳 114DNS | 114.114.114.114 / 114.114.115.115 | 240c::6666 / 240c::6644 |
  | 🇨🇳 腾讯 DNSPod | 119.29.29.29 / 119.28.28.28 | 2402:4e00:: / 2402:4e00:1:: |
  | 🇨🇳 百度 DNS | 180.76.76.76 / 180.76.77.77 | 2400:da00::6666 |
  | 🌍 Google DNS | 8.8.8.8 / 8.8.4.4 | 2001:4860:4860::8888 / 2001:4860:4860::8844 |
  | 🌍 Cloudflare | 1.1.1.1 / 1.0.0.1 | 2606:4700:4700::1111 / 2606:4700:4700::1001 |
  | 🌍 Quad9 | 9.9.9.9 / 149.112.112.112 | 2620:fe::fe / 2620:fe::9 |

  - 手动输入自定义 DNS，支持双框输入（首选/备用）
  - 一键恢复「自动获取 DNS」（`Set-DnsClientServerAddress -ResetServerAddresses`）
  - **IP 地址格式校验**：严格的 IPv4/IPv6 格式验证
- **DNS 缓存** — 一键清除 DNS 缓存（`ipconfig /flushdns`）

### ⏱ 网站测速

- **批量测速** — 同时对 20 个国内网站 + 20 个国外网站执行 Ping 测试
  - 🇨🇳 百度、腾讯、淘宝、京东、新浪、搜狐、网易、天猫、B站、微博、知乎、CSDN、阿里云、小米、华为、美团、抖音、豆瓣、爱奇艺、携程
  - 🌍 Google、YouTube、Facebook、Twitter/X、Instagram、LinkedIn、GitHub、StackOverflow、Reddit、Wikipedia、Amazon、Microsoft、Apple、Netflix、Cloudflare、Docker、Python、Nginx、Apache、Figma
- **并发测试** — 使用 Python `ThreadPoolExecutor(max_workers=10)` 并发执行 Ping，快速出结果
- **区域过滤** — 支持「全部 / 国内网站 / 国外网站」三类视图筛选，前端即时过滤展示
- **结果详情** — 每个站点显示：IP 地址、最小/平均/最大延迟（ms）、丢包率、状态（正常/部分丢包/超时/解析失败）
- **自定义测试** — 对任意域名或 IP 执行 Ping 或 Nslookup 诊断：
  - **Ping**：发送 4 个包，展示延迟分级（低 <50ms / 中 <150ms / 高 ≥150ms）和丢包分级
  - **Nslookup**：智能解析 DNS 服务器和解析结果，自动识别 IPv4/IPv6 地址，支持超时和解析失败友好提示

### 🔌 电源选项

- **电源方案切换** — 查看和切换 Windows 电源计划（高性能/平衡/节能等）
- **快速启动** — 启用或禁用 Windows 快速启动（休眠功能）

### ⏰ 定时关机

- **倒计时关机** — 设置小时 + 分钟组合的倒计时（最少 1 分钟），通过 `shutdown /s /t` 命令执行
- **指定时间关机** — 设置具体时间点（HH:MM），自动计算剩余秒数，跨天支持（若设定时间已过则顺延至次日）
- **取消关机** — 随时取消已设置的关机任务（`shutdown /a`）
- **重复计划** — 通过 Windows 任务计划程序（`schtasks` / `Register-ScheduledTask`）创建每周定时关机计划
  - 支持任意组合的星期选择，指定具体时间
  - 已创建的计划列表展示，支持单个删除
- **实时倒计时** — 设置后页面显示实时倒计时（时:分:秒），每秒更新

### ⚡ 快捷设置

内置 8 大分类、30+ 常用 Windows 系统工具快捷入口，单击即达（通过 `cmd /c` 启动对应命令）：

| 分类 | 工具 |
|------|------|
| ⚙️ 系统核心配置 | 控制面板 (`control`)、本地组策略编辑器 (`gpedit.msc`)、系统配置 (`msconfig`) |
| 💾 硬件与磁盘管理 | 设备管理器 (`devmgmt.msc`)、磁盘管理 (`diskmgmt.msc`)、DirectX 诊断工具 (`dxdiag`)、系统信息 (`msinfo32`) |
| 🌐 网络与远程管理 | 网络连接 (`ncpa.cpl`)、网络和共享中心、远程桌面 (`mstsc`)、资源监视器 (`resmon`) |
| 📊 系统状态与监控 | 任务管理器 (`taskmgr`)、事件查看器 (`eventvwr.msc`)、性能监视器 (`perfmon`) |
| 🔄 更新与应用管理 | Windows 更新、应用和功能、程序和功能 (`appwiz.cpl`) |
| 🖥 电源显示与个性化 | 电源选项 (`powercfg.cpl`)、显示设置、个性化设置、鼠标/键盘设置 |
| 🔒 系统维护与安全 | 系统属性 (`sysdm.cpl`)、防火墙 (`wf.msc`)、Windows 安全中心、注册表编辑器 (`regedit`)、服务 (`services.msc`)、计算机管理 (`compmgmt.msc`)、用户账户 (`netplwiz`)、磁盘清理 (`cleanmgr`)、碎片整理 (`dfrgui`)、系统还原 (`rstrui`)、凭据管理器 |
| ⌨️ 命令与快捷工具 | 命令提示符 CMD (`start cmd`)、PowerShell (`start powershell`) |

### 🔑 系统激活

- **KMS 激活** — 通过 KMS 服务器激活 Windows，使用 `slmgr.vbs` 脚本
- **三步流程**：`slmgr /ipk` 安装 GVLK 密钥 → `slmgr /skms` 设置 KMS 服务器 → `slmgr /ato` 执行激活，最后 `slmgr /xpr` 查询激活状态
- **详细步骤输出** — 每步执行结果（含标准输出和错误输出）完整展示，带 ✓/✗ 图标标识
- **内置 GVLK 密钥库** — 覆盖 Win11、Win10、Win8.1、Win8 的多个版本：

| 分类 | 版本 |
|------|------|
| Win11 | 专业版、家庭版、专业工作站版、企业版、教育版 |
| Win10 | 专业版、家庭版、专业工作站版、企业版、教育版 |
| Win8.1 | 专业版、企业版、核心版 |
| Win8 | 专业版、企业版 |

- **内置 KMS 服务器列表** — 6 个可用服务器一键选择：`kms.03k.org`、`kms.cgtsoft.com`、`kms.moeyuuko.com`、`kms.loli.best`、`kms.sixyin.com`、`kms.loli.beer`

### 🎨 个性化

- **桌面背景** — 内置多张高清壁纸（`login-1.png` ~ `login-4.png`），单击即可设置为桌面背景
  - **双路径设置**：优先使用 PowerShell 设置壁纸，失败时自动回退到 ctypes Win32 API `SystemParametersInfoW`
  - **预览即时生效**：点击壁纸缩略图后，先预加载图片，然后立即切换背景，同时请求后端持久化
  - **本地缓存**：当前壁纸名存储到 localStorage，刷新页面后自动恢复
  - **Service Worker 缓存**：壁纸图片通过 Cache API 缓存，支持离线展示
- **深色主题** — 内置「暗夜科技」深色主题，沉浸式深色 UI
  - **CSS Custom Properties 驱动**：所有颜色变量集中管理
  - **平滑过渡动画**：主题应用使用 `requestAnimationFrame` 双缓冲，避免闪烁
  - **登录页同步**：登录和注册页面同样应用深色主题

### 🗑 应用卸载

- **一键卸载** — 通过 `Get-AppxPackage | Remove-AppxPackage` PowerShell 命令卸载 Windows 系统自带应用
- **分类展示** — 7 大分类，30+ 可卸载应用，单击后确认即执行
- **卸载确认机制** — 每次卸载前弹出确认对话框，防止误操作
- **支持的内置应用分类：**

| 分类 | 应用 |
|------|------|
| 🎮 娱乐与社交类 | Xbox 全部组件、Skype、纸牌游戏集合、你的手机、人脉 |
| 🎬 媒体与创作类 | 电影和电视、Groove 音乐、3D 建模/打印、照片查看器、混合现实门户 |
| 📰 新闻与工具类 | 必应天气、必应新闻、Windows 地图、OneNote (UWP)、反馈中心、邮件和日历、计算器 |
| ⏰ 日常工具类 | 闹钟和时钟、相机、录音机、便签、截图和草图 |
| 💡 帮助与说明类 | 提示 (Tips)、获取帮助、Office 助手 |
| 🖼 媒体扩展类 | HEIF 图像扩展、Web 媒体扩展、VP9 视频扩展 |
| 🎶 第三方推广类 | Spotify、Disney+、消息 (Messaging) |

### ⟳ 延迟更新

- **终极暂停** — 将 Windows 更新推迟 10,000 天（约 27 年），通过修改注册表 `PauseUpdatesExpiryTime` 实现
- **多重防护机制**：
  - 注册表策略：设置 `NoAutoUpdate = 1`、`AUOptions = 2`、`FlightSettingsMaxPauseDays = 10000`
  - 服务禁用：同时禁用并停止三个更新服务——`wuauserv`（Windows Update）、`UsoSvc`（更新 Orchestrator）、`bits`（后台智能传输）
- **一键还原** — 清除所有修改的注册表项，重新启用三个更新服务并设为自动启动
- **状态可视化** — 首页显示当前暂停状态和到期时间（已转换为本地时区）

### ⊞ Win11 优化专区

专门针对 Windows 11 系统优化和个性化调整的功能集合：

| 功能 | 技术原理 | 说明 |
|------|----------|------|
| 经典右键菜单 | 注册表 `HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32` | 恢复 Windows 10 完整右键菜单，避免 Win11 二级菜单延迟。启用/禁用开关即时切换 |
| 任务栏左对齐 | 注册表 `TaskbarAl` 值设置 | 将任务栏图标改为左对齐（Windows 10 风格）或恢复居中对齐（Windows 11 默认） |
| 禁用搜索建议 | 注册表 `DisableSearchBoxSuggestions` 策略 | 禁止开始菜单联网搜索建议（Bing），仅搜索本地内容，提升搜索速度与隐私 |
| 重启资源管理器 | `Stop-Process -Name explorer -Force` | 修改注册表后一键重启 Explorer 使更改生效，无需手动注销 |

> ⚡ 所有 Win11 优化操作均通过注册表修改实现，改变即时写入，重启 Explorer 后完全生效。

---

### 🔄 全局后台刷新

WinOperation 内置一个**独立于 Tab 切换的 30 秒后台刷新机制**，确保关键页面数据保持最新：

- **工作方式**：页面加载完成后启动 30 秒定时器，根据当前所在 Tab 自动刷新对应数据
- **覆盖范围**：网络设置、电源选项、定时关机三个页面在激活期间自动保持数据更新
- **生命周期**：页面关闭或 Tab 切换时自动停止，释放资源

### 🔔 Toast 通知系统

- **三类状态通知**：成功（绿色）/ 错误（红色）/ 普通（默认）
- **自动消失**：3 秒后自动移除，不干扰操作
- **容器定位**：固定在页面右上角，支持多个通知堆叠

### 🚪 安全退出

- **退出确认弹窗**：点击「退出程序」按钮弹出毛玻璃确认对话框，带 fadeIn + scaleIn 动画
- **优雅退出流程**：确认后调用 API 退出后端进程，前端显示友好提示，自动关闭标签页
- **资源清理**：页面 `beforeunload` 时自动停止所有计时器和数据刷新

---

## 🖼 界面预览

| 登录页 | 仪表盘 |
|:---:|:---:|
| 快速登录 + 管理员登录弹窗 | 系统/硬件/网络/GPU/电池信息卡片 |
| **首页** | **系统状态** |
| 实时时钟 + 功能搜索 | CPU/内存/磁盘负载 + 进程列表 |
| **网络设置** | **网站测速** |
| 适配器管理 + DNS 预设 | 40 站点并发 Ping + 自定义诊断 |
| **电源管理** | **Win11 优化** |
| 电源方案 + 快速启动 | 右键菜单/任务栏/搜索/资源管理器 |

> WinOperation 支持 **深色/浅色** 双主题，通过个性化设置一键切换，全局生效。

---

## 🏗 技术架构

```
┌─────────────────────────────────────────────────┐
│                  Browser (SPA)                    │
│  ┌─────────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Vanilla JS  │  │  CSS3    │  │ localStorage│  │
│  │  (ES Modules)│  │  Grid/Flex│  │  缓存      │  │
│  └──────┬───────┘  └──────────┘  └────────────┘  │
└─────────┼─────────────────────────────────────────┘
          │  REST API (JSON)   127.0.0.1:2233
┌─────────┼─────────────────────────────────────────┐
│  ┌──────┴────────────────────────────────────────┐ │
│  │              Flask Web Server                  │ │
│  │  ┌──────────┐ ┌──────────┐ ┌────────────────┐ │ │
│  │  │ Flask 2.x │ │Flask-Login│ │ Flask-SQLAlchemy│ │
│  │  └──────────┘ └──────────┘ └────────────────┘ │ │
│  │           ┌────────────────────┐               │ │
│  │           │   SQLite (data/)   │               │ │
│  │           └────────────────────┘               │ │
│  └────────────────────┬───────────────────────────┘ │
│                       │                              │
│  ┌────────────────────┴───────────────────────────┐ │
│  │           PowerShell Subprocess                 │ │
│  │  ┌───────┐ ┌────────┐ ┌──────┐ ┌───────────┐  │ │
│  │  │ WMI   │ │Registry│ │power-│ │ netsh /    │  │ │
│  │  │ CIM   │ │        │ │ cfg  │ │ ipconfig   │  │ │
│  │  └───────┘ └────────┘ └──────┘ └───────────┘  │ │
│  │  ┌────────┐ ┌────────┐ ┌──────────────┐       │ │
│  │  │schtasks│ │ nvidia-│ │ slmgr.vbs /  │       │ │
│  │  │        │ │ smi    │ │ cscript      │       │ │
│  │  └────────┘ └────────┘ └──────────────┘       │ │
│  └────────────────────────────────────────────────┘ │
│                    Windows OS                        │
└─────────────────────────────────────────────────────┘
```

### 技术栈明细

| 层次 | 技术 | 用途 |
|------|------|------|
| **后端框架** | Flask 2.x | Web 服务器与 REST API |
| **认证授权** | Flask-Login + Session | 会话管理与用户认证 |
| **数据持久化** | Flask-SQLAlchemy + SQLite | 用户数据存储 (`data/app.db`) |
| **密码加密** | bcrypt | 用户密码哈希存储 |
| **系统交互** | PowerShell Subprocess | 调用 WMI/CIM、注册表、系统命令、计划任务 |
| **原生 API** | ctypes Win32 / nvidia-smi | 壁纸设置（后备方案）、GPU 详情查询 |
| **前端** | Vanilla JS (ES Modules) | 无框架单页应用，模块化组织 |
| **CSS 架构** | CSS Custom Properties + 模块化文件 | 26 个按功能拆分的 CSS 文件 |
| **主题系统** | CSS Custom Properties + `data-theme` 属性 | 双主题驱动，无需切换样式表 |
| **数据缓存** | Browser localStorage + Cache API | 仪表盘数据缓存 + 壁纸 Service Worker 缓存 |
| **并发处理** | Python ThreadPoolExecutor / JS Promise.allSettled | 批量 Ping 并发测试 + 前端并行数据加载 |
| **后台刷新** | setInterval (30s) | 网络/电源/关机页面定时自动刷新 |
| **打包分发** | PyInstaller (onefile) | 打包为独立 EXE |

### 设计特点

- **单页应用 (SPA)** — Tab 式页面切换，无刷新操作体验，支持 URL hash 历史记录
- **模块化前端** — ES Module 组织代码，12 个功能 Tab 各自独立初始化，首次访问时按需加载
- **Tab 生命周期管理** — 切换 Tab 时自动停止上一个 Tab 的定时器（如仪表盘轮询），释放资源
- **智能数据更新** — 仪表盘数据变更检测机制：仅在 CPU/内存/磁盘/进程数据发生有意义的变化时才更新 DOM
- **全局后台刷新** — 独立于 Tab 的 30 秒定时器（`startGlobalRefresh`），在查看网络/电源/关机页面时自动刷新数据
- **离线缓存** — 仪表盘数据缓存到 localStorage，切换页面不丢失；壁纸图片通过 Cache API 缓存
- **双层容错** — 壁纸设置同时实现 PowerShell 和 ctypes Win32 API 两种方式，自动回退
- **管理员提权** — 启动时自动检测并请求管理员权限，确保系统操作可用
- **端口绑定** — 固定使用 127.0.0.1:2233，仅本地访问，安全可控
- **自适应加载动画** — 网络数据加载时使用 `0.65^t` 衰减曲线模拟进度动画，最少展示 1.5 秒
- **主题联动** — 切换主题时自动同步切换配套壁纸，登录页/注册页/仪表盘统一风格

---

## 📁 项目结构

```
WinOperation/
├── main.py                  # 应用入口（薄层，委托 src/main.py）
├── build.py                 # PyInstaller 打包脚本
├── start.bat                # 启动脚本（自动提权）
├── requirements.txt         # Python 依赖
│
├── src/                     # Python 源码包
│   ├── main.py              #   应用工厂、系统 API、权限提升
│   ├── config.py            #   配置管理（密钥、数据库路径、资源路径）
│   ├── models.py            #   数据模型（User 表）
│   ├── auth.py              #   认证模块（登录/注册/快速登录）
│   ├── activation.py        #   Windows KMS 激活
│   ├── network.py           #   网络设置（适配器、WiFi、DNS）
│   ├── power.py             #   电源管理（方案切换、快速启动）
│   ├── scheduler.py         #   定时关机（倒计时、指定时间、重复计划）
│   ├── speedtest.py         #   网站测速（批量 Ping、Nslookup）
│   ├── quick_settings.py    #   快捷设置（30+ 系统工具快捷入口）
│   ├── update.py            #   Windows 更新管理（推迟/还原）
│   ├── app_uninstall.py     #   应用卸载
│   ├── win11.py             #   Win11 优化（右键菜单、任务栏、搜索）
│   ├── home.py              #   首页 API（时钟数据）
│   └── utils.py             #   工具函数（PowerShell 执行器）
│
├── templates/               # Jinja2 模板
│   ├── base.html            #   基础布局（主题预加载、通用组件）
│   ├── login.html           #   登录页
│   ├── register.html        #   注册页
│   └── dashboard.html       #   主仪表盘（所有 Tab 的定义）
│
├── static/                  # 静态资源
│   ├── css/                 #   样式系统（25 个模块化 CSS 文件）
│   │   ├── style.css                        # 样式总入口（@import 聚合 24 个子文件）
│   │   ├── theme-dark-overrides.css          # 深色主题 CSS 变量（70+ 规则）
│   │   ├── base-reset-typography.css         # CSS Reset 与排版基础
│   │   ├── layout-dashboard-sidebar.css      # Grid 布局 + 侧边栏样式 + 退出弹窗
│   │   ├── page-auth-login.css               # 登录/注册页样式
│   │   ├── components-buttons.css            # 按钮系统（primary/secondary/danger/warning）
│   │   ├── components-cards-info.css         # 卡片容器、统计信息、状态指示器
│   │   ├── components-toast.css              # Toast 通知（右上角弹出 + 自动消失）
│   │   ├── tab-dashboard-overview.css        # 仪表盘：进度条、进程表、温度、核心网格
│   │   ├── tab-home.css                      # 首页：时钟（5rem）、搜索框、建议列表
│   │   ├── tab-network-dns.css               # 网络适配器、WiFi 控制、DNS 预设按钮
│   │   ├── tab-power-schemes.css             # 电源方案下拉 + 快速启动状态
│   │   ├── tab-shutdown-scheduler.css         # 定时关机：倒计时显示、重复计划
│   │   ├── tab-quick-settings.css            # 快捷设置：分类网格布局
│   │   ├── tab-speedtest.css                 # 测速：进度条、表格、结果卡片
│   │   ├── tab-activation.css                # 激活：表单、版本按钮、步骤输出
│   │   ├── tab-app-uninstall.css             # 应用卸载：分类网格
│   │   ├── tab-win11.css                     # Win11 优化：开关切换、操作按钮
│   │   └── responsive-breakpoints.css        # 响应式断点（1024/768/480px）
│   ├── js/                  # JavaScript 模块（17 个 ES Module 文件）
│   │   ├── main.js          #   主入口：认证检测、Tab/模块初始化、退出弹窗
│   │   ├── tabs.js          #   Tab 生命周期管理（切换/初始化/停止）
│   │   ├── dashboard.js     #   仪表盘与系统状态（8 个 API + 数据缓存 + 变更检测）
│   │   ├── network.js       #   网络设置（适配器、WiFi、DNS 预设、IP 校验）
│   │   ├── power.js         #   电源管理（方案切换、快速启动）
│   │   ├── shutdown.js      #   定时关机（倒计时、指定时间、重复计划 CRUD）
│   │   ├── speedtest.js     #   网站测速（批量测速渲染、自定义 Ping/Nslookup）
│   │   ├── activation.js    #   系统激活（KMS 列表、GVLK 版本库、步骤展示）
│   │   ├── app_uninstall.js #   应用卸载（7 分类网格 + 确认对话框）
│   │   ├── update.js        #   更新管理（状态展示、推迟/还原操作）
│   │   ├── win11.js         #   Win11 优化（三开关状态同步、Explorer 重启）
│   │   ├── quicksettings.js #   快捷设置（8 分类 30+ 工具的网格渲染）
│   │   ├── home.js          #   首页（时钟 1s 定时器、模块搜索/键盘导航）
│   │   ├── auth.js          #   认证（登录检测、用户名展示、退出）
│   │   ├── global.js        #   全局后台刷新（30s 定时器管理）
│   │   └── utils.js         #   工具函数（apiFetch、DOM 操作、Cache API 封装）
│   ├── login-1.png ~ login-4.png  # 登录页背景图片（4 张）
│   └── logo.ico / logo.png       # 应用图标
│
├── data/                    # 运行时数据（SQLite DB、配置缓存）
│   └── app.db               #   用户数据库
│
├── dist/                    # PyInstaller 打包输出
│   └── WinOperation.exe        #   独立可执行文件
│
└── build/                   # PyInstaller 构建临时目录
```

---

## 🚀 快速开始

### 运行方式一：直接运行（开发调试）

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/WinOperation.git
cd WinOperation

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行（自动提权）
python main.py
```

### 运行方式二：启动脚本（推荐）

双击 `start.bat`，脚本会自动检测权限并提权，然后启动服务。

```batch
start.bat
```

### 运行方式三：打包后运行

```bash
# 构建
python build.py

# 运行
dist\WinOperation.exe
```

### 访问

浏览器自动打开 `http://127.0.0.1:2233`

---

## 🏗 构建与打包

### 使用构建脚本

```bash
python build.py
```

输出位置：`dist/WinOperation.exe`

### 使用 PyInstaller 直接打包

```bash
pip install pyinstaller
pyinstaller WinOperation.spec
```

### 构建参数说明

- `--onefile` — 打包为单个 EXE 文件
- `--windowed` — 无控制台窗口运行
- `--collect-all flask` — 收集 Flask 及其依赖
- 模板和静态文件自动包含在包内

---

## 🔐 认证系统

WinOperation 提供多层认证机制：

### 用户类型

| 类型 | 说明 |
|------|------|
| **内置管理员** | 预设的管理员账号，首次运行自动创建 |
| **游客** | 快速登录模式，无需密码，适合临时使用 |
| **注册用户** | 首次运行时注册，单用户模式 |

### 登录方式

1. **快速登录** — 点击「快速登录」按钮，直接以游客身份进入，无需密码
2. **管理员登录** — **点击页面标题「WinOperation」文字**弹出登录弹窗，输入内置账号或注册账号的密码
3. **用户注册** — 首次运行自动跳转到注册页，单用户注册模式（仅可注册一个自定义账号）

> 💡 **UX 细节：** 管理员登录入口隐藏在「点击标题弹出」的交互中，保持登录页简洁；游客可一键快速进入，需要管理操作时再通过标题弹窗登录。

### 安全机制

- 密码使用 bcrypt 哈希存储
- Session ID 使用随机 token
- Session Cookie 名称带随机后缀（`winoperation_session_` + 8 位随机 hex）
- 内置凭据在代码中经过轻度混淆（ASCII 偏移编码），防止直接明文暴露
- 未认证请求返回 401 JSON 响应
- 所有数据 API 均受 `@login_required` 保护
- 数据库文件存储在 `data/` 目录（已在 `.gitignore` 中排除）

---

## 📡 API 概览

### 系统信息

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/system/info` | 系统基本信息（OS、主机名、运行时长） |
| GET | `/api/system/hardware` | 硬件信息（CPU、GPU、频率） |
| GET | `/api/system/resources` | 资源使用率（CPU、RAM、磁盘、进程） |
| GET | `/api/system/public-ip` | 公网 IP 地址 |
| GET | `/api/system/gpu-detail` | GPU 详细信息（需 NVIDIA GPU） |
| GET | `/api/system/battery` | 电池信息 |
| GET | `/api/system/temps` | CPU/GPU 温度 |
| GET | `/api/system/wifi-detail` | WiFi 连接详情 |
| GET | `/api/system/latency` | 网络延迟与丢包率 |
| POST | `/api/system/exit` | 退出程序 |

### 认证

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/api/login` | 用户登录 |
| POST | `/api/register` | 用户注册 |
| POST | `/api/quick-login` | 快速登录（游客） |
| POST | `/api/logout` | 退出登录 |
| GET | `/api/check_auth` | 检查登录状态 |
| GET | `/api/check_first_run` | 检查是否首次运行 |

### 功能模块

| 模块 | 端点 | 说明 |
|------|------|------|
| 首页 | `/api/home/time` | 当前时间 |
| 网络 | `/api/network/status` | 网络状态 |
| 网络 | `/api/network/wifi` | WiFi 开关 |
| 网络 | `/api/network/dns` | DNS 设置 |
| 网络 | `/api/network/flushdns` | 清除 DNS 缓存 |
| 电源 | `/api/power/status` | 电源方案与快速启动状态 |
| 电源 | `/api/power/scheme` | 切换电源方案 |
| 电源 | `/api/power/faststartup` | 切换快速启动 |
| 定时关机 | `/api/shutdown/status` | 关机定时器状态 |
| 定时关机 | `/api/shutdown/timer` | 设置关机定时器 |
| 定时关机 | `/api/shutdown/cancel` | 取消关机 |
| 定时关机 | `/api/shutdown/schedule` | 创建重复计划 |
| 测速 | `/api/speedtest` | 批量网站测速 |
| 测速 | `/api/speedtest/custom` | 自定义 Ping/Nslookup |
| 快捷设置 | `/api/quick/launch` | 启动系统工具 |
| 激活 | `/api/activation/activate` | Windows 激活 |
| 更新 | `/api/update/status` | 更新暂停状态 |
| 更新 | `/api/update/delay` | 推迟更新 10000 天 |
| 更新 | `/api/update/restore` | 还原更新设置 |
| 应用卸载 | `/api/app-uninstall/uninstall` | 卸载应用 |
| Win11 | `/api/win11/classic-menu` | 经典右键菜单 |
| Win11 | `/api/win11/taskbar-align` | 任务栏对齐 |
| Win11 | `/api/win11/disable-search` | 搜索建议开关 |
| Win11 | `/api/win11/restart-explorer` | 重启资源管理器 |

> 除认证接口外，所有 API 均需登录认证（`@login_required`）。

---

## ❓ 常见问题

**Q：为什么需要管理员权限？**

WinOperation 需要执行系统级操作，如修改注册表（Win11 优化、更新策略）、切换电源方案、激活系统等，这些操作需要管理员权限。程序启动时会自动请求提权。

**Q：端口 2233 被占用怎么办？**

修改 `main.py` 中的端口号：
```python
app.run(host="127.0.0.1", port=2233, debug=False)
```

> ℹ️ 注意：`start.bat` 中提示的端口为 8080，但实际运行的端口以 `main.py` 中的配置为准（默认 2233）。启动后浏览器的自动打开地址取决于 `main.py` 中的配置。

**Q：是否可以远程访问？**

默认绑定 `127.0.0.1` 仅限本地访问。如需远程访问，请修改为 `0.0.0.0` 并自行配置防火墙规则和 HTTPS 加密。

**Q：数据存储在哪里？**

- 用户数据：`data/app.db`（SQLite 数据库）
- 前端缓存：浏览器 localStorage

**Q：温度监控不显示数据？**

CPU/GPU 温度需要安装 [OpenHardwareMonitor](https://openhardwaremonitor.org/) 并以其管理员模式运行。如未安装，温度显示为空白。

**Q：激活功能是否支持所有 Windows 版本？**

KMS 激活需要对应的 GVLK 密钥。内置的密钥库覆盖 Windows 10/11 的主流版本（专业版、企业版、教育版等）。请确保使用与您系统版本匹配的 GVLK 密钥。

**Q：如何完全卸载 WinOperation？**

删除 WinOperation 所在目录即可。如设置了定时关机计划，可在 WinOperation 中取消或通过 `schtasks.exe` 删除。

---

## 📜 更新日志

### v1.0.0 (2026-05)

- 🎉 初始版本发布
- 📊 仪表盘：系统信息、硬件信息、网络状态、GPU 详情、电池、温度
- 📈 系统状态：实时负载监控、进程列表自动刷新
- 🌐 网络设置：适配器管理、WiFi 控制、DNS 配置、缓存清理
- ⏱ 网站测速：40 站点批量 Ping、自定义 Nslookup 诊断
- 🔌 电源选项：方案切换、快速启动控制
- ⏰ 定时关机：倒计时、指定时间、重复计划
- ⚡ 快捷设置：30+ 系统工具快捷入口
- 🔑 系统激活：KMS 激活流程、多版本支持
- 🎨 个性化：壁纸设置、深色/浅色主题切换
- 🗑 应用卸载：一键移除内置应用
- ⟳ 延迟更新：暂停 10000 天、还原默认
- ⊞ Win11 优化：经典菜单、任务栏、搜索、Explorer 管理

---

<div align="center">

**WinOperation** — 让 Windows 管理更简单

Built with ❤️ using Python & Flask

</div>
