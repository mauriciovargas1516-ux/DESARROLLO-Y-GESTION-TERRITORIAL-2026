# -*- coding: utf-8 -*-
"""
motor_fluidez_territorial_60fps.py — LABORATORIO TERRITORIAL FLUIDO A 60 FPS CON FLECHAS Y RASTRO FANTASMA
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Extensión modular independiente para DESARROLLO-Y-GESTION-TERRITORIAL-2026.

Renderiza en el navegador (HTML5 SVG + JavaScript sin recarga de servidor):
  1) Von Thünen: Gradiente de Renta Locacional LR(d) + Mapa de Anillos Concéntricos en Vivo.
  2) Alfred Weber: Triángulo Locacional, Índice de Materiales (IM), Vectores de Tracción e Isodápana Crítica.
  3) Paul Krugman (1991): Bifurcación Centro-Periferia, Umbral τ* y Flujo de Macrocefalia Regional.
  4) Disparidades REAT y OT: Curva de Lorenz, Gini y Primacía Urbana (IP4 escala 0-3) en Tiempo Real.
"""

import streamlit as st
import streamlit.components.v1 as components


HTML_TERRITORIAL_60FPS = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
  body { margin: 0; padding: 0; background: #F8FAFC; color: #0F172A; }
  .wrap { max-width: 1220px; margin: 0 auto; padding: 6px 4px 14px 4px; }
  .top-tabs { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  .tab-btn {
    border: 1px solid #CBD5E1; background: #FFFFFF; color: #334155;
    padding: 8px 13px; border-radius: 6px; font-weight: 700; font-size: 12.5px;
    cursor: pointer; transition: all 0.15s ease;
  }
  .tab-btn:hover { border-color: #1D4ED8; color: #1D4ED8; background: #EFF6FF; }
  .tab-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .panel { display: none; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 16px; }
  .panel.active { display: block; }
  .sec-title {
    font-size: 13px; font-weight: 700; color: #1E3A8A;
    background: #DBEAFE; border-left: 4px solid #1D4ED8;
    padding: 7px 12px; border-radius: 4px; margin-bottom: 12px;
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
  }
  .btn-bar { display: flex; gap: 6px; flex-wrap: wrap; }
  .act-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #0F172A;
    padding: 5px 10px; border-radius: 5px; font-size: 11.5px; font-weight: 700; cursor: pointer;
  }
  .act-btn:hover { background: #EFF6FF; border-color: #1D4ED8; color: #1D4ED8; }
  .act-btn.primary { background: #1D4ED8; color: #FFFFFF; border-color: #1D4ED8; }
  .act-btn.primary:hover { background: #1E40AF; }
  .sliders-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap: 10px; margin-bottom: 12px; }
  .sl-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 10px; }
  .sl-head { display: flex; justify-content: space-between; font-size: 11.5px; font-weight: 700; color: #1E293B; margin-bottom: 4px; gap: 4px; }
  .sl-val { color: #1D4ED8; font-family: Consolas, monospace; white-space: nowrap; }
  .sl-delta { font-size: 10.5px; font-weight: 700; margin-left: 4px; }
  .d-up { color: #15803D; }
  .d-down { color: #DC2626; }
  .d-eq { color: #64748B; }
  input[type="range"] { width: 100%; accent-color: #1D4ED8; cursor: pointer; margin: 2px 0; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 8px; margin-bottom: 10px; }
  .kpi { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 3px solid #0F172A; border-radius: 5px; padding: 7px 10px; }
  .kpi-lbl { font-size: 11px; color: #475569; font-weight: 600; }
  .kpi-val { font-size: 14.5px; font-weight: 800; color: #0F172A; font-family: Consolas, monospace; margin-top: 2px; }
  .kpi-sub { font-size: 11px; color: #334155; margin-top: 1px; }
  .svg-box { width: 100%; border: 1px solid #E2E8F0; border-radius: 6px; background: #FFFFFF; overflow: hidden; }
  svg { width: 100%; height: auto; display: block; }
  .legend-bar {
    display: flex; gap: 14px; flex-wrap: wrap; font-size: 11.5px; color: #334155;
    margin-top: 8px; padding: 6px 10px; background: #F8FAFC; border-radius: 5px; border: 1px solid #E2E8F0;
  }
  .leg-item { display: inline-flex; align-items: center; gap: 5px; font-weight: 600; }
  .sw { width: 12px; height: 12px; border-radius: 2px; display: inline-block; }
  .sw-line { width: 16px; height: 3px; display: inline-block; }
  .note-box {
    margin-top: 8px; padding: 8px 12px; border-radius: 5px; font-size: 12.2px; line-height: 1.42;
    background: #EFF6FF; border-left: 4px solid #1D4ED8; color: #1E293B;
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="top-tabs">
    <button class="tab-btn active" onclick="openTab('thunen', this)">1. Von Thünen (Anillos + Gradiente LR)</button>
    <button class="tab-btn" onclick="openTab('weber', this)">2. Weber (Triángulo, IM e Isodápana)</button>
    <button class="tab-btn" onclick="openTab('krugman', this)">3. Krugman (Centro-Periferia y Umbral τ*)</button>
    <button class="tab-btn" onclick="openTab('lorenz', this)">4. Lorenz, Gini y Primacía Urbana (IP4)</button>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 1: VON THÜNEN (RENTA LOCACIONAL + ANILLOS CONCÉNTRICOS)          -->
  <!-- ====================================================================== -->
  <div id="panel-thunen" class="panel active">
    <div class="sec-title">
      <span>VON THÜNEN EN VIVO (60 FPS): RENTA LOCACIONAL LR(d) = Y(m - c) - Y·t·d Y ANILLOS CONCÉNTRICOS</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarThunen()">Reproducir Baja de Flete Lechero</button>
        <button class="act-btn" onclick="fijarGhostThunen()">Fijar Fantasma Aquí</button>
        <button class="act-btn" onclick="resetThunen()">Restaurar Base Osorno</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>1. Margen Lechería/Hortalizas</span><span><span id="vt-m1-v" class="sl-val">120</span><span id="vt-m1-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-m1" type="range" min="60" max="170" step="2" value="120" oninput="drawThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>1. Flete Lechería (t1)</span><span><span id="vt-t1-v" class="sl-val">4,5</span><span id="vt-t1-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-t1" type="range" min="1.5" max="7.5" step="0.1" value="4.5" oninput="drawThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>2. Margen Agroindustria</span><span><span id="vt-m2-v" class="sl-val">85</span><span id="vt-m2-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-m2" type="range" min="45" max="135" step="2" value="85" oninput="drawThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>2. Flete Agroindustria (t2)</span><span><span id="vt-t2-v" class="sl-val">2,0</span><span id="vt-t2-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-t2" type="range" min="0.8" max="4.5" step="0.1" value="2.0" oninput="drawThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>3. Flete Forestal Extensiva (t3)</span><span><span id="vt-t3-v" class="sl-val">0,8</span><span id="vt-t3-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-t3" type="range" min="0.4" max="2.2" step="0.05" value="0.8" oninput="drawThunen()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Anillo 1: Lechería / Hortalizas</div><div id="vt-k-r1" class="kpi-val">0 → 14,0 km</div><div id="vt-k-r1d" class="kpi-sub">Frontera con Agroindustria</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Anillo 2: Agroindustria / Cultivos</div><div id="vt-k-r2" class="kpi-val">14,0 → 29,2 km</div><div id="vt-k-r2d" class="kpi-sub">Frontera con Forestal</div></div>
      <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Anillo 3: Forestal / Extensiva</div><div id="vt-k-r3" class="kpi-val">29,2 → 62,5 km</div><div id="vt-k-r3d" class="kpi-sub">Límite de Renta Nula (LR=0)</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Movimiento vs. Fantasma</div><div id="vt-k-mov" class="kpi-val">Referencia base</div><div id="vt-k-mov2" class="kpi-sub">Mueve un margen o flete</div></div>
    </div>

    <div class="svg-box"><svg id="svg-thunen" viewBox="0 0 980 400"></svg></div>
    <div class="legend-bar">
      <span class="leg-item"><span class="sw" style="background:rgba(220,38,38,0.28);border:1px solid #DC2626;"></span>Anillo 1: Intensiva / Lechería</span>
      <span class="leg-item"><span class="sw" style="background:rgba(29,78,216,0.24);border:1px solid #1D4ED8;"></span>Anillo 2: Agroindustria / Cultivos</span>
      <span class="leg-item"><span class="sw" style="background:rgba(5,150,105,0.24);border:1px solid #059669;"></span>Anillo 3: Forestal / Extensiva</span>
      <span class="leg-item"><span class="sw-line" style="border-top:2px dashed #94A3B8;"></span>Rastro Fantasma (Anillo anterior)</span>
    </div>
    <div class="note-box"><b>Lectura de cátedra (Duch Brown / Mancilla):</b> Cada actividad ocupa el anillo donde ofrece la mayor renta locacional <b>LR(d)</b>. Al bajar el costo de transporte (<b>t1</b>) o subir el margen neto, observa cómo las flechas empujan hacia afuera el borde del anillo tanto en la curva (izquierda) como en el mapa espacial (derecha).</div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 2: WEBER (TRIÁNGULO LOCACIONAL, IM E ISODÁPANA CRÍTICA)          -->
  <!-- ====================================================================== -->
  <div id="panel-weber" class="panel">
    <div class="sec-title">
      <span>WEBER EN VIVO (60 FPS): TRIÁNGULO LOCACIONAL, ÍNDICE DE MATERIALES (IM) E ISODÁPANA CRÍTICA</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarWeber()">Reproducir Aumento de IM</button>
        <button class="act-btn" onclick="presetWeber(45, 35, 35, 30)">IM &gt; 1 (Aserradero/Insumos)</button>
        <button class="act-btn" onclick="presetWeber(15, 15, 70, 30)">IM &lt; 1 (Bebidas/Mercado)</button>
        <button class="act-btn" onclick="presetWeber(25, 25, 45, 135)">Salto a Enclave Laboral L</button>
        <button class="act-btn" onclick="fijarGhostWeber()">Fijar Fantasma</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Peso MP1 Localizada (W1)</span><span id="wb-w1-v" class="sl-val">40 t</span></div>
        <input id="wb-w1" type="range" min="5" max="80" step="1" value="40" oninput="drawWeber()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Peso MP2 Localizada (W2)</span><span id="wb-w2-v" class="sl-val">30 t</span></div>
        <input id="wb-w2" type="range" min="5" max="80" step="1" value="30" oninput="drawWeber()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Peso Producto Final (WM)</span><span id="wb-wm-v" class="sl-val">40 t</span></div>
        <input id="wb-wm" type="range" min="10" max="90" step="1" value="40" oninput="drawWeber()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Ahorro Laboral en Enclave L</span><span id="wb-ah-v" class="sl-val">$55 / unid</span></div>
        <input id="wb-ah" type="range" min="0" max="180" step="5" value="55" oninput="drawWeber()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Índice de Materiales (IM)</div><div id="wb-k-im" class="kpi-val">1,75</div><div id="wb-k-ori" class="kpi-sub">IM &gt; 1: Orientada a Insumos</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Costo Transporte Mínimo en P*</div><div id="wb-k-ct" class="kpi-val">$248,1</div><div class="kpi-sub">Óptimo puro de transporte</div></div>
      <div class="kpi" style="border-left-color:#EA580C;"><div class="kpi-lbl">Sobre-costo Transporte hasta L</div><div id="wb-k-dl" class="kpi-val">+$98,4</div><div id="wb-k-iso" class="kpi-sub">Radio Isodápana Crítica</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Decisión Locacional Final</div><div id="wb-k-dec" class="kpi-val">Permanecer en P*</div><div id="wb-k-dec2" class="kpi-sub">L fuera de Isodápana Crítica</div></div>
    </div>

    <div class="svg-box"><svg id="svg-weber" viewBox="0 0 980 410"></svg></div>
    <div class="legend-bar">
      <span class="leg-item"><span class="sw" style="background:#0F172A;"></span>P* Óptimo de Transporte</span>
      <span class="leg-item"><span class="sw" style="background:rgba(21,128,61,0.16);border:1.5px dashed #15803D;"></span>Isodápana Crítica (Ahorro salarial = Sobre-costo flete)</span>
      <span class="leg-item"><span class="sw-line" style="background:#1D4ED8;"></span>Vectores de Tracción (W1, W2, WM)</span>
      <span class="leg-item"><span class="sw-line" style="background:#DC2626;"></span>Flecha de Desplazamiento desde Fantasma P*</span>
    </div>
    <div id="wb-note" class="note-box"><b>Regla de examen (Duch Brown / Mancilla):</b> Si <b>IM &gt; 1</b> (pérdida de peso en el proceso, ej. aserradero o lácteos en polvo), la planta se acerca a las materias primas; si <b>IM &lt; 1</b> (ganancia de peso/ubicuos), se pega al mercado. La fábrica solo salta al Enclave Laboral <b>L</b> si cae <b>dentro de la Isodápana Crítica</b>.</div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 3: KRUGMAN 1991 (BIFURCACIÓN CENTRO-PERIFERIA Y MACROCEFALIA)    -->
  <!-- ====================================================================== -->
  <div id="panel-krugman" class="panel">
    <div class="sec-title">
      <span>KRUGMAN (1991) EN VIVO (60 FPS): BIFURCACIÓN CENTRO-PERIFERIA, UMBRAL τ* Y MACROCEFALIA</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarKrugman()">Reproducir Baja de Fletes (τ: 10 → 1)</button>
        <button class="act-btn" onclick="fijarGhostKrugman()">Fijar Fantasma Aquí</button>
        <button class="act-btn" onclick="resetKrugman()">Restaurar Base</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Costo de Transporte (τ)</span><span><span id="kr-tau-v" class="sl-val">3,5</span><span id="kr-tau-d" class="sl-delta d-eq"></span></span></div>
        <input id="kr-tau" type="range" min="1.0" max="10.0" step="0.1" value="3.5" oninput="drawKrugman()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Economías de Escala (1 a 10)</span><span id="kr-esc-v" class="sl-val">7,0</span></div>
        <input id="kr-esc" type="range" min="1.0" max="10.0" step="0.2" value="7.0" oninput="drawKrugman()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Movilidad Laboral (1 a 10)</span><span id="kr-mov-v" class="sl-val">6,5</span></div>
        <input id="kr-mov" type="range" min="1.0" max="10.0" step="0.2" value="6.5" oninput="drawKrugman()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#D97706;"><div class="kpi-lbl">Umbral Crítico (τ*)</div><div id="kr-k-ust" class="kpi-val">5,43</div><div class="kpi-sub">Punto de bifurcación espacial</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Cuota Capital Regional (Centro)</div><div id="kr-k-cen" class="kpi-val">89,1%</div><div id="kr-k-reg" class="kpi-sub">Régimen de Aglomeración</div></div>
      <div class="kpi" style="border-left-color:#64748B;"><div class="kpi-lbl">Cuota Comunas Periféricas</div><div id="kr-k-per" class="kpi-val">10,9%</div><div id="kr-k-per2" class="kpi-sub">Respecto a simetría (50%)</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Fuerza Predominante</div><div id="kr-k-fza" class="kpi-val">Centrípeta → Centro</div><div id="kr-k-fza2" class="kpi-sub">τ ≤ τ* dispara macrocefalia</div></div>
    </div>

    <div class="svg-box"><svg id="svg-krugman" viewBox="0 0 980 390"></svg></div>
    <div class="note-box"><b>Intuición espacial:</b> Presiona <b>Reproducir Baja de Fletes (τ: 10 → 1)</b> para ver cómo al cruzar el umbral crítico <b>τ*</b> se activan las flechas migratorias desde la periferia hacia la capital regional, concentrando empresas y empleo en el núcleo metropolitano.</div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 4: LORENZ, GINI Y PRIMACÍA URBANA (IP4 ESCALA 0-3)               -->
  <!-- ====================================================================== -->
  <div id="panel-lorenz" class="panel">
    <div class="sec-title">
      <span>DISPARIDADES REAT Y OT EN VIVO (60 FPS): CURVA DE LORENZ, GINI Y PRIMACÍA URBANA (IP4)</span>
      <div class="btn-bar">
        <button class="act-btn" onclick="presetLorenz('lagos')">Los Lagos (Censo 2024)</button>
        <button class="act-btn" onclick="presetLorenz('biobio')">Biobío (Censo 2024)</button>
        <button class="act-btn" onclick="presetLorenz('mancilla')">Ejemplo Mancilla (Lám. 12)</button>
        <button class="act-btn" onclick="fijarGhostLorenz()">Fijar Fantasma Aquí</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l1">Ciudad 1 (P1 - Capital)</span><span id="lz-p1-v" class="sl-val">275.473</span></div>
        <input id="lz-p1" type="range" min="1000" max="600000" step="1000" value="275473" oninput="drawLorenz()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l2">Ciudad 2 (P2)</span><span id="lz-p2-v" class="sl-val">174.998</span></div>
        <input id="lz-p2" type="range" min="500" max="350000" step="500" value="174998" oninput="drawLorenz()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l3">Ciudad 3 (P3)</span><span id="lz-p3-v" class="sl-val">50.010</span></div>
        <input id="lz-p3" type="range" min="100" max="250000" step="500" value="50010" oninput="drawLorenz()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l4">Ciudad 4 (P4)</span><span id="lz-p4-v" class="sl-val">48.632</span></div>
        <input id="lz-p4" type="range" min="50" max="200000" step="500" value="48632" oninput="drawLorenz()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Índice de Primacía (IP4)</div><div id="lz-k-ip4" class="kpi-val">1,007</div><div id="lz-k-ip2" class="kpi-sub">IP2 (P1/P2) = 1,574</div></div>
      <div class="kpi" style="border-left-color:#D97706;"><div class="kpi-lbl">Estandarización OT (0 a 3)</div><div id="lz-k-cat" class="kpi-val">Valor 2: Concentrada</div><div class="kpi-sub">Escala 06 OT 2024.pdf</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Índice de Gini (G)</div><div id="lz-k-gini" class="kpi-val">0,432</div><div id="lz-k-dgini" class="kpi-sub">ΔG vs Fantasma: 0,000</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Cuota Capital Regional (P1)</div><div id="lz-k-cuota" class="kpi-val">50,2%</div><div class="kpi-sub">Sobre suma Top 4</div></div>
    </div>

    <div class="svg-box"><svg id="svg-lorenz" viewBox="0 0 980 390"></svg></div>
    <div class="note-box"><b>Conexión Unidades 3 y 5:</b> Al aumentar la población de la capital regional <b>P1</b>, observa cómo las flechas empujan la Curva de Lorenz alejándola de la diagonal de equidad (sube el Gini) y cómo el marcador de <b>Primacía IP4</b> cruza los umbrales de cátedra (0,65 | 1,00 | 1,50).</div>
  </div>
</div>

<script>
const NS = "http://www.w3.org/2000/svg";
function fmtInt(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, "."); }
function fmtDec(n, d=1) {
  const s = Number(n).toFixed(d).split(".");
  return s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ".") + (d > 0 ? "," + s[1] : "");
}
function el(tag, attrs, parent) {
  const node = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs || {})) node.setAttribute(k, v);
  if (parent) parent.appendChild(node);
  return node;
}
function addDefs(svg) {
  const defs = el("defs", {}, svg);
  const colors = [
    ["arr-red", "#DC2626"], ["arr-blue", "#1D4ED8"], ["arr-green", "#15803D"],
    ["arr-orange", "#EA580C"], ["arr-dark", "#0F172A"]
  ];
  for (const [id, col] of colors) {
    const m = el("marker", { id, viewBox: "0 0 10 10", refX: "8", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" }, defs);
    el("path", { d: "M 0 1 L 10 5 L 0 9 z", fill: col }, m);
  }
}
function drawArrow(svg, x1, y1, x2, y2, color, markerId, label, lx, ly, anchor="middle") {
  const dist = Math.hypot(x2 - x1, y2 - y1);
  if (dist < 6) return;
  el("line", { x1, y1, x2, y2, stroke: color, "stroke-width": "2.6", "marker-end": `url(#${markerId})` }, svg);
  if (label) {
    const bgW = Math.max(52, label.length * 6.5 + 10);
    const rx = anchor === "middle" ? lx - bgW / 2 : (anchor === "start" ? lx - 4 : lx - bgW + 4);
    el("rect", { x: rx, y: ly - 12, width: bgW, height: 17, rx: 4, fill: "rgba(255,255,255,0.94)", stroke: color, "stroke-width": "1" }, svg);
    const t = el("text", { x: lx, y: ly, fill: color, "font-size": "10.8", "font-weight": "700", "text-anchor": anchor }, svg);
    t.textContent = label;
  }
}
function setDelta(id, diff, dec=1) {
  const node = document.getElementById(id);
  if (!node) return;
  if (Math.abs(diff) < 1e-4) { node.textContent = ""; node.className = "sl-delta d-eq"; return; }
  node.textContent = `(${diff > 0 ? "↑ +" : "↓ -"}${fmtDec(Math.abs(diff), dec)})`;
  node.className = "sl-delta " + (diff > 0 ? "d-up" : "d-down");
}
function openTab(name, btn) {
  document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("panel-" + name).classList.add("active");
  btn.classList.add("active");
  if (name === "thunen") drawThunen();
  if (name === "weber") drawWeber();
  if (name === "krugman") drawKrugman();
  if (name === "lorenz") drawLorenz();
}

// ============================================================================
// 1. VON THÜNEN (GRADIENTE 2D + MAPA DE ANILLOS CONCÉNTRICOS)
// ============================================================================
let ghostVt = { m1: 120, t1: 4.5, m2: 85, t2: 2.0, m3: 50, t3: 0.8 };
let animVtId = null;

function fijarGhostThunen() {
  ghostVt = {
    m1: +document.getElementById("vt-m1").value,
    t1: +document.getElementById("vt-t1").value,
    m2: +document.getElementById("vt-m2").value,
    t2: +document.getElementById("vt-t2").value,
    m3: 50,
    t3: +document.getElementById("vt-t3").value,
  };
  drawThunen();
}
function resetThunen() {
  if (animVtId) cancelAnimationFrame(animVtId);
  document.getElementById("vt-m1").value = 120;
  document.getElementById("vt-t1").value = 4.5;
  document.getElementById("vt-m2").value = 85;
  document.getElementById("vt-t2").value = 2.0;
  document.getElementById("vt-t3").value = 0.8;
  ghostVt = { m1: 120, t1: 4.5, m2: 85, t2: 2.0, m3: 50, t3: 0.8 };
  drawThunen();
}
function animarThunen() {
  if (animVtId) cancelAnimationFrame(animVtId);
  const startT1 = 6.0, endT1 = 2.6;
  document.getElementById("vt-t1").value = startT1;
  fijarGhostThunen();
  const t0 = performance.now(), dur = 1800;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    document.getElementById("vt-t1").value = (startT1 + (endT1 - startT1) * ease).toFixed(2);
    drawThunen();
    if (u < 1) animVtId = requestAnimationFrame(step);
  }
  animVtId = requestAnimationFrame(step);
}
function calcRadiosThunen(s) {
  const d10 = s.m1 / s.t1;
  const d20 = s.m2 / s.t2;
  const d30 = s.m3 / s.t3;
  // Cálculo exacto por envolvente superior LR*(d) = max(LR1, LR2, LR3, 0)
  let r1 = 0, r2 = 0, r3 = 0;
  const step = 0.2;
  for (let d = 0; d <= 70; d += step) {
    const l1 = Math.max(0, s.m1 - s.t1 * d);
    const l2 = Math.max(0, s.m2 - s.t2 * d);
    const l3 = Math.max(0, s.m3 - s.t3 * d);
    const mx = Math.max(l1, l2, l3);
    if (mx <= 0) break;
    if (l1 >= l2 && l1 >= l3) { r1 = d; r2 = Math.max(r2, d); r3 = Math.max(r3, d); }
    else if (l2 >= l1 && l2 >= l3) { r2 = d; r3 = Math.max(r3, d); }
    else { r3 = d; }
  }
  return { r1, r2, r3, d10, d20, d30 };
}
function drawThunen() {
  const s = {
    m1: +document.getElementById("vt-m1").value,
    t1: +document.getElementById("vt-t1").value,
    m2: +document.getElementById("vt-m2").value,
    t2: +document.getElementById("vt-t2").value,
    m3: 50,
    t3: +document.getElementById("vt-t3").value,
  };
  document.getElementById("vt-m1-v").textContent = fmtInt(s.m1);
  document.getElementById("vt-t1-v").textContent = fmtDec(s.t1, 1);
  document.getElementById("vt-m2-v").textContent = fmtInt(s.m2);
  document.getElementById("vt-t2-v").textContent = fmtDec(s.t2, 1);
  document.getElementById("vt-t3-v").textContent = fmtDec(s.t3, 2);
  setDelta("vt-m1-d", s.m1 - ghostVt.m1, 0);
  setDelta("vt-t1-d", s.t1 - ghostVt.t1, 1);
  setDelta("vt-m2-d", s.m2 - ghostVt.m2, 0);
  setDelta("vt-t2-d", s.t2 - ghostVt.t2, 1);
  setDelta("vt-t3-d", s.t3 - ghostVt.t3, 2);

  const cur = calcRadiosThunen(s);
  const gho = calcRadiosThunen(ghostVt);
  document.getElementById("vt-k-r1").textContent = `0 → ${fmtDec(cur.r1, 1)} km`;
  document.getElementById("vt-k-r2").textContent = `${fmtDec(cur.r1, 1)} → ${fmtDec(cur.r2, 1)} km`;
  document.getElementById("vt-k-r3").textContent = `${fmtDec(cur.r2, 1)} → ${fmtDec(cur.r3, 1)} km`;
  const dr1 = cur.r1 - gho.r1;
  const dr3 = cur.r3 - gho.r3;
  if (Math.abs(dr1) >= 0.3) {
    document.getElementById("vt-k-mov").textContent = dr1 > 0 ? `→ Anillo 1 +${fmtDec(dr1, 1)} km` : `← Anillo 1 -${fmtDec(Math.abs(dr1), 1)} km`;
    document.getElementById("vt-k-mov2").textContent = dr1 > 0 ? "Lechería gana territorio rural" : "Agroindustria avanza hacia el centro";
  } else if (Math.abs(dr3) >= 0.3) {
    document.getElementById("vt-k-mov").textContent = dr3 > 0 ? `→ Frontera +${fmtDec(dr3, 1)} km` : `← Frontera -${fmtDec(Math.abs(dr3), 1)} km`;
    document.getElementById("vt-k-mov2").textContent = "Cambio en radio agrícola total";
  } else {
    document.getElementById("vt-k-mov").textContent = "En referencia fantasma";
    document.getElementById("vt-k-mov2").textContent = "Mueve un margen o flete";
  }

  const svg = document.getElementById("svg-thunen");
  svg.innerHTML = "";
  addDefs(svg);

  // IZQUIERDA: Curvas de Renta LR(d)
  const M = { l: 55, r: 420, t: 30, b: 48 };
  const W = 980, H = 400, maxD = 70, maxR = 175;
  const sx = d => M.l + (d / maxD) * (W - M.l - M.r);
  const sy = r => H - M.b - (r / maxR) * (H - M.t - M.b);

  for (let y = 0; y <= 160; y += 40) {
    el("line", { x1: M.l, y1: sy(y), x2: W - M.r, y2: sy(y), stroke: "#E2E8F0" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(y) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = y;
  }
  for (let d = 0; d <= 70; d += 10) {
    el("line", { x1: sx(d), y1: M.t, x2: sx(d), y2: H - M.b, stroke: "#F1F5F9" }, svg);
    const t = el("text", { x: sx(d), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    t.textContent = d + " km";
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  // Áreas sombreadas de cada anillo bajo la envolvente superior
  if (cur.r1 > 0.2) {
    const rAt1 = Math.max(0, s.m1 - s.t1 * cur.r1);
    el("polygon", { points: `${sx(0)},${sy(0)} ${sx(cur.r1)},${sy(0)} ${sx(cur.r1)},${sy(rAt1)} ${sx(0)},${sy(s.m1)}`, fill: "rgba(220,38,38,0.18)" }, svg);
  }
  if (cur.r2 > cur.r1 + 0.2) {
    const rA = Math.max(0, s.m2 - s.t2 * cur.r1), rB = Math.max(0, s.m2 - s.t2 * cur.r2);
    el("polygon", { points: `${sx(cur.r1)},${sy(0)} ${sx(cur.r2)},${sy(0)} ${sx(cur.r2)},${sy(rB)} ${sx(cur.r1)},${sy(rA)}`, fill: "rgba(29,78,216,0.16)" }, svg);
  }
  if (cur.r3 > cur.r2 + 0.2) {
    const rA = Math.max(0, s.m3 - s.t3 * cur.r2);
    el("polygon", { points: `${sx(cur.r2)},${sy(0)} ${sx(cur.r3)},${sy(0)} ${sx(cur.r2)},${sy(rA)}`, fill: "rgba(5,150,105,0.16)" }, svg);
  }

  // Fantasma de curva 1 si cambió
  if (Math.abs(s.m1 - ghostVt.m1) > 0.5 || Math.abs(s.t1 - ghostVt.t1) > 0.05) {
    el("line", { x1: sx(0), y1: sy(ghostVt.m1), x2: sx(Math.min(maxD, ghostVt.m1 / ghostVt.t1)), y2: sy(Math.max(0, ghostVt.m1 - ghostVt.t1 * maxD)), stroke: "#94A3B8", "stroke-width": "1.6", "stroke-dasharray": "5,4" }, svg);
  }
  // Curvas actuales
  const drawRentLine = (m, t, col) => {
    const dZero = Math.min(maxD, m / t);
    const yEnd = Math.max(0, m - t * dZero);
    el("line", { x1: sx(0), y1: sy(m), x2: sx(dZero), y2: sy(yEnd), stroke: col, "stroke-width": "2.6" }, svg);
  };
  drawRentLine(s.m1, s.t1, "#DC2626");
  drawRentLine(s.m2, s.t2, "#1D4ED8");
  drawRentLine(s.m3, s.t3, "#059669");

  // Flecha vectorial de desplazamiento de frontera r1 vs fantasma
  if (Math.abs(dr1) >= 0.4) {
    const colA = dr1 > 0 ? "#15803D" : "#DC2626";
    const mk = dr1 > 0 ? "arr-green" : "arr-red";
    drawArrow(svg, sx(gho.r1), sy(142), sx(cur.r1), sy(142), colA, mk, `${dr1 > 0 ? "→ +" : "← -"}${fmtDec(Math.abs(dr1), 1)} km`, (sx(gho.r1) + sx(cur.r1)) / 2, sy(153));
  }

  // DERECHA: Mapa Espacial de Anillos Concéntricos
  const cx = 775, cy = 205, maxPixR = 160;
  const sr = km => (Math.min(km, 70) / 70) * maxPixR;
  const tMap = el("text", { x: cx, y: 24, fill: "#0F172A", "font-size": "12", "font-weight": "700", "text-anchor": "middle" }, svg);
  tMap.textContent = "Mapa Espacial de Anillos Concéntricos (Ciudad al Centro)";

  el("circle", { cx, cy, r: sr(cur.r3), fill: "rgba(5,150,105,0.22)", stroke: "#059669", "stroke-width": "1.8" }, svg);
  el("circle", { cx, cy, r: sr(cur.r2), fill: "rgba(29,78,216,0.24)", stroke: "#1D4ED8", "stroke-width": "1.8" }, svg);
  el("circle", { cx, cy, r: sr(cur.r1), fill: "rgba(220,38,38,0.28)", stroke: "#DC2626", "stroke-width": "2" }, svg);

  // Anillo fantasma del borde 1
  if (Math.abs(dr1) >= 0.4) {
    el("circle", { cx, cy, r: sr(gho.r1), fill: "none", stroke: "#64748B", "stroke-width": "1.6", "stroke-dasharray": "5,4" }, svg);
    drawArrow(svg, cx + sr(gho.r1), cy, cx + sr(cur.r1), cy, dr1 > 0 ? "#15803D" : "#DC2626", dr1 > 0 ? "arr-green" : "arr-red", "", cx, cy);
  }

  el("circle", { cx, cy, r: 9, fill: "#0F172A" }, svg);
  const tCen = el("text", { x: cx, y: cy + 23, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
  tCen.textContent = "Mercado";
}

// ============================================================================
// 2. WEBER (TRIÁNGULO LOCACIONAL, IM, WEISZFELD 60 FPS E ISODÁPANA CRÍTICA)
// ============================================================================
const WB_M1 = { x: 180, y: 80, name: "MP1 (Bosque/Predio)" };
const WB_M2 = { x: 180, y: 330, name: "MP2 (Insumo 2)" };
const WB_MK = { x: 700, y: 205, name: "Mercado (Ciudad)" };
const WB_L  = { x: 525, y: 88,  name: "Enclave Laboral Barato (L)" };
let ghostWb = { w1: 40, w2: 30, wm: 40, ah: 55 };
let animWbId = null;

function solveWeber(w1, w2, wm) {
  const pts = [[WB_M1.x, WB_M1.y, w1], [WB_M2.x, WB_M2.y, w2], [WB_MK.x, WB_MK.y, wm]];
  let x = (WB_M1.x * w1 + WB_M2.x * w2 + WB_MK.x * wm) / (w1 + w2 + wm);
  let y = (WB_M1.y * w1 + WB_M2.y * w2 + WB_MK.y * wm) / (w1 + w2 + wm);
  for (let it = 0; it < 35; it++) {
    let nx = 0, ny = 0, den = 0;
    for (const [px, py, w] of pts) {
      const d = Math.max(4, Math.hypot(x - px, y - py));
      nx += (w * px) / d;
      ny += (w * py) / d;
      den += w / d;
    }
    x = nx / den;
    y = ny / den;
  }
  const costFn = (px, py) => (w1 * Math.hypot(px - WB_M1.x, py - WB_M1.y) + w2 * Math.hypot(px - WB_M2.x, py - WB_M2.y) + wm * Math.hypot(px - WB_MK.x, py - WB_MK.y)) / 100;
  return { x, y, costMin: costFn(x, y), costAtL: costFn(WB_L.x, WB_L.y), costFn };
}
function fijarGhostWeber() {
  ghostWb = {
    w1: +document.getElementById("wb-w1").value,
    w2: +document.getElementById("wb-w2").value,
    wm: +document.getElementById("wb-wm").value,
    ah: +document.getElementById("wb-ah").value,
  };
  drawWeber();
}
function presetWeber(w1, w2, wm, ah) {
  if (animWbId) cancelAnimationFrame(animWbId);
  fijarGhostWeber();
  document.getElementById("wb-w1").value = w1;
  document.getElementById("wb-w2").value = w2;
  document.getElementById("wb-wm").value = wm;
  document.getElementById("wb-ah").value = ah;
  drawWeber();
}
function animarWeber() {
  if (animWbId) cancelAnimationFrame(animWbId);
  document.getElementById("wb-w1").value = 12;
  document.getElementById("wb-w2").value = 12;
  document.getElementById("wb-wm").value = 70;
  document.getElementById("wb-ah").value = 45;
  fijarGhostWeber();
  const t0 = performance.now(), dur = 1800;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    document.getElementById("wb-w1").value = Math.round(12 + 43 * ease);
    document.getElementById("wb-w2").value = Math.round(12 + 38 * ease);
    document.getElementById("wb-wm").value = Math.round(70 - 40 * ease);
    drawWeber();
    if (u < 1) animWbId = requestAnimationFrame(step);
  }
  animWbId = requestAnimationFrame(step);
}
function drawWeber() {
  const w1 = +document.getElementById("wb-w1").value;
  const w2 = +document.getElementById("wb-w2").value;
  const wm = +document.getElementById("wb-wm").value;
  const ah = +document.getElementById("wb-ah").value;

  document.getElementById("wb-w1-v").textContent = w1 + " t";
  document.getElementById("wb-w2-v").textContent = w2 + " t";
  document.getElementById("wb-wm-v").textContent = wm + " t";
  document.getElementById("wb-ah-v").textContent = "$" + ah + " / unid";

  const im = (w1 + w2) / wm;
  const opt = solveWeber(w1, w2, wm);
  const gOpt = solveWeber(ghostWb.w1, ghostWb.w2, ghostWb.wm);
  const extraCostL = opt.costAtL - opt.costMin;
  const convieneL = ah > extraCostL && ah > 0;

  document.getElementById("wb-k-im").textContent = fmtDec(im, 2);
  document.getElementById("wb-k-ori").textContent = im > 1.05 ? "IM > 1: Orientada a Insumos" : (im < 0.95 ? "IM < 1: Orientada al Mercado" : "IM ≈ 1: Punto Intermedio");
  document.getElementById("wb-k-ct").textContent = "$" + fmtDec(opt.costMin, 1);
  document.getElementById("wb-k-dl").textContent = "+$" + fmtDec(extraCostL, 1);
  document.getElementById("wb-k-iso").textContent = `Ahorro en L = $${ah}`;
  document.getElementById("wb-k-dec").textContent = convieneL ? "DESVIAR A ENCLAVE L" : "PERMANECER EN P*";
  document.getElementById("wb-k-dec2").textContent = convieneL ? `Ahorro neto: +$${fmtDec(ah - extraCostL, 1)}/unid` : "L queda fuera de la isodápana";

  const svg = document.getElementById("svg-weber");
  svg.innerHTML = "";
  addDefs(svg);

  // Triángulo base
  el("polygon", {
    points: `${WB_M1.x},${WB_M1.y} ${WB_M2.x},${WB_M2.y} ${WB_MK.x},${WB_MK.y}`,
    fill: "#F8FAFC", stroke: "#CBD5E1", "stroke-width": "2"
  }, svg);

  // Isodápana Crítica (aproximación polar exacta en 48 direcciones para ver la curva real)
  if (ah > 2) {
    const isoPts = [];
    for (let k = 0; k < 48; k++) {
      const ang = (k / 48) * Math.PI * 2;
      let lo = 0, hi = 420;
      for (let b = 0; b < 14; b++) {
        const mid = (lo + hi) / 2;
        const c = opt.costFn(opt.x + Math.cos(ang) * mid, opt.y + Math.sin(ang) * mid) - opt.costMin;
        if (c < ah) lo = mid; else hi = mid;
      }
      isoPts.push(`${(opt.x + Math.cos(ang) * lo).toFixed(1)},${(opt.y + Math.sin(ang) * lo).toFixed(1)}`);
    }
    el("polygon", {
      points: isoPts.join(" "),
      fill: convieneL ? "rgba(21,128,61,0.14)" : "rgba(234,88,12,0.10)",
      stroke: convieneL ? "#15803D" : "#EA580C",
      "stroke-width": "2", "stroke-dasharray": "6,4"
    }, svg);
  }

  // Vectores de tracción proporcionales al peso desde P* hacia cada vértice
  const drawPull = (vx, vy, w, col) => {
    const dx = vx - opt.x, dy = vy - opt.y, dist = Math.hypot(dx, dy);
    if (dist < 10) return;
    el("line", { x1: opt.x, y1: opt.y, x2: vx, y2: vy, stroke: "#CBD5E1", "stroke-dasharray": "3,3" }, svg);
    const len = Math.min(dist - 12, 26 + w * 1.1);
    drawArrow(svg, opt.x, opt.y, opt.x + (dx / dist) * len, opt.y + (dy / dist) * len, col, col === "#1D4ED8" ? "arr-blue" : "arr-dark", "", 0, 0);
  };
  drawPull(WB_M1.x, WB_M1.y, w1, "#1D4ED8");
  drawPull(WB_M2.x, WB_M2.y, w2, "#1D4ED8");
  drawPull(WB_MK.x, WB_MK.y, wm, "#0F172A");

  // Rastro fantasma P* anterior y flecha de movimiento
  if (Math.hypot(opt.x - gOpt.x, opt.y - gOpt.y) > 8) {
    el("circle", { cx: gOpt.x, cy: gOpt.y, r: 6, fill: "#94A3B8" }, svg);
    drawArrow(svg, gOpt.x, gOpt.y, opt.x, opt.y, "#DC2626", "arr-red", "Movimiento P*", (gOpt.x + opt.x) / 2, (gOpt.y + opt.y) / 2 - 12);
  }

  // Si conviene saltar a L, flecha verde de salto locacional
  if (convieneL) {
    drawArrow(svg, opt.x, opt.y, WB_L.x, WB_L.y, "#15803D", "arr-green", "Salto óptimo → L", (opt.x + WB_L.x) / 2 + 12, (opt.y + WB_L.y) / 2 - 10, "start");
  }

  // Vértices y etiquetas
  const drawNode = (pt, col, sub, anchor="middle", dy=-14) => {
    el("circle", { cx: pt.x, cy: pt.y, r: 9, fill: col, stroke: "#FFFFFF", "stroke-width": "2" }, svg);
    const t = el("text", { x: pt.x, y: pt.y + dy, fill: "#0F172A", "font-size": "11.5", "font-weight": "700", "text-anchor": anchor }, svg);
    t.textContent = `${pt.name} ${sub}`;
  };
  drawNode(WB_M1, "#1D4ED8", `(${w1}t)`, "middle", -14);
  drawNode(WB_M2, "#1D4ED8", `(${w2}t)`, "middle", 22);
  drawNode(WB_MK, "#0F172A", `(${wm}t)`, "start", 4);
  drawNode(WB_L, convieneL ? "#15803D" : "#EA580C", `(-$${ah})`, "start", -12);

  // Punto P*
  el("circle", { cx: opt.x, cy: opt.y, r: 8.5, fill: "#DC2626", stroke: "#FFFFFF", "stroke-width": "2" }, svg);
  const tP = el("text", { x: opt.x, y: opt.y + 22, fill: "#DC2626", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  tP.textContent = "P* (Fábrica)";
}

// ============================================================================
// 3. KRUGMAN (1991) — BIFURCACIÓN Y MACROCEFALIA A 60 FPS
// ============================================================================
let ghostKr = { tau: 3.5, esc: 7.0, mov: 6.5 };
let animKrId = null;

function calcKrugman(tau, esc, mov) {
  const ust = 0.45 * esc + 0.35 * mov;
  const pres = (ust - tau) * 1.45;
  let cen = 50 + 43 / (1 + Math.exp(-pres));
  cen = Math.min(95, Math.max(50, cen));
  return { ust, cen, per: 100 - cen };
}
function fijarGhostKrugman() {
  ghostKr = {
    tau: +document.getElementById("kr-tau").value,
    esc: +document.getElementById("kr-esc").value,
    mov: +document.getElementById("kr-mov").value,
  };
  drawKrugman();
}
function resetKrugman() {
  if (animKrId) cancelAnimationFrame(animKrId);
  document.getElementById("kr-tau").value = 3.5;
  document.getElementById("kr-esc").value = 7.0;
  document.getElementById("kr-mov").value = 6.5;
  ghostKr = { tau: 3.5, esc: 7.0, mov: 6.5 };
  drawKrugman();
}
function animarKrugman() {
  if (animKrId) cancelAnimationFrame(animKrId);
  document.getElementById("kr-tau").value = 9.5;
  fijarGhostKrugman();
  const t0 = performance.now(), dur = 2200;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 2.5);
    document.getElementById("kr-tau").value = (9.5 - 8.2 * ease).toFixed(2);
    drawKrugman();
    if (u < 1) animKrId = requestAnimationFrame(step);
  }
  animKrId = requestAnimationFrame(step);
}
function drawKrugman() {
  const tau = +document.getElementById("kr-tau").value;
  const esc = +document.getElementById("kr-esc").value;
  const mov = +document.getElementById("kr-mov").value;

  document.getElementById("kr-tau-v").textContent = fmtDec(tau, 1);
  document.getElementById("kr-esc-v").textContent = fmtDec(esc, 1);
  document.getElementById("kr-mov-v").textContent = fmtDec(mov, 1);
  setDelta("kr-tau-d", tau - ghostKr.tau, 1);

  const cur = calcKrugman(tau, esc, mov);
  const gho = calcKrugman(ghostKr.tau, ghostKr.esc, ghostKr.mov);
  const aglom = tau <= cur.ust;

  document.getElementById("kr-k-ust").textContent = fmtDec(cur.ust, 2);
  document.getElementById("kr-k-cen").textContent = fmtDec(cur.cen, 1) + "%";
  document.getElementById("kr-k-reg").textContent = aglom ? "Régimen de Aglomeración" : "Equilibrio Disperso";
  document.getElementById("kr-k-per").textContent = fmtDec(cur.per, 1) + "%";
  document.getElementById("kr-k-per2").textContent = `${fmtDec(cur.per - 50, 1)} pp vs simetría`;
  document.getElementById("kr-k-fza").textContent = aglom ? "Centrípeta → Centro" : "Centrífuga ↔ Dispersión";
  document.getElementById("kr-k-fza2").textContent = aglom ? "τ ≤ τ* dispara macrocefalia" : "τ > τ* protege a la periferia";

  const svg = document.getElementById("svg-krugman");
  svg.innerHTML = "";
  addDefs(svg);

  // IZQUIERDA: Curva S de Bifurcación
  const M = { l: 55, r: 440, t: 30, b: 48 }, W = 980, H = 390;
  const sx = t => M.l + ((t - 1) / 9) * (W - M.l - M.r);
  const sy = c => H - M.b - ((c - 45) / 55) * (H - M.t - M.b);

  for (let c = 50; c <= 100; c += 10) {
    el("line", { x1: M.l, y1: sy(c), x2: W - M.r, y2: sy(c), stroke: "#E2E8F0" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(c) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = c + "%";
  }
  for (let t = 1; t <= 10; t += 1) {
    const tx = el("text", { x: sx(t), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    tx.textContent = "τ=" + t;
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  // Umbral crítico vertical τ*
  el("line", { x1: sx(cur.ust), y1: M.t, x2: sx(cur.ust), y2: H - M.b, stroke: "#D97706", "stroke-width": "2", "stroke-dasharray": "6,4" }, svg);
  const tUst = el("text", { x: sx(cur.ust) + 5, y: M.t + 14, fill: "#B45309", "font-size": "11", "font-weight": "700" }, svg);
  tUst.textContent = `Umbral τ* = ${fmtDec(cur.ust, 1)}`;

  // Curva S
  const pts = [];
  for (let t = 1; t <= 10.01; t += 0.15) {
    const r = calcKrugman(t, esc, mov);
    pts.push(`${sx(t).toFixed(1)},${sy(r.cen).toFixed(1)}`);
  }
  el("polyline", { points: pts.join(" "), fill: "none", stroke: "#1D4ED8", "stroke-width": "2.8" }, svg);

  // Punto fantasma y flecha hacia punto actual
  if (Math.hypot(sx(tau) - sx(ghostKr.tau), sy(cur.cen) - sy(gho.cen)) > 10) {
    el("circle", { cx: sx(ghostKr.tau), cy: sy(gho.cen), r: 5.5, fill: "#94A3B8" }, svg);
    drawArrow(svg, sx(ghostKr.tau), sy(gho.cen), sx(tau), sy(cur.cen), "#DC2626", "arr-red", `${cur.cen >= gho.cen ? "↑ +" : "↓ -"}${fmtDec(Math.abs(cur.cen - gho.cen), 1)} pp`, (sx(ghostKr.tau) + sx(tau)) / 2, (sy(gho.cen) + sy(cur.cen)) / 2 - 12);
  }
  el("circle", { cx: sx(tau), cy: sy(cur.cen), r: 7, fill: "#DC2626", stroke: "#FFFFFF", "stroke-width": "2" }, svg);

  // DERECHA: Diagrama Espacial de Flujo Periferia <-> Capital Regional
  const xCen = 665, xPer = 880, yMid = 205;
  const rCen = 28 + (cur.cen / 100) * 58;
  const rPer = 22 + (cur.per / 100) * 58;

  const tSp = el("text", { x: 770, y: 26, fill: "#0F172A", "font-size": "12", "font-weight": "700", "text-anchor": "middle" }, svg);
  tSp.textContent = "Dinámica Espacial: Capital Regional vs. Periferia";

  el("circle", { cx: xCen, cy: yMid, r: rCen, fill: "rgba(29,78,216,0.22)", stroke: "#1D4ED8", "stroke-width": "2.4" }, svg);
  el("circle", { cx: xPer, cy: yMid, r: rPer, fill: "rgba(100,116,139,0.22)", stroke: "#475569", "stroke-width": "2" }, svg);

  const lC = el("text", { x: xCen, y: yMid - 4, fill: "#1E3A8A", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  lC.textContent = "Capital Regional";
  const lC2 = el("text", { x: xCen, y: yMid + 14, fill: "#1D4ED8", "font-size": "14", "font-weight": "800", "text-anchor": "middle" }, svg);
  lC2.textContent = fmtDec(cur.cen, 1) + "%";

  const lP = el("text", { x: xPer, y: yMid - 4, fill: "#334155", "font-size": "11.5", "font-weight": "700", "text-anchor": "middle" }, svg);
  lP.textContent = "Periferia";
  const lP2 = el("text", { x: xPer, y: yMid + 14, fill: "#475569", "font-size": "13.5", "font-weight": "800", "text-anchor": "middle" }, svg);
  lP2.textContent = fmtDec(cur.per, 1) + "%";

  // Flechas de migración / atracción según régimen
  if (aglom) {
    drawArrow(svg, xPer - rPer - 6, yMid - 14, xCen + rCen + 8, yMid - 14, "#DC2626", "arr-red", "Aglomeración (Backwash)", 775, yMid - 42);
    drawArrow(svg, xPer - rPer - 6, yMid + 14, xCen + rCen + 8, yMid + 14, "#DC2626", "arr-red", "", 0, 0);
  } else {
    drawArrow(svg, xCen + rCen + 8, yMid, xPer - rPer - 8, yMid, "#15803D", "arr-green", "Equilibrio Disperso", 775, yMid - 20);
  }
}

// ============================================================================
// 4. CURVA DE LORENZ, GINI Y PRIMACÍA URBANA IP4 (ESCALA 0-3)
// ============================================================================
let ghostLz = [275473, 174998, 50010, 48632];

function presetLorenz(caso) {
  fijarGhostLorenz();
  const s1 = document.getElementById("lz-p1"), s2 = document.getElementById("lz-p2");
  const s3 = document.getElementById("lz-p3"), s4 = document.getElementById("lz-p4");
  if (caso === "lagos") {
    s1.max = 600000; s2.max = 350000; s3.max = 250000; s4.max = 200000;
    s1.value = 275473; s2.value = 174998; s3.value = 50010; s4.value = 48632;
    document.getElementById("lz-l1").textContent = "P1: Puerto Montt";
    document.getElementById("lz-l2").textContent = "P2: Osorno";
    document.getElementById("lz-l3").textContent = "P3: Puerto Varas";
    document.getElementById("lz-l4").textContent = "P4: Castro";
  } else if (caso === "biobio") {
    s1.max = 600000; s2.max = 350000; s3.max = 250000; s4.max = 200000;
    s1.value = 230375; s2.value = 219441; s3.value = 150992; s4.value = 147322;
    document.getElementById("lz-l1").textContent = "P1: Concepción";
    document.getElementById("lz-l2").textContent = "P2: Los Ángeles";
    document.getElementById("lz-l3").textContent = "P3: San Pedro Paz";
    document.getElementById("lz-l4").textContent = "P4: Talcahuano";
  } else {
    s1.max = 20000; s2.max = 10000; s3.max = 5000; s4.max = 5000;
    s1.value = 5520; s2.value = 4541; s3.value = 122; s4.value = 50;
    document.getElementById("lz-l1").textContent = "P1: Villa Esperanza";
    document.getElementById("lz-l2").textContent = "P2: El Rincón";
    document.getElementById("lz-l3").textContent = "P3: Pueblo Nuevo";
    document.getElementById("lz-l4").textContent = "P4: El Quebradero";
  }
  drawLorenz();
}
function fijarGhostLorenz() {
  ghostLz = [
    +document.getElementById("lz-p1").value,
    +document.getElementById("lz-p2").value,
    +document.getElementById("lz-p3").value,
    +document.getElementById("lz-p4").value,
  ];
  drawLorenz();
}
function calcLorenz(arr) {
  const ord = [...arr].sort((a, b) => a - b);
  const tot = ord.reduce((s, v) => s + v, 0) || 1;
  const n = ord.length;
  const pts = [{ p: 0, q: 0 }];
  let acc = 0, areaTrap = 0;
  for (let i = 0; i < n; i++) {
    const qPrev = acc / tot;
    acc += ord[i];
    const qCur = acc / tot;
    pts.push({ p: (i + 1) / n, q: qCur });
    areaTrap += (1 / n) * (qPrev + qCur);
  }
  return { pts, gini: Math.max(0, 1 - areaTrap), tot };
}
function drawLorenz() {
  const arr = [
    +document.getElementById("lz-p1").value,
    +document.getElementById("lz-p2").value,
    +document.getElementById("lz-p3").value,
    +document.getElementById("lz-p4").value,
  ];
  document.getElementById("lz-p1-v").textContent = fmtInt(arr[0]);
  document.getElementById("lz-p2-v").textContent = fmtInt(arr[1]);
  document.getElementById("lz-p3-v").textContent = fmtInt(arr[2]);
  document.getElementById("lz-p4-v").textContent = fmtInt(arr[3]);

  const desc = [...arr].sort((a, b) => b - a);
  const ip4 = desc[0] / Math.max(1, desc[1] + desc[2] + desc[3]);
  const ip2 = desc[0] / Math.max(1, desc[1]);
  const cur = calcLorenz(arr);
  const gho = calcLorenz(ghostLz);

  let catTxt = "Valor 0: Muy Dispersa";
  if (ip4 >= 1.50) catTxt = "Valor 3: Alt. Concentrada";
  else if (ip4 >= 1.00) catTxt = "Valor 2: Concentrada";
  else if (ip4 >= 0.65) catTxt = "Valor 1: Dispersa";

  document.getElementById("lz-k-ip4").textContent = fmtDec(ip4, 3);
  document.getElementById("lz-k-ip2").textContent = `IP2 (P1/P2) = ${fmtDec(ip2, 3)}`;
  document.getElementById("lz-k-cat").textContent = catTxt;
  document.getElementById("lz-k-gini").textContent = fmtDec(cur.gini, 3);
  const dg = cur.gini - gho.gini;
  document.getElementById("lz-k-dgini").textContent = `ΔG vs Fantasma: ${dg >= 0 ? "+" : "-"}${fmtDec(Math.abs(dg), 3)}`;
  document.getElementById("lz-k-cuota").textContent = fmtDec((desc[0] / cur.tot) * 100, 1) + "%";

  const svg = document.getElementById("svg-lorenz");
  svg.innerHTML = "";
  addDefs(svg);

  // IZQUIERDA: Curva de Lorenz
  const M = { l: 64, r: 460, t: 30, b: 48 }, W = 980, H = 390;
  const sx = p => M.l + p * (W - M.l - M.r);
  const sy = q => H - M.b - q * (H - M.t - M.b);

  for (let v = 0; v <= 1.001; v += 0.25) {
    el("line", { x1: M.l, y1: sy(v), x2: W - M.r, y2: sy(v), stroke: "#E2E8F0" }, svg);
    el("line", { x1: sx(v), y1: M.t, x2: sx(v), y2: H - M.b, stroke: "#F1F5F9" }, svg);
    const ty = el("text", { x: M.l - 8, y: sy(v) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    ty.textContent = Math.round(v * 100) + "%";
    const tx = el("text", { x: sx(v), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    tx.textContent = Math.round(v * 100) + "%";
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);
  el("line", { x1: M.l, y1: M.t, x2: M.l, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  // Diagonal 45°
  el("line", { x1: sx(0), y1: sy(0), x2: sx(1), y2: sy(1), stroke: "#64748B", "stroke-width": "1.8", "stroke-dasharray": "6,4" }, svg);

  // Área Gini sombreada
  const polyG = cur.pts.map(pt => `${sx(pt.p)},${sy(pt.q)}`).join(" ") + ` ${sx(0)},${sy(0)}`;
  el("polygon", { points: polyG, fill: "rgba(220,38,38,0.16)" }, svg);

  // Curva Fantasma
  if (Math.abs(dg) > 0.004) {
    el("polyline", { points: gho.pts.map(pt => `${sx(pt.p)},${sy(pt.q)}`).join(" "), fill: "none", stroke: "#94A3B8", "stroke-width": "2", "stroke-dasharray": "4,4" }, svg);
    const pMid = cur.pts[3], gMid = gho.pts[3];
    drawArrow(svg, sx(gMid.p), sy(gMid.q), sx(pMid.p), sy(pMid.q), dg > 0 ? "#DC2626" : "#15803D", dg > 0 ? "arr-red" : "arr-green", dg > 0 ? "↑ Mayor Gini" : "↓ Menor Gini", sx(pMid.p) - 46, (sy(gMid.q) + sy(pMid.q)) / 2);
  }

  // Curva actual
  el("polyline", { points: cur.pts.map(pt => `${sx(pt.p)},${sy(pt.q)}`).join(" "), fill: "none", stroke: "#DC2626", "stroke-width": "2.8" }, svg);
  cur.pts.forEach(pt => el("circle", { cx: sx(pt.p), cy: sy(pt.q), r: 4.5, fill: "#DC2626" }, svg));

  // DERECHA: Termómetro Horizontal de Primacía IP4 (Umbrales 0,65 | 1,00 | 1,50)
  const bx = 575, bw = 370, by = 185, bh = 32;
  const maxIP = 2.4;
  const sip = v => bx + (Math.min(v, maxIP) / maxIP) * bw;

  const tBar = el("text", { x: bx + bw / 2, y: 120, fill: "#0F172A", "font-size": "12.5", "font-weight": "700", "text-anchor": "middle" }, svg);
  tBar.textContent = "Escala Estandarizada de Primacía IP4 (06 OT 2024.pdf)";

  const segs = [
    [0, 0.65, "#DCFCE7", "#166534", "0: Muy Disp."],
    [0.65, 1.00, "#DBEAFE", "#1E40AF", "1: Disp."],
    [1.00, 1.50, "#FEF3C7", "#92400E", "2: Conc."],
    [1.50, maxIP, "#FEE2E2", "#991B1B", "3: Macrocefalia"],
  ];
  for (const [a, b, bg, fg, lbl] of segs) {
    el("rect", { x: sip(a), y: by, width: sip(b) - sip(a), height: bh, fill: bg, stroke: "#CBD5E1" }, svg);
    const tl = el("text", { x: (sip(a) + sip(b)) / 2, y: by + bh + 18, fill: fg, "font-size": "10.5", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = lbl;
  }
  const gDesc = [...ghostLz].sort((a, b) => b - a);
  const gIp4 = gDesc[0] / Math.max(1, gDesc[1] + gDesc[2] + gDesc[3]);
  if (Math.abs(ip4 - gIp4) > 0.02) {
    drawArrow(svg, sip(gIp4), by - 20, sip(ip4), by - 20, ip4 > gIp4 ? "#DC2626" : "#15803D", ip4 > gIp4 ? "arr-red" : "arr-green", `IP4: ${fmtDec(ip4, 2)}`, (sip(gIp4) + sip(ip4)) / 2, by - 30);
  }
  el("circle", { cx: sip(ip4), cy: by + bh / 2, r: 8, fill: "#0F172A", stroke: "#FFFFFF", "stroke-width": "2" }, svg);
}

drawThunen();
</script>
</body>
</html>
"""


def renderizar_laboratorio_fluido_territorial():
    """Punto de entrada modular para app.py (Módulo 10 — Laboratorio Fluido 60 FPS)."""
    st.header("10. Laboratorio Fluido a 60 FPS: Localización, Macrocefalia y Disparidades")
    st.markdown(
        "Simulador vectorial en tiempo real (sin recarga de servidor) con **Rastro Fantasma** y **flechas de dirección** "
        "para explorar los modelos centrales de la cátedra: **Von Thünen**, **Weber (IM e Isodápana Crítica)**, "
        "**Krugman (Bifurcación $\\tau^*$)** y **Curva de Lorenz / Primacía Urbana ($IP_4$)**."
    )
    components.html(HTML_TERRITORIAL_60FPS, height=740, scrolling=True)
