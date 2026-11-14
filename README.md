# Desarrollo y Gestión Territorial 2026 — Universidad de Los Lagos

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://desarrollo-y-gestion-territorial-2026-ec6keylhsgra88s77bkl6f.streamlit.app/)
[![Lanzar Plataforma en Streamlit](https://img.shields.io/badge/ABRIR_PLATAFORMA_INTERACTIVA_EN_STREAMLIT-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://desarrollo-y-gestion-territorial-2026-ec6keylhsgra88s77bkl6f.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026)

Plataforma integral de modelamiento econométrico, análisis espacial, redes productivas y ordenamiento territorial desarrollada en **Python + Streamlit** para la asignatura de **Desarrollo y Gestión Territorial** (Ingeniería Comercial, Universidad de Los Lagos — Prof. Claudio Mancilla).

**Acceso directo a la aplicación web en vivo:**  
https://desarrollo-y-gestion-territorial-2026-ec6keylhsgra88s77bkl6f.streamlit.app/

---

## Guía Rápida de Uso (Sin conocimientos de programación)

Cualquier estudiante, grupo de trabajo o analista regional puede utilizar la plataforma directamente desde el navegador en **3 pasos**:

1. **Seleccionar el Módulo en la Barra Lateral Izquierda:** El menú organiza secuencialmente las unidades del curso y las entregas prácticas (Módulos 1 al 7).
2. **Elegir Región, Variable o Matriz de Trabajo:**
   * En los **Módulos 1, 2 y 5**, puedes seleccionar cualquier región de Chile disponible en la base nacional del SII (`ILPES GRUPO 10 29-10-2026.xlsx`), cambiar la métrica económica (*Ventas en UF, Trabajadores dependientes, Número de empresas, Renta neta*) o subir tu propio archivo Excel del SII.
   * En los **Módulos 3, 4 y 7**, todas las tablas en pantalla son **interactivas y editables en vivo**: haz doble clic sobre cualquier celda para modificar coordenadas, poblaciones censales o vínculos `1/0` y los gráficos, mapas e indicadores se recalcularán al instante.
3. **Descargar Entregables en Excel con Fórmulas Nativas Activas:** Cada módulo cuenta con botones de exportación directa a `.xlsx` que entregan tanto las matrices procesadas como libros con **fórmulas nativas de Excel vivas** (`=LN`, `=SLOPE`, `=STDEV.P`, `=RANK`, `=SUM`, `=COUNTIF`), listos para auditar o adjuntar en controles e informes.

---

## Potencia del Sistema vs. Flujo de Trabajo Manual Tradicional

El desarrollo de esta arquitectura unificada reemplaza el uso fragmentado de múltiples programas (planillas Excel manuales, scripts aislados en R Studio para el paquete `REAT`, software antiguo de escritorio como `UCINET` y validación manual de coordenadas para Google My Maps), eliminando errores de arrastre de fórmulas y reduciendo horas de cálculo operativo a segundos:

| Dimensión Analítica / Tarea | Flujo Manual Tradicional (Excel / R / UCINET) | Motor Automatizado en Python + Streamlit |
| :--- | :--- | :--- |
| **Limpieza y cruce de microdatos SII (26 MB)** | Filtrado manual con tablas dinámicas, riesgo de desalineación de comunas o rubros sin datos entre $t_0$ y $t_f$ (**2 a 4 horas por región**). | Alineación matricial exacta ($V_0$ y $V_t$) con limpieza automática de caracteres del SII y cambio de región/año en **1 clic (< 2 segundos)**. |
| **Sistema TAREA (ILPES) y Shift & Share (MADE)** | Construcción manual de 8 a 10 pestañas interconectadas para $Q_{ij}, Q_r, CR_r, X_{ij}, M_j$, Efectos $ET, EE, ED, EI, EM, ERM$ y clasificación visual en las 6 tipologías de Boisier y 14 de Stilwell. | Cálculo simultáneo de todas las matrices e identificación algorítmica inmediata de los **Cuadrantes de Silva Lira**, **6 tipos de Boisier** y **14 tipos de Stilwell**. |
| **Convergencia ($\sigma, \beta$) y Desigualdad (`REAT`)** | Exportar datos a R Studio, instalar paquete `REAT`, correr regresiones OLS por comando, armar trapecios de Lorenz a mano y programar potencias de matrices de Markov. | Réplica nativa en Python de **Convergencia $\sigma$ y $\beta$** ($\lambda$, semivida, $R^2$, $p$-valor), **Lorenz/Gini**, **Theil**, **HHI**, **Hannah-Kay ($\alpha$ dinámico)** y **Markov a $n$ décadas**. |
| **Redes Sociométricas (UCINET / Dini) y Sistema ELITE** | Uso de software externo (`UCINET` / `NetDraw`) o conteo manual de vínculos de cooperación, conflicto y neutralidad sobre matrices cuadradas. | Editor matricial en pantalla con renderizado en tiempo real del grafo sociométrico, grados de entrada/salida, densidad de Dini (2010) y Poder Social ELITE (Boisier, 1995). |
| **Georreferenciación Google My Maps (Controles 2 y 4)** | Revisión fila por fila de comas vs. puntos decimales, rangos de latitud/longitud, coordenadas duplicadas y encabezados rotos al importar en My Maps. | **Validador automático de los 8 criterios técnicos de rúbrica**, previsualización en mapa interactivo y descarga de `.xlsx` limpio en fila 1 para Google My Maps. |
| **Ordenamiento Territorial y Control 5 Multirregional** | Búsqueda comunal en censos INE, cálculo manual de ponderaciones inversas de Rondinelli ($100/F_i$) y conteo de rutas de aislamiento. | **97 comunas precargadas en 4 regiones** (Los Lagos, Biobío, Los Ríos y La Araucanía), Primacía 2017–2024, Guttman en 4 dimensiones, Aislamiento 0/1 y buscador normativo PROT. |
| **Auditoría Académica de Fórmulas en Excel** | Entregar valores planos pegados como número o arriesgar referencias rotas (`#¡REF!`, `#¡DIV/0!`) al mover columnas. | Generación en memoria (`openpyxl`) de libros `.xlsx` profesionales de **10 hojas SII** y **4 hojas de cátedra/controles con fórmulas nativas de Excel activas** en cada celda. |

---

## Arquitectura Detallada de los 7 Módulos

### 1. Técnicas de Análisis Regional (ILPES / SII 2005–2024)
* Procesamiento automatizado de microdatos comunales y sectoriales del **Servicio de Impuestos Internos (SII)** con foco en las 33 comunas de la Región del Biobío y selector multirregional.
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
* **Cruce PIB Regional y Censo 2024:** Serie de PIB Regional encadenado del Banco Central (2015–2025) cruzada con la población del Censo Oficial 2024 (INE) y proyecciones demográficas para las **16 regiones de Chile**.
* **Sistema TAREA (Manual 59 ILPES — Lira y Quiroga):** Resolución completa del caso de cátedra (*Badalona, Pueblo Seco y Pueblo Nuevo*) y del caso de las *Regiones de Colombia (1980–1996)*, incluyendo las **6 tipologías de Boisier (1980)**, las **14 tipologías de Stilwell (1969)**, Concentración Espacial ($Q_s$), Redistribución ($CR_s$) y Matriz de Asociación Geográfica ($CA_{i,k}$).
* **Laboratorio Unidad 3:** Convergencia Base 1 (2010–2020), Gini por método de trapecios, Theil por cuotas, indicadores de desigualdad **CASEN (2009–2024)** ($10/10, 20/20, 10/40$), Concentración Relativa $CR_3$ en la Región de Los Lagos y **Cadenas de Markov** con vector ergódico de largo plazo (*Figueroa y Herrero, 2003*).
* **Descarga de Excel con Fórmulas Nativas Activas:** Genera el archivo `Laboratorio_Catedra_Formulas_Vivas_ULagos.xlsx` con funciones vivas de Excel (`=LN`, `=SLOPE`, `=INTERCEPT`, `=RSQ`, `=STDEV.P`, `=SUM`, trapecios de Lorenz, MADE y Rondinelli).

### 7. Laboratorio Práctico Multirregional Controles 2, 4 y 5 (My Maps, Cadenas, ELITE y PROT)
* **Control 2 y Control 4 (Google My Maps):** Base georreferenciada editable de **22 establecimientos de la Cadena Láctea y Agroindustrial de Osorno** y base oficial de los **15 Liceos de Osorno (`Liceos.xlsx`)**, con validador automático de la rúbrica de 8 criterios técnicos y exportador directo para importar en Google My Maps.
* **Unidad 4 y Control 4 (Cadenas de Valor y Entrevistas):** Caracterización de eslabones, actores directos y entidades de apoyo para la **Cadena Láctea y Quesera (ODEPA, 2019)** y el **Clúster de la Salmonicultura (Araya, 2016)**, junto con la pauta de 3 perfiles de entrevista y cuestionario validado de 8 preguntas.
* **Sistema ELITE (Boisier, 1995):** Sociograma interinstitucional con índices de Cooperatividad, Conflictividad, Neutralidad y Ranking de Importancia Social Relativa.
* **Control 5 Multirregional (97 Comunas) y PROT (SUBDERE-CEPAL, 2011):** Cálculo interactivo de **Índice de Primacía Urbana** (2 y 4 ciudades) y Ley de Zipf entre los Censos 2017 y 2024 para **4 regiones completas** (*Los Lagos 30 comunas, Biobío 33 comunas, Los Ríos 12 comunas y La Araucanía 32 comunas*), **Escala de Guttman** adaptada al Top 10 comunal en las 4 dimensiones oficiales, **Matriz de Aislamiento Comunal (0/1)** y buscador normativo del **Anexo 2 del PROT**, con exportación a Excel con fórmulas vivas para la región seleccionada.

---

## Estructura del Repositorio

```text
DESARROLLO-Y-GESTION-TERRITORIAL-2026/
├── app.py                              # Aplicación principal Streamlit y enrutador de los 7 módulos
├── motor_sii_exportador.py             # Motor econométrico SII (ILPES / MADE / REAT) y exportador de 10 hojas
├── motor_laboratorio_catedra.py        # Motor Sistema TAREA, PIB Censo 2024, Markov y Excel con fórmulas vivas
├── motor_redes_territorio_ot.py        # Motor Multirregional Controles 2, 4 y 5 (My Maps, Cadenas, ELITE, Guttman y PROT)
├── ILPES GRUPO 10 29-10-2026.xlsx      # Base de datos estadísticos SII e ILPES integrada en el repositorio
├── cuestionario_entrevista.pdf         # Instrumento oficial de entrevista para trabajo de campo
├── requirements.txt                    # Dependencias del entorno de ejecución en Python
└── README.md                           # Documentación técnica, guía de uso y comparativa metodológica
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

* **Boisier, S. (1980, 1995).** *Técnicas de análisis regional con información limitada* y *El desafío territorial: Sistema ELITE*. ILPES / CEPAL.
* **Dini, M. (2010).** *Competitividad, redes de empresas y cooperación empresarial*. Serie Gestión Pública N° 72, CEPAL.
* **Figueroa, E. & Herrero, C. (2003).** *Análisis dinámico del desarrollo comunal en Chile mediante Cadenas de Markov*.
* **Lira, L. & Quiroga, B. (2009).** *Técnicas de análisis regional (Sistema TAREA)*. Serie Manuales N° 59, ILPES / CEPAL.
* **Padilla Pérez, R. & Oddone, N. (2016).** *Manual para el fortalecimiento de cadenas de valor*. CEPAL.
* **Rondinelli, D. A. (1985).** *Applied Methods of Regional Analysis: The Spatial Dimensions of Development Policy*.
* **Silva Lira, I. (2005).** *Disparidades, competitividad territorial y desarrollo local y regional en América Latina*. Serie Gestión Pública N° 33, ILPES / CEPAL.
* **SUBDERE & CEPAL (2011).** *Guía Metodológica para la Elaboración del Plan Regional de Ordenamiento Territorial (PROT)*.
