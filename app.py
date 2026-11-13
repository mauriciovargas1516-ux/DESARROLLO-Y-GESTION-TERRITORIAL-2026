import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Desarrollo y Gestión Territorial 2026 - ULagos",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# DATOS NATIVOS PRECARGADOS (BIOBÍO 2014-2024 + CÁTEDRA ULAGOS)
# ==============================================================================
COMUNAS_BIOBIO = [
    "Alto Biobío", "Antuco", "Arauco", "Cabrero", "Cañete", "Chiguayante",
    "Concepción", "Contulmo", "Coronel", "Curanilahue", "Florida", "Hualpén",
    "Hualqui", "Laja", "Lebu", "Los Álamos", "Los Ángeles", "Lota", "Mulchén",
    "Nacimiento", "Negrete", "Penco", "Quilaco", "Quilleco",
    "San Pedro de la Paz", "San Rosendo", "Santa Bárbara", "Santa Juana",
    "Talcahuano", "Tirúa", "Tomé", "Tucapel", "Yumbel"
]

SECTORES_SII = [
    "A - Agricultura, ganadería, silvicultura y pesca",
    "B - Explotación de minas y canteras",
    "C - Industria manufacturera",
    "D - Suministro de electricidad, gas, vapor y aire acondicionado",
    "E - Suministro de agua; evacuación de aguas residuales, gestión de desechos y descontaminación",
    "F - Construcción",
    "G - Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas",
    "H - Transporte y almacenamiento",
    "I - Actividades de alojamiento y de servicio de comidas",
    "J - Información y comunicaciones",
    "K - Actividades financieras y de seguros",
    "L - Actividades inmobiliarias",
    "M - Actividades profesionales, científicas y técnicas",
    "N - Actividades de servicios administrativos y de apoyo",
    "P - Enseñanza",
    "Q - Actividades de atención de la salud humana y de asistencia social",
    "R - Actividades artísticas, de entretenimiento y recreativas",
    "S - Otras actividades de servicios",
]

POB_BIOBIO_2024 = [
    6016, 4373, 37163, 31256, 34640, 85822, 230375, 5905, 123648, 31119,
    12958, 87731, 25795, 23706, 25246, 21950, 219441, 39980, 29036, 26140,
    10723, 48971, 4440, 9700, 150992, 3575, 14075, 14947, 147322, 10208,
    56907, 15729, 23170
]

V2014_PC = [
    6.304916, 54.55178, 5197.97975, 186.113676, 120.676258, 109.830903,
    772.334019, 63.116018, 436.488085, 119.223359, 151.27644, 139.613426,
    222.629362, 90.189561, 65.940309, 86.879193, 387.833042, 159.708211,
    104.999434, 110.442669, 80.502587, 157.243242, 37.344772, 53.069558,
    836.764784, 10.029459, 85.352122, 43.759293, 525.167243, 51.2336,
    124.18896, 106.467259, 58.11466
]

V2024_PC = [
    26.381046, 79.070172, 3053.58138, 250.857866, 147.790774, 212.211666,
    1053.1213, 165.403329, 545.962497, 149.011386, 174.318417, 229.23751,
    261.886502, 141.759479, 147.570688, 80.595738, 776.469253, 215.25987,
    167.121471, 230.192941, 303.748609, 288.491574, 78.400854, 100.75093,
    322.338096, 91.493346, 142.421854, 150.724739, 874.776102, 101.66577,
    231.470801, 282.174351, 109.821053
]

MAT_2014 = [
    [16166.85, 99691.01, 1950305.85, 961285.46, 1422286.9, 651277.85, 17746770.88, 87150.64, 10145986.65, 1185174.69, 411713.92, 527339.58, 321435.67, 122604.14, 787121.64, 580411.59, 31414312.91, 1712930.65, 1556451.89, 804568.42, 364507.11, 503346.56, 110136.22, 336666.43, 82105835.51, 0.0, 445369.66, 111592.32, 3954028.39, 226336.6, 2862299.94, 1076161.3, 450238.76],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1018736.82, 0.0, 94015.0, 431777.78, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 902434.78, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 536140.51, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 9359.83, 191610149.38, 2493994.26, 375962.32, 1389424.02, 15044583.28, 64384.21, 22588675.36, 521391.41, 67978.87, 3284860.72, 98960.9, 421065.26, 119099.7, 151972.27, 10911733.11, 2787812.41, 140304.22, 225369.14, 189087.94, 1676345.11, 0.0, 14494.66, 4090555.31, 0.0, 117220.6, 208945.13, 49223652.13, 60382.48, 903926.2, 88579.13, 164988.2],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1192105.69, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 43121.69, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 9009.99, 0.0, 11236407.92, 0.0, 24798.78, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 564584.44, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 335239.03, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 811238.78, 397932.69, 383264.97, 1074313.06, 14201236.28, 0.0, 4847362.88, 340849.59, 22774.34, 2209671.43, 31036.23, 704685.72, 130418.6, 215436.24, 4462830.37, 910498.92, 143210.37, 622337.81, 28034.17, 458314.15, 10899.16, 69052.65, 6290278.64, 11410.11, 148838.84, 49804.8, 4694726.7, 72439.95, 383831.34, 68587.56, 98968.26],
    [18874.53, 114658.91, 1457333.45, 1200586.98, 1371893.69, 1917693.89, 55158929.63, 202523.36, 9727195.08, 905880.83, 172176.85, 5261286.37, 515677.68, 601993.35, 601925.74, 713226.62, 19714472.97, 1617722.15, 1081632.2, 966897.43, 91678.18, 1795111.4, 29449.08, 73162.65, 8687537.74, 22487.23, 403126.5, 198331.28, 5922123.53, 174782.53, 1161866.04, 225494.42, 470218.05],
    [1242.8, 0.0, 298544.17, 377593.63, 430815.58, 280130.93, 5100065.82, 32113.49, 1147322.9, 430651.87, 79293.31, 442224.74, 144644.31, 143435.99, 17285.16, 148631.33, 4050278.28, 234322.62, 136485.0, 231084.0, 106151.34, 1760731.13, 0.0, 37886.49, 1418604.66, 0.0, 78098.07, 38856.72, 10781248.35, 6973.14, 1163601.32, 86796.64, 35525.52],
    [5731.78, 6826.07, 111676.47, 72351.8, 70852.99, 173166.53, 2378893.86, 7230.44, 153261.48, 68956.53, 5595.43, 120082.4, 18782.48, 46680.23, 25484.04, 28040.58, 1088303.51, 63204.12, 55711.15, 55287.66, 30316.78, 133076.82, 4309.62, 2988.36, 308061.27, 3191.6, 17859.42, 16996.89, 867809.66, 10051.43, 110943.08, 15936.24, 33163.29],
    [0.0, 0.0, 0.0, 0.0, 8779.42, 15149.31, 1870345.92, 0.0, 9655.05, 11019.71, 0.0, 28608.83, 0.0, 0.0, 0.0, 0.0, 214395.74, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 95261.04, 0.0, 0.0, 0.0, 32060.77, 0.0, 4147.26, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 349042.58, 20120726.87, 0.0, 1521471.58, 0.0, 0.0, 283558.3, 4386413.36, 0.0, 0.0, 0.0, 740311.9, 0.0, 0.0, 0.0, 0.0, 296014.57, 0.0, 0.0, 1017739.3, 0.0, 0.0, 0.0, 1025719.79, 0.0, 220602.2, 0.0, 0.0],
    [0.0, 0.0, 9690.87, 6237.12, 15205.79, 2739259.01, 8337188.07, 0.0, 192238.85, 0.0, 1007527.38, 145622.03, 0.0, 0.0, 0.0, 0.0, 1336465.89, 16317.56, 0.0, 0.0, 0.0, 251559.44, 0.0, 0.0, 1088137.34, 0.0, 0.0, 0.0, 1249810.71, 0.0, 166044.84, 0.0, 0.0],
    [0.0, 0.0, 43805.97, 0.0, 25673.86, 150534.35, 3259499.7, 0.0, 371997.57, 6470.62, 0.0, 49640.79, 0.0, 0.0, 0.0, 0.0, 445621.43, 11856.55, 0.0, 19148.36, 0.0, 28902.01, 0.0, 0.0, 488466.12, 0.0, 0.0, 0.0, 451426.83, 0.0, 23869.9, 0.0, 0.0],
    [0.0, 0.0, 280858.21, 8467.23, 30717.16, 285395.09, 8450501.64, 0.0, 442367.55, 9646.93, 0.0, 138194.07, 0.0, 87062.04, 0.0, 5237.71, 1523210.91, 19706.34, 5605.91, 51494.78, 0.0, 643249.79, 0.0, 0.0, 748592.98, 0.0, 0.0, 2834.39, 1303664.02, 0.0, 91036.04, 0.0, 12986.26],
    [0.0, 0.0, 201563.75, 0.0, 119682.12, 539380.63, 9770045.95, 0.0, 429457.6, 0.0, 0.0, 389458.68, 0.0, 0.0, 0.0, 0.0, 1342288.05, 0.0, 54064.65, 0.0, 0.0, 135272.33, 0.0, 0.0, 1027726.49, 0.0, 0.0, 0.0, 402830.83, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 9836.17, 0.0, 14093.57, 150863.59, 4218344.34, 0.0, 69775.47, 0.0, 0.0, 340838.87, 0.0, 0.0, 0.0, 0.0, 1078690.62, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 221384.19, 0.0, 0.0, 0.0, 1119896.19, 0.0, 21125.66, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 0.0, 1844.56, 86306.79, 0.0, 1915.33, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 201084.52, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 34501.03, 0.0, 0.0, 0.0, 1186767.77, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 5312.2, 4288.06, 48608.88, 46821.35, 808704.6, 0.0, 99509.03, 86216.17, 0.0, 23599.32, 918.11, 946.91, 83029.97, 32939.19, 163211.07, 14529.08, 44452.26, 69379.44, 0.0, 6013.26, 0.0, 0.0, 66661.56, 0.0, 11302.54, 2991.08, 488381.82, 0.0, 13289.67, 0.0, 1392.39]
]

