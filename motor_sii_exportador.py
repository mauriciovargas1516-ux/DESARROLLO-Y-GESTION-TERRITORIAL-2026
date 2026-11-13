import io
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats


@st.cache_data(show_spinner=False)
def cargar_base_nacional_sii(archivo_subido=None):
    """Lee y limpia la base nacional del SII (PUB_COMU_RUBR) desde archivo subido o repositorio local."""
    df = None
    if archivo_subido is not None:
        nombre = archivo_subido.name.lower()
        if nombre.endswith(".xlsb"):
            df = pd.read_excel(archivo_subido, engine="pyxlsb")
        else:
            xls = pd.ExcelFile(archivo_subido)
            hoja = "Datos" if "Datos" in xls.sheet_names else xls.sheet_names[0]
            df = pd.read_excel(xls, hoja)
    else:
        for ruta in ["ILPES GRUPO 10 29-10-2026.xlsx", "ILPES GRUPO 10 TERRITORIAL AL 19-10-2026.xlsx"]:
            if os.path.exists(ruta):
                xls = pd.ExcelFile(ruta)
                if "Datos" in xls.sheet_names:
                    df = pd.read_excel(xls, "Datos")
                    break

        if df is None:
            for arch in os.listdir("."):
                if arch.lower().endswith(".xlsb"):
                    df = pd.read_excel(arch, engine="pyxlsb")
                    break

    if df is None:
        return None

    # Normalización de nombres de columnas por si varía entre versiones de Excel/XLSB del SII
    col_map = {}
    for c in df.columns:
        cl = str(c).strip()
        if "año" in cl.lower() and "comercial" in cl.lower():
            col_map[c] = "Año Comercial"
        elif "comuna" in cl.lower() and "domicilio" in cl.lower():
            col_map[c] = "Comuna del domicilio o casa matriz"
        elif "regi" in cl.lower() and "domicilio" in cl.lower():
            col_map[c] = "Región del domicilio o casa matriz"
        elif "rubro" in cl.lower() and "econ" in cl.lower():
            col_map[c] = "Rubro económico"
    if col_map:
        df = df.rename(columns=col_map)

    return df


def obtener_variables_sii_disponibles(df_sii):
    """Devuelve las columnas numéricas económicas disponibles en la base del SII."""
    candidatas = [
        "Ventas anuales en UF",
        "Número de empresas",
        "Número de trabajadores dependientes informados",
        "Renta neta informada en UF",
        "Trabajadores ponderados por meses trabajados",
    ]
    disp = [c for c in candidatas if c in df_sii.columns]
    return disp if disp else candidatas


def construir_matrices_region(df_raw, region_sel, anio_0, anio_t, col_variable):
    """Filtra la región seleccionada, convierte celdas con '*' a 0 y construye las matrices V0 y Vt."""
    df = df_raw[
        (df_raw["Región del domicilio o casa matriz"] == region_sel)
        & (df_raw["Comuna del domicilio o casa matriz"].notna())
        & (df_raw["Comuna del domicilio o casa matriz"] != "Sin Información")
        & (df_raw["Rubro económico"].notna())
        & (~df_raw["Rubro económico"].astype(str).str.lower().str.contains("sin informaci"))
        & (df_raw["Año Comercial"].isin([anio_0, anio_t]))
    ].copy()

    df["Valor_Limpio"] = pd.to_numeric(df[col_variable], errors="coerce").fillna(0.0)

    comunas = sorted(df["Comuna del domicilio o casa matriz"].astype(str).unique())
    sectores = sorted(df["Rubro económico"].astype(str).unique())

    df_0 = (
        df[df["Año Comercial"] == anio_0]
        .pivot_table(
            index="Rubro económico",
            columns="Comuna del domicilio o casa matriz",
            values="Valor_Limpio",
            aggfunc="sum",
            fill_value=0.0,
        )
        .reindex(index=sectores, columns=comunas, fill_value=0.0)
    )

    df_t = (
        df[df["Año Comercial"] == anio_t]
        .pivot_table(
            index="Rubro económico",
            columns="Comuna del domicilio o casa matriz",
            values="Valor_Limpio",
            aggfunc="sum",
            fill_value=0.0,
        )
        .reindex(index=sectores, columns=comunas, fill_value=0.0)
    )

    return df_0, df_t, comunas, sectores


