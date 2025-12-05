# app.py
#
# Obsahuje:
# main, zpracuj_akce
#
# Volá:
# if_dir_exist, if_file_exist, load_css, init_session_state_on_startup, zobraz_hlavni_layout, zpracuj_akce,
# zobraz_slova_vety, zobraz_toast, vloz_slovo_do_matice_vety, vysklonuj_slovo_do_vety, sestav_vetu, aplikuj_sandhi,
# aplikuj_transliteraci, export_vety, ne_sestav_vetu, smaz_vetu

# Podtržené je nepoužito
# svislá čára vlevo
#  - zelená  - smaž nevyužité řádky
#  - červená - přidej importy, které chybí
#  - modrá   - přidej importy, které jsou v aplikaci použity, ale nejsou v tomto souboru

# Standardní knihovny
# Importy pro práci se soubory
import os

# Importy
# Knihovny třetích stran
import streamlit as st
import pandas as pd

# Základní moduly

# Vlastní moduly
from helpers.ui_display import (
    zobraz_toast,
    zobraz_vetu,
    vypis_konfiguraci,
    vypis_streamlit_system_info,
)

from helpers.session_state_defaults import (
    load_css,
    init_session_state_on_startup,
)

# from helpers.sandhi_processor import apply_sandhi_python, apply_sandhi_regex, SandhiProcessor

from helpers.utils import (
    if_dir_exist,
    if_file_exist,
    sestav_vetu,
    aplikuj_sandhi,
    aplikuj_transliteraci,
    export_vety,
    ne_sestav_vetu,
    smaz_vetu,
    prazdna_veta,
    vloz_slovo_do_matice_vety,
    vysklonuj_slovo_do_vety,
    # TEST1,
    # TEST2,
    # TEST3,
)

from helpers.ui_layout import (
    zobraz_hlavni_layout,
    vypis_tvaru_slova,
    zobraz_slova_vety,
    zobraz_tlacitka_pro_vlozeni_do_matice_vety,
)

from helpers.forms import vyber_slova_form
from helpers.loader_csv import nacti_soubor, nacti_csv
from helpers.sklonovani import ziskej_koncovku_padu_k, sklonuj_k
from helpers.casovani import ziskej_koncovku_casu_k, ziskej_koncovku_casu_d

from helpers.transliterate import (
    transliterate_iast_to_deva,
    transliterate_deva_to_iast,
    transliterate_iast_to_czech_v,
    transliterate_czech_v_to_iast,
    transliterate_czech_v_to_deva,
    transliterate_iast_to_czech_f,
    transliterate_iast_to_czech_l,
)

# Kontrola existence složky programových modulů
# Kontrola existence datové složky
if_dir_exist("adresare_projektu.csv")  # utils

# Kontrola existence souborů programových modulů
# Kontrola existence datových souborů
if_file_exist("soubory_projektu.csv")  # utils


# ---------------------------------------------------------
# Hlavní funkce aplikace
# ---------------------------------------------------------
# if True:


# po vytvoření st.session_state lze zavolat
def main():
    # odtud se spouští st.rerun()
    # tzn. pokud při svém běhu narazí na další st.rerun() vrací se sem
    # tzn. že každý st.rerun() musí být za něčím skryt aby nebyl v cestě linearního běhu aplikací

    ss = st.session_state

    # a v ní vytvořit st.session_state proměnné

    # -------------------------------------------------
    # 0. Konfigurace stránky
    # 1️⃣ Konfigurace stránky
    # -------------------------------------------------
    # st.set_page_config(page_title = "1. Sandhi Processor", layout = "wide")
    # st.set_page_config(page_title = "Sanskrtská aplikace", layout = "wide")
    # st.title("2. Sandhi Processor")

    # -------------------------------------------------
    # 1. 1️⃣ Načtení CSS stylu
    # -------------------------------------------------
    # Styl
    # CSS
    # otevři
    load_css()  # session_state_defaults

    # TEST3()

    # return

    if "cfg" not in ss:
        pass

        # zavři
        # vypis_streamlit_system_info()
        # vypis_konfiguraci()

        # return

        # -------------------------------------------------
        # 2. Inicializace session_state
        # -------------------------------------------------
        # otevři
        # session_state_defaults
        init_session_state_on_startup()

    if ss.get("index_edit_word") is None:
        ss["index_edit_word"] = -1

    # ===========================================================
    # original_warning = st.warning

    # def debug_warning(*args, **kwargs):
    #     print("WARNING called:", args, kwargs)
    #     return original_warning(*args, **kwargs)

    # st.warning = debug_warning
    # ===========================================================

    # -------------------------------------------------
    # 4. Hlavní rozhraní
    # -------------------------------------------------
    # 🧭 Hlavní rozhraní (výběr směru překladu)
    # A volání v hlavním běhu aplikace:
    # otevři
    zobraz_hlavni_layout()  # ui_layout
    # a zavolá i vyber_slova_form()  # forms.py
    # a vytvoření tlačítek formuláře

    # 8️⃣ Akce tlačítek (reaktivní logika)
    # if ss['smer_prekladu'] == ss['volby_smer_prekladu'][0]:
    # otevři
    # toto by mělo být až po všech zobrazeních
    # místo toho dát skupinu na odchycení stavů
    # a provedení dát do utils
    zpracuj_akce()  # app


