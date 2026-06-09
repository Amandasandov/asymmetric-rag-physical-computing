import os
import sys
import re

def fix_json_structure(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Errore lettura {file_path}: {e}")
        return False

    # Troviamo l'ultima parentesi graffa chiusa '}'
    last_curly_index = content.rfind('}')

    if last_curly_index == -1:
        # Non c'è nemmeno una graffa chiusa? File probabilmente vuoto o corrotto in altro modo.
        return False

    # Prendiamo tutto ciò che c'è DOPO l'ultima graffa
    tail = content[last_curly_index+1:]

    # Contiamo quante parentesi quadre ci sono nella "coda"
    brackets_count = tail.count(']')

    # SE c'è più di una parentesi quadra, OPPURE c'è sporcizia ma nessuna quadra (caso raro),
    # OPPURE c'è una quadra ma è seguita da altra roba strana...
    #
    # La logica più sicura per te è:
    # Se dopo l'ultima '}' c'è qualcosa, noi vogliamo che quel qualcosa diventi SOLO un ']' (e magari un a capo).
    
    # Verifichiamo se la coda è GIA' corretta (ovvero: solo spazi e UNA sola quadra)
    # Regex: Cerca stringhe che contengono solo spazi e ESATTAMENTE una ']'
    if re.fullmatch(r'\s*\]\s*', tail):
        # È già perfetto (es: "  ]\n"), non tocchiamo nulla.
        return False

    # Se siamo qui, la coda è sbagliata (es: "]]", "] ]", "  ] \n ]").
    # Tagliamo il file alla graffa e aggiungiamo la quadra singola.
    
    new_content = content[:last_curly_index+1] + "]"
    
    # Salviamo
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main(start_dir="."):
    count = 0
    abs_path = os.path.abspath(start_dir)
    print(f"--- Riparazione avanzata (Clean Tail) in: {abs_path} ---")
    
    for root, dirs, files in os.walk(start_dir):
        for filename in files:
            if filename.lower().endswith(".json"):
                full_path = os.path.join(root, filename)
                
                if fix_json_structure(full_path):
                    print(f"[FIXED] {filename}")
                    count += 1

    print(f"\nOperazione completata. File corretti: {count}")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    main(target_dir)