MAT_2024 = [
    [0.0, 24563.46, 1197334.76, 496383.02, 921105.53, 364713.43, 9810669.86, 175695.0, 12040133.11, 277677.15, 1220890.4, 117329.49, 385276.35, 56866.22, 1018570.39, 242588.68, 34116621.56, 3325203.58, 1756511.97, 1229021.83, 793650.36, 708202.21, 164229.35, 563686.23, 485204.63, 0.0, 503740.55, 77570.98, 5654723.5, 252998.35, 812536.4, 490234.54, 123469.46],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 579134.5, 0.0, 0.0, 143766.62, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 564193.98, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 42122.04, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 24100.85, 106067947.92, 2423659.37, 362651.01, 1768639.37, 12188265.12, 194019.9, 32914931.36, 275239.02, 91109.25, 4994235.02, 237028.51, 557006.91, 102178.41, 93694.82, 82352548.88, 3209720.52, 156267.77, 787428.72, 184399.84, 4383411.25, 3366.83, 23465.79, 6449785.82, 20540.62, 67378.28, 849350.46, 75842247.18, 29531.48, 7955494.94, 973363.97, 470414.87],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2302747.36, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 952860.4, 0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 91003.08, 13304.73, 34323.26, 0.0, 9664589.76, 0.0, 223898.6, 0.0, 0.0, 269618.65, 0.0, 53095.93, 0.0, 0.0, 416303.09, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 606573.93, 0.0, 6785.76, 0.0, 1419970.13, 0.0, 0.0, 0.0, 10560.49],
    [24055.98, 16819.25, 838913.17, 606572.09, 744208.74, 1327602.34, 18122552.91, 26099.87, 1665696.01, 426884.08, 138708.2, 1511586.63, 164878.06, 427839.68, 161942.57, 90471.09, 6480227.74, 152765.21, 198388.03, 400671.72, 624461.38, 534379.08, 32014.7, 28520.49, 6695997.31, 0.0, 66684.09, 161516.63, 4267227.18, 25826.2, 303089.37, 99085.87, 85414.79],
    [105299.83, 191275.02, 2181883.73, 1923978.64, 2019109.84, 3352217.83, 88519637.26, 441535.79, 12102280.21, 2532569.88, 413961.51, 3784476.97, 916890.04, 1085788.38, 1839673.83, 883148.71, 21623765.16, 1223318.53, 1691948.95, 1694938.86, 613662.58, 3826497.74, 83775.42, 241530.62, 22069590.04, 299806.62, 833397.68, 755965.98, 10483805.95, 573202.29, 2067834.84, 1131741.68, 1409077.63],
    [10260.82, 59043.34, 2206566.99, 1359454.98, 538486.84, 638552.24, 10217639.8, 109755.4, 4405465.02, 545107.17, 204264.96, 1552697.23, 138672.08, 251241.29, 95903.62, 197571.63, 9727039.79, 229461.83, 482959.24, 1160039.64, 353288.75, 3281048.5, 28413.27, 87175.95, 2164022.85, 1961.42, 269972.64, 185520.43, 16970994.41, 132463.86, 444095.56, 249545.88, 104596.89],
    [19091.74, 24762.7, 310234.99, 214658.3, 127731.11, 252191.84, 5456262.28, 21666.06, 570839.16, 114902.18, 38087.52, 590794.44, 45870.91, 91649.27, 84625.8, 73420.76, 2057739.77, 118782.24, 104584.92, 187294.21, 69611.14, 219944.73, 16559.75, 25540.27, 1155122.62, 4780.05, 115961.29, 45577.78, 1503688.2, 18873.98, 460914.46, 35303.73, 136200.13],
    [0.0, 0.0, 0.0, 5106.98, 20784.04, 54247.24, 2493211.2, 0.0, 48690.85, 14543.34, 0.0, 80936.11, 0.0, 0.0, 4843.55, 0.0, 583553.86, 9925.52, 0.0, 18283.98, 0.0, 2144.62, 0.0, 0.0, 311136.45, 0.0, 0.0, 0.0, 124998.71, 0.0, 38799.24, 0.0, 3731.64],
    [0.0, 0.0, 0.0, 0.0, 0.0, 6994922.92, 9103703.69, 0.0, 31160.85, 0.0, 0.0, 1005189.93, 2786710.44, 0.0, 0.0, 0.0, 592377.3, 0.0, 0.0, 0.0, 0.0, 48206.4, 0.0, 0.0, 272814.38, 0.0, 0.0, 0.0, 1165838.93, 0.0, 174308.54, 1241332.2, 0.0],
    [0.0, 0.0, 24291.3, 34371.42, 37196.47, 1467299.64, 11199921.06, 0.0, 312182.83, 12122.97, 87321.44, 374173.73, 1847498.32, 56905.97, 27132.91, 0.0, 2165602.29, 15930.49, 36484.59, 16753.64, 445640.49, 292793.06, 0.0, 0.0, 1797284.61, 0.0, 7850.59, 50770.33, 1540796.12, 0.0, 373594.08, 155173.37, 34355.14],
    [0.0, 0.0, 46280.67, 139998.4, 48040.99, 283596.0, 9307279.73, 0.0, 889788.83, 31885.77, 26010.77, 2267128.3, 49108.38, 616257.78, 21572.92, 10983.62, 1285315.09, 160889.22, 70897.93, 57204.0, 80705.59, 85963.18, 0.0, 0.0, 2379488.67, 0.0, 50282.49, 15005.33, 1108158.87, 0.0, 182312.3, 14710.72, 20852.38],
    [0.0, 3834.99, 228129.43, 461820.33, 126783.4, 497109.4, 11452580.77, 5917.17, 1462374.83, 161893.19, 36583.77, 854283.41, 112757.91, 84362.43, 24091.41, 25355.54, 3329106.84, 62112.1, 203156.35, 276839.52, 74554.87, 549179.75, 19740.47, 0.0, 1844780.52, 0.0, 70181.78, 44810.89, 2936130.26, 0.0, 150540.0, 42209.3, 114383.57],
    [0.0, 0.0, 179849.08, 36703.75, 5721.13, 569621.74, 27090120.15, 0.0, 460772.2, 7789.25, 0.0, 425717.18, 0.0, 0.0, 0.0, 0.0, 1747204.22, 26421.05, 48037.31, 97447.04, 0.0, 83247.74, 0.0, 0.0, 1227728.55, 0.0, 0.0, 60805.47, 654996.44, 0.0, 28674.37, 0.0, 0.0],
    [0.0, 0.0, 74189.33, 92873.08, 63079.76, 418410.03, 10815352.47, 0.0, 154802.18, 33331.67, 0.0, 2102638.28, 30675.75, 59401.99, 31112.65, 3005.77, 2349502.08, 42398.27, 15522.19, 29871.59, 0.0, 33177.08, 0.0, 0.0, 730868.31, 0.0, 0.0, 0.0, 2264918.33, 0.0, 65562.8, 0.0, 20243.83],
    [0.0, 0.0, 12327.02, 7312.02, 11871.97, 46595.57, 1116297.59, 0.0, 50909.96, 0.0, 0.0, 82557.34, 30230.33, 5284.73, 2754.35, 4401.84, 452125.41, 4464.1, 8191.21, 18919.48, 0.0, 43586.34, 0.0, 0.0, 166172.18, 0.0, 0.0, 0.0, 1674676.02, 0.0, 55096.95, 0.0, 0.0],
    [0.0, 1374.25, 21293.49, 24616.36, 58378.33, 176710.03, 3172853.79, 2017.47, 173244.77, 59373.02, 1880.23, 97873.25, 9765.25, 14849.63, 311167.18, 144433.99, 545962.37, 24696.94, 79588.57, 42529.24, 17121.33, 35939.19, 0.0, 7364.67, 271780.94, 0.0, 12352.44, 5988.39, 307734.23, 4908.02, 59455.03, 5619.1, 11252.98]
]

