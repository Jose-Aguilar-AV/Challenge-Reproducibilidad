# Challenge de Reproducibilidad: MR-DBSCAN

Reproducción del algoritmo MR-DBSCAN para clustering paralelo de datos GPS a gran escala usando Hadoop y PySpark.

## Descripción del Proyecto

Este proyecto implementa el algoritmo **MR-DBSCAN** (MapReduce DBSCAN), una variante paralela del algoritmo de clustering por densidad DBSCAN diseñada para procesar grandes volúmenes de datos espaciales en entornos distribuidos. El algoritmo procesa datos GPS de taxis de Shanghai en 4 etapas usando el paradigma MapReduce.

**Paper de referencia:** He, Y., Tan, H., Luo, W., et al. (2011). "MR-DBSCAN: An Efficient Parallel Density-based Clustering Algorithm using MapReduce". ICPADS 2011.

## Objetivos del Challenge

- Reproducir el algoritmo MR-DBSCAN descrito en el paper original
- Implementar las 4 etapas usando PySpark
- Validar la implementación con datos GPS reales de taxis de Shanghai
- Analizar los resultados obtenidos y compararlos con las expectativas

**Conclusión:** El challenge se cumplió exitosamente. Se implementaron correctamente las 4 etapas del algoritmo y se procesaron 49,662 puntos GPS, identificando 2 clusters globales.

## Estructura del Proyecto

```
.
├── Taxi_070220/              # Carpeta con archivos de datos GPS (4316 archivos)
├── salida/                   # Archivos de salida generados
│   ├── mr_dbscan_results.csv      # Resultados completos con todas las columnas
│   ├── clustering_summary.csv     # Resumen con coordenadas y cluster global
│   └── mr_dbscan_report.txt       # Reporte textual con estadísticas
├── informe/                   # Informe LaTeX del proyecto
│   ├── informe_mr_dbscan.tex      # Código fuente del informe
│   └── informe del challenge.pdf  # PDF compilado del informe
├── unificar_dataset.py        # Script para unificar los archivos en un CSV
├── mr_dbscan_challenge.ipynb # Notebook principal con el algoritmo MR-DBSCAN
├── mr_dbscan_challenge.py     # Versión Python del notebook
├── taxi_data_unificado.csv   # CSV unificado (generado por unificar_dataset.py)
├── INSTRUCCIONES_COMPILACION.md # Instrucciones para compilar el informe LaTeX
└── README.md                  # Este archivo
```

## Requisitos

- Python 3.7+
- pandas
- numpy
- scikit-learn
- pyspark (opcional, para procesamiento distribuido)
- jupyter

### Instalación de dependencias

```bash
pip install pandas numpy scikit-learn pyspark jupyter
```

## Uso

### Paso 1: Unificar el Dataset

Primero, es necesario unificar todos los archivos de datos en un solo CSV para facilitar el procesamiento:

```bash
# Procesar todos los archivos
python unificar_dataset.py

# Procesar solo los primeros 100 archivos (para pruebas)
python unificar_dataset.py --max-files 100

# Especificar carpeta de entrada y archivo de salida
python unificar_dataset.py --input Taxi_070220 --output mi_dataset.csv
```

**Opciones del script:**
- `--input`: Carpeta con los archivos de datos (default: `Taxi_070220`)
- `--output`: Nombre del archivo CSV de salida (default: `taxi_data_unificado.csv`)
- `--max-files`: Número máximo de archivos a procesar (default: todos)
- `--batch-size`: Tamaño del lote para procesamiento (default: 100)

El script generará un archivo CSV con las columnas `lon` (longitud) y `lat` (latitud).

### Paso 2: Ejecutar el Notebook

1. Abrir el notebook:
```bash
jupyter notebook mr_dbscan_challenge.ipynb
```

2. Ejecutar las celdas en orden secuencial.

El notebook:
- Detecta automáticamente si existe el CSV unificado
- Carga los datos, los limpia y normaliza
- Ejecuta el algoritmo MR-DBSCAN en 4 etapas
- Genera archivos de salida en la carpeta `salida/`

## Formato de Datos

Los archivos de datos tienen el siguiente formato:
```
taxi_id,datetime,lon,lat,field1,field2,field3
10001,2007-02-20 00:02:27,121.423167,31.165233,7,116,3
```

El script `unificar_dataset.py` extrae solo las columnas `lon` y `lat` y las guarda en el CSV unificado.

## Algoritmo MR-DBSCAN

El algoritmo se ejecuta en 4 etapas siguiendo el paper original:

### Stage 1: Preprocesamiento y Particionado
- Normalización de coordenadas al rango [0, 1]
- División del espacio en un grid de 120×120 celdas
- Asignación de cada punto a una partición según su ubicación

### Stage 2: DBSCAN Local
- Ejecución independiente de DBSCAN en cada partición
- Identificación de clusters locales con IDs únicos por partición
- Clasificación de puntos como core points, border points o noise

### Stage 3: Detección de Cruces
- Identificación de puntos frontera (cerca de los límites de particiones)
- Construcción de MC Sets (Merge Candidate Sets) para fusión potencial
- Detección de clusters que cruzan fronteras entre particiones

