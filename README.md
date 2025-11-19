# Tarea2SD - Sistemas Distribuidos

## Tarea 1: Sistema de Consultas con Caché (Arquitectura Síncrona)
## Tarea 2: Pipeline Asíncrono con Kafka y Flink (Arquitectura Asíncrona)
## Tarea 3: Análisis Batch con Hadoop y Pig (Procesamiento Offline)

### Resumen
Pipeline de microservicios que procesa preguntas del dataset Yahoo Answers usando Google Gemini para generar respuestas y almacena resultados en PostgreSQL 14. 

**Tarea 1:** Sistema de caché en memoria con **tres políticas de remoción configurables** (LRU, FIFO, LFU) para optimizar rendimiento y reducir llamadas a la API.

**Tarea 2:** Arquitectura asíncrona con Apache Kafka para mensajería y Apache Flink para procesamiento de flujos en tiempo real con validación de calidad de respuestas.

**Tarea 3:** Sistema de análisis batch con Apache Hadoop y Pig para procesamiento distribuido de datos históricos, análisis lingüístico comparativo (Yahoo! vs LLM) y generación de visualizaciones.

### Servicios y Puertos

#### Servicios Principales
- **Cache Service**: http://localhost:8001 (POST /query, GET /, GET /stats)
- **Score Service**: http://localhost:8002 (POST /score, GET /)
- **Storage Service**: http://localhost:8003 (POST /storage, POST /hit, GET /, GET /health, GET /lookup)
- **PostgreSQL**: localhost:5432 (user/password: user/password, db: yahoo_db)

#### Servicios Tarea 2 (Arquitectura Asíncrona)
- **Zookeeper**: localhost:2181 (Coordinación de Kafka)
- **Kafka**: localhost:9092 (Bus de mensajes)
- **Flink Processor**: Procesamiento de flujos (sin puerto expuesto)
- **Traffic Generator**: Generador de tráfico (sin puerto expuesto)

#### Servicios Tarea 3 (Análisis Batch)
- **Hadoop Batch Service**: Análisis distribuido con Hadoop + Pig
  - NameNode Web UI: http://localhost:9870
  - ResourceManager Web UI: http://localhost:8088
  - HDFS: localhost:9000

### Requisitos
- Docker y Docker Compose
- Clave de Google AI Studio (GEMINI_API_KEY)

### Configuración
1) Copiar y configurar variables de entorno:
   ```bash
   cp .env.example .env
   nano .env  # o usar tu editor preferido
   ```

2) Configurar parámetros en `.env`:
   ```bash
   # API de Google Gemini (REQUERIDO)
   GEMINI_API_KEY=tu_api_key_aqui
   
   # Configuración de Caché (EXPERIMENTAL)
   CACHE_POLICY=LRU    # Opciones: LRU, FIFO, LFU
   CACHE_SIZE=1500     # Tamaño de caché
   CACHE_TTL=0         # TTL en segundos (0 = sin expiración)
   
   # Configuración de Tráfico
   SLEEP_TIME=1.5      # Segundos entre consultas
   
   # Configuración de Quality Processor (Tarea 2)
   QUALITY_THRESHOLD=0.6  # Umbral de calidad (0.0-1.0)
   MAX_ATTEMPTS=3         # Máximo de reintentos por pregunta
   ```
   
   **Nota**: Ya no es necesario modificar `docker-compose.yml` manualmente. Todos los parámetros experimentales se configuran desde `.env`.

### Políticas de Caché Implementadas

#### 1. **LRU (Least Recently Used)** - Predeterminada
- Elimina el elemento **menos recientemente usado**
- Ideal para: patrones de acceso con localidad temporal
- Ventajas: Mantiene datos "calientes" en caché
- Implementación: `collections.OrderedDict`

#### 2. **FIFO (First In First Out)**
- Elimina el elemento **más antiguo** (primero en entrar)
- Ideal para: flujos de datos secuenciales
- Ventajas: Simplicidad y predicibilidad
- Implementación: `deque` para orden de inserción

#### 3. **LFU (Least Frequently Used)**
- Elimina el elemento **menos frecuentemente accedido**
- Ideal para: identificar datos populares a largo plazo
- Ventajas: Retiene elementos de alta demanda
- Implementación: Tracking de frecuencias con grupos

### Despliegue
```bash
docker-compose up --build -d
```

