# -*- coding: utf-8 -*-
"""
MÓDULO DE SIMULACIÓN INTERACTIVA DE TEORÍA REGIONAL AVANZADA
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Archivo: motor_teoria_territorial.py

Transforma los marcos teóricos de Krugman (NEG), Perroux, Myrdal, Hirschman,
Granovetter (con grafo interactivo de vínculos fuertes y débiles en vivo) y Christaller
en simuladores interactivos fáciles de entender.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from motor_redes_dinamicas_dini import renderizar_burbuja_tip


def renderizar_modulo_teoria_avanzada():
    st.header("Laboratorio Interactivo de Teoría Regional (Krugman, Perroux, Granovetter, Christaller)")
    st.markdown(
        "Mueve los deslizadores y cambia los datos en cada pestaña para **comprobar en vivo** cómo operan "
        "la **Nueva Economía Geográfica (Krugman)**, los **Polos y Multiplicadores (Perroux, Myrdal, Hirschman)**, "
        "los **Vínculos Fuertes y Débiles en Red (Granovetter)** y el **Umbral Urbano (Christaller)**."
    )

    tabs_teoria = st.tabs([
        "1. Simulador de Krugman (Costos de Transporte y Macrocefalia)",
        "2. Simulador de Perroux, Myrdal y Hirschman (Polos y Multiplicadores)",
        "3. Simulador de Red en Vivo de Granovetter (Vínculos Fuertes vs. Débiles)",
        "4. Calculadora en Vivo de Christaller (Umbral y Alcance)",
    ])

    with tabs_teoria[0]:
        st.subheader("Simulador en Vivo: Nueva Economía Geográfica (Paul Krugman, 1991)")
        st.markdown(
            "**¿Qué vas a probar aquí?** Cómo al bajar los costos de transporte por debajo de un punto crítico, "
            "las empresas dejan de repartirse en partes iguales y se mudan en masa a la capital regional (**macrocefalia**)."
        )

        renderizar_burbuja_tip(
            titulo_boton="Tip: ¿Cómo funciona el efecto de Krugman en simple?",
            titulo_interno="Fuerzas Centrípetas vs. Centrífugas (Krugman, 1991)",
            formula_latex=r"\text{Aglomeración Neta} = \text{Economías de Escala} + \text{Tamaño de Mercado} - \text{Costos de Transporte }(\tau)",
            explicacion_md=(
                "- **Si transportar es caro:** A las fábricas les conviene quedarse repartidas en cada comuna para no pagar fletes altos.\n"
                "- **Si transportar se vuelve barato:** Las fábricas prefieren concentrarse en una sola gran ciudad (ej. Concepción o Puerto Montt) para aprovechar proveedores y clientes juntos, despachando desde ahí al resto de la región."
            ),
        )

        col_k1, col_k2, col_k3 = st.columns(3)
        with col_k1:
            costo_transporte = st.slider(
                "1. Costo de Transporte (τ) [10 = Muy Caro | 1 = Muy Barato]:",
                min_value=1.0,
                max_value=10.0,
                value=3.5,
                step=0.5,
                key="krug_tau",
            )
        with col_k2:
            economias_escala = st.slider(
                "2. Ventaja de Producir a Gran Escala (1 a 10):",
                min_value=1.0,
                max_value=10.0,
                value=7.0,
                step=0.5,
                key="krug_escala",
            )
        with col_k3:
            movilidad_laboral = st.slider(
                "3. Facilidad de los Trabajadores para Mudarse (1 a 10):",
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
        k1.metric("Umbral Crítico de Transporte (τ*)", f"{umbral_critico_tau:.1f}", "Punto de quiebre territorial")
        k2.metric(
            "Actividad en Capital Regional (Centro)",
            f"{cuota_centro_pct:.1f}%",
            "Macrocefalia Activa" if costo_transporte <= umbral_critico_tau else "Equilibrio Disperso",
        )
        k3.metric(
            "Actividad en Comunas Periféricas",
            f"{cuota_periferia_pct:.1f}%",
            f"{cuota_periferia_pct - 50.0:+.1f}% vs. reparto equitativo",
        )

        if costo_transporte <= umbral_critico_tau:
            st.warning(
                f"**Diagnóstico en Vivo (Macrocefalia):** Como el costo de transporte actual (**{costo_transporte:.1f}**) "
                f"bajó del umbral crítico (**{umbral_critico_tau:.1f}**), se activaron las fuerzas centrípetas de Krugman: "
                f"la capital regional absorbe el **{cuota_centro_pct:.1f}%** de la industria y el empleo."
            )
        else:
            st.success(
                f"**Diagnóstico en Vivo (Territorio Equilibrado):** Como el costo de transporte (**{costo_transporte:.1f}**) "
                f"es mayor al umbral crítico (**{umbral_critico_tau:.1f}**), las empresas se mantienen distribuidas entre "
                f"el centro (**{cuota_centro_pct:.1f}%**) y las comunas periféricas (**{cuota_periferia_pct:.1f}%**)."
            )

        g_k1, g_k2 = st.columns(2)
        with g_k1:
            df_reparto = pd.DataFrame({
                "Territorio": ["Capital Regional (Centro)", "Comunas Periféricas"],
                "Porcentaje de Empresas y Empleo (%)": [cuota_centro_pct, cuota_periferia_pct],
            })
            fig_bar_k = px.bar(
                df_reparto,
                x="Territorio",
                y="Porcentaje de Empresas y Empleo (%)",
                color="Territorio",
                text_auto=".1f",
                range_y=[0, 100],
                color_discrete_sequence=["#1d4ed8", "#64748b"],
                title="Reparto en Vivo: Capital Regional vs. Periferia",
            )
            fig_bar_k.add_hline(y=50, line_dash="dash", line_color="#dc2626", annotation_text="Reparto 50/50")
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
                    name="Concentración en la Capital (%)",
                )
            )
            fig_curva_k.add_trace(
                go.Scatter(
                    x=[costo_transporte],
                    y=[cuota_centro_pct],
                    mode="markers+text",
                    text=[f"Tu simulación ({cuota_centro_pct:.1f}%)"],
                    textposition="top center",
                    marker=dict(size=14, color="#dc2626", line=dict(width=2, color="#ffffff")),
                    name="Punto Actual",
                )
            )
            fig_curva_k.add_vline(
                x=umbral_critico_tau,
                line_dash="dash",
                line_color="#d97706",
                annotation_text=f"Umbral Crítico τ*={umbral_critico_tau:.1f}",
            )
            fig_curva_k.update_layout(
                title="Curva de Krugman: ¿En qué punto se dispara la concentración?",
                xaxis_title="Costo de Transporte (τ) [Menor costo a la izquierda]",
                yaxis_title="% Concentrado en la Capital Regional",
                yaxis_range=[45, 100],
            )
            st.plotly_chart(fig_curva_k, use_container_width=True)

    with tabs_teoria[1]:
        st.subheader("Simulador en Vivo: Polos de Crecimiento y Multiplicadores (Perroux, Myrdal y Hirschman)")
        st.markdown(
            "**¿Qué vas a probar aquí?** Qué pasa cuando se inyecta inversión en una industria motriz (ej. maderera o láctea) "
            "y cómo sus compras a proveedores locales (**Hirschman**) generan difusión (**Spread**) o absorción (**Backwash**)."
        )

        renderizar_burbuja_tip(
            titulo_boton="Tip: Diferencia entre Perroux, Myrdal y Hirschman",
            titulo_interno="Tres Conceptos Clave Conectados",
            formula_latex=r"M_{\text{Hirschman}} = \frac{1}{1 - (b_{\text{atrás}} + f_{\text{adelante}})} \quad ; \quad \text{Impacto Periferia} = \text{Difusión (Spread)} - \text{Absorción (Backwash)}",
            explicacion_md=(
                "- **Perroux (Polos):** El crecimiento nace en una industria motriz dominante, no en todas las comunas a la vez.\n"
                "- **Hirschman (Encadenamientos):** El polo multiplica la actividad si compra insumos locales (*hacia atrás*) y si sus productos se procesan en la misma región (*hacia adelante*).\n"
                "- **Myrdal (Causalidad Acumulativa):** Si el polo solo succiona trabajadores y capital de los pueblos vecinos (*Backwash* > *Spread*), la desigualdad regional aumenta."
            ),
        )

        caso_polo = st.selectbox(
            "Selecciona un Caso Aplicado de Cátedra para cargar valores base:",
            [
                "Caso 1: Clúster Forestal-Maderero PymeMad (Los Ángeles / Biobío)",
                "Caso 2: Complejo Agroindustrial Lácteo-Quesero (Osorno / Los Lagos)",
                "Caso 3: Enclave Industrial Aislado (Poca compra a proveedores locales)",
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
                "Compras Locales Hacia Atrás (0 a 0.45):",
                min_value=0.05,
                max_value=0.45,
                value=def_atras,
                step=0.05,
                key="h_atras",
            )
        with c_p3:
            enc_adelante = st.slider(
                "Procesamiento Local Hacia Adelante (0 a 0.45):",
                min_value=0.05,
                max_value=0.45,
                value=def_adel,
                step=0.05,
                key="h_adel",
            )
        with c_p4:
            pct_difusion = st.slider(
                "% Difusión a Comunas Vecinas (Spread):",
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
        p1.metric("Multiplicador de Hirschman", f"{multiplicador_h:.2f}x", f"Encadenamiento total: {propension_local*100:.0f}%")
        p2.metric("Actividad Total Generada", f"{impacto_total:,.0f} MM$", f"+{efecto_indirecto:,.0f} MM$ en encadenamientos")
        p3.metric("Efecto Difusión (Spread)", f"{difusion_mm:,.0f} MM$", "Compras a comunas vecinas")
        p4.metric(
            "Saldo Neto en Periferia (Myrdal)",
            f"{saldo_periferia:+,.0f} MM$",
            "Polo Integrador" if saldo_periferia >= 0 else "Enclave Absorbente (Backwash)",
        )

        rondas = ["Ronda 1 (Choque Inicial)", "Ronda 2 (Proveedores)", "Ronda 3 (Servicios)", "Ronda 4 (Consumo Local)", "Ronda 5 (Acumulado)"]
        impactos_ronda = [inversion_inicial * (propension_local ** r) for r in range(5)]
        acumulado_ronda = np.cumsum(impactos_ronda)

        df_rondas = pd.DataFrame({
            "Etapa del Efecto Multiplicador": rondas,
            "Impacto en cada Ronda (MM$)": np.round(impactos_ronda, 1),
            "Actividad Acumulada en la Región (MM$)": np.round(acumulado_ronda, 1),
        })

        fig_hirsch = px.bar(
            df_rondas,
            x="Etapa del Efecto Multiplicador",
            y=["Impacto en cada Ronda (MM$)", "Actividad Acumulada en la Región (MM$)"],
            barmode="group",
            text_auto=".0f",
            title="Causalidad Acumulativa en Vivo: Propagación del Choque Productivo en 5 Rondas",
        )
        st.plotly_chart(fig_hirsch, use_container_width=True)

    with tabs_teoria[2]:
        st.subheader("Simulador de Red en Vivo: La Fuerza de los Vínculos Débiles (Mark Granovetter, 1973)")
        st.markdown(
            "**¿Qué vas a probar aquí?** Mueve los deslizadores para armar la red en vivo: los **vínculos fuertes (azules)** "
            "unen a las PyMEs de la misma comuna, mientras que los **vínculos débiles (puentes rojos)** conectan al clúster "
            "con universidades, centros de I+D y mercados externos evitando el bloqueo (*lock-in*)."
        )

        cg1, cg2 = st.columns(2)
        with cg1:
            vinculos_fuertes = st.slider(
                "1. Vínculos Fuertes Internos (Enlaces azules entre PyMEs locales) [1 a 10]:",
                min_value=1,
                max_value=10,
                value=8,
                key="gran_fuertes",
            )
        with cg2:
            vinculos_debiles = st.slider(
                "2. Vínculos Débiles / Puentes Externos (Puentes rojos a I+D, ULagos, Exportación) [0 a 10]:",
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
        m_g1.metric("Cohesión y Confianza Local", f"{cohesion_interna:.0f} / 100", f"{vinculos_fuertes} enlaces fuertes activos")
        m_g2.metric("Entrada de Ideas e Innovación", f"{acceso_innovacion:.0f} / 100", f"{vinculos_debiles} puentes débiles activos")
        m_g3.metric(
            "Riesgo de Encierro (Lock-in)",
            f"{riesgo_lockin:.0f}%",
            "Peligro de endogamia" if riesgo_lockin > 40 else "Red abierta y saludable",
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
                    name="Vínculos Débiles (Puentes de Innovación)",
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
                    name="Fuentes Externas de Innovación",
                )
            )
            fig_red_gran.update_layout(
                title="Grafo en Vivo: Clúster Local (Azul) vs. Puentes Débiles (Rojo)",
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
                    "Confianza Local",
                    "Innovación Externa",
                    "Riesgo Lock-in",
                    "Desempeño Clúster",
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
                title="Diagnóstico del Clúster en Vivo",
            )
            fig_gran.update_layout(height=390, showlegend=False)
            st.plotly_chart(fig_gran, use_container_width=True)

    with tabs_teoria[3]:
        st.subheader("Calculadora en Vivo: Umbral y Alcance de un Servicio Urbano (Walter Christaller)")
        st.markdown(
            "**¿Qué vas a probar aquí?** Introduce la población de una comuna y la distancia que la gente está dispuesta a viajar "
            "para comprobar al instante si un servicio especializado es viable o no en ese territorio."
        )

        renderizar_burbuja_tip(
            titulo_boton="Tip: ¿Qué son el Umbral y el Alcance de Christaller?",
            titulo_interno="Regla de Decisión de Lugares Centrales",
            formula_latex=r"\text{Viabilidad: Población Comunal} \ge \text{Umbral Mínimo} \quad \wedge \quad \text{Alcance Máximo (km)} \ge \text{Distancia al Usuario}",
            explicacion_md=(
                "- **Umbral (*Threshold*):** Cantidad mínima de habitantes o clientes necesaria para que el servicio cubra sus costos y no quiebre.\n"
                "- **Alcance (*Range*):** Distancia máxima (en km) que una persona acepta viajar para usar ese servicio."
            ),
        )

        servicio_sel = st.selectbox(
            "Selecciona el tipo de equipamiento o servicio a evaluar:",
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
                "Población Comuna + Entorno:",
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
                "Distancia de las Localidades Vecinas (km):",
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
                f"✅ **SERVICIO VIABLE Y SOSTENIBLE EN LA COMUNA:** La población ({pob_comuna:,} hab.) supera el "
                f"**Umbral Mínimo** ({umbral_min:,} hab. → **{cobertura_pct:.1f}%** de cobertura) y el **Alcance** "
                f"({alcance_max} km) cubre perfectamente a las localidades vecinas ({dist_real} km)."
            )
        elif not cumple_umbral:
            st.error(
                f"❌ **NO ALCANZA EL UMBRAL MÍNIMO DE CHRISTALLER:** La comuna tiene **{pob_comuna:,} habitantes**, "
                f"pero este servicio necesita al menos **{umbral_min:,} habitantes** para sostenerse ({cobertura_pct:.1f}% del umbral). "
                "Por jerarquía urbana, este servicio tiende a concentrarse en la capital provincial o regional."
            )
        else:
            st.warning(
                f"⚠️ **PROBLEMA DE ALCANCE ESPACIAL:** Aunque hay población suficiente, la distancia de las localidades "
                f"vecinas (**{dist_real} km**) supera lo que los usuarios están dispuestos a viajar (**{alcance_max} km**)."
            )

        df_ch = pd.DataFrame({
            "Indicador": ["Población Disponible en la Comuna", "Umbral Mínimo Exigido (Christaller)"],
            "Habitantes": [pob_comuna, umbral_min],
        })
        fig_ch = px.bar(
            df_ch,
            x="Indicador",
            y="Habitantes",
            color="Indicador",
            text_auto=",",
            color_discrete_sequence=["#059669" if cumple_umbral else "#dc2626", "#1e293b"],
            title="Comparación en Vivo: Demanda Comunal vs. Umbral Mínimo de Christaller",
        )
        st.plotly_chart(fig_ch, use_container_width=True)
