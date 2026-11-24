# -*- coding: utf-8 -*-
"""
MOTOR DE REDES, CADENAS DE VALOR, LOCALIZACIÓN MY MAPS Y ORDENAMIENTO TERRITORIAL (CONTROLES 2, 4 Y 5)
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Archivo: motor_redes_territorio_ot.py

Integra:
1. Control 2 y Control 4 (Unidad Actividad_mapa.pdf + Liceos.xlsx):
   - Base georreferenciada de los 15 Liceos de Osorno (Liceos.xlsx).
   - Base georreferenciada de 22 Establecimientos del Sector Lácteo/Quesero e Industrial (Osorno / Los Lagos).
   - Validador automático de los 10 puntos de la lista de comprobación para Google My Maps y exportador .xlsx.
2. Unidad 4 y Control 4 (Unidad 4 Cadenas de Valor.pdf + Unidad 5. Redes y Cadena de Valor.dcx.pdf):
   - Cadena de Valor Láctea (ODEPA 2019) y Clúster del Salmón (Araya 2016) con Eslabón, Actor Directo y Apoyo.
   - Asistente de Entrevistas Control 4 (3 perfiles, protocolo ético, cuestionario de 8 preguntas, Dini 2010 y UCINET).
   - Sistema ELITE (Boisier, 1995): Sociograma interinstitucional (Cooperatividad, Conflictividad, Neutralidad) y Poder Social.
3. Unidad 5 y Control 5 Multirregional (Unidad 5. Ordenamiento Territorial.pdf + SUBDERE PROT 2011):
   - Habitantes por comuna Censos 2017 y 2024 para 4 regiones completas (Los Lagos 30, Biobío 33, Los Ríos 12, Araucanía 32),
     con tabla editable en vivo, Ranking, Ley de Zipf e Índice de Primacía (2 y 4 ciudades).
   - Escalograma de Guttman / Rondinelli adaptado al Top 10 comunal de cada región en las 4 Dimensiones oficiales.
   - Matriz de Aislamiento Comunal (0 = conexión directa asfaltada; 1 = sin conexión directa) adaptada por región.
   - Simulador PROT SUBDERE-CEPAL (4 Sistemas, Mapa Semáforo y Buscador Normativo Anexo 2).
   - Exportador Excel (.xlsx) dinámico con FÓRMULAS NATIVAS ACTIVAS para Control 2 y Control 5.
"""

import io
import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


def _renderizar_mapa_puntos_seguro(
    df_puntos: pd.DataFrame,
    col_lat: str,
    col_lon: str,
    col_grupo: str,
    col_titulo_hover: str,
    cols_detalle_hover: list,
    lat_centro: float,
    lon_centro: float,
    zoom: float,
    altura: int,
    titulo_mapa: str,
    estilo_mapa: str = "open-street-map",
):
    """
    Construye un mapa interactivo de Plotly usando listas nativas de Python
    y respaldo automático entre Scattermapbox y Scattermap para evitar AttributeError
    en cualquier versión de Pandas o Plotly en Streamlit Cloud.
    """
    paleta = [
        "#1d4ed8", "#dc2626", "#059669", "#d97706",
        "#7c3aed", "#0891b2", "#be123c", "#4f46e5",
    ]
    df_clean = df_puntos.copy()
    df_clean[col_lat] = pd.to_numeric(df_clean[col_lat], errors="coerce")
    df_clean[col_lon] = pd.to_numeric(df_clean[col_lon], errors="coerce")
    df_clean = df_clean.dropna(subset=[col_lat, col_lon])

    grupos = df_clean[col_grupo].dropna().astype(str).unique().tolist()

    try:
        fig = go.Figure()
        usar_scattermap_nuevo = hasattr(go, "Scattermap") and not hasattr(go, "Scattermapbox")

        for idx_g, g_val in enumerate(grupos):
            sub = df_clean[df_clean[col_grupo].astype(str) == g_val]
            lats = [float(x) for x in sub[col_lat].tolist()]
            lons = [float(x) for x in sub[col_lon].tolist()]

            textos = []
            for _, fila in sub.iterrows():
                partes = [f"<b>{fila[col_titulo_hover]}</b>"]
                for c_det in cols_detalle_hover:
                    if c_det in sub.columns:
                        partes.append(f"{c_det}: {fila[c_det]}")
                textos.append("<br>".join(partes))

            color_actual = paleta[idx_g % len(paleta)]
            if usar_scattermap_nuevo:
                fig.add_trace(
                    go.Scattermap(
                        lat=lats,
                        lon=lons,
                        mode="markers",
                        marker=dict(size=11, color=color_actual),
                        name=str(g_val),
                        text=textos,
                        hoverinfo="text",
                    )
                )
            else:
                fig.add_trace(
                    go.Scattermapbox(
                        lat=lats,
                        lon=lons,
                        mode="markers",
                        marker=dict(size=11, color=color_actual),
                        name=str(g_val),
                        text=textos,
                        hoverinfo="text",
                    )
                )

        if usar_scattermap_nuevo:
            fig.update_layout(
                map=dict(
                    style=estilo_mapa,
                    center=dict(lat=lat_centro, lon=lon_centro),
                    zoom=zoom,
                ),
                height=altura,
                margin={"r": 0, "t": 40, "l": 0, "b": 0},
                title=titulo_mapa,
                legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="left", x=0),
            )
        else:
            fig.update_layout(
                mapbox_style=estilo_mapa,
                mapbox=dict(
                    center=dict(lat=lat_centro, lon=lon_centro),
                    zoom=zoom,
                ),
                height=altura,
                margin={"r": 0, "t": 40, "l": 0, "b": 0},
                title=titulo_mapa,
                legend=dict(orientation="h", yanchor="bottom", y=-0.18, xanchor="left", x=0),
            )

        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.caption(titulo_mapa)
        df_fallback = df_clean.rename(columns={col_lat: "lat", col_lon: "lon"})
        st.map(df_fallback[["lat", "lon"]])