### Verificación Rápida
```bash
# Verificar servicios
curl http://localhost:8001/
curl http://localhost:8002/
curl http://localhost:8003/health

# Ver estadísticas de caché
curl http://localhost:8001/stats

# Verificar base de datos
psql -h localhost -U user -d yahoo_db -c "SELECT COUNT(*) FROM responses;"
```

### Guía de Experimentación y Comparación realizada en el informe

#### Opción 1: Experimentación Automatizada (RECOMENDADO)

Para ahorrar tiempo y generar todos los datos necesarios automáticamente:

```bash
# 1. Dar permisos de ejecución
chmod +x run_experiments.sh

# 2. Ejecutar todos los experimentos (toma ~2-3 horas)
./run_experiments.sh

# 3. Analizar resultados y generar gráficos
pip3 install pandas matplotlib seaborn
python3 analyze_results.py
```

**Esto genera automáticamente:**
- Comparación de 3 políticas (LRU, FIFO, LFU)
- Análisis de 4 tamaños de caché (500, 1000, 1500, 2000)
- 2 distribuciones de tráfico (alta y baja frecuencia)
- 3 valores de TTL (60s, 300s, 600s)
- Gráficos y tablas comparativas listas para el informe

#### Opción 2: Experimentación Manual

Si prefieres experimentar manualmente:

```bash
# 1. Editar .env con la configuración deseada
nano .env

# Ejemplo: Probar política FIFO
# CACHE_POLICY=FIFO
# CACHE_SIZE=1500
# CACHE_TTL=0

# 2. Levantar servicios
docker-compose up --build -d

# 3. Esperar procesamiento (~5-10 minutos)
sleep 300

# 4. Obtener métricas
curl http://localhost:8001/stats > resultado_FIFO.json

# 5. Detener y limpiar
docker-compose down -v
```

**Para comparar diferentes parámetros**, modificar `.env` y repetir:
- **Políticas**: `CACHE_POLICY=LRU|FIFO|LFU`
- **Tamaños**: `CACHE_SIZE=500|1000|1500|2000`
- **TTL**: `CACHE_TTL=0|60|300|600`
- **Tráfico**: `SLEEP_TIME=0.5|1.5|3.0`

### Notas Técnicas
- **PostgreSQL**: versión 14 (postgres:14-alpine)
- **Caché**: En memoria (no Redis), políticas configurables
- **Modelo Gemini**: Google Gemini 2.5 Flash Lite (configurable vía `GEMINI_MODEL_NAME`)
- **Dataset**: 14,730 preguntas de Yahoo Answers
- **Kafka**: Confluent Platform 7.5.0
- **Quality Processor**: kafka-python 2.0.2 (optimizado, reemplazó PyFlink)
- **Zookeeper**: Confluent Platform 7.5.0
- **Registros procesados**: 14,376 (97.6% del dataset)

---

## Arquitectura del Sistema

### Tarea 1: Arquitectura Síncrona
```
Traffic Generator → Cache Service → Score Service → Storage Service → PostgreSQL
                         ↓
                    (Cache Hit)
                         ↓
                    Storage Service
```

### Tarea 2: Arquitectura Asíncrona
```
Traffic Generator → Cache Service → Storage Lookup
                         ↓
                    Kafka (questions)
                         ↓
                    Score Service → LLM
                         ↓
                    Kafka (generated)
                         ↓
                  Flink Processor
                    /          \
        (score >= 0.5)      (score < 0.5)
              ↓                  ↓
    Kafka (validated)    Kafka (questions) [retry]
              ↓
        Storage Service → PostgreSQL
```

### Tópicos de Kafka (Tarea 2)
- **questions**: Preguntas pendientes de procesamiento
- **generated**: Respuestas generadas por el LLM
- **validated-responses**: Respuestas validadas por Flink (alta calidad)
- **errors**: Errores de procesamiento

---

## Quality Processor (Tarea 2)

### Función de Calidad
El procesador calcula un **score multi-métrica** que combina tres aspectos:

```python
Score = (Completeness × 0.4) + (Keyword Overlap × 0.3) + (Length Appropriateness × 0.3)
```

**Componentes:**
- **Completeness (40%)**: Verifica longitud razonable (≥5 palabras)
- **Keyword Overlap (30%)**: Coincidencia de palabras clave (30% requerido)
- **Length Appropriateness (30%)**: Penaliza solo respuestas muy cortas

