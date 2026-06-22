import pandas as pd
import pingouin as pg
import os
import sys

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_archivo = os.path.join("data", "03_processed_metrics", "Activities_evaluation_results.xlsx")
ruta_salida = os.path.join(directorio_actual, "Activities_evaluation_results.txt")

df_rubrica = pd.read_excel(ruta_archivo)
columnas_rubrica = df_rubrica.columns[3:] 

df_rubrica['Global_Score'] = df_rubrica[columnas_rubrica].mean(axis=1)

dimensiones_dict = {
    'Pedagogical quality': [
        'Pedagogical quality (1. Relación Objetivos)', 
        'Pedagogical quality (8. Claridad Diseño)'
    ],
    'Promotion of CT': [
        'Promotion of CT (2. Abstracción/Algoritmos)', 
        'Promotion of CT (3. Descomposición/Patrones)'
    ],
    'Tech feasibility': [
        'Tech feasibility (4. Componentes Físicos)', 
        'Tech feasibility (7. Factibilidad/Recursos)'
    ],
    'Creativity and connection': [
        'Creativity and connection (6. Contextualización)', 
        'Creativity and connection (7. Creatividad/Escenario)'
    ]
}

for dim_name, cols in dimensiones_dict.items():
    df_rubrica[f'Score_{dim_name}'] = df_rubrica[cols].mean(axis=1)

# Variable central para agrupar (usada en Fiabilidad y TOST)
col_actividad = 'Actividad' 

original_stdout = sys.stdout
with open(ruta_salida, 'w', encoding='utf-8') as f:
    sys.stdout = f
    
    print("="*80)
    print("MÉTRICAS DE EVALUACIÓN (Rúbricas - Consistencia y TOST)")
    print("="*80)

    print("\n--- 4.4 CONSISTENCIA INTERNA ---")
    print("-> Alfa de Cronbach (Rúbrica Completa - 8 ítems):")
    for mod in df_rubrica['Modalidad'].unique():
        df_sub = df_rubrica[df_rubrica['Modalidad'] == mod][columnas_rubrica]
        alpha, ci = pg.cronbach_alpha(data=df_sub)
        print(f"   Modalidad '{mod}': Alfa = {alpha:.3f}")

    print("\n-> Fiabilidad Inter-ítem (Spearman-Brown) por Dimensión (k=2):")
    print("(Calculado sobre el promedio de calificaciones por Actividad en el dataset completo)")
    
    if col_actividad in df_rubrica.columns:
        df_agg_fiabilidad = df_rubrica.groupby(col_actividad)[columnas_rubrica].mean().reset_index()
        
        for dim_name, (item1, item2) in dimensiones_dict.items():
            if item1 in df_agg_fiabilidad.columns and item2 in df_agg_fiabilidad.columns:
                # Correlación cruda sobre datos agregados
                corr = pg.corr(df_agg_fiabilidad[item1], df_agg_fiabilidad[item2], method='spearman')
                r_val = corr['r'].values[0]
                
                # Corrección de Spearman-Brown para 2 ítems
                if r_val != -1: 
                    spearman_brown = (2 * r_val) / (1 + r_val)
                else:
                    spearman_brown = float('nan')
                    
                print(f"      {dim_name}: r_crudo = {r_val:.3f} | Spearman-Brown = {spearman_brown:.3f}")
    else:
        print(f"ADVERTENCIA: No se encontró la columna '{col_actividad}' para agrupar.")

    print("\n--- 4.2 TEST DE EQUIVALENCIA (TOST) - RAG vs Estandar ---")
    print("Margen de relevancia (SESOI): ±0.5 puntos")
    
    items_a_evaluar = ['Global_Score'] + [f'Score_{d}' for d in dimensiones_dict.keys()] + list(columnas_rubrica)
    
    if col_actividad in df_rubrica.columns:
        df_tost = df_rubrica.groupby(['Modalidad', col_actividad])[items_a_evaluar].mean().reset_index()
        print(f"(Nota: Datos colapsados por '{col_actividad}' para evitar pseudo-replicación. N={len(df_tost)})")
    else:
        print(f"ADVERTENCIA: No se encontró la columna '{col_actividad}'. TOST se correrá con pseudo-replicación.")
        df_tost = df_rubrica

    for item in items_a_evaluar:
        rag_scores = df_tost[df_tost['Modalidad'] == 'RAG'][item].dropna()
        std_scores = df_tost[df_tost['Modalidad'] == 'Estandar'][item].dropna()
        
        tost_res = pg.tost(x=rag_scores, y=std_scores, bound=0.5)
        p_cols = [c for c in tost_res.columns if 'pval' in c.lower() or 'p-val' in c.lower() or 'p_val' in c.lower()]
        
        if p_cols:
            p_val = tost_res[p_cols[0]].values[0]
            estado = "Equivalencia Confirmada" if p_val < 0.05 else "Inconcluso"
            print(f"{item[:45]:<45} | p-val TOST = {p_val:.4f} | {estado}")

sys.stdout = original_stdout
print(f"¡Listo! Resultados guardados en: {ruta_salida}")