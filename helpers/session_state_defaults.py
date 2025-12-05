# helpers/session_state_defaults.py
#
# ===============================================================
# session_state_defaults.py
# ---------------------------------------------------------------
# Inicializace výchozího stavu aplikace (Streamlit session_state)
# ===============================================================

# Obsahuje:
# if_dir_exist, if_file_exist, load_css, init_ciselniky_session_state, init_session_state_on_startup
#
# Volá:
# zobraz_toast, nacti_soubor, nacti_csv, prazdna_veta, generovani_sandhi_pravidel

# import
import os
import csv
import streamlit as st
import logging


# Vlastní moduly
from helpers.ui_display import zobraz_toast

from helpers.loader_csv import (
    nacti_soubor,
    nacti_csv,
)

from helpers.utils import (
    prazdna_veta,
    if_dir_exist,
    if_file_exist,
)

from helpers.generovani_sandhi_json import generovani_sandhi_pravidel


# 2️⃣ Načtení CSS stylu
# -------------------------------------------------
# 🟢 Pomocná funkce: Načtení CSS
# -------------------------------------------------
def load_css():
    css = nacti_soubor("style.css")
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# 3️⃣ Inicializace hlavních číselníků
def _init_ciselniky(ciselnik):

    ss = st.session_state

    # 1. Vytvoří seznamy pro každý typ (pad, rod, cislo, osoba, slovni_druh, pada, aktivita)
    # ss['pad'] = ["N","Ak","I","D","Abl","G","L","V"]
    # ss['rod'] = ["m","n","f"]
    # ss['cislo'] = ["sg.","du.","pl."]
    # ss['osoba'] = [1,2,3]
    # ss['pada'] = ["parasmai","átmané"]
    # ss['aktivita'] = ["aktivum","médium","pasivum"]
    # ss['slovni_druh'] = ["pj","aj","zj","","slv","","","","","","ost"]

    typy = set(r["typ"] for r in ciselnik)

    for typ in typy:
        if typ != "slovni_druh":
            hodnoty = []
            for r in ciselnik:
                if r["typ"] == typ:
                    z = r["zkratka"]
                    if typ == "osoba" and z.isdigit():
                        hodnoty.append(int(z))  # převést na int
                    else:
                        hodnoty.append(z)
            ss[typ] = hodnoty

    # 🔹 Slovní druhy
    # 🔹 2. seznam slovníků pro slovní druhy
    ss["slovni_druh"] = [
        {
            "zkratka": r["zkratka"],  # koncovka, zkratka, kód „pj“, „aj“ atd.
            "nazev": r["nazev"],  # název cz „Podstatné jméno“, „Přídavné jméno“ atd.
            "typ": r["sanskrt"],  # kód „sub“, „adj“ atd.
            "nazev_l": r["devanagari"],  # název latin „Substantivum“, „Adjektivum“ atd.
            "slovnik": r["slovnik"],  # cesta ke slovníku csv
        }
        for r in ciselnik
        if r.get("typ") == "slovni_druh" and r.get("slovnik")
    ]

    ss["slovni_druh_lookup"] = {
        # klíče podle typ (sub, adj...)
        **{d["typ"]: d for d in ss["slovni_druh"]},
        # klíče podle název ("Podstatné jméno", ...)
        **{d["nazev"]: d for d in ss["slovni_druh"]},
    }

    # 🔹 Seznam všech sanskrtských kódů druhů slov
    # ["sub", "adj", "pron", "verb", "ost"]
    ss["slovni_druhy_list"] = [d["typ"] for d in ss["slovni_druh"]]

    # 🔹 Množina pro rychlé testování v podmínkách
    # {"sub", "adj", "pron", "verb", "ost"}
    ss["slovni_druhy_set"] = set(ss["slovni_druhy_list"])


# 3️⃣ Inicializace hlavních slovníků
def _init_slovniky(ciselnik):

    ss = st.session_state

    # 3. Slovníky - vytvoří seznam slovníh druhů ke kterým jsou slovníky a cesty k souborům
    # Projde všechny záznamy (řádky) v seznamu ciselnik.
    # ciselnik = nacti_csv(cesta="data/pad_rod_ciso_osoba_sans.csv" ...
    # typ;zkratka;nazev;sanskrt;devanagari;otazky;funkce;slovnik
    # slovni_druh;pj;Podstatné jméno;sub;Substantivum;;;data/podstatna_jmena.csv

    # Z každého, kde:
    #  . typ == "slovni_druh"
    #  . a má neprázdný klíč "slovnik"
    # vytvoří dvojici
    # (název → cesta k souboru) (Podstatné jméno → data/podstatna_jmena.csv)
    # podmíněný comprehension s kontrolou, zda klíč v řádku existuje a není prázdný

    ss["slovniky"] = {
        r["nazev"]: r["slovnik"]
        for r in ciselnik
        if r.get("typ") == "slovni_druh" and r.get("slovnik")  # musí existovat a nebýt ""
    }


