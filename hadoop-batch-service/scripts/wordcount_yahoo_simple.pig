-- Script Pig para Análisis de Vocabulario - Yahoo! Answers (Versión Simplificada)
-- Tarea 3: Análisis Batch con Hadoop y Pig

-- Cargar datos de respuestas de Yahoo!
raw_data = LOAD '/input/yahoo_answers.txt' AS (line:chararray);

-- Tokenizar: separar en palabras y convertir a minúsculas
words = FOREACH raw_data GENERATE FLATTEN(TOKENIZE(LOWER(line))) AS word;

-- Limpiar: eliminar puntuación y caracteres especiales
-- Mantener solo letras (a-z, incluyendo acentos)
clean_words = FOREACH words GENERATE REPLACE(word, '[^a-záéíóúñü]', '') AS word;

-- Filtrar palabras vacías y palabras muy cortas (menos de 3 caracteres)
filtered = FILTER clean_words BY SIZE(word) >= 3;

-- Agrupar por palabra
grouped = GROUP filtered BY word;

-- Contar frecuencia de cada palabra
wordcount = FOREACH grouped GENERATE 
    group AS word, 
    COUNT(filtered) AS count;

-- Ordenar por frecuencia (descendente)
sorted = ORDER wordcount BY count DESC;

-- Guardar resultados en HDFS
STORE sorted INTO '/output/yahoo_wordcount' USING PigStorage('\t');
