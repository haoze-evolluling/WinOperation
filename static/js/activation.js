import { apiFetch, showToast, escapeHtml } from "./utils.js";

const KMS_SERVERS = [
  "kms.03k.org",
  "kms.cgtsoft.com",
  "kms.moeyuuko.com",
  "kms.loli.best",
  "kms.sixyin.com",
  "kms.loli.beer",
];

const VERSION_GROUPS = [
  {
    name: "Win11 版本",
    versions: [
      { label: "Win11 专业版", key: "W269N-WFGWX-YVC9B-4J6C9-T83GX" },
      { label: "Win11 家庭版", key: "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99" },
      { label: "Win11 专业工作站版", key: "NRG8B-VKK3Q-CXVCJ-9G2XF-6Q84J" },
      { label: "Win11 企业版", key: "NPPR9-FWDCX-D2C8J-H872K-2YT43" },
      { label: "Win11 教育版", key: "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2" },
    ],
  },
  {
    name: "Win10 版本",
    versions: [
      { label: "Win10 专业版", key: "W269N-WFGWX-YVC9B-4J6C9-T83GX" },
      { label: "Win10 家庭版", key: "TX9XD-98N7V-6WMQ6-BX7FG-H8Q99" },
      { label: "Win10 专业工作站版", key: "NRG8B-VKK3Q-CXVCJ-9G2XF-6Q84J" },
      { label: "Win10 企业版", key: "NPPR9-FWDCX-D2C8J-H872K-2YT43" },
      { label: "Win10 教育版", key: "NW6C2-QMPVW-D7KKK-3GKT6-VCFB2" },
    ],
  },
  {
    name: "Win8.1 版本",
    versions: [
      { label: "Win8.1 专业版", key: "GCRJD-8NW9H-F2CDX-CCM8D-9D6T9" },
      { label: "Win8.1 企业版", key: "MHF9N-XY6XB-WVXMC-BTDCT-MKKG7" },
      { label: "Win8.1 核心版", key: "BB6NG-PQ82V-VRDPW-8XVD2-V8P66" },
    ],
  },
  {
    name: "Win8 版本",
    versions: [
      { label: "Win8 专业版", key: "NG4HW-VH26C-733KW-K6QRF-8C8BT" },
      { label: "Win8 企业版", key: "32JNW-9KQ84-P47T8-D8GGY-CWCK7" },
    ],
  },
];

let state = {
  currentStep: 1,
  selectedVersion: null,
  selectedVersionLabel: "",
  selectedKms: "",
};

export function initActivation() {
  renderVersions();
  renderKmsButtons();
  updateStepIndicator();
  updateNavButtons();

  document.getElementById("wizard-next").addEventListener("click", onNext);
  document.getElementById("wizard-prev").addEventListener("click", onPrev);

  document.getElementById("kms-use-custom").addEventListener("click", () => {
    const val = document.getElementById("activation-kms-custom").value.trim();
    if (val) selectKms(val);
  });

  document.getElementById("activation-kms-custom").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      const val = e.target.value.trim();
      if (val) selectKms(val);
    }
  });

  document.getElementById("activation-start").addEventListener("click", startActivation);
}

function renderVersions() {
  const container = document.getElementById("activation-versions");
  if (!container) return;

  container.innerHTML = "";
  VERSION_GROUPS.forEach((group) => {
    const groupDiv = document.createElement("div");
    groupDiv.className = "version-group";

    const title = document.createElement("div");
    title.className = "version-group-title";
    title.textContent = group.name;
    groupDiv.appendChild(title);

    const grid = document.createElement("div");
    grid.className = "version-grid";
    group.versions.forEach((v) => {
      const btn = document.createElement("button");
      btn.className = "version-btn";
      btn.textContent = v.label;
      btn.dataset.key = v.key;
      btn.dataset.label = v.label;
      btn.addEventListener("click", () => selectVersion(btn, v.key, v.label));
      grid.appendChild(btn);
    });
    groupDiv.appendChild(grid);
    container.appendChild(groupDiv);
  });
}

function renderKmsButtons() {
  const container = document.getElementById("activation-kms-list");
  if (!container) return;

  container.innerHTML = "";
  KMS_SERVERS.forEach((addr) => {
    const btn = document.createElement("button");
    btn.className = "kms-pill";
    btn.textContent = addr;
    btn.addEventListener("click", () => selectKms(addr));
    container.appendChild(btn);
  });
}

function selectVersion(btn, key, label) {
  document.querySelectorAll(".version-btn").forEach((el) => el.classList.remove("selected"));
  btn.classList.add("selected");
  state.selectedVersion = key;
  state.selectedVersionLabel = label;
}

function selectKms(addr) {
  document.querySelectorAll(".kms-pill").forEach((el) => el.classList.remove("selected"));
  const pills = document.querySelectorAll(".kms-pill");
  for (const p of pills) {
    if (p.textContent === addr) {
      p.classList.add("selected");
      break;
    }
  }
  state.selectedKms = addr;
  document.getElementById("activation-kms-custom").value = addr;
}