# -------------------------------------------------
# 🧩 Akce tlačítek – odděleně, přehledně
# -------------------------------------------------
def _akce_zmena_smeru():

    ss = st.session_state

    if ss.get("f_smer_zmenen"):
        zobraz_toast(f"Směr změněn na {ss['smer_prekladu']}")  # ui_layout
        ss["f_smer_zmenen"] = False


def _f_cfg():

    ss = st.session_state

    if ss.get("index_edit_word") is None:
        ss["index_edit_word"] = -1

    if ss["cfg"]["f_auto_sandhi"]:
        if ss["f_sestav_vetu"]:
            ss["f_aplikuj_sandhi"] = True

    if ss["f_aplikuj_sandhi"]:
        ss["f_aplikuj_transliteraci"] = True


def _akce_vlevo():

    ss = st.session_state

    # 🟦 1. Sestavení věty

    # -------------------------------------------------
    # 7. --- Vložení slova do matice věty ---
    # 🧩 BLOK PRO VLOŽENÍ / SKLOŇOVÁNÍ SLOVA DO VĚTY
    # -------------------------------------------------
    # if "matice_nove_slovo" in ss and ss['matice_nove_slovo']: # zkontroluje, zda existuje a není prázdný

    # 2️⃣ Logika po stisku tlačítek
    # 🧩 2️⃣ Ale akce dovol jen tehdy, pokud je co vkládat
    if ss.get("f_vloz_do_matice_vety"):
        # if ss.get("matice_nove_slovo"):  # zkontroluje, zda existuje a není prázdný
        # nove_slovo = ss.get("matice_nove_slovo", {})
        nove_slovo = ss.get("matice_nove_slovo")

        if nove_slovo is None:
            zobraz_toast("⚠️ Chybí klíč matice_nove_slovo – nebyla provedena inicializace.")
        else:
            # z_index = ss.get("index_edit_word", None)
            # zobraz_toast(f"Tlačítko - ukládám index {z_index}. slovo.", trvani=5)  # ui_layout

            if nove_slovo and any(v for v in nove_slovo.values()):
                vloz_slovo_do_matice_vety()  # (utils.py) z leva do prava
            else:
                zobraz_toast("⚠️ Neexistuje žádné nové slovo k vložení.")  # ui_layout

        # Reset po pokusu o vložení
        # Vyprázdní pro další slovo
        ss["matice_nove_slovo"] = {}
        # Reset indexu - "slovo zpět ku tvarování" - po uložení slova do věty
        # vrátit slovo na tvarování i = index slova ve větě
        ss["index_edit_word"] = None
        ss["f_edit"] = False
        # Vrátit slovo na tvarování i = index slova ve větě
        ss["f_vloz_do_matice_vety"] = False
        st.rerun()

    if ss.get("f_vysklonuj"):
        if ss.get("matice_nove_slovo"):  # zkontroluje, zda existuje a není prázdný
            vysklonuj_slovo_do_vety()  # (utils.py)
        else:
            zobraz_toast("⚠️ Není co skloňovat.")
        # Reset po vyskloňování
        ss["matice_nove_slovo"] = {}  # vyprázdní pro další slovo
        ss["f_vysklonuj"] = False
        st.rerun()

    # 3️⃣ Po akci: volitelné resetování / vyčištění
    # if "matice_nove_slovo" not in ss:
    #     ss['matice_nove_slovo'] = {}


