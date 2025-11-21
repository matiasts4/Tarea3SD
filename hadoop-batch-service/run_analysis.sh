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

# Salir del modo seguro de HDFS
echo "[INFO] Verificando modo seguro de HDFS..."
hdfs dfsadmin -safemode wait
echo "[INFO] ✓ HDFS fuera de modo seguro"
echo ""

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
echo "[INFO] Cargando yahoo_answers.txt..."
hdfs dfs -put -f /app/data/yahoo_answers.txt /input/ 2>&1
echo "[INFO] Cargando llm_answers.txt..."
hdfs dfs -put -f /app/data/llm_answers.txt /input/ 2>&1
echo "[INFO] Cargando stopwords_es.txt..."
hdfs dfs -put -f /app/scripts/stopwords_es.txt /stopwords/ 2>&1
echo "[INFO] Cargando stopwords_en.txt..."
hdfs dfs -put -f /app/scripts/stopwords_en.txt /stopwords/ 2>&1
echo "       ✓ Datos cargados a HDFS"
echo ""

# Verificar archivos en HDFS
echo "[INFO] Verificando archivos en HDFS..."
echo "[INFO] Contenido de /input/:"
hdfs dfs -ls /input/
echo "[INFO] Contenido de /stopwords/:"
hdfs dfs -ls /stopwords/
echo "[INFO] Verificando permisos:"
hdfs dfs -ls -R / | grep -E "(input|stopwords)"
echo ""

# Ejecutar análisis Pig para Yahoo! Answers
echo "[7/10] Ejecutando análisis Pig para Yahoo! Answers..."
echo "[INFO] Copiando archivos de HDFS al sistema de archivos local para Pig..."
mkdir -p /input /output /stopwords
hdfs dfs -get /input/yahoo_answers.txt /input/
hdfs dfs -get /stopwords/stopwords_es.txt /stopwords/
hdfs dfs -get /stopwords/stopwords_en.txt /stopwords/
echo "[INFO] Ejecutando Pig en modo local..."
pig -x local -f /app/scripts/wordcount_yahoo_simple.pig
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo en el análisis de Yahoo! Answers"
    echo "[INFO] Revisando logs de Pig..."
    cat /app/pig_*.log | tail -100
    exit 1
fi
echo "       ✓ Análisis de Yahoo! completado"
echo ""

# Ejecutar análisis Pig para LLM Answers
echo "[8/10] Ejecutando análisis Pig para LLM Answers..."
echo "[INFO] Copiando archivo LLM de HDFS al sistema de archivos local..."
hdfs dfs -get /input/llm_answers.txt /input/
echo "[INFO] Ejecutando Pig en modo local..."
pig -x local -f /app/scripts/wordcount_llm_simple.pig
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo en el análisis de LLM Answers"
    exit 1
fi
echo "       ✓ Análisis de LLM completado"
echo ""

# Copiar resultados al directorio de resultados
echo "[9/10] Copiando resultados..."
# Los resultados ya están en /output/ (modo local), solo necesitamos copiarlos
cat /output/yahoo_wordcount/part-r-00000 > /app/results/yahoo_wordcount.txt
cat /output/llm_wordcount/part-r-00000 > /app/results/llm_wordcount.txt
echo "       ✓ Resultados copiados"
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