def calcular_todo_el_ramo(df_0, df_t, anio_0, anio_t, alfa_hk=2.0):
    """Calcula todas las matrices de análisis regional ILPES, Shift & Share y Convergencia REAT."""
    V0 = df_0.values.astype(float)
    Vt = df_t.values.astype(float)
    comunas = list(df_0.columns)
    sectores = list(df_0.index)
    T = max(1, abs(int(anio_t) - int(anio_0)))

    tot_reg_0 = V0.sum(axis=0)
    tot_sec_0 = V0.sum(axis=1)
    tot_nac_0 = V0.sum()

    tot_reg_t = Vt.sum(axis=0)
    tot_sec_t = Vt.sum(axis=1)
    tot_nac_t = Vt.sum()

    # 1. Matriz de Participación Sectorial (P_ij)
    P0 = np.divide(V0, tot_reg_0, out=np.zeros_like(V0), where=tot_reg_0 != 0)
    Pt = np.divide(Vt, tot_reg_t, out=np.zeros_like(Vt), where=tot_reg_t != 0)
    P_nac_0 = tot_sec_0 / tot_nac_0 if tot_nac_0 != 0 else np.zeros_like(tot_sec_0)
    P_nac_t = tot_sec_t / tot_nac_t if tot_nac_t != 0 else np.zeros_like(tot_sec_t)

    # 2. Cociente de Localización (Q_ij)
    Q0 = np.divide(P0, P_nac_0[:, None], out=np.zeros_like(P0), where=P_nac_0[:, None] != 0)
    Qt = np.divide(Pt, P_nac_t[:, None], out=np.zeros_like(Pt), where=P_nac_t[:, None] != 0)

    # 3. Coeficiente de Especialización (Q_r) y Reestructuración (CR_r)
    diff_esp_0 = np.abs(P0 - P_nac_0[:, None])
    diff_esp_t = np.abs(Pt - P_nac_t[:, None])
    Qr_0 = 0.5 * np.sum(diff_esp_0, axis=0)
    Qr_t = 0.5 * np.sum(diff_esp_t, axis=0)

    diff_reest = np.abs(Pt - P0)
    CRr = 0.5 * np.sum(diff_reest, axis=0)

    # 4. Base Económica Exportadora (X_ij, X_j, M_j)
    X0_mat = np.where(Q0 > 1.0, V0 - (V0 / np.where(Q0 > 1.0, Q0, 1.0)), 0.0)
    Xt_mat = np.where(Qt > 1.0, Vt - (Vt / np.where(Qt > 1.0, Qt, 1.0)), 0.0)
    X0_tot = X0_mat.sum(axis=0)
    Xt_tot = Xt_mat.sum(axis=0)
    M0 = np.divide(tot_reg_0, X0_tot, out=np.zeros_like(tot_reg_0), where=X0_tot != 0)
    Mt = np.divide(tot_reg_t, Xt_tot, out=np.zeros_like(tot_reg_t), where=Xt_tot != 0)

    # 5. Variación Intertemporal (rV_ij y rR_j)
    rV_mat = np.divide(Vt, V0, out=np.zeros_like(Vt), where=V0 != 0)
    rR_j = np.divide(tot_reg_t, tot_reg_0, out=np.zeros_like(tot_reg_t), where=tot_reg_0 != 0)

    # 6. Shift & Share (MADE Clásico y MADE Modificado)
    r_nac = tot_nac_t / tot_nac_0 if tot_nac_0 != 0 else 1.0
    r_sec = np.divide(tot_sec_t, tot_sec_0, out=np.ones_like(tot_sec_0), where=tot_sec_0 != 0)

    ET = tot_reg_t - tot_reg_0 * r_nac
    EE_mat = V0 * (r_sec[:, None] - r_nac)
    EE = np.sum(EE_mat, axis=0)
    ED_mat = Vt - V0 * r_sec[:, None]
    ED = ET - EE

    r_nac_inv = tot_nac_0 / tot_nac_t if tot_nac_t != 0 else 1.0
    r_sec_inv = np.divide(tot_sec_0, tot_sec_t, out=np.ones_like(tot_sec_t), where=tot_sec_t != 0)
    EI_mat = Vt * (r_nac_inv - r_sec_inv[:, None])
    EI = np.sum(EI_mat, axis=0)
    EM = EI - EE
    ERM = ET - EI

    # 7. Cuadrantes de Silva Lira (CEPAL, 2005)
    tasa_anual_com = (np.power(np.maximum(rR_j, 1e-9), 1.0 / T) - 1.0) * 100.0
    tasa_anual_reg = ((r_nac ** (1.0 / T)) - 1.0) * 100.0 if r_nac > 0 else 0.0
    media_nivel_t = np.mean(tot_reg_t)

    cuadrantes = []
    for c_rate, v_niv in zip(tasa_anual_com, tot_reg_t):
        if c_rate >= tasa_anual_reg and v_niv >= media_nivel_t:
            cuadrantes.append("C1 (+ +): Ganadores / Dinámicos Alto Nivel")
        elif c_rate >= tasa_anual_reg and v_niv < media_nivel_t:
            cuadrantes.append("C2 (- +): En Marcha / Convergentes")
        elif c_rate < tasa_anual_reg and v_niv < media_nivel_t:
            cuadrantes.append("C3 (- -): Estancados / Bajo Nivel")
        else:
            cuadrantes.append("C4 (+ -): En Retroceso / Desacelerados")

    df_resumen = pd.DataFrame({
        "Territorio": comunas,
        "Ventas_0": tot_reg_0,
        "Ventas_t": tot_reg_t,
        "Var_Ratio (rRj)": rR_j,
        "Tasa_Crec_Anual (%)": tasa_anual_com,
        "Cuadrante_Silva": cuadrantes,
        "Qr_0 (Especialización)": Qr_0,
        "Qr_t (Especialización)": Qr_t,
        "CRr (Reestructuración)": CRr,
        "Exportación_Básica_0 (Xj)": X0_tot,
        "Exportación_Básica_t (Xj)": Xt_tot,
        "Multiplicador_0 (Mj)": M0,
        "Multiplicador_t (Mj)": Mt,
        "Efecto_Total (ET)": ET,
        "Efecto_Estructural (EE)": EE,
        "Efecto_Diferencial (ED)": ED,
        "Efecto_Est_Inverso (EI)": EI,
        "Efecto_Est_Modificado (EM)": EM,
        "Efecto_Reg_Modificado (ERM)": ERM,
    })

    # 8. Indicadores REAT de Disparidad, Concentración y Convergencia entre Comunas
    y0_pos = np.where(tot_reg_0 > 0, tot_reg_0, 1.0)
    yt_pos = np.where(tot_reg_t > 0, tot_reg_t, 1.0)
    ln_y0 = np.log(y0_pos)
    ln_yt = np.log(yt_pos)
    g_anual = (ln_yt - ln_y0) / T
    N = len(comunas)

    slope, intercept, r_val, p_val, std_err = stats.linregress(ln_y0, g_anual)
    t_stat = slope / std_err if std_err != 0 else np.nan
    B_acum = slope * T
    vel_lambda = -np.log(1.0 + B_acum) / T if (1.0 + B_acum) > 0 else np.nan
    semivida = np.log(2.0) / vel_lambda if vel_lambda and vel_lambda > 0 else np.nan

    def lorenz_gini(x):
        xs = np.sort(np.maximum(x, 0.0))
        n = len(xs)
        if xs.sum() == 0 or n < 2:
            return np.linspace(0, 1, n + 1), np.linspace(0, 1, n + 1), 0.0, 0.0
        cp = np.arange(0, n + 1) / n
        cq = np.concatenate([[0.0], np.cumsum(xs) / xs.sum()])
        gini = 1.0 - np.sum((cp[1:] - cp[:-1]) * (cq[1:] + cq[:-1]))
        gini_n = gini * (n / (n - 1.0))
        return cp, cq, gini, gini_n

    p0_lor, q0_lor, gini_0, gini_n0 = lorenz_gini(tot_reg_0)
    pt_lor, qt_lor, gini_t, gini_nt = lorenz_gini(tot_reg_t)

    s0 = y0_pos / y0_pos.sum()
    st_sh = yt_pos / yt_pos.sum()
    theil_0 = np.sum(s0 * np.log(N * s0))
    theil_t = np.sum(st_sh * np.log(N * st_sh))
    hhi_0 = np.sum(s0 ** 2)
    hhi_t = np.sum(st_sh ** 2)
    hk_0 = (np.sum(s0 ** alfa_hk)) ** (1.0 / (alfa_hk - 1.0))
    hk_t = (np.sum(st_sh ** alfa_hk)) ** (1.0 / (alfa_hk - 1.0))

    df_reat = pd.DataFrame([
        {"Indicador REAT": "Número de Comunas Analizadas (N)", str(anio_0): N, str(anio_t): N},
        {"Indicador REAT": "Promedio Comunal", str(anio_0): np.mean(tot_reg_0), str(anio_t): np.mean(tot_reg_t)},
        {"Indicador REAT": "Desviación Estándar de Logaritmos (Convergencia Sigma σ_ln)", str(anio_0): np.std(ln_y0, ddof=1), str(anio_t): np.std(ln_yt, ddof=1)},
        {"Indicador REAT": "Coeficiente de Variación en Niveles (CV)", str(anio_0): np.std(tot_reg_0, ddof=0) / np.mean(tot_reg_0) if np.mean(tot_reg_0) > 0 else 0.0, str(anio_t): np.std(tot_reg_t, ddof=0) / np.mean(tot_reg_t) if np.mean(tot_reg_t) > 0 else 0.0},
        {"Indicador REAT": "Índice de Desigualdad de Gini Estándar", str(anio_0): gini_0, str(anio_t): gini_t},
        {"Indicador REAT": "Índice de Gini Normalizado (n/(n-1))", str(anio_0): gini_n0, str(anio_t): gini_nt},
        {"Indicador REAT": "Índice de Entropía de Theil", str(anio_0): theil_0, str(anio_t): theil_t},
        {"Indicador REAT": "Índice Herfindahl-Hirschman (HHI)", str(anio_0): hhi_0, str(anio_t): hhi_t},
        {"Indicador REAT": f"Índice de Concentración Hannah-Kay (α = {alfa_hk})", str(anio_0): hk_0, str(anio_t): hk_t},
        {"Indicador REAT": "Comunas Equivalentes (1 / HHI)", str(anio_0): 1.0 / hhi_0 if hhi_0 > 0 else np.nan, str(anio_t): 1.0 / hhi_t if hhi_t > 0 else np.nan},
        {"Indicador REAT": "Pendiente Convergencia Beta Anual (β OLS)", str(anio_0): slope, str(anio_t): np.nan},
        {"Indicador REAT": "Estadístico t de Student (Beta OLS)", str(anio_0): t_stat, str(anio_t): np.nan},
        {"Indicador REAT": "Valor p Bilateral (Significancia Beta)", str(anio_0): p_val, str(anio_t): np.nan},
        {"Indicador REAT": "Bondad de Ajuste Regresión Beta (R²)", str(anio_0): r_val ** 2, str(anio_t): np.nan},
        {"Indicador REAT": "Velocidad de Convergencia (λ anual)", str(anio_0): vel_lambda, str(anio_t): np.nan},
        {"Indicador REAT": "Semivida / Half-Life (años para cerrar 50% brecha)", str(anio_0): semivida, str(anio_t): np.nan},
    ])

    df_reat_comunal = pd.DataFrame({
        "Comuna": comunas,
        f"Valor_{anio_0}": tot_reg_0,
        f"Valor_{anio_t}": tot_reg_t,
        f"ln({anio_0})": ln_y0,
        f"ln({anio_t})": ln_yt,
        "Crecimiento_Log_Anual (gi)": g_anual,
        "Prediccion_OLS": intercept + slope * ln_y0,
        f"Participacion_s_{anio_0}": s0,
        f"Participacion_s_{anio_t}": st_sh,
    })

    return {
        "resumen": df_resumen,
        "df_resumen": df_resumen,
        "df_reat": df_reat,
        "df_reat_comunal": df_reat_comunal,
        "reat_dict": {
            "sigma_ln_0": np.std(ln_y0, ddof=1),
            "sigma_ln_t": np.std(ln_yt, ddof=1),
            "beta_anual": slope,
            "intercepto": intercept,
            "r2": r_val ** 2,
            "t_stat": t_stat,
            "p_value": p_val,
            "velocidad_b": vel_lambda,
            "semivida_b": semivida,
            "gini_0": gini_0,
            "gini_t": gini_t,
            "lorenz_0": (p0_lor, q0_lor),
            "lorenz_t": (pt_lor, qt_lor),
            "ln_y0": ln_y0,
            "ln_yt": ln_yt,
            "g_anual": g_anual,
        },
        "df_0": df_0,
        "df_t": df_t,
        "P0": pd.DataFrame(P0, index=sectores, columns=comunas),
        "Pt": pd.DataFrame(Pt, index=sectores, columns=comunas),
        "Q0": pd.DataFrame(Q0, index=sectores, columns=comunas),
        "Qt": pd.DataFrame(Qt, index=sectores, columns=comunas),
        "X0": pd.DataFrame(X0_mat, index=sectores, columns=comunas),
        "Xt": pd.DataFrame(Xt_mat, index=sectores, columns=comunas),
        "rV": pd.DataFrame(rV_mat, index=sectores, columns=comunas),
        "CRr_mat": pd.DataFrame(diff_reest, index=sectores, columns=comunas),
        "ED_mat": pd.DataFrame(ED_mat, index=sectores, columns=comunas),
        "EE_mat": pd.DataFrame(EE_mat, index=sectores, columns=comunas),
        "EI_mat": pd.DataFrame(EI_mat, index=sectores, columns=comunas),
        "tasa_anual_reg": tasa_anual_reg,
        "media_nivel_t": media_nivel_t,
        "r_nac": r_nac,
    }


