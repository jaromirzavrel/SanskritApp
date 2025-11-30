# helpers/utils.py
#
# Obsahuje:
# clean_value, safe_index_or_default, convert_csv_comma_to_semicolon, vloz_slovo_do_matice_vety,
# vysklonuj_slovo_do_vety, prazdna_veta, sestav_vetu, aplikuj_sandhi, aplikuj_transliteraci, export_vety,
# ne_sestav_vetu, smaz_vetu, sklonuj_slovo, vytvor_verze_vety, y_aplikuj_sandhi, transliterace, vysklonuj
#
# Volá:
# aplikuj_sandhi, prazdna_veta, aplikuj_transliteraci, ne_sestav_vetu,
# zobraz_vetu, zobraz_toast, SandhiProcessor, transliterate_czech_v_to_iast, transliterate_czech_v_to_deva

# modul pro zpracování tlačítek z ui_layout
# sestavení věty, provedení sandhi (volá sandhi_engine), převod do dévanágarí, export, výmaz matice věty, matice vět, věty
# zobrazení má na starosti ui_layout (musí zobrazit po návratu do app.py)

# import
import streamlit as st
import pandas as pd
import numpy as np
import inspect
import os
import csv
import time

# Vlastní moduly
from helpers.ui_display import (
    zobraz_toast,
    zobraz_vetu,
)

from helpers.sandhi_processor import SandhiProcessor

from helpers.transliterate import (
    transliterate_iast_to_deva,
    transliterate_deva_to_iast,
    transliterate_iast_to_czech_v,
    transliterate_czech_v_to_iast,
    transliterate_czech_v_to_deva,
    transliterate_iast_to_czech_f,
    transliterate_iast_to_czech_l,
)

# ==============================================================================================================================================


