#!/bin/bash
set -e

echo "========================================================================"
echo "ANÁLISIS BATCH CON HADOOP Y PIG - TAREA 3"
echo "========================================================================"
echo ""

# Función para verificar si HDFS está listo
wait_for_hdfs() {
    echo "[INFO] Esperando a que HDFS esté listo..."
    for i in {1..30}; do
        if hdfs dfs -ls / &> /dev/null; then
            echo "[INFO] ✓ HDFS está listo"
            return 0
        fi
        echo "[INFO] Intento $i/30: HDFS no está listo, esperando..."
        sleep 2
    done
    echo "[ERROR] HDFS no está disponible después de 60 segundos"
    return 1
}

# Iniciar servicio SSH
echo "[1/10] Iniciando servicio SSH..."
service ssh start
echo "       ✓ SSH iniciado"
echo ""

# Formatear NameNode (solo si no existe)
if [ ! -d "/opt/hadoop/hdfs/namenode/current" ]; then
    echo "[2/10] Formateando NameNode (primera vez)..."
    hdfs namenode -format -force
    echo "       ✓ NameNode formateado"
else
    echo "[2/10] NameNode ya está formateado, omitiendo..."
fi
echo ""

# Iniciar servicios de Hadoop
echo "[3/10] Iniciando servicios de Hadoop..."
start-dfs.sh
start-yarn.sh
echo "       ✓ HDFS y YARN iniciados"
echo ""

# Esperar a que HDFS esté listo
wait_for_hdfs

# Crear directorios en HDFS
echo "[4/10] Creando directorios en HDFS..."
hdfs dfs -mkdir -p /input
hdfs dfs -mkdir -p /output
hdfs dfs -mkdir -p /stopwords
echo "       ✓ Directorios creados"
echo ""

# Extraer datos de PostgreSQL
echo "[5/10] Extrayendo datos de PostgreSQL..."
python3 /app/extract_data.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo en la extracción de datos"
    exit 1
fi
echo ""

# Cargar datos a HDFS
echo "[6/10] Cargando datos a HDFS..."
hdfs dfs -put -f /app/data/yahoo_answers.txt /input/
hdfs dfs -put -f /app/data/llm_answers.txt /input/
hdfs dfs -put -f /app/scripts/stopwords_es.txt /stopwords/
hdfs dfs -put -f /app/scripts/stopwords_en.txt /stopwords/
echo "       ✓ Datos cargados a HDFS"
echo ""

# Verificar archivos en HDFS
echo "[INFO] Verificando archivos en HDFS..."
hdfs dfs -ls /input/
hdfs dfs -ls /stopwords/
echo ""

# Ejecutar análisis Pig para Yahoo! Answers
echo "[7/10] Ejecutando análisis Pig para Yahoo! Answers..."
pig -x mapreduce /app/scripts/wordcount_yahoo.pig
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo en el análisis de Yahoo! Answers"
    exit 1
fi
echo "       ✓ Análisis de Yahoo! completado"
echo ""

# Ejecutar análisis Pig para LLM Answers
echo "[8/10] Ejecutando análisis Pig para LLM Answers..."
pig -x mapreduce /app/scripts/wordcount_llm.pig
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo en el análisis de LLM Answers"
    exit 1
fi
echo "       ✓ Análisis de LLM completado"
echo ""

# Descargar resultados de HDFS
echo "[9/10] Descargando resultados de HDFS..."
hdfs dfs -getmerge /output/yahoo_wordcount /app/results/yahoo_wordcount.txt
hdfs dfs -getmerge /output/llm_wordcount /app/results/llm_wordcount.txt
echo "       ✓ Resultados descargados"
echo ""

# Generar análisis y visualizaciones
echo "[10/10] Generando análisis y visualizaciones..."
python3 /app/analyze_wordcount.py
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo en la generación de visualizaciones"
    exit 1
fi
echo "        ✓ Visualizaciones generadas"
echo ""

echo "========================================================================"
echo "✓ ANÁLISIS BATCH COMPLETADO EXITOSAMENTE"
echo "========================================================================"
echo ""
echo "RESULTADOS DISPONIBLES EN:"
echo "  - /app/results/yahoo_wordcount.txt"
echo "  - /app/results/llm_wordcount.txt"
echo "  - /app/results/analysis_report.json"
echo "  - /app/results/wordcloud_yahoo.png"
echo "  - /app/results/wordcloud_llm.png"
echo "  - /app/results/top_words_comparison.png"
echo ""
echo "Para mantener el contenedor activo, presiona Ctrl+C para salir"
echo "o ejecuta: docker logs -f hadoop-batch-service"
echo ""

# Mantener el contenedor activo
tail -f /dev/null
