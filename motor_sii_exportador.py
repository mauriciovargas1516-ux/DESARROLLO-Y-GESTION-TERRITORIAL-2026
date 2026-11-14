# -*- coding: utf-8 -*-
"""
MOTOR ECONOMÉTRICO Y EXPORTADOR SII - ILPES / MADE / REAT
Asignatura: Desarrollo y Gestión Territorial - Universidad de Los Lagos
Archivo: motor_sii_exportador.py
"""

import io
import os
import unicodedata
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from openpyxl import Workbook
from openpyxl.chart import Reference, ScatterChart, Series
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


ARCHIVO_DEFAULT_REPO = "ILPES GRUPO 10 29-10-2026.xlsx"


def _normalizar_texto(texto: str) -> str:
    if texto is None:
        return ""
    texto_str = str(texto).strip().lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", texto_str)
        if unicodedata.category(c) != "Mn"
    )


def _buscar_columna(columnas, candidatos):
    mapa = {_normalizar_texto(c): c for c in columnas}
    for cand in candidatos:
        cand_norm = _normalizar_texto(cand)
        if cand_norm in mapa:
            return mapa[cand_norm]
    for col_norm, col_real in mapa.items():
        for cand in candidatos:
            if _normalizar_texto(cand) in col_norm:
                return col_real
    return None


def _a_numero_sii(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0.0)
    limpia = (
        serie.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.replace("*", "0", regex=False)
        .str.strip()
    )
    return pd.to_numeric(limpia, errors="coerce").fillna(0.0)


@st.cache_data(show_spinner=False)
def cargar_base_nacional_sii(fuente_archivo):
    """
    Carga la hoja 'Datos' (o la primera hoja tabular con microdatos comunales/rubros)
    desde el archivo Excel del repositorio o desde un archivo subido por el usuario.
    """
    xl = pd.ExcelFile(fuente_archivo)
    hojas = xl.sheet_names

    hoja_datos = None
    for h in hojas:
        if _normalizar_texto(h) in ["datos", "base", "sii", "base_sii", "microdatos"]:
            hoja_datos = h
            break
    if hoja_datos is None:
        hoja_datos = hojas[0]

    df = xl.parse(hoja_datos)
    df.columns = [str(c).strip() for c in df.columns]

    col_anio = _buscar_columna(df.columns, ["Año Comercial", "Anio Comercial", "Año", "Periodo"])
    col_region = _buscar_columna(df.columns, ["Región del domicilio o casa matriz", "Region del domicilio", "Región", "Region"])
    col_comuna = _buscar_columna(df.columns, ["Comuna del domicilio o casa matriz", "Comuna del domicilio", "Comuna"])
    col_rubro = _buscar_columna(df.columns, ["Rubro económico", "Rubro economico", "Rubro", "Sector"])

    posibles_metricas = [
        "Ventas anuales en UF",
        "Número de trabajadores dependientes informados",
        "Numero de trabajadores dependientes informados",
        "Número de empresas",
        "Numero de empresas",
        "Renta neta informada en UF",
        "Trabajadores ponderados por meses",
    ]
    columnas_metricas = []
    for c in df.columns:
        if c not in [col_anio, col_region, col_comuna, col_rubro]:
            if any(_normalizar_texto(m) in _normalizar_texto(c) for m in posibles_metricas):
                columnas_metricas.append(c)

    if not columnas_metricas:
        for c in df.columns:
            if c not in [col_anio, col_region, col_comuna, col_rubro]:
                if pd.api.types.is_numeric_dtype(df[c]):
                    columnas_metricas.append(c)

    for m in columnas_metricas:
        df[m] = _a_numero_sii(df[m])

    if col_anio:
        df[col_anio] = pd.to_numeric(df[col_anio], errors="coerce").dropna().astype(int)

    metadatos = {
        "hoja_leida": hoja_datos,
        "hojas_disponibles": hojas,
        "col_anio": col_anio,
        "col_region": col_region,
        "col_comuna": col_comuna,
        "col_rubro": col_rubro,
        "columnas_metricas": columnas_metricas,
    }
    return df, metadatos


def construir_matrices_region(
    df: pd.DataFrame,
    meta: dict,
    region_sel: str,
    anio_0: int,
    anio_t: int,
    variable_sel: str,
):
    """
    Filtra la base del SII por región y construye las matrices Rubro x Comuna
    para el año inicial (V0) y el año final (Vt), asegurando alineación exacta.
    """
    col_anio = meta["col_anio"]
    col_region = meta["col_region"]
    col_comuna = meta["col_comuna"]
    col_rubro = meta["col_rubro"]

    df_trab = df.copy()
    if col_region and region_sel and region_sel != "Todas (Consolidado)":
        df_trab = df_trab[df_trab[col_region].astype(str).str.strip() == str(region_sel).strip()]

    df_trab = df_trab.dropna(subset=[col_comuna, col_rubro, col_anio])
    df_trab[col_comuna] = df_trab[col_comuna].astype(str).str.strip()
    df_trab[col_rubro] = df_trab[col_rubro].astype(str).str.strip()

    exclusiones = ["total", "sin informacion", "sin información"]
    df_trab = df_trab[
        ~df_trab[col_comuna].apply(lambda x: _normalizar_texto(x) in exclusiones)
    ]

    df_0 = df_trab[df_trab[col_anio] == int(anio_0)]
    df_t = df_trab[df_trab[col_anio] == int(anio_t)]

    comunas = sorted(list(set(df_0[col_comuna].unique()).union(set(df_t[col_comuna].unique()))))
    rubros = sorted(list(set(df_0[col_rubro].unique()).union(set(df_t[col_rubro].unique()))))

    piv_0 = (
        df_0.pivot_table(
            index=col_rubro,
            columns=col_comuna,
            values=variable_sel,
            aggfunc="sum",
            fill_value=0.0,
        )
        .reindex(index=rubros, columns=comunas, fill_value=0.0)
        .astype(float)
    )

    piv_t = (
        df_t.pivot_table(
            index=col_rubro,
            columns=col_comuna,
            values=variable_sel,
            aggfunc="sum",
            fill_value=0.0,
        )
        .reindex(index=rubros, columns=comunas, fill_value=0.0)
        .astype(float)
    )

    comunas_activas = [c for c in comunas if (piv_0[c].sum() + piv_t[c].sum()) > 0]
    rubros_activos = [r for r in rubros if (piv_0.loc[r].sum() + piv_t.loc[r].sum()) > 0]

    piv_0 = piv_0.loc[rubros_activos, comunas_activas]
    piv_t = piv_t.loc[rubros_activos, comunas_activas]

    return piv_0, piv_t


def _calcular_gini_y_lorenz(valores: np.ndarray):
    x = np.asarray(valores, dtype=float)
    x = x[np.isfinite(x)]
    x = np.maximum(x, 0.0)
    n = len(x)
    if n == 0 or np.sum(x) == 0:
        return 0.0, 0.0, np.array([0.0, 1.0]), np.array([0.0, 1.0])

    x_ord = np.sort(x)
    acum_x = np.cumsum(x_ord)
    p = np.arange(1, n + 1) / n
    lorenz_y = acum_x / acum_x[-1]

    p_full = np.concatenate([[0.0], p])
    l_full = np.concatenate([[0.0], lorenz_y])

    indices = np.arange(1, n + 1)
    gini = (2.0 * np.sum(indices * x_ord) / (n * np.sum(x_ord))) - ((n + 1.0) / n)
    gini = float(max(0.0, gini))
    gini_norm = float(gini * (n / (n - 1.0))) if n > 1 else gini
    return gini, gini_norm, p_full, l_full


def _calcular_theil(valores: np.ndarray) -> float:
    x = np.asarray(valores, dtype=float)
    x = x[x > 0]
    n = len(x)
    if n <= 1 or np.sum(x) == 0:
        return 0.0
    media = np.mean(x)
    ratios = x / media
    theil = float(np.sum(ratios * np.log(ratios)) / n)
    return max(0.0, theil)


def _calcular_hhi_hk(valores: np.ndarray, alpha: float = 2.0):
    x = np.asarray(valores, dtype=float)
    x = np.maximum(x, 0.0)
    total = np.sum(x)
    n = len(x)
    if total <= 0 or n == 0:
        return 0.0, 0.0, 0.0
    s = x / total
    hhi = float(np.sum(s ** 2))
    hhi_norm = float((hhi - (1.0 / n)) / (1.0 - (1.0 / n))) if n > 1 else 1.0

    s_pos = s[s > 0]
    if abs(alpha - 1.0) < 1e-6:
        hk = float(np.exp(-np.sum(s_pos * np.log(s_pos))))
    else:
        hk = float((np.sum(s_pos ** alpha)) ** (1.0 / (1.0 - alpha)))
    return hhi, max(0.0, hhi_norm), hk


