# Desarrollo y Gestion Territorial 2026 - ULagos

Aplicacion en Python y Streamlit para el ramo Desarrollo y Gestion Territorial (Ingenieria Comercial, Universidad de Los Lagos).

App en linea: https://desarrollo-y-gestion-territorial-2026-azi4k3liecm2g45r97lkff.streamlit.app/

## Datos utilizados

- **Empresas por rubro y comuna (2014-2024):** base del Servicio de Impuestos Internos (`ILPES GRUPO 10 29-10-2026.xlsx`).
- **Poblacion Censo 2017:** resultados definitivos del INE por comuna (`1_1_poblacion.xls`, Biobio: 1.556.805 habitantes).
- **Poblacion Censo 2024:** resultados regionales del INE (`poblacion 2024.pdf`, Biobio: 1.613.059 habitantes).
- **Entrevistas Control 4:** pauta en `cuestionario_entrevista.pdf`.

Los indicadores economicos (ILPES, Silva Lira, MADE y convergencia) trabajan con datos del SII para el periodo 2014-2024. Los indicadores demograficos de ordenamiento territorial (primacia y ranking de asentamientos) comparan los censos 2017 y 2024 del INE.

## Contenido del repositorio

- `app.py`: archivo principal de la aplicacion en Streamlit.
- `motor_sii_exportador.py`: calculo de indicadores SII (Qij, Qr, CRr, base exportadora, Silva Lira, MADE, convergencia), ordenamiento territorial (primacia, Rondinelli, aislamiento) y exportacion a Excel en formato simple con formato condicional en Qij > 1 y Xij > 0. Lee directamente la pestana `Comuna` de `1_1_poblacion.xls` filtrando `Total Comuna`.
- `motor_fluidez_territorial_60fps.py`: simuladores y material de estudio de las unidades del ramo.
- `motor_laboratorio_catedra.py`: ejercicios de PIB regional, TAREA, convergencia, Gini, Theil y Markov.
- `motor_redes_territorio_ot.py`: datos de controles 2, 4 y 5 (mapas, cadenas de valor, sistema ELITE y ordenamiento territorial).
- `motor_redes_dinamicas_dini.py`: matrices y grafos de redes empresariales (Dini, 2010).
- `ILPES GRUPO 10 29-10-2026.xlsx`: base de datos SII (2014-2024).
- `1_1_poblacion.xls`: poblacion comunal Censo 2017 (INE).
- `poblacion 2024.pdf`: resultados Censo 2024 Region del Biobio (INE).
- `cuestionario_entrevista.pdf`: pauta de entrevista para terreno.
- `requirements.txt`: librerias necesarias para ejecutar la app (incluye `xlrd` para leer `.xls`).

## Ejecucion local

```bash
pip install -r requirements.txt
streamlit run app.py
```
