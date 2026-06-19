import pandas as pd
import pingouin as pg
import os
import sys

directorio_actual = os.path.dirname(os.path.abspath(__file__))
ruta_archivo = os.path.join("data", "03_processed_metrics", "Generation_time_activities.xlsx")
ruta_salida = os.path.join(directorio_actual, "Time_analysis_results.txt")

df_tiempo = pd.read_excel(ruta_archivo)
df_tiempo['Modality'] = df_tiempo['Modality'].replace({'Standard': 'Estandar'})

original_stdout = sys.stdout
with open(ruta_salida, 'w', encoding='utf-8') as f:
    sys.stdout = f
    
    print("="*80)
    print("ANÁLISIS DE TIEMPOS DE GENERACIÓN")
    print("="*80)
    print("[NOTA METODOLÓGICA]: Los tiempos de 'Human' están censurados a la derecha")
    print("a los 26 min (límite del round). Esto subestima la verdadera ventaja de la IA.\n")
    
    print("--- Estadísticas Descriptivas ---")
    print(df_tiempo.groupby('Modality')['Time'].describe().round(2), "\n")

    kw_res = pg.kruskal(data=df_tiempo, dv='Time', between='Modality')
    print("--- 4.3 Kruskal-Wallis Global ---")
    print(kw_res, "\n")

    p_kw_col = [c for c in kw_res.columns if 'p' in c.lower() and 'unc' in c.lower()][0]

    if kw_res[p_kw_col].values[0] < 0.05:
        print("--- Análisis Post-Hoc (Mann-Whitney U) ---")
        comparaciones = [('Human', 'Estandar'), ('Human', 'RAG'), ('Estandar', 'RAG')]
        for g1, g2 in comparaciones:
            t1 = df_tiempo[df_tiempo['Modality'] == g1]['Time'].dropna()
            t2 = df_tiempo[df_tiempo['Modality'] == g2]['Time'].dropna()
            
            mwu = pg.mwu(t1, t2)
            
            # Extracción directa del tamaño de efecto no paramétrico (Rank-Biserial Correlation) devuelto por mwu
            rbc = mwu['RBC'].values[0]
            
            print(f"\n{g1} vs {g2}:")
            print(mwu.to_string(index=False))
            print(f"Tamaño de Efecto (Rank-Biserial Correlation): {rbc:.3f}")

    print("\n" + "-"*80)
    print("--- 4.2 TEST DE EQUIVALENCIA (TOST) - RAG vs Estandar ---")
    print("Margen de relevancia (SESOI): ±2.0 minutos\n")
    
    t1_rag = df_tiempo[df_tiempo['Modality'] == 'RAG']['Time'].dropna()
    t2_std = df_tiempo[df_tiempo['Modality'] == 'Estandar']['Time'].dropna()
    
    tost_time = pg.tost(x=t1_rag, y=t2_std, bound=2.0)
    print(tost_time.to_string(index=False))
    
    p_cols = [c for c in tost_time.columns if 'pval' in c.lower() or 'p-val' in c.lower() or 'p_val' in c.lower()]
    if p_cols:
        p_tost = tost_time[p_cols[0]].values[0]
        estado = "Equivalencia Confirmada" if p_tost < 0.05 else "Inconcluso"
        print(f"\n-> Conclusión: p-val = {p_tost:.4f} | {estado}")

sys.stdout = original_stdout
print(f"¡Listo! Resultados guardados en: {ruta_salida}")