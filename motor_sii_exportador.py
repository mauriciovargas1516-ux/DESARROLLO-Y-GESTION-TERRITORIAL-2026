# -*- coding: utf-8 -*-
"""
Procesamiento de datos SII, indicadores regionales y exportacion a Excel.
Asignatura: Desarrollo y Gestion Territorial - Universidad de Los Lagos.
"""

import io
import re
import os
import unicodedata
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference, ScatterChart, Series
from openpyxl.chart.label import DataLabelList
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


ARCHIVO_DEFAULT_REPO = "ILPES GRUPO 10 29-10-2026.xlsx"
ARCHIVO_CENSO_2017_REPO = "1_1_poblacion.xls"


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


def _parsear_celda_sii(val) -> float:
    """
    Convierte una celda individual de la base SII a float sin destruir decimales.
    Preserva intactos los int/float nativos de Excel (que aparecen en columnas
    dtype=object cuando conviven con asteriscos '*' de secreto tributario).
    """
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return 0.0
    if isinstance(val, (int, float, np.number)) and not isinstance(val, bool):
        return float(val) if np.isfinite(val) else 0.0

    s = str(val).strip()
    if not s or s in {"*", "-", "--", "nan", "None", "N/A", "S/I"}:
        return 0.0

    s = s.replace(" ", "").replace("$", "")

    if re.fullmatch(r"[+-]?\d+(\.\d+)?[eE][+-]?\d+", s):
        return float(s)

    if "." in s and "," in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        if s.count(",") == 1:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "." in s:
        partes = s.split(".")
        if len(partes) > 2:
            s = s.replace(".", "")
        else:
            izq, der = partes[0].lstrip("+-"), partes[1]
            if len(der) == 3 and 1 <= len(izq) <= 3 and izq != "0":
                s = s.replace(".", "")

    try:
        v = float(s)
        return v if np.isfinite(v) else 0.0
    except ValueError:
        return 0.0


def _a_numero_sii(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie):
        return pd.to_numeric(serie, errors="coerce").fillna(0.0)
    return serie.map(_parsear_celda_sii).astype(float)


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

    if col_anio:
        df[col_anio] = pd.to_numeric(df[col_anio], errors="coerce")
        df = df.dropna(subset=[col_anio]).copy()
        df[col_anio] = df[col_anio].astype(int)

    for m in columnas_metricas:
        df[m] = _a_numero_sii(df[m])

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

    ET_j = total_comuna_t - (total_comuna_0 * r_reg)
    EG_j = total_comuna_0 * (r_reg - 1.0)

    EE_mat = V0.multiply(r_i_sec - r_reg, axis=0)
    EE_j = EE_mat.sum(axis=0)

    ED_mat = Vt - V0.multiply(r_i_sec, axis=0)
    ED_j = ED_mat.sum(axis=0)

    inv_r_reg = (total_reg_0 / max(total_reg_t, eps)) if total_reg_t > 0 else 1.0
    inv_r_i_sec = (total_rubro_0 / total_rubro_t.replace(0, np.nan)).fillna(1.0)
    EI_mat = Vt.multiply(inv_r_reg - inv_r_i_sec, axis=0)
    EI_j = EI_mat.sum(axis=0)

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



# Poblacion comunal Censo 2024 INE (Biobio, Los Lagos, Los Rios y La Araucania)
_POBLACION_CENSO_2024_RAW = {
    # Region del Biobio (33 comunas, total: 1.613.059)
    "Alto Biobío": 6016, "Antuco": 4373, "Arauco": 37163, "Cabrero": 31256,
    "Cañete": 34640, "Chiguayante": 85822, "Concepción": 230375, "Contulmo": 5905,
    "Coronel": 123648, "Curanilahue": 31119, "Florida": 12958, "Hualpén": 87731,
    "Hualqui": 25795, "Laja": 23706, "Lebu": 25246, "Los Álamos": 21950,
    "Los Ángeles": 219441, "Lota": 39980, "Mulchén": 29036, "Nacimiento": 26140,
    "Negrete": 10723, "Penco": 48971, "Quilaco": 4440, "Quilleco": 9700,
    "San Pedro de la Paz": 150992, "San Rosendo": 3575, "Santa Bárbara": 14075,
    "Santa Juana": 14947, "Talcahuano": 147322, "Tirúa": 10208, "Tomé": 56907,
    "Tucapel": 15729, "Yumbel": 23170,
    # Región de Los Lagos (30 comunas)
    "Puerto Montt": 275473, "Osorno": 174998, "Puerto Varas": 50010, "Castro": 48632,
    "Ancud": 42158, "Calbuco": 37620, "Quellón": 30910, "Purranque": 21475,
    "Frutillar": 21220, "Llanquihue": 19380, "Los Muermos": 17950, "Maullín": 15110,
    "Río Negro": 14560, "Dalcahue": 15240, "Chonchi": 16120, "Fresia": 12810,
    "Puyehue": 12390, "San Pablo": 10540, "Puerto Octay": 9450, "Quinchao": 8420,
    "Quemchi": 8790, "San Juan de la Costa": 7890, "Hualaihué": 9680, "Queilén": 5610,
    "Chaitén": 5420, "Cochamó": 4180, "Puqueldón": 4350, "Curaco de Vélez": 4080,
    "Futaleufú": 2910, "Palena": 1890,
    # Región de Los Ríos (12 comunas)
    "Valdivia": 181240, "La Unión": 39850, "Panguipulli": 36410, "Río Bueno": 32680,
    "Mariquina": 22840, "Paillaco": 21150, "Los Lagos": 20590, "Lanco": 17890,
    "Futrono": 15520, "Lago Ranco": 10420, "Máfil": 7450, "Corral": 5510,
    # Región de La Araucanía (32 comunas)
    "Temuco": 304820, "Padre Las Casas": 83540, "Villarrica": 63910, "Angol": 56840,
    "Victoria": 36120, "Lautaro": 40890, "Pucón": 34950, "Nueva Imperial": 34620,
    "Carahue": 25680, "Loncoche": 24910, "Collipulli": 25840, "Pitrufquén": 26410,
    "Freire": 25920, "Vilcún": 30480, "Traiguén": 19450, "Curacautín": 18290,
    "Cunco": 18460, "Gorbea": 15180, "Teodoro Schmidt": 15620, "Saavedra": 13010,
    "Purén": 12190, "Galvarino": 12540, "Cholchol": 12380, "Lonquimay": 10890,
    "Renaico": 10740, "Toltén": 10120, "Lumaco": 9890, "Ercilla": 8110,
    "Curarrehue": 8040, "Los Sauces": 7580, "Perquenco": 7320, "Melipeuco": 6650,
}
POBLACION_CENSO_2024 = {_normalizar_texto(k): int(v) for k, v in _POBLACION_CENSO_2024_RAW.items()}


def _obtener_poblacion_comunas(comunas: list):
    """Retorna lista de poblaciones Censo 2024 si todas las comunas están disponibles; si no, None."""
    pobs = []
    for com in comunas:
        val = POBLACION_CENSO_2024.get(_normalizar_texto(com))
        if val is None or val <= 0:
            return None
        pobs.append(int(val))
    return pobs

@st.cache_data(show_spinner=False)
def cargar_poblacion_censo_2017_xls(ruta_xls: str = ARCHIVO_CENSO_2017_REPO) -> dict:
    """
    Lee directamente la pestaña 'Comuna' del archivo oficial INE '1_1_poblacion.xls'
    (Censo 2017, actualizado con Región de Ñuble) sin requerir filtros manuales en Excel.
    Filtra automáticamente 'EDAD == Total Comuna' y retorna un diccionario normalizado
    con las 346 comunas del país. Si el archivo o xlrd no están disponibles, retorna {}.
    """
    if not ruta_xls or not os.path.exists(ruta_xls):
        return {}
    try:
        df_17 = pd.read_excel(ruta_xls, sheet_name="Comuna", header=2)
    except Exception:
        return {}

    col_com = _buscar_columna(df_17.columns, ["NOMBRE COMUNA", "Comuna"])
    col_prov = _buscar_columna(df_17.columns, ["NOMBRE PROVINCIA", "Provincia"])
    col_reg = _buscar_columna(df_17.columns, ["NOMBRE REGIÓN", "NOMBRE REGION", "Región", "Region"])
    col_edad = _buscar_columna(df_17.columns, ["EDAD", "Edad"])
    col_tot = _buscar_columna(
        df_17.columns,
        ["TOTAL POBLACIÓN EFECTIVAMENTE CENSADA", "TOTAL POBLACION EFECTIVAMENTE CENSADA", "Total"],
    )
    if not col_com or not col_edad or not col_tot:
        return {}

    mask_tot = df_17[col_edad].astype(str).apply(_normalizar_texto) == "total comuna"
    df_tot = df_17[mask_tot].copy()
    mapa = {}
    for _, row in df_tot.iterrows():
        com_raw = str(row[col_com]).strip()
        com_key = _normalizar_texto(com_raw)
        if not com_key or com_key == "pais":
            continue
        val_num = pd.to_numeric(row[col_tot], errors="coerce")
        if pd.isna(val_num) or val_num <= 0:
            continue
        prov_nom = str(row[col_prov]).strip().title() if col_prov and pd.notna(row[col_prov]) else ""
        reg_nom = str(row[col_reg]).strip().title() if col_reg and pd.notna(row[col_reg]) else ""
        mapa[com_key] = {
            "comuna": com_raw.title(),
            "provincia": prov_nom,
            "region": reg_nom,
            "pob_2017": int(round(float(val_num))),
        }
    return mapa



def _etiquetas_variable_sii(variable_sel: str, anio_0: int, anio_t: int):
    """Genera etiquetas limpias para encabezados de la hoja Cuadrantes Silva."""
    v_norm = _normalizar_texto(variable_sel)
    if "venta" in v_norm:
        return f"Ventas UF {anio_0}", f"Ventas UF {anio_t}", f"Ventas per cápita {anio_t} UF", "#,##0", "#,##0"
    if "renta" in v_norm:
        return f"Renta UF {anio_0}", f"Renta UF {anio_t}", f"Renta per cápita {anio_t} UF", "#,##0", "#,##0"
    if "trabajador" in v_norm:
        return f"Trabajadores {anio_0}", f"Trabajadores {anio_t}", f"Trabajadores per cápita {anio_t}", "#,##0", "0.000"
    if "empresa" in v_norm:
        return f"Empresas {anio_0}", f"Empresas {anio_t}", f"Empresas per cápita {anio_t}", "#,##0", "0.000"
    base_txt = str(variable_sel).strip()[:20]
    return f"{base_txt} {anio_0}", f"{base_txt} {anio_t}", f"{base_txt} per cápita {anio_t}", "#,##0.00", "0.00"


def _estilizar_hoja_excel(ws, titulo_hoja: str, subtitulo: str, df_tabla: pd.DataFrame):
    """Aplica formato simple de tabla Excel con encabezado gris claro."""
    fill_titulo = PatternFill(fill_type=None)
    fill_header = PatternFill("solid", fgColor="D9D9D9")
    fill_zebra = PatternFill(fill_type=None)

    font_titulo = Font(name="Calibri", size=11, bold=True, color="000000")
    font_sub = Font(name="Calibri", size=10, italic=True, color="333333")
    font_header = Font(name="Calibri", size=10, bold=True, color="000000")
    font_celda = Font(name="Calibri", size=10, color="000000")

    borde_fino = Border(
        left=Side(style="thin", color="BFBFBF"),
        right=Side(style="thin", color="BFBFBF"),
        top=Side(style="thin", color="BFBFBF"),
        bottom=Side(style="thin", color="BFBFBF"),
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

    _autoajustar_columnas_hoja(ws, max_width=58, min_width=13, col_a_max=64)


def _medir_ancho_celda_excel(cell, col_idx: int) -> float:
    """Estima el ancho visual real de una celda en Excel (Calibri 10pt), evitando inflar por decimales crudos."""
    val = cell.value
    if val is None:
        return 0.0

    nf = str(cell.number_format or "")
    es_negrita = bool(cell.font and cell.font.bold)
    mult_bold = 1.07 if es_negrita else 1.0

    if isinstance(val, bool):
        return 7.0

    if isinstance(val, (int, float, np.number)):
        fval = float(val)
        if not np.isfinite(fval):
            return 8.0
        if "%" in nf:
            txt = f"{fval * 100:,.2f}%"
        elif "0.0000" in nf:
            txt = f"{fval:,.4f}"
        elif "0.000" in nf:
            txt = f"{fval:,.3f}"
        elif "0.00" in nf:
            txt = f"{fval:,.2f}"
        elif "0.0" in nf:
            txt = f"{fval:,.1f}"
        elif nf in ("0", "#,##0", "+#,##0;-#,##0;0"):
            txt = f"{fval:,.0f}"
        else:
            txt = f"{fval:,.2f}" if abs(fval) >= 1 else f"{fval:.4f}"
        return len(txt) * mult_bold + 2.5

    s_val = str(val)
    if s_val.startswith("="):
        s_up = s_val.upper()
        if "ALTAMENTE CONCENTRADA" in s_up:
            return 23.0
        if "SUBE" in s_up or "BAJA" in s_up:
            return 11.0
        if "DINÁMICA" in s_up or "RETROCESO" in s_up or "ESTANCADA" in s_up:
            return 19.0
        if "%" in nf:
            return 10.5
        if "0.0000" in nf:
            return 10.5
        if "0.000" in nf:
            return 9.5
        if "0.00" in nf:
            return 13.5
        if "#,##0" in nf:
            return 12.0
        if nf == "0":
            return 7.5
        return 11.5

    lineas = s_val.splitlines() or [s_val]
    largo_max = max(len(ln) for ln in lineas)
    wrap_activo = bool(cell.alignment and cell.alignment.wrap_text)

    if col_idx > 1 and wrap_activo and largo_max > 20:
        palabras = [p for ln in lineas for p in ln.split()]
        pal_max = max((len(p) for p in palabras), default=12)
        ancho_2_lineas = max(pal_max + 2, (largo_max / 2.0) + 3.0)
        return ancho_2_lineas * mult_bold + 1.5

    return largo_max * mult_bold + 2.8


def _autoajustar_columnas_hoja(ws, max_width: int = 28, min_width: int = 11, col_a_max: int = 96):
    """
    Ajusta automáticamente el ancho de cada columna según su contenido visible real,
    ignorando celdas combinadas (títulos/banners) y evitando cortar nombres largos en la columna A.
    """
    celdas_combinadas_horiz = set()
    for rng in ws.merged_cells.ranges:
        if rng.max_col > rng.min_col:
            for r_m in range(rng.min_row, rng.max_row + 1):
                for c_m in range(rng.min_col, rng.max_col + 1):
                    celdas_combinadas_horiz.add((r_m, c_m))

    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        if ws.column_dimensions[col_letter].hidden:
            continue

        ancho_est = 0.0
        for r_idx in range(1, ws.max_row + 1):
            if (r_idx, col_idx) in celdas_combinadas_horiz:
                continue
            celda = ws.cell(row=r_idx, column=col_idx)
            if celda.value is None:
                continue
            w_c = _medir_ancho_celda_excel(celda, col_idx)
            if w_c > ancho_est:
                ancho_est = w_c

        limite_sup = col_a_max if col_idx == 1 else max_width
        min_col = max(min_width, 16) if col_idx == 1 else min_width
        ws.column_dimensions[col_letter].width = round(max(min(ancho_est, limite_sup), min_col), 1)

    # Asegurar altura cómoda en filas de cabecera con texto ajustado en 2 líneas
    for r_idx in range(1, ws.max_row + 1):
        necesita_alto = False
        for c_idx in range(2, ws.max_column + 1):
            if (r_idx, c_idx) in celdas_combinadas_horiz:
                continue
            celda = ws.cell(row=r_idx, column=c_idx)
            if isinstance(celda.value, str) and not celda.value.startswith("="):
                if celda.alignment and celda.alignment.wrap_text:
                    col_w = ws.column_dimensions[get_column_letter(c_idx)].width or 14
                    if len(celda.value) > col_w - 2:
                        necesita_alto = True
                        break
        if necesita_alto:
            h_act = ws.row_dimensions[r_idx].height or 18
            if h_act < 30:
                ws.row_dimensions[r_idx].height = 30




# Ordenamiento Territorial e Indice Compuesto (Min-Max)

DIMENSIONES_GUTTMAN_OT = [
    "1. Servicios a la producción",
    "2. Infraestructura, transporte y telecomunicaciones",
    "3. Infraestructura de salud y educacional",
    "4. Servicios recreacionales, deportivos y grandes centros comerciales",
]


def _mapear_region_a_control5(region_sel: str):
    """Vincula el nombre de región del SII con las 4 regiones precargadas."""
    r_norm = _normalizar_texto(region_sel)
    if "biob" in r_norm:
        return "Región del Biobío (33 comunas)"
    if "lagos" in r_norm:
        return "Región de Los Lagos (30 comunas)"
    if "rios" in r_norm:
        return "Región de Los Ríos (12 comunas)"
    if "araucan" in r_norm:
        return "Región de La Araucanía (32 comunas)"
    return None


def _matriz_guttman_discriminante_default(dimension: str, comunas_top10: list, region_sel: str = "") -> pd.DataFrame:
    """
    Genera una matriz binaria (1/0) de 8 variables para el Top 10 comunal según las
    4 dimensiones de 'Unidad 5. Ordenamiento Territorial.pdf', asegurando que cada
    variable discrimine entre las comunas (ni puros 1 ni puros 0).
    Para Región del Biobío utiliza un levantamiento verificable por comuna.
    """
    n_c = len(comunas_top10)
    es_biobio = "biob" in _normalizar_texto(region_sel) or (
        len(comunas_top10) >= 2
        and "concepcion" in _normalizar_texto(comunas_top10[0])
        and "angeles" in _normalizar_texto(comunas_top10[1])
    )

    if "1. Servicios a la producción" in dimension:
        cols = [
            "OTEC / Capacitación",
            "Cámara de Comercio local",
            "Banco (más de 1 banco)",
            "Asistencia Técnica (Sercotec / INDAP)",
            "Empresa de reclutamiento laboral",
            "Centro de Negocios Sercotec",
            "Oficina SII (atención empresas)",
            "Oficina Regional CORFO / Gremio Regional",
        ]
        if es_biobio:
            # Concepción, Los Ángeles, San Pedro, Talcahuano, Coronel, Hualpén, Chiguayante, Tomé, Penco, Lota
            mat_10 = [
                [1, 1, 1, 1, 1, 1, 1, 1],  # Concepción (8)
                [1, 1, 1, 1, 1, 1, 1, 1],  # Los Ángeles (8)
                [1, 1, 1, 1, 1, 0, 0, 0],  # San Pedro de la Paz (5)
                [1, 1, 1, 1, 1, 1, 1, 0],  # Talcahuano (7)
                [1, 1, 1, 1, 1, 1, 1, 0],  # Coronel (7)
                [1, 0, 0, 0, 0, 0, 0, 0],  # Hualpén (1)
                [1, 1, 1, 0, 0, 0, 0, 0],  # Chiguayante (3)
                [1, 1, 0, 1, 0, 0, 0, 0],  # Tomé (3)
                [1, 0, 0, 0, 0, 0, 0, 0],  # Penco (1)
                [0, 1, 0, 0, 0, 0, 0, 0],  # Lota (1)
            ]
        else:
            mat_10 = [
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 1, 1, 0, 1, 1, 0],
                [1, 1, 1, 1, 0, 0, 0, 0],
                [1, 1, 0, 1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
            ]
    elif "2. Infraestructura, transporte" in dimension:
        cols = [
            "Terminal de Buses",
            "Periódico / Medio local",
            "Área industrial",
            "Estación de tren / Biotren",
            "Puerto comercial",
            "Señal de TV local",
            "Aeropuerto / Aeródromo comercial",
            "Puerto seco / Centro logístico",
        ]
        if es_biobio:
            mat_10 = [
                [1, 1, 1, 1, 0, 1, 0, 1],  # Concepción (6)
                [1, 1, 1, 0, 0, 1, 1, 1],  # Los Ángeles (6)
                [0, 1, 1, 1, 0, 0, 0, 0],  # San Pedro de la Paz (3)
                [1, 1, 1, 1, 1, 1, 1, 1],  # Talcahuano (8 - Carriel Sur + San Vicente)
                [1, 1, 1, 1, 1, 1, 0, 1],  # Coronel (7)
                [0, 0, 1, 1, 0, 0, 0, 0],  # Hualpén (2)
                [0, 0, 0, 1, 0, 0, 0, 0],  # Chiguayante (1)
                [1, 1, 0, 0, 0, 1, 0, 0],  # Tomé (3)
                [0, 0, 1, 0, 1, 0, 0, 0],  # Penco (2 - Puerto Lirquén)
                [1, 1, 0, 0, 0, 0, 0, 0],  # Lota (2)
            ]
        else:
            mat_10 = [
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 0, 0, 1, 1, 1],
                [1, 1, 1, 1, 1, 0, 0, 1],
                [1, 1, 1, 0, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 0, 0, 0],
                [1, 0, 1, 0, 1, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 1, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
            ]
    elif "3. Infraestructura de salud" in dimension:
        cols = [
            "Educación media técnica",
            "Centro dental",
            "Hospital tipo 2 (mediana / baja comp.)",
            "Clínica privada",
            "CFT",
            "Instituto Profesional (IP)",
            "Universidad",
            "Hospital tipo 1 (alta complejidad)",
        ]
        if es_biobio:
            mat_10 = [
                [1, 1, 0, 1, 1, 1, 1, 1],  # Concepción (7)
                [1, 1, 0, 1, 1, 1, 1, 1],  # Los Ángeles (7)
                [1, 1, 0, 1, 0, 0, 1, 0],  # San Pedro de la Paz (4)
                [1, 1, 0, 1, 1, 1, 1, 1],  # Talcahuano (7 - Las Higueras)
                [1, 1, 1, 0, 1, 0, 0, 0],  # Coronel (4)
                [1, 1, 0, 0, 0, 0, 1, 0],  # Hualpén (3 - U. Federico Santa María)
                [1, 1, 0, 0, 0, 0, 0, 0],  # Chiguayante (2)
                [1, 1, 1, 0, 0, 0, 0, 0],  # Tomé (3)
                [1, 0, 1, 0, 0, 0, 0, 0],  # Penco (2 - Hosp. Penco-Lirquén)
                [1, 0, 1, 0, 1, 0, 0, 0],  # Lota (3 - CFT Lota-Arauco + Hosp. Lota)
            ]
        else:
            mat_10 = [
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 1, 1, 1, 1, 0, 0],
                [1, 1, 1, 0, 1, 0, 0, 0],
                [1, 1, 1, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
            ]
    else:
        cols = [
            "Estadios",
            "Gimnasios de gran capacidad",
            "Pistas de atletismo",
            "Piscinas públicas",
            "Multitiendas",
            "Centros comerciales (tipo mall)",
            "Cines",
            "Teatro / Centro cultural regional",
        ]
        if es_biobio:
            mat_10 = [
                [1, 1, 1, 1, 1, 1, 1, 1],  # Concepción (8)
                [1, 1, 1, 1, 1, 1, 1, 1],  # Los Ángeles (8)
                [1, 1, 1, 1, 1, 0, 0, 1],  # San Pedro de la Paz (6)
                [1, 1, 1, 1, 1, 1, 1, 0],  # Talcahuano (7 - Mall Plaza Trébol)
                [1, 1, 0, 0, 1, 1, 1, 0],  # Coronel (5 - Mall Arauco Coronel)
                [1, 1, 0, 0, 1, 0, 0, 0],  # Hualpén (3)
                [1, 1, 0, 1, 0, 0, 0, 0],  # Chiguayante (3)
                [1, 1, 0, 0, 0, 0, 0, 0],  # Tomé (2)
                [1, 0, 0, 0, 0, 0, 0, 0],  # Penco (1)
                [1, 0, 0, 0, 0, 0, 0, 1],  # Lota (2 - Teatro Lota)
            ]
        else:
            mat_10 = [
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1, 1, 1, 0],
                [1, 1, 0, 1, 1, 1, 1, 0],
                [1, 1, 0, 0, 1, 1, 0, 0],
                [1, 1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 1, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0, 0, 0],
            ]

    if n_c <= len(mat_10):
        mat = [row[:] for row in mat_10[:n_c]]
    else:
        mat = [row[:] for row in mat_10] + [[0] * len(cols) for _ in range(n_c - len(mat_10))]

    if n_c >= 2:
        for j in range(len(cols)):
            col_sum = sum(mat[i][j] for i in range(n_c))
            if col_sum == n_c:
                mat[-1][j] = 0
            elif col_sum == 0:
                mat[0][j] = 1

    return pd.DataFrame(mat, index=comunas_top10, columns=cols)

