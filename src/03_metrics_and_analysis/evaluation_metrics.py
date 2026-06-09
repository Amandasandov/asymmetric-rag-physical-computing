import pandas as pd
import numpy as np
from scipy import stats
import scikit_posthocs as sp
import pingouin as pg
import sys
import re

def iqr(x):
    """Calculates the Interquartile Range"""
    return x.quantile(0.75) - x.quantile(0.25)

def calculate_icc_for_dataset(df_to_analyze, item_cols):
    """Helper function to calculate ICC(A,k) robustly on any given dataset."""
    icc_results = []
    for metric in item_cols:
        df_metric = df_to_analyze[['Target_ID', 'Evaluador_ID', metric]].copy()
        df_metric[metric] = pd.to_numeric(df_metric[metric], errors='coerce')
        
        # Aggregate any duplicate evaluator submissions
        df_metric = df_metric.groupby(['Target_ID', 'Evaluador_ID'])[metric].mean().reset_index()
        
        # Pivot to a wide matrix
        wide_df = df_metric.pivot(index='Target_ID', columns='Evaluador_ID', values=metric)
        
        # Impute any remaining NaNs with the activity's mean score to perfectly balance the matrix
        wide_df = wide_df.apply(lambda row: row.fillna(row.mean()), axis=1)
        
        # Melt back to long format
        balanced_df = wide_df.reset_index().melt(
            id_vars='Target_ID', 
            var_name='Evaluador_ID', 
            value_name=metric
        )
        
        try:
            icc = pg.intraclass_corr(
                data=balanced_df, 
                targets='Target_ID', 
                raters='Evaluador_ID', 
                ratings=metric
            )
            
            # Check for BOTH the new and old Pingouin naming conventions
            if 'ICC(A,k)' in icc['Type'].values:
                icc_row = icc[icc['Type'] == 'ICC(A,k)']
            elif 'ICC2k' in icc['Type'].values:
                icc_row = icc[icc['Type'] == 'ICC2k']
            else:
                icc_row = pd.DataFrame() # Empty if neither is found
                
            if not icc_row.empty:
                icc_value = icc_row['ICC'].values[0]
                icc_results.append({'Metric': metric, 'ICC(A,k)': round(icc_value, 3)})
            else:
                available = ", ".join(icc['Type'].astype(str).tolist())
                icc_results.append({'Metric': metric, 'ICC(A,k)': f"Missing! Found: {available}"})
                
        except Exception as e:
            icc_results.append({'Metric': metric, 'ICC(A,k)': f"Error: {e}"})
            
    return pd.DataFrame(icc_results)


