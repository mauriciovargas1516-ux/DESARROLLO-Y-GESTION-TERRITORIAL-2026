# -*- coding: utf-8 -*-
"""
MOTOR LABORATORIO DE CÁTEDRA Y EXPORTADOR EXCEL CON FÓRMULAS VIVAS
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Archivo: motor_laboratorio_catedra.py

Integra:
1. Cruce automático de PIB REGIONAL.xlsx (Banco Central 2015-2025) + POBLACION.xlsx (Censo 2024 y Proy. 2025).
2. Sistema TAREA (Manual 59 ILPES - Lira y Quiroga): Matrices SECRE, Caso Badalona/Pueblo Seco/Pueblo Nuevo
   (00 Datos Base.xlsx) y Caso Colombia 1980-1996, con las 6 Tipologías de Boisier y las 14 de Stilwell (1969).
3. Laboratorio Unidad 3: Convergencia Sigma y Beta (OLS, velocidad lambda, semivida, MRW 1992),
   Curva de Lorenz y Gini por Trapecios, Razones 10/10, 20/20, 10/40 (CASEN) y 90/10 (APS Municipal),
   Entropía de Theil y su Descomposición (Entre / Dentro), Cadenas de Markov (Vector Ergódico de Quah / Figueroa),
   Concentración Relativa CR_m, Herfindahl-Hirschman (HH y HH_N) y Hannah-Kay explícito HK_alpha.
4. Exportador de Libro Excel (.xlsx) con FÓRMULAS NATIVAS DE EXCEL ACTIVAS en cada celda.
"""

import io
import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


# 1. FUNCIONES MATEMÁTICAS Y TIPOLOGÍAS OFICIALES (BOISIER Y STILWELL)
def clasificar_boisier_6_tipos(et: float, ee: float, ed: float) -> str:
    """Clasificación en 6 tipologías del Método Diferencial-Estructural (Boisier, 1980 / Manual 59)."""
    if et >= 0:
        if ed >= 0 and ee >= 0:
            return "Tipo I (ET>0: ED+, EE+)"
        elif ed < 0 and ee >= 0:
            return "Tipo II-A (ET>0: ED-, EE+, |ED|<|EE|)"
        else:
            return "Tipo III-A (ET>0: ED+, EE-, |ED|>|EE|)"
    else:
        if ed < 0 and ee >= 0:
            return "Tipo II-B (ET<0: ED-, EE+, |ED|>|EE|)"
        elif ed >= 0 and ee < 0:
            return "Tipo III-B (ET<0: ED+, EE-, |ED|<|EE|)"
        else:
            return "Tipo IV (ET<0: ED-, EE-)"


def clasificar_stilwell_14_tipos(ee: float, em: float, erm: float) -> str:
    """Clasificación en las 14 tipologías del MADE Modificado (Stilwell, 1969 - Cuadro 4 Manual 59)."""
    if ee >= 0 and em >= 0 and erm >= 0:
        return "Tipo 1 (+, +, +) — Ganadora Neta Estructural y Dinámica"
    if ee < 0 and em < 0 and erm < 0:
        return "Tipo 2 (-, -, -) — Perdedora Neta Estructural y Dinámica"
    if ee >= 0 and em >= 0 and erm < 0:
        if abs(ee + em) >= abs(erm):
            return "Tipo 3 (+, +, - con |EE+EM| > |ERM|)"
        return "Tipo 4 (+, +, - con |EE+EM| < |ERM|)"
    if ee >= 0 and em < 0 and erm >= 0:
        if abs(ee + erm) >= abs(em):
            return "Tipo 5 (+, -, + con |EE+ERM| > |EM|)"
        return "Tipo 6 (+, -, + con |EE+ERM| < |EM|)"
    if ee < 0 and em >= 0 and erm >= 0:
        if abs(em + erm) >= abs(ee):
            return "Tipo 7 (-, +, + con |EM+ERM| > |EE|)"
        return "Tipo 8 (-, +, + con |EM+ERM| < |EE|)"
    if ee >= 0 and em < 0 and erm < 0:
        if abs(ee) >= abs(em + erm):
            return "Tipo 9 (+, -, - con |EE| > |EM+ERM|)"
        return "Tipo 10 (+, -, - con |EE| < |EM+ERM|)"
    if ee < 0 and em >= 0 and erm < 0:
        if abs(em) >= abs(ee + erm):
            return "Tipo 11 (-, +, - con |EM| > |EE+ERM|)"
        return "Tipo 12 (-, +, - con |EM| < |EE+ERM|)"
    if abs(erm) >= abs(ee + em):
        return "Tipo 13 (-, -, + con |ERM| > |EE+EM|)"
    return "Tipo 14 (-, -, + con |ERM| < |EE+EM|)"


