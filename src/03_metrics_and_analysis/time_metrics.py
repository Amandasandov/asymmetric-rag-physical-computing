import pandas as pd

# 1. Load the data
file_path = "data/raw_metrics/Generation_time_activities.xslx"
df = pd.read_excel(file_path)

df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
df = df.dropna(subset=['Time'])

# 2. Map the Modality names to the expected Methodology names
name_mapping = {
    'Standard': 'Standard AI',
    'RAG': 'RAG AI',
    'Human': 'Human'
}
df['Methodology'] = df['Modality'].map(name_mapping).fillna(df['Modality'])

# 3. Calculate the metrics (N, Mean, SD, Median, Min, Max)
summary_stats = df.groupby('Methodology')['Time'].agg(
    N='count',
    Mean='mean',
    SD='std',
    Median='median',
    Min='min',
    Max='max'
).reset_index()

# 4. Sort the rows to match the specific order: Standard AI, RAG AI, Human
order = ['Standard AI', 'RAG AI', 'Human']
summary_stats['Methodology'] = pd.Categorical(summary_stats['Methodology'], categories=order, ordered=True)
summary_stats = summary_stats.sort_values('Methodology')

# 5. Format the text output
text_output = f"{'Methodology':<12} | {'N':<2} | {'Mean':<5} | {'SD':<4} | {'Median':<6} | {'Min':<3} | {'Max':<3}\n"
text_output += "-" * 57 + "\n"

for index, row in summary_stats.iterrows():
    method = f"{row['Methodology']:<12}"
    n = f"{int(row['N']):<2}"
    mean = f"{row['Mean']:.2f}"
    sd = f"{row['SD']:.2f}"
    median = f"{row['Median']:.2f}"
    min_val = f"{int(row['Min']):<3}"
    max_val = f"{int(row['Max']):<3}"
    
    text_output += f"{method} | {n} | {mean} | {sd} | {median} | {min_val} | {max_val}\n"

text_output += "-" * 57 + "\n"
text_output += "N: Sample Size. SD: Standard Deviation. Min/Max: Minimum and Maximum time recorded in minutes.\n"

# 6. Save to txt file
output_path = "generation_metrics.txt"
with open(output_path, "w") as f:
    f.write(text_output)

print(f"Results successfully saved to {output_path}")