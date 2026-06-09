import os
import json
import shutil
import sys

def get_expected_components(filename):
    """
    Estrae i componenti attesi dal nome del file.
    Es: "Compass-Inclination-Musical Drum.json" 
    -> set({"Compass", "Inclination", "Musical Drum"})
    """
    name_without_ext = os.path.splitext(filename)[0]
    # Dividiamo per '-' e rimuoviamo spazi extra
    components = [c.strip() for c in name_without_ext.split('-')]
    return set(components)

def is_file_semantically_valid(file_path, expected_components):
    """
    Controlla se TUTTI gli oggetti nel JSON contengono TUTTI i componenti attesi.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            print(f"   [!] {os.path.basename(file_path)} non è una lista JSON.")
            return False

        # Controlliamo ogni idea generata dentro il file
        for index, item in enumerate(data):
            used_list = item.get("componentUsed", [])
            used_set = set(used_list)
            
            # Verifichiamo se i componenti attesi sono un sottoinsieme di quelli usati.
            # (Ovvero: devono esserci TUTTI quelli del nome del file, 
            # se ce ne sono di più va bene, ma se ne mancano no).
            if not expected_components.issubset(used_set):
                missing = expected_components - used_set
                # print(f"      -> Idea #{index+1} manca di: {missing}") # Decommenta per debug dettagliato
                return False
                
        return True

    except Exception as e:
        print(f"   [!] Errore lettura {os.path.basename(file_path)}: {e}")
        return False

def main(target_dir="."):
    abs_target_dir = os.path.abspath(target_dir)
    corrupted_dir = os.path.join(abs_target_dir, "corrotti")
    
    # Crea la cartella corrotti se non esiste
    if not os.path.exists(corrupted_dir):
        os.makedirs(corrupted_dir)

    print(f"--- Controllo completezza componenti in: {abs_target_dir} ---")
    print(f"--- I file incompleti verranno spostati in: {corrupted_dir} ---\n")

    moved_count = 0
    checked_count = 0

    for root, dirs, files in os.walk(abs_target_dir):
        # Evitiamo di scansionare la cartella "corrotti" stessa se è una sottocartella
        if "corrotti" in root:
            continue

        for filename in files:
            if filename.lower().endswith(".json"):
                full_path = os.path.join(root, filename)
                checked_count += 1

                # 1. Capiamo cosa ci aspettiamo dal nome del file
                expected_set = get_expected_components(filename)
                
                # 2. Controlliamo se il contenuto rispetta il nome
                is_valid = is_file_semantically_valid(full_path, expected_set)

                if not is_valid:
                    print(f"[SPOSTO] {filename} -> Manca di componenti.")
                    
                    # Costruiamo il percorso di destinazione
                    dest_path = os.path.join(corrupted_dir, filename)
                    
                    # Spostiamo il file
                    try:
                        shutil.move(full_path, dest_path)
                        moved_count += 1
                    except Exception as e:
                        print(f"   [ERRORE SPOSTAMENTO] {e}")

    print(f"\n--- Riepilogo ---")
    print(f"File controllati: {checked_count}")
    print(f"File incompleti spostati: {moved_count}")

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    main(folder)