def construir_datos_ot_region(
    region_sel: str,
    resultados: dict,
    dimension_ot: str = DIMENSIONES_GUTTMAN_OT[0],
) -> dict:
    """
    Prepara los 3 insumos de Ordenamiento Territorial sincronizados con la región seleccionada:
    - df_censo: Comunas ordenadas por población 2024 (Censos 2017 y 2024).
    - df_guttman: Matriz binaria 1/0 (Top 10 comunas x 8 variables).
    - df_aislamiento: Matriz simétrica 0/1 (0 = conexión directa; 1 = sin conexión directa).
    """
    reg_ot_key = _mapear_region_a_control5(region_sel)
    df_censo = None
    df_aislamiento = None
    es_base_censo_oficial = False
    mapa_censo_17 = cargar_poblacion_censo_2017_xls()
    usa_archivo_censo_2017 = False

    if reg_ot_key is not None:
        try:
            from motor_redes_territorio_ot import (
                obtener_poblacion_censos_control5,
                obtener_matriz_aislamiento_control5,
            )
            df_censo = obtener_poblacion_censos_control5(reg_ot_key).copy()
            df_aislamiento = obtener_matriz_aislamiento_control5(reg_ot_key).copy()
            es_base_censo_oficial = True
            if mapa_censo_17 and not df_censo.empty:
                matches_17 = 0
                for idx_c, row_c in df_censo.iterrows():
                    info_17 = mapa_censo_17.get(_normalizar_texto(row_c["Comuna"]))
                    if info_17 is not None:
                        df_censo.at[idx_c, "Censo_2017"] = int(info_17["pob_2017"])
                        matches_17 += 1
                if matches_17 == len(df_censo):
                    usa_archivo_censo_2017 = True
        except Exception:
            df_censo = None
            df_aislamiento = None

    if df_censo is None or df_censo.empty:
        V0 = resultados["V0"]
        Vt = resultados["Vt"]
        tot_0 = V0.sum(axis=0)
        tot_t = Vt.sum(axis=0)
        filas = []
        n_match_17 = 0
        n_match_24 = 0
        for com in Vt.columns:
            com_key = _normalizar_texto(com)
            info_17 = mapa_censo_17.get(com_key) if mapa_censo_17 else None
            p24 = POBLACION_CENSO_2024.get(com_key)
            prov_nom = str(region_sel)
            if info_17 is not None:
                p17 = int(info_17["pob_2017"])
                if info_17.get("provincia"):
                    prov_nom = info_17["provincia"]
                n_match_17 += 1
            else:
                p17 = None
            if p24 is not None:
                p24 = int(p24)
                n_match_24 += 1
            if p24 is None and p17 is not None:
                p24 = max(500, int(round(p17 * 1.04)))
            elif p17 is None and p24 is not None:
                p17 = max(500, int(round(p24 * 0.94)))
            elif p17 is None and p24 is None:
                p24 = max(1000, int(round(float(tot_t.get(com, 1.0)))))
                p17 = max(1000, int(round(float(tot_0.get(com, 1.0)))))
            filas.append((str(com), prov_nom, int(p17), int(p24)))
        df_censo = pd.DataFrame(filas, columns=["Comuna", "Provincia", "Censo_2017", "Censo_2024"])
        df_censo = df_censo.sort_values("Censo_2024", ascending=False).reset_index(drop=True)
        if len(filas) > 0 and n_match_17 == len(filas):
            usa_archivo_censo_2017 = True
            if n_match_24 == len(filas):
                es_base_censo_oficial = True

    df_censo = df_censo.sort_values("Censo_2024", ascending=False).reset_index(drop=True)
    top10_comunas = df_censo["Comuna"].astype(str).tolist()[:10]
    df_guttman = _matriz_guttman_discriminante_default(dimension_ot, top10_comunas, region_sel=region_sel)

    todas_comunas = df_censo["Comuna"].astype(str).tolist()
    if df_aislamiento is None or df_aislamiento.empty or len(df_aislamiento) < len(todas_comunas):
        n_l = len(todas_comunas)
        mat_a = np.ones((n_l, n_l), dtype=int)
        np.fill_diagonal(mat_a, 0)
        # Conecta la capital regional (0) con los polos provinciales y enlaza corredor base editable
        prov_vistos = {}
        provs_list = df_censo["Provincia"].astype(str).tolist() if "Provincia" in df_censo.columns else ["Reg"] * n_l
        for i, pr_n in enumerate(provs_list):
            if pr_n not in prov_vistos:
                prov_vistos[pr_n] = i
                if i > 0:
                    mat_a[0, i] = 0
                    mat_a[i, 0] = 0
            else:
                hub_p = prov_vistos[pr_n]
                mat_a[hub_p, i] = 0
                mat_a[i, hub_p] = 0
        for i in range(1, min(n_l, 5)):
            mat_a[0, i] = 0
            mat_a[i, 0] = 0
        if df_aislamiento is not None and not df_aislamiento.empty:
            idx_full = {_normalizar_texto(c): idx for idx, c in enumerate(todas_comunas)}
            for r_nm in df_aislamiento.index:
                ri = idx_full.get(_normalizar_texto(r_nm))
                if ri is None:
                    continue
                for c_nm in df_aislamiento.columns:
                    ci = idx_full.get(_normalizar_texto(c_nm))
                    if ci is not None and ri != ci:
                        val_ex = int(pd.to_numeric(df_aislamiento.loc[r_nm, c_nm], errors="coerce") or 0)
                        mat_a[ri, ci] = 0 if val_ex == 0 else 1
                        mat_a[ci, ri] = mat_a[ri, ci]
        df_aislamiento = pd.DataFrame(mat_a, index=todas_comunas, columns=todas_comunas)

    p_24 = df_censo["Censo_2024"].astype(float).values
    p_17 = np.sort(df_censo["Censo_2017"].astype(float).values)[::-1]
    ip4_24 = float(p_24[0] / np.sum(p_24[1:4])) if len(p_24) >= 4 and np.sum(p_24[1:4]) > 0 else (
        float(p_24[0] / np.sum(p_24[1:])) if len(p_24) > 1 and np.sum(p_24[1:]) > 0 else 0.0
    )
    ip2_24 = float(p_24[0] / p_24[1]) if len(p_24) >= 2 and p_24[1] > 0 else 0.0
    ip4_17 = float(p_17[0] / np.sum(p_17[1:4])) if len(p_17) >= 4 and np.sum(p_17[1:4]) > 0 else 0.0

    if ip4_24 >= 1.50:
        cat_ip4, cod_ip4 = "Altamente Concentrada", 3
    elif ip4_24 >= 1.00:
        cat_ip4, cod_ip4 = "Concentrada", 2
    elif ip4_24 >= 0.65:
        cat_ip4, cod_ip4 = "Dispersa", 1
    else:
        cat_ip4, cod_ip4 = "Muy Dispersa", 0

    pob_reg_17 = int(df_censo["Censo_2017"].sum())
    pob_reg_24 = int(df_censo["Censo_2024"].sum())

    return {
        "df_censo": df_censo,
        "df_guttman": df_guttman,
        "df_aislamiento": df_aislamiento,
        "dimension_ot": dimension_ot,
        "es_base_censo_oficial": es_base_censo_oficial,
        "usa_archivo_censo_2017": usa_archivo_censo_2017,
        "pob_reg_17": pob_reg_17,
        "pob_reg_24": pob_reg_24,
        "ip4_24": ip4_24,
        "ip2_24": ip2_24,
        "ip4_17": ip4_17,
        "cat_ip4": cat_ip4,
        "cod_ip4": cod_ip4,
    }


def calcular_rondinelli_df(df_guttman: pd.DataFrame, df_censo: pd.DataFrame):
    """Calcula frecuencias fk, pesos Wk = 100/fk, índice de Rondinelli y columnas sin variación."""
    mat = df_guttman.apply(pd.to_numeric, errors="coerce").fillna(0).clip(0, 1).astype(int)
    n_com = len(mat)
    frec = mat.sum(axis=0)
    pesos = frec.apply(lambda f: (100.0 / float(f)) if f > 0 else 0.0)
    mat_pond = mat.multiply(pesos, axis=1)
    indice_ic = mat_pond.sum(axis=1)
    total_func = mat.sum(axis=1)

    mapa_pob = {
        _normalizar_texto(r["Comuna"]): int(r["Censo_2024"])
        for _, r in df_censo.iterrows()
    }
    pobs = [mapa_pob.get(_normalizar_texto(c), 0) for c in mat.index]
    tot_pob = max(sum(pobs), 1)

    df_res = pd.DataFrame({
        "Comuna": list(mat.index),
        "Poblacion_2024": pobs,
        "Pct_Poblacion_%": [(p / tot_pob) * 100.0 for p in pobs],
        "Total_Funciones": total_func.values,
        "Indice_Rondinelli": indice_ic.values,
    })
    df_res["Ranking_Funcional"] = df_res["Indice_Rondinelli"].rank(ascending=False, method="min").astype(int)

    cols_sin_discriminar = [
        col for col in mat.columns
        if int(frec[col]) == 0 or int(frec[col]) == n_com
    ]
    return df_res, mat_pond, frec, pesos, cols_sin_discriminar


def calcular_aislamiento_df(df_aislamiento: pd.DataFrame) -> pd.DataFrame:
    """Calcula suma de aislamiento (1), índice promedio (%) y conexiones directas (0) sin diagonal."""
    mat = df_aislamiento.apply(pd.to_numeric, errors="coerce").fillna(1).clip(0, 1).astype(int)
    n_l = len(mat)
    filas = []
    for i, loc in enumerate(mat.index):
        vals = [int(mat.iloc[i, j]) for j in range(n_l) if j != i]
        suma_1 = sum(vals)
        ind_pct = (suma_1 / max(len(vals), 1)) * 100.0
        conex_0 = sum(1 for v in vals if v == 0)
        filas.append({
            "Comuna_Localidad": str(loc),
            "Suma_Aislamiento_1": suma_1,
            "Indice_Aislamiento_%": ind_pct,
            "Conexiones_Directas_0": conex_0,
        })
    df_out = pd.DataFrame(filas)
    df_out["Ranking_Conectividad"] = df_out["Indice_Aislamiento_%"].rank(ascending=True, method="min").astype(int)
    return df_out.sort_values("Indice_Aislamiento_%", ascending=True).reset_index(drop=True)


