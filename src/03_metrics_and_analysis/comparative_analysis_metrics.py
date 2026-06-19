import pandas as pd
import numpy as np
from scipy.stats import friedmanchisquare, wilcoxon, iqr
from statsmodels.stats.multitest import multipletests 

# 1. Cargar datos
df_comp = pd.read_excel('data/03_processed_metrics/Comparative_questionnaire_results.xlsx')

preguntas_comp = df_comp.iloc[1:8, 0].tolist()
user_cols = df_comp.columns[1:]

def clean_to_numeric(series):
    return pd.to_numeric(series, errors='coerce')

# Extraer y limpiar bloques de datos
hh_data = df_comp.iloc[1:8][user_cols].apply(clean_to_numeric, axis=1).values
normal_data = df_comp.iloc[10:17][user_cols].apply(clean_to_numeric, axis=1).values
rag_data = df_comp.iloc[19:26][user_cols].apply(clean_to_numeric, axis=1).values

# Diccionario de traducciones para el gráfico en inglés
translations_comp = {
    '¿Qué tan útil fue esta modalidad para generar una actividad contextualizada a los intereses de los estudiantes?': 'Usefulness for\ncontextualized activities',
    '¿Qué tan satisfecho/a quedó con la calidad pedagógica de la actividad final generada?': 'Satisfaction with\npedagogical quality',
    '¿Qué tan fácil fue integrar los recursos de computación física (ej. Protobject) en el diseño de la actividad?': 'Ease of integrating\nphysical computing',
    'El proceso de co-creación (con su colega o la IA) fue fluido y productivo': 'Fluidity and productivity\nof co-creation',
    'Sentí que esta modalidad me ayudó a superar bloqueos creativos durante el diseño.': 'Help in overcoming\ncreative blocks',
    'Considero que el tiempo invertido en esta modalidad fue eficiente para el resultado obtenido.': 'Efficiency of\ntime invested',
    '¿Qué tan probable es que use esta modalidad en su práctica docente futura?': 'Probability of future\nuse in teaching'
}

resultados_estadisticos_comp = []
datos_grafico_comp = []

for idx, pregunta in enumerate(preguntas_comp):
    hh = hh_data[idx]
    norm = normal_data[idx]
    rag = rag_data[idx]
    
    # Máscara para casos completos (exigencia de Friedman)
    mask = ~np.isnan(hh) & ~np.isnan(norm) & ~np.isnan(rag)
    hh_clean = hh[mask]
    norm_clean = norm[mask]
    rag_clean = rag[mask]
    N = len(hh_clean)
    k = 3 # Número de modalidades
    
    # Obtener traducción para el gráfico
    q_en = translations_comp.get(pregunta, f"Question {idx+1}")
    
    for val in hh_clean: datos_grafico_comp.append({'Question': q_en, 'Modality': 'Human-Human', 'Score': val})
    for val in norm_clean: datos_grafico_comp.append({'Question': q_en, 'Modality': 'Standard AI', 'Score': val})
    for val in rag_clean: datos_grafico_comp.append({'Question': q_en, 'Modality': 'Specialized AI (RAG)', 'Score': val})
    
    try:
        # Prueba ómnibus y Tamaño de Efecto (Kendall's W)
        stat_f, p_f = friedmanchisquare(hh_clean, norm_clean, rag_clean)
        kendall_w = stat_f / (N * (k - 1))
        
        # Pruebas Post-Hoc de Wilcoxon (P-valores crudos)
        stat_hh_norm, p_hh_norm = wilcoxon(hh_clean, norm_clean)
        stat_norm_rag, p_norm_rag = wilcoxon(norm_clean, rag_clean)
        stat_hh_rag, p_hh_rag = wilcoxon(hh_clean, rag_clean)
        
        # --- CORRECCIÓN DE BONFERRONI ---
        p_values = [p_hh_norm, p_norm_rag, p_hh_rag]
        reject, p_values_adj, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')
        
        p_hh_norm_adj = p_values_adj[0]
        p_norm_rag_adj = p_values_adj[1]
        p_hh_rag_adj = p_values_adj[2]
        
    except ValueError:
        stat_f, p_f, kendall_w = np.nan, np.nan, np.nan
        stat_hh_norm, p_hh_norm = np.nan, np.nan
        stat_norm_rag, p_norm_rag = np.nan, np.nan
        stat_hh_rag, p_hh_rag = np.nan, np.nan
        p_hh_norm_adj, p_norm_rag_adj, p_hh_rag_adj = np.nan, np.nan, np.nan
        
    resultados_estadisticos_comp.append({
        'Question (ID)': f'P{idx+1}',
        'Question Text': pregunta,
        'HH Mean (SD)': f"{np.mean(hh_clean):.2f} ({np.std(hh_clean, ddof=1):.2f})",
        'Std Mean (SD)': f"{np.mean(norm_clean):.2f} ({np.std(norm_clean, ddof=1):.2f})",
        'RAG Mean (SD)': f"{np.mean(rag_clean):.2f} ({np.std(rag_clean, ddof=1):.2f})",
        'HH Median (IQR)': f"{np.median(hh_clean):.2f} ({iqr(hh_clean):.2f})",
        'Std Median (IQR)': f"{np.median(norm_clean):.2f} ({iqr(norm_clean):.2f})",
        'RAG Median (IQR)': f"{np.median(rag_clean):.2f} ({iqr(rag_clean):.2f})",
        'Friedman X2': stat_f,
        'Friedman p-val': p_f,
        'Kendall W': kendall_w,
        'Wilcoxon H-H vs Std (W, p_adj)': f"W={stat_hh_norm}, p_adj={p_hh_norm_adj:.3f}" if not np.isnan(p_hh_norm_adj) else "NaN",
        'Wilcoxon Std vs RAG (W, p_adj)': f"W={stat_norm_rag}, p_adj={p_norm_rag_adj:.3f}" if not np.isnan(p_norm_rag_adj) else "NaN",
        'Wilcoxon H-H vs RAG (W, p_adj)': f"W={stat_hh_rag}, p_adj={p_hh_rag_adj:.3f}" if not np.isnan(p_hh_rag_adj) else "NaN"
    })

df_res = pd.DataFrame(resultados_estadisticos_comp)
df_res.to_csv('comparative_metrics.csv', index=False)