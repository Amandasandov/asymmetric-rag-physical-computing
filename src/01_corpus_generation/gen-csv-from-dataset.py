import os
import json
import csv
import sys

# ==========================================
# CONFIGURAZIONE CAMPI (MAPPING)
# ==========================================
# Qui puoi definire quali chiavi del JSON vuoi estrarre e come vuoi chiamarle nel CSV.
# Sintassi: "ChiaveNelJSON": "NomeColonnaNelCSV"
# Commenta o decommenta le linee per includere/escludere i campi.

KEY_MAPPING = {
    # --- Chiavi richieste ---
    "transformedIdeaTitle": "idea",
    "transformedIdeaDescription": "descripcion",
    "minAge": "edad minima",
    "maxAge": "edad maxima",
    "difficultyLevel": "nivel dificuldad",

    # --- Altre chiavi disponibili (decommenta per usare) ---
    # "originalIdeaTitle": "titolo originale",
    # "originalIdeaDescription": "descrizione originale",
    # "algorithmUsed": "algoritmo",
    "componentUsed": "componentes", # Nota: questo è una lista nel JSON
}

# ==========================================
# LOGICA DEL PROGRAMMA
# ==========================================

def get_subdirectories(directory):
    """Restituisce una lista di sottocartelle nella directory data."""
    return [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]

def process_folder(folder_name):
    """Legge i JSON in una cartella e prepara i dati per il CSV."""
    folder_path = os.path.join(os.getcwd(), folder_name)
    all_rows = []

    # Trova tutti i file .json nella sottocartella
    files = [f for f in os.listdir(folder_path) if f.lower().endswith('.json')]
    
    if not files:
        print(f"⚠️  Nessun file JSON trovato nella cartella: {folder_name}")
        return None

    print(f"📂 Elaborazione cartella: {folder_name} ({len(files)} file trovati)...")

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            # FERMA IL LAVORO SE IL JSON NON È VALIDO
            print("\n" + "="*50)
            print(f"❌ ERRORE FATALE: JSON non valido trovato!")
            print(f"📁 File: {file_path}")
            print(f"💬 Errore: {e}")
            print("="*50 + "\n")
            sys.exit(1) # Esce dal programma con codice di errore
        
        # Gestisce il caso in cui il JSON sia una lista o un singolo oggetto
        if isinstance(data, list):
            items = data
        else:
            items = [data]

        # Estrazione dei dati in base alla configurazione
        for item in items:
            row = {}
            for json_key, csv_header in KEY_MAPPING.items():
                # Prende il valore, se non esiste mette stringa vuota
                value = item.get(json_key, "")
                
                # Se il valore è una lista (es. componentUsed), la unisce in una stringa
                if isinstance(value, list):
                    value = ", ".join(value)
                
                row[csv_header] = value
            all_rows.append(row)

    return all_rows

def write_csv(folder_name, rows):
    """Scrive i dati nel file CSV nella directory corrente."""
    if not rows:
        return

    csv_filename = f"{folder_name}.csv"
    
    # Recupera i nomi delle colonne dalla configurazione
    fieldnames = list(KEY_MAPPING.values())

    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"✅ Generato: {csv_filename} ({len(rows)} righe)")
    except IOError as e:
        print(f"❌ Errore nella scrittura del file {csv_filename}: {e}")

def main():
    current_dir = os.getcwd()
    subdirs = get_subdirectories(current_dir)

    if not subdirs:
        print("Nessuna sottocartella trovata nella directory corrente.")
        return

    for subdir in subdirs:
        # Ignora cartelle nascoste (es. .git) o output script
        if subdir.startswith('.'): 
            continue
            
        rows = process_folder(subdir)
        if rows:
            write_csv(subdir, rows)

if __name__ == "__main__":
    main()