# Caso Clásico Cátedra: 00 Datos Base.xlsx
TERRITORIOS_CATEDRA = ["Badalona", "Pueblo Seco", "Pueblo Nuevo"]
SECTORES_CATEDRA = ["Agricultura", "Minería", "Pesca", "Industria"]
MAT_CATEDRA_0 = [
    [60.0, 100.0, 212.0],
    [75.0, 210.0, 235.0],
    [120.0, 253.0, 452.0],
    [40.0, 77.0, 98.0],
]
MAT_CATEDRA_1 = [
    [68.0, 300.0, 57.0],
    [79.0, 200.0, 303.0],
    [142.0, 400.0, 432.0],
    [45.0, 300.0, 42.0],
]

# Liceos de Osorno (Liceos.xlsx)
LICEOS_OSORNO = [
    {"id": 1, "Liceo": "Liceo Carmela Carvajal de Prat", "Dirección": "Francisco Bilbao 1380, Osorno", "lat": -40.575314, "lon": -73.134019},
    {"id": 2, "Liceo": "Liceo San Sebastián", "Dirección": "Los Carrera 602-700, Osorno", "lat": -40.573369, "lon": -73.122975},
    {"id": 3, "Liceo": "Liceo Eleuterio Ramírez Osorno", "Dirección": "Ramón Freire 752, Osorno", "lat": -40.575337, "lon": -73.130475},
    {"id": 4, "Liceo": "Liceo Manuel Baquedano", "Dirección": "Manuel Baquedano 413, Osorno", "lat": -40.571003, "lon": -73.143513},
    {"id": 5, "Liceo": "Liceo Técnico Adolfo Matthei", "Dirección": "Av. René Soriano 2615, Osorno", "lat": -40.589083, "lon": -73.109866},
    {"id": 6, "Liceo": "Liceo Tecnológico Luz de las Naciones", "Dirección": "Francisco Bilbao 1841, Osorno", "lat": -40.576632, "lon": -73.118119},
    {"id": 7, "Liceo": "Liceo Rahue Osorno", "Dirección": "Del Pacífico 1360, Osorno", "lat": -40.577143, "lon": -73.163588},
    {"id": 8, "Liceo": "Liceo Comercial Bartolomé de Las Casas", "Dirección": "Av. República 547, Osorno", "lat": -40.573865, "lon": -73.153096},
    {"id": 9, "Liceo": "Liceo Técnico Monseñor Francisco Valdés", "Dirección": "Ramón Freire 1140, Osorno", "lat": -40.580237, "lon": -73.129584},
    {"id": 10, "Liceo": "Sociedad Educacional Crecer Limitada", "Dirección": "Patricio Lynch 1639, Osorno", "lat": -40.574137, "lon": -73.121479},
    {"id": 11, "Liceo": "Liceo Artístico Santa Cecilia", "Dirección": "Virgen del Socorro 10, Osorno", "lat": -40.568845, "lon": -73.118041},
    {"id": 12, "Liceo": "Liceo Industrial Osorno", "Dirección": "Guillermo Hollstein 125, Osorno", "lat": -40.580024, "lon": -73.101489},
    {"id": 13, "Liceo": "Instituto Comercial de Osorno", "Dirección": "Los Carrera 718, Osorno", "lat": -40.571339, "lon": -73.137692},
    {"id": 14, "Liceo": "Colegio Técnico Diego Portales Limitada", "Dirección": "Gómez Carreño 2425, Osorno", "lat": -40.584195, "lon": -73.110051},
    {"id": 15, "Liceo": "Colegio Luis Pasteur", "Dirección": "Ramón Freire 341, Osorno", "lat": -40.570432, "lon": -73.131061},
]

