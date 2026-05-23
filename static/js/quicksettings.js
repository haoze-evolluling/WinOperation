import { apiFetch, showToast } from "./utils.js";

const categories = [
  {
    title: "系统核心配置",
    items: [
      { id: "control_panel", icon: "\u2699", label: "控制面板" },
      { id: "local_group_policy", icon: "\uD83D\uDCCB", label: "本地组策略编辑器" },
      { id: "msconfig", icon: "\u26A1", label: "系统配置 (msconfig)" },
    ],
  },
  {
    title: "硬件与磁盘管理",
    items: [
      { id: "device_manager", icon: "\uD83D\uDDA5", label: "设备管理器" },
      { id: "disk_management", icon: "\uD83D\uDCBE", label: "磁盘管理" },
      { id: "dxdiag", icon: "\uD83C\uDFAE", label: "DirectX 诊断工具" },
      { id: "system_info", icon: "\u2139", label: "系统信息 (msinfo32)" },
    ],
  },
  {
    title: "网络与远程管理",
    items: [
      { id: "network_connections", icon: "\uD83C\uDF10", label: "网络连接" },
      { id: "network_sharing_center", icon: "\uD83C\uDF0D", label: "网络和共享中心" },
      { id: "remote_desktop", icon: "\uD83D\uDDBB", label: "远程桌面连接" },
      { id: "resource_monitor", icon: "\uD83D\uDCC8", label: "资源监视器" },
    ],
  },
  {
    title: "系统状态与监控",
    items: [
      { id: "task_manager", icon: "\uD83D\uDCCA", label: "任务管理器" },
      { id: "event_viewer", icon: "\uD83D\uDCCB", label: "事件查看器" },
      { id: "perfmon", icon: "\uD83D\uDCC8", label: "性能监视器 (perfmon)" },
    ],
  },
  {
    title: "更新与应用管理",
    items: [
      { id: "windows_update", icon: "\uD83D\uDD04", label: "Windows 更新" },
      { id: "apps_features", icon: "\uD83D\uDCE6", label: "应用和功能" },
      { id: "programs_features", icon: "\uD83D\uDCC0", label: "程序和功能 (旧版卸载)" },
    ],
  },
  {
    title: "电源与显示设置",
    items: [
      { id: "power_options", icon: "\uD83D\uDD0B", label: "电源选项" },
      { id: "display_settings", icon: "\uD83D\uDDA5", label: "显示设置" },
      { id: "mouse_keyboard", icon: "\uD83D\uDDB1", label: "鼠标/键盘设置" },
    ],
  },
  {
    title: "系统维护与安全",
    items: [
      { id: "system_properties", icon: "\u2139", label: "系统属性" },
      { id: "firewall", icon: "\uD83D\uDEE1", label: "防火墙" },
      { id: "windows_security", icon: "\uD83D\uDEE1", label: "Windows 安全中心" },
      { id: "registry_editor", icon: "\uD83D\uDCDD", label: "注册表编辑器" },
      { id: "services", icon: "\u2699", label: "服务" },
      { id: "computer_management", icon: "\uD83D\uDDA5", label: "计算机管理" },
      { id: "user_accounts", icon: "\uD83D\uDC64", label: "用户账户" },
      { id: "disk_cleanup", icon: "\uD83D\uDDD1", label: "磁盘清理" },
      { id: "defrag", icon: "\uD83D\uDCBF", label: "碎片整理和优化驱动器" },
      { id: "system_restore", icon: "\u23EA", label: "系统还原" },
      { id: "credential_manager", icon: "\uD83D\uDD11", label: "凭据管理器" },
    ],
  },
  {
    title: "命令与快捷工具",
    items: [
      { id: "cmd_prompt", icon: "\u2328", label: "命令提示符 (CMD)" },
      { id: "powershell", icon: "\uD83D\uDCBB", label: "PowerShell" },
    ],
  },
];

export function initQuickSettings() {
  const container = document.getElementById("quick-grid");
  if (!container) return;
  container.textContent = "";

  categories.forEach(cat => {
    const section = document.createElement("div");
    section.className = "quick-category";

    const title = document.createElement("div");
    title.className = "quick-category-title";
    title.textContent = cat.title;
    section.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "quick-grid";

    cat.items.forEach(cmd => {
      const div = document.createElement("div");
      div.className = "quick-item";
      div.innerHTML = '<span class="icon">' + cmd.icon + '</span><span class="label">' + cmd.label + '</span>';
      div.addEventListener("click", async () => {
        const res = await apiFetch("/api/quick/launch", { method: "POST", body: JSON.stringify({ command_id: cmd.id }) });
        if (res) showToast(res.message, res.success ? "success" : "error");
      });
      grid.appendChild(div);
    });

    section.appendChild(grid);
    container.appendChild(section);
  });
}