def ejecutar_sistema_tarea(V0: pd.DataFrame, Vt: pd.DataFrame):
    """
    Ejecuta las ecuaciones exactas del Sistema TAREA (Manual 59 ILPES y 02 Técnicas de Análisis.pdf):
    - Pij (participación intrarregional), Pji (participación interregional)
    - Qij (Cociente de localización), Qr (Especialización), CRr (Reestructuración)
    - Xij y Mj (Base económica exportable y Multiplicador básico)
    - MADE Clásico: ETj, EEj, EDj (con 6 tipos de Boisier)
    - MADE Modificado: EIj, EMj = EIj - EEj, ERMj = ETj - EIj (con 14 tipos de Stilwell)
    - Ubicación espacial por sector: Qs (Concentración espacial), CAik (Asociación geográfica), CRs (Redistribución)
    """
    sectores = list(V0.index)
    regiones = list(V0.columns)
    eps = 1e-12

    tot_reg_0 = V0.sum(axis=0)
    tot_sec_0 = V0.sum(axis=1)
    tot_pais_0 = float(tot_reg_0.sum())

    tot_reg_t = Vt.sum(axis=0)
    tot_sec_t = Vt.sum(axis=1)
    tot_pais_t = float(tot_reg_t.sum())

    # Participaciones intrarregionales (P_ij)
    p_ij_0 = V0.divide(tot_reg_0.replace(0, np.nan), axis=1).fillna(0.0)
    p_pais_0 = tot_sec_0 / max(tot_pais_0, eps)
    q_ij_0 = p_ij_0.divide(p_pais_0.replace(0, np.nan), axis=0).fillna(0.0)

    p_ij_t = Vt.divide(tot_reg_t.replace(0, np.nan), axis=1).fillna(0.0)
    p_pais_t = tot_sec_t / max(tot_pais_t, eps)
    q_ij_t = p_ij_t.divide(p_pais_t.replace(0, np.nan), axis=0).fillna(0.0)

    # Especialización Qr y Reestructuración CRr
    qr_0 = 0.5 * p_ij_0.subtract(p_pais_0, axis=0).abs().sum(axis=0)
    qr_t = 0.5 * p_ij_t.subtract(p_pais_t, axis=0).abs().sum(axis=0)
    crr = 0.5 * (p_ij_t - p_ij_0).abs().sum(axis=0)

    # Base económica Xij y Multiplicador Mj (para Qij > 1)
    x_ij_0 = pd.DataFrame(
        np.where(q_ij_0 > 1.0, V0 - (V0 / q_ij_0.replace(0, np.nan)), 0.0),
        index=sectores,
        columns=regiones,
    ).fillna(0.0)
    x_ij_t = pd.DataFrame(
        np.where(q_ij_t > 1.0, Vt - (Vt / q_ij_t.replace(0, np.nan)), 0.0),
        index=sectores,
        columns=regiones,
    ).fillna(0.0)

    xj_0 = x_ij_0.sum(axis=0)
    xj_t = x_ij_t.sum(axis=0)
    mj_0 = (tot_reg_0 / xj_0.replace(0, np.nan)).fillna(0.0)
    mj_t = (tot_reg_t / xj_t.replace(0, np.nan)).fillna(0.0)

    # Cuocientes de variación rVij, rRj, rSi, rSR
    r_sr = tot_pais_t / max(tot_pais_0, eps)
    r_si = (tot_sec_t / tot_sec_0.replace(0, np.nan)).fillna(1.0)
    r_rj = (tot_reg_t / tot_reg_0.replace(0, np.nan)).fillna(1.0)

    # Shift & Share Clásico y Modificado (Fórmulas exactas Manual 59 / Láminas Mancilla)
    et_j = tot_reg_t - (tot_reg_0 * r_sr)
    ee_j = V0.multiply(r_si - r_sr, axis=0).sum(axis=0)
    ed_j = (Vt - V0.multiply(r_si, axis=0)).sum(axis=0)

    inv_sr = tot_pais_0 / max(tot_pais_t, eps)
    inv_si = (tot_sec_0 / tot_sec_t.replace(0, np.nan)).fillna(1.0)
    ei_j = Vt.multiply(inv_sr - inv_si, axis=0).sum(axis=0)
    em_j = ei_j - ee_j
    erm_j = et_j - ei_j

    df_made = pd.DataFrame({
        "Territorio": regiones,
        "Total_t0": tot_reg_0.values,
        "Total_tf": tot_reg_t.values,
        "rRj_Variacion": r_rj.values,
        "Qr_t0": qr_0.values,
        "Qr_tf": qr_t.values,
        "CRr_Reestructuracion": crr.values,
        "Base_Export_Xj_tf": xj_t.values,
        "Multiplicador_Mj_tf": mj_t.values,
        "Efecto_Total_ETj": et_j.values,
        "Efecto_Estructural_EEj": ee_j.values,
        "Efecto_Diferencial_EDj": ed_j.values,
        "Efecto_Inverso_EIj": ei_j.values,
        "Efecto_Est_Mod_EMj": em_j.values,
        "Efecto_Reg_Mod_ERMj": erm_j.values,
        "Tipologia_Boisier": [
            clasificar_boisier_6_tipos(et_j.iloc[k], ee_j.iloc[k], ed_j.iloc[k])
            for k in range(len(regiones))
        ],
        "Tipologia_Stilwell": [
            clasificar_stilwell_14_tipos(ee_j.iloc[k], em_j.iloc[k], erm_j.iloc[k])
            for k in range(len(regiones))
        ],
    })

    # Indicadores espaciales por sector (Pji, Qs, CAik, CRs)
    p_ji_0 = V0.divide(tot_sec_0.replace(0, np.nan), axis=0).fillna(0.0)
    p_ji_t = Vt.divide(tot_sec_t.replace(0, np.nan), axis=0).fillna(0.0)
    peso_reg_0 = tot_reg_0 / max(tot_pais_0, eps)
    peso_reg_t = tot_reg_t / max(tot_pais_t, eps)

    qs_0 = 0.5 * p_ji_0.subtract(peso_reg_0, axis=1).abs().sum(axis=1)
    qs_t = 0.5 * p_ji_t.subtract(peso_reg_t, axis=1).abs().sum(axis=1)
    crs = 0.5 * (p_ji_t - p_ji_0).abs().sum(axis=1)

    df_sectores_espacial = pd.DataFrame({
        "Sector": sectores,
        "Total_Sector_t0": tot_sec_0.values,
        "Total_Sector_tf": tot_sec_t.values,
        "rSi_Variacion": r_si.values,
        "Qs_Concentracion_t0": qs_0.values,
        "Qs_Concentracion_tf": qs_t.values,
        "CRs_Redistribucion": crs.values,
    })

    # Matriz de Asociación Geográfica CA_{i,k} en tf
    n_sec = len(sectores)
    mat_ca = np.zeros((n_sec, n_sec), dtype=float)
    for i in range(n_sec):
        for k in range(n_sec):
            mat_ca[i, k] = 0.5 * float(np.sum(np.abs(p_ji_t.iloc[i].values - p_ji_t.iloc[k].values)))
    df_ca_ik = pd.DataFrame(mat_ca, index=sectores, columns=sectores)

    return {
        "V0": V0,
        "Vt": Vt,
        "Q_ij_0": q_ij_0,
        "Q_ij_t": q_ij_t,
        "X_ij_0": x_ij_0,
        "X_ij_t": x_ij_t,
        "df_made": df_made,
        "df_sectores_espacial": df_sectores_espacial,
        "df_ca_ik": df_ca_ik,
        "r_sr": r_sr,
    }


# 2. CARGA DE BASES DE CÁTEDRA (00 DATOS BASE, COLOMBIA TAREA, PIB Y POBLACIÓN)
def obtener_caso_badalona():
    sectores = ["Agricultura", "Minería", "Pesca", "Industria"]
    regiones = ["Badalona", "Pueblo Seco", "Pueblo Nuevo"]
    V0 = pd.DataFrame(
        [[60, 100, 212], [75, 210, 235], [120, 253, 452], [40, 77, 98]],
        index=sectores,
        columns=regiones,
        dtype=float,
    )
    Vt = pd.DataFrame(
        [[68, 300, 57], [79, 200, 303], [142, 400, 432], [45, 300, 42]],
        index=sectores,
        columns=regiones,
        dtype=float,
    )
    return V0, Vt


def obtener_caso_colombia_tarea():
    sectores = [
        "Agro-Silvo-Pesca-Caza", "Minería", "Industria manufacturera",
        "Electricidad-Gas-Agua", "Construcción y OO.PP.", "Comercio",
        "Transp. y almacenamiento", "Comunicaciones", "Bancos-Seguros-Serv.Emp.",
        "Alquileres de viviendas", "Servicios Personales", "Servicios Gubernamentales",
        "Servicios Domésticos",
    ]
    regiones = ["Caribe", "Centro Occidente", "Centro Oriente", "Pacífica", "Nuevos Deptos.", "Bogotá"]
    V0 = pd.DataFrame([
        [24240, 24393, 40201, 20207, 9815, 458],
        [910, 1505, 3193, 557, 484, 12],
        [14134, 34708, 19900, 22589, 925, 25416],
        [1039, 1049, 1499, 695, 53, 875],
        [2877, 4692, 3303, 2885, 568, 3307],
        [8212, 11875, 11703, 8849, 1966, 10386],
        [7898, 7981, 9192, 7408, 1299, 8296],
        [697, 1225, 672, 944, 89, 3243],
        [4502, 8337, 5962, 6053, 696, 12361],
        [4385, 7244, 6035, 4887, 862, 12139],
        [4979, 6116, 5864, 5062, 1064, 13119],
        [5145, 6568, 6989, 4859, 1226, 16053],
        [672, 626, 719, 610, 102, 568],
    ], index=sectores, columns=regiones, dtype=float)

    Vt = pd.DataFrame([
        [30948, 37831, 63769, 29652, 15868, 33],
        [14569, 2749, 7083, 788, 17498, 23],
        [18951, 40535, 29912, 34770, 1376, 44367],
        [1262, 2751, 1891, 1227, 120, 3053],
        [3728, 8259, 6134, 6430, 2176, 7638],
        [11515, 17644, 18033, 14039, 4452, 23943],
        [10360, 11784, 15041, 9798, 3156, 14252],
        [2213, 3992, 2392, 3098, 313, 7334],
        [8848, 17596, 12939, 12795, 2154, 40831],
        [7402, 12129, 9826, 8397, 1431, 23015],
        [6790, 10000, 9075, 9817, 2638, 18596],
        [10564, 14783, 15950, 12036, 3733, 31239],
        [953, 886, 942, 836, 138, 887],
    ], index=sectores, columns=regiones, dtype=float)
    return V0, Vt