# 4️⃣ Inicializace časů (lakára, participia)
def _init_casy():

    ss = st.session_state

    # ------------------------------------------------------------
    # časy a další tvary pro dějová slova, načtené z data/cas.csv
    # poradi;lakara;cas_l;cas_cz;pada;aktivita;poznamka
    # ------------------------------------------------------------

    ss["casy"] = nacti_csv("data/cas.csv", sloupec_trideni="poradi", zobraz=False)

    casy = ss["casy"]
    if "casy_participa_pasiv_list" not in ss:
        ss["casy_participa_pasiv_list"] = (
            casy[(casy["lakara"] == "participium") & (casy["aktivita"] == "pasivum")]["cas_l"]
            .dropna()
            .unique()
            .tolist()
        )
    if "casy_participa_pasiv_set" not in ss:
        ss["casy_participa_pasiv_set"] = set(ss["casy_participa_pasiv_list"])

    if "casy_participa_aktiv_list" not in ss:
        ss["casy_participa_aktiv_list"] = (
            casy[(casy["lakara"] == "participium") & (casy["aktivita"] == "aktivum")]["cas_l"]
            .dropna()
            .unique()
            .tolist()
        )
    if "casy_participa_aktiv_set" not in ss:
        ss["casy_participa_aktiv_set"] = set(ss["casy_participa_aktiv_list"])

    if "casy_participa_list" not in ss:
        ss["casy_participa_list"] = (
            casy[(casy["lakara"] == "participium")]["cas_l"].dropna().unique().tolist()
        )
    if "casy_participa_set" not in ss:
        ss["casy_participa_set"] = set(ss["casy_participa_list"])

    if "cas_ve_treti_osobe_list" not in ss:
        ss["cas_ve_treti_osobe_list"] = ["prezent", "aorist"]
    if "cas_ve_treti_osobe_set" not in ss:
        ss["cas_ve_treti_osobe_set"] = set(ss["cas_ve_treti_osobe_list"])


# 5️⃣ Inicializace editace, věty, konfigurace, atd.


def _init_ciselniky_session_state(ciselnik):
    _init_ciselniky(ciselnik)
    _init_slovniky(ciselnik)
    _init_casy()


# -------------------------------------------------
# -------------------------------------------------


def _init_on_startup_ciselnik():
    """
    Inicializace všech číselníků aplikace:
    - pády, rody, čísla, osoby
    - slovníky
    - časy (lakára, participia)
    - editační proměnné
    """

    ss = st.session_state

    # Načtení číselníků a seznamu slovníků !!! POZOR KOMPLETNÍ ČÍSELNÍK !!!
    ciselnik = nacti_csv(
        cesta="data/pad_rod_ciso_osoba_sans.csv", sloupec_trideni=None, zobraz=False, typ="list"
    )
    if ciselnik:
        # 1. uložíme originální CSV
        ss["ciselnik"] = ciselnik
        # 2. naplníme session_state hodnotami z CSV
        _init_ciselniky_session_state(ciselnik)
    else:
        # 1. uložíme prázdný seznam (není CSV)
        ss["ciselnik"] = []
        # 2. inicializujeme session_state prázdně, aby aplikace běžela
        _init_ciselniky_session_state([])

    if "cas" not in ss:
        ss["cas"] = nacti_csv(cesta="data/cas.csv", sloupec_trideni="poradi", zobraz=False)

    return


def _init_on_startup_odvozeno():

    ss = st.session_state

    # Odvozené hodnoty – až po inicializaci základu
    if "enable_edit_set" not in ss:
        ss["enable_edit_set"] = set(ss["enable_edit_list"])

    # Směr překladu (musí být až po volby_smer_prekladu a smer_index)
    if "smer_prekladu" not in ss:
        ss["smer_prekladu"] = ss["volby_smer_prekladu"][ss["smer_index"]]

    # -------------------------------------------------
    # 4️⃣ Inicializace dat a pravidel Sandhi
    # -------------------------------------------------
    if "sandhi_skupiny" not in ss or "sandhi_pravidla" not in ss:
        ss["sandhi_pravidla_file_def"] = "data/sandhi_pravidla_default.json"
        ss["sandhi_pravidla_file"] = "data/sandhi_pravidla.json"
        ss["sandhi_skupiny"], ss["sandhi_pravidla"] = generovani_sandhi_pravidel(
            ss["sandhi_pravidla_file_def"],
            ss["sandhi_pravidla_file"],
        )

    # -----------------------------------------------------
    # 5️⃣ Inicializace prázdné věty (pokud existuje funkce)
    # -----------------------------------------------------
    if "prazdna_veta" in globals():
        # prázdná tabulka s 7 variantami
        prazdna_veta()

    # -------------------------------------------------
    # 6️⃣ Logování (pokud je aktivní)
    # -------------------------------------------------
    if ss["cfg"]["f_log"]:
        logging.basicConfig(filename="data/debug_log.txt", level=logging.DEBUG, encoding="utf-8")


