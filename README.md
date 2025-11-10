# Challenge de Reproducibilidad: MR-DBSCAN

Reproducción del algoritmo MR-DBSCAN para clustering paralelo de datos GPS a gran escala usando Hadoop y PySpark.

## Descripción del Proyecto

Este proyecto implementa el algoritmo MR-DBSCAN (MapReduce DBSCAN) para clustering de datos espaciales distribuidos. El algoritmo procesa datos GPS de taxis de Shanghai en 4 etapas usando MapReduce.

## Estructura del Proyecto

```
.
├── Taxi_070220/              # Carpeta con archivos de datos GPS (4316 archivos)
├── unificar_dataset.py       # Script para unificar los archivos en un CSV
├── mr_dbscan_challenge.ipynb # Notebook principal con el algoritmo MR-DBSCAN
├── taxi_data_unificado.csv   # CSV unificado (generado por unificar_dataset.py)
└── README.md                 # Este archivo
```

## Requisitos

- Python 3.7+
- pandas
- numpy
- scikit-learn
- pyspark (opcional, para procesamiento distribuido)
- jupyter

Instalar dependencias:
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
- Si no existe, puede generarlo automáticamente (si `GENERAR_CSV_AUTOMATICAMENTE = True`)
- Carga los datos, los limpia y normaliza
- Ejecuta el algoritmo MR-DBSCAN en 4 etapas

## Formato de Datos

Los archivos de datos tienen el siguiente formato:
```
taxi_id,datetime,lon,lat,field1,field2,field3
10001,2007-02-20 00:02:27,121.423167,31.165233,7,116,3
```

El script `unificar_dataset.py` extrae solo las columnas `lon` y `lat` y las guarda en el CSV unificado.

## Algoritmo MR-DBSCAN

El algoritmo se ejecuta en 4 etapas:

1. **Stage 1 - Preprocesamiento:** Particionamiento del dataset en grid
2. **Stage 2 - DBSCAN Local:** Clustering independiente en cada partición
3. **Stage 3 - Detección de Cruces:** Identificar clusters que cruzan fronteras
4. **Stage 4 - Fusión Global:** Unificar clusters y relabeling global

### Parámetros

- **Eps (epsilon):** 0.002 (radio máximo de vecindad)
- **MinPts:** 1000 (número mínimo de puntos para formar un cluster)
- **n_strips:** 120 (número de divisiones por dimensión en el grid)

## Notas

- La primera ejecución del script de unificación puede tardar varios minutos (procesa 4316 archivos)
- El CSV unificado se guarda para uso posterior (las siguientes ejecuciones son más rápidas)
- El notebook está diseñado para ejecutarse en un cluster Hadoop con 3 nodos, pero también funciona en modo local
- Para pruebas rápidas, puedes limitar el número de archivos usando `--max-files`

## Autores

- Persona 1: Etapa 1 (Preprocesamiento y Particionado)
- Persona 2: Etapa 2 (DBSCAN Local) + Etapa 3 (Detección de Cruces)
- Persona 3: Etapa 4 (Fusión Global) + Validación y Reportes

## Referencias

- Paper: MR-DBSCAN: An Efficient Parallel Density-based Clustering Algorithm using MapReduce
- Autores: Yaobin He, Haoyu Tan, Wuman Luo, et al.
- Dataset: Datos GPS reales de taxis de Shanghai


## Link del dataset
https://www.dropbox.com/scl/fi/mcduu3xv7prq8u1jjiw23/taxi_data_unificado.csv?rlkey=z9usi8jw246ys0gwznw0rm7ax&st=ba9dqy76&dl=0