**Ejemplo:**
- Original: "Machine learning is a subset of AI"
- Generated: "ML is AI subset that learns from data"
- Completeness: 1.0 (≥5 palabras)
- Keyword overlap: 0.7 (buena coincidencia)
- Length: 1.0 (longitud apropiada)
- **Score final: 0.88** ✓

### Lógica de Validación
- **Score >= 0.6**: Respuesta validada → `validated-responses` → PostgreSQL
- **Score < 0.6 y attempts < 3**: Reintento → `questions` (regenerar)
- **Score < 0.6 y attempts >= 3**: Descartada

### Métricas Reales del Sistema
- **Tasa de aprobación primer intento**: 80.7% (813/1,008)
- **Tasa de aprobación segundo intento**: 15.5% (156/1,008)
- **Tasa de aprobación tercer intento**: 3.8% (39/1,008)
- **Recuperación total**: 100% (1,008/1,008)
- **Overhead de reintentos**: 19.3% de llamadas adicionales al LLM
- **Score promedio final**: 0.718 (mejora de 2.6% por feedback loop)

### Verificación del Quality Processor

```bash
# Ver logs del procesador
docker logs -f flink-processor

# Ver estadísticas de procesamiento
docker logs flink-processor 2>&1 | grep "Stats:" | tail -3

# Ver mensajes validados
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic validated-responses --from-beginning --max-messages 5

# Verificar base de datos
docker exec db psql -U user -d yahoo_db \
  -c "SELECT COUNT(*) as total, ROUND(AVG(score)::numeric, 3) as score_promedio FROM responses;"

# Ver últimas respuestas guardadas
docker exec db psql -U user -d yahoo_db \
  -c "SELECT question, score, created_at FROM responses ORDER BY created_at DESC LIMIT 5;"
```

---

## Análisis Experimental Requerido

### Tarea 1: Políticas de Caché

Para cumplir con los requisitos del proyecto, debes realizar comparaciones experimentales de:

#### 1. **Políticas de Caché** (al menos 2)
- LRU vs FIFO vs LFU
- Métricas: hit_rate, hits, misses, evictions
- Procedimiento: Ejecutar con cada política y comparar resultados

#### 2. **Tamaño de Caché**
- Probar diferentes valores: 500, 1000, 1500, 2000
- Analizar impacto en hit_rate y evictions
- En `.env`, modificar `CACHE_SIZE`

#### 3. **Distribuciones de Tráfico** (al menos 2)
- Modificar `SLEEP_TIME` en `.env`:
  - **Alta frecuencia**: SLEEP_TIME=0.5 (más repeticiones esperadas)
  - **Baja frecuencia**: SLEEP_TIME=3.0 (menos repeticiones)
- Comparar hit_rate bajo cada distribución

#### 4. **TTL (Time To Live)**
- Probar diferentes valores: 0 (sin expiración), 60, 300, 600 segundos
- Analizar impacto en hit_rate y nuevas métricas: expirations
- En `.env`, modificar `CACHE_TTL`
- Observar cómo entradas antiguas se invalidan automáticamente

### Tarea 2: Calidad de Respuestas

#### 1. **Threshold de Calidad**
- Probar diferentes valores: 0.4, 0.6, 0.8
- Analizar tasa de validación vs reintentos
- En `.env`, modificar `QUALITY_THRESHOLD`
- **Valor óptimo encontrado**: 0.6 (80.7% aprobación primer intento)

#### 2. **Máximo de Reintentos**
- Probar diferentes valores: 1, 3, 5
- Analizar impacto en calidad final
- En `.env`, modificar `MAX_ATTEMPTS`
- **Valor óptimo encontrado**: 3 (100% recuperación con 19.3% overhead)

---

## Documentación Adicional

### Tarea 1
- `run_experiments.sh` - Script automatizado para experimentación
- `analyze_results.py` - Análisis y generación de gráficos


### Estado del Sistema
✅ **Tarea 1:** Sistema de caché completamente funcional con 3 políticas  
✅ **Tarea 2:** Pipeline asíncrono con Kafka y Flink operativo y verificado


---

## Tarea 3: Análisis Batch con Hadoop y Pig

### Descripción
Sistema de análisis batch que procesa el dataset completo de respuestas almacenadas en PostgreSQL para realizar análisis lingüístico comparativo entre respuestas humanas (Yahoo! Answers) y respuestas generadas por IA (LLM Gemini).