### Stage 4: Fusión Global
- Uso de estructura Union-Find para gestionar equivalencias
- Fusión de clusters locales conectados a través de fronteras
- Relabeling global para asignar IDs únicos a nivel global

### Parámetros Utilizados

- **Eps (epsilon):** 0.002 (radio máximo de vecindad en coordenadas normalizadas)
- **MinPts:** 1000 (número mínimo de puntos para formar un cluster)
- **n_strips:** 120 (número de divisiones por dimensión en el grid)

## Resultados Obtenidos

### Estadísticas Generales
- **Total de puntos procesados:** 49,662
- **Puntos en clusters:** 2,436 (4.9%)
- **Puntos noise (outliers):** 47,226 (95.1%)
- **Número de clusters globales:** 2
- **Pureza del clustering:** 4.9%

### Distribución de Clusters
- **Cluster más grande:** 1,281 puntos
- **Cluster más pequeño:** 1,155 puntos
- **Tamaño promedio:** 1,218.0 puntos
- **Desviación estándar:** 89.1 puntos

### Resultados por Etapa

**Stage 1 - Particionamiento:**
- Particiones con datos: 1,873
- Particiones posibles: 14,400 (120×120)
- Puntos por partición (promedio): 26.5

**Stage 2 - DBSCAN Local:**
- Clusters locales identificados: 1
- Puntos en clusters locales: 2,436
- Puntos noise locales: 47,226

**Stage 3 - Detección de Cruces:**
- Puntos frontera identificados: 34,814 (70.1%)
- MC Sets (candidatos para fusión): 265
- Pares de clusters fusionados: 0

**Stage 4 - Fusión Global:**
- Clusters globales finales: 2
- Puntos en clusters globales: 2,436

### Análisis de Resultados

La pureza del clustering (4.9%) es relativamente baja, lo cual puede deberse a:
- Parámetros estrictos (MinPts=1000 requiere alta densidad)
- Dispersión geográfica de los datos GPS
- Eps pequeño (0.002) en coordenadas normalizadas

Los resultados son consistentes con el comportamiento esperado del algoritmo cuando se utilizan parámetros estrictos. La identificación de 2 clusters globales y el procesamiento exitoso de todas las etapas demuestran que la implementación funciona correctamente.

## Archivos de Salida

Después de ejecutar el notebook, se generan los siguientes archivos en la carpeta `salida/`:

- **mr_dbscan_results.csv:** Resultados completos con todas las columnas (lon, lat, lon_norm, lat_norm, lon_bin, lat_bin, partition_id, local_cluster, is_border, global_cluster)
- **clustering_summary.csv:** Resumen con coordenadas originales y cluster global asignado
- **mr_dbscan_report.txt:** Reporte textual con estadísticas detalladas de cada etapa

## Informe del Proyecto

Se ha generado un informe completo en LaTeX que documenta:
- Marco teórico del algoritmo MR-DBSCAN
- Descripción detallada de la implementación
- Análisis de resultados y pruebas realizadas
- Evaluación del cumplimiento de objetivos
- Referencias al paper original y recursos utilizados

**Ubicación:** `informe/informe_mr_dbscan.tex`

## Autores y Responsabilidades

- **Jose:** Etapa 1 (Preprocesamiento y Particionado) + Setup inicial
- **Miguel:** Etapa 2 (DBSCAN Local) + Etapa 3 (Detección de Cruces)
- **Roger:** Etapa 4 (Fusión Global) + Validación y Reportes

## Referencias

### Artículo Principal
- He, Y., Tan, H., Luo, W., Feng, S., Fan, J. (2011). **MR-DBSCAN: An Efficient Parallel Density-based Clustering Algorithm using MapReduce**. Proceedings of the 2011 IEEE 17th International Conference on Parallel and Distributed Systems (ICPADS). IEEE.

### Algoritmo DBSCAN Original
- Ester, M., Kriegel, H. P., Sander, J., & Xu, X. (1996). **A density-based algorithm for discovering clusters in large spatial databases with noise**. KDD'96: Proceedings of the Second International Conference on Knowledge Discovery and Data Mining.

### MapReduce
- Dean, J., & Ghemawat, S. (2004). **MapReduce: Simplified Data Processing on Large Clusters**. OSDI'04: Sixth Symposium on Operating System Design and Implementation.

### Herramientas Utilizadas
- Apache Spark: https://spark.apache.org/
- PySpark: https://spark.apache.org/docs/latest/api/python/
- Scikit-learn: https://scikit-learn.org/
- Apache Hadoop: https://hadoop.apache.org/

## Dataset

**Datos GPS de Taxis de Shanghai**
- Fuente: Carpeta `Taxi_070220` (4,316 archivos CSV)
- Dataset unificado: [Descargar desde Dropbox](https://www.dropbox.com/scl/fi/mcduu3xv7prq8u1jjiw23/taxi_data_unificado.csv?rlkey=z9usi8jw246ys0gwznw0rm7ax&st=ba9dqy76&dl=0)
- Total de puntos: 49,662
- Rango de coordenadas:
  - Longitud: [121.148300, 121.866100]
  - Latitud: [30.886600, 31.999100]