def _agregar_hojas_ot_y_u6(
    wb: Workbook,
    resultados: dict,
    region_sel: str,
    variable_sel: str,
    anio_0: int,
    anio_t: int,
    datos_ot: dict,
    estilos: dict,
    incluir_ot: bool = True,
    incluir_u6: bool = False,
):
    """
    Agrega al libro Excel las hojas de Ordenamiento Territorial (Primacia y Ranking,
    Rondinelli, Aislamiento) y opcionalmente Indice Desarrollo (Min-Max).
    """
    if not incluir_ot and not incluir_u6:
        return

    fill_titulo = estilos["fill_titulo"]
    fill_header = estilos["fill_header"]
    fill_subbloque = estilos["fill_subbloque"]
    fill_gris_total = estilos["fill_gris_total"]
    fill_made_mod = estilos["fill_made_mod"]
    fill_fila_blanca = estilos["fill_fila_blanca"]
    fill_fila_cebra = estilos["fill_fila_cebra"]

    font_titulo = estilos["font_titulo"]
    font_sub = estilos["font_sub"]
    font_header = estilos["font_header"]
    font_subbloque = estilos["font_subbloque"]
    font_bold = estilos["font_bold"]
    font_celda = estilos["font_celda"]

    borde_fino = estilos["borde_fino"]
    borde_total = estilos["borde_total"]

    df_censo = datos_ot["df_censo"].sort_values("Censo_2024", ascending=False).reset_index(drop=True)
    df_guttman = datos_ot["df_guttman"].copy()
    df_aislamiento = datos_ot["df_aislamiento"].copy()
    dim_ot = datos_ot.get("dimension_ot", DIMENSIONES_GUTTMAN_OT[0])
    dim_nombre = dim_ot.split(".", 1)[1].strip() if "." in dim_ot else dim_ot
    if datos_ot.get("es_base_censo_oficial") and datos_ot.get("usa_archivo_censo_2017"):
        fuente_censo = "Fuente: INE, Censo 2017 y Censo 2024"
    elif datos_ot.get("es_base_censo_oficial"):
        fuente_censo = "Fuente: INE (Censos de Población 2017 y 2024)"
    elif datos_ot.get("usa_archivo_censo_2017"):
        fuente_censo = "Fuente: INE Censo 2017 y estimacion comunal 2024"
    else:
        fuente_censo = "Fuente: Estimación comunal referencial (2017 y 2024)"

    def _banner_sheet(ws, n_cols: int, titulo: str, subtitulo: str):
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(n_cols, 2))
        ct = ws.cell(row=1, column=1, value=titulo)
        ct.fill = fill_titulo
        ct.font = font_titulo
        ct.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[1].height = 26

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=max(n_cols, 2))
        cs = ws.cell(row=2, column=1, value=subtitulo)
        cs.font = font_sub
        cs.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[2].height = 19

    # Datos base de Rondinelli compartidos si se activa U6
    mat_g = df_guttman.apply(pd.to_numeric, errors="coerce").fillna(0).clip(0, 1).astype(int)
    funcs_cols = list(mat_g.columns)
    comunas_g = list(mat_g.index)
    n_f = len(funcs_cols)
    n_g = len(comunas_g)
    mapa_pob_censo = {
        _normalizar_texto(r["Comuna"]): int(r["Censo_2024"])
        for _, r in df_censo.iterrows()
    }
    df_rond_calc, _, _, _, _ = calcular_rondinelli_df(mat_g, df_censo)
    col_ic_rond_let = get_column_letter(5 + n_f)
    f_ini_rond = 5

    if incluir_ot:
        # HOJA: PRIMACÍA Y RANKING (CON FLECHAS DE CAMBIO Y GRÁFICO DE CRUCE)
        ws11 = wb.create_sheet("Primacía y Ranking")
        headers_11 = [
            "Comuna", "Provincia", "Población Censo 2017", "Población Censo 2024",
            "Ranking 2017", "Ranking 2024", "Cambio", "Tendencia",
            "Variación (%)", "Cuota Regional (%)", "Zipf Teórico (P1/Rango)",
        ]
        _banner_sheet(
            ws11,
            len(headers_11),
            f"Ranking de asentamientos e índice de primacía - {region_sel}",
            f"{fuente_censo}",
        )

        for c_i, h in enumerate(headers_11, start=1):
            ch = ws11.cell(row=4, column=c_i, value=h)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws11.row_dimensions[4].height = 25

        n_com = len(df_censo)
        f_ini_11 = 5
        f_fin_11 = f_ini_11 + n_com - 1
        f_tot_11 = f_fin_11 + 1

        # Pre-cálculo de rankings para columnas ocultas del gráfico de cruce (2017 -> 2024)
        rk17_ser = df_censo["Censo_2017"].rank(ascending=False, method="min").astype(int).tolist()
        rk24_ser = df_censo["Censo_2024"].rank(ascending=False, method="min").astype(int).tolist()

        for idx_off, row in enumerate(df_censo.itertuples(index=False)):
            idx_r = f_ini_11 + idx_off
            fill_r = fill_fila_blanca if (idx_r % 2 == 1) else fill_fila_cebra
            c_com = ws11.cell(row=idx_r, column=1, value=str(row.Comuna))
            c_pro = ws11.cell(row=idx_r, column=2, value=str(row.Provincia))
            for ct in (c_com, c_pro):
                ct.font = font_celda
                ct.fill = fill_r
                ct.alignment = Alignment(horizontal="left", vertical="center")
                ct.border = borde_fino

            c17 = ws11.cell(row=idx_r, column=3, value=int(row.Censo_2017))
            c24 = ws11.cell(row=idx_r, column=4, value=int(row.Censo_2024))
            for cp in (c17, c24):
                cp.fill = fill_r
                cp.font = font_celda
                cp.number_format = "#,##0"
                cp.alignment = Alignment(horizontal="right", vertical="center")
                cp.border = borde_fino

            cr17 = ws11.cell(row=idx_r, column=5, value=f"=RANK(C{idx_r},$C${f_ini_11}:$C${f_fin_11},0)")
            cr24 = ws11.cell(row=idx_r, column=6, value=f"=RANK(D{idx_r},$D${f_ini_11}:$D${f_fin_11},0)")
            cchg = ws11.cell(row=idx_r, column=7, value=f"=E{idx_r}-F{idx_r}")
            cten = ws11.cell(row=idx_r, column=8, value=f'=IF(E{idx_r}>F{idx_r},"Sube",IF(E{idx_r}<F{idx_r},"Baja","Igual"))')
            cvar = ws11.cell(row=idx_r, column=9, value=f"=IF(C{idx_r}>0,(D{idx_r}/C{idx_r})-1,0)")
            ccuo = ws11.cell(row=idx_r, column=10, value=f"=IF($D${f_tot_11}>0,D{idx_r}/$D${f_tot_11},0)")
            czip = ws11.cell(row=idx_r, column=11, value=f"=IF(F{idx_r}>0,$D${f_ini_11}/F{idx_r},0)")

            for cf, fmt, al in [
                (cr17, "0", "right"),
                (cr24, "0", "right"),
                (cchg, "+#,##0;-#,##0;0", "right"),
                (cten, "@", "center"),
                (cvar, "0.00%", "right"),
                (ccuo, "0.00%", "right"),
                (czip, "#,##0", "right"),
            ]:
                cf.fill = fill_made_mod
                cf.font = font_celda
                cf.number_format = fmt
                cf.alignment = Alignment(horizontal=al, vertical="center")
                cf.border = borde_fino

        ws11.cell(row=f_tot_11, column=1, value="Total regional")
        ws11.cell(row=f_tot_11, column=3, value=f"=SUM(C{f_ini_11}:C{f_fin_11})").number_format = "#,##0"
        ws11.cell(row=f_tot_11, column=4, value=f"=SUM(D{f_ini_11}:D{f_fin_11})").number_format = "#,##0"
        ws11.cell(row=f_tot_11, column=9, value=f"=IF(C{f_tot_11}>0,(D{f_tot_11}/C{f_tot_11})-1,0)").number_format = "0.00%"
        ws11.cell(row=f_tot_11, column=10, value=f"=SUM(J{f_ini_11}:J{f_fin_11})").number_format = "0.00%"
        for c_i in range(1, len(headers_11) + 1):
            ct = ws11.cell(row=f_tot_11, column=c_i)
            ct.font = font_bold
            ct.fill = fill_gris_total
            ct.border = borde_total
            if c_i >= 3:
                ct.alignment = Alignment(horizontal="right", vertical="center")

        # Bloque resumen de Índice de Primacía
        f_ip_hd = f_tot_11 + 2
        ws11.merge_cells(start_row=f_ip_hd, start_column=1, end_row=f_ip_hd, end_column=2)
        ws11.cell(row=f_ip_hd, column=1, value="Índice de Primacía Urbana")
        ws11.cell(row=f_ip_hd, column=3, value="Censo 2017")
        ws11.cell(row=f_ip_hd, column=4, value="Censo 2024")
        for c_i in range(1, 5):
            ch = ws11.cell(row=f_ip_hd, column=c_i)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center" if c_i >= 3 else "left", vertical="center")
            ch.border = borde_fino

        if n_com >= 2:
            f_ip2_17 = f"=IF(LARGE($C${f_ini_11}:$C${f_fin_11},2)>0,LARGE($C${f_ini_11}:$C${f_fin_11},1)/LARGE($C${f_ini_11}:$C${f_fin_11},2),0)"
            f_ip2_24 = f"=IF(LARGE($D${f_ini_11}:$D${f_fin_11},2)>0,LARGE($D${f_ini_11}:$D${f_fin_11},1)/LARGE($D${f_ini_11}:$D${f_fin_11},2),0)"
        else:
            f_ip2_17, f_ip2_24 = "=0", "=0"

        if n_com >= 4:
            den17 = f"(LARGE($C${f_ini_11}:$C${f_fin_11},2)+LARGE($C${f_ini_11}:$C${f_fin_11},3)+LARGE($C${f_ini_11}:$C${f_fin_11},4))"
            den24 = f"(LARGE($D${f_ini_11}:$D${f_fin_11},2)+LARGE($D${f_ini_11}:$D${f_fin_11},3)+LARGE($D${f_ini_11}:$D${f_fin_11},4))"
            f_ip4_17 = f"=IF({den17}>0,LARGE($C${f_ini_11}:$C${f_fin_11},1)/{den17},0)"
            f_ip4_24 = f"=IF({den24}>0,LARGE($D${f_ini_11}:$D${f_fin_11},1)/{den24},0)"
        else:
            f_ip4_17, f_ip4_24 = f_ip2_17, f_ip2_24

        r_ip2 = f_ip_hd + 1
        r_ip4 = f_ip_hd + 2
        r_val = f_ip_hd + 3
        r_cat = f_ip_hd + 4

        filas_ip = [
            (r_ip2, "Primacía 2 ciudades (P1 / P2)", f_ip2_17, f_ip2_24, "0.000"),
            (r_ip4, "Primacía 4 ciudades (P1 / (P2+P3+P4))", f_ip4_17, f_ip4_24, "0.000"),
            (r_val, "Valor estandarizado (0 a 3)", f"=IF(C{r_ip4}>=1.5,3,IF(C{r_ip4}>=1,2,IF(C{r_ip4}>=0.65,1,0)))", f"=IF(D{r_ip4}>=1.5,3,IF(D{r_ip4}>=1,2,IF(D{r_ip4}>=0.65,1,0)))", "0"),
            (r_cat, "Clasificación", f'=IF(C{r_ip4}>=1.5,"Altamente Concentrada",IF(C{r_ip4}>=1,"Concentrada",IF(C{r_ip4}>=0.65,"Dispersa","Muy Dispersa")))', f'=IF(D{r_ip4}>=1.5,"Altamente Concentrada",IF(D{r_ip4}>=1,"Concentrada",IF(D{r_ip4}>=0.65,"Dispersa","Muy Dispersa")))', "@"),
        ]
        for r_curr, etq_ip, form_c, form_d, fmt_ip in filas_ip:
            ws11.merge_cells(start_row=r_curr, start_column=1, end_row=r_curr, end_column=2)
            cl = ws11.cell(row=r_curr, column=1, value=etq_ip)
            cl.font = font_bold
            cl.fill = fill_subbloque
            ws11.cell(row=r_curr, column=1).border = borde_fino
            ws11.cell(row=r_curr, column=2).border = borde_fino
            for col_p, form_p in [(3, form_c), (4, form_d)]:
                cp = ws11.cell(row=r_curr, column=col_p, value=form_p)
                cp.font = font_bold
                cp.fill = fill_made_mod
                cp.number_format = fmt_ip
                cp.alignment = Alignment(horizontal="right" if fmt_ip != "@" else "center", vertical="center")
                cp.border = borde_fino

        # Tabla referencial de estandarización (Cols F:H)
        for ci_e, txt_e in [(6, "Categoría"), (7, "Rango IP4"), (8, "Valor")]:
            ce_h = ws11.cell(row=f_ip_hd, column=ci_e, value=txt_e)
            ce_h.fill = fill_header
            ce_h.font = font_header
            ce_h.alignment = Alignment(horizontal="center", vertical="center")
            ce_h.border = borde_fino

        escala_ref = [
            ("Altamente Concentrada", ">= 1,50", 3),
            ("Concentrada", "1,00 a 1,49", 2),
            ("Dispersa", "0,65 a 0,99", 1),
            ("Muy Dispersa", "< 0,65", 0),
        ]
        for off_e, (etq_e, rng_e, val_e) in enumerate(escala_ref, start=1):
            rr = f_ip_hd + off_e
            for ci_e, vv_e, al_e in [(6, etq_e, "left"), (7, rng_e, "center"), (8, val_e, "center")]:
                ce = ws11.cell(row=rr, column=ci_e, value=vv_e)
                ce.font = font_celda
                ce.fill = fill_fila_blanca if off_e % 2 == 1 else fill_fila_cebra
                ce.alignment = Alignment(horizontal=al_e, vertical="center")
                ce.border = borde_fino

        # Gráfico nativo de cruce de ranking (Top 10 comunas: Censo 2017 -> Censo 2024)
        top_n_rk = min(10, n_com)
        if top_n_rk >= 2:
            col_hid_cat = 27  # AA
            ws11.cell(row=4, column=col_hid_cat, value="Periodo")
            ws11.cell(row=5, column=col_hid_cat, value="Censo 2017")
            ws11.cell(row=6, column=col_hid_cat, value="Censo 2024")
            ws11.column_dimensions[get_column_letter(col_hid_cat)].hidden = True

            max_rk_plot = top_n_rk
            for k_rk in range(top_n_rk):
                c_col = col_hid_cat + 1 + k_rk
                ws11.cell(row=4, column=c_col, value=str(df_censo.loc[k_rk, "Comuna"]))
                ws11.cell(row=5, column=c_col, value=int(rk17_ser[k_rk]))
                ws11.cell(row=6, column=c_col, value=int(rk24_ser[k_rk]))
                ws11.column_dimensions[get_column_letter(c_col)].hidden = True
                max_rk_plot = max(max_rk_plot, int(rk17_ser[k_rk]), int(rk24_ser[k_rk]))

            chart_rk = LineChart()
            chart_rk.visible_cells_only = False
            chart_rk.title = f"Cambio de ranking comunal (Top {top_n_rk}, 2017 a 2024)"
            chart_rk.style = 2
            chart_rk.y_axis.title = "Posición en Ranking (1 = Mayor población)"
            chart_rk.y_axis.scaling.orientation = "maxMin"
            chart_rk.y_axis.scaling.min = 1
            chart_rk.y_axis.scaling.max = int(max_rk_plot)
            chart_rk.y_axis.majorUnit = 1
            chart_rk.y_axis.crosses = "max"
            chart_rk.x_axis.tickLblPos = "low"
            chart_rk.y_axis.tickLblPos = "low"
            chart_rk.legend.position = "r"
            chart_rk.width = 21
            chart_rk.height = 14.5

            data_rk = Reference(ws11, min_col=col_hid_cat + 1, max_col=col_hid_cat + top_n_rk, min_row=4, max_row=6)
            cats_rk = Reference(ws11, min_col=col_hid_cat, min_row=5, max_row=6)
            chart_rk.add_data(data_rk, titles_from_data=True)
            chart_rk.set_categories(cats_rk)

            paleta_rk = ["4472C4", "ED7D31", "A5A5A5", "FFC000", "5B9BD5", "70AD47", "264478", "9E480E", "636363", "997300"]
            for s_idx, ser in enumerate(chart_rk.series):
                col_hex = paleta_rk[s_idx % len(paleta_rk)]
                ser.graphicalProperties.line.solidFill = col_hex
                ser.graphicalProperties.line.width = 22000
                ser.marker.symbol = "circle"
                ser.marker.size = 6
                ser.marker.graphicalProperties.solidFill = col_hex
                ser.marker.graphicalProperties.line.solidFill = col_hex

            ws11.add_chart(chart_rk, "M4")

        _autoajustar_columnas_hoja(ws11, max_width=22, min_width=11, col_a_max=34)
        ws11.page_setup.orientation = ws11.ORIENTATION_LANDSCAPE
        ws11.page_setup.paperSize = ws11.PAPERSIZE_LETTER
        ws11.sheet_properties.pageSetUpPr.fitToPage = True
        ws11.page_setup.fitToWidth = 1
        ws11.page_setup.fitToHeight = 1
        ws11.print_area = f"A1:K{r_cat}"

        # HOJA: RONDINELLI (ESCALOGRAMA DE GUTTMAN + MATRIZ PONDERADA + GRÁFICO)
        ws12 = wb.create_sheet("Rondinelli")
        headers_12 = (
            ["Comuna", "Población (Censo 2024)", "% Población"]
            + funcs_cols
            + ["Total Servicios", "Índice Rondinelli", "Ranking Funcional"]
        )
        n_cols_12 = len(headers_12)
        _banner_sheet(
            ws12,
            n_cols_12,
            f"Escala de Guttman y matriz de Rondinelli - {dim_nombre} ({region_sel})",
            f"{region_sel}, Top {n_g} comunas por población (Censo 2024)",
        )

        ws12.merge_cells(start_row=3, start_column=1, end_row=3, end_column=n_cols_12)
        c_b1_tit = ws12.cell(row=3, column=1, value="1. Presencia / Ausencia de servicios (1 = presente, 0 = ausente)")
        c_b1_tit.fill = fill_subbloque
        c_b1_tit.font = font_subbloque
        ws12.row_dimensions[3].height = 20

        for c_i, h in enumerate(headers_12, start=1):
            ch = ws12.cell(row=4, column=c_i, value=h)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws12.row_dimensions[4].height = 28

        f_ini_12 = 5
        f_fin_12 = f_ini_12 + n_g - 1
        f_frec_12 = f_fin_12 + 1
        f_peso_12 = f_frec_12 + 1

        col_ini_var = 4
        col_fin_var = 3 + n_f
        col_ini_var_let = get_column_letter(col_ini_var)
        col_fin_var_let = get_column_letter(col_fin_var)
        col_tot_serv = col_fin_var + 1
        col_ic = col_fin_var + 2
        col_rk_f = col_fin_var + 3
        col_ic_let = get_column_letter(col_ic)

        col_hid_x = n_cols_12 + 2
        col_hid_y = n_cols_12 + 3

        for idx_off, com_nom in enumerate(comunas_g):
            r_i = f_ini_12 + idx_off
            fill_r = fill_fila_blanca if (r_i % 2 == 1) else fill_fila_cebra
            pob_c = mapa_pob_censo.get(_normalizar_texto(com_nom), 0)

            c_com = ws12.cell(row=r_i, column=1, value=str(com_nom))
            c_com.font = font_celda
            c_com.fill = fill_r
            c_com.border = borde_fino

            c_pob = ws12.cell(row=r_i, column=2, value=int(pob_c))
            c_pob.font = font_celda
            c_pob.fill = fill_r
            c_pob.number_format = "#,##0"
            c_pob.alignment = Alignment(horizontal="right", vertical="center")
            c_pob.border = borde_fino

            c_pct = ws12.cell(row=r_i, column=3, value=f"=IF($B${f_frec_12}>0,B{r_i}/$B${f_frec_12},0)")
            c_pct.font = font_celda
            c_pct.fill = fill_made_mod
            c_pct.number_format = "0.00%"
            c_pct.alignment = Alignment(horizontal="right", vertical="center")
            c_pct.border = borde_fino

            for f_off, f_nom in enumerate(funcs_cols):
                c_v = ws12.cell(row=r_i, column=col_ini_var + f_off, value=int(mat_g.loc[com_nom, f_nom]))
                c_v.font = font_celda
                c_v.fill = fill_r
                c_v.alignment = Alignment(horizontal="center", vertical="center")
                c_v.border = borde_fino

            c_ts = ws12.cell(row=r_i, column=col_tot_serv, value=f"=SUM({col_ini_var_let}{r_i}:{col_fin_var_let}{r_i})")
            c_ic_cell = ws12.cell(
                row=r_i,
                column=col_ic,
                value=f"=SUMPRODUCT({col_ini_var_let}{r_i}:{col_fin_var_let}{r_i},${col_ini_var_let}${f_peso_12}:${col_fin_var_let}${f_peso_12})",
            )
            c_rk = ws12.cell(row=r_i, column=col_rk_f, value=f"=RANK({col_ic_let}{r_i},${col_ic_let}${f_ini_12}:${col_ic_let}${f_fin_12},0)")

            for cf, fmt in [(c_ts, "0"), (c_ic_cell, "0.00"), (c_rk, "0")]:
                cf.fill = fill_made_mod
                cf.font = font_bold if cf is c_ic_cell else font_celda
                cf.number_format = fmt
                cf.alignment = Alignment(horizontal="right", vertical="center")
                cf.border = borde_fino

            ws12.cell(row=r_i, column=col_hid_x, value=float(pob_c))
            ws12.cell(row=r_i, column=col_hid_y, value=float(df_rond_calc.loc[idx_off, "Indice_Rondinelli"]))

        # Filas resumen Tabla 1: Suma (fk) y Ponderación (100/fk)
        ws12.cell(row=f_frec_12, column=1, value="Suma (frecuencia)")
        ws12.cell(row=f_frec_12, column=2, value=f"=SUM(B{f_ini_12}:B{f_fin_12})").number_format = "#,##0"
        ws12.cell(row=f_frec_12, column=3, value=f"=SUM(C{f_ini_12}:C{f_fin_12})").number_format = "0.00%"
        ws12.cell(row=f_frec_12, column=col_tot_serv, value=f"=SUM({get_column_letter(col_tot_serv)}{f_ini_12}:{get_column_letter(col_tot_serv)}{f_fin_12})").number_format = "0"
        ws12.cell(row=f_frec_12, column=col_ic, value=f"=SUM({col_ic_let}{f_ini_12}:{col_ic_let}{f_fin_12})").number_format = "0.00"

        ws12.cell(row=f_peso_12, column=1, value="Ponderación (100 / Suma)")
        for c_i in range(col_ini_var, col_fin_var + 1):
            cl = get_column_letter(c_i)
            c_fr = ws12.cell(row=f_frec_12, column=c_i, value=f"=SUM({cl}{f_ini_12}:{cl}{f_fin_12})")
            c_fr.alignment = Alignment(horizontal="center", vertical="center")
            c_pe = ws12.cell(row=f_peso_12, column=c_i, value=f"=IF({cl}{f_frec_12}>0,100/{cl}{f_frec_12},0)")
            c_pe.number_format = "0.00"
            c_pe.alignment = Alignment(horizontal="right", vertical="center")

        for c_i in range(1, n_cols_12 + 1):
            c1 = ws12.cell(row=f_frec_12, column=c_i)
            c1.font = font_bold
            c1.fill = fill_gris_total
            c1.border = borde_total
            if c_i in (2, 3, col_tot_serv, col_ic):
                c1.alignment = Alignment(horizontal="right", vertical="center")

            c2 = ws12.cell(row=f_peso_12, column=c_i)
            c2.font = font_bold
            c2.fill = fill_subbloque
            c2.border = borde_fino

        # Tabla 2: Matriz Ponderada de Rondinelli
        f_b2_tit = f_peso_12 + 2
        ws12.merge_cells(start_row=f_b2_tit, start_column=1, end_row=f_b2_tit, end_column=col_tot_serv)
        c_b2 = ws12.cell(row=f_b2_tit, column=1, value="2. Matriz ponderada (Rondinelli)")
        c_b2.fill = fill_subbloque
        c_b2.font = font_subbloque
        ws12.row_dimensions[f_b2_tit].height = 20

        f_b2_hd = f_b2_tit + 1
        headers_b2 = ["Comuna", "Población (Censo 2024)", "% Población"] + funcs_cols + ["Índice Funcional"]
        for c_i, h in enumerate(headers_b2, start=1):
            ch = ws12.cell(row=f_b2_hd, column=c_i, value=h)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws12.row_dimensions[f_b2_hd].height = 26

        f_b2_ini = f_b2_hd + 1
        f_b2_fin = f_b2_ini + n_g - 1
        f_b2_tot = f_b2_fin + 1

        for idx_off in range(n_g):
            r_src = f_ini_12 + idx_off
            r_dst = f_b2_ini + idx_off
            fill_r = fill_fila_blanca if (r_dst % 2 == 1) else fill_fila_cebra

            c_a = ws12.cell(row=r_dst, column=1, value=f"=A{r_src}")
            c_a.font = font_celda
            c_a.fill = fill_r
            c_a.border = borde_fino

            c_b = ws12.cell(row=r_dst, column=2, value=f"=B{r_src}")
            c_b.font = font_celda
            c_b.fill = fill_r
            c_b.number_format = "#,##0"
            c_b.alignment = Alignment(horizontal="right", vertical="center")
            c_b.border = borde_fino

            c_c = ws12.cell(row=r_dst, column=3, value=f"=C{r_src}")
            c_c.font = font_celda
            c_c.fill = fill_made_mod
            c_c.number_format = "0.00%"
            c_c.alignment = Alignment(horizontal="right", vertical="center")
            c_c.border = borde_fino

            for f_off in range(n_f):
                c_idx = col_ini_var + f_off
                cl = get_column_letter(c_idx)
                cp = ws12.cell(row=r_dst, column=c_idx, value=f"=IF({cl}{r_src}=1,{cl}${f_peso_12},0)")
                cp.font = font_celda
                cp.fill = fill_r
                cp.number_format = "0.00"
                cp.alignment = Alignment(horizontal="right", vertical="center")
                cp.border = borde_fino

            c_sum_p = ws12.cell(row=r_dst, column=col_tot_serv, value=f"=SUM({col_ini_var_let}{r_dst}:{col_fin_var_let}{r_dst})")
            c_sum_p.font = font_bold
            c_sum_p.fill = fill_made_mod
            c_sum_p.number_format = "0.00"
            c_sum_p.alignment = Alignment(horizontal="right", vertical="center")
            c_sum_p.border = borde_fino

        ws12.cell(row=f_b2_tot, column=1, value="Total ponderado")
        ws12.cell(row=f_b2_tot, column=2, value=f"=SUM(B{f_b2_ini}:B{f_b2_fin})").number_format = "#,##0"
        ws12.cell(row=f_b2_tot, column=3, value=f"=SUM(C{f_b2_ini}:C{f_b2_fin})").number_format = "0.00%"
        for c_i in range(col_ini_var, col_tot_serv + 1):
            cl = get_column_letter(c_i)
            cs = ws12.cell(row=f_b2_tot, column=c_i, value=f"=SUM({cl}{f_b2_ini}:{cl}{f_b2_fin})")
            cs.number_format = "0.00"
            cs.alignment = Alignment(horizontal="right", vertical="center")
        for c_i in range(1, col_tot_serv + 1):
            ct = ws12.cell(row=f_b2_tot, column=c_i)
            ct.font = font_bold
            ct.fill = fill_gris_total
            ct.border = borde_total
            if c_i >= 2:
                ct.alignment = Alignment(horizontal="right", vertical="center")

        ws12.column_dimensions[get_column_letter(col_hid_x)].hidden = True
        ws12.column_dimensions[get_column_letter(col_hid_y)].hidden = True

        chart_rond = ScatterChart()
        chart_rond.visible_cells_only = False
        chart_rond.title = f"Complejidad funcional vs. población (Censo 2024) - {region_sel}"
        chart_rond.style = 2
        chart_rond.legend = None
        chart_rond.x_axis.title = "Población Comunal (Censo 2024)"
        chart_rond.y_axis.title = "Índice de Centralidad Funcional (Rondinelli)"
        chart_rond.x_axis.number_format = "#,##0"
        chart_rond.y_axis.number_format = "0.0"
        chart_rond.x_axis.tickLblPos = "low"
        chart_rond.y_axis.tickLblPos = "low"
        chart_rond.width = 24
        chart_rond.height = 13.5

        for idx_off in range(n_g):
            r_i = f_ini_12 + idx_off
            nom_c = str(comunas_g[idx_off])
            x_ref = Reference(ws12, min_col=col_hid_x, min_row=r_i, max_row=r_i)
            y_ref = Reference(ws12, min_col=col_hid_y, min_row=r_i, max_row=r_i)
            s_pt = Series(y_ref, x_ref, title=nom_c)
            s_pt.marker.symbol = "circle"
            s_pt.marker.size = 7
            s_pt.marker.graphicalProperties.solidFill = "4472C4"
            s_pt.marker.graphicalProperties.line.solidFill = "2F5597"
            s_pt.graphicalProperties.line.noFill = True
            s_pt.dLbls = DataLabelList()
            s_pt.dLbls.showSerName = True
            s_pt.dLbls.showVal = False
            s_pt.dLbls.showCatName = False
            s_pt.dLbls.showLegendKey = False
            chart_rond.series.append(s_pt)

        ws12.add_chart(chart_rond, f"A{f_b2_tot + 3}")
        _autoajustar_columnas_hoja(ws12, max_width=22, min_width=12, col_a_max=34)
        ws12.page_setup.orientation = ws12.ORIENTATION_LANDSCAPE
        ws12.page_setup.paperSize = ws12.PAPERSIZE_LETTER
        ws12.sheet_properties.pageSetUpPr.fitToPage = True
        ws12.page_setup.fitToWidth = 1
        ws12.page_setup.fitToHeight = 1
        ws12.print_area = f"A1:{get_column_letter(n_cols_12)}{f_b2_tot}"

        # HOJA: AISLAMIENTO (MATRIZ 0/1 Y RANKING DE CONECTIVIDAD)
        ws13 = wb.create_sheet("Aislamiento")
        mat_a = df_aislamiento.apply(pd.to_numeric, errors="coerce").fillna(1).clip(0, 1).astype(int)
        locs = list(mat_a.index)
        n_l = len(locs)
        headers_13 = (
            ["Localidad / Comuna"]
            + locs
            + ["Suma Aislamiento", "Índice Aislamiento (%)", "Conexiones Directas", "Ranking Conectividad"]
        )
        _banner_sheet(
            ws13,
            len(headers_13),
            f"Matriz de aislamiento comunal - {region_sel}",
            "Conectividad vial (0 = conexión directa asfaltada, 1 = sin conexión directa)",
        )

        for c_i, h in enumerate(headers_13, start=1):
            ch = ws13.cell(row=4, column=c_i, value=h)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws13.row_dimensions[4].height = 25

        f_ini_13 = 5
        f_fin_13 = f_ini_13 + n_l - 1
        f_prom_13 = f_fin_13 + 1
        col_fin_l_let = get_column_letter(1 + n_l)
        col_sum1 = 2 + n_l
        col_avg1 = 3 + n_l
        col_con0 = 4 + n_l
        col_rk_a = 5 + n_l
        col_avg1_let = get_column_letter(col_avg1)

        for idx_off, loc_nom in enumerate(locs):
            r_i = f_ini_13 + idx_off
            fill_r = fill_fila_blanca if (r_i % 2 == 1) else fill_fila_cebra
            c_loc = ws13.cell(row=r_i, column=1, value=str(loc_nom))
            c_loc.font = font_celda
            c_loc.fill = fill_r
            c_loc.border = borde_fino

            for c_off, col_nom in enumerate(locs):
                c_i = 2 + c_off
                if idx_off == c_off:
                    cd = ws13.cell(row=r_i, column=c_i, value=None)
                    cd.fill = fill_subbloque
                    cd.border = borde_fino
                else:
                    val_a = int(mat_a.loc[loc_nom, col_nom]) if col_nom in mat_a.columns else 1
                    ca = ws13.cell(row=r_i, column=c_i, value=val_a)
                    ca.fill = fill_r
                    ca.font = font_celda
                    ca.alignment = Alignment(horizontal="center", vertical="center")
                    ca.border = borde_fino

            csum1 = ws13.cell(row=r_i, column=col_sum1, value=f"=SUM(B{r_i}:{col_fin_l_let}{r_i})")
            cavg1 = ws13.cell(row=r_i, column=col_avg1, value=f"=AVERAGE(B{r_i}:{col_fin_l_let}{r_i})")
            ccon0 = ws13.cell(row=r_i, column=col_con0, value=f"=COUNTIF(B{r_i}:{col_fin_l_let}{r_i},0)")
            crka = ws13.cell(row=r_i, column=col_rk_a, value=f"=RANK({col_avg1_let}{r_i},${col_avg1_let}${f_ini_13}:${col_avg1_let}${f_fin_13},1)")

            for cf, fmt in [(csum1, "0"), (cavg1, "0.00%"), (ccon0, "0"), (crka, "0")]:
                cf.fill = fill_made_mod
                cf.font = font_bold if cf is cavg1 else font_celda
                cf.number_format = fmt
                cf.alignment = Alignment(horizontal="right", vertical="center")
                cf.border = borde_fino

        ws13.cell(row=f_prom_13, column=1, value="Promedio regional")
        ws13.cell(row=f_prom_13, column=col_sum1, value=f"=AVERAGE({get_column_letter(col_sum1)}{f_ini_13}:{get_column_letter(col_sum1)}{f_fin_13})").number_format = "0.00"
        ws13.cell(row=f_prom_13, column=col_avg1, value=f"=AVERAGE({col_avg1_let}{f_ini_13}:{col_avg1_let}{f_fin_13})").number_format = "0.00%"
        ws13.cell(row=f_prom_13, column=col_con0, value=f"=AVERAGE({get_column_letter(col_con0)}{f_ini_13}:{get_column_letter(col_con0)}{f_fin_13})").number_format = "0.00"
        for c_i in range(1, len(headers_13) + 1):
            cp = ws13.cell(row=f_prom_13, column=c_i)
            cp.font = font_bold
            cp.fill = fill_gris_total
            cp.border = borde_total
            if c_i >= col_sum1:
                cp.alignment = Alignment(horizontal="right", vertical="center")

        fill_con0_13 = PatternFill("solid", fgColor="EDEDED")
        font_con0_13 = Font(name="Calibri", size=9, bold=True, color="000000")
        for r_chk in range(f_ini_13, f_fin_13 + 1):
            for c_chk in range(2, 2 + n_l):
                cel_v = ws13.cell(row=r_chk, column=c_chk)
                if cel_v.value == 0:
                    cel_v.fill = fill_con0_13
                    cel_v.font = font_con0_13

        ws13.freeze_panes = "B5"
        if n_l > 12:
            ws13.row_dimensions[4].height = 96
            for c_i in range(2, 2 + n_l):
                ws13.cell(row=4, column=c_i).alignment = Alignment(
                    horizontal="center", vertical="bottom", textRotation=90, wrap_text=False
                )
                ws13.column_dimensions[get_column_letter(c_i)].width = 4.2
            ws13.column_dimensions["A"].width = 24
            for c_i in range(col_sum1, len(headers_13) + 1):
                ws13.column_dimensions[get_column_letter(c_i)].width = 14
        else:
            _autoajustar_columnas_hoja(ws13, max_width=18, min_width=11, col_a_max=30)

        ws13.page_setup.orientation = ws13.ORIENTATION_LANDSCAPE
        ws13.page_setup.paperSize = ws13.PAPERSIZE_LETTER
        ws13.sheet_properties.pageSetUpPr.fitToPage = True
        ws13.page_setup.fitToWidth = 1
        ws13.page_setup.fitToHeight = 1
        ws13.print_area = f"A1:{get_column_letter(len(headers_13))}{f_prom_13}"

    if incluir_u6:
        # HOJA OPCIONAL: ÍNDICE DESARROLLO (NORMALIZACIÓN Min-Max Y PESOS)
        ws14 = wb.create_sheet("Índice Desarrollo")
        _, lbl_vt_sii, lbl_pc_sii, fmt_tot_sii, fmt_pc_sii = _etiquetas_variable_sii(variable_sel, anio_0, anio_t)

        Vt_tot = resultados["Vt"].sum(axis=0)
        mapa_sii_norm = {_normalizar_texto(k): float(v) for k, v in Vt_tot.items()}

        pobs_top = [mapa_pob_censo.get(_normalizar_texto(c), 0) for c in comunas_g]
        usa_pc_u6 = all(p > 0 for p in pobs_top)
        if usa_pc_u6:
            lbl_v1 = lbl_pc_sii
            fmt_v1 = fmt_pc_sii
            v1_vals = [mapa_sii_norm.get(_normalizar_texto(c), 0.0) / float(p) for c, p in zip(comunas_g, pobs_top)]
        else:
            lbl_v1 = lbl_vt_sii
            fmt_v1 = fmt_tot_sii
            v1_vals = [mapa_sii_norm.get(_normalizar_texto(c), 0.0) for c in comunas_g]

        headers_14 = [
            "Comuna", lbl_v1, "Índice Rondinelli",
            "u(v1)", "u(v2)",
            "Índice 50 / 50", "Índice 70 / 30",
            "Ranking 50 / 50", "Ranking 70 / 30", "Cambio",
        ]
        _banner_sheet(
            ws14,
            len(headers_14),
            f"Índice de desarrollo territorial - {region_sel}",
            f"{region_sel}, normalización Mín-Máx [0, 1] y pesos 50/50 vs. 70/30 ({anio_t})",
        )

        for ci_p, txt_p in [(1, "Parámetro"), (2, "v1 (Económica)"), (3, "v2 (Funcional)"), (4, "Referencia")]:
            ch = ws14.cell(row=5, column=ci_p, value=txt_p)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center")
            ch.border = borde_fino

        for ci_w, txt_w in [(6, "Escenario"), (7, "Peso v1"), (8, "Peso v2")]:
            ch = ws14.cell(row=5, column=ci_w, value=txt_w)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center")
            ch.border = borde_fino

        f_ini_14 = 11
        f_fin_14 = f_ini_14 + n_g - 1

        ws14.cell(row=6, column=1, value="Mínimo").font = font_bold
        ws14.cell(row=6, column=2, value=f"=MIN(B{f_ini_14}:B{f_fin_14})").number_format = fmt_v1
        ws14.cell(row=6, column=3, value=f"=MIN(C{f_ini_14}:C{f_fin_14})").number_format = "0.00"
        ws14.cell(row=6, column=4, value=f"Mínimo ({n_g} comunas)")

        ws14.cell(row=7, column=1, value="Máximo").font = font_bold
        ws14.cell(row=7, column=2, value=f"=MAX(B{f_ini_14}:B{f_fin_14})").number_format = fmt_v1
        ws14.cell(row=7, column=3, value=f"=MAX(C{f_ini_14}:C{f_fin_14})").number_format = "0.00"
        ws14.cell(row=7, column=4, value="Sentido positivo")

        ws14.cell(row=6, column=6, value="50 / 50").font = font_bold
        ws14.cell(row=6, column=7, value=0.50).number_format = "0%"
        ws14.cell(row=6, column=8, value=0.50).number_format = "0%"

        ws14.cell(row=7, column=6, value="70 / 30").font = font_bold
        ws14.cell(row=7, column=7, value=0.70).number_format = "0%"
        ws14.cell(row=7, column=8, value=0.30).number_format = "0%"

        for rr in (6, 7):
            for cc in (1, 2, 3, 4, 6, 7, 8):
                cel = ws14.cell(row=rr, column=cc)
                cel.border = borde_fino
                if cc in (2, 3):
                    cel.fill = fill_made_mod
                    cel.font = font_bold
                    cel.alignment = Alignment(horizontal="right", vertical="center")
                elif cc in (7, 8):
                    cel.fill = fill_fila_blanca
                    cel.font = font_bold
                    cel.alignment = Alignment(horizontal="right", vertical="center")
                else:
                    cel.fill = fill_subbloque if cc in (1, 6) else fill_fila_cebra
                    if cc == 4:
                        cel.font = font_celda

        for c_i, h in enumerate(headers_14, start=1):
            ch = ws14.cell(row=10, column=c_i, value=h)
            ch.fill = fill_header
            ch.font = font_header
            ch.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            ch.border = borde_fino
        ws14.row_dimensions[10].height = 26

        v2_vals = [float(df_rond_calc.loc[i, "Indice_Rondinelli"]) for i in range(n_g)]
        min_v1, max_v1 = (min(v1_vals), max(v1_vals)) if v1_vals else (0.0, 1.0)
        min_v2, max_v2 = (min(v2_vals), max(v2_vals)) if v2_vals else (0.0, 1.0)

        ws14.cell(row=10, column=13, value="Comuna")
        ws14.cell(row=10, column=14, value="Índice 50 / 50")
        ws14.cell(row=10, column=15, value="Índice 70 / 30")

        for idx_off in range(n_g):
            r_i = f_ini_14 + idx_off
            r_ot = f_ini_rond + idx_off
            fill_r = fill_fila_blanca if (r_i % 2 == 1) else fill_fila_cebra

            val_com = f"='Rondinelli'!A{r_ot}" if incluir_ot else str(comunas_g[idx_off])
            val_v2 = f"='Rondinelli'!{col_ic_rond_let}{r_ot}" if incluir_ot else float(v2_vals[idx_off])

            c_a = ws14.cell(row=r_i, column=1, value=val_com)
            c_a.font = font_celda
            c_a.fill = fill_r
            c_a.border = borde_fino

            c_b = ws14.cell(row=r_i, column=2, value=float(v1_vals[idx_off]))
            c_b.font = font_celda
            c_b.fill = fill_r
            c_b.number_format = fmt_v1
            c_b.alignment = Alignment(horizontal="right", vertical="center")
            c_b.border = borde_fino

            c_c = ws14.cell(row=r_i, column=3, value=val_v2)
            c_c.font = font_celda
            c_c.fill = fill_made_mod if incluir_ot else fill_r
            c_c.number_format = "0.00"
            c_c.alignment = Alignment(horizontal="right", vertical="center")
            c_c.border = borde_fino

            c_u1 = ws14.cell(row=r_i, column=4, value=f"=IF(($B$7-$B$6)>0,(B{r_i}-$B$6)/($B$7-$B$6),0)")
            c_u2 = ws14.cell(row=r_i, column=5, value=f"=IF(($C$7-$C$6)>0,(C{r_i}-$C$6)/($C$7-$C$6),0)")
            c_i50 = ws14.cell(row=r_i, column=6, value=f"=(D{r_i}*$G$6)+(E{r_i}*$H$6)")
            c_i70 = ws14.cell(row=r_i, column=7, value=f"=(D{r_i}*$G$7)+(E{r_i}*$H$7)")
            c_r50 = ws14.cell(row=r_i, column=8, value=f"=RANK(F{r_i},$F${f_ini_14}:$F${f_fin_14},0)")
            c_r70 = ws14.cell(row=r_i, column=9, value=f"=RANK(G{r_i},$G${f_ini_14}:$G${f_fin_14},0)")
            c_dif = ws14.cell(row=r_i, column=10, value=f"=H{r_i}-I{r_i}")

            for cf, fmt in [
                (c_u1, "0.000"), (c_u2, "0.000"),
                (c_i50, "0.000"), (c_i70, "0.000"),
                (c_r50, "0"), (c_r70, "0"), (c_dif, "+#,##0;-#,##0;0"),
            ]:
                cf.fill = fill_made_mod
                cf.font = font_bold if cf in (c_i50, c_i70) else font_celda
                cf.number_format = fmt
                cf.alignment = Alignment(horizontal="right", vertical="center")
                cf.border = borde_fino

            u1_num = (v1_vals[idx_off] - min_v1) / (max_v1 - min_v1) if max_v1 > min_v1 else 0.0
            u2_num = (v2_vals[idx_off] - min_v2) / (max_v2 - min_v2) if max_v2 > min_v2 else 0.0
            ws14.cell(row=r_i, column=13, value=str(comunas_g[idx_off]))
            ws14.cell(row=r_i, column=14, value=float(0.5 * u1_num + 0.5 * u2_num))
            ws14.cell(row=r_i, column=15, value=float(0.7 * u1_num + 0.3 * u2_num))

        f_avg_14 = f_fin_14 + 1
        ws14.cell(row=f_avg_14, column=1, value="Promedio")
        for ci_a, fmt_a in [(2, fmt_v1), (3, "0.00"), (4, "0.000"), (5, "0.000"), (6, "0.000"), (7, "0.000")]:
            cl = get_column_letter(ci_a)
            ca = ws14.cell(row=f_avg_14, column=ci_a, value=f"=AVERAGE({cl}{f_ini_14}:{cl}{f_fin_14})")
            ca.number_format = fmt_a
            ca.alignment = Alignment(horizontal="right", vertical="center")
        for c_i in range(1, len(headers_14) + 1):
            ct = ws14.cell(row=f_avg_14, column=c_i)
            ct.font = font_bold
            ct.fill = fill_gris_total
            ct.border = borde_total

        for col_hid_let in ("M", "N", "O"):
            ws14.column_dimensions[col_hid_let].hidden = True

        chart_u6 = BarChart()
        chart_u6.type = "col"
        chart_u6.grouping = "clustered"
        chart_u6.visible_cells_only = False
        chart_u6.title = f"Índice de desarrollo (50/50 vs. 70/30) - {region_sel}"
        chart_u6.style = 2
        chart_u6.y_axis.title = "Puntaje Normalizado [0, 1]"
        chart_u6.y_axis.number_format = "0.00"
        chart_u6.y_axis.scaling.min = 0.0
        chart_u6.y_axis.scaling.max = 1.0
        chart_u6.width = 24
        chart_u6.height = 12.5

        data_ref = Reference(ws14, min_col=14, max_col=15, min_row=10, max_row=f_fin_14)
        cats_ref = Reference(ws14, min_col=13, min_row=f_ini_14, max_row=f_fin_14)
        chart_u6.add_data(data_ref, titles_from_data=True)
        chart_u6.set_categories(cats_ref)
        if len(chart_u6.series) >= 2:
            chart_u6.series[0].graphicalProperties.solidFill = "4472C4"
            chart_u6.series[1].graphicalProperties.solidFill = "A5A5A5"
        ws14.add_chart(chart_u6, f"A{f_avg_14 + 3}")

        _autoajustar_columnas_hoja(ws14, max_width=22, min_width=11, col_a_max=32)
        ancho_com_u6 = max((len(str(c)) for c in comunas_g), default=14) + 4
        ws14.column_dimensions["A"].width = round(max(ws14.column_dimensions["A"].width or 16, min(ancho_com_u6, 32)), 1)


