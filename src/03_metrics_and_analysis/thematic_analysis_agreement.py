import pandas as pd
from sklearn.metrics import cohen_kappa_score

# 1. Cargar los datos desde el archivo Excel
df = pd.read_excel("data/03_processed_metrics/coding_themed_analysis.xlsx", sheet_name="Hoja 1")

# 2. Filtrar solo las filas donde 'Considered for evaluation' es 'Yes'
df_eval = df[df['Considered for evaluation'].astype(str).str.strip() == 'Yes'].copy()

# Categorías a evaluar
categories = [
    "Substantial pedagogical modification",
    "Formatting struggle",
    "Delegate technical",
    "Adapted for special needs"
]

# Variable para almacenar el texto final
texto_resultados = "Resultados del Acuerdo Humano-IA:\n\n"

# 3. Iterar y calcular
for cat in categories:
    human_col = f"{cat} human"
    ai_col = f"{cat} AI"
    
    if human_col in df_eval.columns and ai_col in df_eval.columns:
        human_data = df_eval[human_col].astype(str).str.strip()
        ai_data = df_eval[ai_col].astype(str).str.strip()
        
        # Mapeo a formato binario
        human_mapped = human_data.map({'Yes': 1, 'No': 0})
        ai_mapped = ai_data.map({'1': 1, '0': 0, '1.0': 1, '0.0': 0})
        
        # Unir y limpiar nulos
        temp_df = pd.DataFrame({'human': human_mapped, 'ai': ai_mapped}).dropna()
        
        if len(temp_df) > 0:
            # Calcular métricas base
            kappa = cohen_kappa_score(temp_df['human'], temp_df['ai'])
            exact_agreement = (temp_df['human'] == temp_df['ai']).mean() * 100
            
            # Contar la cantidad de veces que se detectó la categoría ("Sí" = 1)
            # Como los datos están en 1 y 0, sumar la columna equivale a contar los "Sí"
            human_yes = int(temp_df['human'].sum())
            ai_yes = int(temp_df['ai'].sum())
            
            # Agregar al texto
            texto_resultados += f"Categoría: {cat}\n"
            texto_resultados += f"  - Kappa de Cohen: {round(kappa, 4)}\n"
            texto_resultados += f"  - Acuerdo Exacto: {round(exact_agreement, 2)}%\n"
            texto_resultados += f"  - 'Sí' detectados por Humano: {human_yes}\n"
            texto_resultados += f"  - 'Sí' detectados por IA: {ai_yes}\n"
            texto_resultados += f"  - N (Filas evaluadas): {len(temp_df)}\n\n"

# 4. Guardar los resultados en un archivo .txt
with open('agreement_results.txt', 'w', encoding='utf-8') as file:
    file.write(texto_resultados)

print("¡Listo! Se ha creado el archivo 'agreement_results.txt' con éxito.")