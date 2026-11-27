# -*- coding: utf-8 -*-
"""
motor_expansion_dgt_ra2.py — CRONOGRAMA DGT 2026 + ACCESO RÁPIDO 1 CLIC + REFUERZO PALABRAL Y TESTEO (CONTROL 4 / OT / CRITIC)
Módulo plug-and-play para DESARROLLO-Y-GESTION-TERRITORIAL-2026 (ULagos — Prof. Claudio Mancilla).
Cero emojis. Estética académica sobria lista para presentar en cátedra y estudiar para RA2.

Incluye sobre `HTML_TERRITORIAL_60FPS`:
  1) Cronograma DGT 2026 (modo docente: Unidades I a VI limpias; modo admin: hitos reales incluyendo Vie 4 Dic Control 4 y 14-15 Dic RA2).
  2) Barra de Acceso Rápido en 1 Clic (4 modelos estrella: Weber/Krugman, Lorenz/Gini/Theil, Redes Dini + Cadenas CEPAL, OT Rondinelli + CRITIC).
  3) Refuerzo Pedagógico Palabral-Conceptual + Precisiones (No confundir) + Síntesis Oral (30 seg con Modo Ciego)
     + Autoevaluación Conceptual en Vivo (10 preguntas nuevas) en:
       - Unidad IV · Control 4: Redes Empresariales (Dini 2010 hasta p. 26) y Cadenas de Valor (CEPAL Cap. 3).
       - Unidad V · Ordenamiento Territorial: Guttman / Rondinelli y Aislamiento.
       - Unidad VI · Método CRITIC Objetivo (2017 vs. 2024 y Convergencia).
  4) Separación limpia de los 3 pasos en Modo Aprender + 2 nuevos retos en Modo Practicar (Retos 9 y 10).
"""


