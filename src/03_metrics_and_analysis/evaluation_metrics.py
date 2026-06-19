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

    print("\n-> Correlación Inter-ítem (Spearman) por Dimensión (k=2):")
    for mod in df_rubrica['Modalidad'].unique():
        print(f"\n   [ Modalidad: {mod} ]")
        df_sub = df_rubrica[df_rubrica['Modalidad'] == mod]
        
        for dim_name, (item1, item2) in dimensiones_dict.items():
            if item1 in df_sub.columns and item2 in df_sub.columns:
                corr = pg.corr(df_sub[item1], df_sub[item2], method='spearman')
                r_val = corr['r'].values[0]
                
                # BÚSQUEDA ROBUSTA DEL P-VALOR
                # Buscamos cualquier columna que contenga la letra 'p' y que NO sea 'r' o 'n'
                p_col_candidates = [c for c in corr.columns if 'p' in c.lower() and c.lower() not in ['r', 'n', 'ci95%']]
                
                if p_col_candidates:
                    p_col = p_col_candidates[0]
                    pval = corr[p_col].values[0]
                    print(f"      {dim_name}: r = {r_val:.3f} (p={pval:.3f})")
                else:
                    # Si falla, imprimimos las columnas disponibles para depurar
                    print(f"      {dim_name}: r = {r_val:.3f} (No se pudo extraer p-valor, cols: {list(corr.columns)})")

    print("\n--- 4.2 TEST DE EQUIVALENCIA (TOST) - RAG vs Estandar ---")
    print("Margen de relevancia (SESOI): ±0.5 puntos")
    
    items_a_evaluar = ['Global_Score'] + [f'Score_{d}' for d in dimensiones_dict.keys()] + list(columnas_rubrica)
    
    for item in items_a_evaluar:
        rag_scores = df_rubrica[df_rubrica['Modalidad'] == 'RAG'][item].dropna()
        std_scores = df_rubrica[df_rubrica['Modalidad'] == 'Estandar'][item].dropna()
        
        tost_res = pg.tost(x=rag_scores, y=std_scores, bound=0.5)
        p_cols = [c for c in tost_res.columns if 'pval' in c.lower() or 'p-val' in c.lower() or 'p_val' in c.lower()]
        
        if p_cols:
            p_val = tost_res[p_cols[0]].values[0]
            estado = "Equivalencia Confirmada" if p_val < 0.05 else "Inconcluso"
            print(f"{item[:45]:<45} | p-val TOST = {p_val:.4f} | {estado}")

sys.stdout = original_stdout
print(f"¡Listo! Resultados guardados en: {ruta_salida}")