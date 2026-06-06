import { apiFetch, showToast, escapeHtml } from "./utils.js";

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

let catalogCategories = categories;
let appSearchTerm = "";

export function initAppUninstall() {
  renderAppCatalog();
  loadAppCatalog();

  const search = document.getElementById("app-uninstall-search");
  if (search) {
    search.addEventListener("input", () => {
      appSearchTerm = search.value.trim().toLowerCase();
      renderAppCatalog();
    });
  }
}

async function loadAppCatalog() {
  const res = await apiFetch("/api/app-uninstall/catalog", { silent: true });
  if (!res || !res.success) return;
  catalogCategories = res.data.categories || categories;
  updateCatalogStats(res.data.category_count, res.data.item_count);
  renderAppCatalog();
}

function updateCatalogStats(categoryCount, itemCount, matchCount) {
  const catEl = document.getElementById("app-catalog-category-count");
  const itemEl = document.getElementById("app-catalog-item-count");
  const matchEl = document.getElementById("app-catalog-match-count");
  if (catEl) catEl.textContent = categoryCount;
  if (itemEl) itemEl.textContent = itemCount;
  if (matchEl && matchCount != null) matchEl.textContent = matchCount;
}

function renderAppCatalog() {
  const container = document.getElementById("app-uninstall-grid");
  if (!container) return;
  container.textContent = "";

  const totalCategories = catalogCategories.length;
  const totalItems = catalogCategories.reduce((sum, cat) => sum + cat.items.length, 0);
  let matchCount = 0;

  catalogCategories.forEach(cat => {
    const filteredItems = cat.items.filter(item => {
      if (!appSearchTerm) return true;
      return item.label.toLowerCase().includes(appSearchTerm) || cat.title.toLowerCase().includes(appSearchTerm);
    });
    matchCount += filteredItems.length;
    if (filteredItems.length === 0) return;

    const section = document.createElement("div");
    section.className = "quick-category";

    const title = document.createElement("div");
    title.className = "quick-category-title";
    title.innerHTML = `${escapeHtml(cat.title)} <span class="module-count-pill">${filteredItems.length}</span>`;
    section.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "quick-grid";

    filteredItems.forEach(item => {
      const div = document.createElement("div");
      div.className = "quick-item";
      div.innerHTML = '<span class="icon">' + escapeHtml(item.icon) + '</span><span class="label">' + escapeHtml(item.label) + '</span>';
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

  updateCatalogStats(totalCategories, totalItems, matchCount);
  if (matchCount === 0) {
    container.innerHTML = '<div class="empty-hint">没有匹配的应用项</div>';
  }
}
