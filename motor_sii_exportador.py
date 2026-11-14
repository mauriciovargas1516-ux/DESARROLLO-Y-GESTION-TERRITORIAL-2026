# -*- coding: utf-8 -*-
"""
MOTOR ECONOMÉTRICO Y EXPORTADOR SII - ILPES / MADE / REAT
Asignatura: Desarrollo y Gestión Territorial - Universidad de Los Lagos
Archivo: motor_sii_exportador.py (PARTE 1 DE 2)
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
from openpyxl.chart.label import DataLabelList
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
    Ejecuta todos los cálculos de Análisis Regional (ILPES / CEPAL Manual 59),
    Base Económica Exportadora, Shift & Share (MADE Clásico y Modificado exacto al Excel ILPES)
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

    # 4. Descomposición Shift & Share (Ecuaciones Exactas ILPES Manual 59 / hojas MADE y Made Modificado)
    r_reg = (total_reg_t / max(total_reg_0, eps)) if total_reg_0 > 0 else 1.0
    r_i_sec = (total_rubro_t / total_rubro_0.replace(0, np.nan)).fillna(1.0)

    # Efecto Total ILPES: ET_j = V_tj - V_0j * r_SR (idéntico a fila 2 de hoja MADE)
    ET_j = total_comuna_t - (total_comuna_0 * r_reg)
    EG_j = total_comuna_0 * (r_reg - 1.0)

    # Matriz Rubro x Comuna de Efecto Estructural: EE_ij = V_0ij * (r_Si - r_SR)
    EE_mat = V0.multiply(r_i_sec - r_reg, axis=0)
    EE_j = EE_mat.sum(axis=0)

    # Matriz Rubro x Comuna de Efecto Diferencial: ED_ij = V_tij - V_0ij * r_Si
    ED_mat = Vt - V0.multiply(r_i_sec, axis=0)
    ED_j = ED_mat.sum(axis=0)

    # Matriz Rubro x Comuna de Efecto Inverso (Made Modificado): EI_ij = V_tij * (1/r_SR - 1/r_Si)
    inv_r_reg = (total_reg_0 / max(total_reg_t, eps)) if total_reg_t > 0 else 1.0
    inv_r_i_sec = (total_rubro_0 / total_rubro_t.replace(0, np.nan)).fillna(1.0)
    EI_mat = Vt.multiply(inv_r_reg - inv_r_i_sec, axis=0)
    EI_j = EI_mat.sum(axis=0)

    # Efecto Modificado (EM_j = EI_j - EE_j) y Efecto Comunal Modificado (ERM_j = ET_j - EI_j)
    EM_j = EI_j - EE_j
    ERM_j = ET_j - EI_j

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
        "ED_mat": ED_mat,
        "EE_mat": EE_mat,
        "EI_mat": EI_mat,
        "df_especializacion": df_especializacion,
        "df_shift_share": df_shift_share,
        "df_reat_resumen": df_reat_resumen,
        "df_beta_comunas": df_beta_comunas,
        "metricas_beta": metricas_beta,
        "totales": {
            "total_reg_0": total_reg_0,
            "total_reg_t": total_reg_t,
            "tasa_var_reg": tasa_var_reg,
            "r_reg": r_reg,
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
