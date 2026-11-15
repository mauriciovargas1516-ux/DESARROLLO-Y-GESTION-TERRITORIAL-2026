[readme_desarrollo_y_gestion_territorial_2026.md](https://github.com/user-attachments/files/34865658/readme_desarrollo_y_gestion_territorial_2026.md)
# Plataforma Integral de Desarrollo y Gestión Territorial 2026 — ULagos

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://desarrollo-y-gestion-territorial-2026-ec6keylhsgra88s77bkl6f.streamlit.app/)
[![Lanzar Plataforma en Streamlit](https://img.shields.io/badge/ABRIR_PLATAFORMA_TERRITORIAL_EN_STREAMLIT-1E3A8A?style=for-the-badge&logo=streamlit&logoColor=white)](https://desarrollo-y-gestion-territorial-2026-ec6keylhsgra88s77bkl6f.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026)

Motor econométrico, sociométrico y espacial desarrollado en **Python (`Streamlit`, `Pandas`, `NumPy`, `SciPy`, `Plotly`, `OpenPyXL`)** para la asignatura **Desarrollo y Gestión Territorial** (Carrera de Ingeniería Comercial, Universidad de Los Lagos — Prof. Claudio Mancilla). Integra en **8 módulos interactivos** el procesamiento de estadísticas tributarias comunales del **SII (2014–2024)**, metodologías de análisis regional de **ILPES / CEPAL (Lira y Quiroga; Silva Lira)**, réplica econométrica del paquete **REAT** de R, **Sistemas Productivos Locales y Redes Empresariales (Dini, 2010; UCINET)**, **Cadenas de Valor (Padilla y Oddone, 2016)** y **Ordenamiento Territorial (Rondinelli, Guttman, Primacía Urbana, von Thünen, Boisier ELITE y PROT)**.

**Acceso directo a la aplicación web en vivo:**  
https://desarrollo-y-gestion-territorial-2026-ec6keylhsgra88s77bkl6f.streamlit.app/

---

## Arquitectura de los 8 Módulos Interactivos (`app.py`)

### 1. Técnicas de Análisis Regional (ILPES / SII 2014–2024)
* Construcción automatizada de matrices sectoriales-comunales $V_{ij}$ desde la base oficial del SII (`ILPES GRUPO 10 29-10-2026.xlsx`).
* Cálculo de **Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)**, **Coeficiente de Reestructuración ($CR_r$)**, **Base Económica Exportadora de Tiebout ($X_j$ y multiplicador $M_j$)**, **Cuadrantes de Silva Lira (CEPAL, 2005)** y descomposición **Shift & Share Clásico y Modificado (MADE: $ET_j = EE_j + ED_j$, $EI_j, EM_j, ERM_j$)** con Notas Metodológicas desplegables.

### 2. Disparidades, Concentración y Convergencia Regional (Motor REAT)
* Réplica exacta en Python del paquete **REAT (*Regional Economic Analysis Toolbox*)**: **Convergencia Sigma ($\sigma_t, CV_t$)**, **Convergencia Beta Absoluta OLS ($\beta$, velocidad anual $\lambda$, semivida $t_{1/2}$ y valor $p$)**, **Curva de Lorenz**, **Índice de Gini ($G, G^*$)**, **Entropía de Theil ($T$)**, **Índice de Herfindahl-Hirschman ($HHI$)** e **Índice de Hannah-Kay ($HK_\alpha$)**.

### 3. Sistemas Productivos Locales (SPL), Redes (UCINET) y Cadenas de Valor
* Simulador interactivo de matrices de adyacencia binaria (reemplazo de **UCINET**) con cálculo de grados de entrada/salida, centralidad nodal y densidad de red, junto al diagnóstico de restricciones y *Upgrading* de la cadena forestal-maderera (**PymeMad Biobío / Los Ángeles**).

### 4. Ordenamiento Territorial, Escalograma de Rondinelli y Georreferenciación
* Matriz editable de funciones urbanas con ponderación inversa de frecuencia ($W_k = N / f_k$) para el cálculo del **Índice de Centralidad Funcional de Rondinelli (1985)** y cartografía interactiva.

### 5. Exportador Maestro SII (Generador Excel de 10 Hojas)
* Compila y descarga un libro `.xlsx` de 10 hojas con todas las matrices sectoriales, indicadores ILPES, Shift & Share y regresiones REAT para cualquier región de Chile.

### 6. Laboratorio de Cátedra + Exportador Excel con Fórmulas Nativas Vivas
* Simulador de **Movilidad de Quah (Cadenas de Markov y Vector Ergódico)**, **Descomposición de Theil ($T = T_B + T_W$)**, **Concentración Espacial de Ellison-Glaeser ($\gamma_i$)**, **Curvas de Renta de von Thünen** y descarga de libro Excel con fórmulas nativas vinculadas (`=SLOPE`, `=STDEV.P`, `=SUMPRODUCT`, `=RANK`, `=COUNTIF`).

### 7. Controles 2, 4 y 5: Google My Maps, Cadenas, Sistema ELITE y PROT Multirregional
* Catastro georreferenciado validado para **Google My Maps** (15 Liceos de Osorno y 22 establecimientos del complejo lácteo-quesero e industrial de Osorno), **Sistema ELITE de Sergio Boisier (1995)** y **Matriz de Compatibilidad Territorial PROT** para las 97 comunas de Biobío, La Araucanía, Los Ríos y Los Lagos.

### 8. Extensión Interactiva: Redes en Vivo (Dini, 2010) y Gradientes de Concentración (`motor_redes_dinamicas_dini.py`)
* **Constructor Animado de Redes Paso a Paso:** Permite visualizar mediante deslizador de secuencia o animación `Play` cómo se tejen los vínculos en las **5 estructuras de Dini (2010, `04 SPL.pdf` pág. 14)** (*Red Simétrica, Red con Liderazgo, Red Jerárquica, Red de Redes y Red de Producción de Aviones*) y en los **2 casos reales del Control 4** (*Red Láctea-Quesera de Osorno* y *Clúster Maderero PymeMad Biobío*), calculando en tiempo real el grado nodal $k_i$, la fórmula oficial de densidad:
  $$D = \frac{2L}{n(n-1)}$$
  y la curva de **Gradiente de Concentración de la Red ($GC_{red}$)**, con exportación directa a `.xlsx` con fórmulas vivas.
* **Simulador de Gradiente de Concentración Territorial (`06 OT 2024.pdf`):** Integra el **Índice de Primacía Urbana ($IP_4 = \frac{P_1}{P_2+P_3+P_4}$)** con su tabla de estandarización de cátedra ($0$ a $3$), la curva de **Gradiente Jerárquico Funcional de Guttman / Rondinelli** y los anillos de **Renta Locacional de von Thünen ($LR(d) = Y(m-c) - Ytd$)**.
* **Comparador de las 3 Estrategias de Articulación (`04 SPL.pdf` págs. 5–13):** Red Empresarial, Clúster Productivo y Sistema Productivo Local (SPL) junto al Cuadro 2 de cooperación interempresarial de **Schmitz (1999)**.

---

## Estructura de Archivos del Repositorio

```text
DESARROLLO-Y-GESTION-TERRITORIAL-2026/
├── app.py                               # Aplicación principal en Streamlit (Menú de 8 Módulos + Notas Metodológicas)
├── motor_sii_exportador.py              # Motor matricial SII, ILPES, Shift & Share MADE, REAT y exportador Excel 10 hojas
├── motor_laboratorio_catedra.py         # Motor de Markov (Quah), Theil (TB + TW), Ellison-Glaeser y Excel Fórmulas Vivas
├── motor_redes_territorio_ot.py         # Motor Controles 2, 4 y 5 (Google My Maps, ODEPA, Boisier ELITE y PROT 97 comunas)
├── motor_redes_dinamicas_dini.py        # Módulo 8: Redes animadas en vivo (Dini 2010), Notas Metodológicas y Gradientes
├── ILPES GRUPO 10 29-10-2026.xlsx       # Base oficial nacional del SII e ILPES (26,1 MB)
├── cuestionario_entrevista.pdf          # Instrumento oficial de levantamiento primario en terreno
├── requirements.txt                     # Dependencias para despliegue en Streamlit Cloud
└── README.md                            # Documentación técnica y académica del repositorio
```

---

## Instalación y Ejecución Local

```bash
git clone https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026.git
cd DESARROLLO-Y-GESTION-TERRITORIAL-2026
pip install -r requirements.txt
streamlit run app.py
```