# Matriz Binaria de Redes (Datos.xlsx - 15 empresas A..O)
NODOS_RED = list("ABCDEFGHIJKLMNO")
MATRIZ_RED_DINI = [
    [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
    [0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
]


# ==============================================================================
# FUNCIONES MATEMÁTICAS DE ECONOMÍA REGIONAL Y REAT
# ==============================================================================
def calcular_indicadores_regionales(V0, Vt, nombres_reg, nombres_sec):
    """Calcula Qij, Qr, Xj, Mj, CRr, MADE clásico y MADE modificado."""
    V0 = np.array(V0, dtype=float)
    Vt = np.array(Vt, dtype=float)

    # Totales
    tot_reg_0 = V0.sum(axis=0)
    tot_sec_0 = V0.sum(axis=1)
    tot_nac_0 = V0.sum()

    tot_reg_t = Vt.sum(axis=0)
    tot_sec_t = Vt.sum(axis=1)
    tot_nac_t = Vt.sum()

    # Participación sectorial en cada región P_ij
    P0 = np.divide(V0, tot_reg_0, out=np.zeros_like(V0), where=tot_reg_0 != 0)
    Pt = np.divide(Vt, tot_reg_t, out=np.zeros_like(Vt), where=tot_reg_t != 0)

    # Participación nacional de cada sector
    P_nac_0 = tot_sec_0 / tot_nac_0
    P_nac_t = tot_sec_t / tot_nac_t

    # Cociente de Localización Qij
    Q0 = np.divide(P0, P_nac_0[:, None], out=np.zeros_like(P0), where=P_nac_0[:, None] != 0)
    Qt = np.divide(Pt, P_nac_t[:, None], out=np.zeros_like(Pt), where=P_nac_t[:, None] != 0)

    # Coeficiente de Especialización Qr (0 a 1)
    Qr_0 = 0.5 * np.sum(np.abs(P0 - P_nac_0[:, None]), axis=0)
    Qr_t = 0.5 * np.sum(np.abs(Pt - P_nac_t[:, None]), axis=0)

    # Producción Básica Exportable Xij (donde Qij > 1)
    X0_mat = np.where(Q0 > 1, V0 - (V0 / np.where(Q0 > 1, Q0, 1.0)), 0.0)
    Xt_mat = np.where(Qt > 1, Vt - (Vt / np.where(Qt > 1, Qt, 1.0)), 0.0)
    X0_tot = X0_mat.sum(axis=0)
    Xt_tot = Xt_mat.sum(axis=0)

    # Multiplicador Básico Regional Mj = PTj / Xj
    M0 = np.divide(tot_reg_0, X0_tot, out=np.zeros_like(tot_reg_0), where=X0_tot != 0)
    Mt = np.divide(tot_reg_t, Xt_tot, out=np.zeros_like(tot_reg_t), where=Xt_tot != 0)

    # Coeficiente de Reestructuración CRr
    CRr = 0.5 * np.sum(np.abs(Pt - P0), axis=0)

    # Shift & Share (MADE Clásico)
    r_nac = tot_nac_t / tot_nac_0
    r_sec = np.divide(tot_sec_t, tot_sec_0, out=np.ones_like(tot_sec_0), where=tot_sec_0 != 0)

    ET = tot_reg_t - tot_reg_0 * r_nac
    EE = np.sum(V0 * (r_sec[:, None] - r_nac), axis=0)
    ED = ET - EE

    # Shift & Share Modificado (Esteban-Marquillas / Arcelus / Lira & Quiroga)
    r_nac_inv = tot_nac_0 / tot_nac_t
    r_sec_inv = np.divide(tot_sec_0, tot_sec_t, out=np.ones_like(tot_sec_t), where=tot_sec_t != 0)
    EI = np.sum(Vt * (r_nac_inv - r_sec_inv[:, None]), axis=0)
    EM = EI - EE
    ERM = ET - EI

    df_resumen = pd.DataFrame({
        "Territorio": nombres_reg,
        "Ventas_0": tot_reg_0,
        "Ventas_t": tot_reg_t,
        "Var_Ratio (rRj)": np.divide(tot_reg_t, tot_reg_0, out=np.zeros_like(tot_reg_0), where=tot_reg_0 != 0),
        "Qr_0 (Especialización)": Qr_0,
        "Qr_t (Especialización)": Qr_t,
        "CRr (Reestructuración)": CRr,
        "Exportación_Básica_0 (Xj)": X0_tot,
        "Exportación_Básica_t (Xj)": Xt_tot,
        "Multiplicador_0 (Mj)": M0,
        "Multiplicador_t (Mj)": Mt,
        "Efecto_Total (ET)": ET,
        "Efecto_Estructural (EE)": EE,
        "Efecto_Diferencial (ED)": ED,
        "Efecto_Est_Inverso (EI)": EI,
        "Efecto_Est_Modificado (EM)": EM,
        "Efecto_Reg_Modificado (ERM)": ERM,
    })

    return {
        "resumen": df_resumen,
        "Q0": pd.DataFrame(Q0, index=nombres_sec, columns=nombres_reg),
        "Qt": pd.DataFrame(Qt, index=nombres_sec, columns=nombres_reg),
        "P0": pd.DataFrame(P0, index=nombres_sec, columns=nombres_reg),
        "Pt": pd.DataFrame(Pt, index=nombres_sec, columns=nombres_reg),
    }


def calcular_reat_convergencia(y0, yt, T=10):
    """Calcula Convergencia Sigma, Beta OLS, Lorenz, Gini, Theil y HHI."""
    y0 = np.array(y0, dtype=float)
    yt = np.array(yt, dtype=float)
    N = len(y0)

    ln_y0 = np.log(y0)
    ln_yt = np.log(yt)
    g_anual = (ln_yt - ln_y0) / T

    # Sigma y CV (con divisor N y N-1)
    sigma_ln_0 = np.std(ln_y0, ddof=1)
    sigma_ln_t = np.std(ln_yt, ddof=1)
    sigma_niv_0 = np.std(y0, ddof=0)
    sigma_niv_t = np.std(yt, ddof=0)
    cv_0 = sigma_niv_0 / np.mean(y0)
    cv_t = sigma_niv_t / np.mean(yt)

    # Regresión OLS Convergencia Beta: g_anual = alpha + beta * ln(y0)
    slope, intercept, r_value, p_value, std_err = stats.linregress(ln_y0, g_anual)
    t_stat = slope / std_err
    B_acum = slope * T
    velocidad_b = -np.log(1 + B_acum) / T if (1 + B_acum) > 0 else np.nan
    semivida_b = np.log(2) / velocidad_b if velocidad_b and velocidad_b > 0 else np.nan

    # Gini y Curva de Lorenz
    def lorenz_gini(x):
        x_sorted = np.sort(x)
        n = len(x_sorted)
        cum_p = np.arange(0, n + 1) / n
        cum_q = np.concatenate([[0.0], np.cumsum(x_sorted) / np.sum(x_sorted)])
        trapecios = (cum_p[1:] - cum_p[:-1]) * (cum_q[1:] + cum_q[:-1])
        gini = 1.0 - np.sum(trapecios)
        gini_norm = gini * (n / (n - 1))
        return cum_p, cum_q, gini, gini_norm

    p0, q0, gini_0, gini_n0 = lorenz_gini(y0)
    pt, qt, gini_t, gini_nt = lorenz_gini(yt)

    # Índice de Theil
    s0 = y0 / np.sum(y0)
    st_share = yt / np.sum(yt)
    theil_0 = np.sum(s0 * np.log(N * s0))
    theil_t = np.sum(st_share * np.log(N * st_share))

    # HHI (sobre vectores per cápita o totales)
    hhi_0 = np.sum(s0 ** 2)
    hhi_t = np.sum(st_share ** 2)

    return {
        "sigma_ln_0": sigma_ln_0,
        "sigma_ln_t": sigma_ln_t,
        "sigma_niv_0": sigma_niv_0,
        "sigma_niv_t": sigma_niv_t,
        "cv_0": cv_0,
        "cv_t": cv_t,
        "beta_anual": slope,
        "intercepto": intercept,
        "r2": r_value ** 2,
        "std_err": std_err,
        "t_stat": t_stat,
        "p_value": p_value,
        "B_acum": B_acum,
        "velocidad_b": velocidad_b,
        "semivida_b": semivida_b,
        "gini_0": gini_0,
        "gini_t": gini_t,
        "gini_n0": gini_n0,
        "gini_nt": gini_nt,
        "theil_0": theil_0,
        "theil_t": theil_t,
        "hhi_0": hhi_0,
        "hhi_t": hhi_t,
        "lorenz_0": (p0, q0),
        "lorenz_t": (pt, qt),
        "ln_y0": ln_y0,
        "ln_yt": ln_yt,
        "g_anual": g_anual,
    }


# ==============================================================================
# BARRA LATERAL Y NAVEGACIÓN
# ==============================================================================
st.sidebar.title("🌍 Gestión Territorial 2026")
st.sidebar.markdown("**Universidad de Los Lagos**  \nIngeniería Comercial | Prof. Claudio Mancilla")
st.sidebar.divider()

archivo_subido = st.sidebar.file_uploader(
    "📂 Cargar Excel ILPES (Opcional)",
    type=["xlsx"],
    help="El sistema ya incluye precargada toda la base de las 33 comunas de Biobío (2014-2024) y datos de cátedra.",
)

ruta_local = "ILPES GRUPO 10 TERRITORIAL AL 19-10-2026.xlsx"
if archivo_subido is not None:
    st.sidebar.success("✅ Excel cargado dinámicamente.")
elif os.path.exists(ruta_local):
    st.sidebar.info("📘 Leyendo archivo Excel local del repositorio.")
else:
    st.sidebar.info("⚡ Operando con motor de datos nativo integrado (33 comunas Biobío + Cátedra).")

modulo = st.sidebar.radio(
    "Selecciona el Módulo de Análisis:",
    [
        "1. Técnicas de Análisis Regional (ILPES / MADE)",
        "2. Disparidades, Concentración y Convergencia (REAT)",
        "3. SPL, Redes Empresariales (Dini) y Cadenas de Valor",
        "4. Ordenamiento Territorial y Georreferenciación",
        "5. Conmutación Laboral Patagonia (Mancilla et al.)",
    ],
)

st.title("🌍 Plataforma Interactiva: Desarrollo y Gestión Territorial 2026")
st.caption("Repositorio Académico e Inteligencia Territorial en Python + Streamlit | Ingeniería Comercial - ULagos")

# ==============================================================================
# MÓDULO 1: TÉCNICAS DE ANÁLISIS REGIONAL (ILPES / CUADRANTES DE SILVA / MADE)
# ==============================================================================
if modulo.startswith("1."):
    st.header("1. Técnicas de Análisis Regional: Localización, Base Exportadora y Shift & Share")

    fuente_datos = st.radio(
        "Seleccionar Base de Datos:",
        [
            "Región del Biobío - 33 Comunas y 18 Rubros SII (2014 vs 2024)",
            "Caso Clásico de Cátedra - 00 Datos Base.xlsx (Badalona, Pueblo Seco, Pueblo Nuevo)",
        ],
        horizontal=True,
    )

    if fuente_datos.startswith("Región del Biobío"):
        res = calcular_indicadores_regionales(MAT_2014, MAT_2024, COMUNAS_BIOBIO, SECTORES_SII)
        etiqueta_0, etiqueta_t = "2014", "2024"
    else:
        res = calcular_indicadores_regionales(MAT_CATEDRA_0, MAT_CATEDRA_1, TERRITORIOS_CATEDRA, SECTORES_CATEDRA)
        etiqueta_0, etiqueta_t = "Año 0", "Período 1"

    df_res = res["resumen"]

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Cuadrantes de Silva (2005)",
        "📍 Localización (Qij) y Especialización (Qr)",
        "🚢 Base Exportadora (Xj) y Multiplicador (Mj)",
        "⚙️ Shift & Share (MADE y MADE Modificado)",
    ])

    with tab1:
        st.subheader("Tipología de Territorios Subnacionales - Cuadrantes de Silva Lira (CEPAL, 2005)")
        if fuente_datos.startswith("Región del Biobío"):
            df_silva = pd.DataFrame({
                "Comuna": COMUNAS_BIOBIO,
                "Ventas_UF_2014": df_res["Ventas_0"],
                "Ventas_UF_2024": df_res["Ventas_t"],
                "Población_2024": POB_BIOBIO_2024,
                "Tasa_Crec_Anual (%)": ((df_res["Ventas_t"] / df_res["Ventas_0"]) ** (1 / 10) - 1) * 100,
                "Ventas_Per_Capita_2024_UF": V2024_PC,
            })
            prom_crec = ((df_res["Ventas_t"].sum() / df_res["Ventas_0"].sum()) ** (1 / 10) - 1) * 100
            prom_pc = df_res["Ventas_t"].sum() / sum(POB_BIOBIO_2024)

            def clasificar_silva(row):
                alto_crec = row["Tasa_Crec_Anual (%)"] >= prom_crec
                alto_pc = row["Ventas_Per_Capita_2024_UF"] >= prom_pc
                if alto_crec and alto_pc:
                    return "C1 (+ +): Ganadores"
                elif alto_crec and not alto_pc:
                    return "C2 (- +): En Marcha (Convergentes)"
                elif not alto_crec and not alto_pc:
                    return "C3 (- -): Estancados"
                else:
                    return "C4 (+ -): En Retroceso"

            df_silva["Cuadrante"] = df_silva.apply(clasificar_silva, axis=1)

            c1, c2, c3 = st.columns(3)
            c1.metric("Crecimiento Promedio Regional Anual", f"{prom_crec:.2f}%")
            c2.metric("Ventas per Cápita Promedio Regional (2024)", f"{prom_pc:.2f} UF/hab")
            c3.metric("Comunas en Marcha / Ganadoras", f"{(df_silva['Tasa_Crec_Anual (%)'] >= prom_crec).sum()} de 33")

            fig_silva = px.scatter(
                df_silva,
                x="Ventas_Per_Capita_2024_UF",
                y="Tasa_Crec_Anual (%)",
                color="Cuadrante",
                hover_name="Comuna",
                size="Población_2024",
                log_x=True,
                title="Cuadrantes de Silva - 33 Comunas Región del Biobío (2014-2024)",
            )
            fig_silva.add_hline(y=prom_crec, line_dash="dash", line_color="red", annotation_text="Crec. Regional")
            fig_silva.add_vline(x=prom_pc, line_dash="dash", line_color="blue", annotation_text="PIB/Ventas PC Media")
            st.plotly_chart(fig_silva, use_container_width=True)
            st.dataframe(df_silva.round(3), use_container_width=True)
        else:
            st.info("Selecciona la base de la Región del Biobío arriba para visualizar los Cuadrantes de Silva con población comunal.")

    with tab2:
        st.subheader(f"Cociente de Localización (Qij) - {etiqueta_t}")
        st.markdown("Valores $Q_{ij} > 1$ indican especialización relativa favorable (sector básico exportador).")
        fig_q = px.imshow(
            res["Qt"].round(2),
            aspect="auto",
            color_continuous_scale="RdBu_r",
            color_continuous_midpoint=1.0,
            title=f"Mapa de Calor: Cociente de Localización (Qij) en {etiqueta_t}",
        )
        st.plotly_chart(fig_q, use_container_width=True)

        col_a, col_b = st.columns(2)
        with col_a:
            fig_qr = px.bar(
                df_res.sort_values("Qr_t (Especialización)", ascending=False),
                x="Territorio",
                y=["Qr_0 (Especialización)", "Qr_t (Especialización)"],
                barmode="group",
                title="Coeficiente de Especialización (Qr): Comparación Temporal",
            )
            st.plotly_chart(fig_qr, use_container_width=True)
        with col_b:
            fig_crr = px.bar(
                df_res.sort_values("CRr (Reestructuración)", ascending=False),
                x="Territorio",
                y="CRr (Reestructuración)",
                color="CRr (Reestructuración)",
                title="Coeficiente de Reestructuración (CRr) entre Períodos",
            )
            st.plotly_chart(fig_crr, use_container_width=True)

    with tab3:
        st.subheader("Base Económica Exportadora ($X_j$) y Multiplicador Básico Regional ($M_j$)")
        st.dataframe(
            df_res[[
                "Territorio", "Ventas_0", "Exportación_Básica_0 (Xj)", "Multiplicador_0 (Mj)",
                "Ventas_t", "Exportación_Básica_t (Xj)", "Multiplicador_t (Mj)"
            ]].round(3),
            use_container_width=True,
        )

    with tab4:
        st.subheader("Método de Análisis Diferencial-Estructural (MADE Clásico y Modificado)")
        st.markdown(
            "**MADE Clásico:** $ET_j = EE_j + ED_j$ | **MADE Modificado:** $ET_j = EE_j + EM_j + ERM_j$"
        )
        fig_made = px.bar(
            df_res,
            x="Territorio",
            y=["Efecto_Estructural (EE)", "Efecto_Diferencial (ED)"],
            barmode="relative",
            title="Descomposición Shift & Share (Efecto Estructural vs. Efecto Diferencial)",
        )
        st.plotly_chart(fig_made, use_container_width=True)
        st.dataframe(
            df_res[[
                "Territorio", "Efecto_Total (ET)", "Efecto_Estructural (EE)",
                "Efecto_Diferencial (ED)", "Efecto_Est_Inverso (EI)",
                "Efecto_Est_Modificado (EM)", "Efecto_Reg_Modificado (ERM)"
            ]].round(2),
            use_container_width=True,
        )