# 1️⃣ Ověření adresářů
def if_dir_exist(seznam: str):
    """
    Načte seznam adresářů z CSV a ověří jejich existenci.
    Pokud adresář neexistuje, vytvoří ho.
    """
    soubor = os.path.basename(seznam)
    adresar = os.path.dirname(seznam) or "."
    if not os.path.exists(seznam):
        zobraz_toast(
            text=f"Soubor seznamu adresářů projektu '{soubor}' nebyl nalezen v adresáři '{adresar}'.",
            icon="⚠️",
            trvani=3,
        )
        return

    with open(seznam, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        data = [row for row in reader if any(row.values())]  # ignoruje zcela prázdné řádky
        for radek in data:
            adresar = radek["cesta"]
            # popis = radek.get('popis', '')
            if not os.path.exists(adresar):
                os.makedirs(adresar)


# 1️⃣ Ověření souborů
def if_file_exist(seznam: str):
    """
    Načte seznam souborů z CSV a ověří jejich existenci.
    Pokud soubor neexistuje, zobrazí toast.
    """
    soubor = os.path.basename(seznam)
    adresar = os.path.dirname(seznam) or "."
    if not os.path.exists(seznam):
        zobraz_toast(
            text=f"Soubor seznamu souborů projektu '{soubor}' nebyl nalezen v adresáři '{adresar}'.",
            icon="⚠️",
            trvani=3,
        )
        return

    with open(seznam, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        data = [row for row in reader if any(row.values())]  # ignoruje zcela prázdné řádky
        for radek in data:
            cesta = radek["cesta"]
            soubor = os.path.basename(cesta)
            adresar = os.path.dirname(cesta) or "."
            popis = radek.get("popis", "")
            if not os.path.exists(cesta):
                zobraz_toast(
                    text=f"Soubor '{soubor}' ({popis}) nebyl nalezen v adresáři '{adresar}'!",
                    icon="⚠️",
                    trvani=3,
                )


def clean_value(value, default=None, strip=True):
    """
    Vyčistí hodnotu: odstraní NaN, None, prázdné řetězce, a volitelně ořeže mezery.
    Vrátí vyčištěnou hodnotu – odstraní mezery a zkontroluje prázdnotu.
    Vrátí výchozí hodnotu, pokud je hodnota prázdná nebo neplatná.
    Pokud je hodnota None nebo prázdný řetězec, vrátí `default`.
    """
    # Pokud je hodnota typu pandas.NaT / NaN
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default

    # Pokud je hodnota prázdný řetězec nebo jen mezery
    if isinstance(value, str):
        v = value.strip() if strip else value
        if v == "":
            return default
        return v

    # Pokud je to jiný typ (např. int, bool), vrátíme přímo
    return value


# použití
# rod_puvodni = r_vybrane_slovo.get('rod', None)
# value_rod = clean_value(rod_puvodni, default = "m")

# ==============================================================================================================================================


def safe_index_or_default(options, value, default_index=0):
    """
    Vrátí index hodnoty `value` v seznamu `options`, pokud existuje.
    Pokud není nalezena, vrátí `default_index` (výchozí 0).
    Používá se například při získávání indexu pro Streamlit výběrník (radio/selectbox).
    Ošetří None, NaN, prázdné řetězce a neexistující hodnoty.

    :param options:       seznam
    :param value:         hledaná hodnota
    :param default_index: výchozí index, pokud není nalezena hodnota
    :return:              int – index hodnoty nebo default_index
    Parametry:
        options:       seznam, ve kterém hledáme hodnotu (např. ["m", "f", "n"])
        value:         hledaná hodnota (např. 'm', 'n', 'f')
        default_index: výchozí index, návratová hodnota, pokud hodnota v seznamu není
    return:            int – index hodnoty nebo default_index

    Příklad:
        safe_index_or_default(['m','n','f'], 'n')     -> 1
        safe_index_or_default(['m','n','f'], 'x')     -> 0
        safe_index_or_default(['m','n','f'], None, 2) -> 2
    """
    try:
        # NaN / None
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return default_index

        # prázdný řetězec
        if isinstance(value, str):
            v = value.strip()
            if not v:
                return default_index
            value = v

        # hledání indexu
        return options.index(value)
    except Exception:
        return default_index


# použití
# rod_puvodni = r_vybrane_slovo.get('rod', None)
# value_rod = clean_value(rod_puvodni, default = "m")
# index_rod = safe_index_or_default(ss['rod'], value_rod, 0)

# ==============================================================================================================================================


def convert_csv_comma_to_semicolon(vstup: str, vystup: str | None = None) -> None:
    """
    Načte CSV s oddělovačem čárka a uloží jej zpět se středníkem.
    Pokud není zadán výstup, přepíše původní soubor.
    """

    # určím, jestli přepsat nebo uložit jako nový
    if vystup is None:
        # vystup = vstup
        # vytvoř název pro nový soubor (rozdělí na jméno a příponu)
        root, ext = os.path.splitext(vstup)
        vystup = f"{root}_semicolon{ext}"

    # načte CSV se stávajícím oddělovačem čárka
    df = pd.read_csv(vstup, sep=",", encoding="utf-8")

    # uloží zpátky se středníkem
    df.to_csv(vystup, sep=";", index=False, encoding="utf-8")


# použití
# convert_csv_comma_to_semicolon("sandhi_pravidla_zdroj.csv")

# ==============================================================================================================================================


def urci_koncovku(typ: str = "") -> str:
    """
    Najde koncovku podle typu slova (např. 'sub', 'adj', 'pron', 'verb', 'ost').
    """

    ss = st.session_state

    # ➡️ Načte seznam slovních druhů z session_state
    # (pokud tam není, použije prázdný seznam).
    slovni_druhy = ss.get("slovni_druh", [])
    key_typ = "typ"
    # sjednocení systému — používá se stejný klíč
    key_koncovka = key_typ

    # Najdi záznam ve slovních druzích
    # Najdi první záznam, který odpovídá typu
    # ➡️ Najde první záznam (slovník) ve slovni_druhy, kde r['typ'] == typ.
    # Pokud žádný takový není, vrátí None.
    r_typ = next((r for r in slovni_druhy if r.get(key_typ) == typ), None)

    # ➡️Pokud se záznam našel, vezme z něj hodnotu pod klíčem key_koncovka, jinak prázdný řetězec.
    koncovka = r_typ.get(key_koncovka, "") if r_typ else ""

    ss["koncovka"] = koncovka
    return koncovka


# ==============================================================================================================================================


def vloz_slovo_do_matice_vety():
    """
    Vloží nebo nahradí slovo v matici věty.
    """

    ss = st.session_state

    nove = ss["matice_nove_slovo"]
    index = ss["index_edit_word"]
    # index = ss.get('index_edit_word', None)
    zobraz_toast(f"index {index}.", trvani=15)
    zobraz_toast(f"ss[f_edit] {ss['f_edit']}.", trvani=15)

    if index is not None and index >= 0:
        # EDITACE
        # Nahradí slovo na daném indexu
        ss["matice_vety"][index] = nove
        # vrátit slovo na tvarování i = index slova ve větě
        # ss['index_edit_word'] = None
        # zobraz_toast(f"Slovo na pozici {index + 1} bylo nahrazeno.", trvani=5)
        # st.rerun()
    else:
        # Nové slovo
        index = len(ss["matice_vety"])
        # Vložení slova do věty
        ss["matice_vety"].append(nove)
        # zobraz_toast(f"{index}. Slovo přidáno do věty.", trvani=5)


# ==============================================================================================================================================


def vysklonuj_slovo_do_vety():
    """Vyskloňuje a vloží slovo do věty."""

    ss = st.session_state

    nove = ss["matice_nove_slovo"]
    ss["matice_vety"].append(nove)
    zobraz_toast("Slovo bylo vyskloňováno a přidáno do věty.")


# ==============================================================================================================================================


def prazdna_veta() -> bool:

    ss = st.session_state

    ss.matice_vet = [
        {"Varianta": "Trans cz popis", "Věta": ss["veta_tran_cz_popis"]},
        {"Varianta": "Trans cz", "Věta": ss["veta_tran_cz"]},
        {"Varianta": "Trans IAST", "Věta": ss["veta_tran_iast"]},
        {"Varianta": "CZ", "Věta": ss["veta_cz"]},
        {"Varianta": "Trans cz sandhi", "Věta": ss["veta_tran_cz_sandhi"]},
        {"Varianta": "Trans IAST sandhi", "Věta": ss["veta_tran_iast_sandhi"]},
        {"Varianta": "Dévanágarí", "Věta": ss["veta_dev_sandhi"]},
    ]


# ==============================================================================================================================================


def sestav_vetu() -> bool:
    """
    Sestaví větu (7 verzí) z matice vety a uloží ji do ss.
    koncovka = varianta dle slovního druhu (např. pj, aj, zj, slv, ost ...)
    """

    ss = st.session_state

    # Kontrola, že matice existuje
    if "matice_vety" not in ss or not ss["matice_vety"]:
        # st.warning("Matice věty není definována nebo je prázdná.")
        return False

    # 1. Inicializace výstupních proměnných
    veta_tran_cz_popis = ""
    veta_tran_cz = ""
    veta_tran_iast = ""
    veta_cz = ""
    veta_tran_cz_sandhi = ""
    veta_tran_iast_sandhi = ""
    veta_dev_sandhi = ""

    # 3. Sestavení věty
    for radek in ss["matice_vety"]:
        typ = radek.get("typ", "")
        koncovka = urci_koncovku(typ)  # (utils.py)
        # st.write(f"(typ >{typ}<, koncovka >{koncovka}<)")

        veta_tran_cz_popis += radek.get(f"slovo_tran_cz_{koncovka}_popis", "") + " "
        veta_tran_cz += radek.get(f"slovo_tran_cz_{koncovka}", "") + " "
        veta_tran_iast += radek.get(f"slovo_tran_iast_{koncovka}", "") + " "
        veta_cz += radek.get(f"cz_{koncovka}", "") + " "

    # 4. Odstranění přebytečných mezer
    veta_tran_cz_popis = veta_tran_cz_popis.strip()
    veta_tran_cz = veta_tran_cz.strip()
    veta_tran_iast = veta_tran_iast.strip()
    veta_cz = veta_cz.strip()

    # 5. Sandhi
    # Aplikuj sandhi jen na přepis CZ
    # 2. Pokud je auto_sandhi zapnuté → aplikuj sandhi a převody
    # if f_auto_sandhi:
    # ss['veta_tran_cz']     = veta_tran_cz # věta bez popisu CZ
    # ss['f_aplikuj_sandhi'] = True         # Stisknutí tlačítka "Aplikuj Sandhi"
    # veta_tran_cz_sandhi               = aplikuj_sandhi(veta_tran_cz)
    # veta_tran_cz_sandhi               = aplikuj_sandhi()
    # aplikuj_sandhi()
    # veta_tran_cz_sandhi               = ss['veta_tran_cz_sandhi'] # Výstup
    # veta_tran_iast_sandhi             = transliterate_czech_v_to_iast(veta_tran_cz_sandhi)
    # veta_dev_sandhi                   = transliterate_iast_to_deva(veta_tran_iast_sandhi)

    # typ
    # slovo_tran_cz_pj_popis
    # slovo_tran_cz_pj
    # slovo_tran_iast_pj
    # cz_pj

    # veta_tran_cz_popis
    # veta_tran_cz
    # veta_tran_iast
    # veta_cz
    # veta_tran_cz_sandhi
    # veta_tran_iast_sandhi
    # veta_dev_sandhi

    # 6. Návrat výsledků
    ss["veta_tran_cz_popis"] = veta_tran_cz_popis  # věta s popisem
    ss["veta_tran_cz"] = veta_tran_cz  # věta bez popisu CZ
    ss["veta_tran_iast"] = veta_tran_iast  # věta bez popisu IAST
    ss["veta_cz"] = veta_cz  # věta CZ
    ss["veta_tran_cz_sandhi"] = veta_tran_cz_sandhi  # věta po sandhi CZ
    ss["veta_tran_iast_sandhi"] = veta_tran_iast_sandhi  # věta po sandhi IAST
    ss["veta_dev_sandhi"] = veta_dev_sandhi  # věta po sandhi devanagari

    # Naplnění prázdné věty, případně přepsání aktuální větou v 7 verzích
    prazdna_veta()

    # 7. Výpis výsledků - přesunout do ui_layout.py
    # funkce = inspect.currentframe().f_code.co_name
    # zobraz_vetu(kdo_vola=funkce)
    if False:
        # st.markdown("### Věta s popisem:")
        st.write(ss["veta_tran_cz_popis"])
        # st.markdown("### Věta bez popisu:")
        st.write(ss["veta_tran_cz"])
        st.write(ss["veta_tran_iast"])
        st.write(ss["veta_cz"])
        st.write(ss["veta_tran_cz_sandhi"])
        st.write(ss["veta_tran_iast_sandhi"])
        st.write(ss["veta_dev_sandhi"])

        # vytvoř popis (vše kromě typu a použitého sloupcového klíče)
    #     popis_parts = []
    #     for klic, hodnota in radek.items():
    #         if klic not in ("typ", klic_slova) and hodnota:
    #             popis_parts.append(f"{klic}: {hodnota}")

    #     if popis_parts:
    #         veta_s_popisem.append(f"{slovo} ({', '.join(popis_parts)})")
    #     else:
    #         veta_s_popisem.append(slovo)

    #     veta_bez_popisu.append(slovo)

    # return " ".join(veta_s_popisem), " ".join(veta_bez_popisu)

    # ss['f_sestav_vetu'] = False # Uvolnění tlačítka "Sestav větu"
    # zobraz_toast(text: str, trvani: float = 2.5)
    # zobraz_toast(text = "📝 Věta sestavena!", trvani = 2.5)
    # st.success("📝 Věta sestavena!")

    # st.toast("📝 Věta sestavena!", icon="✅")

    # placeholder = st.empty()
    # placeholder.success("📝 Věta sestavena!")
    # time.sleep(10)  # zobrazí 2 sekundy
    # placeholder.empty()

    # st.markdown("""
    #     <script>
    #     alert("📝 Věta sestavena!");
    #     </script>
    #     """, unsafe_allow_html=True)

    # st.rerun() # běží stále
    return True


# ==============================================================================================================================================


# Nahrazeno procesorem
def aplikuj_sandhi() -> bool:

    ss = st.session_state

    if ss.get("f_aplikuj_sandhi", False):
        # Kontrola, že věta existuje
        if "veta_tran_cz" not in ss or not ss["veta_tran_cz"]:
            # st.warning("X1. Věta není definována nebo je prázdná.")
            return False

        # Načtení původní věty
        veta_tran_cz = ss.get("veta_tran_cz", "").strip()  # Převzetí parametrů - věty
        if not veta_tran_cz:
            return False  # věta je prázdná

        # Inicializace
        veta_tran_cz_sandhi = ""
        veta_tran_cz_sandhi_zmeny = []  # seznam (index, původní_dvojice, nová_dvojice)

        #         veta_sandhi = aplikuj_sandhi(ss['veta'])
        #         ss['veta_sandhi'] = veta_sandhi
        # if 'veta_sandhi' in ss:
        #     st.markdown("### Věta po Sandhi:")
        #     st.write(ss['veta_sandhi'])

        # Inicializace Processor
        json_file = ss["sandhi_pravidla_file"]
        skupiny = ss["sandhi_skupiny"]
        pravidla = ss["sandhi_pravidla"]
        # pravidla = ss['sandhi_pravidla_file']
        processor = SandhiProcessor(json_file=json_file, skupiny=skupiny, pravidla=pravidla)

        # Zpracuj sandhi do veta_tran_cz_sandhi
        # Provedení Sandhi
        veta_tran_cz_sandhi, veta_tran_cz_sandhi_zmeny = processor.aplikuj_sandhi(veta_tran_cz)
        # veta_tran_cz_sandhi = veta_tran_cz  # Prozatím bez změn

        # Uložení výsledků
        ss["veta_tran_cz_sandhi"] = veta_tran_cz_sandhi  # věta po sandhi CZ
        ss["veta_tran_cz_sandhi_zmeny"] = veta_tran_cz_sandhi_zmeny  # Výstup
        # zobraz_toast(f"Po sandhi >{veta_tran_cz_sandhi}<", trvani = 5)

        # (pokud provede sandhi tak i transliteraci - auto - odchytí stav)
        # aplikuj_transliteraci()

        # st.write(f"Věta cz po Sandhi: >{veta_tran_cz_sandhi}<")
        # st.write("Změny provedené Sandhi:")
        # for zmena in veta_tran_cz_sandhi_zmeny:
        #     st.write(f" - {zmena['index']+1}. `{zmena['puvod']}` → `{zmena['novy']}` (pravidlo: {zmena['pravidlo']})")
        # st.write(f"Věta IAST po Sandhi: >{ss['veta_tran_iast_sandhi']}<")
        # st.write(f"Věta Dev po Sandhi:  >{ss['veta_dev_sandhi']}<")

        # ss['f_aplikuj_sandhi'] = False # Uvolnění tlačítka "Aplikuj Sandhi"
        # # st.success("Sandhi aplikováno!")

        return True
    return False


# ==============================================================================================================================================


def aplikuj_transliteraci() -> bool:

    ss = st.session_state

    if (
        "veta_tran_cz_sandhi" not in ss
        or not ss["veta_tran_cz_sandhi"]
        or ss["veta_tran_cz_sandhi"] == ""
    ):
        pass
    else:
        # 1. vezmi větu po sandhi
        veta_tran_cz_sandhi = ss["veta_tran_cz_sandhi"]  # Výstup

        # 2. proveď transliteraci
        veta_tran_iast_sandhi = transliterate_czech_v_to_iast(veta_tran_cz_sandhi)
        veta_dev_sandhi = transliterate_czech_v_to_deva(veta_tran_cz_sandhi)
        # veta_dev_sandhi                           = transliterate_iast_to_deva(veta_tran_iast_sandhi)

        # 3. ulož výsledky do session_state
        ss["veta_tran_iast_sandhi"] = veta_tran_iast_sandhi  # věta po sandhi IAST
        ss["veta_dev_sandhi"] = veta_dev_sandhi  # věta po sandhi devanagari

        # Naplnění prázdné věty, případně přepsání aktuální větou v 7 verzích
        prazdna_veta()

        return True
    return False


# ==============================================================================================================================================


def export_vety() -> bool:

    ss = st.session_state

    if ss.get("f_export_vety", False):
        if "veta_tran_cz" not in ss or not ss["veta_tran_cz"]:
            return False

        # st.download_button(
        #         label="Export věty",
        #         data=export_vetu(ss['veta_sandhi']),
        #         file_name="veta.txt"
        #     )
        # ss['f_export_vety'] = False # Uvolnění tlačítka "Export věty"
        # st.success("📝 Věta exportována!")

        return True
    return False


# ==============================================================================================================================================


def ne_sestav_vetu() -> bool:

    ss = st.session_state

    if ss.get("f_ne_sestav_vetu", False):
        # Výmaz výpisu celé věty
        ss["veta_tran_cz_popis"] = ""  # věta s popisem
        ss["veta_tran_cz"] = ""  # věta bez popisu CZ
        ss["veta_tran_iast"] = ""  # věta bez popisu IAST
        ss["veta_cz"] = ""  # věta CZ
        ss["veta_tran_cz_sandhi"] = ""  # věta po sandhi CZ
        ss["veta_tran_iast_sandhi"] = ""  # věta po sandhi IAST
        ss["veta_dev_sandhi"] = ""  # věta po sandhi dev
        ss["matice_vet"] = []  # každý prvek: {"Varianta": ..., "Věta": ...}
        prazdna_veta()  # prázdná tabulka s 7 variantami

        return True
    return False


# ==============================================================================================================================================


def smaz_vetu() -> bool:

    ss = st.session_state

    if ss.get("f_smaz_vetu", False):
        # definována jako list (seznam), dict (slovníků) na řádku,
        ss["matice_vety"] = []
        # dict dočasný slovník pro aktuální slovo
        ss["matice_nove_slovo"] = {}
        # aktuálně vybrané slovo (ještě než se vloží do věty) pro zobrazení názvu slova
        ss["slovo"] = ""
        # to, co se zobrazuje jako průběžný výpis parametrů vybraného slova
        ss["matice_vypis"] = {}
        # výchozí slovník
        ss["slovnik"] = "hlavni"
        # režim ladění vypnut
        # ss['f_debug'] = False

        return True
    return False


# ==============================================================================================================================================
# ================================================================
# Vyskloňuj
# ================================================================

# Chci vytvořit funkci Vyskloňuj
# tj. ve všech pádech, číslech se zachováním rodu a
# vložením do verzí seznamu slov věty,
# pak sestav verze věty, sandhi, transliterace IAST, DEV.

# ChatGPT řekl:
# Rozumím — chceš funkci vysklonuj(), která:
# 1. Vezme vybrané slovo (s rodem).
# 2. Vygeneruje všechny pády (1.–8.) ve všech číslech (sg, du, pl).
# 3. Zachová rod.
# 4. Vloží každý tvar jako samostatnou verzi slova do seznamu variant věty.
# 5. Sestaví z toho všechny možné verze věty.
# 6. Na každou verzi aplikuje sandhi.
# 7. Vygeneruje IAST přepis.
# 8. Vygeneruje dévanágarí (DEV).

# ==============================================================================================================================================


# 1. Získání tvarů pro slovo
def sklonuj_slovo(slovo, rod, vzor):
    # rod: "m" | "f" | "n"
    # vzor: např. "a-kmen", "i-kmen"
    pady = [
        "nominativ",
        "akuzativ",
        "instrumentál",
        "datív",
        "ablatív",
        "genitiv",
        "lokativ",
        "vokativ",
    ]
    cisla = ["sg", "du", "pl"]

    # Tady by se načetla koncovková tabulka podle rodu a vzoru
    KONCOVKY = ["-a", "-am", "-ena"]  # příklad
    tabulka_koncovek = KONCOVKY[vzor][rod]

    tvary = []
    for i, pad in enumerate(pady):
        radek = []
        for j, cislo in enumerate(cisla):
            tvar = slovo + tabulka_koncovek[i][j]
            radek.append(tvar)
        tvary.append(radek)
    return tvary  # [ [sg, du, pl], [sg, du, pl], ... ]


# ==============================================================================================================================================


# 2. Vytvoření verzí věty
def vytvor_verze_vety(veta_slova, index, tvary, rod):
    # veta_slova = ["rámaḥ", "gaččhati"]
    # index = pozice slova, které skloňujeme
    verze = []
    for i, radek in enumerate(tvary):  # pro každý pád
        for j, tvar in enumerate(radek):  # pro každé číslo
            nova_veta = veta_slova.copy()
            nova_veta[index] = tvar
            verze.append(
                {"pad": i + 1, "rod": rod, "cislo": ["sg", "du", "pl"][j], "veta": nova_veta}
            )
    return verze


# ==============================================================================================================================================


# 3. Sandhi aplikace + IAST + Dévanágarí
#    Tady použijeme existující pravidla sandhi.json:
def y_aplikuj_sandhi(slova):
    spojena = " ".join(slova)
    # Aplikace pravidel sandhi
    SANDHI_PRAVIDLA = {"a+a": "ā", "a+i": "e"}  # příklad
    for pravidlo in SANDHI_PRAVIDLA:
        spojena = spojena.replace(pravidlo["pred"], pravidlo["po"])
    return spojena


# ==============================================================================================================================================


def transliterace(slova, typ="IAST"):
    if typ == "IAST":
        return [transliterate_czech_v_to_iast(s) for s in slova]
    elif typ == "DEV":
        return [transliterate_czech_v_to_deva(s) for s in slova]


# ==============================================================================================================================================


# 4. Finální funkce vyskloňuj()
def vysklonuj(slovo, rod, vzor, veta_slova, index):
    tvary = sklonuj_slovo(slovo, rod, vzor)
    verze_vety = vytvor_verze_vety(veta_slova, index, tvary, rod)

    vysledky = []
    for v in verze_vety:
        bez_sandhi_text = v["veta"]
        sandhi_text = aplikuj_sandhi(bez_sandhi_text)
        vysledky.append(
            {
                "pad": v["pad"],
                "rod": rod,
                "cislo": v["cislo"],
                "bez_sandhi": bez_sandhi_text,
                "sandhi": sandhi_text,
                "iast": transliterace(v["veta"], "IAST"),
                "dev": transliterace(v["veta"], "DEV"),
            }
        )
    return vysledky


# =======================================================================================================
# TESTY
# =======================================================================================================

# import streamlit as st

# st.title("📜 Sanskrit Sentence Builder - Výběr parametrů slova")

# --- Callback ---
# def aktualizuj_vyber():
#     ss['vypis'] = (
#         f"Pád: {ss['pad']}, "
#         f"Rod: {ss['rod']}, "
#         f"Číslo: {ss['cislo']}"
#     )


# def TEST1():
#     # Nastav výchozí hodnotu
#     if "pad" not in ss:
#         ss["pad"] = "N"

#     if "rod" not in ss:
#         ss["rod"] = "f"

#     if "cislo" not in ss:
#         ss["cislo"] = "sg."

#     # --- Segmented controls ---
#     pad = st.segmented_control(
#         "Vyber pád",
#         options=["N", "Ak", "I", "D", "Abl", "G", "L", "V"],
#         key="pad",
#         # index=0,
#         help="Vyber pád",
#         on_change=aktualizuj_vyber,
#     )

#     rod = st.segmented_control(
#         "Vyber rod",
#         options=["m", "n", "f"],
#         key="rod",
#         # index=0,
#         disabled=True,
#         on_change=aktualizuj_vyber,
#     )

#     cislo = st.segmented_control(
#         "Vyber číslo",
#         options=["sg.", "du.", "pl."],
#         key="cislo",
#         # index=0,
#         on_change=aktualizuj_vyber,
#     )

#     # --- Výpis aktuálního výběru ---
#     if 'vypis' not in ss:
#         aktualizuj_vyber()

#         # ss['vypis'] = ""

#         # při tomto zápisu nevoláš ji, jen jí přiřadíš referenci
#         # ss['vypis'] = aktualizuj_vyber # ss['vypis'] je teď funkce
#         # To znamená, že později můžeš funkci zavolat přes:
#         # ss['vypis']()

#         st.info(ss['vypis'])

# # Takže workflow je opravdu:
# # Uživatel změní widget →
# # ss[key] je okamžitě aktualizováno →
# # on_change() běží →
# # rerun celé skriptu →
# # všechny widgety znovu vykresleny s hodnotami ze session_state (a může ragovat na změny, stav) →
# # čeká


# def TEST2():
#     # --- Inicializace výchozích hodnot ---
#     defaults = {"pad": "N", "rod": "f", "cislo": "sg."}
#     for k, v in defaults.items():
#         if k not in ss:
#             ss[k] = v

#     # --- Definice parametrů pro segmented controls ---
#     widgets = [
#         ("Vyber pád", "pad", ["N", "Ak", "I", "D", "Abl", "G", "L", "V"], False),
#         ("Vyber rod", "rod", ["m", "n", "f"], True),
#         ("Vyber číslo", "cislo", ["sg.", "du.", "pl."], False),
#     ]

#     # --- Vykreslení widgetů ---
#     for label, key, options, disabled in widgets:
#         st.segmented_control(
#             label,
#             options=options,
#             key=key,
#             disabled=disabled,
#             on_change=aktualizuj_vyber
#         )

#     # --- Inicializace výpisu, pokud ještě neexistuje ---
#     if "vypis" not in ss:
#         aktualizuj_vyber()

#     # --- Zobrazení aktuálního výběru ---
#     st.info(ss['vypis'])


# # --- Funkce pro zjednodušené vytvoření widgetu ---
# def st_widget(label, key=None, help: str | None = None, **kwargs):
#     # kwargs mohou obsahovat např. on_change, disabled, index atd.
#     return st.segmented_control(label=label, key=key, help=help, **kwargs)
#     # return st.selectbox(label=label, key=key, help=help, **kwargs)


# def akce_tlacitka3():
#     # proved akci
#     st.write("Tlačítko bylo stisknuto a akce vykonána")
#     # reset stavu, aby mohlo být znovu použito
#     ss["btn_click"] = False


# def TEST3():

#     ss = st.session_state

#     if "init" not in ss:
#         ss['init'] = 0
#     else:
#         ss['init'] += 1
#     st.sidebar.write("**ss['init']:**", ss.get('init'))

#     st.button("Klikni mě", key="btn_click", on_click=akce_tlacitka3)

#     return

#     if ss.get("btn_click"):
#         st.write("Před - Tlačítko bylo stisknuto.")
#         ss['btn_click'] = False
#     else:
#         st.write("Před - Tlačítko není stisknuto, nebo bylo uvolněno.")

#     st.button("Klikni mě", key="btn_click")

#     if ss.get("btn_click"):
#         st.write("Po - Tlačítko bylo stisknuto.")
#     else:
#         st.write("Po - Tlačítko není stisknuto, nebo bylo uvolněno.")

#     return

#     st.write("Aktuální stav 1 před:", ss.get("f_vloz_do_matice_vety_tl1_", False))
#     st.write("Aktuální stav 2 před:", ss.get("f_vloz_do_matice_vety_tl2_", False))

#     ss["f_vloz_do_matice_vety_tl1_"] = st.button(
#         "Klikni 1 (s on_click)",
#         key="f_vloz_do_matice_vety_tl1",
#     )

#     ss["f_vloz_do_matice_vety_tl2_"] = st.button(
#         "Klikni 2 (s on_click)",
#         key="f_vloz_do_matice_vety_tl2",
#     )

#     st.write("Aktuální stav 1 po:", ss.get("f_vloz_do_matice_vety_tl1_", False))
#     st.write("Aktuální stav 2 po:", ss.get("f_vloz_do_matice_vety_tl2_", False))

#     return

#     funkce = inspect.currentframe().f_code.co_name
#     # st.divider()KUS
#     # st.info(funkce)

#     # Výchozí hodnoty
#     if "pad" not in ss:
#         ss["pad"] = "N"
#     if "rod" not in ss:
#         ss["rod"] = "f"
#     if "cislo" not in ss:
#         ss["cislo"] = "sg."
#     if "vypis" not in ss:
#         aktualizuj_vyber()

#     # --- Expander místo help ---
#     # help_pad = "Vyber správný pád pro slovo"
#     help_pad = (
#             """N = Nominativ (kdo? co?)  .
#             Ak = Akuzativ (koho? co?)  .
#             I = Instrumentál (kým? čím?)  .
#             D = Dativ (komu? čemu?)  .
#             Abl = Ablativ (od koho? od čeho?)  .
#             G = Genitiv (koho? čeho? čí?)  .
#             L = Lokál (o kom? o čem?)  .
#             V = Vokativ (oslovení)"""
#         )

#     # with st.expander("🔍 Debug – aktuální stav"):
#     #     st.write("Zde se zobrazí ladicí informace")
#     #     st.json({"mód": "editace", "index": 2})

#     # with st.expander("ℹ️ Popis pádu"):
#     #     st.write(help_pad)

#     # --- Widgety ---
#     pad = st_widget(
#         "Vyber pád",
#         key="pad",
#         help=help_pad,
#         options=["N", "Ak", "I", "D", "Abl", "G", "L", "V"],
#         on_change=aktualizuj_vyber
#     )

#     rod = st_widget(
#         "Vyber rod",
#         key="rod",
#         help="Mužský / ženský / střední",
#         options=["m", "n", "f"],
#         disabled=False,
#         on_change=aktualizuj_vyber
#     )

#     cislo = st_widget(
#         "Vyber číslo",
#         key="cislo",
#         help="Jednotné / dvojné / množné",
#         options=["sg.", "du.", "pl."],
#         on_change=aktualizuj_vyber
#     )

#     # --- Výpis aktuálního výběru ---
#     st.info(ss['vypis'])
