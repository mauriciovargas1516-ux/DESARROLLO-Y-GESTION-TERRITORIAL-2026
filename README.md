# Desarrollo y Gestión Territorial 2026 — ULagos

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/)
[![Lanzar App Interactiva](https://img.shields.io/badge/🚀_ABRIR_PLATAFORMA_INTERACTIVA_EN_STREAMLIT-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/mauriciovargas1516-ux/DESARROLLO-Y-GESTION-TERRITORIAL-2026)

Motor de cálculo econométrico, espacial y territorial en **Python + Streamlit** desarrollado para la asignatura de **Desarrollo y Gestión Territorial** (Ingeniería Comercial, Universidad de Los Lagos — Prof. Claudio Mancilla).

**Acceso directo a la aplicación web en vivo:**  
**[https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/](https://desarrollo-y-gestion-territorial-2026-9yq3jazfc52x93tfumxwpz.streamlit.app/)**

---

##  Módulos Integrados en la Plataforma

1. **Técnicas de Análisis Regional (ILPES / SII Región del Biobío 2014–2024):**
   - Clasificación interactiva de las 33 comunas en los **Cuadrantes de Silva Lira (CEPAL, 2005)**.
   - Matriz de **Cociente de Localización ($Q_{ij}$)**, **Coeficiente de Especialización ($Q_r$)** y **Coeficiente de Reestructuración ($CR_r$)** en 18 rubros económicos del SII.
   - Cálculo de **Base Económica Exportadora ($X_j$)** y **Multiplicador Básico Regional ($M_j$)**.
   - Descomposición **Shift & Share (MADE Clásico y Modificado)**: Efecto Total ($ET_j$), Estructural ($EE_j$), Diferencial ($ED_j$), Estructural Inverso ($EI_j$), Estructural Modificado ($EM_j$) y Regional Modificado ($ERM_j$).

2. **Disparidades, Concentración y Convergencia Regional (Motor REAT en Python):**
   - Réplica automatizada del paquete `REAT` de R aplicada a las 33 comunas del Biobío y casos de cátedra.
   - **Convergencia Sigma ($\sigma_{\ln}$)**, **Coeficiente de Variación ($CV$)** y regresión OLS de **Convergencia Beta Absoluta ($\beta$)** con cálculo de velocidad ($\lambda$) y semivida (*Half-life*).
   - **Curva de Lorenz**, **Índice de Gini** (estándar y normalizado), **Entropía de Theil**, **Herfindahl-Hirschman ($HHI$)** e **Índice de Hannah-Kay ($HK_\alpha$)** con parámetro de sensibilidad $\alpha$ dinámico.

3. **Sistemas Productivos Locales (SPL), Redes Empresariales y Cadenas de Valor:**
   - Simulador de grafos de articulación empresarial (reemplazo interactivo de **UCINET**) con cálculo de densidad y grados nodales según **Dini (2010)**.
   - Diagnóstico de cadenas de valor bajo metodología **CEPAL (Padilla y Oddone, 2016)** y caracterización del ecosistema **MIPE en la Región de Los Lagos**.

4. **Ordenamiento Territorial y Georreferenciación:**
   - **Ranking de Asentamientos** e **Índice de Primacía Urbana ($IP$)**.
   - **Matriz de Complejidad Funcional de Rondinelli (Escala de Guttman)**.
   - Mapa georreferenciado interactivo de los **15 establecimientos de educación media de Osorno**.

5. **Conmutación Laboral Intertemporal en la Patagonia Chilena:**
   - Evaluación de flujos de conmutación intra, inter y extrarregional hacia los 5 Centros Nodales Principales (**Valdivia, Osorno, Puerto Montt, Coyhaique y Punta Arenas**).
   - Cálculo automatizado del **Índice de Similitud Temporal** y prueba no paramétrica $\chi^2$ (*Mancilla, Soza-Amigo y Ferrada, 2021*).

---

## 🛠️ Ejecución Local

```bash
pip install -r requirements.txt
streamlit run app.py
