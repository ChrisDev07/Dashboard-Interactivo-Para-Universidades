"""Generate a standalone HTML dashboard from the Excel dataset."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "estudiantes_universitarios.xlsx"
OUTPUT_PATH = BASE_DIR / "web" / "dashboard.html"


def _clean_records(dataframe: pd.DataFrame) -> list[dict]:
    """Convert pandas values into browser-friendly JSON records."""
    clean = dataframe.copy()
    for column in clean.columns:
        if pd.api.types.is_datetime64_any_dtype(clean[column]):
            clean[column] = clean[column].dt.strftime("%Y-%m-%d").fillna("")
    clean = clean.fillna("")
    return clean.to_dict(orient="records")


def build_dashboard() -> Path:
    dataframe = pd.read_excel(DATASET_PATH)
    records_json = json.dumps(_clean_records(dataframe), ensure_ascii=False)
    programs_json = json.dumps(sorted(dataframe["programa"].dropna().unique().tolist()), ensure_ascii=False)
    semesters = sorted(set(dataframe["semestre_ingreso"].dropna()) | set(dataframe["semestre_actual"].dropna()))
    semesters_json = json.dumps(semesters, ensure_ascii=False)
    genders_json = json.dumps(sorted(dataframe["genero"].dropna().unique().tolist()), ensure_ascii=False)
    states_json = json.dumps(sorted(dataframe["estado"].dropna().unique().tolist()), ensure_ascii=False)

    html = HTML_TEMPLATE.replace("__RECORDS__", records_json)
    html = html.replace("__PROGRAMS__", programs_json)
    html = html.replace("__SEMESTERS__", semesters_json)
    html = html.replace("__GENDERS__", genders_json)
    html = html.replace("__STATES__", states_json)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(html, encoding="utf-8")
    return OUTPUT_PATH


HTML_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard Estudiantil Universitario</title>
  <style>
    :root {
      --bg: #0b1020;
      --panel: #111a2e;
      --panel-2: #132238;
      --panel-3: #162a46;
      --line: #243b61;
      --text: #f8fafc;
      --muted: #9db0c9;
      --cyan: #2dd4bf;
      --blue: #60a5fa;
      --yellow: #ffd166;
      --pink: #ef476f;
      --green: #84cc16;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background:
        radial-gradient(circle at top left, rgba(45, 212, 191, .12), transparent 32rem),
        linear-gradient(135deg, #07101f, var(--bg));
      color: var(--text);
      font-family: "Segoe UI", Arial, sans-serif;
      min-width: 1040px;
    }
    .app { display: grid; grid-template-columns: 272px 1fr; min-height: 100vh; }
    aside {
      background: linear-gradient(180deg, #111a2e, #0d1729);
      border-right: 1px solid var(--line);
      padding: 18px;
      box-shadow: 12px 0 30px rgba(0, 0, 0, .14);
    }
    main { padding: 16px; }
    h1, h2, h3, p { margin: 0; }
    .brand { color: var(--yellow); font-size: 15px; font-weight: 800; }
    .muted { color: var(--muted); font-size: 13px; margin-top: 4px; }
    .filter-block { border-top: 1px solid var(--line); margin-top: 18px; padding-top: 16px; }
    label { display: block; color: #dbeafe; font-size: 13px; font-weight: 700; margin-bottom: 7px; }
    .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 16px; }
    button.action {
      border: 1px solid var(--line);
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: var(--text);
      border-radius: 6px;
      padding: 10px;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 10px 22px rgba(37, 99, 235, .16);
    }
    button.action:hover { background: var(--cyan); color: #06121f; }
    .action-wide { grid-column: 1 / -1; background: #132238; }
    select, input {
      width: 100%;
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 11px;
      outline: none;
      font-size: 14px;
      transition: border-color .16s ease, box-shadow .16s ease;
    }
    select:focus, input:focus { border-color: var(--cyan); box-shadow: 0 0 0 3px rgba(45, 212, 191, .12); }
    .checks label {
      display: flex;
      gap: 8px;
      align-items: center;
      color: var(--muted);
      font-weight: 600;
      margin: 8px 0;
    }
    .checks input { width: auto; }
    .hero {
      position: relative;
      overflow: hidden;
      height: 174px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, #101a2e, #10293b);
      padding: 24px 28px;
      border-radius: 10px;
      box-shadow: 0 20px 50px rgba(0, 0, 0, .18);
    }
    .hero:before {
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(112deg, rgba(45, 212, 191, .15), transparent 45%),
        repeating-linear-gradient(120deg, transparent 0 34px, rgba(96, 165, 250, .12) 35px 37px);
      pointer-events: none;
    }
    .hero-content { position: relative; z-index: 1; display: flex; justify-content: space-between; gap: 22px; }
    .hero h1 { font-size: 30px; letter-spacing: 0; }
    .hero p { color: #afc1d8; margin-top: 6px; }
    .chips { display: flex; gap: 8px; margin-top: 22px; }
    .chip { padding: 7px 10px; font-size: 11px; font-weight: 800; background: var(--blue); color: #06121f; }
    .chip:nth-child(2) { background: var(--pink); color: white; }
    .chip:nth-child(3) { background: var(--cyan); }
    .chip:nth-child(4) { background: var(--yellow); }
    .hero-metrics { display: flex; gap: 12px; }
    .hero-metric { width: 142px; height: 94px; background: rgba(11, 22, 40, .92); border: 1px solid var(--line); padding: 14px; }
    .hero-metric span { color: var(--cyan); font-size: 12px; font-weight: 800; }
    .hero-metric strong { display: block; color: var(--yellow); font-size: 24px; margin-top: 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .cards { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; margin-top: 14px; }
    .card, .chart-panel, .table-panel {
      background: linear-gradient(180deg, var(--panel-2), #101c30);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 14px 32px rgba(0, 0, 0, .16);
    }
    .card { padding: 14px; min-height: 142px; cursor: grab; transition: transform .16s ease, border-color .16s ease, opacity .16s ease, box-shadow .16s ease; }
    .card:hover { transform: translateY(-2px); border-color: rgba(45, 212, 191, .55); box-shadow: 0 18px 38px rgba(0, 0, 0, .2); }
    .card:active { cursor: grabbing; }
    .card.dragging { opacity: .58; border-color: var(--cyan); transform: scale(.98); }
    .card.drop-before { box-shadow: -4px 0 0 var(--cyan); }
    .card.drop-after { box-shadow: 4px 0 0 var(--cyan); }
    .card h3 { color: #afc1d8; font-size: 12px; text-transform: uppercase; }
    .card h3 .drag-hint { float: right; display: inline; color: var(--cyan); font-size: 11px; font-weight: 800; text-transform: none; }
    .card strong { display: block; font-size: 24px; margin-top: 10px; }
    .card span { display: block; color: #7f95b2; font-size: 12px; margin-top: 2px; min-height: 16px; }
    .spark { width: 100%; height: 46px; margin-top: 12px; display: block; background: #0b1628; border-radius: 6px; }
    .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
    .chart-panel { padding: 14px; min-height: 330px; }
    .chart-title { color: var(--yellow); font-size: 14px; font-weight: 800; margin-bottom: 10px; display: flex; align-items: center; gap: 8px; }
    .chart-title:before { content: ""; width: 8px; height: 8px; background: var(--cyan); display: inline-block; }
    .chart { width: 100%; height: 266px; display: block; background: linear-gradient(135deg, #0b1628, #132238); border-radius: 7px; border: 1px solid rgba(36, 59, 97, .7); }
    .table-panel { margin-top: 14px; overflow: hidden; }
    .table-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; border-bottom: 1px solid var(--line); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { text-align: left; padding: 9px 10px; border-bottom: 1px solid rgba(36, 59, 97, .65); white-space: nowrap; }
    th { color: var(--yellow); background: #1d3557; cursor: pointer; position: sticky; top: 0; z-index: 1; }
    td { color: #eaf2ff; }
    tr:hover td { background: rgba(96, 165, 250, .08); }
    .table-wrap { max-height: 330px; overflow: auto; }
    .empty { color: var(--muted); padding: 22px; }
    .modal {
      position: fixed;
      inset: 0;
      display: none;
      place-items: center;
      background: rgba(3, 7, 18, .68);
      z-index: 20;
    }
    .modal.open { display: grid; }
    .modal-card {
      width: min(520px, calc(100vw - 32px));
      background: #111a2e;
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 24px 70px rgba(0, 0, 0, .42);
      overflow: hidden;
    }
    .modal-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
    }
    .modal-head strong { color: var(--yellow); }
    .modal button {
      border: 1px solid var(--line);
      background: var(--panel-2);
      color: var(--text);
      border-radius: 6px;
      padding: 7px 10px;
      cursor: pointer;
    }
    .modal-body { padding: 14px 16px 16px; }
    .breakdown-row {
      display: grid;
      grid-template-columns: 1fr 62px;
      gap: 12px;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid rgba(36, 59, 97, .55);
      color: #eaf2ff;
    }
    .mini-bar { height: 7px; background: #0b1628; margin-top: 5px; }
    .mini-bar span { display: block; height: 100%; background: var(--cyan); }
    .metric-menu { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px; }
    .metric-menu button {
      background: #132238;
      border: 1px solid var(--line);
      color: var(--text);
      border-radius: 6px;
      padding: 12px;
      font-weight: 800;
      cursor: pointer;
    }
    .metric-menu button:hover { background: var(--cyan); color: #06121f; }
  </style>
</head>
<body>
  <div class="app">
    <aside>
      <div class="brand">UNIVERSIDAD NOVA ANDINA</div>
      <div class="muted">Dashboard HTML sin servidor</div>
      <div class="actions">
        <button class="action" id="exportJpg" type="button">Exportar JPG</button>
        <button class="action" id="exportPdf" type="button">Exportar PDF</button>
        <button class="action action-wide" id="clearFilters" type="button">Limpiar filtros</button>
      </div>

      <div class="filter-block">
        <label for="search">Buscar nombre</label>
        <input id="search" type="search" placeholder="Ej. Laura, Camilo">
      </div>
      <div class="filter-block">
        <label for="program">Carrera</label>
        <select id="program"></select>
      </div>
      <div class="filter-block">
        <label for="semester">Semestre</label>
        <select id="semester"></select>
      </div>
      <div class="filter-block">
        <label for="gender">Genero</label>
        <select id="gender"></select>
      </div>
      <div class="filter-block">
        <label for="state">Estado</label>
        <select id="state"></select>
      </div>
      <div class="filter-block checks">
        <label><input id="delay" type="checkbox"> Aplazamiento</label>
        <label><input id="dropout" type="checkbox"> Desercion voluntaria</label>
        <label><input id="risk" type="checkbox"> Bajo rendimiento</label>
      </div>
    </aside>

    <main>
      <section class="hero">
        <div class="hero-content">
          <div>
            <h1>Centro de Control Academico</h1>
            <p>Admisiones, permanencia, alertas e ingresos en una vista web local.</p>
            <div class="chips">
              <div class="chip">ADMITIDOS</div>
              <div class="chip">RIESGO</div>
              <div class="chip">INGRESOS</div>
              <div class="chip">EXPORTACION</div>
            </div>
          </div>
          <div class="hero-metrics">
            <div class="hero-metric"><span>Registros</span><strong id="heroTotal">0</strong></div>
            <div class="hero-metric"><span>Vista actual</span><strong id="heroContext">Todos</strong></div>
          </div>
        </div>
      </section>

      <section class="cards" id="cards"></section>
      <section class="charts">
        <div class="chart-panel"><div class="chart-title">Evolucion de inscripciones</div><canvas class="chart" id="lineChart"></canvas></div>
        <div class="chart-panel"><div class="chart-title">Distribucion por estado</div><canvas class="chart" id="pieChart"></canvas></div>
        <div class="chart-panel"><div class="chart-title">Desercion y bajo rendimiento por programa</div><canvas class="chart" id="barChart"></canvas></div>
        <div class="chart-panel"><div class="chart-title">Mapa 3D de riesgo academico por carrera</div><canvas class="chart" id="threeDChart"></canvas></div>
      </section>
      <section class="table-panel">
        <div class="table-head"><strong>Detalle de estudiantes</strong><span class="muted" id="rowCount">0 registros</span></div>
        <div class="table-wrap"><table id="studentTable"></table></div>
      </section>
    </main>
  </div>

  <div class="modal" id="enrollmentModal">
    <div class="modal-card">
      <div class="modal-head">
        <strong id="modalTitle">Detalle de inscripciones</strong>
        <button id="modalClose" type="button">Cerrar</button>
      </div>
      <div class="modal-body" id="modalBody"></div>
    </div>
  </div>

  <script>
    const STUDENTS = __RECORDS__;
    const PROGRAMS = __PROGRAMS__;
    const SEMESTERS = __SEMESTERS__;
    const GENDERS = __GENDERS__;
    const STATES = __STATES__;
    const COLORS = ["#2dd4bf", "#ffd166", "#ef476f", "#60a5fa", "#84cc16", "#a78bfa"];
    const controls = ["search", "program", "semester", "gender", "state", "delay", "dropout", "risk"].reduce((map, id) => {
      map[id] = document.getElementById(id);
      return map;
    }, {});
    let sortColumn = "id_estudiante";
    let sortDir = 1;
    let cardOrder = ["total", "delay", "dropout", "risk", "gender"];
    let draggedCardKey = null;
    let lineHitboxes = [];
    let barHitboxes = [];

    function fillSelect(select, values) {
      select.innerHTML = `<option>Todos</option>${values.map(value => `<option>${value}</option>`).join("")}`;
    }

    function filteredStudents() {
      const search = controls.search.value.trim().toLowerCase();
      return STUDENTS.filter(student => {
        if (search && !String(student.nombre).toLowerCase().includes(search)) return false;
        if (controls.program.value !== "Todos" && student.programa !== controls.program.value) return false;
        if (controls.semester.value !== "Todos" && student.semestre_ingreso !== controls.semester.value && student.semestre_actual !== controls.semester.value) return false;
        if (controls.gender.value !== "Todos" && student.genero !== controls.gender.value) return false;
        if (controls.state.value !== "Todos" && student.estado !== controls.state.value) return false;
        if (controls.delay.checked && !student.aplazamiento) return false;
        if (controls.dropout.checked && !student.desercion_voluntaria) return false;
        if (controls.risk.checked && !student.bajo_rendimiento) return false;
        return true;
      });
    }

    function percent(records, field) {
      return records.length ? `${(records.filter(item => item[field]).length / records.length * 100).toFixed(1)}%` : "0.0%";
    }

    function countBy(records, field, values) {
      return values.map(value => records.filter(item => item[field] === value).length);
    }

    function drawSpark(canvas, progress) {
      const ctx = setupCanvas(canvas);
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#0b1628");
      bg.addColorStop(1, "#10293b");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, width, height);
      ctx.strokeStyle = "rgba(45, 212, 191, .18)";
      ctx.strokeRect(.5, .5, width - 1, height - 1);
      ctx.strokeStyle = "rgba(96, 165, 250, .16)";
      for (let x = 0; x < width; x += 22) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x + 26, height);
        ctx.stroke();
      }
      ctx.fillStyle = "#2dd4bf";
      ctx.fillRect(0, height - 8, Math.max(18, width * progress), 8);
      const values = [0.18, progress * .52 + .12, progress * .74 + .08, progress * .62 + .24, progress * .9 + .06, progress || .08];
      ctx.strokeStyle = "#8be9dd";
      ctx.lineWidth = 2;
      ctx.beginPath();
      values.forEach((value, index) => {
        const x = 12 + (width - 24) * index / (values.length - 1);
        const y = 30 - Math.min(.95, value) * 20;
        index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
      });
      ctx.stroke();
      const lastX = 12 + (width - 24);
      const lastY = 30 - Math.min(.95, values[values.length - 1]) * 20;
      ctx.fillStyle = "#ffd166";
      ctx.beginPath();
      ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    function setupCanvas(canvas) {
      const ratio = window.devicePixelRatio || 1;
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      canvas.width = width * ratio;
      canvas.height = height * ratio;
      const ctx = canvas.getContext("2d");
      ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
      return ctx;
    }

    function drawLine(canvas, labels, values) {
      const ctx = setupCanvas(canvas);
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const pad = 46;
      const max = Math.max(1, ...values);
      drawChartBackground(ctx, width, height);
      drawGrid(ctx, width, height, pad, max);
      const area = new Path2D();
      values.forEach((value, index) => {
        const x = pad + (width - pad * 2) * index / Math.max(1, labels.length - 1);
        const y = height - pad - (height - pad * 2) * value / max;
        index ? area.lineTo(x, y) : area.moveTo(x, y);
      });
      area.lineTo(width - pad, height - pad);
      area.lineTo(pad, height - pad);
      area.closePath();
      const fill = ctx.createLinearGradient(0, pad, 0, height - pad);
      fill.addColorStop(0, "rgba(45, 212, 191, .28)");
      fill.addColorStop(1, "rgba(96, 165, 250, .02)");
      ctx.fillStyle = fill;
      ctx.fill(area);
      ctx.strokeStyle = "#2dd4bf";
      ctx.lineWidth = 3;
      ctx.beginPath();
      lineHitboxes = [];
      values.forEach((value, index) => {
        const x = pad + (width - pad * 2) * index / Math.max(1, labels.length - 1);
        const y = height - pad - (height - pad * 2) * value / max;
        index ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
        lineHitboxes.push({ x, y, semester: labels[index], value });
      });
      ctx.stroke();
      ctx.fillStyle = "#ffd166";
      values.forEach((value, index) => {
        const x = pad + (width - pad * 2) * index / Math.max(1, labels.length - 1);
        const y = height - pad - (height - pad * 2) * value / max;
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#eaf2ff";
        ctx.font = "10px Segoe UI";
        ctx.fillText(String(value), x - 6, y - 10);
        ctx.fillStyle = "#ffd166";
      });
      drawAxisLabels(ctx, labels, width, height, pad);
      canvas.onclick = event => {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const hit = lineHitboxes.find(point => Math.hypot(point.x - x, point.y - y) <= 16);
        if (hit) showEnrollmentPopup(hit.semester);
      };
    }

    function drawPie(canvas, labels, values) {
      const ctx = setupCanvas(canvas);
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const total = Math.max(1, values.reduce((sum, value) => sum + value, 0));
      let angle = -Math.PI / 2;
      const radius = Math.min(width, height) * .32;
      const cx = width * .38;
      const cy = height * .52;
      drawChartBackground(ctx, width, height);
      ctx.shadowColor = "rgba(0, 0, 0, .35)";
      ctx.shadowBlur = 14;
      ctx.shadowOffsetY = 8;
      values.forEach((value, index) => {
        const next = angle + (value / total) * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.arc(cx, cy, radius, angle, next);
        ctx.closePath();
        ctx.fillStyle = COLORS[index % COLORS.length];
        ctx.fill();
        angle = next;
      });
      ctx.shadowColor = "transparent";
      ctx.fillStyle = "#0b1628";
      ctx.beginPath();
      ctx.arc(cx, cy, radius * .55, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = "#eaf2ff";
      ctx.font = "bold 18px Segoe UI";
      ctx.textAlign = "center";
      ctx.fillText(String(total), cx, cy + 6);
      ctx.textAlign = "start";
      labels.forEach((label, index) => {
        ctx.fillStyle = COLORS[index % COLORS.length];
        ctx.fillRect(width * .68, 50 + index * 28, 12, 12);
        ctx.fillStyle = "#eaf2ff";
        ctx.font = "12px Segoe UI";
        ctx.fillText(`${label}: ${values[index]}`, width * .68 + 18, 61 + index * 28);
      });
    }

    function drawBar(canvas, labels, first, second) {
      const ctx = setupCanvas(canvas);
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const pad = 46;
      const max = Math.max(1, ...first, ...second);
      const groupWidth = (width - pad * 2) / labels.length;
      drawChartBackground(ctx, width, height);
      drawGrid(ctx, width, height, pad, max);
      barHitboxes = [];
      labels.forEach((label, index) => {
        const x = pad + index * groupWidth + groupWidth * .22;
        const barWidth = Math.max(8, groupWidth * .2);
        const h1 = (height - pad * 2) * first[index] / max;
        const h2 = (height - pad * 2) * second[index] / max;
        drawBarColumn(ctx, x, height - pad - h1, barWidth, h1, "#ef476f");
        drawBarColumn(ctx, x + barWidth + 4, height - pad - h2, barWidth, h2, "#ffd166");
        if (first[index] > 0) drawValueLabel(ctx, first[index], x + barWidth / 2, height - pad - h1 - 5, "#ef476f");
        if (second[index] > 0) drawValueLabel(ctx, second[index], x + barWidth * 1.5 + 4, height - pad - h2 - 5, "#ffd166");
        barHitboxes.push({
          program: label,
          x,
          y: height - pad - Math.max(h1, h2) - 8,
          width: barWidth * 2 + 8,
          height: Math.max(h1, h2) + 16,
          dropout: first[index],
          risk: second[index],
        });
        ctx.save();
        ctx.translate(x, height - 11);
        ctx.rotate(-0.32);
        ctx.fillStyle = "#afc1d8";
        ctx.font = "10px Segoe UI";
        ctx.fillText(label.slice(0, 14), 0, 0);
        ctx.restore();
      });
      ctx.fillStyle = "#ef476f";
      ctx.fillRect(width - 150, 18, 10, 10);
      ctx.fillStyle = "#eaf2ff";
      ctx.fillText("Deserciones", width - 134, 27);
      ctx.fillStyle = "#ffd166";
      ctx.fillRect(width - 150, 38, 10, 10);
      ctx.fillStyle = "#eaf2ff";
      ctx.fillText("Bajo rendimiento", width - 134, 47);
      canvas.onclick = event => {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const hit = barHitboxes.find(box => x >= box.x - 4 && x <= box.x + box.width + 4 && y >= box.y && y <= box.y + box.height);
        if (hit) showProgramMetricPopup(hit.program, hit.dropout, hit.risk);
      };
    }

    function drawThreeD(canvas, records) {
      const ctx = setupCanvas(canvas);
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      drawChartBackground(ctx, width, height);
      const originX = 72;
      const originY = height - 40;
      const xStep = (width - 220) / Math.max(1, PROGRAMS.length - 1);
      const zStep = 28;
      const rowShift = 22;
      const metrics = [
        { key: "aplazamiento", label: "Aplazamientos", color: "#60a5fa" },
        { key: "desercion_voluntaria", label: "Deserciones", color: "#ef476f" },
        { key: "bajo_rendimiento", label: "Bajo rendimiento", color: "#ffd166" },
      ];
      const counts = metrics.map(metric => PROGRAMS.map(program => records.filter(item => item.programa === program && item[metric.key]).length));
      const max = Math.max(1, ...counts.flat());
      drawThreeDAxis(ctx, originX, originY, max);
      ctx.fillStyle = "#afc1d8";
      ctx.font = "11px Segoe UI";
      ctx.fillText("Altura = estudiantes con alerta dentro de los filtros actuales", 54, 18);
      ctx.strokeStyle = "rgba(45, 212, 191, .24)";
      for (let z = 0; z < metrics.length; z++) {
        ctx.beginPath();
        ctx.moveTo(originX + z * rowShift, originY - z * zStep);
        ctx.lineTo(width - 174 + z * rowShift, originY - z * zStep);
        ctx.stroke();
      }
      for (let x = 0; x < PROGRAMS.length; x++) {
        ctx.beginPath();
        ctx.moveTo(originX + x * xStep, originY);
        ctx.lineTo(originX + x * xStep + metrics.length * rowShift, originY - metrics.length * zStep);
        ctx.stroke();
      }
      const bars = [];
      metrics.forEach((metric, row) => {
        PROGRAMS.forEach((program, col) => {
          const value = counts[row][col];
          const x = originX + col * xStep + row * rowShift;
          const baseY = originY - row * zStep;
          bars.push({ x, baseY, value, row, col, h: (height - 132) * value / max });
        });
      });
      bars.sort((a, b) => b.row - a.row).forEach(bar => {
        const color = metrics[bar.row].color;
        drawIsoBar(ctx, bar.x, bar.baseY, Math.max(2, bar.h), color);
        if (bar.value > 0 && (bar.value === max || bar.value >= max * .55)) {
          ctx.fillStyle = "#eaf2ff";
          ctx.font = "10px Segoe UI";
          ctx.fillText(String(bar.value), bar.x + 2, bar.baseY - bar.h - 8);
        }
      });
      PROGRAMS.forEach((program, index) => {
        ctx.fillStyle = "#ffd166";
        ctx.font = "10px Segoe UI";
        ctx.save();
        ctx.translate(originX + index * xStep - 8, height - 10);
        ctx.rotate(-0.25);
        ctx.fillText(program.slice(0, 13), 0, 0);
        ctx.restore();
      });
      metrics.forEach((metric, index) => {
        ctx.fillStyle = metric.color;
        ctx.fillRect(width - 170, 42 + index * 24, 10, 10);
        ctx.fillStyle = "#afc1d8";
        ctx.font = "11px Segoe UI";
        ctx.fillText(metric.label, width - 154, 51 + index * 24);
      });
    }

    function drawChartBackground(ctx, width, height) {
      const bg = ctx.createLinearGradient(0, 0, width, height);
      bg.addColorStop(0, "#0b1628");
      bg.addColorStop(1, "#132238");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, width, height);
      ctx.strokeStyle = "rgba(45, 212, 191, .12)";
      for (let x = -height; x < width; x += 34) {
        ctx.beginPath();
        ctx.moveTo(x, height);
        ctx.lineTo(x + height, 0);
        ctx.stroke();
      }
      const glow = ctx.createRadialGradient(width * .82, 18, 8, width * .82, 18, width * .5);
      glow.addColorStop(0, "rgba(45, 212, 191, .16)");
      glow.addColorStop(1, "rgba(45, 212, 191, 0)");
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, width, height);
    }

    function drawBarColumn(ctx, x, y, width, height, color) {
      const gradient = ctx.createLinearGradient(0, y, 0, y + height);
      gradient.addColorStop(0, color);
      gradient.addColorStop(1, "rgba(96, 165, 250, .72)");
      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, width, height);
      ctx.fillStyle = "rgba(255, 255, 255, .18)";
      ctx.fillRect(x + width - 3, y, 3, height);
    }

    function drawValueLabel(ctx, value, x, y, color) {
      ctx.fillStyle = "rgba(11, 22, 40, .84)";
      ctx.fillRect(x - 10, y - 12, 20, 14);
      ctx.fillStyle = color;
      ctx.font = "bold 10px Segoe UI";
      ctx.textAlign = "center";
      ctx.fillText(String(value), x, y - 2);
      ctx.textAlign = "start";
    }

    function drawThreeDAxis(ctx, originX, originY, max) {
      const axisTop = 46;
      ctx.strokeStyle = "#5b7192";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(38, originY);
      ctx.lineTo(38, axisTop);
      ctx.stroke();
      ctx.fillStyle = "#afc1d8";
      ctx.font = "10px Segoe UI";
      for (let i = 0; i <= 4; i++) {
        const value = Math.round(max - (max * i / 4));
        const y = axisTop + (originY - axisTop) * i / 4;
        ctx.strokeStyle = "rgba(91, 113, 146, .6)";
        ctx.beginPath();
        ctx.moveTo(34, y);
        ctx.lineTo(42, y);
        ctx.stroke();
        ctx.fillText(String(value), 8, y + 4);
        ctx.strokeStyle = "rgba(36, 59, 97, .24)";
        ctx.beginPath();
        ctx.moveTo(42, y);
        ctx.lineTo(originX, y);
        ctx.stroke();
      }
      ctx.fillStyle = "#5eead4";
      ctx.font = "bold 10px Segoe UI";
      ctx.fillText("Cantidad", 4, axisTop - 14);
    }

    function drawIsoBar(ctx, x, baseY, height, color) {
      const w = 10;
      const d = 8;
      const top = baseY - height;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(x, baseY);
      ctx.lineTo(x + w, baseY - 4);
      ctx.lineTo(x + w, top - 4);
      ctx.lineTo(x, top);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = "rgba(255, 255, 255, .22)";
      ctx.beginPath();
      ctx.moveTo(x, top);
      ctx.lineTo(x + w, top - 4);
      ctx.lineTo(x + w + d, top);
      ctx.lineTo(x + d, top + 4);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = "rgba(0, 0, 0, .22)";
      ctx.beginPath();
      ctx.moveTo(x + w, baseY - 4);
      ctx.lineTo(x + w + d, baseY);
      ctx.lineTo(x + w + d, top);
      ctx.lineTo(x + w, top - 4);
      ctx.closePath();
      ctx.fill();
    }

    function drawGrid(ctx, width, height, pad, maxValue) {
      ctx.strokeStyle = "#243b61";
      ctx.lineWidth = 1;
      ctx.fillStyle = "#afc1d8";
      ctx.font = "11px Segoe UI";
      for (let i = 0; i <= 4; i++) {
        const y = pad + (height - pad * 2) * i / 4;
        ctx.beginPath();
        ctx.moveTo(pad, y);
        ctx.lineTo(width - pad, y);
        ctx.stroke();
        const value = Math.round(maxValue - (maxValue * i / 4));
        ctx.fillText(String(value), 10, y + 4);
      }
      ctx.strokeStyle = "#5b7192";
      ctx.beginPath();
      ctx.moveTo(pad, pad);
      ctx.lineTo(pad, height - pad);
      ctx.lineTo(width - pad, height - pad);
      ctx.stroke();
    }

    function drawAxisLabels(ctx, labels, width, height, pad) {
      ctx.fillStyle = "#afc1d8";
      ctx.font = "11px Segoe UI";
      labels.forEach((label, index) => {
        const x = pad + (width - pad * 2) * index / Math.max(1, labels.length - 1);
        ctx.save();
        ctx.translate(x - 8, height - 11);
        ctx.rotate(-0.35);
        ctx.fillText(label, 0, 0);
        ctx.restore();
      });
    }

    function renderCards(records) {
      const genderText = GENDERS.map(gender => `${gender}: ${records.filter(item => item.genero === gender).length}`).join(" / ");
      const itemsByKey = {
        total: ["Total estudiantes", records.length, "Registros visibles en la vista", Math.min(1, records.length / 500)],
        delay: ["Aplazamientos", percent(records, "aplazamiento"), "Porcentaje de estudiantes con pausa", parseFloat(percent(records, "aplazamiento")) / 100],
        dropout: ["Deserciones", percent(records, "desercion_voluntaria"), "Retiro declarado por el estudiante", parseFloat(percent(records, "desercion_voluntaria")) / 100],
        risk: ["Bajo rendimiento", percent(records, "bajo_rendimiento"), "Alertas academicas activas", parseFloat(percent(records, "bajo_rendimiento")) / 100],
        gender: ["Genero", genderText, "Distribucion por poblacion filtrada", records.length ? .5 : 0]
      };
      const items = cardOrder.map(key => [key, ...itemsByKey[key]]);
      document.getElementById("cards").innerHTML = items.map((item, index) => `
        <article class="card" draggable="true" data-key="${item[0]}">
          <h3>${item[1]} <span class="drag-hint">Mover</span></h3>
          <strong>${item[2]}</strong>
          <span>${item[3]}</span>
          <canvas class="spark" id="spark${index}"></canvas>
        </article>`).join("");
      items.forEach((item, index) => drawSpark(document.getElementById(`spark${index}`), item[4]));
      attachCardDrag();
    }

    function attachCardDrag() {
      const cardsContainer = document.getElementById("cards");
      cardsContainer.querySelectorAll(".card").forEach(card => {
        card.addEventListener("dragstart", event => {
          draggedCardKey = card.dataset.key;
          card.classList.add("dragging");
          event.dataTransfer.effectAllowed = "move";
        });
        card.addEventListener("dragend", () => {
          draggedCardKey = null;
          cardsContainer.querySelectorAll(".card").forEach(item => item.classList.remove("dragging", "drop-before", "drop-after"));
        });
        card.addEventListener("dragover", event => {
          event.preventDefault();
          const rect = card.getBoundingClientRect();
          const after = event.clientX > rect.left + rect.width / 2;
          cardsContainer.querySelectorAll(".card").forEach(item => item.classList.remove("drop-before", "drop-after"));
          card.classList.add(after ? "drop-after" : "drop-before");
        });
        card.addEventListener("drop", event => {
          event.preventDefault();
          if (!draggedCardKey || draggedCardKey === card.dataset.key) return;
          const rect = card.getBoundingClientRect();
          const after = event.clientX > rect.left + rect.width / 2;
          const withoutDragged = cardOrder.filter(key => key !== draggedCardKey);
          const targetIndex = withoutDragged.indexOf(card.dataset.key) + (after ? 1 : 0);
          withoutDragged.splice(targetIndex, 0, draggedCardKey);
          cardOrder = withoutDragged;
          render();
        });
      });
    }

    function renderTable(records) {
      const columns = ["id_estudiante", "nombre", "genero", "programa", "semestre_ingreso", "semestre_actual", "aplazamiento", "desercion_voluntaria", "bajo_rendimiento", "estado"];
      const sorted = [...records].sort((a, b) => String(a[sortColumn]).localeCompare(String(b[sortColumn]), "es", { numeric: true }) * sortDir);
      document.getElementById("rowCount").textContent = `${records.length} registros`;
      if (!sorted.length) {
        document.getElementById("studentTable").innerHTML = `<tbody><tr><td class="empty">No hay registros para los filtros actuales.</td></tr></tbody>`;
        return;
      }
      document.getElementById("studentTable").innerHTML = `
        <thead><tr>${columns.map(column => `<th data-column="${column}">${column}</th>`).join("")}</tr></thead>
        <tbody>${sorted.map(row => `<tr>${columns.map(column => `<td>${row[column]}</td>`).join("")}</tr>`).join("")}</tbody>`;
      document.querySelectorAll("th").forEach(th => th.addEventListener("click", () => {
        const column = th.dataset.column;
        sortDir = sortColumn === column ? sortDir * -1 : 1;
        sortColumn = column;
        renderTable(filteredStudents());
      }));
    }

    function render() {
      const records = filteredStudents();
      const context = controls.semester.value !== "Todos" ? controls.semester.value : controls.program.value;
      document.getElementById("heroTotal").textContent = records.length;
      document.getElementById("heroContext").textContent = context;
      renderCards(records);
      const lineSemesters = controls.semester.value !== "Todos" ? [controls.semester.value] : SEMESTERS;
      drawLine(document.getElementById("lineChart"), lineSemesters, lineSemesters.map(semester => records.filter(item => item.semestre_ingreso === semester).length));
      drawPie(document.getElementById("pieChart"), STATES, countBy(records, "estado", STATES));
      drawBar(
        document.getElementById("barChart"),
        PROGRAMS,
        PROGRAMS.map(program => records.filter(item => item.programa === program && item.desercion_voluntaria).length),
        PROGRAMS.map(program => records.filter(item => item.programa === program && item.bajo_rendimiento).length)
      );
      drawThreeD(document.getElementById("threeDChart"), records);
      renderTable(records);
    }

    function showEnrollmentPopup(semester) {
      const records = filteredStudents().filter(student => student.semestre_ingreso === semester);
      const counts = PROGRAMS.map(program => ({
        program,
        count: records.filter(student => student.programa === program).length
      }));
      const max = Math.max(1, ...counts.map(item => item.count));
      document.getElementById("modalTitle").textContent = `Inscripciones en ${semester}: ${records.length}`;
      document.getElementById("modalBody").innerHTML = counts.map(item => `
        <div class="breakdown-row">
          <div>
            <strong>${item.program}</strong>
            <div class="mini-bar"><span style="width:${Math.round(item.count / max * 100)}%"></span></div>
          </div>
          <div>${item.count}</div>
        </div>`).join("");
      document.getElementById("enrollmentModal").classList.add("open");
    }

    function showProgramMetricPopup(program, dropoutCount, riskCount) {
      document.getElementById("modalTitle").textContent = `Comparativa en ${program}`;
      document.getElementById("modalBody").innerHTML = `
        <p class="muted" style="margin-bottom:12px">Selecciona el indicador que quieres revisar para esta carrera.</p>
        <div class="metric-menu">
          <button type="button" id="metricDropout">Deserciones (${dropoutCount})</button>
          <button type="button" id="metricRisk">Bajo rendimiento (${riskCount})</button>
        </div>
        <div id="metricDetail"></div>`;
      document.getElementById("enrollmentModal").classList.add("open");
      document.getElementById("metricDropout").addEventListener("click", () => renderMetricDetail(program, "desercion_voluntaria", "Deserciones"));
      document.getElementById("metricRisk").addEventListener("click", () => renderMetricDetail(program, "bajo_rendimiento", "Bajo rendimiento"));
    }

    function renderMetricDetail(program, field, label) {
      const records = filteredStudents().filter(student => student.programa === program && student[field]);
      const counts = metricSemesterCounts(records);
      const max = Math.max(1, ...counts.map(item => item.count));
      document.getElementById("metricDetail").innerHTML = `
        <strong>${label}: ${records.length} estudiantes</strong>
        ${counts.map(item => `
          <div class="breakdown-row">
            <div>
              <strong>${item.semester}</strong>
              <div class="mini-bar"><span style="width:${Math.round(item.count / max * 100)}%"></span></div>
            </div>
            <div>${item.count}</div>
          </div>`).join("")}`;
    }

    function metricSemesterCounts(records) {
      if (controls.semester.value !== "Todos") {
        return [{ semester: controls.semester.value, count: records.length }];
      }
      return SEMESTERS.map(semester => ({
        semester,
        count: records.filter(student => student.semestre_actual === semester).length
      }));
    }

    function currentKpiItems(records) {
      const genderText = GENDERS.map(gender => `${gender}: ${records.filter(item => item.genero === gender).length}`).join(" / ");
      return [
        ["Total estudiantes", String(records.length)],
        ["Aplazamientos", percent(records, "aplazamiento")],
        ["Deserciones", percent(records, "desercion_voluntaria")],
        ["Bajo rendimiento", percent(records, "bajo_rendimiento")],
        ["Genero", genderText]
      ];
    }

    function makeReportCanvas(records) {
      const canvas = document.createElement("canvas");
      const width = 1600;
      const height = 2100;
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#f5f7fa";
      ctx.fillRect(0, 0, width, height);
      ctx.fillStyle = "#111a2e";
      ctx.fillRect(0, 0, width, 190);
      ctx.fillStyle = "#f8fafc";
      ctx.font = "bold 42px Segoe UI, Arial";
      ctx.fillText("Dashboard Estudiantil Universitario", 60, 76);
      ctx.fillStyle = "#9db0c9";
      ctx.font = "24px Segoe UI, Arial";
      ctx.fillText(`Reporte generado desde HTML - ${records.length} registros filtrados`, 60, 118);
      ctx.fillStyle = "#ffd166";
      ctx.font = "bold 24px Segoe UI, Arial";
      ctx.fillText(`Contexto: ${document.getElementById("heroContext").textContent}`, 60, 154);

      currentKpiItems(records).forEach((item, index) => {
        const x = 60 + index * 296;
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x, 230, 270, 128);
        ctx.strokeStyle = "#e2e8f0";
        ctx.strokeRect(x, 230, 270, 128);
        ctx.fillStyle = "#718096";
        ctx.font = "bold 18px Segoe UI, Arial";
        ctx.fillText(item[0], x + 18, 270);
        ctx.fillStyle = "#2d3748";
        ctx.font = "bold 28px Segoe UI, Arial";
        wrapText(ctx, item[1], x + 18, 316, 230, 31);
      });

      const charts = [
        ["Evolucion de inscripciones", "lineChart", 60, 420],
        ["Distribucion por estado", "pieChart", 830, 420],
        ["Comparativa entre carreras", "barChart", 60, 790],
        ["Mapa 3D de riesgo academico", "threeDChart", 830, 790]
      ];
      charts.forEach(([title, id, x, y]) => {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(x, y, 710, 318);
        ctx.strokeStyle = "#e2e8f0";
        ctx.strokeRect(x, y, 710, 318);
        ctx.fillStyle = "#2d3748";
        ctx.font = "bold 22px Segoe UI, Arial";
        ctx.fillText(title, x + 18, y + 34);
        const source = document.getElementById(id);
        ctx.drawImage(source, x + 18, y + 52, 674, 242);
      });

      ctx.fillStyle = "#2d3748";
      ctx.font = "bold 26px Segoe UI, Arial";
      ctx.fillText("Detalle de estudiantes", 60, 1180);
      drawReportTable(ctx, records.slice(0, 32), 60, 1210, 1480);
      ctx.fillStyle = "#718096";
      ctx.font = "18px Segoe UI, Arial";
      const remaining = Math.max(0, records.length - 32);
      ctx.fillText(remaining ? `Se muestran 32 filas en el reporte visual. Total filtrado: ${records.length}.` : `Total filtrado: ${records.length}.`, 60, 2048);
      return canvas;
    }

    function drawReportTable(ctx, records, x, y, width) {
      const columns = [
        ["id_estudiante", 90],
        ["nombre", 260],
        ["genero", 90],
        ["programa", 330],
        ["semestre_ingreso", 150],
        ["semestre_actual", 150],
        ["estado", 150],
        ["bajo_rendimiento", 180]
      ];
      ctx.fillStyle = "#1d3557";
      ctx.fillRect(x, y, width, 36);
      ctx.fillStyle = "#ffd166";
      ctx.font = "bold 16px Segoe UI, Arial";
      let currentX = x + 8;
      columns.forEach(([column, colWidth]) => {
        ctx.fillText(column, currentX, y + 24);
        currentX += colWidth;
      });
      ctx.font = "15px Segoe UI, Arial";
      records.forEach((row, index) => {
        const rowY = y + 36 + index * 24;
        ctx.fillStyle = index % 2 ? "#ffffff" : "#edf2f7";
        ctx.fillRect(x, rowY, width, 24);
        ctx.fillStyle = "#2d3748";
        currentX = x + 8;
        columns.forEach(([column, colWidth]) => {
          const value = String(row[column]).slice(0, Math.floor(colWidth / 9));
          ctx.fillText(value, currentX, rowY + 17);
          currentX += colWidth;
        });
      });
      ctx.strokeStyle = "#e2e8f0";
      ctx.strokeRect(x, y, width, 36 + records.length * 24);
    }

    function wrapText(ctx, text, x, y, maxWidth, lineHeight) {
      const words = String(text).split(" ");
      let line = "";
      words.forEach(word => {
        const testLine = line ? `${line} ${word}` : word;
        if (ctx.measureText(testLine).width > maxWidth && line) {
          ctx.fillText(line, x, y);
          line = word;
          y += lineHeight;
        } else {
          line = testLine;
        }
      });
      if (line) ctx.fillText(line, x, y);
    }

    function exportJpg() {
      render();
      const canvas = makeReportCanvas(filteredStudents());
      const link = document.createElement("a");
      link.download = `dashboard_universitario_${new Date().toISOString().slice(0, 10)}.jpg`;
      link.href = canvas.toDataURL("image/jpeg", .92);
      link.click();
    }

    function exportPdf() {
      render();
      const canvas = makeReportCanvas(filteredStudents());
      const image = canvas.toDataURL("image/jpeg", .92);
      const printWindow = window.open("", "_blank");
      if (!printWindow) {
        alert("El navegador bloqueo la ventana de exportacion. Permite ventanas emergentes para generar el PDF.");
        return;
      }
      printWindow.document.write(`
        <!doctype html>
        <html>
        <head>
          <title>Reporte PDF Dashboard Universitario</title>
          <style>
            @page { size: A4 portrait; margin: 10mm; }
            body { margin: 0; background: #f5f7fa; }
            img { width: 100%; display: block; }
          </style>
        </head>
        <body>
          <img src="${image}" alt="Reporte Dashboard Universitario">
          <script>
            window.onload = () => {
              window.focus();
              window.print();
            };
          <\/script>
        </body>
        </html>`);
      printWindow.document.close();
    }

    function clearAllFilters() {
      controls.search.value = "";
      controls.program.value = "Todos";
      controls.semester.value = "Todos";
      controls.gender.value = "Todos";
      controls.state.value = "Todos";
      controls.delay.checked = false;
      controls.dropout.checked = false;
      controls.risk.checked = false;
      render();
    }

    fillSelect(controls.program, PROGRAMS);
    fillSelect(controls.semester, SEMESTERS);
    fillSelect(controls.gender, GENDERS);
    fillSelect(controls.state, STATES);
    Object.values(controls).forEach(control => control.addEventListener("input", render));
    Object.values(controls).forEach(control => control.addEventListener("change", render));
    document.getElementById("exportJpg").addEventListener("click", exportJpg);
    document.getElementById("exportPdf").addEventListener("click", exportPdf);
    document.getElementById("clearFilters").addEventListener("click", clearAllFilters);
    document.getElementById("modalClose").addEventListener("click", () => document.getElementById("enrollmentModal").classList.remove("open"));
    document.getElementById("enrollmentModal").addEventListener("click", event => {
      if (event.target.id === "enrollmentModal") event.target.classList.remove("open");
    });
    window.addEventListener("resize", render);
    render();
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    print(build_dashboard())
