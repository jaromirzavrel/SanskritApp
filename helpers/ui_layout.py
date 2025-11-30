# helpers/ui_layout.py
#
# Obsahuje:
# nastyluj_sloupce, zobraz_prepinac_smeru, layout_cz_do_sanskrt, layout_sanskrt_do_cz, zobraz_hlavni_layout,
# zobraz_tlacitka_pro_vlozeni_do_matice_vety, zobraz_label_hodnotu, vypis_tvaru_slova, presun_hore, presun_dolu,
# smaz_slovo, uprav_slovo, zobraz_slova_vety, render_sentence_matrix_0
#
# Volá:
# vyber_slova_form, vypis_tvaru_slova, zobraz_tlacitka_pro_vlozeni_do_matice_vety, render_sentence_matrix_0,
# zobraz_vetu, vypis_nove_slovo, nastyluj_sloupce, zobraz_prepinac_smeru, layout_cz_do_sanskrt,
# layout_sanskrt_do_cz, zobraz_label_hodnotu, urci_koncovku
#
# Nevyužito:
# test_radku_0, radek_hybrid, radek_flexbox, radek_sloupce,
# mini_button_html_1, mini_button_html_0, render_sentence_matrix_c, render_sentence_matrix_1, render_text_row,
# mini_button, mini_button_0

# ✅ Co máme teď:
# 🔘 Přepínač větve překladu
# 📥 Vstupní pole pro větu v češtině
# 📤 Vstupní pole pro sanskrtskou větu
# 🧱 Základní strukturu layoutu pro obě větve

# Importy
import streamlit as st
import inspect
import os

# import pandas as pd
# import streamlit.runtime.config as _cfg
import streamlit.components.v1 as components
import uuid

# import hashlib
# import json

# Vlastní moduly
from dataclasses import dataclass, field
from typing import Sequence, Optional, List, Dict, Any
from functools import partial

# from datetime         import datetime
from helpers.ui_display import (
    zobraz_toast,
    zobraz_vetu,
    vypis_konfiguraci,
    dump_state,
)

from helpers.forms import vyber_slova_form
from helpers.utils import urci_koncovku

# Obecné
# ================================================================
# icon=emoji (⚠️, ℹ️, ✅ …)

# Úvod
# ================================================================


@dataclass
class TvarSlova:
    # Zdroj:
    typ: str = ""
    cz: str = ""
    x_kmen: str = ""  # a-, i-, u- kmen
    kmen_tran_cz: str = ""
    tran_prezens_3sg: str = ""
    tran_ppp: str = ""
    kmen_dev: str = ""
    dev_prezens_3sg: str = ""
    dev_ppp: str = ""
    # Parametry:
    cas: str = ""
    pad: str = ""
    pada: str = ""
    aktiv: str = ""
    rod: str = ""
    osoba: str = ""
    cislo: str = ""
    # Tvarování:
    prefix: str = ""
    kmen_0_tran_cz: str = ""
    koncovka_tran_cz: str = ""
    slovo_tran_cz: str = ""
    slovo_tran_iast: str = ""
    slovo_dev: str = ""
    # Dodatek:
    variant: str = ""
    pozice: str = ""
    funkce: str = ""
    poznamka: str = ""


@dataclass
class WordData:
    typ: str = ""
    cz: str = ""
    prefix: str = ""
    kmen: str = ""
    pripona: str = ""
    popis1: str = ""
    popis2: str = ""
    popis3: str = ""
    popis4: str = ""
    dev: str = ""

    # volitelná specifika pro různé typy
    cas: Optional[str] = None
    aktivita: Optional[str] = None
    pada: Optional[str] = None
    osoba: Optional[str] = None
    rod: Optional[str] = None
    cislo: Optional[str] = None


# Funkce pro bezpečné vytvoření TvarSlova z dictu
def create_tvar_slova_from_dict(d: dict) -> TvarSlova:
    """Vytvoří objekt TvarSlova, doplní chybějící klíče default hodnotami."""

    # Získáme všechna pole z dataclass
    fields = {f.name for f in TvarSlova.__dataclass_fields__.values()}

    # Vyplníme dict chybějícími poli default ""
    safe_dict = {key: d.get(key, "") for key in fields}
    return TvarSlova(**safe_dict)


# ================================================================


