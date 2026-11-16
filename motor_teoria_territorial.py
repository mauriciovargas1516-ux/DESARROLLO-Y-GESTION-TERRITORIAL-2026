# -*- coding: utf-8 -*-
"""
MÓDULO DE PROFUNDIZACIÓN TEÓRICA Y DEBATES ACADÉMICOS
Asignatura: Desarrollo y Gestión Territorial — Universidad de Los Lagos (Prof. Claudio Mancilla)
Archivo: motor_teoria_territorial.py

Integra marcos teóricos avanzados de la Economía Regional, la Nueva Economía Geográfica (NEG)
y la Sociología Económica (Krugman, Perroux, Myrdal, Hirschman, Granovetter, Christaller).
"""

import streamlit as st
from motor_redes_dinamicas_dini import renderizar_burbuja_tip

def renderizar_modulo_teoria_avanzada():
    st.header("9. Fundamentos Teóricos y Debates Académicos en Economía Regional")
    st.markdown(
        "Módulo de profundización conceptual diseñado para conectar los motores cuantitativos de la plataforma "
        "(ILPES, REAT, Dini, Rondinelli) con los grandes paradigmas del pensamiento territorial y la "
        "Nueva Economía Geográfica (NEG)."
    )

    tabs_teoria = st.tabs([
        "1. Polos de Crecimiento y Causalidad (Perroux, Myrdal, Hirschman)",
        "2. Nueva Economía Geográfica y Aglomeración (Krugman)",
        "3. Capital Social, Redes y Vínculos Débiles (Granovetter)",
        "4. Jerarquía Urbana y Lugares Centrales (Christaller, Lösch)",
    ])

    with tabs_teoria[0]:
        st.subheader("Polarización, Causalidad Cumulativa y Encadenamientos Productivos")
        st.markdown(
            "En la evolución del pensamiento territorial, el desarrollo deja de concebirse como un proceso lineal y homogéneo "
            "para entenderse como un fenómeno polarizado y acumulativo."
        )

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                "##### A. Polos de Crecimiento (François Perroux, 1955)\n"
                "- **Concepto clave:** El crecimiento no aparece en todas partes a la vez; se manifiesta en puntos o **polos de crecimiento** "
                "con intensidades variables, desde los cuales se propaga a través de canales económicos hacia el resto del territorio.\n"
                "- **Efectos de Polarización:**\n"
                "  - *Efecto de Arrastre (Backwash):* Atracción centrípeta de capitales, trabajo calificado e insumos hacia el polo dinámico.\n"
                "  - *Efecto de Difusión (Spread):* Propagación de demanda, spillover tecnológico y encadenamientos hacia las periferias."
            )
            renderizar_burbuja_tip(
                titulo_boton="Causalidad Cumulativa (Myrdal)",
                titulo_interno="Causalidad Circular y Cumulativa (Gunnar Myrdal, 1957)",
                formula_latex=r"Y_t = f(Y_{t-1}, 	ext{Inversión}, 	ext{Migración Neta})",
                explicacion_md=(
                    "- Myrdal sostiene que el mercado libre tiende cumulativamente a aumentar, no a disminuir, las desigualdades regionales.\n"
                    "- Un choque inicial favorable en una comuna (ej. instalación de un polo industrial) activa fuerzas circulares que atraen más factores productivos, desfavoreciendo a las regiones rezagadas."
                ),
            )

        with c2:
            st.markdown(
                "##### B. Encadenamientos Hacia Atrás y Hacia Adelante (Albert Hirschman, 1958)\n"
                "- **Encadenamientos hacia atrás (*Backward Linkages*):** Estimulación de la demanda sobre proveedores de insumos, maquinaria y materias primas ubicados en el territorio.\n"
                "- **Encadenamientos hacia adelante (*Forward Linkages*):** Estímulo para la creación de industrias procesadoras o de servicios que utilizan los productos del sector matriz.\n"
                "- *Implicancia de política:* La selección de sectores clave con altos multiplicadores de enlace maximiza el impacto regional por cada peso invertido."
            )
            renderizar_burbuja_tip(
                titulo_boton="Efectos Hirschman",
                titulo_interno="Eslabones Críticos en la Cadena de Valor",
                formula_latex=r"E_k = rac{\sum_j I_{jk}}{V_k}",
                explicacion_md=(
                    "- Un sector clave presenta altos índices de encadenamiento tanto hacia atrás como hacia adelante.\n"
                    "- Permite superar cuellos de botella en economías subdesarrolladas mediante desequilibrios intencionados en la inversión."
                ),
            )

    with tabs_teoria[1]:
        st.subheader("Nueva Economía Geográfica (NEG): Fuerzas Centrípetas y Centrifugas (Paul Krugman, 1991)")
        st.markdown(
            "La Nueva Economía Geográfica (Premio Nobel de Economía 2008) explica la aglomeración espacial de la actividad "
            "económica combinando tres pilares: **rendimientos de escala crecientes**, **costos de transporte** y **competencia imperfecta**."
        )

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(
                "##### Fuerzas Centrípetas (Favorecen la Aglomeración)\n"
                "1. **Economías de escala internas:** Las empresas concentran su producción en pocas plantas gigantes para minimizar costos unitarios.\n"
                "2. **Mercado de trabajo especializado:** Las comunas densas ofrecen reserva de talento con habilidades específicas.\n"
                "3. **Externalidades de conocimiento y *spillovers*:** La proximidad física facilita la innovación y el intercambio informal de información.\n"
                "4. **Encadenamientos de demanda y oferta (*Market Size Effects*):** Las empresas se ubican donde hay más clientes y clientes donde hay más empleadores."
            )
        with cc2:
            st.markdown(
                "##### Fuerzas Centrífugas (Dispersan la Actividad)\n"
                "1. **Costos de transporte y barreras logísticas:** Llevar productos finales a mercados alejados encarece el producto si se concentra en exceso.\n"
                "2. **Competencia local intensa:** Mayor rivalidad por el mercado en zonas densas.\n"
                "3. **Precios de suelo y congestión:** El valor de las rentas inmobiliarias y los tiempos de desplazamiento desalientan la aglomeración infinita.\n"
                "- *Conclusión NEG:* El territorio experimenta rupturas no lineales; al bajar los costos de transporte por debajo de un umbral crítico, las regiones pueden despoblarse abruptamente hacia un único centro dominante (macrocefalia)."
            )

    with tabs_teoria[2]:
        st.subheader("Sociología Económica del Territorio: Capital Social y Vínculos Débiles (Mark Granovetter)")
        st.markdown(
            "Los Sistemas Productivos Locales (SPL) y los clústeres no solo dependen de infraestructura dura o subsidios financieros, "
            "sino de la **estructura social y la gobernanza colaborativa** entre los actores locales."
        )

        cg1, cg2 = st.columns(2)
        with cg1:
            st.markdown(
                "##### A. La Fuerza de los Vínculos Débiles (Granovetter, 1973)\n"
                "- **Vínculos Fuertes:** Relaciones de confianza densa y frecuente (familia, amigos íntimos, socios habituales). Generan alta cohesión pero **información redundante**.\n"
                "- **Vínculos Débiles:** Relaciones ocasionales o puentes entre redes distintas (conocidos, contactos interregionales). Son los **canales clave de innovación**, ya que conectan mundos que no dialogan habitualmente y permiten la llegada de tecnología externa al clúster."
            )
        with cg2:
            st.markdown(
                "##### B. Confianza y Capital Social (Putnam / Coleman)\n"
                "- **Capital social cognitivo y relacional:** La cooperación interempresarial (como en los distritos industriales italianos o PymeMad Biobío) se sustenta en normas cívicas, reputación y confianza institucional.\n"
                "- *Riesgo de bloqueo (*lock-in*):* Si un clúster cierra sus vínculos y cae en endogamia institucional, pierde capacidad de adaptación ante cambios tecnológicos globales."
            )

    with tabs_teoria[3]:
        st.subheader("Teoría de Lugares Centrales y Jerarquía Urbana (Walter Christaller / August Lösch)")
        st.markdown(
            "Explica el espaciamiento, tamaño y número de ciudades y centros de servicio en un territorio basándose en dos conceptos fundamentales: "
            "el **Umbral (*Threshold*)** y el **Alcance (*Range*)** de un bien o servicio."
        )

        ccx1, ccx2 = st.columns(2)
        with ccx1:
            st.markdown(
                "##### Principios de Organización Espacial\n"
                "- **Umbral:** Volumen mínimo de ventas o población requerido para que un servicio o comercio sea rentable.\n"
                "- **Alcance (Rango):** Distancia máxima que un consumidor está dispuesto a viajar para adquirir dicho bien o servicio.\n"
                "- **Jerarquía Hexagonal:** En un plano isótropo sin accidentes geográficos, los mercados tienden a organizarse en mallas hexagonales perfectas de orden inferior (pueblos), medio (ciudades provinciales) y superior (metrópolis regionales)."
            )
        with ccx2:
            st.markdown(
                "##### Conexión con el Escalograma de Rondinelli\n"
                "- El modelo de Rondinelli que aplicas en el Módulo 4 de tu app operativa es la operacionalización empírica de Christaller.\n"
                "- Permite auditar si una región presenta una distribución equilibrada de centros intermedios o si padece una primacía urbana desequilibrada."
            )