# ==============================================================================
# MÓDULO 2: DISPARIDADES, CONCENTRACIÓN Y CONVERGENCIA (MOTOR REAT)
# ==============================================================================
elif modulo.startswith("2."):
    st.header("2. Disparidades, Concentración y Convergencia Regional (Motor REAT)")

    base_conv = st.selectbox(
        "Seleccionar Serie de Convergencia:",
        [
            "Región del Biobío - 33 Comunas (Ventas UF per cápita 2014 vs 2024)",
            "Ejemplo de Cátedra REAT - Ejemplo 1 TE.xlsx (7 territorios: 2010 vs 2020)",
        ],
    )

    if base_conv.startswith("Región del Biobío"):
        nombres_c = COMUNAS_BIOBIO
        y0_c, yt_c, T_c = V2014_PC, V2024_PC, 10
        lbl_0, lbl_t = "2014", "2024"
    else:
        nombres_c = ["A", "B", "C", "D", "E", "F", "G"]
        y0_c = [49, 11, 50, 19, 61, 146, 32]
        yt_c = [94, 23, 121, 67, 107, 311, 116]
        T_c = 10
        lbl_0, lbl_t = "2010", "2020"

    reat = calcular_reat_convergencia(y0_c, yt_c, T=T_c)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(f"Sigma Log ({lbl_0} → {lbl_t})", f"{reat['sigma_ln_t']:.4f}", f"{reat['sigma_ln_t'] - reat['sigma_ln_0']:.4f}", delta_color="inverse")
    k2.metric("Pendiente Beta Anual (β)", f"{reat['beta_anual']:.5f}", f"p = {reat['p_value']:.4e}")
    k3.metric("Bondad de Ajuste (R²)", f"{reat['r2'] * 100:.2f}%", f"t = {reat['t_stat']:.2f}")
    k4.metric("Índice de Gini", f"{reat['gini_t']:.4f}", f"{reat['gini_t'] - reat['gini_0']:.4f}", delta_color="inverse")

    col_beta, col_lorenz = st.columns(2)

    with col_beta:
        df_beta = pd.DataFrame({
            "Territorio": nombres_c,
            f"ln({lbl_0})": reat["ln_y0"],
            "Crecimiento_Log_Anual": reat["g_anual"],
            "Ajuste_OLS": reat["intercepto"] + reat["beta_anual"] * reat["ln_y0"],
        })
        fig_beta = px.scatter(
            df_beta,
            x=f"ln({lbl_0})",
            y="Crecimiento_Log_Anual",
            hover_name="Territorio",
            text="Territorio",
            title=f"Convergencia Beta Absoluta ({lbl_0}-{lbl_t}): β = {reat['beta_anual']:.4f}",
        )
        fig_beta.add_traces(
            go.Scatter(
                x=df_beta[f"ln({lbl_0})"],
                y=df_beta["Ajuste_OLS"],
                mode="lines",
                name="Tendencia OLS",
                line=dict(color="red", dash="dash"),
            )
        )
        st.plotly_chart(fig_beta, use_container_width=True)

    with col_lorenz:
        p0, q0 = reat["lorenz_0"]
        pt, qt = reat["lorenz_t"]
        fig_lor = go.Figure()
        fig_lor.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode="lines", name="Equidistribución (45°)", line=dict(dash="dot", color="gray")))
        fig_lor.add_trace(go.Scatter(x=p0, y=q0, mode="lines+markers", name=f"Lorenz {lbl_0} (Gini={reat['gini_0']:.3f})"))
        fig_lor.add_trace(go.Scatter(x=pt, y=qt, mode="lines+markers", name=f"Lorenz {lbl_t} (Gini={reat['gini_t']:.3f})"))
        fig_lor.update_layout(title="Curva de Lorenz e Índice de Gini", xaxis_title="Proporción acumulada de territorios", yaxis_title="Proporción acumulada de ingreso/ventas")
        st.plotly_chart(fig_lor, use_container_width=True)

    st.subheader("Tabla Oficial de Indicadores REAT y Concentración (Hannah-Kay / Herfindahl / Theil)")
    alfa_hk = st.slider("Parámetro de sensibilidad α para Índice Hannah-Kay (HK):", min_value=1.5, max_value=5.0, value=2.0, step=0.5)
    s0_tot = np.array(y0_c) / np.sum(y0_c)
    st_tot = np.array(yt_c) / np.sum(yt_c)
    hk_0 = (np.sum(s0_tot ** alfa_hk)) ** (1.0 / (alfa_hk - 1.0))
    hk_t = (np.sum(st_tot ** alfa_hk)) ** (1.0 / (alfa_hk - 1.0))

    df_tabla_reat = pd.DataFrame([
        {"Indicador": "Sigma de logaritmos (σ_ln)", lbl_0: reat["sigma_ln_0"], lbl_t: reat["sigma_ln_t"]},
        {"Indicador": "Desviación Estándar en niveles", lbl_0: reat["sigma_niv_0"], lbl_t: reat["sigma_niv_t"]},
        {"Indicador": "Coeficiente de Variación (CV)", lbl_0: reat["cv_0"], lbl_t: reat["cv_t"]},
        {"Indicador": "Índice de Gini Estándar", lbl_0: reat["gini_0"], lbl_t: reat["gini_t"]},
        {"Indicador": "Índice de Gini Normalizado", lbl_0: reat["gini_n0"], lbl_t: reat["gini_nt"]},
        {"Indicador": "Índice de Entropía de Theil", lbl_0: reat["theil_0"], lbl_t: reat["theil_t"]},
        {"Indicador": "Índice Herfindahl-Hirschman (HHI per cápita)", lbl_0: reat["hhi_0"], lbl_t: reat["hhi_t"]},
        {"Indicador": f"Índice Hannah-Kay (α = {alfa_hk})", lbl_0: hk_0, lbl_t: hk_t},
        {"Indicador": "Velocidad de Convergencia λ (usando B acum.)", lbl_0: reat["velocidad_b"], lbl_t: np.nan},
        {"Indicador": "Semivida / Half-life en años (usando B acum.)", lbl_0: reat["semivida_b"], lbl_t: np.nan},
    ])
    st.dataframe(df_tabla_reat.round(4), use_container_width=True)