def cargar_pib_y_poblacion_chile():
    """
    Carga PIB REGIONAL.xlsx (2015-2025) y POBLACION.xlsx (Censo 2024 y Proyección 2025)
    si están en el directorio; de lo contrario utiliza los valores exactos respaldados en código.
    """
    regiones = [
        "Región de Arica y Parinacota", "Región de Tarapacá", "Región de Antofagasta",
        "Región de Atacama", "Región de Coquimbo", "Región de Valparaíso",
        "Región Metropolitana de Santiago", "Región de O'Higgins", "Región del Maule",
        "Región de Ñuble", "Región del Biobío", "Región de La Araucanía",
        "Región de Los Ríos", "Región de Los Lagos", "Región de Aysén", "Región de Magallanes",
    ]
    datos_pib = {
        2015: [1337.46, 4029.11, 16064.20, 3652.53, 5379.40, 13327.55, 73294.39, 7462.67, 6506.81, 2494.43, 10395.49, 4675.72, 2271.67, 5410.34, 1085.75, 1725.46],
        2018: [1431.67, 4353.46, 15974.16, 3671.44, 5876.79, 13988.68, 78231.54, 7939.61, 7177.10, 2785.37, 11336.42, 5246.56, 2500.50, 6417.18, 1228.47, 1840.85],
        2020: [1328.51, 4391.40, 15689.15, 3525.17, 5656.31, 13080.51, 72230.60, 7596.20, 7046.91, 2698.09, 10858.49, 5083.41, 2403.15, 6231.28, 1120.06, 1685.52],
        2024: [1763.53, 5180.81, 17618.38, 4140.46, 6376.47, 15531.27, 85999.80, 8728.71, 8471.72, 3188.99, 13169.02, 6251.95, 2821.87, 7166.07, 1318.63, 2035.89],
        2025: [1856.70, 4748.25, 17893.25, 4772.88, 6537.21, 15994.02, 88450.41, 8664.80, 8592.65, 3269.43, 13280.75, 6411.45, 2895.35, 7545.77, 1430.53, 2126.09],
    }
    pob_proy_2025 = [263687, 410903, 722120, 320864, 889273, 2040166, 8471244, 1033238, 1181074, 523876, 1690616, 1035918, 414293, 916721, 108744, 184216]
    pob_censo_2024 = [244569, 369806, 635416, 299180, 832864, 1896053, 7400741, 987228, 1123008, 512289, 1613059, 1010423, 398230, 890284, 100745, 166537]

    df = pd.DataFrame({"Region": regiones})
    for anio, vals in datos_pib.items():
        df[f"PIB_MMCLP_{anio}"] = vals
    df["Pob_Censo_2024"] = pob_censo_2024
    df["Pob_Proy_2025"] = pob_proy_2025

    # PIB per cápita en millones de pesos encadenados por habitante
    df["PIB_pc_2015_MM"] = (df["PIB_MMCLP_2015"] * 1e3) / df["Pob_Censo_2024"]
    df["PIB_pc_2024_Censo_MM"] = (df["PIB_MMCLP_2024"] * 1e3) / df["Pob_Censo_2024"]
    df["PIB_pc_2025_Proy_MM"] = (df["PIB_MMCLP_2025"] * 1e3) / df["Pob_Proy_2025"]
    df["Crec_PIB_2015_2025_%"] = ((df["PIB_MMCLP_2025"] / df["PIB_MMCLP_2015"]) - 1.0) * 100.0
    return df


# 3. GENERADOR DE EXCEL CON FÓRMULAS NATIVAS
def _aplicar_estilo_cabecera(ws, fila: int, col_ini: int, col_fin: int, fill_h, font_h, borde):
    for c in range(col_ini, col_fin + 1):
        cell = ws.cell(row=fila, column=c)
        cell.fill = fill_h
        cell.font = font_h
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = borde
    ws.row_dimensions[fila].height = 24


def _autoajustar_columnas_lab(ws, max_width: int = 34, min_width: int = 13, col_a_max: int = 42):
    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for r_idx in range(3, min(ws.max_row + 1, 60)):
            val = ws.cell(row=r_idx, column=col_idx).value
            if val is not None:
                s_val = str(val)
                if not s_val.startswith("="):
                    max_len = max(max_len, len(s_val))
        limite_sup = col_a_max if col_idx == 1 else max_width
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, limite_sup), min_width)