def analyze_rubric_data(input_filepath, output_filepath, disagreement_threshold=0.90):
    original_stdout = sys.stdout
    
    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            sys.stdout = f
            
            print(f"--- Analysis Results for {input_filepath} ---\n")
            
            # 1. Load the data
            df = pd.read_excel(input_filepath)
            df.columns = df.columns.str.strip()

            # 2. Define the dimensions
            dimensions = {
                "Dim: Pedagogical Quality": [col for col in df.columns if "Pedagogical quality" in col],
                "Dim: Promotion of CT": [col for col in df.columns if "Promotion of CT" in col],
                "Dim: Technical Feasibility": [col for col in df.columns if "Tech feasibility" in col],
                "Dim: Creativity & Connection": [col for col in df.columns if "Creativity and connection" in col]
            }

            # 3. Clean string data and calculate primary Dimension scores
            for dim, cols in dimensions.items():
                if cols:
                    for col in cols:
                        # Ultra-robust numeric conversion
                        clean_str = df[col].astype(str).str.replace(',', '.').str.extract(r'([-+]?\d*\.?\d+)')[0]
                        df[col] = pd.to_numeric(clean_str, errors='coerce')
                    df[dim] = df[cols].mean(axis=1)

            item_cols = [col for cols in dimensions.values() for col in cols]
            all_metrics = list(dimensions.keys()) + item_cols

            # Clean identifiers for grouping
            df['Modalidad'] = df['Modalidad'].astype(str).str.strip()
            df['Actividad'] = df['Actividad'].astype(str).str.strip()
            df['Evaluador_ID'] = df['Evaluador_ID'].astype(str).str.strip()
            df['Target_ID'] = df['Modalidad'] + "_" + df['Actividad']

            # 4. INTER-RATER RELIABILITY (ICC) ON FULL DATASET (BEFORE OMISSIONS)
            # -------------------------------------------------------------------------
            print("="*80)
            print("1. INTER-RATER RELIABILITY (ICC(A,k) - Full Dataset Before Omissions)")
            print("Guidelines: <0.5 (Poor), 0.5-0.75 (Moderate), 0.75-0.9 (Good), >0.90 (Excellent)")
            print("="*80)
            
            icc_before_df = calculate_icc_for_dataset(df, item_cols)
            print(icc_before_df.to_string(index=False))
            print("\n")

            # 5. CALCULATE DISAGREEMENT & OMIT POLARIZED ACTIVITIES
            # -------------------------------------------------------------------------
            print("="*80)
            print(f"2. DATA FILTERING (Omission Threshold: SD >= {disagreement_threshold})")
            print("="*80)
            
            df_std = df.groupby(['Modalidad', 'Actividad'])[item_cols].std().reset_index()
            df_std['Overall_Disagreement_Score'] = df_std[item_cols].mean(axis=1).round(3)
            
            # Identify activities to omit
            omitted_activities = df_std[df_std['Overall_Disagreement_Score'] >= disagreement_threshold]['Actividad'].tolist()
            
            print(f"Activities Flagged for Omission ({len(omitted_activities)} total):")
            if omitted_activities:
                omitted_df = df_std[df_std['Actividad'].isin(omitted_activities)][['Modalidad', 'Actividad', 'Overall_Disagreement_Score']]
                print(omitted_df.sort_values(by='Overall_Disagreement_Score', ascending=False).to_string(index=False))
            else:
                print("None.")
            
            # Filter the main dataframe
            df_filtered = df[~df['Actividad'].isin(omitted_activities)].copy()
            print(f"\nRemaining valid activities for comparative analysis: {df_filtered['Actividad'].nunique()}")
            print("\n")

            # 6. INTER-RATER RELIABILITY (ICC) ON FILTERED DATASET (AFTER OMISSIONS)
            # -------------------------------------------------------------------------
            print("="*80)
            print("3. INTER-RATER RELIABILITY (ICC(A,k) - Filtered Dataset After Omissions)")
            print("Note: Due to variance restriction, scores may remain stable or shift slightly.")
            print("="*80)
            
            icc_after_df = calculate_icc_for_dataset(df_filtered, item_cols)
            print(icc_after_df.to_string(index=False))
            print("\n")

            # 7. Consolidate Filtered Data at the Activity Level
            df_activities = df_filtered.groupby(['Modalidad', 'Actividad'])[all_metrics].mean().reset_index()

            # 8. DESCRIPTIVE STATISTICS (Filtered Dataset)
            # -------------------------------------------------------------------------
            print("="*80)
            print("4. DESCRIPTIVE STATISTICS (Median and IQR by Modality - Cleaned Data)")
            print("="*80)
            
            desc_stats = df_activities.groupby('Modalidad')[all_metrics].agg(['median', iqr]).round(2)
            print(desc_stats.T.to_string())
            print("\n")

            # 9. INFERENTIAL STATISTICS (Filtered Dataset)
            # -------------------------------------------------------------------------
            print("="*80)
            print("5. INFERENTIAL STATISTICS (Kruskal-Wallis & Dunn's Post-Hoc - Cleaned Data)")
            print("="*80)
            
            for metric in all_metrics:
                groups = [group[metric].values for name, group in df_activities.groupby('Modalidad')]
                
                if len(groups) > 1:
                    stat, p_val = stats.kruskal(*groups)
                    print(f"\n--- Metric: {metric} ---")
                    print(f"Kruskal-Wallis H = {stat:.3f}, Global p-value = {p_val:.3f}")
                    
                    if p_val < 0.05:
                        print("  >> Global significance found. Pairwise p-values (Bonferroni adjusted):")
                        posthoc = sp.posthoc_dunn(df_activities, val_col=metric, group_col='Modalidad', p_adjust='bonferroni')
                        print(posthoc.round(3).to_string())
                    else:
                        print("  >> No statistically significant differences detected across modalities (p >= 0.05).")
                        
    finally:
        sys.stdout = original_stdout
        print(f"Analysis complete! Cleaned results successfully written to '{output_filepath}'.")

if __name__ == "__main__":
    input_file = "data/03_processed_metrics/Activities_evaluation_results.xslx"
    output_file = "evaluation_metrics_results.txt"
    
    analyze_rubric_data(input_file, output_file, disagreement_threshold=0.90)