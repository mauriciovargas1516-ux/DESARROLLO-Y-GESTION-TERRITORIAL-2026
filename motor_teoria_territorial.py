# -*- coding: utf-8 -*-
"""
Simulación de Teoría Regional y Economía Espacial
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Archivo: motor_teoria_territorial.py
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from motor_redes_dinamicas_dini import renderizar_burbuja_tip


def renderizar_modulo_teoria_avanzada():
    st.header("1. Fundamentos y Simulación Teórica Regional (Krugman, Perroux, Granovetter, Christaller)")
    st.markdown(
        "Modelamiento interactivo de los marcos teóricos de localización y desarrollo regional: "
        "**Nueva Economía Geográfica (Krugman, 1991)**, **Polos de Crecimiento y Multiplicadores (Perroux, Myrdal, Hirschman)**, "
        "**Fuerza de los Vínculos Débiles en Sistemas Productivos Locales (Granovetter, 1973)** y "
        "**Teoría de Lugares Centrales (Christaller, 1933)**."
    )

    tabs_teoria = st.tabs([
        "1. Nueva Economía Geográfica (Krugman)",
        "2. Polos y Multiplicadores (Perroux, Myrdal, Hirschman)",
        "3. Redes y Vínculos Débiles (Granovetter)",
        "4. Umbral y Alcance Urbano (Christaller)",
    ])

    # Pestaña 1: Nueva Economía Geográfica (Krugman, 1991)
    with tabs_teoria[0]:
        st.subheader("Modelo Centro-Periferia y Costos de Transporte (Paul Krugman, 1991)")
        st.markdown(
            "Evalúa el equilibrio espacial entre fuerzas centrípetas (economías de escala y tamaño de mercado) "
            "y fuerzas centrífugas (costos de transporte $\\tau$), identificando el umbral crítico en el que "
            "la actividad productiva se concentra en la capital regional (**macrocefalia**)."
        )

        renderizar_burbuja_tip(
            titulo_boton="Nota Metodológica: Fuerzas Centrípetas vs. Centrífugas",
            titulo_interno="Equilibrio Centro-Periferia (Krugman, 1991)",
            formula_latex=r"\text{Aglomeración Neta} = \text{Economías de Escala} + \text{Efecto Mercado Local} - \text{Costos de Transporte }(\tau)",
            explicacion_md=(
                "- **Costos de transporte altos ($\\tau > \\tau^*$):** Las empresas priorizan abastecer la demanda local desde cada comuna para evitar costos logísticos elevados, manteniendo una distribución territorial dispersa.\n"
                "- **Costos de transporte bajos ($\\tau \\le \\tau^*$):** Se vuelve rentable concentrar la planta productiva en el mercado de mayor tamaño (capital regional) para capturar economías de escala y despachar hacia la periferia."
            ),
        )

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            costo_transporte = st.slider(
                "1. Costo de Transporte (τ) [10 = Alto | 1 = Bajo]:",
                min_value=1.0,
                max_value=10.0,
                value=3.5,
                step=0.5,
                key="krug_tau",
            )
        with col_k2:
            economias_escala = st.slider(
                "2. Retornos Crecientes / Economías de Escala (1 a 10):",
                min_value=1.0,
                max_value=10.0,
                value=7.0,
                step=0.5,
                key="krug_escala",
            )
        with col_k3:
            movilidad_laboral = st.slider(
                "3. Movilidad Interregional del Trabajo (1 a 10):",
                min_value=1.0,
                max_value=10.0,
                value=6.5,
                step=0.5,
                key="krug_mov",
            )

        umbral_critico_tau = round(0.45 * economias_escala + 0.35 * movilidad_laboral, 2)
        presion_aglomeracion = (umbral_critico_tau - costo_transporte) * 1.35
        cuota_centro_pct = float(np.clip(50.0 + 42.0 / (1.0 + np.exp(-presion_aglomeracion)), 50.0, 95.0))
        if costo_transporte > umbral_critico_tau + 1.2:
            cuota_centro_pct = float(np.clip(50.0 + (umbral_critico_tau / max(costo_transporte, 1.0)) * 4.0, 50.0, 58.0))
        cuota_periferia_pct = 100.0 - cuota_centro_pct

        k1, k2, k3 = st.columns(3)
        k1.metric("Umbral Crítico de Transporte (τ*)", f"{umbral_critico_tau:.1f}", "Punto de bifurcación espacial")
        k2.metric(
            "Participación Capital Regional (Centro)",
            f"{cuota_centro_pct:.1f}%",
            " Régimen de Aglomeración" if costo_transporte <= umbral_critico_tau else "Equilibrio Disperso",
        )
        k3.metric(
            "Participación Comunas Periféricas",
            f"{cuota_periferia_pct:.1f}%",
            f"{cuota_periferia_pct - 50.0:+.1f} pp respecto a simetría",
        )

        if costo_transporte <= umbral_critico_tau:
            st.warning(
                f"**Diagnóstico Territorial (Concentración Centro-Periferia):** Con un costo de transporte $\\tau = {costo_transporte:.1f}$ "
                f"inferior al umbral crítico ($\\tau^* = {umbral_critico_tau:.1f}$), predominan las fuerzas centrípetas y "
                f"el nodo metropolitano concentra el **{cuota_centro_pct:.1f}%** de la actividad manufacturera y de servicios."
            )
        else:
            st.success(
                f"**Diagnóstico Territorial (Distribución Equilibrada):** Con un costo de transporte $\\tau = {costo_transporte:.1f}$ "
                f"superior al umbral crítico ($\\tau^* = {umbral_critico_tau:.1f}$), los costos de flete actúan como fuerza centrífuga "
                f"manteniendo una participación de **{cuota_centro_pct:.1f}%** en el centro y **{cuota_periferia_pct:.1f}%** en la periferia."
            )

        g_k1, g_k2 = st.columns(2)
        with g_k1:
            df_reparto = pd.DataFrame({
                "Territorio": ["Capital Regional (Centro)", "Comunas Periféricas"],
                "Participación Productiva (%)": [cuota_centro_pct, cuota_periferia_pct],
            })
            fig_bar_k = px.bar(
                df_reparto,
                x="Territorio",
                y="Participación Productiva (%)",
                color="Territorio",
                text_auto=".1f",
                range_y=[0, 100],
                color_discrete_sequence=["#1d4ed8", "#64748b"],
                title="Distribución Espacial de la Actividad: Centro vs. Periferia",
            )
            fig_bar_k.add_hline(y=50, line_dash="dash", line_color="#dc2626", annotation_text="Simetría (50%)")
            st.plotly_chart(fig_bar_k, use_container_width=True)

        with g_k2:
            tau_vec = np.linspace(1.0, 10.0, 80)
            cuota_vec = 50.0 + 42.0 / (1.0 + np.exp(-(umbral_critico_tau - tau_vec) * 1.6))
            fig_curva_k = go.Figure()
            fig_curva_k.add_trace(
                go.Scatter(
                    x=tau_vec,
                    y=cuota_vec,
                    mode="lines",
                    line=dict(color="#1d4ed8", width=3),
                    name="Cuota del Centro (%)",
                )
            )
            fig_curva_k.add_trace(
                go.Scatter(
                    x=[costo_transporte],
                    y=[cuota_centro_pct],
                    mode="markers+text",
                    text=[f"Parámetro actual ({cuota_centro_pct:.1f}%)"],
                    textposition="top center",
                    marker=dict(size=13, color="#dc2626", line=dict(width=2, color="#ffffff")),
                    name="Estado Evaluado",
                )
            )
            fig_curva_k.add_vline(
                x=umbral_critico_tau,
                line_dash="dash",
                line_color="#d97706",
                annotation_text=f"Umbral Crítico τ*={umbral_critico_tau:.1f}",
            )
            fig_curva_k.update_layout(
                title="Curva de Aglomeración Espacial según Costo de Transporte (τ)",
                xaxis_title="Costo de Transporte (τ)",
                yaxis_title="Participación de la Capital Regional (%)",
                yaxis_range=[45, 100],
            )
            st.plotly_chart(fig_curva_k, use_container_width=True)

    # Pestaña 2: Polos de Perroux, Causalidad de Myrdal y Encadenamientos de Hirschman
    with tabs_teoria[1]:
        st.subheader("Polos de Crecimiento, Causalidad Acumulativa y Encadenamientos (Perroux, Myrdal, Hirschman)")
        st.markdown(
            "Modela la propagación de un choque de inversión en una industria motriz (**Perroux**), cuantificando "
            "el multiplicador de encadenamientos hacia atrás y hacia adelante (**Hirschman**) y el saldo neto entre "
            "efectos de difusión (*Spread*) y absorción (*Backwash*) sobre las comunas vecinas (**Myrdal**)."
        )

        renderizar_burbuja_tip(
            titulo_boton="Nota Metodológica: Ecuaciones de Hirschman y Myrdal",
            titulo_interno="Multiplicador de Encadenamientos y Saldo Territorial",
            formula_latex=r"M_{\text{Hirschman}} = \frac{1}{1 - (b_{\text{atrás}} + f_{\text{adelante}})} \quad ; \quad \text{Saldo Periferia} = \text{Spread} - \text{Backwash}",
            explicacion_md=(
                "- **Perroux (1955):** El crecimiento regional se origina en unidades motrices dominantes con capacidad de inducir actividad en su entorno.\n"
                "- **Hirschman (1958):** El efecto multiplicador depende de la fracción de insumos adquiridos localmente ($b_{\\text{atrás}}$) y del procesamiento local de bienes intermedios ($f_{\\text{adelante}}$).\n"
                "- **Myrdal (1957):** Si la absorción de capital y mano de obra calificada (*Backwash*) supera las compras a comunas vecinas (*Spread*), el polo opera como enclave y amplía las disparidades."
            ),
        )

        caso_polo = st.selectbox(
            "Caso de referencia regional:",
            [
                "Caso 1: Clúster Forestal-Maderero PymeMad (Los Ángeles / Biobío)",
                "Caso 2: Complejo Agroindustrial Lácteo-Quesero (Osorno / Los Lagos)",
                "Caso 3: Enclave Extractivo con Baja Articulación Local",
            ],
            key="perroux_caso",
        )

        if "PymeMad" in caso_polo:
            def_inv, def_atras, def_adel, def_spread = 1000.0, 0.35, 0.25, 65
        elif "Lácteo" in caso_polo:
            def_inv, def_atras, def_adel, def_spread = 1200.0, 0.40, 0.22, 70
        else:
            def_inv, def_atras, def_adel, def_spread = 1000.0, 0.12, 0.08, 25

        c_p1, c_p2, c_p3, c_p4 = st.columns(4)
        with c_p1:
            inversion_inicial = st.number_input(
                "Inversión / Demanda Inicial (MM$):",
                min_value=100.0,
                max_value=50000.0,
                value=def_inv,
                step=100.0,
                key="h_inv",
            )
        with c_p2:
            enc_atras = st.slider(
                "Coeficiente Hacia Atrás b (0,05 a 0,45):",
                min_value=0.05,
                max_value=0.45,
                value=def_atras,
                step=0.05,
                key="h_atras",
            )
        with c_p3:
            enc_adelante = st.slider(
                "Coeficiente Hacia Adelante f (0,05 a 0,45):",
                min_value=0.05,
                max_value=0.45,
                value=def_adel,
                step=0.05,
                key="h_adel",
            )
        with c_p4:
            pct_difusion = st.slider(
                "Proporción de Difusión Regional — Spread (%):",
                min_value=0,
                max_value=100,
                value=def_spread,
                step=5,
                key="h_spread",
            )

        propension_local = min(enc_atras + enc_adelante, 0.88)
        multiplicador_h = 1.0 / (1.0 - propension_local)
        impacto_total = inversion_inicial * multiplicador_h
        efecto_indirecto = impacto_total - inversion_inicial

        difusion_mm = efecto_indirecto * (pct_difusion / 100.0)
        absorcion_mm = efecto_indirecto * ((100.0 - pct_difusion) / 100.0) * 0.6
        saldo_periferia = difusion_mm - absorcion_mm

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Multiplicador de Hirschman", f"{multiplicador_h:.2f}x", f"Retención local: {propension_local*100:.0f}%")
        p2.metric("Producción Total Inducida", f"{impacto_total:,.0f} MM$", f"+{efecto_indirecto:,.0f} MM$ indirectos")
        p3.metric("Efecto Difusión (Spread)", f"{difusion_mm:,.0f} MM$", "Demanda hacia comunas vecinas")
        p4.metric(
            "Saldo Neto en Periferia (Myrdal)",
            f"{saldo_periferia:+,.0f} MM$",
            "Polo Integrador (Spread > Backwash)" if saldo_periferia >= 0 else "Efecto Backwash Predominante",
        )

        rondas = ["Ronda 1 (Impulso Inicial)", "Ronda 2 (Proveedores Directos)", "Ronda 3 (Servicios Conexos)", "Ronda 4 (Demanda Inducida)", "Ronda 5 (Consolidado)"]
        impactos_ronda = [inversion_inicial * (propension_local ** r) for r in range(5)]
        acumulado_ronda = np.cumsum(impactos_ronda)

        df_rondas = pd.DataFrame({
            "Etapa del Multiplicador": rondas,
            "Impacto Marginal por Ronda (MM$)": np.round(impactos_ronda, 1),
            "Producción Acumulada Regional (MM$)": np.round(acumulado_ronda, 1),
        })

        fig_hirsch = px.bar(
            df_rondas,
            x="Etapa del Multiplicador",
            y=["Impacto Marginal por Ronda (MM$)", "Producción Acumulada Regional (MM$)"],
            barmode="group",
            text_auto=".0f",
            title="Propagación Iterativa del Efecto Multiplicador Regional (5 Rondas)",
        )
        st.plotly_chart(fig_hirsch, use_container_width=True)

    # Pestaña 3: Capital Social y Vínculos Débiles (Granovetter, 1973)
    with tabs_teoria[2]:
        st.subheader("Estructura de Red y Fuerza de los Vínculos Débiles (Mark Granovetter, 1973)")
        st.markdown(
            "Analiza el balance sociométrico entre **vínculos fuertes** (cohesión y confianza al interior del clúster comunal) "
            "y **vínculos débiles** (puentes interinstitucionales hacia universidades, centros de I+D y mercados externos) "
            "para prevenir el bloqueo cognitivo (*lock-in*)."
        )

        cg1, cg2 = st.columns(2)
        with cg1:
            vinculos_fuertes = st.slider(
                "1. Vínculos Fuertes Intralocales (Cohesión horizontal entre PyMEs) [1 a 10]:",
                min_value=1,
                max_value=10,
                value=8,
                key="gran_fuertes",
            )
        with cg2:
            vinculos_debiles = st.slider(
                "2. Vínculos Débiles Extralocales (Puentes hacia I+D, ULagos y mercados) [0 a 10]:",
                min_value=0,
                max_value=10,
                value=6,
                key="gran_debiles",
            )

        cohesion_interna = vinculos_fuertes * 10.0
        acceso_innovacion = min(100.0, vinculos_debiles * 11.5 + vinculos_fuertes * 2.0)
        riesgo_lockin = max(0.0, (vinculos_fuertes * 10.0) - (vinculos_debiles * 12.0))
        puntaje_spl = round(0.45 * cohesion_interna + 0.55 * acceso_innovacion - 0.30 * riesgo_lockin, 1)

        m_g1, m_g2, m_g3 = st.columns(3)
        m_g1.metric("Índice de Cohesión Local", f"{cohesion_interna:.0f} / 100", f"{vinculos_fuertes} enlaces internos")
        m_g2.metric("Acceso a Información No Redundante", f"{acceso_innovacion:.0f} / 100", f"{vinculos_debiles} puentes externos")
        m_g3.metric(
            "Riesgo de Bloqueo (Lock-in)",
            f"{riesgo_lockin:.0f}%",
            "Red endogámica" if riesgo_lockin > 40 else "Red abierta con puentes activos",
        )

        col_gr_grafo, col_gr_bar = st.columns([1.35, 1.0])
        with col_gr_grafo:
            nodos_locales = ["PyME Local 1", "PyME Local 2", "PyME Local 3", "PyME Local 4", "Gremio Local"]
            ang_loc = np.linspace(0, 2 * np.pi, 5, endpoint=False)
            x_loc = -1.0 + 0.55 * np.cos(ang_loc)
            y_loc = 0.55 * np.sin(ang_loc)

            nodos_ext = [
                "Universidad (ULagos)",
                "Centro I+D (INIA)",
                "Comprador Internacional",
                "Proveedor Tecnológico",
                "Agencia Fomento (CORFO)",
            ]
            x_ext = np.array([1.1, 1.25, 1.3, 1.25, 1.1])
            y_ext = np.array([0.75, 0.38, 0.0, -0.38, -0.75])

            pares_fuertes_posibles = [
                (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
                (0, 2), (1, 3), (2, 4), (0, 3), (1, 4),
            ]
            pares_debiles_posibles = [
                (4, 0), (0, 1), (1, 2), (2, 3), (4, 4),
                (3, 1), (0, 0), (2, 2), (1, 3), (3, 4),
            ]

            fx, fy = [], []
            for u, v in pares_fuertes_posibles[:vinculos_fuertes]:
                fx.extend([x_loc[u], x_loc[v], None])
                fy.extend([y_loc[u], y_loc[v], None])

            dx, dy = [], []
            for u_loc, v_ext in pares_debiles_posibles[:vinculos_debiles]:
                dx.extend([x_loc[u_loc], x_ext[v_ext], None])
                dy.extend([y_loc[u_loc], y_ext[v_ext], None])

            fig_red_gran = go.Figure()
            fig_red_gran.add_trace(
                go.Scatter(
                    x=fx, y=fy, mode="lines",
                    line=dict(width=3, color="#2563eb"),
                    name="Vínculos Fuertes (Cohesión Local)",
                )
            )
            fig_red_gran.add_trace(
                go.Scatter(
                    x=dx, y=dy, mode="lines",
                    line=dict(width=2.8, color="#dc2626", dash="dash"),
                    name="Vínculos Débiles (Puentes Externos)",
                )
            )
            fig_red_gran.add_trace(
                go.Scatter(
                    x=x_loc, y=y_loc, mode="markers+text",
                    text=nodos_locales, textposition="top center",
                    marker=dict(size=22, color="#1d4ed8", line=dict(width=2, color="#0f172a")),
                    name="Clúster Local",
                )
            )
            fig_red_gran.add_trace(
                go.Scatter(
                    x=x_ext, y=y_ext, mode="markers+text",
                    text=nodos_ext, textposition="middle right",
                    marker=dict(size=20, color="#059669", symbol="diamond", line=dict(width=2, color="#0f172a")),
                    name="Entidades Externas de Conocimiento",
                )
            )
            fig_red_gran.update_layout(
                title="Topología Sociométrica: Vínculos Fuertes vs. Puentes Débiles (Granovetter)",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.9, 2.3]),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.1, 1.1]),
                height=390,
                margin=dict(l=10, r=10, t=40, b=10),
                plot_bgcolor="#f8fafc",
                legend=dict(orientation="h", y=-0.12),
            )
            st.plotly_chart(fig_red_gran, use_container_width=True)

        with col_gr_bar:
            df_gran = pd.DataFrame({
                "Dimensión": [
                    "Cohesión Local",
                    "Innovación Externa",
                    "Riesgo Lock-in",
                    "Desempeño SPL",
                ],
                "Puntaje (0 a 100)": [cohesion_interna, acceso_innovacion, riesgo_lockin, max(0.0, puntaje_spl)],
            })
            fig_gran = px.bar(
                df_gran,
                x="Dimensión",
                y="Puntaje (0 a 100)",
                color="Dimensión",
                text_auto=".0f",
                range_y=[0, 105],
                title="Indicadores de Desempeño Sociométrico",
            )
            fig_gran.update_layout(height=390, showlegend=False)
            st.plotly_chart(fig_gran, use_container_width=True)

    # Pestaña 4: Teoría de Lugares Centrales (Christaller / Lösch)
    with tabs_teoria[3]:
        st.subheader("Teoría de Lugares Centrales: Umbral y Alcance (Walter Christaller, 1933)")
        st.markdown(
            "Contrasta la demanda demográfica comunal frente al **Umbral Mínimo (*Threshold*)** requerido para sostener "
            "un servicio urbano y verifica si la distancia vial hacia las localidades tributarias se encuentra dentro del "
            "**Alcance Máximo (*Range*)**."
        )

        renderizar_burbuja_tip(
            titulo_boton="Nota Metodológica: Condición de Viabilidad de Christaller",
            titulo_interno="Umbral de Demanda y Alcance Espacial",
            formula_latex=r"\text{Población Comunal} \ge \text{Umbral Mínimo} \quad \wedge \quad \text{Alcance Máximo (km)} \ge \text{Distancia Vial}",
            explicacion_md=(
                "- **Umbral (*Threshold*):** Población o masa crítica mínima necesaria para que el equipamiento opere sobre su punto de equilibrio.\n"
                "- **Alcance (*Range*):** Distancia máxima en kilómetros que la población está dispuesta a recorrer para acceder al servicio."
            ),
        )

        servicio_sel = st.selectbox(
            "Jerarquía del equipamiento o servicio urbano a evaluar:",
            [
                "1. Hospital de Alta Complejidad / Universidad (Servicio de Orden Superior)",
                "2. Centro de Negocios / Instituto Técnico / Banco Comercial (Orden Intermedio)",
                "3. CESFAM / Farmacia / Comercio Básico (Orden Inferior)",
            ],
            key="chris_serv",
        )

        if "Superior" in servicio_sel:
            umbral_def, alcance_def = 120000, 90
        elif "Intermedio" in servicio_sel:
            umbral_def, alcance_def = 30000, 45
        else:
            umbral_def, alcance_def = 5000, 15

        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1:
            pob_comuna = st.number_input(
                "Población Comuna + Área de Influencia:",
                min_value=1000,
                max_value=500000,
                value=37000,
                step=1000,
                key="ch_pob",
            )
        with cc2:
            umbral_min = st.number_input(
                "Umbral Mínimo Requerido (Hab.):",
                min_value=1000,
                max_value=300000,
                value=umbral_def,
                step=1000,
                key="ch_umb",
            )
        with cc3:
            alcance_max = st.slider(
                "Alcance Máximo del Servicio (km):",
                min_value=5,
                max_value=150,
                value=alcance_def,
                key="ch_alc",
            )
        with cc4:
            dist_real = st.slider(
                "Distancia de Localidades Vecinas (km):",
                min_value=2,
                max_value=150,
                value=35,
                key="ch_dist",
            )

        cumple_umbral = pob_comuna >= umbral_min
        cumple_alcance = alcance_max >= dist_real
        cobertura_pct = (pob_comuna / max(umbral_min, 1)) * 100.0

        if cumple_umbral and cumple_alcance:
            st.success(
                f"**Factibilidad Positiva (Cumple Umbral y Alcance):** La demanda disponible ({pob_comuna:,} hab.) supera el "
                f"**Umbral Mínimo** ({umbral_min:,} hab., cobertura del **{cobertura_pct:.1f}%**) y el **Alcance** "
                f"({alcance_max} km) cubre la distancia de desplazamiento de las localidades tributarias ({dist_real} km)."
            )
        elif not cumple_umbral:
            st.error(
                f"**Restricción de Umbral Demográfico:** La población del área ({pob_comuna:,} hab.) es inferior al "
                f"**Umbral Mínimo** exigido por el servicio ({umbral_min:,} hab., equivalente al {cobertura_pct:.1f}% del umbral). "
                "De acuerdo con la jerarquía de lugares centrales, este equipamiento se localiza en cabeceras provinciales o regionales."
            )
        else:
            st.warning(
                f"**Restricción de Alcance Espacial:** Aunque existe masa crítica demográfica, la distancia de las localidades "
                f"vecinas (**{dist_real} km**) excede el radio máximo de desplazamiento (**{alcance_max} km**)."
            )

        df_ch = pd.DataFrame({
            "Indicador": ["Población Disponible en el Área", "Umbral Mínimo Requerido (Christaller)"],
            "Habitantes": [pob_comuna, umbral_min],
        })
        fig_ch = px.bar(
            df_ch,
            x="Indicador",
            y="Habitantes",
            color="Indicador",
            text_auto=",",
            color_discrete_sequence=["#059669" if cumple_umbral else "#dc2626", "#1e293b"],
            title="Evaluación de Umbral Demográfico (Demanda Local vs. Umbral Mínimo)",
        )
        st.plotly_chart(fig_ch, use_container_width=True)
