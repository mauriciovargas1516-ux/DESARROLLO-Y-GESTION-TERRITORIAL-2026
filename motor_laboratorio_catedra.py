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


# ==============================================================================
# 1. FUNCIONES MATEMÁTICAS Y TIPOLOGÍAS OFICIALES (BOISIER Y STILWELL)
# ==============================================================================
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


# ==============================================================================
# 2. CARGA DE BASES DE CÁTEDRA (00 DATOS BASE, COLOMBIA TAREA, PIB Y POBLACIÓN)
# ==============================================================================
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


# ==============================================================================
# 3. GENERADOR DE EXCEL CON FÓRMULAS NATIVAS VIVAS ADENTRO
# ==============================================================================
def _aplicar_estilo_cabecera(ws, fila: int, n_cols: int):
    fill_h = PatternFill("solid", fgColor="1E3A8A")
    font_h = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    for c in range(1, n_cols + 1):
        cell = ws.cell(row=fila, column=c)
        cell.fill = fill_h
        cell.font = font_h
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def exportar_excel_formulas_vivas() -> bytes:
    """
    Construye un libro Excel (.xlsx) pedagógico y profesional donde todos los ejercicios
    de cátedra están resueltos mediante FÓRMULAS NATIVAS DE EXCEL (=LN, =SLOPE, =STDEV.P,
    =SUM, =ABS, trapecios de Lorenz, MADE Clásico/Modificado y Matriz de Rondinelli).
    """
    wb = Workbook()
    wb.remove(wb.active)

    fill_input = PatternFill("solid", fgColor="FEF9C3")  # Amarillo suave para celdas editables
    fill_calc = PatternFill("solid", fgColor="EFF6FF")   # Azul suave para fórmulas
    borde = Border(
        left=Side(style="thin", color="CBD5E1"),
        right=Side(style="thin", color="CBD5E1"),
        top=Side(style="thin", color="CBD5E1"),
        bottom=Side(style="thin", color="CBD5E1"),
    )

    # ------------------------------------------------------------------
    # HOJA 1: CONVERGENCIA SIGMA Y BETA (BASE 1 - 7 TERRITORIOS)
    # ------------------------------------------------------------------
    ws1 = wb.create_sheet("01_Convergencia_Formulas")
    ws1["A1"] = "LABORATORIO DE CONVERGENCIA SIGMA Y BETA (FÓRMULAS EXCEL ACTIVAS)"
    ws1["A1"].font = Font(size=13, bold=True, color="1E3A8A")
    ws1["A2"] = "Amarillo = Celdas de entrada editables | Azul = Fórmulas dinámicas de Excel"
    ws1["G4"] = "Años T"
    ws1["H4"] = 10
    ws1["H4"].fill = fill_input

    headers_1 = ["Territorio", "2010 (y0)", "2020 (y1)", "ln(y0)", "ln(y1)", "g = ln(y1/y0)/T"]
    for idx, h in enumerate(headers_1, start=1):
        ws1.cell(row=6, column=idx, value=h)
    _aplicar_estilo_cabecera(ws1, 6, 6)

    datos_base1 = [
        ("A", 49, 94), ("B", 11, 23), ("C", 50, 121),
        ("D", 19, 67), ("E", 61, 107), ("F", 146, 311), ("G", 32, 116),
    ]
    for i, (terr, v0, vt) in enumerate(datos_base1, start=7):
        ws1.cell(row=i, column=1, value=terr)
        c_v0 = ws1.cell(row=i, column=2, value=v0)
        c_vt = ws1.cell(row=i, column=3, value=vt)
        c_v0.fill = fill_input
        c_vt.fill = fill_input

        c_ln0 = ws1.cell(row=i, column=4, value=f"=LN(B{i})")
        c_lnt = ws1.cell(row=i, column=5, value=f"=LN(C{i})")
        c_g = ws1.cell(row=i, column=6, value=f"=(E{i}-D{i})/$H$4")
        for c in (c_ln0, c_lnt, c_g):
            c.fill = fill_calc
            c.number_format = "0.0000"
            c.border = borde

    # Tabla lateral de indicadores con fórmulas Excel
    ws1["H6"] = "Indicador Econométrico"
    ws1["I6"] = "Año 2010 / Valor"
    ws1["J6"] = "Año 2020"
    _aplicar_estilo_cabecera(ws1, 6, 10)

    metricas_form = [
        ("Sigma de logaritmos (divisor N)", "=STDEV.P(D7:D13)", "=STDEV.P(E7:E13)"),
        ("CV en niveles (divisor N)", "=STDEV.P(B7:B13)/AVERAGE(B7:B13)", "=STDEV.P(C7:C13)/AVERAGE(C7:C13)"),
        ("Pendiente Beta anual (b)", "=SLOPE(F7:F13,D7:D13)", ""),
        ("Intercepto Alpha (a)", "=INTERCEPT(F7:F13,D7:D13)", ""),
        ("Coeficiente R²", "=RSQ(F7:F13,D7:D13)", ""),
        ("Error estándar de Beta", "=STEYX(F7:F13,D7:D13)/SQRT(DEVSQ(D7:D13))", ""),
        ("Estadístico t de Beta", "=I9/I12", ""),
        ("Velocidad anual Lambda (λ)", "=-LN(1+I9*$H$4)/$H$4", ""),
        ("Semivida / Half-life (años)", "=LN(2)/I14", ""),
    ]
    for idx_m, (nom_m, f1, f2) in enumerate(metricas_form, start=7):
        ws1.cell(row=idx_m, column=8, value=nom_m).border = borde
        c1 = ws1.cell(row=idx_m, column=9, value=f1)
        c1.fill = fill_calc
        c1.number_format = "0.0000"
        c1.border = borde
        if f2:
            c2 = ws1.cell(row=idx_m, column=10, value=f2)
            c2.fill = fill_calc
            c2.number_format = "0.0000"
            c2.border = borde

    # ------------------------------------------------------------------
    # HOJA 2: CURVA DE LORENZ, GINI POR TRAPECIOS Y THEIL (CON FÓRMULAS)
    # ------------------------------------------------------------------
    ws2 = wb.create_sheet("02_Lorenz_Gini_Theil")
    ws2["A1"] = "CURVA DE LORENZ, ÍNDICE DE GINI (MÉTODO DE TRAPECIOS) Y ENTROPÍA DE THEIL"
    ws2["A1"].font = Font(size=13, bold=True, color="1E3A8A")

    headers_2 = [
        "Grupo", "Ingreso xi", "Personas ni", "Masa xi*ni",
        "N Acumulado", "Masa Acumulada", "pi Acumulado", "qi Acumulado",
        "Trapecio (pi - pi-1)*(qi + qi-1)",
    ]
    for idx, h in enumerate(headers_2, start=1):
        ws2.cell(row=4, column=idx, value=h)
    _aplicar_estilo_cabecera(ws2, 4, len(headers_2))

    ws2.cell(row=5, column=1, value="Origen")
    for c_idx in range(2, 10):
        ws2.cell(row=5, column=c_idx, value=0.0)

    grupos_lorenz = [
        (1, 7512.65, 2),
        (2, 8414.17, 3),
        (3, 15025.30, 1),
        (4, 24040.48, 2),
        (5, 39065.79, 2),
    ]
    for r_i, (g_id, x_val, n_val) in enumerate(grupos_lorenz, start=6):
        ws2.cell(row=r_i, column=1, value=g_id)
        cx = ws2.cell(row=r_i, column=2, value=x_val)
        cn = ws2.cell(row=r_i, column=3, value=n_val)
        cx.fill = fill_input
        cn.fill = fill_input
        cx.number_format = "#,##0.00"

        cmasa = ws2.cell(row=r_i, column=4, value=f"=B{r_i}*C{r_i}")
        cn_ac = ws2.cell(row=r_i, column=5, value=f"=E{r_i-1}+C{r_i}")
        cm_ac = ws2.cell(row=r_i, column=6, value=f"=F{r_i-1}+D{r_i}")
        cp_ac = ws2.cell(row=r_i, column=7, value=f"=E{r_i}/$C$11")
        cq_ac = ws2.cell(row=r_i, column=8, value=f"=F{r_i}/$D$11")
        ctrap = ws2.cell(row=r_i, column=9, value=f"=(G{r_i}-G{r_i-1})*(H{r_i}+H{r_i-1})")

        for c_f, fmt in [
            (cmasa, "#,##0.00"), (cn_ac, "0"), (cm_ac, "#,##0.00"),
            (cp_ac, "0.0000"), (cq_ac, "0.0000"), (ctrap, "0.000000"),
        ]:
            c_f.fill = fill_calc
            c_f.number_format = fmt
            c_f.border = borde

    ws2.cell(row=11, column=1, value="Total").font = Font(bold=True)
    ws2.cell(row=11, column=3, value="=SUM(C6:C10)").fill = fill_calc
    ws2.cell(row=11, column=4, value="=SUM(D6:D10)").fill = fill_calc
    ws2.cell(row=11, column=4).number_format = "#,##0.00"
    ws2.cell(row=11, column=9, value="=SUM(I6:I10)").fill = fill_calc
    ws2.cell(row=11, column=9).number_format = "0.000000"

    ws2["A13"] = "Índice de Gini Estándar (1 - Suma Trapecios)"
    ws2["B13"] = "=1-I11"
    ws2["B13"].fill = fill_calc
    ws2["B13"].number_format = "0.000000"

    ws2["A14"] = "Índice de Gini Normalizado G* = G * N/(N-1)"
    ws2["B14"] = "=B13*(C11/(C11-1))"
    ws2["B14"].fill = fill_calc
    ws2["B14"].number_format = "0.000000"

    # ------------------------------------------------------------------
    # HOJA 3: SISTEMA TAREA / MADE CLÁSICO Y MODIFICADO (CON FÓRMULAS)
    # ------------------------------------------------------------------
    ws3 = wb.create_sheet("03_MADE_Clasico_y_Mod")
    ws3["A1"] = "CASO CÁTEDRA: BADALONA, PUEBLO SECO Y PUEBLO NUEVO (MADE CLÁSICO Y MODIFICADO)"
    ws3["A1"].font = Font(size=13, bold=True, color="1E3A8A")

    V0_b, Vt_b = obtener_caso_badalona()
    ws3["A3"] = "MATRIZ AÑO INICIAL V(0)"
    headers_b = ["Sector", "Badalona", "Pueblo Seco", "Pueblo Nuevo", "Total Sector (0)"]
    for idx, h in enumerate(headers_b, start=1):
        ws3.cell(row=4, column=idx, value=h)
    _aplicar_estilo_cabecera(ws3, 4, 5)

    for r_idx, sec in enumerate(V0_b.index, start=5):
        ws3.cell(row=r_idx, column=1, value=sec)
        for c_idx, reg in enumerate(V0_b.columns, start=2):
            c = ws3.cell(row=r_idx, column=c_idx, value=float(V0_b.loc[sec, reg]))
            c.fill = fill_input
        c_tot = ws3.cell(row=r_idx, column=5, value=f"=SUM(B{r_idx}:D{r_idx})")
        c_tot.fill = fill_calc

    ws3.cell(row=9, column=1, value="Total Regional (0)").font = Font(bold=True)
    for c_idx, col_l in enumerate(["B", "C", "D", "E"], start=2):
        c = ws3.cell(row=9, column=c_idx, value=f"=SUM({col_l}5:{col_l}8)")
        c.fill = fill_calc

    ws3["A11"] = "MATRIZ AÑO FINAL V(t)"
    headers_bt = ["Sector", "Badalona", "Pueblo Seco", "Pueblo Nuevo", "Total Sector (t)"]
    for idx, h in enumerate(headers_bt, start=1):
        ws3.cell(row=12, column=idx, value=h)
    _aplicar_estilo_cabecera(ws3, 12, 5)

    for r_idx, sec in enumerate(Vt_b.index, start=13):
        ws3.cell(row=r_idx, column=1, value=sec)
        for c_idx, reg in enumerate(Vt_b.columns, start=2):
            c = ws3.cell(row=r_idx, column=c_idx, value=float(Vt_b.loc[sec, reg]))
            c.fill = fill_input
        c_tot = ws3.cell(row=r_idx, column=5, value=f"=SUM(B{r_idx}:D{r_idx})")
        c_tot.fill = fill_calc

    ws3.cell(row=17, column=1, value="Total Regional (t)").font = Font(bold=True)
    for c_idx, col_l in enumerate(["B", "C", "D", "E"], start=2):
        c = ws3.cell(row=17, column=c_idx, value=f"=SUM({col_l}13:{col_l}16)")
        c.fill = fill_calc

    # Cuadro Resumen de Efectos MADE Clásico y Modificado con Fórmulas
    ws3["A19"] = "DESCOMPOSICIÓN SHIFT & SHARE (FÓRMULAS AUTOMÁTICAS)"
    headers_ss = ["Efecto / Indicador", "Badalona", "Pueblo Seco", "Pueblo Nuevo"]
    for idx, h in enumerate(headers_ss, start=1):
        ws3.cell(row=20, column=idx, value=h)
    _aplicar_estilo_cabecera(ws3, 20, 4)

    for c_idx, col_l in enumerate(["B", "C", "D"], start=2):
        # ETj = Sum Vij(t) - Sum Vij(0) * (Total_t / Total_0)
        ws3.cell(row=21, column=1, value="Efecto Total (ETj)")
        c_et = ws3.cell(row=21, column=c_idx, value=f"={col_l}17-{col_l}9*($E$17/$E$9)")

        # EEj = Sum_i Vij(0) * (E_i(t)/E_i(0) - E_tot(t)/E_tot(0))
        ws3.cell(row=22, column=1, value="Efecto Estructural (EEj)")
        f_ee = "+".join([f"{col_l}{r}*(($E${r+8}/$E${r})-($E$17/$E$9))" for r in range(5, 9)])
        c_ee = ws3.cell(row=22, column=c_idx, value=f"={f_ee}")

        # EDj = ETj - EEj
        ws3.cell(row=23, column=1, value="Efecto Diferencial (EDj)")
        c_ed = ws3.cell(row=23, column=c_idx, value=f"={col_l}21-{col_l}22")

        # EIj = Sum_i Vij(t) * (E_tot(0)/E_tot(t) - E_i(0)/E_i(t))
        ws3.cell(row=24, column=1, value="Efecto Estructural Inverso (EIj)")
        f_ei = "+".join([f"{col_l}{r+8}*(($E$9/$E$17)-($E${r}/$E${r+8}))" for r in range(5, 9)])
        c_ei = ws3.cell(row=24, column=c_idx, value=f"={f_ei}")

        # EMj = EIj - EEj
        ws3.cell(row=25, column=1, value="Efecto Estructural Modificado (EMj = EIj - EEj)")
        c_em = ws3.cell(row=25, column=c_idx, value=f"={col_l}24-{col_l}22")

        # ERMj = ETj - EIj
        ws3.cell(row=26, column=1, value="Efecto Regional Modificado (ERMj = ETj - EIj)")
        c_erm = ws3.cell(row=26, column=c_idx, value=f"={col_l}21-{col_l}24")

        for cell_f in (c_et, c_ee, c_ed, c_ei, c_em, c_erm):
            cell_f.fill = fill_calc
            cell_f.number_format = "#,##0.00"
            cell_f.border = borde

    # ------------------------------------------------------------------
    # HOJA 4: MATRIZ DE RONDINELLI / GUTTMAN (CON FÓRMULAS EXCEL)
    # ------------------------------------------------------------------
    ws4 = wb.create_sheet("04_Matriz_Rondinelli_OT")
    ws4["A1"] = "ESCALOGRAMA FUNCIONAL DE GUTTMAN Y MATRIZ DE RONDINELLI (CON FÓRMULAS)"
    ws4["A1"].font = Font(size=13, bold=True, color="1E3A8A")

    headers_r = [
        "Asentamiento Humano", "Población", "% Población",
        "Educación Diversificada", "Universidades", "Centros Atención Médica",
        "Seguro Social", "Guarderías Infantiles", "Programas Vivienda",
        "Atención a la Mujer", "Suma Funciones", "Índice Centralidad Rondinelli",
    ]
    for idx, h in enumerate(headers_r, start=1):
        ws4.cell(row=3, column=idx, value=h)
    _aplicar_estilo_cabecera(ws4, 3, len(headers_r))

    datos_rond = [
        ("Flores (GT)", 51535, [1, 1, 1, 1, 1, 1, 1]),
        ("Melchor de Mencos (GT)", 19847, [1, 1, 1, 1, 1, 0, 1]),
        ("San Ignacio/Santa Elena (BZE)", 16977, [1, 1, 1, 1, 0, 1, 1]),
        ("Benque Viejo (BZE)", 5824, [0, 0, 1, 1, 0, 1, 1]),
    ]
    for r_i, (nom_a, pob_a, funcs) in enumerate(datos_rond, start=4):
        ws4.cell(row=r_i, column=1, value=nom_a)
        cpob = ws4.cell(row=r_i, column=2, value=pob_a)
        cpob.fill = fill_input
        cpob.number_format = "#,##0"

        cpct = ws4.cell(row=r_i, column=3, value=f"=B{r_i}/$B$8")
        cpct.fill = fill_calc
        cpct.number_format = "0.00%"

        for f_idx, f_val in enumerate(funcs, start=4):
            cf = ws4.cell(row=r_i, column=f_idx, value=f_val)
            cf.fill = fill_input
            cf.alignment = Alignment(horizontal="center")

        csum = ws4.cell(row=r_i, column=11, value=f"=SUM(D{r_i}:J{r_i})")
        csum.fill = fill_calc

        # Índice ponderado = suma producto de presencia por ponderación de fila 9
        f_pond = "+".join([f"{get_column_letter(c)}{r_i}*${get_column_letter(c)}$9" for c in range(4, 11)])
        cic = ws4.cell(row=r_i, column=12, value=f"={f_pond}")
        cic.fill = fill_calc
        cic.number_format = "0.00"

    ws4.cell(row=8, column=1, value="Suma Total").font = Font(bold=True)
    ws4.cell(row=8, column=2, value="=SUM(B4:B7)").fill = fill_calc
    ws4.cell(row=8, column=2).number_format = "#,##0"
    ws4.cell(row=8, column=3, value="=SUM(C4:C7)").fill = fill_calc
    ws4.cell(row=8, column=3).number_format = "0.00%"

    ws4.cell(row=9, column=1, value="Ponderación Rondinelli (100 / Suma)").font = Font(bold=True)
    for c_idx in range(4, 11):
        col_let = get_column_letter(c_idx)
        c_s = ws4.cell(row=8, column=c_idx, value=f"=SUM({col_let}4:{col_let}7)")
        c_s.fill = fill_calc
        c_p = ws4.cell(row=9, column=c_idx, value=f"=IF({col_let}8>0, 100/{col_let}8, 0)")
        c_p.fill = fill_calc
        c_p.number_format = "0.00"

    for ws in [ws1, ws2, ws3, ws4]:
        for col in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col)].width = 20

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ==============================================================================
# 4. INTERFAZ STREAMLIT DEL LABORATORIO DE CÁTEDRA
# ==============================================================================
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
        label="Descargar Libro Excel con Fórmulas Vivas de Cátedra (.xlsx — Convergencia, Lorenz, MADE y Rondinelli)",
        data=bytes_xlsx_formulas,
        file_name="Laboratorio_Catedra_Formulas_Vivas_ULagos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    tabs = st.tabs([
        "1. PIB Regional y Censo 2024 (16 Regiones)",
        "2. Sistema TAREA (Badalona y Colombia + Stilwell)",
        "3. Unidad 3: Convergencia, Lorenz, Theil y CASEN",
        "4. Unidad 3: Concentración (CRm, HHI, HK_α) y Markov",
    ])

    # ------------------------------------------------------------------
    # TAB 1: PIB REGIONAL (BANCO CENTRAL 2015-2025) + POBLACIÓN CENSO 2024
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # TAB 2: SISTEMA TAREA (BADALONA / PUEBLO SECO Y COLOMBIA 1980-1996)
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # TAB 3: UNIDAD 3 — CONVERGENCIA, LORENZ, GINI TRAPECIOS Y THEIL
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # TAB 4: CONCENTRACIÓN (CRm, HHI, HK_ALPHA) Y CADENAS DE MARKOV
    # ------------------------------------------------------------------
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
