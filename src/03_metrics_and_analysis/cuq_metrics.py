import pandas as pd
import pingouin as pg
import os
import sys
import warnings

warnings.filterwarnings('ignore')

directorio_actual = os.path.dirname(os.path.abspath(__file__))
archivo_std = os.path.join("data", "03_processed_metrics", "CUQ -  Results and calculation tool - standard.xlsx")
archivo_rag = os.path.join("data", "03_processed_metrics", "CUQ - Results and calculation tool - rag.xlsx")
ruta_salida = os.path.join(directorio_actual, "CUQ_analysis_results.txt")

def cargar_cuq(ruta, modalidad):
    df = pd.read_excel(ruta, sheet_name="Data", skiprows=4)
    df.columns = df.columns.astype(str)
    cols_preguntas = [str(i) for i in range(1, 17)]
    df = df.dropna(subset=cols_preguntas)
    df[cols_preguntas] = df[cols_preguntas].apply(pd.to_numeric, errors='coerce')
    df['CUQ Score'] = pd.to_numeric(df['CUQ Score'], errors='coerce')
    df['Modality'] = modalidad
    return df

df_cuq_std = cargar_cuq(archivo_std, "Estandar")
df_cuq_rag = cargar_cuq(archivo_rag, "RAG")
df_cuq = pd.concat([df_cuq_std, df_cuq_rag], ignore_index=True)

original_stdout = sys.stdout
with open(ruta_salida, 'w', encoding='utf-8') as f:
    sys.stdout = f
    
    print("="*80)
    print("ANÁLISIS DE CUQ (Consistencia Interna y Equivalencia)")
    print("="*80)

    print("\n--- 4.4 CONSISTENCIA INTERNA (Alfa de Cronbach) ---")
    cols_preguntas = [str(i) for i in range(1, 17)]

    cols_negativas = ['2', '4', '6', '8', '10', '12', '14', '16'] 
    
    for mod in ['Estandar', 'RAG']:
        df_sub = df_cuq[df_cuq['Modality'] == mod][cols_preguntas].copy()
        
        for col in cols_negativas:
            if col in df_sub.columns:
                df_sub[col] = 6 - df_sub[col]
                
        alpha, ci = pg.cronbach_alpha(data=df_sub)
        print(f"Modalidad '{mod}': Alfa = {alpha:.3f} (95% CI: {ci})")

    print("\n--- 4.2 TEST DE EQUIVALENCIA (TOST) ---")
    print("Margen de relevancia (SESOI): ±10 puntos en la escala 0-100 del CUQ")
    print("[NOTA]: Se busca rechazar hipótesis de que la diferencia es mayor a 10 puntos.\n")
    
    scores_rag = df_cuq[df_cuq['Modality'] == 'RAG']['CUQ Score'].dropna()
    scores_std = df_cuq[df_cuq['Modality'] == 'Estandar']['CUQ Score'].dropna()
    
    tost_cuq = pg.tost(x=scores_rag, y=scores_std, bound=10.0)
    print(tost_cuq.to_string(index=False))
    
    p_cols = [c for c in tost_cuq.columns if 'pval' in c.lower() or 'p-val' in c.lower() or 'p_val' in c.lower()]
    if p_cols:
        p_val_tost = tost_cuq[p_cols[0]].values[0]
        estado = "Equivalencia Confirmada" if p_val_tost < 0.05 else "Inconcluso"
        print(f"\n-> Conclusión: p-val TOST = {p_val_tost:.4f} | {estado}")

sys.stdout = original_stdout
print(f"¡Listo! Resultados guardados en: {ruta_salida}")