CSS_EXPANSION_DGT_RA2 = r"""
<style id="css-expansion-dgt-ra2">
  /* === BARRA CRONOGRAMA DGT 2026 === */
  .cal-bar {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 4px solid #0F766E;
    border-radius: 8px;
    padding: 7px 12px;
    margin-bottom: 10px;
    font-size: 11.6px;
  }
  .cal-bar summary {
    cursor: pointer;
    font-weight: 800;
    color: #0F172A;
    list-style: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
  }
  .cal-bar summary::-webkit-details-marker { display: none; }
  .cal-badge-new {
    font-size: 10.2px;
    font-weight: 800;
    color: #FFFFFF;
    background: #059669;
    padding: 2px 8px;
    border-radius: 10px;
  }
  .cal-strip {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px dashed #CBD5E1;
  }
  .cal-pill {
    border: 1px solid #CBD5E1;
    background: #F8FAFC;
    color: #1E293B;
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.14s ease;
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
  .cal-pill:hover { border-color: #1D4ED8; background: #EFF6FF; color: #1D4ED8; }
  .cal-pill.cp-eval { border-color: #FDBA74; background: #FFFBEB; color: #9A3412; }
  .cal-pill.cp-new { border-color: #10B981; background: #ECFDF5; color: #065F46; }
  .cal-dt {
    font-family: Consolas, monospace;
    font-size: 10.2px;
    font-weight: 800;
    background: #E2E8F0;
    color: #0F172A;
    padding: 1px 5px;
    border-radius: 4px;
  }
  .cal-pill.cp-eval .cal-dt { background: #FDE68A; color: #78350F; }
  .cal-pill.cp-new .cal-dt { background: #059669; color: #FFFFFF; }

  /* === BARRA ACCESO RÁPIDO EN 1 CLIC (4 MODELOS CLAVE) === */
  .qs-shell {
    display: none;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 9px;
    padding: 9px 12px;
    margin-bottom: 10px;
  }
  .wrap.mode-aprender .qs-shell { display: block; }
  .qs-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 7px;
  }
  .qs-tit {
    font-size: 11.4px;
    font-weight: 800;
    color: #0F172A;
    text-transform: uppercase;
    letter-spacing: 0.3px;
  }
  .qs-hint {
    font-size: 11.2px;
    color: #475569;
    font-weight: 600;
  }
  .qs-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 7px;
  }
  @media (max-width: 820px) { .qs-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 500px) { .qs-grid { grid-template-columns: 1fr; } }
  .qs-btn {
    border: 1.5px solid #CBD5E1;
    border-left: 4px solid #1D4ED8;
    background: #F8FAFC;
    color: #0F172A;
    border-radius: 7px;
    padding: 7px 9px;
    text-align: left;
    cursor: pointer;
    transition: all 0.14s ease;
  }
  .qs-btn:hover { border-color: #1D4ED8; background: #EFF6FF; transform: translateY(-1px); }
  .qs-btn.active { background: #0F172A; color: #FFFFFF; border-color: #0F172A; border-left-color: #38BDF8; }
  .qs-btn b { display: block; font-size: 11.8px; line-height: 1.25; }
  .qs-btn span { display: block; font-size: 10.6px; color: #475569; margin-top: 2px; line-height: 1.25; }
  .qs-btn.active span { color: #CBD5E1; }

  /* === TUTOR CONCEPTUAL PALABRAL + CONECTORES + SÍNTESIS ORAL + AUTOEVALUACIÓN === */
  .tutor-box {
    margin: 10px 0;
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border: 1.5px solid #BFDBFE;
    border-left: 5px solid #1E3A8A;
    border-radius: 8px;
    padding: 11px 14px;
  }
  .tutor-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
    padding-bottom: 7px;
    border-bottom: 1px dashed #CBD5E1;
  }
  .tutor-tit { font-size: 12.4px; font-weight: 800; color: #1E3A8A; }
  .tutor-prose { font-size: 12.1px; line-height: 1.58; color: #1E293B; margin-bottom: 9px; }
  .tutor-prose p { margin: 0 0 7px 0; }
  .tutor-prose p:last-child { margin-bottom: 0; }
  .conn-tag {
    display: inline-block;
    font-weight: 800;
    font-size: 11.1px;
    padding: 0.5px 6px;
    border-radius: 4px;
    margin-right: 3px;
    background: #DBEAFE;
    color: #1E40AF;
  }
  .conn-tag.ct-warn { background: #FEF3C7; color: #92400E; }
  .conn-tag.ct-ok   { background: #DCFCE7; color: #166534; }
  .conn-tag.ct-purp { background: #F3E8FF; color: #6B21A8; }
  .conn-tag.ct-red  { background: #FEE2E2; color: #991B1B; }

  .tutor-cols {
    display: grid;
    grid-template-columns: 1.1fr 1fr;
    gap: 10px;
    margin-top: 8px;
  }
  @media (max-width: 820px) { .tutor-cols { grid-template-columns: 1fr; } }
  .comp-card {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-top: 3px solid #7C3AED;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.5px;
    line-height: 1.44;
  }
  .comp-card-tit { font-size: 11.1px; font-weight: 800; color: #6B21A8; text-transform: uppercase; margin-bottom: 5px; }
  .comp-item { padding: 4px 0; border-bottom: 1px dashed #E2E8F0; }
  .comp-item:last-child { border-bottom: none; padding-bottom: 0; }

  .oral-card {
    background: #F0FDF4;
    border: 1px solid #86EFAC;
    border-top: 3px solid #15803D;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.6px;
    line-height: 1.48;
    color: #14532D;
  }
  .oral-head { display: flex; justify-content: space-between; align-items: center; gap: 6px; margin-bottom: 5px; }
  .oral-tit { font-size: 11.1px; font-weight: 800; color: #166534; text-transform: uppercase; }
  .oral-blur { filter: blur(5px); user-select: none; cursor: pointer; transition: filter 0.15s ease; }

  .mt-box {
    margin: 10px 0;
    background: #FFFFFF;
    border: 1.5px solid #CBD5E1;
    border-top: 3.5px solid #0F172A;
    border-radius: 8px;
    padding: 10px 13px;
  }
  .mt-head { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
  .mt-tit { font-size: 12.2px; font-weight: 800; color: #0F172A; }
  .mt-qcard {
    border: 1px solid #CBD5E1;
    border-left: 4px solid #475569;
    border-radius: 6px;
    background: #F8FAFC;
    padding: 8px 11px;
    margin-bottom: 7px;
  }
  .mt-qcard.ok { border-left-color: #15803D; background: #F0FDF4; }
  .mt-qcard.bad { border-left-color: #DC2626; background: #FEF2F2; }
  .mt-qtxt { font-size: 12px; font-weight: 700; color: #0F172A; margin-bottom: 6px; line-height: 1.42; }
  .mt-opts { display: flex; gap: 6px; flex-wrap: wrap; }
  .mt-btn {
    border: 1px solid #94A3B8;
    background: #FFFFFF;
    color: #0F172A;
    padding: 4px 10px;
    border-radius: 5px;
    font-size: 11.4px;
    font-weight: 700;
    cursor: pointer;
    text-align: left;
  }
  .mt-btn:hover { background: #EFF6FF; border-color: #1D4ED8; color: #1D4ED8; }
  .mt-btn.sel { background: #0F172A; color: #FFFFFF; border-color: #0F172A; }
  .mt-fb { display: none; margin-top: 6px; padding-top: 6px; border-top: 1px dashed #CBD5E1; font-size: 11.6px; line-height: 1.46; color: #1E293B; }
  .mt-qcard.answered .mt-fb { display: block; }

  /* Separación limpia en 3 pasos dentro de Modo Aprender: Tutor y Autoevaluación aparecen en Paso 3 (y siempre en Lab) */
  .wrap.mode-aprender.step-1 .tutor-box,
  .wrap.mode-aprender.step-1 .mt-box,
  .wrap.mode-aprender.step-2 .tutor-box,
  .wrap.mode-aprender.step-2 .mt-box { display: none !important; }
  .wrap.mode-aprender.step-3 .tutor-box,
  .wrap.mode-aprender.step-3 .mt-box { display: block !important; }
</style>
"""


