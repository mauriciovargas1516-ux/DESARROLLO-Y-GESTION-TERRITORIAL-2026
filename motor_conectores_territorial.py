# -*- coding: utf-8 -*-
"""
motor_conectores_territorial.py — CAPA DE FLUIDEZ NARRATIVA Y CONECTORES VIVOS (60 FPS)
Módulo plug-and-play para DESARROLLO-Y-GESTION-TERRITORIAL-2026 (ULagos — Prof. Claudio Mancilla).
Inyecta sobre `HTML_TERRITORIAL_60FPS` (sin alterar cálculos base y sin emojis):
  - Franja de "Hilo Conductor Vivo" (3 pasos con conectores causales dinámicos) en:
    Perroux/Myrdal, Von Thünen, Weber, Krugman, Christaller/Granovetter, Lorenz/Gini/Theil/IP4,
    Redes Dini 2010, OT (Ranking, Rondinelli, Aislamiento) y Unidad VI (Mín-Máx y CRITIC).
"""


CSS_CONECTORES_TERRITORIAL = r"""
<style id="css-conectores-territorial">
  .hilo-box {
    background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
    border: 1px solid #BFDBFE;
    border-left: 4.5px solid #1D4ED8;
    border-radius: 8px;
    padding: 10px 13px;
    margin: 9px 0 9px 0;
  }
  .hilo-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 7px;
    flex-wrap: wrap;
  }
  .hilo-title {
    font-size: 11.4px;
    font-weight: 800;
    color: #1E3A8A;
    text-transform: uppercase;
    letter-spacing: 0.35px;
  }
  .hilo-sub {
    font-size: 11px;
    color: #475569;
    font-weight: 600;
  }
  .hilo-steps {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
  @media (max-width: 860px) {
    .hilo-steps { grid-template-columns: 1fr; }
  }
  .hilo-step {
    background: #FFFFFF;
    border: 1px solid #DBEAFE;
    border-top: 3px solid #1D4ED8;
    border-radius: 6px;
    padding: 8px 10px;
    font-size: 11.7px;
    line-height: 1.45;
    color: #1E293B;
  }
  .hilo-step.hs-p { border-top-color: #7C3AED; }
  .hilo-step.hs-g { border-top-color: #059669; }
  .hilo-step.hs-b { border-top-color: #1D4ED8; }
  .hilo-step.hs-r { border-top-color: #DC2626; }
  .hilo-step.hs-o { border-top-color: #EA580C; }
  .hilo-conn {
    display: inline-block;
    font-size: 10.2px;
    font-weight: 800;
    padding: 1.5px 7px;
    border-radius: 10px;
    margin-right: 5px;
    margin-bottom: 3px;
    vertical-align: middle;
  }
  .hc-p { background: #F3E8FF; color: #6B21A8; }
  .hc-g { background: #DCFCE7; color: #166534; }
  .hc-b { background: #DBEAFE; color: #1E40AF; }
  .hc-r { background: #FEE2E2; color: #991B1B; }
  .hc-o { background: #FFEDD5; color: #9A3412; }

  /* Visible en Paso 1, Paso 2 y Laboratorio Completo; oculto en Paso 3 (foco en Tutor y Autoevaluación) */
  .wrap.mode-aprender .panel .hilo-box { display: block; }
  .wrap.mode-aprender.step-3 .panel .hilo-box { display: none; }
</style>
"""