# 6️⃣ Hlavní spouštěcí funkce
# defaults, setups
def init_session_state_on_startup():
    """Inicializace session_state při startu aplikace."""

    ss = st.session_state

    # --- Inicializace session_state ---
    # for key in list(ss.keys()):
    #     del ss[key]

    # Definice + počáteční hodnoty

    # definice defaultních proměnných do ss a jejich počátečních hodnot jako dict (ss jako klíč / hodnota)
    defaults = {
        # -------------------------------------------------
        # 2. Inicializace session_state
        # -------------------------------------------------
        # _init_on_startup_cfg()
        # počet průběhů
        # "init": 0,
        # inicializace konfigurace aplikace
        "cfg": {},
        # Překlad a směr
        # nastaveni_smeru / parametry překladu
        # stav radio buttonu pro směr překladu (CZ → SAN, SAN → CZ)
        # směr překladu
        "volby_smer_prekladu": ["cz → sanskrt", "sanskrt → cz"],
        "smer_index": 0,
        # Editace a věta
        # i = index slova ve větě
        "index_edit_word": None,
        # --- Inicializace session_state (matice_vety) ---
        # Základní struktura věty: list - seznam všech slov ve větě - slovo - řádek jako dict
        # hlavní seznam slov, která tvoří větu
        # definována jako list (seznam), dict (slovníků) na řádku,
        "matice_vety": [],
        # dočasná struktura pro aktuálně vybrané/parametrizované slovo (ještě než se vloží do věty) celý slovník parametrů
        # dict dočasný slovník pro aktuální slovo
        "matice_nove_slovo": {},
        # aktuálně vybrané slovo (ještě než se vloží do věty) pro zobrazení názvu slova
        "slovo": "",
        # to, co se zobrazuje jako průběžný výpis parametrů vybraného slova
        "matice_vypis": {},
        # Filtry a výběry
        # filtry / vybraný slovník - ZATÍM NEVYUŽITO
        # když si uživatel vybere slovník nebo filtr hledání, musí se to uložit,
        # aby se to neztratilo po dalším renderu
        # výchozí slovník
        "slovnik": "hlavni",
        # _init_on_startup_veta()
        # Věty
        # věta s popisem
        "veta_tran_cz_popis": "",
        # věta bez popisu CZ
        "veta_tran_cz": "",
        # věta bez popisu IAST
        "veta_tran_iast": "",
        # věta CZ
        "veta_cz": "",
        # věta po sandhi CZ
        "veta_tran_cz_sandhi": "",
        # věta po sandhi IAST
        "veta_tran_iast_sandhi": "",
        # věta po sandhi dev
        "veta_dev_sandhi": "",
        # _init_on_startup_f()
        # Výsledky
        # Inicializace seznamu výsledků vět
        # každý prvek: {"Název": ..., "Věta": ...}
        "matice_vet": [],
        # prázdná tabulka s 7 variantami
        # spustit prazdna_veta()
        # _init_on_startup_sandhi()
        # -------------------------------------------------
        # 3. Načtení ciselníků a dat
        # -------------------------------------------------
        # Při startu aplikace
        # 1. se spustí funkce generovani_sandhi_pravidel() v helpers.generovani_sandhi_json
        #    ta používá na vstupu "data/sandhi_pravidla_zdroj.csv"
        # 2. ta vytvoří (nebo přepíše) "data/sandhi_pravidla.json"
        # 3. pravidla se uloží do ss.sandhi_pravidla
        # 4. a ta se použijí funkcí apply_sandhi v helpers.sandhi_processor
        #    a vytvoří ze vstupní věty cz tran sandhi cz tran
        # Sandhi
        # Inicializace - rozepsaná pravidla sandhi
        "sandhi_pravidla_file_def": "",
        "sandhi_pravidla_file": "",
        # _init_edit()
        # Edit (typy slov)
        # "typ" (udělat set)
        "enable_edit_list": ["sub", "adj", "verb"],
        # defaultni slovní druh, koncovka proměnné (klíče v ss) rozlišující slovní druh
        "koncovka": "sub",
        # časy a další tvary pro dějová slova, načtené z data/cas.csv
        # poradi;lakara;cas_l;cas_cz;pada;aktivita;poznamka
        "casy": {},
        # _init_on_startup_ciselnik()
    }

    # 2️⃣ Nastavení hlavních klíčů
    for k, v in defaults.items():
        if k not in ss:
            ss[k] = v

    # --- Inicializace flagů / kontrolních proměnných ---
    flags_defaults = {
        # Průběhové semafory
        # směr překladu - prvotní
        "f_smer_zmenen": False,
        # 1️⃣ Vložit hotové slovo - vlevo 1.
        "f_vloz_do_matice_vety": False,
        # 2️⃣ Vyskloňovat a vložit - vlevo 2.
        "f_vysklonuj": False,
        # když uživatel stiskne tlačítko pro sestavení věty - vpravo 1.
        "f_sestav_vetu": False,
        # Když uživatel stiskne tlačítko pro aplikaci sandhi - vpravo 3.
        "f_aplikuj_sandhi": False,
        "f_aplikuj_transliteraci": False,
        # Akce
        # Když uživatel stiskne tlačítko pro export věty - vpravo 4.
        "f_export_vety": False,
        # Když uživatel stiskne tlačítko "Bez sestavení" věty - vpravo 5.
        "f_ne_sestav_vetu": False,
        # Když uživatel stiskne tlačítko pro smazání věty - vpravo 6.
        "f_smaz_vetu": False,
        # Když uživatel stiskne tlačítko pro vložení prvního slova do věty
        # (je-li f_hlavicka_slov = False => není zobrazena,
        # tj. před 1. slovem zobraz hlavičku, a nastav True a již ji nezobrazuj)
        "f_hlavicka_slov": False,
        # slovo zpět ku tvarování
        "f_edit": False,
        # -------------------------------------------------
        # POM SEKCE pro nastavení dočasných hodnot
    }
    for k, v in flags_defaults.items():
        if k not in ss:
            ss[k] = v

    # -------------------------------------------------
    # 3️⃣ Konfigurace (cfg)
    # -------------------------------------------------
    # 3️⃣ Výchozí konfigurace (vnořený slovník)
    cfg_defaults = {
        # DEFAULT
        # -------------------------------------------------
        # Nastvení aplikace - DEFAULT
        # formát výpisu
        "f_bez_tlacitek": False,
        # konfigurace aplikace - auto sandhi po sestavení věty - vpravo 2.
        "f_auto_sandhi": True,  # noqa: F601
        # -------------------------------------------------
        # Ladění a Debug - DEFAULT
        # pomůcka při návrhu rozměrů sloupců
        "f_test_sloupcu": False,
        # je-li True všechna hlášení vypnuta, pro hlášení vyžadováno nastavení f_privileg = True
        "f_zobraz_toast_privileg": False,
        # je-li True zobraz debug hlášení, pro hlášení vyžadováno nastavení režm i volání f_debug = True
        "f_zobraz_toast_debug": False,
        # Debug
        # Debug / ladění (pokud si necháš přepínač testovacího režimu) - ZATÍM NEVYUŽITO
        # režim ladění vypnut
        "f_debug": False,
        # režim logování vypnut
        "f_log": False,
        # -------------------------------------------------
        # POM SEKCE pro nastavení dočasných hodnot
        # Nastvení aplikace
        # konfigurace aplikace - auto sandhi po sestavení věty - vpravo 2.
        "f_auto_sandhi": False,
        # -------------------------------------------------
        # Ladění a Debug
        # pomůcka při návrhu rozměrů sloupců
        "f_test_sloupcu": False,
        # je-li True všechna hlášení vypnuta, pro hlášení vyžadováno nastavení f_privileg = True
        "f_zobraz_toast_privileg": False,
        # je-li True zobraz debug hlášení, pro hlášení vyžadováno nastavení režm i volání f_debug = True
        "f_zobraz_toast_debug": False,
        # Debug
        # Debug / ladění (pokud si necháš přepínač testovacího režimu) - ZATÍM NEVYUŽITO
        # režim ladění vypnut
        "f_debug": False,
        # režim logování vypnut
        "f_log": False,
    }

    # 4️⃣ Nastavení hodnot uvnitř ss["cfg"]
    for k, v in cfg_defaults.items():
        if k not in ss["cfg"]:
            ss["cfg"][k] = v

    # počet průběhů
    if "init" not in ss:
        ss["init"] = 0
    else:
        ss["init"] += 1
    if ss["cfg"]["f_debug"]:
        ss.write("**ss['init']:**", ss.get("init"))

    # načte konfigurační hodnoty (cfg) ze souboru config.json, pokud existuje

    # Inicializace odvozených hodnot
    _init_on_startup_odvozeno()

    # Inicializace všech číselníků aplikace:
    _init_on_startup_ciselnik()
