"""
Script para unificar todos los archivos de datos de taxi en un solo archivo CSV.

Este script lee todos los archivos de la carpeta Taxi_070220 y los combina
en un único archivo CSV con las columnas necesarias para el análisis MR-DBSCAN.

Uso:
    python unificar_dataset.py

El archivo de salida será: taxi_data_unificado.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import sys
from datetime import datetime

warnings.filterwarnings('ignore')

def unificar_dataset(data_folder='Taxi_070220', output_file='taxi_data_unificado.csv', 
                     max_files=None, batch_size=100):
    """
    Unifica todos los archivos de datos de taxi en un solo CSV.
    
    Parámetros:
        data_folder (str): Ruta a la carpeta con los archivos de datos
        output_file (str): Nombre del archivo CSV de salida
        max_files (int): Número máximo de archivos a procesar (None = todos)
        batch_size (int): Tamaño del lote para procesamiento por lotes
    
    Retorna:
        str: Ruta al archivo CSV generado
    """
    print("=" * 70)
    print("UNIFICACIÓN DE DATASET DE TAXIS")
    print("=" * 70)
    print(f"Fecha de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verificar que la carpeta existe
    data_path = Path(data_folder)
    if not data_path.exists():
        raise FileNotFoundError(f"La carpeta {data_folder} no existe. Verifica la ruta.")
    
    # Obtener lista de archivos
    data_files = sorted(list(data_path.glob('Taxi_*')))
    total_files = len(data_files)
    
    if total_files == 0:
        raise ValueError(f"No se encontraron archivos en la carpeta {data_folder}")
    
    print(f"✓ Archivos encontrados: {total_files:,}")
    
    # Limitar archivos si se especifica
    if max_files is not None and max_files < total_files:
        data_files = data_files[:max_files]
        print(f"⚠ Usando solo los primeros {max_files:,} archivos (modo prueba)")
        print(f"  Para procesar todos, ejecutar sin --max-files")
    else:
        print(f"✓ Procesando todos los {total_files:,} archivos")
    
    print()
    print("⏳ Leyendo archivos...")
    print("-" * 70)
    
    # Procesar archivos en lotes
    data_list = []
    processed_count = 0
    errors_count = 0
    total_rows = 0
    
    for batch_start in range(0, len(data_files), batch_size):
        batch_files = data_files[batch_start:batch_start + batch_size]
        batch_data = []
        
        for file_path in batch_files:
            try:
                # Leer archivo CSV
                df_temp = pd.read_csv(
                    file_path,
                    header=None,
                    engine='c',
                    low_memory=False
                )
                
                # Seleccionar solo las columnas que necesitamos (lon y lat)
                if df_temp.shape[1] >= 4:
                    df_temp = df_temp.iloc[:, [2, 3]].copy()
                    df_temp.columns = ['lon', 'lat']
                    
                    # Convertir a float, manejando errores
                    df_temp['lon'] = pd.to_numeric(df_temp['lon'], errors='coerce')
                    df_temp['lat'] = pd.to_numeric(df_temp['lat'], errors='coerce')
                    
                    # Eliminar filas con valores no numéricos
                    df_temp = df_temp.dropna()
                    
                    if len(df_temp) > 0:
                        batch_data.append(df_temp)
                        processed_count += 1
                        total_rows += len(df_temp)
                        
            except Exception as e:
                errors_count += 1
                if errors_count <= 5:
                    print(f"  ⚠ Error al leer {file_path.name}: {e}")
                continue
        
        # Combinar datos del lote
        if batch_data:
            batch_df = pd.concat(batch_data, ignore_index=True)
            data_list.append(batch_df)
        
        # Mostrar progreso
        progress = min(batch_start + batch_size, len(data_files))
        percentage = (progress / len(data_files)) * 100
        print(f"  Procesados: {progress:,} / {len(data_files):,} archivos ({percentage:.1f}%) - "
              f"Filas acumuladas: {total_rows:,}")
    
    if errors_count > 5:
        print(f"\n⚠ Total de archivos con errores: {errors_count}")
    
    if len(data_list) == 0:
        raise ValueError("No se pudo leer ningún archivo. Verifica el formato de los archivos.")
    
    # Combinar todos los DataFrames
    print()
    print("-" * 70)
    print(f"⏳ Combinando {len(data_list):,} lotes de datos...")
    data = pd.concat(data_list, ignore_index=True)
    
    print(f"✓ Datos combinados: {len(data):,} filas")
    
    # Limpiar datos
    print()
    print("⏳ Limpiando datos...")
    initial_count = len(data)
    
    # Eliminar valores nulos
    data = data.dropna(subset=['lon', 'lat'])
    
    # Filtrar coordenadas inválidas (rango válido para GPS de Shanghai)
    data = data[(data['lon'] >= 120) & (data['lon'] <= 122)]
    data = data[(data['lat'] >= 30) & (data['lat'] <= 32)]
    
    removed_count = initial_count - len(data)
    if removed_count > 0:
        print(f"  - Filas eliminadas (valores inválidos): {removed_count:,}")
        print(f"  - Filas válidas: {len(data):,}")
    
    # Guardar a CSV
    print()
    print("⏳ Guardando archivo CSV...")
    output_path = Path(output_file)
    data.to_csv(output_path, index=False)
    
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print()
    print("=" * 70)
    print("✓ UNIFICACIÓN COMPLETADA")
    print("=" * 70)
    print(f"  - Archivo de salida: {output_file}")
    print(f"  - Tamaño del archivo: {file_size_mb:.2f} MB")
    print(f"  - Total de filas: {len(data):,}")
    print(f"  - Archivos procesados: {processed_count:,}")
    print(f"  - Archivos con errores: {errors_count}")
    print(f"  - Rango Longitud: [{data['lon'].min():.6f}, {data['lon'].max():.6f}]")
    print(f"  - Rango Latitud: [{data['lat'].min():.6f}, {data['lat'].max():.6f}]")
    print(f"  - Fecha de finalización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return str(output_path)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Unifica archivos de datos de taxi en un solo CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Procesar todos los archivos
  python unificar_dataset.py
  
  # Procesar solo los primeros 100 archivos (prueba)
  python unificar_dataset.py --max-files 100
  
  # Especificar carpeta y archivo de salida
  python unificar_dataset.py --input Taxi_070220 --output mi_dataset.csv
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='Taxi_070220',
        help='Carpeta con los archivos de datos (default: Taxi_070220)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='taxi_data_unificado.csv',
        help='Nombre del archivo CSV de salida (default: taxi_data_unificado.csv)'
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        default=None,
        help='Número máximo de archivos a procesar (default: todos)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=100,
        help='Tamaño del lote para procesamiento (default: 100)'
    )
    
    args = parser.parse_args()
    
    try:
        output_path = unificar_dataset(
            data_folder=args.input,
            output_file=args.output,
            max_files=args.max_files,
            batch_size=args.batch_size
        )
        print(f"\n✓ Archivo generado exitosamente: {output_path}")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

