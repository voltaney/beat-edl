// Frontend logic for beat-edl. Talks to Python via window.pywebview.api.

const $ = (id) => document.getElementById(id);

let audioPath = null;

function setStatus(text, isError = false) {
  const el = $("status");
  el.textContent = text;
  el.style.color = isError ? "#ff6b6b" : "";
}

function gatherParams() {
  return {
    backend: $("backend").value || null,
    beats_per_bar: parseInt($("beats-per-bar").value, 10),
    fps: parseFloat($("fps").value),
    tempo_hint: parseFloat($("tempo-hint").value) || 0,
    beat_interval: parseInt($("beat-interval").value, 10),
    timeline_start: $("timeline-start").value,
    color: $("color").value,
    downbeat_color: $("downbeat-color").value,
    mark_downbeats: $("mark-downbeats").checked,
    downbeats_only: $("downbeats-only").checked,
  };
}

async function pickFile() {
  const path = await window.pywebview.api.open_audio_dialog();
  if (!path) return;
  audioPath = path;
  $("file-name").textContent = path.split(/[\\/]/).pop();
  $("analyze").disabled = false;
  $("export").disabled = true;
  setStatus("");
}

async function analyze() {
  if (!audioPath) return;
  setStatus("解析中…");
  $("analyze").disabled = true;
  const res = await window.pywebview.api.analyze(audioPath, gatherParams());
  $("analyze").disabled = false;
  if (!res.ok) {
    setStatus("エラー: " + res.error, true);
    return;
  }
  setStatus(
    `${res.backend} | ${res.tempo} BPM | ビート ${res.beats.length} / 小節頭 ${res.downbeats.length}`
  );
  $("export").disabled = false;
}

async function exportEdl() {
  if (!audioPath) return;
  setStatus("書き出し中…");
  const res = await window.pywebview.api.export_edl(audioPath, gatherParams());
  if (!res.ok) {
    setStatus(res.error === "cancelled" ? "キャンセルしました" : "エラー: " + res.error, res.error !== "cancelled");
    return;
  }
  setStatus(`保存しました: ${res.path}（マーカー ${res.marker_count} 個）`);
}

function fillColorSelect(select, colors, selected) {
  select.innerHTML = "";
  for (const c of colors) {
    const opt = document.createElement("option");
    opt.value = c;
    opt.textContent = c;
    if (c === selected) opt.selected = true;
    select.appendChild(opt);
  }
}

async function boot() {
  const caps = await window.pywebview.api.get_capabilities();
  const backendSel = $("backend");
  backendSel.innerHTML = "";
  for (const b of caps.backends) {
    const opt = document.createElement("option");
    opt.value = b;
    opt.textContent = b;
    backendSel.appendChild(opt);
  }
  $("backend-badge").textContent = caps.backends.join(" / ") || "バックエンドなし";
  fillColorSelect($("color"), caps.colors, "Blue");
  fillColorSelect($("downbeat-color"), caps.colors, "Red");

  $("pick-file").addEventListener("click", pickFile);
  $("analyze").addEventListener("click", analyze);
  $("export").addEventListener("click", exportEdl);
}

window.addEventListener("pywebviewready", boot);