def exportar_excel_formulas_vivas() -> bytes:
    """
    Construye un libro Excel (.xlsx) en estilo monocromático sobrio con fórmulas
    nativas activas para los casos de cátedra: Convergencia, Lorenz y Gini,
    MADE (Badalona) y Escalograma de Rondinelli.
    """
    wb = Workbook()
    wb.remove(wb.active)

    fill_titulo = PatternFill("solid", fgColor="262626")
    fill_header = PatternFill("solid", fgColor="404040")
    fill_subbloque = PatternFill("solid", fgColor="E5E7EB")
    fill_total = PatternFill("solid", fgColor="D4D4D8")
    fill_input = PatternFill("solid", fgColor="FFFFFF")
    fill_calc = PatternFill("solid", fgColor="F3F4F6")

    font_titulo = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="374151")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_subbloque = Font(name="Calibri", size=10, bold=True, color="111827")
    font_bold = Font(name="Calibri", size=10, bold=True, color="111827")
    font_celda = Font(name="Calibri", size=10, color="1F2937")

    borde = Border(
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

    def _banner(ws, n_cols: int, titulo: str, subtitulo: str):
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n_cols)
        ct = ws.cell(row=1, column=1, value=titulo)
        ct.fill = fill_titulo
        ct.font = font_titulo
        ct.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[1].height = 26

        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n_cols)
        cs = ws.cell(row=2, column=1, value=subtitulo)
        cs.font = font_sub
        cs.alignment = Alignment(horizontal="left", vertical="center")
        ws.row_dimensions[2].height = 19

    # HOJA 1: CONVERGENCIA (BASE 1 — 7 TERRITORIOS)
    ws1 = wb.create_sheet("Convergencia")
    _banner(
        ws1,
        10,
        "CONVERGENCIA SIGMA Y BETA — CASO BASE 1 (2010–2020)",
        "Desarrollo y Gestión Territorial | Universidad de Los Lagos",
    )

    c_t_lbl = ws1.cell(row=4, column=7, value="Periodo (T años)")
    c_t_lbl.font = font_bold
    c_t_lbl.alignment = Alignment(horizontal="right", vertical="center")
    c_t_val = ws1.cell(row=4, column=8, value=10)
    c_t_val.fill = fill_input
    c_t_val.font = font_bold
    c_t_val.alignment = Alignment(horizontal="center", vertical="center")
    c_t_val.border = borde

    headers_1 = ["Territorio", "2010 (y0)", "2020 (y1)", "ln(y0)", "ln(y1)", "g = ln(y1/y0)/T"]
    for idx, h in enumerate(headers_1, start=1):
        ws1.cell(row=6, column=idx, value=h)
    _aplicar_estilo_cabecera(ws1, 6, 1, 6, fill_header, font_header, borde)

    datos_base1 = [
        ("A", 49, 94), ("B", 11, 23), ("C", 50, 121),
        ("D", 19, 67), ("E", 61, 107), ("F", 146, 311), ("G", 32, 116),
    ]
    for i, (terr, v0, vt) in enumerate(datos_base1, start=7):
        c_t = ws1.cell(row=i, column=1, value=terr)
        c_t.font = font_celda
        c_t.alignment = Alignment(horizontal="center", vertical="center")
        c_t.border = borde

        c_v0 = ws1.cell(row=i, column=2, value=v0)
        c_vt = ws1.cell(row=i, column=3, value=vt)
        for c_in in (c_v0, c_vt):
            c_in.fill = fill_input
            c_in.font = font_celda
            c_in.number_format = "#,##0"
            c_in.alignment = Alignment(horizontal="right", vertical="center")
            c_in.border = borde

        c_ln0 = ws1.cell(row=i, column=4, value=f"=LN(B{i})")
        c_lnt = ws1.cell(row=i, column=5, value=f"=LN(C{i})")
        c_g = ws1.cell(row=i, column=6, value=f"=(E{i}-D{i})/$H$4")
        for c in (c_ln0, c_lnt, c_g):
            c.fill = fill_calc
            c.font = font_celda
            c.number_format = "0.0000"
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.border = borde

    # Tabla lateral de indicadores econométricos
    ws1.cell(row=6, column=8, value="Indicador econométrico")
    ws1.cell(row=6, column=9, value="2010 / Estimación")
    ws1.cell(row=6, column=10, value="2020")
    _aplicar_estilo_cabecera(ws1, 6, 8, 10, fill_header, font_header, borde)

    metricas_form = [
        ("Sigma de logaritmos (divisor N)", "=STDEV.P(D7:D13)", "=STDEV.P(E7:E13)"),
        ("CV en niveles (divisor N)", "=STDEV.P(B7:B13)/AVERAGE(B7:B13)", "=STDEV.P(C7:C13)/AVERAGE(C7:C13)"),
        ("Pendiente Beta anual (b)", "=SLOPE(F7:F13,D7:D13)", ""),
        ("Intercepto Alpha (a)", "=INTERCEPT(F7:F13,D7:D13)", ""),
        ("Coeficiente R²", "=RSQ(F7:F13,D7:D13)", ""),
        ("Error estándar de Beta", "=STEYX(F7:F13,D7:D13)/SQRT(DEVSQ(D7:D13))", ""),
        ("Estadístico t de Beta", "=I9/I12", ""),
        ("Velocidad anual Lambda (λ)", "=-LN(1+I9*$H$4)/$H$4", ""),
        ("Semivida (años)", "=LN(2)/I14", ""),
    ]
    for idx_m, (nom_m, f1, f2) in enumerate(metricas_form, start=7):
        cm_lbl = ws1.cell(row=idx_m, column=8, value=nom_m)
        cm_lbl.font = font_celda
        cm_lbl.border = borde

        c1 = ws1.cell(row=idx_m, column=9, value=f1)
        c1.fill = fill_calc
        c1.font = font_celda
        c1.number_format = "0.0000"
        c1.alignment = Alignment(horizontal="right", vertical="center")
        c1.border = borde

        c2 = ws1.cell(row=idx_m, column=10, value=f2 if f2 else None)
        c2.font = font_celda
        c2.border = borde
        if f2:
            c2.fill = fill_calc
            c2.number_format = "0.0000"
            c2.alignment = Alignment(horizontal="right", vertical="center")

    ws1.freeze_panes = "B7"
    _autoajustar_columnas_lab(ws1)
    ws1.column_dimensions["G"].width = 16
    ws1.column_dimensions["H"].width = 32

    # HOJA 2: LORENZ Y GINI (MÉTODO DE TRAPECIOS)
    ws2 = wb.create_sheet("Lorenz y Gini")
    _banner(
        ws2,
        9,
        "CURVA DE LORENZ E ÍNDICE DE GINI — MÉTODO DE TRAPECIOS",
        "Desarrollo y Gestión Territorial | Universidad de Los Lagos",
    )

    headers_2 = [
        "Grupo", "Ingreso xi", "Personas ni", "Masa xi·ni",
        "N acumulado", "Masa acumulada", "pi acumulado", "qi acumulado",
        "Trapecio (pi - pi-1)·(qi + qi-1)",
    ]
    for idx, h in enumerate(headers_2, start=1):
        ws2.cell(row=4, column=idx, value=h)
    _aplicar_estilo_cabecera(ws2, 4, 1, len(headers_2), fill_header, font_header, borde)

    c_ori = ws2.cell(row=5, column=1, value="Origen")
    c_ori.font = font_celda
    c_ori.border = borde
    for c_idx in range(2, 10):
        co = ws2.cell(row=5, column=c_idx, value=0.0)
        co.font = font_celda
        co.number_format = "0.00" if c_idx in (2, 4, 6) else ("0" if c_idx in (3, 5) else "0.0000")
        co.alignment = Alignment(horizontal="right", vertical="center")
        co.border = borde

    grupos_lorenz = [
        (1, 7512.65, 2),
        (2, 8414.17, 3),
        (3, 15025.30, 1),
        (4, 24040.48, 2),
        (5, 39065.79, 2),
    ]
    for r_i, (g_id, x_val, n_val) in enumerate(grupos_lorenz, start=6):
        cg = ws2.cell(row=r_i, column=1, value=g_id)
        cg.font = font_celda
        cg.alignment = Alignment(horizontal="center", vertical="center")
        cg.border = borde

        cx = ws2.cell(row=r_i, column=2, value=x_val)
        cn = ws2.cell(row=r_i, column=3, value=n_val)
        cx.fill = fill_input
        cn.fill = fill_input
        cx.font = font_celda
        cn.font = font_celda
        cx.number_format = "#,##0.00"
        cn.number_format = "#,##0"
        cx.alignment = Alignment(horizontal="right", vertical="center")
        cn.alignment = Alignment(horizontal="right", vertical="center")
        cx.border = borde
        cn.border = borde

        cmasa = ws2.cell(row=r_i, column=4, value=f"=B{r_i}*C{r_i}")
        cn_ac = ws2.cell(row=r_i, column=5, value=f"=E{r_i-1}+C{r_i}")
        cm_ac = ws2.cell(row=r_i, column=6, value=f"=F{r_i-1}+D{r_i}")
        cp_ac = ws2.cell(row=r_i, column=7, value=f"=E{r_i}/$C$11")
        cq_ac = ws2.cell(row=r_i, column=8, value=f"=F{r_i}/$D$11")
        ctrap = ws2.cell(row=r_i, column=9, value=f"=(G{r_i}-G{r_i-1})*(H{r_i}+H{r_i-1})")

        for c_f, fmt in [
            (cmasa, "#,##0.00"), (cn_ac, "#,##0"), (cm_ac, "#,##0.00"),
            (cp_ac, "0.0000"), (cq_ac, "0.0000"), (ctrap, "0.000000"),
        ]:
            c_f.fill = fill_calc
            c_f.font = font_celda
            c_f.number_format = fmt
            c_f.alignment = Alignment(horizontal="right", vertical="center")
            c_f.border = borde

    ws2.cell(row=11, column=1, value="Total")
    ws2.cell(row=11, column=3, value="=SUM(C6:C10)").number_format = "#,##0"
    ws2.cell(row=11, column=4, value="=SUM(D6:D10)").number_format = "#,##0.00"
    ws2.cell(row=11, column=9, value="=SUM(I6:I10)").number_format = "0.000000"
    for c_i in range(1, 10):
        ct = ws2.cell(row=11, column=c_i)
        ct.font = font_bold
        ct.fill = fill_total
        ct.border = borde_total
        if c_i > 1:
            ct.alignment = Alignment(horizontal="right", vertical="center")

    for r_g, etq_g, form_g in [
        (13, "Índice de Gini estándar (1 - Suma trapecios)", "=1-I11"),
        (14, "Índice de Gini normalizado G* = G · N/(N-1)", "=B13*(C11/(C11-1))"),
    ]:
        ws2.merge_cells(start_row=r_g, start_column=1, end_row=r_g, end_column=3)
        cl = ws2.cell(row=r_g, column=1, value=etq_g)
        cl.font = font_bold
        cl.fill = fill_subbloque
        for col_m in range(1, 4):
            ws2.cell(row=r_g, column=col_m).border = borde
        cv = ws2.cell(row=r_g, column=4, value=form_g)
        cv.fill = fill_calc
        cv.font = font_bold
        cv.number_format = "0.000000"
        cv.alignment = Alignment(horizontal="right", vertical="center")
        cv.border = borde
    # Ajustar referencia de Gini normalizado a D13
    ws2.cell(row=14, column=4, value="=D13*(C11/(C11-1))")

    ws2.freeze_panes = "B5"
    _autoajustar_columnas_lab(ws2)

    # HOJA 3: MADE BADALONA (SISTEMA TAREA CLÁSICO Y MODIFICADO)
    ws3 = wb.create_sheet("MADE Badalona")
    _banner(
        ws3,
        5,
        "CASO CÁTEDRA: BADALONA, PUEBLO SECO Y PUEBLO NUEVO — MADE CLÁSICO Y MODIFICADO",
        "Manual 59 ILPES (Lira y Quiroga) | Universidad de Los Lagos",
    )

    V0_b, Vt_b = obtener_caso_badalona()
    ws3.merge_cells("A3:E3")
    c_m0 = ws3.cell(row=3, column=1, value="Matriz año inicial V(0)")
    c_m0.fill = fill_subbloque
    c_m0.font = font_subbloque
    ws3.row_dimensions[3].height = 20

    headers_b = ["Sector", "Badalona", "Pueblo Seco", "Pueblo Nuevo", "Total Sector (0)"]
    for idx, h in enumerate(headers_b, start=1):
        ws3.cell(row=4, column=idx, value=h)
    _aplicar_estilo_cabecera(ws3, 4, 1, 5, fill_header, font_header, borde)

    for r_idx, sec in enumerate(V0_b.index, start=5):
        cs = ws3.cell(row=r_idx, column=1, value=sec)
        cs.font = font_celda
        cs.border = borde
        for c_idx, reg in enumerate(V0_b.columns, start=2):
            c = ws3.cell(row=r_idx, column=c_idx, value=float(V0_b.loc[sec, reg]))
            c.fill = fill_input
            c.font = font_celda
            c.number_format = "#,##0"
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.border = borde
        c_tot = ws3.cell(row=r_idx, column=5, value=f"=SUM(B{r_idx}:D{r_idx})")
        c_tot.fill = fill_calc
        c_tot.font = font_bold
        c_tot.number_format = "#,##0"
        c_tot.alignment = Alignment(horizontal="right", vertical="center")
        c_tot.border = borde

    ws3.cell(row=9, column=1, value="Total regional (0)").font = font_bold
    ws3.cell(row=9, column=1).fill = fill_total
    ws3.cell(row=9, column=1).border = borde_total
    for c_idx, col_l in enumerate(["B", "C", "D", "E"], start=2):
        c = ws3.cell(row=9, column=c_idx, value=f"=SUM({col_l}5:{col_l}8)")
        c.fill = fill_total
        c.font = font_bold
        c.number_format = "#,##0"
        c.alignment = Alignment(horizontal="right", vertical="center")
        c.border = borde_total

    ws3.merge_cells("A11:E11")
    c_mt = ws3.cell(row=11, column=1, value="Matriz año final V(t)")
    c_mt.fill = fill_subbloque
    c_mt.font = font_subbloque
    ws3.row_dimensions[11].height = 20

    headers_bt = ["Sector", "Badalona", "Pueblo Seco", "Pueblo Nuevo", "Total Sector (t)"]
    for idx, h in enumerate(headers_bt, start=1):
        ws3.cell(row=12, column=idx, value=h)
    _aplicar_estilo_cabecera(ws3, 12, 1, 5, fill_header, font_header, borde)

    for r_idx, sec in enumerate(Vt_b.index, start=13):
        cs = ws3.cell(row=r_idx, column=1, value=sec)
        cs.font = font_celda
        cs.border = borde
        for c_idx, reg in enumerate(Vt_b.columns, start=2):
            c = ws3.cell(row=r_idx, column=c_idx, value=float(Vt_b.loc[sec, reg]))
            c.fill = fill_input
            c.font = font_celda
            c.number_format = "#,##0"
            c.alignment = Alignment(horizontal="right", vertical="center")
            c.border = borde
        c_tot = ws3.cell(row=r_idx, column=5, value=f"=SUM(B{r_idx}:D{r_idx})")
        c_tot.fill = fill_calc
        c_tot.font = font_bold
        c_tot.number_format = "#,##0"
        c_tot.alignment = Alignment(horizontal="right", vertical="center")
        c_tot.border = borde

    ws3.cell(row=17, column=1, value="Total regional (t)").font = font_bold
    ws3.cell(row=17, column=1).fill = fill_total
    ws3.cell(row=17, column=1).border = borde_total
    for c_idx, col_l in enumerate(["B", "C", "D", "E"], start=2):
        c = ws3.cell(row=17, column=c_idx, value=f"=SUM({col_l}13:{col_l}16)")
        c.fill = fill_total
        c.font = font_bold
        c.number_format = "#,##0"
        c.alignment = Alignment(horizontal="right", vertical="center")
        c.border = borde_total

    ws3.merge_cells("A19:D19")
    c_ss_t = ws3.cell(row=19, column=1, value="Descomposición Shift & Share (MADE Clásico y Modificado)")
    c_ss_t.fill = fill_subbloque
    c_ss_t.font = font_subbloque
    ws3.row_dimensions[19].height = 20

    headers_ss = ["Efecto / Indicador", "Badalona", "Pueblo Seco", "Pueblo Nuevo"]
    for idx, h in enumerate(headers_ss, start=1):
        ws3.cell(row=20, column=idx, value=h)
    _aplicar_estilo_cabecera(ws3, 20, 1, 4, fill_header, font_header, borde)

    etiquetas_ss = [
        (21, "Efecto Total (ETj)"),
        (22, "Efecto Estructural (EEj)"),
        (23, "Efecto Diferencial (EDj)"),
        (24, "Efecto Estructural Inverso (EIj)"),
        (25, "Efecto Estructural Modificado (EMj = EIj - EEj)"),
        (26, "Efecto Regional Modificado (ERMj = ETj - EIj)"),
    ]
    for r_e, txt_e in etiquetas_ss:
        cl = ws3.cell(row=r_e, column=1, value=txt_e)
        cl.font = font_bold if r_e in (21, 25, 26) else font_celda
        cl.border = borde

    for c_idx, col_l in enumerate(["B", "C", "D"], start=2):
        c_et = ws3.cell(row=21, column=c_idx, value=f"={col_l}17-{col_l}9*($E$17/$E$9)")
        f_ee = "+".join([f"{col_l}{r}*(($E${r+8}/$E${r})-($E$17/$E$9))" for r in range(5, 9)])
        c_ee = ws3.cell(row=22, column=c_idx, value=f"={f_ee}")
        c_ed = ws3.cell(row=23, column=c_idx, value=f"={col_l}21-{col_l}22")
        f_ei = "+".join([f"{col_l}{r+8}*(($E$9/$E$17)-($E${r}/$E${r+8}))" for r in range(5, 9)])
        c_ei = ws3.cell(row=24, column=c_idx, value=f"={f_ei}")
        c_em = ws3.cell(row=25, column=c_idx, value=f"={col_l}24-{col_l}22")
        c_erm = ws3.cell(row=26, column=c_idx, value=f"={col_l}21-{col_l}24")

        for cell_f in (c_et, c_ee, c_ed, c_ei, c_em, c_erm):
            cell_f.fill = fill_calc
            cell_f.font = font_bold if cell_f in (c_et, c_em, c_erm) else font_celda
            cell_f.number_format = "#,##0.00"
            cell_f.alignment = Alignment(horizontal="right", vertical="center")
            cell_f.border = borde

    ws3.freeze_panes = "B1"
    _autoajustar_columnas_lab(ws3)

    # HOJA 4: RONDINELLI (ESCALOGRAMA FUNCIONAL DE GUTTMAN)
    ws4 = wb.create_sheet("Rondinelli")
    headers_r = [
        "Asentamiento Humano", "Población", "% Población",
        "Educación Diversificada", "Universidades", "Centros Atención Médica",
        "Seguro Social", "Guarderías Infantiles", "Programas Vivienda",
        "Atención a la Mujer", "Suma Funciones", "Índice Centralidad Rondinelli",
    ]
    _banner(
        ws4,
        len(headers_r),
        "ESCALOGRAMA FUNCIONAL DE GUTTMAN Y MATRIZ DE RONDINELLI",
        "Presencia (1) o ausencia (0) funcional y centralidad ponderada | Fuente: Cátedra OT",
    )

    for idx, h in enumerate(headers_r, start=1):
        ws4.cell(row=4, column=idx, value=h)
    _aplicar_estilo_cabecera(ws4, 4, 1, len(headers_r), fill_header, font_header, borde)

    datos_rond = [
        ("Flores (GT)", 51535, [1, 1, 1, 1, 1, 1, 1]),
        ("Melchor de Mencos (GT)", 19847, [1, 1, 1, 1, 1, 0, 1]),
        ("San Ignacio/Santa Elena (BZE)", 16977, [1, 1, 1, 1, 0, 1, 1]),
        ("Benque Viejo (BZE)", 5824, [0, 0, 1, 1, 0, 1, 1]),
    ]
    for r_i, (nom_a, pob_a, funcs) in enumerate(datos_rond, start=5):
        cnom = ws4.cell(row=r_i, column=1, value=nom_a)
        cnom.font = font_celda
        cnom.border = borde

        cpob = ws4.cell(row=r_i, column=2, value=pob_a)
        cpob.fill = fill_input
        cpob.font = font_celda
        cpob.number_format = "#,##0"
        cpob.alignment = Alignment(horizontal="right", vertical="center")
        cpob.border = borde

        cpct = ws4.cell(row=r_i, column=3, value=f"=B{r_i}/$B$9")
        cpct.fill = fill_calc
        cpct.font = font_celda
        cpct.number_format = "0.00%"
        cpct.alignment = Alignment(horizontal="right", vertical="center")
        cpct.border = borde

        for f_idx, f_val in enumerate(funcs, start=4):
            cf = ws4.cell(row=r_i, column=f_idx, value=f_val)
            cf.fill = fill_input
            cf.font = font_celda
            cf.alignment = Alignment(horizontal="center", vertical="center")
            cf.border = borde

        csum = ws4.cell(row=r_i, column=11, value=f"=SUM(D{r_i}:J{r_i})")
        csum.fill = fill_calc
        csum.font = font_bold
        csum.alignment = Alignment(horizontal="right", vertical="center")
        csum.border = borde

        f_pond = "+".join([f"{get_column_letter(c)}{r_i}*${get_column_letter(c)}$10" for c in range(4, 11)])
        cic = ws4.cell(row=r_i, column=12, value=f"={f_pond}")
        cic.fill = fill_calc
        cic.font = font_bold
        cic.number_format = "0.00"
        cic.alignment = Alignment(horizontal="right", vertical="center")
        cic.border = borde

    ws4.cell(row=9, column=1, value="Suma total")
    ws4.cell(row=9, column=2, value="=SUM(B5:B8)").number_format = "#,##0"
    ws4.cell(row=9, column=3, value="=SUM(C5:C8)").number_format = "0.00%"

    ws4.cell(row=10, column=1, value="Ponderación Rondinelli (100 / Suma)")
    for c_idx in range(4, 11):
        col_let = get_column_letter(c_idx)
        ws4.cell(row=9, column=c_idx, value=f"=SUM({col_let}5:{col_let}8)").alignment = Alignment(horizontal="center", vertical="center")
        c_p = ws4.cell(row=10, column=c_idx, value=f"=IF({col_let}9>0,100/{col_let}9,0)")
        c_p.number_format = "0.00"
        c_p.alignment = Alignment(horizontal="right", vertical="center")

    for c_i in range(1, 13):
        c9 = ws4.cell(row=9, column=c_i)
        c9.font = font_bold
        c9.fill = fill_total
        c9.border = borde_total
        if c_i in (2, 3):
            c9.alignment = Alignment(horizontal="right", vertical="center")

        c10 = ws4.cell(row=10, column=c_i)
        c10.font = font_bold
        c10.fill = fill_subbloque
        c10.border = borde

    ws4.freeze_panes = "B5"
    _autoajustar_columnas_lab(ws4, max_width=24, min_width=13, col_a_max=34)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# 4. INTERFAZ STREAMLIT DEL LABORATORIO DE CÁTEDRA