JS_EXPANSION_DGT_RA2 = r"""
<script id="js-expansion-dgt-ra2">
(function() {
  if (window.__expansionDgtRa2Activa) return;
  window.__expansionDgtRa2Activa = true;

  const __ES_MODO_CATEDRA = __FLAG_MODO_CATEDRA__;

  // ==========================================================================
  // 1. CRONOGRAMA DGT 2026 (MODO DOCENTE LIMPIO vs. MODO ADMIN CON HITOS)
  // ==========================================================================
  const CALENDARIO_DGT = __ES_MODO_CATEDRA ? [
    { dt: "01 Sep", lbl: "Unidad I · Crecimiento Territorial, Polos e ILPES",   tipo: "cls", topicIdx: 0 },
    { dt: "22 Sep", lbl: "Unidad II · Localización: Von Thünen, Weber, Krugman", tipo: "cls", topicIdx: 2 },
    { dt: "06 Oct", lbl: "Unidad III · Disparidades REAT: Lorenz, Gini y Theil", tipo: "cls", topicIdx: 5 },
    { dt: "20 Oct", lbl: "Cierre RA1 · Síntesis Unidades I a III",              tipo: "cls", topicIdx: 5 },
    { dt: "10 Nov", lbl: "Unidad V · Ordenamiento Territorial y PROT",          tipo: "cls", topicIdx: 7 },
    { dt: "24 Nov", lbl: "Unidad VI · Indicadores de Desarrollo y CRITIC",      tipo: "cls", topicIdx: 9 },
    { dt: "04 Dic", lbl: "Unidad IV · SPL, Redes Dini y Cadenas CEPAL",         tipo: "new", topicIdx: 6 },
    { dt: "14–15 Dic", lbl: "Cierre RA2 · Síntesis Unidades IV a VI",           tipo: "new", topicIdx: 9 }
  ] : [
    { dt: "01 Sep", lbl: "Control 1 · U.I Crecimiento e ILPES",                 tipo: "cls",  topicIdx: 0 },
    { dt: "22 Sep", lbl: "Control 2 · U.II Localización y Mapas",               tipo: "cls",  topicIdx: 2 },
    { dt: "06 Oct", lbl: "Control 3 · U.III Disparidades y Convergencia",       tipo: "cls",  topicIdx: 5 },
    { dt: "20 Oct", lbl: "Evaluación Producto RA1 · Unidades I a III",          tipo: "eval", topicIdx: 5 },
    { dt: "10 Nov", lbl: "Control 5 · U.V Ordenamiento Territorial",            tipo: "eval", topicIdx: 7 },
    { dt: "24 Nov", lbl: "Taller U.VI · Ponderación CRITIC (R)",                tipo: "cls",  topicIdx: 9 },
    { dt: "04 Dic", lbl: "Control 4 (Vie 11:59) · Redes Dini + Cadenas CEPAL",  tipo: "new",  topicIdx: 6 },
    { dt: "14–15 Dic", lbl: "Evaluación Producto RA2 · Unidades IV a VI",       tipo: "eval", topicIdx: 9 }
  ];

  function montarCalendarioDgt() {
    const studioBar = document.querySelector(".studio-bar");
    if (!studioBar || document.getElementById("cal-dgt-bar")) return;
    const det = document.createElement("details");
    det.id = "cal-dgt-bar";
    det.className = "cal-bar";
    det.open = true;
    const pills = CALENDARIO_DGT.map(c => {
      const cls = c.tipo === "new" ? "cp-new" : (c.tipo === "eval" ? "cp-eval" : "");
      return `<button class="cal-pill ${cls}" onclick="abrirHitoDgt(${c.topicIdx})"><span class="cal-dt">${c.dt}</span><span>${c.lbl}</span></button>`;
    }).join("");
    const badgeTxt = __ES_MODO_CATEDRA ? "Unidades I a VI · 2026-2SEM" : "Próximo hito: Vie 4 Dic · Control 4";
    det.innerHTML = `
      <summary>
        <span>Cronograma DGT 2026 (2026-2SEM) y Fechas por Unidad — Clic en cualquier fecha para abrir su simulador</span>
        <span class="cal-badge-new">${badgeTxt}</span>
      </summary>
      <div class="cal-strip">${pills}</div>
    `;
    studioBar.parentNode.insertBefore(det, studioBar.nextSibling);
  }

  window.abrirHitoDgt = function(topicIdx) {
    if (typeof setStudioMode === "function" && studioMode !== "aprender") setStudioMode("aprender");
    if (typeof selectLearnTopic === "function") selectLearnTopic(topicIdx);
  };

  // ==========================================================================
  // 2. BARRA DE ACCESO RÁPIDO EN 1 CLIC (4 MODELOS ESTRELLA)
  // ==========================================================================
  function montarInicioRapidoDgt() {
    const learnShell = document.querySelector(".learn-shell");
    if (!learnShell || document.getElementById("qs-dgt-bar")) return;
    const qs = document.createElement("div");
    qs.id = "qs-dgt-bar";
    qs.className = "qs-shell";
    qs.innerHTML = `
      <div class="qs-head">
        <span class="qs-tit">Acceso Rápido en 1 Clic — 4 Modelos Clave del Curso</span>
        <span class="qs-hint">Cómo usar: 1) Elige un modelo · 2) Interactúa con el gráfico · 3) Avanza a Fórmulas y Autoevaluación</span>
      </div>
      <div class="qs-grid">
        <button class="qs-btn" data-qs="weber" style="border-left-color:#1D4ED8;" onclick="irModeloDgt('weber')">
          <b>1. Localización (Weber / Krugman)</b>
          <span>Índice IM, isodápana crítica y τ*</span>
        </button>
        <button class="qs-btn" data-qs="lorenz" style="border-left-color:#DC2626;" onclick="irModeloDgt('lorenz')">
          <b>2. Disparidades (Lorenz / Gini / Theil)</b>
          <span>Desigualdad REAT y primacía IP4</span>
        </button>
        <button class="qs-btn" data-qs="dini" style="border-left-color:#7C3AED;" onclick="irModeloDgt('dini')">
          <b>3. Redes Dini y Cadenas CEPAL (U.IV)</b>
          <span>Densidad, GC, gobernanza y upgrading</span>
        </button>
        <button class="qs-btn" data-qs="critic" style="border-left-color:#059669;" onclick="irModeloDgt('critic')">
          <b>4. OT Rondinelli y CRITIC (U.V–U.VI)</b>
          <span>Ponderación objetiva 2017–2024</span>
        </button>
      </div>
    `;
    learnShell.parentNode.insertBefore(qs, learnShell);
  }

  function syncQsDgt(key) {
    document.querySelectorAll("#qs-dgt-bar .qs-btn").forEach(b => {
      b.classList.toggle("active", b.dataset.qs === key);
    });
  }

  window.irModeloDgt = function(key) {
    if (typeof setStudioMode === "function" && studioMode !== "aprender") setStudioMode("aprender");
    if (key === "weber") selectLearnTopic(2);
    else if (key === "lorenz") selectLearnTopic(5);
    else if (key === "dini") selectLearnTopic(6);
    else if (key === "critic") selectLearnTopic(9);
    syncQsDgt(key);
  };

  // ==========================================================================
  // 3. TUTORES PALABRALES + SÍNTESIS ORAL + AUTOEVALUACIÓN EN VIVO (10 PREG.)
  // ==========================================================================
  const DGT_MT_BANK = {
    c4: [
      {
        id: "c4_1",
        q: "1. Según Dini (2010, CEPAL hasta secc. 1.3), ¿qué diferencia una Red Empresarial de un Clúster y de un Sistema Productivo Local (SPL)?",
        opts: [
          "La Red es cooperación voluntaria entre empresas; el Clúster es aglomeración sectorial con masa crítica; y el SPL suma instituciones públicas, universidades y gremios del territorio",
          "Son sinónimos exactos que describen solo a grandes empresas exportadoras",
          "El SPL se compone únicamente de municipalidades sin participación de empresas privadas"
        ],
        ans: 0,
        why: "<b>Exacto (Dini, 2010):</b> son 3 círculos concéntricos: Red Empresarial (núcleo de cooperación) ⊂ Clúster (concentración geográfica sectorial) ⊂ SPL (tejido productivo + institucionalidad local)."
      },
      {
        id: "c4_2",
        q: "2. Según el Capítulo 3 de CEPAL (Cadenas de Valor), ¿qué diferencia el escalamiento (upgrading) de PROCESO del escalamiento FUNCIONAL?",
        opts: [
          "El de proceso mejora eficiencia/tecnología en la misma etapa; el funcional implica asumir nuevas etapas de mayor valor agregado (ej. diseño, marca o comercialización directa)",
          "El de proceso consiste en cambiar de industria y el funcional en reducir el personal",
          "Ambos se refieren únicamente a bajar precios mediante subsidios estatales"
        ],
        ans: 0,
        why: "<b>Clave de Control 4 (CEPAL Cap. 3):</b> el upgrading puede ser de proceso (hacerlo mejor), producto (más sofisticado), funcional (subir de eslabón en la cadena) o intersectorial (saltar a una cadena más rentable)."
      },
      {
        id: "c4_3",
        q: "3. En una red empresarial modelada en UCINET, ¿qué ocurre si la estructura es tipo estrella (Red con Liderazgo) con GC = 100%?",
        opts: [
          "Tiene máxima resiliencia ante la salida del líder porque todos los proveedores se conectan entre sí",
          "Coordina rápido los estándares, pero es altamente vulnerable porque si el nodo ancla desaparece la densidad cae a 0%",
          "La diagonal principal de la matriz debe llenarse con 1 para compensar al líder"
        ],
        ans: 1,
        why: "<b>Precisión UCINET + Dini:</b> la diagonal siempre es <b>A<sub>ii</sub> = 0</b>; en una estrella (GC = 100%), toda la conectividad pasa por un único líder, por lo que su salida desconecta a toda la base."
      },
      {
        id: "c4_4",
        q: "4. En el protocolo de entrevistas de campo para cadenas de valor (Control 4), ¿qué regla metodológica debe respetarse?",
        opts: [
          "Preguntar directamente al entrevistado por sus 'debilidades' y sugerirle que debe formarse un clúster",
          "Entrevistar a 3 actores de organizaciones distintas en al menos 2 eslabones (ej. 1 gremio + 2 empresas), preguntando por 'desafíos' sin inducir el término clúster",
          "Entrevistar a 3 personas de la misma empresa para obtener respuestas idénticas"
        ],
        ans: 1,
        why: "<b>Regla explícita de cátedra:</b> para evitar sesgo de inducción se cubren al menos 2 eslabones distintos y se indaga por <i>desafíos</i> o <i>aspectos por fortalecer</i>."
      }
    ],
    critic: [
      {
        id: "cr_1",
        q: "1. En el método CRITIC (Diakoulaki et al., 1995), ¿por qué una dimensión recibe un peso objetivo alto (w_j)?",
        opts: [
          "Porque combina alta desviación estándar (variabilidad entre regiones) con baja correlación frente al resto de dimensiones (mayor conflicto / menor redundancia)",
          "Porque está casi perfectamente correlacionada (r ≈ 0,99) con todas las demás dimensiones",
          "Porque el investigador elige manualmente los porcentajes según su preferencia"
        ],
        ans: 0,
        why: "<b>Fórmula central:</b> <i>C<sub>j</sub> = σ<sub>j</sub> · ∑(1 − r<sub>jk</sub>)</i>. Si <i>r<sub>jk</sub> → 1</i>, la dimensión repite información que ya traen otras y su término <i>(1 − r)</i> tiende a cero."
      },
      {
        id: "cr_2",
        q: "2. Al comparar el Índice de Desarrollo CRITIC entre 2017 y 2024 para evaluar Convergencia Beta y Sigma, ¿qué pesos deben aplicarse a los datos de 2024?",
        opts: [
          "Los pesos CRITIC fijos del año base (2017), para no cambiar la regla de medición entre períodos",
          "Pesos iguales (1/7) en 2024 y pesos CRITIC en 2017",
          "Solo las desviaciones estándar de 2024 sin multiplicar por la matriz normalizada"
        ],
        ans: 0,
        why: "<b>Consistencia intertemporal:</b> fijar <i>w<sub>2017</sub></i> garantiza que la variación del índice entre 2017 y 2024 refleje cambios reales en el territorio y no un reajuste de ponderadores."
      },
      {
        id: "cr_3",
        q: "3. Antes de ejecutar CRITIC sobre una matriz con Pobreza, Ingresos, Salud y Educación, ¿qué condición previa deben cumplir las variables?",
        opts: [
          "Deben estar normalizadas en [0, 1] y orientadas en el mismo sentido (mayor valor = mejor desempeño)",
          "Pueden mezclarse en pesos, porcentajes y años sin normalizar",
          "Pobreza debe dejarse en sentido inverso para que reste automáticamente"
        ],
        ans: 0,
        why: "<b>Requisito previo:</b> sin normalización [0, 1], una variable medida en miles tendría una σ artificialmente gigante; y sin orientación uniforme, el producto matricial <i>X · w</i> perdería coherencia."
      }
    ],
    ot_rd: [
      {
        id: "ot_1",
        q: "1. En la Matriz de Rondinelli (W_k = 100 / f_k), ¿por qué un equipamiento presente en solo 2 comunas otorga 50 puntos mientras uno presente en 10 comunas otorga solo 10 puntos?",
        opts: [
          "Porque los servicios más escasos representan mayor jerarquía y complejidad funcional en el sistema de ciudades",
          "Por un error de escala que se corrige dividiendo por la población",
          "Porque los servicios básicos siempre valen más que los especializados"
        ],
        ans: 0,
        why: "<b>Lógica de centralidad:</b> un equipamiento raro (ej. Hospital Tipo 1, Universidad o Aeropuerto) distingue a los lugares centrales de orden superior (Christaller)."
      },
      {
        id: "ot_2",
        q: "2. Si al armar el Escalograma de Guttman para las 10 comunas más pobladas notas que 'Farmacia' tiene valor 1 en las 10 filas, ¿qué corresponde hacer?",
        opts: [
          "Dejarla fija porque confirma que las 10 comunas son iguales",
          "Reemplazarla por un equipamiento de mayor jerarquía que sí discrimine entre comunas",
          "Cambiar todos los 1 por 0 para invertir la columna"
        ],
        ans: 1,
        why: "<b>Criterio de discriminación:</b> una variable presente en el 100% (o 0%) de las comunas no aporta diferenciación funcional y debe sustituirse."
      },
      {
        id: "ot_3",
        q: "3. ¿Cuál es la diferencia clave de codificación entre la Matriz de Rondinelli y la Matriz de Aislamiento Comunal?",
        opts: [
          "En Rondinelli 1 = presencia del servicio (positivo); en Aislamiento 0 = conexión vial directa asfaltada (positivo) y 1 = falta de conexión (aislamiento)",
          "En ambas matrices 1 significa siempre lo mismo (aislamiento)",
          "En ambas matrices se rellena la diagonal principal con 1"
        ],
        ans: 0,
        why: "<b>Trampa clásica de control:</b> en Aislamiento, un menor porcentaje de unos indica <b>mejor conectividad</b>; en Rondinelli, más unos (especialmente en servicios escasos) indican <b>mayor centralidad</b>."
      }
    ]
  };

  const dgtMtAns = {};

  function renderDgtMiniTest(blockKey, containerId, titulo) {
    const box = document.getElementById(containerId);
    if (!box) return;
    const qs = DGT_MT_BANK[blockKey] || [];
    let okBlock = 0, okAll = 0, totAll = 0;
    Object.keys(DGT_MT_BANK).forEach(bk => {
      DGT_MT_BANK[bk].forEach(q => {
        totAll++;
        if (dgtMtAns[q.id] === q.ans) okAll++;
      });
    });

    const cards = qs.map(q => {
      const u = dgtMtAns[q.id];
      const isAns = u !== undefined;
      const isOk = isAns && u === q.ans;
      if (isOk) okBlock++;
      const cls = isAns ? (" answered " + (isOk ? "ok" : "bad")) : "";
      const btns = q.opts.map((op, idx) =>
        `<button class="mt-btn ${u === idx ? 'sel' : ''}" onclick="responderDgtMt('${blockKey}','${q.id}',${idx},'${containerId}','${titulo.replace(/'/g, "\\'")}')">${op}</button>`
      ).join("");
      const stTxt = isAns ? `<span style="font-weight:800;font-size:11.3px;color:${isOk?'#15803D':'#DC2626'};margin-left:6px;">${isOk ? '✓ Correcto' : '✗ Revisa la lógica'}</span>` : "";
      return `
        <div class="mt-qcard${cls}">
          <div class="mt-qtxt">${q.q}${stTxt}</div>
          <div class="mt-opts">${btns}</div>
          <div class="mt-fb">${q.why}</div>
        </div>`;
    }).join("");

    box.innerHTML = `
      <div class="mt-head">
        <span class="mt-tit">Autoevaluación Conceptual en Vivo — ${titulo} (${okBlock}/${qs.length})</span>
        <span class="pill-score" style="font-size:11px;">Puntaje Total RA2: ${okAll} / ${totAll}</span>
      </div>
      ${cards}`;
  }

  window.responderDgtMt = function(bk, qId, optIdx, cid, tit) {
    dgtMtAns[qId] = optIdx;
    renderDgtMiniTest(bk, cid, tit);
  };

  window.toggleDgtOral = function(elId, btn) {
    const node = document.getElementById(elId);
    if (!node) return;
    const blurred = node.classList.toggle("oral-blur");
    if (btn) btn.textContent = blurred ? "Revelar texto" : "Modo Ciego (Practicar oral)";
  };

  function montarBloquesPalabrales() {
    // 1. Bloque Tutor + Autoevaluación en Unidad IV (#panel-dini — Control 4: Dini + CEPAL Cadenas de Valor)
    const pedDini = document.getElementById("ped-dini");
    if (pedDini && !document.getElementById("dgt-tutor-c4")) {
      const htmlC4 = `
        <div id="dgt-tutor-c4" class="tutor-box">
          <div class="tutor-head">
            <span class="tutor-tit">Tutor Conceptual — Redes Empresariales (Dini, 2010) y Cadenas de Valor (CEPAL Cap. 3)</span>
            <span class="enun-badge">Unidad IV · Lecturas Control 4 (40%)</span>
          </div>
          <div class="tutor-prose">
            <p><span class="conn-tag">En primer lugar</span> las pequeñas empresas suelen fracasar al competir aisladas por falta de escala y acceso tecnológico; <b>sin embargo</b>, al asociarse voluntariamente forman una <b>Red Empresarial</b> (Dini, 2010), que cuando alcanza masa crítica sectorial da origen a un <b>Clúster</b> y, al integrarse con universidades, gremios y gobierno local, configura un <b>Sistema Productivo Local (SPL)</b>.</p>
            <p><span class="conn-tag ct-ok">En paralelo (CEPAL, Cap. 3)</span> el enfoque de <b>Cadenas de Valor</b> mira el recorrido completo desde insumos hasta el consumidor final para detectar <b>cuellos de botella (restricciones)</b>, identificar quién ejerce la <b>gobernanza</b> (el actor que fija estándares, precios y plazos) y diseñar estrategias de <b>escalamiento (upgrading)</b> de proceso, producto, funcional o intersectorial.</p>
            <p><span class="conn-tag ct-purp">Por lo tanto</span> en el análisis de redes (UCINET) no basta con medir <b>Densidad (D)</b>: también debes observar el <b>Gradiente de Concentración (GC)</b> para distinguir una red simétrica horizontal (GC ≈ 0%) de una red dependiente de un líder único (GC = 100%).</p>
          </div>
          <div class="tutor-cols">
            <div class="comp-card">
              <div class="comp-card-tit">Precisiones Conceptuales (No confundir)</div>
              <div class="comp-item"><b>Cooperación horizontal vs. vertical (Schmitz):</b> horizontal une a pares del mismo eslabón (ej. compras conjuntas en Aproleche/PymeMad); vertical une proveedor con comprador a lo largo de la cadena.</div>
              <div class="comp-item"><b>Upgrading de proceso vs. funcional (CEPAL):</b> de proceso produce más eficiente en el mismo eslabón; funcional implica asumir nuevas funciones de mayor valor (diseño, marca, comercialización directa).</div>
            </div>
            <div class="oral-card">
              <div class="oral-head">
                <span class="oral-tit">Síntesis Oral (30 seg)</span>
                <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleDgtOral('oral-dgt-c4', this)">Modo Ciego (Practicar oral)</button>
              </div>
              <div id="oral-dgt-c4">
                "<b>En primer lugar</b>, Dini (2010) distingue tres escalas de articulación: la red empresarial (cooperación entre pares), el clúster (masa crítica sectorial localizada) y el SPL (que suma institucionalidad territorial). <b>Complementariamente</b>, CEPAL (Cap. 3) analiza la cadena de valor para identificar gobernanza, cuellos de botella y oportunidades de upgrading. <b>En consecuencia</b>, combinar cooperación horizontal y vínculos débiles externos permite a las PyMEs ganar eficiencia colectiva sin quedar atrapadas en dependencia de un solo líder."
              </div>
            </div>
          </div>
        </div>
        <div id="dgt-mt-c4" class="mt-box"></div>
      `;
      pedDini.insertAdjacentHTML("beforebegin", htmlC4);
      renderDgtMiniTest("c4", "dgt-mt-c4", "Unidad IV: Redes Dini (2010) y Cadenas de Valor (CEPAL)");
    }

    // 2. Bloque Tutor + Autoevaluación en Unidad VI CRITIC (#ped-u6-critic)
    const pedCr = document.getElementById("ped-u6-critic");
    if (pedCr && !document.getElementById("dgt-tutor-critic")) {
      const htmlCr = `
        <div id="dgt-tutor-critic" class="tutor-box">
          <div class="tutor-head">
            <span class="tutor-tit">Tutor Conceptual — Ponderación Objetiva CRITIC (Diakoulaki et al., 1995)</span>
            <span class="enun-badge">Unidad VI · Taller R 2017 vs. 2024</span>
          </div>
          <div class="tutor-prose">
            <p><span class="conn-tag">¿Por qué nace CRITIC?</span> Cuando construyes un índice de desarrollo regional con varias dimensiones, asignar pesos "a ojo" (50/50 o 70/30) introduce subjetividad; <b>en cambio</b>, CRITIC deriva los pesos directamente desde los datos normalizados en [0, 1].</p>
            <p><span class="conn-tag ct-ok">En otras palabras</span> una dimensión aporta más información cuando cumple dos condiciones simultáneas: tiene alta <b>variabilidad entre regiones (σ<sub>j</sub>)</b> y baja <b>redundancia con las demás dimensiones ∑(1 − r<sub>jk</sub>)</b>. <span class="conn-tag ct-warn">Por esa razón</span> en el taller de 2017 <b>Pobreza</b> obtuvo el mayor peso (24,72%) y <b>Salud</b> el menor (9,14%).</p>
            <p><span class="conn-tag ct-purp">Finalmente, al comparar en el tiempo</span> para evaluar si las 16 regiones convergieron entre 2017 y 2024 debes aplicar los <b>pesos fijos de 2017</b> sobre la matriz normalizada de 2024.</p>
          </div>
          <div class="tutor-cols">
            <div class="comp-card">
              <div class="comp-card-tit">Precisiones Conceptuales (No confundir)</div>
              <div class="comp-item"><b>Correlación alta ≠ Mayor peso:</b> al revés, si dos dimensiones se mueven casi igual (r → 1), se vuelven redundantes y CRITIC <b>reduce</b> su ponderación.</div>
              <div class="comp-item"><b>Pesos fijos vs. recalculados:</b> recalcular CRITIC en 2024 sirve para ver cambios de estructura, pero <b>fijar w<sub>2017</sub></b> es obligatorio para medir Convergencia β y σ con la misma vara.</div>
            </div>
            <div class="oral-card">
              <div class="oral-head">
                <span class="oral-tit">Síntesis Oral (30 seg)</span>
                <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleDgtOral('oral-dgt-cr', this)">Modo Ciego (Practicar oral)</button>
              </div>
              <div id="oral-dgt-cr">
                "<b>Primero</b>, normalizamos todas las dimensiones en [0, 1] con orientación favorable. <b>Luego</b>, CRITIC calcula el contenido informativo C<sub>j</sub> multiplicando la desviación estándar de cada dimensión por la suma de (1 − r<sub>jk</sub>), premiando la variabilidad y castigando la redundancia. <b>Por último</b>, al mantener fijos los pesos de 2017 sobre 2024 verificamos convergencia territorial tanto en β (pendiente negativa) como en σ (menor dispersión)."
              </div>
            </div>
          </div>
        </div>
        <div id="dgt-mt-critic" class="mt-box"></div>
      `;
      pedCr.insertAdjacentHTML("beforebegin", htmlCr);
      renderDgtMiniTest("critic", "dgt-mt-critic", "Unidad VI: Método CRITIC y Convergencia 2017–2024");
    }

    // 3. Bloque Tutor + Autoevaluación en Unidad V OT Rondinelli (#ped-ot-rd)
    const pedOt = document.getElementById("ped-ot-rd");
    if (pedOt && !document.getElementById("dgt-tutor-ot")) {
      const htmlOt = `
        <div id="dgt-tutor-ot" class="tutor-box">
          <div class="tutor-head">
            <span class="tutor-tit">Tutor Conceptual — Escalograma de Guttman, Matriz de Rondinelli y Aislamiento (OT)</span>
            <span class="enun-badge">Unidad V · Ordenamiento Territorial y PROT</span>
          </div>
          <div class="tutor-prose">
            <p><span class="conn-tag">En primer lugar</span> el tamaño poblacional por sí solo no dice qué servicios ofrece una ciudad; <b>por ello</b> la Matriz de Rondinelli registra presencia (<code>1</code>) o ausencia (<code>0</code>) de equipamientos dentro de una misma dimensión (unidimensionalidad de Guttman).</p>
            <p><span class="conn-tag ct-ok">A continuación</span> cada equipamiento recibe un peso inverso a su frecuencia (<b>W<sub>k</sub> = 100 / f<sub>k</sub></b>): <b>en consecuencia</b>, los servicios más escasos (ej. Hospital Tipo 1, Universidad o Aeropuerto) otorgan la mayor centralidad funcional.</p>
          </div>
          <div class="tutor-cols">
            <div class="comp-card">
              <div class="comp-card-tit">Precisiones Conceptuales (No confundir)</div>
              <div class="comp-item"><b>Rondinelli (1=Bueno) vs. Aislamiento (0=Bueno):</b> en Rondinelli el <code>1</code> suma centralidad; en la Matriz de Aislamiento el <code>0</code> indica conexión vial asfaltada directa y el <code>1</code> penaliza falta de conexión.</div>
              <div class="comp-item"><b>Variable con puros 1:</b> si todas las comunas del Top 10 tienen un servicio básico (ej. farmacia), no discrimina y debe reemplazarse.</div>
            </div>
            <div class="oral-card">
              <div class="oral-head">
                <span class="oral-tit">Síntesis Oral (30 seg)</span>
                <button class="act-btn" style="padding:2px 7px;font-size:10.5px;" onclick="toggleDgtOral('oral-dgt-ot', this)">Modo Ciego (Practicar oral)</button>
              </div>
              <div id="oral-dgt-ot">
                "<b>Para diagnosticar la jerarquía urbana</b>, combinamos tres herramientas: el Ranking y Primacía IP<sub>4</sub> miden concentración demográfica; la Matriz de Rondinelli mide complejidad funcional ponderando por escasez (W<sub>k</sub> = 100/f<sub>k</sub>) en una escala unidimensional de Guttman; y la Matriz de Aislamiento evalúa conectividad vial directa (0 = asfaltada, 1 = sin conexión) para orientar las prioridades del PROT."
              </div>
            </div>
          </div>
        </div>
        <div id="dgt-mt-ot" class="mt-box"></div>
      `;
      pedOt.insertAdjacentHTML("beforebegin", htmlOt);
      renderDgtMiniTest("ot_rd", "dgt-mt-ot", "Unidad V: Guttman, Rondinelli y Aislamiento");
    }
  }

  // ==========================================================================
  // 4. SUMAR 2 RETOS CONCEPTUALES EN MODO PRACTICAR (RETOS 9 Y 10: CONTROL 4 Y CRITIC)
  // ==========================================================================
  function expandirRetosDgt() {
    if (Array.isArray(PRAC_RETOS) && !PRAC_RETOS.some(r => r.id === "tr9")) {
      PRAC_RETOS.push(
        {
          id: "tr9", topicIdx: 6, short: "9. Control 4 Cadenas",
          title: "Control 4 — Redes Empresariales (Dini 2010) y Cadenas de Valor (CEPAL Cap. 3)",
          enun: "Comprueba tu dominio de las lecturas oficiales del <b>Control 4 (40%)</b>: Dini (2010, hasta sección 1.3) y CEPAL Cadenas de Valor (Capítulo 3).",
          qs: [
            { lbl: "1. ¿Qué concepto agrega universidades, gremios e instituciones locales al tejido de empresas?", type: "sel", opts: ["Seleccionar...", "Sistema Productivo Local (SPL)", "Red Bilateral", "Enclave Extractivo"], ans: "Sistema Productivo Local (SPL)" },
            { lbl: "2. En CEPAL Cap. 3, pasar de solo producir materia prima a diseñar marca y vender directo es:", type: "sel", opts: ["Seleccionar...", "Escalamiento (Upgrading) Funcional", "Escalamiento de Proceso", "Bloqueo Cognitivo (Lock-in)"], ans: "Escalamiento (Upgrading) Funcional" },
            { lbl: "3. En UCINET, una red no dirigida de n=6 empresas en estrella (L=5) tiene Densidad D (%) igual a:", type: "num", ans: 33.3, tol: 0.03, ph: "ej. 33.3" }
          ],
          hint: "<b>Pista:</b> D = 2L / [n(n−1)] × 100 = (2×5)/(6×5)×100. Red ⊂ Clúster ⊂ SPL. Asumir nuevas etapas de mayor valor = Upgrading Funcional.",
          sol: "1) <b>Sistema Productivo Local (SPL)</b> | 2) <b>Upgrading Funcional</b> | 3) D = 10/30 = <b>33,3%</b> (con GC = 100%)."
        },
        {
          id: "tr10", topicIdx: 9, short: "10. CRITIC & OT",
          title: "Síntesis RA2 — Método CRITIC (U.VI) y Ordenamiento Territorial (U.V)",
          enun: "En un cálculo CRITIC, una dimensión tiene <b>σ<sub>j</sub> = 0,30</b> y suma de conflictos <b>∑(1 − r<sub>jk</sub>) = 4,0</b> (con suma total ∑C = 4,80). Además, en Rondinelli un equipamiento existe en <b>4 comunas</b>.",
          qs: [
            { lbl: "1. Contenido informativo C_j = σ_j × ∑(1 − r_jk)", type: "num", ans: 1.2, tol: 0.02, ph: "ej. 1.2" },
            { lbl: "2. Peso objetivo CRITIC w_j (%) = (C_j / 4,80) × 100", type: "num", ans: 25, tol: 0.02, ph: "ej. 25" },
            { lbl: "3. Peso Rondinelli W_k = 100 / f_k para un servicio presente en 4 comunas", type: "num", ans: 25, tol: 0.02, ph: "ej. 25" },
            { lbl: "4. Para medir Convergencia 2017 → 2024 con CRITIC, ¿qué pesos aplicas a 2024?", type: "sel", opts: ["Seleccionar...", "Los pesos CRITIC fijos del año base (2017)", "Pesos iguales 1/7", "Solo la varianza de 2024"], ans: "Los pesos CRITIC fijos del año base (2017)" }
          ],
          hint: "<b>Pista:</b> C_j = 0,30 × 4,0; w_j = C_j / 4,80; W_k = 100 / 4. Para comparar en el tiempo la vara de medición debe mantenerse fija.",
          sol: "C_j = <b>1,20</b> | w_j = 1,20/4,80 = <b>25%</b> | W_k = 100/4 = <b>25 pts</b> | Pesos fijos del año base (<b>2017</b>)."
        }
      );
      if (typeof saveStudioProg === "function") saveStudioProg();
      const btnRetos = document.getElementById("pr-sub-retos");
      if (btnRetos) btnRetos.textContent = `Retos Numéricos y Conceptuales (${PRAC_RETOS.length})`;
    }
  }

  montarCalendarioDgt();
  montarInicioRapidoDgt();
  montarBloquesPalabrales();
  expandirRetosDgt();
})();
</script>
"""


def inyectar_expansion_dgt_ra2(html_base: str, modo_catedra: bool = False) -> str:
    """Inyecta de forma segura el cronograma DGT, acceso rápido 1 clic y bloques palabrales/testeo RA2."""
    if not html_base or 'id="js-expansion-dgt-ra2"' in html_base:
        return html_base

    js_in = JS_EXPANSION_DGT_RA2.replace("__FLAG_MODO_CATEDRA__", "true" if modo_catedra else "false")
    html_out = html_base
    if "</head>" in html_out:
        html_out = html_out.replace("</head>", CSS_EXPANSION_DGT_RA2 + "\n</head>", 1)
    else:
        html_out = CSS_EXPANSION_DGT_RA2 + html_out

    idx_body = html_out.rfind("</body>")
    if idx_body != -1:
        html_out = html_out[:idx_body] + js_in + "\n" + html_out[idx_body:]
    else:
        html_out = html_out + js_in
    return html_out
