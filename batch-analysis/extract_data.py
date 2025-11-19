#!/usr/bin/env python3
"""
Script de Extracción de Datos - Tarea 3
Extrae respuestas de Yahoo! y LLM desde PostgreSQL para análisis batch
"""

import os
import sys
import json
import psycopg2
from datetime import datetime

# Configuración de base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db/yahoo_db")

def parse_database_url(url):
    """Parsear URL de PostgreSQL"""
    # postgresql://user:password@host:port/database
    url = url.replace("postgresql://", "")
    auth, rest = url.split("@")
    user, password = auth.split(":")
    host_port, database = rest.split("/")
    
    if ":" in host_port:
        host, port = host_port.split(":")
    else:
        host = host_port
        port = "5432"
    
    return {
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": database
    }

def extract_data():
    """Extraer datos de PostgreSQL y guardar en archivos de texto"""
    
    print("=" * 70)
    print("EXTRACCIÓN DE DATOS PARA ANÁLISIS BATCH - TAREA 3")
    print("=" * 70)
    print()
    
    # Parsear configuración
    db_config = parse_database_url(DATABASE_URL)
    print(f"[1/6] Conectando a PostgreSQL...")
    print(f"      Host: {db_config['host']}")
    print(f"      Database: {db_config['database']}")
    
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        print("      ✓ Conexión exitosa")
        print()
        
        # Obtener estadísticas generales
        print("[2/6] Obteniendo estadísticas de la base de datos...")
        cursor.execute("SELECT COUNT(*) FROM responses;")
        total_records = cursor.fetchone()[0]
        print(f"      Total de registros: {total_records}")
        
        cursor.execute("SELECT COUNT(*) FROM responses WHERE original_answer IS NOT NULL AND original_answer != '';")
        yahoo_count = cursor.fetchone()[0]
        print(f"      Respuestas Yahoo! válidas: {yahoo_count}")
        
        cursor.execute("SELECT COUNT(*) FROM responses WHERE llm_answer IS NOT NULL AND llm_answer != '';")
        llm_count = cursor.fetchone()[0]
        print(f"      Respuestas LLM válidas: {llm_count}")
        print()

        # Extraer respuestas de Yahoo!
        print("[3/6] Extrayendo respuestas de Yahoo! Answers...")
        cursor.execute("""
            SELECT original_answer 
            FROM responses 
            WHERE original_answer IS NOT NULL 
              AND original_answer != ''
            ORDER BY id;
        """)
        
        yahoo_answers = []
        for row in cursor.fetchall():
            answer = row[0].strip()
            if answer:  # Filtrar respuestas vacías
                yahoo_answers.append(answer)
        
        print(f"      ✓ {len(yahoo_answers)} respuestas extraídas")
        
        # Guardar respuestas de Yahoo!
        output_dir = "/app/data"
        os.makedirs(output_dir, exist_ok=True)
        
        yahoo_file = os.path.join(output_dir, "yahoo_answers.txt")
        with open(yahoo_file, "w", encoding="utf-8") as f:
            for answer in yahoo_answers:
                # Limpiar saltos de línea internos para tener una respuesta por línea
                clean_answer = answer.replace("\n", " ").replace("\r", " ")
                f.write(clean_answer + "\n")
        
        print(f"      ✓ Guardado en: {yahoo_file}")
        print()
        
        # Extraer respuestas del LLM
        print("[4/6] Extrayendo respuestas del LLM (Gemini)...")
        cursor.execute("""
            SELECT llm_answer 
            FROM responses 
            WHERE llm_answer IS NOT NULL 
              AND llm_answer != ''
            ORDER BY id;
        """)
        
        llm_answers = []
        for row in cursor.fetchall():
            answer = row[0].strip()
            if answer:  # Filtrar respuestas vacías
                llm_answers.append(answer)
        
        print(f"      ✓ {len(llm_answers)} respuestas extraídas")
        
        # Guardar respuestas del LLM
        llm_file = os.path.join(output_dir, "llm_answers.txt")
        with open(llm_file, "w", encoding="utf-8") as f:
            for answer in llm_answers:
                # Limpiar saltos de línea internos
                clean_answer = answer.replace("\n", " ").replace("\r", " ")
                f.write(clean_answer + "\n")
        
        print(f"      ✓ Guardado en: {llm_file}")
        print()
        
        # Calcular estadísticas
        print("[5/6] Calculando estadísticas...")
        
        yahoo_words = sum(len(answer.split()) for answer in yahoo_answers)
        yahoo_chars = sum(len(answer) for answer in yahoo_answers)
        
        llm_words = sum(len(answer.split()) for answer in llm_answers)
        llm_chars = sum(len(answer) for answer in llm_answers)
        
        stats = {
            "extraction_date": datetime.now().isoformat(),
            "database": {
                "total_records": total_records,
                "yahoo_valid": yahoo_count,
                "llm_valid": llm_count
            },
            "yahoo_answers": {
                "count": len(yahoo_answers),
                "total_words": yahoo_words,
                "total_chars": yahoo_chars,
                "avg_words_per_answer": round(yahoo_words / len(yahoo_answers), 2) if yahoo_answers else 0,
                "avg_chars_per_answer": round(yahoo_chars / len(yahoo_answers), 2) if yahoo_answers else 0
            },
            "llm_answers": {
                "count": len(llm_answers),
                "total_words": llm_words,
                "total_chars": llm_chars,
                "avg_words_per_answer": round(llm_words / len(llm_answers), 2) if llm_answers else 0,
                "avg_chars_per_answer": round(llm_chars / len(llm_answers), 2) if llm_answers else 0
            }
        }
        
        # Guardar estadísticas
        stats_file = os.path.join(output_dir, "extraction_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        
        print(f"      Yahoo! Answers:")
        print(f"        - Total palabras: {yahoo_words:,}")
        print(f"        - Promedio palabras/respuesta: {stats['yahoo_answers']['avg_words_per_answer']}")
        print(f"      LLM Answers:")
        print(f"        - Total palabras: {llm_words:,}")
        print(f"        - Promedio palabras/respuesta: {stats['llm_answers']['avg_words_per_answer']}")
        print(f"      ✓ Estadísticas guardadas en: {stats_file}")
        print()
        
        # Cerrar conexión
        cursor.close()
        conn.close()
        
        print("[6/6] ✓ Extracción completada exitosamente")
        print()
        print("=" * 70)
        print("ARCHIVOS GENERADOS:")
        print(f"  - {yahoo_file}")
        print(f"  - {llm_file}")
        print(f"  - {stats_file}")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"✗ Error durante la extracción: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = extract_data()
    sys.exit(0 if success else 1)
