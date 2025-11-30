"# SanskritApp"  
# SanskritApp – Interaktivní překladač a generátor sanskrtských vět

## 📦 Obsah složky

- `app.py` ................ hlavní aplikace (Streamlit)
- `transliterate.py` ...... převody IAST ↔ dévanágarí ↔ český přepis
- `sandhi_engine.py` ...... pravidla sandhi – spojování slov
- `parser.py` ............. základní rozbor vět
- `helpers/` .............. pomocné funkce
  - `slovnik.py` ........... načítání dat ze souborů
  - `sklonovani.py` ....... skloňování
  - `casovani.py` .......... časování
- `data/` .................. vstupní soubory (CSV)
  - `podstatna_jmena.csv`
  - `pridavna_jmena.csv`
  - `slovesa.csv`
  - `ostatni_slova.csv`
  - `koncovky_pady.csv`
  - `koncovky_casy.csv`
- `style.css` ............. volitelný styl aplikace

## 🧰 Instalace (Windows)

1. Stáhni Python 3.10+ z [python.org](https://www.python.org/downloads/)
2. Spusť příkazový řádek (CMD nebo PowerShell)
3. Instaluj knihovny:
```bash
pip install -r requirements.txt

"# SanskritApp"  
