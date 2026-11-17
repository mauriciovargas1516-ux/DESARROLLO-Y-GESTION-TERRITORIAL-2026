# -*- coding: utf-8 -*-
"""
Motor Econométrico y Exportador SII — ILPES / MADE / REAT
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos
Archivo: motor_sii_exportador.py
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



# Población comunal referencial (Censo 2024 INE — Biobío, Los Lagos, Los Ríos y La Araucanía)
_POBLACION_CENSO_2024_RAW = {
    # Región del Biobío (33 comunas — Total: 1.613.059)
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
    """Aplica estilo monocromático limpio para tablas resumen."""
    fill_titulo = PatternFill("solid", fgColor="262626")
    fill_header = PatternFill("solid", fgColor="404040")
    fill_zebra = PatternFill("solid", fgColor="F9FAFB")

    font_titulo = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="374151")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_celda = Font(name="Calibri", size=10, color="111827")

    borde_fino = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
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
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, 44), 14)


def _autoajustar_columnas_hoja(ws, max_width: int = 34, min_width: int = 13, col_a_max: int = 44):
    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        if ws.column_dimensions[col_letter].hidden:
            continue
        max_len = 0
        for r_idx in range(3, min(ws.max_row + 1, 95)):
            val = ws.cell(row=r_idx, column=col_idx).value
            if val is not None:
                s_val = str(val)
                if not s_val.startswith("="):
                    max_len = max(max_len, len(s_val))
        limite_sup = col_a_max if col_idx == 1 else max_width
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, limite_sup), min_width)


def compilar_excel_10_hojas(
    resultados: dict,
    region_sel: str,
    variable_sel: str,
    anio_0: int,
    anio_t: int,
    alpha_hk: float = 2.0,
) -> bytes:
    """
    Genera en memoria un libro Excel (.xlsx) de 10 hojas con nombres naturales,
    paleta monocromática sobria, fórmulas dinámicas y Cuadrantes de Silva Lira
    en formato estándar con Población (Censo 2024) e indicador per cápita.
    """
    wb = Workbook()
    wb.remove(wb.active)

    sub_general = f"{region_sel} | {variable_sel} | Periodo {anio_0}–{anio_t} | Fuente: SII"

    # Paleta monocromática sobria
    fill_titulo = PatternFill("solid", fgColor="262626")
    fill_header = PatternFill("solid", fgColor="404040")
    fill_subbloque = PatternFill("solid", fgColor="E5E7EB")
    fill_gris_total = PatternFill("solid", fgColor="D4D4D8")
    fill_ref = PatternFill("solid", fgColor="E4E4E7")
    fill_made_mod = PatternFill("solid", fgColor="F3F4F6")
    fill_rosado_q = PatternFill("solid", fgColor="FFC7CE")

    fill_fila_blanca = PatternFill("solid", fgColor="FFFFFF")
    fill_fila_cebra = PatternFill("solid", fgColor="F9FAFB")
    fill_cuad_1 = PatternFill("solid", fgColor="F3F4F6")
    fill_cuad_2 = PatternFill("solid", fgColor="FAFAFA")
    fill_cuad_3 = PatternFill("solid", fgColor="F4F4F5")
    fill_cuad_4 = PatternFill("solid", fgColor="EBECEF")

    font_titulo = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="374151")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_subbloque = Font(name="Calibri", size=10, bold=True, color="111827")
    font_bold = Font(name="Calibri", size=10, bold=True, color="111827")
    font_celda = Font(name="Calibri", size=10, color="1F2937")
    font_rojo_q = Font(name="Calibri", size=10, bold=True, color="9C0006")

    borde_fino = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )
    borde_total = Border(
        left=Side(style="thin", color="9CA3AF"),
        right=Side(style="thin", color="9CA3AF"),
        top=Side(style="thin", color="262626"),
        bottom=Side(style="double", color="262626"),
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
        {"Indicador": "Periodo de análisis", "Valor": f"{anio_0} – {anio_t} ({mb['T_anios']} años)"},
        {"Indicador": "Comunas activas", "Valor": tot["n_comunas"]},
        {"Indicador": "Rubros económicos SII", "Valor": tot["n_rubros"]},
        {"Indicador": f"Total regional {anio_0}", "Valor": tot["total_reg_0"]},
        {"Indicador": f"Total regional {anio_t}", "Valor": tot["total_reg_t"]},
        {"Indicador": "Variación regional acumulada (%)", "Valor": tot["tasa_var_reg"]},
        {"Indicador": "Pendiente Beta absoluta (OLS)", "Valor": mb["beta"]},
        {"Indicador": "Intercepto Alpha (OLS)", "Valor": mb["alpha"]},
        {"Indicador": "Coeficiente R² (Convergencia Beta)", "Valor": mb["r2"]},
        {"Indicador": "P-valor regresión Beta", "Valor": mb["p_value"]},
        {"Indicador": "Velocidad de convergencia (λ anual)", "Valor": mb["velocidad_lambda"]},
        {
            "Indicador": "Semivida (años)",
            "Valor": float(mb["half_life"]) if np.isfinite(mb["half_life"]) else "No aplica (divergencia)",
        },
    ])
    ws1 = wb.create_sheet("Resumen")
    _estilizar_hoja_excel(
        ws1,
        f"RESUMEN EJECUTIVO — ANÁLISIS REGIONAL ({region_sel.upper()})",
        sub_general,
        df_portada,
    )

    # HOJAS 2 Y 3: BASE t0 Y BASE tf
    for anio_mat, df_mat in [(anio_0, V0), (anio_t, Vt)]:
        ws_m = wb.create_sheet(f"Base {anio_mat}")
        n_cols_m = n_comunas + 2
        ws_m.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_m)
        ct = ws_m.cell(row=1, column=1, value=f"MATRIZ SECTORIAL-COMUNAL ({anio_mat}) — {variable_sel.upper()}")
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

        ws_m.freeze_panes = "B5"
        _autoajustar_columnas_hoja(ws_m)

    # HOJA 4: LOCALIZACIÓN Qij
    ws4 = wb.create_sheet("Localización Qij")
    n_cols_q = n_comunas + 1
    ws4.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_q)
    c4_t = ws4.cell(row=1, column=1, value=f"COCIENTE DE LOCALIZACIÓN (Qij) — AÑOS {anio_0} Y {anio_t}")
    c4_t.fill = fill_titulo
    c4_t.font = font_titulo
    ws4.row_dimensions[1].height = 26

    ws4.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_q)
    c4_s = ws4.cell(
        row=2,
        column=1,
        value="Valores destacados (Qij > 1) indican especialización relativa respecto al promedio regional.",
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
        cb = ws4.cell(row=fila_cursor, column=1, value=f"Cociente de Localización (Qij) — Año {etq_anio}")
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

    ws4.freeze_panes = "B1"
    _autoajustar_columnas_hoja(ws4)

    # HOJA 5: ESPECIALIZACIÓN (Qr y CRr)
    ws5 = wb.create_sheet("Especialización")
    n_cols_e = n_comunas + 1
    ws5.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_e)
    c5_t = ws5.cell(
        row=1,
        column=1,
        value=f"COEFICIENTE DE ESPECIALIZACIÓN (Qr) Y REESTRUCTURACIÓN (CRr) — {anio_0} Y {anio_t}",
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
            value=f"Diferencias absolutas |Pij - Pi| por rubro y comuna — Año {etq_anio}",
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

    ws5.freeze_panes = "B1"
    _autoajustar_columnas_hoja(ws5)

    # HOJA 6: PROD. BÁSICA (Xij y Mj)
    ws6 = wb.create_sheet("Prod. Básica")
    n_cols_x = n_comunas + 2
    ws6.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_x)
    c6_t = ws6.cell(
        row=1,
        column=1,
        value=f"PRODUCCIÓN BÁSICA EXPORTABLE (Xij) Y MULTIPLICADOR BÁSICO (Mj) — {anio_t} Y {anio_0}",
    )
    c6_t.fill = fill_titulo
    c6_t.font = font_titulo
    ws6.row_dimensions[1].height = 26

    ws6.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols_x)
    c6_s = ws6.cell(
        row=2,
        column=1,
        value="Excedente exportador en rubros con Qij > 1 y multiplicador básico comunal (Mj = Vj / Xj).",
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
            value=f"Excedente básico exportable (Xij > 0) — Año {etq_anio}",
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
        c_vj_lbl = ws6.cell(row=f_vj, column=1, value=f"Vj — Actividad total comunal ({etq_anio})")
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
        c_xj_lbl = ws6.cell(row=f_xj, column=1, value=f"Xj — Producción básica total ({etq_anio})")
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
        c_mj_lbl = ws6.cell(row=f_mj, column=1, value=f"Mj — Multiplicador básico Vj / Xj ({etq_anio})")
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

    ws6.freeze_panes = "B1"
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
        value=f"CUADRANTES DE SILVA LIRA (CEPAL, 2005) — {region_sel.upper()} ({anio_0}–{anio_t})",
    )
    c7_t.fill = fill_titulo
    c7_t.font = font_titulo
    ws7.row_dimensions[1].height = 26

    ws7.merge_cells("A2:L2")
    sub_silva = (
        f"Variable: {variable_sel} | Fuente: SII y Censo 2024 (INE)"
        if usa_per_capita
        else f"Variable: {variable_sel} | Fuente: SII"
    )
    c7_s = ws7.cell(row=2, column=1, value=sub_silva)
    c7_s.font = font_sub
    ws7.row_dimensions[2].height = 19

    if usa_per_capita:
        headers_silva = [
            "Comuna",
            lbl_v0,
            lbl_vt,
            "Población",
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

    # Coordenadas de las 2 líneas de corte en columnas ocultas Q (17) y R (18) — nada visible bajo la tabla
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
    chart_silva.title = f"Cuadrantes de Silva Lira ({region_sel}, {anio_0}–{anio_t})"
    chart_silva.style = 2
    chart_silva.legend = None
    chart_silva.x_axis.title = lbl_pc if usa_per_capita else f"Participación Comunal {anio_t} (%)"
    chart_silva.y_axis.title = f"Tasa promedio anual de crecimiento ({anio_0}–{anio_t})"
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
        s_com.marker.graphicalProperties.solidFill = "374151"
        s_com.marker.graphicalProperties.line.solidFill = "111827"
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
    s_linea_v.graphicalProperties.line.solidFill = "991B1B"
    s_linea_v.graphicalProperties.line.width = 22000

    xh_ref = Reference(ws7, min_col=17, min_row=7, max_row=8)
    yh_ref = Reference(ws7, min_col=18, min_row=7, max_row=8)
    s_linea_h = Series(yh_ref, xh_ref, title="Promedio Regional Y")
    s_linea_h.marker.symbol = "none"
    s_linea_h.graphicalProperties.line.solidFill = "991B1B"
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
    c_m2_tit = ws7.cell(row=f_m2, column=9, value="MATRIZ 2×2 — CLASIFICACIÓN DE SILVA LIRA (CEPAL, 2005)")
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

    ws7.freeze_panes = "B5"
    _autoajustar_columnas_hoja(ws7, max_width=26, min_width=14, col_a_max=24)
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
        value=f"MÉTODO DIFERENCIAL-ESTRUCTURAL (MADE CLÁSICO) — {anio_0}–{anio_t}",
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
    cb_ed = ws8.cell(row=f_cur_8, column=1, value=f"Efecto Diferencial ({anio_0}–{anio_t})")
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
    cb_ee = ws8.cell(row=f_cur_8, column=1, value=f"Efecto Estructural ({anio_0}–{anio_t})")
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

    ws8.freeze_panes = "B1"
    _autoajustar_columnas_hoja(ws8)

    # HOJA 9: MADE MODIFICADO
    ws9 = wb.create_sheet("MADE Modificado")
    ws9.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols_ss)
    c9_t = ws9.cell(
        row=1,
        column=1,
        value=f"MÉTODO DIFERENCIAL-ESTRUCTURAL (MADE MODIFICADO) — {anio_0}–{anio_t}",
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

    ws9.freeze_panes = "B1"
    _autoajustar_columnas_hoja(ws9)

    # HOJA 10: CONVERGENCIA
    ws10 = wb.create_sheet("Convergencia")
    df_reat_excel = resultados["df_reat_resumen"].copy()
    df_reat_excel.columns = ["Indicador", f"Año {anio_0}", f"Año {anio_t}", "Variación", "Interpretación"]
    _estilizar_hoja_excel(
        ws10,
        f"DISPARIDADES, CONCENTRACIÓN Y CONVERGENCIA REGIONAL (α = {alpha_hk})",
        sub_general,
        df_reat_excel,
    )

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def _estilizar_qij_streamlit(df_q: pd.DataFrame):
    """Aplica estilo rosado/rojo a celdas Q_ij > 1 compatible con cualquier versión de Pandas."""
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
        label="Descargar Reporte Excel (10 Hojas — ILPES, Silva Lira, MADE y REAT)",
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
                "Población": pob_st,
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
                "Tasa prom. de crecimiento (%)": f"Tasa promedio anual {anio_0}–{anio_t} (%)",
            },
            title=f"Cuadrantes de Silva Lira (CEPAL, 2005 — {region_sel}, {anio_0}–{anio_t})",
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

        st.markdown("**Matriz 2×2 — Clasificación de Silva Lira**")
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


# Alias de compatibilidad para importación desde app.py
renderizar_modulo_exportador_sii = renderizar_exportador_sii
mostrar_exportador_sii = renderizar_exportador_sii