# ==============================================================================
# MÓDULO 3: SPL, REDES EMPRESARIALES (DINI / UCINET) Y CADENAS DE VALOR (CEPAL)
# ==============================================================================
elif modulo.startswith("3."):
    st.header("3. Sistemas Productivos Locales, Redes (Dini 2010) y Cadenas de Valor (CEPAL)")

    sub1, sub2, sub3 = st.tabs([
        "🌲 Caso Aplicado: Cadena Maderera Los Ángeles (PYMEMAD / CORMA)",
        "🕸️ Simulador de Redes Empresariales (UCINET / Dini)",
        "⛓️ Metodología CEPAL y Ecosistema MIPE Los Lagos",
    ])

    with sub1:
        st.subheader("Cadena de Valor Forestal-Maderera en Los Ángeles (Región del Biobío)")
        st.markdown(
            "**Esquema Preliminar de 4 Eslabones para Validación Empírica (Control 4):**  \n"
            "`1. Plantación Silvícola` ➡️ `2. Servicios de Cosecha y Faena` ➡️ "
            "`3. Aserraderos e Industria Secundaria` ➡️ `4. Comercialización y Distribución`"
        )

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            st.info(
                "**Bloque 1: Validar Cadena (5 min)**\n"
                "1. **Eslabones:** ¿Las 4 etapas reflejan bien al sector o falta alguna intermedia?\n"
                "2. **Localización:** ¿Qué etapas se realizan casi 100% en Los Ángeles y cuáles dependen de fuera?\n"
                "3. **Identificación:** ¿Qué empresas u organizaciones son las más representativas por etapa?"
            )
        with col_b2:
            st.warning(
                "**Bloque 2: Red y Cooperación - Dini (6 min)**\n"
                "4. **Articulación:** ¿Existe empresa tractora/líder o coordinan vía gremios (CORMA / PYMEMAD)?\n"
                "5. **Cooperación H/V:** ¿Colaboran en transporte, capacitación, prevención de incendios o certificaciones?\n"
                "6. **Falta de actores:** ¿Falta algún servicio técnico especializado, centro tecnológico o apoyo estatal?"
            )
        with col_b3:
            st.success(
                "**Bloque 3: Desafíos y Derivación (4 min)**\n"
                "7. **Cuellos de botella:** ¿En qué etapa o vínculo entre empresas está el principal desafío a fortalecer?\n"
                "8. **Red de contactos:** ¿Qué aserradero y qué proveedor de servicios recomienda contactar para contrastar visiones?"
            )

        if os.path.exists("cuestionario_entrevista.pdf"):
            with open("cuestionario_entrevista.pdf", "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar Pauta Oficial de Entrevista (cuestionario_entrevista.pdf)",
                    data=pdf_file,
                    file_name="cuestionario_entrevista.pdf",
                    mime="application/pdf",
                )

    with sub2:
        st.subheader("Análisis de Estructura y Densidad de Red (Base Datos.xlsx - 15 Nodos)")
        mat_red = np.array(MATRIZ_RED_DINI)
        n_nodos = len(NODOS_RED)
        total_lazos_dirigidos = np.sum(mat_red)
        densidad_dirigida = total_lazos_dirigidos / (n_nodos * (n_nodos - 1))

        grado_salida = np.sum(mat_red, axis=1)
        grado_entrada = np.sum(mat_red, axis=0)

        m1, m2, m3 = st.columns(3)
        m1.metric("Número de Nodos (n)", n_nodos)
        m2.metric("Total Vínculos Activos", int(total_lazos_dirigidos))
        m3.metric("Densidad de la Red", f"{densidad_dirigida * 100:.2f}%")

        angulos = np.linspace(0, 2 * np.pi, n_nodos, endpoint=False)
        x_pos = np.cos(angulos)
        y_pos = np.sin(angulos)

        edge_x, edge_y = [], []
        for i in range(n_nodos):
            for j in range(n_nodos):
                if mat_red[i, j] == 1:
                    edge_x.extend([x_pos[i], x_pos[j], None])
                    edge_y.extend([y_pos[i], y_pos[j], None])

        fig_red = go.Figure()
        fig_red.add_trace(go.Scatter(x=edge_x, y=edge_y, mode="lines", line=dict(width=1, color="#888"), hoverinfo="none", name="Vínculos"))
        fig_red.add_trace(
            go.Scatter(
                x=x_pos,
                y=y_pos,
                mode="markers+text",
                text=NODOS_RED,
                textposition="top center",
                marker=dict(
                    size=12 + grado_salida * 3,
                    color=grado_salida,
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Grado Salida"),
                ),
                name="Empresas (A-O)",
            )
        )
        fig_red.update_layout(title="Grafo de Articulación Empresarial (Reemplazo Interactivo de UCINET)", xaxis=dict(visible=False), yaxis=dict(visible=False), height=500)
        st.plotly_chart(fig_red, use_container_width=True)

        df_grados = pd.DataFrame({
            "Empresa (Nodo)": NODOS_RED,
            "Grado de Salida (Vínculos emitidos)": grado_salida,
            "Grado de Entrada (Vínculos recibidos)": grado_entrada,
            "Grado Total": grado_salida + grado_entrada,
        }).sort_values("Grado Total", ascending=False)
        st.dataframe(df_grados, use_container_width=True)

    with sub3:
        st.subheader("Metodología CEPAL (Padilla y Oddone, 2016) y Ecosistema MIPE Los Lagos")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("**Brechas en los Emprendimientos MIPE (Observatorio Laboral Los Lagos)**")
            st.markdown(
                "- **Modelo de negocio:** Identidad corporativa, diferenciación y estacionalidad.\n"
                "- **Asociatividad y cadena de valor:** Encadenamiento horizontal y vertical con proveedores.\n"
                "- **Procesos:** Formalización, resolución sanitaria rural y logística.\n"
                "- **Competencias:** Habilidades blandas, alfabetización digital (TIC) y manejo técnico."
            )
        with col_m2:
            st.markdown("**Brechas en los Instrumentos de Apoyo Público (GORE / CORFO / SERCOTEC / INDAP)**")
            st.markdown(
                "- **Evaluación:** Pasar de control de gasto a indicadores de impacto real.\n"
                "- **Coordinación:** Reducir superposición programática multisectorial.\n"
                "- **Accesibilidad:** Acercar la oferta a comunas aisladas y rurales.\n"
                "- **Descentralización:** Diseñar instrumentos con pertinencia territorial local."
            )

