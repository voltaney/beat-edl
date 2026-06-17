// Frontend logic for beat-edl. Talks to Python via window.pywebview.api.

const $ = (id) => document.getElementById(id);

let audioPath = null;
let wavesurfer = null;
let lastResult = null;

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

function initWavesurfer() {
  if (wavesurfer) wavesurfer.destroy();
  wavesurfer = WaveSurfer.create({
    container: "#waveform",
    waveColor: "#5b6072",
    progressColor: "#5b8def",
    height: 110,
    cursorColor: "#f8f8f2",
  });
}

// Draw beat markers as thin vertical overlays over the waveform.
function drawBeats(result) {
  const container = $("waveform");
  container.querySelectorAll(".beat-line").forEach((n) => n.remove());
  const duration = wavesurfer ? wavesurfer.getDuration() : 0;
  if (!duration) return;

  const downbeatSet = new Set(result.downbeats.map((t) => t.toFixed(3)));
  for (const t of result.beats) {
    const isDown = downbeatSet.has(t.toFixed(3));
    const line = document.createElement("div");
    line.className = "beat-line";
    line.style.position = "absolute";
    line.style.top = "8px";
    line.style.bottom = "8px";
    line.style.width = isDown ? "2px" : "1px";
    line.style.background = isDown ? "#ff6b6b" : "rgba(248,248,242,0.45)";
    line.style.left = `${(t / duration) * 100}%`;
    line.style.pointerEvents = "none";
    container.appendChild(line);
  }
  container.style.position = "relative";
}

async function pickFile() {
  const path = await window.pywebview.api.open_audio_dialog();
  if (!path) return;
  audioPath = path;
  $("file-name").textContent = path.split(/[\\/]/).pop();
  $("analyze").disabled = false;
  $("export").disabled = true;
  initWavesurfer();
  // pywebview can serve a local file via the file:// protocol.
  wavesurfer.load("file://" + path);
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
  lastResult = res;
  drawBeats(res);
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