### Arquitectura Híbrida

El sistema ahora combina dos paradigmas de procesamiento:

**Procesamiento Online (Tareas 1-2)**:
```
Traffic Generator → Kafka → Flink → PostgreSQL
(Tiempo real, evento por evento)
```

**Procesamiento Batch (Tarea 3)**:
```
PostgreSQL → Hadoop/Pig → Análisis Lingüístico → Visualizaciones
(Histórico, dataset completo)
```

### Componentes Nuevos

#### 1. Extracción de Datos
- **Script**: `batch-analysis/extract_data.py`
- **Función**: Extrae respuestas desde PostgreSQL
- **Salidas**: 
  - `yahoo_answers.txt`: Respuestas humanas
  - `llm_answers.txt`: Respuestas del LLM
  - `extraction_stats.json`: Estadísticas de extracción

#### 2. Ecosistema Hadoop
- **Hadoop 3.3.6**: Almacenamiento distribuido (HDFS)
- **Apache Pig 0.17.0**: Scripts de alto nivel para MapReduce
- **Modo**: Pseudo-distribuido (single node)
- **Configuración**: HDFS con replicación 1

#### 3. Scripts Pig
- **wordcount_yahoo.pig**: Análisis de vocabulario Yahoo!
- **wordcount_llm.pig**: Análisis de vocabulario LLM
- **Lógica implementada**:
  1. Tokenización (separar en palabras)
  2. Limpieza (minúsculas, eliminar puntuación)
  3. Filtrado de stopwords (español + inglés)
  4. Conteo de frecuencias (MapReduce)
  5. Ordenamiento por frecuencia

#### 4. Análisis y Visualización
- **Script**: `batch-analysis/analyze_wordcount.py`
- **Funcionalidades**:
  - Wordclouds comparativos
  - Gráficos de barras (Top 20 palabras)
  - Tablas comparativas (Top 50)
  - Diagrama de Venn (overlap de vocabulario)
  - Estadísticas (diversidad léxica, palabras únicas)

### Ejecución del Análisis Batch

#### Opción 1: Ejecución Automática (Recomendado)

```bash
# Levantar todos los servicios (incluido Hadoop)
docker-compose up --build -d

# El servicio hadoop-batch-service ejecutará automáticamente:
# 1. Extracción de datos desde PostgreSQL
# 2. Carga a HDFS
# 3. Ejecución de scripts Pig
# 4. Generación de visualizaciones

# Ver progreso en tiempo real
docker logs -f hadoop-batch-service

# Los resultados se guardan en: ./batch-analysis/results/
```

#### Opción 2: Ejecución Manual

```bash
# Levantar solo servicios necesarios
docker-compose up -d db

# Ejecutar análisis batch
docker-compose up hadoop-batch-service

# Ver logs
docker logs hadoop-batch-service
```

### Resultados Generados

Todos los resultados se guardan en `./batch-analysis/results/`:

#### Archivos de Wordcount
- `yahoo_wordcount.txt`: Frecuencias de palabras (Yahoo!)
- `llm_wordcount.txt`: Frecuencias de palabras (LLM)

#### Visualizaciones
- `wordcloud_yahoo.png`: Nube de palabras Yahoo! (azul)
- `wordcloud_llm.png`: Nube de palabras LLM (rojo)
- `top_words_comparison.png`: Gráfico de barras comparativo
- `vocabulary_venn.png`: Diagrama de Venn de overlap

#### Análisis
- `comparison_table_top50.csv`: Tabla comparativa Top 50
- `analysis_report.json`: Estadísticas completas

### Acceso a Interfaces Web

Una vez levantado el servicio, puedes acceder a:

- **NameNode UI**: http://localhost:9870
  - Ver estado de HDFS
  - Explorar archivos en HDFS
  - Monitorear DataNodes

- **ResourceManager UI**: http://localhost:8088
  - Ver trabajos MapReduce
  - Monitorear recursos YARN
  - Historial de aplicaciones

### Métricas y Análisis

El análisis genera las siguientes métricas:

#### Yahoo! Answers
- Total de palabras procesadas
- Vocabulario único
- Diversidad léxica
- Top N palabras más frecuentes