# ==============================================================================
# MÓDULO 4: ORDENAMIENTO TERRITORIAL Y GEORREFERENCIACIÓN (OSORNO)
# ==============================================================================
elif modulo.startswith("4."):
    st.header("4. Ordenamiento Territorial: Primacía, Matriz de Rondinelli y Georreferenciación")

    ot1, ot2, ot3 = st.tabs([
        "🏙️ Índice de Primacía Urbana",
        "📋 Matriz Funcional de Rondinelli (Guttman)",
        "🗺️ Mapa Georreferenciado: 15 Liceos de Osorno",
    ])

    with ot1:
        st.subheader("Cálculo del Índice de Primacía ($IP = P_1 / (P_2 + P_3 + P_4)$)")
        df_pob_biobio = pd.DataFrame({"Comuna": COMUNAS_BIOBIO, "Población_2024": POB_BIOBIO_2024}).sort_values("Población_2024", ascending=False).reset_index(drop=True)
        df_pob_biobio["Ranking"] = df_pob_biobio.index + 1

        top4 = df_pob_biobio.iloc[:4]
        ip_biobio = top4.loc[0, "Población_2024"] / top4.loc[1:3, "Población_2024"].sum()

        c_ip1, c_ip2 = st.columns(2)
        c_ip1.metric("Índice de Primacía Región del Biobío (Censo 2024)", f"{ip_biobio:.4f}")
        c_ip2.info(f"Centro principal: **{top4.loc[0, 'Comuna']}** ({top4.loc[0, 'Población_2024']:,} hab) frente a **{', '.join(top4.loc[1:3, 'Comuna'])}**.")
        st.dataframe(df_pob_biobio.head(10), use_container_width=True)

    with ot2:
        st.subheader("Complejidad Funcional de Asentamientos - Matriz de Rondinelli (Escala de Guttman)")
        df_rond = pd.DataFrame({
            "Asentamiento Humano": ["Flores (GT)", "Melchor de Mencos (GT)", "San Ignacio/Santa Elena (BZE)", "Benque Viejo (BZE)"],
            "Población": [51535, 19847, 16977, 5824],
            "Educación Diversificada": [1, 1, 1, 0],
            "Universidades": [1, 1, 1, 0],
            "Centros Atención Médica": [1, 1, 1, 1],
            "Seguro Social": [1, 1, 1, 1],
            "Guarderías Infantiles": [1, 1, 0, 0],
            "Programas de Vivienda": [1, 0, 1, 1],
            "Atención a la Mujer": [1, 1, 1, 1],
        })
        servicios_cols = df_rond.columns[2:]
        df_rond["Suma_Servicios (Complejidad)"] = df_rond[servicios_cols].sum(axis=1)
        df_rond["%_Población"] = (df_rond["Población"] / df_rond["Población"].sum() * 100).round(2)
        st.dataframe(df_rond, use_container_width=True)

    with ot3:
        st.subheader("Distribución Espacial de Establecimientos Educacionales en Osorno (Liceos.xlsx)")
        df_liceos = pd.DataFrame(LICEOS_OSORNO)
        st.map(df_liceos, latitude="lat", longitude="lon", size=25)
        st.dataframe(df_liceos, use_container_width=True)