def calcular_todo_el_ramo(
    V0: pd.DataFrame,
    Vt: pd.DataFrame,
    anio_0: int,
    anio_t: int,
    alpha_hk: float = 2.0,
):
    """
    Ejecuta todos los cálculos de Análisis Regional (ILPES / CEPAL),
    Base Económica Exportadora, Shift & Share (MADE Clásico y Modificado)
    y Disparidades / Convergencia Regional (Motor REAT).
    """
    rubros = list(V0.index)
    comunas = list(V0.columns)
    eps = 1e-12

    total_comuna_0 = V0.sum(axis=0)
    total_rubro_0 = V0.sum(axis=1)
    total_reg_0 = float(total_comuna_0.sum())

    total_comuna_t = Vt.sum(axis=0)
    total_rubro_t = Vt.sum(axis=1)
    total_reg_t = float(total_comuna_t.sum())

    # 1. Participaciones P_ij y Cociente de Localización Q_ij (en t0 y tf)
    P_ij_0 = V0.divide(total_comuna_0.replace(0, np.nan), axis=1).fillna(0.0)
    P_i_reg_0 = (total_rubro_0 / max(total_reg_0, eps)).fillna(0.0)
    Q_ij_0 = P_ij_0.divide(P_i_reg_0.replace(0, np.nan), axis=0).fillna(0.0)

    P_ij_t = Vt.divide(total_comuna_t.replace(0, np.nan), axis=1).fillna(0.0)
    P_i_reg_t = (total_rubro_t / max(total_reg_t, eps)).fillna(0.0)
    Q_ij_t = P_ij_t.divide(P_i_reg_t.replace(0, np.nan), axis=0).fillna(0.0)

    # 2. Coeficiente de Especialización (Qr) en t0 y tf, y Reestructuración (CRr)
    diff_esp_0 = P_ij_0.subtract(P_i_reg_0, axis=0).abs()
    Qr_0 = 0.5 * diff_esp_0.sum(axis=0)

    diff_esp_t = P_ij_t.subtract(P_i_reg_t, axis=0).abs()
    Qr_t = 0.5 * diff_esp_t.sum(axis=0)

    diff_reest = (P_ij_t - P_ij_0).abs()
    CRr = 0.5 * diff_reest.sum(axis=0)

    # 3. Producción Básica Exportable (X_ij) y Multiplicador Básico Regional (M_j)
    esperado_reg_0 = pd.DataFrame(
        np.outer(P_i_reg_0.values, total_comuna_0.values),
        index=rubros,
        columns=comunas,
    )
    X_ij_0 = (V0 - esperado_reg_0).clip(lower=0.0)

    esperado_reg_t = pd.DataFrame(
        np.outer(P_i_reg_t.values, total_comuna_t.values),
        index=rubros,
        columns=comunas,
    )
    X_ij_t = (Vt - esperado_reg_t).clip(lower=0.0)

    X_j_0 = X_ij_0.sum(axis=0)
    X_j_t = X_ij_t.sum(axis=0)

    mult_basico_0 = (total_comuna_0 / X_j_0.replace(0, np.nan)).fillna(0.0)
    mult_basico_t = (total_comuna_t / X_j_t.replace(0, np.nan)).fillna(0.0)

    df_especializacion = pd.DataFrame({
        "Comuna": comunas,
        f"Total_{anio_0}": total_comuna_0.values,
        f"Total_{anio_t}": total_comuna_t.values,
        f"Part_Reg_{anio_0}_%": (total_comuna_0.values / max(total_reg_0, eps)) * 100.0,
        f"Part_Reg_{anio_t}_%": (total_comuna_t.values / max(total_reg_t, eps)) * 100.0,
        f"Qr_Especializacion_{anio_0}": Qr_0.values,
        f"Qr_Especializacion_{anio_t}": Qr_t.values,
        "CRr_Reestructuracion": CRr.values,
        f"Base_Exportadora_Xj_{anio_t}": X_j_t.values,
        f"Prop_Basica_{anio_t}_%": np.where(
            total_comuna_t.values > 0,
            (X_j_t.values / total_comuna_t.values) * 100.0,
            0.0,
        ),
        f"Multiplicador_Basico_Mj_{anio_t}": mult_basico_t.values,
    })

    # 4. Descomposición Shift & Share (MADE Clásico y MADE Modificado)
    r_reg = (total_reg_t / max(total_reg_0, eps)) if total_reg_0 > 0 else 1.0
    r_i_sec = (total_rubro_t / total_rubro_0.replace(0, np.nan)).fillna(1.0)

    ET_j = total_comuna_t - total_comuna_0
    EG_j = total_comuna_0 * (r_reg - 1.0)

    diff_tasas_sec = r_i_sec - r_reg
    EE_mat = V0.multiply(diff_tasas_sec, axis=0)
    EE_j = EE_mat.sum(axis=0)

    esperado_sec = V0.multiply(r_i_sec, axis=0)
    ED_mat = Vt - esperado_sec
    ED_j = ED_mat.sum(axis=0)

    V_homotetica_t = pd.DataFrame(
        np.outer(P_i_reg_t.values, total_comuna_0.values),
        index=rubros,
        columns=comunas,
    )
    EI_mat = (V_homotetica_t - V0).multiply(r_i_sec - 1.0, axis=0)
    EI_j = EI_mat.sum(axis=0)

    EM_j = EE_j + EI_j
    ERM_j = ET_j - EM_j

    # Clasificación de Cuadrantes de Silva Lira (CEPAL, 2005)
    tasa_var_comuna = np.where(
        total_comuna_0.values > 0,
        ((total_comuna_t.values - total_comuna_0.values) / total_comuna_0.values) * 100.0,
        0.0,
    )
    tasa_var_reg = ((total_reg_t - total_reg_0) / max(total_reg_0, eps)) * 100.0
    part_media_comunal = 100.0 / max(len(comunas), 1)
    part_inicial_pct = (total_comuna_0.values / max(total_reg_0, eps)) * 100.0

    cuadrantes_silva = []
    tipologia_shift = []
    for idx in range(len(comunas)):
        crece_mas = tasa_var_comuna[idx] >= tasa_var_reg
        alto_peso = part_inicial_pct[idx] >= part_media_comunal
        if crece_mas and alto_peso:
            cuadrantes_silva.append("I. Dinámica (Alto Peso y Alto Crecimiento)")
        elif crece_mas and not alto_peso:
            cuadrantes_silva.append("II. Emergente / Convergente (Bajo Peso y Alto Crecimiento)")
        elif not crece_mas and alto_peso:
            cuadrantes_silva.append("III. Estancada / Madura (Alto Peso y Bajo Crecimiento)")
        else:
            cuadrantes_silva.append("IV. En Retroceso / Rezagada (Bajo Peso y Bajo Crecimiento)")

        ee_val = EE_j.values[idx]
        ed_val = ED_j.values[idx]
        if ee_val >= 0 and ed_val >= 0:
            tipologia_shift.append("Tipo I: Estructura Favorable + Dinamismo Local (+,+)")
        elif ee_val >= 0 and ed_val < 0:
            tipologia_shift.append("Tipo II: Estructura Favorable pero Pérdida Competitiva (+,-)")
        elif ee_val < 0 and ed_val >= 0:
            tipologia_shift.append("Tipo III: Estructura Desfavorable compensada por Competitividad (-,+)")
        else:
            tipologia_shift.append("Tipo IV: Rezago Estructural y Competitivo (-,-)")

    df_shift_share = pd.DataFrame({
        "Comuna": comunas,
        f"Nivel_{anio_0}": total_comuna_0.values,
        f"Nivel_{anio_t}": total_comuna_t.values,
        "Var_Absoluta": (total_comuna_t - total_comuna_0).values,
        "Var_Porcentual_%": tasa_var_comuna,
        "Efecto_Global_EG": EG_j.values,
        "Efecto_Total_ET": ET_j.values,
        "Efecto_Estructural_EE": EE_j.values,
        "Efecto_Diferencial_ED": ED_j.values,
        "Efecto_Inverso_EI": EI_j.values,
        "Efecto_Estructural_Mod_EM": EM_j.values,
        "Efecto_Regional_Mod_ERM": ERM_j.values,
        "Tipologia_Shift_Share": tipologia_shift,
        "Cuadrante_Silva_Lira": cuadrantes_silva,
    })

    # 5. Motor REAT: Disparidades, Concentración y Convergencia Regional (Sigma y Beta)
    y0 = total_comuna_0.values.astype(float)
    yt = total_comuna_t.values.astype(float)
    mask_pos = (y0 > 0) & (yt > 0)

    T_anios = max(int(anio_t) - int(anio_0), 1)
    ln_y0 = np.log(np.maximum(y0[mask_pos], eps))
    ln_yt = np.log(np.maximum(yt[mask_pos], eps))
    crec_anual_log = (ln_yt - ln_y0) / T_anios

    sigma_0 = float(np.std(ln_y0, ddof=1)) if len(ln_y0) > 1 else 0.0
    sigma_t = float(np.std(ln_yt, ddof=1)) if len(ln_yt) > 1 else 0.0
    cv_0 = float(np.std(y0, ddof=1) / np.mean(y0)) if np.mean(y0) > 0 and len(y0) > 1 else 0.0
    cv_t = float(np.std(yt, ddof=1) / np.mean(yt)) if np.mean(yt) > 0 and len(yt) > 1 else 0.0

    if len(ln_y0) > 2:
        ols = stats.linregress(ln_y0, crec_anual_log)
        beta_ols = float(ols.slope)
        alpha_ols = float(ols.intercept)
        r2_ols = float(ols.rvalue ** 2)
        p_val_ols = float(ols.pvalue)
        std_err_ols = float(ols.stderr)
    else:
        beta_ols, alpha_ols, r2_ols, p_val_ols, std_err_ols = 0.0, 0.0, 0.0, 1.0, 0.0

    val_interior = 1.0 + beta_ols * T_anios
    if beta_ols < 0 and val_interior > 0:
        velocidad_lambda = float(-np.log(val_interior) / T_anios)
        half_life = float(np.log(2.0) / velocidad_lambda) if velocidad_lambda > 0 else np.nan
    else:
        velocidad_lambda = 0.0
        half_life = np.nan

    gini_0, gini_norm_0, lorenz_p_0, lorenz_l_0 = _calcular_gini_y_lorenz(y0)
    gini_t, gini_norm_t, lorenz_p_t, lorenz_l_t = _calcular_gini_y_lorenz(yt)

    theil_0 = _calcular_theil(y0)
    theil_t = _calcular_theil(yt)

    hhi_0, hhi_norm_0, hk_0 = _calcular_hhi_hk(y0, alpha=alpha_hk)
    hhi_t, hhi_norm_t, hk_t = _calcular_hhi_hk(yt, alpha=alpha_hk)

    df_reat_resumen = pd.DataFrame([
        {
            "Indicador_REAT": "Desviación Estándar Logarítmica (Sigma Convergencia)",
            f"Año_{anio_0}": sigma_0,
            f"Año_{anio_t}": sigma_t,
            "Variacion": sigma_t - sigma_0,
            "Interpretacion_Econometrica": (
                "Convergencia Sigma (Reducción de disparidades)"
                if sigma_t < sigma_0
                else "Divergencia Sigma (Aumento de disparidades)"
            ),
        },
        {
            "Indicador_REAT": "Coeficiente de Variación (CV)",
            f"Año_{anio_0}": cv_0,
            f"Año_{anio_t}": cv_t,
            "Variacion": cv_t - cv_0,
            "Interpretacion_Econometrica": (
                "Menor dispersión relativa" if cv_t < cv_0 else "Mayor dispersión relativa"
            ),
        },
        {
            "Indicador_REAT": "Índice de Gini Estándar (G)",
            f"Año_{anio_0}": gini_0,
            f"Año_{anio_t}": gini_t,
            "Variacion": gini_t - gini_0,
            "Interpretacion_Econometrica": (
                "Menor concentración territorial" if gini_t < gini_0 else "Mayor concentración territorial"
            ),
        },
        {
            "Indicador_REAT": "Índice de Gini Normalizado (G*)",
            f"Año_{anio_0}": gini_norm_0,
            f"Año_{anio_t}": gini_norm_t,
            "Variacion": gini_norm_t - gini_norm_0,
            "Interpretacion_Econometrica": "Ajustado por tamaño muestral N/(N-1)",
        },
        {
            "Indicador_REAT": "Índice de Entropía de Theil (T)",
            f"Año_{anio_0}": theil_0,
            f"Año_{anio_t}": theil_t,
            "Variacion": theil_t - theil_0,
            "Interpretacion_Econometrica": (
                "Menor desigualdad inter-comunal" if theil_t < theil_0 else "Mayor desigualdad inter-comunal"
            ),
        },
        {
            "Indicador_REAT": "Índice de Herfindahl-Hirschman (HHI)",
            f"Año_{anio_0}": hhi_0,
            f"Año_{anio_t}": hhi_t,
            "Variacion": hhi_t - hhi_0,
            "Interpretacion_Econometrica": f"HHI Normalizado final = {hhi_norm_t:.4f}",
        },
        {
            "Indicador_REAT": f"Índice de Hannah-Kay HK(alpha={alpha_hk}) - N° Equivalente",
            f"Año_{anio_0}": hk_0,
            f"Año_{anio_t}": hk_t,
            "Variacion": hk_t - hk_0,
            "Interpretacion_Econometrica": "Número efectivo de comunas equivalentes",
        },
    ])

    df_beta_comunas = pd.DataFrame({
        "Comuna": np.array(comunas)[mask_pos],
        f"Nivel_{anio_0}": y0[mask_pos],
        f"Nivel_{anio_t}": yt[mask_pos],
        f"ln_Y_{anio_0}": ln_y0,
        f"ln_Y_{anio_t}": ln_yt,
        "Tasa_Crec_Anual_Log": crec_anual_log,
        "Prediccion_OLS": alpha_ols + beta_ols * ln_y0,
    })

    metricas_beta = {
        "beta": beta_ols,
        "alpha": alpha_ols,
        "r2": r2_ols,
        "p_value": p_val_ols,
        "std_err": std_err_ols,
        "velocidad_lambda": velocidad_lambda,
        "half_life": half_life,
        "T_anios": T_anios,
        "lorenz_p_0": lorenz_p_0,
        "lorenz_l_0": lorenz_l_0,
        "lorenz_p_t": lorenz_p_t,
        "lorenz_l_t": lorenz_l_t,
    }

    return {
        "V0": V0,
        "Vt": Vt,
        "P_ij_0": P_ij_0,
        "P_ij_t": P_ij_t,
        "P_i_reg_0": P_i_reg_0,
        "P_i_reg_t": P_i_reg_t,
        "Q_ij_0": Q_ij_0,
        "Q_ij_t": Q_ij_t,
        "diff_esp_0": diff_esp_0,
        "diff_esp_t": diff_esp_t,
        "diff_reest": diff_reest,
        "X_ij_0": X_ij_0,
        "X_ij_t": X_ij_t,
        "df_especializacion": df_especializacion,
        "df_shift_share": df_shift_share,
        "df_reat_resumen": df_reat_resumen,
        "df_beta_comunas": df_beta_comunas,
        "metricas_beta": metricas_beta,
        "totales": {
            "total_reg_0": total_reg_0,
            "total_reg_t": total_reg_t,
            "tasa_var_reg": tasa_var_reg,
            "n_comunas": len(comunas),
            "n_rubros": len(rubros),
        },
    }