function onNext() {
  if (state.currentStep === 1 && !state.selectedVersion) {
    showToast("请先选择一个 Windows 版本", "error");
    return;
  }
  if (state.currentStep === 2 && !state.selectedKms) {
    showToast("请选择一个 KMS 服务器或输入自定义地址", "error");
    return;
  }
  state.currentStep = Math.min(state.currentStep + 1, 3);
  updateStepIndicator();
  showPane(state.currentStep);
  updateNavButtons();
  updateSummary();
}

function onPrev() {
  state.currentStep = Math.max(state.currentStep - 1, 1);
  updateStepIndicator();
  showPane(state.currentStep);
  updateNavButtons();
}

function showPane(step) {
  document.querySelectorAll(".wizard-pane").forEach((el) => el.classList.remove("active"));
  const pane = document.getElementById("wizard-step-" + step);
  if (pane) {
    pane.classList.add("active");
    // Re-trigger animation
    pane.style.animation = "none";
    requestAnimationFrame(() => {
      pane.style.animation = "";
    });
  }
}
function updateStepIndicator() {
  document.querySelectorAll(".wizard-step").forEach((el) => {
    const s = parseInt(el.dataset.step, 10);
    el.classList.toggle("active", s === state.currentStep);
    el.classList.toggle("completed", s < state.currentStep);
  });

  document.querySelectorAll(".wizard-connector").forEach((el, i) => {
    el.classList.toggle("done", i + 1 < state.currentStep);
  });
}

function updateNavButtons() {
  const prevBtn = document.getElementById("wizard-prev");
  const nextBtn = document.getElementById("wizard-next");
  const nav = document.querySelector(".wizard-nav");

  const showPrev = state.currentStep > 1;
  const showNext = state.currentStep < 3;

  prevBtn.style.display = showPrev ? "" : "none";
  nextBtn.style.display = showNext ? "" : "none";

  nav.classList.toggle("single-btn", showPrev !== showNext);
}

function updateSummary() {
  const verEl = document.getElementById("summary-version");
  const kmsEl = document.getElementById("summary-kms");
  if (verEl) verEl.textContent = state.selectedVersionLabel || "未选择";
  if (kmsEl) kmsEl.textContent = state.selectedKms || "未选择";
}

async function startActivation() {
  if (!state.selectedVersion || !state.selectedKms) {
    showToast("请完成前两步后再激活", "error");
    return;
  }

  const btn = document.getElementById("activation-start");
  btn.disabled = true;
  btn.textContent = "正在激活...";

  const resultArea = document.getElementById("activation-result-area");
  const timeline = document.getElementById("activation-timeline");
  resultArea.style.display = "none";

  try {
    const res = await apiFetch("/api/activation/activate", {
      method: "POST",
      body: JSON.stringify({
        gvlk_key: state.selectedVersion,
        kms_server: state.selectedKms,
      }),
    });

    if (res) {
      resultArea.style.display = "block";
      renderTimeline(res, timeline);
      showToast(res.message, res.success ? "success" : "error");
    }
  } finally {
    btn.disabled = false;
    btn.textContent = "开始激活";
  }
}
function renderTimeline(res, container) {
  const steps = res.steps || [];

  if (steps.length === 0) {
    container.innerHTML = '<div class="timeline-step"><div class="timeline-body"><div class="timeline-label">无返回结果</div></div></div>';
    return;
  }

  let html = "";
  steps.forEach((s, i) => {
    const iconClass = s.success ? "success" : "fail";
    const iconText = s.success ? "✓" : "✗";
    const statusText = s.success ? "完成" : "失败";

    html += '<div class="timeline-step" style="animation-delay:' + (i * 0.1) + 's">';
    html += '<div class="timeline-icon ' + iconClass + '">' + iconText + "</div>";
    html += '<div class="timeline-body">';
    html += '<div class="timeline-label">' + escapeHtml(s.step) + "</div>";
    html += '<div class="timeline-status-text">' + statusText + "</div>";
    if (s.output) {
      html += '<button class="timeline-toggle" data-idx="' + i + '">查看详情</button>';
      html += '<div class="timeline-detail" id="timeline-detail-' + i + '">' + escapeHtml(s.output) + "</div>";
    }
    html += "</div></div>";
  });
  container.innerHTML = html;

  // Toggle detail
  container.querySelectorAll(".timeline-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const idx = btn.dataset.idx;
      const detail = document.getElementById("timeline-detail-" + idx);
      if (detail) {
        detail.classList.toggle("open");
        btn.textContent = detail.classList.contains("open") ? "收起详情" : "查看详情";
      }
    });
  });

  // Badge
  const badgeEl = document.getElementById("activation-complete-badge");
  if (badgeEl) {
    const allOk = steps.every((s) => s.success);
    if (allOk) {
      badgeEl.innerHTML = '<span class="activation-complete-badge">✓ 激活完成</span>';
    } else {
      badgeEl.innerHTML = "";
    }
  }
}
