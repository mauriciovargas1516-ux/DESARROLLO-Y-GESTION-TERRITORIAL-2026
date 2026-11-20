# -*- coding: utf-8 -*-
"""
motor_fluidez_territorial_60fps.py — ESTUDIO TERRITORIAL INTEGRAL A 60 FPS (9 MÓDULOS + LECTURA VIVA + HOJA MECÁNICA)
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Renderiza en el navegador (HTML5 SVG + JavaScript sin lag de servidor):
  1) Von Thünen: Editor libre de ecuaciones LR(d) + Gradiente 2D + Mapa de Anillos Concéntricos.
  2) Alfred Weber: Triángulo Locacional, Índice de Materiales (IM), Weiszfeld e Isodápana Crítica.
  3) Paul Krugman (1991): Bifurcación Centro-Periferia, Umbral τ* y Macrocefalia Regional.
  4) Perroux, Myrdal y Hirschman: Multiplicador en 5 Rondas y Balanza Spread vs. Backwash.
  5) Christaller (Umbral/Alcance) + Granovetter (Vínculos Fuertes vs. Débiles y Lock-in).
  6) Disparidades REAT y OT: Curva de Lorenz, Gini, Entropía de Theil y Primacía Urbana (IP4).
  7) Redes Empresariales (Dini 2010): Animación 60 FPS de 7 topologías, Densidad D y Gradiente GC.
  8) Hoja de Entrenamiento Mecánico Territorial: 16 Fórmulas Puras + 6 Esqueletos SVG + Modo Ciego.
"""

import streamlit.components.v1 as components


HTML_TERRITORIAL_60FPS = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<style>
  * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; }
  body { margin: 0; padding: 0; background: #F8FAFC; color: #0F172A; }
  .wrap { max-width: 1240px; margin: 0 auto; padding: 4px 4px 14px 4px; }
  .top-tabs {
    display: flex; gap: 6px; margin-bottom: 11px; flex-wrap: wrap;
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 8px;
  }
  .tab-btn {
    border: 1px solid #CBD5E1; background: #F8FAFC; color: #334155;
    padding: 6px 11px; border-radius: 6px; font-weight: 700; font-size: 12px;
    cursor: pointer; transition: all 0.14s ease;
  }
  .tab-btn:hover { border-color: #1D4ED8; color: #1D4ED8; background: #EFF6FF; }
  .tab-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .panel { display: none; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 16px; }
  .panel.active { display: block; }
  .sec-title {
    font-size: 13px; font-weight: 700; color: #1E3A8A;
    background: #DBEAFE; border-left: 4px solid #1D4ED8;
    padding: 7px 12px; border-radius: 4px; margin-bottom: 10px;
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
  .sliders-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(185px, 1fr)); gap: 10px; margin-bottom: 11px; }
  .sl-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px 10px; }
  .sl-head { display: flex; justify-content: space-between; font-size: 11.5px; font-weight: 700; color: #1E293B; margin-bottom: 4px; gap: 4px; }
  .sl-val { color: #1D4ED8; font-family: Consolas, monospace; white-space: nowrap; }
  .sl-delta { font-size: 10.5px; font-weight: 700; margin-left: 4px; }
  .d-up { color: #15803D; }
  .d-down { color: #DC2626; }
  .d-eq { color: #64748B; }
  input[type="range"] { width: 100%; accent-color: #1D4ED8; cursor: pointer; margin: 2px 0; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; margin-bottom: 10px; }
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
  .enun-box {
    background: #FFFFFF; border: 1px solid #CBD5E1; border-left: 4px solid #0F172A;
    border-radius: 6px; padding: 9px 13px; margin-bottom: 10px; font-size: 12.1px; line-height: 1.46; color: #1E293B;
  }
  .enun-box summary {
    cursor: pointer; font-weight: 800; color: #0F172A; font-size: 12.3px; list-style: none;
    display: flex; justify-content: space-between; align-items: center;
  }
  .enun-box summary::-webkit-details-marker { display: none; }
  .enun-badge { font-size: 10.5px; font-weight: 700; color: #1E3A8A; background: #DBEAFE; padding: 2px 8px; border-radius: 10px; }
  .enun-body { margin-top: 7px; border-top: 1px dashed #CBD5E1; padding-top: 7px; }
  .eq-editor-bar {
    display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 8px; align-items: end;
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 9px 11px; margin-bottom: 10px;
  }
  @media (max-width: 820px) { .eq-editor-bar { grid-template-columns: 1fr; } }
  .eq-field label { display: block; font-size: 11px; font-weight: 700; color: #1E293B; margin-bottom: 3px; }
  .eq-input {
    width: 100%; padding: 6px 9px; border: 1px solid #94A3B8; border-radius: 5px;
    font-family: Consolas, monospace; font-size: 12px; font-weight: 700; color: #0F172A; background: #FFFFFF;
  }
  .eq-input:focus { outline: 2px solid #1D4ED8; border-color: #1D4ED8; }
  .eq-err { font-size: 11px; font-weight: 700; color: #DC2626; margin-top: 4px; display: none; }
  .sol-box {
    margin-top: 8px; background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #15803D;
    border-radius: 6px; padding: 9px 12px; font-size: 12px; line-height: 1.48; color: #0F172A;
    font-family: Consolas, monospace;
  }
  .sol-box b { color: #1E3A8A; }

  /* === HOJA DE ENTRENAMIENTO MECÁNICO === */
  .mec-toolbar {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 12px; margin-bottom: 10px;
  }
  .mec-filters { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
  .flt-btn {
    border: 1px solid #CBD5E1; background: #FFFFFF; color: #334155;
    padding: 4px 10px; border-radius: 14px; font-size: 11.5px; font-weight: 700; cursor: pointer;
  }
  .flt-btn.active { background: #1E293B; color: #FFFFFF; border-color: #1E293B; }
  .pill-score {
    background: #0F172A; color: #FFFFFF; padding: 5px 11px; border-radius: 14px;
    font-size: 12px; font-weight: 700; font-family: Consolas, monospace;
  }
  .mec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 9px; margin-bottom: 14px; }
  @media (max-width: 780px) { .mec-grid { grid-template-columns: 1fr; } }
  .f-card {
    border: 1px solid #CBD5E1; border-left: 3.5px solid #1E293B; border-radius: 6px;
    background: #FFFFFF; padding: 9px 11px; transition: border-color 0.15s ease;
  }
  .f-card.mastered { border-left-color: #15803D; background: #F0FDF4; }
  .f-head { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 5px; }
  .f-title { font-size: 12px; font-weight: 800; color: #0F172A; }
  .f-cat { font-size: 10px; font-weight: 700; color: #475569; background: #E2E8F0; padding: 2px 6px; border-radius: 4px; }
  .chk-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #475569; width: 22px; height: 22px;
    border-radius: 4px; font-size: 12px; font-weight: 800; cursor: pointer; line-height: 1; padding: 0;
  }
  .f-card.mastered .chk-btn { background: #15803D; color: #FFFFFF; border-color: #15803D; }
  .f-body {
    background: #F8FAFC; border: 1px dashed #CBD5E1; border-radius: 4px; padding: 7px 9px;
    cursor: pointer; min-height: 44px; display: flex; flex-direction: column; justify-content: center;
  }
  .f-eq {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 14.5px; font-weight: 700; color: #0F172A; letter-spacing: 0.2px;
    display: block; line-height: 1.65;
  }
  .f-eq sup, .fstrip-eq sup, .fstrip-sub sup { font-size: 0.72em; vertical-align: super; line-height: 0; }
  .f-eq sub, .fstrip-eq sub, .fstrip-sub sub { font-size: 0.72em; vertical-align: sub; line-height: 0; }
  .f-rule { font-size: 11px; color: #334155; margin-top: 5px; line-height: 1.32; }
  .frac { display: inline-flex; flex-direction: column; align-items: center; vertical-align: middle; margin: 0 2px; font-size: 0.88em; line-height: 1.1; }
  .frac .num { border-bottom: 1.4px solid #0F172A; padding: 0 3px 1px 3px; text-align: center; }
  .frac .den { padding: 1px 3px 0 3px; text-align: center; }
  .blind-cover { display: none; font-size: 11.5px; font-weight: 700; color: #1D4ED8; text-align: center; padding: 4px 0; }
  .blind-mode .f-card:not(.revealed) .f-eq,
  .blind-mode .f-card:not(.revealed) .f-rule { display: none; }
  .blind-mode .f-card:not(.revealed) .blind-cover { display: block; }
  .skel-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
  @media (max-width: 860px) { .skel-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 560px) { .skel-grid { grid-template-columns: 1fr; } }
  .s-card { border: 1px solid #CBD5E1; border-radius: 6px; background: #FFFFFF; padding: 8px 9px; cursor: pointer; }
  .s-title { font-size: 11.5px; font-weight: 800; color: #0F172A; margin-bottom: 4px; }
  .s-sub { font-size: 10.5px; color: #475569; margin-top: 4px; line-height: 1.3; }
  .blind-mode .s-card:not(.revealed) .sk-lbl { opacity: 0; }
  .blind-mode .s-card:not(.revealed) .s-sub { visibility: hidden; }

  /* === MAPA TEÓRICO Y LECTURA VIVA (PESTAÑA 9) === */
  .map-detail-card {
    margin-top: 9px; background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #1D4ED8;
    border-radius: 6px; padding: 10px 13px; font-size: 12.2px; line-height: 1.48; color: #0F172A;
  }
  .map-detail-head {
    display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
    margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px dashed #CBD5E1;
  }
  .map-detail-title { font-size: 13px; font-weight: 800; color: #1E3A8A; }
  .jump-btn {
    border: 1px solid #1D4ED8; background: #EFF6FF; color: #1E3A8A;
    padding: 4px 9px; border-radius: 5px; font-size: 11px; font-weight: 700; cursor: pointer;
  }
  .jump-btn:hover { background: #1D4ED8; color: #FFFFFF; }
  .lec-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 12px; }
  @media (max-width: 820px) { .lec-grid { grid-template-columns: 1fr; } }
  .lec-card {
    border: 1px solid #CBD5E1; border-top: 3.5px solid #1E3A8A; border-radius: 6px;
    background: #FFFFFF; padding: 10px 12px; display: flex; flex-direction: column; gap: 6px;
  }
  .lec-meta { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 4px; }
  .lec-unit { font-size: 10px; font-weight: 800; color: #FFFFFF; background: #1E293B; padding: 2px 7px; border-radius: 4px; }
  .lec-src { font-size: 10.5px; font-weight: 600; color: #475569; font-family: Consolas, monospace; }
  .lec-title { font-size: 12.6px; font-weight: 800; color: #0F172A; }
  .lec-layer {
    font-size: 11.8px; line-height: 1.44; color: #1E293B; padding: 6px 9px; border-radius: 5px;
    background: #F8FAFC; border-left: 3px solid #94A3B8;
  }
  .lec-layer.l-core { border-left-color: #1D4ED8; background: #EFF6FF; }
  .lec-layer.l-bridge { border-left-color: #059669; background: #ECFDF5; }
  .lec-layer.l-trap { border-left-color: #DC2626; background: #FEF2F2; }
  .lec-layer b { color: #0F172A; }
  .qz-card {
    border: 1px solid #CBD5E1; border-left: 4px solid #334155; border-radius: 6px;
    background: #FFFFFF; padding: 9px 12px; margin-bottom: 8px;
  }
  .qz-card.ok { border-left-color: #15803D; background: #F0FDF4; }
  .qz-card.bad { border-left-color: #DC2626; background: #FEF2F2; }
  .qz-tag { font-size: 10px; font-weight: 800; color: #1E3A8A; background: #DBEAFE; padding: 2px 7px; border-radius: 4px; margin-right: 6px; }
  .qz-q { font-size: 12.2px; font-weight: 700; color: #0F172A; margin: 4px 0 7px 0; line-height: 1.42; }
  .qz-opts { display: flex; gap: 7px; flex-wrap: wrap; align-items: center; }
  .qz-btn {
    border: 1px solid #94A3B8; background: #FFFFFF; color: #0F172A;
    padding: 4px 10px; border-radius: 5px; font-size: 11.4px; font-weight: 700; cursor: pointer;
  }
  .qz-btn:hover { background: #EFF6FF; border-color: #1D4ED8; }
  .qz-btn.sel { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .qz-fb { font-size: 11.5px; color: #1E293B; margin-top: 7px; line-height: 1.42; display: none; border-top: 1px dashed #CBD5E1; padding-top: 6px; }
  .qz-card.answered .qz-fb { display: block; }
  /* === CÁPSULAS PEDAGÓGICAS VIVAS DENTRO DE CADA INTERACTIVO === */
  .ped-grid {
    display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-top: 10px;
  }
  @media (max-width: 860px) { .ped-grid { grid-template-columns: 1fr; } }
  .ped-card {
    background: #F8FAFC; border: 1px solid #CBD5E1; border-top: 3.5px solid #1D4ED8;
    border-radius: 6px; padding: 9px 11px; font-size: 11.7px; line-height: 1.46; color: #1E293B;
  }
  .ped-card.p-cur { border-top-color: #7C3AED; background: #FAF5FF; }
  .ped-card.p-def { border-top-color: #059669; background: #F0FDF4; }
  .ped-hd {
    font-size: 10.6px; font-weight: 800; letter-spacing: 0.3px; text-transform: uppercase;
    margin-bottom: 5px; color: #1E3A8A;
  }
  .ped-card.p-cur .ped-hd { color: #6D28D9; }
  .ped-card.p-def .ped-hd { color: #065F46; }
  .ped-card b { color: #0F172A; }
  /* === UNIDAD VI: INDICADORES DE DESARROLLO (MÍN-MÁX) === */
  .u6-grid { display: grid; grid-template-columns: 1.15fr 1fr; gap: 12px; align-items: start; margin-top: 8px; }
  @media (max-width: 880px) { .u6-grid { grid-template-columns: 1fr; } }
  .u6-tbl { width: 100%; border-collapse: collapse; font-size: 11.2px; }
  .u6-tbl th { background: #1E293B; color: #FFFFFF; padding: 5px 6px; border: 1px solid #CBD5E1; text-align: center; font-weight: 700; }
  .u6-tbl td { padding: 4px 6px; border: 1px solid #E2E8F0; text-align: right; font-family: Consolas, monospace; color: #0F172A; }
  .u6-tbl td:first-child { text-align: left; font-family: inherit; font-weight: 700; background: #F8FAFC; }
  .u6-tbl tr.u6-top td { background: #F0FDF4; }
  .u6-tbl tr.u6-bot td { background: #FEF2F2; }
  .u6-rk-up { color: #15803D; font-weight: 800; }
  .u6-rk-dn { color: #DC2626; font-weight: 800; }
  .u6-rk-eq { color: #64748B; }
  .u6-pill-row { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; margin-bottom: 9px; }
  /* === TARJETAS DE FÓRMULAS VIVAS (GRANDE + EDITABLE IN-PLACE + RAYOS X) === */
  .fstrip-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(310px, 1fr));
    gap: 10px; margin: 10px 0 12px 0;
  }
  .fstrip-card {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1px solid #CBD5E1; border-left: 4px solid #1E3A8A;
    border-radius: 8px; padding: 11px 14px;
    transition: box-shadow 0.16s ease, border-color 0.16s ease;
    position: relative;
  }
  .fstrip-card:hover {
    border-color: #93C5FD; box-shadow: 0 3px 12px rgba(29, 78, 216, 0.09);
  }
  .fstrip-card.xray-on {
    background: linear-gradient(180deg, #F0F9FF 0%, #FFFFFF 100%);
    border-color: #3B82F6;
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.14);
  }
  .fstrip-head {
    display: flex; justify-content: space-between; align-items: center; gap: 8px;
    margin-bottom: 7px; cursor: pointer;
  }
  .fstrip-lbl { font-size: 12px; font-weight: 800; color: #1E3A8A; letter-spacing: 0.1px; }
  .xray-pill {
    font-size: 10.5px; font-weight: 800; padding: 3px 8px; border-radius: 12px;
    border: 1px solid #BFDBFE; background: #EFF6FF; color: #1D4ED8;
    white-space: nowrap; transition: all 0.15s ease; cursor: pointer;
  }
  .xray-pill:hover { background: #DBEAFE; }
  .fstrip-card.xray-on .xray-pill {
    background: #0F172A; color: #FFFFFF; border-color: #0F172A;
  }
  .fstrip-eq {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 16.5px; font-weight: 700; color: #0F172A;
    display: block; line-height: 1.75;
  }
  .fstrip-sub {
    font-family: "Cambria Math", "Times New Roman", Georgia, serif;
    font-size: 15.2px; font-weight: 700; color: #0F172A;
    margin-top: 8px; padding-top: 8px; border-top: 1px dashed #CBD5E1;
    display: block; line-height: 1.95;
  }
  .fstrip-card.xray-on .fstrip-eq { display: none; }
  .fstrip-card.xray-on .fstrip-sub {
    margin-top: 4px; padding-top: 2px; border-top: none; font-size: 17.5px; line-height: 2.05;
  }
  .fstrip-card .frac {
    font-size: 0.96em; margin: 0 3px; line-height: 1.25;
  }
  .fstrip-card .frac .num {
    border-bottom: 1.7px solid #0F172A; padding: 0 5px 2px 5px;
  }
  .fstrip-card .frac .den {
    padding: 2px 5px 0 5px;
  }
  .fstrip-note {
    font-size: 11.4px; color: #475569; margin-top: 6px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    display: flex; flex-wrap: wrap; gap: 5px; align-items: center; line-height: 1.4;
  }
  .v-chip {
    display: inline-block; padding: 1px 7px; border-radius: 5px;
    font-family: Consolas, monospace; font-size: 0.94em; font-weight: 800;
    border: 1.3px solid transparent; line-height: 1.35; vertical-align: baseline;
    transition: transform 0.14s ease, box-shadow 0.14s ease;
  }
  .v-chip.editable {
    cursor: text; border-style: dashed;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
  }
  .v-chip.editable:hover {
    transform: translateY(-1px) scale(1.04);
    border-style: solid;
    box-shadow: 0 0 0 2.5px rgba(29, 78, 216, 0.22);
  }
  .chip-inline-in {
    font-family: Consolas, monospace; font-size: 0.96em; font-weight: 800;
    color: #0F172A; background: #FFFFFF; border: 2px solid #1D4ED8;
    border-radius: 5px; padding: 1px 5px; text-align: center;
    outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.20);
    vertical-align: baseline;
  }
  .vc-b { background: #DBEAFE; color: #1E40AF; border-color: #60A5FA; }
  .vc-t { background: #CCFBF1; color: #0F766E; border-color: #2DD4BF; }
  .vc-p { background: #F3E8FF; color: #6B21A8; border-color: #C084FC; }
  .vc-o { background: #FFEDD5; color: #9A3412; border-color: #FB923C; }
  .vc-r { background: #FEE2E2; color: #991B1B; border-color: #F87171; }
  .vc-g { background: #DCFCE7; color: #166534; border-color: #4ADE80; }
  .vc-res {
    background: #15803D; color: #FFFFFF; border-color: #166534;
    padding: 2px 8px; border-radius: 6px; font-family: Consolas, monospace;
    font-size: 0.98em; font-weight: 800; display: inline-block; line-height: 1.35;
  }
  .vc-res.neg { background: #DC2626; border-color: #991B1B; }
  @keyframes chipPop {
    0% { transform: scale(1); }
    45% { transform: scale(1.09); filter: brightness(1.05); }
    100% { transform: scale(1); }
  }
  .v-pop { animation: chipPop 0.25s ease-out; }
  .sym-b { color: #1D4ED8; }
  .sym-t { color: #0F766E; }
  .sym-p { color: #7C3AED; }
  .sym-o { color: #C2410C; }
  .sym-r { color: #DC2626; }
  .sl-num {
    width: 78px; padding: 2px 5px; border: 1px solid #94A3B8; border-radius: 4px;
    font-family: Consolas, monospace; font-size: 11.5px; font-weight: 700;
    color: #1D4ED8; background: #FFFFFF; text-align: right;
  }
  .sl-num:focus { outline: 2px solid #1D4ED8; border-color: #1D4ED8; }
  .teo-box {
    margin-top: 10px; background: #FFFFFF; border: 1px solid #CBD5E1;
    border-left: 4px solid #334155; border-radius: 6px; padding: 8px 12px;
    font-size: 11.9px; line-height: 1.48; color: #1E293B;
  }
  .teo-box summary {
    cursor: pointer; font-weight: 800; color: #0F172A; font-size: 12px; list-style: none;
    display: flex; justify-content: space-between; align-items: center;
  }
  .teo-box summary::-webkit-details-marker { display: none; }
  .teo-body { margin-top: 7px; border-top: 1px dashed #CBD5E1; padding-top: 7px; }
  .teo-body ul { margin: 4px 0 0 18px; padding: 0; }
  .teo-body li { margin-bottom: 4px; }
  .u6-edit-bar {
    display: grid; grid-template-columns: 1.4fr 1fr 1fr auto; gap: 8px; align-items: end;
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 8px 10px; margin-bottom: 10px;
  }
  @media (max-width: 820px) { .u6-edit-bar { grid-template-columns: 1fr; } }

  /* === UNIDAD V: LABORATORIO ORDENAMIENTO TERRITORIAL (OT 60 FPS) === */
  .ot-subtabs {
    display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px; padding: 6px;
  }
  .ot-sub-btn {
    border: 1px solid #CBD5E1; background: #FFFFFF; color: #334155;
    padding: 5px 12px; border-radius: 5px; font-size: 11.8px; font-weight: 700; cursor: pointer;
    transition: all 0.14s ease;
  }
  .ot-sub-btn:hover { border-color: #1D4ED8; color: #1D4ED8; background: #EFF6FF; }
  .ot-sub-btn.active { background: #1E3A8A; color: #FFFFFF; border-color: #1E3A8A; }
  .ot-subpanel { display: none; }
  .ot-subpanel.active { display: block; }
  .ot-grid-2 { display: grid; grid-template-columns: 1fr 1.32fr; gap: 12px; align-items: start; margin-top: 8px; }
  @media (max-width: 880px) { .ot-grid-2 { grid-template-columns: 1fr; } }
  .ot-num-in {
    width: 78px; padding: 3px 5px; border: 1px solid #94A3B8; border-radius: 4px;
    font-family: Consolas, monospace; font-size: 11px; font-weight: 700;
    color: #0F172A; background: #FFFFFF; text-align: right;
  }
  .ot-num-in:focus { outline: 2px solid #1D4ED8; border-color: #1D4ED8; }
  .ot-mat-wrap { overflow-x: auto; border: 1px solid #CBD5E1; border-radius: 6px; background: #FFFFFF; }
  .ot-mat-tbl { width: 100%; border-collapse: collapse; font-size: 11px; }
  .ot-mat-tbl th {
    background: #1E293B; color: #FFFFFF; padding: 5px 6px; border: 1px solid #CBD5E1;
    text-align: center; font-weight: 700; line-height: 1.25;
  }
  .ot-mat-tbl td {
    padding: 4px 5px; border: 1px solid #E2E8F0; text-align: center;
    font-family: Consolas, monospace; color: #0F172A;
  }
  .ot-mat-tbl td:first-child {
    text-align: left; font-family: inherit; font-weight: 700; background: #F8FAFC;
    white-space: nowrap; padding-left: 7px; padding-right: 8px;
  }
  .ot-mat-tbl tr.ot-sum-row td { background: #E2E8F0; font-weight: 800; color: #0F172A; }
  .ot-mat-tbl tr.ot-wt-row td { background: #EFF6FF; font-weight: 800; color: #1E3A8A; }
  .ot-mat-tbl tr.ot-val-row td { background: #F8FAFC; font-weight: 800; font-size: 10.5px; }
  .ot-cell-btn {
    width: 30px; height: 22px; border-radius: 4px; font-family: Consolas, monospace;
    font-size: 11px; font-weight: 800; cursor: pointer; border: 1px solid #CBD5E1;
    transition: transform 0.1s ease;
  }
  .ot-cell-btn:hover { transform: scale(1.08); }
  .ot-c1 { background: #DBEAFE; color: #1E40AF; border-color: #60A5FA; }
  .ot-c0 { background: #F8FAFC; color: #94A3B8; border-color: #CBD5E1; }
  .ot-ai0 { background: #DCFCE7; color: #166534; border-color: #4ADE80; }
  .ot-ai1 { background: #FEE2E2; color: #991B1B; border-color: #FCA5A5; }
  .ot-diag { background: #E2E8F0 !important; color: #64748B !important; }
  .ot-badge-ok { color: #15803D; font-weight: 800; }
  .ot-badge-bad { background: #FEE2E2 !important; color: #991B1B !important; font-weight: 800; }
  .ot-banner-warn {
    background: #FEF2F2; border: 1px solid #FCA5A5; border-left: 4px solid #DC2626;
    color: #991B1B; border-radius: 5px; padding: 7px 11px; font-size: 11.6px; font-weight: 600; margin: 8px 0;
  }
  .ot-banner-ok {
    background: #F0FDF4; border: 1px solid #86EFAC; border-left: 4px solid #15803D;
    color: #166534; border-radius: 5px; padding: 7px 11px; font-size: 11.6px; font-weight: 600; margin: 8px 0;
  }

  .ot-teo-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; margin-bottom: 11px; }
  .ot-teo-grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 11px; }
  @media (max-width: 860px) { .ot-teo-grid, .ot-teo-grid-3 { grid-template-columns: 1fr; } }
  .ot-tcard {
    background: #FFFFFF; border: 1px solid #CBD5E1; border-top: 3.5px solid #1E3A8A;
    border-radius: 6px; padding: 10px 12px; font-size: 11.7px; line-height: 1.46; color: #1E293B;
  }
  .ot-tcard.tc-dark { border-top-color: #0F172A; }
  .ot-tcard.tc-green { border-top-color: #059669; }
  .ot-tcard.tc-amber { border-top-color: #B45309; }
  .ot-tcard.tc-red { border-top-color: #DC2626; }
  .ot-tcard-hd { font-size: 12px; font-weight: 800; color: #0F172A; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; gap: 6px; }
  .ot-tcard-tag { font-size: 9.8px; font-weight: 800; color: #1E3A8A; background: #DBEAFE; padding: 2px 6px; border-radius: 4px; white-space: nowrap; }
  .ot-tcard ul { margin: 5px 0 0 16px; padding: 0; }
  .ot-tcard li { margin-bottom: 3.5px; }
  .ot-pills-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin: 6px 0 2px 0; }
  .ot-mini-pill {
    background: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 5px; padding: 4px 8px;
    font-size: 11.1px; color: #0F172A; line-height: 1.32; flex: 1 1 200px;
  }
  .ot-mini-pill b { color: #1E3A8A; }
  .ot-search-in {
    width: 100%; padding: 6px 10px; border: 1px solid #94A3B8; border-radius: 5px;
    font-size: 12px; color: #0F172A; background: #FFFFFF; margin-bottom: 8px;
  }
  .ot-search-in:focus { outline: 2px solid #1D4ED8; border-color: #1D4ED8; }
  .ot-sys-detail {
    background: #F8FAFC; border: 1px solid #CBD5E1; border-left: 4px solid #1D4ED8;
    border-radius: 6px; padding: 9px 12px; font-size: 11.9px; line-height: 1.46; color: #1E293B; margin: 8px 0 11px 0;
  }

  @media print {
    body { background: #FFFFFF !important; }
    .top-tabs, .mec-toolbar, .mec-filters, .btn-bar, .chk-btn { display: none !important; }
    .panel { display: none !important; border: none !important; padding: 0 !important; }
    #panel-mecanica { display: block !important; }
    .sec-title { background: #F1F5F9 !important; color: #000000 !important; border-left: 3px solid #000 !important; padding: 4px 8px !important; font-size: 11px !important; }
    .mec-grid { grid-template-columns: repeat(2, 1fr) !important; gap: 6px !important; }
    .f-card { break-inside: avoid; border: 1px solid #94A3B8 !important; padding: 5px 7px !important; }
    .blind-mode .f-card .f-eq, .blind-mode .f-card .f-rule { display: block !important; }
    .blind-mode .f-card .blind-cover { display: none !important; }
    .blind-mode .s-card .sk-lbl { opacity: 1 !important; }
    .blind-mode .s-card .s-sub { visibility: visible !important; }
    .skel-grid { grid-template-columns: repeat(3, 1fr) !important; gap: 6px !important; }
  }
</style>
</head>
<body>
<div class="wrap">
  <div class="top-tabs">
    <button class="tab-btn active" onclick="openTab('perroux', this)">1. Crecimiento y Polos de Desarrollo (Unidad 1)</button>
    <button class="tab-btn" onclick="openTab('thunen', this)">2. Localización Rural: Von Thünen (Unidad 2)</button>
    <button class="tab-btn" onclick="openTab('weber', this)">3. Localización Industrial: Weber (Unidad 2)</button>
    <button class="tab-btn" onclick="openTab('krugman', this)">4. Centro-Periferia: Krugman (Unidad 2)</button>
    <button class="tab-btn" onclick="openTab('christaller', this)">5. Lugares Centrales y Capital Social (Unidades 2 y 4)</button>
    <button class="tab-btn" onclick="openTab('lorenz', this)">6. Disparidades y Primacía: Lorenz, Gini, Theil e IP4 (Unidades 3 y 5)</button>
    <button class="tab-btn" onclick="openTab('dini', this)">7. Redes Empresariales y UCINET: Dini 2010 (Unidad 4)</button>
    <button class="tab-btn" onclick="openTab('ot', this)">8. Ordenamiento Territorial: Flechas, Primacía, Rondinelli y Aislamiento (Unidad 5)</button>
    <button class="tab-btn" onclick="openTab('indicadores', this)">9. Indicadores de Desarrollo Mín–Máx (Unidad 6)</button>
    <button class="tab-btn" onclick="openTab('mecanica', this)">10. Formulario de Fórmulas y Gráficos (Modo Ciego)</button>
    <button class="tab-btn" onclick="openTab('lectura', this)">11. Mapa Teórico Integrado y Control de Lectura</button>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 1: VON THÜNEN + EDITOR LIBRE DE ECUACIONES LR(d)                 -->
  <!-- ====================================================================== -->
  <div id="panel-thunen" class="panel">
    <div class="sec-title">
      <span>Modelo de Von Thünen: Renta Locacional LR(d) = Y(m − c) − Y·t·d, Ecuaciones y Anillos</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarThunen()">Reproducir Baja de Flete</button>
        <button class="act-btn" onclick="fijarGhostThunen()">Fijar Fantasma</button>
        <button class="act-btn" onclick="resetThunen()">Caso Osorno</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento del Problema (Duch Brown / Prof. Claudio Mancilla — Anillos Concéntricos)</span>
        <span class="enun-badge">Enunciado y ecuaciones sincronizados en vivo</span>
      </summary>
      <div class="enun-body" id="vt-enunciado"></div>
    </details>

    <div class="eq-editor-bar">
      <div class="eq-field">
        <label>Ecuación Actividad 1 (Intensiva / Lechería):</label>
        <input id="vt-eq-1" class="eq-input" type="text" value="LR1 = 120 - 4.5*d" onkeydown="if(event.key==='Enter') aplicarEqThunen()" />
      </div>
      <div class="eq-field">
        <label>Ecuación Actividad 2 (Agroindustria):</label>
        <input id="vt-eq-2" class="eq-input" type="text" value="LR2 = 85 - 2.0*d" onkeydown="if(event.key==='Enter') aplicarEqThunen()" />
      </div>
      <div class="eq-field">
        <label>Ecuación Actividad 3 (Forestal / Extensiva):</label>
        <input id="vt-eq-3" class="eq-input" type="text" value="LR3 = 50 - 0.8*d" onkeydown="if(event.key==='Enter') aplicarEqThunen()" />
      </div>
      <button class="act-btn primary" style="height:33px;" onclick="aplicarEqThunen()">Aplicar Ecuaciones</button>
    </div>
    <div id="vt-eq-err" class="eq-err"></div>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>1. Margen Lechería (M1)</span><span><span id="vt-m1-v" class="sl-val">120</span><span id="vt-m1-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-m1" type="range" min="60" max="200" step="2" value="120" oninput="onSliderThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>1. Flete Lechería (t1)</span><span><span id="vt-t1-v" class="sl-val">4,5</span><span id="vt-t1-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-t1" type="range" min="1.2" max="8.0" step="0.1" value="4.5" oninput="onSliderThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>2. Margen Agroindustria (M2)</span><span><span id="vt-m2-v" class="sl-val">85</span><span id="vt-m2-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-m2" type="range" min="40" max="160" step="2" value="85" oninput="onSliderThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>2. Flete Agroindustria (t2)</span><span><span id="vt-t2-v" class="sl-val">2,0</span><span id="vt-t2-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-t2" type="range" min="0.8" max="5.0" step="0.1" value="2.0" oninput="onSliderThunen()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>3. Flete Forestal (t3)</span><span><span id="vt-t3-v" class="sl-val">0,80</span><span id="vt-t3-d" class="sl-delta d-eq"></span></span></div>
        <input id="vt-t3" type="range" min="0.4" max="2.5" step="0.05" value="0.8" oninput="onSliderThunen()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Anillo 1: Intensiva / Lechería</div><div id="vt-k-r1" class="kpi-val">0 → 14,0 km</div><div class="kpi-sub">Corte LR1 = LR2</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Anillo 2: Agroindustria</div><div id="vt-k-r2" class="kpi-val">14,0 → 29,2 km</div><div class="kpi-sub">Corte LR2 = LR3</div></div>
      <div class="kpi" style="border-left-color:#059669;"><div class="kpi-lbl">Anillo 3: Forestal / Extensiva</div><div id="vt-k-r3" class="kpi-val">29,2 → 62,5 km</div><div class="kpi-sub">Frontera agrícola (LR=0)</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Movimiento vs. Fantasma</div><div id="vt-k-mov" class="kpi-val">Referencia base</div><div id="vt-k-mov2" class="kpi-sub">Mueve un margen o flete</div></div>
    </div>

    <div id="vt-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-thunen" viewBox="0 0 980 390"></svg></div>
    <div id="vt-sol" class="sol-box"></div>
    <div id="ped-thunen" class="ped-grid"></div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 2: WEBER (TRIÁNGULO LOCACIONAL, IM E ISODÁPANA CRÍTICA)          -->
  <!-- ====================================================================== -->
  <div id="panel-weber" class="panel">
    <div class="sec-title">
      <span>Modelo de Weber: Triángulo Locacional, Índice de Materiales (IM) e Isodápana Crítica</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarWeber()">Reproducir Aumento de IM</button>
        <button class="act-btn" onclick="presetWeber(45, 35, 35, 30)">IM &gt; 1 (Aserradero)</button>
        <button class="act-btn" onclick="presetWeber(15, 15, 70, 30)">IM &lt; 1 (Bebidas/Mercado)</button>
        <button class="act-btn" onclick="presetWeber(25, 25, 45, 135)">Salto a Enclave L</button>
        <button class="act-btn" onclick="fijarGhostWeber()">Fijar Fantasma</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Oficial (Alfred Weber — Orientación a Insumos vs. Mercado e Isodápana Crítica)</span>
        <span class="enun-badge">Fórmula: IM = (W1 + W2) / WM</span>
      </summary>
      <div class="enun-body" id="wb-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card"><div class="sl-head"><span>Peso MP1 Localizada (W1)</span><span id="wb-w1-v" class="sl-val">40 t</span></div><input id="wb-w1" type="range" min="5" max="80" step="1" value="40" oninput="drawWeber()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Peso MP2 Localizada (W2)</span><span id="wb-w2-v" class="sl-val">30 t</span></div><input id="wb-w2" type="range" min="5" max="80" step="1" value="30" oninput="drawWeber()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Peso Producto Final (WM)</span><span id="wb-wm-v" class="sl-val">40 t</span></div><input id="wb-wm" type="range" min="10" max="90" step="1" value="40" oninput="drawWeber()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Ahorro Laboral en Enclave L</span><span id="wb-ah-v" class="sl-val">$55 / unid</span></div><input id="wb-ah" type="range" min="0" max="180" step="5" value="55" oninput="drawWeber()" /></div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Índice de Materiales (IM)</div><div id="wb-k-im" class="kpi-val">1,75</div><div id="wb-k-ori" class="kpi-sub">IM &gt; 1: Insumos</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Costo Transporte Mínimo P*</div><div id="wb-k-ct" class="kpi-val">$248,1</div><div class="kpi-sub">Óptimo puro de flete</div></div>
      <div class="kpi" style="border-left-color:#EA580C;"><div class="kpi-lbl">Sobre-costo Flete hasta L</div><div id="wb-k-dl" class="kpi-val">+$98,4</div><div id="wb-k-iso" class="kpi-sub">Ahorro en L = $55</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Decisión Locacional Final</div><div id="wb-k-dec" class="kpi-val">Permanecer en P*</div><div id="wb-k-dec2" class="kpi-sub">L fuera de Isodápana</div></div>
    </div>

    <div id="wb-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-weber" viewBox="0 0 980 400"></svg></div>
    <div id="wb-sol" class="sol-box"></div>
    <div id="ped-weber" class="ped-grid"></div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 3: KRUGMAN (1991) — BIFURCACIÓN CENTRO-PERIFERIA Y UMBRAL τ*     -->
  <!-- ====================================================================== -->
  <div id="panel-krugman" class="panel">
    <div class="sec-title">
      <span>Nueva Economía Geográfica (Krugman, 1991): Umbral de Transporte τ* y Centro-Periferia</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarKrugman()">Reproducir Baja de Fletes (τ: 10 → 1)</button>
        <button class="act-btn" onclick="fijarGhostKrugman()">Fijar Fantasma</button>
        <button class="act-btn" onclick="resetKrugman()">Restaurar Base</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Conceptual (Fuerzas Centrípetas vs. Centrífugas y Punto de Bifurcación τ*)</span>
        <span class="enun-badge">Enunciado sincronizado en vivo</span>
      </summary>
      <div class="enun-body" id="kr-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card"><div class="sl-head"><span>Costo de Transporte (τ)</span><span><span id="kr-tau-v" class="sl-val">3,5</span><span id="kr-tau-d" class="sl-delta d-eq"></span></span></div><input id="kr-tau" type="range" min="1.0" max="10.0" step="0.1" value="3.5" oninput="drawKrugman()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Economías de Escala (1–10)</span><span id="kr-esc-v" class="sl-val">7,0</span></div><input id="kr-esc" type="range" min="1.0" max="10.0" step="0.2" value="7.0" oninput="drawKrugman()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Movilidad Laboral (1–10)</span><span id="kr-mov-v" class="sl-val">6,5</span></div><input id="kr-mov" type="range" min="1.0" max="10.0" step="0.2" value="6.5" oninput="drawKrugman()" /></div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#D97706;"><div class="kpi-lbl">Umbral Crítico (τ*)</div><div id="kr-k-ust" class="kpi-val">5,43</div><div class="kpi-sub">Bifurcación espacial</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Cuota Capital Regional</div><div id="kr-k-cen" class="kpi-val">89,1%</div><div id="kr-k-reg" class="kpi-sub">Aglomeración</div></div>
      <div class="kpi" style="border-left-color:#64748B;"><div class="kpi-lbl">Cuota Periferia</div><div id="kr-k-per" class="kpi-val">10,9%</div><div id="kr-k-per2" class="kpi-sub">vs simetría (50%)</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Fuerza Predominante</div><div id="kr-k-fza" class="kpi-val">Centrípeta →</div><div id="kr-k-fza2" class="kpi-sub">τ ≤ τ*</div></div>
    </div>

    <div id="kr-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-krugman" viewBox="0 0 980 385"></svg></div>
    <div id="ped-krugman" class="ped-grid"></div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 4: PERROUX, MYRDAL Y HIRSCHMAN (MULTIPLICADOR 5 RONDAS 60 FPS)   -->
  <!-- ====================================================================== -->
  <div id="panel-perroux" class="panel active">
    <div class="sec-title">
      <span>Perroux, Myrdal y Hirschman: Polos de Crecimiento, Encadenamientos y Efectos Spread vs. Backwash</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="presetPerroux('pymemad')">Clúster PymeMad Biobío</button>
        <button class="act-btn" onclick="presetPerroux('lacteo')">Complejo Lácteo Osorno</button>
        <button class="act-btn" onclick="presetPerroux('enclave')">Enclave Extractivo</button>
        <button class="act-btn" onclick="fijarGhostPerroux()">Fijar Fantasma</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Teórico (Multiplicador de Hirschman y Causalidad Acumulativa de Myrdal)</span>
        <span class="enun-badge">Fórmula: M_H = 1 / [1 − (b + f)]</span>
      </summary>
      <div class="enun-body" id="px-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card"><div class="sl-head"><span>Inversión Motriz I0 (MM$)</span><span id="px-i0-v" class="sl-val">$1.000 MM</span></div><input id="px-i0" type="range" min="200" max="5000" step="100" value="1000" oninput="drawPerroux()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Encaden. Hacia Atrás (b)</span><span id="px-b-v" class="sl-val">0,35</span></div><input id="px-b" type="range" min="0.05" max="0.45" step="0.01" value="0.35" oninput="drawPerroux()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Encaden. Hacia Adelante (f)</span><span id="px-f-v" class="sl-val">0,25</span></div><input id="px-f" type="range" min="0.05" max="0.45" step="0.01" value="0.25" oninput="drawPerroux()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Proporción Difusión Spread (%)</span><span id="px-sp-v" class="sl-val">65%</span></div><input id="px-sp" type="range" min="5" max="95" step="5" value="65" oninput="drawPerroux()" /></div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Multiplicador Hirschman (M_H)</div><div id="px-k-mh" class="kpi-val">2,50x</div><div id="px-k-ret" class="kpi-sub">Retención local: 60%</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Producción Total Inducida</div><div id="px-k-tot" class="kpi-val">$2.500 MM</div><div id="px-k-ind" class="kpi-sub">+$1.500 MM indirectos</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Efecto Difusión (Spread)</div><div id="px-k-sp" class="kpi-val">+$975 MM</div><div class="kpi-sub">Compras a comunas vecinas</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Saldo Neto Periferia (Myrdal)</div><div id="px-k-sal" class="kpi-val">+$660 MM</div><div id="px-k-diag" class="kpi-sub">Polo Integrador</div></div>
    </div>

    <div id="px-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-perroux" viewBox="0 0 980 370"></svg></div>
    <div id="px-sol" class="sol-box"></div>
    <div id="ped-perroux" class="ped-grid"></div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 5: CHRISTALLER (UMBRAL/ALCANCE) + GRANOVETTER (VÍNCULOS DÉBILES) -->
  <!-- ====================================================================== -->
  <div id="panel-christaller" class="panel">
    <div class="sec-title">
      <span>Teoría de los Lugares Centrales (Christaller, 1933): Umbral de Demanda y Alcance Espacial</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="presetChris(120000, 90)">Orden Superior (Hospital/Univ.)</button>
        <button class="act-btn" onclick="presetChris(30000, 45)">Orden Intermedio (Banco/CFT)</button>
        <button class="act-btn" onclick="presetChris(5000, 15)">Orden Inferior (CESFAM/Farmacia)</button>
      </div>
    </div>

    <div class="sliders-grid">
      <div class="sl-card"><div class="sl-head"><span>Población Área Influencia</span><span id="ch-pob-v" class="sl-val">37.000 hab.</span></div><input id="ch-pob" type="range" min="2000" max="220000" step="1000" value="37000" oninput="drawChrisGran()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Umbral Mínimo (Threshold)</span><span id="ch-umb-v" class="sl-val">30.000 hab.</span></div><input id="ch-umb" type="range" min="2000" max="180000" step="1000" value="30000" oninput="drawChrisGran()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Alcance Máximo (Range km)</span><span id="ch-alc-v" class="sl-val">45 km</span></div><input id="ch-alc" type="range" min="5" max="130" step="1" value="45" oninput="drawChrisGran()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Distancia Vial Localidades (km)</span><span id="ch-dst-v" class="sl-val">35 km</span></div><input id="ch-dst" type="range" min="2" max="130" step="1" value="35" oninput="drawChrisGran()" /></div>
    </div>
    <div id="ch-diag" class="sol-box" style="margin-top:0;margin-bottom:10px;"></div>

    <div class="sec-title">
      <span>Capital Social y Redes (Granovetter, 1973): Vínculos Fuertes Intralocales vs. Puentes Débiles</span>
      <div class="btn-bar">
        <button class="act-btn" onclick="presetGran(9, 1)">Red Endogámica (Lock-in)</button>
        <button class="act-btn primary" onclick="presetGran(8, 7)">SPL Innovador con Puentes I+D</button>
      </div>
    </div>

    <div class="sliders-grid" style="grid-template-columns: 1fr 1fr;">
      <div class="sl-card"><div class="sl-head"><span>Vínculos Fuertes Locales (Cohesión PyMEs)</span><span id="gr-f-v" class="sl-val">8 / 10</span></div><input id="gr-f" type="range" min="1" max="10" step="1" value="8" oninput="drawChrisGran()" /></div>
      <div class="sl-card"><div class="sl-head"><span>Vínculos Débiles Externos (Puentes ULagos/INIA/CORFO)</span><span id="gr-d-v" class="sl-val">6 / 10</span></div><input id="gr-d" type="range" min="0" max="10" step="1" value="6" oninput="drawChrisGran()" /></div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Cohesión Interna Local</div><div id="gr-k-coh" class="kpi-val">80 / 100</div><div class="kpi-sub">Confianza horizontal</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Acceso a Innovación (Info no redund.)</div><div id="gr-k-inn" class="kpi-val">85 / 100</div><div class="kpi-sub">Puentes externos activos</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Riesgo de Bloqueo (Lock-in)</div><div id="gr-k-lck" class="kpi-val">8%</div><div id="gr-k-lck2" class="kpi-sub">Red abierta</div></div>
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Desempeño SPL Global</div><div id="gr-k-spl" class="kpi-val">80,4 pts</div><div class="kpi-sub">Balance cohesión + puentes</div></div>
    </div>

    <div id="cg-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-gran" viewBox="0 0 980 320"></svg></div>
    <div id="ped-chrisgran" class="ped-grid"></div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 6: LORENZ, GINI, THEIL Y PRIMACÍA URBANA (IP4 ESCALA 0–3)        -->
  <!-- ====================================================================== -->
  <div id="panel-lorenz" class="panel">
    <div class="sec-title">
      <span>6. Disparidades Territoriales y Primacía Urbana: Curva de Lorenz, Gini, Theil, HHI, Hannah-Kay e IP4</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="presetLorenz('lagos')">Los Lagos (Censo 2024)</button>
        <button class="act-btn" onclick="presetLorenz('biobio')">Biobío (Censo 2024)</button>
        <button class="act-btn" onclick="presetLorenz('mancilla')">Ejemplo Mancilla (Lám. 12)</button>
        <button class="act-btn" onclick="presetLorenz('equidad')">Equidad Perfecta (G=0)</button>
        <button class="act-btn" onclick="fijarGhostLorenz()">Fijar Fantasma</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Planteamiento Integrado (Unidad 3: REAT / Desigualdad y Unidad 5: Ordenamiento Territorial)</span>
        <span class="enun-badge">Edita cualquier población en los cuadros o mueve los sliders</span>
      </summary>
      <div class="enun-body" id="lz-enunciado"></div>
    </details>

    <div class="sliders-grid" style="grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));">
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l1">P1: Puerto Montt</span><input id="lz-p1-in" class="sl-num" type="number" min="10" max="1500000" step="100" value="275473" oninput="syncLorenzFromInput(1)" /></div>
        <input id="lz-p1" type="range" min="1000" max="600000" step="1000" value="275473" oninput="syncLorenzFromSlider(1)" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l2">P2: Osorno</span><input id="lz-p2-in" class="sl-num" type="number" min="10" max="1500000" step="100" value="174998" oninput="syncLorenzFromInput(2)" /></div>
        <input id="lz-p2" type="range" min="500" max="350000" step="500" value="174998" oninput="syncLorenzFromSlider(2)" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l3">P3: Puerto Varas</span><input id="lz-p3-in" class="sl-num" type="number" min="10" max="1500000" step="100" value="50010" oninput="syncLorenzFromInput(3)" /></div>
        <input id="lz-p3" type="range" min="100" max="250000" step="500" value="50010" oninput="syncLorenzFromSlider(3)" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span id="lz-l4">P4: Castro</span><input id="lz-p4-in" class="sl-num" type="number" min="10" max="1500000" step="100" value="48632" oninput="syncLorenzFromInput(4)" /></div>
        <input id="lz-p4" type="range" min="50" max="200000" step="500" value="48632" oninput="syncLorenzFromSlider(4)" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Parámetro α (Hannah-Kay)</span><span id="lz-al-v" class="sl-val">α = 2,0</span></div>
        <input id="lz-al" type="range" min="1.5" max="4.0" step="0.5" value="2.0" oninput="drawLorenz()" />
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Índice Primacía (IP4)</div><div id="lz-k-ip4" class="kpi-val">1,007</div><div id="lz-k-ip2" class="kpi-sub">IP2 = 1,574</div></div>
      <div class="kpi" style="border-left-color:#D97706;"><div class="kpi-lbl">Estandarización OT (0–3)</div><div id="lz-k-cat" class="kpi-val">Valor 2: Concentrada</div><div class="kpi-sub">06 OT 2024.pdf</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Índice de Gini (G)</div><div id="lz-k-gini" class="kpi-val">0,432</div><div id="lz-k-dgini" class="kpi-sub">ΔG vs Fantasma: 0,000</div></div>
      <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Entropía de Theil (T)</div><div id="lz-k-theil" class="kpi-val">0,312</div><div id="lz-k-cuota" class="kpi-sub">Cuota P1: 50,2%</div></div>
      <div class="kpi" style="border-left-color:#0F766E;"><div class="kpi-lbl">Concentración HHI y HK_α</div><div id="lz-k-hhi" class="kpi-val">0,369</div><div id="lz-k-hk" class="kpi-sub">HK = 2,71 ciudades equiv.</div></div>
    </div>

    <div id="lz-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-lorenz" viewBox="0 0 980 390"></svg></div>
    <div id="ped-lorenz" class="ped-grid"></div>

    <details class="teo-box">
      <summary>
        <span>Marco Teórico y Claves de Interpretación (Unidad 3 REAT · Unidad 5 Ordenamiento Territorial)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Curva de Lorenz e Índice de Gini (G):</b> ordena los territorios de menor a mayor y grafica población acumulada (<i>q<sub>i</sub></i>) frente a proporción acumulada de territorios (<i>p<sub>i</sub></i>). Si todos pesan igual, la curva coincide con la diagonal de 45° (<b>G = 0</b>). A mayor concentración, mayor área A entre la diagonal y la curva (<b>G → 1</b>).</li>
          <li><b>Entropía de Theil (T):</b> varía entre <b>0</b> (equidad perfecta) y <b>ln(n)</b> (máxima concentración; con n = 4 el tope es ln(4) ≈ 1,386). Su gran ventaja frente al Gini es ser <b>perfectamente descomponible</b> en desigualdad <i>entre regiones</i> + desigualdad <i>dentro de cada región</i>.</li>
          <li><b>Herfindahl-Hirschman (HHI) y Hannah-Kay (HK<sub>α</sub>):</b> HHI = ∑ s<sub>i</sub><sup>2</sup> varía entre 1/n (0,25 con 4 ciudades iguales) y 1. El número equivalente <b>HK<sub>α</sub> = (∑ s<sub>i</sub><sup>α</sup>)<sup>1/(1−α)</sup></b> indica cuántas ciudades de igual tamaño replicarían el mismo grado de concentración; al subir α se castiga más el peso de la ciudad líder.</li>
          <li><b>Índice de Primacía (IP<sub>4</sub>) y Ley de Zipf (06 OT 2024.pdf):</b> compara la ciudad mayor con las tres siguientes: &lt;0,65 (Muy Dispersa = 0), 0,65–1,00 (Dispersa = 1), 1,00–1,50 (Concentrada = 2) y ≥1,50 (Macrocefalia = 3). La <b>Ley de Zipf</b> postula que una red urbana equilibrada sigue P<sub>r</sub> = P<sub>1</sub> / r (la 2ª ciudad debería medir ~50% de la 1ª, la 3ª ~33% y la 4ª ~25%).</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 7: REDES EMPRESARIALES DE DINI (2010) A 60 FPS                   -->
  <!-- ====================================================================== -->
  <div id="panel-dini" class="panel">
    <div class="sec-title">
      <span>Redes Empresariales (Dini, 2010): Variables Libres (n, L), Densidad (D) y Gradiente de Concentración (GC)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="animarDini()">Play: Armar Vínculos</button>
        <button class="act-btn" onclick="saturarDini()">Saturar 100% (K_n)</button>
        <button id="dn-btn-quiebra" class="act-btn" onclick="toggleQuiebraLiderDini()">Simular Quiebra del Líder</button>
        <button class="act-btn" onclick="resetTopologiaDini()">Restaurar Topología</button>
      </div>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="setTopologiaDini('simetrica', this)">1. Simétrica (Pares)</button>
      <button class="flt-btn" onclick="setTopologiaDini('liderazgo', this)">2. Con Liderazgo (Estrella)</button>
      <button class="flt-btn" onclick="setTopologiaDini('jerarquica', this)">3. Jerárquica (Pirámide)</button>
      <button class="flt-btn" onclick="setTopologiaDini('red_redes', this)">4. Red de Redes (Diag. 3)</button>
      <button class="flt-btn" onclick="setTopologiaDini('aviones', this)">5. Prod. Aviones (Diag. 4)</button>
      <button class="flt-btn" onclick="setTopologiaDini('osorno', this)">6. Red Láctea Osorno (C4)</button>
      <button class="flt-btn" onclick="setTopologiaDini('pymemad', this)">7. Clúster PymeMad Biobío (C4)</button>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Tipología Dini (2010, CEPAL — 04 SPL.pdf pág. 14) y Laboratorio Libre UCINET</span>
        <span class="enun-badge">Haz clic en 2 nodos del grafo para crear o borrar vínculos</span>
      </summary>
      <div class="enun-body" id="dn-enunciado"></div>
    </details>

    <div class="sliders-grid" style="grid-template-columns: 1fr 1.35fr 1fr;">
      <div class="sl-card">
        <div class="sl-head"><span>Actores en la Red (n)</span><span><input id="dn-n-in" class="sl-num" style="width:58px;" type="number" min="4" max="15" step="1" value="8" oninput="onInputNDini()" /></span></div>
        <input id="dn-n" type="range" min="4" max="15" step="1" value="8" oninput="onSliderNDini()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Vínculos Activos (L)</span><span><input id="dn-l-in" class="sl-num" style="width:58px;" type="number" min="0" max="28" step="1" value="16" oninput="onInputLDini()" /> <span id="dn-step-v" class="sl-val" style="font-size:10.8px;">/ 28</span></span></div>
        <input id="dn-step" type="range" min="0" max="28" step="1" value="16" oninput="onSliderLDini()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Tipo de Matriz (UCINET)</span><span id="dn-dir-v" class="sl-val">No Dirigida (2L)</span></div>
        <div class="btn-bar" style="margin-top:4px;">
          <button id="dn-dir-no" class="act-btn primary" onclick="setDirigidaDini(false)">No Dirigida (2L)</button>
          <button id="dn-dir-si" class="act-btn" onclick="setDirigidaDini(true)">Dirigida (L)</button>
        </div>
      </div>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Actores (n) y Vínculos (L)</div><div id="dn-k-nl" class="kpi-val">n=8 | L=16</div><div id="dn-k-lmax" class="kpi-sub">Máx posible: 28</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Densidad de la Red (D)</div><div id="dn-k-den" class="kpi-val">57,1%</div><div id="dn-k-denf" class="kpi-sub">D = 2L / [n(n−1)]</div></div>
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Grado Máximo y Promedio</div><div id="dn-k-k" class="kpi-val">k_máx=4 | k̄=4,0</div><div id="dn-k-iso" class="kpi-sub">Aislados (k=0): 0</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Gradiente Concentración (GC)</div><div id="dn-k-gc" class="kpi-val">0,0%</div><div id="dn-k-gcd" class="kpi-sub">Simétrica (0%) ↔ Líder (100%)</div></div>
    </div>

    <div id="dn-fstrip" class="fstrip-grid"></div>
    <div class="svg-box"><svg id="svg-dini" viewBox="0 0 980 400"></svg></div>
    <div id="dn-sol" class="sol-box"></div>
    <div id="ped-dini" class="ped-grid"></div>

    <details class="teo-box">
      <summary>
        <span>Marco Teórico de Redes, Clúster y SPL (Dini 2010 · Schmitz 1999 · Reglas UCINET Control 4)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>Los 3 círculos concéntricos de Dini (2010, CEPAL — 04 SPL.pdf):</b> (1) <b>Red Empresarial</b> (núcleo): empresas independientes que cooperan voluntariamente en compras, ventas o certificaciones; (2) <b>Clúster</b> (anillo medio): masa crítica de empresas especializadas y relacionadas en un área reducida; (3) <b>Sistema Productivo Local — SPL</b> (anillo exterior): empresas + universidades, centros I+D, gremios y gobierno local.</li>
          <li><b>Tipología de Cooperación (Schmitz, 1999):</b> distingue relaciones <b>Horizontales</b> (empresas del mismo eslabón, ej. Aproleche o PymeMad) vs. <b>Verticales</b> (proveedor–comprador a lo largo de la cadena), y <b>Bilaterales</b> (2 firmas: Joint Venture / Subcontratación) vs. <b>Multilaterales</b> (asociaciones o redes).</li>
          <li><b>Lectura de Densidad (D) y Gradiente de Concentración (GC):</b> <b>D &gt; 50%</b> revela alta cohesión y confianza; <b>GC ≈ 0%</b> indica gobernanza simétrica sin actor dominante, mientras <b>GC → 100%</b> señala una estrella controlada por un único líder (alta eficiencia coordinadora, pero frágil ante su salida).</li>
          <li><b>Reglas prácticas UCINET y Control 4 (Prof. Mancilla):</b> la diagonal principal de la matriz de adyacencia siempre es <b>A<sub>ii</sub> = 0</b>. En entrevistas (3 actores de organizaciones distintas en ≥ 2 eslabones), nunca inducir la palabra "clúster" ni preguntar por "debilidades" (usar "desafíos" o "aspectos por fortalecer").</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 8 (U.V): ORDENAMIENTO TERRITORIAL (FLECHAS, RONDINELLI, AISLAM.) -->
  <!-- ====================================================================== -->
  <div id="panel-ot" class="panel">
    <div class="sec-title">
      <span>Unidad V — Ordenamiento Territorial (OT): Ranking con Flechas, Primacía, Guttman/Rondinelli y Aislamiento</span>
      <span style="font-size:11px;font-weight:700;color:#1E3A8A;">Laboratorio interactivo 60 FPS · 4 indicadores de cátedra</span>
    </div>

    <div class="ot-subtabs">
      <button id="ot-subbtn-rk" class="ot-sub-btn active" onclick="openOtSub('rk', this)">A. Ranking con Flechas y Primacía (2 Censos)</button>
      <button id="ot-subbtn-rd" class="ot-sub-btn" onclick="openOtSub('rd', this)">B. Guttman / Rondinelli (1/0 + Gráfico)</button>
      <button id="ot-subbtn-ai" class="ot-sub-btn" onclick="openOtSub('ai', this)">C. Aislamiento Comunal (0/1 + Red Vial)</button>
      <button id="ot-subbtn-teo" class="ot-sub-btn" onclick="openOtSub('teo', this)">D. Base Teórica OT, Escalas, 6 Problemas y PLADECO/ERD</button>
      <button id="ot-subbtn-prot" class="ot-sub-btn" onclick="openOtSub('prot', this)">E. Manual PROT (SUBDERE-CEPAL) + Control de Lectura (10)</button>
    </div>

    <!-- SUB-PANEL A: RANKING CON FLECHAS CRUZADAS Y PRIMACÍA ENTRE 2 CENSOS -->
    <div id="ot-sub-rk" class="ot-subpanel active">
      <div class="sec-title">
        <span>1 y 2. Ranking de Asentamientos (Flechas Cruzadas) y Primacía IP4 entre Dos Censos</span>
        <div class="btn-bar">
          <button class="act-btn primary" onclick="animarOtRanking()">Play: Animar Cruce Censal</button>
          <button class="act-btn" onclick="presetOtRanking('mancilla')">Ejemplo Mancilla (Lám. 10)</button>
          <button class="act-btn" onclick="presetOtRanking('biobio')">Biobío (2017 → 2024)</button>
          <button class="act-btn" onclick="presetOtRanking('lagos')">Los Lagos (2017 → 2024)</button>
          <button class="act-btn" onclick="presetOtRanking('araucania')">Araucanía (2017 → 2024)</button>
          <button class="act-btn" onclick="shockOtRanking()">Simular Migración</button>
        </div>
      </div>

      <details class="enun-box" open>
        <summary>
          <span>Interpretación de Flechas Cruzadas y Evolución de Primacía (06 OT 2024, láminas 10–12)</span>
          <span class="enun-badge">Edita cualquier población en la tabla para ver las flechas cruzarse en vivo</span>
        </summary>
        <div class="enun-body" id="ot-rk-enun"></div>
      </details>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Primacía IP4 (Censo 1 → 2)</div><div id="ot-rk-k-ip4" class="kpi-val">1,17 → 1,17</div><div id="ot-rk-k-dip4" class="kpi-sub">ΔIP4: 0,000</div></div>
        <div class="kpi" style="border-left-color:#D97706;"><div class="kpi-lbl">Escala OT Censo 2 (0–3)</div><div id="ot-rk-k-cat" class="kpi-val">Valor 2: Concentrada</div><div id="ot-rk-k-ip2" class="kpi-sub">IP2 = 1,22</div></div>
        <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Movilidad Jerárquica</div><div id="ot-rk-k-mov" class="kpi-val">3 suben · 2 bajan</div><div id="ot-rk-k-eq" class="kpi-sub">3 mantienen posición</div></div>
        <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Mayor Cambio de Rango</div><div id="ot-rk-k-top" class="kpi-val">Valle Hermoso (-2)</div><div id="ot-rk-k-top2" class="kpi-sub">Cruce relevante en ranking</div></div>
      </div>

      <div id="ot-rk-fstrip" class="fstrip-grid"></div>

      <div class="ot-grid-2">
        <div id="ot-rk-tbl-box" class="ot-mat-wrap"></div>
        <div class="svg-box"><svg id="svg-ot-flechas" viewBox="0 0 600 415"></svg></div>
      </div>
      <div id="ped-ot-rk" class="ped-grid"></div>
    </div>

    <!-- SUB-PANEL B: ESCALA DE GUTTMAN Y MATRIZ DE RONDINELLI -->
    <div id="ot-sub-rd" class="ot-subpanel">
      <div class="sec-title">
        <span>3. Escala de Guttman y Matriz de Rondinelli (1/0 Clicable + Gráfico Complejidad vs. Población)</span>
        <div class="btn-bar">
          <button class="act-btn primary" onclick="presetOtRond('ejemplo')">Ejemplo Excel (Flores–Benque)</button>
          <button class="act-btn" onclick="presetOtRond('lagos')">Los Lagos (Top 10)</button>
          <button class="act-btn" onclick="presetOtRond('biobio')">Biobío (Top 10)</button>
          <button id="ot-rd-btn-mode" class="act-btn" onclick="toggleOtRondMode()">Ver Matriz Ponderada (Wk)</button>
          <button class="act-btn" onclick="testOtRondError()">Probar Error: Todo en 1</button>
        </div>
      </div>

      <details class="enun-box" open>
        <summary>
          <span>Complejidad Funcional de Asentamientos Humanos (Guttman / Rondinelli — láminas 12–15)</span>
          <span class="enun-badge">Haz clic en cualquier celda 1 / 0 para modificar la matriz en tiempo real</span>
        </summary>
        <div class="enun-body" id="ot-rd-enun"></div>
      </details>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Líder Funcional (IC máx)</div><div id="ot-rd-k-top" class="kpi-val">Flores (GT)</div><div id="ot-rd-k-topv" class="kpi-sub">225,00 pts (7/7)</div></div>
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Servicio Más Escaso (Mayor Wk)</div><div id="ot-rd-k-rar" class="kpi-val">Guarderías</div><div id="ot-rd-k-rarv" class="kpi-sub">fk=2 → Wk=50,00</div></div>
        <div class="kpi" style="border-left-color:#D97706;"><div class="kpi-lbl">Validación Discriminación</div><div id="ot-rd-k-val" class="kpi-val">4 / 7 discriminan</div><div id="ot-rd-k-val2" class="kpi-sub">Regla: evitar puros 1 o 0</div></div>
        <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Verificación Suma Ponderada</div><div id="ot-rd-k-sum" class="kpi-val">700,00 pts</div><div id="ot-rd-k-sum2" class="kpi-sub">100 × 7 servicios activos</div></div>
      </div>

      <div id="ot-rd-fstrip" class="fstrip-grid"></div>
      <div id="ot-rd-alert"></div>
      <div id="ot-rd-tbl-box" class="ot-mat-wrap" style="margin-bottom:10px;"></div>
      <div class="svg-box"><svg id="svg-ot-rond" viewBox="0 0 980 345"></svg></div>
      <div id="ped-ot-rd" class="ped-grid"></div>
    </div>

    <!-- SUB-PANEL C: ÍNDICE DE AISLAMIENTO COMUNAL -->
    <div id="ot-sub-ai" class="ot-subpanel">
      <div class="sec-title">
        <span>4. Índice de Aislamiento Comunal (Matriz Simétrica 0/1 Clicable y Red Vial)</span>
        <div class="btn-bar">
          <button class="act-btn primary" onclick="presetOtAisl('pauta')">Ejemplo Pauta (Osorno–Puaucho–Entre Lagos)</button>
          <button class="act-btn" onclick="presetOtAisl('lagos')">Corredor Los Lagos (10)</button>
          <button class="act-btn" onclick="presetOtAisl('biobio')">Corredor Biobío (10)</button>
          <button class="act-btn" onclick="conectarRutaOtAisl()">Pavimentar Nueva Ruta (0)</button>
        </div>
      </div>

      <details class="enun-box" open>
        <summary>
          <span>Conectividad y Aislamiento Territorial (0 = Conexión Directa / Asfalto · 1 = Sin Conexión Directa)</span>
          <span class="enun-badge">Haz clic en cualquier celda 0/1 o en 2 comunas del mapa vial</span>
        </summary>
        <div class="enun-body" id="ot-ai-enun"></div>
      </details>

      <div class="kpis">
        <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">Mejor Conectada (Menor IA)</div><div id="ot-ai-k-best" class="kpi-val">Osorno</div><div id="ot-ai-k-bestv" class="kpi-sub">0,0% aislamiento</div></div>
        <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Mayor Aislamiento (Mayor IA)</div><div id="ot-ai-k-worst" class="kpi-val">Puaucho</div><div id="ot-ai-k-worstv" class="kpi-sub">50,0% aislamiento</div></div>
        <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Aislamiento Promedio Red</div><div id="ot-ai-k-avg" class="kpi-val">33,3%</div><div id="ot-ai-k-avg2" class="kpi-sub">Menor % = mejor acceso</div></div>
        <div class="kpi" style="border-left-color:#0F172A;"><div class="kpi-lbl">Rutas Directas Activas (0)</div><div id="ot-ai-k-con" class="kpi-val">2 / 3 pares</div><div id="ot-ai-k-con2" class="kpi-sub">Matriz simétrica (diag. vacía)</div></div>
      </div>

      <div id="ot-ai-fstrip" class="fstrip-grid"></div>

      <div class="ot-grid-2">
        <div id="ot-ai-tbl-box" class="ot-mat-wrap"></div>
        <div class="svg-box"><svg id="svg-ot-aisl" viewBox="0 0 560 405"></svg></div>
      </div>
      <div id="ped-ot-ai" class="ped-grid"></div>
    </div>

    <!-- SUB-PANEL D: BASE TEÓRICA COMPLETA OT (06 OT 2024 + PLADECO + ERD) -->
    <div id="ot-sub-teo" class="ot-subpanel">
      <div class="sec-title">
        <span>Base Teórica de Ordenamiento Territorial (06 OT 2024 — Prof. Claudio Mancilla)</span>
        <span style="font-size:11px;font-weight:700;color:#1E3A8A;">Definiciones · Estados · Enfoques · Escalas · 6 Problemas · PLADECO y ERD</span>
      </div>

      <div class="ot-teo-grid">
        <div class="ot-tcard">
          <div class="ot-tcard-hd"><span>1. Definiciones Fundamentales del OT</span><span class="ot-tcard-tag">Massiris 2002 · Carta Europea 1983</span></div>
          <ul>
            <li><b>Massiris (2002) [Lám. 2]:</b> proceso e instrumento de planificación, de carácter <b>técnico-político-administrativo</b>, para configurar en el <b>largo plazo</b> una organización del uso y ocupación del territorio acorde con: (a) sus <b>potencialidades y limitaciones</b>, (b) las <b>expectativas y aspiraciones de la población</b>, y (c) los <b>objetivos de desarrollo</b>.</li>
            <li><b>Carta Europea de OT (1983) / Gómez Orea (1994):</b> expresión espacial de las políticas económicas, sociales, culturales y ecológicas de la sociedad; disciplina científica, técnica administrativa y política orientada al desarrollo equilibrado regional.</li>
            <li><b>5 Puntos Centrales [Lám. 5]:</b> (1) Política de Estado, (2) Largo plazo, (3) Instrumento básico = planificación, (4) Concilia desarrollo económico con ocupación del territorio, (5) Fin último: elevar el nivel de vida de la población.</li>
          </ul>
        </div>

        <div class="ot-tcard tc-dark">
          <div class="ot-tcard-hd"><span>2. Dos Enfoques Mundiales y 4 Principios del OT</span><span class="ot-tcard-tag">Láms. 5–6</span></div>
          <ul>
            <li><b>Enfoque Planificación Física (Chile, Brasil):</b> énfasis a escala regional, subregional o local en la regulación del <b>uso y ocupación física</b> del territorio.</li>
            <li><b>Enfoque Planificación Integral (Alemania, Francia, Reino Unido):</b> estrechamente vinculada a la <b>planificación económica y social</b> para garantizar equilibrio en el desarrollo regional.</li>
          </ul>
          <div class="ot-pills-wrap" style="margin-top:7px;">
            <div class="ot-mini-pill"><b>1. Principio del orden:</b> la localización espacial juega un rol clave.</div>
            <div class="ot-mini-pill"><b>2. Bien público:</b> interés general prima sobre el particular.</div>
            <div class="ot-mini-pill"><b>3. Integralidad:</b> no solo lo físico; integrado a la planificación global.</div>
            <div class="ot-mini-pill"><b>4. Normativo y orientador:</b> combina normas obligatorias y acuerdos.</div>
          </div>
        </div>
      </div>

      <div class="ot-tcard tc-amber" style="margin-bottom:11px;">
        <div class="ot-tcard-hd"><span>3. Contexto Político-Administrativo y Constitución de Chile</span><span class="ot-tcard-tag">Láms. 3–4 · Art. 3, 111 y 115 CPR</span></div>
        <div class="ot-pills-wrap">
          <div class="ot-mini-pill"><b>Estado Unitario:</b> un solo centro de impulsión política y monopolio en la creación de normas jurídicas aplicables en todo el territorio (caso de Chile).</div>
          <div class="ot-mini-pill"><b>Estado Federal:</b> Constitución Federal + poder constituyente de estados miembros + cláusulas residuales + poder legislativo bicameral + tribunal federal.</div>
          <div class="ot-mini-pill"><b>Confederación:</b> pacto internacional permanente; los estados miembros mantienen independencia soberana y priman relaciones de coordinación.</div>
          <div class="ot-mini-pill"><b>Regional / Autonómico:</b> desde un Estado unitario se crean unidades subestatales con autonomía política propia, pero bajo una sola soberanía.</div>
        </div>
        <div style="margin-top:7px;padding:7px 9px;background:#FFFBEB;border-left:3px solid #D97706;border-radius:4px;">
          <b>Artículo 3° Constitución de Chile:</b> <i>"El Estado de Chile es unitario. La administración del Estado será funcional y territorialmente descentralizada, o desconcentrada en su caso, de conformidad a la ley. Los órganos del Estado promoverán el fortalecimiento de la regionalización del país y el desarrollo equitativo y solidario entre las regiones, provincias y comunas."</i> (Art. 111 radica la administración regional en el GORE; Art. 115 fija el principio de desarrollo territorial armónico y equitativo).
        </div>
      </div>

      <div class="ot-tcard" style="margin-bottom:11px;">
        <div class="ot-tcard-hd"><span>4. Las 8 Características de un Plan de OT</span><span class="ot-tcard-tag">Lám. 5</span></div>
        <div class="ot-pills-wrap">
          <div class="ot-mini-pill"><b>1. Participativo:</b> considera intereses y opiniones de la comunidad.</div>
          <div class="ot-mini-pill"><b>2. Integral:</b> ve el territorio como sistema (económico, social, ambiental).</div>
          <div class="ot-mini-pill"><b>3. Flexible:</b> se ajusta a los cambios que ocurren en el tiempo.</div>
          <div class="ot-mini-pill"><b>4. Prospectivo:</b> parte de una visión común de futuro.</div>
          <div class="ot-mini-pill"><b>5. Conciliador:</b> concierta soluciones y resuelve conflictos de interés.</div>
          <div class="ot-mini-pill"><b>6. Coordinado:</b> se articula con escalas mayores, vecinos y planes sectoriales.</div>
          <div class="ot-mini-pill"><b>7. Transparente:</b> libre acceso a metodología, resultados, reglamentos y propuestas.</div>
          <div class="ot-mini-pill"><b>8. Verificado:</b> su grado de cumplimiento se evalúa constantemente.</div>
        </div>
      </div>

      <div class="ot-teo-grid">
        <div class="ot-tcard tc-dark">
          <div class="ot-tcard-hd"><span>5. Las 6 Escalas del Ordenamiento Territorial</span><span class="ot-tcard-tag">Lám. 6 · Arriba-Abajo vs. Abajo-Arriba</span></div>
          <table class="ot-mat-tbl" style="margin-top:4px;">
            <thead><tr><th>Escala</th><th>Dirección</th><th>Enfoque / Ejemplos</th></tr></thead>
            <tbody>
              <tr><td>Internacional</td><td>Coordinación</td><td style="text-align:left;font-family:inherit;">Ciudades transfronterizas, cuencas y áreas homogéneas internacionales.</td></tr>
              <tr><td>Nacional</td><td>Arriba → Abajo</td><td style="text-align:left;font-family:inherit;">Política nacional de OT, redistribución regional, relación campo-ciudad.</td></tr>
              <tr><td>Regional</td><td>Arriba → Abajo</td><td style="text-align:left;font-family:inherit;">Sustentabilidad, equilibrio regional y Sistema de Asentamientos Humanos (PROT).</td></tr>
              <tr><td>Interlocal</td><td>Articulada</td><td style="text-align:left;font-family:inherit;">Conurbaciones, metrópolis y problemas comunes entre comunas vecinas.</td></tr>
              <tr><td>Local</td><td>Abajo → Arriba</td><td style="text-align:left;font-family:inherit;">Planificación físico-espacial, densidades, zonificaciones y normas urbanas (PRC/PLADECO).</td></tr>
              <tr><td>Vecinal</td><td>Abajo → Arriba</td><td style="text-align:left;font-family:inherit;">Planes específicos, barriales, patrimoniales e históricos.</td></tr>
            </tbody>
          </table>
        </div>

        <div class="ot-tcard tc-red">
          <div class="ot-tcard-hd"><span>6. ¿Por Qué Ordenar el Territorio? (6 Problemas Clave)</span><span class="ot-tcard-tag">Láms. 7–8</span></div>
          <ul>
            <li><b>1. Conflictos de delimitación (concurrencias territoriales):</b> límites y competencias poco claras entre espacios administrativos o naturales (ej. límite rural/urbano, cuencas, áreas protegidas).</li>
            <li><b>2. Conflictos de uso de suelo:</b> intereses contrapuestos sobre un mismo terreno (ej. proteger un bosque nativo vs. instalar una empresa).</li>
            <li><b>3. Subaprovechamiento de potencialidades:</b> el uso actual no es óptimo y otro uso generaría mayores beneficios sociales/económicos.</li>
            <li><b>4. Territorio mal utilizado o sobreexplotado:</b> contaminación (ej. mala exploración minera), sobreexplotación de recursos o deforestación por expansión urbana.</li>
            <li><b>5. Localización en zonas de alto riesgo:</b> asentamientos humanos o actividades expuestas a amenazas naturales (vulnerabilidad diferenciada según recursos).</li>
            <li><b>6. Infraestructura estratégica mal localizada o dimensionada:</b> hospitales sobredimensionados, relaves mineros cerca de escuelas o disposición de residuos en zonas turísticas.</li>
          </ul>
        </div>
      </div>

      <div class="ot-teo-grid">
        <div class="ot-tcard tc-green">
          <div class="ot-tcard-hd"><span>7. PLADECO — Caso Osorno (Escala Comunal)</span><span class="ot-tcard-tag">SUBDERE 2009 · Láms. 3, 16–17</span></div>
          <p style="margin:0 0 6px 0;"><b>Definición (SUBDERE 2009, pág. 9):</b> principal instrumento de planificación y gestión municipal; representa la visión de futuro comunal fruto del trabajo conjunto entre <b>Municipio y Comunidad</b> como proceso continuo y dinámico.</p>
          <ul>
            <li><b>Tema 1:</b> Osorno con identidad fluvial e integrada con sus ríos (ej. actualización plano regulador, circuitos peatonales, Parque Hott, Parque Bellavista, parque habitacional Río Rahue, miradores).</li>
            <li><b>Tema 2:</b> Osorno, ciudad de servicios turísticos (consolidar ubicación geográfica estratégica).</li>
            <li><b>Tema 3:</b> Osorno, capital ganadera y ruralmente responsable / facilitador del emprendimiento local.</li>
            <li><b>Tema 4:</b> Osorno equitativo, participativo y conectado (subvención pasajes adultos mayores, calles y aceras, Av. República, alarmas comunitarias, CESFAM, farmacia vecinal).</li>
          </ul>
        </div>

        <div class="ot-tcard tc-green">
          <div class="ot-tcard-hd"><span>8. ERD Los Lagos 2030 (Escala Regional)</span><span class="ot-tcard-tag">Láms. 18–20</span></div>
          <ul>
            <li><b>Bienestar Socioterritorial:</b> disminuir brechas de inequidad en acceso y calidad de bienes y servicios públicos entre asentamientos urbanos y rurales, con foco en grupos vulnerables o aislados.
              <br/><i>— Medioambiente y Eficiencia Energética:</i> calidad del aire por calefacción (Osorno y Puerto Montt), contaminantes en cuerpos de agua, residuos domiciliarios y pobreza energética.
              <br/><i>— Servicios Básicos:</i> alcantarillado, aguas servidas tratadas, frecuencia de transporte público en Chiloé y Palena, internet fija rural, agua potable rural y servicios bancarios/correos rurales.</li>
            <li><b>Cohesión e Identidad Sociocultural:</b> pertinencia local en infraestructura, oficios tradicionales y currículos educativos.</li>
            <li><b>Capital Humano Calificado:</b> formación, retención y atracción de profesionales y técnicos en alianza academia–empresas–sector público (cobertura técnico-profesional presencial y a distancia).</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- SUB-PANEL E: MANUAL PROT (SUBDERE-CEPAL 2011) + SISTEMAS SVG + BUSCADOR ANEXO 2 + QUIZ -->
    <div id="ot-sub-prot" class="ot-subpanel">
      <div class="sec-title">
        <span>Manual PROT (SUBDERE–CEPAL, 2011): 4 Sistemas Territoriales, Marco Legal y Estructura</span>
        <span style="font-size:11px;font-weight:700;color:#1E3A8A;">Haz clic en cada sistema del corte geográfico para ver su rol y normas legales</span>
      </div>

      <div class="svg-box"><svg id="svg-ot-sistemas" viewBox="0 0 980 215"></svg></div>
      <div id="ot-sys-detail" class="ot-sys-detail"></div>

      <div class="ot-teo-grid-3">
        <div class="ot-tcard">
          <div class="ot-tcard-hd"><span>Territorio, Fricción y Funciones</span><span class="ot-tcard-tag">Cap. 2 · Págs. 11–14</span></div>
          <ul>
            <li><b>3 Visiones de Territorio (Arenas, 2008):</b> (1) espacio de redes, flujos e identidad; (2) área de aplicación de una política pública (ej. Zonas Saturadas, ADI); (3) unidad político-administrativa con autoridad competente (la <b>Región</b> y el GORE).</li>
            <li><b>Rugosidad y Fricción de la Distancia (Pujadas &amp; Font):</b> topografía difícil, malos caminos o combinación de transportes elevan el aislamiento y disparan un <b>círculo vicioso</b> (menos empleo → despoblamiento → baja el umbral → cierre de servicios). La fricción también sube artificialmente (ej. alzas de peajes).</li>
            <li><b>5 Funciones Territoriales:</b> Identidad, Hábitat, Trabajo, Abastecimiento y Recreación.</li>
            <li><b>Capital Territorial:</b> funciones ambientales, información, tecnología, RR.HH., gestión, base económica e identidad regional.</li>
          </ul>
        </div>

        <div class="ot-tcard tc-green">
          <div class="ot-tcard-hd"><span>Desarrollo Territorial Sustentable</span><span class="ot-tcard-tag">Folch 2003 · Págs. 21–22</span></div>
          <ul>
            <li><b>No es solo "higiene ambiental":</b> exige consumir renovables bajo tasa de renovación, no renovables bajo tasa de sustitución, verter residuos bajo capacidad de asimilación y conservar biodiversidad <i>in situ</i>.</li>
            <li><b>3 Pilares Simultáneos:</b>
              <br/>1) <b>Funcionalidad:</b> productividad, economías de aglomeración y valorización de infraestructura.
              <br/>2) <b>Habitabilidad:</b> calidad de vida, servicios básicos, vivienda segura, gobernabilidad y equidad social.
              <br/>3) <b>Competitividad (3 ópticas):</b> física (infraestructura/entorno), intangible (<b>"competir con la gente"</b>: educación y capacitación) y sustentable (rentabilidad económica, social y ambiental).</li>
            <li><b>Justicia Socio-Espacial (Pág. 8):</b> igualdad de acceso a recursos y servicios sin importar la comuna donde se resida.</li>
          </ul>
        </div>

        <div class="ot-tcard tc-amber">
          <div class="ot-tcard-hd"><span>GORE, Ley 19.175 y el PROT</span><span class="ot-tcard-tag">Cap. 3 y 4 · Págs. 23–27</span></div>
          <ul>
            <li><b>Del PRDU al PROT (Pág. 9):</b> supera la mirada sectorial urbana del PRDU hacia una visión integral regional. El PROT <b>espacializa la ERD</b> con horizonte de <b>10 años</b> y carácter <b>orientador</b> (compatibiliza usos y da certeza a públicos y privados).</li>
            <li><b>6 Funciones OT del GORE (Ley 19.175 LOCGAR, Arts. 17, 24 y 26):</b> (1) sistema de asentamientos humanos, (2) infraestructura y equipamiento, (3) protección ambiental, (4) servicios de transporte, (5) áreas rurales y localidades aisladas, (6) aprobar/promulgar planes reguladores (PRI/PRM/PRC).</li>
            <li><b>Herencias Espaciales Pesadas (Pág. 25):</b> estructuras difíciles de mover (ubicación de ciudades, caminos, barrios) que el PROT debe ponderar.</li>
            <li><b>Información Territorial:</b> UGIT regional homologada al <b>SNIT (DS 28/2006)</b>.</li>
          </ul>
        </div>
      </div>

      <div class="ot-teo-grid">
        <div class="ot-tcard tc-dark">
          <div class="ot-tcard-hd"><span>Estructura del PROT (4 Capítulos y Escalas Cartográficas)</span><span class="ot-tcard-tag">Cap. 4.4 · Anexo 1 · Págs. 28–42</span></div>
          <ul>
            <li><b>1. Memoria Explicativa:</b> Introducción, Objetivos (generales desde ERD y específicos territorializados), Metodología, <b>Diagnóstico Analítico Territorial</b> (<i>selectivo, enfocado y participativo</i>; diferencia catastrar vs. analizar vs. diagnosticar; componentes físico-ambiental, económico y social) y <b>Análisis Prospectivo</b> (escenarios <i>deseable, probable y posible</i>).</li>
            <li><b>2. Modelo de OT y Zonificación:</b> del modelo territorial actual al deseado; referentes de Andalucía (Sistemas, Articulación, Dominios y Unidades Territoriales); <b>zonificación por usos preferentes</b> cubriendo urbano y rural.</li>
            <li><b>3. Normativa de Gestión y Seguimiento:</b> Plan de Acción (proyectos y financiamiento), Normativa vinculante (reglamentos regionales) e indicadores de seguimiento.</li>
            <li><b>4. Cartografía:</b> Carta Base (<b>DATA CORE / SNIT</b>), Mapas temáticos (físico, social, económico), <b>Mapa Semáforo</b> (focos de conflictos de interés por uso del suelo), Zonificación de prioridades y Mapa orientador sectorial.</li>
            <li><b>3 Escalas de Trabajo (Pág. 35):</b> <b>1:250.000</b> (operativa), hasta <b>1:750.000</b> (impresión en regiones extensas como XI y XII) y hasta <b>1:100.000</b> (zoom en conurbaciones o áreas especiales).</li>
          </ul>
        </div>

        <div class="ot-tcard">
          <div class="ot-tcard-hd"><span>Principios, Condiciones y Buscador Rápido Anexo 2</span><span class="ot-tcard-tag">Págs. 25–26 y 43–58</span></div>
          <div style="font-size:11.3px;margin-bottom:7px;">
            <b>Principios PROT:</b> Descentralización, Participación, Sustentabilidad, Integración social, Cohesión, Diferenciación, Gobernabilidad, Diversidad, Solidaridad territorial (compensación de externalidades), <b>Subsidiariedad</b> (traspaso al nivel inferior si tiene capacidad) y Complementariedad.<br/>
            <b>6 Condiciones:</b> Modelo de OT · Inclusivo y estratégico · Participativo · Sintético · Económico (actualizable cada 10 años) · Flexible.
          </div>
          <input id="ot-anexo2-q" class="ot-search-in" type="text" placeholder="Buscar norma del Anexo 2 (ej. borde costero, aguas, bosques, 19.175, urbanismo, rústicos)..." oninput="renderOtAnexo2()" />
          <div id="ot-anexo2-box" class="ot-mat-wrap" style="max-height:175px;overflow-y:auto;"></div>
        </div>
      </div>

      <div class="sec-title" style="margin-top:6px;">
        <span>Control de Lectura Interactivo — Ordenamiento Territorial y PROT (10 Preguntas Tipo Prueba)</span>
        <div class="btn-bar">
          <span id="ot-qz-score" class="pill-score">Aciertos OT: 0 / 10</span>
          <button class="act-btn" onclick="toggleSoloErrOtQz(this)">Ver Solo Pendientes / Erradas</button>
          <button class="act-btn" onclick="resetOtQuiz()">Reiniciar Control OT</button>
        </div>
      </div>
      <div id="ot-qz-list"></div>
    </div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL U.VI: INDICADORES DE DESARROLLO (MÍNIMO-MÁXIMO Y PONDERACIONES)  -->
  <!-- ====================================================================== -->
  <div id="panel-indicadores" class="panel">
    <div class="sec-title">
      <span>Unidad VI — Indicadores de Desarrollo: Normalización Mínimo-Máximo [0, 1], Sentido y Ponderaciones</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="presetU6('base50')">Caso Clase 50 / 50</button>
        <button class="act-btn" onclick="presetU6('base70')">Caso Clase 70 / 30</button>
        <button class="act-btn" onclick="presetU6('inv_v2')">Invertir v2 (Desfavorable −)</button>
        <button class="act-btn" onclick="presetU6('outlier3000')">Prueba Outlier (Escala 200 → 3.000)</button>
      </div>
    </div>

    <details class="enun-box" open>
      <summary>
        <span>Ejercicio Oficial Unidad VI (ejemplo.xlsx — 15 Provincias: Arica a Marga Marga · Caso ACP)</span>
        <span class="enun-badge">u+(x) = (x − mín)/(máx − mín) · u−(x) = (máx − x)/(máx − mín)</span>
      </summary>
      <div class="enun-body" id="u6-enunciado"></div>
    </details>

    <div class="sliders-grid">
      <div class="sl-card">
        <div class="sl-head"><span>Peso Variable v1 (w1) / v2 (w2)</span><span id="u6-w1-v" class="sl-val">50% / 50%</span></div>
        <input id="u6-w1" type="range" min="0" max="100" step="5" value="50" oninput="drawIndicadoresU6()" />
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Sentido de v1</span><span id="u6-s1-v" class="sl-val">Favorable (+)</span></div>
        <div class="btn-bar" style="margin-top:4px;">
          <button id="u6-s1-pos" class="act-btn primary" onclick="setSentidoU6(1, 1)">Favorable (+)</button>
          <button id="u6-s1-neg" class="act-btn" onclick="setSentidoU6(1, -1)">Desfavorable (−)</button>
        </div>
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Sentido de v2</span><span id="u6-s2-v" class="sl-val">Favorable (+)</span></div>
        <div class="btn-bar" style="margin-top:4px;">
          <button id="u6-s2-pos" class="act-btn primary" onclick="setSentidoU6(2, 1)">Favorable (+)</button>
          <button id="u6-s2-neg" class="act-btn" onclick="setSentidoU6(2, -1)">Desfavorable (−)</button>
        </div>
      </div>
      <div class="sl-card">
        <div class="sl-head"><span>Shock Outlier en Líder v1 (× mult)</span><span id="u6-out-v" class="sl-val">1,0x (Original)</span></div>
        <input id="u6-out" type="range" min="1.0" max="5.0" step="0.25" value="1.0" oninput="drawIndicadoresU6()" />
      </div>
    </div>

    <div class="u6-edit-bar">
      <div class="eq-field">
        <label>Editar valores reales de cualquier provincia (ej. prueba poner 3000 o 200):</label>
        <select id="u6-prov-sel" class="eq-input" onchange="loadProvEditorU6()"></select>
      </div>
      <div class="eq-field">
        <label>Valor original v1:</label>
        <input id="u6-ed-v1" class="eq-input" type="number" step="0.01" oninput="applyProvEditU6()" />
      </div>
      <div class="eq-field">
        <label>Valor original v2:</label>
        <input id="u6-ed-v2" class="eq-input" type="number" step="0.01" oninput="applyProvEditU6()" />
      </div>
      <button class="act-btn" style="height:33px;" onclick="resetU6Data()">Restaurar Datos Originales</button>
    </div>

    <div class="kpis">
      <div class="kpi" style="border-left-color:#15803D;"><div class="kpi-lbl">1° Lugar del Ranking (#1)</div><div id="u6-k-top" class="kpi-val">Antofagasta</div><div id="u6-k-topv" class="kpi-sub">Índice = 0,852</div></div>
      <div class="kpi" style="border-left-color:#DC2626;"><div class="kpi-lbl">Último Lugar (#15)</div><div id="u6-k-bot" class="kpi-val">Petorca</div><div id="u6-k-botv" class="kpi-sub">Índice = 0,000</div></div>
      <div class="kpi" style="border-left-color:#1D4ED8;"><div class="kpi-lbl">Promedio Normalizado (15 prov.)</div><div id="u6-k-avg" class="kpi-val">0,393</div><div id="u6-k-avg2" class="kpi-sub">Sensibilidad a outliers</div></div>
      <div class="kpi" style="border-left-color:#7C3AED;"><div class="kpi-lbl">Cambios vs. Escenario 50/50</div><div id="u6-k-chg" class="kpi-val">0 provincias</div><div id="u6-k-chg2" class="kpi-sub">Estabilidad de ponderación</div></div>
    </div>

    <div id="u6-fstrip" class="fstrip-grid"></div>
    <div class="u6-grid">
      <div class="svg-box"><svg id="svg-u6" viewBox="0 0 560 440"></svg></div>
      <div id="u6-tbl-box" style="max-height:445px;overflow-y:auto;"></div>
    </div>
    <div id="u6-sol" class="sol-box"></div>
    <div id="ped-u6" class="ped-grid"></div>

    <details class="teo-box">
      <summary>
        <span>Marco Teórico de Indicadores Compuestos de Desarrollo (Unidad 6 · Normalización y Ponderación)</span>
        <span class="enun-badge">Desplegar teoría de apoyo</span>
      </summary>
      <div class="teo-body">
        <ul>
          <li><b>¿Por qué normalizar?</b> Los indicadores territoriales vienen en unidades incompatibles (PIB en $, pobreza en %, escolaridad en años, distancia en km). La transformación Mín–Máx lleva toda variable al rango adimensional <b>[0, 1]</b> sin cambiar el orden relativo.</li>
          <li><b>Sentido Favorable (+) vs. Desfavorable (−):</b> si un valor más alto significa mayor bienestar (ingresos, conectividad), usa <b>(x − mín)/(máx − mín)</b> para que el mayor reciba 1. Si un valor más alto significa peor desempeño (pobreza, desempleo, aislamiento), invierte con <b>(máx − x)/(máx − mín)</b> para que el menor reciba 1.</li>
          <li><b>Ponderación y robustez del ranking:</b> un índice compuesto <b>I<sub>i</sub> = ∑ w<sub>k</sub>·u<sub>k</sub></b> refleja prioridades de política pública. Probar escenarios alternativos (ej. 50/50 vs. 70/30) permite verificar qué territorios son líderes robustos y cuáles son sensibles al peso asignado.</li>
          <li><b>Límite clave (Sensibilidad a Outliers):</b> prueba escribir <code>3000</code> en <code>v1</code> de cualquier provincia arriba — esa provincia pasará a <code>1,000</code>, pero al agrandar el denominador <code>(máx − mín)</code> comprimirá hacia <code>0</code> los puntajes de las demás 14 provincias.</li>
        </ul>
      </div>
    </details>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 8: HOJA DE ENTRENAMIENTO MECÁNICO TERRITORIAL (MODO CIEGO)       -->
  <!-- ====================================================================== -->
  <div id="panel-mecanica" class="panel">
    <div class="sec-title">
      <span>Formulario y Entrenamiento Mecánico — Desarrollo y Gestión Territorial (ULagos 2026)</span>
      <div class="btn-bar">
        <button id="btn-modo-copia" class="act-btn primary" onclick="setModoMec(false)">Modo Copia (Todo Visible)</button>
        <button id="btn-modo-ciego" class="act-btn" onclick="setModoMec(true)">Modo Ciego (Autoevaluación)</button>
        <button class="act-btn" onclick="resetDominadas()">Reiniciar ✓</button>
        <button class="act-btn" onclick="window.print()">Imprimir / Guardar PDF (Carta)</button>
      </div>
    </div>

    <div class="mec-toolbar">
      <div style="font-size:12px;color:#334155;">
        <b>Método de cuaderno:</b> copia cada fórmula y esqueleto varias veces; luego activa <b>Modo Ciego</b>, escríbelos sin mirar y haz clic en cada recuadro para comprobar y marcar <b>✓</b>.
      </div>
      <span id="mec-score" class="pill-score">Dominadas: 0 / 18</span>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="filtrarMec('all', this)">Todas (18)</button>
      <button class="flt-btn" onclick="filtrarMec('ilpes', this)">U.I · Crecimiento ILPES/MADE (5)</button>
      <button class="flt-btn" onclick="filtrarMec('loc', this)">U.II · Localización y Polos (4)</button>
      <button class="flt-btn" onclick="filtrarMec('reat', this)">U.III · Disparidades REAT (4)</button>
      <button class="flt-btn" onclick="filtrarMec('ot', this)">U.IV–V · Redes Dini y OT (3)</button>
      <button class="flt-btn" onclick="filtrarMec('ind', this)">U.VI · Indicadores Mín-Máx (2)</button>
    </div>

    <div id="mec-container">
      <div class="mec-grid" id="mec-formulas-grid"></div>
      <div class="sec-title" style="margin-top:6px;">
        <span>Esqueletos de Gráficos Clave para Repaso en Cuaderno (6 diagramas)</span>
        <span style="font-size:11px;font-weight:600;color:#334155;">En Modo Ciego, haz clic en cada gráfico para revelar las etiquetas</span>
      </div>
      <div class="skel-grid" id="mec-skel-grid"></div>
    </div>
  </div>

  <!-- ====================================================================== -->
  <!-- PANEL 9: MAPA CAUSAL TEÓRICO, LECTURA EN 3 CAPAS Y QUIZ INTER-UNIDADES -->
  <!-- ====================================================================== -->
  <div id="panel-lectura" class="panel">
    <div class="sec-title">
      <span>Mapa Conceptual Integrado — Programa Oficial Desarrollo y Gestión Territorial (Unidades I a VI)</span>
      <div class="btn-bar">
        <button class="act-btn primary" onclick="activarEscenarioMapa('fletes')">Cadena A: Baja de Fletes (τ↓)</button>
        <button class="act-btn" onclick="activarEscenarioMapa('cluster')">Cadena B: Política Clúster / SPL</button>
        <button class="act-btn" onclick="activarEscenarioMapa('prot')">Cadena C: OT + Índice Desarrollo</button>
        <button class="act-btn" onclick="selectUnidadMapa('U1')">Ver Todo Libre</button>
      </div>
    </div>

    <div class="svg-box"><svg id="svg-mapa-teoria" viewBox="0 0 980 315"></svg></div>
    <div id="mapa-detail-box" class="map-detail-card"></div>

    <div class="sec-title" style="margin-top:14px;">
      <span>Síntesis Teórica en 3 Capas por Autor y Bibliografía Oficial</span>
      <div class="btn-bar">
        <button id="cap-btn-core" class="act-btn primary" onclick="setCapaLectura('core')">Capa 1: Idea Central</button>
        <button id="cap-btn-bridge" class="act-btn" onclick="setCapaLectura('bridge')">Capa 2: Puentes Inter-Unidades</button>
        <button id="cap-btn-trap" class="act-btn" onclick="setCapaLectura('trap')">Capa 3: Trampas de Control</button>
        <button id="cap-btn-all" class="act-btn" onclick="setCapaLectura('all')">Ver las 3 Capas</button>
      </div>
    </div>

    <div class="mec-filters">
      <button class="flt-btn active" onclick="filtrarLectura('all', this)">Todas las Unidades (7)</button>
      <button class="flt-btn" onclick="filtrarLectura('U1', this)">U.I: Crecimiento e ILPES (2)</button>
      <button class="flt-btn" onclick="filtrarLectura('U2', this)">U.II: Espacio y Localización (1)</button>
      <button class="flt-btn" onclick="filtrarLectura('U3', this)">U.III: Disparidades y REAT (1)</button>
      <button class="flt-btn" onclick="filtrarLectura('U4', this)">U.IV: SPL y Cadenas (1)</button>
      <button class="flt-btn" onclick="filtrarLectura('U5', this)">U.V: Ordenamiento OT (1)</button>
      <button class="flt-btn" onclick="filtrarLectura('U6', this)">U.VI: Indicadores Mín-Máx (1)</button>
    </div>

    <div class="lec-grid" id="lec-cards-grid"></div>

    <div class="sec-title" style="margin-top:14px;">
      <span>Control de Lectura y Aplicación Cruzada (12 preguntas integradas)</span>
      <div class="btn-bar">
        <span id="qz-score" class="pill-score">Aciertos: 0 / 12</span>
        <button class="act-btn" onclick="toggleSoloErradasQz(this)">Ver Solo Pendientes / Erradas</button>
        <button class="act-btn" onclick="resetQuizLectura()">Reiniciar Control</button>
      </div>
    </div>
    <div id="qz-list"></div>
  </div>
</div>

<script>
const NS = "http://www.w3.org/2000/svg";

function drawAxesPizarra(svg, x0, yTop, xRight, yBot, yTitle, xTitle) {
  el("line", { x1: x0, y1: yBot, x2: xRight + 6, y2: yBot, stroke: "#0F172A", "stroke-width": "1.8", "marker-end": "url(#arr-dark)" }, svg);
  el("line", { x1: x0, y1: yBot, x2: x0, y2: yTop - 6, stroke: "#0F172A", "stroke-width": "1.8", "marker-end": "url(#arr-dark)" }, svg);
  if (yTitle) {
    const ty = el("text", { x: x0 + 8, y: yTop - 7, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "start" }, svg);
    ty.textContent = yTitle;
  }
  if (xTitle) {
    const tx = el("text", { x: xRight + 4, y: yBot + 36, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "end" }, svg);
    tx.textContent = xTitle;
  }
}
function drawPill(svg, x, y, text, color, bg="rgba(255,255,255,0.95)", anchor="middle", fs="10.8") {
  const bw = Math.max(26, text.length * 6.3 + 10);
  const rx = anchor === "middle" ? x - bw / 2 : (anchor === "start" ? x - 4 : x - bw + 4);
  el("rect", { x: rx, y: y - 11.5, width: bw, height: 16.5, rx: 4, fill: bg, stroke: color, "stroke-width": "1.1" }, svg);
  const t = el("text", { x, y: y + 0.5, fill: color, "font-size": fs, "font-weight": "800", "text-anchor": anchor }, svg);
  t.textContent = text;
}
function drawAxisBreakX(svg, xPos, yBot) {
  el("rect", { x: xPos - 5, y: yBot - 5, width: 10, height: 10, fill: "#FFFFFF" }, svg);
  el("line", { x1: xPos - 4, y1: yBot + 5, x2: xPos, y2: yBot - 5, stroke: "#0F172A", "stroke-width": "1.5" }, svg);
  el("line", { x1: xPos + 1, y1: yBot + 5, x2: xPos + 5, y2: yBot - 5, stroke: "#0F172A", "stroke-width": "1.5" }, svg);
}

const fstripXrayState = {};
const fstripPrevVals = {};

function mFrac(num, den) {
  return `<span class="frac"><span class="num">${num}</span><span class="den">${den}</span></span>`;
}
function vChip(val, cls="vc-b", tip="", trackKey="") {
  let pop = "";
  if (trackKey) {
    if (fstripPrevVals[trackKey] !== undefined && fstripPrevVals[trackKey] !== String(val)) pop = " v-pop";
    fstripPrevVals[trackKey] = String(val);
  }
  const tAttr = tip ? ` title="${tip.replace(/"/g, '&quot;')}"` : "";
  return `<span class="v-chip ${cls}${pop}"${tAttr}>${val}</span>`;
}
function eChip(displayVal, rawNum, bindKey, step="any", cls="vc-b", tip="") {
  let pop = "";
  if (bindKey) {
    if (fstripPrevVals[bindKey] !== undefined && fstripPrevVals[bindKey] !== String(displayVal)) pop = " v-pop";
    fstripPrevVals[bindKey] = String(displayVal);
  }
  const fullTip = (tip ? tip + " · " : "") + "Clic para editar directo en la fórmula (Enter aplica)";
  const tAttr = ` title="${fullTip.replace(/"/g, '&quot;')}"`;
  return `<span class="v-chip editable ${cls}${pop}"${tAttr} data-bind="${bindKey}" data-raw="${rawNum}" data-step="${step}" onclick="openChipEditor(event, this)">${displayVal}</span>`;
}
function rChip(val, isNeg=false, tip="") {
  const tAttr = tip ? ` title="${tip.replace(/"/g, '&quot;')}"` : "";
  return `<span class="vc-res${isNeg ? ' neg' : ''}"${tAttr}>${val}</span>`;
}
function toggleXrayCard(cardKey, headEl) {
  const cardEl = headEl.closest(".fstrip-card");
  if (!cardEl) return;
  fstripXrayState[cardKey] = !fstripXrayState[cardKey];
  cardEl.classList.toggle("xray-on", !!fstripXrayState[cardKey]);
  const pill = cardEl.querySelector(".xray-pill");
  if (pill) pill.textContent = fstripXrayState[cardKey] ? "Rayos X: ON ⇄" : "f(x) → 123";
}
function setSliderSmart(id, val, hardMin=null, hardMax=null) {
  const sl = document.getElementById(id);
  if (!sl) return val;
  let v = val;
  if (hardMin !== null) v = Math.max(hardMin, v);
  if (hardMax !== null) v = Math.min(hardMax, v);
  if (v > parseFloat(sl.max) && (hardMax === null || v <= hardMax)) sl.max = Math.ceil(v * 1.25);
  if (v < parseFloat(sl.min) && (hardMin === null || v >= hardMin)) sl.min = Math.floor(v * 0.5);
  sl.value = v;
  return v;
}
function applyChipEdit(bindKey, rawStr) {
  const clean = String(rawStr || "").replace(/,/g, ".").trim();
  const val = parseFloat(clean);
  if (!Number.isFinite(val)) return false;

  // 1. Perroux / Hirschman / Myrdal
  if (bindKey === "px_i0") { setSliderSmart("px-i0", Math.max(50, Math.round(val)), 50, null); drawPerroux(); return true; }
  if (bindKey === "px_b")  { setSliderSmart("px-b", val, 0.01, 0.45); drawPerroux(); return true; }
  if (bindKey === "px_f")  { setSliderSmart("px-f", val, 0.01, 0.45); drawPerroux(); return true; }
  if (bindKey === "px_sp") { setSliderSmart("px-sp", Math.round(val), 5, 95); drawPerroux(); return true; }

  // 2. Von Thünen
  if (bindKey === "vt_m1") { stateVt.m1 = Math.max(10, val); setSliderSmart("vt-m1", stateVt.m1, 10, null); syncEqInputsVt(); drawThunen(); return true; }
  if (bindKey === "vt_t1") { stateVt.t1 = Math.max(0.2, val); setSliderSmart("vt-t1", stateVt.t1, 0.2, null); syncEqInputsVt(); drawThunen(); return true; }
  if (bindKey === "vt_m2") { stateVt.m2 = Math.max(10, val); setSliderSmart("vt-m2", stateVt.m2, 10, null); syncEqInputsVt(); drawThunen(); return true; }
  if (bindKey === "vt_t2") { stateVt.t2 = Math.max(0.2, val); setSliderSmart("vt-t2", stateVt.t2, 0.2, null); syncEqInputsVt(); drawThunen(); return true; }
  if (bindKey === "vt_m3") { stateVt.m3 = Math.max(5, val); syncEqInputsVt(); drawThunen(); return true; }
  if (bindKey === "vt_t3") { stateVt.t3 = Math.max(0.1, val); setSliderSmart("vt-t3", stateVt.t3, 0.1, null); syncEqInputsVt(); drawThunen(); return true; }

  // 3. Weber
  if (bindKey === "wb_w1") { setSliderSmart("wb-w1", Math.round(val), 1, null); drawWeber(); return true; }
  if (bindKey === "wb_w2") { setSliderSmart("wb-w2", Math.round(val), 1, null); drawWeber(); return true; }
  if (bindKey === "wb_wm") { setSliderSmart("wb-wm", Math.round(val), 1, null); drawWeber(); return true; }
  if (bindKey === "wb_ah") { setSliderSmart("wb-ah", Math.round(val), 0, null); drawWeber(); return true; }

  // 4. Krugman
  if (bindKey === "kr_t") { setSliderSmart("kr-tau", val, 1.0, 10.0); drawKrugman(); return true; }
  if (bindKey === "kr_e") { setSliderSmart("kr-esc", val, 1.0, 10.0); drawKrugman(); return true; }
  if (bindKey === "kr_m") { setSliderSmart("kr-mov", val, 1.0, 10.0); drawKrugman(); return true; }

  // 5. Christaller & Granovetter
  if (bindKey === "ch_pob") { setSliderSmart("ch-pob", Math.round(val), 500, null); drawChrisGran(); return true; }
  if (bindKey === "ch_umb") { setSliderSmart("ch-umb", Math.round(val), 500, null); drawChrisGran(); return true; }
  if (bindKey === "ch_alc") { setSliderSmart("ch-alc", Math.round(val), 2, null); drawChrisGran(); return true; }
  if (bindKey === "ch_dst") { setSliderSmart("ch-dst", Math.round(val), 1, null); drawChrisGran(); return true; }
  if (bindKey === "gr_f")   { setSliderSmart("gr-f", Math.round(val), 1, 10); drawChrisGran(); return true; }
  if (bindKey === "gr_d")   { setSliderSmart("gr-d", Math.round(val), 0, 10); drawChrisGran(); return true; }

  // 6. Lorenz / Gini / Theil / HHI / Hannah-Kay / IP4
  if (bindKey.startsWith("lz_p")) {
    const idx = parseInt(bindKey.slice(4), 10);
    if (idx >= 1 && idx <= 4) {
      const vPos = Math.max(10, Math.round(val));
      document.getElementById("lz-p" + idx + "-in").value = vPos;
      syncLorenzFromInput(idx);
      return true;
    }
  }
  if (bindKey === "lz_al") { setSliderSmart("lz-al", val, 1.5, 4.0); drawLorenz(); return true; }

  // 7. Redes Dini
  if (bindKey === "dn_n") {
    const newN = Math.max(4, Math.min(15, Math.round(val)));
    document.getElementById("dn-n").value = newN;
    const inN = document.getElementById("dn-n-in");
    if (inN) inN.value = newN;
    loadDiniTopology(diniKey, newN);
    return true;
  }
  if (bindKey === "dn_L") {
    const sl = document.getElementById("dn-step");
    const newL = Math.max(0, Math.min(+sl.max, Math.round(val)));
    sl.value = newL;
    const inL = document.getElementById("dn-l-in");
    if (inL) inL.value = newL;
    onSliderLDini();
    return true;
  }

  // 8. Indicadores Mín-Máx (Unidad 6)
  if (bindKey === "u6_v1") {
    u6DataLive[u6SelIdx].v1 = val;
    document.getElementById("u6-ed-v1").value = val;
    drawIndicadoresU6();
    return true;
  }
  if (bindKey === "u6_v2") {
    u6DataLive[u6SelIdx].v2 = val;
    document.getElementById("u6-ed-v2").value = val;
    drawIndicadoresU6();
    return true;
  }
  if (bindKey === "u6_w1") {
    const pct = val <= 1.0001 ? Math.round(val * 100) : Math.round(val);
    document.getElementById("u6-w1").value = Math.max(0, Math.min(100, pct));
    drawIndicadoresU6();
    return true;
  }
  if (bindKey === "u6_w2") {
    const pct2 = val <= 1.0001 ? Math.round(val * 100) : Math.round(val);
    document.getElementById("u6-w1").value = Math.max(0, Math.min(100, 100 - pct2));
    drawIndicadoresU6();
    return true;
  }
  return false;
}
function openChipEditor(ev, chipEl) {
  ev.stopPropagation();
  if (chipEl.dataset.editing === "1") return;
  chipEl.dataset.editing = "1";
  const bindKey = chipEl.dataset.bind;
  const rawVal = chipEl.dataset.raw;
  const stepVal = chipEl.dataset.step || "any";
  const origHtml = chipEl.innerHTML;

  const inp = document.createElement("input");
  inp.type = "number";
  inp.step = stepVal;
  inp.value = rawVal;
  inp.className = "chip-inline-in";
  inp.style.width = Math.max(66, String(rawVal).length * 10 + 30) + "px";

  let finished = false;
  const commit = () => {
    if (finished) return;
    finished = true;
    const ok = applyChipEdit(bindKey, inp.value);
    if (!ok) {
      chipEl.innerHTML = origHtml;
      chipEl.dataset.editing = "0";
    }
  };
  const cancel = () => {
    if (finished) return;
    finished = true;
    chipEl.innerHTML = origHtml;
    chipEl.dataset.editing = "0";
  };

  inp.addEventListener("keydown", e => {
    if (e.key === "Enter") { e.preventDefault(); commit(); }
    else if (e.key === "Escape") { e.preventDefault(); cancel(); }
  });
  inp.addEventListener("blur", () => commit());
  inp.addEventListener("click", e => e.stopPropagation());

  chipEl.innerHTML = "";
  chipEl.appendChild(inp);
  inp.focus();
  inp.select();
}
function renderFormulaStrip(id, cards) {
  const box = document.getElementById(id);
  if (!box) return;
  box.innerHTML = cards.map((c, idx) => {
    const k = `${id}_${idx}`;
    const isOn = !!fstripXrayState[k];
    const noteHtml = c.note ? `<div class="fstrip-note">${c.note}</div>` : "";
    return `
      <div class="fstrip-card${isOn ? ' xray-on' : ''}" style="border-left-color:${c.col || '#1E3A8A'};">
        <div class="fstrip-head" onclick="toggleXrayCard('${k}', this)" title="Clic aquí para alternar Modo Rayos X">
          <span class="fstrip-lbl" style="color:${c.col || '#1E3A8A'};">${c.lbl}</span>
          <span class="xray-pill">${isOn ? "Rayos X: ON ⇄" : "f(x) → 123"}</span>
        </div>
        <div class="fstrip-eq">${c.eq}</div>
        <div class="fstrip-sub">${c.sub || c.live || ""}</div>
        ${noteHtml}
      </div>`;
  }).join("");
}

function renderPedBox(id, lectura, paradoja, defensa) {
  const box = document.getElementById(id);
  if (!box) return;
  box.innerHTML = `
    <div class="ped-card">
      <div class="ped-hd">Lectura Dinámica del Escenario</div>
      <div>${lectura}</div>
    </div>
    <div class="ped-card p-cur">
      <div class="ped-hd">Dato Curioso y Paradoja Teórica</div>
      <div>${paradoja}</div>
    </div>
    <div class="ped-card p-def">
      <div class="ped-hd">Aplicación Real y Defensa en Prueba</div>
      <div>${defensa}</div>
    </div>`;
}

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
  const colors = [["arr-red", "#DC2626"], ["arr-blue", "#1D4ED8"], ["arr-green", "#15803D"], ["arr-orange", "#EA580C"], ["arr-dark", "#0F172A"]];
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
  if (name === "perroux") drawPerroux();
  if (name === "christaller") drawChrisGran();
  if (name === "lorenz") drawLorenz();
  if (name === "dini") drawDini();
  if (name === "ot") drawOtActive();
  if (name === "indicadores") drawIndicadoresU6();
  if (name === "mecanica") renderMecanica();
  if (name === "lectura") { drawMapaTeoria(); renderLecturaCards(); renderQuizLectura(); }
}
function jumpToTab(name) {
  const btns = Array.from(document.querySelectorAll(".top-tabs .tab-btn"));
  const target = btns.find(b => (b.getAttribute("onclick") || "").includes("'" + name + "'"));
  if (target) {
    openTab(name, target);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// ============================================================================
// 1. VON THÜNEN + PARSER LIBRE DE ECUACIONES LR(d)
// ============================================================================
let stateVt = { m1: 120, t1: 4.5, m2: 85, t2: 2.0, m3: 50, t3: 0.8 };
let ghostVt = { m1: 120, t1: 4.5, m2: 85, t2: 2.0, m3: 50, t3: 0.8 };
let animVtId = null;

function parseRentEq(raw) {
  let s = String(raw || "").replace(/,/g, ".").replace(/−/g, "-").replace(/\s+/g, "");
  if (s.includes("=")) s = s.split("=").pop();
  s = s.replace(/\*/g, "").replace(/[dDxX]/g, "d");
  const toks = s.match(/[+-]?[^+-]+/g);
  if (!toks) return null;
  let m = 0, slope = 0, hasD = false;
  for (const tk of toks) {
    if (tk.includes("d")) {
      hasD = true;
      const c = tk.replace("d", "");
      if (c === "" || c === "+") slope += 1;
      else if (c === "-") slope -= 1;
      else { const v = parseFloat(c); if (!Number.isFinite(v)) return null; slope += v; }
    } else {
      const v = parseFloat(tk);
      if (!Number.isFinite(v)) return null;
      m += v;
    }
  }
  if (!hasD || slope >= 0 || m <= 0) return null;
  return { m, t: Math.abs(slope) };
}
function syncEqInputsVt() {
  document.getElementById("vt-eq-1").value = `LR1 = ${stateVt.m1} - ${stateVt.t1}*d`;
  document.getElementById("vt-eq-2").value = `LR2 = ${stateVt.m2} - ${stateVt.t2}*d`;
  document.getElementById("vt-eq-3").value = `LR3 = ${stateVt.m3} - ${stateVt.t3}*d`;
}
function aplicarEqThunen() {
  const err = document.getElementById("vt-eq-err");
  err.style.display = "none";
  const r1 = parseRentEq(document.getElementById("vt-eq-1").value);
  const r2 = parseRentEq(document.getElementById("vt-eq-2").value);
  const r3 = parseRentEq(document.getElementById("vt-eq-3").value);
  if (!r1 || !r2 || !r3) {
    err.textContent = "Formato esperado: lineal con pendiente negativa en d (ej: LR1 = 120 - 4.5*d).";
    err.style.display = "block";
    return;
  }
  fijarGhostThunen();
  stateVt = { m1: r1.m, t1: r1.t, m2: r2.m, t2: r2.t, m3: r3.m, t3: r3.t };
  document.getElementById("vt-m1").max = Math.max(200, Math.ceil(r1.m * 1.4));
  document.getElementById("vt-m1").value = r1.m;
  document.getElementById("vt-t1").max = Math.max(8, Math.ceil(r1.t * 1.5));
  document.getElementById("vt-t1").value = r1.t;
  document.getElementById("vt-m2").max = Math.max(160, Math.ceil(r2.m * 1.4));
  document.getElementById("vt-m2").value = r2.m;
  document.getElementById("vt-t2").value = r2.t;
  document.getElementById("vt-t3").value = r3.t;
  drawThunen();
}
function onSliderThunen() {
  stateVt.m1 = +document.getElementById("vt-m1").value;
  stateVt.t1 = +document.getElementById("vt-t1").value;
  stateVt.m2 = +document.getElementById("vt-m2").value;
  stateVt.t2 = +document.getElementById("vt-t2").value;
  stateVt.t3 = +document.getElementById("vt-t3").value;
  syncEqInputsVt();
  drawThunen();
}
function fijarGhostThunen() {
  ghostVt = { ...stateVt };
  drawThunen();
}
function resetThunen() {
  if (animVtId) cancelAnimationFrame(animVtId);
  stateVt = { m1: 120, t1: 4.5, m2: 85, t2: 2.0, m3: 50, t3: 0.8 };
  ghostVt = { ...stateVt };
  document.getElementById("vt-m1").value = 120;
  document.getElementById("vt-t1").value = 4.5;
  document.getElementById("vt-m2").value = 85;
  document.getElementById("vt-t2").value = 2.0;
  document.getElementById("vt-t3").value = 0.8;
  syncEqInputsVt();
  drawThunen();
}
function animarThunen() {
  if (animVtId) cancelAnimationFrame(animVtId);
  stateVt.t1 = 6.0;
  document.getElementById("vt-t1").value = 6.0;
  fijarGhostThunen();
  const t0 = performance.now(), dur = 1700;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const ease = 1 - Math.pow(1 - u, 3);
    stateVt.t1 = +(6.0 - 3.4 * ease).toFixed(2);
    document.getElementById("vt-t1").value = stateVt.t1;
    syncEqInputsVt();
    drawThunen();
    if (u < 1) animVtId = requestAnimationFrame(step);
  }
  animVtId = requestAnimationFrame(step);
}
function calcRadiosThunen(s) {
  let r1 = 0, r2 = 0, r3 = 0;
  const maxScan = Math.max(70, (s.m3 / s.t3) * 1.1, (s.m2 / s.t2) * 1.1, (s.m1 / s.t1) * 1.1);
  for (let d = 0; d <= maxScan; d += 0.2) {
    const l1 = Math.max(0, s.m1 - s.t1 * d);
    const l2 = Math.max(0, s.m2 - s.t2 * d);
    const l3 = Math.max(0, s.m3 - s.t3 * d);
    const mx = Math.max(l1, l2, l3);
    if (mx <= 0) break;
    if (l1 >= l2 && l1 >= l3) { r1 = d; r2 = Math.max(r2, d); r3 = Math.max(r3, d); }
    else if (l2 >= l1 && l2 >= l3) { r2 = d; r3 = Math.max(r3, d); }
    else { r3 = d; }
  }
  return { r1, r2, r3, maxScan };
}
function drawThunen() {
  const s = stateVt;
  document.getElementById("vt-m1-v").textContent = fmtDec(s.m1, 0);
  document.getElementById("vt-t1-v").textContent = fmtDec(s.t1, 1);
  document.getElementById("vt-m2-v").textContent = fmtDec(s.m2, 0);
  document.getElementById("vt-t2-v").textContent = fmtDec(s.t2, 1);
  document.getElementById("vt-t3-v").textContent = fmtDec(s.t3, 2);
  setDelta("vt-m1-d", s.m1 - ghostVt.m1, 0);
  setDelta("vt-t1-d", s.t1 - ghostVt.t1, 1);
  setDelta("vt-m2-d", s.m2 - ghostVt.m2, 0);
  setDelta("vt-t2-d", s.t2 - ghostVt.t2, 1);
  setDelta("vt-t3-d", s.t3 - ghostVt.t3, 2);

  const cur = calcRadiosThunen(s), gho = calcRadiosThunen(ghostVt);
  const d12 = Math.abs(s.t1 - s.t2) > 1e-4 ? (s.m1 - s.m2) / (s.t1 - s.t2) : 0;
  const d23 = Math.abs(s.t2 - s.t3) > 1e-4 ? (s.m2 - s.m3) / (s.t2 - s.t3) : 0;
  const d30 = s.m3 / s.t3;

  document.getElementById("vt-enunciado").innerHTML =
    `En una llanura homogénea alrededor de un mercado urbano central compiten tres actividades con rentas locacionales: ` +
    `<b>LR<sub>1</sub>(d) = ${fmtDec(s.m1,0)} − ${fmtDec(s.t1,1)}·d</b> (Lechería/Hortalizas), ` +
    `<b>LR<sub>2</sub>(d) = ${fmtDec(s.m2,0)} − ${fmtDec(s.t2,1)}·d</b> (Agroindustria) y ` +
    `<b>LR<sub>3</sub>(d) = ${fmtDec(s.m3,0)} − ${fmtDec(s.t3,2)}·d</b> (Forestal/Extensiva). ` +
    `Determine los radios de transición de los anillos concéntricos y el límite agrícola donde la renta se hace cero.`;

  document.getElementById("vt-sol").innerHTML =
    `<b>Cortes exactos:</b> LR1=LR2 ⇒ d<sub>12</sub> = (${fmtDec(s.m1,0)}−${fmtDec(s.m2,0)})/(${fmtDec(s.t1,1)}−${fmtDec(s.t2,1)}) = <b>${fmtDec(Math.max(0,d12),1)} km</b> | ` +
    `LR2=LR3 ⇒ d<sub>23</sub> = (${fmtDec(s.m2,0)}−${fmtDec(s.m3,0)})/(${fmtDec(s.t2,1)}−${fmtDec(s.t3,2)}) = <b>${fmtDec(Math.max(0,d23),1)} km</b> | ` +
    `Frontera LR3=0 ⇒ d<sub>máx</sub> = ${fmtDec(s.m3,0)}/${fmtDec(s.t3,2)} = <b>${fmtDec(d30,1)} km</b>`;

  document.getElementById("vt-k-r1").textContent = `0 → ${fmtDec(cur.r1, 1)} km`;
  document.getElementById("vt-k-r2").textContent = `${fmtDec(cur.r1, 1)} → ${fmtDec(cur.r2, 1)} km`;
  document.getElementById("vt-k-r3").textContent = `${fmtDec(cur.r2, 1)} → ${fmtDec(cur.r3, 1)} km`;
  const dr1 = cur.r1 - gho.r1;
  document.getElementById("vt-k-mov").textContent = Math.abs(dr1) >= 0.3 ? `${dr1 > 0 ? "→ +" : "← -"}${fmtDec(Math.abs(dr1), 1)} km` : "En fantasma";
  document.getElementById("vt-k-mov2").textContent = Math.abs(dr1) >= 0.3 ? (dr1 > 0 ? "Anillo 1 se expande" : "Anillo 1 se contrae") : "Mueve un parámetro";

  const svg = document.getElementById("svg-thunen");
  svg.innerHTML = "";
  addDefs(svg);
  const M = { l: 55, r: 420, t: 30, b: 44 }, W = 980, H = 390;
  const maxD = Math.max(70, Math.ceil(cur.r3 * 1.12 / 10) * 10);
  const maxR = Math.max(175, Math.max(s.m1, s.m2, s.m3) * 1.15);
  const sx = d => M.l + (d / maxD) * (W - M.l - M.r);
  const sy = r => H - M.b - (r / maxR) * (H - M.t - M.b);

  for (let i = 0; i <= 4; i++) {
    const yv = (maxR / 4) * i, dv = (maxD / 5) * i;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#E2E8F0" }, svg);
    const ty = el("text", { x: M.l - 8, y: sy(yv) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    ty.textContent = fmtInt(yv);
  }
  for (let i = 0; i <= 5; i++) {
    const dv = (maxD / 5) * i;
    el("line", { x1: sx(dv), y1: M.t, x2: sx(dv), y2: H - M.b, stroke: "#F1F5F9" }, svg);
    const tx = el("text", { x: sx(dv), y: H - M.b + 16, fill: "#475569", "font-size": "11", "text-anchor": "middle" }, svg);
    tx.textContent = fmtInt(dv) + " km";
  }
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Renta Locacional LR(d)", "Distancia al Mercado (d, km)");

  if (cur.r1 > 0.2) el("polygon", { points: `${sx(0)},${sy(0)} ${sx(cur.r1)},${sy(0)} ${sx(cur.r1)},${sy(Math.max(0, s.m1 - s.t1 * cur.r1))} ${sx(0)},${sy(s.m1)}`, fill: "rgba(220,38,38,0.18)" }, svg);
  if (cur.r2 > cur.r1 + 0.2) el("polygon", { points: `${sx(cur.r1)},${sy(0)} ${sx(cur.r2)},${sy(0)} ${sx(cur.r2)},${sy(Math.max(0, s.m2 - s.t2 * cur.r2))} ${sx(cur.r1)},${sy(Math.max(0, s.m2 - s.t2 * cur.r1))}`, fill: "rgba(29,78,216,0.16)" }, svg);
  if (cur.r3 > cur.r2 + 0.2) el("polygon", { points: `${sx(cur.r2)},${sy(0)} ${sx(cur.r3)},${sy(0)} ${sx(cur.r2)},${sy(Math.max(0, s.m3 - s.t3 * cur.r2))}`, fill: "rgba(5,150,105,0.16)" }, svg);

  if (Math.abs(s.m1 - ghostVt.m1) > 0.5 || Math.abs(s.t1 - ghostVt.t1) > 0.05) {
    el("line", { x1: sx(0), y1: sy(ghostVt.m1), x2: sx(Math.min(maxD, ghostVt.m1 / ghostVt.t1)), y2: sy(Math.max(0, ghostVt.m1 - ghostVt.t1 * maxD)), stroke: "#94A3B8", "stroke-width": "1.6", "stroke-dasharray": "5,4" }, svg);
  }
  const drawRL = (m, t, col) => {
    const dz = Math.min(maxD, m / t);
    el("line", { x1: sx(0), y1: sy(m), x2: sx(dz), y2: sy(Math.max(0, m - t * dz)), stroke: col, "stroke-width": "2.6" }, svg);
  };
  drawRL(s.m1, s.t1, "#DC2626");
  drawRL(s.m2, s.t2, "#1D4ED8");
  drawRL(s.m3, s.t3, "#059669");
  // Rótulos de recta y cortes de transición en el eje X estilo pizarra
  drawPill(svg, sx(Math.min(maxD * 0.16, cur.r1 * 0.55)), sy(Math.max(12, s.m1 - s.t1 * Math.min(maxD * 0.16, cur.r1 * 0.55))) - 14, "LR1 (Lechería)", "#DC2626", "#FEF2F2", "start", "10");
  drawPill(svg, sx((cur.r1 + cur.r2) * 0.5), sy(Math.max(12, s.m2 - s.t2 * ((cur.r1 + cur.r2) * 0.5))) - 14, "LR2 (Agroind.)", "#1D4ED8", "#EFF6FF", "middle", "10");
  drawPill(svg, sx((cur.r2 + cur.r3) * 0.5), sy(Math.max(12, s.m3 - s.t3 * ((cur.r2 + cur.r3) * 0.5))) - 14, "LR3 (Forestal)", "#059669", "#ECFDF5", "middle", "10");
  if (cur.r1 > 0.5 && cur.r1 < maxD) {
    const y12 = Math.max(0, s.m1 - s.t1 * cur.r1);
    el("line", { x1: sx(cur.r1), y1: sy(y12), x2: sx(cur.r1), y2: H - M.b, stroke: "#DC2626", "stroke-dasharray": "4,3" }, svg);
    el("circle", { cx: sx(cur.r1), cy: sy(y12), r: 4.8, fill: "#DC2626", stroke: "#FFF", "stroke-width": "1.4" }, svg);
    drawPill(svg, sx(cur.r1), H - M.b + 28, `r1=${fmtDec(cur.r1,1)}`, "#DC2626", "#FEF2F2", "middle", "9.6");
  }
  if (cur.r2 > cur.r1 + 0.5 && cur.r2 < maxD) {
    const y23 = Math.max(0, s.m2 - s.t2 * cur.r2);
    el("line", { x1: sx(cur.r2), y1: sy(y23), x2: sx(cur.r2), y2: H - M.b, stroke: "#1D4ED8", "stroke-dasharray": "4,3" }, svg);
    el("circle", { cx: sx(cur.r2), cy: sy(y23), r: 4.8, fill: "#1D4ED8", stroke: "#FFF", "stroke-width": "1.4" }, svg);
    drawPill(svg, sx(cur.r2), H - M.b + 28, `r2=${fmtDec(cur.r2,1)}`, "#1D4ED8", "#EFF6FF", "middle", "9.6");
  }

  if (Math.abs(dr1) >= 0.4) {
    drawArrow(svg, sx(gho.r1), sy(maxR * 0.84), sx(cur.r1), sy(maxR * 0.84), dr1 > 0 ? "#15803D" : "#DC2626", dr1 > 0 ? "arr-green" : "arr-red",
      `${dr1 > 0 ? "→ +" : "← -"}${fmtDec(Math.abs(dr1), 1)} km`, (sx(gho.r1) + sx(cur.r1)) / 2, sy(maxR * 0.91));
  }

  // Mapa concéntrico derecho
  const cx = 775, cy = 200, maxPixR = 152;
  const sr = km => (Math.min(km, maxD) / maxD) * maxPixR;
  const tMap = el("text", { x: cx, y: 24, fill: "#0F172A", "font-size": "12", "font-weight": "700", "text-anchor": "middle" }, svg);
  tMap.textContent = "Mapa Espacial de Anillos Concéntricos";
  el("circle", { cx, cy, r: sr(cur.r3), fill: "rgba(5,150,105,0.22)", stroke: "#059669", "stroke-width": "1.8" }, svg);
  el("circle", { cx, cy, r: sr(cur.r2), fill: "rgba(29,78,216,0.24)", stroke: "#1D4ED8", "stroke-width": "1.8" }, svg);
  el("circle", { cx, cy, r: sr(cur.r1), fill: "rgba(220,38,38,0.28)", stroke: "#DC2626", "stroke-width": "2" }, svg);
  if (Math.abs(dr1) >= 0.4) {
    el("circle", { cx, cy, r: sr(gho.r1), fill: "none", stroke: "#64748B", "stroke-width": "1.6", "stroke-dasharray": "5,4" }, svg);
    drawArrow(svg, cx + sr(gho.r1), cy, cx + sr(cur.r1), cy, dr1 > 0 ? "#15803D" : "#DC2626", dr1 > 0 ? "arr-green" : "arr-red", "", cx, cy);
  }
  el("circle", { cx, cy, r: 8, fill: "#0F172A" }, svg);
  const tCen = el("text", { x: cx, y: cy + 21, fill: "#0F172A", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
  tCen.textContent = "Mercado";

  renderFormulaStrip("vt-fstrip", [
    {
      lbl: "Renta Locacional LR(d)", col: "#DC2626",
      eq: `LR<sub>1</sub>(d) = <span class="sym-r">M<sub>1</sub></span> − <span class="sym-o">t<sub>1</sub></span>·d`,
      sub: `LR<sub>1</sub>(d) = ${eChip(fmtDec(s.m1,0),s.m1,"vt_m1","2","vc-r","Margen M1")} − ${eChip(fmtDec(s.t1,1),s.t1,"vt_t1","0.1","vc-o","Flete t1")}·d`,
      note: `Anillo 2: LR<sub>2</sub> = ${fmtDec(s.m2,0)} − ${fmtDec(s.t2,1)}·d · Haz clic en cualquier cápsula con borde punteado para editar`
    },
    {
      lbl: "Corte Anillo 1 → 2 (LR1 = LR2)", col: "#1D4ED8",
      eq: `d<sub>12</sub> = ${mFrac('<span class="sym-r">M<sub>1</sub></span> − <span class="sym-b">M<sub>2</sub></span>', '<span class="sym-o">t<sub>1</sub></span> − <span class="sym-t">t<sub>2</sub></span>')}`,
      sub: `d<sub>12</sub> = ${mFrac(eChip(fmtDec(s.m1,0),s.m1,"vt_m1","2","vc-r","M1") + " − " + eChip(fmtDec(s.m2,0),s.m2,"vt_m2","2","vc-b","M2"), eChip(fmtDec(s.t1,1),s.t1,"vt_t1","0.1","vc-o","t1") + " − " + eChip(fmtDec(s.t2,1),s.t2,"vt_t2","0.1","vc-t","t2"))} = ${rChip(fmtDec(Math.max(0,d12),1) + " km")}`,
      note: `Numerador: ${fmtDec(s.m1-s.m2,0)} | Dif. flete: ${fmtDec(s.t1-s.t2,1)}`
    },
    {
      lbl: "Frontera Agrícola (LR3 = 0)", col: "#059669",
      eq: `d<sub>máx</sub> = ${mFrac('<span class="sym-t">M<sub>3</sub></span>', '<span class="sym-p">t<sub>3</sub></span>')}`,
      sub: `d<sub>máx</sub> = ${mFrac(eChip(fmtDec(s.m3,0),s.m3,"vt_m3","2","vc-t","Margen M3"), eChip(fmtDec(s.t3,2),s.t3,"vt_t3","0.05","vc-p","Flete t3"))} = ${rChip(fmtDec(d30,1) + " km")}`,
      note: `Más allá de ${fmtDec(d30,1)} km la renta es negativa`
    }
  ]);
  renderPedBox("ped-thunen",
    `La actividad que puja más alto en el borde urbano gana el suelo: hoy <b>Lechería</b> domina hasta <b>${fmtDec(cur.r1,1)} km</b> (pendiente −${fmtDec(s.t1,1)}/km), luego cede paso a <b>Agroindustria</b> hasta <b>${fmtDec(cur.r2,1)} km</b> y finalmente a <b>Forestal</b> hasta el borde de cultivo en <b>${fmtDec(cur.r3,1)} km</b>.`,
    `<b>¿Por qué la lechería no se instala lejos aunque la tierra sea barata?</b> Porque la leche fresca es perecible y pesada (flete t<sub>1</sub> alto): cada kilómetro extra devora su margen mucho más rápido que en la madera o los granos. Si cae t<sub>1</sub> (refrigeración o mejor ruta), el anillo interior se expande y desplaza a la agroindustria.`,
    `En la Provincia de Osorno este mecanismo explica el cinturón lechero cercano a la Ruta 5 y centros de acopio, mientras predios más alejados hacia la precordillera o costa derivan a ganadería extensiva o uso forestal. En prueba: siempre despeja primero los cortes <b>LR<sub>1</sub>=LR<sub>2</sub></b> y <b>LR<sub>2</sub>=LR<sub>3</sub></b>.`
  );
}

// ============================================================================
// 2. WEBER (TRIÁNGULO LOCACIONAL, IM E ISODÁPANA CRÍTICA)
// ============================================================================
const WB_M1 = { x: 180, y: 78, name: "MP1 (Bosque/Predio)" };
const WB_M2 = { x: 180, y: 325, name: "MP2 (Insumo 2)" };
const WB_MK = { x: 700, y: 202, name: "Mercado (Ciudad)" };
const WB_L  = { x: 525, y: 86,  name: "Enclave Laboral L" };
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
      nx += (w * px) / d; ny += (w * py) / d; den += w / d;
    }
    x = nx / den; y = ny / den;
  }
  const costFn = (px, py) => (w1 * Math.hypot(px - WB_M1.x, py - WB_M1.y) + w2 * Math.hypot(px - WB_M2.x, py - WB_M2.y) + wm * Math.hypot(px - WB_MK.x, py - WB_MK.y)) / 100;
  return { x, y, costMin: costFn(x, y), costAtL: costFn(WB_L.x, WB_L.y), costFn };
}
function fijarGhostWeber() {
  ghostWb = { w1: +document.getElementById("wb-w1").value, w2: +document.getElementById("wb-w2").value, wm: +document.getElementById("wb-wm").value, ah: +document.getElementById("wb-ah").value };
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
  document.getElementById("wb-w1").value = 12; document.getElementById("wb-w2").value = 12; document.getElementById("wb-wm").value = 70; document.getElementById("wb-ah").value = 45;
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
  const w1 = +document.getElementById("wb-w1").value, w2 = +document.getElementById("wb-w2").value;
  const wm = +document.getElementById("wb-wm").value, ah = +document.getElementById("wb-ah").value;
  document.getElementById("wb-w1-v").textContent = w1 + " t";
  document.getElementById("wb-w2-v").textContent = w2 + " t";
  document.getElementById("wb-wm-v").textContent = wm + " t";
  document.getElementById("wb-ah-v").textContent = "$" + ah + " / unid";

  const im = (w1 + w2) / wm;
  const opt = solveWeber(w1, w2, wm), gOpt = solveWeber(ghostWb.w1, ghostWb.w2, ghostWb.wm);
  const extraCostL = opt.costAtL - opt.costMin;
  const convieneL = ah > extraCostL && ah > 0;

  document.getElementById("wb-enunciado").innerHTML =
    `Una industria utiliza dos materias primas localizadas de pesos <b>W<sub>1</sub> = ${w1} t</b> y <b>W<sub>2</sub> = ${w2} t</b> para elaborar un producto final de <b>W<sub>M</sub> = ${wm} t</b>. ` +
    `Existe además un enclave laboral <b>L</b> que ofrece un ahorro salarial de <b>$${ah}/unidad</b>. Determine el Índice de Materiales (IM), la ubicación óptima P* y si conviene desviarse hacia L.`;

  document.getElementById("wb-sol").innerHTML =
    `<b>IM</b> = (${w1}+${w2})/${wm} = <b>${fmtDec(im,2)}</b> (${im > 1.05 ? "IM > 1 ⇒ pérdida de peso, atracción hacia insumos" : (im < 0.95 ? "IM < 1 ⇒ ganancia de peso, atracción hacia mercado" : "IM ≈ 1 ⇒ equilibrio")}) | ` +
    `<b>Isodápana Crítica:</b> Sobre-costo flete hacia L = <b>+$${fmtDec(extraCostL,1)}</b> vs. Ahorro salarial = <b>$${ah}</b> ⇒ <b>${convieneL ? "CONVIENE DESVIAR A L (Ahorro neto +$" + fmtDec(ah - extraCostL,1) + ")" : "PERMANECER EN P*"}</b>`;

  document.getElementById("wb-k-im").textContent = fmtDec(im, 2);
  document.getElementById("wb-k-ori").textContent = im > 1.05 ? "IM > 1: Insumos" : (im < 0.95 ? "IM < 1: Mercado" : "IM ≈ 1: Intermedio");
  document.getElementById("wb-k-ct").textContent = "$" + fmtDec(opt.costMin, 1);
  document.getElementById("wb-k-dl").textContent = "+$" + fmtDec(extraCostL, 1);
  document.getElementById("wb-k-iso").textContent = `Ahorro L = $${ah}`;
  document.getElementById("wb-k-dec").textContent = convieneL ? "DESVIAR A L" : "PERMANECER EN P*";
  document.getElementById("wb-k-dec2").textContent = convieneL ? `Neto: +$${fmtDec(ah - extraCostL, 1)}/unid` : "L fuera de isodápana";

  const svg = document.getElementById("svg-weber");
  svg.innerHTML = "";
  addDefs(svg);
  el("polygon", { points: `${WB_M1.x},${WB_M1.y} ${WB_M2.x},${WB_M2.y} ${WB_MK.x},${WB_MK.y}`, fill: "#F8FAFC", stroke: "#CBD5E1", "stroke-width": "2" }, svg);

  if (ah > 2) {
    const isoPts = [];
    for (let k = 0; k < 48; k++) {
      const ang = (k / 48) * Math.PI * 2;
      let lo = 0, hi = 420;
      for (let b = 0; b < 14; b++) {
        const mid = (lo + hi) / 2;
        if (opt.costFn(opt.x + Math.cos(ang) * mid, opt.y + Math.sin(ang) * mid) - opt.costMin < ah) lo = mid; else hi = mid;
      }
      isoPts.push(`${(opt.x + Math.cos(ang) * lo).toFixed(1)},${(opt.y + Math.sin(ang) * lo).toFixed(1)}`);
    }
    el("polygon", { points: isoPts.join(" "), fill: convieneL ? "rgba(21,128,61,0.14)" : "rgba(234,88,12,0.10)", stroke: convieneL ? "#15803D" : "#EA580C", "stroke-width": "2", "stroke-dasharray": "6,4" }, svg);
    drawPill(svg, opt.x, Math.min(378, opt.y + 68), `Isodápana Crítica ($${ah})`, convieneL ? "#15803D" : "#EA580C", "#FFFFFF", "middle", "10.2");
  }
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

  if (Math.hypot(opt.x - gOpt.x, opt.y - gOpt.y) > 8) {
    el("circle", { cx: gOpt.x, cy: gOpt.y, r: 6, fill: "#94A3B8" }, svg);
    drawArrow(svg, gOpt.x, gOpt.y, opt.x, opt.y, "#DC2626", "arr-red", "Movimiento P*", (gOpt.x + opt.x) / 2, (gOpt.y + opt.y) / 2 - 12);
  }
  if (convieneL) drawArrow(svg, opt.x, opt.y, WB_L.x, WB_L.y, "#15803D", "arr-green", "Salto óptimo → L", (opt.x + WB_L.x) / 2 + 12, (opt.y + WB_L.y) / 2 - 10, "start");

  const drawNode = (pt, col, sub, anchor="middle", dy=-14) => {
    el("circle", { cx: pt.x, cy: pt.y, r: 9, fill: col, stroke: "#FFFFFF", "stroke-width": "2" }, svg);
    const t = el("text", { x: pt.x, y: pt.y + dy, fill: "#0F172A", "font-size": "11.5", "font-weight": "700", "text-anchor": anchor }, svg);
    t.textContent = `${pt.name} ${sub}`;
  };
  drawNode(WB_M1, "#1D4ED8", `(${w1}t)`, "middle", -14);
  drawNode(WB_M2, "#1D4ED8", `(${w2}t)`, "middle", 22);
  drawNode(WB_MK, "#0F172A", `(${wm}t)`, "start", 4);
  drawNode(WB_L, convieneL ? "#15803D" : "#EA580C", `(-$${ah})`, "start", -12);
  el("circle", { cx: opt.x, cy: opt.y, r: 8.5, fill: "#DC2626", stroke: "#FFFFFF", "stroke-width": "2" }, svg);
  const tP = el("text", { x: opt.x, y: opt.y + 22, fill: "#DC2626", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  tP.textContent = "P* (Fábrica)";

  renderFormulaStrip("wb-fstrip", [
    {
      lbl: "Índice de Materiales (IM)", col: "#1D4ED8",
      eq: `IM = ${mFrac('<span class="sym-b">W<sub>1</sub></span> + <span class="sym-t">W<sub>2</sub></span>', '<span class="sym-p">W<sub>M</sub></span>')}`,
      sub: `IM = ${mFrac(eChip(w1+"t",w1,"wb_w1","1","vc-b","Peso MP1") + " + " + eChip(w2+"t",w2,"wb_w2","1","vc-t","Peso MP2"), eChip(wm+"t",wm,"wb_wm","1","vc-p","Peso Producto Final"))} = ${mFrac(w1+w2, wm)} = ${rChip(fmtDec(im,2))}`,
      note: im > 1.05 ? "IM &gt; 1 → Pierde peso (atracción a insumos)" : (im < 0.95 ? "IM &lt; 1 → Gana peso (atracción a mercado)" : "IM ≈ 1 → Equilibrio")
    },
    {
      lbl: "Prueba Isodápana Crítica", col: "#EA580C",
      eq: `<span class="sym-t">Ahorro<sub>L</sub></span> &gt; <span class="sym-o">ΔFlete(P*→L)</span>`,
      sub: `${eChip("$"+ah,ah,"wb_ah","5","vc-t","Ahorro salarial en L")} ${convieneL ? "&gt;" : "≤"} ${vChip("$"+fmtDec(extraCostL,1),"vc-o","Sobrecosto flete hacia L")} ⇒ ${rChip(convieneL ? "Saltar a L" : "Quedar en P*", !convieneL)}`,
      note: convieneL ? "L cae dentro de la curva isodápana" : "L queda fuera de la curva isodápana"
    },
    {
      lbl: "Balance Neto por Unidad", col: "#15803D",
      eq: `Δ<sub>neto</sub> = <span class="sym-t">Ahorro<sub>L</sub></span> − <span class="sym-o">ΔFlete</span>`,
      sub: `Δ<sub>neto</sub> = ${eChip("$"+ah,ah,"wb_ah","5","vc-t","Ahorro L")} − ${vChip("$"+fmtDec(extraCostL,1),"vc-o","ΔFlete")} = ${rChip((ah-extraCostL>=0?"+":"-")+"$"+fmtDec(Math.abs(ah-extraCostL),1), ah < extraCostL)}`,
      note: `Costo mínimo de flete en P*: $${fmtDec(opt.costMin,1)}`
    }
  ]);
  renderPedBox("ped-weber",
    `Con <b>IM = ${fmtDec(im,2)}</b>, los insumos localizados pesan ${im > 1.05 ? "más" : (im < 0.95 ? "menos" : "casi lo mismo")} que el producto final; por eso el punto óptimo de transporte <b>P*</b> se inclina hacia ${im > 1.05 ? "los vértices MP1 y MP2" : (im < 0.95 ? "el Mercado consumidor" : "el centro del triángulo")}. Hoy el desvío hacia el enclave L ${convieneL ? "<b>sí conviene</b> (L cae dentro de la isodápana)" : "<b>no conviene</b> (L queda fuera de la isodápana)"}.`,
    `<b>Paradoja de las bebidas vs. aserraderos:</b> una embotelladora (ej. Coca-Cola) agrega agua (insumo ubicuo disponible en toda ciudad), por lo que su producto pesa mucho más que el jarabe concentrado (<b>IM &lt; 1</b>) y se instala pegada a la ciudad. En cambio, un aserradero o planta de leche en polvo elimina agua/corteza (<b>IM &gt; 1</b>) y se ubica junto al bosque o los predios.`,
    `La <b>Isodápana Crítica</b> es el límite exacto donde el ahorro salarial en L iguala al sobrecosto de flete adicional. Regla de control (Duch Brown): solo se abandona P* si L queda estrictamente <b>dentro</b> de la curva cerrada.`
  );
}

// ============================================================================
// 3. KRUGMAN (1991) — CENTRO-PERIFERIA Y UMBRAL τ*
// ============================================================================
let ghostKr = { tau: 3.5, esc: 7.0, mov: 6.5 };
let animKrId = null;

function calcKrugman(tau, esc, mov) {
  const ust = 0.45 * esc + 0.35 * mov;
  const pres = (ust - tau) * 1.45;
  let cen = Math.min(95, Math.max(50, 50 + 43 / (1 + Math.exp(-pres))));
  return { ust, cen, per: 100 - cen };
}
function fijarGhostKrugman() { ghostKr = { tau: +document.getElementById("kr-tau").value, esc: +document.getElementById("kr-esc").value, mov: +document.getElementById("kr-mov").value }; drawKrugman(); }
function resetKrugman() {
  if (animKrId) cancelAnimationFrame(animKrId);
  document.getElementById("kr-tau").value = 3.5; document.getElementById("kr-esc").value = 7.0; document.getElementById("kr-mov").value = 6.5;
  ghostKr = { tau: 3.5, esc: 7.0, mov: 6.5 }; drawKrugman();
}
function animarKrugman() {
  if (animKrId) cancelAnimationFrame(animKrId);
  document.getElementById("kr-tau").value = 9.5; fijarGhostKrugman();
  const t0 = performance.now(), dur = 2100;
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
  const tau = +document.getElementById("kr-tau").value, esc = +document.getElementById("kr-esc").value, mov = +document.getElementById("kr-mov").value;
  document.getElementById("kr-tau-v").textContent = fmtDec(tau, 1);
  document.getElementById("kr-esc-v").textContent = fmtDec(esc, 1);
  document.getElementById("kr-mov-v").textContent = fmtDec(mov, 1);
  setDelta("kr-tau-d", tau - ghostKr.tau, 1);

  const cur = calcKrugman(tau, esc, mov), gho = calcKrugman(ghostKr.tau, ghostKr.esc, ghostKr.mov);
  const aglom = tau <= cur.ust;

  document.getElementById("kr-enunciado").innerHTML =
    `En una economía de dos regiones (<b>Capital Regional</b> y <b>Periferia</b>) con economías de escala = <b>${fmtDec(esc,1)}</b> y movilidad laboral = <b>${fmtDec(mov,1)}</b>, ` +
    `el umbral crítico de bifurcación se ubica en <b>τ* = ${fmtDec(cur.ust,2)}</b>. Con un costo de transporte actual de <b>τ = ${fmtDec(tau,1)}</b>, ` +
    `predominan las fuerzas <b>${aglom ? "centrípetas (aglomeración hacia el centro: " + fmtDec(cur.cen,1) + "%)" : "centrífugas (equilibrio disperso entre regiones)"}</b>.`;

  document.getElementById("kr-k-ust").textContent = fmtDec(cur.ust, 2);
  document.getElementById("kr-k-cen").textContent = fmtDec(cur.cen, 1) + "%";
  document.getElementById("kr-k-reg").textContent = aglom ? "Aglomeración" : "Equilibrio Disperso";
  document.getElementById("kr-k-per").textContent = fmtDec(cur.per, 1) + "%";
  document.getElementById("kr-k-per2").textContent = `${fmtDec(cur.per - 50, 1)} pp vs 50%`;
  document.getElementById("kr-k-fza").textContent = aglom ? "Centrípeta →" : "Centrífuga ↔";
  document.getElementById("kr-k-fza2").textContent = aglom ? "τ ≤ τ* (Macrocefalia)" : "τ > τ* (Protege periferia)";

  const svg = document.getElementById("svg-krugman");
  svg.innerHTML = "";
  addDefs(svg);
  const M = { l: 55, r: 440, t: 28, b: 46 }, W = 980, H = 385;
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
  // Zonas de régimen estilo pizarra (Aglomeración vs Dispersión)
  el("rect", { x: M.l, y: M.t, width: Math.max(0, sx(cur.ust) - M.l), height: H - M.b - M.t, fill: "rgba(220,38,38,0.05)" }, svg);
  el("rect", { x: sx(cur.ust), y: M.t, width: Math.max(0, (W - M.r) - sx(cur.ust)), height: H - M.b - M.t, fill: "rgba(21,128,61,0.05)" }, svg);
  el("line", { x1: M.l, y1: sy(50), x2: W - M.r, y2: sy(50), stroke: "#94A3B8", "stroke-dasharray": "4,3" }, svg);
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Cuota Capital Regional (%)", "Costo de Transporte (τ)");
  el("line", { x1: sx(cur.ust), y1: M.t, x2: sx(cur.ust), y2: H - M.b, stroke: "#D97706", "stroke-width": "2.2", "stroke-dasharray": "6,4" }, svg);
  drawPill(svg, sx(cur.ust), M.t + 14, `Umbral τ* = ${fmtDec(cur.ust, 1)}`, "#B45309", "#FEF3C7", "middle", "10.2");
  if (sx(cur.ust) - M.l > 110) {
    const tz1 = el("text", { x: (M.l + sx(cur.ust)) / 2, y: sy(54), fill: "#991B1B", "font-size": "10.3", "font-weight": "800", "text-anchor": "middle" }, svg);
    tz1.textContent = "Centro-Periferia (τ ≤ τ*)";
  }
  if ((W - M.r) - sx(cur.ust) > 110) {
    const tz2 = el("text", { x: (sx(cur.ust) + (W - M.r)) / 2, y: sy(92), fill: "#166534", "font-size": "10.3", "font-weight": "800", "text-anchor": "middle" }, svg);
    tz2.textContent = "Equilibrio Disperso (τ > τ*)";
  }

  const pts = [];
  for (let t = 1; t <= 10.01; t += 0.15) pts.push(`${sx(t).toFixed(1)},${sy(calcKrugman(t, esc, mov).cen).toFixed(1)}`);
  el("polyline", { points: pts.join(" "), fill: "none", stroke: "#1D4ED8", "stroke-width": "2.8" }, svg);

  if (Math.hypot(sx(tau) - sx(ghostKr.tau), sy(cur.cen) - sy(gho.cen)) > 10) {
    el("circle", { cx: sx(ghostKr.tau), cy: sy(gho.cen), r: 5.5, fill: "#94A3B8" }, svg);
    drawArrow(svg, sx(ghostKr.tau), sy(gho.cen), sx(tau), sy(cur.cen), "#DC2626", "arr-red", `${cur.cen >= gho.cen ? "↑ +" : "↓ -"}${fmtDec(Math.abs(cur.cen - gho.cen), 1)} pp`, (sx(ghostKr.tau) + sx(tau)) / 2, (sy(gho.cen) + sy(cur.cen)) / 2 - 12);
  }
  el("circle", { cx: sx(tau), cy: sy(cur.cen), r: 7, fill: "#DC2626", stroke: "#FFFFFF", "stroke-width": "2" }, svg);

  const xCen = 665, xPer = 880, yMid = 200;
  const rCen = 28 + (cur.cen / 100) * 56, rPer = 22 + (cur.per / 100) * 56;
  el("circle", { cx: xCen, cy: yMid, r: rCen, fill: "rgba(29,78,216,0.22)", stroke: "#1D4ED8", "stroke-width": "2.4" }, svg);
  el("circle", { cx: xPer, cy: yMid, r: rPer, fill: "rgba(100,116,139,0.22)", stroke: "#475569", "stroke-width": "2" }, svg);
  const mkT = (x, y, txt, sz, col) => { const n = el("text", { x, y, fill: col, "font-size": sz, "font-weight": "800", "text-anchor": "middle" }, svg); n.textContent = txt; };
  mkT(xCen, yMid - 4, "Capital Regional", 11.5, "#1E3A8A");
  mkT(xCen, yMid + 14, fmtDec(cur.cen, 1) + "%", 14, "#1D4ED8");
  mkT(xPer, yMid - 4, "Periferia", 11.5, "#334155");
  mkT(xPer, yMid + 14, fmtDec(cur.per, 1) + "%", 13.5, "#475569");
  if (aglom) {
    drawArrow(svg, xPer - rPer - 6, yMid - 14, xCen + rCen + 8, yMid - 14, "#DC2626", "arr-red", "Aglomeración (Backwash)", 775, yMid - 42);
    drawArrow(svg, xPer - rPer - 6, yMid + 14, xCen + rCen + 8, yMid + 14, "#DC2626", "arr-red", "", 0, 0);
  } else {
    drawArrow(svg, xCen + rCen + 8, yMid, xPer - rPer - 8, yMid, "#15803D", "arr-green", "Equilibrio Disperso", 775, yMid - 20);
  }

  renderFormulaStrip("kr-fstrip", [
    {
      lbl: "Umbral Crítico de Bifurcación (τ*)", col: "#D97706",
      eq: `τ* = 0,45·<span class="sym-b">Esc</span> + 0,35·<span class="sym-p">Mov</span>`,
      sub: `τ* = 0,45·${eChip(fmtDec(esc,1),esc,"kr_e","0.2","vc-b","Economías de escala (1–10)")} + 0,35·${eChip(fmtDec(mov,1),mov,"kr_m","0.2","vc-p","Movilidad laboral (1–10)")} = ${rChip(fmtDec(cur.ust,2))}`,
      note: `Fijación monopolística: p*(x) = a·W(x) / ρ`
    },
    {
      lbl: "Condición de Régimen Espacial", col: "#1D4ED8",
      eq: `<span class="sym-r">τ</span> ≤ <span class="sym-o">τ*</span> ⇒ Aglomeración`,
      sub: `${eChip("τ="+fmtDec(tau,1),tau,"kr_t","0.1","vc-r","Costo transporte τ (1–10)")} ${aglom ? "≤" : "&gt;"} ${vChip("τ*="+fmtDec(cur.ust,2),"vc-o","Umbral crítico")} ⇒ ${rChip(aglom ? "Centro-Periferia" : "Dispersión", aglom)}`,
      note: aglom ? "Fuerzas centrípetas dominan" : "Fuerzas centrífugas protegen la periferia"
    },
    {
      lbl: "Reparto del Mercado (Centro vs. Periferia)", col: "#DC2626",
      eq: `<span class="sym-b">s<sub>Centro</sub></span> + <span class="sym-t">s<sub>Periferia</sub></span> = 100%`,
      sub: `${vChip(fmtDec(cur.cen,1)+"%","vc-b","Cuota Capital Regional","kr_c")} + ${vChip(fmtDec(cur.per,1)+"%","vc-t","Cuota Periferia")} = ${rChip("100%")}`,
      note: `Brecha vs. simetría (50%): ${cur.cen >= 50 ? "+" : ""}${fmtDec(cur.cen-50,1)} pp`
    }
  ]);
  renderPedBox("ped-krugman",
    `El umbral de bifurcación está en <b>τ* = ${fmtDec(cur.ust,2)}</b>. Con transporte <b>τ = ${fmtDec(tau,1)}</b>, la economía se encuentra en régimen ${aglom ? `<b>Centro-Periferia</b> (${fmtDec(cur.cen,1)}% concentrado en la capital)` : `<b>disperso</b> (${fmtDec(cur.cen,1)}% vs. ${fmtDec(cur.per,1)}%)`}. Subir economías de escala o movilidad laboral empuja τ* hacia la derecha y vuelve más fácil que ocurra aglomeración.`,
    `<b>La Paradoja de la Carretera:</b> intuimos que pavimentar una autopista hacia una comuna pequeña siempre la hará crecer. Krugman (Premio Nobel 2008) demostró lo contrario: si el flete cae bajo τ*, las fábricas ya no necesitan tener sucursal en la periferia; producen todo en la gran ciudad aprovechando escala y despachan barato hacia afuera, vaciando la periferia.`,
    `Esta tensión entre <b>fuerzas centrípetas</b> (mercado local, encadenamientos, escala) y <b>centrífugas</b> (fletes altos, rentas del suelo, congestión) explica por qué Chile concentra PIB en la RM y por qué las políticas regionales necesitan acompañar infraestructura vial con fomento productivo local.`
  );
}

// ============================================================================
// 4. PERROUX, MYRDAL Y HIRSCHMAN (5 RONDAS + SPREAD VS. BACKWASH A 60 FPS)
// ============================================================================
let ghostPx = 2500;
function fijarGhostPerroux() {
  const i0 = +document.getElementById("px-i0").value;
  const p = Math.min(0.88, +document.getElementById("px-b").value + +document.getElementById("px-f").value);
  ghostPx = i0 / (1 - p);
  drawPerroux();
}
function presetPerroux(tipo) {
  fijarGhostPerroux();
  if (tipo === "pymemad") { document.getElementById("px-i0").value = 1000; document.getElementById("px-b").value = 0.35; document.getElementById("px-f").value = 0.25; document.getElementById("px-sp").value = 65; }
  else if (tipo === "lacteo") { document.getElementById("px-i0").value = 1200; document.getElementById("px-b").value = 0.40; document.getElementById("px-f").value = 0.22; document.getElementById("px-sp").value = 70; }
  else { document.getElementById("px-i0").value = 1000; document.getElementById("px-b").value = 0.12; document.getElementById("px-f").value = 0.08; document.getElementById("px-sp").value = 25; }
  drawPerroux();
}
function drawPerroux() {
  const i0 = +document.getElementById("px-i0").value;
  const b = +document.getElementById("px-b").value;
  const f = +document.getElementById("px-f").value;
  const spPct = +document.getElementById("px-sp").value;
  document.getElementById("px-i0-v").textContent = `$${fmtInt(i0)} MM`;
  document.getElementById("px-b-v").textContent = fmtDec(b, 2);
  document.getElementById("px-f-v").textContent = fmtDec(f, 2);
  document.getElementById("px-sp-v").textContent = spPct + "%";

  const prop = Math.min(0.88, b + f);
  const mh = 1 / (1 - prop);
  const tot = i0 * mh;
  const ind = tot - i0;
  const spread = ind * (spPct / 100);
  const backwash = ind * ((100 - spPct) / 100) * 0.6;
  const saldo = spread - backwash;

  document.getElementById("px-enunciado").innerHTML =
    `Una industria motriz (<b>Perroux</b>) inyecta <b>I<sub>0</sub> = $${fmtInt(i0)} MM</b> en un polo regional con encadenamientos hacia atrás <b>b = ${fmtDec(b,2)}</b> y hacia adelante <b>f = ${fmtDec(f,2)}</b>. ` +
    `De los efectos indirectos inducidos, el <b>${spPct}%</b> se difunde hacia comunas vecinas (<i>Spread</i>) mientras el resto genera atracción/absorción de factores hacia el centro (<i>Backwash</i>).`;

  document.getElementById("px-k-mh").textContent = fmtDec(mh, 2) + "x";
  document.getElementById("px-k-ret").textContent = `Retención b+f = ${fmtDec(prop * 100, 0)}%`;
  document.getElementById("px-k-tot").textContent = `$${fmtInt(tot)} MM`;
  document.getElementById("px-k-ind").textContent = `+$${fmtInt(ind)} MM indirectos`;
  document.getElementById("px-k-sp").textContent = `+$${fmtInt(spread)} MM`;
  document.getElementById("px-k-sal").textContent = `${saldo >= 0 ? "+" : "-"}$${fmtInt(Math.abs(saldo))} MM`;
  document.getElementById("px-k-diag").textContent = saldo >= 0 ? "Polo Integrador (Spread > Backwash)" : "Enclave Extractivo (Backwash)";

  document.getElementById("px-sol").innerHTML =
    `<b>Multiplicador:</b> M<sub>H</sub> = 1 / [1 − (${fmtDec(b,2)}+${fmtDec(f,2)})] = <b>${fmtDec(mh,2)}x</b> ⇒ Producción Total = <b>$${fmtInt(tot)} MM</b> | ` +
    `<b>Myrdal:</b> Spread ($${fmtInt(spread)}M) − Backwash ($${fmtInt(backwash)}M) = <b>${saldo >= 0 ? "+" : "-"}$${fmtInt(Math.abs(saldo))} MM</b>`;

  const svg = document.getElementById("svg-perroux");
  svg.innerHTML = "";
  addDefs(svg);

  // Izquierda: 5 rondas acumuladas
  const rondas = [], acum = [];
  let ac = 0;
  for (let r = 0; r < 5; r++) {
    const val = i0 * Math.pow(prop, r);
    ac += val;
    rondas.push(val); acum.push(ac);
  }
  const M = { l: 64, r: 360, t: 30, b: 46 }, W = 980, H = 370;
  const maxY = Math.max(tot, ghostPx) * 1.15;
  const sy = v => H - M.b - (v / maxY) * (H - M.t - M.b);
  for (let i = 0; i <= 4; i++) {
    const yv = (maxY / 4) * i;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#E2E8F0" }, svg);
    const t = el("text", { x: M.l - 8, y: sy(yv) + 4, fill: "#475569", "font-size": "11", "text-anchor": "end" }, svg);
    t.textContent = "$" + fmtInt(yv) + "M";
  }
  el("line", { x1: M.l, y1: H - M.b, x2: W - M.r, y2: H - M.b, stroke: "#334155", "stroke-width": "1.5" }, svg);

  const slotW = (W - M.l - M.r) / 5, bw = slotW * 0.56;
  const linePts = [];
  for (let r = 0; r < 5; r++) {
    const x0 = M.l + r * slotW + (slotW - bw) / 2;
    el("rect", { x: x0, y: sy(acum[r]), width: bw, height: Math.max(2, sy(0) - sy(acum[r])), fill: "#1D4ED8", opacity: "0.24", stroke: "#1D4ED8", rx: 3 }, svg);
    el("rect", { x: x0, y: sy(rondas[r]), width: bw, height: Math.max(2, sy(0) - sy(rondas[r])), fill: "#1D4ED8", rx: 3 }, svg);
    linePts.push(`${x0 + bw / 2},${sy(acum[r])}`);
    const tl = el("text", { x: x0 + bw / 2, y: H - M.b + 17, fill: "#1E293B", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = `Ronda ${r + 1}`;
    const tv = el("text", { x: x0 + bw / 2, y: sy(acum[r]) - 6, fill: "#0F172A", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, svg);
    tv.textContent = `$${fmtInt(acum[r])}M`;
  }
  el("polyline", { points: linePts.join(" "), fill: "none", stroke: "#0F172A", "stroke-width": "2.4" }, svg);

  // Derecha: Balanza Myrdal (Spread vs Backwash vs Saldo)
  const bx0 = 670, bSlot = 95, bw2 = 58;
  const maxB = Math.max(spread, backwash, Math.abs(saldo), 200) * 1.25;
  const syB = v => 295 - (v / maxB) * 220;
  const tM = el("text", { x: 805, y: 26, fill: "#0F172A", "font-size": "12", "font-weight": "700", "text-anchor": "middle" }, svg);
  tM.textContent = "Balance Myrdal: Spread vs. Backwash";
  el("line", { x1: 650, y1: 295, x2: 955, y2: 295, stroke: "#334155", "stroke-width": "1.5" }, svg);

  const itemsB = [
    { lbl: "Spread (+)", val: spread, col: "#15803D" },
    { lbl: "Backwash (−)", val: backwash, col: "#DC2626" },
    { lbl: "Saldo Neto", val: Math.abs(saldo), col: saldo >= 0 ? "#1D4ED8" : "#991B1B", sign: saldo >= 0 ? "+" : "-" },
  ];
  itemsB.forEach((it, k) => {
    const x = bx0 + k * bSlot;
    el("rect", { x, y: syB(it.val), width: bw2, height: Math.max(2, 295 - syB(it.val)), fill: it.col, rx: 4 }, svg);
    const tv = el("text", { x: x + bw2 / 2, y: syB(it.val) - 6, fill: it.col, "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
    tv.textContent = `${it.sign || ""}$${fmtInt(it.val)}M`;
    const tl = el("text", { x: x + bw2 / 2, y: 314, fill: "#1E293B", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = it.lbl;
  });

  renderFormulaStrip("px-fstrip", [
    {
      lbl: "Multiplicador de Hirschman (M_H)", col: "#1D4ED8",
      eq: `M<sub>H</sub> = ${mFrac("1", '1 − (<span class="sym-b">b</span> + <span class="sym-p">f</span>)')}`,
      sub: `M<sub>H</sub> = ${mFrac("1", "1 − (" + eChip(fmtDec(b,2),b,"px_b","0.01","vc-b","Encadenamiento atrás b") + " + " + eChip(fmtDec(f,2),f,"px_f","0.01","vc-p","Encadenamiento adelante f") + ")")} = ${mFrac("1", fmtDec(1-prop,2))} = ${rChip(fmtDec(mh,2)+"x")}`,
      note: `Retención local (b + f) = ${fmtDec(prop*100,0)}% · Clic en b o f para escribir directo`
    },
    {
      lbl: "Producción Total Inducida (Perroux)", col: "#0F172A",
      eq: `Y<sub>tot</sub> = <span class="sym-t">I<sub>0</sub></span> · <span class="sym-b">M<sub>H</sub></span>`,
      sub: `Y<sub>tot</sub> = ${eChip("$"+fmtInt(i0)+"M",i0,"px_i0","100","vc-t","Inversión motriz I0 (MM$)")} × ${vChip(fmtDec(mh,2),"vc-b","Multiplicador M_H")} = ${rChip("$"+fmtInt(tot)+"M")}`,
      note: `Efecto indirecto puro: +$${fmtInt(ind)} MM`
    },
    {
      lbl: "Balanza Periferia (Myrdal)", col: saldo >= 0 ? "#15803D" : "#DC2626",
      eq: `Saldo = <span class="sym-t">Spread</span> − <span class="sym-r">Backwash</span>`,
      sub: `Saldo = ${vChip("$"+fmtInt(spread)+"M","vc-t","Difusión Spread")} − ${vChip("$"+fmtInt(backwash)+"M","vc-r","Absorción Backwash")} = ${rChip((saldo>=0?"+":"-")+"$"+fmtInt(Math.abs(saldo))+"M", saldo < 0)}`,
      note: `Proporción Spread: ${eChip(spPct+"%",spPct,"px_sp","5","vc-g","% Difusión Spread (5–95)")} · ${saldo >= 0 ? "Polo Integrador" : "Enclave Extractivo"}`
    }
  ]);
  renderPedBox("ped-perroux",
    `Cada $1 invertido en la industria motriz genera <b>$${fmtDec(mh,2)}</b> totales en el territorio gracias a una retención local <b>b + f = ${fmtDec(prop*100,0)}%</b>. Como el efecto difusión (<b>+$${fmtInt(spread)}M</b>) ${saldo >= 0 ? "supera" : "es menor que"} la absorción hacia el centro (<b>−$${fmtInt(backwash)}M</b>), el saldo neto sobre la periferia es <b>${saldo >= 0 ? "positivo" : "negativo"}</b>.`,
    `<b>Un mega-proyecto NO siempre es un Polo de Desarrollo:</b> si una gran planta importa casi toda su maquinaria, contrata ingenieros fuera de la región y exporta materia prima sin procesar (b y f bajos), actúa como un <b>enclave extractivo</b> donde el <i>Backwash</i> (Myrdal) drena mano de obra joven y capital desde las comunas vecinas.`,
    `Para transformar un enclave en un <b>Polo Integrador</b> (como PymeMad en Biobío o el complejo lácteo en Osorno), la política regional debe subir <b>b</b> (desarrollo de proveedores locales) y <b>f</b> (encadenamientos aguas abajo con mayor valor agregado).`
  );
}

// ============================================================================
// 5. CHRISTALLER (UMBRAL/ALCANCE) + GRANOVETTER (VÍNCULOS DÉBILES A 60 FPS)
// ============================================================================
function presetChris(umb, alc) {
  document.getElementById("ch-umb").value = umb;
  document.getElementById("ch-alc").value = alc;
  drawChrisGran();
}
function presetGran(f, d) {
  document.getElementById("gr-f").value = f;
  document.getElementById("gr-d").value = d;
  drawChrisGran();
}
function drawChrisGran() {
  const pob = +document.getElementById("ch-pob").value;
  const umb = +document.getElementById("ch-umb").value;
  const alc = +document.getElementById("ch-alc").value;
  const dst = +document.getElementById("ch-dst").value;

  document.getElementById("ch-pob-v").textContent = fmtInt(pob) + " hab.";
  document.getElementById("ch-umb-v").textContent = fmtInt(umb) + " hab.";
  document.getElementById("ch-alc-v").textContent = alc + " km";
  document.getElementById("ch-dst-v").textContent = dst + " km";

  const okU = pob >= umb, okA = alc >= dst;
  const cob = (pob / Math.max(1, umb)) * 100;
  let diagC = "";
  if (okU && okA) diagC = `<span style="color:#15803D;font-weight:800;">✓ VIABLE (Cumple Umbral y Alcance):</span> Demanda cubre <b>${fmtDec(cob,1)}%</b> del umbral mínimo y el alcance (${alc} km) supera la distancia vial (${dst} km).`;
  else if (!okU && okA) diagC = `<span style="color:#DC2626;font-weight:800;">✗ DÉFICIT DE UMBRAL:</span> Faltan <b>${fmtInt(umb - pob)} hab.</b> de masa crítica (solo cubre ${fmtDec(cob,1)}%). Requiere asociar comunas vecinas.`;
  else if (okU && !okA) diagC = `<span style="color:#EA580C;font-weight:800;">⚠ FUERA DE ALCANCE ESPACIAL:</span> Hay masa crítica, pero los usuarios están a <b>${dst} km &gt; ${alc} km</b> de alcance máximo.`;
  else diagC = `<span style="color:#DC2626;font-weight:800;">✗ NO FACTIBLE:</span> No alcanza umbral mínimo ni cobertura territorial; el servicio debe concentrarse en un Lugar Central de orden superior.`;
  document.getElementById("ch-diag").innerHTML = diagC;

  // Granovetter 60 FPS
  const f = +document.getElementById("gr-f").value;
  const d = +document.getElementById("gr-d").value;
  document.getElementById("gr-f-v").textContent = `${f} / 10`;
  document.getElementById("gr-d-v").textContent = `${d} / 10`;

  const coh = f * 10;
  const inn = Math.min(100, d * 11.5 + f * 2);
  const lck = Math.max(0, f * 10 - d * 12);
  const spl = 0.45 * coh + 0.55 * inn - 0.30 * lck;

  document.getElementById("gr-k-coh").textContent = `${fmtInt(coh)} / 100`;
  document.getElementById("gr-k-inn").textContent = `${fmtInt(inn)} / 100`;
  document.getElementById("gr-k-lck").textContent = `${fmtInt(lck)}%`;
  document.getElementById("gr-k-lck2").textContent = lck > 40 ? "Red endogámica (Lock-in)" : "Puentes externos activos";
  document.getElementById("gr-k-spl").textContent = `${fmtDec(spl, 1)} pts`;

  const svg = document.getElementById("svg-gran");
  svg.innerHTML = "";
  const locNames = ["PyME 1", "PyME 2", "PyME 3", "PyME 4", "Gremio Local"];
  const extNames = ["Univ. ULagos", "Centro I+D INIA", "Comprador Ext.", "Prov. Tecnología", "CORFO / Fomento"];
  const locPts = locNames.map((nm, i) => {
    const a = (i / 5) * Math.PI * 2 - Math.PI / 2;
    return { x: 255 + 115 * Math.cos(a), y: 165 + 100 * Math.sin(a), nm };
  });
  const extPts = extNames.map((nm, i) => ({ x: 755 + (i % 2 === 0 ? 0 : 28), y: 52 + i * 56, nm }));

  const pFuertes = [[0,1],[1,2],[2,3],[3,4],[4,0],[0,2],[1,3],[2,4],[0,3],[1,4]];
  const pDebiles = [[4,0],[0,1],[1,2],[2,3],[4,4],[3,1],[0,0],[2,2],[1,3],[3,4]];

  // Enlaces fuertes (azul sólido)
  for (let i = 0; i < f; i++) {
    const [u, v] = pFuertes[i];
    el("line", { x1: locPts[u].x, y1: locPts[u].y, x2: locPts[v].x, y2: locPts[v].y, stroke: "#1D4ED8", "stroke-width": "2.6" }, svg);
  }
  // Enlaces débiles puente (rojo punteado)
  for (let i = 0; i < d; i++) {
    const [u, v] = pDebiles[i];
    el("line", { x1: locPts[u].x, y1: locPts[u].y, x2: extPts[v].x, y2: extPts[v].y, stroke: "#DC2626", "stroke-width": "2.2", "stroke-dasharray": "6,4" }, svg);
  }
  locPts.forEach(p => {
    el("circle", { cx: p.x, cy: p.y, r: 11, fill: "#1D4ED8", stroke: "#FFFFFF", "stroke-width": "2" }, svg);
    const t = el("text", { x: p.x, y: p.y - 15, fill: "#0F172A", "font-size": "11", "font-weight": "700", "text-anchor": "middle" }, svg);
    t.textContent = p.nm;
  });
  extPts.forEach(p => {
    el("circle", { cx: p.x, cy: p.y, r: 10, fill: "#DC2626", stroke: "#FFFFFF", "stroke-width": "2" }, svg);
    const t = el("text", { x: p.x + 15, y: p.y + 4, fill: "#991B1B", "font-size": "11", "font-weight": "700" }, svg);
    t.textContent = p.nm;
  });
  const tl1 = el("text", { x: 255, y: 24, fill: "#1E3A8A", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  tl1.textContent = "Clúster Comunal (Vínculos Fuertes)";
  const tl2 = el("text", { x: 785, y: 24, fill: "#991B1B", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  tl2.textContent = "Ecosistema Externo (Puentes Débiles)";

  renderFormulaStrip("cg-fstrip", [
    {
      lbl: "Cobertura de Umbral (Christaller)", col: "#1D4ED8",
      eq: `Cob = ${mFrac('<span class="sym-b">Pob</span>', '<span class="sym-p">Umbral</span>')} × 100%`,
      sub: `Cob = ${mFrac(eChip(fmtInt(pob),pob,"ch_pob","1000","vc-b","Población área influencia"), eChip(fmtInt(umb),umb,"ch_umb","1000","vc-p","Umbral mínimo"))} = ${rChip(fmtDec(cob,1)+"%", !okU)}`,
      note: `Alcance ${eChip(alc+" km",alc,"ch_alc","1","vc-t","Alcance máximo")} ${okA ? "≥" : "&lt;"} Dist ${eChip(dst+" km",dst,"ch_dst","1","vc-o","Distancia vial")}`
    },
    {
      lbl: "Riesgo de Lock-in (Granovetter)", col: "#DC2626",
      eq: `Lock = máx(0, 10·<span class="sym-b">F</span> − 12·<span class="sym-r">D</span>)`,
      sub: `Lock = máx(0, 10·${eChip(f,f,"gr_f","1","vc-b","Vínculos fuertes F (1–10)")} − 12·${eChip(d,d,"gr_d","1","vc-r","Vínculos débiles D (0–10)")}) = ${rChip(fmtInt(lck)+"%", lck > 40)}`,
      note: lck > 40 ? "Peligro de información redundante" : "Puentes externos evitan el bloqueo"
    },
    {
      lbl: "Desempeño Global del SPL", col: "#15803D",
      eq: `SPL = 0,45<span class="sym-b">Coh</span> + 0,55<span class="sym-t">Inn</span> − 0,30<span class="sym-r">Lock</span>`,
      sub: `SPL = 0,45·${vChip(fmtInt(coh),"vc-b","Cohesión")} + 0,55·${vChip(fmtInt(inn),"vc-t","Innovación")} − 0,30·${vChip(fmtInt(lck),"vc-r","Lock-in")} = ${rChip(fmtDec(spl,1))}`,
      note: "Escala sintética 0–100 pts"
    }
  ]);
  renderPedBox("ped-chrisgran",
    `En <b>Christaller</b>, el servicio ${okU && okA ? "es viable porque supera umbral y alcance" : (!okU ? "carece de masa crítica suficiente" : "excede la distancia máxima que la población está dispuesta a viajar")}. En <b>Granovetter</b>, con <b>${f}/10</b> lazos fuertes y <b>${d}/10</b> puentes débiles, el riesgo de bloqueo cognitivo es <b>${fmtInt(lck)}%</b>.`,
    `<b>La Fuerza de los Vínculos Débiles (Granovetter, 1973):</b> aunque suene contradictorio, las ideas nuevas y los nuevos clientes rara vez llegan desde tus amigos más cercanos (vínculos fuertes), porque todos leen y saben lo mismo. Quien rompe el <i>lock-in</i> es el "conocido lejano" (universidad, centro I+D, comprador externo) que conecta dos mundos separados.`,
    `Conecta ambos autores en pruebas: <b>Christaller</b> explica por qué un hospital de alta complejidad o una universidad solo existen en ciudades de orden superior (Osorno / Puerto Montt), mientras <b>Granovetter</b> explica por qué un gremio local cerrado fracasa si no tiende puentes con ULagos, INIA o CORFO.`
  );
}

// ============================================================================
// 6. LORENZ, GINI, THEIL Y PRIMACÍA URBANA (IP4 ESCALA 0–3)
// ============================================================================
let ghostLz = [275473, 174998, 50010, 48632];
function syncLorenzFromSlider(idx) {
  const v = +document.getElementById("lz-p" + idx).value;
  document.getElementById("lz-p" + idx + "-in").value = v;
  drawLorenz();
}
function syncLorenzFromInput(idx) {
  let v = parseFloat(document.getElementById("lz-p" + idx + "-in").value);
  if (!Number.isFinite(v) || v < 1) return;
  const sl = document.getElementById("lz-p" + idx);
  if (v > +sl.max) sl.max = Math.ceil(v * 1.25);
  if (v < +sl.min) sl.min = Math.max(1, Math.floor(v * 0.5));
  sl.value = v;
  drawLorenz();
}
function setLzValues(vals, labels, maxs) {
  for (let i = 0; i < 4; i++) {
    const sl = document.getElementById("lz-p" + (i + 1));
    const inp = document.getElementById("lz-p" + (i + 1) + "-in");
    sl.min = maxs[i] > 50000 ? 500 : 10;
    sl.max = maxs[i];
    sl.value = vals[i];
    inp.value = vals[i];
    document.getElementById("lz-l" + (i + 1)).textContent = labels[i];
  }
}
function presetLorenz(caso) {
  fijarGhostLorenz();
  if (caso === "lagos") {
    setLzValues([275473, 174998, 50010, 48632], ["P1: Puerto Montt", "P2: Osorno", "P3: Puerto Varas", "P4: Castro"], [600000, 350000, 250000, 200000]);
  } else if (caso === "biobio") {
    setLzValues([230375, 219441, 150992, 147322], ["P1: Concepción", "P2: Los Ángeles", "P3: San Pedro Paz", "P4: Talcahuano"], [600000, 350000, 250000, 200000]);
  } else if (caso === "equidad") {
    setLzValues([100000, 100000, 100000, 100000], ["P1: Ciudad 1", "P2: Ciudad 2", "P3: Ciudad 3", "P4: Ciudad 4"], [400000, 400000, 400000, 400000]);
  } else {
    setLzValues([5520, 4541, 122, 50], ["P1: Villa Esperanza", "P2: El Rincón", "P3: Pueblo Nuevo", "P4: El Quebradero"], [20000, 10000, 5000, 5000]);
  }
  drawLorenz();
}
function fijarGhostLorenz() {
  ghostLz = [1, 2, 3, 4].map(i => Math.max(1, +document.getElementById("lz-p" + i + "-in").value || +document.getElementById("lz-p" + i).value));
  drawLorenz();
}
function calcLorenz(arr, alpha = 2.0) {
  const ord = [...arr].sort((a, b) => a - b);
  const tot = ord.reduce((s, v) => s + v, 0) || 1;
  const n = ord.length;
  const pts = [{ p: 0, q: 0 }];
  let acc = 0, areaTrap = 0, theil = 0, hhi = 0, sumAlpha = 0;
  const traps = [], shares = [];
  for (let i = 0; i < n; i++) {
    const qPrev = acc / tot;
    acc += ord[i];
    const qCur = acc / tot;
    pts.push({ p: (i + 1) / n, q: qCur });
    const tr = (1 / n) * (qPrev + qCur);
    traps.push(tr);
    areaTrap += tr;
    const si = ord[i] / tot;
    shares.push(si);
    if (si > 0) {
      theil += si * Math.log(n * si);
      hhi += si * si;
      sumAlpha += Math.pow(si, alpha);
    }
  }
  const hk = Math.pow(Math.max(1e-12, sumAlpha), 1 / (1 - alpha));
  return { pts, traps, shares, gini: Math.max(0, 1 - areaTrap), areaTrap, theil: Math.max(0, theil), hhi, hk, tot };
}
function drawLorenz() {
  const arr = [1, 2, 3, 4].map(i => Math.max(1, +document.getElementById("lz-p" + i + "-in").value || +document.getElementById("lz-p" + i).value));
  const alpha = +document.getElementById("lz-al").value;
  document.getElementById("lz-al-v").textContent = "α = " + fmtDec(alpha, 1);

  const desc = [...arr].sort((a, b) => b - a);
  const sum234 = desc[1] + desc[2] + desc[3];
  const ip4 = desc[0] / Math.max(1, sum234);
  const ip2 = desc[0] / Math.max(1, desc[1]);
  const cur = calcLorenz(arr, alpha), gho = calcLorenz(ghostLz, alpha);

  let catTxt = "Valor 0: Muy Dispersa";
  if (ip4 >= 1.50) catTxt = "Valor 3: Alt. Concentrada";
  else if (ip4 >= 1.00) catTxt = "Valor 2: Concentrada";
  else if (ip4 >= 0.65) catTxt = "Valor 1: Dispersa";

  document.getElementById("lz-enunciado").innerHTML =
    `Las cuatro mayores ciudades ordenadas de mayor a menor concentran <b>P<sub>1</sub> = ${fmtInt(desc[0])}</b>, <b>P<sub>2</sub> = ${fmtInt(desc[1])}</b>, ` +
    `<b>P<sub>3</sub> = ${fmtInt(desc[2])}</b> y <b>P<sub>4</sub> = ${fmtInt(desc[3])} hab.</b> (Total = <b>${fmtInt(cur.tot)}</b>). ` +
    `Según <b>Ley de Zipf (P<sub>1</sub>/r)</b>, un sistema equilibrado tendría 2ª=${fmtInt(desc[0]/2)}, 3ª=${fmtInt(desc[0]/3)} y 4ª=${fmtInt(desc[0]/4)} hab.`;

  document.getElementById("lz-k-ip4").textContent = fmtDec(ip4, 3);
  document.getElementById("lz-k-ip2").textContent = `IP2 (P1/P2) = ${fmtDec(ip2, 3)}`;
  document.getElementById("lz-k-cat").textContent = catTxt;
  document.getElementById("lz-k-gini").textContent = fmtDec(cur.gini, 3);
  const dg = cur.gini - gho.gini;
  document.getElementById("lz-k-dgini").textContent = `ΔG vs Fantasma: ${dg >= 0 ? "+" : "-"}${fmtDec(Math.abs(dg), 3)}`;
  document.getElementById("lz-k-theil").textContent = fmtDec(cur.theil, 3);
  document.getElementById("lz-k-cuota").textContent = `Cuota P1: ${fmtDec((desc[0] / cur.tot) * 100, 1)}%`;
  document.getElementById("lz-k-hhi").textContent = fmtDec(cur.hhi, 3);
  document.getElementById("lz-k-hk").textContent = `HK(${fmtDec(alpha,1)}) = ${fmtDec(cur.hk, 2)} ciud. equiv.`;

  const pairedDesc = arr.map((v, idx) => ({ v, origIdx: idx + 1 })).sort((a, b) => b.v - a.v);
  const sDesc = desc.map(v => v / cur.tot);
  const sChipsSq = sDesc.map((sv, i) => `${vChip(fmtDec(sv,2), ["vc-b","vc-t","vc-p","vc-o"][i], `Cuota ciudad #${i+1}: ${fmtDec(sv*100,1)}%`)}<sup>2</sup>`).join(" + ");
  const tTerm1 = sDesc[0] * Math.log(4 * sDesc[0]);
  const tTerm2 = sDesc[1] * Math.log(4 * sDesc[1]);
  const q1L = cur.pts[1].q, q2L = cur.pts[2].q, q3L = cur.pts[3].q;
  renderFormulaStrip("lz-fstrip", [
    {
      lbl: "Primacía Urbana (IP4)", col: "#1D4ED8",
      eq: `IP<sub>4</sub> = ${mFrac('<span class="sym-b">P<sub>1</sub></span>', '<span class="sym-t">P<sub>2</sub></span> + <span class="sym-p">P<sub>3</sub></span> + <span class="sym-o">P<sub>4</sub></span>')}`,
      sub: `IP<sub>4</sub> = ${mFrac(eChip(fmtInt(desc[0]),desc[0],"lz_p"+pairedDesc[0].origIdx,"1000","vc-b","P1 (Mayor ciudad)"), eChip(fmtInt(desc[1]),desc[1],"lz_p"+pairedDesc[1].origIdx,"500","vc-t","P2") + " + " + eChip(fmtInt(desc[2]),desc[2],"lz_p"+pairedDesc[2].origIdx,"500","vc-p","P3") + " + " + eChip(fmtInt(desc[3]),desc[3],"lz_p"+pairedDesc[3].origIdx,"500","vc-o","P4"))} = ${mFrac(fmtInt(desc[0]), fmtInt(sum234))} = ${rChip(fmtDec(ip4,3), ip4 >= 1.5)}`,
      note: `Clasificación OT: ${catTxt} · Clic en P1–P4 para escribir población`
    },
    {
      lbl: "Gini por Trapecios (G)", col: "#DC2626",
      eq: `G = 1 − ∑ (p<sub>i</sub> − p<sub>i−1</sub>)(q<sub>i</sub> + q<sub>i−1</sub>)`,
      sub: `G = 1 − ${mFrac("1","4")}·[(0+${vChip(fmtDec(q1L,2),"vc-o","q1")})+(${vChip(fmtDec(q1L,2),"vc-o")}+${vChip(fmtDec(q2L,2),"vc-p","q2")})+(${vChip(fmtDec(q2L,2),"vc-p")}+${vChip(fmtDec(q3L,2),"vc-t","q3")})+(${vChip(fmtDec(q3L,2),"vc-t")}+1)] = 1 − ${fmtDec(cur.areaTrap,3)} = ${rChip(fmtDec(cur.gini,3), cur.gini >= 0.45)}`,
      note: `Área bajo Lorenz = ${fmtDec(cur.areaTrap/2,3)} | G = 2·Área A`
    },
    {
      lbl: "Entropía de Theil (T)", col: "#7C3AED",
      eq: `T = ∑ <span class="sym-b">s<sub>i</sub></span> · ln(<span class="sym-p">n</span> · <span class="sym-b">s<sub>i</sub></span>)`,
      sub: `T = ${vChip(fmtDec(sDesc[0],2),"vc-b","Cuota s1","lz_s1")}·ln(4·${fmtDec(sDesc[0],2)}) + ${vChip(fmtDec(sDesc[1],2),"vc-t","Cuota s2")}·ln(4·${fmtDec(sDesc[1],2)}) + … = ${rChip(fmtDec(cur.theil,3))}`,
      note: `Aporte P1: ${tTerm1>=0?"+":""}${fmtDec(tTerm1,3)} | P2: ${tTerm2>=0?"+":""}${fmtDec(tTerm2,3)} | Tope ln(4)=1,386`
    },
    {
      lbl: `HHI y Hannah-Kay (α = ${fmtDec(alpha,1)})`, col: "#0F766E",
      eq: `HHI = ∑ s<sub>i</sub><sup>2</sup> &nbsp;|&nbsp; HK<sub><span class="sym-p">α</span></sub> = (∑ s<sub>i</sub><sup><span class="sym-p">α</span></sup>)<sup>1/(1−<span class="sym-p">α</span>)</sup>`,
      sub: `HHI = ${sChipsSq} = ${rChip(fmtDec(cur.hhi,3))}<br/>HK<sub>${eChip(fmtDec(alpha,1),alpha,"lz_al","0.5","vc-p","Parámetro α (1,5–4,0)")}</sub> = (${fmtDec(sDesc.reduce((a,s)=>a+Math.pow(s,alpha),0),3)})<sup>${fmtDec(1/(1-alpha),2)}</sup> = ${rChip(fmtDec(cur.hk,2)+" ciud.")}`,
      note: `Con 4 ciudades iguales: HHI = 0,250 y HK = 4,00 · Clic en α para cambiar`
    }
  ]);

  const svg = document.getElementById("svg-lorenz");
  svg.innerHTML = "";
  addDefs(svg);
  const M = { l: 64, r: 460, t: 28, b: 48 }, W = 980, H = 390;
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
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "% Población Acum. (q_i)", "% Ciudades Acum. (p_i)");
  el("line", { x1: sx(0), y1: sy(0), x2: sx(1), y2: sy(1), stroke: "#64748B", "stroke-width": "1.9", "stroke-dasharray": "6,4" }, svg);
  drawPill(svg, sx(0.38), sy(0.56), "45° Equidad Perfecta", "#475569", "#FFFFFF", "middle", "10");
  el("polygon", { points: cur.pts.map(pt => `${sx(pt.p)},${sy(pt.q)}`).join(" ") + ` ${sx(0)},${sy(0)}`, fill: "rgba(220,38,38,0.16)" }, svg);
  if (Math.abs(dg) > 0.004) {
    el("polyline", { points: gho.pts.map(pt => `${sx(pt.p)},${sy(pt.q)}`).join(" "), fill: "none", stroke: "#94A3B8", "stroke-width": "2", "stroke-dasharray": "4,4" }, svg);
    drawArrow(svg, sx(gho.pts[3].p), sy(gho.pts[3].q), sx(cur.pts[3].p), sy(cur.pts[3].q), dg > 0 ? "#DC2626" : "#15803D", dg > 0 ? "arr-red" : "arr-green", dg > 0 ? "↑ Mayor Gini" : "↓ Menor Gini", sx(cur.pts[3].p) - 54, (sy(gho.pts[3].q) + sy(cur.pts[3].q)) / 2 - 4);
  }
  el("polyline", { points: cur.pts.map(pt => `${sx(pt.p)},${sy(pt.q)}`).join(" "), fill: "none", stroke: "#DC2626", "stroke-width": "2.8" }, svg);
  cur.pts.forEach(pt => el("circle", { cx: sx(pt.p), cy: sy(pt.q), r: 4.5, fill: "#DC2626" }, svg));
  drawPill(svg, sx(0.76), sy(0.11), `Área A · G = ${fmtDec(cur.gini,3)}`, "#DC2626", "#FEF2F2", "middle", "10.3");

  // Termómetro IP4 derecho + comparador Zipf
  const bx = 575, bw = 370, by = 148, bh = 32, maxIP = 2.4;
  const sip = v => bx + (Math.min(v, maxIP) / maxIP) * bw;
  const tBar = el("text", { x: bx + bw / 2, y: 88, fill: "#0F172A", "font-size": "12.5", "font-weight": "700", "text-anchor": "middle" }, svg);
  tBar.textContent = "Escala Estandarizada de Primacía IP4 (06 OT 2024.pdf)";
  for (const [a, b, bg, fg, lbl] of [[0,0.65,"#DCFCE7","#166534","0: Muy Disp."],[0.65,1.00,"#DBEAFE","#1E40AF","1: Disp."],[1.00,1.50,"#FEF3C7","#92400E","2: Conc."],[1.50,maxIP,"#FEE2E2","#991B1B","3: Macrocefalia"]]) {
    el("rect", { x: sip(a), y: by, width: sip(b) - sip(a), height: bh, fill: bg, stroke: "#CBD5E1" }, svg);
    const tl = el("text", { x: (sip(a) + sip(b)) / 2, y: by + bh + 18, fill: fg, "font-size": "10.5", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = lbl;
  }
  const gDesc = [...ghostLz].sort((a, b) => b - a);
  const gIp4 = gDesc[0] / Math.max(1, gDesc[1] + gDesc[2] + gDesc[3]);
  if (Math.abs(ip4 - gIp4) > 0.02) {
    drawArrow(svg, sip(gIp4), by - 18, sip(ip4), by - 18, ip4 > gIp4 ? "#DC2626" : "#15803D", ip4 > gIp4 ? "arr-red" : "arr-green", `IP4: ${fmtDec(ip4, 2)}`, (sip(gIp4) + sip(ip4)) / 2, by - 28);
  }
  el("circle", { cx: sip(ip4), cy: by + bh / 2, r: 8, fill: "#0F172A", stroke: "#FFFFFF", "stroke-width": "2" }, svg);

  // Mini barras Real vs. Zipf Teórico (P1/r) debajo del termómetro
  const zyTop = 240, zyBot = 342, zSlot = bw / 4, zBw = 30;
  const tZip = el("text", { x: bx + bw / 2, y: zyTop - 10, fill: "#0F172A", "font-size": "11.5", "font-weight": "700", "text-anchor": "middle" }, svg);
  tZip.textContent = "Real (azul) vs. Ley de Zipf Teórica P1/r (gris)";
  el("line", { x1: bx, y1: zyBot, x2: bx + bw, y2: zyBot, stroke: "#334155", "stroke-width": "1.3" }, svg);
  const zMax = Math.max(1, desc[0]);
  for (let r = 0; r < 4; r++) {
    const cxZ = bx + r * zSlot + zSlot / 2;
    const hReal = (desc[r] / zMax) * (zyBot - zyTop - 12);
    const hZipf = ((desc[0] / (r + 1)) / zMax) * (zyBot - zyTop - 12);
    el("rect", { x: cxZ - zBw - 2, y: zyBot - hReal, width: zBw, height: Math.max(2, hReal), fill: "#1D4ED8", rx: 2 }, svg);
    el("rect", { x: cxZ + 2, y: zyBot - hZipf, width: zBw, height: Math.max(2, hZipf), fill: "#CBD5E1", stroke: "#64748B", "stroke-dasharray": "3,2", rx: 2 }, svg);
    const tl = el("text", { x: cxZ, y: zyBot + 15, fill: "#334155", "font-size": "10.5", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = `Rango ${r + 1}`;
  }

  renderPedBox("ped-lorenz",
    `La ciudad líder concentra el <b>${fmtDec((desc[0]/cur.tot)*100,1)}%</b> de las 4 principales urbes, arrojando <b>IP<sub>4</sub> = ${fmtDec(ip4,3)}</b> (${catTxt}), <b>Gini = ${fmtDec(cur.gini,3)}</b>, <b>Theil = ${fmtDec(cur.theil,3)}</b> y <b>HK(${fmtDec(alpha,1)}) = ${fmtDec(cur.hk,2)} ciudades equivalentes</b>.`,
    `<b>¿Por qué usar Theil si ya existe el Gini?</b> Porque el Gini tiene un defecto oculto en política regional: NO se puede sumar limpiamente por subgrupos. La <b>Entropía de Theil</b> sí se descompone exactamente en desigualdad <i>entre regiones</i> + desigualdad <i>dentro de cada región</i>, permitiendo saber si la brecha está en Santiago o dentro de Los Lagos.`,
    `Fíjate en el contraste real del Censo 2024: <b>Los Lagos</b> cae en <b>Valor 2 (Concentrada, IP<sub>4</sub> ≈ 1,01)</b> por el peso de Puerto Montt sobre Osorno, Puerto Varas y Castro, mientras <b>Biobío</b> es más policéntrica (<b>Valor 0, IP<sub>4</sub> ≈ 0,45</b>) gracias al contrapeso de Los Ángeles, San Pedro y Talcahuano.`
  );
}

// ============================================================================
// 7. REDES EMPRESARIALES DE DINI (2010) — LABORATORIO INTERACTIVO (n, L, CLIC)
// ============================================================================
const TOPOS_DINI = {
  simetrica: {
    parametric: true,
    desc: "<b>Red Simétrica (Dini, 2010 — Diagrama 2):</b> Cooperación horizontal entre pares con grado nodal homogéneo. Mueve <b>n</b> o <b>L</b>, o haz clic en 2 nodos para editar la red.",
    nodes: Array.from({length: 8}, (_, i) => ({ nm: `PyME ${i+1}`, x: 265 + 145 * Math.cos(i * Math.PI / 4), y: 200 + 132 * Math.sin(i * Math.PI / 4) })),
    edges: [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,0],[0,2],[1,3],[2,4],[3,5],[4,6],[5,7],[6,0],[7,1]]
  },
  liderazgo: {
    parametric: true,
    desc: "<b>Red con Liderazgo (Dini, 2010 — Diagrama 2):</b> Estructura radial tipo estrella. Un nodo ancla centraliza todos los acuerdos (<b>GC = 100%</b>). Prueba <b>Simular Quiebra del Líder</b>.",
    nodes: [{ nm: "Empresa Líder", x: 265, y: 200 }, ...Array.from({length: 7}, (_, i) => ({ nm: `PyME ${i+1}`, x: 265 + 145 * Math.cos(i * 2 * Math.PI / 7), y: 200 + 132 * Math.sin(i * 2 * Math.PI / 7) }))],
    edges: [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7]]
  },
  jerarquica: {
    parametric: true,
    desc: "<b>Red Jerárquica (Dini, 2010 — Diagrama 2):</b> Subcontratación escalonada por niveles (Matriz → Contratistas → Talleres) sin vínculos horizontales en la base.",
    nodes: [
      { nm: "Matriz Ancla", x: 265, y: 58 }, { nm: "Contratista 1A", x: 160, y: 178 }, { nm: "Contratista 1B", x: 370, y: 178 },
      { nm: "Taller 2A", x: 95, y: 315 }, { nm: "Taller 2B", x: 210, y: 315 }, { nm: "Taller 2C", x: 320, y: 315 }, { nm: "Proveedor 2D", x: 435, y: 315 }
    ],
    edges: [[0,1],[0,2],[1,3],[1,4],[2,5],[2,6]]
  },
  red_redes: {
    parametric: false,
    desc: "<b>Red de Redes (Dini, 2010 — Diagrama 3):</b> Tres clústeres locales (Osorno, Pto. Montt, Valdivia) cohesionados cuyos nodos puente se articulan entre sí.",
    nodes: [
      { nm: "Líder Osorno", x: 165, y: 140 }, { nm: "O1", x: 95, y: 74 }, { nm: "O2", x: 85, y: 180 }, { nm: "O3", x: 160, y: 220 },
      { nm: "Líder P.Montt", x: 370, y: 140 }, { nm: "M1", x: 445, y: 78 }, { nm: "M2", x: 455, y: 180 }, { nm: "M3", x: 365, y: 220 },
      { nm: "Líder Valdivia", x: 265, y: 290 }, { nm: "V1", x: 195, y: 350 }, { nm: "V2", x: 335, y: 350 }, { nm: "V3", x: 265, y: 230 }
    ],
    edges: [[0,4],[4,8],[0,8],[0,1],[0,2],[0,3],[4,5],[4,6],[4,7],[6,7],[8,9],[8,10],[8,11]]
  },
  aviones: {
    parametric: false,
    desc: "<b>Red de Redes en Producción de Aviones (Dini, 2010 — Diagrama 4):</b> Una gran ensambladora central coordina a los líderes de subsistemas (Motores, Aviónica, Fuselaje).",
    nodes: [
      { nm: "ENSAMBLADORA", x: 265, y: 200 },
      { nm: "Líder Motores", x: 135, y: 130 }, { nm: "Turb.A", x: 65, y: 72 }, { nm: "Turb.B", x: 60, y: 170 },
      { nm: "Líder Aviónica", x: 395, y: 130 }, { nm: "Soft.A", x: 465, y: 72 }, { nm: "Radar", x: 470, y: 170 },
      { nm: "Líder Fuselaje", x: 265, y: 310 }, { nm: "Aleac.", x: 185, y: 355 }, { nm: "Cabina", x: 345, y: 355 }
    ],
    edges: [[0,1],[0,4],[0,7],[1,2],[1,3],[4,5],[4,6],[7,8],[7,9],[8,9]]
  },
  osorno: {
    parametric: false,
    desc: "<b>Caso Control 4 — Red Láctea-Quesera de Osorno:</b> Articulación multilateral liderada por <i>Aproleche</i> y <i>Cooprinsem</i> conectada a plantas ancla (<i>Nestlé, Watt's</i>) e <i>INIA Remehue</i>.",
    nodes: [
      { nm: "Aproleche", x: 265, y: 160 }, { nm: "Cooprinsem", x: 225, y: 240 }, { nm: "INIA", x: 120, y: 95 }, { nm: "Lech.Matthei", x: 90, y: 220 },
      { nm: "Q.Las Ánimas", x: 145, y: 330 }, { nm: "Láct.Osorno", x: 315, y: 335 }, { nm: "Nestlé", x: 425, y: 120 }, { nm: "Watt's", x: 440, y: 240 }, { nm: "DeLaval", x: 345, y: 70 }
    ],
    edges: [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[1,2],[1,3],[1,4],[1,5],[1,6],[1,7],[1,8],[2,3],[3,6],[3,7],[4,5],[6,8],[7,8]]
  },
  pymemad: {
    parametric: false,
    desc: "<b>Caso Control 4 — Clúster Forestal-Maderero PymeMad (Biobío):</b> El gremio <i>PymeMad</i> coordina aserraderos y plantas de remanufactura CLT para compras y certificación estructural.",
    nodes: [
      { nm: "Gremio PymeMad", x: 265, y: 200 }, { nm: "Aserradero 1", x: 130, y: 110 }, { nm: "Aserradero 2", x: 115, y: 265 },
      { nm: "Remanuf. CLT", x: 265, y: 340 }, { nm: "Prov. Forestal", x: 265, y: 60 }, { nm: "Logística", x: 410, y: 285 },
      { nm: "Planta Ancla", x: 420, y: 135 }, { nm: "Centro I+D", x: 365, y: 70 }
    ],
    edges: [[0,1],[0,2],[0,3],[0,4],[0,6],[0,7],[1,2],[1,3],[1,4],[2,3],[3,5],[3,6],[3,7],[4,5],[4,6],[5,6],[6,7]]
  }
};

let diniKey = "simetrica";
let diniNodes = [];
let diniEdges = [];
let diniDirected = false;
let diniSelectedNode = null;
let diniQuiebraIdx = null;
let animDnId = null;

function edgeKeyDini(u, v, dir) {
  return dir ? `${u}>${v}` : (u < v ? `${u}-${v}` : `${v}-${u}`);
}
function buildAllPossibleEdges(n, dir) {
  const out = [];
  for (let i = 0; i < n; i++) {
    for (let j = dir ? 0 : i + 1; j < n; j++) {
      if (i !== j) out.push([i, j]);
    }
  }
  return out;
}
function buildParametricGraph(key, n) {
  const nodes = [], edges = [];
  if (key === "liderazgo") {
    nodes.push({ nm: "Empresa Líder", x: 265, y: 200 });
    for (let i = 0; i < n - 1; i++) {
      const ang = (i / (n - 1)) * Math.PI * 2 - Math.PI / 2;
      nodes.push({ nm: `PyME ${i + 1}`, x: 265 + 148 * Math.cos(ang), y: 200 + 132 * Math.sin(ang) });
      edges.push([0, i + 1]);
    }
  } else if (key === "jerarquica") {
    nodes.push({ nm: "Matriz Ancla", x: 265, y: 58 });
    const nMid = Math.max(1, Math.min(4, Math.floor((n - 1) / 3) + 1));
    const nBot = Math.max(0, n - 1 - nMid);
    for (let i = 0; i < nMid; i++) {
      const x = nMid === 1 ? 265 : 120 + (i / (nMid - 1)) * 290;
      nodes.push({ nm: `Contr. ${i + 1}`, x, y: 178 });
      edges.push([0, 1 + i]);
    }
    for (let j = 0; j < nBot; j++) {
      const x = nBot === 1 ? 265 : 68 + (j / (nBot - 1)) * 394;
      nodes.push({ nm: `Taller ${j + 1}`, x, y: 318 });
      const parentIdx = 1 + (j % nMid);
      edges.push([parentIdx, 1 + nMid + j]);
    }
  } else {
    // Simétrica (anillo + saltos de paso 2 si n >= 5)
    for (let i = 0; i < n; i++) {
      const ang = (i / n) * Math.PI * 2 - Math.PI / 2;
      nodes.push({ nm: `PyME ${i + 1}`, x: 265 + 148 * Math.cos(ang), y: 200 + 132 * Math.sin(ang) });
    }
    for (let i = 0; i < n; i++) edges.push([i, (i + 1) % n]);
    if (n >= 5) {
      const seen = new Set(edges.map(([u, v]) => edgeKeyDini(u, v, false)));
      for (let i = 0; i < n; i++) {
        const u = i, v = (i + 2) % n;
        const k = edgeKeyDini(u, v, false);
        if (!seen.has(k)) { seen.add(k); edges.push([u, v]); }
      }
    }
  }
  return { nodes, edges };
}
function loadDiniTopology(key, customN = null) {
  diniKey = key;
  diniSelectedNode = null;
  diniQuiebraIdx = null;
  const btnQ = document.getElementById("dn-btn-quiebra");
  if (btnQ) { btnQ.classList.remove("primary"); btnQ.textContent = "Simular Quiebra del Líder"; }

  const topo = TOPOS_DINI[key];
  if (customN !== null) {
    if (topo.parametric) {
      const g = buildParametricGraph(key, customN);
      diniNodes = g.nodes;
      diniEdges = g.edges.map(e => [...e]);
    } else {
      // Para casos reales, recorta o agrega nodos en el perímetro conservando el núcleo
      const baseN = topo.nodes.length;
      if (customN <= baseN) {
        diniNodes = topo.nodes.slice(0, customN).map(nd => ({ ...nd }));
        diniEdges = topo.edges.filter(([u, v]) => u < customN && v < customN).map(e => [...e]);
      } else {
        diniNodes = topo.nodes.map(nd => ({ ...nd }));
        diniEdges = topo.edges.map(e => [...e]);
        for (let i = baseN; i < customN; i++) {
          const ang = ((i - baseN) / Math.max(1, customN - baseN)) * Math.PI * 2 - 0.5;
          diniNodes.push({ nm: `Actor ${i + 1}`, x: Math.max(58, Math.min(472, 265 + 168 * Math.cos(ang))), y: Math.max(54, Math.min(358, 200 + 148 * Math.sin(ang))) });
          diniEdges.push([0, i]);
        }
      }
    }
  } else {
    diniNodes = topo.nodes.map(nd => ({ ...nd }));
    diniEdges = topo.edges.map(e => [...e]);
  }
  syncDiniSliders();
  drawDini();
}
function syncDiniSliders() {
  const n = diniNodes.length;
  const lMax = diniDirected ? n * (n - 1) : (n * (n - 1)) / 2;
  const slN = document.getElementById("dn-n");
  const slL = document.getElementById("dn-step");
  if (slN) slN.value = n;
  if (slL) {
    slL.max = lMax;
    slL.value = Math.min(lMax, diniEdges.length);
  }
}
function setTopologiaDini(key, btn) {
  if (animDnId) cancelAnimationFrame(animDnId);
  btn.parentElement.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  loadDiniTopology(key, null);
}
function resetTopologiaDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  loadDiniTopology(diniKey, null);
}
function onSliderNDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  const newN = +document.getElementById("dn-n").value;
  loadDiniTopology(diniKey, newN);
}
function onInputNDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  let newN = parseInt(document.getElementById("dn-n-in").value, 10);
  if (!Number.isFinite(newN)) return;
  newN = Math.max(4, Math.min(15, newN));
  document.getElementById("dn-n").value = newN;
  loadDiniTopology(diniKey, newN);
}
function onInputLDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  let newL = parseInt(document.getElementById("dn-l-in").value, 10);
  if (!Number.isFinite(newL)) return;
  const sl = document.getElementById("dn-step");
  newL = Math.max(0, Math.min(+sl.max, newL));
  sl.value = newL;
  onSliderLDini();
}
function onSliderLDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  diniQuiebraIdx = null;
  const btnQ = document.getElementById("dn-btn-quiebra");
  if (btnQ) { btnQ.classList.remove("primary"); btnQ.textContent = "Simular Quiebra del Líder"; }

  const targetL = +document.getElementById("dn-step").value;
  const n = diniNodes.length;
  if (targetL < diniEdges.length) {
    diniEdges = diniEdges.slice(0, targetL);
  } else if (targetL > diniEdges.length) {
    // Primero reponer aristas base de la topología si faltan, luego completar hasta L_max
    const seen = new Set(diniEdges.map(([u, v]) => edgeKeyDini(u, v, diniDirected)));
    const topoBase = TOPOS_DINI[diniKey].parametric ? buildParametricGraph(diniKey, n).edges : TOPOS_DINI[diniKey].edges.filter(([u, v]) => u < n && v < n);
    const pool = [...topoBase, ...buildAllPossibleEdges(n, diniDirected)];
    for (const [u, v] of pool) {
      if (diniEdges.length >= targetL) break;
      const k = edgeKeyDini(u, v, diniDirected);
      if (!seen.has(k)) {
        seen.add(k);
        diniEdges.push([u, v]);
      }
    }
  }
  drawDini();
}
function setDirigidaDini(isDir) {
  if (animDnId) cancelAnimationFrame(animDnId);
  diniDirected = isDir;
  document.getElementById("dn-dir-no").classList.toggle("primary", !isDir);
  document.getElementById("dn-dir-si").classList.toggle("primary", isDir);
  document.getElementById("dn-dir-v").textContent = isDir ? "Dirigida (L)" : "No Dirigida (2L)";
  if (!isDir) {
    // Deduplicar pares (u,v) y (v,u) al volver a no dirigida
    const seen = new Set();
    diniEdges = diniEdges.filter(([u, v]) => {
      const k = edgeKeyDini(u, v, false);
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  }
  syncDiniSliders();
  drawDini();
}
function saturarDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  diniQuiebraIdx = null;
  const btnQ = document.getElementById("dn-btn-quiebra");
  if (btnQ) { btnQ.classList.remove("primary"); btnQ.textContent = "Simular Quiebra del Líder"; }
  const n = diniNodes.length;
  const slL = document.getElementById("dn-step");
  slL.value = diniDirected ? n * (n - 1) : (n * (n - 1)) / 2;
  onSliderLDini();
}
function toggleQuiebraLiderDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  const btnQ = document.getElementById("dn-btn-quiebra");
  if (diniQuiebraIdx !== null) {
    diniQuiebraIdx = null;
    btnQ.classList.remove("primary");
    btnQ.textContent = "Simular Quiebra del Líder";
  } else {
    const n = diniNodes.length;
    const deg = new Array(n).fill(0);
    diniEdges.forEach(([u, v]) => { deg[u]++; deg[v]++; });
    let best = 0;
    for (let i = 1; i < n; i++) if (deg[i] > deg[best]) best = i;
    diniQuiebraIdx = best;
    btnQ.classList.add("primary");
    btnQ.textContent = `Quiebra Activa (${diniNodes[best].nm}) — Restaurar`;
  }
  drawDini();
}
function clickNodeDini(idx) {
  if (animDnId) cancelAnimationFrame(animDnId);
  if (diniQuiebraIdx === idx) return;
  if (diniSelectedNode === null) {
    diniSelectedNode = idx;
    drawDini();
    return;
  }
  if (diniSelectedNode === idx) {
    diniSelectedNode = null;
    drawDini();
    return;
  }
  const u = diniSelectedNode, v = idx;
  const targetKey = edgeKeyDini(u, v, diniDirected);
  const pos = diniEdges.findIndex(([a, b]) => edgeKeyDini(a, b, diniDirected) === targetKey);
  if (pos >= 0) {
    diniEdges.splice(pos, 1);
  } else {
    diniEdges.push([u, v]);
  }
  diniSelectedNode = null;
  syncDiniSliders();
  drawDini();
}
function animarDini() {
  if (animDnId) cancelAnimationFrame(animDnId);
  diniQuiebraIdx = null;
  const btnQ = document.getElementById("dn-btn-quiebra");
  if (btnQ) { btnQ.classList.remove("primary"); btnQ.textContent = "Simular Quiebra del Líder"; }
  const targetL = Math.max(1, diniEdges.length);
  const savedEdges = diniEdges.map(e => [...e]);
  const t0 = performance.now(), dur = Math.max(1100, targetL * 115);
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    const k = Math.round(u * targetL);
    diniEdges = savedEdges.slice(0, k);
    document.getElementById("dn-step").value = k;
    drawDini();
    if (u < 1) animDnId = requestAnimationFrame(step);
  }
  animDnId = requestAnimationFrame(step);
}
function drawDini() {
  const n = diniNodes.length;
  const lMax = diniDirected ? n * (n - 1) : (n * (n - 1)) / 2;
  const actEdges = diniQuiebraIdx === null ? diniEdges : diniEdges.filter(([u, v]) => u !== diniQuiebraIdx && v !== diniQuiebraIdx);
  const L = actEdges.length;

  const inN = document.getElementById("dn-n-in"), inL = document.getElementById("dn-l-in");
  if (inN && document.activeElement !== inN) inN.value = n;
  if (inL) { inL.max = lMax; if (document.activeElement !== inL) inL.value = L; }
  document.getElementById("dn-step-v").textContent = `/ ${lMax}`;
  const selHint = diniSelectedNode !== null
    ? `<br/><span style="color:#B45309;font-weight:800;">● Nodo seleccionado: ${diniNodes[diniSelectedNode].nm} — haz clic en otro actor para crear o eliminar su vínculo (o clic de nuevo para cancelar).</span>`
    : `<br/><span style="color:#475569;">Modo edición directa activo: haz clic en cualquier actor del grafo y luego en otro para sumar/quitar vínculos, o mueve los sliders de <b>n</b> y <b>L</b>.</span>`;
  document.getElementById("dn-enunciado").innerHTML = TOPOS_DINI[diniKey].desc + selHint;

  // Grados nodales (para GC usamos vecinos únicos conectados para mantener GC siempre en [0%, 100%])
  const deg = new Array(n).fill(0);
  const uniqAdj = Array.from({ length: n }, () => new Set());
  actEdges.forEach(([u, v]) => {
    if (diniDirected) { deg[u]++; } else { deg[u]++; deg[v]++; }
    uniqAdj[u].add(v);
    uniqAdj[v].add(u);
  });
  const degGC = uniqAdj.map(s => s.size);
  const den = lMax > 0 ? (L / lMax) * 100 : 0;
  const kMax = Math.max(0, ...degGC);
  const kAvg = degGC.reduce((s, v) => s + v, 0) / n;
  const sumDiff = degGC.reduce((s, v) => s + (kMax - v), 0);
  const denGC = (n - 1) * (n - 2);
  const gc = n > 2 ? (sumDiff / denGC) * 100 : 0;
  const aislados = degGC.filter((k, i) => k === 0 && i !== diniQuiebraIdx).length;

  document.getElementById("dn-k-nl").textContent = `n=${n} | L=${L}`;
  document.getElementById("dn-k-lmax").textContent = `Máx posible: ${lMax}`;
  document.getElementById("dn-k-den").textContent = fmtDec(den, 1) + "%";
  document.getElementById("dn-k-denf").textContent = diniDirected ? "D = L / [n(n−1)]" : "D = 2L / [n(n−1)]";
  document.getElementById("dn-k-k").textContent = `k_máx=${kMax} | k̄=${fmtDec(kAvg, 1)}`;
  document.getElementById("dn-k-iso").textContent = `Aislados (k=0): ${aislados}`;
  document.getElementById("dn-k-gc").textContent = fmtDec(gc, 1) + "%";
  document.getElementById("dn-k-gcd").textContent = L === 0 ? "Red desconectada (Colapso)" : (gc < 15 ? "Red Simétrica / Horizontal" : (gc > 68 ? "Red con Liderazgo Fuerte" : "Red Jerárquica / Policéntrica"));

  const cMaxPct = (kMax / Math.max(1, n - 1)) * 100;
  renderFormulaStrip("dn-fstrip", [
    {
      lbl: "Vínculos Máximos (Diagonal A_ii = 0)", col: "#0F172A",
      eq: diniDirected ? `L<sub>máx</sub> = <span class="sym-b">n</span>(<span class="sym-b">n</span> − 1)` : `L<sub>máx</sub> = ${mFrac('<span class="sym-b">n</span>(<span class="sym-b">n</span> − 1)', "2")}`,
      sub: diniDirected
        ? `L<sub>máx</sub> = ${eChip(n,n,"dn_n","1","vc-b","Actores n (4–15)")}·(${n}−1) = ${rChip(lMax)}`
        : `L<sub>máx</sub> = ${mFrac(eChip(n,n,"dn_n","1","vc-b","Actores n (4–15)") + "·(" + n + "−1)", "2")} = ${mFrac(n*(n-1), "2")} = ${rChip(lMax)}`,
      note: `Clic en n para cambiar la cantidad de empresas`
    },
    {
      lbl: "Densidad de la Red (D)", col: "#1D4ED8",
      eq: diniDirected ? `D = ${mFrac('<span class="sym-t">L</span>', '<span class="sym-b">n</span>(<span class="sym-b">n</span> − 1)')}` : `D = ${mFrac('2·<span class="sym-t">L</span>', '<span class="sym-b">n</span>(<span class="sym-b">n</span> − 1)')}`,
      sub: diniDirected
        ? `D = ${mFrac(eChip(L,L,"dn_L","1","vc-t","Vínculos activos L"), eChip(n,n,"dn_n","1","vc-b","Actores n") + "·" + (n-1))} = ${mFrac(L, n*(n-1))} = ${rChip(fmtDec(den,1)+"%")}`
        : `D = ${mFrac("2·" + eChip(L,L,"dn_L","1","vc-t","Vínculos activos L"), eChip(n,n,"dn_n","1","vc-b","Actores n") + "·" + (n-1))} = ${mFrac(2*L, n*(n-1))} = ${rChip(fmtDec(den,1)+"%")}`,
      note: diniDirected ? "Matriz dirigida · Clic en L o n para editar" : "Matriz simétrica · Clic en L o n para editar"
    },
    {
      lbl: "Centralidad del Nodo Líder (C_máx)", col: "#15803D",
      eq: `C<sub>máx</sub> = ${mFrac('<span class="sym-r">k<sub>máx</sub></span>', '<span class="sym-b">n</span> − 1')}`,
      sub: `C<sub>máx</sub> = ${mFrac(vChip(kMax,"vc-r","Grado máximo k_máx","dn_km"), eChip(n,n,"dn_n","1","vc-b","Actores n") + " − 1")} = ${mFrac(kMax, n-1)} = ${rChip(fmtDec(cMaxPct,1)+"%")}`,
      note: `Grado promedio k̄ = ${fmtDec(kAvg,1)} | Aislados = ${aislados}`
    },
    {
      lbl: "Gradiente de Concentración (GC)", col: "#DC2626",
      eq: `GC = ${mFrac('∑(<span class="sym-r">k<sub>máx</sub></span> − k<sub>i</sub>)', '(<span class="sym-b">n</span>−1)(<span class="sym-b">n</span>−2)')}`,
      sub: `GC = ${mFrac(vChip(sumDiff,"vc-r","Suma brechas ∑(k_máx−k_i)","dn_sd"), "(" + vChip(n-1,"vc-b","n−1") + ")·(" + vChip(n-2,"vc-p","n−2") + ")")} = ${mFrac(sumDiff, denGC)} = ${rChip(fmtDec(gc,1)+"%", gc > 68)}`,
      note: gc < 15 ? "≈ 0% Simétrica" : (gc > 68 ? "→ 100% Estrella / Líder único" : "Intermedia / Jerárquica")
    }
  ]);

  // Caja de fórmulas sustituidas en vivo (estilo cuaderno/examen)
  const solEl = document.getElementById("dn-sol");
  if (solEl) {
    const numD = diniDirected ? `${L}` : `2·(${L}) = ${2 * L}`;
    const denD = `${n}·(${n - 1}) = ${n * (n - 1)}`;
    const qNote = diniQuiebraIdx !== null ? ` &nbsp;|&nbsp; <span style="color:#DC2626;"><b>SIMULACIÓN QUIEBRA (${diniNodes[diniQuiebraIdx].nm}):</b> ${aislados} actores quedaron aislados (k=0)</span>` : "";
    solEl.innerHTML =
      `<b>Cálculo en vivo:</b> D = ${numD} / [${denD}] = <b>${fmtDec(den, 1)}%</b> &nbsp;|&nbsp; ` +
      `GC = ∑(${kMax} − k<sub>i</sub>) / [(${n - 1})·(${n - 2})] = ${sumDiff} / ${denGC} = <b>${fmtDec(gc, 1)}%</b>${qNote}`;
  }

  const svg = document.getElementById("svg-dini");
  svg.innerHTML = "";
  addDefs(svg);

  // Izquierda: Grafo SVG interactivo
  const tG = el("text", { x: 265, y: 22, fill: "#0F172A", "font-size": "11.5", "font-weight": "700", "text-anchor": "middle" }, svg);
  tG.textContent = diniDirected ? "Grafo Dirigido (Clic en 2 nodos = crear/borrar flecha)" : "Grafo No Dirigido (Clic en 2 nodos = crear/borrar vínculo)";

  actEdges.forEach(([u, v], idx) => {
    const isLast = idx === L - 1;
    const x1 = diniNodes[u].x, y1 = diniNodes[u].y, x2 = diniNodes[v].x, y2 = diniNodes[v].y;
    const dx = x2 - x1, dy = y2 - y1, dist = Math.hypot(dx, dy) || 1;
    const rEnd = 11 + degGC[v] * 1.9 + 5;
    const attrs = {
      x1, y1,
      x2: diniDirected ? x2 - (dx / dist) * rEnd : x2,
      y2: diniDirected ? y2 - (dy / dist) * rEnd : y2,
      stroke: isLast ? "#DC2626" : "#64748B",
      "stroke-width": isLast ? "3.0" : "1.9",
      opacity: "0.88"
    };
    if (diniDirected) attrs["marker-end"] = isLast ? "url(#arr-red)" : "url(#arr-dark)";
    el("line", attrs, svg);
  });

  diniNodes.forEach((nd, i) => {
    const isBroken = i === diniQuiebraIdx;
    const isSel = i === diniSelectedNode;
    const kVal = degGC[i];
    const r = Math.min(24, 9.5 + kVal * 1.9);
    const isHub = kVal === kMax && kMax > 0 && !isBroken;
    const g = el("g", { style: isBroken ? "cursor:not-allowed;" : "cursor:pointer;", onclick: `clickNodeDini(${i})` }, svg);
    if (isSel) {
      el("circle", { cx: nd.x, cy: nd.y, r: r + 5.5, fill: "rgba(245,158,11,0.22)", stroke: "#D97706", "stroke-width": "2.4", "stroke-dasharray": "4,2" }, g);
    }
    el("circle", {
      cx: nd.x, cy: nd.y, r,
      fill: isBroken ? "#E2E8F0" : (isHub ? "#DC2626" : (kVal === 0 ? "#94A3B8" : "#1D4ED8")),
      stroke: isBroken ? "#DC2626" : "#FFFFFF",
      "stroke-width": "2",
      "stroke-dasharray": isBroken ? "4,2" : ""
    }, g);
    if (isBroken) {
      el("line", { x1: nd.x - 6, y1: nd.y - 6, x2: nd.x + 6, y2: nd.y + 6, stroke: "#DC2626", "stroke-width": "2.4" }, g);
      el("line", { x1: nd.x + 6, y1: nd.y - 6, x2: nd.x - 6, y2: nd.y + 6, stroke: "#DC2626", "stroke-width": "2.4" }, g);
    }
    const t = el("text", { x: nd.x, y: nd.y - r - 4, fill: isBroken ? "#DC2626" : "#0F172A", "font-size": "10.2", "font-weight": "700", "text-anchor": "middle" }, g);
    t.textContent = isBroken ? `${nd.nm} (FUERA)` : `${nd.nm} (k=${kVal})`;
  });

  // Derecha: Curva de Gradiente Nodal (k_i ordenado de mayor a menor)
  const ord = diniNodes.map((nd, i) => ({ nm: nd.nm, k: degGC[i], broken: i === diniQuiebraIdx })).sort((a, b) => b.k - a.k);
  const bx = 545, bwTot = 410, by = 335, bhMax = 250;
  const maxKPlot = Math.max(4, kMax);
  const slot = bwTot / n, bw = Math.min(34, slot * 0.65);
  const tTit = el("text", { x: bx + bwTot / 2, y: 26, fill: "#0F172A", "font-size": "12", "font-weight": "700", "text-anchor": "middle" }, svg);
  tTit.textContent = "Gradiente de Concentración Nodal (k_i ordenado)";
  el("line", { x1: bx, y1: by, x2: bx + bwTot, y2: by, stroke: "#334155", "stroke-width": "1.5" }, svg);

  const lPts = [];
  ord.forEach((o, i) => {
    const x0 = bx + i * slot + (slot - bw) / 2;
    const h = (o.k / maxKPlot) * bhMax;
    el("rect", { x: x0, y: by - h, width: bw, height: Math.max(2, h), fill: o.broken ? "#CBD5E1" : (i === 0 && o.k > 0 ? "#DC2626" : "#2563EB"), rx: 3 }, svg);
    lPts.push(`${x0 + bw / 2},${by - h}`);
    const tv = el("text", { x: x0 + bw / 2, y: by - h - 5, fill: "#0F172A", "font-size": "10.2", "font-weight": "800", "text-anchor": "middle" }, svg);
    tv.textContent = o.k;
    const tl = el("text", { x: x0 + bw / 2, y: by + 14, fill: "#334155", "font-size": n > 11 ? "8.0" : "9.1", "font-weight": "700", "text-anchor": "middle" }, svg);
    tl.textContent = o.nm.slice(0, n > 11 ? 5 : 7);
  });
  if (lPts.length > 1) el("polyline", { points: lPts.join(" "), fill: "none", stroke: "#DC2626", "stroke-width": "2.2", "stroke-dasharray": "4,3" }, svg);

  // Cápsulas pedagógicas dinámicas que reaccionan a quiebra, saturación, n y L
  if (diniQuiebraIdx !== null) {
    renderPedBox("ped-dini",
      `Al retirar al nodo ancla <b>${diniNodes[diniQuiebraIdx].nm}</b>, la red cayó a <b>L = ${L} vínculos</b> (<b>D = ${fmtDec(den,1)}%</b>) dejando a <b>${aislados} de ${n - 1} actores restantes totalmente aislados (k = 0)</b>.`,
      `<b>Prueba de Estrés de Resiliencia Territorial:</b> en una <b>Red con Liderazgo (estrella, GC = 100%)</b>, perder a la empresa líder derrumba la densidad a <b>0,0%</b> al instante. En cambio, en una <b>Red Simétrica</b> o en la <b>Red Láctea de Osorno</b>, el resto de los actores conserva sus vínculos horizontales y sobrevive.`,
      `Argumento de oro para el <b>Control 4 (Dini, 2010)</b>: la política pública de fomento (CORFO / GORE) busca crear vínculos horizontales entre PyMEs precisamente para reducir la vulnerabilidad frente a la salida de un comprador único.`
    );
  } else if (den >= 99.5) {
    renderPedBox("ped-dini",
      `¡Red completamente saturada (<b>K<sub>${n}</sub></b>)! Existen los <b>${lMax} vínculos máximos posibles</b> (<b>D = 100%</b>), todos los actores tienen grado idéntico <b>k = ${n - 1}</b> y por eso el Gradiente de Concentración vuelve a <b>GC = 0,0%</b>.`,
      `<b>Paradoja de la Densidad Máxima:</b> a medida que subes <b>n</b>, el número máximo de vínculos crece cuadráticamente como n(n−1)/2 (con n=5 son 10 vínculos, pero con n=15 son <b>105 vínculos</b>). En la realidad empresarial, mantener 100% de densidad con muchos actores es imposible por costos de transacción y reuniones.`,
      `Por eso Dini (2010) propone el modelo de <b>Red de Redes</b> (Diagrama 3): clústeres pequeños con alta densidad interna unidos por pocos nodos puente.`
    );
  } else {
    const diniPed = {
      simetrica: [
        `Con <b>n = ${n} actores</b> y <b>L = ${L} vínculos</b>, la densidad es <b>${fmtDec(den,1)}%</b> y el gradiente <b>GC = ${fmtDec(gc,1)}%</b>. Haz clic en dos nodos cualesquiera para romper la simetría y ver cómo sube GC al instante.`,
        `<b>Ventaja oculta y límite práctico:</b> una red simétrica es extremadamente resiliente (prueba <i>Simular Quiebra del Líder</i>), pero tiene altos costos de coordinación porque toda decisión requiere consenso entre pares.`,
        `Típica de <b>cooperativas de compras conjuntas o asociaciones de pequeños productores</b>. Recuerda el truco de examen: en matriz <b>dirigida</b> el mismo L da exactamente la <b>mitad</b> de densidad que en no dirigida.`
      ],
      liderazgo: [
        `Estructura radial con <b>n = ${n}</b> y <b>L = ${L}</b> (<b>GC = ${fmtDec(gc,1)}%</b>): la <b>Empresa Líder</b> concentra los acuerdos (<b>k<sub>máx</sub> = ${kMax}</b>). Prueba subir <b>n</b> de 4 a 15: verás que en una estrella pura la densidad <b>baja</b> (2/n) mientras GC sigue clavado en <b>100%</b>.`,
        `<b>La Fragilidad del Nodo Ancla:</b> aunque esta red es muy rápida para estandarizar calidad, sufre riesgo sistémico extremo: presiona <i>Simular Quiebra del Líder</i> arriba y mira cómo D cae a 0,0%.`,
        `Clásico de grandes compradores agroindustriales que articulan proveedores individuales. En examen (Dini, 2010): demuestra que <b>GC = 100%</b> siempre corresponde a la topología estrella.`
      ],
      jerarquica: [
        `En esta pirámide de <b>n = ${n} actores</b> (<b>D = ${fmtDec(den,1)}%</b>, <b>GC = ${fmtDec(gc,1)}%</b>), los contratistas intermedios actúan como <i>brokers</i> entre la Matriz Ancla y los talleres base (k = 1).`,
        `<b>Paradoja del Cuello de Botella:</b> aunque la Matriz manda desde la cúspide, si un contratista filtra precios o tecnología, los talleres de la base no se enteran. Prueba hacer clic entre dos talleres de la base para crear cooperación horizontal y mira cómo baja GC.`,
        `Frecuente en subcontratación forestal, construcción y metalmecánica. Para lograr <b>Upgrading funcional</b> (Padilla y Oddone), los talleres deben tejer vínculos horizontales entre sí.`
      ],
      red_redes: [
        `Tres sub-redes locales cohesionadas (Osorno, Puerto Montt y Valdivia) se articulan a través de sus nodos líderes formando un triángulo interregional (<b>n = ${n}</b>, <b>D = ${fmtDec(den,1)}%</b>, <b>GC = ${fmtDec(gc,1)}%</b>).`,
        `<b>Mundo Pequeño (Small-World):</b> combina alta confianza dentro de cada comuna (vínculos fuertes) con pocos saltos para transferir innovación entre ciudades distintas (puentes entre líderes).`,
        `Corresponde al <b>Diagrama 3 de Dini (2010)</b> en <i>04 SPL.pdf</i>. Es el modelo objetivo de una política regional de articulación territorial cuando existen gremios locales ya consolidados.`
      ],
      aviones: [
        `Una gran <b>Ensambladora</b> coordina líderes especializados por subsistema (Motores, Aviónica y Fuselaje), los cuales gestionan sus propios proveedores de nicho (<b>n = ${n}</b>, <b>GC = ${fmtDec(gc,1)}%</b>).`,
        `<b>Modularidad Productiva:</b> la ensambladora no podría gestionar miles de talleres por sí sola (colapsaría en costos de transacción); por eso delega módulos complejos a líderes de primer nivel (<i>Tier-1</i>).`,
        `Corresponde al <b>Diagrama 4 de Dini (2010)</b>. Explica cadenas globales de valor donde coexisten jerarquía tecnológica y cooperación especializada.`
      ],
      osorno: [
        `La <b>Red Láctea-Quesera de Osorno</b> alcanza alta densidad (<b>D = ${fmtDec(den,1)}%</b>) y concentración moderada (<b>GC = ${fmtDec(gc,1)}%</b>) porque <i>Aproleche</i> y <i>Cooprinsem</i> actúan como doble núcleo articulador.`,
        `<b>Por qué no colapsa ante un solo comprador:</b> prueba <i>Simular Quiebra del Líder</i> aquí y compáralo con la Estrella — al existir doble núcleo más <i>INIA Remehue</i>, la red sigue viva.`,
        `Caso directo del <b>Control 4 (Prof. Mancilla)</b>: ilustra el paso de <b>Red Empresarial → Clúster → SPL</b> al sumar instituciones tecnológicas y gremiales al territorio.`
      ],
      pymemad: [
        `En el <b>Clúster Forestal-Maderero PymeMad (Biobío)</b> (<b>D = ${fmtDec(den,1)}%</b>, <b>GC = ${fmtDec(gc,1)}%</b>), el gremio conecta aserraderos y plantas de remanufactura CLT con centros de I+D y logística.`,
        `<b>Eficiencia Colectiva (Schmitz):</b> un aserradero PyME aislado no puede certificar madera estructural CLT ni exportar lotes grandes; al cooperar horizontalmente captura economías de escala.`,
        `Caso aplicado del <b>Control 4</b>: recuerda validar el mapa de la cadena en entrevista sin imponer la palabra "clúster" ni preguntar por "debilidades" (usar "desafíos").`
      ]
    };
    const dp = diniPed[diniKey] || diniPed.simetrica;
    renderPedBox("ped-dini", dp[0], dp[1], dp[2]);
  }
}

// ============================================================================
// 8. HOJA DE ENTRENAMIENTO MECÁNICO TERRITORIAL (16 FÓRMULAS + 6 ESQUELETOS)
// ============================================================================
const FORMULAS_TERR = [
  { id: 1, cat: "loc", tag: "Von Thünen", title: "1. Renta Locacional y Anillos",
    eq: `LR(d) = Y(m − c) − Y·t·d`,
    rule: "Pendiente negativa (-Y·t). Las actividades con mayor flete/margen ocupan el anillo más cercano al mercado urbano." },
  { id: 2, cat: "loc", tag: "Weber", title: "2. Índice de Materiales (IM) e Isodápana",
    eq: `IM = <span class="frac"><span class="num">Peso MP Localizadas</span><span class="den">Peso Producto Final</span></span>`,
    rule: "IM > 1 → cerca de insumos (pérdida de peso). IM < 1 → cerca del mercado. Desvío a L solo si cae dentro de la isodápana crítica." },
  { id: 3, cat: "loc", tag: "Krugman", title: "3. Nueva Economía Geográfica (Precio y τ*)",
    eq: `p*(x) = <span class="frac"><span class="num">a·W(x)</span><span class="den">ρ</span></span> &nbsp;|&nbsp; τ ≤ τ* ⇒ Aglomeración`,
    rule: "Si el costo de transporte τ cae bajo el umbral crítico τ*, las fuerzas centrípetas (escala + mercado local) disparan la macrocefalia." },
  { id: 4, cat: "loc", tag: "Hirschman", title: "4. Polos (Perroux/Hirschman/Myrdal) y Christaller",
    eq: `M<sub>H</sub> = <span class="frac"><span class="num">1</span><span class="den">1 − (b + f)</span></span> &nbsp;|&nbsp; Pob ≥ Umbral ∧ Alcance ≥ Dist`,
    rule: "Saldo periferia = Spread − Backwash. En Christaller un servicio es viable si supera el Umbral demográfico dentro de su Alcance (km)." },

  { id: 5, cat: "ilpes", tag: "ILPES 59", title: "5. Cociente de Localización (Qij)",
    eq: `Q<sub>ij</sub> = <span class="frac"><span class="num">V<sub>ij</sub> / ∑<sub>i</sub> V<sub>ij</sub></span><span class="den">∑<sub>j</sub> V<sub>ij</sub> / ∑<sub>i</sub>∑<sub>j</sub> V<sub>ij</sub></span></span>`,
    rule: "Qij > 1 indica especialización relativa de la comuna j en el sector i (sector básico exportador)." },
  { id: 6, cat: "ilpes", tag: "ILPES 59", title: "6. Coeficiente de Especialización (Qr)",
    eq: `Q<sub>r</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> ∑<sub>i</sub> |P<sub>ij</sub> − P<sub>i</sub>|`,
    rule: "Rango [0, 1]. Cercano a 0 = estructura diversificada (igual a la región); cercano a 1 = alta especialización comunal." },
  { id: 7, cat: "ilpes", tag: "ILPES 59", title: "7. Coeficiente de Reestructuración (CRr)",
    eq: `CR<sub>r</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> ∑<sub>i</sub> |P<sub>ij,t</sub> − P<sub>ij,0</sub>|`,
    rule: "Rango [0, 1]. Mide cuánto cambió la composición sectorial de una comuna entre el año inicial t0 y el final tf." },
  { id: 8, cat: "ilpes", tag: "Tiebout", title: "8. Base Económica Exportadora y Multiplicador",
    eq: `X<sub>ij</sub> = V<sub>ij</sub> − <span class="frac"><span class="num">V<sub>ij</sub></span><span class="den">Q<sub>ij</sub></span></span> (∀Q<sub>ij</sub>&gt;1) &nbsp;|&nbsp; M<sub>j</sub> = <span class="frac"><span class="num">V<sub>j</sub></span><span class="den">X<sub>j</sub></span></span>`,
    rule: "Xj es el excedente exportable de la comuna. Mj indica cuánta actividad total genera cada $1 de base exportadora." },
  { id: 9, cat: "ilpes", tag: "MADE", title: "9. Shift & Share Clásico y Modificado (Stilwell)",
    eq: `ET<sub>j</sub> = EE<sub>j</sub> + ED<sub>j</sub> &nbsp;|&nbsp; EM<sub>j</sub> = EI<sub>j</sub> − EE<sub>j</sub> ; ERM<sub>j</sub> = ET<sub>j</sub> − EI<sub>j</sub>`,
    rule: "EE = composición sectorial; ED = competitividad local. 6 tipologías de Boisier (clásico) y 14 tipologías de Stilwell (modificado)." },

  { id: 10, cat: "reat", tag: "REAT", title: "10. Convergencia Sigma (σ) y Beta Absoluta (β)",
    eq: `<span class="frac"><span class="num">1</span><span class="den">T</span></span>ln(<span class="frac"><span class="num">Y<sub>i,t</sub></span><span class="den">Y<sub>i,0</sub></span></span>) = α + β·ln(Y<sub>i,0</sub>) + ε<sub>i</sub>`,
    rule: "β < 0 y p < 0,05 confirma Convergencia Beta. Velocidad λ = −ln(1 + βT)/T y Semivida t(1/2) = ln(2)/λ." },
  { id: 11, cat: "reat", tag: "REAT", title: "11. Curva de Lorenz e Índice de Gini (Trapecios)",
    eq: `G = 1 − ∑<sub>i=1..n</sub> (p<sub>i</sub> − p<sub>i-1</sub>)(q<sub>i</sub> + q<sub>i-1</sub>) &nbsp;|&nbsp; G* = G·<span class="frac"><span class="num">N</span><span class="den">N−1</span></span>`,
    rule: "G = 0 equidad perfecta; G → 1 concentración absoluta. A mayor alejamiento de la diagonal de 45°, mayor desigualdad." },
  { id: 12, cat: "reat", tag: "REAT", title: "12. Índice de Entropía de Theil (T)",
    eq: `T = ∑<sub>i=1..n</sub> s<sub>i</sub> · ln(n · s<sub>i</sub>)`,
    rule: "Rango [0, ln(n)]. Su gran ventaja sobre el Gini es ser perfectamente descomponible en desigualdad Entre-regiones + Intra-región." },
  { id: 13, cat: "reat", tag: "REAT", title: "13. Concentración: HHI y Hannah-Kay (HKα)",
    eq: `HHI = ∑ s<sub>i</sub><sup>2</sup> &nbsp;|&nbsp; HK<sub>α</sub> = (∑ s<sub>i</sub><sup>α</sup>)<sup>1/(1−α)</sup>`,
    rule: "HHI ∈ [1/n, 1]. En la convención de número equivalente, HKα indica cuántas comunas de igual tamaño replican la concentración." },

  { id: 14, cat: "ot", tag: "Dini 2010", title: "14. Densidad de Red y Gradiente de Concentración",
    eq: `D = <span class="frac"><span class="num">2L</span><span class="den">n(n − 1)</span></span> &nbsp;|&nbsp; GC<sub>red</sub> = <span class="frac"><span class="num">∑(k<sub>máx</sub> − k<sub>i</sub>)</span><span class="den">(n−1)(n−2)</span></span>`,
    rule: "Diagonal principal A_ii = 0. En red dirigida D = L/[n(n−1)]. GC = 0% (Red Simétrica) ↔ GC = 100% (Red Estrella/Liderazgo)." },
  { id: 15, cat: "ot", tag: "OT 2024", title: "15. Índice de Primacía Urbana (IP4) y Zipf",
    eq: `IP<sub>4</sub> = <span class="frac"><span class="num">P<sub>1</sub></span><span class="den">P<sub>2</sub> + P<sub>3</sub> + P<sub>4</sub></span></span> &nbsp;|&nbsp; P<sub>r</sub> = <span class="frac"><span class="num">P<sub>1</sub></span><span class="den">r</span></span>`,
    rule: "Escala Mancilla (0–3): <0,65 Muy Disp.(0) · 0,65–1,00 Disp.(1) · 1,00–1,50 Conc.(2) · ≥1,50 Macrocefalia(3)." },
  { id: 16, cat: "ot", tag: "Rondinelli", title: "16. Escalograma de Guttman y Centralidad Rondinelli",
    eq: `W<sub>k</sub> = <span class="frac"><span class="num">100</span><span class="den">f<sub>k</sub></span></span> &nbsp;|&nbsp; IC<sub>i</sub> = ∑<sub>k</sub> X<sub>ik</sub> · W<sub>k</sub>`,
    rule: "X_ik ∈ {0,1}. Variables deben discriminar entre comunas (si todas tienen 1, reemplazar). Servicios más raros otorgan mayor peso Wk." },

  { id: 17, cat: "ind", tag: "Unidad VI", title: "17. Normalización Mínimo–Máximo (Favorable vs. Desfavorable)",
    eq: `u<sup>+</sup>(x<sub>i</sub>) = <span class="frac"><span class="num">x<sub>i</sub> − mín</span><span class="den">máx − mín</span></span> &nbsp;|&nbsp; u<sup>−</sup>(x<sub>i</sub>) = <span class="frac"><span class="num">máx − x<sub>i</sub></span><span class="den">máx − mín</span></span>`,
    rule: "Lleva cualquier escala (ej. 200–3.000 o %) al intervalo [0, 1]. Favorable (+): el valor más alto da 1; Desfavorable (−): el valor más bajo da 1." },
  { id: 18, cat: "ind", tag: "Unidad VI", title: "18. Índice Compuesto Ponderado y Ranking Territorial",
    eq: `I<sub>i</sub> = ∑<sub>k</sub> w<sub>k</sub> · u<sub>k</sub>(x<sub>ik</sub>) &nbsp;&nbsp;(∑ w<sub>k</sub> = 1)`,
    rule: "Un territorio solo alcanza I = 1,00 si es líder simultáneo en todas las variables. Cambiar pesos (ej. 50/50 → 70/30) altera el ranking." }
];

const ESQUELETOS_TERR = [
  {
    title: "1. Von Thünen (Gradiente LR y Anillos)",
    sub: "Mayor pendiente = anillo interior; los cortes LR1=LR2 y LR2=LR3 fijan los radios.",
    svg: `<svg viewBox="0 0 260 150">
      <line x1="22" y1="128" x2="148" y2="128" stroke="#0F172A" stroke-width="1.5"/><line x1="22" y1="16" x2="22" y2="128" stroke="#0F172A" stroke-width="1.5"/>
      <line x1="22" y1="26" x2="78" y2="128" stroke="#DC2626" stroke-width="2"/><line x1="22" y1="58" x2="112" y2="128" stroke="#1D4ED8" stroke-width="2"/>
      <line x1="22" y1="90" x2="144" y2="128" stroke="#059669" stroke-width="2"/>
      <circle cx="206" cy="76" r="46" fill="rgba(5,150,105,0.18)" stroke="#059669"/><circle cx="206" cy="76" r="30" fill="rgba(29,78,216,0.20)" stroke="#1D4ED8"/>
      <circle cx="206" cy="76" r="15" fill="rgba(220,38,38,0.24)" stroke="#DC2626"/><circle cx="206" cy="76" r="3" fill="#0F172A"/>
      <g class="sk-lbl" font-size="9" font-weight="700">
        <text x="10" y="24">LR</text><text x="142" y="142">d</text><text x="48" y="45" fill="#DC2626">LR1</text><text x="86" y="76" fill="#1D4ED8">LR2</text><text x="122" y="106" fill="#059669">LR3</text>
        <text x="206" y="140" text-anchor="middle">Anillos 1-2-3</text>
      </g>
    </svg>`
  },
  {
    title: "2. Triángulo de Weber + Isodápana",
    sub: "IM>1 atrae P* a MP1/MP2; desvío a L solo si L cae dentro de la curva punteada.",
    svg: `<svg viewBox="0 0 260 150">
      <polygon points="48,26 48,128 214,78" fill="#F8FAFC" stroke="#94A3B8" stroke-width="1.6"/>
      <circle cx="114" cy="78" r="44" fill="rgba(21,128,61,0.12)" stroke="#15803D" stroke-width="1.6" stroke-dasharray="4,3"/>
      <circle cx="48" cy="26" r="5" fill="#1D4ED8"/><circle cx="48" cy="128" r="5" fill="#1D4ED8"/><circle cx="214" cy="78" r="5" fill="#0F172A"/>
      <circle cx="114" cy="78" r="5" fill="#DC2626"/><circle cx="146" cy="46" r="5" fill="#EA580C"/>
      <g class="sk-lbl" font-size="9" font-weight="700">
        <text x="26" y="22" fill="#1D4ED8">MP1</text><text x="26" y="142" fill="#1D4ED8">MP2</text><text x="218" y="82">M</text>
        <text x="106" y="96" fill="#DC2626">P*</text><text x="154" y="46" fill="#EA580C">L</text><text x="118" y="138" fill="#15803D">Isodápana</text>
      </g>
    </svg>`
  },
  {
    title: "3. Bifurcación de Krugman (τ*)",
    sub: "Al bajar τ bajo τ* la participación del centro salta de 50% a aglomeración.",
    svg: `<svg viewBox="0 0 260 150">
      <line x1="28" y1="128" x2="244" y2="128" stroke="#0F172A" stroke-width="1.5"/><line x1="28" y1="16" x2="28" y2="128" stroke="#0F172A" stroke-width="1.5"/>
      <line x1="136" y1="18" x2="136" y2="128" stroke="#D97706" stroke-width="1.8" stroke-dasharray="4,3"/>
      <path d="M 34 28 C 95 30, 120 55, 136 74 C 152 93, 175 112, 240 116" fill="none" stroke="#1D4ED8" stroke-width="2.4"/>
      <g class="sk-lbl" font-size="9" font-weight="700">
        <text x="6" y="28">100%</text><text x="8" y="120">50%</text><text x="140" y="28" fill="#B45309">τ*</text>
        <text x="48" y="50" fill="#DC2626">Aglomeración</text><text x="166" y="102" fill="#15803D">Dispersión</text><text x="234" y="142">τ</text>
      </g>
    </svg>`
  },
  {
    title: "4. Cuadrantes de Silva Lira (2×2)",
    sub: "Eje X: Nivel per cápita vs prom. reg.; Eje Y: Crec. anual vs prom. reg.",
    svg: `<svg viewBox="0 0 260 150">
      <rect x="26" y="18" width="214" height="108" fill="#FFFFFF" stroke="#94A3B8"/>
      <line x1="133" y1="18" x2="133" y2="126" stroke="#1D4ED8" stroke-width="1.6" stroke-dasharray="4,3"/>
      <line x1="26" y1="72" x2="240" y2="72" stroke="#DC2626" stroke-width="1.6" stroke-dasharray="4,3"/>
      <g class="sk-lbl" font-size="9" font-weight="700" text-anchor="middle">
        <text x="80" y="48" fill="#1D4ED8">II. Emergente (-,+)</text><text x="186" y="48" fill="#15803D">I. Dinámica (+,+)</text>
        <text x="80" y="102" fill="#DC2626">IV. Retroceso (-,-)</text><text x="186" y="102" fill="#B45309">III. Estancada (+,-)</text>
        <text x="133" y="142">Nivel per cápita (X)</text>
      </g>
    </svg>`
  },
  {
    title: "5. Curva de Lorenz y Gini",
    sub: "Diagonal 45° = equidad perfecta; área sombreada = desigualdad (G = 2A).",
    svg: `<svg viewBox="0 0 260 150">
      <line x1="34" y1="128" x2="224" y2="128" stroke="#0F172A" stroke-width="1.5"/><line x1="34" y1="18" x2="34" y2="128" stroke="#0F172A" stroke-width="1.5"/>
      <line x1="34" y1="128" x2="224" y2="18" stroke="#64748B" stroke-width="1.6" stroke-dasharray="5,3"/>
      <path d="M 34 128 Q 160 122 224 18 L 34 128 Z" fill="rgba(220,38,38,0.18)" stroke="#DC2626" stroke-width="2"/>
      <g class="sk-lbl" font-size="9" font-weight="700">
        <text x="108" y="64" fill="#475569">45° Equidad</text><text x="132" y="104" fill="#DC2626">Área A (G=2A)</text>
        <text x="205" y="142">p_i %</text><text x="8" y="26">q_i %</text>
      </g>
    </svg>`
  },
  {
    title: "6. Redes Dini: Simétrica vs. Liderazgo",
    sub: "Izq: todos igual k (GC=0%). Der: nodo líder central (GC=100%).",
    svg: `<svg viewBox="0 0 260 150">
      <polygon points="62,36 96,60 84,104 40,104 28,60" fill="none" stroke="#1D4ED8" stroke-width="1.8"/>
      <circle cx="62" cy="36" r="5" fill="#1D4ED8"/><circle cx="96" cy="60" r="5" fill="#1D4ED8"/><circle cx="84" cy="104" r="5" fill="#1D4ED8"/><circle cx="40" cy="104" r="5" fill="#1D4ED8"/><circle cx="28" cy="60" r="5" fill="#1D4ED8"/>
      <line x1="194" y1="74" x2="194" y2="34" stroke="#DC2626" stroke-width="1.8"/><line x1="194" y1="74" x2="232" y2="62" stroke="#DC2626" stroke-width="1.8"/>
      <line x1="194" y1="74" x2="218" y2="108" stroke="#DC2626" stroke-width="1.8"/><line x1="194" y1="74" x2="170" y2="108" stroke="#DC2626" stroke-width="1.8"/><line x1="194" y1="74" x2="156" y2="62" stroke="#DC2626" stroke-width="1.8"/>
      <circle cx="194" cy="74" r="8" fill="#DC2626"/><circle cx="194" cy="34" r="4.5" fill="#0F172A"/><circle cx="232" cy="62" r="4.5" fill="#0F172A"/><circle cx="218" cy="108" r="4.5" fill="#0F172A"/><circle cx="170" cy="108" r="4.5" fill="#0F172A"/><circle cx="156" cy="62" r="4.5" fill="#0F172A"/>
      <g class="sk-lbl" font-size="9" font-weight="700" text-anchor="middle">
        <text x="62" y="138" fill="#1D4ED8">Simétrica (GC=0%)</text><text x="194" y="138" fill="#DC2626">Liderazgo (GC=100%)</text>
      </g>
    </svg>`
  }
];

let mecBlind = false, mecFilter = "all", mecMastered = new Set(), mecBuilt = false;
function renderMecanica() {
  const fGrid = document.getElementById("mec-formulas-grid"), sGrid = document.getElementById("mec-skel-grid");
  if (!fGrid || !sGrid) return;
  fGrid.innerHTML = "";
  FORMULAS_TERR.filter(f => mecFilter === "all" || f.cat === mecFilter).forEach(item => {
    const card = document.createElement("div");
    card.className = "f-card" + (mecMastered.has(item.id) ? " mastered" : "");
    card.innerHTML = `
      <div class="f-head">
        <div><span class="f-cat">${item.tag}</span> <span class="f-title">${item.title}</span></div>
        <button class="chk-btn" title="Marcar dominada" onclick="toggleMastered(${item.id}, event)">✓</button>
      </div>
      <div class="f-body" onclick="this.parentElement.classList.toggle('revealed')">
        <div class="blind-cover">Haz clic para revelar y comprobar tu cuaderno</div>
        <div class="f-eq">${item.eq}</div>
        <div class="f-rule">${item.rule}</div>
      </div>`;
    fGrid.appendChild(card);
  });
  if (!mecBuilt) {
    sGrid.innerHTML = "";
    ESQUELETOS_TERR.forEach(sk => {
      const sc = document.createElement("div");
      sc.className = "s-card";
      sc.onclick = function() { this.classList.toggle("revealed"); };
      sc.innerHTML = `<div class="s-title">${sk.title}</div>${sk.svg}<div class="s-sub">${sk.sub}</div>`;
      sGrid.appendChild(sc);
    });
    mecBuilt = true;
  }
  document.getElementById("mec-score").textContent = `Dominadas: ${mecMastered.size} / ${FORMULAS_TERR.length}`;
}
function setModoMec(isBlind) {
  mecBlind = isBlind;
  const cont = document.getElementById("mec-container");
  cont.classList.toggle("blind-mode", isBlind);
  document.getElementById("btn-modo-copia").classList.toggle("primary", !isBlind);
  document.getElementById("btn-modo-ciego").classList.toggle("primary", isBlind);
  cont.querySelectorAll(".f-card, .s-card").forEach(n => n.classList.remove("revealed"));
}
function filtrarMec(cat, btn) {
  mecFilter = cat;
  btn.parentElement.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderMecanica();
}
function toggleMastered(id, ev) {
  ev.stopPropagation();
  if (mecMastered.has(id)) mecMastered.delete(id); else mecMastered.add(id);
  renderMecanica();
}
function resetDominadas() { mecMastered.clear(); renderMecanica(); }

drawThunen();
drawWeber();
drawKrugman();
drawPerroux();
drawChrisGran();
drawLorenz();

// ============================================================================
// 9. MAPA CAUSAL TEÓRICO, LECTURA EN 3 CAPAS Y QUIZ CRUZADO (60 FPS)
// ============================================================================
const MAPA_UNIDADES = {
  U1: {
    id: "U1", x: 165, y: 86, w: 255, h: 74, col: "#0F766E",
    lbl: "U.I · CRECIMIENTO TERRITORIAL",
    sub: "Manual 59 ILPES · Silva Lira (2005)\nQij · Qr · MADE · Perroux/Hirschman",
    explica: "Analiza la estructura productiva y el dinamismo de los territorios usando matrices Sector × Comuna (SII / BCCh): vocación exportadora (Q<sub>ij</sub> &gt; 1), diversificación (Q<sub>r</sub>), cambio estructural (CR<sub>r</sub>), polos motrices, Silva Lira (4 cuadrantes) y Shift &amp; Share (EE + ED).",
    puentes: "<b>→ Hacia U.II:</b> la concentración sectorial observada se explica por los costos de transporte y economías de escala. <b>→ Hacia U.III:</b> las comunas Emergentes (Cuadrante II Silva Lira) son el motor empírico de la Convergencia β. <b>→ Hacia U.VI:</b> el PIB per cápita y dinamismo alimentan los índices sintéticos de desarrollo.",
    jumps: [["perroux", "Abrir Polos (U.I)"], ["mecanica", "Ver Fórmulas ILPES/MADE"]]
  },
  U2: {
    id: "U2", x: 490, y: 86, w: 255, h: 74, col: "#1D4ED8",
    lbl: "U.II · ESPACIO Y LOCALIZACIÓN",
    sub: "Duch Brown (2005) · Von Thünen\nWeber · Christaller · Krugman (1991)",
    explica: "Explica por qué la actividad económica se aglomera o se dispersa en el espacio: anillos de renta locacional LR(d), triangulación de costos de transporte e isodápana crítica (IM), umbral/alcance de ciudades y bifurcación Centro-Periferia cuando cae el transporte τ ≤ τ*.",
    puentes: "<b>→ Hacia U.III:</b> si τ ≤ τ* (Krugman), se dispara la concentración regional (suben Gini, Theil y HHI). <b>→ Hacia U.V:</b> el umbral y alcance de Christaller fundamentan la jerarquía de servicios de Rondinelli/Guttman.",
    jumps: [["thunen", "Abrir Von Thünen"], ["weber", "Abrir Weber"], ["krugman", "Abrir Krugman"]]
  },
  U3: {
    id: "U3", x: 815, y: 86, w: 255, h: 74, col: "#B91C1C",
    lbl: "U.III · DISPARIDADES Y REAT",
    sub: "Convergencia σ y β · Lorenz/Gini\nTheil · HHI/HKα · Figueroa · Riquelme",
    explica: "Evalúa si las brechas entre territorios se cierran o amplían: Convergencia Sigma (dispersión σ), Convergencia Beta (β &lt; 0), desigualdad (Gini y Theil descomponible inter/intra-región), concentración espacial (HHI, HK<sub>α</sub>) y cadenas de Markov.",
    puentes: "<b>← Desde U.I y U.II:</b> cuantifica las brechas que nacen de la aglomeración y los polos. <b>→ Hacia U.V y U.VI:</b> la desigualdad territorial sustenta el Ordenamiento Territorial (PROT) y exige indicadores multidimensionales comparables.",
    jumps: [["lorenz", "Abrir Lorenz, Gini y Theil"]]
  },
  U4: {
    id: "U4", x: 165, y: 235, w: 255, h: 74, col: "#7C3AED",
    lbl: "U.IV · SPL, REDES Y CADENAS",
    sub: "Dini (2010) · Granovetter · UCINET\nCadenas de Valor (CEPAL) · ELITE",
    explica: "Aporta la palanca productiva e institucional para que las PyMEs compitan: cooperación horizontal (Red → Clúster → SPL), puentes débiles para innovación (evitar <i>lock-in</i>), escalamiento (Upgrading) y densidad/gradiente de concentración en UCINET.",
    puentes: "<b>→ Hacia U.I y U.III:</b> las redes empresariales (Aproleche, PymeMad) elevan los encadenamientos (b+f) y la competitividad local (ED<sub>j</sub> &gt; 0), impulsando convergencia territorial.",
    jumps: [["dini", "Abrir Redes Dini 2010"], ["christaller", "Abrir Granovetter"]]
  },
  U5: {
    id: "U5", x: 490, y: 235, w: 255, h: 74, col: "#B45309",
    lbl: "U.V · ORDENAMIENTO OT / PROT",
    sub: "06 OT 2026 · Primacía IP4 · Zipf\nGuttman/Rondinelli · Aislamiento · PROT",
    explica: "Diagnostica la red de asentamientos humanos y resuelve conflictos de uso del suelo (Sistemas Costero, Urbano, Rural y Cuencas) usando Primacía Urbana (IP<sub>4</sub> escala 0–3), centralidad funcional (Rondinelli) y Matriz de Aislamiento vial.",
    puentes: "<b>← Desde U.II y U.III:</b> traduce la aglomeración en IP<sub>4</sub> y jerarquías urbanas. <b>→ Hacia U.VI:</b> los indicadores de equipamiento y aislamiento se normalizan en [0,1] para construir índices sintéticos comunales.",
    jumps: [["ot", "Abrir Laboratorio OT (U.V)"], ["mecanica", "Ver Fórmulas OT"]]
  },
  U6: {
    id: "U6", x: 815, y: 235, w: 255, h: 74, col: "#15803D",
    lbl: "U.VI · INDICADORES DESARROLLO",
    sub: "Normalización Mín–Máx [0, 1]\nFavorable (+) / Desfavorable (−) · Pesos",
    explica: "Integra múltiples variables en distintas unidades (pesos, %, tasas, distancias) en un único Índice Sintético entre 0 y 1 mediante estandarización Mínimo–Máximo, distinguiendo sentido favorable vs. desfavorable y evaluando la sensibilidad del ranking ante cambios de ponderación (50/50 vs. 70/30).",
    puentes: "<b>← Desde U.I, U.III y U.V:</b> sintetiza indicadores de crecimiento, desigualdad, equipamiento y aislamiento en un ranking territorial comparable para priorizar inversión pública regional.",
    jumps: [["indicadores", "Abrir Laboratorio Mín-Máx (U.VI)"]]
  }
};

const MAPA_EDGES = [
  { a: "U1", b: "U2", lbl: "Localización ↔ Qij" },
  { a: "U2", b: "U3", lbl: "τ ≤ τ* → Gini↑" },
  { a: "U1", b: "U4", lbl: "EDj+ ↔ Redes" },
  { a: "U4", b: "U5", lbl: "SPL + Gobernanza" },
  { a: "U3", b: "U5", lbl: "Brecha → OT/PROT" },
  { a: "U3", b: "U6", lbl: "Variables → [0,1]" },
  { a: "U5", b: "U6", lbl: "OT → Ranking U.VI" },
  { a: "U2", b: "U5", lbl: "Umbral/Rondinelli" }
];

const ESCENARIOS_MAPA = {
  fletes: {
    titulo: "Cadena A: Shock de Baja en Costos de Transporte (τ ↓)",
    nodes: ["U2", "U3", "U5"],
    edges: [["U2", "U3"], ["U3", "U5"], ["U2", "U5"]],
    texto: "<b>1) En U.II (Krugman):</b> al caer τ bajo τ*, predominan las fuerzas centrípetas y las firmas se concentran en la capital regional. " +
           "<b>2) En U.III (REAT):</b> sube la dispersión σ y la Curva de Lorenz se abomba (suben Gini, Theil y HHI). " +
           "<b>3) En U.V (OT):</b> el Índice de Primacía IP<sub>4</sub> salta al tramo ≥ 1,50 (Macrocefalia), exigiendo políticas PROT de reequilibrio.",
    jumps: [["krugman", "Probar τ ↓ en Krugman"], ["ot", "Ver Flechas e IP4 (OT)"], ["lorenz", "Ver Gini y Lorenz"]]
  },
  cluster: {
    titulo: "Cadena B: Política de Clúster, Puentes I+D y Upgrading (SPL)",
    nodes: ["U4", "U1", "U3"],
    edges: [["U1", "U4"], ["U1", "U2"], ["U2", "U3"]],
    texto: "<b>1) En U.IV (Dini + Granovetter):</b> un gremio articulador (PymeMad o Aproleche) abre vínculos débiles con universidades/I+D, evita el <i>lock-in</i> y hace Upgrading. " +
           "<b>2) En U.I (ILPES/MADE):</b> la comuna mejora su competitividad local (ED<sub>j</sub> &gt; 0) y salta a Cuadrante II (Emergente) o I (Dinámica) en Silva Lira. " +
           "<b>3) En U.III (REAT):</b> el mayor dinamismo de comunas intermedias impulsa la Convergencia Beta (β &lt; 0).",
    jumps: [["dini", "Probar Red Dini"], ["christaller", "Probar Puentes Granovetter"]]
  },
  prot: {
    titulo: "Cadena C: Del Diagnóstico Territorial (OT) al Índice Sintético de Desarrollo (U.VI)",
    nodes: ["U3", "U5", "U6"],
    edges: [["U3", "U5"], ["U5", "U6"], ["U3", "U6"]],
    texto: "<b>1) En U.III y U.V:</b> se levantan indicadores heterogéneos por comuna o provincia (PIB per cápita en $, pobreza en %, centralidad de Rondinelli en puntos, aislamiento en %). " +
           "<b>2) En U.VI (Indicadores Mín-Máx):</b> cada variable se normaliza a [0, 1] respetando su sentido favorable (+) o desfavorable (−), se pondera y se prueba la estabilidad del ranking (50/50 vs. 70/30) para focalizar presupuestos regionales.",
    jumps: [["ot", "Abrir Laboratorio OT (U.V)"], ["indicadores", "Abrir Laboratorio Mín-Máx (U.VI)"]]
  }
};

let mapaActivoUnidad = "U1";
let mapaEscenarioKey = null;

function selectUnidadMapa(uKey) {
  mapaEscenarioKey = null;
  mapaActivoUnidad = uKey;
  drawMapaTeoria();
}
function activarEscenarioMapa(escKey) {
  mapaEscenarioKey = escKey;
  drawMapaTeoria();
}
function drawMapaTeoria() {
  const svg = document.getElementById("svg-mapa-teoria");
  const box = document.getElementById("mapa-detail-box");
  if (!svg || !box) return;
  svg.innerHTML = "";
  addDefs(svg);

  const esc = mapaEscenarioKey ? ESCENARIOS_MAPA[mapaEscenarioKey] : null;
  const activeNodes = new Set(esc ? esc.nodes : [mapaActivoUnidad]);

  // Dibujar aristas causales
  MAPA_EDGES.forEach(ed => {
    const na = MAPA_UNIDADES[ed.a], nb = MAPA_UNIDADES[ed.b];
    let isHot = false;
    if (esc) {
      isHot = esc.edges.some(([x, y]) => (x === ed.a && y === ed.b) || (x === ed.b && y === ed.a));
    } else {
      isHot = (ed.a === mapaActivoUnidad || ed.b === mapaActivoUnidad);
    }
    const dx = nb.x - na.x, dy = nb.y - na.y, dist = Math.hypot(dx, dy) || 1;
    const x1 = na.x + (dx / dist) * 58, y1 = na.y + (dy / dist) * 32;
    const x2 = nb.x - (dx / dist) * 62, y2 = nb.y - (dy / dist) * 34;

    el("line", {
      x1, y1, x2, y2,
      stroke: isHot ? "#DC2626" : "#CBD5E1",
      "stroke-width": isHot ? "2.8" : "1.5",
      "stroke-dasharray": isHot ? "" : "4,3",
      "marker-end": isHot ? "url(#arr-red)" : ""
    }, svg);

    const mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
    if (isHot) {
      const bw = Math.max(76, ed.lbl.length * 6.2 + 10);
      el("rect", { x: mx - bw / 2, y: my - 9, width: bw, height: 16, rx: 4, fill: "#FFFFFF", stroke: "#DC2626", "stroke-width": "1" }, svg);
      const tl = el("text", { x: mx, y: my + 3, fill: "#991B1B", "font-size": "9.8", "font-weight": "700", "text-anchor": "middle" }, svg);
      tl.textContent = ed.lbl;
    }
  });

  // Dibujar nodos interactivos clicables
  Object.values(MAPA_UNIDADES).forEach(nd => {
    const isSel = activeNodes.has(nd.id);
    const g = el("g", { style: "cursor:pointer;", onclick: `selectUnidadMapa('${nd.id}')` }, svg);
    el("rect", {
      x: nd.x - nd.w / 2, y: nd.y - nd.h / 2, width: nd.w, height: nd.h, rx: 9,
      fill: isSel ? nd.col : "#FFFFFF",
      stroke: isSel ? "#0F172A" : nd.col,
      "stroke-width": isSel ? "2.6" : "1.8",
      opacity: esc && !isSel ? "0.45" : "1"
    }, g);

    const t1 = el("text", { x: nd.x, y: nd.y - 12, fill: isSel ? "#FFFFFF" : nd.col, "font-size": "11.5", "font-weight": "800", "text-anchor": "middle" }, g);
    t1.textContent = nd.lbl;
    nd.sub.split("\n").forEach((ln, k) => {
      const ts = el("text", { x: nd.x, y: nd.y + 6 + k * 14, fill: isSel ? "#F1F5F9" : "#334155", "font-size": "10", "font-weight": "600", "text-anchor": "middle" }, g);
      ts.textContent = ln;
    });
  });

  // Render detalle inferior
  if (esc) {
    const btnsHtml = esc.jumps.map(([tb, lbl]) => `<button class="jump-btn" onclick="jumpToTab('${tb}')">${lbl} →</button>`).join(" ");
    box.innerHTML = `
      <div class="map-detail-head">
        <span class="map-detail-title">${esc.titulo}</span>
        <div class="btn-bar">${btnsHtml}</div>
      </div>
      <div>${esc.texto}</div>`;
  } else {
    const u = MAPA_UNIDADES[mapaActivoUnidad];
    const btnsHtml = u.jumps.map(([tb, lbl]) => `<button class="jump-btn" onclick="jumpToTab('${tb}')">${lbl} →</button>`).join(" ");
    box.innerHTML = `
      <div class="map-detail-head">
        <span class="map-detail-title">${u.lbl} (Haz clic en cualquier otra unidad del diagrama para cambiar el foco)</span>
        <div class="btn-bar">${btnsHtml}</div>
      </div>
      <div><b>Lógica central:</b> ${u.explica}</div>
      <div style="margin-top:5px;"><b>Interrelación con el resto del ramo:</b> ${u.puentes}</div>`;
  }
}

const FICHAS_LECTURA = [
  {
    unit: "U2", src: "Duch (2005) La teoría de la localización · Atienza y Aroca (2012)",
    title: "1. Teoría Clásica y Nueva Economía Geográfica (Von Thünen, Weber, Christaller, Krugman)",
    core: "<b>Idea central:</b> La distancia cuesta dinero. Von Thünen ordena el uso del suelo rural en anillos según renta locacional LR(d); Weber minimiza el flete industrial con el Índice de Materiales (IM) y evalúa desvíos salariales con la Isodápana Crítica; Christaller define la jerarquía de ciudades por Umbral y Alcance; Krugman (1991) formaliza la competencia imperfecta y muestra que bajar τ bajo τ* dispara la aglomeración Centro-Periferia.",
    bridge: "<b>Puente inter-unidades:</b> Es la causa teórica de lo que luego mides empíricamente en U2 (especialización Q<sub>ij</sub>), U3 (concentración Gini/HHI) y U5 (macrocefalia IP<sub>4</sub> y centralidad de Rondinelli).",
    trap: "<b>Trampas de control:</b> (1) En Weber, si IM &gt; 1 (pierde peso al procesar, ej. madera/leche en polvo) se ubica cerca de insumos; si IM &lt; 1 (gana peso con insumos ubicuos, ej. bebidas) se ubica cerca del mercado. (2) Desviarse a un enclave laboral barato L solo conviene si L cae <i>dentro</i> de la isodápana crítica (ahorro salarial &gt; sobrecosto de flete)."
  },
  {
    unit: "U1", src: "Perroux (1955) · Myrdal (1957) · Hirschman (1958)",
    title: "2. Polos de Crecimiento, Causalidad Acumulativa y Encadenamientos",
    core: "<b>Idea central:</b> El crecimiento no surge parejo en todos lados sino en <i>polos motrices</i> (Perroux). Su impacto regional depende de los encadenamientos hacia atrás (proveedores b) y hacia adelante (procesamiento f) de Hirschman, y del balance neto entre difusión hacia comunas vecinas (<i>Spread</i>) versus absorción de talento y capital (<i>Backwash</i>) de Myrdal.",
    bridge: "<b>Puente inter-unidades:</b> Si un polo tiene bajo b + f opera como enclave y genera divergencia en U3; para volverlo polo integrador se requieren redes de proveedores y Upgrading de U4.",
    trap: "<b>Trampas de control:</b> No confundir un proyecto grande con un polo integrador: si la industria importa sus insumos y se lleva los excedentes (Backwash &gt; Spread), profundiza la desigualdad intercomunal en lugar de generar convergencia."
  },
  {
    unit: "U1", src: "Manual 59 ILPES (Lira & Quiroga) · Silva Lira (2005) · PIB/Pob",
    title: "3. Técnicas de Análisis Regional (Matrices SII, Qij, Base Exportadora y MADE)",
    core: "<b>Idea central:</b> A partir de matrices Sector × Comuna (t<sub>0</sub> y t<sub>f</sub>), Q<sub>ij</sub> &gt; 1 identifica vocación exportadora; Q<sub>r</sub> mide especialización y CR<sub>r</sub> reestructuración; Tiebout estima el excedente exportable X<sub>j</sub> y su multiplicador M<sub>j</sub> = V<sub>j</sub>/X<sub>j</sub>; Silva Lira clasifica territorios en 4 cuadrantes (Dinámica, Emergente, Estancada, En retroceso); y Shift &amp; Share separa Efecto Estructural (EE) de Efecto Diferencial (ED).",
    bridge: "<b>Puente inter-unidades:</b> Las comunas del Cuadrante II de Silva Lira (Emergentes: bajo nivel inicial y alto crecimiento) son el motor empírico de la Convergencia Beta (U3). El ED<sub>j</sub> &gt; 0 suele correlacionarse con clústeres activos (U4).",
    trap: "<b>Trampas de control:</b> (1) Q<sub>r</sub> y CR<sub>r</sub> siempre van entre 0 y 1 (multiplicando por 1/2 para no contar doble). (2) En MADE Clásico existen 6 tipologías de Boisier, mientras que en MADE Modificado (EM<sub>j</sub> = EI<sub>j</sub> − EE<sub>j</sub>; ERM<sub>j</sub> = ET<sub>j</sub> − EI<sub>j</sub>) existen 14 tipologías de Stilwell (1969)."
  },
  {
    unit: "U3", src: "Motor REAT · Figueroa & Herrero (2003) · CASEN",
    title: "4. Disparidades, Convergencia (σ y β), Desigualdad (Gini/Theil) y Markov",
    core: "<b>Idea central:</b> Convergencia Beta ocurre cuando territorios pobres crecen más rápido (β &lt; 0 en OLS); Convergencia Sigma cuando cae la dispersión transversal (σ<sub>t</sub> &lt; σ<sub>0</sub>). Gini mide desigualdad global desde la Curva de Lorenz; Theil mide entropía y se descompone aditivamente; HHI y Hannah-Kay (HK<sub>α</sub>) miden concentración; Markov proyecta la distribución ergódica de largo plazo.",
    bridge: "<b>Puente inter-unidades:</b> Responde si los polos (U1) y la reestructuración sectorial (U2) cerraron o abrieron las brechas territoriales, dando la línea base cuantitativa para justificar intervenciones OT (U5).",
    trap: "<b>Trampas de control:</b> (1) La Convergencia Beta es condición <i>necesaria pero NO suficiente</i> para que exista Convergencia Sigma (choques aleatorios pueden mantener alta la dispersión σ). (2) Para analizar desigualdad 'entre regiones' vs. 'dentro de regiones' se usa Theil, no Gini. (3) En Base1 (n=7), β es negativo pero con p=0,420 no es estadísticamente significativo al 5%."
  },
  {
    unit: "U4", src: "04 SPL.pdf (Dini 2010) · Granovetter · Padilla & Oddone · Boisier",
    title: "5. Redes Empresariales, Clúster, SPL, Cadenas de Valor y Sistema ELITE",
    core: "<b>Idea central:</b> Dini (2010) ordena la articulación en 3 círculos concéntricos: Red Empresarial (cooperación voluntaria entre pares) ⊂ Clúster (masa crítica sectorial localizada) ⊂ SPL (actores productivos + instituciones del territorio). Granovetter destaca los vínculos débiles para traer innovación; Padilla &amp; Oddone plantean Upgrading (proceso, producto, funcional); Boisier (ELITE) evalúa poder e interacción institucional.",
    bridge: "<b>Puente inter-unidades:</b> Es la dimensión institucional y microeconómica que transforma una aglomeración pasiva (U1) en competitividad genuina (ED<sub>j</sub> &gt; 0 en U2), como los casos PymeMad Biobío y Red Láctea Osorno.",
    trap: "<b>Trampas de control (Control 4):</b> (1) En matrices UCINET la diagonal principal es siempre 0 (A<sub>ii</sub> = 0); en red no dirigida D = 2L/[n(n−1)] y en dirigida D = L/[n(n−1)]. (2) Entrevista obligatoria a 3 personas de organizaciones distintas cubriendo mínimo 2 eslabones (1 gremio + 2 empresas). (3) Regla de oro del Prof. Mancilla: NO sugerir que debe existir un clúster ni usar la palabra 'debilidades' (preguntar por desafíos o aspectos por fortalecer)."
  },
  {
    unit: "U5", src: "06 OT 2024.pdf · Unidad 5 OT · PROT SUBDERE-CEPAL (2011)",
    title: "6. Ordenamiento Territorial: Primacía IP4, Guttman/Rondinelli, Aislamiento y PROT",
    core: "<b>Idea central:</b> El Ordenamiento Territorial diagnostica la red de asentamientos con Primacía Urbana (IP<sub>4</sub> = P<sub>1</sub>/[P<sub>2</sub>+P<sub>3</sub>+P<sub>4</sub>] en escala 0–3), jerarquía funcional con Escalograma de Guttman / Rondinelli (peso inverso W<sub>k</sub> = 100/f<sub>k</sub>) y conectividad vial con Matriz de Aislamiento (0 = asfalto directo, 1 = sin conexión directa). El PROT articula 4 sistemas: Costero, Urbano, Rural y Cuencas.",
    bridge: "<b>Puente inter-unidades:</b> Cierra el ciclo del ramo: conecta la densidad de servicios de Christaller (U1) y la concentración poblacional/económica (U3) con instrumentos públicos reales (PROT, PLADECO, LGUC, Ley 19.175 LOCGAR).",
    trap: "<b>Trampas de control (Control 5):</b> (1) En la Escala de Guttman (Top 10 comunas más pobladas y mínimo 7 variables), las variables DEBEN discriminar entre comunas: si todas tienen 1, debes reemplazar la variable. (2) En Rondinelli, mientras más escaso es un equipamiento (menor frecuencia f<sub>k</sub>), MAYOR peso de centralidad W<sub>k</sub> aporta. (3) En Matriz de Aislamiento, 0 es bueno (conectada directamente) y 1 indica aislamiento."
  },
  {
    unit: "U6", src: "Unidad VI — Indicadores de Desarrollo (ejemplo.xlsx · 15 Provincias)",
    title: "7. Indicadores Sintéticos de Desarrollo: Normalización Mínimo–Máximo y Ponderaciones",
    core: "<b>Idea central:</b> Para combinar variables en distintas unidades (pesos, tasas, puntajes) se normaliza cada una al rango <b>[0, 1]</b>. Si la variable es <b>favorable (+)</b> (más es mejor, ej. ingresos, escolaridad), se usa <b>(x − mín)/(máx − mín)</b>; si es <b>desfavorable (−)</b> (menos es mejor, ej. pobreza, desempleo, aislamiento), se invierte con <b>(máx − x)/(máx − mín)</b>. Luego se pondera linealmente: I = ∑ w<sub>k</sub>·u<sub>k</sub>.",
    bridge: "<b>Puente inter-unidades:</b> Cierra todo el curso integrando resultados de crecimiento (U.I), disparidades (U.III) y equipamiento/aislamiento (U.V) en un único ranking territorial comparable.",
    trap: "<b>Trampas de prueba (Unidad VI):</b> (1) Aunque la mejor comuna siempre obtiene <b>1</b> en cada variable individual, en el <b>índice compuesto</b> solo obtiene 1,00 si es líder simultáneo en <i>todas</i> las variables. (2) <b>Efecto Outlier:</b> si una comuna extrema salta a 3.000, sigue sacando 1,00, pero <i>aplasta hacia 0</i> los puntajes de todas las comunas intermedias. (3) En Excel, <code>RANK(celda, rango, 0)</code> da lugar 1 al mayor valor (orden descendente); usar <code>1</code> invierte el ranking."
  }
];

let capaLecturaActiva = "core";
let filtroLecturaUnit = "all";

function setCapaLectura(capa) {
  capaLecturaActiva = capa;
  ["core", "bridge", "trap", "all"].forEach(k => {
    const b = document.getElementById("cap-btn-" + k);
    if (b) b.classList.toggle("primary", k === capa);
  });
  renderLecturaCards();
}
function filtrarLectura(unit, btn) {
  filtroLecturaUnit = unit;
  btn.parentElement.querySelectorAll(".flt-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  renderLecturaCards();
}
function renderLecturaCards() {
  const grid = document.getElementById("lec-cards-grid");
  if (!grid) return;
  grid.innerHTML = "";
  FICHAS_LECTURA.filter(f => filtroLecturaUnit === "all" || f.unit === filtroLecturaUnit).forEach(f => {
    const card = document.createElement("div");
    card.className = "lec-card";
    let layersHtml = "";
    if (capaLecturaActiva === "core" || capaLecturaActiva === "all") layersHtml += `<div class="lec-layer l-core">${f.core}</div>`;
    if (capaLecturaActiva === "bridge" || capaLecturaActiva === "all") layersHtml += `<div class="lec-layer l-bridge">${f.bridge}</div>`;
    if (capaLecturaActiva === "trap" || capaLecturaActiva === "all") layersHtml += `<div class="lec-layer l-trap">${f.trap}</div>`;
    card.innerHTML = `
      <div class="lec-meta"><span class="lec-unit">${f.unit}</span><span class="lec-src">${f.src}</span></div>
      <div class="lec-title">${f.title}</div>
      ${layersHtml}`;
    grid.appendChild(card);
  });
}

const QUIZ_LECTURA_DATA = [
  {
    tag: "U1 ↔ U5",
    q: "Si una mejora vial reduce el costo de transporte τ por debajo del umbral crítico τ* en el modelo de Krugman (1991), ¿qué tendencia cabría esperar en el Índice de Primacía (IP4) y en la Curva de Lorenz?",
    opts: ["Disminuyen IP4 y Gini (dispersión automática)", "Aumentan IP4 y Gini (mayor aglomeración en el centro)", "No cambia la distribución espacial"],
    ans: 1,
    why: "Al caer τ ≤ τ* predominan las fuerzas centrípetas (economías de escala + mercado local), concentrando producción y población en la capital regional, lo que eleva IP4 y aleja la Curva de Lorenz de la diagonal (Duch Brown / Krugman 1991)."
  },
  {
    tag: "U1 Weber",
    q: "Una planta procesadora de madera aserrada o leche en polvo tiene un Índice de Materiales IM = 1,85 y existe un enclave laboral barato L fuera de su Isodápana Crítica. ¿Dónde debe ubicarse?",
    opts: ["Cerca de las materias primas en P* (no salta a L)", "En el enclave laboral L para ahorrar salarios", "Pegada al mercado consumidor porque IM > 1"],
    ans: 0,
    why: "Como IM > 1 (pérdida de peso en el proceso), P* se orienta a los insumos. Como L queda FUERA de la Isodápana Crítica, el sobrecosto de transporte hacia L supera el ahorro salarial, por lo que permanece en P* (Duch Brown, Sec. 1.2)."
  },
  {
    tag: "U2 ↔ U3",
    q: "Una comuna ubicada en el Cuadrante II de Silva Lira (Emergente: bajo PIB per cápita inicial y tasa de crecimiento superior al promedio regional) aporta evidencia en favor de:",
    opts: ["Divergencia absoluta (β > 0)", "Macrocefalia urbana (IP4 ≥ 1,50)", "Convergencia Beta (β < 0)"],
    ans: 2,
    why: "La Convergencia Beta ocurre precisamente cuando las economías que parten rezagadas (bajo nivel inicial) crecen proporcionalmente más rápido que el promedio, cerrando la brecha (Silva Lira 2005 / Motor REAT)."
  },
  {
    tag: "U3 REAT",
    q: "Verdadero o Falso: Si en una regresión transversal regional encontramos Convergencia Beta estadísticamente significativa (β < 0), eso garantiza automáticamente que exista Convergencia Sigma (σ_t < σ_0).",
    opts: ["Verdadero", "Falso"],
    ans: 1,
    why: "Falso: En econometría regional (REAT / Barro y Sala-i-Martin), la Convergencia Beta es condición necesaria pero NO suficiente para Convergencia Sigma, ya que choques aleatorios pueden sostener o ampliar la dispersión transversal."
  },
  {
    tag: "U3 Desigualdad",
    q: "Si el GORE necesita descomponer exactamente cuánto de la desigualdad total de ingresos se explica 'entre provincias' y cuánto 'dentro de cada provincia', ¿qué indicador debe elegir?",
    opts: ["Índice de Gini estándar (G)", "Índice de Primacía IP2", "Índice de Entropía de Theil (T)"],
    ans: 2,
    why: "La principal ventaja analítica de la Entropía de Theil frente al Gini es su perfecta descomponibilidad aditiva en componente inter-grupal (entre territorios) e intra-grupal (dentro de cada territorio)."
  },
  {
    tag: "U4 Dini / Granovetter",
    q: "Un clúster local tiene 100% de vínculos fuertes internos entre sus 6 PyMEs, pero cero vínculos débiles con universidades, centros I+D o compradores externos. Según Granovetter (1973), ¿cuál es su principal riesgo?",
    opts: ["Exceso de competencia desleal por baja cohesión", "Bloqueo cognitivo (lock-in) por información redundante", "Pérdida inmediata de densidad D = 0%"],
    ans: 1,
    why: "Sin vínculos débiles externos que operen como puentes hacia nueva tecnología y mercados, las redes altamente endogámicas caen en bloqueo cognitivo (lock-in) y repiten información redundante."
  },
  {
    tag: "U4 Control 4",
    q: "En el protocolo de entrevistas del Taller de Redes y Cadenas de Valor (Control 4, Prof. Mancilla), ¿cuál de estas prácticas es INCORRECTA?",
    opts: ["Entrevistar a 3 actores de organizaciones distintas cubriendo mínimo 2 eslabones (1 gremio + 2 empresas)", "Preguntar por 'desafíos' o 'aspectos por fortalecer' y validar el esquema de la cadena", "Sugerir al entrevistado que debe existir un clúster y preguntarle por sus 'debilidades'"],
    ans: 2,
    why: "Regla explícita de cátedra ('Unidad 5. Redes y Cadena de Valor.dcx.pdf'): no se debe inducir la existencia de un clúster ni usar la palabra 'debilidades', sino consultar por desafíos o aspectos por fortalecer."
  },
  {
    tag: "U4 Dini 2010",
    q: "En una red no dirigida de n = 6 empresas con L = 5 vínculos todos conectados a una única empresa ancla (estrella), ¿qué valores toman la Densidad (D) y el Gradiente de Concentración (GC)?",
    opts: ["D = 33,3% y GC = 100% (Red con Liderazgo)", "D = 100% y GC = 0% (Red Simétrica)", "D = 50,0% y GC = 50% (Red Jerárquica)"],
    ans: 0,
    why: "D = 2L/[n(n−1)] = 10/30 = 33,3%. Como el líder tiene k_max = 5 y las otras 5 empresas tienen k_i = 1, ∑(5−k_i) = 20 y (n−1)(n−2) = 5×4 = 20 ⇒ GC = 20/20 = 100% (04 SPL.pdf, pág. 14)."
  },
  {
    tag: "U5 Guttman / Rondinelli",
    q: "Al construir tu Escala de Guttman / Matriz de Rondinelli para las 10 comunas más pobladas, notas que la variable 'Escuela Básica' tiene valor 1 en las 10 comunas. ¿Qué debes hacer según la pauta de cátedra?",
    opts: ["Mantenerla porque otorga el mayor peso Wk = 100/f_k", "Reemplazar esa variable por un equipamiento que sí discrimine entre comunas", "Asignarle peso 0 pero dejarla como indicador principal de jerarquía"],
    ans: 1,
    why: "En el Escalograma de Guttman ('06 OT 2024.pdf' / Control 5), las variables elegidas deben discriminar jerárquicamente entre comunas; si todas tienen valor 1 no aporta diferenciación y debe reemplazarse."
  },
  {
    tag: "U5 Aislamiento",
    q: "En la Matriz de Aislamiento Comunal del Control 5 (0 = conexión directa asfaltada; 1 = sin conexión directa), una comuna con Índice de Aislamiento = 22% frente a otra con 78% indica que:",
    opts: ["La primera está más aislada porque tiene menos unos", "Ambas tienen el mismo nivel de centralidad funcional", "La primera está mejor conectada (es un nodo más accesible en la red vial)"],
    ans: 2,
    why: "Como el valor 0 marca conexión directa y el 1 marca ausencia de conexión directa, un menor porcentaje de 1s refleja mayor accesibilidad y menor aislamiento territorial."
  },
  {
    tag: "U.VI Mín-Máx",
    q: "En la normalización Mínimo–Máximo [0, 1] de una variable de sentido DESFAVORABLE (ej. tasa de pobreza comunal o índice de aislamiento), ¿qué fórmula corresponde y qué valor obtiene la mejor comuna (la de menor pobreza)?",
    opts: ["(x − mín)/(máx − mín) y la mejor comuna obtiene 0,00", "(máx − x)/(máx − mín) y la mejor comuna obtiene 1,00", "(x / máx) y la mejor comuna obtiene el promedio regional"],
    ans: 1,
    why: "Cuando una variable es desfavorable (menos es mejor), se invierte con u−(x) = (máx − x)/(máx − mín) para que la comuna con menor pobreza/aislamiento reciba el puntaje máximo 1,00 y la peor reciba 0,00."
  },
  {
    tag: "U.VI Outlier",
    q: "Si en una planilla de 15 provincias la mejor provincia en v1 aumenta repentinamente de 1.000 a 3.000 mientras las demás 14 no cambian, ¿qué ocurre con los valores normalizados Mín–Máx?",
    opts: ["La líder sigue obteniendo 1,00 y la mínima 0,00, pero todas las provincias intermedias se comprimen (caen) hacia 0", "Todas las provincias mantienen exactamente el mismo valor normalizado entre 0 y 1", "La líder pasa a obtener 3,00 porque superó la escala original"],
    ans: 0,
    why: "La normalización Mín–Máx siempre acota los extremos a 0 y 1 sin importar la unidad, pero es muy sensible a valores atípicos (outliers): al agrandar el denominador (máx − mín), comprime hacia cero a todos los territorios intermedios."
  }
];

let qzAnswers = {};
let qzSoloPend = false;

function toggleSoloErradasQz(btn) {
  qzSoloPend = !qzSoloPend;
  btn.classList.toggle("primary", qzSoloPend);
  renderQuizLectura();
}
function responderQuizLectura(idx, optIdx) {
  qzAnswers[idx] = optIdx;
  renderQuizLectura();
}
function resetQuizLectura() {
  qzAnswers = {};
  qzSoloPend = false;
  renderQuizLectura();
}
function renderQuizLectura() {
  const wrap = document.getElementById("qz-list");
  if (!wrap) return;
  wrap.innerHTML = "";
  let okCount = 0;
  QUIZ_LECTURA_DATA.forEach((item, idx) => {
    const uAns = qzAnswers[idx];
    const isAns = uAns !== undefined;
    const isOk = isAns && uAns === item.ans;
    if (isOk) okCount++;
    if (qzSoloPend && isOk) return;

    const card = document.createElement("div");
    card.className = "qz-card" + (isAns ? (" answered " + (isOk ? "ok" : "bad")) : "");
    const btns = item.opts.map((op, oi) =>
      `<button class="qz-btn ${uAns === oi ? "sel" : ""}" onclick="responderQuizLectura(${idx}, ${oi})">${op}</button>`
    ).join("");
    const badgeRes = isAns ? `<span style="font-size:11.5px;font-weight:800;color:${isOk ? "#15803D" : "#DC2626"};">${isOk ? "✓ Correcto" : "✗ Revisar"}</span>` : "";
    card.innerHTML = `
      <div><span class="qz-tag">${item.tag}</span> <span style="font-size:11px;color:#475569;font-weight:700;">Pregunta ${idx + 1}</span></div>
      <div class="qz-q">${item.q}</div>
      <div class="qz-opts">${btns}${badgeRes}</div>
      <div class="qz-fb"><b>Fundamento teórico de cátedra:</b> ${item.why}</div>`;
    wrap.appendChild(card);
  });
  document.getElementById("qz-score").textContent = `Aciertos: ${okCount} / ${QUIZ_LECTURA_DATA.length}`;
}


// ============================================================================
// 7B. UNIDAD VI: INDICADORES DE DESARROLLO (MÍN-MÁX, SENTIDO, PESOS Y OUTLIER)
// ============================================================================
const U6_DATA_BASE = [
  { prov: "Arica",       v1: 0.3043503653, v2: 0.4252707581 },
  { prov: "Iquique",     v1: 0.8951429388, v2: 0.4328626035 },
  { prov: "Antofagasta", v1: 1.0000000000, v2: 0.6211934593 },
  { prov: "Copiapó",     v1: 0.6789344969, v2: 0.3804735613 },
  { prov: "Huasco",      v1: 0.3755450406, v2: 0.4764599703 },
  { prov: "Elqui",       v1: 0.4062766788, v2: 0.6139732427 },
  { prov: "Choapa",      v1: 0.2302111177, v2: 0.4122106604 },
  { prov: "Limarí",      v1: 0.2164904672, v2: 0.4434805691 },
  { prov: "Valparaíso",  v1: 0.6833221403, v2: 0.8345083882 },
  { prov: "Los Andes",   v1: 0.2465828124, v2: 0.2325865364 },
  { prov: "Petorca",     v1: 0.0838059083, v2: 0.1162136335 },
  { prov: "Quillota",    v1: 0.2825429064, v2: 0.1541834784 },
  { prov: "San Antonio", v1: 0.2681639109, v2: 0.1978020811 },
  { prov: "San Felipe",  v1: 0.1117198411, v2: 0.1905500106 },
  { prov: "Marga_Marga", v1: 0.4764931727, v2: 0.6271182841 }
];
let u6DataLive = U6_DATA_BASE.map(d => ({ ...d }));
let u6Dir1 = 1, u6Dir2 = 1;
let u6SelIdx = 2; // Antofagasta por defecto

function initProvEditorU6() {
  const sel = document.getElementById("u6-prov-sel");
  if (!sel || sel.options.length > 0) return;
  u6DataLive.forEach((d, i) => {
    const opt = document.createElement("option");
    opt.value = i;
    opt.textContent = `${i + 1}. ${d.prov.replace("_", " ")}`;
    sel.appendChild(opt);
  });
  sel.value = u6SelIdx;
  loadProvEditorU6();
}
function loadProvEditorU6() {
  const sel = document.getElementById("u6-prov-sel");
  if (!sel) return;
  u6SelIdx = parseInt(sel.value, 10) || 0;
  document.getElementById("u6-ed-v1").value = Number(u6DataLive[u6SelIdx].v1.toFixed(4));
  document.getElementById("u6-ed-v2").value = Number(u6DataLive[u6SelIdx].v2.toFixed(4));
  drawIndicadoresU6();
}
function applyProvEditU6() {
  const v1 = parseFloat(document.getElementById("u6-ed-v1").value);
  const v2 = parseFloat(document.getElementById("u6-ed-v2").value);
  if (Number.isFinite(v1)) u6DataLive[u6SelIdx].v1 = v1;
  if (Number.isFinite(v2)) u6DataLive[u6SelIdx].v2 = v2;
  drawIndicadoresU6();
}
function resetU6Data() {
  u6DataLive = U6_DATA_BASE.map(d => ({ ...d }));
  document.getElementById("u6-out").value = 1.0;
  loadProvEditorU6();
}

function setSentidoU6(which, dir) {
  if (which === 1) {
    u6Dir1 = dir;
    document.getElementById("u6-s1-pos").classList.toggle("primary", dir === 1);
    document.getElementById("u6-s1-neg").classList.toggle("primary", dir === -1);
  } else {
    u6Dir2 = dir;
    document.getElementById("u6-s2-pos").classList.toggle("primary", dir === 1);
    document.getElementById("u6-s2-neg").classList.toggle("primary", dir === -1);
  }
  drawIndicadoresU6();
}
function presetU6(mode) {
  if (mode === "base50") {
    document.getElementById("u6-w1").value = 50;
    document.getElementById("u6-out").value = 1.0;
    setSentidoU6(1, 1); setSentidoU6(2, 1);
  } else if (mode === "base70") {
    document.getElementById("u6-w1").value = 70;
    document.getElementById("u6-out").value = 1.0;
    setSentidoU6(1, 1); setSentidoU6(2, 1);
  } else if (mode === "inv_v2") {
    document.getElementById("u6-w1").value = 50;
    document.getElementById("u6-out").value = 1.0;
    setSentidoU6(1, 1); setSentidoU6(2, -1);
  } else if (mode === "outlier3000") {
    document.getElementById("u6-w1").value = 50;
    document.getElementById("u6-out").value = 4.0;
    setSentidoU6(1, 1); setSentidoU6(2, 1);
  }
  drawIndicadoresU6();
}
function computeU6Rows(w1Frac, dir1, dir2, outMult, useBase = false) {
  const srcArr = useBase ? U6_DATA_BASE : u6DataLive;
  const raw = srcArr.map((d, i) => ({
    prov: d.prov,
    v1: i === 2 ? d.v1 * outMult : d.v1,
    v2: d.v2
  }));
  const v1s = raw.map(r => r.v1), v2s = raw.map(r => r.v2);
  const min1 = Math.min(...v1s), max1 = Math.max(...v1s);
  const min2 = Math.min(...v2s), max2 = Math.max(...v2s);
  const rng1 = Math.max(1e-9, max1 - min1), rng2 = Math.max(1e-9, max2 - min2);
  const w2Frac = 1 - w1Frac;
  const rows = raw.map(r => {
    const u1 = dir1 === 1 ? (r.v1 - min1) / rng1 : (max1 - r.v1) / rng1;
    const u2 = dir2 === 1 ? (r.v2 - min2) / rng2 : (max2 - r.v2) / rng2;
    return { ...r, u1, u2, idx: w1Frac * u1 + w2Frac * u2 };
  });
  const sorted = [...rows].sort((a, b) => b.idx - a.idx);
  rows.forEach(r => { r.rank = sorted.findIndex(x => x.prov === r.prov) + 1; });
  return { rows, min1, max1, min2, max2 };
}
function drawIndicadoresU6() {
  const w1Pct = +document.getElementById("u6-w1").value;
  const outMult = +document.getElementById("u6-out").value;
  document.getElementById("u6-w1-v").textContent = `${w1Pct}% / ${100 - w1Pct}%`;
  document.getElementById("u6-s1-v").textContent = u6Dir1 === 1 ? "Favorable (+)" : "Desfavorable (−)";
  document.getElementById("u6-s2-v").textContent = u6Dir2 === 1 ? "Favorable (+)" : "Desfavorable (−)";
  document.getElementById("u6-out-v").textContent = outMult <= 1.01 ? "1,0x (Original)" : `${fmtDec(outMult, 2)}x (Outlier)`;

  initProvEditorU6();
  const base = computeU6Rows(0.5, 1, 1, 1.0, true);
  const cur = computeU6Rows(w1Pct / 100, u6Dir1, u6Dir2, outMult, false);
  const baseRankMap = {};
  base.rows.forEach(r => { baseRankMap[r.prov] = r.rank; });

  const ordered = [...cur.rows].sort((a, b) => a.rank - b.rank);
  const top = ordered[0], bot = ordered[ordered.length - 1];
  const avgIdx = cur.rows.reduce((s, r) => s + r.idx, 0) / cur.rows.length;
  const chgCount = cur.rows.filter(r => r.rank !== baseRankMap[r.prov]).length;

  document.getElementById("u6-enunciado").innerHTML =
    `Con las 15 provincias de <b>ejemplo.xlsx</b> (Arica a Marga Marga), cada variable se lleva a <b>[0, 1]</b> usando Mín–Máx ` +
    `(v1: <b>${u6Dir1 === 1 ? "Favorable +" : "Desfavorable −"}</b>, rango [${fmtDec(cur.min1,3)}; ${fmtDec(cur.max1,3)}] | ` +
    `v2: <b>${u6Dir2 === 1 ? "Favorable +" : "Desfavorable −"}</b>, rango [${fmtDec(cur.min2,3)}; ${fmtDec(cur.max2,3)}]) y se pondera <b>${w1Pct}% v1 + ${100 - w1Pct}% v2</b>. ` +
    `<b>Nota de auditoría:</b> en el Excel original la columna <code>RANK</code> dejó fuera a Marga_Marga (rango <code>$F$11:$F$24</code> → <code>#N/A</code>) y ordenó ascendente (1); aquí se corrige sobre las <b>15 provincias en orden descendente (#1 = mejor)</b>.`;

  document.getElementById("u6-k-top").textContent = top.prov.replace("_", " ");
  document.getElementById("u6-k-topv").textContent = `Índice = ${fmtDec(top.idx, 3)} (u1=${fmtDec(top.u1,2)}, u2=${fmtDec(top.u2,2)})`;
  document.getElementById("u6-k-bot").textContent = bot.prov.replace("_", " ");
  document.getElementById("u6-k-botv").textContent = `Índice = ${fmtDec(bot.idx, 3)}`;
  document.getElementById("u6-k-avg").textContent = fmtDec(avgIdx, 3);
  document.getElementById("u6-k-avg2").textContent = outMult > 1.05 ? `Bajó desde 0,393 por compresión outlier` : `Promedio de las 15 provincias`;
  document.getElementById("u6-k-chg").textContent = `${chgCount} provincias`;
  document.getElementById("u6-k-chg2").textContent = chgCount === 0 ? "Idéntico al ranking 50/50" : "Cambiaron de puesto vs. 50/50";

  // Gráfico horizontal estilo pizarra (Top #1 a #15)
  const svg = document.getElementById("svg-u6");
  if (svg) {
    svg.innerHTML = "";
    addDefs(svg);
    const M = { l: 102, r: 44, t: 32, b: 36 }, W = 560, H = 440;
    const sx = v => M.l + v * (W - M.l - M.r);
    const rowH = (H - M.t - M.b) / ordered.length;
    const tHd = el("text", { x: (M.l + W - M.r) / 2, y: 18, fill: "#0F172A", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
    tHd.textContent = `Ranking Compuesto (${w1Pct}/${100 - w1Pct}) — Escala [0, 1]`;

    for (const gx of [0, 0.25, 0.5, 0.75, 1.0]) {
      el("line", { x1: sx(gx), y1: M.t, x2: sx(gx), y2: H - M.b, stroke: gx === 0 ? "#334155" : "#E2E8F0", "stroke-width": gx === 0 ? "1.5" : "1" }, svg);
      const tx = el("text", { x: sx(gx), y: H - M.b + 16, fill: "#475569", "font-size": "10.5", "font-weight": "700", "text-anchor": "middle" }, svg);
      tx.textContent = fmtDec(gx, 2);
    }
    ordered.forEach((r, i) => {
      const y0 = M.t + i * rowH + 3, bh = Math.max(8, rowH - 6);
      const col = i === 0 ? "#15803D" : (i === ordered.length - 1 ? "#DC2626" : "#1D4ED8");
      const wBar = Math.max(2, sx(r.idx) - sx(0));
      el("rect", { x: M.l, y: y0, width: wBar, height: bh, fill: col, rx: 3, opacity: "0.86" }, svg);
      // Desglose interno del aporte w1*u1 (barra más oscura al inicio)
      const wPart1 = sx((w1Pct / 100) * r.u1) - sx(0);
      if (wPart1 > 2) el("rect", { x: M.l, y: y0, width: wPart1, height: bh, fill: "#0F172A", opacity: "0.20", rx: 2 }, svg);
      const tl = el("text", { x: M.l - 6, y: y0 + bh * 0.72, fill: "#0F172A", "font-size": "10.3", "font-weight": "700", "text-anchor": "end" }, svg);
      tl.textContent = `#${r.rank} ${r.prov.replace("_", " ")}`;
      const tv = el("text", { x: M.l + wBar + 5, y: y0 + bh * 0.72, fill: col, "font-size": "10", "font-weight": "800", "text-anchor": "start" }, svg);
      tv.textContent = fmtDec(r.idx, 3);
    });
  }

  // Tabla comparada de las 15 provincias
  let tbl = `<table class="u6-tbl"><thead><tr><th>Provincia</th><th>u(v1)</th><th>u(v2)</th><th>Índice</th><th>#Rk</th><th>Δ vs 50/50</th></tr></thead><tbody>`;
  ordered.forEach(r => {
    const diff = baseRankMap[r.prov] - r.rank;
    const dCls = diff > 0 ? "u6-rk-up" : (diff < 0 ? "u6-rk-dn" : "u6-rk-eq");
    const dTxt = diff > 0 ? `↑ +${diff}` : (diff < 0 ? `↓ ${diff}` : "—");
    const rowCls = r.rank === 1 ? "u6-top" : (r.rank === 15 ? "u6-bot" : "");
    tbl += `<tr class="${rowCls}"><td>${r.prov.replace("_"," ")}</td><td>${fmtDec(r.u1,3)}</td><td>${fmtDec(r.u2,3)}</td><td><b>${fmtDec(r.idx,3)}</b></td><td><b>#${r.rank}</b></td><td class="${dCls}">${dTxt}</td></tr>`;
  });
  tbl += `</tbody></table>`;
  document.getElementById("u6-tbl-box").innerHTML = tbl;

  const selRow = cur.rows[u6SelIdx] || top;
  const selNm = selRow.prov.replace("_", " ");
  const num1Val = u6Dir1 === 1 ? (selRow.v1 - cur.min1) : (cur.max1 - selRow.v1);
  const num2Val = u6Dir2 === 1 ? (selRow.v2 - cur.min2) : (cur.max2 - selRow.v2);
  renderFormulaStrip("u6-fstrip", [
    {
      lbl: `Normalización v1 — ${selNm} (${u6Dir1 === 1 ? "+" : "−"})`, col: "#1D4ED8",
      eq: u6Dir1 === 1 ? `u<sub>1</sub> = ${mFrac('<span class="sym-b">x<sub>i</sub></span> − <span class="sym-o">mín</span>', '<span class="sym-t">máx</span> − <span class="sym-o">mín</span>')}` : `u<sub>1</sub> = ${mFrac('<span class="sym-t">máx</span> − <span class="sym-b">x<sub>i</sub></span>', '<span class="sym-t">máx</span> − <span class="sym-o">mín</span>')}`,
      sub: u6Dir1 === 1
        ? `u<sub>1</sub> = ${mFrac(eChip(fmtDec(selRow.v1,2),Number(selRow.v1.toFixed(4)),"u6_v1","0.05","vc-b","v1 de "+selNm) + " − " + vChip(fmtDec(cur.min1,2),"vc-o","Mínimo v1"), vChip(fmtDec(cur.max1,2),"vc-t","Máximo v1") + " − " + vChip(fmtDec(cur.min1,2),"vc-o","Mínimo v1"))} = ${mFrac(fmtDec(num1Val,2), fmtDec(cur.max1-cur.min1,2))} = ${rChip(fmtDec(selRow.u1,3))}`
        : `u<sub>1</sub> = ${mFrac(vChip(fmtDec(cur.max1,2),"vc-t","Máximo v1") + " − " + eChip(fmtDec(selRow.v1,2),Number(selRow.v1.toFixed(4)),"u6_v1","0.05","vc-b","v1 de "+selNm), vChip(fmtDec(cur.max1,2),"vc-t","Máximo v1") + " − " + vChip(fmtDec(cur.min1,2),"vc-o","Mínimo v1"))} = ${mFrac(fmtDec(num1Val,2), fmtDec(cur.max1-cur.min1,2))} = ${rChip(fmtDec(selRow.u1,3))}`,
      note: `Sentido ${u6Dir1 === 1 ? "Favorable (+)" : "Desfavorable (−)"} · Clic en x_i para escribir (ej. 3000)`
    },
    {
      lbl: `Normalización v2 — ${selNm} (${u6Dir2 === 1 ? "+" : "−"})`, col: "#059669",
      eq: u6Dir2 === 1 ? `u<sub>2</sub> = ${mFrac('<span class="sym-b">x<sub>i</sub></span> − <span class="sym-o">mín</span>', '<span class="sym-t">máx</span> − <span class="sym-o">mín</span>')}` : `u<sub>2</sub> = ${mFrac('<span class="sym-t">máx</span> − <span class="sym-b">x<sub>i</sub></span>', '<span class="sym-t">máx</span> − <span class="sym-o">mín</span>')}`,
      sub: u6Dir2 === 1
        ? `u<sub>2</sub> = ${mFrac(eChip(fmtDec(selRow.v2,2),Number(selRow.v2.toFixed(4)),"u6_v2","0.05","vc-b","v2 de "+selNm) + " − " + vChip(fmtDec(cur.min2,2),"vc-o","Mínimo v2"), vChip(fmtDec(cur.max2,2),"vc-t","Máximo v2") + " − " + vChip(fmtDec(cur.min2,2),"vc-o","Mínimo v2"))} = ${mFrac(fmtDec(num2Val,2), fmtDec(cur.max2-cur.min2,2))} = ${rChip(fmtDec(selRow.u2,3))}`
        : `u<sub>2</sub> = ${mFrac(vChip(fmtDec(cur.max2,2),"vc-t","Máximo v2") + " − " + eChip(fmtDec(selRow.v2,2),Number(selRow.v2.toFixed(4)),"u6_v2","0.05","vc-b","v2 de "+selNm), vChip(fmtDec(cur.max2,2),"vc-t","Máximo v2") + " − " + vChip(fmtDec(cur.min2,2),"vc-o","Mínimo v2"))} = ${mFrac(fmtDec(num2Val,2), fmtDec(cur.max2-cur.min2,2))} = ${rChip(fmtDec(selRow.u2,3))}`,
      note: `Sentido ${u6Dir2 === 1 ? "Favorable (+)" : "Desfavorable (−)"} · Clic en x_i para escribir`
    },
    {
      lbl: `Índice Compuesto (${w1Pct}/${100 - w1Pct}) — ${selNm}`, col: "#7C3AED",
      eq: `I<sub>i</sub> = <span class="sym-p">w<sub>1</sub></span>·<span class="sym-b">u<sub>1</sub></span> + <span class="sym-o">w<sub>2</sub></span>·<span class="sym-t">u<sub>2</sub></span>`,
      sub: `I = ${eChip(fmtDec(w1Pct/100,2),Number((w1Pct/100).toFixed(2)),"u6_w1","0.05","vc-p","Peso w1 (ej. 0.7 o 70)")}·${vChip(fmtDec(selRow.u1,3),"vc-b","u1")} + ${eChip(fmtDec((100-w1Pct)/100,2),Number(((100-w1Pct)/100).toFixed(2)),"u6_w2","0.05","vc-o","Peso w2 (ej. 0.3 o 30)")}·${vChip(fmtDec(selRow.u2,3),"vc-t","u2")} = ${rChip(fmtDec(selRow.idx,3)+" (#"+selRow.rank+")")}`,
      note: `Clic en w1 o w2 para cambiar la ponderación directo aquí`
    }
  ]);

  document.getElementById("u6-sol").innerHTML =
    `<b>Fórmulas aplicadas:</b> u(v1) = ${u6Dir1 === 1 ? "(v1 − mín)/(máx − mín)" : "(máx − v1)/(máx − mín)"} | ` +
    `u(v2) = ${u6Dir2 === 1 ? "(v2 − mín)/(máx − mín)" : "(máx − v2)/(máx − mín)"} | ` +
    `<b>Índice</b> = ${fmtDec(w1Pct/100,2)}·u(v1) + ${fmtDec((100-w1Pct)/100,2)}·u(v2) &nbsp;⇒&nbsp; Líder: <b>${top.prov.replace("_"," ")} (${fmtDec(top.idx,3)})</b>`;

  renderPedBox("ped-u6",
    `Con ponderación <b>${w1Pct}/${100-w1Pct}</b>, <b>${top.prov.replace("_"," ")}</b> ocupa el <b>#1 (${fmtDec(top.idx,3)})</b> y <b>${bot.prov.replace("_"," ")}</b> el <b>#15 (${fmtDec(bot.idx,3)})</b>. Nota que ${top.idx < 0.999 ? `la mejor provincia NO llega a 1,000 exacto porque no es líder en ambas variables a la vez` : `al ser líder en las dos dimensiones simultáneamente sí alcanza el 1,000 perfecto`}.`,
    `<b>¿Da igual poner 200 y 3.000? (La Paradoja del Outlier):</b> sí, la transformación Mín–Máx siempre deja en <b>1,00</b> al mejor y en <b>0,00</b> al peor sin importar la escala. <b>Pero cuidado:</b> mueve el slider de <i>Shock Outlier</i> hacia 4,0x y verás cómo el promedio del país se desploma (de 0,393 hacia ~0,29) porque un extremo gigantesco aplasta hacia 0 a todas las comunas intermedias.`,
    `En pruebas de Unidad VI (Indicadores de Desarrollo): (1) justifica siempre el <b>sentido (+) o (−)</b> de cada indicador antes de normalizar; (2) demuestra con dos ponderaciones (ej. 50/50 vs. 70/30) si el ranking es robusto o sensible (aquí <b>Copiapó, Elqui, Marga Marga, Los Andes y San Antonio</b> cambian de lugar); y (3) verifica en Excel que <code>RANK</code> use todo el rango y el argumento <code>0</code> (descendente).`
  );
}


// ============================================================================
// 7A. UNIDAD V: LABORATORIO ORDENAMIENTO TERRITORIAL A 60 FPS (FLECHAS, RONDINELLI, AISLAMIENTO)
// ============================================================================
let otSubActive = "rk";

function openOtSub(subKey, btn) {
  otSubActive = subKey;
  document.querySelectorAll("#panel-ot .ot-subpanel").forEach(p => p.classList.remove("active"));
  document.querySelectorAll("#panel-ot .ot-sub-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("ot-sub-" + subKey).classList.add("active");
  if (btn) btn.classList.add("active");
  drawOtActive();
}
function drawOtActive() {
  if (otSubActive === "rk") drawOtRanking();
  else if (otSubActive === "rd") drawOtRond();
  else if (otSubActive === "ai") drawOtAisl();
  else if (otSubActive === "prot") { drawOtSistemasSvg(); renderOtAnexo2(); renderOtQuiz(); }
}

// --- A. RANKING DE ASENTAMIENTOS (FLECHAS CRUZADAS) Y PRIMACÍA 2 CENSOS ---
const OT_RK_PRESETS = {
  mancilla: {
    titulo: "Ejemplo Cátedra (Lám. 10: Censo 1990 → Censo 2000)",
    c1Lbl: "Censo 1990",
    c2Lbl: "Censo 2000",
    rows: [
      { nm: "La Esperanza",   p1: 5100, p2: 5520 },
      { nm: "El Rincón",      p1: 4200, p2: 4541 },
      { nm: "Pueblo Nuevo",   p1: 1850, p2: 1920 },
      { nm: "El Quebradero",  p1: 1620, p2: 2180 },
      { nm: "Valle Hermoso",  p1: 1380, p2: 1120 },
      { nm: "Ipiales",        p1: 1190, p2: 1510 },
      { nm: "El Trancón",     p1: 980,  p2: 1340 },
      { nm: "Mojandas",       p1: 740,  p2: 810 }
    ]
  },
  biobio: {
    titulo: "Región del Biobío (Top 10 Comunas — Censos 2017 → 2024)",
    c1Lbl: "Censo 2017",
    c2Lbl: "Censo 2024",
    rows: [
      { nm: "Concepción",          p1: 223574, p2: 230375 },
      { nm: "Los Ángeles",         p1: 202331, p2: 219441 },
      { nm: "Talcahuano",          p1: 151749, p2: 147322 },
      { nm: "San Pedro de la Paz", p1: 131808, p2: 150992 },
      { nm: "Coronel",             p1: 116262, p2: 123648 },
      { nm: "Hualpén",             p1: 91773,  p2: 87731  },
      { nm: "Chiguayante",         p1: 85938,  p2: 85822  },
      { nm: "Tomé",                p1: 54946,  p2: 56907  },
      { nm: "Penco",               p1: 47367,  p2: 48971  },
      { nm: "Lota",                p1: 43535,  p2: 39980  }
    ]
  },
  lagos: {
    titulo: "Región de Los Lagos (Top 10 Comunas — Censos 2017 → 2024)",
    c1Lbl: "Censo 2017",
    c2Lbl: "Censo 2024",
    rows: [
      { nm: "Puerto Montt", p1: 245902, p2: 275473 },
      { nm: "Osorno",       p1: 161460, p2: 174998 },
      { nm: "Puerto Varas", p1: 44578,  p2: 50010  },
      { nm: "Castro",       p1: 43807,  p2: 48632  },
      { nm: "Ancud",        p1: 38991,  p2: 42158  },
      { nm: "Calbuco",      p1: 33985,  p2: 37620  },
      { nm: "Quellón",      p1: 27192,  p2: 30910  },
      { nm: "Purranque",    p1: 20369,  p2: 21475  },
      { nm: "Frutillar",    p1: 18428,  p2: 21220  },
      { nm: "Llanquihue",   p1: 17591,  p2: 19380  }
    ]
  },
  araucania: {
    titulo: "Región de La Araucanía (Top 10 Comunas — Censos 2017 → 2024)",
    c1Lbl: "Censo 2017",
    c2Lbl: "Censo 2024",
    rows: [
      { nm: "Temuco",          p1: 282415, p2: 304820 },
      { nm: "Padre Las Casas", p1: 76126,  p2: 83540  },
      { nm: "Villarrica",      p1: 55478,  p2: 63910  },
      { nm: "Angol",           p1: 53262,  p2: 56840  },
      { nm: "Lautaro",         p1: 38013,  p2: 40890  },
      { nm: "Victoria",        p1: 34182,  p2: 36120  },
      { nm: "Nueva Imperial",  p1: 32510,  p2: 34620  },
      { nm: "Pucón",           p1: 28523,  p2: 34950  },
      { nm: "Vilcún",          p1: 28151,  p2: 30480  },
      { nm: "Pitrufquén",      p1: 24837,  p2: 26410  }
    ]
  }
};

let otRkKey = "mancilla";
let otRkRows = OT_RK_PRESETS.mancilla.rows.map(r => ({ ...r }));
let otRkC1Lbl = OT_RK_PRESETS.mancilla.c1Lbl;
let otRkC2Lbl = OT_RK_PRESETS.mancilla.c2Lbl;
let otRkAnimU = 1.0;
let otRkAnimId = null;
let otRkHoverIdx = -1;

function presetOtRanking(key) {
  if (otRkAnimId) cancelAnimationFrame(otRkAnimId);
  const pr = OT_RK_PRESETS[key] || OT_RK_PRESETS.mancilla;
  otRkKey = key;
  otRkRows = pr.rows.map(r => ({ ...r }));
  otRkC1Lbl = pr.c1Lbl;
  otRkC2Lbl = pr.c2Lbl;
  otRkAnimU = 1.0;
  otRkHoverIdx = -1;
  renderOtRkTable();
  drawOtRanking();
}
function shockOtRanking() {
  if (otRkAnimId) cancelAnimationFrame(otRkAnimId);
  const idxMid = Math.min(otRkRows.length - 1, Math.max(2, Math.floor(otRkRows.length / 2)));
  otRkRows[idxMid].p2 = Math.round(otRkRows[idxMid].p2 * 1.55);
  otRkAnimU = 1.0;
  renderOtRkTable();
  drawOtRanking();
}
function animarOtRanking() {
  if (otRkAnimId) cancelAnimationFrame(otRkAnimId);
  const t0 = performance.now(), dur = 1650;
  function step(now) {
    const u = Math.min(1, (now - t0) / dur);
    otRkAnimU = 1 - Math.pow(1 - u, 3);
    drawOtRanking();
    if (u < 1) otRkAnimId = requestAnimationFrame(step);
  }
  otRkAnimId = requestAnimationFrame(step);
}
function updateOtRkCell(idx, field, rawVal) {
  const v = parseFloat(rawVal);
  if (!Number.isFinite(v) || v < 1) return;
  otRkRows[idx][field] = Math.round(v);
  otRkAnimU = 1.0;
  drawOtRanking();
}
function renderOtRkTable() {
  const box = document.getElementById("ot-rk-tbl-box");
  if (!box) return;
  let html = `<table class="ot-mat-tbl"><thead><tr><th>Asentamiento</th><th>${otRkC1Lbl}</th><th>${otRkC2Lbl}</th><th>Orden</th></tr></thead><tbody>`;
  otRkRows.forEach((r, i) => {
    html += `<tr onmouseenter="otRkHoverIdx=${i};drawOtRanking();" onmouseleave="otRkHoverIdx=-1;drawOtRanking();">` +
      `<td>${r.nm}</td>` +
      `<td><input class="ot-num-in" type="number" min="1" step="100" value="${r.p1}" oninput="updateOtRkCell(${i},'p1',this.value)"/></td>` +
      `<td><input class="ot-num-in" type="number" min="1" step="100" value="${r.p2}" oninput="updateOtRkCell(${i},'p2',this.value)"/></td>` +
      `<td id="ot-rk-ord-${i}" style="font-weight:800;">—</td>` +
      `</tr>`;
  });
  html += `</tbody></table>`;
  box.innerHTML = html;
}
function calcOtPrimacia(vals) {
  const d = [...vals].sort((a, b) => b - a);
  const p1 = d[0] || 1;
  const p2 = d[1] || 1;
  const sum234 = (d[1] || 0) + (d[2] || 0) + (d[3] || 0);
  const ip4 = sum234 > 0 ? p1 / sum234 : 0;
  const ip2 = p2 > 0 ? p1 / p2 : 0;
  let cat = "Muy Dispersa", cod = 0;
  if (ip4 >= 1.50) { cat = "Altamente Concentrada"; cod = 3; }
  else if (ip4 >= 1.00) { cat = "Concentrada"; cod = 2; }
  else if (ip4 >= 0.65) { cat = "Dispersa"; cod = 1; }
  return { d, ip4, ip2, sum234, cat, cod };
}
function drawOtRanking() {
  if (!document.getElementById("ot-rk-tbl-box").innerHTML) renderOtRkTable();
  const n = otRkRows.length;
  const idx1 = otRkRows.map((r, i) => ({ i, v: r.p1 })).sort((a, b) => b.v - a.v);
  const idx2 = otRkRows.map((r, i) => ({ i, v: r.p2 })).sort((a, b) => b.v - a.v);
  const rank1 = new Array(n), rank2 = new Array(n);
  idx1.forEach((o, pos) => { rank1[o.i] = pos + 1; });
  idx2.forEach((o, pos) => { rank2[o.i] = pos + 1; });

  let nUp = 0, nDn = 0, nEq = 0, maxMove = 0, topMoverNm = "Sin cambios", topMoveDelta = 0;
  otRkRows.forEach((r, i) => {
    const chg = rank1[i] - rank2[i];
    if (chg > 0) nUp++;
    else if (chg < 0) nDn++;
    else nEq++;
    if (Math.abs(chg) > maxMove) { maxMove = Math.abs(chg); topMoverNm = r.nm; topMoveDelta = chg; }
    const td = document.getElementById("ot-rk-ord-" + i);
    if (td) {
      const col = chg > 0 ? "#15803D" : (chg < 0 ? "#DC2626" : "#64748B");
      const sym = chg > 0 ? "↗" : (chg < 0 ? "↘" : "→");
      td.innerHTML = `<span style="color:${col};">${rank1[i]} ${sym} ${rank2[i]}</span>`;
    }
  });

  const pr1 = calcOtPrimacia(otRkRows.map(r => r.p1));
  const pr2 = calcOtPrimacia(otRkRows.map(r => r.p2));
  const dIp = pr2.ip4 - pr1.ip4;

  document.getElementById("ot-rk-enun").innerHTML =
    `<b>${OT_RK_PRESETS[otRkKey].titulo}:</b> el diagrama ordena las <b>${n} localidades</b> de mayor a menor población en <b>${otRkC1Lbl}</b> (izquierda) ` +
    `y en <b>${otRkC2Lbl}</b> (derecha). Las flechas <b>verdes (↗)</b> marcan ascensos jerárquicos, las <b>rojas (↘)</b> descensos y las <b>grises (→)</b> estabilidad. ` +
    `Simultáneamente se evalúa si la primacía urbana (<b>IP<sub>4</sub></b>) aumentó o se desconcentró entre ambos censos.`;

  document.getElementById("ot-rk-k-ip4").textContent = `${fmtDec(pr1.ip4, 2)} → ${fmtDec(pr2.ip4, 2)}`;
  document.getElementById("ot-rk-k-dip4").textContent = `ΔIP4: ${dIp >= 0 ? "+" : "-"}${fmtDec(Math.abs(dIp), 3)}`;
  document.getElementById("ot-rk-k-cat").textContent = `Valor ${pr2.cod}: ${pr2.cat}`;
  document.getElementById("ot-rk-k-ip2").textContent = `IP2 (P1/P2) = ${fmtDec(pr2.ip2, 2)}`;
  document.getElementById("ot-rk-k-mov").textContent = `${nUp} suben · ${nDn} bajan`;
  document.getElementById("ot-rk-k-eq").textContent = `${nEq} mantienen puesto`;
  document.getElementById("ot-rk-k-top").textContent = maxMove > 0 ? `${topMoverNm} (${topMoveDelta > 0 ? "+" : ""}${topMoveDelta})` : "Sin cruces";
  document.getElementById("ot-rk-k-top2").textContent = maxMove > 0 ? "Mayor salto en la jerarquía" : "Jerarquía idéntica entre censos";

  renderFormulaStrip("ot-rk-fstrip", [
    {
      lbl: `Primacía IP4 — ${otRkC1Lbl}`, col: "#475569",
      eq: `IP<sub>4</sub>(t<sub>0</sub>) = ${mFrac('<span class="sym-b">P<sub>1</sub></span>', '<span class="sym-t">P<sub>2</sub></span> + <span class="sym-p">P<sub>3</sub></span> + <span class="sym-o">P<sub>4</sub></span>')}`,
      sub: `IP<sub>4</sub> = ${mFrac(vChip(fmtInt(pr1.d[0]),"vc-b"), vChip(fmtInt(pr1.d[1]),"vc-t") + " + " + vChip(fmtInt(pr1.d[2]),"vc-p") + " + " + vChip(fmtInt(pr1.d[3]),"vc-o"))} = ${rChip(fmtDec(pr1.ip4,3))}`,
      note: `Clasificación ${otRkC1Lbl}: Valor ${pr1.cod} (${pr1.cat})`
    },
    {
      lbl: `Primacía IP4 — ${otRkC2Lbl}`, col: "#1D4ED8",
      eq: `IP<sub>4</sub>(t<sub>1</sub>) = ${mFrac('<span class="sym-b">P<sub>1</sub></span>', '<span class="sym-t">P<sub>2</sub></span> + <span class="sym-p">P<sub>3</sub></span> + <span class="sym-o">P<sub>4</sub></span>')}`,
      sub: `IP<sub>4</sub> = ${mFrac(vChip(fmtInt(pr2.d[0]),"vc-b"), vChip(fmtInt(pr2.d[1]),"vc-t") + " + " + vChip(fmtInt(pr2.d[2]),"vc-p") + " + " + vChip(fmtInt(pr2.d[3]),"vc-o"))} = ${rChip(fmtDec(pr2.ip4,3), pr2.ip4 >= 1.5)}`,
      note: `Clasificación ${otRkC2Lbl}: Valor ${pr2.cod} (${pr2.cat})`
    },
    {
      lbl: "Dinámica Intercensal (ΔIP4 y Cruces)", col: dIp > 0.02 ? "#DC2626" : "#15803D",
      eq: `ΔIP<sub>4</sub> = IP<sub>4</sub>(t<sub>1</sub>) − IP<sub>4</sub>(t<sub>0</sub>)`,
      sub: `ΔIP<sub>4</sub> = ${vChip(fmtDec(pr2.ip4,3),"vc-b")} − ${vChip(fmtDec(pr1.ip4,3),"vc-o")} = ${rChip((dIp>=0?"+":"-")+fmtDec(Math.abs(dIp),3), dIp > 0.02)}`,
      note: dIp > 0.02 ? "Tendencia a mayor concentración en la capital" : (dIp < -0.02 ? "Tendencia a desconcentración en ciudades intermedias" : "Estructura urbana estable entre censos")
    }
  ]);

  // Dibujar Diagrama SVG de Flechas Cruzadas (estilo lámina 10)
  const svg = document.getElementById("svg-ot-flechas");
  if (!svg) return;
  svg.innerHTML = "";
  addDefs(svg);

  const W = 600, H = 415;
  const xLBox = 18, wBox = 178, xLNum = xLBox + wBox + 14;
  const xRBox = W - 18 - wBox, xRNum = xRBox - 14;
  const yTop = 52, yBot = H - 24;
  const stepY = (yBot - yTop) / Math.max(1, n - 1);
  const yOfRank = rk => yTop + (rk - 1) * stepY;

  // Títulos de columnas
  const hdL = el("text", { x: xLBox + wBox / 2, y: 24, fill: "#0F172A", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  hdL.textContent = `Orden ${otRkC1Lbl}`;
  const hdM = el("text", { x: W / 2, y: 24, fill: "#1E3A8A", "font-size": "11.2", "font-weight": "800", "text-anchor": "middle" }, svg);
  hdM.textContent = "Flechas de Cambio Jerárquico";
  const hdR = el("text", { x: xRBox + wBox / 2, y: 24, fill: "#0F172A", "font-size": "12", "font-weight": "800", "text-anchor": "middle" }, svg);
  hdR.textContent = `Orden ${otRkC2Lbl}`;

  el("line", { x1: xLBox, y1: 33, x2: W - 18, y2: 33, stroke: "#CBD5E1", "stroke-width": "1.2" }, svg);

  // Flechas cruzadas primero (debajo de badges)
  otRkRows.forEach((r, i) => {
    const r1 = rank1[i], r2 = rank2[i];
    const chg = r1 - r2;
    const y1 = yOfRank(r1);
    const y2Target = yOfRank(r2);
    const y2 = y1 + (y2Target - y1) * otRkAnimU;
    const x1 = xLNum + 14;
    const x2End = xRNum - 14;
    const x2 = x1 + (x2End - x1) * Math.max(0.08, otRkAnimU);

    const isHov = (otRkHoverIdx === i);
    const dimOther = (otRkHoverIdx >= 0 && !isHov);
    const col = chg > 0 ? "#15803D" : (chg < 0 ? "#DC2626" : "#64748B");
    const mk = chg > 0 ? "arr-green" : (chg < 0 ? "arr-red" : "arr-dark");

    el("line", {
      x1, y1, x2, y2,
      stroke: col,
      "stroke-width": isHov ? "3.6" : (chg !== 0 ? "2.4" : "1.7"),
      "stroke-dasharray": chg === 0 ? "4,3" : "",
      opacity: dimOther ? "0.22" : "0.95",
      "marker-end": `url(#${mk})`
    }, svg);

    if (chg !== 0 && otRkAnimU > 0.75) {
      const xm = (x1 + x2End) / 2 + (chg > 0 ? -18 : 18);
      const ym = (y1 + y2Target) / 2 - 4;
      if (isHov || Math.abs(chg) >= 1) {
        drawPill(svg, xm, ym, `${chg > 0 ? "↑+" : "↓"}${chg}`, col, "#FFFFFF", "middle", "9.3");
      }
    }
  });

  // Cajas izquierda (Censo 1) y derecha (Censo 2)
  idx1.forEach((o, pos) => {
    const i = o.i, r = otRkRows[i], rk = pos + 1;
    const y = yOfRank(rk);
    const chg = rank1[i] - rank2[i];
    const isHov = (otRkHoverIdx === i);
    const bg = isHov ? "#EFF6FF" : "#F8FAFC";
    const strokeC = isHov ? "#1D4ED8" : "#CBD5E1";
    const g = el("g", { style: "cursor:pointer;", onmouseenter: `otRkHoverIdx=${i};drawOtRanking();`, onmouseleave: `otRkHoverIdx=-1;drawOtRanking();` }, svg);
    el("rect", { x: xLBox, y: y - 13, width: wBox, height: 26, rx: 5, fill: bg, stroke: strokeC, "stroke-width": isHov ? "1.8" : "1" }, g);
    const tNm = el("text", { x: xLBox + 8, y: y + 4, fill: "#0F172A", "font-size": "10.6", "font-weight": "700" }, g);
    tNm.textContent = r.nm.length > 18 ? r.nm.slice(0, 17) + "…" : r.nm;
    const tPb = el("text", { x: xLBox + wBox - 6, y: y + 4, fill: "#475569", "font-size": "9.6", "font-weight": "600", "text-anchor": "end" }, g);
    tPb.textContent = fmtInt(r.p1);
    el("circle", { cx: xLNum, cy: y, r: 10.5, fill: chg > 0 ? "#15803D" : (chg < 0 ? "#DC2626" : "#334155") }, g);
    const tR = el("text", { x: xLNum, y: y + 3.5, fill: "#FFFFFF", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, g);
    tR.textContent = rk;
  });

  idx2.forEach((o, pos) => {
    const i = o.i, r = otRkRows[i], rk = pos + 1;
    const y = yOfRank(rk);
    const chg = rank1[i] - rank2[i];
    const isHov = (otRkHoverIdx === i);
    const bg = isHov ? "#EFF6FF" : (chg > 0 ? "#F0FDF4" : (chg < 0 ? "#FEF2F2" : "#F8FAFC"));
    const strokeC = isHov ? "#1D4ED8" : (chg > 0 ? "#86EFAC" : (chg < 0 ? "#FCA5A5" : "#CBD5E1"));
    const g = el("g", { style: "cursor:pointer;", onmouseenter: `otRkHoverIdx=${i};drawOtRanking();`, onmouseleave: `otRkHoverIdx=-1;drawOtRanking();` }, svg);
    el("circle", { cx: xRNum, cy: y, r: 10.5, fill: chg > 0 ? "#15803D" : (chg < 0 ? "#DC2626" : "#334155") }, g);
    const tR = el("text", { x: xRNum, y: y + 3.5, fill: "#FFFFFF", "font-size": "10.5", "font-weight": "800", "text-anchor": "middle" }, g);
    tR.textContent = rk;
    el("rect", { x: xRBox, y: y - 13, width: wBox, height: 26, rx: 5, fill: bg, stroke: strokeC, "stroke-width": isHov ? "1.8" : "1" }, g);
    const tNm = el("text", { x: xRBox + 8, y: y + 4, fill: "#0F172A", "font-size": "10.6", "font-weight": "700" }, g);
    tNm.textContent = r.nm.length > 18 ? r.nm.slice(0, 17) + "…" : r.nm;
    const tPb = el("text", { x: xRBox + wBox - 6, y: y + 4, fill: "#475569", "font-size": "9.6", "font-weight": "600", "text-anchor": "end" }, g);
    tPb.textContent = fmtInt(r.p2);
  });

  renderPedBox("ped-ot-rk",
    `Entre <b>${otRkC1Lbl}</b> y <b>${otRkC2Lbl}</b> se registran <b>${nUp} ascensos</b> y <b>${nDn} descensos</b> en el ordenamiento poblacional. El Índice de Primacía pasó de <b>${fmtDec(pr1.ip4,3)}</b> a <b>${fmtDec(pr2.ip4,3)}</b> (<b>Valor ${pr2.cod}: ${pr2.cat}</b>).`,
    `<b>Por qué las flechas se cruzan aunque nadie pierda población:</b> una localidad puede crecer en habitantes y aun así bajar de puesto (flecha roja ↘) si su vecina creció mucho más rápido por migración residencial, turismo o nuevas fuentes laborales (como ocurrió en Biobío con San Pedro de la Paz superando a Talcahuano).`,
    `En evaluación de OT (06 OT 2024, láms. 10–11): el <b>Ranking de Asentamientos</b> detecta migraciones y reordenamientos internos de la red urbana, mientras el <b>Índice de Primacía (IP<sub>4</sub>)</b> cuantifica si el sistema regional tiende a la macrocefalia o al equilibrio policéntrico.`
  );
}

// --- B. ESCALA DE GUTTMAN Y MATRIZ DE RONDINELLI (1/0 CLICABLE + GRÁFICO) ---
const OT_RD_PRESETS = {
  ejemplo: {
    titulo: "Ejemplo Excel de Cátedra (Flores, Melchor de Mencos, San Ignacio y Benque Viejo)",
    cols: ["Educ. Divers.", "Universid.", "C. Médica", "Seg. Social", "Guarderías", "Vivienda", "At. Mujer"],
    rows: [
      { nm: "Flores (GT)",               pob: 51535, v: [1, 1, 1, 1, 1, 1, 1] },
      { nm: "Melchor de Mencos (GT)",    pob: 19847, v: [1, 1, 1, 1, 1, 0, 1] },
      { nm: "San Ignacio/Sta. Elena",    pob: 16977, v: [1, 1, 1, 1, 0, 1, 1] },
      { nm: "Benque Viejo (BZE)",        pob: 5824,  v: [0, 0, 1, 1, 0, 1, 1] }
    ]
  },
  lagos: {
    titulo: "Región de Los Lagos (Top 10 — Servicios a la Producción)",
    cols: ["OTEC", "+1 Banco", "Of. Fomento", "Asist. Téc.", "Reclutam.", "C. Negocios", "Lab. Cert.", "Gremio Reg."],
    rows: [
      { nm: "Puerto Montt", pob: 275473, v: [1, 1, 1, 1, 1, 1, 1, 1] },
      { nm: "Osorno",       pob: 174998, v: [1, 1, 1, 1, 1, 1, 1, 1] },
      { nm: "Puerto Varas", pob: 50010,  v: [1, 1, 1, 1, 1, 1, 1, 0] },
      { nm: "Castro",       pob: 48632,  v: [1, 1, 1, 1, 0, 1, 1, 0] },
      { nm: "Ancud",        pob: 42158,  v: [1, 1, 1, 1, 0, 0, 0, 0] },
      { nm: "Calbuco",      pob: 37620,  v: [1, 0, 1, 0, 0, 0, 1, 0] },
      { nm: "Quellón",      pob: 30910,  v: [1, 1, 1, 0, 0, 0, 1, 0] },
      { nm: "Purranque",    pob: 21475,  v: [1, 0, 1, 1, 0, 0, 0, 0] },
      { nm: "Frutillar",    pob: 21220,  v: [1, 1, 1, 0, 0, 0, 0, 0] },
      { nm: "Llanquihue",   pob: 19380,  v: [0, 0, 0, 0, 0, 0, 1, 0] }
    ]
  },
  biobio: {
    titulo: "Región del Biobío (Top 10 — Servicios a la Producción)",
    cols: ["OTEC", "+1 Banco", "Of. Fomento", "Asist. Téc.", "Reclutam.", "C. Negocios", "Lab. Cert.", "Gremio Reg."],
    rows: [
      { nm: "Concepción",          pob: 230375, v: [1, 1, 1, 1, 1, 1, 1, 1] },
      { nm: "Los Ángeles",         pob: 219441, v: [1, 1, 1, 1, 1, 1, 1, 1] },
      { nm: "San Pedro de la Paz", pob: 150992, v: [1, 1, 1, 1, 1, 1, 1, 0] },
      { nm: "Talcahuano",          pob: 147322, v: [1, 1, 1, 1, 0, 1, 1, 0] },
      { nm: "Coronel",             pob: 123648, v: [1, 1, 1, 1, 0, 0, 0, 0] },
      { nm: "Hualpén",             pob: 87731,  v: [1, 0, 1, 0, 0, 0, 1, 0] },
      { nm: "Chiguayante",         pob: 85822,  v: [1, 1, 1, 0, 0, 0, 1, 0] },
      { nm: "Tomé",                pob: 56907,  v: [1, 0, 1, 1, 0, 0, 0, 0] },
      { nm: "Penco",               pob: 48971,  v: [1, 1, 1, 0, 0, 0, 0, 0] },
      { nm: "Lota",                pob: 39980,  v: [0, 0, 0, 0, 0, 0, 1, 0] }
    ]
  }
};

let otRdKey = "ejemplo";
let otRdCols = [...OT_RD_PRESETS.ejemplo.cols];
let otRdRows = OT_RD_PRESETS.ejemplo.rows.map(r => ({ nm: r.nm, pob: r.pob, v: [...r.v] }));
let otRdShowWeights = false;

function presetOtRond(key) {
  const pr = OT_RD_PRESETS[key] || OT_RD_PRESETS.ejemplo;
  otRdKey = key;
  otRdCols = [...pr.cols];
  otRdRows = pr.rows.map(r => ({ nm: r.nm, pob: r.pob, v: [...r.v] }));
  drawOtRond();
}
function toggleOtRondCell(ri, ci) {
  otRdRows[ri].v[ci] = otRdRows[ri].v[ci] === 1 ? 0 : 1;
  drawOtRond();
}
function toggleOtRondMode() {
  otRdShowWeights = !otRdShowWeights;
  const btn = document.getElementById("ot-rd-btn-mode");
  if (btn) {
    btn.classList.toggle("primary", otRdShowWeights);
    btn.textContent = otRdShowWeights ? "Ver Matriz Binaria (1 / 0)" : "Ver Matriz Ponderada (Wk)";
  }
  drawOtRond();
}
function testOtRondError() {
  otRdRows.forEach(r => { r.v[0] = 1; });
  drawOtRond();
}
function drawOtRond() {
  const n = otRdRows.length, m = otRdCols.length;
  const totPob = otRdRows.reduce((s, r) => s + r.pob, 0) || 1;
  const fk = new Array(m).fill(0);
  otRdRows.forEach(r => r.v.forEach((x, j) => { fk[j] += x; }));
  const wk = fk.map(f => f > 0 ? 100 / f : 0);

  const scores = otRdRows.map(r => {
    let sumF = 0, ic = 0;
    r.v.forEach((x, j) => { sumF += x; ic += x * wk[j]; });
    return { nm: r.nm, pob: r.pob, sumF, ic };
  });
  const totIC = scores.reduce((s, o) => s + o.ic, 0);
  const activeCols = fk.filter(f => f > 0).length;
  const badCols = [];
  for (let j = 0; j < m; j++) {
    if (fk[j] === 0 || fk[j] === n) badCols.push(otRdCols[j]);
  }
  const best = [...scores].sort((a, b) => b.ic - a.ic)[0];
  let rarIdx = 0, maxW = -1;
  wk.forEach((w, j) => { if (w > maxW) { maxW = w; rarIdx = j; } });

  // Detectar anomalías jerárquicas (ciudad menos poblada con mayor IC que una más poblada)
  const anomalies = [];
  for (let i = 1; i < n; i++) {
    if (scores[i].ic > scores[i - 1].ic + 0.01) anomalies.push(scores[i].nm);
  }

  document.getElementById("ot-rd-enun").innerHTML =
    `<b>${OT_RD_PRESETS[otRdKey].titulo}:</b> las localidades están ordenadas de mayor a menor población. ` +
    `Cada servicio presente suma un peso inverso <b>W<sub>k</sub> = 100 / f<sub>k</sub></b>: mientras menos comunas tienen el servicio, mayor puntaje aporta. ` +
    `Modo actual: <b>${otRdShowWeights ? "Matriz Ponderada (Wk)" : "Matriz Binaria (1 / 0)"}</b>.`;

  document.getElementById("ot-rd-k-top").textContent = best.nm;
  document.getElementById("ot-rd-k-topv").textContent = `${fmtDec(best.ic, 2)} pts (${best.sumF}/${m} servicios)`;
  document.getElementById("ot-rd-k-rar").textContent = otRdCols[rarIdx];
  document.getElementById("ot-rd-k-rarv").textContent = `fk = ${fk[rarIdx]} → Wk = ${fmtDec(wk[rarIdx], 2)}`;
  document.getElementById("ot-rd-k-val").textContent = badCols.length === 0 ? `${m} / ${m} discriminan` : `${badCols.length} sin discriminar`;
  document.getElementById("ot-rd-k-val2").textContent = badCols.length === 0 ? "Cumple regla de cátedra" : "Tienen puros 1 o puros 0";
  document.getElementById("ot-rd-k-sum").textContent = `${fmtDec(totIC, 2)} pts`;
  document.getElementById("ot-rd-k-sum2").textContent = `100 × ${activeCols} servicios activos`;

  const alertBox = document.getElementById("ot-rd-alert");
  if (badCols.length > 0) {
    alertBox.innerHTML = `<div class="ot-banner-warn">Regla de cátedra (Unidad 5 OT): las columnas <b>${badCols.join(", ")}</b> tienen puros 1 o puros 0 y no diferencian entre comunas. Haz clic en alguna celda para discriminar o reemplaza esa variable.</div>`;
  } else {
    alertBox.innerHTML = `<div class="ot-banner-ok">Validación OK: las ${m} variables discriminan efectivamente entre las ${n} localidades.${anomalies.length ? " Anomalía jerárquica detectada en: <b>" + anomalies.join(", ") + "</b> (supera en servicios a una ciudad más poblada)." : ""}</div>`;
  }

  renderFormulaStrip("ot-rd-fstrip", [
    {
      lbl: `Peso Inverso — ${otRdCols[rarIdx]}`, col: "#1D4ED8",
      eq: `W<sub>k</sub> = ${mFrac("100", '<span class="sym-r">f<sub>k</sub></span>')}`,
      sub: `W<sub>${rarIdx + 1}</sub> = ${mFrac("100", vChip(fk[rarIdx], "vc-r", "Localidades con el servicio"))} = ${rChip(fmtDec(wk[rarIdx], 2) + " pts")}`,
      note: "Servicio más escaso = mayor peso en el índice"
    },
    {
      lbl: `Índice Funcional — ${best.nm}`, col: "#15803D",
      eq: `IC<sub>i</sub> = ∑ <span class="sym-b">X<sub>ik</sub></span> · <span class="sym-p">W<sub>k</sub></span>`,
      sub: `IC = ${vChip(best.sumF + " serv.", "vc-b")} ponderados = ${rChip(fmtDec(best.ic, 2) + " pts")}`,
      note: `Cuota poblacional: ${fmtDec((best.pob / totPob) * 100, 1)}%`
    },
    {
      lbl: "Propiedad de Verificación Total", col: "#0F172A",
      eq: `∑ IC<sub>i</sub> = 100 · <span class="sym-t">m<sub>activos</sub></span>`,
      sub: `∑ IC<sub>i</sub> = 100 · ${vChip(activeCols, "vc-t")} = ${rChip(fmtDec(totIC, 2))}`,
      note: "Cada servicio activo reparte exactamente 100 puntos"
    }
  ]);

  // Tabla interactiva clicable
  let tbl = `<table class="ot-mat-tbl"><thead><tr><th>Localidad</th><th>Pob.</th><th>% Pob</th>`;
  otRdCols.forEach(c => { tbl += `<th>${c}</th>`; });
  tbl += `<th>Suma</th><th>Índice IC</th></tr></thead><tbody>`;

  otRdRows.forEach((r, ri) => {
    tbl += `<tr><td>${r.nm}</td><td style="text-align:right;">${fmtInt(r.pob)}</td><td style="text-align:right;">${fmtDec((r.pob / totPob) * 100, 1)}%</td>`;
    r.v.forEach((x, ci) => {
      const lbl = otRdShowWeights ? (x === 1 ? fmtDec(wk[ci], 1) : "0") : String(x);
      const cls = x === 1 ? "ot-c1" : "ot-c0";
      const wStyle = otRdShowWeights ? "width:42px;font-size:10px;" : "";
      tbl += `<td><button class="ot-cell-btn ${cls}" style="${wStyle}" onclick="toggleOtRondCell(${ri},${ci})" title="Clic para alternar 1 / 0">${lbl}</button></td>`;
    });
    tbl += `<td style="font-weight:800;">${scores[ri].sumF}</td><td style="font-weight:800;color:#1E3A8A;text-align:right;">${fmtDec(scores[ri].ic, 2)}</td></tr>`;
  });

  tbl += `<tr class="ot-sum-row"><td>Frecuencia (fk)</td><td style="text-align:right;">${fmtInt(totPob)}</td><td style="text-align:right;">100%</td>`;
  fk.forEach(f => { tbl += `<td>${f}</td>`; });
  tbl += `<td>${scores.reduce((s, o) => s + o.sumF, 0)}</td><td style="text-align:right;">${fmtDec(totIC, 2)}</td></tr>`;

  tbl += `<tr class="ot-wt-row"><td>Ponderación (100/fk)</td><td>—</td><td>—</td>`;
  wk.forEach(w => { tbl += `<td>${fmtDec(w, 2)}</td>`; });
  tbl += `<td>—</td><td>—</td></tr>`;

  tbl += `<tr class="ot-val-row"><td>Discriminación</td><td>—</td><td>—</td>`;
  fk.forEach(f => {
    const ok = f > 0 && f < n;
    tbl += `<td class="${ok ? "ot-badge-ok" : "ot-badge-bad"}">${ok ? "OK" : "Cambiar"}</td>`;
  });
  tbl += `<td>—</td><td>—</td></tr></tbody></table>`;
  document.getElementById("ot-rd-tbl-box").innerHTML = tbl;

  // SVG Gráfico Complejidad Funcional vs. Población (lámina 15)
  const svg = document.getElementById("svg-ot-rond");
  if (!svg) return;
  svg.innerHTML = "";
  addDefs(svg);
  const M = { l: 64, r: 44, t: 30, b: 46 }, W = 980, H = 345;
  const maxP = Math.max(...scores.map(s => s.pob), 1000) * 1.12;
  const maxIC = Math.max(...scores.map(s => s.ic), 50) * 1.18;
  const sx = p => M.l + (p / maxP) * (W - M.l - M.r);
  const sy = ic => H - M.b - (ic / maxIC) * (H - M.t - M.b);

  for (let k = 0; k <= 4; k++) {
    const yv = (maxIC / 4) * k;
    el("line", { x1: M.l, y1: sy(yv), x2: W - M.r, y2: sy(yv), stroke: "#E2E8F0" }, svg);
    const ty = el("text", { x: M.l - 8, y: sy(yv) + 4, fill: "#475569", "font-size": "10.8", "text-anchor": "end" }, svg);
    ty.textContent = fmtDec(yv, 0);
  }
  for (let k = 0; k <= 4; k++) {
    const xv = (maxP / 4) * k;
    el("line", { x1: sx(xv), y1: M.t, x2: sx(xv), y2: H - M.b, stroke: "#F1F5F9" }, svg);
    const tx = el("text", { x: sx(xv), y: H - M.b + 16, fill: "#475569", "font-size": "10.8", "text-anchor": "middle" }, svg);
    tx.textContent = fmtInt(xv);
  }
  drawAxesPizarra(svg, M.l, M.t, W - M.r, H - M.b, "Índice de Complejidad Funcional (Rondinelli)", "Población del Asentamiento (Habitantes)");

  const ptsLine = scores.map(s => `${sx(s.pob).toFixed(1)},${sy(s.ic).toFixed(1)}`).join(" ");
  el("polyline", { points: ptsLine, fill: "none", stroke: "#1D4ED8", "stroke-width": "2.2", "stroke-dasharray": "5,4" }, svg);

  scores.forEach((s, i) => {
    const isAnom = i > 0 && s.ic > scores[i - 1].ic + 0.01;
    const cx = sx(s.pob), cy = sy(s.ic);
    el("circle", { cx, cy, r: isAnom ? 7.5 : 6.2, fill: isAnom ? "#DC2626" : "#1E3A8A", stroke: "#FFFFFF", "stroke-width": "2" }, svg);
    const dy = (i % 2 === 0) ? -12 : 16;
    const t = el("text", { x: cx, y: Math.max(M.t + 10, Math.min(H - M.b - 6, cy + dy)), fill: isAnom ? "#991B1B" : "#0F172A", "font-size": "10.2", "font-weight": "700", "text-anchor": cx > W - 120 ? "end" : "middle" }, svg);
    t.textContent = `${s.nm} (${fmtDec(s.ic, 1)})`;
  });

  renderPedBox("ped-ot-rd",
    `<b>${best.nm}</b> encabeza la complejidad funcional con <b>${fmtDec(best.ic,2)} puntos</b>. El servicio más escaso es <b>${otRdCols[rarIdx]}</b> (presente en solo ${fk[rarIdx]} localidad(es)), entregando <b>${fmtDec(wk[rarIdx],2)} pts</b> a quien lo posee.`,
    `<b>Por qué dos ciudades con igual cantidad de servicios pueden tener puntajes distintos:</b> en el ejemplo de cátedra, <i>Melchor de Mencos</i> y <i>San Ignacio</i> tienen <b>6 servicios cada una</b>, pero Melchor saca <b>191,67</b> y San Ignacio <b>175,00</b> porque Melchor posee <b>Guarderías</b> (el más escaso: 50 pts) mientras a San Ignacio le falta.`,
    `En el Control 5 (Unidad 5 OT): el Escalograma de Guttman / Rondinelli se aplica a las <b>10 comunas más pobladas</b> con mínimo <b>7 variables</b>. Si una columna queda con puros <code>1</code> no aporta diferenciación y debes cambiarla; además siempre se acompaña del gráfico de <b>Complejidad vs. Población</b>.`
  );
}

// --- C. ÍNDICE DE AISLAMIENTO COMUNAL (0/1 CLICABLE + RED VIAL SVG) ---
const OT_AI_PRESETS = {
  pauta: {
    titulo: "Ejemplo Oficial Pauta Unidad 5 (Osorno, Puaucho y Entre Lagos)",
    locs: ["Osorno", "Puaucho", "Entre Lagos"],
    links0: [[0, 1], [0, 2]]
  },
  lagos: {
    titulo: "Corredor Región de Los Lagos (10 localidades — Osorno a Puerto Montt)",
    locs: ["Osorno", "Puaucho", "Entre Lagos", "San Pablo", "Río Negro", "Purranque", "Pto. Octay", "Frutillar", "Pto. Varas", "Pto. Montt"],
    links0: [[0,1],[0,2],[0,3],[0,4],[0,6],[2,6],[4,5],[5,7],[6,7],[7,8],[8,9]]
  },
  biobio: {
    titulo: "Corredor Región del Biobío (10 comunas — Concepción a Los Ángeles)",
    locs: ["Concepción", "Talcahuano", "Hualpén", "San Pedro", "Chiguayante", "Coronel", "Lota", "Penco", "Tomé", "Los Ángeles"],
    links0: [[0,1],[0,2],[0,3],[0,4],[0,7],[0,9],[1,2],[3,5],[5,6],[7,8]]
  }
};

let otAiKey = "pauta";
let otAiLocs = [];
let otAiMat = [];
let otAiSelNode = -1;

function presetOtAisl(key) {
  const pr = OT_AI_PRESETS[key] || OT_AI_PRESETS.pauta;
  otAiKey = key;
  otAiLocs = [...pr.locs];
  const n = otAiLocs.length;
  otAiMat = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => (i === j ? 0 : 1)));
  pr.links0.forEach(([u, v]) => { otAiMat[u][v] = 0; otAiMat[v][u] = 0; });
  otAiSelNode = -1;
  drawOtAisl();
}
function toggleOtAislCell(i, j) {
  if (i === j) return;
  const nv = otAiMat[i][j] === 0 ? 1 : 0;
  otAiMat[i][j] = nv;
  otAiMat[j][i] = nv;
  drawOtAisl();
}
function clickOtAislNode(idx) {
  if (otAiSelNode < 0) { otAiSelNode = idx; drawOtAisl(); return; }
  if (otAiSelNode === idx) { otAiSelNode = -1; drawOtAisl(); return; }
  toggleOtAislCell(otAiSelNode, idx);
  otAiSelNode = -1;
  drawOtAisl();
}
function conectarRutaOtAisl() {
  const n = otAiLocs.length;
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (otAiMat[i][j] === 1) {
        otAiMat[i][j] = 0; otAiMat[j][i] = 0;
        drawOtAisl();
        return;
      }
    }
  }
}
function drawOtAisl() {
  if (otAiLocs.length === 0) { presetOtAisl("pauta"); return; }
  const n = otAiLocs.length;
  const totPairs = (n * (n - 1)) / 2;
  let directPairs = 0;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (otAiMat[i][j] === 0) directPairs++;

  const stats = otAiLocs.map((nm, i) => {
    let sum1 = 0, con0 = 0;
    for (let j = 0; j < n; j++) {
      if (i === j) continue;
      if (otAiMat[i][j] === 1) sum1++; else con0++;
    }
    const pct = (sum1 / Math.max(1, n - 1)) * 100;
    return { i, nm, sum1, con0, pct };
  });
  const ordBest = [...stats].sort((a, b) => a.pct - b.pct);
  const best = ordBest[0], worst = ordBest[ordBest.length - 1];
  const avgPct = stats.reduce((s, o) => s + o.pct, 0) / n;

  const selTxt = otAiSelNode >= 0
    ? ` <span style="color:#B45309;font-weight:800;">● Nodo seleccionado: ${otAiLocs[otAiSelNode]} — haz clic en otra localidad del grafo para abrir/cerrar ruta directa.</span>`
    : ` Recuerda la convención clave de examen: <b>0 = bueno (conectada directamente / asfaltada)</b> y <b>1 = malo (sin conexión directa / aislada)</b>.`;
  document.getElementById("ot-ai-enun").innerHTML = `<b>${OT_AI_PRESETS[otAiKey].titulo}.</b>${selTxt}`;

  document.getElementById("ot-ai-k-best").textContent = best.nm;
  document.getElementById("ot-ai-k-bestv").textContent = `${fmtDec(best.pct, 1)}% aislamiento (${best.con0} rutas)`;
  document.getElementById("ot-ai-k-worst").textContent = worst.nm;
  document.getElementById("ot-ai-k-worstv").textContent = `${fmtDec(worst.pct, 1)}% aislamiento (${worst.con0} rutas)`;
  document.getElementById("ot-ai-k-avg").textContent = `${fmtDec(avgPct, 1)}%`;
  document.getElementById("ot-ai-k-avg2").textContent = "Promedio de las " + n + " localidades";
  document.getElementById("ot-ai-k-con").textContent = `${directPairs} / ${totPairs} pares`;
  document.getElementById("ot-ai-k-con2").textContent = `${fmtDec((directPairs / Math.max(1, totPairs)) * 100, 1)}% conectividad vial`;

  renderFormulaStrip("ot-ai-fstrip", [
    {
      lbl: `Índice de Aislamiento — ${best.nm}`, col: "#15803D",
      eq: `IA<sub>i</sub> = ${mFrac('∑ <span class="sym-r">a<sub>ij</sub></span> (unos)', '<span class="sym-b">n</span> − 1')} × 100%`,
      sub: `IA = ${mFrac(vChip(best.sum1, "vc-r", "Pares sin conexión directa"), vChip(n - 1, "vc-b", "Otras localidades"))} × 100% = ${rChip(fmtDec(best.pct, 1) + "%")}`,
      note: `Conexiones directas (ceros): ${best.con0} de ${n - 1}`
    },
    {
      lbl: `Índice de Aislamiento — ${worst.nm}`, col: "#DC2626",
      eq: `IA<sub>i</sub> = ${mFrac('∑ <span class="sym-r">a<sub>ij</sub></span> (unos)', '<span class="sym-b">n</span> − 1')} × 100%`,
      sub: `IA = ${mFrac(vChip(worst.sum1, "vc-r"), vChip(n - 1, "vc-b"))} × 100% = ${rChip(fmtDec(worst.pct, 1) + "%", worst.pct > 50)}`,
      note: `Conexiones directas (ceros): ${worst.con0} de ${n - 1}`
    }
  ]);

  // Matriz simétrica clicable
  let tbl = `<table class="ot-mat-tbl"><thead><tr><th>Localidad</th>`;
  otAiLocs.forEach(l => { tbl += `<th>${l.length > 8 ? l.slice(0, 7) + "." : l}</th>`; });
  tbl += `<th>Suma (1)</th><th>IA (%)</th></tr></thead><tbody>`;

  otAiLocs.forEach((nm, i) => {
    tbl += `<tr><td>${nm}</td>`;
    for (let j = 0; j < n; j++) {
      if (i === j) {
        tbl += `<td class="ot-diag">—</td>`;
      } else {
        const v = otAiMat[i][j];
        const cls = v === 0 ? "ot-ai0" : "ot-ai1";
        tbl += `<td><button class="ot-cell-btn ${cls}" style="width:26px;" onclick="toggleOtAislCell(${i},${j})" title="${nm} ↔ ${otAiLocs[j]}: clic para alternar 0/1">${v}</button></td>`;
      }
    }
    tbl += `<td style="font-weight:800;">${stats[i].sum1}</td><td style="font-weight:800;color:${stats[i].pct <= 50 ? "#15803D" : "#DC2626"};">${fmtDec(stats[i].pct, 1)}%</td></tr>`;
  });
  tbl += `</tbody></table>`;
  document.getElementById("ot-ai-tbl-box").innerHTML = tbl;

  // SVG Red Vial (arriba) + Barras de Aislamiento (abajo)
  const svg = document.getElementById("svg-ot-aisl");
  if (!svg) return;
  svg.innerHTML = "";
  const W = 560, H = 405;
  const cx = W / 2, cy = 128, rx = n <= 4 ? 145 : 205, ry = n <= 4 ? 76 : 92;
  const pts = otAiLocs.map((nm, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2;
    return { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a), nm };
  });

  const tHd = el("text", { x: W / 2, y: 18, fill: "#0F172A", "font-size": "11.5", "font-weight": "800", "text-anchor": "middle" }, svg);
  tHd.textContent = "Red Vial Directa (Línea verde = 0 conectada · Clic en 2 nodos edita)";

  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (otAiMat[i][j] === 0) {
        el("line", { x1: pts[i].x, y1: pts[i].y, x2: pts[j].x, y2: pts[j].y, stroke: "#15803D", "stroke-width": "2.4", opacity: "0.85" }, svg);
      }
    }
  }
  pts.forEach((p, i) => {
    const isSel = (otAiSelNode === i);
    const col = stats[i].pct === best.pct ? "#15803D" : (stats[i].pct >= 75 ? "#DC2626" : "#1D4ED8");
    const g = el("g", { style: "cursor:pointer;", onclick: `clickOtAislNode(${i})` }, svg);
    if (isSel) el("circle", { cx: p.x, cy: p.y, r: 16, fill: "rgba(245,158,11,0.22)", stroke: "#D97706", "stroke-width": "2.2", "stroke-dasharray": "4,2" }, g);
    el("circle", { cx: p.x, cy: p.y, r: 10.5, fill: col, stroke: "#FFFFFF", "stroke-width": "2" }, g);
    const t = el("text", { x: p.x, y: p.y - 13, fill: "#0F172A", "font-size": "10", "font-weight": "700", "text-anchor": "middle" }, g);
    t.textContent = p.nm;
  });

  // Mini ranking de barras horizontales abajo (y=252..392)
  el("line", { x1: 16, y1: 242, x2: W - 16, y2: 242, stroke: "#CBD5E1" }, svg);
  const tB = el("text", { x: W / 2, y: 258, fill: "#1E3A8A", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }, svg);
  tB.textContent = "Índice de Aislamiento (%) — Menor barra = Mejor Conectividad";

  const showBars = ordBest.slice(0, Math.min(8, n));
  const rowH = Math.min(18, 130 / Math.max(1, showBars.length));
  showBars.forEach((stItem, k) => {
    const y0 = 266 + k * rowH;
    const xL = 112, maxBw = 370;
    const bw = Math.max(3, (stItem.pct / 100) * maxBw);
    const col = stItem.pct <= 45 ? "#15803D" : (stItem.pct <= 70 ? "#D97706" : "#DC2626");
    const tl = el("text", { x: xL - 6, y: y0 + rowH * 0.72, fill: "#0F172A", "font-size": "9.8", "font-weight": "700", "text-anchor": "end" }, svg);
    tl.textContent = stItem.nm;
    el("rect", { x: xL, y: y0 + 2, width: bw, height: Math.max(6, rowH - 5), fill: col, rx: 3 }, svg);
    const tv = el("text", { x: xL + bw + 5, y: y0 + rowH * 0.72, fill: col, "font-size": "9.6", "font-weight": "800" }, svg);
    tv.textContent = `${fmtDec(stItem.pct, 1)}%`;
  });

  renderPedBox("ped-ot-ai",
    `<b>${best.nm}</b> presenta el menor aislamiento (<b>${fmtDec(best.pct,1)}%</b> con ${best.con0} conexiones directas), mientras <b>${worst.nm}</b> registra el mayor aislamiento (<b>${fmtDec(worst.pct,1)}%</b>). El promedio de la red es <b>${fmtDec(avgPct,1)}%</b>.`,
    `<b>La Trampa Clásica del 0 y el 1 en Pruebas:</b> en Rondinelli, <code>1</code> es positivo (tiene el servicio); pero en la Matriz de Aislamiento es exactamente al revés: <b><code>0</code> es positivo (conectada directamente por asfalto)</b> y <b><code>1</code> penaliza (sin conexión directa)</b>. Por eso quien suma MENOS unos está mejor conectado.`,
    `Vincula este indicador con el <b>PROT (SUBDERE-CEPAL, 2011)</b>: el aislamiento aumenta por la <i>fricción de la distancia</i> y la <i>rugosidad topográfica</i> (pág. 12), generando círculos viciosos de baja población y escasez de servicios que el GORE debe corregir mediante inversión en conectividad.`
  );
}


loadDiniTopology('simetrica', null);
presetOtRanking('mancilla');
presetOtRond('ejemplo');

// --- D & E. MANUAL PROT (4 SISTEMAS SVG, ANEXO 2 Y CONTROL DE LECTURA OT DE 10 PREGUNTAS) ---
const OT_SISTEMAS_DATA = {
  costero: {
    nm: "Sistema Costero",
    col: "#0284C7",
    bg: "#E0F2FE",
    rol: "Define <b>usos preferentes del borde costero</b> considerando factores geográficos, recursos marinos, centros poblados aledaños y concesiones existentes para impulsar el desarrollo sustentable del litoral (SUBDERE, pág. 20).",
    conflictos: "Superposición entre acuicultura/salmonicultura, pesca artesanal, turismo de playas, puertos comerciales y áreas marinas protegidas.",
    normas: "DS 475/1994 (Política Nacional de Uso del Borde Costero · CNUBC / CRUBC), DFL 340 (Concesiones Marítimas · SSFFAA / DIRECTEMAR), Ley 18.892 (Pesca y Acuicultura · SUBPESCA / SERNAPESCA)."
  },
  urbano: {
    nm: "Sistema Urbano",
    col: "#1D4ED8",
    bg: "#DBEAFE",
    rol: "Planifica la <b>configuración, articulación y organización del sistema de ciudades y centros poblados</b> en perspectiva dinámico-temporal, integrando procesos <i>interurbanos</i> (redes entre ciudades) e <i>intraurbanos</i> (usos del suelo, densidades) (pág. 20).",
    conflictos: "Expansión urbana descontrolada sobre suelo agrícola, segregación socioespacial, congestión vial y déficit de equipamiento/vivienda.",
    normas: "DFL 458/1975 (Ley General de Urbanismo y Construcciones — LGUC), DS 47/1992 (OGUC · MINVU / DOM), Ley 18.695 (Municipalidades · PLADECO y PRC), Ley 19.525 (Aguas Lluvias)."
  },
  rural: {
    nm: "Sistema Rural",
    col: "#059669",
    bg: "#DCFCE7",
    rol: "Aborda los <b>desequilibrios territoriales rurales</b> para reducir externalidades negativas del crecimiento espontáneo y del deterioro ecológico, mejorando el bienestar rural en armonía con el patrimonio natural (pág. 20).",
    conflictos: "Parcelaciones de agrado y fragmentación de suelo productivo (DL 3.516), despoblamiento juvenil, aislamiento vial/digital y falta de agua potable rural.",
    normas: "DL 3.516 (División de Predios Rústicos · SAG / SEREMI MINVU), DL 3.557 (Protección Agrícola · SAG), DL 701 / DS 4.363 (Bosques y Fomento Forestal · CONAF), Ley 19.253 (Desarrollo Indígena · CONADI)."
  },
  cuenca: {
    nm: "Sistema Cuenca Hidrográfica",
    col: "#7C3AED",
    bg: "#F3E8FF",
    rol: "Orienta el <b>uso y manejo integrado de los recursos naturales de la cuenca</b> de forma ordenada, articulada e informada para optimizar impactos sociales, económicos y ambientales presentes y futuros (pág. 20).",
    conflictos: "Competencia por derechos de agua (riego, hidroelectricidad, consumo humano), contaminación de cauces, erosión de laderas y riesgos de inundación o remoción en masa.",
    normas: "DFL 1.122/1981 (Código de Aguas · DGA / MOP), Ley 19.300 (Bases Generales del Medio Ambiente y SEIA · MMA), Ley 18.362 (SNASPE · CONAF), DS 609/1978 (Deslindes de cauces de ríos y lagos · Bienes Nacionales)."
  }
};

let otSysSel = "costero";

function selectOtSistema(key) {
  otSysSel = key;
  drawOtSistemasSvg();
}
function drawOtSistemasSvg() {
  const svg = document.getElementById("svg-ot-sistemas");
  const det = document.getElementById("ot-sys-detail");
  if (!svg || !det) return;
  svg.innerHTML = "";

  // Perfil topográfico estilo Figura 1 (pág. 20 SUBDERE-CEPAL)
  // Fondo zonas clicables
  const zonas = [
    { key: "costero", x: 18,  w: 175, lbl: "1. Sistema Costero" },
    { key: "urbano",  x: 193, w: 205, lbl: "2. Sistema Urbano" },
    { key: "rural",   x: 398, w: 270, lbl: "3. Sistema Rural" },
    { key: "cuenca",  x: 668, w: 294, lbl: "4. Sistema Cuenca Hidrográfica" }
  ];

  zonas.forEach(z => {
    const info = OT_SISTEMAS_DATA[z.key];
    const isAct = (otSysSel === z.key);
    const g = el("g", { style: "cursor:pointer;", onclick: `selectOtSistema('${z.key}')` }, svg);
    el("rect", {
      x: z.x, y: 12, width: z.w, height: 192, rx: 4,
      fill: isAct ? info.bg : "#FFFFFF",
      stroke: isAct ? info.col : "#CBD5E1",
      "stroke-width": isAct ? "2.4" : "1"
    }, g);
    const t = el("text", {
      x: z.x + z.w / 2, y: 32,
      fill: isAct ? info.col : "#334155",
      "font-size": "11.5", "font-weight": "800", "text-anchor": "middle"
    }, g);
    t.textContent = z.lbl;
    el("line", { x1: z.x + 12, y1: 41, x2: z.x + z.w - 12, y2: 41, stroke: info.col, "stroke-width": "1.6", "stroke-dasharray": isAct ? "" : "4,3" }, g);
  });

  // Silueta mar + costa + ciudad + campo + cordillera (continuo territorial)
  el("rect", { x: 24, y: 158, width: 148, height: 38, fill: "rgba(2,132,199,0.22)" }, svg);
  el("polyline", { points: "24,158 172,158 205,134 670,134 730,96 765,112 835,54 895,110 952,188", fill: "none", stroke: "#0F172A", "stroke-width": "2.4" }, svg);
  el("line", { x1: 24, y1: 196, x2: 954, y2: 196, stroke: "#64748B", "stroke-width": "1.4" }, svg);

  // Íconos geométricos limpios: mar (triángulo nivel agua), edificios (urbano), casas/árboles (rural), río descendiendo (cuenca)
  el("polygon", { points: "95,146 111,146 103,157", fill: "none", stroke: "#0284C7", "stroke-width": "1.8" }, svg);
  // Edificios urbanos
  [[232,96,20,38],[260,82,22,52],[290,104,18,30],[316,74,24,60],[348,108,18,26]].forEach(([bx,by,bw,bh]) => {
    el("rect", { x: bx, y: by, width: bw, height: bh, fill: "#93C5FD", stroke: "#1E3A8A", "stroke-width": "1.3" }, svg);
  });
  // Casas rurales y árboles
  [[455,116],[555,116]].forEach(([hx,hy]) => {
    el("rect", { x: hx, y: hy, width: 20, height: 18, fill: "#BBF7D0", stroke: "#065F46", "stroke-width": "1.3" }, svg);
    el("polygon", { points: `${hx-3},${hy} ${hx+10},${hy-13} ${hx+23},${hy}`, fill: "#34D399", stroke: "#065F46", "stroke-width": "1.2" }, svg);
  });
  [[510,122],[615,122]].forEach(([tx,ty]) => {
    el("line", { x1: tx, y1: ty, x2: tx, y2: 134, stroke: "#78350F", "stroke-width": "2.4" }, svg);
    el("circle", { cx: tx, cy: ty - 6, r: 9, fill: "#10B981", stroke: "#065F46", "stroke-width": "1.2" }, svg);
  });
  // Flujo de cuenca hídrica
  el("polyline", { points: "835,58 790,118 725,134 670,134", fill: "none", stroke: "#7C3AED", "stroke-width": "2.6", "stroke-dasharray": "5,3" }, svg);
  const tNote = el("text", { x: 490, y: 184, fill: "#334155", "font-size": "10.3", "font-weight": "700", "text-anchor": "middle" }, svg);
  tNote.textContent = "Continuo Territorial Regional (Figura 1, SUBDERE-CEPAL 2011, pág. 20) — Ningún sistema opera aislado de los demás";

  const cur = OT_SISTEMAS_DATA[otSysSel];
  det.style.borderLeftColor = cur.col;
  det.innerHTML =
    `<div style="font-size:12.6px;font-weight:800;color:${cur.col};margin-bottom:4px;">${cur.nm} (Componente de Análisis del PROT)</div>` +
    `<div><b>Propósito en el PROT:</b> ${cur.rol}</div>` +
    `<div style="margin-top:4px;"><b>Conflictos típicos de uso:</b> ${cur.conflictos}</div>` +
    `<div style="margin-top:4px;"><b>Normativa e instituciones clave (Anexo 2):</b> ${cur.normas}</div>`;
}

const OT_ANEXO2_DATA = [
  { mat: "Gobierno Regional (OT)", norma: "DFL 1/2005 (Ley 19.175 LOCGAR)", org: "GORE, CORE, SEREMI MINVU, Municipalidades" },
  { mat: "Urbanismo y Construcciones", norma: "DFL 458/1975 (LGUC) y DS 47/1992 (OGUC)", org: "MINVU, DOM Municipal, Asesor Urbanista" },
  { mat: "Municipalidades (PLADECO)", norma: "DFL 1/2006 (Ley 18.695 LOCM)", org: "Municipalidad, SECPLA, Alcalde y Concejo" },
  { mat: "Borde Costero", norma: "DS 475/1994 (Política Borde Costero) y DFL 340", org: "CNUBC, CRUBC, GORE, DIRECTEMAR, SSFFAA" },
  { mat: "Aguas y Cuencas", norma: "DFL 1.122/1981 (Código de Aguas) y Ley 19.525", org: "DGA, MOP, MMA, MINVU (aguas lluvias)" },
  { mat: "Medio Ambiente y SEIA", norma: "Ley 19.300 y DS 95/2001 (Reglamento SEIA)", org: "Ministerio del Medio Ambiente, SEREMI MMA" },
  { mat: "Predios Rústicos (Rural)", norma: "DL 3.516 (División de Predios Rústicos)", org: "SAG, SEREMI MINVU, Municipalidades" },
  { mat: "Bosques y Fomento Forestal", norma: "DS 4.363/1931 (Ley Bosques) y DL 701 / 2.565", org: "CONAF, SAG, Min. Agricultura, Bienes Nacionales" },
  { mat: "Áreas Silvestres Protegidas", norma: "Ley 18.362 (SNASPE)", org: "CONAF, Bienes Nacionales, Min. Agricultura" },
  { mat: "Acuicultura y Pesca", norma: "DS 430/1991 (Ley 18.892) y DS 320/2001 (RAMA)", org: "SUBPESCA, SERNAPESCA, DIRECTEMAR" },
  { mat: "Desarrollo Indígena", norma: "Ley 19.253 (Áreas de Desarrollo Indígena)", org: "CONADI, GORE, Municipalidades, MINVU" },
  { mat: "Catástrofes y Riesgos", norma: "Ley 16.282 y DS 156/2002 (Protección Civil)", org: "Min. Interior, Protección Civil/SENAPRED, GORE" },
  { mat: "Monumentos y Patrimonio", norma: "Ley 17.288 (Monumentos Nacionales)", org: "Consejo de Monumentos Nacionales, Municipalidades" },
  { mat: "Información Territorial", norma: "DS 28/2006 (Homologación SNIT / UGIT)", org: "Ministerio de Bienes Nacionales, GORE" }
];

function renderOtAnexo2() {
  const box = document.getElementById("ot-anexo2-box");
  if (!box) return;
  const q = (document.getElementById("ot-anexo2-q")?.value || "").trim().toLowerCase();
  const rows = OT_ANEXO2_DATA.filter(r => !q || (r.mat + " " + r.norma + " " + r.org).toLowerCase().includes(q));
  let h = `<table class="ot-mat-tbl"><thead><tr><th>Materia</th><th>Norma Legal</th><th>Organismos</th></tr></thead><tbody>`;
  if (rows.length === 0) {
    h += `<tr><td colspan="3" style="text-align:center;color:#64748B;">Sin coincidencias para "${q}".</td></tr>`;
  } else {
    rows.forEach(r => {
      h += `<tr><td>${r.mat}</td><td style="text-align:left;font-family:inherit;"><b>${r.norma}</b></td><td style="text-align:left;font-family:inherit;">${r.org}</td></tr>`;
    });
  }
  h += `</tbody></table>`;
  box.innerHTML = h;
}

const OT_QUIZ_DATA = [
  {
    tag: "06 OT · Lám. 2 y 5",
    q: "Según Massiris (2002) y las láminas de cátedra, ¿cómo se diferencia el enfoque predominante del Ordenamiento Territorial en Chile/Brasil frente a Alemania, Francia y Reino Unido?",
    opts: [
      "Chile y Brasil lo conciben como planificación física (uso y ocupación del suelo), mientras Europa lo integra a la planificación económica y social",
      "Chile y Brasil aplican un modelo federal descentralizado, mientras Europa utiliza solo planes reguladores comunales",
      "Ambos bloques lo entienden exclusivamente como zonificación urbana municipal sin vínculos económicos"
    ],
    ans: 0,
    why: "Lámina 5 de '06 OT 2024': Chile y Brasil han puesto el énfasis en la planificación física del uso y ocupación del territorio, mientras Alemania, Francia y Reino Unido lo entienden como planificación integral estrechamente ligada a la planificación económica y social."
  },
  {
    tag: "06 OT · Lám. 4 / PROT p.23",
    q: "De acuerdo con el Artículo 3° de la Constitución Política de Chile, ¿cuál es el contexto político-administrativo del país para el Ordenamiento Territorial?",
    opts: [
      "Estado Federal con constituciones regionales y tribunal federal",
      "Estado Unitario con administración funcional y territorialmente descentralizada o desconcentrada",
      "Confederación de regiones soberanas regidas solo por coordinación voluntaria"
    ],
    ans: 1,
    why: "Art. 3° CPR (Lám. 4 y SUBDERE pág. 7 y 23): Chile es un Estado unitario cuya administración será funcional y territorialmente descentralizada o desconcentrada, promoviendo la regionalización y el desarrollo equitativo y solidario."
  },
  {
    tag: "06 OT · Lám. 6",
    q: "Al comparar las escalas del Ordenamiento Territorial, ¿qué dirección predominante tienen las políticas de nivel Nacional y Regional frente al nivel Local?",
    opts: [
      "Nacional y Regional son de abajo hacia arriba; Local es de arriba hacia abajo",
      "Todas las escalas son estrictamente de arriba hacia abajo",
      "Nacional y Regional son de arriba hacia abajo; Local es de abajo hacia arriba (regulaciones y dinámicas urbanas)"
    ],
    ans: 2,
    why: "Lámina 6 de '06 OT 2024': Nacional y Regional operan con políticas de arriba hacia abajo (redistribución, sustentabilidad, sistema de asentamientos), mientras el nivel Local opera de abajo hacia arriba (planificación físico-espacial, densidades y zonificaciones)."
  },
  {
    tag: "PROT · Págs. 5, 9 y 26",
    q: "¿Cuál es la relación exacta entre la Estrategia Regional de Desarrollo (ERD) y el Plan Regional de Ordenamiento Territorial (PROT), y cuál es su horizonte temporal?",
    opts: [
      "El PROT reemplaza a la ERD cada 4 años como norma restrictiva urbana",
      "El PROT espacializa los objetivos de la ERD con un horizonte de 10 años y carácter orientador",
      "La ERD es un anexo cartográfico del PROT elaborado por cada municipalidad"
    ],
    ans: 1,
    why: "SUBDERE-CEPAL (2011, págs. 5, 25 y 26): el PROT es un complemento que posibilita la espacialización de los objetivos de la ERD en un horizonte de mediano plazo de 10 años, con carácter orientador más que meramente restrictivo."
  },
  {
    tag: "PROT · Pág. 12",
    q: "En el manual SUBDERE-CEPAL (pág. 12), ¿qué ocurre cuando aumenta la 'rugosidad de la superficie' o sube el peaje de fin de semana?",
    opts: [
      "Disminuye la fricción de la distancia y mejora el índice de centralidad",
      "Aumenta la fricción de la distancia, agravando el aislamiento y pudiendo activar un círculo vicioso de menos empleo, despoblamiento y pérdida de servicios",
      "Solo afecta a la distancia en kilómetros pero no tiene efecto territorial"
    ],
    ans: 1,
    why: "SUBDERE-CEPAL (pág. 12): la accesibilidad depende de la rugosidad física (relieve, malas rutas, transbordos) y la fricción de la distancia, que incluso puede elevarse artificialmente por costos de peaje, cerrando círculos viciosos de enclave y reducción de umbrales poblacionales."
  },
  {
    tag: "PROT · Págs. 19–20",
    q: "¿Cuáles son los 4 componentes de análisis territorial (sistemas) que el PROT debe integrar de forma continua en la región?",
    opts: [
      "Urbano, Industrial, Minero y Turístico",
      "Rural, Urbano, Costero y de Cuencas Hidrográficas",
      "Comunal, Provincial, Regional y Nacional"
    ],
    ans: 1,
    why: "SUBDERE-CEPAL (Figura 1, págs. 19–20): el PROT integra los sistemas Costero, Urbano, Rural y de Cuencas Hidrográficas como un continuo territorial."
  },
  {
    tag: "PROT · Págs. 21–22",
    q: "Según el enfoque de Desarrollo Territorial Sustentable (Folch 2003 / SUBDERE págs. 21–22), ¿cuáles son los 3 objetivos territoriales simultáneos y qué significa 'competir con la gente'?",
    opts: [
      "Funcionalidad, Habitabilidad y Competitividad; 'competir con la gente' alude a variables intangibles como educación, capacitación laboral y educación ciudadana",
      "Higiene ambiental, Crecimiento del PIB y Densificación; 'competir con la gente' significa bajar salarios locales",
      "Primacía, Aislamiento y Zonificación; 'competir con la gente' implica aumentar la población urbana"
    ],
    ans: 0,
    why: "SUBDERE-CEPAL (págs. 21–22): el desarrollo sustentable busca simultáneamente Funcionalidad, Habitabilidad y Competitividad, incorporando en esta última variables intangibles ('competir con la gente')."
  },
  {
    tag: "PROT · Págs. 25, 32 y 35",
    q: "Dentro de la estructura del PROT (Cap. 4), ¿qué función cumple el 'Mapa Semáforo' y qué son los escenarios 'deseable, probable y posible'?",
    opts: [
      "El Mapa Semáforo mide la congestión vehicular urbana y los escenarios se usan en el Plan de Acción financiero",
      "El Mapa Semáforo permite observar rápidamente los focos de conflictos de intereses por uso del territorio, y los escenarios forman parte del Análisis Prospectivo",
      "Ambos pertenecen exclusivamente al PLADECO comunal a escala 1:100.000"
    ],
    ans: 1,
    why: "SUBDERE-CEPAL (págs. 31–32 y 35): el Análisis Prospectivo construye escenarios (deseable, probable y posible) para pasar del modelo actual al deseado; en Cartografía, el Mapa Semáforo visibiliza focos de conflictos de interés sobre usos del territorio."
  },
  {
    tag: "06 OT · Lám. 10–15",
    q: "En la Escala de Guttman / Matriz de Rondinelli (Control 5), ¿por qué dos comunas con el mismo número total de servicios pueden obtener distinto puntaje de centralidad funcional?",
    opts: [
      "Porque el peso Wk = 100 / fk premia con mayor puntaje a los servicios más escasos (menor frecuencia fk), no valen todos lo mismo",
      "Porque el puntaje de Rondinelli se divide por la población de cada comuna",
      "Porque los servicios presentes en todas las comunas (fk = n) reciben peso 100"
    ],
    ans: 0,
    why: "En Rondinelli (06 OT 2024, láms. 14–15), un equipamiento raro presente en solo 2 ciudades entrega Wk = 100/2 = 50 pts, mientras uno común presente en 4 entrega 25 pts. Además, las variables donde todas tienen 1 no discriminan y deben reemplazarse."
  },
  {
    tag: "Unidad 5 OT · Pauta",
    q: "Al comparar la Matriz de Rondinelli con la Matriz de Aislamiento Comunal, ¿qué representa el valor 0 en cada instrumento?",
    opts: [
      "En ambos instrumentos 0 indica ausencia de problemas (buen desempeño)",
      "En Rondinelli 0 significa ausencia del servicio (desfavorable), mientras en Aislamiento 0 significa conexión directa asfaltada (favorable)",
      "En Rondinelli 0 significa presencia y en Aislamiento 0 significa localidad aislada"
    ],
    ans: 1,
    why: "Pauta 'Unidad 5. Ordenamiento Territorial': en Guttman/Rondinelli 1 = Presente y 0 = Ausente; en Aislamiento 0 = Conectada directamente (o asfaltada) y 1 = No conectada directamente (ripio/tierra o sin ruta directa)."
  }
];

let otQzAns = {};
let otQzSoloPend = false;

function toggleSoloErrOtQz(btn) {
  otQzSoloPend = !otQzSoloPend;
  btn.classList.toggle("primary", otQzSoloPend);
  renderOtQuiz();
}
function responderOtQuiz(idx, optIdx) {
  otQzAns[idx] = optIdx;
  renderOtQuiz();
}
function resetOtQuiz() {
  otQzAns = {};
  otQzSoloPend = false;
  renderOtQuiz();
}
function renderOtQuiz() {
  const wrap = document.getElementById("ot-qz-list");
  if (!wrap) return;
  wrap.innerHTML = "";
  let okCount = 0;
  OT_QUIZ_DATA.forEach((item, idx) => {
    const uAns = otQzAns[idx];
    const isAns = uAns !== undefined;
    const isOk = isAns && uAns === item.ans;
    if (isOk) okCount++;
    if (otQzSoloPend && isOk) return;

    const card = document.createElement("div");
    card.className = "qz-card" + (isAns ? (" answered " + (isOk ? "ok" : "bad")) : "");
    const btns = item.opts.map((op, oi) =>
      `<button class="qz-btn ${uAns === oi ? "sel" : ""}" onclick="responderOtQuiz(${idx}, ${oi})">${op}</button>`
    ).join("");
    const badgeRes = isAns ? `<span style="font-size:11.5px;font-weight:800;color:${isOk ? "#15803D" : "#DC2626"};">${isOk ? "✓ Correcto" : "✗ Revisar"}</span>` : "";
    card.innerHTML = `
      <div><span class="qz-tag">${item.tag}</span> <span style="font-size:11px;color:#475569;font-weight:700;">Pregunta OT ${idx + 1}</span></div>
      <div class="qz-q">${item.q}</div>
      <div class="qz-opts">${btns}${badgeRes}</div>
      <div class="qz-fb"><b>Respaldo oficial:</b> ${item.why}</div>`;
    wrap.appendChild(card);
  });
  const sc = document.getElementById("ot-qz-score");
  if (sc) sc.textContent = `Aciertos OT: ${okCount} / ${OT_QUIZ_DATA.length}`;
}

presetOtAisl('pauta');
drawOtSistemasSvg();
renderOtAnexo2();
renderOtQuiz();
drawIndicadoresU6();
renderMecanica();
drawMapaTeoria();
renderLecturaCards();
renderQuizLectura();
</script>
</body>
</html>
"""


def renderizar_laboratorio_fluido_territorial():
    """Renderiza el Estudio Territorial Integral a 60 FPS (11 pestañas, incluyendo Laboratorio OT Unidad V) sin recarga de servidor."""
    components.html(HTML_TERRITORIAL_60FPS, height=1280, scrolling=True)