def _estilizar_hoja_excel(ws, titulo_hoja: str, subtitulo: str, df_tabla: pd.DataFrame):
    fill_titulo = PatternFill("solid", fgColor="1B365D")
    fill_header = PatternFill("solid", fgColor="2C5282")
    fill_zebra = PatternFill("solid", fgColor="F4F7FA")

    font_titulo = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="1B365D")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_celda = Font(name="Calibri", size=10, color="111111")

    borde_fino = Border(
        left=Side(style="thin", color="D0D7DE"),
        right=Side(style="thin", color="D0D7DE"),
        top=Side(style="thin", color="D0D7DE"),
        bottom=Side(style="thin", color="D0D7DE"),
    )

    n_cols = max(len(df_tabla.columns), 2)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols)
    celda_t = ws.cell(row=1, column=1, value=titulo_hoja)
    celda_t.fill = fill_titulo
    celda_t.font = font_titulo
    celda_t.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 26

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols)
    celda_sub = ws.cell(row=2, column=1, value=subtitulo)
    celda_sub.font = font_sub
    celda_sub.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[2].height = 19

    fila_header = 4
    for col_idx, col_name in enumerate(df_tabla.columns, start=1):
        c = ws.cell(row=fila_header, column=col_idx, value=str(col_name))
        c.fill = fill_header
        c.font = font_header
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = borde_fino
    ws.row_dimensions[fila_header].height = 24

    for r_idx, row_vals in enumerate(df_tabla.itertuples(index=False), start=fila_header + 1):
        es_par = (r_idx % 2 == 0)
        for c_idx, val in enumerate(row_vals, start=1):
            if isinstance(val, (np.floating, float)):
                val_clean = float(val) if np.isfinite(val) else 0.0
            elif isinstance(val, (np.integer, int)):
                val_clean = int(val)
            else:
                val_clean = val

            celda = ws.cell(row=r_idx, column=c_idx, value=val_clean)
            celda.font = font_celda
            celda.border = borde_fino
            if es_par:
                celda.fill = fill_zebra

            if isinstance(val_clean, float):
                if abs(val_clean) >= 100:
                    celda.number_format = "#,##0.00"
                else:
                    celda.number_format = "0.0000"
                celda.alignment = Alignment(horizontal="right", vertical="center")
            elif isinstance(val_clean, int):
                celda.number_format = "#,##0"
                celda.alignment = Alignment(horizontal="right", vertical="center")
            else:
                celda.alignment = Alignment(horizontal="left", vertical="center")

    ws.freeze_panes = "B5"
    for col_idx in range(1, len(df_tabla.columns) + 1):
        col_letter = get_column_letter(col_idx)
        max_len = max(
            len(str(ws.cell(row=r, column=col_idx).value or ""))
            for r in range(fila_header, min(fila_header + len(df_tabla) + 1, fila_header + 60))
        )
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, 38), 13)


def _autoajustar_columnas_hoja(ws, max_width: int = 34, min_width: int = 12):
    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for r_idx in range(3, min(ws.max_row + 1, 95)):
            val = ws.cell(row=r_idx, column=col_idx).value
            if val is not None:
                s_val = str(val)
                if not s_val.startswith("="):
                    max_len = max(max_len, len(s_val))
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, max_width), min_width)