JS_CONECTORES_TERRITORIAL = r"""
<script id="js-conectores-territorial">
(function() {
  if (window.__conectoresTerritorialesActivos) return;
  window.__conectoresTerritorialesActivos = true;

  function ensureHiloBox(hiloId, beforeId) {
    let box = document.getElementById(hiloId);
    if (box) return box;
    const ref = document.getElementById(beforeId);
    if (!ref || !ref.parentNode) return null;
    box = document.createElement("div");
    box.id = hiloId;
    box.className = "hilo-box";
    ref.parentNode.insertBefore(box, ref);
    return box;
  }

  function renderHilo(hiloId, beforeId, titulo, subtitulo, steps) {
    const box = ensureHiloBox(hiloId, beforeId);
    if (!box) return;
    const stepsHtml = steps.map(s => `
      <div class="hilo-step ${s.cls || 'hs-b'}">
        <span class="hilo-conn ${s.cCls || 'hc-b'}">${s.conn}</span>${s.html}
      </div>
    `).join("");
    box.innerHTML = `
      <div class="hilo-head">
        <span class="hilo-title">${titulo}</span>
        <span class="hilo-sub">${subtitulo}</span>
      </div>
      <div class="hilo-steps">${stepsHtml}</div>
    `;
  }

  // 1. Perroux / Hirschman / Myrdal (Unidad I)
  const _origPx = window.drawPerroux;
  if (typeof _origPx === "function") {
    window.drawPerroux = function(...args) {
      const ret = _origPx.apply(this, args);
      const i0 = +document.getElementById("px-i0").value;
      const b = +document.getElementById("px-b").value;
      const f = +document.getElementById("px-f").value;
      const spPct = +document.getElementById("px-sp").value;
      const prop = Math.min(0.88, b + f);
      const mh = 1 / (1 - prop);
      const tot = i0 * mh, ind = tot - i0;
      const spread = ind * (spPct / 100), backwash = ind * ((100 - spPct) / 100) * 0.6;
      const saldo = spread - backwash;
      renderHilo("px-hilo", "px-fstrip",
        "Hilo Conductor Vivo — Polos de Crecimiento (Perroux, Hirschman y Myrdal)",
        "Unidad I · De la inversión motriz al saldo neto en la periferia",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Primero, el impulso", html: `La industria motriz inyecta <b>$${fmtInt(i0)} MM</b> con encadenamientos locales <b>b + f = ${fmtDec(prop*100,0)}%</b>.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Luego, el multiplicador", html: `Con <b>M<sub>H</sub> = ${fmtDec(mh,2)}x</b>, la producción regional escala hasta <b>$${fmtInt(tot)} MM</b> (+$${fmtInt(ind)} MM indirectos).` },
          { cls: saldo >= 0 ? "hs-g" : "hs-r", cCls: saldo >= 0 ? "hc-g" : "hc-r", conn: saldo >= 0 ? "3. En consecuencia (Spread)" : "3. Sin embargo (Backwash)",
            html: saldo >= 0
              ? `La difusión hacia comunas vecinas (+$${fmtInt(spread)}M) supera la absorción (−$${fmtInt(backwash)}M): saldo <b>+$${fmtInt(saldo)} MM</b> (Polo Integrador).`
              : `La absorción de factores (−$${fmtInt(backwash)}M) supera la difusión (+$${fmtInt(spread)}M): saldo <b>-$${fmtInt(Math.abs(saldo))} MM</b> (Enclave Extractivo).` }
        ]);
      return ret;
    };
  }

  // 2. Von Thünen (Unidad II)
  const _origVt = window.drawThunen;
  if (typeof _origVt === "function") {
    window.drawThunen = function(...args) {
      const ret = _origVt.apply(this, args);
      const cur = calcRadiosThunen(stateVt);
      renderHilo("vt-hilo", "vt-fstrip",
        "Hilo Conductor Vivo — Renta Locacional y Anillos Concéntricos (Von Thünen)",
        "Unidad II · Por qué el costo de flete ordena el suelo rural",
        [
          { cls: "hs-r", cCls: "hc-r", conn: "1. Primero, el flete manda", html: `Lechería/Intensiva tiene la pendiente más empinada (<b>−${fmtDec(stateVt.t1,1)}/km</b>), <b>por lo que</b> puja más alto cerca del mercado.` },
          { cls: "hs-b", cCls: "hc-b", conn: "2. Luego, los cortes LR", html: `Al alejarse, cede paso a Agroindustria en <b>${fmtDec(cur.r1,1)} km</b> y a Forestal en <b>${fmtDec(cur.r2,1)} km</b>.` },
          { cls: "hs-g", cCls: "hc-g", conn: "3. Finalmente, la frontera", html: `Más allá de <b>${fmtDec(cur.r3,1)} km</b> la renta locacional cae a cero y cesa la actividad económica rentable.` }
        ]);
      return ret;
    };
  }

  // 3. Alfred Weber (Unidad II)
  const _origWb = window.drawWeber;
  if (typeof _origWb === "function") {
    window.drawWeber = function(...args) {
      const ret = _origWb.apply(this, args);
      const w1 = +document.getElementById("wb-w1").value, w2 = +document.getElementById("wb-w2").value;
      const wm = +document.getElementById("wb-wm").value, ah = +document.getElementById("wb-ah").value;
      const im = (w1 + w2) / wm;
      const opt = solveWeber(w1, w2, wm);
      const extra = opt.costAtL - opt.costMin;
      const okL = ah > extra && ah > 0;
      renderHilo("wb-hilo", "wb-fstrip",
        "Hilo Conductor Vivo — Triángulo de Weber e Isodápana Crítica",
        "Unidad II · Cómo decide una fábrica entre insumos, mercado y salarios",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Calculamos IM", html: `Con <b>IM = (${w1}+${w2})/${wm} = ${fmtDec(im,2)}</b>, el proceso ${im > 1.05 ? "pierde peso (atracción hacia insumos)" : (im < 0.95 ? "gana peso (atracción hacia el mercado)" : "mantiene equilibrio intermedio")}.` },
          { cls: "hs-o", cCls: "hc-o", conn: "2. Medimos desvío a L", html: `Mover la planta desde P* al enclave laboral L cuesta <b>+$${fmtDec(extra,1)}/u</b> extra en flete frente a un ahorro salarial de <b>$${ah}/u</b>.` },
          { cls: okL ? "hs-g" : "hs-r", cCls: okL ? "hc-g" : "hc-r", conn: "3. En consecuencia",
            html: okL
              ? `Como L cae <b>dentro</b> de la isodápana crítica, conviene saltar a L (ganancia neta <b>+$${fmtDec(ah-extra,1)}/u</b>).`
              : `Como L queda <b>fuera</b> de la isodápana crítica, conviene permanecer en el mínimo de flete <b>P*</b>.` }
        ]);
      return ret;
    };
  }

  // 4. Krugman (Unidad II)
  const _origKr = window.drawKrugman;
  if (typeof _origKr === "function") {
    window.drawKrugman = function(...args) {
      const ret = _origKr.apply(this, args);
      const tau = +document.getElementById("kr-tau").value, esc = +document.getElementById("kr-esc").value, mov = +document.getElementById("kr-mov").value;
      const cur = calcKrugman(tau, esc, mov);
      const agl = tau <= cur.ust;
      renderHilo("kr-hilo", "kr-fstrip",
        "Hilo Conductor Vivo — Nueva Economía Geográfica (Krugman, 1991)",
        "Unidad II · Por qué bajar fletes puede vaciar la periferia",
        [
          { cls: "hs-o", cCls: "hc-o", conn: "1. Fijamos umbral τ*", html: `Con escala (${fmtDec(esc,1)}) y movilidad (${fmtDec(mov,1)}), el punto crítico de bifurcación se ubica en <b>τ* = ${fmtDec(cur.ust,2)}</b>.` },
          { cls: "hs-b", cCls: "hc-b", conn: "2. Comparamos con τ", html: `El costo de transporte actual es <b>τ = ${fmtDec(tau,1)}</b>, es decir <b>${agl ? "por debajo (τ ≤ τ*)" : "por encima (τ > τ*)"}</b> del umbral.` },
          { cls: agl ? "hs-r" : "hs-g", cCls: agl ? "hc-r" : "hc-g", conn: "3. En consecuencia",
            html: agl
              ? `Dominan las fuerzas <b>centrípetas</b>: la capital absorbe <b>${fmtDec(cur.cen,1)}%</b> de la actividad y surge macrocefalia.`
              : `Dominan las fuerzas <b>centrífugas</b>: la periferia conserva <b>${fmtDec(cur.per,1)}%</b> en un equilibrio espacial más disperso.` }
        ]);
      return ret;
    };
  }

  // 5. Christaller & Granovetter (Unidades II y IV)
  const _origCg = window.drawChrisGran;
  if (typeof _origCg === "function") {
    window.drawChrisGran = function(...args) {
      const ret = _origCg.apply(this, args);
      const pob = +document.getElementById("ch-pob").value, umb = +document.getElementById("ch-umb").value;
      const alc = +document.getElementById("ch-alc").value, dst = +document.getElementById("ch-dst").value;
      const f = +document.getElementById("gr-f").value, d = +document.getElementById("gr-d").value;
      const lck = Math.max(0, f * 10 - d * 12);
      renderHilo("cg-hilo", "cg-fstrip",
        "Hilo Conductor Vivo — Lugares Centrales (Christaller) y Puentes Débiles (Granovetter)",
        "Unidades II y IV · Masa crítica espacial + apertura a la innovación",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Regla Christaller", html: `Población (${fmtInt(pob)}) vs. Umbral (${fmtInt(umb)}) y Alcance (${alc} km) vs. Distancia (${dst} km): servicio <b>${pob >= umb && alc >= dst ? "viable" : "con brecha espacial"}</b>.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Estructura Granovetter", html: `La red local tiene <b>${f}/10</b> lazos fuertes (confianza) y <b>${d}/10</b> puentes débiles con centros I+D/mercados externos.` },
          { cls: lck > 40 ? "hs-r" : "hs-g", cCls: lck > 40 ? "hc-r" : "hc-g", conn: "3. En consecuencia",
            html: lck > 40
              ? `Riesgo de bloqueo cognitivo (<b>lock-in = ${fmtInt(lck)}%</b>): faltan puentes débiles para traer información no redundante.`
              : `Red abierta (<b>lock-in = ${fmtInt(lck)}%</b>): combina cohesión local con flujo constante de innovación externa.` }
        ]);
      return ret;
    };
  }

  // 6. Lorenz, Gini, Theil, HHI e IP4 (Unidades III y V)
  const _origLz = window.drawLorenz;
  if (typeof _origLz === "function") {
    window.drawLorenz = function(...args) {
      const ret = _origLz.apply(this, args);
      const arr = [1,2,3,4].map(i => Math.max(1, +document.getElementById("lz-p"+i+"-in").value || +document.getElementById("lz-p"+i).value));
      const desc = [...arr].sort((a,b) => b-a);
      const ip4 = desc[0] / Math.max(1, desc[1]+desc[2]+desc[3]);
      const cur = calcLorenz(arr, +document.getElementById("lz-al").value);
      renderHilo("lz-hilo", "lz-fstrip",
        "Hilo Conductor Vivo — Desigualdad (Gini/Theil) y Primacía Urbana (IP4)",
        "Unidades III y V · Leyendo la misma concentración desde 4 lentes complementarios",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Peso de la ciudad líder", html: `La mayor urbe concentra <b>${fmtDec(desc[0]/cur.tot*100,1)}%</b> del sistema Top 4, arrojando <b>IP<sub>4</sub> = ${fmtDec(ip4,3)}</b>.` },
          { cls: "hs-r", cCls: "hc-r", conn: "2. Brecha en Lorenz", html: `Al alejarse de la diagonal de 45°, el <b>Gini</b> llega a <b>${fmtDec(cur.gini,3)}</b> y la <b>Entropía de Theil</b> (descomponible) a <b>${fmtDec(cur.theil,3)}</b>.` },
          { cls: "hs-g", cCls: "hc-g", conn: "3. Número equivalente", html: `Con <b>HHI = ${fmtDec(cur.hhi,3)}</b> y <b>HK = ${fmtDec(cur.hk,2)}</b>, el sistema funciona como si tuviera solo ${fmtDec(cur.hk,2)} ciudades de igual tamaño.` }
        ]);
      return ret;
    };
  }

  // 7. Redes Dini 2010 (Unidad IV — Control 4)
  const _origDn = window.drawDini;
  if (typeof _origDn === "function") {
    window.drawDini = function(...args) {
      const ret = _origDn.apply(this, args);
      const n = diniNodes.length;
      const lMax = diniDirected ? n*(n-1) : n*(n-1)/2;
      const actEdges = diniQuiebraIdx === null ? diniEdges : diniEdges.filter(([u,v]) => u !== diniQuiebraIdx && v !== diniQuiebraIdx);
      const L = actEdges.length;
      const den = lMax > 0 ? (L / lMax) * 100 : 0;
      const adj = Array.from({length:n}, () => new Set());
      actEdges.forEach(([u,v]) => { adj[u].add(v); adj[v].add(u); });
      const deg = adj.map(s => s.size);
      const kMax = Math.max(0, ...deg);
      const gc = n > 2 ? (deg.reduce((s,v) => s + (kMax - v), 0) / ((n-1)*(n-2))) * 100 : 0;
      renderHilo("dn-hilo", "dn-fstrip",
        "Hilo Conductor Vivo — Densidad, Concentración y Resiliencia en Redes (Dini, 2010)",
        "Unidad IV · Control 4 (UCINET y Cadenas de Valor)",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Medimos cohesión (D)", html: `Con <b>n = ${n}</b> actores y <b>L = ${L}</b> vínculos (${diniDirected ? "dirigida" : "no dirigida"}), la densidad alcanza <b>D = ${fmtDec(den,1)}%</b>.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Medimos asimetría (GC)", html: `El nodo líder tiene <b>k<sub>máx</sub> = ${kMax}</b>, generando un gradiente <b>GC = ${fmtDec(gc,1)}%</b> (${gc < 15 ? "simétrica" : (gc > 68 ? "estrella / líder único" : "policéntrica / jerárquica")}).` },
          { cls: diniQuiebraIdx !== null || gc > 68 ? "hs-r" : "hs-g", cCls: diniQuiebraIdx !== null || gc > 68 ? "hc-r" : "hc-g", conn: "3. Lectura de política SPL",
            html: diniQuiebraIdx !== null
              ? `Al retirar al nodo ancla, la red perdió cohesión de inmediato; <b>por ello</b> Dini promueve vínculos horizontales entre PyMEs.`
              : (gc > 68
                ? `Alta eficiencia coordinadora; <b>sin embargo</b>, si se retira el líder la red colapsa (pruébalo con <i>Simular Quiebra</i>).`
                : `La cooperación horizontal reparte la conectividad entre varios actores y otorga resiliencia al territorio.`) }
        ]);
      return ret;
    };
  }

  // 8. OT Ranking, Rondinelli y Aislamiento (Unidad V)
  const _origOtRk = window.drawOtRanking;
  if (typeof _origOtRk === "function") {
    window.drawOtRanking = function(...args) {
      const ret = _origOtRk.apply(this, args);
      const pr1 = calcOtPrimacia(otRkRows.map(r => r.p1));
      const pr2 = calcOtPrimacia(otRkRows.map(r => r.p2));
      const dIp = pr2.ip4 - pr1.ip4;
      renderHilo("ot-rk-hilo", "ot-rk-fstrip",
        "Hilo Conductor Vivo — Ranking Intercensal y Primacía IP4 (OT)",
        "Unidad V · Diagnóstico de equilibrio urbano entre 2 censos",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Ordenamos 2 censos", html: `Comparamos las <b>${otRkRows.length} localidades</b> entre ${otRkC1Lbl} y ${otRkC2Lbl} para detectar cruces migratorios.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Calculamos IP4", html: `La primacía pasó de <b>${fmtDec(pr1.ip4,3)}</b> a <b>${fmtDec(pr2.ip4,3)}</b> (variación <b>${dIp>=0?"+":"-"}${fmtDec(Math.abs(dIp),3)}</b>).` },
          { cls: pr2.cod >= 2 ? "hs-o" : "hs-g", cCls: pr2.cod >= 2 ? "hc-o" : "hc-g", conn: "3. Estandarización (0–3)",
            html: `En la escala OT (0–3), la red clasifica en <b>Valor ${pr2.cod}: ${pr2.cat}</b>.` }
        ]);
      return ret;
    };
  }

  const _origOtRd = window.drawOtRond;
  if (typeof _origOtRd === "function") {
    window.drawOtRond = function(...args) {
      const ret = _origOtRd.apply(this, args);
      const n = otRdRows.length, m = otRdCols.length;
      const fk = new Array(m).fill(0);
      otRdRows.forEach(r => r.v.forEach((x,j) => { fk[j] += x; }));
      const bad = fk.filter(f => f === 0 || f === n).length;
      renderHilo("ot-rd-hilo", "ot-rd-fstrip",
        "Hilo Conductor Vivo — Escala de Guttman y Matriz de Rondinelli (OT)",
        "Unidad V · Jerarquía funcional por escasez de servicios (Wk = 100/fk)",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Matriz binaria 1/0", html: `Registramos presencia (<code>1</code>) o ausencia (<code>0</code>) de <b>${m} variables</b> en las <b>${n} localidades</b> más pobladas.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Ponderamos por escasez", html: `Cada servicio reparte 100 puntos entre quienes lo poseen (<b>W<sub>k</sub> = 100/f<sub>k</sub></b>): <b>por eso</b> un equipamiento raro pesa mucho más.` },
          { cls: bad > 0 ? "hs-r" : "hs-g", cCls: bad > 0 ? "hc-r" : "hc-g", conn: bad > 0 ? "3. Alerta de discriminación" : "3. Validación correcta",
            html: bad > 0
              ? `Hay <b>${bad} variable(s)</b> con puros 1 o puros 0; <b>por lo tanto</b> no discriminan y deben reemplazarse.`
              : `Todas las variables discriminan: al ordenar el escalograma aparece el patrón acumulativo de Guttman.` }
        ]);
      return ret;
    };
  }

  const _origOtAi = window.drawOtAisl;
  if (typeof _origOtAi === "function") {
    window.drawOtAisl = function(...args) {
      const ret = _origOtAi.apply(this, args);
      const n = otAiLocs.length;
      if (n > 0) {
        let tot1 = 0;
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) if (i !== j && otAiMat[i][j] === 1) tot1++;
        const avg = (tot1 / Math.max(1, n * (n - 1))) * 100;
        renderHilo("ot-ai-hilo", "ot-ai-fstrip",
          "Hilo Conductor Vivo — Conectividad Vial e Índice de Aislamiento (OT)",
          "Unidad V · Cuidado con el signo: 0 = Conectada · 1 = Aislada",
          [
            { cls: "hs-b", cCls: "hc-b", conn: "1. Matriz simétrica 0/1", html: `Evaluamos cada par de localidades (diagonal vacía): <b>0</b> indica ruta directa asfaltada y <b>1</b> ausencia de conexión directa.` },
            { cls: "hs-p", cCls: "hc-p", conn: "2. Promediamos unos", html: `Dividiendo la suma de unos por <b>n − 1 = ${n-1}</b>, el aislamiento promedio de esta red es <b>${fmtDec(avg,1)}%</b>.` },
            { cls: "hs-g", cCls: "hc-g", conn: "3. Impacto territorial", html: `Pavimentar un solo enlace cambia el par de <b>1 → 0</b> y reduce la fricción de la distancia en el PROT.` }
          ]);
      }
      return ret;
    };
  }

  // 9. Unidad VI (Mín-Máx y CRITIC)
  const _origU6 = window.drawIndicadoresU6;
  if (typeof _origU6 === "function") {
    window.drawIndicadoresU6 = function(...args) {
      const ret = _origU6.apply(this, args);
      const w1 = +document.getElementById("u6-w1").value;
      const outM = +document.getElementById("u6-out").value;
      renderHilo("u6-hilo", "u6-fstrip",
        "Hilo Conductor Vivo — Normalización Mín–Máx [0, 1] y Sensibilidad a Pesos",
        "Unidad VI (A) · Cómo unir variables en unidades distintas sin distorsionar",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Llevamos a [0, 1]", html: `Transformamos v1 (${u6Dir1===1?"Favorable +":"Desfavorable −"}) y v2 (${u6Dir2===1?"Favorable +":"Desfavorable −"}) a escala adimensional.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Ponderamos", html: `Combinamos <b>${w1}% v1 + ${100-w1}% v2</b> para ordenar las 15 provincias y medir cuántas cambian de puesto frente al 50/50.` },
          { cls: outM > 1.05 ? "hs-r" : "hs-g", cCls: outM > 1.05 ? "hc-r" : "hc-g", conn: outM > 1.05 ? "3. Efecto Outlier activo" : "3. Lectura clave",
            html: outM > 1.05
              ? `El outlier (<b>${fmtDec(outM,2)}x</b>) agranda el denominador (máx − mín) y <b>aplasta hacia 0</b> a las provincias intermedias.`
              : `Una provincia solo obtiene <b>1,000</b> si es líder simultáneo en todas las dimensiones.` }
        ]);
      return ret;
    };
  }

  const _origCr = window.drawCriticU6;
  if (typeof _origCr === "function") {
    window.drawCriticU6 = function(...args) {
      const ret = _origCr.apply(this, args);
      const mAct = criticActiveDims.filter(Boolean).length;
      const modoTxt = criticMode === "2017" ? "Año Base 2017" : (criticMode === "2024_fijo" ? "2024 con Pesos Fijos 2017" : "2024 CRITIC Recalculado");
      renderHilo("cr-hilo", "cr-fstrip",
        "Hilo Conductor Vivo — Ponderación Objetiva CRITIC (Diakoulaki et al., 1995)",
        "Unidad VI (B) · Variabilidad (σ) × No Redundancia ∑(1−r) en 16 Regiones",
        [
          { cls: "hs-b", cCls: "hc-b", conn: "1. Medimos información", html: `Sobre <b>${mAct} dimensiones</b> normalizadas en [0, 1], CRITIC multiplica dispersión (<b>σ<sub>j</sub></b>) por conflicto <b>∑(1 − r<sub>jk</sub>)</b>.` },
          { cls: "hs-p", cCls: "hc-p", conn: "2. Pesos 100% objetivos", html: `Las dimensiones con mayor contraste y menor correlación con las demás reciben mayor peso <b>w<sub>j</sub> = C<sub>j</sub> / ∑C</b> (sin subjetividad).` },
          { cls: criticMode === "2024_recalc" ? "hs-o" : "hs-g", cCls: criticMode === "2024_recalc" ? "hc-o" : "hc-g", conn: "3. Comparación 2017 → 2024",
            html: criticMode === "2024_recalc"
              ? `Estás en <b>${modoTxt}</b>: ojo, para medir convergencia real debes mantener fijos los pesos de 2017 (<b>2024 Pesos Fijos</b>).`
              : `En <b>${modoTxt}</b> la regla de medición se mantiene constante, confirmando <b>Convergencia β (−0,0721) y σ</b> entre 2017 y 2024.` }
        ]);
      return ret;
    };
  }

  // Disparo inicial de todos los conectores
  ["drawPerroux","drawThunen","drawWeber","drawKrugman","drawChrisGran","drawLorenz","drawDini","drawOtRanking","drawOtRond","drawOtAisl","drawIndicadoresU6","drawCriticU6"].forEach(fn => {
    try { if (typeof window[fn] === "function") window[fn](); } catch (e) {}
  });
})();
</script>
"""


def inyectar_conectores_territorial(html_base: str) -> str:
    """Inyecta de forma segura la capa de conectores narrativos vivos en el HTML 60 FPS territorial."""
    if not html_base or 'id="js-conectores-territorial"' in html_base:
        return html_base
    html_out = html_base
    if "</head>" in html_out:
        html_out = html_out.replace("</head>", CSS_CONECTORES_TERRITORIAL + "\n</head>", 1)
    else:
        html_out = CSS_CONECTORES_TERRITORIAL + html_out
    idx_body = html_out.rfind("</body>")
    if idx_body != -1:
        html_out = html_out[:idx_body] + JS_CONECTORES_TERRITORIAL + "\n" + html_out[idx_body:]
    else:
        html_out = html_out + JS_CONECTORES_TERRITORIAL
    return html_out
