README.txt
1  SanskritApp – Interaktivní překladač a generátor sanskrtských vět
2  ------------------------------------------------------------------
3  
4  📦 OBSAH SLOŽKY:
5  ├── app.py ................ hlavní aplikace (Streamlit)
6  ├── transliterate.py ...... převody IAST ↔ dévanágarí ↔ český přepis
7  ├── sandhi_engine.py ...... pravidla sandhi – spojování slov
8  ├── parser.py ............. základní rozbor vět
9  ├── helpers/ .............. pomocné funkce
10 │   ├── slovnik.py ........... načítání dat ze souborů
11 │   ├── sklonovani.py ........ skloňování
12 │   └── casovani.py .......... časování
13 ├── data/ ................. vstupní soubory (CSV)
14 │   ├── podstatna_jmena.csv
15 │   ├── pridavna_jmena.csv
16 │   ├── slovesa.csv
17 │   ├── ostatni_slova.csv
18 │   ├── koncovky_pady.csv
19 │   └── koncovky_casy.csv
20 └── style.css ............. volitelný styl aplikace
21 
22  
23  🧰 INSTALACE (Windows):
24  ------------------------
25  1. Stáhni Python 3.10+ z https://www.python.org/downloads/
26  2. Spusť příkazový řádek (CMD nebo PowerShell)
27  3. Instaluj knihovny:
28     pip install streamlit pandas indic-transliteration
29  4. Spusť aplikaci:
30     streamlit run app.py
31 
32  🔁 Přístup v prohlížeči: http://localhost:8501
33 
34  
35  📝 OVLÁDÁNÍ:
36  ------------
37  - Vyber slova ze slovníku
38  - Zadej parametry (pád, rod, číslo, osoba…)
39  - Vytvoř větu – provede se sandhi a přepis
40  - Výsledný výstup = věta v dévanágarí + přepis + překlad
41 
42  
43  📌 POZNÁMKY:
44  -----------
45  - Veškeré CSV soubory musí být v UTF-8
46  - Data můžeš rozšířit přidáním dalších slov
47  - Funguje offline (plně)
48 
49  📧 Kontakt:
50     Ing. Jaromír Zavřel + SanskritApp Dev