def compilar_excel_10_hojas(res_calc, anio_0, anio_t):
    """Empaqueta todos los indicadores y matrices del curso en un archivo Excel (.xlsx) de 11 hojas."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        res_calc["df_resumen"].round(4).to_excel(writer, sheet_name="1_Resumen_ILPES_MADE", index=False)
        res_calc["df_reat"].round(6).to_excel(writer, sheet_name="2_Convergencia_REAT", index=False)
        res_calc["df_reat_comunal"].round(6).to_excel(writer, sheet_name="3_Datos_REAT_Lorenz_OLS", index=False)
        res_calc["df_0"].round(2).to_excel(writer, sheet_name=f"4_Base_{anio_0}")
        res_calc["df_t"].round(2).to_excel(writer, sheet_name=f"5_Base_{anio_t}")
        res_calc["P0"].round(5).to_excel(writer, sheet_name=f"6_Porcentaje_Pij_{anio_0}")
        res_calc["Pt"].round(5).to_excel(writer, sheet_name=f"7_Porcentaje_Pij_{anio_t}")
        res_calc["Q0"].round(4).to_excel(writer, sheet_name=f"8_Localizacion_Qij_{anio_0}")
        res_calc["Qt"].round(4).to_excel(writer, sheet_name=f"9_Localizacion_Qij_{anio_t}")
        res_calc["Xt"].round(2).to_excel(writer, sheet_name=f"10_Base_Exportadora_{anio_t}")

        df_made_sheet = pd.concat([
            res_calc["EE_mat"].round(2).assign(Matriz="1. Efecto Estructural Sectorial (EE_ij)"),
            res_calc["ED_mat"].round(2).assign(Matriz="2. Efecto Diferencial Sectorial (ED_ij)"),
            res_calc["EI_mat"].round(2).assign(Matriz="3. Efecto Estructural Inverso (EI_ij)"),
            res_calc["CRr_mat"].round(4).assign(Matriz="4. Diferencia Reestructuración (|Pt - P0|)"),
            res_calc["rV"].round(4).assign(Matriz="5. Variación Intertemporal Sectorial (Vt / V0)"),
        ])
        df_made_sheet.to_excel(writer, sheet_name="11_Desglose_MADE_Sectorial")

    return buffer.getvalue()


def renderizar_modulo_nacional_sii(archivo_subido=None):
    """Renderiza el laboratorio interactivo multirregional SII (16 regiones) con todos los gráficos y Excel."""
    st.markdown(
        "<div class='sec-header'>LABORATORIO MULTIRREGIONAL SII (16 REGIONES DE CHILE, 2005-2024) Y EXPORTADOR MAESTRO EXCEL</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "Selecciona **cualquier región de Chile**, **cualquier variable económica oficial del SII** y **cualquier par de años comerciales** "
        "para generar automáticamente todas las matrices, gráficos interactivos, diagnósticos de examen y el libro Excel completo de la asignatura."
    )

    with st.spinner("Cargando base nacional del SII (126.095 registros, 16 regiones de Chile, 2005-2024)..."):
        df_sii = cargar_base_nacional_sii(archivo_subido)

    if df_sii is None:
        st.warning("No se detectó la base nacional del SII en el repositorio. Sube el archivo PUB_COMU_RUBR.xlsb o tu Excel ILPES en el panel izquierdo.")
        return

    regiones_disp = sorted([
        str(r) for r in df_sii["Región del domicilio o casa matriz"].dropna().unique()
        if str(r) != "Sin Información"
    ])
    anios_disp = sorted([int(a) for a in df_sii["Año Comercial"].dropna().unique()])
    variables_disp = obtener_variables_sii_disponibles(df_sii)

    c1, c2, c3, c4 = st.columns([2.2, 2.0, 1.0, 1.0])
    idx_def = regiones_disp.index("Región de Los Lagos") if "Región de Los Lagos" in regiones_disp else 0
    region_sel = c1.selectbox("1. Región de Chile:", regiones_disp, index=idx_def, key="sii_reg")
    var_sel = c2.selectbox("2. Variable Económica SII:", variables_disp, index=0, key="sii_var")
    anio_0 = c3.selectbox("3. Año Inicial (t0):", anios_disp, index=anios_disp.index(2014) if 2014 in anios_disp else 0, key="sii_a0")
    anio_t = c4.selectbox("4. Año Final (t1):", anios_disp, index=anios_disp.index(2024) if 2024 in anios_disp else len(anios_disp) - 1, key="sii_at")

    df_0, df_t, comunas, sectores = construir_matrices_region(df_sii, region_sel, anio_0, anio_t, var_sel)
    res_calc = calcular_todo_el_ramo(df_0, df_t, anio_0, anio_t)
    df_res = res_calc["df_resumen"]
    reat_d = res_calc["reat_dict"]

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Comunas Analizadas", f"{len(comunas)} comunas")
    k2.metric(f"Total Regional ({anio_0})", f"{df_0.values.sum():,.0f}")
    k3.metric(f"Total Regional ({anio_t})", f"{df_t.values.sum():,.0f}")
    crec_reg = ((df_t.values.sum() / df_0.values.sum()) - 1.0) * 100.0 if df_0.values.sum() > 0 else 0.0
    k4.metric(f"Variación Acumulada ({anio_0}-{anio_t})", f"{crec_reg:.2f}%", f"{res_calc['tasa_anual_reg']:.2f}% anual")

    excel_bytes = compilar_excel_10_hojas(res_calc, anio_0, anio_t)
    nombre_limpio = region_sel.replace(" ", "_").replace(".", "")
    st.download_button(
        label=f"Descargar Libro Excel Completo (11 Hojas Calculadas) — {region_sel} ({var_sel}, {anio_0}-{anio_t}).xlsx",
        data=excel_bytes,
        file_name=f"ILPES_REAT_{nombre_limpio}_{anio_0}_{anio_t}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        use_container_width=True,
    )

    # --- SIMULADOR DE ESTUDIO PASO A PASO POR COMUNA ---
    with st.expander(" Simulador de Estudio y Defensa de Examen: Elige una Comuna para ver sus Fórmulas y Diagnóstico Automático", expanded=True):
        com_estudio = st.selectbox("Selecciona la Comuna a explicar paso a paso:", comunas, index=0, key="sii_com_est")
        fila = df_res[df_res["Territorio"] == com_estudio].iloc[0]
        q_col = res_calc["Qt"][com_estudio]
        basicos = q_col[q_col > 1.0].sort_values(ascending=False)
        txt_basicos = ", ".join([f"{s.split(' - ')[-1]} (Q={v:.2f})" for s, v in basicos.head(3).items()]) if len(basicos) > 0 else "Ninguno (Qij <= 1)"

        ganadora_made = "GANADORA (ET > 0: crece por sobre el ritmo regional)" if fila["Efecto_Total (ET)"] >= 0 else "PERDEDORA (ET < 0: crece menos que el promedio regional)"
        diag_erm = "ventajas competitivas locales o dinamismo endógeno positivo (ERM > 0)" if fila["Efecto_Reg_Modificado (ERM)"] >= 0 else "pérdida de competitividad territorial interna (ERM < 0)"
        diag_em = "reestructuración positiva hacia sectores en expansión (EM > 0)" if fila["Efecto_Est_Modificado (EM)"] >= 0 else "especialización creciente en rubros de menor crecimiento relativo (EM < 0)"

        st.markdown(
            f"""
            <div class='study-box'>
            <b>Explicación de Prueba Paso a Paso — Comuna de {com_estudio} ({region_sel}, {anio_0} vs {anio_t}):</b><br>
            • <b>1. Tipología de Silva Lira (CEPAL, 2005):</b> Clasifica en <b>{fila['Cuadrante_Silva']}</b> con una tasa de crecimiento anual de <b>{fila['Tasa_Crec_Anual (%)']:.2f}%</b> (frente a la media regional de <b>{res_calc['tasa_anual_reg']:.2f}%</b> anual).<br>
            • <b>2. Especialización ($Q_r$) y Reestructuración ($CR_r$):</b> Su Coeficiente de Especialización en {anio_t} es <b>Qr = {fila['Qr_t (Especialización)']:.3f}</b> (donde 0 = estructura idéntica a la región y 1 = especialización extrema) y su Coeficiente de Reestructuración entre {anio_0} y {anio_t} es <b>CRr = {fila['CRr (Reestructuración)']:.3f}</b>. Sus principales rubros básicos exportadores ($Q_{{ij}} > 1$) son: <b>{txt_basicos}</b>.<br>
            • <b>3. Base Exportadora ($X_j$) y Multiplicador Básico ($M_j = V_j / X_j$):</b> De un total comunal de <b>{fila['Ventas_t']:,.1f}</b> en {anio_t}, el excedente básico exportador es <b>Xj = {fila['Exportación_Básica_t (Xj)']:,.1f}</b>, arrojando un Multiplicador <b>Mj = {fila['Multiplicador_t (Mj)']:.2f}</b> (por cada 1 unidad generada en el sector básico exportador, la comuna genera <b>{fila['Multiplicador_t (Mj)']:.2f}</b> unidades de actividad total).<br>
            • <b>4. Shift & Share (MADE Clásico y Modificado):</b> Es una comuna <b>{ganadora_made}</b> con Efecto Total <b>ET = {fila['Efecto_Total (ET)']:,.1f}</b>, explicado por un Efecto Estructural <b>EE = {fila['Efecto_Estructural (EE)']:,.1f}</b> y un Efecto Diferencial <b>ED = {fila['Efecto_Diferencial (ED)']:,.1f}</b>. Al aislar el cambio estructural mediante el MADE Modificado ($ET = EE + EM + ERM$), exhibe <b>{diag_em}</b> (<b>EM = {fila['Efecto_Est_Modificado (EM)']:,.1f}</b>) y <b>{diag_erm}</b> (<b>ERM = {fila['Efecto_Reg_Modificado (ERM)']:,.1f}</b>).
            </div>
            """,
            unsafe_allow_html=True,
        )

    t1, t2, t3, t4, t5 = st.tabs([
        "I. Cuadrantes de Silva y Tabla Maestra",
        "II. Mapa de Calor Localización (Qij) y Especialización (Qr / CRr)",
        "III. Base Exportadora (Xj) y Multiplicador (Mj)",
        "IV. Shift & Share (MADE Clásico y Modificado)",
        "V. Convergencia y Desigualdad Regional (Motor REAT)",
    ])

    with t1:
        fig_s = px.scatter(
            df_res,
            x="Ventas_t",
            y="Tasa_Crec_Anual (%)",
            color="Cuadrante_Silva",
            hover_name="Territorio",
            size=np.maximum(df_res["Ventas_t"], 1.0),
            log_x=True,
            title=f"Cuadrantes de Silva Lira — {region_sel} ({var_sel}: {anio_0} vs {anio_t})",
        )
        fig_s.add_hline(y=res_calc["tasa_anual_reg"], line_dash="dash", line_color="red", annotation_text="Crec. Anual Regional")
        fig_s.add_vline(x=res_calc["media_nivel_t"], line_dash="dash", line_color="blue", annotation_text=f"Nivel Medio {anio_t}")
        st.plotly_chart(fig_s, use_container_width=True)
        st.dataframe(df_res.round(3), use_container_width=True, hide_index=True)

    with t2:
        fig_q = px.imshow(
            res_calc["Qt"].round(2),
            aspect="auto",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=1.0,
            title=f"Mapa de Calor: Cociente de Localización (Qij) — {region_sel} ({anio_t})",
        )
        st.plotly_chart(fig_q, use_container_width=True)
        ca, cb = st.columns(2)
        with ca:
            fig_qr = px.bar(
                df_res.sort_values("Qr_t (Especialización)", ascending=False),
                x="Territorio",
                y=["Qr_0 (Especialización)", "Qr_t (Especialización)"],
                barmode="group",
                title=f"Coeficiente de Especialización (Qr): {anio_0} vs {anio_t}",
            )
            st.plotly_chart(fig_qr, use_container_width=True)
        with cb:
            fig_cr = px.bar(
                df_res.sort_values("CRr (Reestructuración)", ascending=False),
                x="Territorio",
                y="CRr (Reestructuración)",
                color="CRr (Reestructuración)",
                title=f"Coeficiente de Reestructuración (CRr): {anio_0}-{anio_t}",
            )
            st.plotly_chart(fig_cr, use_container_width=True)

    with t3:
        st.dataframe(
            df_res[[
                "Territorio", "Ventas_0", "Exportación_Básica_0 (Xj)", "Multiplicador_0 (Mj)",
                "Ventas_t", "Exportación_Básica_t (Xj)", "Multiplicador_t (Mj)"
            ]].round(3),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown(f"**Matriz de Excedente Exportador Básico ($X_{{ij}}$ para sectores con $Q_{{ij}} > 1$) en {anio_t}:**")
        st.dataframe(res_calc["Xt"].round(1), use_container_width=True)

    with t4:
        fig_m = px.bar(
            df_res,
            x="Territorio",
            y=["Efecto_Estructural (EE)", "Efecto_Diferencial (ED)"],
            barmode="relative",
            title=f"Descomposición Shift & Share ({region_sel}: {anio_0} vs {anio_t})",
        )
        st.plotly_chart(fig_m, use_container_width=True)
        st.dataframe(
            df_res[[
                "Territorio", "Efecto_Total (ET)", "Efecto_Estructural (EE)",
                "Efecto_Diferencial (ED)", "Efecto_Est_Inverso (EI)",
                "Efecto_Est_Modificado (EM)", "Efecto_Reg_Modificado (ERM)"
            ]].round(2),
            use_container_width=True,
            hide_index=True,
        )

    with t5:
        r1, r2, r3, r4 = st.columns(4)
        r1.metric(f"Sigma Log ({anio_0}->{anio_t})", f"{reat_d['sigma_ln_t']:.4f}", f"{reat_d['sigma_ln_t'] - reat_d['sigma_ln_0']:.4f}", delta_color="inverse")
        r2.metric("Pendiente Beta Anual (β)", f"{reat_d['beta_anual']:.5f}", f"p = {reat_d['p_value']:.4f}")
        r3.metric("Bondad Ajuste (R²)", f"{reat_d['r2'] * 100:.2f}%", f"t = {reat_d['t_stat']:.2f}")
        r4.metric("Índice de Gini", f"{reat_d['gini_t']:.4f}", f"{reat_d['gini_t'] - reat_d['gini_0']:.4f}", delta_color="inverse")

        col_b, col_l = st.columns(2)
        with col_b:
            df_b = res_calc["df_reat_comunal"]
            fig_b = px.scatter(
                df_b,
                x=f"ln({anio_0})",
                y="Crecimiento_Log_Anual (gi)",
                hover_name="Comuna",
                text="Comuna",
                title=f"Convergencia Beta Absoluta ({region_sel}, {anio_0}-{anio_t}): β = {reat_d['beta_anual']:.4f}",
            )
            fig_b.add_traces(go.Scatter(x=df_b[f"ln({anio_0})"], y=df_b["Prediccion_OLS"], mode="lines", name="Recta OLS", line=dict(color="red", dash="dash")))
            st.plotly_chart(fig_b, use_container_width=True)
        with col_l:
            p0_l, q0_l = reat_d["lorenz_0"]
            pt_l, qt_l = reat_d["lorenz_t"]
            fig_l = go.Figure()
            fig_l.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Equidistribución (45°)", line=dict(dash="dot", color="gray")))
            fig_l.add_trace(go.Scatter(x=p0_l, y=q0_l, mode="lines+markers", name=f"Lorenz {anio_0} (Gini={reat_d['gini_0']:.3f})"))
            fig_l.add_trace(go.Scatter(x=pt_l, y=qt_l, mode="lines+markers", name=f"Lorenz {anio_t} (Gini={reat_d['gini_t']:.3f})"))
            fig_l.update_layout(title=f"Curva de Lorenz Regional ({region_sel})", xaxis_title="Proporción acumulada de comunas", yaxis_title="Proporción acumulada de variable")
            st.plotly_chart(fig_l, use_container_width=True)

        st.dataframe(res_calc["df_reat"].round(5), use_container_width=True, hide_index=True)