def nastyluj_sloupce():

    ss = st.session_state

    f_test_sloupcu = ss["cfg"]["f_test_sloupcu"]

    if f_test_sloupcu:
        st.markdown(
            """
            <style>
            div[data-testid="column"] {
                border:  1px dashed gray;
                padding: 10px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <style>
            div[data-testid="column"] {
                border:  none;
                padding: 0px;
                margin:  0px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


# ================================================================


def zobraz_prepinac_smeru(col1, col2, col3, col4, col5, col6):

    ss = st.session_state

    f_test_sloupcu = ss["cfg"]["f_test_sloupcu"]

    # otevři
    # return ss["smer_prekladu"]

    with col1:
        if f_test_sloupcu:
            st.markdown(
                """
            <div style="border: 2px solid red; padding: 10px;">
                Sloupec 1
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
            <div style="border: none; padding: 0px;">
                &nbsp;
            </div>
            """,
                unsafe_allow_html=True,
            )

        volby = ss["volby_smer_prekladu"]

        st.radio(
            label="Směr:",
            options=volby,
            horizontal=True,
            key="smer_prekladu",
            label_visibility="collapsed",
            on_change=lambda: ss.update(
                {
                    "smer_index": volby.index(ss["smer_prekladu"]),
                    "f_smer_zmenen": True,
                }
            ),
        )
        # st.write(f"(>{volba}<)")
    # return volba
    return ss["smer_prekladu"]


# Úvod
# ================================================================
# --- pravý panel: tlačítka ---
# Jednotná logika tlačítek — jen nastaví flagy
# ================================================================


def layout_cz_do_sanskrt(col1, col2, col3, col4, col5, col6):

    ss = st.session_state

    f_test_sloupcu = ss["cfg"]["f_test_sloupcu"]
    # --- pravý panel: tlačítka ---
    # Jednotná logika tlačítek — jen nastaví flagy

    # with col1:
    # Zde je přepínač smer_prekladu
    # pass

    with col2:
        if f_test_sloupcu:
            st.markdown(
                """
            <div style="border: 2px solid green; padding: 10px;">
                Sloupec 2
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.button(
            "**Sestav větu**",
            key="sestav_vetu",
            on_click=lambda: ss.update({"f_sestav_vetu": True}),
        )

    with col3:
        if f_test_sloupcu:
            st.markdown(
                """
                <div style="border: 2px solid blue; padding: 10px;">
                    Sloupec 3
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.button(
            "**Aplikuj Sandhi**",
            key="aplikuj_sandhi",
            on_click=lambda: ss.update({"f_aplikuj_sandhi": True}),
        )

    with col4:
        if f_test_sloupcu:
            st.markdown(
                """
                <div style="border: 2px solid orange; padding: 10px;">
                    Sloupec 4
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.button(
            "**Export věty**",
            key="export_vety",
            on_click=lambda: ss.update({"f_export_vety": True}),
        )

    with col5:
        if f_test_sloupcu:
            st.markdown(
                """
                <div style="border: 2px solid orange; padding: 10px;">
                    Sloupec 5
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.button(
            "**Bez sestavení**",
            key="ne_sestav_vetu",
            on_click=lambda: ss.update({"f_ne_sestav_vetu": True}),
        )

    with col6:
        if f_test_sloupcu:
            st.markdown(
                """
                <div style="border: 2px solid orange; padding: 10px;">
                    Sloupec 6
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.button(
            "**Smaž větu**",
            key="smaz_vetu",
            on_click=lambda: ss.update({"f_smaz_vetu": True}),
        )

    # --- levý panel (sidebar): výběr a zobrazení tvarů ---
    # Sidebar — výběr slov
    # st.markdown("### 🛠️ Manuální skládání věty:")
    with st.sidebar:

        # vypis_konfiguraci()
        # pip show streamlit
        # st.write(st.__version__)
        # st.write(_cfg.get_options())
        # st.write(st.config)

        # 🔹 Formulář pro výběr slova - vlevo
        # otevři
        vyber_slova_form()  # forms.py
        # dump_state("Po vykreslení formulářů")

        # 🔹 Pokud uživatel něco vybral — zobraz průběžný výpis - vlevo
        if ss.get("matice_vypis"):
            data = create_tvar_slova_from_dict(ss["matice_vypis"])
            # otevři
            # - vlevo
            vypis_tvaru_slova(data)  # ui_layout

        # 🔹 Tlačítka (vždy zobrazit) - vlevo
        # UI: vždy zobraz ovládání pro vložení slova do věty
        zobraz_tlacitka_pro_vlozeni_do_matice_vety()  # ui_layout

    # 7️⃣ Zobrazení aktuální věty (slova - vpravo)
    # průběžně zobrazuje položky věty - přidaná slova (vpravo).
    # otevři
    zobraz_slova_vety()  # ui_layout

    # TEST TEXTU

    # st.markdown("*Streamlit* is **really** ***cool***.")
    # st.markdown('''
    # ...     :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
    # ...     :gray[pretty] :rainbow[colors] and :blue-background[highlight] text.''')
    # st.markdown("Here's a bouquet &mdash;\
    # ...             :tulip::cherry_blossom::rose::hibiscus::sunflower::blossom:")
    # st.markdown('''If you end a line with two spaces,
    # ... a soft return is used for the next line.
    # ...
    # ... Two (or more) newline characters in a row will result in a hard return.
    # ... ''')

    # st.title("st.title - Ukázka ⬆️⬇️🗑️✏️ výpisů pro větu")

    # st.header("st.header - Výsledná ⬆️⬇️🗑️✏️ věta")
    # st.subheader("st.subheader - Hlavní ⬆️⬇️🗑️✏️ forma")
    # st.write("st.write - SLOVO ⬆️⬇️🗑️✏️")

    # st.text("st.text - Trans CZ popis: + ⬆️⬇️🗑️✏️ SLOVO_popis")

    # st.markdown(f"st.markdown - **Markdown formát: ⬆️⬇️🗑️✏️ ** SLOVO — *⬆️⬇️🗑️✏️ SLOVO_popis*")

    # st.caption("st.caption - Doplňující popisek: věta ⬆️⬇️🗑️✏️ v základním tvaru.")

    # st.code(f"""
    # st.code - # Zvýrazněný kód
    # veta="SLOVO ⬆️⬇️🗑️✏️"
    # popis="SLOVO_popis"
    # print(veta, popis)
    # """, language="python")

    # st.latex(r"st.latex - E=mc^2 ⬆️⬇️🗑️✏️")  # ukázka, nesouvisí s větou

    # st.success("st.success - 📝 Věta ⬆️⬇️🗑️✏️ sestavena!")
    # st.info("st.info - Toto je ⬆️⬇️🗑️✏️ informační zpráva k větě.")
    # st.warning("st.warning - Pozor! ⬆️⬇️🗑️✏️ Ve větě může být chyba.")
    # st.error("st.error - ⬆️⬇️🗑️✏️ Chyba při načítání věty.")


# Úvod
# ================================================================
# zatím nevyužito


def layout_sanskrt_do_cz():
    # st.header("📤 Sanskrit → CZ")

    st.markdown("### 📜 Zadej sanskrtskou větu (v dévanágarí nebo transliteraci)")
    vstup_sa = st.text_input("Zadej větu:", key="vstup_sa")

    if vstup_sa:
        st.write("🔎 *Rozklad na slova, rozpoznání sandhi, analýza tvarů a překlad*")

    st.markdown("🧾 Analytický rozklad:")
    # Později sem přidáme bloky výstupu rozboru a překlad


# Úvod
# ================================================================


def zobraz_hlavni_layout():

    ss = st.session_state

    # st.write("DEBUG: session_state keys:", list(ss.keys()))
    # st.markdown(f"🧩 zobraz_hlavni_layout ({id(form_editace)})")

    # otevři
    nastyluj_sloupce()

    col1, col2, col3, col4, col5, col6 = st.columns([1.9, 0.9, 1.08, 0.9, 1, 3.5], gap="small")
    smer = zobraz_prepinac_smeru(col1, col2, col3, col4, col5, col6)

    # if smer == "cz → sanskrt":
    if smer == ss["volby_smer_prekladu"][0]:
        pass
        # otevři
        layout_cz_do_sanskrt(col1, col2, col3, col4, col5, col6)
    else:
        layout_sanskrt_do_cz()


# Vstup - vlevo
# ================================================================================================================================
# Tlačítka pod formulářem


def zobraz_tlacitka_pro_vlozeni_do_matice_vety():

    ss = st.session_state

    """Zobrazí tlačítka pro vložení nebo skloňování slova do matice věty."""
    with st.sidebar:
        st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            # 1️⃣ Vložit hotové slovo
            st.button(
                "📌 **Vložit slovo do věty**",
                key="vloz_do_matice_vety",
                on_click=lambda: ss.update({"f_vloz_do_matice_vety": True}),
            )

        with col2:
            # 2️⃣ Vyskloňovat a vložit
            st.button(
                "📌 **Vyskloňuj a vlož**",
                key="vysklonuj",
                on_click=lambda: ss.update({"f_vysklonuj": True}),
            )


# Volba tvaru - vlevo
# ================================================================


# Výpis, popis tvaru voleného slova
def zobraz_label_hodnotu(
    label: str = "",
    prefix: str = "",
    kmen: str = "",
    pripona: str = "",
    popis1: str = "",
    popis2: str = "",
    popis3: str = "",
    popis4: str = "",
    border_width: int = 1,
    sirka1: int = 205,
    div3_popis1: str = "",
    sirka2: int = 350,
):
    # st.sidebar.markdown(f"""
    st.markdown(
        f"""
    <div style='display:flex; align-items:center; border-bottom: {border_width}px green solid;'>
      <!-- První div: Label -->
      <div style='width:{sirka1}px; font-weight:bold;'>{label}</div>

      <!-- Druhý div: Popis -->
      <div style='display:inline; width:{sirka2}px'>
        <span style='background-color: #00ff00; font-weight:bold;'>{prefix}</span>{kmen}<span style='background-color: #ffff38; font-weight:bold;'>{pripona}</span> <span style='font-style: italic;'>{popis1}</span><span style='font-style: italic; font-weight:bold;'>{popis2}</span><span style='background-color: #ffd428; font-style: italic; font-weight:bold;'>{popis3}</span><span style='font-style: italic;'>{popis4}</span>
      </div>

      <!-- Třetí div: dévanágarí -->
      <div style='display:inline;'>
        {div3_popis1}
      </div>

    </div>
    """,
        unsafe_allow_html=True,
    )


# Volba tvaru - vlevo
# ================================================================


def _vypis_tvaru_slova_kmen(data: TvarSlova):

    header_text = "Vybrané cz slovo s parametry a výsledný tvar:"
    st.markdown(
        f"""
    <div style='display:flex; font-weight:bold; font-size: 1.2em; align-items:center; border-bottom: 3px solid; border-color: #00bf00;'>
        {f"🧾 {header_text}"}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Vybrané slovo
    zobraz_label_hodnotu(label="🔹 Slovo cz:", kmen=data.cz)

    # Pokud se slovo tvaruje z kmene, zobrazit kmen
    if data.typ in {"sub", "adj"}:
        zobraz_label_hodnotu(
            label=f"🔹 {data.x_kmen}- Kmen tran cz v:",
            kmen=data.kmen_tran_cz,
            border_width=3,
        )  # border

    if data.typ == "verb":
        sirka1 = 205 - 5  # šířka prvního divu

        max_len = (
            max(len(f"{data.kmen_tran_cz}-"), len(data.tran_prezens_3sg), len(data.tran_ppp)) + 5
        )

        sirka2 = min(350, max_len * 5.7)  # šířka druhého divu

        zobraz_label_hodnotu(
            label="🔹 Kmen tran cz v:",
            kmen=data.kmen_tran_cz,
            div3_popis1=f"{data.kmen_dev}-",
            sirka1=sirka1,
            sirka2=sirka2,
        )

        zobraz_label_hodnotu(
            label="🔹 Tvar tran cz v 3. os. sg.:",
            kmen=data.tran_prezens_3sg,
            div3_popis1=data.dev_prezens_3sg,
            sirka1=sirka1,
            sirka2=sirka2,
        )

        zobraz_label_hodnotu(
            label=f"🔹 {data.x_kmen}- Tvar tran cz v pro PPP:",
            kmen=data.tran_ppp,
            border_width=3,
            div3_popis1=data.dev_ppp,
            sirka1=sirka1,
            sirka2=sirka2,
        )


def _vypis_tvaru_slova_rod_cas(data: TvarSlova):

    ss = st.session_state

    # Pokud se slovo tvaruje zobrazit parametry tvarování
    casy_participa_set = ss["casy_participa_set"]

    if data.typ == "verb":
        zobraz_label_hodnotu(label="🔹 Čas:", popis3=data.cas)

    if data.typ in {"sub", "adj", "pron"} or (
        data.typ == "verb" and data.cas in casy_participa_set
    ):
        zobraz_label_hodnotu(label="🔹 Rod sanskrt:", popis3=data.rod)

    if data.typ == "verb" and data.cas not in casy_participa_set:
        zobraz_label_hodnotu(label="🔹 Osoba sanskrt:", popis3=data.osoba)
        zobraz_label_hodnotu(label="🔹 Číslo:", popis3=data.cislo)

    if (
        data.typ == "pron"
        and not data.osoba == ""
        and (not data.variant == "" or not data.pozice == "")
    ):
        zobraz_label_hodnotu(label="🔹 Osoba sanskrt:", popis3=data.osoba)
    if data.typ == "pron" and not data.osoba == "" and data.variant == "" and data.pozice == "":
        zobraz_label_hodnotu(label="🔹 Osoba sanskrt:", popis3=data.osoba, border_width=3)

    if data.typ == "pron" and not data.variant == "" and not data.pozice == "":
        zobraz_label_hodnotu(label="🔹 Varianta, verze:", kmen=data.variant)
    if data.typ == "pron" and not data.variant == "" and data.pozice == "":
        zobraz_label_hodnotu(label="🔹 Varianta, verze:", kmen=data.variant, border_width=3)
    if data.typ == "pron" and not data.pozice == "":
        zobraz_label_hodnotu(label="🔹 Pozice:", kmen=data.pozice, border_width=3)


def _vypis_tvaru_slova_tvar(data: TvarSlova):
    # Tvarování slova
    if data.typ in {"sub", "adj", "verb"}:
        # zobraz_label_hodnotu(label="🔹 Kmen dévanágarí:", kmen=f"{kmen_dev}-", border_width=3)

        if data.typ == "verb":
            # Zobrazit prefix
            zobraz_label_hodnotu(label="🔹 Prefix:", prefix=data.prefix)
        # Zobrazit kmen pro skloňování
        zobraz_label_hodnotu(label="🔹 Kmen 0 tran cz v:", kmen=f"{data.kmen_0_tran_cz}-")
        # Zobrazit koncovku
        zobraz_label_hodnotu(label="🔹 Koncovka tran cz v:", pripona=f"-{data.koncovka_tran_cz}")
        # Zobrazit vyskloňované slovo - iast koncovka dodělat
        zobraz_label_hodnotu(
            label="👉 Tvar tran cz v:",
            prefix=data.prefix,
            kmen=data.kmen_0_tran_cz,
            pripona=data.koncovka_tran_cz,
            border_width=3,
        )

    if data.typ in {"pron", "ost"}:
        zobraz_label_hodnotu(label="👉 Tvar tran cz v:", kmen=data.slovo_tran_cz, border_width=3)


def _vypis_tvaru_slova_iast(data: TvarSlova):
    # Zobrazit tvar v iast a dévanágarí
    zobraz_label_hodnotu(label="🔹 Tvar tran IAST:", kmen=data.slovo_tran_iast)
    zobraz_label_hodnotu(label="👉 Tvar dévanágarí:", kmen=data.slovo_dev, border_width=3)


def _vypis_tvaru_slova_popis(data: TvarSlova):

    ss = st.session_state

    # Popis tvaru
    casy_participa_set = ss["casy_participa_set"]

    if data.typ in {"sub", "adj"}:
        zobraz_label_hodnotu(
            label="👉 Popis tvaru:",
            popis1="(",
            popis2=f"{data.pad} ",
            popis3=f"{data.rod} {data.cislo}",
            popis4=")",
        )

        zobraz_label_hodnotu(
            label="👉 Tvar tran cz v s popisem:",
            kmen=data.kmen_0_tran_cz,
            pripona=data.koncovka_tran_cz,
            popis1="(",
            popis2=f"{data.pad} ",
            popis3=f"{data.rod} {data.cislo}",
            popis4=")",
            border_width=3,
        )

    if data.typ == "verb" and data.cas in casy_participa_set:
        zobraz_label_hodnotu(
            label="👉 Popis tvaru:",
            popis1=f"({data.cas} {data.aktiv} ",
            popis2=f"{data.pad} ",
            popis3=f"{data.rod} {data.cislo}",
            popis4=")",
        )

        zobraz_label_hodnotu(
            label="👉 Tvar tran cz v s popisem:",
            prefix=data.prefix,
            kmen=data.kmen_0_tran_cz,
            pripona=data.koncovka_tran_cz,
            popis1=f"({data.cas} {data.aktiv} ",
            popis2=f"{data.pad} ",
            popis3=f"{data.rod} {data.cislo}",
            popis4=")",
            border_width=3,
        )

    if data.typ == "verb" and data.cas not in casy_participa_set:
        zobraz_label_hodnotu(
            label="👉 Popis tvaru:",
            popis1=f"({data.cas} ",
            popis2=f"{data.pada}pada {data.aktiv} ",
            popis3=f"{data.osoba} {data.cislo}",
            popis4=")",
        )

        zobraz_label_hodnotu(
            label="👉 Tvar tran cz v s popisem:",
            prefix=data.prefix,
            kmen=data.kmen_0_tran_cz,
            pripona=data.koncovka_tran_cz,
            popis1=f" ({data.cas} {data.pada} {data.aktiv} ",
            popis3=f"{data.osoba} {data.cislo}",
            popis4=")",
            border_width=3,
        )

    if (
        data.typ == "pron"
        and not data.pad == ""
        and not data.rod == ""
        and not data.osoba == ""
        and not data.cislo == ""
    ):
        zobraz_label_hodnotu(
            label="👉 Popis tvaru:",
            popis1="(",
            popis2=f"{data.pad} ",
            popis3=f"{data.rod} {data.osoba} {data.cislo}",
            popis4=")",
        )

        zobraz_label_hodnotu(
            label="👉 Tvar tran cz v s popisem:",
            kmen=data.slovo_tran_cz,
            popis1="(",
            popis2=f"{data.pad} ",
            popis3=f"{data.rod} {data.osoba} {data.cislo}",
            popis4=")",
            border_width=3,
        )

    if (
        data.typ == "pron"
        and not data.pad == ""
        and data.rod == ""
        and not data.osoba == ""
        and not data.cislo == ""
    ):
        zobraz_label_hodnotu(
            label="👉 Popis tvaru:",
            popis1="(",
            popis2=f"{data.pad} ",
            popis3=f"{data.osoba} {data.cislo}",
            popis4=")",
        )

        zobraz_label_hodnotu(
            label="👉 Tvar tran cz v s popisem:",
            kmen=data.slovo_tran_cz,
            popis1="(",
            popis2=f"{data.pad} ",
            popis3=f"{data.osoba} {data.cislo}",
            popis4=")",
            border_width=3,
        )


def _vypis_tvaru_slova_dodatek(data: TvarSlova):

    # Dodatek
    if data.typ == "pron" and not data.funkce == "" and not data.poznamka == "":
        zobraz_label_hodnotu(label="🔹 Funkce:", popis1=data.funkce)
    if data.typ == "pron" and not data.funkce == "" and data.poznamka == "":
        zobraz_label_hodnotu(label="🔹 Funkce:", popis1=data.funkce, border_width=3)
    if data.typ == "pron" and not data.poznamka == "":
        zobraz_label_hodnotu(label="🔹 Poznámka:", popis1=data.poznamka, border_width=3)


# Výpis, popis tvaru voleného slova - zápis parametrů dle slovního druhu a tvarování - vlevo
def vypis_tvaru_slova(data: TvarSlova):

    # with st.sidebar:
    if True:
        _vypis_tvaru_slova_kmen(data)
        _vypis_tvaru_slova_rod_cas(data)
        _vypis_tvaru_slova_tvar(data)
        _vypis_tvaru_slova_iast(data)
        _vypis_tvaru_slova_popis(data)
        _vypis_tvaru_slova_dodatek(data)


# ================================================================
# ================================================================
# Vložení do věty - pro vpravo
# ================================================================


def presun_hore(i):
    ss = st.session_state
    matice_vety = ss.get("matice_vety", [])
    if i > 0:
        matice_vety[i], matice_vety[i - 1] = matice_vety[i - 1], matice_vety[i]
        st.rerun()


def presun_dolu(i):
    ss = st.session_state
    matice_vety = ss.get("matice_vety", [])
    if i < len(matice_vety) - 1:
        matice_vety[i], matice_vety[i + 1] = matice_vety[i + 1], matice_vety[i]
        st.rerun()


def smaz_slovo(i):
    ss = st.session_state
    matice_vety = ss.get("matice_vety", [])
    matice_vety.pop(i)
    st.rerun()


def uprav_slovo(i):

    ss = st.session_state

    matice_vety = ss.get("matice_vety", [])
    ss["f_edit"] = True
    ss["index_edit_word"] = i
    ss.slovo = matice_vety[i][f"cz_{matice_vety[i]['typ']}"]
    # zobraz_toast(text=f"Před Edituji - {ss['index_edit_word']} + 1. slovo >{ss.slovo}<", trvani=20)
    # st.sidebar.write(f"Edituji - {i + 1}. slovo >{ss.slovo}<")
    # st.write(f"Edituji - {i + 1}. slovo >{ss.slovo}<")
    # st.sidebar.write(f"❗️ Zadané parametry pro EDITACI. >i={i}<, index_edit_word >{ss['index_edit_word']}<")

    # Toto nechat na hlavní běh

    # Výběr slov a parametrů (forms)
    # vyber_slova_form()
    # zobraz_toast(text=f"Po Edituji - {ss['index_edit_word']} + 1. slovo >{ss.slovo}<", trvani=20)
    # ss['index_edit_word'] = None
    # ss['f_edit'] = False
    st.rerun()


# Vložení do věty - vpravo
# ====================================================================================================================================================


# ------------------------------------------------------------------------
# --- HLAVNÍ RENDER MATICE ---
# ------------------------------------------------------------------------


# Vložení do věty - vpravo
# ====================================================================================================================================================
# Vložení do věty - vpravo - funkční
# ================================================================


def vypis_nove_slovo(
    index: int,
    cz: str = "",
    prefix: str = "",
    kmen: str = "",
    pripona: str = "",
    popis1: str = "",
    popis2: str = "",
    popis3: str = "",
    popis4: str = "",
    dev: str = "",
    border_width: int = 1,
    sirka: int = 600,
    txt_font_size: str = "1.2em",
    txt_padding: str = "0",
    txt_min_height: str = "0",
    txt_line_height: str = "1.2em",
    txt_margin: str = "0",
    font_size: str = "0.8em",
    padding: str = "0.1em 0.3em",
    min_height: str = "0.0em",
    line_height: str = "1.0em",
    margin: str = "0",
):

    # txt_font_size  ="1.2em"   # velikost textu uvnitř tlačítka
    # txt_padding    ="0px 0px" # vnitřní okraje tlačítka: svislé (0.2em) a vodorovné (0.1em)
    # txt_min_height ="0.8em"   # minimální výška tlačítka (bez ohledu na obsah)
    # txt_line_height="1.2em"   # výška řádku textu (ovlivňuje vertikální "nahuštění")
    # txt_margin     ="0px"     # vnější okraje tlačítka (mezery mezi tlačítky nebo okolními prvky)

    # with st.container():
    # st.sidebar.markdown(f""" width:{sirka}px;
    st.markdown(
        f"""
    <div style='display:         flex;
                width:           100%;
                flex-direction:  row;
                justify-content: flex-start;
                align-items:     flex-start; /* zarovná obsah i tlačítka nahoru vertikálně */
                border-bottom:   {border_width}px green solid;
                font-size:       {txt_font_size};
                min-height:      {txt_min_height};
                line-height:     {txt_line_height};
                padding:         {txt_padding};
                margin:          {txt_margin};'>
        <div style="flex: 1; margin: 0 0 0 0.5em; padding: 0;">
            <span style="font-weight:bold;">&nbsp;{index}.</span> {cz} -
            <span style="background-color: #00ff00; font-weight:bold;">{prefix}</span><span style="font-weight:bold;">{kmen}</span><span style="background-color: #ffff38; font-weight:bold;">{pripona}</span>
            <span style="font-style: italic;">{popis1}</span>
            <span style="font-style: italic; font-weight:bold;">{popis2}</span>
            <span style="background-color: #ffd428; font-style: italic; font-weight:bold;">{popis3}</span>
            <span style="font-style: italic;">{popis4}</span>
            <span style="font-weight:bold;">{dev}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# Vložení do věty - vpravo
# -----------------------------------------------------------
# Hlavní funkce pro zobrazení matice věty
# -----------------------------------------------------------
def _render_sentence_matrix_hlavicka(
    i: int = 0,
    cols: Sequence[st.delta_generator.DeltaGenerator] = (),
) -> None:

    ss = st.session_state

    f_bez_tlacitek = ss["cfg"]["f_bez_tlacitek"]

    if not cols:
        return  # pokud nejsou sloupce, nedělej nic

    col1, col2, col3, col4, col5 = cols

    # Mini-tlačítka
    if not f_bez_tlacitek:
        pass
        # --- HLAVIČKA ---
        # když uživatel stiskne tlačítko pro vložení prvního slova do věty
        if f"{i + 1}. slovo" == "1. slovo":
            with col1:
                pass
                st.write("⬆️")
            with col2:
                pass
                st.write("⬇️")
            with col3:
                pass
                st.write("🗑️")
            with col4:
                pass
                st.write("✏️")
            with col5:
                pass
                st.write("**T V A R**")
            ss["f_hlavicka_slov"] = True


def _render_sentence_matrix_col1(i: int = 0):

    ss = st.session_state

    f_bez_tlacitek = ss["cfg"]["f_bez_tlacitek"]

    if not f_bez_tlacitek:
        # První slovo
        if not f"{i + 1}. slovo" == "1. slovo":
            if st.button("", key=f"mini_up_{i}"):
                presun_hore(i)


def _render_sentence_matrix_col2(i: int = 0):

    ss = st.session_state

    f_bez_tlacitek = ss["cfg"]["f_bez_tlacitek"]
    matice_vety = ss.get("matice_vety", [])

    if not f_bez_tlacitek:
        # Poslední slovo
        if not f"{i + 1}. slovo" == f"{len(matice_vety)}. slovo":
            if st.button("", key=f"mini_down_{i}"):
                presun_dolu(i)


def _render_sentence_matrix_col3(i: int = 0):

    ss = st.session_state

    f_bez_tlacitek = ss["cfg"]["f_bez_tlacitek"]

    if not f_bez_tlacitek:
        if st.button("", key=f"mini_del_{i}"):
            smaz_slovo(i)


def _render_sentence_matrix_col4(
    i: int = 0,
    slovo: dict = {},
):

    ss = st.session_state

    f_bez_tlacitek = ss["cfg"]["f_bez_tlacitek"]
    enable_edit_set = ss["enable_edit_set"]  # "typ"

    if not f_bez_tlacitek:
        typ = slovo.get("typ", "")
        # if typ not in {"pron", "ost"}:
        if typ in enable_edit_set:
            if st.button("", key=f"edit_{i}"):
                uprav_slovo(i)


def _render_sentence_matrix_col5(
    slovo: dict = {},
    data: dict = {},
) -> dict:

    ss = st.session_state

    casy_participa_set = ss["casy_participa_set"]
    typ = slovo.get("typ", "")
    koncovka = urci_koncovku(typ)  # (utils.py)

    if koncovka:

        if typ in {"sub", "adj"}:
            # "popis2":  f"{slovo.get(f'pad_{koncovka}', '')} ",
            # "popis3":  f"{slovo.get(f'rod_{koncovka}', '')} {slovo.get(f'cislo_{koncovka}', '')}",
            v_pad = slovo.get(f"pad_{koncovka}", "")
            v_rod = slovo.get(f"rod_{koncovka}", "")
            v_cislo = slovo.get(f"cislo_{koncovka}", "")
            v_popis2 = f"{v_pad} "
            v_popis3 = f"{v_rod} {v_cislo}"

            # zobraz_toast(text=f"Vloženo typ >{typ}<, koncovka >{koncovka}<", trvani=20)
            data = {
                "cz": slovo.get(f"cz_{koncovka}", ""),
                "prefix": "",
                "kmen": slovo.get(f"kmen_0_tran_cz_{koncovka}", ""),
                "pripona": slovo.get(f"koncovka_tran_cz_{koncovka}", ""),
                "popis1": "(",
                "popis2": v_popis2,
                "popis3": v_popis3,
                "popis4": ")",
                "dev": slovo.get(f"slovo_dev_{koncovka}", ""),
            }

        elif typ in {"pron"}:
            v_pad = slovo.get(f"pad_{koncovka}", "")
            v_osoba = slovo.get(f"osoba_{koncovka}", "")
            v_cislo = slovo.get(f"cislo_{koncovka}", "")
            v_popis2 = f"{v_pad} "

            if not slovo.get(f"rod_{koncovka}", "") == "":
                v_rod = slovo.get(f"rod_{koncovka}", "")
                v_popis3 = f"{v_rod} {v_osoba} {v_cislo}"

            if slovo.get(f"rod_{koncovka}", "") == "":
                v_popis3 = f"{v_osoba} {v_cislo}"

            data = {
                "cz": slovo.get(f"cz_{koncovka}", ""),
                "prefix": "",
                "kmen": slovo.get(f"slovo_tran_cz_{koncovka}", ""),
                "pripona": "",
                "popis1": "(",
                "popis2": v_popis2,
                "popis3": v_popis3,
                "popis4": ")",
                "dev": slovo.get(f"slovo_dev_{koncovka}", ""),
            }

        elif typ in {"verb"}:
            v_cas = slovo.get(f"cas_{koncovka}", "")
            v_aktivita = slovo.get(f"aktivita_{koncovka}", "")
            v_cislo = slovo.get(f"cislo_{koncovka}", "")

            if v_cas not in casy_participa_set:
                v_pada = slovo.get(f"pada_{koncovka}", "")
                v_pada = f"{v_pada}pada" if v_pada else ""
                v_popis2 = f"{v_cas} {v_pada} {v_aktivita} "

                v_osoba = slovo.get(f"osoba_{koncovka}", "")
                v_popis3 = f"{v_osoba}. os. {v_cislo}"

            if v_cas in casy_participa_set:
                v_pad = slovo.get(f"pad_{koncovka}", "")
                v_popis2 = f"{v_cas} {v_aktivita} {v_pad} "
                v_rod = slovo.get(f"rod_{koncovka}", "")
                v_popis3 = f"{v_rod} {v_cislo}"

            data = {
                "cz": slovo.get(f"cz_{koncovka}", ""),
                "prefix": slovo.get(f"prefix_{koncovka}", ""),
                "kmen": slovo.get(f"kmen_0_tran_cz_{koncovka}", ""),
                "pripona": slovo.get(f"koncovka_tran_cz_{koncovka}", ""),
                "popis1": "(",
                "popis2": v_popis2,
                "popis3": v_popis3,
                "popis4": ")",
                "dev": slovo.get(f"slovo_dev_{koncovka}", ""),
            }

        elif typ in {"ost"}:
            data = {
                "cz": slovo.get(f"cz_{koncovka}", ""),
                "prefix": "",
                "kmen": slovo.get(f"slovo_tran_cz_{koncovka}", ""),
                "pripona": "",
                "popis1": "",
                "popis2": "",
                "popis3": "",
                "popis4": "",
                "dev": slovo.get(f"slovo_dev_{koncovka}", ""),
            }

    return data


def zobraz_slova_vety():
    """Zobrazí interaktivní matici věty s možností mazání a přesouvání."""
    """Zobrazí interaktivní matici věty s mini-tlačítky."""

    ss = st.session_state

    # f_bez_tlacitek = ss['cfg']["f_bez_tlacitek"]
    matice_vety = ss.get("matice_vety", [])

    # Výpis sestavené věty - přehledová tabulka z "matice_vet"
    # otevři
    funkce = inspect.currentframe().f_code.co_name
    zobraz_vetu(kdo_vola=funkce)  # ui_display.py

    if not matice_vety:
        # st.info("⚠️ 4. Matice věty je zatím prázdná.")
        # zobraz_toast(text="Matice věty je zatím prázdná.", icon="⚠️", trvani=2.5)
        return

    col_rozloz = [1, 1, 1, 1, 25]

    ss["f_hlavicka_slov"] = False

    for i, slovo in enumerate(matice_vety):
        cols = st.columns(col_rozloz, gap=None)
        col1, col2, col3, col4, col5 = cols

        st.markdown(
            """
        <style>
        /* Odstranění extra mezer mezi řádky */
        div[data-testid="stVerticalBlock"] {
            margin-top:     0rem !important;
            margin-bottom:  0rem !important;
            padding-top:    0rem !important;
            padding-bottom: 0rem !important;
        }

        /* Sloupce bez paddingu */
        div[data-testid="column"] {
            padding-left:   0 !important;
            padding-right:  0 !important;
            padding-top:    0 !important;
            padding-bottom: 0 !important;
            margin-top:     0 !important;
            margin-bottom:  0 !important;
        }

        /* Tlačítka menší */
        div.stButton > button {
            font-size:   0.8em;
            padding:     0.1em 0.3em;
            min-height:  1em;
            line-height: 1em;
            margin:      0;
        }

        /* Volitelné: vycentrování tlačítek ve sloupcích */
        div.stButton {
            display:         flex;
            justify-content: flex-start; /* Ovlivňuje horizontální zarovnání elementů v kontejneru. */
            align-items:     flex-start;
        }

        </style>
        """,
            unsafe_allow_html=True,
        )

        #  pro tlačítka
        font_size = "0.8em"  # velikost textu uvnitř tlačítka
        padding = "0.1em 0.3em"  # vnitřní okraje tlačítka: svislé (0.2em) a vodorovné (0.1em)
        min_height = "0.0em"  # minimální výška tlačítka (bez ohledu na obsah)
        line_height = "0.8"  # výška řádku textu (ovlivňuje vertikální "nahuštění")
        margin = "0px"  # vnější okraje tlačítka (mezery mezi tlačítky nebo okolními prvky)

        #  pro text
        txt_font_size = "1.2em"  # velikost textu uvnitř tlačítka
        txt_padding = "0px 0px"  # vnitřní okraje tlačítka: svislé (0.2em) a vodorovné (0.1em)
        txt_min_height = "0.0em"  # minimální výška tlačítka (bez ohledu na obsah)
        txt_line_height = "1.2em"  # výška řádku textu (ovlivňuje vertikální "nahuštění")
        txt_margin = "0px"  # vnější okraje tlačítka (mezery mezi tlačítky nebo okolními prvky)

        # Při 1. slově se vypíše před ním hlavička
        _render_sentence_matrix_hlavicka(
            i=i,
            cols=cols,
        )

        with col1:
            _render_sentence_matrix_col1(i=i)
        with col2:
            _render_sentence_matrix_col2(i=i)
        with col3:
            _render_sentence_matrix_col3(i=i)

        # Tlačítko editovat (kromě typ slova "pron", "ost")
        with col4:
            _render_sentence_matrix_col4(
                i=i,
                slovo=slovo,
            )

        # Zobrazení slova
        with col5:
            # Vyber data podle typu
            data = {}

            data = _render_sentence_matrix_col5(
                slovo=slovo,
                data=data,
            )

            vypis_nove_slovo(
                f"{i + 1}",
                **data,
                txt_font_size=f"{txt_font_size}",
                txt_padding=f"{txt_padding}",
                txt_min_height=f"{txt_min_height}",
                txt_line_height=f"{txt_line_height}",
                txt_margin=f"{txt_margin}",
                font_size=f"{font_size}",
                padding=f"{padding}",
                min_height=f"{min_height}",
                line_height=f"{line_height}",
                margin=f"{margin}",
            )


# ================================================================
# když uživatel stiskne tlačítko pro vložení prvního slova do věty
# if "f_hlavicka_slov" not in ss:
#     ss["f_hlavicka_slov"]=False
# Tvar
