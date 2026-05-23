import { apiFetch, showToast } from "./utils.js";

const categories = [
  {
    title: "娱乐与社交类",
    items: [
      { label: "Xbox 全部组件", icon: "🎮", command: "Get-AppxPackage *xbox* | Remove-AppxPackage" },
      { label: "Skype 客户端", icon: "📹", command: "Get-AppxPackage *skypeapp* | Remove-AppxPackage" },
      { label: "纸牌游戏集合", icon: "🃏", command: "Get-AppxPackage *solitairecollection* | Remove-AppxPackage" },
      { label: "您的手机", icon: "📱", command: "Get-AppxPackage *yourphone* | Remove-AppxPackage" },
      { label: "人脉", icon: "👥", command: "Get-AppxPackage *people* | Remove-AppxPackage" },
    ],
  },
  {
    title: "媒体与创作类",
    items: [
      { label: "电影和电视", icon: "🎬", command: "Get-AppxPackage *zunevideo* | Remove-AppxPackage" },
      { label: "Groove 音乐", icon: "🎧", command: "Get-AppxPackage *zunemusic* | Remove-AppxPackage" },
      { label: "3D 建模/打印相关", icon: "🧊", command: "Get-AppxPackage *3d* | Remove-AppxPackage" },
      { label: "照片查看器", icon: "🖼️", command: "Get-AppxPackage *photos* | Remove-AppxPackage" },
      { label: "混合现实门户", icon: "🥽", command: "Get-AppxPackage *mixedreality.portal* | Remove-AppxPackage" },
    ],
  },
  {
    title: "新闻与工具类",
    items: [
      { label: "必应天气", icon: "🌤️", command: "Get-AppxPackage *bingweather* | Remove-AppxPackage" },
      { label: "必应新闻", icon: "📰", command: "Get-AppxPackage *bingnews* | Remove-AppxPackage" },
      { label: "Windows 地图", icon: "🗺️", command: "Get-AppxPackage *windowsmaps* | Remove-AppxPackage" },
      { label: "OneNote (UWP版)", icon: "📓", command: "Get-AppxPackage *onenote* | Remove-AppxPackage" },
      { label: "反馈中心", icon: "💬", command: "Get-AppxPackage *feedbackhub* | Remove-AppxPackage" },
      { label: "邮件和日历", icon: "📧", command: "Get-AppxPackage *windowscommunicationsapps* | Remove-AppxPackage" },
      { label: "计算器 (慎点)", icon: "🧮", command: "Get-AppxPackage *windowscalculator* | Remove-AppxPackage" },
    ],
  },
  {
    title: "日常工具类",
    items: [
      { label: "闹钟和时钟", icon: "⏰", command: "Get-AppxPackage *windowsalarms* | Remove-AppxPackage" },
      { label: "相机", icon: "📷", command: "Get-AppxPackage *windowscamera* | Remove-AppxPackage" },
      { label: "录音机", icon: "🎙️", command: "Get-AppxPackage *soundrecorder* | Remove-AppxPackage" },
      { label: "便签 (Sticky Notes)", icon: "📝", command: "Get-AppxPackage *stickynotes* | Remove-AppxPackage" },
      { label: "截图和草图", icon: "✂️", command: "Get-AppxPackage *screensketch* | Remove-AppxPackage" },
    ],
  },
  {
    title: "帮助与说明类",
    items: [
      { label: "提示 (Tips)", icon: "💡", command: "Get-AppxPackage *getstarted* | Remove-AppxPackage" },
      { label: "获取帮助", icon: "❓", command: "Get-AppxPackage *gethelp* | Remove-AppxPackage" },
      { label: "Office 助手", icon: "📖", command: "Get-AppxPackage *officehub* | Remove-AppxPackage" },
    ],
  },
  {
    title: "媒体扩展与底层组件",
    items: [
      { label: "HEIF 图像扩展", icon: "🖼️", command: "Get-AppxPackage *heif* | Remove-AppxPackage" },
      { label: "Web 媒体扩展", icon: "🌐", command: "Get-AppxPackage *webmedia* | Remove-AppxPackage" },
      { label: "VP9 视频扩展", icon: "🎥", command: "Get-AppxPackage *vp9* | Remove-AppxPackage" },
    ],
  },
  {
    title: "第三方推广与社交",
    items: [
      { label: "Spotify", icon: "🎶", command: "Get-AppxPackage *spotify* | Remove-AppxPackage" },
      { label: "Disney+", icon: "🏰", command: "Get-AppxPackage *disney* | Remove-AppxPackage" },
      { label: "消息 (Messaging)", icon: "💬", command: "Get-AppxPackage *messaging* | Remove-AppxPackage" },
    ],
  },
];

export function initAppUninstall() {
  const container = document.getElementById("app-uninstall-grid");
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

    cat.items.forEach(item => {
      const div = document.createElement("div");
      div.className = "quick-item";
      div.innerHTML = '<span class="icon">' + item.icon + '</span><span class="label">' + item.label + '</span>';
      div.addEventListener("click", async () => {
        if (!confirm(`确定要卸载「${item.label}」吗？`)) return;
        div.classList.add("loading");
        const res = await apiFetch("/api/app-uninstall/uninstall", {
          method: "POST",
          body: JSON.stringify({ command: item.command, label: item.label }),
        });
        div.classList.remove("loading");
        if (res) showToast(res.message, res.success ? "success" : "error");
      });
      grid.appendChild(div);
    });

    section.appendChild(grid);
    container.appendChild(section);
  });
}