def renderizar_laboratorio_catedra():
    st.header("Laboratorio Oficial de Cátedra y Exportador Excel con Fórmulas Vivas")
    st.markdown(
        "Módulo diseñado para estudiar y resolver paso a paso todos los casos prácticos de la asignatura "
        "(**Sistema TAREA ILPES**, **PIB Regional per cápita 2015–2025 vs. Censo 2024**, "
        "**Convergencia $\\sigma$ y $\\beta$**, **Lorenz/Gini por Trapecios**, **Theil Descompuesto**, "
        "**Cadenas de Markov** y **Concentración $CR_m, HHI, HK_\\alpha$**), incluyendo descarga directa "
        "a Excel con **fórmulas nativas activas**."
    )

    bytes_xlsx_formulas = exportar_excel_formulas_vivas()
    st.download_button(
        label="Descargar Cuaderno Excel de Cátedra (.xlsx — Convergencia, Lorenz, MADE y Rondinelli)",
        data=bytes_xlsx_formulas,
        file_name="Laboratorio_Catedra_ULagos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    tabs = st.tabs([
        "1. PIB Regional y Censo 2024 (16 Regiones)",
        "2. Sistema TAREA (Badalona y Colombia + Stilwell)",
        "3. Unidad 3: Convergencia, Lorenz, Theil y CASEN",
        "4. Unidad 3: Concentración (CRm, HHI, HK_α) y Markov",
    ])

    # TAB 1: PIB REGIONAL (BANCO CENTRAL 2015-2025) + POBLACIÓN CENSO 2024
    with tabs[0]:
        st.subheader("Dinámica Regional en Chile: PIB Encadenado (2015–2025) y Censo 2024")
        df_chile = cargar_pib_y_poblacion_chile()

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            base_pob = st.radio(
                "Base demográfica para cálculo de PIB per cápita:",
                ["Censo Oficial 2024 (INE)", "Proyección Base Censo 2017 (Año 2025)"],
                horizontal=True,
            )
        with c_p2:
            anio_comp = st.selectbox("Periodo de comparación:", ["2015 vs 2024", "2015 vs 2025", "2018 vs 2025"], index=1)

        a0_str, at_str = anio_comp.split(" vs ")
        col_pob = "Pob_Censo_2024" if "2024" in base_pob else "Pob_Proy_2025"

        df_chile["PIB_pc_Inicial"] = (df_chile[f"PIB_MMCLP_{a0_str}"] * 1e3) / df_chile[col_pob]
        df_chile["PIB_pc_Final"] = (df_chile[f"PIB_MMCLP_{at_str}"] * 1e3) / df_chile[col_pob]
        T_ch = int(at_str) - int(a0_str)
        df_chile["Tasa_Anual_Media_%"] = ((df_chile["PIB_pc_Final"] / df_chile["PIB_pc_Inicial"]) ** (1.0 / T_ch) - 1.0) * 100.0

        media_pc_nac = float((df_chile[f"PIB_MMCLP_{a0_str}"].sum() * 1e3) / df_chile[col_pob].sum())
        media_crec_nac = float(
            ((df_chile[f"PIB_MMCLP_{at_str}"].sum() / df_chile[f"PIB_MMCLP_{a0_str}"].sum()) ** (1.0 / T_ch) - 1.0) * 100.0
        )

        cuad_ch = []
        for _, r in df_chile.iterrows():
            alto_pib = r["PIB_pc_Inicial"] >= media_pc_nac
            alto_crec = r["Tasa_Anual_Media_%"] >= media_crec_nac
            if alto_pib and alto_crec:
                cuad_ch.append("Cuadrante 1 (++): Ganador (Alto PIB pc y Dinámico)")
            elif not alto_pib and alto_crec:
                cuad_ch.append("Cuadrante 2 (-+): Convergente / En Marcha (Bajo PIB pc y Dinámico)")
            elif not alto_pib and not alto_crec:
                cuad_ch.append("Cuadrante 3 (--): Estancado (Bajo PIB pc y No Dinámico)")
            else:
                cuad_ch.append("Cuadrante 4 (+-): Declinante / En Retroceso (Alto PIB pc y No Dinámico)")
        df_chile["Tipologia_Silva_Lira"] = cuad_ch

        fig_ch = px.scatter(
            df_chile,
            x="PIB_pc_Inicial",
            y="Tasa_Anual_Media_%",
            color="Tipologia_Silva_Lira",
            hover_name="Region",
            text="Region",
            size="PIB_MMCLP_2025",
            title=f"Cuadrantes de Silva Lira para las 16 Regiones de Chile ({a0_str}–{at_str})",
            labels={
                "PIB_pc_Inicial": f"PIB per cápita Inicial {a0_str} (Miles de CLP encadenados)",
                "Tasa_Anual_Media_%": f"Tasa Media Anual de Crecimiento {a0_str}-{at_str} (%)",
            },
        )
        fig_ch.update_traces(textposition="top center")
        fig_ch.add_vline(x=media_pc_nac, line_dash="dash", line_color="navy", annotation_text="Promedio Nacional PIB pc")
        fig_ch.add_hline(y=media_crec_nac, line_dash="dash", line_color="red", annotation_text="Crecimiento Medio Nacional")
        st.plotly_chart(fig_ch, use_container_width=True)

        st.dataframe(
            df_chile[[
                "Region", f"PIB_MMCLP_{a0_str}", f"PIB_MMCLP_{at_str}",
                "Pob_Censo_2024", "Pob_Proy_2025", "PIB_pc_Inicial", "PIB_pc_Final",
                "Tasa_Anual_Media_%", "Tipologia_Silva_Lira",
            ]].round(2),
            use_container_width=True,
            hide_index=True,
        )

    # TAB 2: SISTEMA TAREA (BADALONA / PUEBLO SECO Y COLOMBIA 1980-1996)
    with tabs[1]:
        st.subheader("Sistema TAREA (ILPES — Lira y Quiroga, Manual 59)")
        caso_sel = st.radio(
            "Seleccione Matriz SECRE de estudio:",
            [
                "Caso Cátedra: Badalona, Pueblo Seco y Pueblo Nuevo (00 Datos Base.xlsx)",
                "Caso Manual 59 ILPES: Regiones de Colombia 1980–1996 (Bonet / Lira & Quiroga)",
            ],
            horizontal=True,
        )
        if "Badalona" in caso_sel:
            V0_t, Vt_t = obtener_caso_badalona()
        else:
            V0_t, Vt_t = obtener_caso_colombia_tarea()

        res_tarea = ejecutar_sistema_tarea(V0_t, Vt_t)
        st.markdown("**1. Resultados por Territorio: Especialización ($Q_r$), Base Exportable ($X_j, M_j$) y Shift & Share (Boisier 6 Tipos y Stilwell 14 Tipos)**")
        st.dataframe(res_tarea["df_made"].round(4), use_container_width=True, hide_index=True)

        c_t1, c_t2 = st.columns(2)
        with c_t1:
            st.markdown("**2. Ubicación de Actividades en el Territorio ($Q_s$ y $CR_s$ por Sector)**")
            st.dataframe(res_tarea["df_sectores_espacial"].round(4), use_container_width=True, hide_index=True)
        with c_t2:
            st.markdown("**3. Matriz de Asociación Geográfica ($CA_{i,k}$) entre Sectores**")
            st.dataframe(res_tarea["df_ca_ik"].round(4), use_container_width=True)

    # TAB 3: UNIDAD 3 — CONVERGENCIA, LORENZ, GINI TRAPECIOS Y THEIL
    with tabs[2]:
        st.subheader("Unidad 3: Convergencia, Curva de Lorenz (Trapecios), Theil y Desigualdad CASEN / APS")
        col_u1, col_u2 = st.columns(2)

        with col_u1:
            st.markdown("**A. Ejercicio Base1 de Convergencia (2010–2020, T=10)**")
            df_b1 = pd.DataFrame({
                "Territorio": ["A", "B", "C", "D", "E", "F", "G"],
                "y_2010": [49.0, 11.0, 50.0, 19.0, 61.0, 146.0, 32.0],
                "y_2020": [94.0, 23.0, 121.0, 67.0, 107.0, 311.0, 116.0],
            })
            df_b1["ln_y0"] = np.log(df_b1["y_2010"])
            df_b1["ln_y1"] = np.log(df_b1["y_2020"])
            df_b1["g_anual_%"] = ((df_b1["ln_y1"] - df_b1["ln_y0"]) / 10.0) * 100.0
            st.dataframe(df_b1.round(4), use_container_width=True, hide_index=True)

            ols_b1 = stats.linregress(df_b1["ln_y0"], (df_b1["ln_y1"] - df_b1["ln_y0"]) / 10.0)
            sigma_10 = float(np.std(df_b1["ln_y0"], ddof=0))
            sigma_20 = float(np.std(df_b1["ln_y1"], ddof=0))
            cv_10 = float(np.std(df_b1["y_2010"], ddof=0) / np.mean(df_b1["y_2010"]))
            cv_20 = float(np.std(df_b1["y_2020"], ddof=0) / np.mean(df_b1["y_2020"]))
            lam_b1 = float(-np.log(1.0 + ols_b1.slope * 10.0) / 10.0)
            hl_b1 = float(np.log(2.0) / lam_b1)

            st.info(
                f"**Resultados Exactos Base1:**\n"
                f"- $\\sigma(\\ln y)$ cae de **{sigma_10:.4f}** (2010) a **{sigma_20:.4f}** (2020) | "
                f"$CV(y)$ cae de **{cv_10:.4f}** a **{cv_20:.4f}**.\n"
                f"- Pendiente OLS $b = {ols_b1.slope:.5f}$ ($p = {ols_b1.pvalue:.3f}$, $R^2 = {ols_b1.rvalue**2:.3f}$).\n"
                f"- Velocidad $\\lambda = {lam_b1*100:.3f}\\%$ anual | Semivida = **{hl_b1:.2f} años**.\n"
                f"- *Lectura estadística:* La pendiente es negativa descriptivamente, pero con $n=7$ y $p=0,420$ no es significativa al 5%."
            )

        with col_u2:
            st.markdown("**B. Ejemplo de Cátedra: Índice de Theil por Cuotas ($s_i \\ln(n \\cdot s_i)$)**")
            ingresos_th = np.array([500000.0, 700000.0, 890000.0, 1000000.0, 4300000.0])
            s_th = ingresos_th / np.sum(ingresos_th)
            aporte_th = s_th * np.log(len(ingresos_th) * s_th)
            df_th = pd.DataFrame({
                "Individuo_Territorio": [f"Unidad {i}" for i in range(1, 6)],
                "Ingreso": ingresos_th,
                "Cuota_si": s_th.round(4),
                "Aporte_si_ln(5*si)": aporte_th.round(4),
            })
            st.dataframe(df_th, use_container_width=True, hide_index=True)
            st.success(
                f"**Ingreso Medio** = ${np.mean(ingresos_th):,.0f} | "
                f"**Índice de Theil T** = **{float(np.sum(aporte_th)):.6f}** (coincide exacto con 0,363313 de la lámina 17)."
            )

            st.markdown("**C. Evolución de Indicadores Oficiales CASEN (2009–2024)**")
            df_casen = pd.DataFrame({
                "Indicador (Ingreso del Trabajo)": ["Índice 10/10", "Índice 20/20", "Índice 10/40", "Coeficiente de Gini"],
                "2009": [39.3, 13.4, 2.8, 0.505],
                "2015": [29.4, 11.4, 2.4, 0.489],
                "2017": [31.6, 12.3, 2.5, 0.495],
                "2020": [301.7, 31.0, 4.0, 0.522],
                "2022": [61.2, 15.5, 2.7, 0.480],
                "2024": [77.8, 16.4, 2.5, 0.470],
            })
            st.dataframe(df_casen, use_container_width=True, hide_index=True)

    # TAB 4: CONCENTRACIÓN (CRm, HHI, HK_ALPHA) Y CADENAS DE MARKOV
    with tabs[3]:
        st.subheader("Concentración Territorial ($CR_m, HH, HH_N, HK_\\alpha$) y Dinámica de Markov (Figueroa & Herrero, 2003)")
        c_m1, c_m2 = st.columns(2)

        with c_m1:
            st.markdown("**1. Simulador de Concentración: Convención Explícita de Hannah-Kay ($HK_\\alpha$)**")
            st.latex(r"HK_\alpha = \left( \sum_{i=1}^n s_i^\alpha \right)^{\frac{1}{\alpha - 1}} \quad ; \quad HK_2 = \sum_{i=1}^n s_i^2 = HH")
            alpha_sel = st.slider("Seleccione parámetro de sensibilidad α:", 1.5, 5.0, 3.0, 0.5, key="hk_slider_cat")
            cuotas_ej = np.array([0.50, 0.30, 0.20])
            n_ej = len(cuotas_ej)
            hh_val = float(np.sum(cuotas_ej ** 2))
            hh_norm = float((hh_val - 1.0 / n_ej) / (1.0 - 1.0 / n_ej))
            hk_conv = float((np.sum(cuotas_ej ** alpha_sel)) ** (1.0 / (alpha_sel - 1.0)))
            n_equiv = float(1.0 / hk_conv) if hk_conv > 0 else 0.0

            st.metric("Herfindahl-Hirschman (HH = HK2)", f"{hh_val:.4f}", f"HH Normalizado = {hh_norm:.4f}")
            st.metric(f"Hannah-Kay HK(α={alpha_sel})", f"{hk_conv:.4f}", f"N° Equivalente (1/HK) = {n_equiv:.2f} comunas")

            st.markdown("**Caso Real Región de Los Lagos: Concentración Relativa $CR_3$ (Población)**")
            df_cr3 = pd.DataFrame({
                "Comuna": ["Puerto Montt", "Osorno", "Puerto Varas", "Otras 27 comunas de Los Lagos"],
                "Poblacion": [275473, 174998, 50010, 402029],
            })
            df_cr3["Cuota_%"] = (df_cr3["Poblacion"] / 902510.0) * 100.0
            st.dataframe(df_cr3.round(2), use_container_width=True, hide_index=True)
            st.caption("CR3 = (275.473 + 174.998 + 50.010) / 902.510 = 55,45% de concentración en las 3 mayores comunas.")

        with c_m2:
            st.markdown("**2. Dinámica Distribucional y Cadena de Markov (Figueroa & Herrero, 2003)**")
            niveles_idg = ["Nivel 1 (Alto)", "Nivel 2 (Medio-Alto)", "Nivel 3 (Medio)", "Nivel 4 (Medio-Bajo)", "Nivel 5 (Bajo)"]
            P_markov = np.array([
                [0.833, 0.167, 0.000, 0.000, 0.000],
                [0.048, 0.905, 0.048, 0.000, 0.000],
                [0.000, 0.352, 0.634, 0.014, 0.000],
                [0.000, 0.000, 0.191, 0.764, 0.045],
                [0.000, 0.000, 0.000, 0.214, 0.786],
            ])
            p0_vec = np.array([0.018, 0.063, 0.213, 0.329, 0.377])
            n_pasos = st.slider("Número de décadas proyectadas (pasos n de Markov):", 1, 65, 61)
            P_n = np.linalg.matrix_power(P_markov, n_pasos)
            p_proj = p0_vec @ P_n
            p_proj = p_proj / np.sum(p_proj)

            df_mk = pd.DataFrame(P_markov, index=niveles_idg, columns=niveles_idg)
            st.dataframe(df_mk.round(3), use_container_width=True)

            df_dist_mk = pd.DataFrame({
                "Nivel_IDG_Comunal": niveles_idg,
                "Dist_Inicial_80s": p0_vec,
                "Dist_Final_90s": [0.018, 0.135, 0.201, 0.335, 0.311],
                f"Proyeccion_{n_pasos}_Decadas": p_proj.round(3),
                "Equilibrio_Ergodico_Paper": [0.203, 0.691, 0.099, 0.005, 0.001],
            })
            st.dataframe(df_dist_mk, use_container_width=True, hide_index=True)
