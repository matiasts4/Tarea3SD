#!/usr/bin/env python3
"""
Script de Análisis y Visualización - Tarea 3
Procesa resultados de wordcount y genera visualizaciones comparativas
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime

# Configuración de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10

def load_wordcount(filepath):
    """Cargar resultados de wordcount desde archivo TSV"""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                word, count = parts
                try:
                    data.append({'word': word, 'count': int(count)})
                except ValueError:
                    continue
    return pd.DataFrame(data)

def generate_wordcloud(df, title, output_path, colormap='Blues'):
    """Generar nube de palabras"""
    # Crear diccionario de frecuencias
    word_freq = dict(zip(df['word'], df['count']))
    
    # Generar wordcloud
    wordcloud = WordCloud(
        width=1200,
        height=800,
        background_color='white',
        colormap=colormap,
        max_words=100,
        relative_scaling=0.5,
        min_font_size=10
    ).generate_from_frequencies(word_freq)
    
    # Crear figura
    plt.figure(figsize=(15, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=20, fontweight='bold', pad=20)
    plt.tight_layout(pad=0)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Wordcloud guardado: {output_path}")

def generate_bar_chart(yahoo_df, llm_df, output_path, top_n=20):
    """Generar gráfico de barras comparativo"""
    # Obtener top N palabras de cada conjunto
    yahoo_top = yahoo_df.head(top_n).copy()
    llm_top = llm_df.head(top_n).copy()
    
    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    # Yahoo! Answers
    ax1.barh(yahoo_top['word'][::-1], yahoo_top['count'][::-1], color='steelblue')
    ax1.set_xlabel('Frecuencia', fontsize=12)
    ax1.set_title(f'Top {top_n} Palabras - Yahoo! Answers', fontsize=14, fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # LLM Answers
    ax2.barh(llm_top['word'][::-1], llm_top['count'][::-1], color='coral')
    ax2.set_xlabel('Frecuencia', fontsize=12)
    ax2.set_title(f'Top {top_n} Palabras - LLM (Gemini)', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Gráfico de barras guardado: {output_path}")

def generate_comparison_table(yahoo_df, llm_df, output_path, top_n=50):
    """Generar tabla comparativa en formato CSV"""
    yahoo_top = yahoo_df.head(top_n).copy()
    llm_top = llm_df.head(top_n).copy()
    
    # Crear DataFrame comparativo
    comparison = pd.DataFrame({
        'Rank': range(1, top_n + 1),
        'Yahoo_Word': yahoo_top['word'].values,
        'Yahoo_Count': yahoo_top['count'].values,
        'LLM_Word': llm_top['word'].values,
        'LLM_Count': llm_top['count'].values
    })
    
    # Guardar como CSV
    comparison.to_csv(output_path, index=False, encoding='utf-8')
    print(f"  ✓ Tabla comparativa guardada: {output_path}")
    
    return comparison


def calculate_statistics(yahoo_df, llm_df):
    """Calcular estadísticas comparativas"""
    # Vocabulario único
    yahoo_unique = set(yahoo_df['word'])
    llm_unique = set(llm_df['word'])
    
    # Palabras comunes y exclusivas
    common_words = yahoo_unique & llm_unique
    yahoo_exclusive = yahoo_unique - llm_unique
    llm_exclusive = llm_unique - yahoo_unique
    
    # Totales
    yahoo_total_words = yahoo_df['count'].sum()
    llm_total_words = llm_df['count'].sum()
    
    # Diversidad léxica (vocabulario único / total palabras)
    yahoo_diversity = len(yahoo_unique) / yahoo_total_words
    llm_diversity = len(llm_unique) / llm_total_words
    
    stats = {
        'analysis_date': datetime.now().isoformat(),
        'yahoo_answers': {
            'total_words': int(yahoo_total_words),
            'unique_words': len(yahoo_unique),
            'lexical_diversity': round(yahoo_diversity, 4),
            'top_10_words': yahoo_df.head(10)[['word', 'count']].to_dict('records')
        },
        'llm_answers': {
            'total_words': int(llm_total_words),
            'unique_words': len(llm_unique),
            'lexical_diversity': round(llm_diversity, 4),
            'top_10_words': llm_df.head(10)[['word', 'count']].to_dict('records')
        },
        'comparison': {
            'common_words': len(common_words),
            'yahoo_exclusive_words': len(yahoo_exclusive),
            'llm_exclusive_words': len(llm_exclusive),
            'vocabulary_overlap_percentage': round(len(common_words) / len(yahoo_unique | llm_unique) * 100, 2)
        }
    }
    
    return stats

def generate_venn_diagram(yahoo_df, llm_df, output_path):
    """Generar diagrama de Venn de palabras comunes"""
    try:
        from matplotlib_venn import venn2
        
        yahoo_words = set(yahoo_df['word'])
        llm_words = set(llm_df['word'])
        
        plt.figure(figsize=(10, 8))
        venn = venn2([yahoo_words, llm_words], 
                     set_labels=('Yahoo! Answers', 'LLM (Gemini)'))
        
        # Personalizar colores
        venn.get_patch_by_id('10').set_color('steelblue')
        venn.get_patch_by_id('10').set_alpha(0.6)
        venn.get_patch_by_id('01').set_color('coral')
        venn.get_patch_by_id('01').set_alpha(0.6)
        venn.get_patch_by_id('11').set_color('mediumpurple')
        venn.get_patch_by_id('11').set_alpha(0.6)
        
        plt.title('Overlap de Vocabulario: Yahoo! vs LLM', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Diagrama de Venn guardado: {output_path}")
    except ImportError:
        print("  ⚠ matplotlib-venn no disponible, omitiendo diagrama de Venn")

def main():
    """Función principal de análisis"""
    print("=" * 70)
    print("ANÁLISIS Y VISUALIZACIÓN DE RESULTADOS - TAREA 3")
    print("=" * 70)
    print()
    
    # Directorios
    results_dir = "/app/results"
    
    # Cargar datos
    print("[1/7] Cargando resultados de wordcount...")
    yahoo_file = os.path.join(results_dir, "yahoo_wordcount.txt")
    llm_file = os.path.join(results_dir, "llm_wordcount.txt")
    
    yahoo_df = load_wordcount(yahoo_file)
    llm_df = load_wordcount(llm_file)
    
    print(f"      Yahoo! Answers: {len(yahoo_df)} palabras únicas")
    print(f"      LLM Answers: {len(llm_df)} palabras únicas")
    print()
    
    # Generar wordclouds
    print("[2/7] Generando nubes de palabras...")
    generate_wordcloud(
        yahoo_df, 
        'Vocabulario Yahoo! Answers',
        os.path.join(results_dir, 'wordcloud_yahoo.png'),
        colormap='Blues'
    )
    generate_wordcloud(
        llm_df,
        'Vocabulario LLM (Gemini)',
        os.path.join(results_dir, 'wordcloud_llm.png'),
        colormap='Reds'
    )
    print()
    
    # Generar gráfico de barras
    print("[3/7] Generando gráfico de barras comparativo...")
    generate_bar_chart(
        yahoo_df,
        llm_df,
        os.path.join(results_dir, 'top_words_comparison.png'),
        top_n=20
    )
    print()
    
    # Generar tabla comparativa
    print("[4/7] Generando tabla comparativa...")
    comparison_table = generate_comparison_table(
        yahoo_df,
        llm_df,
        os.path.join(results_dir, 'comparison_table_top50.csv'),
        top_n=50
    )
    print()
    
    # Calcular estadísticas
    print("[5/7] Calculando estadísticas...")
    stats = calculate_statistics(yahoo_df, llm_df)
    
    # Guardar estadísticas
    stats_file = os.path.join(results_dir, 'analysis_report.json')
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Reporte de análisis guardado: {stats_file}")
    print()
    
    # Generar diagrama de Venn
    print("[6/7] Generando diagrama de Venn...")
    generate_venn_diagram(
        yahoo_df,
        llm_df,
        os.path.join(results_dir, 'vocabulary_venn.png')
    )
    print()
    
    # Mostrar resumen
    print("[7/7] Resumen de resultados:")
    print()
    print("  YAHOO! ANSWERS:")
    print(f"    - Total palabras: {stats['yahoo_answers']['total_words']:,}")
    print(f"    - Vocabulario único: {stats['yahoo_answers']['unique_words']:,}")
    print(f"    - Diversidad léxica: {stats['yahoo_answers']['lexical_diversity']:.4f}")
    print(f"    - Top 3 palabras: {', '.join([w['word'] for w in stats['yahoo_answers']['top_10_words'][:3]])}")
    print()
    print("  LLM (GEMINI):")
    print(f"    - Total palabras: {stats['llm_answers']['total_words']:,}")
    print(f"    - Vocabulario único: {stats['llm_answers']['unique_words']:,}")
    print(f"    - Diversidad léxica: {stats['llm_answers']['lexical_diversity']:.4f}")
    print(f"    - Top 3 palabras: {', '.join([w['word'] for w in stats['llm_answers']['top_10_words'][:3]])}")
    print()
    print("  COMPARACIÓN:")
    print(f"    - Palabras comunes: {stats['comparison']['common_words']:,}")
    print(f"    - Palabras exclusivas Yahoo!: {stats['comparison']['yahoo_exclusive_words']:,}")
    print(f"    - Palabras exclusivas LLM: {stats['comparison']['llm_exclusive_words']:,}")
    print(f"    - Overlap de vocabulario: {stats['comparison']['vocabulary_overlap_percentage']}%")
    print()
    
    print("=" * 70)
    print("✓ ANÁLISIS COMPLETADO EXITOSAMENTE")
    print("=" * 70)
    print()
    print("ARCHIVOS GENERADOS:")
    print(f"  - {os.path.join(results_dir, 'wordcloud_yahoo.png')}")
    print(f"  - {os.path.join(results_dir, 'wordcloud_llm.png')}")
    print(f"  - {os.path.join(results_dir, 'top_words_comparison.png')}")
    print(f"  - {os.path.join(results_dir, 'vocabulary_venn.png')}")
    print(f"  - {os.path.join(results_dir, 'comparison_table_top50.csv')}")
    print(f"  - {os.path.join(results_dir, 'analysis_report.json')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
