# Plataforma Integral de Desarrollo y Gestión Territorial 2026 — ULagos

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/)
[![Lanzar Plataforma en Streamlit](https://img.shields.io/badge/ABRIR_PLATAFORMA_TERRITORIAL_EN_STREAMLIT-1E3A8A?style=for-the-badge&logo=streamlit&logoColor=white)](https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026)

Motor econométrico, sociométrico y espacial desarrollado en **Python (`Streamlit`, `Pandas`, `NumPy`, `SciPy`, `Plotly`, `OpenPyXL`, `xlrd`)** para la asignatura **Desarrollo y Gestión Territorial** (Carrera de Ingeniería Comercial, Universidad de Los Lagos — Prof. Claudio Mancilla). Integra los marcos teóricos de localización y crecimiento (**Krugman, Perroux, Myrdal, Hirschman, Granovetter, Christaller, Weber y von Thünen**), el procesamiento de estadísticas tributarias comunales del **SII (2014–2024)** bajo metodologías de **ILPES / CEPAL (Lira y Quiroga; Silva Lira)**, la réplica econométrica del paquete **REAT** de R, un **Constructor en Vivo de Redes Empresariales (Dini, 2010; UCINET)**, las herramientas de **Ordenamiento Territorial (Primacía Urbana, Ranking de Asentamientos, Guttman/Rondinelli, Aislamiento, Boisier ELITE y PROT)** y los **Indicadores Compuestos Mín–Máx (Unidad VI)**.

**Acceso directo a la aplicación web en vivo:**  
https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/

## Fuentes Oficiales y Trazabilidad de Datos

| Dimensión | Periodo | Fuente Oficial | Respaldo en Repositorio |
| :--- | :--- | :--- | :--- |
| **Empresas por rubro y comuna** | **2014 – 2024** | Servicio de Impuestos Internos (SII) | `ILPES GRUPO 10 29-10-2026.xlsx` |
| **Población comunal (Censo 2017 — 346 comunas)** | **Censo 2017** (Biobío: 1.556.805 hab.) | Instituto Nacional de Estadísticas (INE — Resultados Definitivos) | `1_1_poblacion.xls` |
| **Población comunal (Censo 2024 — Biobío)** | **Censo 2024** (Biobío: 1.613.059 hab.) | Instituto Nacional de Estadísticas (INE — `www.censo2024.cl`) | `poblacion 2024.pdf` |
| **Levantamiento primario (Control 4)** | **2026** | Entrevistas a gremios y empresas de la cadena de valor | `cuestionario_entrevista.pdf` |

> **Nota metodológica de periodos:** Los indicadores económicos sectoriales (ILPES, MADE, Silva Lira y Convergencia SII) cubren el periodo **2014–2024**, mientras que los indicadores demográficos de Ordenamiento Territorial (Índice de Primacía $IP_4$ y Ranking de Asentamientos) comparan los dos últimos censos oficiales del INE (**2017 y 2024**). El módulo `motor_sii_exportador.py` lee automáticamente la pestaña `Comuna` de `1_1_poblacion.xls` (`EDAD == Total Comuna`) sin requerir filtros manuales en Excel.

## Arquitectura de Vistas y Módulos Interactivos (`app.py`)

### 1. Estudio Territorial Interactivo a 60 FPS (`motor_fluidez_territorial_60fps.py`)
* **Localización y Crecimiento (Unidades I y II):** Simuladores en tiempo real de **Perroux, Myrdal y Hirschman** (5 rondas acumulativas y balance *Spread* vs. *Backwash*), **von Thünen** (editor libre de ecuaciones $LR(d)$ y anillos concéntricos), **Weber** (Índice de Materiales $IM$ e isodápana crítica), **Krugman (1991)** (umbral de bifurcación $\tau^*$), **Christaller** (umbral/alcance) y **Granovetter** (vínculos fuertes vs. puentes débiles).
* **Disparidades, Redes, OT e Indicadores (Unidades III a VI):** Curva de Lorenz, Gini, Theil, $HHI$, $HK_\alpha$, Primacía Urbana ($IP_4$ en escala $0$–$3$), **Constructor Sociométrico Dini (2010)**, laboratorio completo de **Ordenamiento Territorial — Control 5** (Ranking con flechas cruzadas, Escalograma de Guttman/Rondinelli en 4 dimensiones, Matriz de Aislamiento vial, base teórica y Manual PROT con Mapa Semáforo), **Normalización Mín–Máx (Unidad VI)**, **Formulario en Modo Ciego** y **Mapa Teórico Integrado con Control de Lectura**.

### 2. Biblioteca Oficial de Cátedra y Visor PDF (`app.py`)
* Acceso integrado a la bibliografía oficial de la asignatura y visor PDF alojado en Google Drive.

### 3. Motor SII / ILPES / MADE / REAT y Exportador Maestro Excel (`motor_sii_exportador.py`)
* Construcción automatizada de matrices sectoriales-comunales $V_{ij}$ (2014–2024) desde `ILPES GRUPO 10 29-10-2026.xlsx`, integrada con lectura directa del Censo 2017 desde `1_1_poblacion.xls` (346 comunas de las 16 regiones).
* Cálculo de **Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)**, **Coeficiente de Reestructuración ($CR_r$)**, **Base Económica Exportadora de Tiebout ($X_j$ y $M_j$)**, **Cuadrantes de Silva Lira (CEPAL, 2005 — per cápita Censo 2024 vs. tasa anualizada)** y **Shift & Share Clásico y Modificado (MADE)**.
* Réplica econométrica del paquete **REAT**: **Convergencia Sigma ($\sigma_t, CV_t$)**, **Convergencia Beta Absoluta OLS ($\beta, \lambda, t_{1/2}, p$)**, **Lorenz / Gini ($G, G^*$)**, **Theil ($T$)**, **$HHI$** y **Hannah-Kay ($HK_\alpha$)**.
* Compilación y descarga de libro `.xlsx` con fórmulas vivas de **13 hojas** con años censales explícitos: `Resumen`, `Base 2014`, `Base 2024`, `Localización Qij`, `Especialización`, `Prod. Básica`, `Cuadrantes Silva`, `MADE`, `MADE Modificado`, `Convergencia`, `Primacía y Ranking`, `Rondinelli` y `Aislamiento`.

### 4. Laboratorio de Cátedra (`motor_laboratorio_catedra.py`)
* Integración de **PIB Regional encadenado 2015–2025 vs. Censo 2024** (16 regiones), **Sistema TAREA** (6 tipologías de Boisier y 14 de Stilwell), **Convergencia $\sigma$ y $\beta$**, **Lorenz/Gini**, **Theil**, evolución **CASEN (2009–2024)**, **Concentración ($CR_m, HH, HH_N, HK_\alpha$)** y **Cadenas de Markov (Figueroa & Herrero, 2003)**, con descarga de `Laboratorio_Catedra_ULagos.xlsx`.

### 5. Terreno, Redes y Controles 2, 4 y 5 (`motor_redes_territorio_ot.py` y `motor_redes_dinamicas_dini.py`)
* Catastro georreferenciado validado para **Google My Maps**, **Sistema ELITE de Sergio Boisier (1995)**, **Primacía (Censos 2017–2024)**, **Escalograma de Guttman / Rondinelli** y **Matriz de Aislamiento** para las comunas de Biobío, La Araucanía, Los Ríos y Los Lagos.
* Constructor editable de matrices sociométricas (reemplazo de **UCINET**) sobre las **5 topologías de Dini (2010)** y los casos del Control 4 (*Red Láctea-Quesera de Osorno* y *Clúster Forestal-Maderero PymeMad Biobío*), más descarga de `cuestionario_entrevista.pdf`.

## Estructura de Archivos del Repositorio

```text
DESARROLLO-Y-GESTION-TERRITORIAL-2026/
├── .streamlit/config.toml               # Configuración visual de la app en Streamlit
├── app.py                               # Orquestador principal (5 Vistas + Modo Presentación Cátedra)
├── motor_fluidez_territorial_60fps.py   # Estudio interactivo 60 FPS (Unidades I–VI, Formulario y Lectura)
├── motor_sii_exportador.py              # Motor matricial SII, ILPES, MADE, REAT y exportador Excel (13 hojas)
├── motor_laboratorio_catedra.py         # PIB Regional, TAREA, Convergencia, Lorenz, Theil, Markov y Excel
├── motor_redes_territorio_ot.py         # Controles 2, 4 y 5 (Google My Maps, ODEPA, Boisier ELITE y PROT)
├── motor_redes_dinamicas_dini.py        # Constructor en vivo de redes (Dini 2010), burbujas y gradientes
├── ILPES GRUPO 10 29-10-2026.xlsx       # Base oficial nacional del SII e ILPES (2014–2024)
├── 1_1_poblacion.xls                    # Respaldo oficial INE: Resultados Definitivos Censo 2017 (346 comunas)
├── poblacion 2024.pdf                   # Respaldo oficial INE: Resultados Región del Biobío Censo 2024
├── cuestionario_entrevista.pdf          # Instrumento oficial de levantamiento primario en terreno (Control 4)
├── requirements.txt                     # Dependencias para despliegue en Streamlit Cloud (incluye xlrd)
└── README.md                            # Documentación técnica y académica del repositorio
```
