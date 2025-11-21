#!/bin/bash
set -e

echo "Iniciando análisis batch..."

# Iniciar servicios
service ssh start > /dev/null 2>&1
[ ! -d "/opt/hadoop/hdfs/namenode/current" ] && hdfs namenode -format -force > /dev/null 2>&1
start-dfs.sh > /dev/null 2>&1
start-yarn.sh > /dev/null 2>&1

# Esperar HDFS
for i in {1..30}; do hdfs dfs -ls / &> /dev/null && break; sleep 2; done
hdfs dfsadmin -safemode wait > /dev/null 2>&1
hdfs dfs -mkdir -p /input /output /stopwords 2>/dev/null || true

# Extraer y cargar datos
echo "[1/4] Extrayendo datos..."
python3 /app/extract_data.py 2>&1 | grep -E "(✓|Total|Promedio)"

echo "[2/4] Cargando a HDFS..."
hdfs dfs -put -f /app/data/*.txt /input/ 2>/dev/null
hdfs dfs -put -f /app/scripts/stopwords_*.txt /stopwords/ 2>/dev/null

# Ejecutar Pig
echo "[3/4] Ejecutando Pig..."
rm -rf /input /output /stopwords && mkdir -p /input /output /stopwords
hdfs dfs -get /input/*.txt /input/ 2>/dev/null
hdfs dfs -get /stopwords/*.txt /stopwords/ 2>/dev/null
pig -x local -f /app/scripts/wordcount_yahoo_simple.pig > /dev/null 2>&1
pig -x local -f /app/scripts/wordcount_llm_simple.pig > /dev/null 2>&1

# Resultados
echo "[4/4] Generando visualizaciones..."
cat /output/yahoo_wordcount/part-r-00000 > /app/results/yahoo_wordcount.txt
cat /output/llm_wordcount/part-r-00000 > /app/results/llm_wordcount.txt
python3 /app/analyze_wordcount.py 2>&1 | grep -E "(✓|Guardado)"

echo ""
echo "✓ Completado - Resultados en ./batch-analysis/results/"
echo ""