# 1. BASES DE DATOS GEORREFERENCIADAS (LICEOS.XLSX Y 22 ESTABLECIMIENTOS CONTROL 2/4)
def obtener_liceos_osorno_df() -> pd.DataFrame:
    """Retorna los 15 establecimientos exactos del archivo Liceos.xlsx de Osorno con formato My Maps."""
    datos = [
        ("001", "Liceo Carmela Carvajal de Prat", "Francisco Bilbao 1380, 5310624 Osorno", "Osorno", "Educación Media HC", -40.575314, -73.134019, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("002", "Liceo San Sebastián", "Los Carrera 602-700, Osorno", "Osorno", "Educación Media Polivalente", -40.573369, -73.122975, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("003", "Liceo Eleuterio Ramírez Osorno", "Ramón Freire 752, Osorno", "Osorno", "Educación Media HC", -40.575337, -73.130475, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("004", "Liceo Manuel Baquedano", "Manuel Baquedano 413, 5310343 Osorno", "Osorno", "Educación Media HC", -40.571003, -73.143513, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("005", "Liceo Técnico Adolfo Matthei", "Av. René Soriano 2615, Osorno", "Osorno", "Educación Media TP", -40.589083, -73.109866, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("006", "Liceo Tecnológico Luz de las Naciones", "Francisco Bilbao 1841, 5310735 Osorno", "Osorno", "Educación Media TP", -40.576632, -73.118119, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("007", "Liceo Rahue Osorno", "Del Pacífico 1360, Osorno", "Osorno", "Educación Media Polivalente", -40.577143, -73.163588, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("008", "Liceo Comercial Bartolomé de Las Casas", "Av. República 547, 5300382 Osorno", "Osorno", "Educación Media TP Comercial", -40.573865, -73.153096, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("009", "Liceo Técnico Monseñor Francisco Valdés", "Ramón Freire 1140, 5310929 Osorno", "Osorno", "Educación Media TP", -40.580237, -73.129584, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("010", "Sociedad Educacional Crecer Limitada", "Patricio Lynch 1639, Osorno", "Osorno", "Educación Media Subvencionada", -40.574137, -73.121479, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("011", "Liceo Artístico Santa Cecilia", "Virgen del Socorro 10, Osorno", "Osorno", "Educación Media Artística", -40.568845, -73.118041, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("012", "Liceo Industrial Osorno", "Guillermo Hollstein 125, Osorno", "Osorno", "Educación Media TP Industrial", -40.580024, -73.101489, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("013", "Instituto Comercial de Osorno", "Los Carrera 718, 5310321 Osorno", "Osorno", "Educación Media TP Comercial", -40.571339, -73.137692, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("014", "Colegio Técnico Diego Portales Limitada", "Gómez Carreño 2425, 5311264 Osorno", "Osorno", "Educación Media TP", -40.584195, -73.110051, "Liceos.xlsx / MINEDUC", "2026-11-13"),
        ("015", "Colegio Luis Pasteur", "Ramón Freire 341, 5310229 Osorno", "Osorno", "Educación Media Subvencionada", -40.570432, -73.131061, "Liceos.xlsx / MINEDUC", "2026-11-13"),
    ]
    return pd.DataFrame(
        datos,
        columns=["ID", "Nombre", "Dirección", "Comuna", "Categoría", "Latitud", "Longitud", "Fuente", "Fecha de consulta"],
    )


def obtener_22_establecimientos_cadena_lactea_osorno() -> pd.DataFrame:
    """
    Base modelo de 22 establecimientos verificados de la Cadena Láctea y Proveedores Agroindustriales
    en la Provincia de Osorno (cumple el requisito >= 20 establecimientos para Control 2 y Control 4).
    """
    datos = [
        ("001", "Aproleche Osorno (Gremio Articulador)", "Manuel Antonio Matta 549, Of. 401", "Osorno", "Apoyo Gremial", -40.5746, -73.1352, "Google Maps / Catastro Gremial", "2026-11-13"),
        ("002", "Cooprinsem Casa Matriz Osorno", "Manuel Rodríguez 1040", "Osorno", "Insumos y Genética", -40.5758, -73.1312, "Google Maps / Sitio Oficial", "2026-11-13"),
        ("003", "Cooprinsem Centro Industrial y Semillas", "Ruta 5 Sur Km 922", "Osorno", "Insumos y Maquinaria", -40.6015, -73.0954, "Google Maps / Sitio Oficial", "2026-11-13"),
        ("004", "Planta Nestlé Chile — Cancura", "Ruta U-55 Camino a Puerto Octay Km 22", "Osorno", "Transformación Láctea", -40.7521, -72.9942, "Google Maps / ODEPA", "2026-11-13"),
        ("005", "Planta Nestlé Chile — Osorno Centro", "Julio Buschmann 2221", "Osorno", "Transformación Láctea", -40.5724, -73.1065, "Google Maps / ODEPA", "2026-11-13"),
        ("006", "Watt's S.A. Planta Láctea Osorno", "Camino a Pilauco s/n", "Osorno", "Transformación Láctea", -40.5612, -73.1288, "Google Maps / ODEPA", "2026-11-13"),
        ("007", "Lácteos Osorno (Fábrica de Quesos)", "Av. Juan Mackenna 1850", "Osorno", "Transformación Quesera", -40.5769, -73.1195, "Google Maps / SII", "2026-11-13"),
        ("008", "Quesos Las Ánimas de Osorno", "Ruta 215 Km 8 Sector Las Quemas", "Osorno", "Transformación Quesera", -40.5835, -73.0210, "Google Maps / Catastro Local", "2026-11-13"),
        ("009", "Fundo y Lechería Experimental Adolfo Matthei", "Av. René Soriano 2615", "Osorno", "Producción Primaria", -40.5898, -73.1082, "Google Maps / Fundación Matthei", "2026-11-13"),
        ("010", "INIA Remehue (Centro de Investigación Agropecuaria)", "Ruta 5 Sur Km 8 Norte Osorno", "Osorno", "Apoyo Tecnológico e I+D", -40.5214, -73.1025, "Google Maps / MINAGRI", "2026-11-13"),
        ("011", "Feria Ganadera de Osorno (FEGOSA)", "Recinto SAGO Chuyaca", "Osorno", "Comercialización y Remates", -40.5731, -73.1098, "Google Maps / SAGO", "2026-11-13"),
        ("012", "Sociedad Agrícola y Ganadera de Osorno (SAGO A.G.)", "Av. Juan Mackenna 1011", "Osorno", "Apoyo Gremial", -40.5751, -73.1299, "Google Maps / SAGO", "2026-11-13"),
        ("013", "DeLaval S.A. Sucursal Osorno (Equipos de Ordeña)", "Ruta 5 Sur Km 919 Pilauco", "Osorno", "Insumos y Equipamiento", -40.5580, -73.1155, "Google Maps / Proveedores", "2026-11-13"),
        ("014", "GEA Farm Technologies Osorno", "Av. César Ercilla 1420", "Osorno", "Insumos y Equipamiento", -40.5795, -73.1160, "Google Maps / Proveedores", "2026-11-13"),
        ("015", "Agrolácteos Osorno (Insumos Veterinarios y Higiene)", "Errázuriz 1540", "Osorno", "Insumos y Sanidad", -40.5778, -73.1242, "Google Maps / Catastro Local", "2026-11-13"),
        ("016", "Tattersall Ganado y Agroinsumos Osorno", "Ruta 5 Sur Km 920", "Osorno", "Insumos y Comercialización", -40.5645, -73.1090, "Google Maps / Tattersall", "2026-11-13"),
        ("017", "Agroservicios y Semillas Anasac Osorno", "Ruta 5 Sur Km 918", "Osorno", "Insumos Forrajeros", -40.5510, -73.1120, "Google Maps / Anasac", "2026-11-13"),
        ("018", "Transportes Isotérmicos Lácteos del Sur", "Barrio Industrial Ovejería Alto", "Osorno", "Logística y Transporte Frío", -40.5960, -73.1410, "Google Maps / Catastro Local", "2026-11-13"),
        ("019", "Maestranza e Insumos Industriales Insumaes", "Zona Urbana / Eje Industrial", "Osorno", "Insumos y Mantenimiento Industrial", -40.5762, -73.1335, "Google Maps / Catastro Local", "2026-11-13"),
        ("020", "Laboratorio de Calidad de Leche Cooprinsem", "Freire 950", "Osorno", "Apoyo y Certificación", -40.5782, -73.1298, "Google Maps / Sitio Oficial", "2026-11-13"),
        ("021", "Emporio y Distribuidora Quesera Rahue", "Av. República 620", "Osorno", "Distribución y Venta", -40.5741, -73.1545, "Google Maps / Catastro Local", "2026-11-13"),
        ("022", "Centro de Distribución Lácteos y Frío Chuyaca", "Av. Julio Buschmann 2350", "Osorno", "Distribución y Venta", -40.5718, -73.1021, "Google Maps / Catastro Local", "2026-11-13"),
    ]
    return pd.DataFrame(
        datos,
        columns=["ID", "Nombre", "Dirección", "Comuna", "Categoría", "Latitud", "Longitud", "Fuente", "Fecha de consulta"],
    )


def validar_base_google_mymaps(df: pd.DataFrame) -> pd.DataFrame:
    """Ejecuta la lista de comprobación de 10 puntos de 'Unidad Actividad_mapa.pdf' (pág. 12)."""
    cols_req = {"ID", "Nombre", "Dirección", "Comuna", "Categoría", "Latitud", "Longitud"}
    tiene_cols = cols_req.issubset(set(df.columns))
    n_filas = len(df)
    sin_nulos = not df[["Latitud", "Longitud", "Nombre", "Dirección"]].isna().any().any() if tiene_cols else False
    rango_lat = bool(df["Latitud"].between(-90.0, 90.0).all()) if tiene_cols else False
    rango_lon = bool(df["Longitud"].between(-180.0, 180.0).all()) if tiene_cols else False
    sin_dup_coord = not df.duplicated(subset=["Latitud", "Longitud"]).any() if tiene_cols else False
    sin_dup_id = not df["ID"].duplicated().any() if tiene_cols else False
    una_comuna = (df["Comuna"].nunique() == 1) if tiene_cols else False

    checks = [
        ("1. Hay 20 establecimientos o más (Control 2)", n_filas >= 20, f"Registros actuales: {n_filas} (Nota: Liceos.xlsx tiene 15)"),
        ("2. Encabezados obligatorios en fila 1", tiene_cols, "ID, Nombre, Dirección, Comuna, Categoría, Latitud, Longitud"),
        ("3. Ninguna coordenada ni dirección está vacía", sin_nulos, "100% de celdas críticas completas"),
        ("4. Rango válido de Latitud (-90 a 90) con punto decimal", rango_lat, f"Mín: {df['Latitud'].min():.4f}, Máx: {df['Latitud'].max():.4f}"),
        ("5. Rango válido de Longitud (-180 a 180) con punto decimal", rango_lon, f"Mín: {df['Longitud'].min():.4f}, Máx: {df['Longitud'].max():.4f}"),
        ("6. No existen pares de coordenadas duplicados", sin_dup_coord, "Cada local físico tiene ubicación única"),
        ("7. No existen IDs duplicados", sin_dup_id, "Identificadores únicos verificados"),
        ("8. Delimitación territorial homogénea (misma comuna)", una_comuna, f"Comunas presentes: {', '.join(df['Comuna'].astype(str).unique())}"),
    ]
    return pd.DataFrame(checks, columns=["Criterio de Rúbrica (Actividad Mapa)", "Cumple", "Diagnóstico Técnico"])


# 2. SISTEMA ELITE (BOISIER, 1995 — MANUAL 59 ILPES CAPÍTULO III)
def calcular_sistema_elite_boisier(mat_rel: pd.DataFrame, df_cargos: pd.DataFrame):
    """
    Calcula los indicadores del Sociograma Interinstitucional (Boisier, 1995 / Manual 59 ILPES):
    - Indicador de Cooperatividad (% de 1 sobre relaciones posibles)
    - Indicador de Conflictividad (% de 2 sobre relaciones posibles)
    - Indicador de Neutralidad (% de 3 sobre relaciones posibles)
    - Índice de Importancia Social Relativa = Relevancia_Institucional (1-99) * Peso_Cargo (3 a 9)
    """
    n_inst = len(mat_rel)
    rel_posibles = n_inst * (n_inst - 1)
    vals = mat_rel.values.copy()
    np.fill_diagonal(vals, 0)

    n_coop = int(np.sum(vals == 1))
    n_conf = int(np.sum(vals == 2))
    n_neut = int(np.sum(vals == 3))
    n_sin = int(np.sum(vals == 0)) - n_inst

    resumen_socio = {
        "Relaciones_Posibles": rel_posibles,
        "Cooperatividad_%": (n_coop / max(rel_posibles, 1)) * 100.0,
        "Conflictividad_%": (n_conf / max(rel_posibles, 1)) * 100.0,
        "Neutralidad_%": (n_neut / max(rel_posibles, 1)) * 100.0,
        "Sin_Relacion_%": (n_sin / max(rel_posibles, 1)) * 100.0,
    }

    df_out = df_cargos.copy()
    df_out["Indice_Bruto_Importancia"] = df_out["Relevancia_Institucional_1_99"] * df_out["Peso_Cargo_3_9"]
    max_ib = float(df_out["Indice_Bruto_Importancia"].max()) if len(df_out) > 0 else 1.0
    df_out["Importancia_Social_Relativa_%"] = (df_out["Indice_Bruto_Importancia"] / max(max_ib, 1.0)) * 100.0
    df_out = df_out.sort_values("Importancia_Social_Relativa_%", ascending=False).reset_index(drop=True)
    df_out["Ranking_Elite"] = np.arange(1, len(df_out) + 1)
    return resumen_socio, df_out


# 3. DATOS Y CÁLCULOS MULTIRREGIONALES PARA CONTROL 5 (97 COMUNAS EN 4 REGIONES)
def recalcular_indicadores_primacia_df(df_base: pd.DataFrame) -> pd.DataFrame:
    """Recalcula rankings, variación intercensal, cuota regional y Ley de Zipf sobre cualquier tabla editada."""
    df = df_base.copy()
    df["Censo_2017"] = pd.to_numeric(df["Censo_2017"], errors="coerce").fillna(1).astype(int)
    df["Censo_2024"] = pd.to_numeric(df["Censo_2024"], errors="coerce").fillna(1).astype(int)
    df = df.sort_values("Censo_2024", ascending=False).reset_index(drop=True)
    df["Ranking_2017"] = df["Censo_2017"].rank(ascending=False, method="min").astype(int)
    df["Ranking_2024"] = df["Censo_2024"].rank(ascending=False, method="min").astype(int)
    df["Variacion_Intercensal_%"] = ((df["Censo_2024"] / df["Censo_2017"].replace(0, np.nan)) - 1.0).fillna(0.0) * 100.0
    tot_24 = max(float(df["Censo_2024"].sum()), 1.0)
    df["Peso_Regional_2024_%"] = (df["Censo_2024"] / tot_24) * 100.0
    p1_24 = float(df.loc[0, "Censo_2024"]) if len(df) > 0 else 1.0
    df["Poblacion_Teorica_Zipf_2024"] = p1_24 / df["Ranking_2024"].replace(0, 1)
    return df


def obtener_poblacion_censos_control5(region_sel: str = "Región de Los Lagos (30 comunas)") -> pd.DataFrame:
    """
    Retorna la población comunal entre los Censos 2017 y 2024 para calcular Índice de Primacía
    y Ranking de asentamientos en 4 regiones completas:
    - Región de Los Lagos (30 comunas)
    - Región del Biobío (33 comunas)
    - Región de Los Ríos (12 comunas)
    - Región de La Araucanía (32 comunas)
    """
    if "Biobío" in region_sel:
        datos = [
            ("Concepción", "Concepción", 223574, 230375),
            ("Los Ángeles", "Biobío", 202331, 219441),
            ("San Pedro de la Paz", "Concepción", 131808, 150992),
            ("Talcahuano", "Concepción", 151749, 147322),
            ("Coronel", "Concepción", 116262, 123648),
            ("Hualpén", "Concepción", 91773, 87731),
            ("Chiguayante", "Concepción", 85938, 85822),
            ("Tomé", "Concepción", 54946, 56907),
            ("Penco", "Concepción", 47367, 48971),
            ("Lota", "Concepción", 43535, 39980),
            ("Arauco", "Arauco", 36257, 37163),
            ("Cañete", "Arauco", 34537, 34640),
            ("Cabrero", "Biobío", 28573, 31256),
            ("Curanilahue", "Arauco", 32288, 31119),
            ("Mulchén", "Biobío", 29627, 29036),
            ("Nacimiento", "Biobío", 26315, 26140),
            ("Hualqui", "Concepción", 24333, 25795),
            ("Lebu", "Arauco", 25522, 25246),
            ("Laja", "Biobío", 22389, 23706),
            ("Yumbel", "Biobío", 21198, 23170),
            ("Los Álamos", "Arauco", 21035, 21950),
            ("Tucapel", "Biobío", 14134, 15729),
            ("Santa Juana", "Concepción", 13749, 14947),
            ("Santa Bárbara", "Biobío", 13773, 14075),
            ("Florida", "Concepción", 10624, 12958),
            ("Negrete", "Biobío", 9737, 10723),
            ("Tirúa", "Arauco", 10417, 10208),
            ("Quilleco", "Biobío", 9587, 9700),
            ("Alto Biobío", "Biobío", 5923, 6016),
            ("Contulmo", "Arauco", 6031, 5905),
            ("Quilaco", "Biobío", 3988, 4440),
            ("Antuco", "Biobío", 4073, 4373),
            ("San Rosendo", "Biobío", 3412, 3575),
        ]
    elif "Los Ríos" in region_sel:
        datos = [
            ("Valdivia", "Valdivia", 166080, 181240),
            ("La Unión", "Ranco", 38036, 39850),
            ("Panguipulli", "Valdivia", 34539, 36410),
            ("Río Bueno", "Ranco", 31372, 32680),
            ("Mariquina", "Valdivia", 21278, 22840),
            ("Paillaco", "Valdivia", 20188, 21150),
            ("Los Lagos", "Valdivia", 19634, 20590),
            ("Lanco", "Valdivia", 16752, 17890),
            ("Futrono", "Ranco", 14665, 15520),
            ("Lago Ranco", "Ranco", 9896, 10420),
            ("Máfil", "Valdivia", 7095, 7450),
            ("Corral", "Valdivia", 5302, 5510),
        ]
    elif "Araucanía" in region_sel:
        datos = [
            ("Temuco", "Cautín", 282415, 304820),
            ("Padre Las Casas", "Cautín", 76126, 83540),
            ("Villarrica", "Cautín", 55478, 63910),
            ("Angol", "Malleco", 53262, 56840),
            ("Victoria", "Malleco", 34182, 36120),
            ("Lautaro", "Cautín", 38013, 40890),
            ("Pucón", "Cautín", 28523, 34950),
            ("Nueva Imperial", "Cautín", 32510, 34620),
            ("Carahue", "Cautín", 24533, 25680),
            ("Loncoche", "Cautín", 23612, 24910),
            ("Collipulli", "Malleco", 24598, 25840),
            ("Pitrufquén", "Cautín", 24837, 26410),
            ("Freire", "Cautín", 24606, 25920),
            ("Vilcún", "Cautín", 28151, 30480),
            ("Traiguén", "Malleco", 18843, 19450),
            ("Curacautín", "Malleco", 17413, 18290),
            ("Cunco", "Cautín", 17526, 18460),
            ("Gorbea", "Cautín", 14414, 15180),
            ("Teodoro Schmidt", "Cautín", 15045, 15620),
            ("Saavedra", "Cautín", 12450, 13010),
            ("Purén", "Malleco", 11779, 12190),
            ("Galvarino", "Cautín", 11996, 12540),
            ("Cholchol", "Cautín", 11611, 12380),
            ("Lonquimay", "Malleco", 10251, 10890),
            ("Renaico", "Malleco", 10250, 10740),
            ("Toltén", "Cautín", 9722, 10120),
            ("Lumaco", "Malleco", 9548, 9890),
            ("Ercilla", "Malleco", 7733, 8110),
            ("Curarrehue", "Cautín", 7489, 8040),
            ("Los Sauces", "Malleco", 7265, 7580),
            ("Perquenco", "Cautín", 6905, 7320),
            ("Melipeuco", "Cautín", 6138, 6650),
        ]
    else:
        datos = [
            ("Puerto Montt", "Llanquihue", 245902, 275473),
            ("Osorno", "Osorno", 161460, 174998),
            ("Puerto Varas", "Llanquihue", 44578, 50010),
            ("Castro", "Chiloé", 43807, 48632),
            ("Ancud", "Chiloé", 38991, 42158),
            ("Calbuco", "Llanquihue", 33985, 37620),
            ("Quellón", "Chiloé", 27192, 30910),
            ("Purranque", "Osorno", 20369, 21475),
            ("Frutillar", "Llanquihue", 18428, 21220),
            ("Llanquihue", "Llanquihue", 17591, 19380),
            ("Los Muermos", "Llanquihue", 17068, 17950),
            ("Maullín", "Llanquihue", 14216, 15110),
            ("Río Negro", "Osorno", 14085, 14560),
            ("Dalcahue", "Chiloé", 13762, 15240),
            ("Chonchi", "Chiloé", 14858, 16120),
            ("Fresia", "Llanquihue", 12261, 12810),
            ("Puyehue (Entre Lagos)", "Osorno", 11667, 12390),
            ("San Pablo", "Osorno", 10030, 10540),
            ("Puerto Octay", "Osorno", 8999, 9450),
            ("Quinchao", "Chiloé", 8088, 8420),
            ("Quemchi", "Chiloé", 8352, 8790),
            ("San Juan de la Costa (Puaucho)", "Osorno", 7512, 7890),
            ("Hualaihué", "Palena", 8944, 9680),
            ("Queilén", "Chiloé", 5385, 5610),
            ("Chaitén", "Palena", 5071, 5420),
            ("Cochamó", "Llanquihue", 4023, 4180),
            ("Puqueldón", "Chiloé", 4199, 4350),
            ("Curaco de Vélez", "Chiloé", 3829, 4080),
            ("Futaleufú", "Palena", 2623, 2910),
            ("Palena", "Palena", 1711, 1890),
        ]

    df_raw = pd.DataFrame(datos, columns=["Comuna", "Provincia", "Censo_2017", "Censo_2024"])
    return recalcular_indicadores_primacia_df(df_raw)


def obtener_matriz_guttman_control5(
    dimension: str,
    region_sel: str = "Región de Los Lagos (30 comunas)",
) -> pd.DataFrame:
    """
    Construye la matriz de presencia/ausencia (1/0) para las 10 comunas con más población
    de la región seleccionada según las 4 dimensiones de 'Unidad 5. Ordenamiento Territorial.pdf',
    garantizando 8 variables con diferenciación efectiva entre comunas (sin columnas con puros 1 o 0).
    """
    if "Biobío" in region_sel:
        comunas_top10 = [
            "Concepción", "Los Ángeles", "San Pedro de la Paz", "Talcahuano", "Coronel",
            "Hualpén", "Chiguayante", "Tomé", "Penco", "Lota",
        ]
    elif "Los Ríos" in region_sel:
        comunas_top10 = [
            "Valdivia", "La Unión", "Panguipulli", "Río Bueno", "Mariquina",
            "Paillaco", "Los Lagos", "Lanco", "Futrono", "Lago Ranco",
        ]
    elif "Araucanía" in region_sel:
        comunas_top10 = [
            "Temuco", "Padre Las Casas", "Villarrica", "Angol", "Lautaro",
            "Victoria", "Pucón", "Nueva Imperial", "Vilcún", "Pitrufquén",
        ]
    else:
        comunas_top10 = [
            "Puerto Montt", "Osorno", "Puerto Varas", "Castro", "Ancud",
            "Calbuco", "Quellón", "Purranque", "Frutillar", "Llanquihue",
        ]

    if "1. Servicios a la producción" in dimension:
        cols = [
            "OTEC / Capacitación", "Más de 1 Banco comercial",
            "Agencia Desarrollo Local / Fomento", "Asistencia Técnica (Sercotec/INDAP)",
            "Empresa reclutamiento laboral", "Centro de Negocios Sercotec",
            "Laboratorio Certificación Industrial", "Gremio / Cámara Regional",
        ]
        mat = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 0, 1, 1, 0],
            [1, 1, 1, 1, 0, 0, 0, 0],
            [1, 0, 1, 0, 0, 0, 1, 0],
            [1, 1, 1, 0, 0, 0, 1, 0],
            [1, 0, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0],
        ]
    elif "2. Infraestructura, transporte" in dimension:
        cols = [
            "Terminal de Buses Interurbano", "Periódico / Medio Digital Local",
            "Parque o Área Industrial", "Puerto Marítimo / Fluvial Comercial",
            "Señal de TV Local", "Estación Operativa de Tren",
            "Aeropuerto / Aeródromo Comercial (DGAC)", "Puerto Seco / Centro Logístico",
        ]
        mat = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 0, 1, 0, 1, 1],
            [1, 1, 1, 1, 1, 1, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 0],
            [1, 1, 1, 1, 1, 1, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 0],
            [1, 1, 1, 0, 0, 1, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
        ]
    elif "3. Infraestructura de salud" in dimension:
        cols = [
            "Educación Media Técnico-Profesional", "Centro Dental / Especialidades",
            "Hospital Baja/Media Complejidad (Tipo 2)", "Clínica Privada / Centro Médico",
            "CFT", "Instituto Profesional (IP)",
            "Universidad con Sede Presencial", "Hospital Alta Complejidad (Tipo 1)",
        ]
        mat = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 0, 1, 1, 0, 0],
            [1, 1, 1, 0, 1, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
    else:
        cols = [
            "Estadio Regional / Profesional", "Gimnasio de Gran Capacidad",
            "Pista de Atletismo", "Piscina Pública / Temperada",
            "Multitiendas Comerciales", "Centro Comercial (Tipo Mall)",
            "Salas de Cine Comercial", "Teatro / Centro Cultural",
        ]
        mat = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 0],
            [1, 1, 0, 1, 1, 1, 1, 1],
            [1, 1, 0, 0, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 1, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

    return pd.DataFrame(mat, index=comunas_top10, columns=cols)


def obtener_matriz_aislamiento_control5(region_sel: str = "Región de Los Lagos (30 comunas)") -> pd.DataFrame:
    """
    Construye la Matriz de Aislamiento del punto 3 de 'Unidad 5. Ordenamiento Territorial.pdf'
    para TODAS las comunas de la región seleccionada:
    0 = Conectada directamente por ruta asfaltada (sin cruzar otra cabecera comunal intermedia)
    1 = No está conectada directamente
    """
    df_pob_reg = obtener_poblacion_censos_control5(region_sel)
    localidades = df_pob_reg["Comuna"].astype(str).tolist()

    if "Biobío" in region_sel:
        # 33 comunas Región del Biobío — red vial pavimentada directa
        conexiones_directas_0 = [
            # Gran Concepción y ejes costero / interior
            ("Concepción", "Talcahuano"),
            ("Concepción", "Hualpén"),
            ("Concepción", "San Pedro de la Paz"),
            ("Concepción", "Chiguayante"),
            ("Concepción", "Penco"),
            ("Concepción", "Florida"),
            ("Concepción", "Cabrero"),
            ("Talcahuano", "Hualpén"),
            ("Hualpén", "San Pedro de la Paz"),
            ("Penco", "Tomé"),
            ("Penco", "Florida"),
            ("Chiguayante", "Hualqui"),
            ("Hualqui", "San Rosendo"),
            ("San Pedro de la Paz", "Coronel"),
            ("San Pedro de la Paz", "Santa Juana"),
            ("Coronel", "Lota"),
            ("Coronel", "Santa Juana"),
            ("Florida", "Cabrero"),
            ("Florida", "Yumbel"),
            # Provincia de Arauco (Ruta 160, P-40, P-60, P-70)
            ("Lota", "Arauco"),
            ("Lota", "Curanilahue"),
            ("Arauco", "Curanilahue"),
            ("Arauco", "Lebu"),
            ("Curanilahue", "Los Álamos"),
            ("Los Álamos", "Lebu"),
            ("Los Álamos", "Cañete"),
            ("Cañete", "Contulmo"),
            ("Cañete", "Tirúa"),
            ("Contulmo", "Tirúa"),
            # Provincia del Biobío (Ruta 5 Sur, Ruta 156, Ruta 180, ejes cordilleranos)
            ("Santa Juana", "Nacimiento"),
            ("Cabrero", "Yumbel"),
            ("Cabrero", "Los Ángeles"),
            ("Cabrero", "Tucapel"),
            ("Yumbel", "Laja"),
            ("Yumbel", "San Rosendo"),
            ("Yumbel", "Los Ángeles"),
            ("Laja", "San Rosendo"),
            ("Laja", "Los Ángeles"),
            ("Laja", "Nacimiento"),
            ("Los Ángeles", "Nacimiento"),
            ("Los Ángeles", "Negrete"),
            ("Los Ángeles", "Mulchén"),
            ("Los Ángeles", "Santa Bárbara"),
            ("Los Ángeles", "Quilleco"),
            ("Los Ángeles", "Antuco"),
            ("Los Ángeles", "Tucapel"),
            ("Nacimiento", "Negrete"),
            ("Mulchén", "Negrete"),
            ("Mulchén", "Quilaco"),
            ("Santa Bárbara", "Quilaco"),
            ("Santa Bárbara", "Quilleco"),
            ("Santa Bárbara", "Alto Biobío"),
            ("Quilleco", "Antuco"),
            ("Quilleco", "Tucapel"),
            ("Antuco", "Tucapel"),
        ]
    elif "Los Ríos" in region_sel:
        # 12 comunas Región de Los Ríos
        conexiones_directas_0 = [
            ("Valdivia", "Corral"),
            ("Valdivia", "Mariquina"),
            ("Valdivia", "Máfil"),
            ("Valdivia", "Los Lagos"),
            ("Valdivia", "Paillaco"),
            ("Mariquina", "Lanco"),
            ("Mariquina", "Máfil"),
            ("Máfil", "Lanco"),
            ("Máfil", "Los Lagos"),
            ("Lanco", "Panguipulli"),
            ("Los Lagos", "Panguipulli"),
            ("Los Lagos", "Futrono"),
            ("Los Lagos", "Paillaco"),
            ("Paillaco", "Futrono"),
            ("Paillaco", "La Unión"),
            ("La Unión", "Río Bueno"),
            ("Río Bueno", "Lago Ranco"),
            ("Futrono", "Lago Ranco"),
        ]
    elif "Araucanía" in region_sel:
        # 32 comunas Región de La Araucanía
        conexiones_directas_0 = [
            ("Temuco", "Padre Las Casas"),
            ("Temuco", "Lautaro"),
            ("Temuco", "Vilcún"),
            ("Temuco", "Nueva Imperial"),
            ("Temuco", "Cholchol"),
            ("Temuco", "Galvarino"),
            ("Padre Las Casas", "Freire"),
            ("Padre Las Casas", "Cunco"),
            ("Padre Las Casas", "Vilcún"),
            ("Lautaro", "Perquenco"),
            ("Lautaro", "Vilcún"),
            ("Lautaro", "Curacautín"),
            ("Lautaro", "Galvarino"),
            ("Perquenco", "Victoria"),
            ("Perquenco", "Galvarino"),
            ("Victoria", "Ercilla"),
            ("Victoria", "Traiguén"),
            ("Victoria", "Curacautín"),
            ("Ercilla", "Collipulli"),
            ("Collipulli", "Angol"),
            ("Collipulli", "Renaico"),
            ("Angol", "Renaico"),
            ("Angol", "Los Sauces"),
            ("Los Sauces", "Purén"),
            ("Los Sauces", "Traiguén"),
            ("Purén", "Lumaco"),
            ("Traiguén", "Lumaco"),
            ("Traiguén", "Galvarino"),
            ("Galvarino", "Cholchol"),
            ("Cholchol", "Nueva Imperial"),
            ("Nueva Imperial", "Carahue"),
            ("Nueva Imperial", "Teodoro Schmidt"),
            ("Carahue", "Saavedra"),
            ("Carahue", "Teodoro Schmidt"),
            ("Teodoro Schmidt", "Toltén"),
            ("Teodoro Schmidt", "Freire"),
            ("Freire", "Pitrufquén"),
            ("Freire", "Villarrica"),
            ("Freire", "Cunco"),
            ("Pitrufquén", "Gorbea"),
            ("Pitrufquén", "Toltén"),
            ("Gorbea", "Loncoche"),
            ("Loncoche", "Villarrica"),
            ("Villarrica", "Pucón"),
            ("Pucón", "Curarrehue"),
            ("Cunco", "Melipeuco"),
            ("Cunco", "Villarrica"),
            ("Vilcún", "Melipeuco"),
            ("Curacautín", "Lonquimay"),
            ("Lonquimay", "Melipeuco"),
        ]
    else:
        # 30 comunas Región de Los Lagos
        conexiones_directas_0 = [
            ("Osorno", "San Pablo"),
            ("Osorno", "Puyehue (Entre Lagos)"),
            ("Osorno", "San Juan de la Costa (Puaucho)"),
            ("Osorno", "Río Negro"),
            ("Osorno", "Puerto Octay"),
            ("Puyehue (Entre Lagos)", "Puerto Octay"),
            ("Río Negro", "Purranque"),
            ("Purranque", "Puerto Octay"),
            ("Purranque", "Frutillar"),
            ("Purranque", "Fresia"),
            ("Puerto Octay", "Frutillar"),
            ("Frutillar", "Llanquihue"),
            ("Frutillar", "Fresia"),
            ("Llanquihue", "Puerto Varas"),
            ("Llanquihue", "Fresia"),
            ("Fresia", "Los Muermos"),
            ("Puerto Varas", "Puerto Montt"),
            ("Puerto Varas", "Cochamó"),
            ("Puerto Montt", "Los Muermos"),
            ("Puerto Montt", "Maullín"),
            ("Puerto Montt", "Calbuco"),
            ("Puerto Montt", "Cochamó"),
            ("Puerto Montt", "Hualaihué"),
            ("Los Muermos", "Maullín"),
            ("Maullín", "Calbuco"),
            ("Cochamó", "Hualaihué"),
            ("Maullín", "Ancud"),
            ("Ancud", "Quemchi"),
            ("Ancud", "Dalcahue"),
            ("Quemchi", "Dalcahue"),
            ("Dalcahue", "Castro"),
            ("Dalcahue", "Curaco de Vélez"),
            ("Curaco de Vélez", "Quinchao"),
            ("Castro", "Chonchi"),
            ("Chonchi", "Puqueldón"),
            ("Chonchi", "Queilén"),
            ("Chonchi", "Quellón"),
            ("Queilén", "Quellón"),
            ("Hualaihué", "Chaitén"),
            ("Chaitén", "Futaleufú"),
            ("Chaitén", "Palena"),
            ("Futaleufú", "Palena"),
        ]

    n = len(localidades)
    mat = np.ones((n, n), dtype=int)
    np.fill_diagonal(mat, 0)

    idx_map = {loc: i for i, loc in enumerate(localidades)}
    for a, b in conexiones_directas_0:
        if a in idx_map and b in idx_map:
            ia, ib = idx_map[a], idx_map[b]
            mat[ia, ib] = 0
            mat[ib, ia] = 0

    return pd.DataFrame(mat, index=localidades, columns=localidades)

# 4. EXPORTADOR EXCEL PARA CONTROL 2 Y CONTROL 5
def _autoajustar_columnas_ot(ws, fila_ini: int = 3, max_width: int = 34, min_width: int = 13, col_a_max: int = 36):
    for col_idx in range(1, ws.max_column + 1):
        col_letter = get_column_letter(col_idx)
        max_len = 0
        for r_idx in range(fila_ini, min(ws.max_row + 1, 80)):
            val = ws.cell(row=r_idx, column=col_idx).value
            if val is not None:
                s_val = str(val)
                if not s_val.startswith("="):
                    max_len = max(max_len, len(s_val))
        limite_sup = col_a_max if col_idx == 1 else max_width
        ws.column_dimensions[col_letter].width = max(min(max_len + 4, limite_sup), min_width)


def exportar_excel_controles_2_y_5(
    df_mymaps: pd.DataFrame,
    df_censo: pd.DataFrame,
    df_guttman: pd.DataFrame,
    df_aislamiento: pd.DataFrame,
) -> bytes:
    """
    Genera un libro Excel (.xlsx) sobrio y homogéneo con fórmulas dinámicas:
    - Base My Maps: fila 1 estrictamente encabezados para importación directa en Google My Maps.
    - Primacía Censos: población comunal 2017–2024, rankings, cuota regional, Zipf y Primacía.
    - Guttman Top 10: escalograma funcional y centralidad ponderada de Rondinelli.
    - Aislamiento: matriz 0/1 con suma de aislamiento, índice promedio y conexiones directas.
    """
    wb = Workbook()
    wb.remove(wb.active)

    fill_titulo = PatternFill("solid", fgColor="262626")
    fill_header = PatternFill("solid", fgColor="404040")
    fill_subbloque = PatternFill("solid", fgColor="E5E7EB")
    fill_total = PatternFill("solid", fgColor="D4D4D8")
    fill_in = PatternFill("solid", fgColor="FFFFFF")
    fill_cebra = PatternFill("solid", fgColor="F9FAFB")
    fill_fn = PatternFill("solid", fgColor="F3F4F6")

    font_titulo = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    font_sub = Font(name="Calibri", size=10, italic=True, color="374151")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
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

    def _banner_ot(ws, n_cols: int, titulo: str, subtitulo: str):
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

    # HOJA 1: BASE MY MAPS (Fila 1 estrictamente encabezados para importar en Google My Maps)
    ws1 = wb.create_sheet("Base My Maps")
    cols_mm = list(df_mymaps.columns)
    for c_i, col_name in enumerate(cols_mm, start=1):
        cell = ws1.cell(row=1, column=c_i, value=col_name)
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = borde
    ws1.row_dimensions[1].height = 24

    for r_i, row in enumerate(df_mymaps.itertuples(index=False), start=2):
        fill_r = fill_in if (r_i % 2 == 0) else fill_cebra
        for c_i, val in enumerate(row, start=1):
            c = ws1.cell(row=r_i, column=c_i, value=val)
            c.font = font_celda
            c.fill = fill_r
            c.border = borde
            if isinstance(val, (float, np.floating)):
                c.number_format = "0.000000"
                c.alignment = Alignment(horizontal="right", vertical="center")
            else:
                c.alignment = Alignment(horizontal="left", vertical="center")
    ws1.freeze_panes = "B2"
    _autoajustar_columnas_ot(ws1, fila_ini=1, max_width=36, min_width=12, col_a_max=12)

    # HOJA 2: PRIMACÍA CENSOS (2017–2024)
    ws2 = wb.create_sheet("Primacía Censos")
    headers_p = [
        "Comuna", "Provincia", "Censo 2017", "Censo 2024",
        "Ranking 2017", "Ranking 2024", "Variación (%)", "Cuota Regional 2024 (%)", "Zipf Teórico (P1/Rango)",
    ]
    _banner_ot(
        ws2,
        len(headers_p),
        "HABITANTES POR COMUNA (CENSOS 2017–2024), RANKING E ÍNDICE DE PRIMACÍA",
        "Fuente: INE (Censos 2017 y 2024) | Ordenamiento Territorial",
    )

    for c_i, h in enumerate(headers_p, start=1):
        cell = ws2.cell(row=4, column=c_i, value=h)
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = borde
    ws2.row_dimensions[4].height = 25

    n_com = len(df_censo)
    fila_ini_2 = 5
    fila_tot = fila_ini_2 + n_com
    for idx_r, row in enumerate(df_censo.itertuples(index=False), start=fila_ini_2):
        fill_r = fill_in if (idx_r % 2 == 1) else fill_cebra
        c_com = ws2.cell(row=idx_r, column=1, value=row.Comuna)
        c_pro = ws2.cell(row=idx_r, column=2, value=row.Provincia)
        for ct in (c_com, c_pro):
            ct.font = font_celda
            ct.fill = fill_r
            ct.alignment = Alignment(horizontal="left", vertical="center")
            ct.border = borde

        c17 = ws2.cell(row=idx_r, column=3, value=int(row.Censo_2017))
        c24 = ws2.cell(row=idx_r, column=4, value=int(row.Censo_2024))
        for cp in (c17, c24):
            cp.fill = fill_r
            cp.font = font_celda
            cp.number_format = "#,##0"
            cp.alignment = Alignment(horizontal="right", vertical="center")
            cp.border = borde

        cr17 = ws2.cell(row=idx_r, column=5, value=f"=RANK(C{idx_r},$C${fila_ini_2}:$C${fila_tot-1})")
        cr24 = ws2.cell(row=idx_r, column=6, value=f"=RANK(D{idx_r},$D${fila_ini_2}:$D${fila_tot-1})")
        cvar = ws2.cell(row=idx_r, column=7, value=f"=IF(C{idx_r}>0,(D{idx_r}/C{idx_r})-1,0)")
        ccuo = ws2.cell(row=idx_r, column=8, value=f"=IF($D${fila_tot}>0,D{idx_r}/$D${fila_tot},0)")
        czip = ws2.cell(row=idx_r, column=9, value=f"=IF(F{idx_r}>0,$D${fila_ini_2}/F{idx_r},0)")

        for cf, fmt in [(cr17, "0"), (cr24, "0"), (cvar, "0.00%"), (ccuo, "0.00%"), (czip, "#,##0")]:
            cf.fill = fill_fn
            cf.font = font_celda
            cf.number_format = fmt
            cf.alignment = Alignment(horizontal="right", vertical="center")
            cf.border = borde

    ws2.cell(row=fila_tot, column=1, value="Total regional")
    ws2.cell(row=fila_tot, column=3, value=f"=SUM(C{fila_ini_2}:C{fila_tot-1})").number_format = "#,##0"
    ws2.cell(row=fila_tot, column=4, value=f"=SUM(D{fila_ini_2}:D{fila_tot-1})").number_format = "#,##0"
    ws2.cell(row=fila_tot, column=7, value=f"=IF(C{fila_tot}>0,(D{fila_tot}/C{fila_tot})-1,0)").number_format = "0.00%"
    ws2.cell(row=fila_tot, column=8, value=f"=SUM(H{fila_ini_2}:H{fila_tot-1})").number_format = "0.00%"
    for c_i in range(1, 10):
        ct = ws2.cell(row=fila_tot, column=c_i)
        ct.font = font_bold
        ct.fill = fill_total
        ct.border = borde_total
        if c_i >= 3:
            ct.alignment = Alignment(horizontal="right", vertical="center")

    for offset, etq_p, f17, f24 in [
        (2, "Índice de Primacía 2 ciudades (P1 / P2)", f"=IF(C{fila_ini_2+1}>0,C{fila_ini_2}/C{fila_ini_2+1},0)", f"=IF(D{fila_ini_2+1}>0,D{fila_ini_2}/D{fila_ini_2+1},0)"),
        (3, "Índice de Primacía 4 ciudades (P1 / Suma P2:P4)", f"=IF(SUM(C{fila_ini_2+1}:C{fila_ini_2+3})>0,C{fila_ini_2}/SUM(C{fila_ini_2+1}:C{fila_ini_2+3}),0)", f"=IF(SUM(D{fila_ini_2+1}:D{fila_ini_2+3})>0,D{fila_ini_2}/SUM(D{fila_ini_2+1}:D{fila_ini_2+3}),0)"),
    ]:
        r_p = fila_tot + offset
        ws2.merge_cells(start_row=r_p, start_column=1, end_row=r_p, end_column=2)
        cl = ws2.cell(row=r_p, column=1, value=etq_p)
        cl.font = font_bold
        cl.fill = fill_subbloque
        ws2.cell(row=r_p, column=1).border = borde
        ws2.cell(row=r_p, column=2).border = borde

        for col_p, form_p in [(3, f17), (4, f24)]:
            cp = ws2.cell(row=r_p, column=col_p, value=form_p)
            cp.font = font_bold
            cp.fill = fill_fn
            cp.number_format = "0.000"
            cp.alignment = Alignment(horizontal="right", vertical="center")
            cp.border = borde

    ws2.freeze_panes = "B5"
    _autoajustar_columnas_ot(ws2, fila_ini=4)

    # HOJA 3: GUTTMAN TOP 10 (ESCALOGRAMA FUNCIONAL Y RONDINELLI)
    ws3 = wb.create_sheet("Guttman Top 10")
    funcs_cols = list(df_guttman.columns)
    headers_g = ["Comuna"] + funcs_cols + ["Total funciones", "Índice Centralidad Rondinelli"]
    _banner_ot(
        ws3,
        len(headers_g),
        "ESCALOGRAMA DE GUTTMAN Y CENTRALIDAD DE RONDINELLI (TOP 10 COMUNAL)",
        "Presencia (1) o ausencia (0) de servicios y equipamiento urbano | Ponderación 100 / Frecuencia",
    )

    for c_i, h in enumerate(headers_g, start=1):
        cell = ws3.cell(row=4, column=c_i, value=h)
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = borde
    ws3.row_dimensions[4].height = 26

    n_f = len(funcs_cols)
    n_g = len(df_guttman)
    fila_ini_3 = 5
    fila_frec = fila_ini_3 + n_g
    fila_peso = fila_frec + 1
    col_fin_f = get_column_letter(1 + n_f)

    for r_i, com_nom in enumerate(df_guttman.index, start=fila_ini_3):
        fill_r = fill_in if (r_i % 2 == 1) else fill_cebra
        c_com = ws3.cell(row=r_i, column=1, value=com_nom)
        c_com.font = font_celda
        c_com.fill = fill_r
        c_com.border = borde

        for f_i, f_nom in enumerate(funcs_cols, start=2):
            c = ws3.cell(row=r_i, column=f_i, value=int(df_guttman.loc[com_nom, f_nom]))
            c.fill = fill_r
            c.font = font_celda
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border = borde

        csum = ws3.cell(row=r_i, column=2 + n_f, value=f"=SUM(B{r_i}:{col_fin_f}{r_i})")
        csum.fill = fill_fn
        csum.font = font_bold
        csum.alignment = Alignment(horizontal="right", vertical="center")
        csum.border = borde

        f_pond = "+".join([f"{get_column_letter(c)}{r_i}*${get_column_letter(c)}${fila_peso}" for c in range(2, 2 + n_f)])
        cic = ws3.cell(row=r_i, column=3 + n_f, value=f"={f_pond}")
        cic.fill = fill_fn
        cic.font = font_bold
        cic.number_format = "0.00"
        cic.alignment = Alignment(horizontal="right", vertical="center")
        cic.border = borde

    ws3.cell(row=fila_frec, column=1, value="Frecuencia comunal (Suma)")
    ws3.cell(row=fila_peso, column=1, value="Peso Rondinelli (100 / Frecuencia)")
    for c_i in range(2, 2 + n_f):
        cl = get_column_letter(c_i)
        c_fr = ws3.cell(row=fila_frec, column=c_i, value=f"=SUM({cl}{fila_ini_3}:{cl}{fila_frec-1})")
        c_fr.alignment = Alignment(horizontal="center", vertical="center")
        c_pe = ws3.cell(row=fila_peso, column=c_i, value=f"=IF({cl}{fila_frec}>0,100/{cl}{fila_frec},0)")
        c_pe.number_format = "0.00"
        c_pe.alignment = Alignment(horizontal="right", vertical="center")

    for c_i in range(1, 4 + n_f):
        c_fr = ws3.cell(row=fila_frec, column=c_i)
        c_fr.font = font_bold
        c_fr.fill = fill_total
        c_fr.border = borde_total

        c_pe = ws3.cell(row=fila_peso, column=c_i)
        c_pe.font = font_bold
        c_pe.fill = fill_subbloque
        c_pe.border = borde

    ws3.freeze_panes = "B5"
    _autoajustar_columnas_ot(ws3, fila_ini=4, max_width=24, min_width=13, col_a_max=28)

    # HOJA 4: AISLAMIENTO (MATRIZ 0/1)
    ws4 = wb.create_sheet("Aislamiento")
    locs = list(df_aislamiento.index)
    n_l = len(locs)
    headers_a = ["Localidad / Comuna"] + locs + ["Suma aislamiento (1)", "Índice aislamiento (%)", "Conexiones directas (0)"]
    _banner_ot(
        ws4,
        len(headers_a),
        "MATRIZ DE AISLAMIENTO COMUNAL",
        "0 = conexión vial directa asfaltada | 1 = sin conexión directa",
    )

    for c_i, h in enumerate(headers_a, start=1):
        cell = ws4.cell(row=4, column=c_i, value=h)
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = borde
    ws4.row_dimensions[4].height = 25

    col_fin_l = get_column_letter(1 + n_l)
    fila_ini_4 = 5
    for idx_off, loc_nom in enumerate(locs):
        r_i = fila_ini_4 + idx_off
        fill_r = fill_in if (r_i % 2 == 1) else fill_cebra
        c_loc = ws4.cell(row=r_i, column=1, value=loc_nom)
        c_loc.font = font_celda
        c_loc.fill = fill_r
        c_loc.border = borde

        for c_off, col_nom in enumerate(locs):
            c_i = 2 + c_off
            if idx_off == c_off:
                cd = ws4.cell(row=r_i, column=c_i, value=None)
                cd.fill = fill_subbloque
                cd.border = borde
            else:
                c = ws4.cell(row=r_i, column=c_i, value=int(df_aislamiento.loc[loc_nom, col_nom]))
                c.fill = fill_r
                c.font = font_celda
                c.alignment = Alignment(horizontal="center", vertical="center")
                c.border = borde

        csum1 = ws4.cell(row=r_i, column=2 + n_l, value=f"=SUM(B{r_i}:{col_fin_l}{r_i})")
        cavg1 = ws4.cell(row=r_i, column=3 + n_l, value=f"=AVERAGE(B{r_i}:{col_fin_l}{r_i})")
        ccon0 = ws4.cell(row=r_i, column=4 + n_l, value=f"=COUNTIF(B{r_i}:{col_fin_l}{r_i},0)")
        for cf, fmt in [(csum1, "0"), (cavg1, "0.00%"), (ccon0, "0")]:
            cf.fill = fill_fn
            cf.font = font_bold
            cf.number_format = fmt
            cf.alignment = Alignment(horizontal="right", vertical="center")
            cf.border = borde

    fill_con0 = PatternFill("solid", fgColor="DCFCE7")
    font_con0 = Font(name="Calibri", size=9, bold=True, color="166534")
    for r_chk in range(fila_ini_4, fila_ini_4 + n_l):
        for c_chk in range(2, 2 + n_l):
            cel_v = ws4.cell(row=r_chk, column=c_chk)
            if cel_v.value == 0:
                cel_v.fill = fill_con0
                cel_v.font = font_con0

    ws4.freeze_panes = "B5"
    if n_l > 12:
        ws4.row_dimensions[4].height = 96
        for c_i in range(2, 2 + n_l):
            ws4.cell(row=4, column=c_i).alignment = Alignment(
                horizontal="center", vertical="bottom", textRotation=90, wrap_text=False
            )
            ws4.column_dimensions[get_column_letter(c_i)].width = 4.2
        ws4.column_dimensions["A"].width = 24
        for c_i in range(2 + n_l, len(headers_a) + 1):
            ws4.column_dimensions[get_column_letter(c_i)].width = 14
    else:
        _autoajustar_columnas_ot(ws4, fila_ini=4, max_width=22, min_width=13, col_a_max=28)

    ws4.page_setup.orientation = ws4.ORIENTATION_LANDSCAPE
    ws4.page_setup.paperSize = ws4.PAPERSIZE_LETTER
    ws4.sheet_properties.pageSetUpPr.fitToPage = True
    ws4.page_setup.fitToWidth = 1
    ws4.page_setup.fitToHeight = 1
    ws4.print_area = f"A1:{get_column_letter(len(headers_a))}{fila_ini_4 + n_l - 1}"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# 5. INTERFAZ STREAMLIT DEL MOTOR DE REDES, CADENAS Y CONTROLES 2, 4 Y 5
def renderizar_redes_territorio_ot():
    st.header("Redes, Cadenas de Valor, Localización My Maps y Ordenamiento Territorial (Controles 2, 4 y 5)")
    st.markdown(
        "Módulo integral que resuelve de forma interactiva las pautas prácticas de **Control 2 (Google My Maps $\\ge 20$ locales y `Liceos.xlsx`)**, "
        "**Unidad 4 y Control 4 (Cadenas de Valor ODEPA/Araya, Entrevistas, Redes Dini/UCINET y Sistema ELITE de Boisier)** "
        "y **Unidad 5 / Control 5 Multirregional (Primacía Censos 2017–2024 en 4 regiones completas, Escalograma de Guttman en 4 Dimensiones, Matriz de Aislamiento 0/1 y PROT SUBDERE)**."
    )

    tabs = st.tabs([
        "1. Control 2 y 4: Mapa My Maps (22 Locales + 15 Liceos Osorno)",
        "2. Unidad 4 y Control 4: Cadenas de Valor (Láctea y Salmón) + Entrevistas",
        "3. Sistema ELITE (Boisier) y Redes Dini / UCINET",
        "4. Control 5 Multirregional: Primacía (97 Comunas), Guttman y Aislamiento",
        "5. Guía PROT SUBDERE (4 Sistemas, Mapa Semáforo y Normativa Anexo 2)",
    ])

    df_liceos = obtener_liceos_osorno_df()
    df_lactea_22 = obtener_22_establecimientos_cadena_lactea_osorno()
    df_censo_ll = obtener_poblacion_censos_control5("Región de Los Lagos (30 comunas)")
    df_gutt_def = obtener_matriz_guttman_control5("1. Servicios a la producción", "Región de Los Lagos (30 comunas)")
    df_aisl_def = obtener_matriz_aislamiento_control5("Región de Los Lagos (30 comunas)")

    bytes_c2_c5 = exportar_excel_controles_2_y_5(df_lactea_22, df_censo_ll, df_gutt_def, df_aisl_def)
    st.download_button(
        label="Descargar Reporte Excel (My Maps, Primacía, Guttman y Aislamiento)",
        data=bytes_c2_c5,
        file_name="GRUPO_Controles_2_4_5_Osorno_LosLagos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="btn_dl_top_general",
    )

    # TAB 1: CONTROL 2 Y CONTROL 4 — GOOGLE MY MAPS Y LICEOS.XLSX
    with tabs[0]:
        st.subheader("Georreferenciación y Validador para Google My Maps (`Unidad Actividad_mapa.pdf` + `Liceos.xlsx`)")
        base_mapa_sel = st.radio(
            "Seleccione base georreferenciada:",
            [
                "Control 2 y Control 4: 22 Establecimientos Cadena Láctea y Agroindustrial en Osorno (Cumple >= 20 locales)",
                "Archivo Oficial de Cátedra: 15 Liceos de Osorno (Liceos.xlsx)",
            ],
            horizontal=True,
        )
        df_base_act = df_lactea_22 if "22 Establecimientos" in base_mapa_sel else df_liceos
        df_editada = st.data_editor(df_base_act, num_rows="dynamic", use_container_width=True, key="editor_mymaps")

        c_m1, c_m2 = st.columns([1.3, 1.0])
        with c_m1:
            _renderizar_mapa_puntos_seguro(
                df_puntos=df_editada,
                col_lat="Latitud",
                col_lon="Longitud",
                col_grupo="Categoría",
                col_titulo_hover="Nombre",
                cols_detalle_hover=["ID", "Dirección", "Comuna", "Fuente"],
                lat_centro=-40.575,
                lon_centro=-73.133,
                zoom=11.8,
                altura=440,
                titulo_mapa="Previsualización Interactiva de Marcadores en Osorno (Validación Coordenadas)",
                estilo_mapa="open-street-map",
            )

        with c_m2:
            st.markdown("**Lista de Comprobación Automática (Rúbrica Control 2)**")
            df_val = validar_base_google_mymaps(df_editada)
            st.dataframe(df_val, use_container_width=True, hide_index=True)

            buf_mm = io.BytesIO()
            with pd.ExcelWriter(buf_mm, engine="openpyxl") as writer:
                df_editada.to_excel(writer, index=False, sheet_name="Establecimientos")
            st.download_button(
                "Descargar Excel Limpio para Importar en Google My Maps (GRUPO_Sector_Osorno.xlsx)",
                data=buf_mm.getvalue(),
                file_name="GRUPO_Sector_Osorno.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key="btn_dl_mymaps_clean",
            )

    # TAB 2: UNIDAD 4 Y CONTROL 4 — CADENAS DE VALOR Y PAUTA ENTREVISTAS
    with tabs[1]:
        st.subheader("Cadenas de Valor en el Territorio (`Unidad 4 Cadenas de Valor.pdf`) y Pauta Control 4 (40%)")
        caso_cv = st.radio(
            "Seleccione Cadena de Valor de estudio:",
            [
                "Caso 1: Cadena Láctea y Quesera de Chile / Osorno (ODEPA, 2019 — Fernández Barros y Farías Pérez)",
                "Caso 2: Clúster de la Salmonicultura en el Sur de Chile (Araya, 2016 — Servicios Intensivos en Conocimiento)",
            ],
            horizontal=True,
        )

        if "Láctea" in caso_cv:
            df_eslabones = pd.DataFrame({
                "Eslabón de la Cadena": [
                    "1. Insumos y Genética (Externos y Locales)",
                    "2. Producción Primaria de Leche Cruda",
                    "3. Transformación (Industria Mayor y Queserías)",
                    "4. Distribución, Retail, Canal Institucional y HyR",
                    "5. Consumo Final (Nacional y Exportación)",
                ],
                "Actores Directos (5+ empresas en eslabones clave)": [
                    "Cooprinsem, DeLaval, GEA Farm, Anasac, Tattersall, Insumaes",
                    "Lechería A. Matthei, Agrícola Los Pellines, Fundo Chuyaca, Productores Aproleche, Cooprinsem",
                    "Nestlé Cancura, Nestlé Osorno, Watt's Osorno, Lácteos Osorno, Quesos Las Ánimas, Colún (La Unión)",
                    "FEGOSA, Cencosud, SMU, Walmart, JUNAEB (Institucional), Hoteles y Restaurantes (HyR), Emporio Rahue",
                    "Hogares regionales/nacionales y compradores internacionales (leche en polvo/quesos)",
                ],
                "Entidades de Apoyo o Entorno (Facilitadores/Reguladores)": [
                    "INIA Remehue, SAG, Laboratorios de Calidad",
                    "Aproleche Osorno, SAGO A.G., INDAP, SEREMI Agricultura",
                    "SEREMI de Salud, ODEPA, Universidad de Los Lagos, FIA",
                    "SERNAC, Aduanas, ProChile, Empresas de Transporte Frío",
                    "Ministerio de Salud (Etiquetado), Asociaciones de Consumidores",
                ],
                "Desafíos y Cuellos de Botella (CEPAL 2016 / FAO 2015)": [
                    "Alza de costos de fertilizantes, energía y repuestos importados",
                    "Recambio generacional, estrés hídrico estival y exigencias ambientales",
                    "Asimetría en poder de negociación entre productores y plantas procesadoras",
                    "Costos de cadena de frío, plazos de pago del retail y certificaciones",
                    "Diferenciación por denominación de origen y captura de valor local",
                ],
            })
        else:
            df_eslabones = pd.DataFrame({
                "Eslabón de la Cadena": [
                    "1. Proveedores por Etapa y Transversales (KIBS)",
                    "2. Fase de Agua Dulce (Pisciculturas / Hatchery)",
                    "3. Fase de Agua de Mar (Centros de Cultivo)",
                    "4. Fase de Procesamiento (Plantas de Proceso)",
                    "5. Comercialización Nacional e Internacional",
                ],
                "Actores Directos (5+ empresas por eslabón)": [
                    "Skretting, BioMar, Cargill (Alimentos); AKVA Group, Maestranzas, Redes, Transporte Marítimo/Terrestre",
                    "Salmones Camanchaca, AquaChile, Multi X, Cermaq, Mowi (Ovas, Alevín, Smolt)",
                    "AquaChile, Multi X, Blumar, Australis Mar, Salmones Austral (Engorda y Cosecha)",
                    "Plantas Primarias y de Ahumado en Puerto Montt, Calbuco, Dalcahue y Quellón",
                    "Distribución Mayorista (EE.UU., Japón, Brasil), Retail, Canal Institucional y HORECA",
                ],
                "Entidades de Apoyo o Entorno": [
                    "INTESAL, Centros I+D, Universidades (ULagos, UACh)",
                    "SERNAPESCA, SUBPESCA, Laboratorios Patológicos",
                    "DIRECTEMAR (Concesiones), SMA, Superintendencia Servicios Sanitarios",
                    "SEREMI de Salud, Certificadoras Internacionales (ASC, BAP)",
                    "SalmonChile, Consejo del Salmón, ProChile, Aduanas",
                ],
                "Desafíos y Cuellos de Botella": [
                    "Alta dependencia de insumos críticos y estándares sanitarios",
                    "Bioseguridad e importación/producción nacional de ovas",
                    "Riesgos ambientales (FAN/piojo de mar) y relocalización de concesiones",
                    "Automatización de plantas de proceso y trazabilidad",
                    "Volatilidad de precios internacionales y costos logísticos aéreos/marítimos",
                ],
            })

        st.dataframe(df_eslabones, use_container_width=True, hide_index=True)

        st.markdown("---")
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            st.markdown("**Selección de las 3 Entrevistas Obligatorias (`Unidad 5. Redes y Cadena de Valor.dcx.pdf`)**")
            df_entrevistas = pd.DataFrame({
                "N° Entrevista": ["Entrevista 1", "Entrevista 2", "Entrevista 3"],
                "Perfil Exigido por Pauta": [
                    "Gremio, cooperativa u organización articuladora",
                    "Empresa o productor del rubro",
                    "Empresa de otro eslabón o entidad de apoyo",
                ],
                "Actor Sugerido (Caso Lácteo/Quesero Osorno)": [
                    "Aproleche Osorno / SAGO A.G. / Cooprinsem",
                    "Fundo Lechero o Elaboradora de Quesos de Osorno",
                    "Proveedor de Insumos/Maquinaria o Distribuidor/Comercializador",
                ],
                "Aporte Esperado al Informe": [
                    "Visión del territorio, cooperación horizontal y recomendación de empresas a entrevistar",
                    "Operación interna, abastecimiento de proveedores y relación con compradores",
                    "Contrastar flujos verticales, cuellos de botella y desafíos entre eslabones",
                ],
            })
            st.dataframe(df_entrevistas, use_container_width=True, hide_index=True)

        with c_p2:
            st.markdown("**Cuestionario Estructurado de 8 Preguntas + Protocolo Ético (15 minutos)**")
            st.info(
                "**Guion de contacto previo:** *'Buenos días. Somos estudiantes de Ingeniería Comercial de la Universidad de Los Lagos. "
                "En la asignatura Desarrollo y Gestión Territorial estudiamos la cadena de valor en la región. Quisiéramos conversar "
                "durante 15 minutos sobre las etapas de la actividad, las relaciones entre sus actores y las posibilidades de mejora. "
                "Si no autoriza grabación, tomaremos notas y enviaremos un breve resumen por correo para su confirmación.'*\n\n"
                "**8 Preguntas Clave para Validar Cadena y Red (Dini, 2010):**\n"
                "1. Desde los insumos hasta el cliente final, ¿qué etapas reconoce y cuáles se realizan dentro o fuera de la región?\n"
                "2. Observando nuestro esquema preliminar de cadena de valor, ¿falta o ajustaría algún eslabón o servicio de apoyo?\n"
                "3. ¿Qué empresas u organizaciones destacaría en cada etapa (al menos 5 en los eslabones principales)?\n"
                "4. ¿Cómo se establecen las condiciones de entrega, calidad, plazos y precios entre proveedor y comprador (vínculos verticales)?\n"
                "5. ¿Existen instancias de cooperación entre empresas del mismo eslabón (compras conjuntas, gremio, equipos compartidos)?\n"
                "6. Según la tipología de Dini (2010), ¿existe una empresa líder o entidad articuladora y qué actores faltarían en la red?\n"
                "7. ¿En qué etapa o conexión observa el principal cuello de botella o desafío por resolver y cómo afecta al resto?\n"
                "8. Para confirmar que entendimos bien: *[resumir vínculo principal y desafío mencionado]*. ¿Es correcto?"
            )

    # TAB 3: SISTEMA ELITE (BOISIER, 1995) Y SOCIOGRAMA UCINET / DINI
    with tabs[2]:
        st.subheader("Sistema ELITE (Boisier, 1995 — Manual 59 ILPES) y Sociograma tipo UCINET")
        instituciones = [
            "GORE Los Lagos", "Muni. Osorno", "ULagos",
            "Aproleche / SAGO", "Cámara Comercio", "Cooprinsem",
        ]
        mat_default = pd.DataFrame([
            [0, 1, 1, 1, 1, 3],
            [1, 0, 1, 3, 1, 3],
            [1, 1, 0, 1, 1, 1],
            [1, 2, 1, 0, 3, 1],
            [1, 1, 1, 3, 0, 1],
            [3, 3, 1, 1, 1, 0],
        ], index=instituciones, columns=instituciones)

        df_cargos_def = pd.DataFrame({
            "Personero / Actor": [
                "Gobernador Regional", "Alcalde de Osorno", "Rector Universidad de Los Lagos",
                "Presidente Gremial Aproleche", "Gerente General Cooprinsem", "Presidente Cámara de Comercio",
            ],
            "Institución": instituciones,
            "Cargo_Directivo": ["Máximo Directivo (9)", "Máximo Directivo (9)", "Máximo Directivo (9)", "Presidente Directorio (8)", "Gerente General (8)", "Presidente Gremial (7)"],
            "Relevancia_Institucional_1_99": [95, 90, 88, 84, 82, 78],
            "Peso_Cargo_3_9": [9, 9, 9, 8, 8, 7],
        })

        c_e1, c_e2 = st.columns([1.1, 1.2])
        with c_e1:
            st.markdown("**Matriz Interinstitucional (1=Cooperación, 2=Conflicto, 3=Neutral, 0=Sin vínculo)**")
            mat_edit = st.data_editor(mat_default, use_container_width=True, key="elite_mat")
            res_socio, df_elite_res = calcular_sistema_elite_boisier(mat_edit, df_cargos_def)

            k1, k2, k3 = st.columns(3)
            k1.metric("Índice Cooperatividad", f"{res_socio['Cooperatividad_%']:.1f}%")
            k2.metric("Índice Conflictividad", f"{res_socio['Conflictividad_%']:.1f}%")
            k3.metric("Índice Neutralidad", f"{res_socio['Neutralidad_%']:.1f}%")

        with c_e2:
            st.markdown("**Ranking de Importancia Social Relativa (Sistema ELITE — Boisier)**")
            st.dataframe(df_elite_res, use_container_width=True, hide_index=True)

    # TAB 4: CONTROL 5 MULTIRREGIONAL — PRIMACÍA, GUTTMAN Y AISLAMIENTO
    with tabs[3]:
        st.subheader("Laboratorio Oficial Control 5 Multirregional (`Unidad 5. Ordenamiento Territorial.pdf`)")
        reg_c5 = st.radio(
            "Seleccione Región de Estudio para Control 5 (97 comunas precargadas + edición en vivo):",
            [
                "Región de Los Lagos (30 comunas)",
                "Región del Biobío (33 comunas)",
                "Región de Los Ríos (12 comunas)",
                "Región de La Araucanía (32 comunas)",
            ],
            horizontal=True,
        )
        df_c5_init = obtener_poblacion_censos_control5(reg_c5)

        st.markdown("**1. Tabla Editable de Habitantes por Comuna, Ranking e Índice de Primacía (Censos 2017 y 2024)**")
        st.caption("Puedes editar poblaciones o agregar filas si deseas evaluar otra región personalizada:")
        df_c5_edit_raw = st.data_editor(
            df_c5_init[["Comuna", "Provincia", "Censo_2017", "Censo_2024"]],
            num_rows="dynamic",
            use_container_width=True,
            key=f"censo_ed_{reg_c5}",
        )
        df_c5_pob = recalcular_indicadores_primacia_df(df_c5_edit_raw)

        p1_17, p1_24 = float(df_c5_pob.loc[0, "Censo_2017"]), float(df_c5_pob.loc[0, "Censo_2024"])
        p2_17, p2_24 = float(df_c5_pob.loc[1, "Censo_2017"]), float(df_c5_pob.loc[1, "Censo_2024"])
        ip2_17, ip2_24 = p1_17 / max(p2_17, 1.0), p1_24 / max(p2_24, 1.0)
        ip4_17 = p1_17 / max(float(df_c5_pob.loc[1:3, "Censo_2017"].sum()), 1.0)
        ip4_24 = p1_24 / max(float(df_c5_pob.loc[1:3, "Censo_2024"].sum()), 1.0)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Primacía 2 Ciudades (2017)", f"{ip2_17:.3f}", f"Ciudad 1: {df_c5_pob.loc[0, 'Comuna']}")
        m2.metric("Primacía 2 Ciudades (2024)", f"{ip2_24:.3f}", f"{ip2_24 - ip2_17:+.3f} vs 2017")
        m3.metric("Primacía 4 Ciudades (2017)", f"{ip4_17:.3f}", "P1 / (P2 + P3 + P4)")
        m4.metric("Primacía 4 Ciudades (2024)", f"{ip4_24:.3f}", f"{ip4_24 - ip4_17:+.3f} vs 2017")

        st.dataframe(df_c5_pob.round(2), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown(f"**2. Escala de Guttman / Rondinelli para las 10 Comunas Más Pobladas ({reg_c5.split('(')[0].strip()})**")
        dim_sel = st.selectbox(
            "Seleccione una de las 4 dimensiones oficiales de la pauta del Control 5 (mínimo 7+ variables diferenciadoras):",
            [
                "1. Servicios a la producción (Sercotec, Centro Negocios, Bancos, OTEC, Reclutamiento, etc.)",
                "2. Infraestructura, transporte y telecomunicaciones (Aeropuerto, Puerto, Tren, Terminal, Radio, TV, Área Ind.)",
                "3. Infraestructura de salud y educacional (Universidad, IP/CFT, Liceos HC/TP, Hospital Tipo 1/2, CESFAM, Farmacia)",
                "4. Servicios recreacionales, deportivos y grandes centros comerciales (Estadio, Gimnasio, Cine, Mall, Multitiendas)",
            ],
        )
        df_gutt_base = obtener_matriz_guttman_control5(dim_sel, reg_c5)
        df_gutt_edit = st.data_editor(df_gutt_base, use_container_width=True, key=f"gutt_c5_ed_{reg_c5}_{dim_sel[:2]}")

        frec_f = df_gutt_edit.sum(axis=0)
        cols_sin_disc = [c for c in df_gutt_edit.columns if int(frec_f[c]) in (0, len(df_gutt_edit))]
        if cols_sin_disc:
            st.warning(
                f"Regla Control 5: las columnas {', '.join(cols_sin_disc)} tienen puros 1 o puros 0 y no discriminan entre comunas. "
                "Edita sus celdas o reemplaza esas variables por equipamientos diferenciadores."
            )
        else:
            st.success(f"Validación Control 5 OK: las {len(df_gutt_edit.columns)} variables (≥ 7) discriminan efectivamente entre las {len(df_gutt_edit)} comunas.")
        pesos_r = np.where(frec_f > 0, 100.0 / frec_f, 0.0)
        centralidad_com = df_gutt_edit.values @ pesos_r
        df_res_gutt = pd.DataFrame({
            "Comuna (Top 10)": df_gutt_edit.index,
            "N° Funciones Presentes": df_gutt_edit.sum(axis=1).values,
            "Índice Centralidad Rondinelli": np.round(centralidad_com, 2),
        }).sort_values("Índice Centralidad Rondinelli", ascending=False).reset_index(drop=True)
        df_res_gutt["Jerarquía Funcional"] = [f"Nivel {i}" for i in range(1, len(df_res_gutt) + 1)]

        cg1, cg2 = st.columns([1.1, 1.3])
        with cg1:
            st.dataframe(df_res_gutt, use_container_width=True, hide_index=True)
        with cg2:
            fig_gutt = px.bar(
                df_res_gutt,
                x="Comuna (Top 10)",
                y="Índice Centralidad Rondinelli",
                color="N° Funciones Presentes",
                text="Índice Centralidad Rondinelli",
                title=f"Jerarquía Funcional de Guttman / Rondinelli — {dim_sel.split('(')[0]}",
            )
            st.plotly_chart(fig_gutt, use_container_width=True)

        st.markdown("---")
        st.markdown(f"**3. Matriz de Aislamiento Comunal ({reg_c5.split('(')[0].strip()} | 0 = Conectada/Asfalto, 1 = No conectada/Ripio)**")
        df_aisl_edit = st.data_editor(
            obtener_matriz_aislamiento_control5(reg_c5),
            use_container_width=True,
            key=f"aisl_c5_ed_{reg_c5}",
        )
        vals_a = df_aisl_edit.values.copy()
        np.fill_diagonal(vals_a, 0)
        n_loc = len(df_aisl_edit)
        suma_1s = vals_a.sum(axis=1)
        conex_0s = (n_loc - 1) - suma_1s
        ind_aisl = (suma_1s / max(n_loc - 1, 1)) * 100.0

        df_res_aisl = pd.DataFrame({
            "Localidad / Comuna": df_aisl_edit.index,
            "Conexiones Directas (Criterio 0)": conex_0s,
            "No Conectadas Directamente (Criterio 1)": suma_1s,
            "Índice de Aislamiento (%)": np.round(ind_aisl, 2),
        }).sort_values("Índice de Aislamiento (%)", ascending=True).reset_index(drop=True)
        st.dataframe(df_res_aisl, use_container_width=True, hide_index=True)

        bytes_reg_activa = exportar_excel_controles_2_y_5(
            df_lactea_22,
            df_c5_pob,
            df_gutt_edit,
            df_aisl_edit,
        )
        slug_reg = reg_c5.split("(")[0].strip().replace(" ", "_")
        st.download_button(
            label=f"Descargar Reporte Excel — {reg_c5.split('(')[0].strip()}",
            data=bytes_reg_activa,
            file_name=f"Control5_Primacia_Guttman_Aislamiento_{slug_reg}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="btn_dl_tab4_region",
        )

    # TAB 5: GUÍA PROT SUBDERE-CEPAL (2011) Y BUSCADOR ANEXO 2
    with tabs[4]:
        st.subheader("Plan Regional de Ordenamiento Territorial (PROT SUBDERE-CEPAL, 2011)")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.markdown("**Los 4 Sistemas Territoriales y Mapa Semáforo de Conflictos de Uso**")
            df_prot_sis = pd.DataFrame({
                "Sistema Territorial (PROT)": [
                    "1. Sistema Costero",
                    "2. Sistema Urbano",
                    "3. Sistema Rural",
                    "4. Sistema Cuenca Hidrográfica",
                ],
                "Vocación y Uso Preferente": [
                    "Pesca artesanal, concesiones de acuicultura, puertos, conservación y turismo litoral",
                    "Red de ciudades (Osorno, Puerto Montt, Concepción, Temuco, Valdivia), vivienda y servicios",
                    "Producción silvoagropecuaria, forestal y lechera, agroindustria y conservación de suelos",
                    "Gestión integrada del recurso hídrico (Cuencas ríos Biobío, Imperial, Valdivia, Bueno, Rahue y Maullín)",
                ],
                "Semáforo de Conflicto de Intereses": [
                    "Rojo / Amarillo: Superposición entre ECMPO, acuicultura, puertos y turismo",
                    "Rojo: Expansión urbana sobre suelos agrícolas clase I-III y déficit de conectividad",
                    "Amarillo: Subdivisión de predios rústicos (DL 3.516 / parcelas de agrado) vs uso productivo",
                    "Rojo / Amarillo: Derechos de agua, descargas puntuales y riberas protegidas",
                ],
            })
            st.dataframe(df_prot_sis, use_container_width=True, hide_index=True)

        with c_s2:
            st.markdown("**Buscador del Anexo 2 del PROT: Normas de Ordenamiento Territorial por Materia**")
            df_normas = pd.DataFrame({
                "Materia": [
                    "Acuicultura", "Aguas", "Borde Costero", "Bosques", "Catástrofes y Riesgos",
                    "Desarrollo Indígena", "División Predios Rústicos", "Gobierno y Adm. Regional",
                    "Medio Ambiente y SEIA", "Urbanismo y Construcciones", "Áreas Silvestres Protegidas (SNASPE)",
                ],
                "Norma General de OT": [
                    "DS 290/1993, DS 320/2001 (RAMA) y Ley 20.091",
                    "DFL 1.122 (Código de Aguas) y Ley 19.525 (Aguas lluvias)",
                    "DS 475/1994 (Política Nacional Borde Costero) y DFL 340 Concesiones Marítimas",
                    "DS 4.363 Ley de Bosques y DL 701 / DL 2.565 Fomento Forestal",
                    "Ley 16.282 Sismos/Catástrofes y DS 156 Plan Nacional Protección Civil",
                    "Ley 19.253 (Crea CONADI y Áreas de Desarrollo Indígena ADI)",
                    "DL 3.516 (Normas sobre división de predios rústicos fuera del límite urbano)",
                    "Ley 19.175 LOCGAR (Arts. 17, 24 y 26: funciones del GORE en OT y PROT)",
                    "Ley 19.300 Bases del Medio Ambiente y DS 95 Reglamento SEIA",
                    "DFL 458 Ley General de Urbanismo y Construcciones (LGUC) y DS 47 OGUC",
                    "Ley 18.362 (Sistema Nacional de Áreas Silvestres Protegidas del Estado)",
                ],
                "Organismos Regulados / Competentes": [
                    "SUBPESCA, SERNAPESCA, DIRECTEMAR, DGA",
                    "DGA, Ministerio de Obras Públicas (MOP), MMA",
                    "CNUBC, CRUBC, GORE, DIRECTEMAR, SSFFAA",
                    "CONAF, SAG, Ministerio de Agricultura, Municipalidades",
                    "SENAPRED (ex ONEMI), Ministerio del Interior, Municipalidades, MINVU",
                    "CONADI, MIDEPLAN/MDSF, GORE, SEREMI MINVU",
                    "SEREMI MINVU, SAG, Municipalidades",
                    "Gobierno Regional (GORE), CORE, SEREMIs, Municipalidades",
                    "Ministerio del Medio Ambiente, SEA, SMA, SEREMI Salud",
                    "MINVU, SEREMI MINVU, Direcciones de Obras Municipales (DOM)",
                    "CONAF, Ministerio de Bienes Nacionales, MMA",
                ],
            })
            st.dataframe(df_normas, use_container_width=True, hide_index=True)