def compilar_excel_10_hojas(
    resultados: dict,
    region_sel: str,
    variable_sel: str,
    anio_0: int,
    anio_t: int,
    alpha_hk: float = 2.0,
) -> bytes:
    """
    Genera en memoria un libro Excel (.xlsx) con 10 hojas completas, incluyendo:
    - Formato condicional rosado/rojo (#FFC7CE / #9C0006) en Localización Q_ij (bloques t0 y tf).
    - Matriz Rubro x Comuna de Especialización |P_ij - P_i| con franja gris y fórmula =SUM(...)/2.
    - Base Exportable X_ij con celdas limpias en blanco cuando Q_ij <= 1, resaltado rosado y filas X_j y M_j con fórmulas vivas.
    - Hoja 07_Cuadrantes_Silva con fórmulas vivas, colores por cuadrante, Matriz Visual 2x2 y ScatterChart nativo de Excel.
    """
    wb = Workbook()
    wb.remove(wb.active)

    sub_general = (
        f"Región: {region_sel} | Variable: {variable_sel} | "
        f"Periodo: {anio_0}-{anio_t} | Universidad de Los Lagos"
    )

    # Paleta de estilos reutilizables
    fill_titulo = PatternFill("solid", fgColor="1B365D")
    fill_header = PatternFill("solid", fgColor="2C5282")
    fill_subbloque = PatternFill("solid", fgColor="D9E1F2")
    fill_gris_total = PatternFill("solid", fgColor="D9D9D9")
    fill_amarillo_ref = PatternFill("solid", fgColor="FFFFCC")
    fill_rosado_q = PatternFill("solid", fgColor="FFC7CE")

    # Colores de Cuadrantes de Silva Lira
    fill_cuad_1 = PatternFill("solid", fgColor="D9EAD3")  # Verde suave: Dinámica (I)
    fill_cuad_2 = PatternFill("solid", fgColor="FFFFCC")  # Amarillo suave: Emergente (II)
    fill_cuad_3 = PatternFill("solid", fgColor="FCE5CD")  # Damasco suave: Estancada (III)
    fill_cuad_4 = PatternFill("solid", fgColor="F2DBDB")  # Rosado suave: En Retroceso (IV)

    font_titulo = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="1B365D")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_subbloque = Font(name="Calibri", size=11, bold=True, color="1B365D")
    font_bold = Font(name="Calibri", size=10, bold=True, color="111111")
    font_celda = Font(name="Calibri", size=10, color="111111")
    font_rojo_q = Font(name="Calibri", size=10, bold=True, color="9C0006")

    borde_fino = Border(
        left=Side(style="thin", color="D0D7DE"),
        right=Side(style="thin", color="D0D7DE"),
        top=Side(style="thin", color="D0D7DE"),
        bottom=Side(style="thin", color="D0D7DE"),
    )
    borde_total = Border(
        left=Side(style="thin", color="888888"),
        right=Side(style="thin", color="888888"),
        top=Side(style="medium", color="1B365D"),
        bottom=Side(style="double", color="1B365D"),
    )

    mb = resultados["metricas_beta"]
    tot = resultados["totales"]
    V0 = resultados["V0"]
    Vt = resultados["Vt"]
    Q0 = resultados["Q_ij_0"]
    Qt = resultados["Q_ij_t"]
    X0 = resultados["X_ij_0"]
    Xt = resultados["X_ij_t"]
    rubros = list(V0.index)
    comunas = list(V0.columns)
    n_rubros = len(rubros)
    n_comunas = len(comunas)

    # ==========================================================================
    # HOJA 1: PORTADA Y RESUMEN EJECUTIVO
    # ==========================================================================
    df_portada = pd.DataFrame([
        {"Parametro_Indicador": "Región Analizada", "Valor": str(region_sel)},
        {"Parametro_Indicador": "Variable Económica SII", "Valor": str(variable_sel)},
        {"Parametro_Indicador": "Periodo de Análisis", "Valor": f"{anio_0} - {anio_t} ({mb['T_anios']} años)"},
        {"Parametro_Indicador": "Número de Comunas Activas", "Valor": tot["n_comunas"]},
        {"Parametro_Indicador": "Número de Rubros Económicos SII", "Valor": tot["n_rubros"]},
        {"Parametro_Indicador": f"Total Regional {anio_0}", "Valor": tot["total_reg_0"]},
        {"Parametro_Indicador": f"Total Regional {anio_t}", "Valor": tot["total_reg_t"]},
        {"Parametro_Indicador": "Variación Regional Acumulada (%)", "Valor": tot["tasa_var_reg"]},
        {"Parametro_Indicador": "Pendiente Beta Absoluta (OLS)", "Valor": mb["beta"]},
        {"Parametro_Indicador": "Intercepto Alpha (OLS)", "Valor": mb["alpha"]},
        {"Parametro_Indicador": "Bondad de Ajuste R² (Convergencia Beta)", "Valor": mb["r2"]},
        {"Parametro_Indicador": "P-Valor Regresión Beta", "Valor": mb["p_value"]},
        {"Parametro_Indicador": "Velocidad de Convergencia (Lambda anual)", "Valor": mb["velocidad_lambda"]},
        {
            "Parametro_Indicador": "Semivida (Half-Life en años)",
            "Valor": float(mb["half_life"]) if np.isfinite(mb["half_life"]) else "No aplica (Divergencia)",
        },
    ])
    ws1 = wb.create_sheet("01_Portada_Resumen")
    _estilizar_hoja_excel(
        ws1,
        "FICHA RESUMEN EJECUTIVA - MOTOR ECONOMÉTRICO SII / ILPES / REAT",
        sub_general,
        df_portada,
    )

    # ==========================================================================
    # HOJAS 2 Y 3: MATRICES BASE V0 Y Vt CON FÓRMULAS =SUM(...)
    # ==========================================================================
    for idx_h, (anio_mat, df_mat, pref_h) in enumerate(
        [(anio_0, V0, "02_Matriz_Base"), (anio_t, Vt, "03_Matriz_Base")], start=2
    ):
        ws_m = wb.create_sheet(f"{pref_h}_{anio_mat}")
        n_cols_m = n_comunas + 2
        ws_m.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_m)
        ct = ws_m.cell(row=1, column=1, value=f"MATRIZ SECTORIAL-COMUNAL (AÑO {anio_mat}) - {variable_sel.upper()}")
        ct.fill = fill_titulo
        ct.font = font_titulo
        ws_m.row_dimensions[1].height = 25

        ws_m.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_m)
        cs = ws_m.cell(row=2, column=1, value=sub_general)
        cs.font = font_sub

        headers_m = ["Rubro Económico SII"] + comunas + [f"TOTAL RUBRO {anio_mat}"]
        for c_i, h_txt in enumerate(headers_m, start=1):
            ch = ws_m.cell(row=4, column=c_i, value=h_txt)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws_m.row_dimensions[4].height = 24

        ult_col_com_let = get_column_letter(1 + n_comunas)
        fila_ini_m = 5
        for r_i, rubro in enumerate(rubros, start=fila_ini_m):
            cr = ws_m.cell(row=r_i, column=1, value=rubro)
            cr.font = font_celda
            cr.border = borde_fino
            for c_i, com in enumerate(comunas, start=2):
                val = float(df_mat.loc[rubro, com])
                cc = ws_m.cell(row=r_i, column=c_i, value=val)
                cc.font = font_celda
                cc.number_format = "#,##0.00"
                cc.alignment = Alignment(horizontal="right", vertical="center")
                cc.border = borde_fino
            c_tot_r = ws_m.cell(row=r_i, column=n_comunas + 2, value=f"=SUM(B{r_i}:{ult_col_com_let}{r_i})")
            c_tot_r.font = font_bold
            c_tot_r.fill = fill_subbloque
            c_tot_r.number_format = "#,##0.00"
            c_tot_r.border = borde_fino

        fila_tot_m = fila_ini_m + n_rubros
        ct_lbl = ws_m.cell(row=fila_tot_m, column=1, value=f"TOTAL COMUNAL {anio_mat}")
        ct_lbl.font = font_bold
        ct_lbl.fill = fill_gris_total
        ct_lbl.border = borde_total

        for c_i in range(2, n_comunas + 3):
            col_l = get_column_letter(c_i)
            c_sum = ws_m.cell(row=fila_tot_m, column=c_i, value=f"=SUM({col_l}{fila_ini_m}:{col_l}{fila_tot_m-1})")
            c_sum.font = font_bold
            c_sum.fill = fill_gris_total
            c_sum.number_format = "#,##0.00"
            c_sum.border = borde_total

        ws_m.freeze_panes = "B5"
        _autoajustar_columnas_hoja(ws_m)

    # ==========================================================================
    # HOJA 4: COCIENTE DE LOCALIZACIÓN Q_ij (BLOQUES t0 Y tf + ROSADO #FFC7CE)
    # ==========================================================================
    ws4 = wb.create_sheet("04_Localizacion_Qij")
    n_cols_q = n_comunas + 1
    ws4.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_q)
    c4_t = ws4.cell(row=1, column=1, value=f"COCIENTE DE LOCALIZACIÓN (Qij) — COMPARATIVO AÑOS {anio_0} Y {anio_t}")
    c4_t.fill = fill_titulo
    c4_t.font = font_titulo
    ws4.row_dimensions[1].height = 26

    ws4.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_q)
    c4_s = ws4.cell(
        row=2,
        column=1,
        value="Celdas resaltadas en rosado (#FFC7CE) y texto rojo (#9C0006) indican especialización relativa exportadora (Qij > 1)",
    )
    c4_s.font = font_sub

    regla_q_mayor_1 = CellIsRule(
        operator="greaterThan",
        formula=["1"],
        stopIfTrue=True,
        fill=fill_rosado_q,
        font=font_rojo_q,
    )

    fila_cursor = 4
    for etq_anio, mat_q in [(anio_0, Q0), (anio_t, Qt)]:
        ws4.merge_cells(start_row=fila_cursor, start_column=1, end_row=fila_cursor, end_column=n_cols_q)
        cb = ws4.cell(row=fila_cursor, column=1, value=f"BLOQUE COCIENTE DE LOCALIZACIÓN (Qij) — AÑO {etq_anio}")
        cb.fill = fill_subbloque
        cb.font = font_subbloque
        ws4.row_dimensions[fila_cursor].height = 21
        fila_cursor += 1

        headers_q = [f"Rubro Económico ({etq_anio})"] + comunas
        for c_i, h_txt in enumerate(headers_q, start=1):
            ch = ws4.cell(row=fila_cursor, column=c_i, value=h_txt)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws4.row_dimensions[fila_cursor].height = 24
        fila_cursor += 1

        fila_ini_bloque_q = fila_cursor
        for rubro in rubros:
            cr = ws4.cell(row=fila_cursor, column=1, value=rubro)
            cr.font = font_celda
            cr.border = borde_fino
            for c_i, com in enumerate(comunas, start=2):
                val_q = float(mat_q.loc[rubro, com])
                cc = ws4.cell(row=fila_cursor, column=c_i, value=val_q)
                cc.number_format = "0.0000"
                cc.alignment = Alignment(horizontal="right", vertical="center")
                cc.border = borde_fino
                if val_q > 1.0:
                    cc.fill = fill_rosado_q
                    cc.font = font_rojo_q
                else:
                    cc.font = font_celda
            fila_cursor += 1

        fila_fin_bloque_q = fila_cursor - 1
        rango_q = f"B{fila_ini_bloque_q}:{get_column_letter(n_cols_q)}{fila_fin_bloque_q}"
        ws4.conditional_formatting.add(rango_q, regla_q_mayor_1)
        fila_cursor += 2

    ws4.freeze_panes = "B6"
    _autoajustar_columnas_hoja(ws4)

    # ==========================================================================
    # HOJA 5: ESPECIALIZACIÓN (Qr) CON MATRIZ RUBRO x COMUNA Y FILA GRIS =SUM()/2
    # ==========================================================================
    ws5 = wb.create_sheet("05_Especializ_Qr_CRr")
    n_cols_e = n_comunas + 1
    ws5.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_e)
    c5_t = ws5.cell(
        row=1,
        column=1,
        value=f"COEFICIENTE DE ESPECIALIZACIÓN (Qr) — MATRIZ |Pij - Pi| Y FÓRMULA ACTIVA =SUM(...)/2 ({anio_0} Y {anio_t})",
    )
    c5_t.fill = fill_titulo
    c5_t.font = font_titulo
    ws5.row_dimensions[1].height = 26

    ws5.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_e)
    c5_s = ws5.cell(
        row=2,
        column=1,
        value="Cada bloque muestra la diferencia absoluta |Pij - Pi| por rubro y comuna, cerrando con la fila gris Coeficiente Especialización =SUM(...)/2",
    )
    c5_s.font = font_sub

    diff_0 = resultados["diff_esp_0"]
    diff_t = resultados["diff_esp_t"]

    fila_cur_5 = 4
    for etq_anio, mat_diff in [(anio_t, diff_t), (anio_0, diff_0)]:
        ws5.merge_cells(start_row=fila_cur_5, start_column=1, end_row=fila_cur_5, end_column=n_cols_e)
        cb = ws5.cell(
            row=fila_cur_5,
            column=1,
            value=f"MATRIZ DE DIFERENCIAS ABSOLUTAS |Pij - Pi| POR RUBRO Y COMUNA — AÑO {etq_anio}",
        )
        cb.fill = fill_subbloque
        cb.font = font_subbloque
        ws5.row_dimensions[fila_cur_5].height = 21
        fila_cur_5 += 1

        headers_e = [f"Rubro Económico ({etq_anio})"] + comunas
        for c_i, h_txt in enumerate(headers_e, start=1):
            ch = ws5.cell(row=fila_cur_5, column=c_i, value=h_txt)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws5.row_dimensions[fila_cur_5].height = 24
        fila_cur_5 += 1

        f_ini_d = fila_cur_5
        for rubro in rubros:
            cr = ws5.cell(row=fila_cur_5, column=1, value=rubro)
            cr.font = font_celda
            cr.border = borde_fino
            for c_i, com in enumerate(comunas, start=2):
                val_d = float(mat_diff.loc[rubro, com])
                cc = ws5.cell(row=fila_cur_5, column=c_i, value=val_d)
                cc.font = font_celda
                cc.number_format = "0.0000"
                cc.alignment = Alignment(horizontal="right", vertical="center")
                cc.border = borde_fino
            fila_cur_5 += 1
        f_fin_d = fila_cur_5 - 1

        # Franja gris con fórmula activa =SUM(...)/2 igual al Excel original
        c_qr_lbl = ws5.cell(row=fila_cur_5, column=1, value=f"Coeficiente Especialización (Qr {etq_anio})")
        c_qr_lbl.font = font_bold
        c_qr_lbl.fill = fill_gris_total
        c_qr_lbl.border = borde_total

        for c_i in range(2, n_cols_e + 1):
            col_l = get_column_letter(c_i)
            c_qr_val = ws5.cell(row=fila_cur_5, column=c_i, value=f"=SUM({col_l}{f_ini_d}:{col_l}{f_fin_d})/2")
            c_qr_val.font = font_bold
            c_qr_val.fill = fill_gris_total
            c_qr_val.number_format = "0.0000"
            c_qr_val.alignment = Alignment(horizontal="right", vertical="center")
            c_qr_val.border = borde_total

        ws5.row_dimensions[fila_cur_5].height = 22
        fila_cur_5 += 3

    # Tabla Resumen Consolidada al pie de la Hoja 5
    df_esp_res = resultados["df_especializacion"]
    ws5.merge_cells(start_row=fila_cur_5, start_column=1, end_row=fila_cur_5, end_column=len(df_esp_res.columns))
    c_res_t = ws5.cell(
        row=fila_cur_5,
        column=1,
        value="TABLA RESUMEN CONSOLIDADA POR COMUNA (Qr, CRr, BASE EXPORTADORA Xj Y MULTIPLICADOR Mj)",
    )
    c_res_t.fill = fill_subbloque
    c_res_t.font = font_subbloque
    fila_cur_5 += 1

    for c_i, col_name in enumerate(df_esp_res.columns, start=1):
        ch = ws5.cell(row=fila_cur_5, column=c_i, value=str(col_name))
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ch.border = borde_fino
    fila_cur_5 += 1

    for row_vals in df_esp_res.itertuples(index=False):
        for c_i, val in enumerate(row_vals, start=1):
            cc = ws5.cell(row=fila_cur_5, column=c_i, value=float(val) if isinstance(val, (int, float, np.number)) else val)
            cc.font = font_celda
            cc.border = borde_fino
            if isinstance(val, (int, float, np.number)):
                cc.number_format = "#,##0.00" if abs(float(val)) >= 100 else "0.0000"
                cc.alignment = Alignment(horizontal="right", vertical="center")
        fila_cur_5 += 1

    ws5.freeze_panes = "B6"
    _autoajustar_columnas_hoja(ws5)

    # ==========================================================================
    # HOJA 6: PRODUCCIÓN BÁSICA EXPORTABLE (CELDAS LIMPIAS + ROSADO + Xj y Mj)
    # ==========================================================================
    ws6 = wb.create_sheet("06_Prod_Basica_Export")
    n_cols_x = n_comunas + 2
    ws6.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_x)
    c6_t = ws6.cell(
        row=1,
        column=1,
        value=f"PRODUCCIÓN BÁSICA EXPORTABLE (Xij) Y MULTIPLICADOR BÁSICO (Mj) — AÑOS {anio_t} Y {anio_0}",
    )
    c6_t.fill = fill_titulo
    c6_t.font = font_titulo
    ws6.row_dimensions[1].height = 26

    ws6.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_x)
    c6_s = ws6.cell(
        row=2,
        column=1,
        value="Celdas sin excedente exportador (Qij <= 1) quedan en blanco; rubros exportadores (Xij > 0) se resaltan en rosado (#FFC7CE). Incluye Xj y Mj con fórmulas vivas.",
    )
    c6_s.font = font_sub

    regla_x_pos = CellIsRule(
        operator="greaterThan",
        formula=["0"],
        stopIfTrue=True,
        fill=fill_rosado_q,
        font=font_rojo_q,
    )

    fila_cur_6 = 4
    ult_col_com_x = get_column_letter(1 + n_comunas)

    for etq_anio, mat_x, mat_v in [(anio_t, Xt, Vt), (anio_0, X0, V0)]:
        ws6.merge_cells(start_row=fila_cur_6, start_column=1, end_row=fila_cur_6, end_column=n_cols_x)
        cb = ws6.cell(
            row=fila_cur_6,
            column=1,
            value=f"MATRIZ DE EXCEDENTE BÁSICO EXPORTABLE (Xij > 0) — AÑO {etq_anio}",
        )
        cb.fill = fill_subbloque
        cb.font = font_subbloque
        ws6.row_dimensions[fila_cur_6].height = 21
        fila_cur_6 += 1

        headers_x = [f"Rubro Económico ({etq_anio})"] + comunas + [f"Total Básico Rubro ({etq_anio})"]
        for c_i, h_txt in enumerate(headers_x, start=1):
            ch = ws6.cell(row=fila_cur_6, column=c_i, value=h_txt)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws6.row_dimensions[fila_cur_6].height = 24
        fila_cur_6 += 1

        f_ini_x = fila_cur_6
        for rubro in rubros:
            cr = ws6.cell(row=fila_cur_6, column=1, value=rubro)
            cr.font = font_celda
            cr.border = borde_fino
            for c_i, com in enumerate(comunas, start=2):
                val_x = float(mat_x.loc[rubro, com])
                # Dejar celda en blanco si no exporta (Xij <= 0)
                if val_x > 1e-6:
                    cc = ws6.cell(row=fila_cur_6, column=c_i, value=val_x)
                    cc.fill = fill_rosado_q
                    cc.font = font_rojo_q
                    cc.number_format = "#,##0.00"
                    cc.alignment = Alignment(horizontal="right", vertical="center")
                else:
                    cc = ws6.cell(row=fila_cur_6, column=c_i, value=None)
                    cc.font = font_celda
                cc.border = borde_fino

            c_tot_rub = ws6.cell(
                row=fila_cur_6,
                column=n_comunas + 2,
                value=f"=SUM(B{fila_cur_6}:{ult_col_com_x}{fila_cur_6})",
            )
            c_tot_rub.font = font_bold
            c_tot_rub.fill = fill_subbloque
            c_tot_rub.number_format = "#,##0.00"
            c_tot_rub.border = borde_fino
            fila_cur_6 += 1

        f_fin_x = fila_cur_6 - 1
        ws6.conditional_formatting.add(f"B{f_ini_x}:{ult_col_com_x}{f_fin_x}", regla_x_pos)

        # Fila 1 al pie: Total Actividad Comunal Vj (necesario para calcular Mj = Vj / Xj en vivo)
        f_vj = fila_cur_6
        c_vj_lbl = ws6.cell(row=f_vj, column=1, value=f"Vj (Actividad Total Comunal {etq_anio})")
        c_vj_lbl.font = font_bold
        c_vj_lbl.fill = fill_subbloque
        c_vj_lbl.border = borde_fino
        totales_com_anio = mat_v.sum(axis=0)
        for c_i, com in enumerate(comunas, start=2):
            cv = ws6.cell(row=f_vj, column=c_i, value=float(totales_com_anio[com]))
            cv.font = font_bold
            cv.fill = fill_subbloque
            cv.number_format = "#,##0.00"
            cv.border = borde_fino
        cv_tot = ws6.cell(row=f_vj, column=n_comunas + 2, value=f"=SUM(B{f_vj}:{ult_col_com_x}{f_vj})")
        cv_tot.font = font_bold
        cv_tot.fill = fill_subbloque
        cv_tot.number_format = "#,##0.00"
        cv_tot.border = borde_fino
        fila_cur_6 += 1

        # Fila 2 al pie: Xj = SUM(Xij) con fórmula activa
        f_xj = fila_cur_6
        c_xj_lbl = ws6.cell(row=f_xj, column=1, value=f"Xj (Producción Básica Exportable Total {etq_anio})")
        c_xj_lbl.font = font_bold
        c_xj_lbl.fill = fill_gris_total
        c_xj_lbl.border = borde_total
        for c_i in range(2, n_comunas + 3):
            col_l = get_column_letter(c_i)
            cx = ws6.cell(row=f_xj, column=c_i, value=f"=SUM({col_l}{f_ini_x}:{col_l}{f_fin_x})")
            cx.font = font_bold
            cx.fill = fill_gris_total
            cx.number_format = "#,##0.00"
            cx.border = borde_total
        fila_cur_6 += 1

        # Fila 3 al pie: Multiplicador Básico Mj = Vj / Xj con fórmula activa
        f_mj = fila_cur_6
        c_mj_lbl = ws6.cell(row=f_mj, column=1, value=f"Mj (Multiplicador Básico = Vj / Xj — {etq_anio})")
        c_mj_lbl.font = font_bold
        c_mj_lbl.fill = fill_amarillo_ref
        c_mj_lbl.border = borde_total
        for c_i in range(2, n_comunas + 3):
            col_l = get_column_letter(c_i)
            cm = ws6.cell(row=f_mj, column=c_i, value=f"=IF({col_l}{f_xj}>0,{col_l}{f_vj}/{col_l}{f_xj},0)")
            cm.font = font_bold
            cm.fill = fill_amarillo_ref
            cm.number_format = "0.0000"
            cm.border = borde_total

        fila_cur_6 += 3

    ws6.freeze_panes = "B6"
    _autoajustar_columnas_hoja(ws6)

    # ==========================================================================
    # HOJA 7: CUADRANTES DE SILVA LIRA (FÓRMULAS + COLORES + MATRIZ 2x2 + GRÁFICO)
    # ==========================================================================
    ws7 = wb.create_sheet("07_Cuadrantes_Silva")
    ws7.merge_cells("A1:M1")
    c7_t = ws7.cell(
        row=1,
        column=1,
        value=f"CLASIFICACIÓN TERRITORIAL EN CUADRANTES DE SILVA LIRA (CEPAL, 2005) — {region_sel.upper()} ({anio_0}–{anio_t})",
    )
    c7_t.fill = fill_titulo
    c7_t.font = font_titulo
    ws7.row_dimensions[1].height = 26

    ws7.merge_cells("A2:M2")
    c7_s = ws7.cell(
        row=2,
        column=1,
        value="Incluye fórmulas vivas de tasa anualizada =((Ct/C0)^(1/T))-1, fila de referencia regional, Matriz Visual 2x2 de Silva Lira y Gráfico de Dispersión nativo",
    )
    c7_s.font = font_sub

    T_per = max(int(anio_t) - int(anio_0), 1)
    df_ss = resultados["df_shift_share"]

    headers_silva = [
        "Comuna",
        f"Nivel {anio_0} (V0)",
        f"Nivel {anio_t} (Vt)",
        "Variación Absoluta",
        f"Crecimiento Acumulado {anio_0}-{anio_t} (%)",
        f"Tasa Promedio Anualizada (T={T_per} años)",
        f"Participación Regional {anio_0} (%)",
        "Cuadrante de Silva Lira (CEPAL, 2005)",
    ]
    fila_hdr_7 = 4
    for c_i, h_txt in enumerate(headers_silva, start=1):
        ch = ws7.cell(row=fila_hdr_7, column=c_i, value=h_txt)
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ch.border = borde_fino
    ws7.row_dimensions[fila_hdr_7].height = 26

    fila_ini_7 = 5
    fila_tot_7 = fila_ini_7 + len(df_ss)

    for idx_r, row_s in enumerate(df_ss.itertuples(index=False), start=fila_ini_7):
        cuad_str = str(row_s.Cuadrante_Silva_Lira)
        if cuad_str.startswith("I."):
            fill_row = fill_cuad_1
        elif cuad_str.startswith("II."):
            fill_row = fill_cuad_2
        elif cuad_str.startswith("III."):
            fill_row = fill_cuad_3
        else:
            fill_row = fill_cuad_4

        v0_val = float(getattr(row_s, f"Nivel_{anio_0}"))
        vt_val = float(getattr(row_s, f"Nivel_{anio_t}"))

        c_com = ws7.cell(row=idx_r, column=1, value=row_s.Comuna)
        c_v0 = ws7.cell(row=idx_r, column=2, value=v0_val)
        c_vt = ws7.cell(row=idx_r, column=3, value=vt_val)
        c_dif = ws7.cell(row=idx_r, column=4, value=f"=C{idx_r}-B{idx_r}")
        c_var = ws7.cell(row=idx_r, column=5, value=f"=IF(B{idx_r}>0,(C{idx_r}-B{idx_r})/B{idx_r},0)")
        c_ tpa = ws7.cell(row=idx_r, column=6, value=f"=IF(B{idx_r}>0,((C{idx_r}/B{idx_r})^(1/{T_per}))-1,0)")
        c_par = ws7.cell(row=idx_r, column=7, value=f"=IF($B${fila_tot_7}>0,B{idx_r}/$B${fila_tot_7},0)")
        c_cua = ws7.cell(row=idx_r, column=8, value=cuad_str)

        c_v0.number_format = "#,##0.00"
        c_vt.number_format = "#,##0.00"
        c_dif.number_format = "#,##0.00"
        c_var.number_format = "0.00%"
        c_tpa.number_format = "0.00%"
        c_par.number_format = "0.00%"

        for cell_item in (c_com, c_v0, c_vt, c_dif, c_var, c_tpa, c_par, c_cua):
            cell_item.fill = fill_row
            cell_item.font = font_celda
            cell_item.border = borde_fino

    # Fila de Referencia Regional (Suma Total y Promedios Umbrales)
    ws7.cell(row=fila_tot_7, column=1, value="SUMA TOTAL / UMBRAL REGIONAL").font = font_bold
    ws7.cell(row=fila_tot_7, column=2, value=f"=SUM(B{fila_ini_7}:B{fila_tot_7-1})").number_format = "#,##0.00"
    ws7.cell(row=fila_tot_7, column=3, value=f"=SUM(C{fila_ini_7}:C{fila_tot_7-1})").number_format = "#,##0.00"
    ws7.cell(row=fila_tot_7, column=4, value=f"=C{fila_tot_7}-B{fila_tot_7}").number_format = "#,##0.00"
    ws7.cell(row=fila_tot_7, column=5, value=f"=IF(B{fila_tot_7}>0,(C{fila_tot_7}-B{fila_tot_7})/B{fila_tot_7},0)").number_format = "0.00%"
    ws7.cell(row=fila_tot_7, column=6, value=f"=IF(B{fila_tot_7}>0,((C{fila_tot_7}/B{fila_tot_7})^(1/{T_per}))-1,0)").number_format = "0.00%"
    ws7.cell(row=fila_tot_7, column=7, value=f"=AVERAGE(G{fila_ini_7}:G{fila_tot_7-1})").number_format = "0.00%"
    ws7.cell(row=fila_tot_7, column=8, value="Corte de Ejes X e Y (Media Regional)")

    for c_i in range(1, 9):
        cell_tot = ws7.cell(row=fila_tot_7, column=c_i)
        cell_tot.fill = fill_amarillo_ref
        cell_tot.font = font_bold
        cell_tot.border = borde_total

    # --------------------------------------------------------------------------
    # MATRIZ VISUAL 2x2 DE CUADRANTES DE SILVA LIRA EN COLUMNAS J:M
    # --------------------------------------------------------------------------
    com_q1 = sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("I.")]["Comuna"].tolist())
    com_q2 = sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("II.")]["Comuna"].tolist())
    com_q3 = sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("III.")]["Comuna"].tolist())
    com_q4 = sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("IV.")]["Comuna"].tolist())

    ws7.merge_cells("J4:M4")
    c_m2_tit = ws7.cell(row=4, column=10, value="MATRIZ VISUAL 2×2 DE CUADRANTES DE SILVA LIRA (CEPAL, 2005)")
    c_m2_tit.fill = fill_titulo
    c_m2_tit.font = font_header
    c_m2_tit.alignment = Alignment(horizontal="center", vertical="center")

    ws7.cell(row=5, column=10, value="Eje Crecimiento (Y) \\ Eje Peso Inicial (X)").fill = fill_header
    ws7.cell(row=5, column=10).font = font_header
    ws7.cell(row=5, column=10).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws7.merge_cells("K5:L5")
    c_x_bajo = ws7.cell(row=5, column=11, value="BAJO PESO INICIAL (< Media Comunal)")
    c_x_bajo.fill = fill_header
    c_x_bajo.font = font_header
    c_x_bajo.alignment = Alignment(horizontal="center", vertical="center")

    c_x_alto = ws7.cell(row=5, column=13, value="ALTO PESO INICIAL (>= Media Comunal)")
    c_x_alto.fill = fill_header
    c_x_alto.font = font_header
    c_x_alto.alignment = Alignment(horizontal="center", vertical="center")

    # Fila Superior del 2x2: Alto Crecimiento (Cuadrante II a la izquierda, Cuadrante I a la derecha)
    ws7.merge_cells("J6:J10")
    c_y_alto = ws7.cell(
        row=6,
        column=10,
        value=f"ALTO DINAMISMO\nCrecimiento >= Media Regional ({tot['tasa_var_reg']:.1f}%)",
    )
    c_y_alto.fill = fill_subbloque
    c_y_alto.font = font_bold
    c_y_alto.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws7.merge_cells("K6:L10")
    txt_q2 = (
        f"CUADRANTE II: EMERGENTES / CONVERGENTES ({len(com_q2)} comunas)\n"
        f"(Bajo Peso Inicial + Alto Crecimiento)\n\n"
        + (", ".join(com_q2) if com_q2 else "Sin comunas en este cuadrante")
    )
    c_box_q2 = ws7.cell(row=6, column=11, value=txt_q2)
    c_box_q2.fill = fill_cuad_2
    c_box_q2.font = font_celda
    c_box_q2.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    ws7.merge_cells("M6:M10")
    txt_q1 = (
        f"CUADRANTE I: DINÁMICAS / GANADORAS ({len(com_q1)} comunas)\n"
        f"(Alto Peso Inicial + Alto Crecimiento)\n\n"
        + (", ".join(com_q1) if com_q1 else "Sin comunas en este cuadrante")
    )
    c_box_q1 = ws7.cell(row=6, column=13, value=txt_q1)
    c_box_q1.fill = fill_cuad_1
    c_box_q1.font = font_celda
    c_box_q1.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    # Fila Inferior del 2x2: Bajo Crecimiento (Cuadrante IV a la izquierda, Cuadrante III a la derecha)
    ws7.merge_cells("J11:J15")
    c_y_bajo = ws7.cell(
        row=11,
        column=10,
        value=f"BAJO DINAMISMO\nCrecimiento < Media Regional ({tot['tasa_var_reg']:.1f}%)",
    )
    c_y_bajo.fill = fill_subbloque
    c_y_bajo.font = font_bold
    c_y_bajo.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws7.merge_cells("K11:L15")
    txt_q4 = (
        f"CUADRANTE IV: EN RETROCESO / REZAGADAS ({len(com_q4)} comunas)\n"
        f"(Bajo Peso Inicial + Bajo Crecimiento)\n\n"
        + (", ".join(com_q4) if com_q4 else "Sin comunas en este cuadrante")
    )
    c_box_q4 = ws7.cell(row=11, column=11, value=txt_q4)
    c_box_q4.fill = fill_cuad_4
    c_box_q4.font = font_celda
    c_box_q4.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    ws7.merge_cells("M11:M15")
    txt_q3 = (
        f"CUADRANTE III: ESTANCADAS / MADURAS ({len(com_q3)} comunas)\n"
        f"(Alto Peso Inicial + Bajo Crecimiento)\n\n"
        + (", ".join(com_q3) if com_q3 else "Sin comunas en este cuadrante")
    )
    c_box_q3 = ws7.cell(row=11, column=13, value=txt_q3)
    c_box_q3.font = font_celda
    c_box_q3.fill = fill_cuad_3
    c_box_q3.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    for r_box in range(4, 16):
        ws7.row_dimensions[r_box].height = 24
        for c_box in range(10, 14):
            ws7.cell(row=r_box, column=c_box).border = borde_fino

    # --------------------------------------------------------------------------
    # GRÁFICO DE DISPERSIÓN (ScatterChart) NATIVO DE EXCEL INCRUSTADO EN J17
    # --------------------------------------------------------------------------
    chart_silva = ScatterChart()
    chart_silva.title = f"Cuadrantes de Silva Lira ({region_sel}, {anio_0}-{anio_t})"
    chart_silva.style = 13
    chart_silva.x_axis.title = f"Participación Comunal Inicial {anio_0} (%)"
    chart_silva.y_axis.title = f"Tasa Promedio Anualizada {anio_0}-{anio_t} (%)"
    chart_silva.width = 22
    chart_silva.height = 14

    xvalues = Reference(ws7, min_col=7, min_row=fila_ini_7, max_row=fila_tot_7 - 1)
    yvalues = Reference(ws7, min_col=6, min_row=fila_ini_7, max_row=fila_tot_7 - 1)
    serie_comunas = Series(yvalues, xvalues, title="Comunas")
    serie_comunas.marker.symbol = "circle"
    serie_comunas.marker.size = 8
    serie_comunas.graphicalProperties.line.noFill = True
    chart_silva.series.append(serie_comunas)

    ws7.add_chart(chart_silva, "J17")
    ws7.freeze_panes = "B5"
    _autoajustar_columnas_hoja(ws7)
    ws7.column_dimensions["J"].width = 24
    ws7.column_dimensions["K"].width = 22
    ws7.column_dimensions["L"].width = 22
    ws7.column_dimensions["M"].width = 38

    # ==========================================================================
    # HOJA 8: SHIFT & SHARE MADE CLÁSICO
    # ==========================================================================
    cols_made_clasico = [
        "Comuna",
        f"Nivel_{anio_0}",
        f"Nivel_{anio_t}",
        "Efecto_Global_EG",
        "Efecto_Total_ET",
        "Efecto_Estructural_EE",
        "Efecto_Diferencial_ED",
        "Tipologia_Shift_Share",
    ]
    ws8 = wb.create_sheet("08_ShiftShare_Clasico")
    _estilizar_hoja_excel(
        ws8,
        "DESCOMPOSICIÓN SHIFT & SHARE - MADE CLÁSICO (ET = EE + ED)",
        sub_general,
        resultados["df_shift_share"][cols_made_clasico],
    )

    # ==========================================================================
    # HOJA 9: SHIFT & SHARE MADE MODIFICADO
    # ==========================================================================
    cols_made_mod = [
        "Comuna",
        "Efecto_Total_ET",
        "Efecto_Estructural_EE",
        "Efecto_Inverso_EI",
        "Efecto_Estructural_Mod_EM",
        "Efecto_Regional_Mod_ERM",
        "Cuadrante_Silva_Lira",
    ]
    ws9 = wb.create_sheet("09_MADE_Modificado")
    _estilizar_hoja_excel(
        ws9,
        "DESCOMPOSICIÓN SHIFT & SHARE - MADE MODIFICADO (EI, EM Y ERM)",
        sub_general,
        resultados["df_shift_share"][cols_made_mod],
    )

    # ==========================================================================
    # HOJA 10: CONVERGENCIA Y CONCENTRACIÓN REAT
    # ==========================================================================
    ws10 = wb.create_sheet("10_Convergencia_REAT")
    _estilizar_hoja_excel(
        ws10,
        f"DISPARIDADES, CONCENTRACIÓN Y CONVERGENCIA REGIONAL (MOTOR REAT - ALPHA={alpha_hk})",
        sub_general,
        resultados["df_reat_resumen"],
    )

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def renderizar_exportador_sii(ruta_excel_default: str = ARCHIVO_DEFAULT_REPO):
    """
    Interfaz interactiva en Streamlit para explorar la base del SII, ejecutar
    el motor econométrico completo y descargar el libro Excel de 10 hojas.
    """
    st.subheader("Motor Automatizado SII — Análisis Regional ILPES, MADE y REAT")
    st.markdown(
        "Procesamiento directo de microdatos estadísticos del **Servicio de Impuestos Internos (SII)** "
        "para construcción de matrices comunales-sectoriales, especialización, base exportadora, "
        "Shift & Share (MADE Clásico y Modificado) y convergencia REAT."
    )

    col_fuente1, col_fuente2 = st.columns([2, 1])
    with col_fuente1:
        archivo_subido = st.file_uploader(
            "Cargar archivo Excel del SII personalizado (.xlsx) o usar base oficial del repositorio:",
            type=["xlsx", "xls"],
            key="uploader_sii_exportador",
        )
    with col_fuente2:
        existe_local = os.path.exists(ruta_excel_default)
        if archivo_subido is not None:
            st.success("Usando archivo cargado por el usuario.")
            fuente_activa = archivo_subido
        elif existe_local:
            st.info(f"Base activa en repositorio: `{ruta_excel_default}`")
            fuente_activa = ruta_excel_default
        else:
            st.warning(f"No se detectó `{ruta_excel_default}` en el directorio actual.")
            fuente_activa = None

    if fuente_activa is None:
        st.stop()

    try:
        df_sii, meta = cargar_base_nacional_sii(fuente_activa)
    except Exception as exc:
        st.error(f"Error al leer la base de datos del SII: {exc}")
        return

    col_anio = meta["col_anio"]
    col_region = meta["col_region"]
    columnas_metricas = meta["columnas_metricas"]

    if not col_anio or not meta["col_comuna"] or not meta["col_rubro"]:
        st.error(
            "La hoja de datos seleccionada no contiene las columnas requeridas "
            "(Año Comercial, Comuna, Rubro económico)."
        )
        return

    anios_disp = sorted(df_sii[col_anio].dropna().unique().tolist())
    if col_region:
        regiones_disp = sorted(df_sii[col_region].dropna().astype(str).str.strip().unique().tolist())
    else:
        regiones_disp = ["Todas (Consolidado)"]

    # Selección por defecto: Región del Biobío y año inicial 2014 (si existe en la base)
    idx_reg_default = 0
    for i, r in enumerate(regiones_disp):
        if "biob" in _normalizar_texto(r):
            idx_reg_default = i
            break

    idx_anio_0_default = anios_disp.index(2014) if 2014 in anios_disp else 0

    c1, c2, c3, c4, c5 = st.columns([2.2, 2.2, 1.1, 1.1, 1.2])
    with c1:
        region_sel = st.selectbox("Región de estudio:", regiones_disp, index=idx_reg_default)
    with c2:
        variable_sel = st.selectbox("Variable económica SII:", columnas_metricas, index=0)
    with c3:
        anio_0 = st.selectbox("Año inicial (t0):", anios_disp, index=idx_anio_0_default)
    with c4:
        anio_t = st.selectbox("Año final (tf):", anios_disp, index=len(anios_disp) - 1)
    with c5:
        alpha_hk = st.number_input(
            "Parámetro α (Hannah-Kay):",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.5,
        )

    if int(anio_0) >= int(anio_t):
        st.warning("Selecciona un año final (tf) estrictamente posterior al año inicial (t0).")
        return

    V0, Vt = construir_matrices_region(df_sii, meta, region_sel, anio_0, anio_t, variable_sel)
    if V0.empty or Vt.empty:
        st.warning("No se encontraron registros activos para la combinación de región y años seleccionada.")
        return

    resultados = calcular_todo_el_ramo(V0, Vt, anio_0, anio_t, alpha_hk=alpha_hk)
    tot = resultados["totales"]
    mb = resultados["metricas_beta"]

    # KPIs Superiores
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Comunas / Rubros", f"{tot['n_comunas']} / {tot['n_rubros']}")
    k2.metric(f"Total Regional {anio_0}", f"{tot['total_reg_0']:,.1f}")
    k3.metric(
        f"Total Regional {anio_t}",
        f"{tot['total_reg_t']:,.1f}",
        f"{tot['tasa_var_reg']:+.2f}%",
    )
    k4.metric(
        "Pendiente Beta (OLS)",
        f"{mb['beta']:.4f}",
        "Convergencia" if mb["beta"] < 0 else "Divergencia",
    )
    k5.metric("Ajuste R² / p-valor", f"{mb['r2']:.3f} (p={mb['p_value']:.3f})")

    # Botón de descarga del libro Excel de 10 hojas mejorado
    bytes_excel = compilar_excel_10_hojas(
        resultados=resultados,
        region_sel=region_sel,
        variable_sel=variable_sel,
        anio_0=anio_0,
        anio_t=anio_t,
        alpha_hk=alpha_hk,
    )
    nombre_archivo_salida = (
        f"Reporte_Territorial_SII_{_normalizar_texto(region_sel).replace(' ', '_')}_{anio_0}_{anio_t}.xlsx"
    )
    st.download_button(
        label="Descargar Libro Maestro Excel (10 Hojas con Formato Condicional, Fórmulas Vivas y Cuadrante de Silva Lira)",
        data=bytes_excel,
        file_name=nombre_archivo_salida,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    tabs = st.tabs([
        "1. Matrices y Localización (Qij)",
        "2. Especialización y Base Exportable",
        "3. Shift & Share (MADE Clásico y Mod.)",
        "4. Cuadrantes de Silva Lira",
        "5. Convergencia y Desigualdad (REAT)",
    ])

    with tabs[0]:
        st.markdown(f"**Matriz de Cociente de Localización ($Q_{{ij}}$) — Año {anio_t} (Resaltado > 1)**")
        fig_q = px.imshow(
            resultados["Q_ij_t"],
            aspect="auto",
            color_continuous_scale="RdBu_r",
            origin="upper",
            labels={"x": "Comuna", "y": "Rubro Económico SII", "color": "Q_ij"},
        )
        fig_q.update_layout(height=520, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_q, use_container_width=True)

        st.dataframe(
            resultados["Q_ij_t"].style.format("{:.4f}").map(
                lambda v: "background-color: #FFC7CE; color: #9C0006; font-weight: bold;"
                if isinstance(v, (int, float, np.number)) and v > 1.0
                else ""
            ),
            use_container_width=True,
        )

    with tabs[1]:
        st.markdown(
            "**Coeficientes de Especialización ($Q_r$), Reestructuración ($CR_r$) "
            "y Multiplicador de Base Económica ($M_j$)**"
        )
        st.dataframe(resultados["df_especializacion"].round(4), use_container_width=True, hide_index=True)

        fig_esp = px.bar(
            resultados["df_especializacion"].sort_values(f"Qr_Especializacion_{anio_t}", ascending=False),
            x="Comuna",
            y=[f"Qr_Especializacion_{anio_0}", f"Qr_Especializacion_{anio_t}", "CRr_Reestructuracion"],
            barmode="group",
            title=f"Evolución de Especialización (Qr) y Reestructuración (CRr) ({anio_0}-{anio_t})",
        )
        st.plotly_chart(fig_esp, use_container_width=True)

    with tabs[2]:
        st.markdown("**Descomposición Shift & Share: MADE Clásico ($ET, EE, ED$) y Modificado ($EI, EM, ERM$)**")
        st.dataframe(resultados["df_shift_share"].round(2), use_container_width=True, hide_index=True)

        fig_ss = px.bar(
            resultados["df_shift_share"].sort_values("Efecto_Total_ET", ascending=False),
            x="Comuna",
            y=["Efecto_Estructural_EE", "Efecto_Diferencial_ED", "Efecto_Inverso_EI"],
            barmode="relative",
            title="Descomposición Sectorial y Competitiva por Comuna",
        )
        st.plotly_chart(fig_ss, use_container_width=True)

    with tabs[3]:
        df_ss = resultados["df_shift_share"].copy()
        part_inicial = (df_ss[f"Nivel_{anio_0}"] / max(tot["total_reg_0"], 1e-9)) * 100.0
        part_media = 100.0 / max(tot["n_comunas"], 1)
        df_ss["Participacion_Inicial_%"] = part_inicial

        fig_silva = px.scatter(
            df_ss,
            x="Participacion_Inicial_%",
            y="Var_Porcentual_%",
            color="Cuadrante_Silva_Lira",
            hover_name="Comuna",
            text="Comuna",
            size=np.maximum(df_ss[f"Nivel_{anio_t}"], 1.0),
            labels={
                "Participacion_Inicial_%": f"Participación Comunal Inicial {anio_0} (%)",
                "Var_Porcentual_%": f"Variación Porcentual {anio_0}-{anio_t} (%)",
            },
            title=f"Tipología Territorial en Cuadrantes de Silva Lira (CEPAL, 2005 — {anio_0}–{anio_t})",
        )
        fig_silva.update_traces(textposition="top center")
        fig_silva.add_hline(
            y=tot["tasa_var_reg"],
            line_dash="dash",
            line_color="red",
            annotation_text=f"Crecimiento Regional ({tot['tasa_var_reg']:.1f}%)",
        )
        fig_silva.add_vline(
            x=part_media,
            line_dash="dash",
            line_color="navy",
            annotation_text=f"Participación Media ({part_media:.2f}%)",
        )
        st.plotly_chart(fig_silva, use_container_width=True)

        # Matriz Visual 2x2 en Streamlit
        c_q1 = ", ".join(sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("I.")]["Comuna"].tolist())) or "Ninguna"
        c_q2 = ", ".join(sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("II.")]["Comuna"].tolist())) or "Ninguna"
        c_q3 = ", ".join(sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("III.")]["Comuna"].tolist())) or "Ninguna"
        c_q4 = ", ".join(sorted(df_ss[df_ss["Cuadrante_Silva_Lira"].str.startswith("IV.")]["Comuna"].tolist())) or "Ninguna"

        st.markdown("**Matriz 2×2 de Clasificación Comunal de Silva Lira**")
        df_mat_2x2 = pd.DataFrame({
            "Dinámica de Crecimiento \\ Peso Inicial": [
                f"Crecimiento >= Media Regional ({tot['tasa_var_reg']:.1f}%)",
                f"Crecimiento < Media Regional ({tot['tasa_var_reg']:.1f}%)",
            ],
            f"Bajo Peso Inicial (< {part_media:.2f}%)": [
                f"II. Emergentes / Convergentes: {c_q2}",
                f"IV. En Retroceso / Rezagadas: {c_q4}",
            ],
            f"Alto Peso Inicial (>= {part_media:.2f}%)": [
                f"I. Dinámicas / Ganadoras: {c_q1}",
                f"III. Estancadas / Maduras: {c_q3}",
            ],
        })
        st.dataframe(df_mat_2x2, use_container_width=True, hide_index=True)

    with tabs[4]:
        st.markdown("**Indicadores de Disparidad, Concentración y Convergencia (Motor REAT)**")
        st.dataframe(resultados["df_reat_resumen"].round(4), use_container_width=True, hide_index=True)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            df_b = resultados["df_beta_comunas"]
            fig_beta = px.scatter(
                df_b,
                x=f"ln_Y_{anio_0}",
                y="Tasa_Crec_Anual_Log",
                hover_name="Comuna",
                title=f"Convergencia Beta Absoluta ({anio_0}-{anio_t}): β = {mb['beta']:.4f}",
                labels={
                    f"ln_Y_{anio_0}": f"Logaritmo Nivel Inicial ln(Y_{anio_0})",
                    "Tasa_Crec_Anual_Log": "Tasa Anual Media de Crecimiento Logarítmico",
                },
            )
            df_b_ord = df_b.sort_values(f"ln_Y_{anio_0}")
            fig_beta.add_trace(
                go.Scatter(
                    x=df_b_ord[f"ln_Y_{anio_0}"],
                    y=df_b_ord["Prediccion_OLS"],
                    mode="lines",
                    name="Ajuste OLS",
                )
            )
            st.plotly_chart(fig_beta, use_container_width=True)

        with col_g2:
            fig_lorenz = go.Figure()
            fig_lorenz.add_trace(
                go.Scatter(
                    x=[0, 1],
                    y=[0, 1],
                    mode="lines",
                    line=dict(dash="dash", color="gray"),
                    name="Equidad Perfecta",
                )
            )
            fig_lorenz.add_trace(
                go.Scatter(
                    x=mb["lorenz_p_0"],
                    y=mb["lorenz_l_0"],
                    mode="lines+markers",
                    name=f"Lorenz {anio_0}",
                )
            )
            fig_lorenz.add_trace(
                go.Scatter(
                    x=mb["lorenz_p_t"],
                    y=mb["lorenz_l_t"],
                    mode="lines+markers",
                    name=f"Lorenz {anio_t}",
                )
            )
            fig_lorenz.update_layout(
                title=f"Curva de Lorenz Comunal ({anio_0} vs {anio_t})",
                xaxis_title="Proporción Acumulada de Comunas",
                yaxis_title=f"Proporción Acumulada de {variable_sel}",
            )
            st.plotly_chart(fig_lorenz, use_container_width=True)


# Alias de compatibilidad para importación desde app.py
renderizar_modulo_exportador_sii = renderizar_exportador_sii
mostrar_exportador_sii = renderizar_exportador_sii
