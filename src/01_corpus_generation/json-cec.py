import os
import json
import sys

# Codici colori ANSI (potrebbero non funzionare su prompt DOS molto vecchi, ma non rompono lo script)
class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_json_files(start_dir="."):
    # Ottieni il percorso assoluto per chiarezza
    abs_path = os.path.abspath(start_dir)
    print("--- Avvio scansione JSON in: '{}' ---".format(abs_path))
    print("")

    invalid_count = 0
    valid_count = 0
    total_files = 0

    for root, dirs, files in os.walk(start_dir):
        for filename in files:
            if filename.lower().endswith(".json"):
                total_files += 1
                full_path = os.path.join(root, filename)

                try:
                    # In Python 2 open() non accetta encoding, ma in Python 3 sì.
                    # Usiamo un approccio base per la compatibilità massima.
                    with open(full_path, 'r') as f:
                        json.load(f)
                    
                    # Se vuoi vedere i file OK, togli il commento sotto:
                    # print("[OK] {}".format(filename))
                    valid_count += 1

                # Catturiamo ValueError perché nelle versioni vecchie di Python
                # gli errori JSON erano semplici ValueError.
                # Nelle versioni nuove, JSONDecodeError è figlio di ValueError, quindi viene catturato lo stesso.
                except ValueError as e:
                    invalid_count += 1
                    
                    # Proviamo a recuperare riga e colonna se disponibili (Python 3.5+)
                    lineno = getattr(e, 'lineno', '?')
                    colno = getattr(e, 'colno', '?')
                    msg = getattr(e, 'msg', str(e))

                    # Stampa in rosso
                    print("{}[INVALIDO] {}{}".format(Colors.FAIL, full_path, Colors.ENDC))
                    
                    # Stampa dettagli errore
                    if lineno != '?':
                        print("    |--> Errore riga {}, colonna {}: {}".format(lineno, colno, msg))
                    else:
                        # Fallback per versioni vecchie che non danno riga/colonna
                        print("    |--> Errore: {}".format(msg))

                except Exception as e:
                    # Altri errori (es. permessi, file system)
                    invalid_count += 1
                    print("{}[ERRORE GENERICO] {}{}".format(Colors.FAIL, full_path, Colors.ENDC))
                    print("    |--> {}".format(str(e)))

    print("\n--- Riepilogo ---")
    print("Totale file: {}".format(total_files))
    print("Validi: {}".format(valid_count))
    
    if invalid_count > 0:
        print("{}Invalidi: {}{}".format(Colors.FAIL, invalid_count, Colors.ENDC))
    else:
        print("{}Invalidi: 0 (Tutto perfetto!){}".format(Colors.OKGREEN, Colors.ENDC))

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    check_json_files(target_dir)