def compilar_excel_10_hojas(
    resultados: dict,
    region_sel: str,
    variable_sel: str,
    anio_0: int,
    anio_t: int,
    alpha_hk: float = 2.0,
    incluir_ot: bool = True,
    incluir_u6: bool = False,
    datos_ot: dict = None,
) -> bytes:
    """
    Genera el archivo Excel (.xlsx) con formulas, formato simple de Excel
    y formato condicional en Qij > 1 y Xij > 0.
    """
    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = ""
    wb.properties.lastModifiedBy = ""
    wb.properties.title = ""
    wb.properties.subject = ""
    wb.properties.description = ""

    sub_general = f"{region_sel}, {variable_sel}, periodo {anio_0}-{anio_t} (Fuente: SII)"

    # Estilo sencillo de Excel: encabezados/totales gris suave y resaltados pedagogicos estandar
    sin_relleno = PatternFill(fill_type=None)
    fill_titulo = sin_relleno
    fill_header = PatternFill("solid", fgColor="D9D9D9")
    fill_subbloque = PatternFill("solid", fgColor="EDEDED")
    fill_gris_total = PatternFill("solid", fgColor="E2E2E2")
    fill_ref = PatternFill("solid", fgColor="F2F2F2")
    fill_made_mod = PatternFill("solid", fgColor="F2F2F2")
    # Relleno rojo claro estandar de Excel para formato condicional (Qij > 1 y Xij > 0)
    fill_rosado_q = PatternFill("solid", fgColor="FFC7CE")

    fill_fila_blanca = sin_relleno
    fill_fila_cebra = sin_relleno
    # Tonos pastel estandar de Excel para distinguir los 4 cuadrantes de Silva Lira
    fill_cuad_1 = PatternFill("solid", fgColor="E2EFDA")
    fill_cuad_2 = PatternFill("solid", fgColor="DDEBF7")
    fill_cuad_3 = PatternFill("solid", fgColor="FFF2CC")
    fill_cuad_4 = PatternFill("solid", fgColor="FCE4D6")

    font_titulo = Font(name="Calibri", size=11, bold=True, color="000000")
    font_sub = Font(name="Calibri", size=10, italic=True, color="333333")
    font_header = Font(name="Calibri", size=10, bold=True, color="000000")
    font_subbloque = Font(name="Calibri", size=10, bold=True, color="000000")
    font_bold = Font(name="Calibri", size=10, bold=True, color="000000")
    font_celda = Font(name="Calibri", size=10, color="000000")
    font_rojo_q = Font(name="Calibri", size=10, bold=True, color="9C0006")

    borde_fino = Border(
        left=Side(style="thin", color="BFBFBF"),
        right=Side(style="thin", color="BFBFBF"),
        top=Side(style="thin", color="BFBFBF"),
        bottom=Side(style="thin", color="BFBFBF"),
    )
    borde_total = Border(
        left=Side(style="thin", color="808080"),
        right=Side(style="thin", color="808080"),
        top=Side(style="thin", color="000000"),
        bottom=Side(style="double", color="000000"),
    )

    mb = resultados["metricas_beta"]
    tot = resultados["totales"]
    V0 = resultados["V0"]
    Vt = resultados["Vt"]
    Q0 = resultados["Q_ij_0"]
    Qt = resultados["Q_ij_t"]
    X0 = resultados["X_ij_0"]
    Xt = resultados["X_ij_t"]
    ED_mat = resultados["ED_mat"]
    EE_mat = resultados["EE_mat"]
    EI_mat = resultados["EI_mat"]
    rubros = list(V0.index)
    comunas = list(V0.columns)
    n_rubros = len(rubros)
    n_comunas = len(comunas)

    # HOJA 1: RESUMEN
    df_portada = pd.DataFrame([
        {"Indicador": "Región analizada", "Valor": str(region_sel)},
        {"Indicador": "Variable económica (SII)", "Valor": str(variable_sel)},
        {"Indicador": "Periodo económico (SII)", "Valor": f"{anio_0}-{anio_t} ({mb['T_anios']} años)"},
        {"Indicador": "Comunas activas", "Valor": tot["n_comunas"]},
        {"Indicador": "Rubros económicos SII", "Valor": tot["n_rubros"]},
        {"Indicador": f"Total regional {anio_0}", "Valor": tot["total_reg_0"]},
        {"Indicador": f"Total regional {anio_t}", "Valor": tot["total_reg_t"]},
        {"Indicador": "Variación regional acumulada (%)", "Valor": tot["tasa_var_reg"]},
        {"Indicador": "Pendiente Beta absoluta (OLS)", "Valor": mb["beta"]},
        {"Indicador": "Intercepto Alpha (OLS)", "Valor": mb["alpha"]},
        {"Indicador": "Coeficiente R2 (Convergencia Beta)", "Valor": mb["r2"]},
        {"Indicador": "P-valor regresión Beta", "Valor": mb["p_value"]},
        {"Indicador": "Velocidad de convergencia (anual)", "Valor": mb["velocidad_lambda"]},
        {
            "Indicador": "Semivida (años)",
            "Valor": float(mb["half_life"]) if np.isfinite(mb["half_life"]) else "No aplica (divergencia)",
        },
    ])

    datos_ot_act = None
    if incluir_ot or incluir_u6:
        datos_ot_act = datos_ot if datos_ot is not None else construir_datos_ot_region(region_sel, resultados)

    if incluir_ot and datos_ot_act is not None:
        df_rond_res, _, _, _, _ = calcular_rondinelli_df(datos_ot_act["df_guttman"], datos_ot_act["df_censo"])
        df_aisl_res = calcular_aislamiento_df(datos_ot_act["df_aislamiento"])
        lider_rond = str(df_rond_res.sort_values("Indice_Rondinelli", ascending=False).iloc[0]["Comuna"]) if not df_rond_res.empty else "-"
        score_rond = float(df_rond_res["Indice_Rondinelli"].max()) if not df_rond_res.empty else 0.0
        mejor_con = str(df_aisl_res.iloc[0]["Comuna_Localidad"]) if not df_aisl_res.empty else "-"
        pct_aisl_min = float(df_aisl_res.iloc[0]["Indice_Aislamiento_%"]) if not df_aisl_res.empty else 0.0
        pob_17_tot = int(datos_ot_act.get("pob_reg_17", datos_ot_act["df_censo"]["Censo_2017"].sum()))
        pob_24_tot = int(datos_ot_act.get("pob_reg_24", datos_ot_act["df_censo"]["Censo_2024"].sum()))
        filas_ot_portada = pd.DataFrame([
            {"Indicador": "Periodo censal población (OT)", "Valor": "Censos 2017 y 2024 (INE)"},
            {"Indicador": "Población regional (Censo 2017)", "Valor": pob_17_tot},
            {"Indicador": "Población regional (Censo 2024)", "Valor": pob_24_tot},
            {"Indicador": "Índice de primacía 4 ciudades (Censo 2017)", "Valor": round(datos_ot_act["ip4_17"], 4)},
            {"Indicador": "Índice de primacía 4 ciudades (Censo 2024)", "Valor": round(datos_ot_act["ip4_24"], 4)},
            {"Indicador": "Clasificación de primacía (Censo 2024)", "Valor": f"{datos_ot_act['cat_ip4']} ({datos_ot_act['cod_ip4']})"},
            {"Indicador": "Mayor centralidad funcional (Rondinelli)", "Valor": f"{lider_rond} ({score_rond:.2f})"},
            {"Indicador": "Menor índice de aislamiento", "Valor": f"{mejor_con} ({pct_aisl_min:.1f}%)"},
        ])
        df_portada = pd.concat([df_portada, filas_ot_portada], ignore_index=True)
    ws1 = wb.create_sheet("Resumen")
    _estilizar_hoja_excel(
        ws1,
        f"Resumen - {region_sel}",
        sub_general,
        df_portada,
    )

    # HOJAS 2 Y 3: BASE t0 Y BASE tf
    for anio_mat, df_mat in [(anio_0, V0), (anio_t, Vt)]:
        ws_m = wb.create_sheet(f"Base {anio_mat}")
        n_cols_m = n_comunas + 2
        ws_m.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_m)
        ct = ws_m.cell(row=1, column=1, value=f"Base {anio_mat} - {variable_sel}")
        ct.fill = fill_titulo
        ct.font = font_titulo
        ws_m.row_dimensions[1].height = 25

        ws_m.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_m)
        cs = ws_m.cell(row=2, column=1, value=sub_general)
        cs.font = font_sub

        headers_m = ["Rubro Económico SII"] + comunas + [f"Total Rubro {anio_mat}"]
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
        ct_lbl = ws_m.cell(row=fila_tot_m, column=1, value=f"Total comunal {anio_mat}")
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

        _autoajustar_columnas_hoja(ws_m)

    # HOJA 4: LOCALIZACIÓN Qij
    ws4 = wb.create_sheet("Localización Qij")
    n_cols_q = n_comunas + 1
    ws4.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_q)
    c4_t = ws4.cell(row=1, column=1, value=f"Cociente de localización (Qij) - {anio_0} y {anio_t}")
    c4_t.fill = fill_titulo
    c4_t.font = font_titulo
    ws4.row_dimensions[1].height = 24

    ws4.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_q)
    c4_s = ws4.cell(
        row=2,
        column=1,
        value="Valores resaltados (Qij > 1) indican especialización relativa respecto al promedio regional.",
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
        cb = ws4.cell(row=fila_cursor, column=1, value=f"Cociente de localización (Qij) - {etq_anio}")
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

    _autoajustar_columnas_hoja(ws4)

    # HOJA 5: ESPECIALIZACIÓN (Qr y CRr)
    ws5 = wb.create_sheet("Especialización")
    n_cols_e = n_comunas + 1
    ws5.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_e)
    c5_t = ws5.cell(
        row=1,
        column=1,
        value=f"Especialización (Qr) y reestructuración (CRr) - {anio_0} y {anio_t}",
    )
    c5_t.fill = fill_titulo
    c5_t.font = font_titulo
    ws5.row_dimensions[1].height = 26

    ws5.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_e)
    c5_s = ws5.cell(
        row=2,
        column=1,
        value="Diferencias absolutas |Pij - Pi| por rubro y comuna. Fuente: SII.",
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
            value=f"Diferencias absolutas |Pij - Pi| - {etq_anio}",
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

        c_qr_lbl = ws5.cell(row=fila_cur_5, column=1, value=f"Coeficiente de Especialización (Qr {etq_anio})")
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

    df_esp_res = resultados["df_especializacion"].copy()
    headers_esp_limpios = [
        "Comuna",
        f"Total {anio_0}",
        f"Total {anio_t}",
        f"Part. Regional {anio_0} (%)",
        f"Part. Regional {anio_t} (%)",
        f"Especialización Qr ({anio_0})",
        f"Especialización Qr ({anio_t})",
        "Reestructuración (CRr)",
        f"Base Exportadora Xj ({anio_t})",
        f"Prop. Básica {anio_t} (%)",
        f"Multiplicador Mj ({anio_t})",
    ]
    ws5.merge_cells(start_row=fila_cur_5, start_column=1, end_row=fila_cur_5, end_column=len(headers_esp_limpios))
    c_res_t = ws5.cell(
        row=fila_cur_5,
        column=1,
        value="Resumen por comuna (Qr, CRr, Base Exportadora Xj y Multiplicador Mj)",
    )
    c_res_t.fill = fill_subbloque
    c_res_t.font = font_subbloque
    fila_cur_5 += 1

    for c_i, col_name in enumerate(headers_esp_limpios, start=1):
        ch = ws5.cell(row=fila_cur_5, column=c_i, value=col_name)
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

    _autoajustar_columnas_hoja(ws5)

    # HOJA 6: PROD. BÁSICA (Xij y Mj)
    ws6 = wb.create_sheet("Prod. Básica")
    n_cols_x = n_comunas + 2
    ws6.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_x)
    c6_t = ws6.cell(
        row=1,
        column=1,
        value=f"Producción básica (Xij) y multiplicador básico (Mj) - {anio_t} y {anio_0}",
    )
    c6_t.fill = fill_titulo
    c6_t.font = font_titulo
    ws6.row_dimensions[1].height = 24

    ws6.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_x)
    c6_s = ws6.cell(
        row=2,
        column=1,
        value="Excedente resaltado (Xij > 0, rubros con Qij > 1) y multiplicador básico comunal (Mj = Vj / Xj).",
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
            value=f"Producción básica (Xij > 0) - {etq_anio}",
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

        f_vj = fila_cur_6
        c_vj_lbl = ws6.cell(row=f_vj, column=1, value=f"Vj - Total comunal ({etq_anio})")
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

        f_xj = fila_cur_6
        c_xj_lbl = ws6.cell(row=f_xj, column=1, value=f"Xj - Producción básica total ({etq_anio})")
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

        f_mj = fila_cur_6
        c_mj_lbl = ws6.cell(row=f_mj, column=1, value=f"Mj - Multiplicador básico Vj / Xj ({etq_anio})")
        c_mj_lbl.font = font_bold
        c_mj_lbl.fill = fill_ref
        c_mj_lbl.border = borde_total
        for c_i in range(2, n_comunas + 3):
            col_l = get_column_letter(c_i)
            cm = ws6.cell(row=f_mj, column=c_i, value=f"=IF({col_l}{f_xj}>0,{col_l}{f_vj}/{col_l}{f_xj},0)")
            cm.font = font_bold
            cm.fill = fill_ref
            cm.number_format = "0.0000"
            cm.border = borde_total

        fila_cur_6 += 3

    _autoajustar_columnas_hoja(ws6)

    # HOJA 7: CUADRANTES SILVA (FORMATO ESTÁNDAR CON POBLACIÓN Y PER CÁPITA)
    ws7 = wb.create_sheet("Cuadrantes Silva")
    T_per = max(int(anio_t) - int(anio_0), 1)
    df_ss = resultados["df_shift_share"]
    pob_comunas = _obtener_poblacion_comunas(list(df_ss["Comuna"]))
    usa_per_capita = pob_comunas is not None
    lbl_v0, lbl_vt, lbl_pc, fmt_v, fmt_pc = _etiquetas_variable_sii(variable_sel, anio_0, anio_t)

    ws7.merge_cells("A1:L1")
    c7_t = ws7.cell(
        row=1,
        column=1,
        value=f"Cuadrantes de Silva Lira - {region_sel} ({anio_0}-{anio_t})",
    )
    c7_t.fill = fill_titulo
    c7_t.font = font_titulo
    ws7.row_dimensions[1].height = 24

    ws7.merge_cells("A2:L2")
    sub_silva = (
        f"Variable: {variable_sel}. Fuente: SII y Censo 2024 (INE)"
        if usa_per_capita
        else f"Variable: {variable_sel}. Fuente: SII"
    )
    c7_s = ws7.cell(row=2, column=1, value=sub_silva)
    c7_s.font = font_sub
    ws7.row_dimensions[2].height = 19

    if usa_per_capita:
        headers_silva = [
            "Comuna",
            lbl_v0,
            lbl_vt,
            "Población (Censo 2024)",
            "Tasa prom. de crecimiento",
            lbl_pc,
            "Cuadrante Silva Lira",
        ]
    else:
        headers_silva = [
            "Comuna",
            lbl_v0,
            lbl_vt,
            "Variación absoluta",
            "Tasa prom. de crecimiento",
            f"Participación {anio_t} (%)",
            "Cuadrante Silva Lira",
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

    umbral_y = (
        ((tot["total_reg_t"] / tot["total_reg_0"]) ** (1.0 / T_per) - 1.0)
        if tot["total_reg_0"] > 0 and tot["total_reg_t"] > 0
        else 0.0
    )
    if usa_per_capita:
        total_pob_reg = float(sum(pob_comunas))
        umbral_x = tot["total_reg_t"] / max(total_pob_reg, 1.0)
    else:
        umbral_x = 1.0 / max(n_comunas, 1)

    xs_vals = []
    ys_vals = []
    com_q1, com_q2, com_q3, com_q4 = [], [], [], []

    for idx_offset, row_s in enumerate(df_ss.itertuples(index=False)):
        idx_r = fila_ini_7 + idx_offset
        com_nom = str(row_s.Comuna)
        v0_val = float(getattr(row_s, f"Nivel_{anio_0}"))
        vt_val = float(getattr(row_s, f"Nivel_{anio_t}"))
        tpa_dec = ((vt_val / v0_val) ** (1.0 / T_per) - 1.0) if v0_val > 0 and vt_val > 0 else 0.0

        if usa_per_capita:
            pob_i = int(pob_comunas[idx_offset])
            x_val = vt_val / max(float(pob_i), 1.0)
        else:
            x_val = (vt_val / max(tot["total_reg_t"], 1e-12)) if tot["total_reg_t"] > 0 else 0.0

        xs_vals.append(x_val)
        ys_vals.append(tpa_dec)

        alto_x = x_val >= umbral_x
        alto_y = tpa_dec >= umbral_y
        if alto_x and alto_y:
            com_q1.append(com_nom)
            fill_col_g = fill_cuad_1
            es_dinamica = True
        elif (not alto_x) and alto_y:
            com_q2.append(com_nom)
            fill_col_g = fill_cuad_2
            es_dinamica = False
        elif alto_x and (not alto_y):
            com_q3.append(com_nom)
            fill_col_g = fill_cuad_3
            es_dinamica = False
        else:
            com_q4.append(com_nom)
            fill_col_g = fill_cuad_4
            es_dinamica = False

        fill_row_datos = fill_fila_blanca if (idx_r % 2 == 1) else fill_fila_cebra

        c_com = ws7.cell(row=idx_r, column=1, value=com_nom)
        c_v0 = ws7.cell(row=idx_r, column=2, value=v0_val)
        c_vt = ws7.cell(row=idx_r, column=3, value=vt_val)
        if usa_per_capita:
            c_col4 = ws7.cell(row=idx_r, column=4, value=pob_i)
            c_col4.number_format = "#,##0"
            c_col6 = ws7.cell(row=idx_r, column=6, value=f"=IF(D{idx_r}>0,C{idx_r}/D{idx_r},0)")
            c_col6.number_format = fmt_pc
        else:
            c_col4 = ws7.cell(row=idx_r, column=4, value=f"=C{idx_r}-B{idx_r}")
            c_col4.number_format = fmt_v
            c_col6 = ws7.cell(row=idx_r, column=6, value=f"=IF($C${fila_tot_7}>0,C{idx_r}/$C${fila_tot_7},0)")
            c_col6.number_format = "0.00%"

        c_tpa = ws7.cell(row=idx_r, column=5, value=f"=IF(B{idx_r}>0,((C{idx_r}/B{idx_r})^(1/{T_per}))-1,0)")
        c_cua = ws7.cell(
            row=idx_r,
            column=7,
            value=(
                f'=IF(AND(F{idx_r}>=$F${fila_tot_7},E{idx_r}>=$E${fila_tot_7}),"I. Dinámica",'
                f'IF(AND(F{idx_r}<$F${fila_tot_7},E{idx_r}>=$E${fila_tot_7}),"II. Emergente",'
                f'IF(AND(F{idx_r}>=$F${fila_tot_7},E{idx_r}<$E${fila_tot_7}),"III. Estancada","IV. En retroceso")))'
            ),
        )

        # Coordenadas numéricas en columnas ocultas O (15) y P (16) para el ScatterChart
        c_x_num = ws7.cell(row=idx_r, column=15, value=float(x_val))
        c_y_num = ws7.cell(row=idx_r, column=16, value=float(tpa_dec))
        c_x_num.number_format = fmt_pc if usa_per_capita else "0.00%"
        c_y_num.number_format = "0.00%"

        c_v0.number_format = fmt_v
        c_vt.number_format = fmt_v
        c_tpa.number_format = "0.00%"

        for cell_item in (c_com, c_v0, c_vt, c_col4, c_tpa, c_col6):
            cell_item.fill = fill_row_datos
            cell_item.font = font_celda
            cell_item.border = borde_fino
        c_com.alignment = Alignment(horizontal="left", vertical="center")
        for cell_num in (c_v0, c_vt, c_col4, c_tpa, c_col6):
            cell_num.alignment = Alignment(horizontal="right", vertical="center")

        c_cua.fill = fill_col_g
        c_cua.font = font_bold if es_dinamica else font_celda
        c_cua.alignment = Alignment(horizontal="left", vertical="center")
        c_cua.border = borde_fino

    # Fila Suma total / Promedio regional
    ws7.cell(row=fila_tot_7, column=1, value="Suma total").alignment = Alignment(horizontal="left", vertical="center")
    ws7.cell(row=fila_tot_7, column=2, value=f"=SUM(B{fila_ini_7}:B{fila_tot_7-1})").number_format = fmt_v
    ws7.cell(row=fila_tot_7, column=3, value=f"=SUM(C{fila_ini_7}:C{fila_tot_7-1})").number_format = fmt_v
    if usa_per_capita:
        ws7.cell(row=fila_tot_7, column=4, value=f"=SUM(D{fila_ini_7}:D{fila_tot_7-1})").number_format = "#,##0"
        ws7.cell(row=fila_tot_7, column=6, value=f"=IF(D{fila_tot_7}>0,C{fila_tot_7}/D{fila_tot_7},0)").number_format = fmt_pc
    else:
        ws7.cell(row=fila_tot_7, column=4, value=f"=C{fila_tot_7}-B{fila_tot_7}").number_format = fmt_v
        ws7.cell(row=fila_tot_7, column=6, value=f"=AVERAGE(F{fila_ini_7}:F{fila_tot_7-1})").number_format = "0.00%"

    ws7.cell(row=fila_tot_7, column=5, value=f"=IF(B{fila_tot_7}>0,((C{fila_tot_7}/B{fila_tot_7})^(1/{T_per}))-1,0)").number_format = "0.00%"
    ws7.cell(row=fila_tot_7, column=7, value="Promedio regional").alignment = Alignment(horizontal="left", vertical="center")

    for c_i in range(1, 8):
        cell_tot = ws7.cell(row=fila_tot_7, column=c_i)
        cell_tot.fill = fill_gris_total
        cell_tot.font = font_bold
        cell_tot.border = borde_total
        if c_i in (2, 3, 4, 5, 6):
            cell_tot.alignment = Alignment(horizontal="right", vertical="center")

    # Coordenadas de lineas de corte para el grafico
    x_max_plot = max(max(xs_vals) * 1.12, umbral_x * 1.5, 0.05) if xs_vals else 100.0
    y_min_val = min(ys_vals + [umbral_y]) if ys_vals else -0.05
    y_max_val = max(ys_vals + [umbral_y]) if ys_vals else 0.10
    margen_y = max((y_max_val - y_min_val) * 0.15, 0.015)
    y_min_plot = y_min_val - margen_y
    y_max_plot = y_max_val + margen_y

    ws7.cell(row=5, column=17, value=float(umbral_x))
    ws7.cell(row=5, column=18, value=float(y_min_plot))
    ws7.cell(row=6, column=17, value=float(umbral_x))
    ws7.cell(row=6, column=18, value=float(y_max_plot))

    ws7.cell(row=7, column=17, value=0.0)
    ws7.cell(row=7, column=18, value=float(umbral_y))
    ws7.cell(row=8, column=17, value=float(x_max_plot))
    ws7.cell(row=8, column=18, value=float(umbral_y))

    for col_oculta in ("O", "P", "Q", "R"):
        ws7.column_dimensions[col_oculta].hidden = True

    # Gráfico de dispersión en I4 leyendo columnas ocultas O:R
    chart_silva = ScatterChart()
    chart_silva.visible_cells_only = False
    chart_silva.title = f"Cuadrantes de Silva Lira ({region_sel}, {anio_0}-{anio_t})"
    chart_silva.style = 2
    chart_silva.legend = None
    chart_silva.x_axis.title = lbl_pc if usa_per_capita else f"Participación Comunal {anio_t} (%)"
    chart_silva.y_axis.title = f"Tasa promedio anual de crecimiento ({anio_0}-{anio_t})"
    chart_silva.x_axis.number_format = fmt_pc if usa_per_capita else "0.0%"
    chart_silva.y_axis.number_format = "0.0%"
    chart_silva.x_axis.tickLblPos = "low"
    chart_silva.y_axis.tickLblPos = "low"
    chart_silva.x_axis.scaling.min = 0.0
    chart_silva.x_axis.scaling.max = float(x_max_plot)
    chart_silva.y_axis.scaling.min = float(y_min_plot)
    chart_silva.y_axis.scaling.max = float(y_max_plot)
    chart_silva.width = 25
    chart_silva.height = 15.5

    for idx_r in range(fila_ini_7, fila_tot_7):
        nom_comuna = str(ws7.cell(row=idx_r, column=1).value)
        x_ref = Reference(ws7, min_col=15, min_row=idx_r, max_row=idx_r)
        y_ref = Reference(ws7, min_col=16, min_row=idx_r, max_row=idx_r)
        s_com = Series(y_ref, x_ref, title=nom_comuna)
        s_com.marker.symbol = "circle"
        s_com.marker.size = 7
        s_com.marker.graphicalProperties.solidFill = "4472C4"
        s_com.marker.graphicalProperties.line.solidFill = "2F5597"
        s_com.graphicalProperties.line.noFill = True

        s_com.dLbls = DataLabelList()
        s_com.dLbls.showSerName = True
        s_com.dLbls.showVal = False
        s_com.dLbls.showCatName = False
        s_com.dLbls.showLegendKey = False
        chart_silva.series.append(s_com)

    xv_ref = Reference(ws7, min_col=17, min_row=5, max_row=6)
    yv_ref = Reference(ws7, min_col=18, min_row=5, max_row=6)
    s_linea_v = Series(yv_ref, xv_ref, title="Promedio Regional X")
    s_linea_v.marker.symbol = "none"
    s_linea_v.graphicalProperties.line.solidFill = "C00000"
    s_linea_v.graphicalProperties.line.width = 22000

    xh_ref = Reference(ws7, min_col=17, min_row=7, max_row=8)
    yh_ref = Reference(ws7, min_col=18, min_row=7, max_row=8)
    s_linea_h = Series(yh_ref, xh_ref, title="Promedio Regional Y")
    s_linea_h.marker.symbol = "none"
    s_linea_h.graphicalProperties.line.solidFill = "C00000"
    s_linea_h.graphicalProperties.line.width = 22000

    chart_silva.series.append(s_linea_v)
    chart_silva.series.append(s_linea_h)
    ws7.add_chart(chart_silva, "I4")

    # Matriz 2x2 debajo del gráfico (I35:L46)
    com_q1, com_q2, com_q3, com_q4 = sorted(com_q1), sorted(com_q2), sorted(com_q3), sorted(com_q4)
    if usa_per_capita:
        txt_x_bajo = f"BAJO NIVEL PER CÁPITA (< {umbral_x:,.1f})" if umbral_x >= 10 else f"BAJO NIVEL PER CÁPITA (< {umbral_x:.3f})"
        txt_x_alto = f"ALTO NIVEL PER CÁPITA (>= {umbral_x:,.1f})" if umbral_x >= 10 else f"ALTO NIVEL PER CÁPITA (>= {umbral_x:.3f})"
        eje_x_lbl = "Nivel per cápita (X)"
    else:
        txt_x_bajo = "BAJA PARTICIPACIÓN (< Prom. comunal)"
        txt_x_alto = "ALTA PARTICIPACIÓN (>= Prom. comunal)"
        eje_x_lbl = "Participación (X)"

    f_m2 = 35
    ws7.merge_cells(start_row=f_m2, start_column=9, end_row=f_m2, end_column=12)
    c_m2_tit = ws7.cell(row=f_m2, column=9, value="Clasificación Silva Lira (2x2)")
    c_m2_tit.fill = fill_titulo
    c_m2_tit.font = font_header
    c_m2_tit.alignment = Alignment(horizontal="center", vertical="center")

    ws7.cell(row=f_m2 + 1, column=9, value=f"Crecimiento (Y) \\ {eje_x_lbl}").fill = fill_header
    ws7.cell(row=f_m2 + 1, column=9).font = font_header
    ws7.cell(row=f_m2 + 1, column=9).alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws7.merge_cells(start_row=f_m2 + 1, start_column=10, end_row=f_m2 + 1, end_column=11)
    c_x_bajo = ws7.cell(row=f_m2 + 1, column=10, value=txt_x_bajo)
    c_x_bajo.fill = fill_header
    c_x_bajo.font = font_header
    c_x_bajo.alignment = Alignment(horizontal="center", vertical="center")

    c_x_alto = ws7.cell(row=f_m2 + 1, column=12, value=txt_x_alto)
    c_x_alto.fill = fill_header
    c_x_alto.font = font_header
    c_x_alto.alignment = Alignment(horizontal="center", vertical="center")

    ws7.merge_cells(start_row=f_m2 + 2, start_column=9, end_row=f_m2 + 6, end_column=9)
    c_y_alto = ws7.cell(
        row=f_m2 + 2,
        column=9,
        value=f"ALTO DINAMISMO\nCrec. anual >= {umbral_y * 100:.2f}%",
    )
    c_y_alto.fill = fill_subbloque
    c_y_alto.font = font_bold
    c_y_alto.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws7.merge_cells(start_row=f_m2 + 2, start_column=10, end_row=f_m2 + 6, end_column=11)
    txt_q2 = (
        f"CUADRANTE II: EMERGENTES ({len(com_q2)} comunas)\n\n"
        + (", ".join(com_q2) if com_q2 else "Sin comunas en este cuadrante")
    )
    c_box_q2 = ws7.cell(row=f_m2 + 2, column=10, value=txt_q2)
    c_box_q2.fill = fill_cuad_2
    c_box_q2.font = font_celda
    c_box_q2.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    ws7.merge_cells(start_row=f_m2 + 2, start_column=12, end_row=f_m2 + 6, end_column=12)
    txt_q1 = (
        f"CUADRANTE I: DINÁMICAS ({len(com_q1)} comunas)\n\n"
        + (", ".join(com_q1) if com_q1 else "Sin comunas en este cuadrante")
    )
    c_box_q1 = ws7.cell(row=f_m2 + 2, column=12, value=txt_q1)
    c_box_q1.fill = fill_cuad_1
    c_box_q1.font = font_celda
    c_box_q1.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    ws7.merge_cells(start_row=f_m2 + 7, start_column=9, end_row=f_m2 + 11, end_column=9)
    c_y_bajo = ws7.cell(
        row=f_m2 + 7,
        column=9,
        value=f"BAJO DINAMISMO\nCrec. anual < {umbral_y * 100:.2f}%",
    )
    c_y_bajo.fill = fill_subbloque
    c_y_bajo.font = font_bold
    c_y_bajo.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws7.merge_cells(start_row=f_m2 + 7, start_column=10, end_row=f_m2 + 11, end_column=11)
    txt_q4 = (
        f"CUADRANTE IV: EN RETROCESO ({len(com_q4)} comunas)\n\n"
        + (", ".join(com_q4) if com_q4 else "Sin comunas en este cuadrante")
    )
    c_box_q4 = ws7.cell(row=f_m2 + 7, column=10, value=txt_q4)
    c_box_q4.fill = fill_cuad_4
    c_box_q4.font = font_celda
    c_box_q4.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    ws7.merge_cells(start_row=f_m2 + 7, start_column=12, end_row=f_m2 + 11, end_column=12)
    txt_q3 = (
        f"CUADRANTE III: ESTANCADAS ({len(com_q3)} comunas)\n\n"
        + (", ".join(com_q3) if com_q3 else "Sin comunas en este cuadrante")
    )
    c_box_q3 = ws7.cell(row=f_m2 + 7, column=12, value=txt_q3)
    c_box_q3.font = font_celda
    c_box_q3.fill = fill_cuad_3
    c_box_q3.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)

    for r_box in range(f_m2, f_m2 + 12):
        ws7.row_dimensions[r_box].height = 24
        for c_box in range(9, 13):
            ws7.cell(row=r_box, column=c_box).border = borde_fino

    _autoajustar_columnas_hoja(ws7, max_width=24, min_width=13, col_a_max=30)
    ws7.column_dimensions["G"].width = 20
    ws7.column_dimensions["H"].width = 3
    ws7.column_dimensions["I"].width = 23
    ws7.column_dimensions["J"].width = 21
    ws7.column_dimensions["K"].width = 21
    ws7.column_dimensions["L"].width = 36

    # HOJA 8: MADE (SHIFT & SHARE CLÁSICO)
    ws8 = wb.create_sheet("MADE")
    n_cols_ss = n_comunas + 1
    ws8.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_ss)
    c8_t = ws8.cell(
        row=1,
        column=1,
        value=f"MADE clásico ({anio_0}-{anio_t})",
    )
    c8_t.fill = fill_titulo
    c8_t.font = font_titulo
    ws8.row_dimensions[1].height = 26

    ws8.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_ss)
    c8_s = ws8.cell(row=2, column=1, value=sub_general)
    c8_s.font = font_sub

    f_cur_8 = 4
    ws8.cell(row=f_cur_8, column=1, value="Comuna").fill = fill_header
    ws8.cell(row=f_cur_8, column=1).font = font_header
    for c_i, com in enumerate(comunas, start=2):
        ch = ws8.cell(row=f_cur_8, column=c_i, value=com)
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center")
        ch.border = borde_fino
    f_cur_8 += 1

    f_et_top = f_cur_8
    c_et_lbl = ws8.cell(row=f_et_top, column=1, value="EFECTO TOTAL")
    c_et_lbl.font = font_bold
    c_et_lbl.fill = fill_subbloque
    c_et_lbl.border = borde_total
    et_vals = resultados["df_shift_share"].set_index("Comuna")["Efecto_Total_ET"]
    for c_i, com in enumerate(comunas, start=2):
        cet = ws8.cell(row=f_et_top, column=c_i, value=float(et_vals[com]))
        cet.font = font_bold
        cet.fill = fill_subbloque
        cet.number_format = "#,##0.00"
        cet.border = borde_total
    f_cur_8 += 2

    ws8.merge_cells(start_row=f_cur_8, start_column=1, end_row=f_cur_8, end_column=n_cols_ss)
    cb_ed = ws8.cell(row=f_cur_8, column=1, value=f"Efecto Diferencial ({anio_0}-{anio_t})")
    cb_ed.fill = fill_subbloque
    cb_ed.font = font_subbloque
    f_cur_8 += 1

    ws8.cell(row=f_cur_8, column=1, value="Rubro Económico").fill = fill_header
    ws8.cell(row=f_cur_8, column=1).font = font_header
    for c_i, com in enumerate(comunas, start=2):
        ch = ws8.cell(row=f_cur_8, column=c_i, value=com)
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center")
        ch.border = borde_fino
    f_cur_8 += 1

    f_ini_ed = f_cur_8
    for rubro in rubros:
        cr = ws8.cell(row=f_cur_8, column=1, value=rubro)
        cr.font = font_celda
        cr.border = borde_fino
        for c_i, com in enumerate(comunas, start=2):
            cc = ws8.cell(row=f_cur_8, column=c_i, value=float(ED_mat.loc[rubro, com]))
            cc.font = font_celda
            cc.number_format = "#,##0.00"
            cc.border = borde_fino
        f_cur_8 += 1
    f_fin_ed = f_cur_8 - 1

    f_sum_ed = f_cur_8
    c_ed_lbl = ws8.cell(row=f_sum_ed, column=1, value="Efecto Diferencial")
    c_ed_lbl.font = font_bold
    c_ed_lbl.fill = fill_gris_total
    c_ed_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        csum = ws8.cell(row=f_sum_ed, column=c_i, value=f"=SUM({col_l}{f_ini_ed}:{col_l}{f_fin_ed})")
        csum.font = font_bold
        csum.fill = fill_gris_total
        csum.number_format = "#,##0.00"
        csum.border = borde_total
    f_cur_8 += 3

    ws8.merge_cells(start_row=f_cur_8, start_column=1, end_row=f_cur_8, end_column=n_cols_ss)
    cb_ee = ws8.cell(row=f_cur_8, column=1, value=f"Efecto Estructural ({anio_0}-{anio_t})")
    cb_ee.fill = fill_subbloque
    cb_ee.font = font_subbloque
    f_cur_8 += 1

    ws8.cell(row=f_cur_8, column=1, value="Rubro Económico").fill = fill_header
    ws8.cell(row=f_cur_8, column=1).font = font_header
    for c_i, com in enumerate(comunas, start=2):
        ch = ws8.cell(row=f_cur_8, column=c_i, value=com)
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center")
        ch.border = borde_fino
    f_cur_8 += 1

    f_ini_ee = f_cur_8
    for rubro in rubros:
        cr = ws8.cell(row=f_cur_8, column=1, value=rubro)
        cr.font = font_celda
        cr.border = borde_fino
        for c_i, com in enumerate(comunas, start=2):
            cc = ws8.cell(row=f_cur_8, column=c_i, value=float(EE_mat.loc[rubro, com]))
            cc.font = font_celda
            cc.number_format = "#,##0.00"
            cc.border = borde_fino
        f_cur_8 += 1
    f_fin_ee = f_cur_8 - 1

    f_sum_ee = f_cur_8
    c_ee_lbl = ws8.cell(row=f_sum_ee, column=1, value="Efecto Estructural")
    c_ee_lbl.font = font_bold
    c_ee_lbl.fill = fill_gris_total
    c_ee_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        csum = ws8.cell(row=f_sum_ee, column=c_i, value=f"=SUM({col_l}{f_ini_ee}:{col_l}{f_fin_ee})")
        csum.font = font_bold
        csum.fill = fill_gris_total
        csum.number_format = "#,##0.00"
        csum.border = borde_total
    f_cur_8 += 2

    f_chk_et = f_cur_8
    c_chk_lbl = ws8.cell(row=f_chk_et, column=1, value="Comprobación (ET = ED + EE)")
    c_chk_lbl.font = font_bold
    c_chk_lbl.fill = fill_ref
    c_chk_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        cchk = ws8.cell(row=f_chk_et, column=c_i, value=f"={col_l}{f_sum_ed}+{col_l}{f_sum_ee}")
        cchk.font = font_bold
        cchk.fill = fill_ref
        cchk.number_format = "#,##0.00"
        cchk.border = borde_total

    _autoajustar_columnas_hoja(ws8)

    # HOJA 9: MADE MODIFICADO
    ws9 = wb.create_sheet("MADE Modificado")
    ws9.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_ss)
    c9_t = ws9.cell(
        row=1,
        column=1,
        value=f"MADE modificado ({anio_0}-{anio_t})",
    )
    c9_t.fill = fill_titulo
    c9_t.font = font_titulo
    ws9.row_dimensions[1].height = 26

    ws9.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_ss)
    c9_s = ws9.cell(row=2, column=1, value=sub_general)
    c9_s.font = font_sub

    f_cur_9 = 4
    ws9.cell(row=f_cur_9, column=1, value="Rubro Económico").fill = fill_header
    ws9.cell(row=f_cur_9, column=1).font = font_header
    for c_i, com in enumerate(comunas, start=2):
        ch = ws9.cell(row=f_cur_9, column=c_i, value=com)
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center")
        ch.border = borde_fino
    f_cur_9 += 1

    f_ini_ee9 = f_cur_9
    for rubro in rubros:
        cr = ws9.cell(row=f_cur_9, column=1, value=rubro)
        cr.font = font_celda
        cr.border = borde_fino
        for c_i, com in enumerate(comunas, start=2):
            cc = ws9.cell(row=f_cur_9, column=c_i, value=float(EE_mat.loc[rubro, com]))
            cc.font = font_celda
            cc.number_format = "#,##0.00"
            cc.border = borde_fino
        f_cur_9 += 1
    f_fin_ee9 = f_cur_9 - 1

    f_sum_ee9 = f_cur_9
    c_ee9_lbl = ws9.cell(row=f_sum_ee9, column=1, value="Efecto Estructural")
    c_ee9_lbl.font = font_bold
    c_ee9_lbl.fill = fill_made_mod
    c_ee9_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        csum = ws9.cell(row=f_sum_ee9, column=c_i, value=f"=SUM({col_l}{f_ini_ee9}:{col_l}{f_fin_ee9})")
        csum.font = font_bold
        csum.fill = fill_made_mod
        csum.number_format = "#,##0.00"
        csum.border = borde_total
    f_cur_9 += 3

    ws9.cell(row=f_cur_9, column=1, value="Rubro Económico").fill = fill_header
    ws9.cell(row=f_cur_9, column=1).font = font_header
    for c_i, com in enumerate(comunas, start=2):
        ch = ws9.cell(row=f_cur_9, column=c_i, value=com)
        ch.fill = fill_header
        ch.font = font_header
        ch.alignment = Alignment(horizontal="center", vertical="center")
        ch.border = borde_fino
    f_cur_9 += 1

    f_ini_ei9 = f_cur_9
    for rubro in rubros:
        cr = ws9.cell(row=f_cur_9, column=1, value=rubro)
        cr.font = font_celda
        cr.border = borde_fino
        for c_i, com in enumerate(comunas, start=2):
            cc = ws9.cell(row=f_cur_9, column=c_i, value=float(EI_mat.loc[rubro, com]))
            cc.font = font_celda
            cc.number_format = "#,##0.00"
            cc.border = borde_fino
        f_cur_9 += 1
    f_fin_ei9 = f_cur_9 - 1

    f_sum_ei9 = f_cur_9
    c_ei9_lbl = ws9.cell(row=f_sum_ei9, column=1, value="Efecto Inverso")
    c_ei9_lbl.font = font_bold
    c_ei9_lbl.fill = fill_made_mod
    c_ei9_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        csum = ws9.cell(row=f_sum_ei9, column=c_i, value=f"=SUM({col_l}{f_ini_ei9}:{col_l}{f_fin_ei9})")
        csum.font = font_bold
        csum.fill = fill_made_mod
        csum.number_format = "#,##0.00"
        csum.border = borde_total
    f_cur_9 += 2

    f_em9 = f_cur_9
    c_em9_lbl = ws9.cell(row=f_em9, column=1, value="Efecto Modificado")
    c_em9_lbl.font = font_bold
    c_em9_lbl.fill = fill_gris_total
    c_em9_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        cem = ws9.cell(row=f_em9, column=c_i, value=f"={col_l}{f_sum_ei9}-{col_l}{f_sum_ee9}")
        cem.font = font_bold
        cem.fill = fill_gris_total
        cem.number_format = "#,##0.00"
        cem.border = borde_total
    f_cur_9 += 2

    f_erm9 = f_cur_9
    c_erm9_lbl = ws9.cell(row=f_erm9, column=1, value="Efecto Comunal Modificado")
    c_erm9_lbl.font = font_bold
    c_erm9_lbl.fill = fill_ref
    c_erm9_lbl.border = borde_total
    for c_i in range(2, n_cols_ss + 1):
        col_l = get_column_letter(c_i)
        cerm = ws9.cell(
            row=f_erm9,
            column=c_i,
            value=f"='MADE'!{col_l}{f_et_top}-{col_l}{f_sum_ei9}",
        )
        cerm.font = font_bold
        cerm.fill = fill_ref
        cerm.number_format = "#,##0.00"
        cerm.border = borde_total

    _autoajustar_columnas_hoja(ws9)

    # HOJA 10: CONVERGENCIA
    ws10 = wb.create_sheet("Convergencia")
    df_reat_excel = resultados["df_reat_resumen"].copy()
    df_reat_excel.columns = ["Indicador", f"Año {anio_0}", f"Año {anio_t}", "Variación", "Interpretación"]
    _estilizar_hoja_excel(
        ws10,
        f"Disparidades y convergencia regional (alpha = {alpha_hk})",
        sub_general,
        df_reat_excel,
    )

    if (incluir_ot or incluir_u6) and datos_ot_act is not None:
        estilos_ot = {
            "fill_titulo": fill_titulo,
            "fill_header": fill_header,
            "fill_subbloque": fill_subbloque,
            "fill_gris_total": fill_gris_total,
            "fill_made_mod": fill_made_mod,
            "fill_fila_blanca": fill_fila_blanca,
            "fill_fila_cebra": fill_fila_cebra,
            "font_titulo": font_titulo,
            "font_sub": font_sub,
            "font_header": font_header,
            "font_subbloque": font_subbloque,
            "font_bold": font_bold,
            "font_celda": font_celda,
            "borde_fino": borde_fino,
            "borde_total": borde_total,
        }
        _agregar_hojas_ot_y_u6(
            wb=wb,
            resultados=resultados,
            region_sel=region_sel,
            variable_sel=variable_sel,
            anio_0=anio_0,
            anio_t=anio_t,
            datos_ot=datos_ot_act,
            estilos=estilos_ot,
            incluir_ot=incluir_ot,
            incluir_u6=incluir_u6,
        )

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