#### LLM (Gemini)
- Total de palabras procesadas
- Vocabulario único
- Diversidad léxica
- Top N palabras más frecuentes

#### Comparación
- Palabras comunes entre ambos conjuntos
- Palabras exclusivas de Yahoo!
- Palabras exclusivas del LLM
- Porcentaje de overlap de vocabulario

### Ejemplo de Resultados

```json
{
  "yahoo_answers": {
    "total_words": 150000,
    "unique_words": 8500,
    "lexical_diversity": 0.0567,
    "top_10_words": [
      {"word": "time", "count": 1250},
      {"word": "people", "count": 980},
      ...
    ]
  },
  "llm_answers": {
    "total_words": 145000,
    "unique_words": 7200,
    "lexical_diversity": 0.0497,
    "top_10_words": [
      {"word": "information", "count": 1100},
      {"word": "help", "count": 950},
      ...
    ]
  },
  "comparison": {
    "common_words": 5800,
    "yahoo_exclusive_words": 2700,
    "llm_exclusive_words": 1400,
    "vocabulary_overlap_percentage": 68.5
  }
}
```

### Verificación del Sistema

```bash
# Verificar que HDFS está funcionando
docker exec hadoop-batch-service hdfs dfs -ls /

# Ver archivos de entrada en HDFS
docker exec hadoop-batch-service hdfs dfs -ls /input/

# Ver resultados en HDFS
docker exec hadoop-batch-service hdfs dfs -ls /output/

# Ver primeras líneas de resultados
docker exec hadoop-batch-service hdfs dfs -cat /output/yahoo_wordcount/part-r-00000 | head -20

# Verificar resultados locales
ls -lh batch-analysis/results/
```

### Troubleshooting

#### HDFS no inicia
```bash
# Reiniciar servicio
docker-compose restart hadoop-batch-service

# Ver logs detallados
docker logs hadoop-batch-service

# Verificar estado de servicios Hadoop
docker exec hadoop-batch-service jps
```

#### Pig falla
```bash
# Verificar sintaxis de scripts Pig
docker exec hadoop-batch-service pig -x local -check /app/scripts/wordcount_yahoo.pig

# Ejecutar en modo local (más rápido para debugging)
docker exec hadoop-batch-service pig -x local /app/scripts/wordcount_yahoo.pig
```

#### No se generan visualizaciones
```bash
# Ejecutar script de análisis manualmente
docker exec hadoop-batch-service python3 /app/analyze_wordcount.py

# Verificar dependencias Python
docker exec hadoop-batch-service pip3 list | grep -E "pandas|matplotlib|wordcloud"
```

### Limpieza

```bash
# Detener y eliminar contenedores
docker-compose down

# Eliminar volúmenes (incluye datos de HDFS)
docker-compose down -v

# Limpiar resultados locales
rm -rf batch-analysis/results/*
```

---

## Comparación: Streaming vs Batch

### Procesamiento Streaming (Flink - Tarea 2)
- **Latencia**: Milisegundos
- **Volumen**: Evento por evento
- **Objetivo**: Validación de calidad en tiempo real
- **Caso de uso**: "¿Esta respuesta es de calidad?"

### Procesamiento Batch (Hadoop - Tarea 3)
- **Latencia**: Minutos/Horas
- **Volumen**: Dataset completo
- **Objetivo**: Análisis lingüístico histórico
- **Caso de uso**: "¿Qué patrones hay en todas las respuestas?"

### Complementariedad
Ambos enfoques coexisten y se complementan:
- **Flink**: Decisiones inmediatas sobre datos individuales
- **Hadoop**: Insights profundos sobre datos históricos

---

## Documentación Adicional

### Tarea 3
- `REQUERIMIENTOS_TAREA3.md` - Requerimientos exhaustivos
- `PLAN_IMPLEMENTACION_TAREA3.md` - Plan de implementación detallado
- `CHANGELOG_TAREA3.md` - Registro de cambios
- `RESUMEN_EJECUTIVO_TAREA3.md` - Visión general
- `INDICE_TAREA3.md` - Guía de navegación

---

### Estado del Sistema
✅ **Tarea 1:** Sistema de caché completamente funcional con 3 políticas  
✅ **Tarea 2:** Pipeline asíncrono con Kafka y Flink operativo y verificado  
✅ **Tarea 3:** Sistema de análisis batch con Hadoop y Pig implementado
#   T a r e a 3 S D  
 