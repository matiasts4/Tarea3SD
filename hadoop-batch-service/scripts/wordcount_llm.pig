-- Script Pig para Análisis de Vocabulario - LLM (Gemini) Answers
-- Tarea 3: Análisis Batch con Hadoop y Pig

-- Cargar datos de respuestas del LLM
raw_data = LOAD '/input/llm_answers.txt' AS (line:chararray);

-- Tokenizar: separar en palabras y convertir a minúsculas
words = FOREACH raw_data GENERATE FLATTEN(TOKENIZE(LOWER(line))) AS word;

-- Limpiar: eliminar puntuación y caracteres especiales
-- Mantener solo letras (a-z, incluyendo acentos)
clean_words = FOREACH words GENERATE REPLACE(word, '[^a-záéíóúñü]', '') AS word;

-- Filtrar palabras vacías y palabras muy cortas (menos de 3 caracteres)
filtered = FILTER clean_words BY SIZE(word) >= 3;

-- Cargar stopwords en español
stopwords_es = LOAD '/stopwords/stopwords_es.txt' AS (stopword:chararray);

-- Cargar stopwords en inglés
stopwords_en = LOAD '/stopwords/stopwords_en.txt' AS (stopword:chararray);

-- Unir ambas listas de stopwords
stopwords = UNION stopwords_es, stopwords_en;

-- Filtrar stopwords usando LEFT OUTER JOIN
words_with_stop = JOIN filtered BY word LEFT OUTER, stopwords BY stopword;
no_stopwords = FILTER words_with_stop BY stopwords::stopword IS NULL;
final_words = FOREACH no_stopwords GENERATE filtered::word AS word;

-- Agrupar por palabra
grouped = GROUP final_words BY word;

-- Contar frecuencia de cada palabra
wordcount = FOREACH grouped GENERATE 
    group AS word, 
    COUNT(final_words) AS count;

-- Ordenar por frecuencia (descendente)
sorted = ORDER wordcount BY count DESC;

-- Guardar resultados en HDFS
STORE sorted INTO '/output/llm_wordcount' USING PigStorage('\t');