compilar_excel_14_hojas = compilar_excel_10_hojas


def _estilizar_qij_streamlit(df_q: pd.DataFrame):
    """Destaca con relleno rojo claro de Excel las celdas con Qij > 1."""
    fn_color = (
        lambda v: "background-color: #FFC7CE; color: #9C0006; font-weight: bold;"
        if isinstance(v, (int, float, np.number)) and v > 1.0
        else ""
    )
    styler = df_q.style.format("{:.4f}")
    if hasattr(styler, "map"):
        return styler.map(fn_color)
    return styler.applymap(fn_color)


def renderizar_exportador_sii(ruta_excel_default: str = ARCHIVO_DEFAULT_REPO):
    """
    Interfaz interactiva en Streamlit para explorar la base del SII, ejecutar
    el motor econométrico completo y descargar el libro Excel de 10 hojas.
    """
    st.subheader("Análisis Regional SII (ILPES, MADE y REAT)")
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

    c_ot_cfg1, c_ot_cfg2, c_ot_cfg3 = st.columns([1.25, 1.15, 1.8])
    with c_ot_cfg1:
        incluir_ot_excel = st.checkbox(
            "Incluir Ordenamiento Territorial (+3 hojas)",
            value=True,
            key="chk_incluir_ot_sii",
        )
    with c_ot_cfg2:
        incluir_u6_excel = st.checkbox(
            "Incluir Índice Mín-Máx U6 (+1 hoja)",
            value=False,
            key="chk_incluir_u6_sii",
        )
    with c_ot_cfg3:
        dim_ot_sel = st.selectbox(
            "Dimensión Rondinelli / Guttman:",
            options=DIMENSIONES_GUTTMAN_OT,
            index=0,
            disabled=not (incluir_ot_excel or incluir_u6_excel),
            key="sel_dim_ot_sii",
        )

    datos_ot_base = construir_datos_ot_region(region_sel, resultados, dimension_ot=dim_ot_sel)
    reg_slug = _normalizar_texto(region_sel).replace(" ", "_")
    dim_slug = str(DIMENSIONES_GUTTMAN_OT.index(dim_ot_sel) + 1)
    key_gutt_ss = f"ot_gutt_edit_{reg_slug}_{dim_slug}"
    key_aisl_ss = f"ot_aisl_edit_all_{reg_slug}"

    datos_ot_export = dict(datos_ot_base)
    if key_gutt_ss in st.session_state:
        datos_ot_export["df_guttman"] = st.session_state[key_gutt_ss]
    if key_aisl_ss in st.session_state:
        datos_ot_export["df_aislamiento"] = st.session_state[key_aisl_ss]

    slot_descarga_superior = st.empty()

    tabs = st.tabs([
        "1. Matrices y Localización (Qij)",
        "2. Especialización y Base Exportable",
        "3. Shift & Share (MADE Clásico y Mod.)",
        "4. Cuadrantes de Silva Lira",
        "5. Convergencia y Desigualdad (REAT)",
        "6. Ordenamiento Territorial (OT) y U6",
    ])

    with tabs[0]:
        st.markdown(f"**Cociente de Localización ($Q_{{ij}}$) - Año {anio_t}**")
        fig_q = px.imshow(
            resultados["Q_ij_t"],
            aspect="auto",
            color_continuous_scale="RdBu_r",
            origin="upper",
            labels={"x": "Comuna", "y": "Rubro Económico SII", "color": "Q_ij"},
        )
        fig_q.update_layout(height=520, margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_q, use_container_width=True)
        st.dataframe(_estilizar_qij_streamlit(resultados["Q_ij_t"]), use_container_width=True)

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
        T_per = max(int(anio_t) - int(anio_0), 1)
        pob_st = _obtener_poblacion_comunas(list(df_ss["Comuna"]))
        lbl_v0, lbl_vt, lbl_pc, _, _ = _etiquetas_variable_sii(variable_sel, anio_0, anio_t)

        v0_arr = df_ss[f"Nivel_{anio_0}"].values.astype(float)
        vt_arr = df_ss[f"Nivel_{anio_t}"].values.astype(float)
        tpa_pct = np.where((v0_arr > 0) & (vt_arr > 0), ((vt_arr / v0_arr) ** (1.0 / T_per) - 1.0) * 100.0, 0.0)
        tpa_reg_pct = (
            ((tot["total_reg_t"] / tot["total_reg_0"]) ** (1.0 / T_per) - 1.0) * 100.0
            if tot["total_reg_0"] > 0 and tot["total_reg_t"] > 0
            else 0.0
        )

        if pob_st is not None:
            pob_arr = np.array(pob_st, dtype=float)
            pc_arr = vt_arr / np.maximum(pob_arr, 1.0)
            umbral_x_st = tot["total_reg_t"] / max(float(np.sum(pob_arr)), 1.0)
            cuads_st = [
                "I. Dinámica" if (pc_arr[i] >= umbral_x_st and tpa_pct[i] >= tpa_reg_pct)
                else ("II. Emergente" if (pc_arr[i] < umbral_x_st and tpa_pct[i] >= tpa_reg_pct)
                else ("III. Estancada" if (pc_arr[i] >= umbral_x_st and tpa_pct[i] < tpa_reg_pct)
                else "IV. En retroceso"))
                for i in range(len(df_ss))
            ]
            df_silva_st = pd.DataFrame({
                "Comuna": df_ss["Comuna"].values,
                lbl_v0: v0_arr,
                lbl_vt: vt_arr,
                "Población (Censo 2024)": pob_st,
                "Tasa prom. de crecimiento (%)": tpa_pct,
                lbl_pc: pc_arr,
                "Cuadrante Silva Lira": cuads_st,
            })
            x_col_st, x_label_st, vline_txt = lbl_pc, lbl_pc, f"Promedio Regional ({umbral_x_st:,.1f})"
        else:
            part_arr = (vt_arr / max(tot["total_reg_t"], 1e-9)) * 100.0
            umbral_x_st = 100.0 / max(tot["n_comunas"], 1)
            cuads_st = [
                "I. Dinámica" if (part_arr[i] >= umbral_x_st and tpa_pct[i] >= tpa_reg_pct)
                else ("II. Emergente" if (part_arr[i] < umbral_x_st and tpa_pct[i] >= tpa_reg_pct)
                else ("III. Estancada" if (part_arr[i] >= umbral_x_st and tpa_pct[i] < tpa_reg_pct)
                else "IV. En retroceso"))
                for i in range(len(df_ss))
            ]
            df_silva_st = pd.DataFrame({
                "Comuna": df_ss["Comuna"].values,
                lbl_v0: v0_arr,
                lbl_vt: vt_arr,
                "Tasa prom. de crecimiento (%)": tpa_pct,
                f"Participación {anio_t} (%)": part_arr,
                "Cuadrante Silva Lira": cuads_st,
            })
            x_col_st = f"Participación {anio_t} (%)"
            x_label_st = x_col_st
            vline_txt = f"Participación Media ({umbral_x_st:.2f}%)"

        fig_silva = px.scatter(
            df_silva_st,
            x=x_col_st,
            y="Tasa prom. de crecimiento (%)",
            color="Cuadrante Silva Lira",
            hover_name="Comuna",
            text="Comuna",
            labels={
                x_col_st: x_label_st,
                "Tasa prom. de crecimiento (%)": f"Tasa promedio anual {anio_0}-{anio_t} (%)",
            },
            title=f"Cuadrantes de Silva Lira ({region_sel}, {anio_0}-{anio_t})",
        )
        fig_silva.update_traces(textposition="top center")
        fig_silva.add_hline(
            y=tpa_reg_pct,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Crecimiento Regional ({tpa_reg_pct:.2f}%)",
        )
        fig_silva.add_vline(
            x=umbral_x_st,
            line_dash="dash",
            line_color="navy",
            annotation_text=vline_txt,
        )
        st.plotly_chart(fig_silva, use_container_width=True)
        st.dataframe(df_silva_st.round(2), use_container_width=True, hide_index=True)

        c_q1 = ", ".join(sorted(df_silva_st[df_silva_st["Cuadrante Silva Lira"] == "I. Dinámica"]["Comuna"].tolist())) or "Ninguna"
        c_q2 = ", ".join(sorted(df_silva_st[df_silva_st["Cuadrante Silva Lira"] == "II. Emergente"]["Comuna"].tolist())) or "Ninguna"
        c_q3 = ", ".join(sorted(df_silva_st[df_silva_st["Cuadrante Silva Lira"] == "III. Estancada"]["Comuna"].tolist())) or "Ninguna"
        c_q4 = ", ".join(sorted(df_silva_st[df_silva_st["Cuadrante Silva Lira"] == "IV. En retroceso"]["Comuna"].tolist())) or "Ninguna"

        st.markdown("**Clasificación de Silva Lira (2x2)**")
        df_mat_2x2 = pd.DataFrame({
            "Dinámica de Crecimiento": [
                f"Crecimiento anual >= Promedio Regional ({tpa_reg_pct:.2f}%)",
                f"Crecimiento anual < Promedio Regional ({tpa_reg_pct:.2f}%)",
            ],
            f"Bajo {x_label_st}": [
                f"II. Emergentes: {c_q2}",
                f"IV. En retroceso: {c_q4}",
            ],
            f"Alto {x_label_st}": [
                f"I. Dinámicas: {c_q1}",
                f"III. Estancadas: {c_q3}",
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


    with tabs[5]:
        st.markdown(f"**Ordenamiento Territorial (OT) - {region_sel}**")
        if not datos_ot_base["es_base_censo_oficial"]:
            st.caption(
                "Región sin tabla censal precargada; se muestra una referencia editable desde las comunas activas del SII."
            )

        ot_m1, ot_m2, ot_m3, ot_m4 = st.columns(4)
        ot_m1.metric("Índice Primacía IP4 (2024)", f"{datos_ot_base['ip4_24']:.3f}", f"IP2 = {datos_ot_base['ip2_24']:.3f}")
        ot_m2.metric("Clasificación Primacía", datos_ot_base["cat_ip4"], f"Valor: {datos_ot_base['cod_ip4']}")
        ot_m3.metric("Comunas en Ranking", f"{len(datos_ot_base['df_censo'])}", "Top 10 en Rondinelli")
        ot_m4.metric("Dimensión Rondinelli", dim_ot_sel.split(".", 1)[1].strip()[:26], "8 variables (1/0)")

        sub_ot1, sub_ot2, sub_ot3 = st.tabs([
            "A. Primacía y Ranking con Flechas",
            "B. Guttman / Rondinelli Editable + Gráfico",
            "C. Aislamiento Editable e Índice Mín-Máx",
        ])

        with sub_ot1:
            df_c_vis = datos_ot_base["df_censo"].copy()
            df_c_vis["Ranking_2017"] = df_c_vis["Censo_2017"].rank(ascending=False, method="min").astype(int)
            df_c_vis["Ranking_2024"] = df_c_vis["Censo_2024"].rank(ascending=False, method="min").astype(int)
            df_c_vis["Cambio"] = df_c_vis["Ranking_2017"] - df_c_vis["Ranking_2024"]
            df_c_vis["Tendencia"] = np.where(
                df_c_vis["Cambio"] > 0, "Sube",
                np.where(df_c_vis["Cambio"] < 0, "Baja", "Igual")
            )
            df_c_vis["Variacion_%"] = ((df_c_vis["Censo_2024"] / df_c_vis["Censo_2017"].replace(0, np.nan)) - 1.0).fillna(0.0) * 100.0

            c_rk1, c_rk2 = st.columns([1.3, 1.0])
            with c_rk1:
                st.dataframe(df_c_vis.round(2), use_container_width=True, hide_index=True)
            with c_rk2:
                df_top_rk = df_c_vis.head(min(10, len(df_c_vis)))
                fig_cruce = go.Figure()
                for _, r_k in df_top_rk.iterrows():
                    fig_cruce.add_trace(
                        go.Scatter(
                            x=["Censo 2017", "Censo 2024"],
                            y=[int(r_k["Ranking_2017"]), int(r_k["Ranking_2024"])],
                            mode="lines+markers+text",
                            text=["", f" {r_k['Comuna']}"],
                            textposition="middle right",
                            name=str(r_k["Comuna"]),
                            showlegend=False,
                        )
                    )
                fig_cruce.update_yaxes(autorange="reversed", dtick=1, title="Posición Ranking")
                fig_cruce.update_layout(
                    title="Cruce de Ranking Top 10 (2017 a 2024)",
                    height=430,
                    margin=dict(l=20, r=120, t=40, b=20),
                )
                st.plotly_chart(fig_cruce, use_container_width=True)

        with sub_ot2:
            st.caption(
                "Edita cualquier `1` (presente) o `0` (ausente) en el Top 10 comunal antes de exportar. "
                "La alerta de discriminación solo aparece aquí en pantalla y no se imprime en el Excel final."
            )
            df_gutt_edit = st.data_editor(
                datos_ot_export["df_guttman"],
                use_container_width=True,
                key=f"editor_gutt_sii_{reg_slug}_{dim_slug}",
            )
            st.session_state[key_gutt_ss] = df_gutt_edit
            datos_ot_export["df_guttman"] = df_gutt_edit

            df_rond_vis, _, _, _, cols_mal = calcular_rondinelli_df(df_gutt_edit, datos_ot_base["df_censo"])
            if cols_mal:
                st.warning(
                    "Variables sin diferenciación (tienen puros 1 o puros 0; conviene ajustarlas antes de descargar): "
                    f"**{', '.join(cols_mal)}**."
                )
            else:
                st.success("Todas las variables discriminan correctamente entre las comunas.")

            cg_r1, cg_r2 = st.columns([1.15, 1.35])
            with cg_r1:
                st.dataframe(df_rond_vis.round(2), use_container_width=True, hide_index=True)
            with cg_r2:
                fig_rond_st = px.scatter(
                    df_rond_vis,
                    x="Poblacion_2024",
                    y="Indice_Rondinelli",
                    text="Comuna",
                    size="Total_Funciones",
                    title=f"Complejidad Funcional vs. Población (Censo 2024) - {region_sel}",
                    labels={
                        "Poblacion_2024": "Población Comunal (Censo 2024)",
                        "Indice_Rondinelli": "Índice de Centralidad Funcional (Rondinelli)",
                    },
                )
                fig_rond_st.update_traces(textposition="top center")
                st.plotly_chart(fig_rond_st, use_container_width=True)

        with sub_ot3:
            n_aisl_com = len(datos_ot_export["df_aislamiento"])
            st.markdown(
                f"**Matriz de Aislamiento Comunal Completa — {n_aisl_com} comunas de {region_sel}** "
                "(0 = conexión directa asfaltada; 1 = sin conexión directa)"
            )
            st.caption(
                "Cumple el punto 3 de la pauta Control 5 (todas las comunas de la región). "
                "Puedes editar cualquier celda 0/1 y el Excel se exporta listo para imprimir en 1 hoja horizontal."
            )
            df_aisl_edit = st.data_editor(
                datos_ot_export["df_aislamiento"],
                use_container_width=True,
                key=f"editor_aisl_all_sii_{reg_slug}",
            )
            st.session_state[key_aisl_ss] = df_aisl_edit
            datos_ot_export["df_aislamiento"] = df_aisl_edit

            df_aisl_vis = calcular_aislamiento_df(df_aisl_edit)
            st.dataframe(df_aisl_vis.round(2), use_container_width=True, hide_index=True)

            st.markdown("**Vista previa Índice Compuesto Mín-Máx (SII + Rondinelli: 50/50 vs. 70/30)**")
            vt_map_st = {_normalizar_texto(k): float(v) for k, v in resultados["Vt"].sum(axis=0).items()}
            pob_map_st = {_normalizar_texto(r["Comuna"]): int(r["Censo_2024"]) for _, r in datos_ot_base["df_censo"].iterrows()}
            df_u6_prev = df_rond_vis[["Comuna", "Indice_Rondinelli"]].copy()
            pobs_u6 = [pob_map_st.get(_normalizar_texto(c), 0) for c in df_u6_prev["Comuna"]]
            if all(p > 0 for p in pobs_u6):
                df_u6_prev["v1_SII"] = [vt_map_st.get(_normalizar_texto(c), 0.0) / float(p) for c, p in zip(df_u6_prev["Comuna"], pobs_u6)]
            else:
                df_u6_prev["v1_SII"] = [vt_map_st.get(_normalizar_texto(c), 0.0) for c in df_u6_prev["Comuna"]]

            r1_rng = float(df_u6_prev["v1_SII"].max() - df_u6_prev["v1_SII"].min())
            r2_rng = float(df_u6_prev["Indice_Rondinelli"].max() - df_u6_prev["Indice_Rondinelli"].min())
            df_u6_prev["u_v1"] = (df_u6_prev["v1_SII"] - df_u6_prev["v1_SII"].min()) / r1_rng if r1_rng > 0 else 0.0
            df_u6_prev["u_v2"] = (df_u6_prev["Indice_Rondinelli"] - df_u6_prev["Indice_Rondinelli"].min()) / r2_rng if r2_rng > 0 else 0.0
            df_u6_prev["Indice_50_50"] = 0.5 * df_u6_prev["u_v1"] + 0.5 * df_u6_prev["u_v2"]
            df_u6_prev["Indice_70_30"] = 0.7 * df_u6_prev["u_v1"] + 0.3 * df_u6_prev["u_v2"]
            df_u6_prev["Rank_50_50"] = df_u6_prev["Indice_50_50"].rank(ascending=False, method="min").astype(int)
            df_u6_prev["Rank_70_30"] = df_u6_prev["Indice_70_30"].rank(ascending=False, method="min").astype(int)
            st.dataframe(df_u6_prev.sort_values("Rank_50_50").round(3), use_container_width=True, hide_index=True)

    bytes_excel = compilar_excel_10_hojas(
        resultados=resultados,
        region_sel=region_sel,
        variable_sel=variable_sel,
        anio_0=anio_0,
        anio_t=anio_t,
        alpha_hk=alpha_hk,
        incluir_ot=incluir_ot_excel,
        incluir_u6=incluir_u6_excel,
        datos_ot=datos_ot_export,
    )
    total_hojas = 10 + (3 if incluir_ot_excel else 0) + (1 if incluir_u6_excel else 0)
    partes_desc = ["ILPES, Silva Lira, MADE y REAT"]
    if incluir_ot_excel:
        partes_desc.append("OT")
    if incluir_u6_excel:
        partes_desc.append("Índice U6")
    suf_nom = ("_OT" if incluir_ot_excel else "") + ("_U6" if incluir_u6_excel else "")
    nombre_archivo_salida = (
        f"Reporte_Territorial_{reg_slug}_{anio_0}_{anio_t}{suf_nom}.xlsx"
    )
    bytes_pdf_c5 = None
    try:
        from generador_imprimible_ot import generar_pdf_imprimible_control5
        bytes_pdf_c5 = generar_pdf_imprimible_control5(
            region_sel=region_sel,
            df_censo=datos_ot_export["df_censo"],
            df_guttman=datos_ot_export["df_guttman"],
            df_aislamiento=datos_ot_export["df_aislamiento"],
            dimension_ot=dim_ot_sel,
        )
    except Exception:
        bytes_pdf_c5 = None

    with slot_descarga_superior.container():
        if bytes_pdf_c5 is not None:
            cdl1, cdl2 = st.columns([1.15, 1.0])
            with cdl1:
                st.download_button(
                    label=f"Descargar Excel ({total_hojas} hojas: {', '.join(partes_desc)})",
                    data=bytes_excel,
                    file_name=nombre_archivo_salida,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_reporte_sii_ot_top",
                )
            with cdl2:
                st.download_button(
                    label=f"Descargar PDF ({len(datos_ot_export['df_aislamiento'])} comunas)",
                    data=bytes_pdf_c5,
                    file_name=f"Control5_OT_{reg_slug}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_imprimible_c5_sii_pdf",
                )
        else:
            st.download_button(
                label=f"Descargar Excel ({total_hojas} hojas: {', '.join(partes_desc)})",
                data=bytes_excel,
                file_name=nombre_archivo_salida,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="dl_reporte_sii_ot_top",
            )


# Alias de compatibilidad para importación desde app.py
renderizar_modulo_exportador_sii = renderizar_exportador_sii
mostrar_exportador_sii = renderizar_exportador_sii