# ==============================================================================
# MÓDULO 5: CONMUTACIÓN LABORAL EN LA PATAGONIA (MANCILLA, SOZA-AMIGO Y FERRADA)
# ==============================================================================
elif modulo.startswith("5."):
    st.header("5. Conmutación Laboral Intertemporal en la Patagonia Chilena (2011 vs 2016)")
    st.markdown("Basado en **Mancilla, Soza-Amigo y Ferrada (2021)**, *Estudios Demográficos y Urbanos*.")

    cnp = ["Valdivia", "Osorno", "Puerto Montt", "Coyhaique", "Punta Arenas"]
    mat_2011_cnp = np.array([
        [2586, 127, 2594],
        [1761, 2250, 1438],
        [3345, 525, 1024],
        [776, 82, 326],
        [195, 327, 799],
    ])
    mat_2016_cnp = np.array([
        [3141, 0, 1231],
        [1336, 955, 137],
        [8951, 1048, 3529],
        [1268, 375, 834],
        [112, 0, 1425],
    ])

    # Índice de Similitud Temporal (Ecuación 4 del paper)
    prop_2011 = mat_2011_cnp / mat_2011_cnp.sum()
    prop_2016 = mat_2016_cnp / mat_2016_cnp.sum()
    ist_cnp = 100.0 * (1.0 - 0.5 * np.sum(np.abs(prop_2016 - prop_2011)))

    chi2_2011, p_2011, _, _ = stats.chi2_contingency(mat_2011_cnp)
    chi2_2016, p_2016, _, _ = stats.chi2_contingency(mat_2016_cnp)

    c_p1, c_p2, c_p3 = st.columns(3)
    c_p1.metric("Índice de Similitud Temporal (2011-2016)", f"{ist_cnp:.2f}%")
    c_p2.metric("Chi-Cuadrado (χ²) 2011", f"{chi2_2011:,.1f}", f"p = {p_2011:.4f}")
    c_p3.metric("Chi-Cuadrado (χ²) 2016", f"{chi2_2016:,.1f}", f"p = {p_2016:.4f}")

    tipos = ["Intrarregional", "Interregional", "Extrarregional"]
    df_c2011 = pd.DataFrame(mat_2011_cnp, index=cnp, columns=tipos)
    df_c2016 = pd.DataFrame(mat_2016_cnp, index=cnp, columns=tipos)

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_11 = px.bar(df_c2011, barmode="stack", title="Flujos de Conmutación hacia Centros Nodales (2011)")
        st.plotly_chart(fig_11, use_container_width=True)
    with col_g2:
        fig_16 = px.bar(df_c2016, barmode="stack", title="Flujos de Conmutación hacia Centros Nodales (2016)")
        st.plotly_chart(fig_16, use_container_width=True)
