# -*- coding: utf-8 -*-
"""
PLATAFORMA INTEGRAL DE DESARROLLO Y GESTIÓN TERRITORIAL 2026
Universidad de Los Lagos — Ingeniería Comercial
Asignatura: Desarrollo y Gestión Territorial (Prof. Claudio Mancilla)
Archivo 2 de 2 (Principal): app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import motor_sii_exportador as msii
from motor_laboratorio_catedra import renderizar_laboratorio_catedra
from motor_redes_territorio_ot import renderizar_redes_territorio_ot, _renderizar_mapa_puntos_seguro
from motor_redes_dinamicas_dini import (
    renderizar_extension_redes_y_gradientes,
    renderizar_burbuja_tip,
    inyectar_estilos_burbujas,
)


# ==============================================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILO INSTITUCIONAL LIMPIO
# ==============================================================================
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
        border: 1px solid #e2eeb0;
        border-color: #e2e8f0;
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


# ==============================================================================
# UTILIDADES PARA CARGA POR DEFECTO DEL CASO BIOBÍO (2014 - 2024)
# ==============================================================================
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


# ==============================================================================
# MÓDULO 1: TÉCNICAS DE ANÁLISIS REGIONAL (ILPES / SII BIOBÍO 2014-2024)
# ==============================================================================
def vista_modulo_1_ilpes():
    st.header("1. Técnicas de Análisis Regional (ILPES / SII 2014–2024)")
    st.markdown(
        "Evaluación estructural e intertemporal mediante matrices sectoriales-comunales del SII: "
        "**Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)**, "
        "**Coeficiente de Reestructuración ($CR_r$)**, **Base Económica Exportadora ($X_j, M_j$)**, "
        "**Cuadrantes de Silva Lira (CEPAL, 2005)** y **Shift & Share (MADE Clásico y Modificado)**."
    )

    if not os.path.exists(ARCHIVO_EXCEL_REPO):
        st.warning(
            f"No se encontró `{ARCHIVO_EXCEL_REPO}` en la raíz. "
            "Dirígete al Módulo 5 (Exportador SII) para subir un archivo manualmente."
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
                "- **Eje X (Peso Inicial):** Compara la cuota comunal inicial con el promedio regional ($100\\% / N$).\n"
                "- **Eje Y (Dinamismo):** Compara el crecimiento comunal con la tasa regional.\n"
                "- **I. Dinámica (+,+):** Alto peso y crece más que la región.\n"
                "- **II. Emergente (-,+):** Bajo peso pero crece rápido (convergente).\n"
                "- **III. Estancada (+,-):** Alto peso pero crece lento.\n"
                "- **IV. En Retroceso (-,-):** Bajo peso y rezagada."
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
        part_ini = (df_ss[f"Nivel_{a0}"] / max(tot["total_reg_0"], 1e-9)) * 100.0
        part_prom = 100.0 / max(tot["n_comunas"], 1)
        df_ss["Participacion_Inicial_%"] = part_ini

        fig_silva = px.scatter(
            df_ss,
            x="Participacion_Inicial_%",
            y="Var_Porcentual_%",
            color="Cuadrante_Silva_Lira",
            hover_name="Comuna",
            size=np.maximum(df_ss[f"Nivel_{at}"], 1.0),
            labels={
                "Participacion_Inicial_%": f"Participación Comunal Inicial {a0} (%)",
                "Var_Porcentual_%": f"Crecimiento Acumulado {a0}-{at} (%)",
            },
            title=f"Clasificación Comunal en Cuadrantes de Silva Lira ({reg_sel}, {a0}–{at})",
        )
        fig_silva.add_hline(
            y=tot["tasa_var_reg"],
            line_dash="dash",
            line_color="#dc2626",
            annotation_text=f"Media Regional ({tot['tasa_var_reg']:.1f}%)",
        )
        fig_silva.add_vline(
            x=part_prom,
            line_dash="dash",
            line_color="#1d4ed8",
            annotation_text=f"Umbral Peso Medio ({part_prom:.2f}%)",
        )
        st.plotly_chart(fig_silva, use_container_width=True)

        resumen_cuad = (
            df_ss.groupby("Cuadrante_Silva_Lira")
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


# ==============================================================================
# MÓDULO 2: DISPARIDADES, CONCENTRACIÓN Y CONVERGENCIA REGIONAL (MOTOR REAT)
# ==============================================================================
def vista_modulo_2_reat():
    st.header("2. Disparidades, Concentración y Convergencia Regional (Motor REAT)")
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
   