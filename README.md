# Desarrollo y Gestión Territorial 2026 — Universidad de Los Lagos

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/)
[![Lanzar Plataforma en Streamlit](https://img.shields.io/badge/ABRIR_PLATAFORMA_INTERACTIVA_EN_STREAMLIT-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026)

Plataforma de modelamiento econométrico, análisis espacial, redes productivas y ordenamiento territorial desarrollada en **Python + Streamlit** para la asignatura de **Desarrollo y Gestión Territorial** (Ingeniería Comercial, Universidad de Los Lagos — Prof. Claudio Mancilla).

**Acceso directo a la aplicación web en vivo:**  
[https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/](https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/)

---

## Arquitectura de los 7 Módulos de la Plataforma

### 1. Técnicas de Análisis Regional (ILPES / SII 2014–2024)
* Procesamiento automatizado de microdatos comunales y sectoriales del **Servicio de Impuestos Internos (SII)** con foco en las 33 comunas de la Región del Biobío y análisis multirregional.
* Clasificación dinámica en los **Cuadrantes de Silva Lira (CEPAL, 2005)**.
* Matrices de **Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)** y **Coeficiente de Reestructuración ($CR_r$)** en los rubros económicos del SII.
* Estimación del modelo de **Base Económica Exportadora ($X_{ij}, X_j$)** y **Multiplicador Básico Regional ($M_j$)** de Tiebout / Lira & Quiroga.
* Descomposición **Shift & Share (MADE Clásico y Modificado)**: Efecto Total ($ET_j$), Estructural ($EE_j$), Diferencial ($ED_j$), Estructural Inverso ($EI_j$), Estructural Modificado ($EM_j$) y Regional Modificado ($ERM_j$).

### 2. Disparidades, Concentración y Convergencia Regional (Motor REAT)
* Réplica en Python de las funciones econométricas del paquete **`REAT` (Regional Economic Analysis Toolbox)** de R.
* **Convergencia Sigma ($\sigma_{\ln}$)**, **Coeficiente de Variación ($CV$)** y regresión OLS de **Convergencia Beta Absoluta ($\beta$)** con cálculo de velocidad anual ($\lambda$), semivida (*Half-life*), $R^2$ y $p$-valor.
* **Curva de Lorenz**, **Índice de Gini** (estándar $G$ y normalizado $G^*$), **Índice de Entropía de Theil ($T$)**, **Herfindahl-Hirschman ($HHI, HHI_N$)** e **Índice de Hannah-Kay ($HK_\alpha$)** con parámetro de sensibilidad $\alpha$ configurable.

### 3. Sistemas Productivos Locales (SPL), Redes Empresariales y Cadenas de Valor
* Simulador interactivo de matrices sociométricas y grafos de articulación empresarial (reemplazo práctico de **UCINET**) con cálculo de densidad de red, grado de entrada/salida y centralidad según **Dini (2010, CEPAL)**.
* Diagnóstico de restricciones y estrategias de escalamiento (*Upgrading* de proceso, producto, funcional y tecnológico) bajo metodología **CEPAL (Padilla y Oddone, 2016)** aplicada al complejo forestal-maderero (**PymeMad Biobío — Los Ángeles**).
* Descarga integrada del instrumento oficial de levantamiento primario en terreno (`cuestionario_entrevista.pdf`).

### 4. Ordenamiento Territorial, Matriz de Rondinelli y Georreferenciación
* **Escalograma Funcional de Rondinelli (1985):** Edición interactiva de matrices de presencia/ausencia de funciones urbanas, ponderación inversa de frecuencia y jerarquización en 3 niveles de centralidad.
* Cartografía georreferenciada de polos productivos y urbanos en las regiones del Biobío y Los Lagos.

### 5. Exportador Maestro SII (Libro Excel de 10 Hojas)
* Motor de compilación en memoria (`openpyxl`) que permite cargar cualquier base estadística del SII o utilizar la base oficial del repositorio (`ILPES GRUPO 10 29-10-2026.xlsx`) y exportar un **libro Excel profesional de 10 hojas** con portada ejecutiva, matrices $V_0$ y $V_t$, $Q_{ij}$, $Q_r$, $CR_r$, $X_{ij}$, Cuadrantes de Silva Lira, Shift & Share Clásico/Modificado e indicadores REAT.

### 6. Laboratorio Oficial de Cátedra + Exportador Excel con Fórmulas Vivas
* **Cruce PIB Regional y Censo 2024:** Serie de PIB Regional encadenado del Banco Central (2015–2025) cruzada con la población del Censo Oficial 2024 (INE) y proyecciones demográficas para las 16 regiones de Chile.
* **Sistema TAREA (Manual 59 ILPES — Lira y Quiroga):** Resolución completa del caso de cátedra (*Badalona, Pueblo Seco y Pueblo Nuevo*) y del caso de las *Regiones de Colombia (1980–1996)*, incluyendo las **6 tipologías de Boisier (1980)**, las **14 tipologías de Stilwell (1969)**, Concentración Espacial ($Q_s$), Redistribución ($CR_s$) y Matriz de Asociación Geográfica ($CA_{i,k}$).
* **Laboratorio Unidad 3:** Convergencia Base 1 (2010–2020), Gini por método de trapecios, Theil por cuotas, indicadores de desigualdad **CASEN (2009–2024)** ($10/10, 20/20, 10/40$), Concentración Relativa $CR_3$ en la Región de Los Lagos y **Cadenas de Markov** con vector ergódico de largo plazo (*Figueroa y Herrero, 2003*).
* **Descarga de Excel con Fórmulas Nativas Activas:** Genera el archivo `Laboratorio_Catedra_Formulas_Vivas_ULagos.xlsx` con funciones vivas de Excel (`=LN`, `=SLOPE`, `=INTERCEPT`, `=RSQ`, `=STDEV.P`, `=SUM`, trapecios de Lorenz, MADE y Rondinelli).

### 7. Laboratorio Práctico Controles 2, 4 y 5 (My Maps, Cadenas, ELITE y PROT)
* **Control 2 y Control 4 (Google My Maps):** Base georreferenciada de **22 establecimientos de la Cadena Láctea y Agroindustrial de Osorno** y base oficial de los **15 Liceos de Osorno (`Liceos.xlsx`)**, con validador automático de la rúbrica de 8 criterios técnicos y exportador directo para importar en Google My Maps.
* **Unidad 4 y Control 4 (Cadenas de Valor y Entrevistas):** Caracterización de eslabones, actores directos y entidades de apoyo para la **Cadena Láctea y Quesera (ODEPA, 2019)** y el **Clúster de la Salmonicultura (Araya, 2016)**, junto con la pauta de 3 perfiles de entrevista y cuestionario validado.
* **Sistema ELITE (Boisier, 1995):** Sociograma interinstitucional con índices de Cooperatividad, Conflictividad, Neutralidad y Ranking de Importancia Social Relativa.
* **Control 5 y PROT (SUBDERE-CEPAL, 2011):** Cálculo de **Índice de Primacía Urbana** (2 y 4 ciudades) y Ley de Zipf entre los Censos 2017 y 2024 (Regiones de Los Lagos y Los Ríos), **Escala de Guttman** para las 10 mayores comunas en las 4 dimensiones oficiales, **Matriz de Aislamiento Comunal (0/1)** y buscador normativo del **Anexo 2 del PROT**.

---

## Estructura del Repositorio

```text
DESARROLLO-Y-GESTION-TERRITORIAL-2026/
├── app.py                              # Aplicación principal Streamlit y enrutador de los 7 módulos
├── motor_sii_exportador.py             # Motor econométrico SII (ILPES / MADE / REAT) y exportador de 10 hojas
├── motor_laboratorio_catedra.py        # Motor Sistema TAREA, PIB Censo 2024, Markov y Excel con fórmulas vivas
├── motor_redes_territorio_ot.py        # Motor Controles 2, 4 y 5 (My Maps, Cadenas, ELITE, Guttman, Aislamiento y PROT)
├── ILPES GRUPO 10 29-10-2026.xlsx      # Base de datos estadísticos SII e ILPES integrada en el repositorio
├── cuestionario_entrevista.pdf         # Instrumento oficial de entrevista para trabajo de campo
├── requirements.txt                    # Dependencias del entorno de ejecución en Python
└── README.md                           # Documentación técnica y académica del proyecto
```

---

## Ejecución Local

1. Clonar el repositorio e instalar las dependencias:

```bash
git clone [https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026.git](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026.git)
cd DESARROLLO-Y-GESTION-TERRITORIAL-2026
pip install -r requirements.txt
```

2. Iniciar la plataforma interactiva en el navegador:

```bash
streamlit run app.py
```

---

## Referencias Metodológicas Principales

* **Boisier, S. (1980, 1995).** *Técnicas de análisis regional con información limitada* y * El desafío territorial: Sistema ELITE*. ILPES / CEPAL.
* **Dini, M. (2010).** *Competitividad, redes de empresas y cooperación empresarial*. Serie Gestión Pública N° 72, CEPAL.
* **Figueroa, E. & Herrero, C. (2003).** *Análisis dinámico del desarrollo comunal en Chile mediante Cadenas de Markov*.
* **Lira, L. & Quiroga, B. (2009).** *Técnicas de análisis regional (Sistema TAREA)*. Serie Manuales N° 59, ILPES / CEPAL.
* **Padilla Pérez, R. & Oddone, N. (2016).** *Manual para el fortalecimiento de cadenas de valor*. CEPAL.
* **Rondinelli, D. A. (1985).** *Applied Methods of Regional Analysis: The Spatial Dimensions of Development Policy*.
* **Silva Lira, I. (2005).** *Disparidades, competitividad territorial y desarrollo local y regional en América Latina*. Serie Gestión Pública N° 33, ILPES / CEPAL.
* **SUBDERE & CEPAL (2011).** *Guía Metodológica para la Elaboración del Plan Regional de Ordenamiento Territorial (PROT)*.
