import re
import shutil
from pathlib import Path

# Configurazione
INPUT_DIR = Path("src")
OUTPUT_DIR = Path("_site")
INCLUDE_DIR = Path("include")
LINGUE = ["it", "en", "fr", "de", "es"]  # Lingue supportate

ESTENSIONI_PROCESSABILI = {'.html'}  #PER FUTURE ESTENSIONI ?!

def is_processabile(filepath: Path) -> bool:
    return filepath.suffix.lower() in ESTENSIONI_PROCESSABILI 

def pulisci_cartella_output():
    """Cancella ricorsivamente la cartella output se esiste, poi la ricrea."""
    if OUTPUT_DIR.exists():
        try:
            shutil.rmtree(OUTPUT_DIR)  # Cancella tutto ricorsivamente
        except Exception as e:
            print(f"Errore nella pulizia: {e}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # Ricrea la cartella

def is_directly_in_xx(path: Path) -> bool:
    """
    Verifica se il percorso è direttamente dentro src/xx/
    Restituisce True solo per:
    - src/xx/miadir
    - src/xx/
    """
    try:
        parts = path.relative_to(INPUT_DIR).parts
        return len(parts) >= 1 and parts[0] == "xx"
    except ValueError:
        return False

def processa_include(input_path , inclusi=None ):
 
    if inclusi is None:
        inclusi = set()

    content = input_path.read_text(encoding="utf-8")

    def sostituisci_include(match):
        include_file = INCLUDE_DIR / match.group(1)
        if include_file in inclusi:
            print(f"ERRORE: Include circolare per {match.group(1)}")
            return f"<!-- ERRORE: Include circolare per {match.group(1)} -->"
        inclusi.add(include_file)
        return processa_include(include_file, inclusi)

    return re.sub(r"@@include\s+(\S+)", sostituisci_include, content)

def processa_traduzioni(content, lingua):
    # Pattern per trovare i blocchi @{ ... }
    pattern_blocco = r"@\{\s*(.*?)\s*\@}"
    
    # Funzione di sostituzione per ogni blocco trovato
    def sostituisci_blocco(match):
        blocco = match.group(1)
        # Cerca la lingua specifica nel blocco
        pattern_lingua = rf'@{lingua}\{{\s*(.*?)\s*}}'
        match_lingua = re.search(pattern_lingua, blocco, re.DOTALL)
        if match_lingua:
            return match_lingua.group(1).strip()
        else:
            # Cerca il testo in italiano come fallback
            pattern_italiano = r'@it\{\s*(.*?)\s*}'
            match_italiano = re.search(pattern_italiano, blocco, re.DOTALL)
            if match_italiano:
                return "TODO: manca la traduzione in "+lingua +" di : "+ match_italiano.group(1).strip()  
            else:
                return "TODO: ERRORE MANCA LINGUA e ITALIANO !! "
    
    # Sostituisce tutti i blocchi nel contenuto
    risultato = re.sub(pattern_blocco, sostituisci_blocco, content, flags=re.DOTALL)
    return risultato

def processa_link(content, lingua):
    # Cerca SOLO la sequenza esatta "@xx" (case-sensitive)
    risultato = re.sub(r'@xx', f'{lingua}', content)
    return risultato

def processa_page_path(content, lingua, path):

    page_path = path.relative_to(OUTPUT_DIR / lingua ).as_posix()

    risultato = re.sub(r'@pagepath', page_path, content)
    return risultato



def main():
    pulisci_cartella_output()

    
    for input_path in sorted(INPUT_DIR.rglob("*")):
        if input_path.is_dir() :
            print(f"{input_path} è una directory , salto")
            continue
        
        if input_path.is_file() and not is_directly_in_xx(input_path):
            print(f"{input_path} non è direttamente in src/xx/")
            print("        copio in _file")
            dst = OUTPUT_DIR / input_path.relative_to(INPUT_DIR)
            # Crea la directory di destinazione se non esiste
            dst.parent.mkdir(parents=True, exist_ok=True)
            # Copia il file
            shutil.copy2(input_path, dst)  # copy2 preserva i metadati
            continue

        ## dovrebbero rimanere solo file in xx/ 
        if input_path.is_file() :
            print(f"processo {input_path}")
            if not is_processabile( input_path): 
                for lingua in LINGUE:
                    dst = OUTPUT_DIR / lingua / input_path.relative_to(INPUT_DIR / "xx")
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(input_path, dst)  
            else:
                for lingua in LINGUE:
                    dst = OUTPUT_DIR / lingua / input_path.relative_to(INPUT_DIR / "xx")
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    content = processa_include(input_path)
                    content = processa_traduzioni(content, lingua)
                    content = processa_link(content, lingua)
                    content = processa_page_path(content, lingua, dst)
                    dst.write_text(content, encoding="utf-8")

        else:
            print(f"{input_path} che cosa è QUESTO NON DOVEVVA ACCADERE")

    print(f"Generazione completata in {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()