def _akce_sestaveni_vety():

    ss = st.session_state

    # -------------------------------------------------
    # 8. Sestavení věty - Spojení slov → věta (cz, tran_cz_popis, tran_cz značky pro sandhi, tran_cz_sandhi, tran_iast_sandhi, dev_sandhi)
    # -------------------------------------------------
    # Když uživatel stiskne tlačítko pro sestavení věty
    if ss.get("f_sestav_vetu", False):
        if sestav_vetu():  # utils (pokud provede sandhi tak i transliteraci)
            # zobraz_vetu() # ! Vyvolává duplicitu klíče
            zobraz_toast(text="📝 Věta sestavena!", trvani=2.5)
            # st.rerun()
        else:
            zobraz_toast(text="1. Matice věty je prázdná.", icon="⚠️", trvani=2.5)
            # st.warning("Matice věty není definována nebo je prázdná.")
        ss["f_sestav_vetu"] = False  # Uvolnění tlačítka "Sestav větu"
        st.rerun()


def _akce_sandhi():

    ss = st.session_state

    # ----------------------------------------------------
    # 9.1. Aplikace, Provedení sandhi (do tran_cz_sandhi)
    # ----------------------------------------------------
    # Když uživatel stiskne tlačítko pro aplikaci sandhi
    if ss.get("f_aplikuj_sandhi", False):
        if aplikuj_sandhi():  # utils (pokud provede sandhi tak i transliteraci)
            st.sidebar.write("veta_tran_cz_sandhi", ss["veta_tran_cz_sandhi"])
            # st.sidebar.write("Po sandhi:", ss.get('matice_vety'))
            zobraz_toast(text="📝 Sandhi aplikováno!", trvani=2.5)
        else:
            zobraz_toast(text="2. Matice věty je prázdná.", icon="⚠️", trvani=2.5)
            # st.warning("Věta není definována nebo je prázdná.")
        ss["f_aplikuj_sandhi"] = False  # Uvolnění tlačítka "Aplikuj Sandhi"
        st.rerun()
        # -------------------------------------------------

    if ss.get("f_aplikuj_transliteraci", False):
        # ---------------------------------------------------
        # 9.2. Transliterace (tran_iast_sandhi, dev_sandhi))
        # ---------------------------------------------------
        if (
            "veta_tran_cz_sandhi" not in ss
            or not ss["veta_tran_cz_sandhi"]
            or ss["veta_tran_cz_sandhi"] == ""
        ):
            pass
        else:  # (pokud provede sandhi tak i transliteraci - odchytí stav "veta_tran_cz_sandhi")
            aplikuj_transliteraci()  # utils
        ss["f_aplikuj_transliteraci"] = False  # Uvolnění tlačítka "Aplikuj transliteraci"
        st.rerun()


def _akce_vpravo():

    ss = st.session_state

    # -------------------------------------------------
    # 10. Export věty
    # -------------------------------------------------
    # Když uživatel stiskne tlačítko pro export věty
    if ss.get("f_export_vety", False):
        if export_vety():  # utils
            zobraz_toast(text="📝 Věta exportována!", trvani=2.5)
        else:
            zobraz_toast(text="3. Matice věty je prázdná.", icon="⚠️", trvani=2.5)
        # Uvolnění tlačítka "Export věty"
        ss["f_export_vety"] = False
        st.rerun()

    # -------------------------------------------------
    # 11. Bez sestavení
    # -------------------------------------------------
    # Když uživatel stiskne tlačítko "Bez sestavení" věty
    if ss.get("f_ne_sestav_vetu", False):
        if ne_sestav_vetu():  # utils
            # zobraz_vetu() # ! Vyvolává duplicitu klíče
            # render_sentence_matrix(ss['matice_vety']) # průběžně zobrazuje položky věty - přidaná slova.
            zobraz_toast(text="📝 Věta nesestavena!", trvani=2.5)
        # Uvolnění tlačítka "Bez sestavení"
        ss["f_ne_sestav_vetu"] = False
        st.rerun()

    # -------------------------------------------------
    # 12. Smazání věty
    # -------------------------------------------------
    # Když uživatel stiskne tlačítko pro smazání věty
    if ss.get("f_smaz_vetu", False):
        if smaz_vetu():  # utils
            # zobraz_vetu() # ! Vyvolává duplicitu klíče
            # render_sentence_matrix(ss['matice_vety']) # průběžně zobrazuje položky věty - přidaná slova.
            zobraz_toast(text="📝 Věta smazána!", trvani=2.5)
        # Uvolnění tlačítka "Smaž větu"
        ss["f_smaz_vetu"] = False

        # Výmaz výpisu celé věty
        # Stisknutí tlačítka "Bez sestavení"
        ss["f_ne_sestav_vetu"] = True
        st.rerun()


def zpracuj_akce():
    _akce_zmena_smeru()
    _f_cfg()
    _akce_vlevo()
    _akce_sestaveni_vety()
    _akce_sandhi()
    _akce_vpravo()


if __name__ == "__main__":
    main()
