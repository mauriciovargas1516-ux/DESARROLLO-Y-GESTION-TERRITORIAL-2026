# Plataforma Integral de Desarrollo y Gestión Territorial 2026 — ULagos

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/)
[![Lanzar Plataforma en Streamlit](https://img.shields.io/badge/ABRIR_PLATAFORMA_TERRITORIAL_EN_STREAMLIT-1E3A8A?style=for-the-badge&logo=streamlit&logoColor=white)](https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026)

Motor econométrico, sociométrico y espacial desarrollado en **Python (`Streamlit`, `Pandas`, `NumPy`, `SciPy`, `Plotly`, `OpenPyXL`)** para la asignatura **Desarrollo y Gestión Territorial** (Carrera de Ingeniería Comercial, Universidad de Los Lagos — Prof. Claudio Mancilla). Integra en **9 módulos interactivos ordenados pedagógicamente** los marcos teóricos de localización y crecimiento (**Krugman, Perroux, Myrdal, Hirschman, Granovetter y Christaller**), el procesamiento de estadísticas tributarias comunales del **SII (2014–2024)** bajo metodologías de **ILPES / CEPAL (Lira y Quiroga; Silva Lira)**, la réplica econométrica del paquete **REAT** de R, un **Constructor en Vivo de Redes Empresariales (Dini, 2010; UCINET)** y las herramientas de **Ordenamiento Territorial (Rondinelli, Guttman, Primacía Urbana, von Thünen, Boisier ELITE y PROT)**.

**Acceso directo a la aplicación web en vivo:**  
https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/

## Secuencia Pedagógica de los 9 Módulos Interactivos (`app.py`)

### 1. Fundamentos y Simulación Teórica (`motor_teoria_territorial.py`)
* **Simulador en Vivo de la Nueva Economía Geográfica (Krugman, 1991):** Deslizadores de costos de transporte ($\tau$), economías de escala y movilidad laboral para visualizar el umbral crítico donde se dispara la macrocefalia regional.
* **Simulador de Polos de Crecimiento y Multiplicadores (Perroux, Myrdal y Hirschman):** Cálculo en tiempo real de encadenamientos hacia atrás/adelante y balance entre difusión (*Spread*) y absorción (*Backwash*) en 5 rondas acumulativas.
* **Grafo Interactivo en Vivo de Vínculos Fuertes vs. Débiles (Granovetter, 1973):** Construcción visual de enlaces locales (azules) y puentes externos de innovación hacia universidades y centros de I+D (rojos) para prevenir el bloqueo (*lock-in*).
* **Calculadora en Vivo de Lugares Centrales (Christaller):** Evaluación instantánea de viabilidad de servicios urbanos según población comunal (**Umbral**) y distancia máxima de viaje (**Alcance**).

### 2. Técnicas de Análisis Regional (ILPES / SII 2014–2024)
* Construcción automatizada de matrices sectoriales-comunales $V_{ij}$ desde la base oficial del SII (`ILPES GRUPO 10 29-10-2026.xlsx`).
* Cálculo de **Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)**, **Coeficiente de Reestructuración ($CR_r$)**, **Base Económica Exportadora de Tiebout ($X_j$ y multiplicador $M_j$)**, **Cuadrantes de Silva Lira (CEPAL, 2005 — per cápita Censo 2024 vs. tasa anualizada)** y descomposición **Shift & Share Clásico y Modificado (MADE: $ET_j = EE_j + ED_j$, $EI_j, EM_j, ERM_j$)** con Notas Metodológicas desplegables.

### 3. Disparidades, Concentración y Convergencia Regional (Motor REAT)
* Réplica en Python del paquete **REAT (*Regional Economic Analysis Toolbox*)**: **Convergencia Sigma ($\sigma_t, CV_t$)**, **Convergencia Beta Absoluta OLS ($\beta$, velocidad anual $\lambda$, semivida $t_{1/2}$ y valor $p$)**, **Curva de Lorenz**, **Índice de Gini ($G, G^*$)**, **Entropía de Theil ($T$)**, **Índice de Herfindahl-Hirschman ($HHI$)** e **Índice de Hannah-Kay ($HK_\alpha$)**.

### 4. Sistemas Productivos Locales (SPL), Redes (UCINET) y Cadenas de Valor
* Simulador interactivo de matrices de adyacencia binaria (reemplazo de **UCINET**) con cálculo de grados de entrada/salida, centralidad nodal y densidad de red, junto al diagnóstico de restricciones y *Upgrading* de la cadena forestal-maderera (**PymeMad Biobío / Los Ángeles**).

### 5. Redes en Vivo (Dini, 2010), Constructor Interactivo y Gradientes (`motor_redes_dinamicas_dini.py`)
* **Constructor Animado e Interactivo en Vivo:** Visualización paso a paso con botón `Play` y **matriz editable con casillas de verificación** para conectar o desconectar empresas en vivo sobre las **5 topologías de Dini (2010, `04 SPL.pdf` pág. 14)**, los **2 casos reales del Control 4** (*Red Láctea-Quesera de Osorno* y *Clúster Maderero PymeMad Biobío*) y un **Laboratorio Libre desde cero**, calculando grado nodal $k_i$, densidad $D = \frac{2L}{n(n-1)}$ y **Gradiente de Concentración ($GC_{red}$)** con exportación a `Matriz_Sociometrica_Red.xlsx`.
* **Simulador de Gradiente de Concentración Territorial (`06 OT 2024.pdf`):** Integra el **Índice de Primacía Urbana ($IP_4$)** con estandarización de cátedra ($0$ a $3$), la curva de **Gradiente Jerárquico Funcional de Guttman / Rondinelli** y los anillos de **Renta Locacional de von Thünen**.

### 6. Ordenamiento Territorial, Escalograma de Rondinelli y Georreferenciación
* Matriz editable de funciones urbanas con ponderación inversa de frecuencia ($W_k = 100 / f_k$) para el cálculo del **Índice de Centralidad Funcional de Rondinelli (1985)** y cartografía interactiva.

### 7. Laboratorio de Cátedra + Cuaderno Excel con Fórmulas Vivas (`motor_laboratorio_catedra.py`)
* Integración de **PIB Regional encadenado 2015–2025 vs. Censo 2024** (16 regiones), **Sistema TAREA (Badalona y Colombia)** con las 6 tipologías de Boisier y 14 de Stilwell, **Convergencia $\sigma$ y $\beta$**, **Lorenz/Gini por trapecios**, **Entropía de Theil**, evolución **CASEN (2009–2024)**, **Concentración ($CR_m, HH, HH_N, HK_\alpha$)** y **Cadenas de Markov (Figueroa & Herrero, 2003)**.
* Descarga directa del cuaderno `Laboratorio_Catedra_ULagos.xlsx` (4 hojas con fórmulas activas).

### 8. Controles 2, 4 y 5: Google My Maps, Cadenas, Sistema ELITE y PROT (`motor_redes_territorio_ot.py`)
* Catastro georreferenciado validado para **Google My Maps** (15 Liceos de Osorno y 22 establecimientos del complejo lácteo-quesero de Osorno), **Sistema ELITE de Sergio Boisier (1995)**, **Primacía (Censos 2017–2024)**, **Escalograma de Guttman / Rondinelli** y **Matriz de Aislamiento** para las 97 comunas de Biobío, La Araucanía, Los Ríos y Los Lagos, con descarga directa en `.xlsx`.

### 9. Exportador Maestro SII (Generador Excel de 10 Hojas — `motor_sii_exportador.py`)
* Compila y descarga un libro `.xlsx` sobrio de 10 hojas (`Resumen`, `Base 2014`, `Base 2024`, `Localización Qij`, `Especialización`, `Prod. Básica`, `Cuadrantes Silva`, `MADE`, `MADE Modificado` y `Convergencia`) con fórmulas vivas, formato condicional, población Censo 2024 y gráfico de dispersión nativo para cualquier región de Chile.

## Estructura de Archivos del Repositorio

```text
DESARROLLO-Y-GESTION-TERRITORIAL-2026/
├── app.py                               # Orquestador principal en Streamlit (9 Módulos en orden pedagógico)
├── motor_teoria_territorial.py          # Módulo 1: Simulador interactivo de Krugman, Perroux, Granovetter y Christaller
├── motor_redes_dinamicas_dini.py        # Módulo 5: Constructor en vivo de redes (Dini 2010), burbujas y gradientes
├── motor_laboratorio_catedra.py         # Módulo 7: PIB Regional, TAREA, Convergencia, Lorenz, Theil, Markov y Excel
├── motor_redes_territorio_ot.py         # Módulo 8: Controles 2, 4 y 5 (Google My Maps, ODEPA, Boisier ELITE y PROT)
├── motor_sii_exportador.py              # Módulo 9: Motor matricial SII, ILPES, MADE, REAT y exportador Excel 10 hojas
├── ILPES GRUPO 10 29-10-2026.xlsx       # Base oficial nacional del SII e ILPES (26,1 MB)
├── cuestionario_entrevista.pdf          # Instrumento oficial de levantamiento primario en terreno
├── requirements.txt                     # Dependencias para despliegue en Streamlit Cloud
└── README.md                            # Documentación técnica y académica del repositorio
```
