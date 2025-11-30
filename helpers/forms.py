# helpers/forms.py
#
# Obsahuje:
# zobraz_prepinac_pad, zobraz_prepinac_rod, zobraz_prepinac_cislo, zobraz_prepinac_osoba, zobraz_prepinac_cas,
# zobraz_prepinac_pada, vyber_slova_form,
#
# Volá:
# zobraz_prepinac_pad, zobraz_prepinac_rod, zobraz_prepinac_cislo, zobraz_prepinac_osoba, zobraz_prepinac_cas,
# zobraz_prepinac_pada, vyber_slova_form, urci_koncovku,
# clean_value, safe_index_or_default, zobraz_toast, nacti_csv, sklonuj_k, casuj_k, transliterate_iast_to_deva,
# transliterate_czech_v_to_iast

# ⬆️ ⬇️ ➡️ 🔜 🔁 🔡 🔠 📘 ℹ️ ▶️ ✅ 🗑️ ✏️
# 👉 👍 👇 🙏 🔔 🧪 📎 🛠️ 🏗️ 🔧 ✂️ 🔑
# ⚙️ ⚙ 📄 📜  📲 📥 📤 📍 📌 🔍 🔗
# 💻 🎁 🧰 📁 💾 ⏳ 🎚️ 📊 💬 🎛️ 💡 🔥 🧠
# 🌍 🌐 🧭 🎉 ❓ ❌ 🕉️ ॐ "ऽ" 🖋 📚
# 🟢 🟡 🔴 🟣
# 🟨 🟧 📦 🗃 🔓 🔐
# 🔸 🔹
# 🏷️ ⚠️ 🎯 🌿 🌱 🚻 👥 🗣️ 🌀 🧹 🧩
# 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 8️⃣
# 👉 Najdeš je zde:
#     • https://emojipedia.org/
#     • https://unicode.org/emoji/charts/full-emoji-list.html
# Zobrazit přepis:
# [✔] ( ) IAST (vědecký)
# [✔] ( ) Český (jazykově přesný)
# [✔] (•) Literární (pro čtení – běžná čeština)

# import
import streamlit as st
import pandas as pd

from dataclasses import dataclass, field
from typing import List, Dict, Union, Optional

from helpers.ui_display import zobraz_toast, dump_state
from helpers.utils import clean_value, safe_index_or_default, urci_koncovku
from helpers.loader_csv import nacti_csv
from helpers.sklonovani import ziskej_koncovku_padu_k, sklonuj_k
from helpers.casovani import casuj_k
from helpers.transliterate import (
    transliterate_iast_to_deva,
    transliterate_deva_to_iast,
    transliterate_iast_to_czech_v,
    transliterate_czech_v_to_iast,
    transliterate_iast_to_czech_f,
    transliterate_iast_to_czech_l,
    transliterate_czech_v_to_deva,
)


def zobraz_prepinac_pad(
    col1, col2, label, volby, key, horizontal=True, disabled=False, index=0
) -> str:
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        volba = st.radio(
            label,
            volby,
            key=key,
            horizontal=horizontal,
            disabled=disabled,
            index=index,
            label_visibility="collapsed",
        )
        return volba


def zobraz_prepinac_rod(
    col1, col2, col3, col4, label, volby, key, horizontal=True, disabled=False, index=0
) -> str:
    with col1:
        st.markdown(f"**{label}**")
    with col2:
        volba = st.radio(
            label,
            volby,
            key=key,
            horizontal=horizontal,
            disabled=disabled,
            index=index,
            label_visibility="collapsed",
        )
        return volba


def zobraz_prepinac_cislo(
    col1, col2, col3, col4, label, volby, key, horizontal=True, disabled=False, index=0
) -> str:
    with col3:
        st.markdown(f"**{label}**")
    with col4:
        volba = st.radio(
            label,
            volby,
            key=key,
            horizontal=horizontal,
            disabled=disabled,
            index=index,
            label_visibility="collapsed",
        )
        return volba


def zobraz_prepinac_osoba(
    col1, col2, col3, col4, label, volby, key, horizontal=True, disabled=False, index=0
) -> str:
    with col1:
        # st.markdown(f"<div style='line-height: 1;'>{label}</div>", unsafe_allow_html=True)
        st.markdown(f"**{label}**")
    with col2:
        volba = st.radio(
            label,
            volby,
            key=key,
            horizontal=horizontal,
            disabled=disabled,
            index=index,
            label_visibility="collapsed",
        )
        return volba


def zobraz_prepinac_cas(
    col1,  # ⟵ můžeš sem posílat sloupce Streamlitu, ale tu se teď nevyužívají
    col2,
    col3,
    label,  # popisek výběru (např. "Vyber čas:")
    volby,  # seznam možností (např. ["prézens", "aorist", "imperfekt"])
    key,  # unikátní klíč pro session_state
    horizontal=True,  # zatím nepoužité — možnost do budoucna
    disabled=False,  # zakázat přepínač
    index=0,  # která položka je vybraná jako výchozí
    format_func=None,  # funkce na úpravu zobrazeného textu (např. převod ID → text)
    format_args=None,  # dodatečné argumenty pro format_func
) -> str:
    # with col1:
    # label  = f"🧭 **Vyber čas:**"
    # Načtení dat
    # Typ: pandas.DataFrame
    # Pokud nacti_csv() načítá CSV, je typicky DataFrame.
    # * volby,
    # Výběr konkrétního slova
    # Typ: str (nebo numpy.str_ pokud přímo z .unique(), ale v praxi se chová jako string)
    # Jeden vybraný název slova ze sloupce cz v DataFrame.
    # *
    if format_func:
        # vytvoří pomocnou lambda, aby mohl sdílet DataFrame
        def ff(v):
            return format_func(v, *format_args)

        volba = st.selectbox(
            label=label,
            options=volby,
            key=key,
            disabled=disabled,
            index=index,
            format_func=ff,  # zobrazí přeformátovaný text
        )
    else:
        volba = st.selectbox(label=label, options=volby, key=key, disabled=disabled, index=index)
    return volba


def zobraz_prepinac_pada(
    col1, col2, col3, label, volby, key, horizontal=True, disabled=False, index=0
) -> str:
    # with col2:
    volba = st.selectbox(label=label, options=volby, key=key, disabled=disabled, index=index)
    # volba = st.radio(label = label, options = volby, key = key, horizontal = horizontal, disabled = disabled, index = index)
    return volba


# -----------------------------
# Definice dataclass
# -----------------------------
@dataclass
class Form_Slovo_Editace:
    """
    Drží aktuální stav výběru a editace jednoho slova.
    Číselníky, položky voleb formuláře.
    Klíče formuláře.
    Průběžná data formuláře.
    Výstup.
    """

    ss = st.session_state

    # -------------------------
    # 1️⃣ Editace a výběr slova
    # -------------------------
    # 🔹 Obecné stavy editace
    # f_edit: bool = False
    index_edit: Optional[int] = None  # index slova k editaci

    # shodné struktury -> ř matice_vety = slovo_k_editaci = matice_nove_slovo
    # parametr, hodnota
    slovo_k_editaci: Optional[Dict[str, str]] = None  # původní hodnoty pro editaci

    # 🔹 Stav UI: zda lze měnit typ a slovo
    f_typ_disable: bool = False
    f_slovo_disable: bool = False

    # 🔹 Slovník pro všechny načtené datové rámce podle koncovky - slovník ke slovnímu druhu
    df_slovnik: Dict[str, pd.DataFrame] = field(default_factory=dict)

    # 🔹 Slovník pro vybrané slovo - typ, slovo a parametry tvarování
    # po přidání tvarů pro zobrazení do věty vznikne matice_nove_slovo
    # parametr, hodnota
    df_vybrane_slovo: Dict[str, str] = field(default_factory=dict)

    # 🔹 Tvary - zde odvozeniny pro zobrazení, výpis, ekvivalenty, doplňky
    df_tvary_slova: Dict[str, str] = field(default_factory=dict)

    # -------------------------
    # 2️⃣ Číselníky / volby
    # -------------------------
    # seznam názvů do selectboxu volby_slovni_druh
    # "Podstatné jméno", "Přídavné jméno", "Zájmeno", "Sloveso", "Ostatní"
    volby_typ: List[str] = field(default_factory=list)
    # ["N", "Ak", "I", "D", "Abl", "G", "L", "V"] Nominativ, Akuzativ ...
    volby_pad: List[str] = field(default_factory=list)
    # ["m", "f", "n"]
    volby_rod: List[str] = field(default_factory=list)
    # [1, 2, 3]
    volby_osoba: List[int] = field(default_factory=list)
    # ["sg.", "du.", "pl."]
    volby_cislo: List[str] = field(default_factory=list)
    # přítomný, PPP, minulý...
    volby_cas: List[str] = field(default_factory=list)
    # "parasmai", "átmané"
    volby_pada: List[str] = field(default_factory=list)
    # "aktivum", "médium", "pasivum"
    volby_aktivita: List[str] = field(default_factory=list)
    casy: pd.DataFrame = field(default_factory=pd.DataFrame)

    # -------------------------
    # 3️⃣ Klíče
    # -------------------------
    df_klice: Dict[str, str] = field(default_factory=dict)
    df_value: Dict[str, str] = field(default_factory=dict)

    # Průběžná data formuláře
    df_prubeh: Dict[str, str] = field(default_factory=dict)

    # 🔹 Připravené hodnoty pro výstupy (matice)
    slovo: str = ""  # aktuálně vybrané slovo
    matice_vypis: Dict[str, str] = field(default_factory=dict)
    matice_nove_slovo: Dict[str, str] = field(default_factory=dict)

    # --------------- 2) naplním session_state hodnoty až tady --------
    def __post_init__(self):

        ss = st.session_state

        self.volby_typ = [r["nazev"] for r in ss["slovni_druh"]]
        self.volby_pad = ss["pad"]
        self.volby_rod = ss["rod"]
        self.volby_osoba = ss["osoba"]
        self.volby_cislo = ss["cislo"]
        self.volby_cas = ss["cas"]["cas_l"].dropna().unique().tolist()
        self.volby_pada = ss["pada"]
        self.volby_aktivita = ss["aktivita"]
        self.casy = ss["casy"]


def osoba_na_int(value_osoba: Union[int, str, None]) -> Union[int, str, None]:
    if value_osoba is None:
        # Zůstane None
        pass
    elif isinstance(value_osoba, int):
        # Už je číslo, necháme jak je
        pass
    elif isinstance(value_osoba, str) and value_osoba.isdigit():
        # Je číselný string → převedeme
        value_osoba = int(value_osoba)
    else:
        # Jinak necháme jako string (např. "1. os." nebo prázdný text)
        pass
    return value_osoba


def _form_data() -> None:
    """
    Určí jde-li o Editaci, nebo Nové slovo a
    Připraví instance tříd dat formuláře do ss
    """

    ss = st.session_state

    # instance třídy pro ...
    # sledování stavu editace
    # pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # Klíče formuláře
    if "form_slovo_editace" not in ss:
        ss["form_slovo_editace"] = Form_Slovo_Editace()

    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # st.sidebar.write(f"❗️ Zadané parametry pro koncovky. index_edit_word >{ss['index_edit_word']}<")
    if ss["f_edit"]:

        # if (
        #     "index_edit_word" in ss
        #     and ss['index_edit_word'] is not None
        #     and ss['index_edit_word'] >= 0
        # ):

        # Načti slovo, zobraz formulář na úpravu
        # ss['f_edit'] = True
        form.index_edit = ss["index_edit_word"]
        st.markdown(f"🛠️ **EDIT - změna tvaru {form.index_edit} + 1. slova:**")
    else:
        # ss['f_edit'] = False
        st.markdown("🛠️ **Zvol jednotlivá slova a tvary ze slovníku:**")

    # Slovní druh (Slovník) - Slovo - Tvar - Vypiš - Zapiš
    # Slovníky
    # Typ: dict[str, str]
    # Slovník, kde klíče jsou názvy kategorií (řetězce) a hodnoty jsou cesty k CSV souborům (řetězce).
    # slovniky = {
    #     "Podstatné jméno": "data/podstatna_jmena.csv",
    #     "Přídavné jméno":  "data/pridavna_jmena.csv",
    #     "Zájmeno":         "data/zajmena.csv",
    #     "Sloveso":         "data/slovesa.csv",
    #     "Ostatní":         "data/ostatni_slova.csv"
    # }

    # dump_state("_form_slovo END")

    # zobraz_toast(f"volby_rod >{volby_rod}<",           trvani = 5)
    # zobraz_toast(f"volby_osoba >{volby_osoba}<",       trvani = 5)
    # zobraz_toast(f"volby_cislo >{volby_cislo}<",       trvani = 5)
    # zobraz_toast(f"volby_cas >{volby_cas}<",           trvani = 5)
    # zobraz_toast(f"volby_pada >{volby_pada}<",         trvani = 5)
    # zobraz_toast(f"volby_aktivita >{volby_aktivita}<", trvani = 5)


def _form_typ() -> None:
    """
    Výběr Slovního druhu
    Definice klíčů
    Iniciačních hodnot voleb
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # 🗂️ Typ slova
    # Typ: str
    label_typ = "🗂️ 🔍 **Vyber typ slova:**"

    # typ je např. "sub", "adj", "pron", "verb", "ost"
    # výchozí typ slova "sub"
    form.df_klice["key_typ"] = "typ"
    form.df_vybrane_slovo[form.df_klice["key_typ"]] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_typ"], "sub"
    )

    # najít řádek podle typu - default "sub"
    # vybere podle verze vyhledávní jeden řádek slovníku např.
    # a z něho pak vybrat hodnotu dle klíče
    # {
    #     "zkratka": "pj",                       # původní zkratka druhu
    #     "nazev": "Podstatné jméno",            # český název
    #     "typ": "sub",                          # sanskrtský typ
    #     "nazev_l": "Substantivum",             # latinský název
    #     "slovnik": "data/podstatna_jmena.csv"  # cesta
    # }
    # 🔹 Získání vybraného slovního druhu z lookup tabulky
    r_typ = ss["slovni_druh_lookup"].get(
        # klíč je buď "sub" nebo název
        form.df_vybrane_slovo.get(form.df_klice["key_typ"], "sub"),
        # výchozí: první řádek, např. "Podstatné jméno"
        ss["slovni_druh"][0],
    )

    # 🔹 Extrakce informací o slovním druhu
    # typ, koncovka / zkratka, český název a cesta ke slovniku.csv
    # typ latinská zkratka výchozí typ "sub"
    form.df_vybrane_slovo[form.df_klice["key_typ"]] = r_typ[form.df_klice["key_typ"]]

    urci_koncovku(r_typ[form.df_klice["key_typ"]])  # (utils.py)
    form.df_klice["koncovka"] = ss["koncovka"]
    # form.df_klice['koncovka'] = "TEST"
    # key, koncovka výchozí "pj" ...
    # form.df_klice['koncovka'] = r_typ['zkratka']
    # typ_slova "Podstatné jméno", "Přídavné jméno", "Zájmeno", "Sloveso", "Ostatní"
    form.df_klice["typ_nazev"] = r_typ["nazev"]
    # cesta k csv "data/podstatna_jmena.csv" ...
    form.df_klice["cesta_slovniku"] = r_typ["slovnik"]

    # najít index podle názvu
    try:
        # index podle předvoleného názvu slovního druhu (volby_typ je název)
        index_typ = form.volby_typ.index(form.df_klice["typ_nazev"])
    except ValueError:
        index_typ = 0
    # unikátní klíč pro každé editační slovo
    key_slovo_typ = f"typ_slova_{ss.get('index_edit_word', 'new')}"

    # Jeden prvek (řetězec) vybraný uživatelem ze seznamu klíčů slovníku slovniky.
    # typ_slova = st.selectbox("🗂️ 🔍 **Vyber typ slova:**", list(slovniky.keys()))

    # ===================================
    # Výběr typu slova - slovního druhu
    # ===================================
    # dát f-ci zobrazuj - typ-nazev, vracej - typ_slova
    # typ_slova
    # "Podstatné jméno", "Přídavné jméno", "Zájmeno", "Sloveso", "Ostatní"
    form.df_vybrane_slovo[form.df_klice["key_typ"]] = st.selectbox(
        label=label_typ,
        # "Podstatné jméno", "Přídavné jméno", "Zájmeno", "Sloveso", "Ostatní"
        options=form.volby_typ,
        index=index_typ,
        key=key_slovo_typ,
        # slovní druh se nemění, pokud je slovo k editaci
        disabled=form.f_typ_disable,
    )

    # 🔹 Načtení dat
    #
    # Slovní druhy v češtině
    # ======================
    # 1 podstatná jména 	(Substantiva)
    # 2 přídavná jména 	    (Adjektiva)
    # 3 zájmena 		    (Pronomina)
    # 4 číslovky 		    (Numeralia)
    # 5 slovesa 		    (Verba)
    # 6 příslovce 		    (Adverbia)
    # 7 předložky 	    	(Prepozice)
    # 8 spojky 		        (Konjunkce)
    # 9 částice 		    (Partikule)
    # 10 citoslovce 		(Interjekce)

    # slovní druhy
    # {"sub", "adj", "pron", "verb", "ost"}
    # vybere podle verze vyhledávní jeden řádek slovníku např.
    # a z něho pak vybrat hodnotu dle klíče
    # {
    #     "zkratka": "pj",                       # původní zkratka druhu
    #     "nazev": "Podstatné jméno",            # český název
    #     "typ": "sub",                          # sanskrtský typ
    #     "nazev_l": "Substantivum",             # latinský název
    #     "slovnik": "data/podstatna_jmena.csv"  # cesta
    # }

    r_typ = ss["slovni_druh_lookup"].get(
        form.df_vybrane_slovo[form.df_klice["key_typ"]],
        # default, pokud klíč nenalezen
        ss["slovni_druh"][0],
    )

    # 🔹 typ, koncovka / zkratka, český název a cesta ke slovniku.csv
    # typ, koncovka / zkratka, český název a cesta ke slovniku.csv
    # typ latinsky, zkratka výchozí typ "sub"
    form.df_vybrane_slovo[form.df_klice["key_typ"]] = r_typ[form.df_klice["key_typ"]]

    urci_koncovku(r_typ[form.df_klice["key_typ"]])  # (utils.py)
    form.df_klice["koncovka"] = ss["koncovka"]

    # z vybraného řádku slovníku vybere hodnotu dle klíče

    # key, koncovka výchozí "pj" ...
    # form.df_klice['koncovka'] = r_typ['zkratka']
    # typ_slova_nazev "Podstatné jméno", "Přídavné jméno", "Zájmeno", "Sloveso", "Ostatní"
    form.df_klice["typ_nazev"] = r_typ["nazev"]
    # cesta k csv "data/podstatna_jmena.csv" ...
    form.df_klice["cesta_slovniku"] = r_typ["slovnik"]

    # 🔹 Kód: výběrníky (selectboxy/radia)
    # Potom je jedno, zda máš podstatné jméno, sloveso nebo zájmeno – klíče do matice_nove_slovo se vytvoří automaticky:
    form.df_klice["key_cz"] = f"cz_{form.df_klice['koncovka']}"
    form.df_klice["key_pad"] = f"pad_{form.df_klice['koncovka']}"
    form.df_klice["key_rod"] = f"rod_{form.df_klice['koncovka']}"
    form.df_klice["key_cislo"] = f"cislo_{form.df_klice['koncovka']}"
    form.df_klice["key_osoba"] = f"osoba_{form.df_klice['koncovka']}"
    form.df_klice["key_cas"] = f"cas_{form.df_klice['koncovka']}"
    form.df_klice["key_pada"] = f"pada_{form.df_klice['koncovka']}"
    form.df_klice["key_aktivita"] = f"aktivita_{form.df_klice['koncovka']}"

    # získej defaultní hodnoty pro výběrníky, hodnotu podle indexu
    # ["N", "Ak", "I", "D", "Abl", "G", "L", "V"] Nominativ, Akuzativ ...
    # st.write(f"form.df_value['value_pad'] >{form.df_value['value_pad']}<")
    form.df_value["value_pad"] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_pad"], form.volby_pad[0]
    )
    # st.write(f"form.df_value['value_pad'] >{form.df_value['value_pad']}<")

    # ["m", "f", "n"]
    form.df_value["value_rod"] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_rod"], form.volby_rod[0]
    )
    # ["sg.", "du.", "pl."]
    form.df_value["value_cislo"] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_cislo"], form.volby_cislo[0]
    )
    # [1, 2, 3] int
    form.df_value["value_osoba"] = int(
        (form.slovo_k_editaci or {}).get(form.df_klice["key_osoba"], form.volby_osoba[0])
    )
    # "prezent", přítomný, PPP, minulý...
    form.df_value["value_cas"] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_cas"], form.volby_cas[0]
    )
    # parasmai, átmané
    form.df_value["value_pada"] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_pada"], form.volby_pada[0]
    )
    # aktivita = "aktivum", "médium", "pasivum"
    form.df_value["value_aktivita"] = (form.slovo_k_editaci or {}).get(
        form.df_klice["key_aktivita"], form.volby_aktivita[0]
    )
    # zobraz_toast(text = f"1. value_rod >'{value_rod}'<", trvani = 5)
    # dump_state("_form_slovo END")


def _form_slovo() -> None:
    """
    Výběr slova
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # 🔹 PODSTATNÉ JMÉNO, substantivum, sub
    # 🔹 PŘÍDAVNÉ JMÉNO, adjektivum, adj
    # 🔹 ZÁJMENO, pronominum, pron
    # 🔹 SLOVESO, verbum, verb
    # 🔹 OSTATNÍ, ost
    if form.df_vybrane_slovo[form.df_klice["key_typ"]] in ss["slovni_druhy_set"]:
        # Načtení dat
        # Typ: pandas.DataFrame
        # Pokud nacti_csv() načítá CSV, je typicky DataFrame.
        form.df_slovnik[form.df_klice["koncovka"]] = nacti_csv(
            cesta=form.df_klice["cesta_slovniku"],
            sloupec_trideni="cz",
            zobraz=False,
            typ="dataframe",
        )

        # Výběr konkrétního slova s možností předvolby
        label_slovo = f"🔍 **Vyber {form.df_klice['typ_nazev'].lower()}:**"
        # sloupec voleb - slovíčka
        volby_slovo = form.df_slovnik[form.df_klice["koncovka"]]["cz"].dropna().unique()
        # pokud je slovo_k_editaci, tak to použij, jinak první z
        # co chceme jako default (např. podle slovo_k_editaci)
        # cz slovo
        # ulož do slovníku vybraného slova
        form.df_vybrane_slovo[form.df_klice["key_cz"]] = (form.slovo_k_editaci or {}).get(
            form.df_klice["key_cz"]
        ) or volby_slovo[0]
        key_slovo_cz = f"{form.df_klice['key_cz']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"  # unikátní klíč pro každé editační slovo

        # Výběr konkrétního slova
        # najít index vybrané hodnoty v volby
        try:
            # když volby už je list nebo iterovatelný objekt
            index_slovo = list(volby_slovo).index(form.df_vybrane_slovo[form.df_klice["key_cz"]])
        except Exception:
            try:
                # když je to numpy/pandas
                index_slovo = volby_slovo.tolist().index(
                    form.df_vybrane_slovo[form.df_klice["key_cz"]]
                )
            except (AttributeError, ValueError):
                # fallback, když tam není
                index_slovo = 0

        # st.write(f">{typ_slova.lower()}< >{label_slovo}< >{form.df_vybrane_slovo[form.df_klice['key_cz']]}< >{index_slovo}<")

        #
        # =========================
        # Výběr konkrétního slova
        # =========================
        #
        # Typ: str (nebo numpy.str_ pokud přímo z .unique(), ale v praxi se chová jako string)
        # Jeden vybraný název slova ze sloupce cz v DataFrame.
        # dát do výběru sloupce parametry pad;rod;osoba;cislo;kmen(já);tvar(my)
        form.df_vybrane_slovo[form.df_klice["key_cz"]] = st.selectbox(
            label=label_slovo,
            options=volby_slovo,
            index=index_slovo,
            key=key_slovo_cz,
            disabled=form.f_slovo_disable,  # slovo se nemění, pokud je slovo k editaci
        )

    else:
        # Err
        st.sidebar.write("❗️ Neznámý slovní druh.")
    # dump_state("_form_slovo END")


def _form_tvar_sub() -> tuple[dict, str, dict]:
    """
    Tvarování slova - skloňování - typů "sub, "adj"
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # cz;kmen;rod;devanagari
    # Pokud je vybráno slovo, zobraz další možnosti
    if form.df_vybrane_slovo.get(form.df_klice["key_cz"]) not in (None, ""):
        # Vybere řádky a z nich 1. (0.) kde je zvolené slovo
        r_vybrane_slovo = form.df_slovnik[form.df_klice["koncovka"]][
            form.df_slovnik[form.df_klice["koncovka"]]["cz"]
            == form.df_vybrane_slovo.get(form.df_klice["key_cz"])
        ].iloc[0]
        # Z tohoto řádku vybere položky - kmen, rod, devanagari
        # kmen - v cz vědecké transliteraci na konci s pomlčkou
        form.df_tvary_slova["kmen_tran_cz"] = r_vybrane_slovo["kmen"]
        # rod - default např. "m", rod v sanskrtu u Podstatého jména je pevně daný
        form.df_value["value_rod"] = clean_value(
            r_vybrane_slovo.get("rod", form.volby_rod[0]),
            default=form.volby_rod[0],
        )
        # devanagari - kmen v sanskrtu v dévanágarí bez pomlčky
        form.df_tvary_slova["kmen_dev"] = r_vybrane_slovo["devanagari"]
        # zobraz_toast(text = f"2. value_rod >'{value_rod}'<", trvani = 5)

        # if f_edit:
        # získej defaultní hodnoty pro výběrníky, hodnotu podle indexu
        # když není form.slovo_k_editaci vem vybrané slovo
        # ["m", "f", "n"]
        form.df_value["value_rod"] = (form.slovo_k_editaci or {}).get(
            form.df_klice["key_rod"], form.df_value["value_rod"]
        )
        # zobraz_toast(text = f"4. value_rod >'{value_rod}'<", trvani = 5)
        # value_rod = (form.slovo_k_editaci or {}).get(key_rod, ss['rod'][0]) # ["m", "f", "n"]
        # zobraz_toast(text = f"3. value_rod >'{value_rod}'<", trvani = 5)
        # zobraz_toast(text = f"1. value_pad >'{value_pad}'<", trvani = 5)
        # zobraz_toast(text = f"1. value_cislo >'{value_cislo}'<", trvani = 5)

        # st.write(f"ss['pad'] >{ss['pad']}<")
        # st.write(f"1. key_slovo_pad >{key_slovo_pad}<")
        # st.write(f"2. form.df_value['value_pad'] >{form.df_value['value_pad']}<")
        # st.write(f"index_pad >{index_pad}<")
        # Vytvoření voleb pádu a předvolení dle slovníku ["N", "Ak", "I", "D", "Abl", "G", "L", "V"]
        index_pad = safe_index_or_default(
            options=form.volby_pad, value=form.df_value["value_pad"], default_index=0
        )
        # Vytvoření voleb rodu a předvolení dle slovníku ["m", "n", "f"]
        index_rod = safe_index_or_default(
            options=form.volby_rod, value=form.df_value["value_rod"], default_index=0
        )
        # Vytvoření voleb čísla a předvolení dle slovníku ["sg.", "du.", "pl."]
        index_cislo = safe_index_or_default(
            options=form.volby_cislo, value=form.df_value["value_cislo"], default_index=0
        )
        # st.write(f"index_pad >{index_pad}<")

        col1, col2 = st.columns([0.9, 3.3], border=False)

        # Výběr pádu, rodu a čísla
        # Výběr pádu
        # label_pad   = "✅ **Pád:**"
        # label_pad   = "✅ **Vyber pád:**"
        # key_slovo_pad = f"{form.df_klice['key_pad']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_pad = (
            f"{form.df_klice['key_pad']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        # st.write(f"2. key_slovo_pad >{key_slovo_pad}<")
        if key_slovo_pad in ss:
            pass
            # st.write(f"2. ss[key_slovo_pad] >{ss[key_slovo_pad]}<")
        horizontal = True
        # horizontal  = False
        # pád je již ve slovníku pj, aj
        # f_pad_pj_aj_disable = True
        # pád není ve slovníku pj, aj
        f_pad_pj_aj_disable = False
        if f_pad_pj_aj_disable:
            label_pad = "❌ **Vyber pád:**"
            # label_pad = "❌ **Vyber pád:** (" + pad_pj + ")"
        else:
            label_pad = "✅ **Vyber pád:**"
        # "sub", "adj"
        form.df_vybrane_slovo[form.df_klice["key_pad"]] = zobraz_prepinac_pad(
            col1,
            col2,
            label=label_pad,
            volby=form.volby_pad,
            key=key_slovo_pad,
            horizontal=horizontal,
            disabled=f_pad_pj_aj_disable,
            index=index_pad,
        )

        col1, col2, col3, col4 = st.columns([2, 3, 1.6, 4], border=False)

        # Výběr rodu
        # Dynamický klíč – vynutí aktualizaci při změně slova
        # key_slovo_rod = f"{form.df_klice['key_rod']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_rod = (
            f"{form.df_klice['key_rod']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        horizontal = True
        # horizontal = False
        # "PODSTATNÉ JMÉNO" rod u "sub" je již ve slovníku
        f_rod_pj_disable = (
            True
            if form.df_vybrane_slovo[form.df_klice["key_typ"]]
            in {
                "sub",
            }
            else False
        )
        if f_rod_pj_disable:
            label_rod = "❌ 🚻 **Rod:**"
            # label_rod = "❌ 🚻 **Vyber rod:** (" + rod_pj_def + ")"
        else:
            label_rod = "✅ 🚻 **Rod:**"
        form.df_vybrane_slovo[form.df_klice["key_rod"]] = zobraz_prepinac_rod(
            col1,
            col2,
            col3,
            col4,
            label=label_rod,
            volby=form.volby_rod,
            key=key_slovo_rod,
            horizontal=horizontal,
            disabled=f_rod_pj_disable,
            index=index_rod,
        )

        # Výběr čísla
        label_cislo = "✅ **Číslo:**"
        # key_slovo_cislo = f"{form.df_klice['key_cislo']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_cislo = (
            f"{form.df_klice['key_cislo']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        horizontal = True
        # horizontal    = False
        form.df_vybrane_slovo[form.df_klice["key_cislo"]] = zobraz_prepinac_cislo(
            col1,
            col2,
            col3,
            col4,
            label=label_cislo,
            volby=form.volby_cislo,
            key=key_slovo_cislo,
            horizontal=horizontal,
            index=index_cislo,
        )

        # ziskej_koncovku_padu_k(pad: str, rod: str, cislo: str)
        # koncovka_tran_cz_pj = ziskej_koncovku_padu_k(pad_pj, rod_pj, cislo_pj)
        # if koncovka_tran_cz_pj: slovo_in: str, pad: str, rod: str, cislo: str
        (
            form.df_tvary_slova["x_kmen"],
            form.df_tvary_slova["kmen_0_tran_cz"],
            form.df_tvary_slova["koncovka_tran_cz"],
            form.df_tvary_slova["slovo_tran_cz"],
        ) = sklonuj_k(
            slovo_in=form.df_tvary_slova["kmen_tran_cz"],
            pad=form.df_vybrane_slovo[form.df_klice["key_pad"]],
            rod=form.df_vybrane_slovo[form.df_klice["key_rod"]],
            cislo=form.df_vybrane_slovo[form.df_klice["key_cislo"]],
        )

        if form.df_tvary_slova["slovo_tran_cz"]:
            # Dopolň tvary
            # Transliterace
            form.df_tvary_slova["slovo_tran_iast"] = transliterate_czech_v_to_iast(
                form.df_tvary_slova["slovo_tran_cz"]
            )
            form.df_tvary_slova["slovo_dev"] = transliterate_czech_v_to_deva(
                form.df_tvary_slova["slovo_tran_cz"]
            )
            # Popis tvaru
            # (N m sg.)
            form.df_tvary_slova["popis_tvaru"] = (
                f"({form.df_vybrane_slovo[form.df_klice['key_pad']]} {form.df_vybrane_slovo[form.df_klice['key_rod']]} {form.df_vybrane_slovo[form.df_klice['key_cislo']]})"
            )
            form.df_tvary_slova["popis_tvaru"] = " ".join(
                form.df_tvary_slova["popis_tvaru"].split()
            )
            # devaḥ (N m sg.)
            form.df_tvary_slova["slovo_tran_cz_popis"] = (
                f"{form.df_tvary_slova['slovo_tran_cz']} {form.df_tvary_slova['popis_tvaru']}"
            )

            # Vypiš "sub", "adj"
            # Výpis tvarů slova jmen "sub", "adj"
            ss["matice_vypis"] = {
                # typ slova "sub" "adj", "pron", "verb", "ost"
                "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
                "cz": form.df_vybrane_slovo.get(form.df_klice["key_cz"]),
                # a-, i-, u- kmen
                "x_kmen": form.df_tvary_slova["x_kmen"],
                "kmen_tran_cz": form.df_tvary_slova["kmen_tran_cz"],
                "pad": form.df_vybrane_slovo[form.df_klice["key_pad"]],
                "rod": form.df_vybrane_slovo[form.df_klice["key_rod"]],
                "cislo": form.df_vybrane_slovo[form.df_klice["key_cislo"]],
                "kmen_dev": form.df_tvary_slova["kmen_dev"],
                "kmen_0_tran_cz": form.df_tvary_slova["kmen_0_tran_cz"],
                "koncovka_tran_cz": form.df_tvary_slova["koncovka_tran_cz"],
                "slovo_tran_iast": form.df_tvary_slova["slovo_tran_iast"],
                "slovo_dev": form.df_tvary_slova["slovo_dev"],
            }

            # Zapiš "sub", "adj"
            # Sestavení nového řádku, tj. slovo s parametry
            ss["slovo"] = form.df_vybrane_slovo.get(form.df_klice["key_cz"])
            ss["matice_nove_slovo"] = {
                # typ slova "sub" "adj", "pron", "verb", "ost"
                "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
                f"cz_{form.df_klice['koncovka']}": form.df_vybrane_slovo.get(
                    form.df_klice["key_cz"]
                ),
                # a-, i-, u- kmen
                f"x_kmen_{form.df_klice['koncovka']}": form.df_tvary_slova["x_kmen"],
                f"kmen_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova["kmen_tran_cz"],
                f"pad_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_pad"]],
                f"rod_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_rod"]],
                f"cislo_{form.df_klice['koncovka']}": form.df_vybrane_slovo[
                    form.df_klice["key_cislo"]
                ],
                f"kmen_dev_{form.df_klice['koncovka']}": form.df_tvary_slova["kmen_dev"],
                f"kmen_0_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "kmen_0_tran_cz"
                ],
                f"koncovka_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "koncovka_tran_cz"
                ],
                f"slovo_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_tran_cz"],
                f"slovo_tran_iast_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "slovo_tran_iast"
                ],
                f"slovo_dev_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_dev"],
                f"popis_tvaru_{form.df_klice['koncovka']}": form.df_tvary_slova["popis_tvaru"],
                f"slovo_tran_cz_{form.df_klice['koncovka']}_popis": form.df_tvary_slova[
                    "slovo_tran_cz_popis"
                ],
            }

            return (
                ss["matice_vypis"],
                ss["slovo"],
                ss["matice_nove_slovo"],
            )
            # return

        else:
            st.sidebar.write("❗️ [sub, adj] Nelze získat tvar pro zadané parametry.")
    else:
        st.sidebar.write("❗️ [sub, adj] Nelze získat tvar pro zadané parametry.")
    # dump_state("_form_slovo END")


def _form_tvar_pron_volby() -> tuple[dict, str, dict]:
    """
    Tvarování slova - skloňování - typů "pron" - volby
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # Výběr pádu, rodu, osoby a čísla
    if not form.df_value["value_pad"] == "":

        col1, col2 = st.columns([0.9, 3.3], border=False)

        # Výběr pádu
        # label_pad   = "✅ **Pád:**"
        # label_pad   = "✅ **Vyber pád:**"
        # key_slovo_pad = f"{form.df_klice['key_pad']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_pad = (
            f"{form.df_klice['key_pad']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_pad = form.volby_pad.index(form.df_value["value_pad"])
        horizontal = True
        # horizontal = False
        # pád je již ve slovníku zj
        f_pad_zj_disable = True
        if f_pad_zj_disable:
            label_pad = "❌ **Vyber pád:**"
            # label_pad = "❌ **Vyber pád:** (" + pad_zj + ")"
        else:
            label_pad = "✅ **Vyber pád:**"
        # Zobraz přepínač pádu
        # "pron"
        form.df_vybrane_slovo[form.df_klice["key_pad"]] = zobraz_prepinac_pad(
            col1,
            col2,
            label=label_pad,
            volby=form.volby_pad,
            key=key_slovo_pad,
            horizontal=horizontal,
            disabled=f_pad_zj_disable,
            index=index_pad,
        )

    col1, col2, col3, col4 = st.columns([2, 3, 1.6, 4], border=False)

    # Výběr rodu
    if not form.df_value["value_rod"] == "":
        # Dynamický klíč – vynutí aktualizaci při změně slova
        # key_slovo_rod = f"{form.df_klice['key_rod']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_rod = (
            f"{form.df_klice['key_rod']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_rod = form.volby_rod.index(form.df_value["value_rod"])
        horizontal = True
        # horizontal = False
        # rod je již ve slovníku zj
        f_rod_zj_disable = True
        if f_rod_zj_disable:
            label_rod = "❌ 🚻 **Rod:**"
            # label_rod = "❌ 🚻 **Vyber rod:** (" + rod_zj_def + ")"
        else:
            label_rod = "✅ 🚻 **Rod:**"
        form.df_vybrane_slovo[form.df_klice["key_rod"]] = zobraz_prepinac_rod(
            col1,
            col2,
            col3,
            col4,
            label=label_rod,
            volby=form.volby_rod,
            key=key_slovo_rod,
            horizontal=horizontal,
            disabled=f_rod_zj_disable,
            index=index_rod,
        )

    # Výběr osoby "pron"
    if not form.df_value["value_osoba"] == "":
        # převede na string
        form.df_value["value_osoba"] = f"{form.df_value['value_osoba']}"
        # převede na int
        form.df_value["value_osoba"] = int(form.df_value["value_osoba"])
        # value_osoba   = f"{value_osoba}. os."
        # st.write(f"(>{osoba_zj}<)")
        # key_slovo_osoba = f"{form.df_klice['key_osoba']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_osoba = (
            f"{form.df_klice['key_osoba']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_osoba = form.volby_osoba.index(form.df_value["value_osoba"])
        # st.write(f"(>{index_osoba_zj}<)")
        horizontal = True
        # horizontal = False
        # osoba je již ve slovníku zj
        f_osoba_zj_disable = True
        if f_osoba_zj_disable:
            label_osoba = "❌ **Osoba:**"
        else:
            label_osoba = "✅ **Osoba:**"
        # Zobraz přepínač osoby
        form.df_vybrane_slovo[form.df_klice["key_osoba"]] = str(
            zobraz_prepinac_osoba(
                col1,
                col2,
                col3,
                col4,
                label=label_osoba,
                volby=form.volby_osoba,
                key=key_slovo_osoba,
                horizontal=horizontal,
                disabled=f_osoba_zj_disable,
                index=index_osoba,
            )
        )
        # st.write(f"(>{osoba_zj}<)")

    # Výběr čísla "pron"
    if not form.df_value["value_cislo"] == "":
        # tečka není ve slovníku zj, a v číselníku čísla je
        form.df_value["value_cislo"] = f"{form.df_value['value_cislo']}."
        # key_slovo_cislo = f"{form.df_klice['key_cislo']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_cislo = (
            f"{form.df_klice['key_cislo']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_cislo = form.volby_cislo.index(form.df_value["value_cislo"])
        horizontal = True
        # horizontal = False
        # číslo je již ve slovníku zj
        f_cislo_zj_disable = True
        if f_cislo_zj_disable:
            label_cislo = "❌ **Číslo:**"
            # label_cislo = "❌ **Vyber číslo:** (" + cislo_zj_def + ")"
        else:
            label_cislo = "✅ **Číslo:**"
        # Zobraz přepínač čísla
        form.df_vybrane_slovo[form.df_klice["key_cislo"]] = zobraz_prepinac_cislo(
            col1,
            col2,
            col3,
            col4,
            label=label_cislo,
            volby=form.volby_cislo,
            key=key_slovo_cislo,
            horizontal=horizontal,
            disabled=f_cislo_zj_disable,
            index=index_cislo,
        )

    if form.df_tvary_slova["slovo_tran_cz"]:
        # Dopolň tvary
        # Transliterace
        form.df_tvary_slova["slovo_tran_iast"] = transliterate_czech_v_to_iast(
            form.df_tvary_slova["slovo_tran_cz"]
        )
        form.df_tvary_slova["slovo_dev"] = transliterate_czech_v_to_deva(
            form.df_tvary_slova["slovo_tran_cz"]
        )
        # Popis tvaru
        # popis_tvaru_zj = f"({pad_zj}, {rod_zj}, {cislo_zj})"
        # (N m 1. os. sg.)
        form.df_tvary_slova["popis_tvaru"] = (
            f"({form.df_vybrane_slovo[form.df_klice['key_pad']]} {form.df_vybrane_slovo[form.df_klice['key_rod']]} {form.df_vybrane_slovo[form.df_klice['key_osoba']]}. os. {form.df_vybrane_slovo[form.df_klice['key_cislo']]})"
        )
        form.df_tvary_slova["popis_tvaru"] = " ".join(form.df_tvary_slova["popis_tvaru"].split())
        # ahaṃ (N m 1. os. sg.)
        form.df_tvary_slova["slovo_tran_cz_popis"] = (
            f"{form.df_tvary_slova['slovo_tran_cz']} {form.df_tvary_slova['popis_tvaru']}"
        )
        # st.write(f"(>{popis_tvaru_zj}<)")

        # Doplnit zdrojové slovo

        # Vypiš "pron"
        # Výpis tvarů slova jmen "pron"
        ss["matice_vypis"] = {
            # typ slova "sub" "adj", "pron", "verb", "ost"
            "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
            "cz": form.df_vybrane_slovo.get(form.df_klice["key_cz"]),
            "pad": form.df_vybrane_slovo[form.df_klice["key_pad"]],
            "rod": form.df_vybrane_slovo[form.df_klice["key_rod"]],
            "osoba": f"{form.df_vybrane_slovo[form.df_klice['key_osoba']]}. os.",
            "cislo": form.df_vybrane_slovo[form.df_klice["key_cislo"]],
            "slovo_tran_cz": form.df_tvary_slova["slovo_tran_cz"],
            "slovo_tran_iast": form.df_tvary_slova["slovo_tran_iast"],
            "slovo_dev": form.df_tvary_slova["slovo_dev"],
            "variant": form.df_tvary_slova["variant"],
            "pozice": form.df_tvary_slova["pozice"],
            "funkce": form.df_tvary_slova["funkce"],
            "poznamka": form.df_tvary_slova["poznamka"],
        }

        # Zapiš "pron"
        # Sestavení nového řádku, tj. slovo s parametry
        ss["slovo"] = form.df_vybrane_slovo.get(form.df_klice["key_cz"])
        ss["matice_nove_slovo"] = {
            # typ slova "sub" "adj", "pron", "verb", "ost"
            "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
            f"cz_{form.df_klice['koncovka']}": form.df_vybrane_slovo.get(form.df_klice["key_cz"]),
            f"pad_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_pad"]],
            f"rod_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_rod"]],
            f"osoba_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_osoba"]],
            f"cislo_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_cislo"]],
            f"slovo_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_tran_cz"],
            f"slovo_tran_iast_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_tran_iast"],
            f"slovo_dev_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_dev"],
            f"popis_tvaru_{form.df_klice['koncovka']}": form.df_tvary_slova["popis_tvaru"],
            f"slovo_tran_cz_{form.df_klice['koncovka']}_popis": form.df_tvary_slova[
                "slovo_tran_cz_popis"
            ],
            f"variant_{form.df_klice['koncovka']}": form.df_tvary_slova["variant"],
            f"pozice_{form.df_klice['koncovka']}": form.df_tvary_slova["pozice"],
            f"funkce_{form.df_klice['koncovka']}": form.df_tvary_slova["funkce"],
            f"poznamka_{form.df_klice['koncovka']}": form.df_tvary_slova["poznamka"],
        }

        return (
            ss["matice_vypis"],
            ss["slovo"],
            ss["matice_nove_slovo"],
        )
        # return

    else:
        st.sidebar.write("❗️ [pron] Nelze získat tvar pro zadané parametry.")
    # dump_state("_form_slovo END")


def _form_tvar_pron() -> tuple[dict, str, dict]:
    """
    Tvarování slova - skloňování - typů "pron" - vstup / výstup
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # cz;transliterace;devanagari;osoba;rod;cislo;pad;variant;pozice;funkce;poznamka
    # Pokud je vybráno slovo, zobraz další možnosti
    if form.df_vybrane_slovo.get(form.df_klice["key_cz"]) not in (None, ""):
        # Vybere řádky a z nich 1. (0.) kde je zvolené slovo
        r_vybrane_slovo = form.df_slovnik[form.df_klice["koncovka"]][
            form.df_slovnik[form.df_klice["koncovka"]]["cz"]
            == form.df_vybrane_slovo.get(form.df_klice["key_cz"])
        ].iloc[0]
        # Z tohoto řádku vybere položky (některá zámena mají jeden tvar, jiná více a parametry ale nepravidelná)
        # Doplnit do slovníku základní tvar
        # dát do výběru parametry pad;rod;osoba;cislo;
        # v cz vědecké transliteraci na konci bez pomlčky
        form.df_tvary_slova["slovo_tran_cz"] = r_vybrane_slovo["transliterace"]
        form.df_tvary_slova["slovo_tran_iast"] = transliterate_czech_v_to_iast(
            form.df_tvary_slova["slovo_tran_cz"]
        )
        # kmen v sanskrtu v dévanágarí bez pomlčky
        form.df_tvary_slova["slovo_dev"] = r_vybrane_slovo["devanagari"]
        # pád v sanskrtu
        form.df_value["value_pad"] = (
            "" if pd.isna(r_vybrane_slovo["pad"]) else str(r_vybrane_slovo["pad"])
        )
        # rod v sanskrtu
        form.df_value["value_rod"] = (
            "" if pd.isna(r_vybrane_slovo["rod"]) else str(r_vybrane_slovo["rod"])
        )
        # osoba v sanskrtu str
        form.df_value["value_osoba"] = (
            "" if pd.isna(r_vybrane_slovo["osoba"]) else str(r_vybrane_slovo["osoba"])
        )
        # číslo v sanskrtu "pron"
        form.df_value["value_cislo"] = (
            "" if pd.isna(r_vybrane_slovo["cislo"]) else str(r_vybrane_slovo["cislo"])
        )
        # varianta
        form.df_tvary_slova["variant"] = (
            "" if pd.isna(r_vybrane_slovo["variant"]) else str(r_vybrane_slovo["variant"])
        )
        # pozice
        form.df_tvary_slova["pozice"] = (
            "" if pd.isna(r_vybrane_slovo["pozice"]) else str(r_vybrane_slovo["pozice"])
        )
        # funkce
        form.df_tvary_slova["funkce"] = (
            "" if pd.isna(r_vybrane_slovo["funkce"]) else str(r_vybrane_slovo["funkce"])
        )
        # poznámka
        form.df_tvary_slova["poznamka"] = (
            "" if pd.isna(r_vybrane_slovo["poznamka"]) else str(r_vybrane_slovo["poznamka"])
        )
        # st.write(f"(>{rod_zj}<)")

        # pád   v sanskrtu
        form.df_vybrane_slovo[form.df_klice["key_pad"]] = ""
        # rod   v sansktu
        form.df_vybrane_slovo[form.df_klice["key_rod"]] = ""
        # osoba v sanskrtu
        form.df_vybrane_slovo[form.df_klice["key_osoba"]] = ""
        # číslo v sanskrtu
        form.df_vybrane_slovo[form.df_klice["key_cislo"]] = ""

        (
            ss["matice_vypis"],
            ss["slovo"],
            ss["matice_nove_slovo"],
        ) = _form_tvar_pron_volby()

        return (
            ss["matice_vypis"],
            ss["slovo"],
            ss["matice_nove_slovo"],
        )
        # return
    else:
        st.sidebar.write("❗️ [pron] Nelze získat tvar pro zadané parametry - ZÁJMENO.")


def _form_tvar_verb_cas(col1, col2, col3) -> None:
    """
    Tvarování slova - časování / skloňování - typů "verb" - čas
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # casy_participa_pasiv_set = ss['casy_participa_pasiv_set']
    # casy_participa_aktiv_set = ss['casy_participa_aktiv_set']
    # casy_participa_set = ss['casy_participa_set']
    # cas_ve_treti_osobe_set = ss['cas_ve_treti_osobe_set']
    label_cas = "🧭 **Vyber čas:**"
    # Vytvoření voleb času a předvolení dle editovaného slova, nebo default
    index_cas = form.volby_cas.index(form.df_value["value_cas"])
    # key_slovo_cas = f"{form.df_klice['key_cas']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
    key_slovo_cas = (
        f"{form.df_klice['key_cas']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
    )
    # laṭ;prezent;přítomný;parasmai;aktivum
    # laṭ;prezent;přítomný;átmané;médium
    # laṅ;imperfekt;minulý;parasmai;aktivum
    # laṅ;imperfekt;minulý;átmané;médium
    # volby_dict = { "přítomný": "laṭ", "minulý": "laṅ", "PPP": "liṭ" }
    # volby    = ["přítomný", "PPP", "minulý"]
    form.df_value["horizontal_verb"] = True

    # form.df_value['horizontal_verb'] = False
    #
    # funkce pro formátování možností z DataFrame
    def format_opt(value, casy):

        ss = st.session_state

        # TEST
        # zobraz_toast("TEST")
        # st.write("TYP:", type(casy))
        # st.write("SLOUPCE:", getattr(casy, "columns", None))
        # st.write("INDEX:", getattr(casy, "index", None))
        # st.write("HLAVICKA:\n", casy.head())
        # st.write("VALUE:", value)
        # st.write("FILTROVANO:\n", casy[casy['cas_l'] == value])
        # st.write("TYP FILTROVANO:", type(casy[casy['cas_l'] == value]))

        # najdeme první výskyt, řádek v DataFrame odpovídající hodnotě
        r = casy[casy["cas_l"] == value].iloc[0]

        # základní zobrazení: lakara – cas_l
        t = f"{r['lakara']} – {r['cas_l']}"

        # přidat třetí sloupec jen pro specifické hodnoty
        # přidá "aktivita"
        if value in ss["casy_participa_set"]:
            t += f" – {r['aktivita']}"

        # co se zobrazí uživateli
        return t

    #
    # čas -> pada, aktivita + osoba, číslo
    # čas PP -> + pád, rod, číslo (váže se k sub v Nominativu -> vyhledat a převzít rod, číslo)
    # vždy
    form.df_vybrane_slovo[form.df_klice["key_cas"]] = zobraz_prepinac_cas(
        col1,
        col2,
        col3,
        label=label_cas,
        volby=form.volby_cas,
        key=key_slovo_cas,
        horizontal=form.df_value["horizontal_verb"],
        format_func=format_opt,
        format_args=(form.casy,),
        index=index_cas,
    )
    r_cas = form.casy[form.casy["cas_l"] == form.df_vybrane_slovo[form.df_klice["key_cas"]]]
    if form.df_vybrane_slovo[form.df_klice["key_cas"]] not in ss["casy_participa_set"]:
        pass
        # Výchozí hodnoty
        form.df_value["pada_default"] = None
        form.df_value["aktivita_default"] = None
        # Ovládací příznaky – zda umožnit změnu
        form.df_value["f_pada_disable"] = False
        form.df_value["f_aktivita_disable"] = False

        # Rozšířená logika pro rozpoznání podle posledního znaku:
        # -i parasmai padam aktivum,-é átmané padam médium,
        if form.df_tvary_slova["x_pada"] in ("i", "í"):
            # parasmaipadová koncovka
            form.df_value["pada_default"] = "parasmai"
            form.df_value["aktivita_default"] = "aktivum"
            form.df_value["f_pada_disable"] = True
            form.df_value["f_aktivita_disable"] = True
        # -i parasmai padam aktivum,-é átmané padam médium,
        # více možností pro médium
        elif form.df_tvary_slova["x_pada"] in ("e", "é", "ai"):
            form.df_value["pada_default"] = "átmané"
            form.df_value["aktivita_default"] = "médium"
            form.df_value["f_pada_disable"] = True
            form.df_value["f_aktivita_disable"] = True
        # např. některé nepravidelné typy
        elif form.df_tvary_slova["x_pada"] in ("a", "á", "u", "ú"):
            # může být nejednoznačné – zobrazit, ale umožnit změnu
            form.df_value["pada_default"] = "parasmai"
            form.df_value["aktivita_default"] = "aktivum"
            form.df_value["f_pada_disable"] = False
            form.df_value["f_aktivita_disable"] = False
        else:
            form.df_value["pada_default"] = None
            form.df_value["aktivita_default"] = None
            # Pokud neznáme – skrýt nebo nechat volitelné
            form.df_value["f_pada_disable"] = False
            form.df_value["f_aktivita_disable"] = False
            # form.df_value['f_pada_disable']     = True
            # form.df_value['f_aktivita_disable'] = True

        form.df_value["value_rod"] = None
        if form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["cas_ve_treti_osobe_set"]:
            # u přítomného času a dalších je běžnější 3. os. sg.
            # [1, 2, 3]
            form.df_value["value_osoba"] = int(
                (form.slovo_k_editaci or {}).get(
                    form.df_klice["key_osoba"], str(form.volby_osoba[2])
                )
            )
        else:
            # jinak 1. os. sg.
            # [1, 2, 3]
            form.df_value["value_osoba"] = int(
                (form.slovo_k_editaci or {}).get(
                    form.df_klice["key_osoba"], str(form.volby_osoba[0])
                )
            )

    elif form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["casy_participa_pasiv_set"]:
        pass
        form.df_value["pada_default"] = clean_value(
            r_cas["pada"].iloc[0] if not r_cas.empty else None
        )
        form.df_value["aktivita_default"] = clean_value(
            r_cas["aktivita"].iloc[0] if not r_cas.empty else None
        )
        # aktivita = "pasivum" # aktivita = "aktivum", "médium", "pasivum"
        form.df_value["f_pada_disable"] = True
        form.df_value["f_aktivita_disable"] = True
        # ["m", "f", "n"]
        form.df_value["value_rod"] = clean_value(
            (form.slovo_k_editaci or {}).get(form.df_klice["key_rod"], form.volby_rod[0]),
            default=form.volby_rod[0],
        )
    elif form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["casy_participa_aktiv_set"]:
        pass
        form.df_value["pada_default"] = clean_value(
            r_cas["pada"].iloc[0] if not r_cas.empty else None
        )
        form.df_value["aktivita_default"] = clean_value(
            r_cas["aktivita"].iloc[0] if not r_cas.empty else None
        )
        # aktivita_slv = "aktivum" # aktivita = "aktivum", "médium", "pasivum"
        form.df_value["f_pada_disable"] = True
        form.df_value["f_aktivita_disable"] = True
        # ["m", "f", "n"]
        form.df_value["value_rod"] = (form.slovo_k_editaci or {}).get(
            form.df_klice["key_rod"], form.volby_rod[0]
        )
    else:
        pass
    # st.write(f"(>{cas_slv}<, >{rod_slv}<, >{osoba_slv}<, >{cislo_slv}<)")
    # dump_state("_form_slovo END")


def _form_tvar_verb_pada(col1, col2, col3) -> None:
    """
    Tvarování slova - časování / skloňování - typů "verb" - pada
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # pada_default = None
    # zobraz_toast(f"pada_default >{pada_default}<", trvani = 5)
    if form.df_value["pada_default"] is None:
        form.df_vybrane_slovo[form.df_klice["key_pada"]] = form.df_value["pada_default"]
    else:
        # key_slovo_pada = f"{form.df_klice['key_pada']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_pada = (
            f"{form.df_klice['key_pada']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        form.df_value["value_pada"] = (
            form.df_value["pada_default"]
            if form.df_value["pada_default"] in form.volby_pada
            else form.volby_pada[0]
        )
        index_pada = (
            form.volby_pada.index(form.df_value["value_pada"])
            if form.df_value["value_pada"] in form.volby_pada
            else 0
        )
        if form.df_value["f_pada_disable"]:
            label_pada = "❌ **Vyber pada:**"
        else:
            label_pada = "🔍 **Vyber pada:**"
        # Zobraz volbu pada
        # "verb"
        form.df_vybrane_slovo[form.df_klice["key_pada"]] = zobraz_prepinac_pada(
            col1,
            col2,
            col3,
            label=label_pada,
            volby=form.volby_pada,
            key=key_slovo_pada,
            horizontal=form.df_value["horizontal_verb"],
            disabled=form.df_value["f_pada_disable"],
            index=index_pada,
        )  # vždy
    # dump_state("_form_slovo END")


def _form_tvar_verb_aktivita(col1, col2, col3) -> None:
    """
    Tvarování slova - časování / skloňování - typů "verb" - aktivita
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    if form.df_value["aktivita_default"] is not None:
        # key_slovo_aktivita = f"{form.df_klice['key_aktivita']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_aktivita = (
            f"{form.df_klice['key_aktivita']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        form.df_value["value_aktivita"] = (
            form.df_value["aktivita_default"]
            if form.df_value["aktivita_default"] in form.volby_aktivita
            else form.volby_aktivita[0]
        )
        index_aktivita = (
            form.volby_aktivita.index(form.df_value["value_aktivita"])
            if form.df_value["value_aktivita"] in form.volby_aktivita
            else 0
        )
        if form.df_value["f_aktivita_disable"]:
            label_aktivita = "❌ **Vyber aktivitu:**"
        else:
            label_aktivita = "⚙️ **Vyber aktivitu:**"
        # Zobraz volbu aktivity
        form.df_vybrane_slovo[form.df_klice["key_aktivita"]] = zobraz_prepinac_pada(
            col1,
            col2,
            col3,
            label=label_aktivita,
            volby=form.volby_aktivita,
            key=key_slovo_aktivita,
            horizontal=form.df_value["horizontal_verb"],
            disabled=form.df_value["f_aktivita_disable"],
            index=index_aktivita,
        )
    else:
        form.df_vybrane_slovo[form.df_klice["key_aktivita"]] = form.df_value["aktivita_default"]
    # dump_state("_form_slovo END")


def _form_tvar_verb_pad() -> None:
    """
    Tvarování slova - časování / skloňování - typů "verb" - pád
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # Pokud je čas PPP, zobraz další možnosti - pád, rod, číslo
    # Výběr pádu
    if form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["casy_participa_set"]:
        col1, col2 = st.columns([0.9, 3.3], border=False)

        # Výběr pádu
        # key_slovo_pad = f"pad_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        # key_slovo_pad = f"{form.df_klice['key_pad']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_pad = (
            f"{form.df_klice['key_pad']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_pad = (
            form.volby_pad.index(form.df_value["value_pad"])
            if form.df_value["value_pad"] in form.volby_pad
            else 0
        )
        form.df_value["horizontal_verb"] = True
        # form.df_value['horizontal_verb'] = False
        f_pad_slv_disable = False  # pád participa nejčastěji "N"
        if f_pad_slv_disable:
            label_pad = "❌ **Vyber pád:**"
            # label_pad_slv = "❌ **Vyber pád:** (" + pad_slv + ")"
        else:
            label_pad = "✅ **Vyber pád:**"
        # Zobraz přepínač pádu
        form.df_vybrane_slovo[form.df_klice["key_pad"]] = zobraz_prepinac_pad(
            col1,
            col2,
            label=label_pad,
            volby=form.volby_pad,
            key=key_slovo_pad,
            horizontal=form.df_value["horizontal_verb"],
            disabled=f_pad_slv_disable,
            index=index_pad,
        )
    else:
        form.df_vybrane_slovo[form.df_klice["key_pad"]] = None
    # dump_state("_form_slovo END")


def _form_tvar_verb_rod_osoba_cislo() -> None:
    """
    Tvarování slova - časování / skloňování - typů "verb" - rod, osoba, číslo
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    col1, col2, col3, col4 = st.columns([2, 3, 1.6, 4], border=False)

    # Výběr rodu
    if form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["casy_participa_set"]:
        # Dynamický klíč – vynutí aktualizaci při změně slova
        # key_slovo_rod = f"{form.df_klice['key_rod']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_rod = (
            f"{form.df_klice['key_rod']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_rod = (
            form.volby_rod.index(form.df_value["value_rod"])
            if form.df_value["value_rod"] in form.volby_rod
            else 0
        )
        form.df_value["horizontal_verb"] = True
        # form.df_value['horizontal_verb'] = False
        f_rod_slv_disable = False  # rod dle podmětu nebo "n"
        if f_rod_slv_disable:
            label_rod = "❌ 🚻 **Rod:**"
            # label_rod = "❌ 🚻 **Vyber rod:** (" + rod_zj_def + ")"
        else:
            label_rod = "✅ 🚻 **Rod:**"
        form.df_vybrane_slovo[form.df_klice["key_rod"]] = zobraz_prepinac_rod(
            col1,
            col2,
            col3,
            col4,
            label=label_rod,
            volby=form.volby_rod,
            key=key_slovo_rod,
            horizontal=form.df_value["horizontal_verb"],
            disabled=f_rod_slv_disable,
            index=index_rod,
        )
    else:
        form.df_vybrane_slovo[form.df_klice["key_rod"]] = None

    # Výběr osoby
    if form.df_vybrane_slovo[form.df_klice["key_cas"]] not in ss["casy_participa_set"]:
        # key_slovo_osoba = f"{form.df_klice['key_osoba']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
        key_slovo_osoba = (
            f"{form.df_klice['key_osoba']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
        )
        index_osoba = (
            form.volby_osoba.index(form.df_value["value_osoba"])
            if form.df_value["value_osoba"] in form.volby_osoba
            else 0
        )
        form.df_value["horizontal_verb"] = True
        # form.df_value['horizontal_verb'] = False
        f_osoba_slv_disable = False  # osoba nejčastěji 3. os. sg.
        if f_osoba_slv_disable:
            label_osoba = "❌ **Osoba:**"
        else:
            label_osoba = "✅ **Osoba:**"
        # Zobraz přepínač osoby
        form.df_vybrane_slovo[form.df_klice["key_osoba"]] = str(
            zobraz_prepinac_osoba(
                col1,
                col2,
                col3,
                col4,
                label=label_osoba,
                volby=form.volby_osoba,
                key=key_slovo_osoba,
                horizontal=form.df_value["horizontal_verb"],
                disabled=f_osoba_slv_disable,
                index=index_osoba,
            )
        )
        # form.df_vybrane_slovo[key_osoba] = f"{form.df_vybrane_slovo[key_osoba]}"
    else:
        form.df_vybrane_slovo[form.df_klice["key_osoba"]] = None

    # Výběr čísla
    # key_slovo_cislo = f"{form.df_klice['key_cislo']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}_{ss.get('index_edit_word', 'new')}"
    key_slovo_cislo = (
        f"{form.df_klice['key_cislo']}_{form.df_vybrane_slovo.get(form.df_klice['key_cz'])}"
    )
    index_cislo = (
        form.volby_cislo.index(form.df_value["value_cislo"])
        if form.df_value["value_cislo"] in form.volby_cislo
        else 0
    )
    form.df_value["horizontal_verb"] = True
    # form.df_value['horizontal_verb'] = False
    f_cislo_slv_disable = False  # číslo nejčastěji "sg."
    if f_cislo_slv_disable:
        label_cislo = "❌ **Číslo:**"
        # label_cislo = "❌ **Vyber číslo:** (" + cislo_slv_def + ")"
    else:
        label_cislo = "✅ **Číslo:**"
    # Zobraz přepínač čísla
    form.df_vybrane_slovo[form.df_klice["key_cislo"]] = zobraz_prepinac_cislo(
        col1,
        col2,
        col3,
        col4,
        label=label_cislo,
        volby=form.volby_cislo,
        key=key_slovo_cislo,
        horizontal=form.df_value["horizontal_verb"],
        disabled=f_cislo_slv_disable,
        index=index_cislo,
    )
    # dump_state("_form_slovo END")


def _form_tvar_verb() -> tuple[dict, str, dict]:
    """
    Tvarování slova - časování / skloňování - typů "verb" - hlavní
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # cz;ot1;pad1_sa;pad1_cz;ot2;pad2_sa;pad2_cz;pada;aktivita;tran_kmen;tran_prezens_3sg;tran_ppp;dev_kmen;dev_prezens_3sg;dev_ppp
    # Pokud je vybráno slovo, zobraz další možnosti
    # if cz_slv:
    if form.df_vybrane_slovo.get(form.df_klice["key_cz"]) not in (None, ""):
        # Získání řádku (slovníku) s daty
        # Vybere řádky a z nich 1. (0.) kde je zvolené slovo
        # Typ: pandas.Series
        # Jeden řádek DataFrame (slovo se všemi parametry slova).
        # zobraz_toast(text = f"Koncovka >{koncovka}<", trvani = 20)
        r_vybrane_slovo = form.df_slovnik[form.df_klice["koncovka"]][
            form.df_slovnik[form.df_klice["koncovka"]]["cz"]
            == form.df_vybrane_slovo.get(form.df_klice["key_cz"])
        ].iloc[0]
        # r_vybrane_slovo = slv[slv['cz'] == cz_slv].iloc[0].to_dict() # pandas.Series to dict
        # a pak načtení do matice_vety - vypsat dict položky přidané + původní takto:
        # ss.matice_slovo = {lic_typ: form.df_vybrane_slovo[form.df_klice['key_typ']], **r_vybrane_slovo} # rozbalí do něj původní dict položky slovesa

        # slovniky    → dict[str, str]
        # typ_slova   → str
        # slv         → pandas.DataFrame
        # cz_slv      → str
        # r_vybrane_slovo → pandas.Series
        #
        # Z tohoto řádku vybere položky - ot1, pad1_sa, pad1_cz, ot2, pad2_sa, pad2_cz, pada, aktivita,
        # tran_kmen, tran_prezens_3sg, tran_ppp, dev_kmen, dev_prezens_3sg, dev_ppp

        # NEPOUŽITO
        # ot1 = r_vybrane_slovo['ot1']  # v cz vědecké transliteraci na konci bez pomlčky
        # pad1_sa = r_vybrane_slovo['pad1_sa']  # pád v sanskrtu
        # pad1_cz = r_vybrane_slovo['pad1_cz']  # pád v češtině
        # ot2 = r_vybrane_slovo['ot2']  # v cz vědecké transliteraci na konci bez pomlčky
        # pad2_sa = r_vybrane_slovo['pad2_sa']  # pád v sanskrtu
        # pad2_cz = r_vybrane_slovo['pad2_cz']  # pád v češtině
        # pada v sanskrtu
        form.df_value["value_pada"] = r_vybrane_slovo["pada"]
        # aktivita
        form.df_value["value_aktivita"] = r_vybrane_slovo["aktivita"]

        # kmen v cz vědecké transliteraci na konci s pomlčkou
        form.df_tvary_slova["tran_kmen"] = r_vybrane_slovo["tran_kmen"]
        # prezens 3. os. sg. v cz vědecké transliteraci
        form.df_tvary_slova["tran_prezens_3sg"] = r_vybrane_slovo["tran_prezens_3sg"]
        # poslední znak slovesa (např. z přítomného kmene 3. os. sg.)
        # -i parasmai padam aktivum,-é átmané padam médium,
        # odstraní mezery a pomlčky
        form.df_tvary_slova["x_pada"] = (
            form.df_tvary_slova["tran_prezens_3sg"].rstrip("- ").strip()[-1]
        )
        # ppp v cz vědecké transliteraci
        form.df_tvary_slova["tran_ppp"] = r_vybrane_slovo["tran_ppp"]
        # a-, i-, u- kmen
        form.df_tvary_slova["x_kmen"] = form.df_tvary_slova["tran_ppp"].rstrip("- ")[-1]

        # kmen v sanskrtu v dévanágarí bez pomlčky
        form.df_tvary_slova["dev_kmen"] = r_vybrane_slovo["dev_kmen"]
        # prezens 3. os. sg. v sanskrtu v dévanágarí
        form.df_tvary_slova["dev_prezens_3sg"] = r_vybrane_slovo["dev_prezens_3sg"]
        # ppp v sanskrtu v dévanágarí
        form.df_tvary_slova["dev_ppp"] = r_vybrane_slovo["dev_ppp"]

        col1, col2, col3 = st.columns([1.32, 0.75, 0.8], border=False)

        # Z tohoto řádku vybere položky - kmen, devanagari
        # dropdown se sloupci čas-zkratka, název, charakter
        # "🧭 Vyber čas:", ["přítomný", "PPP", "minulý"],
        # "🧭 Vyber pada:", ["parasmai", "átmané"]

        # zobraz_prepinac_pad(  col1, col2,             label, volby, key, horizontal=True, disabled=False, index=0) -> str:
        # zobraz_prepinac_rod(  col1, col2, col3, col4, label, volby, key, horizontal=True, disabled=False, index=0) -> str:
        # zobraz_prepinac_cislo(col1, col2, col3, col4, label, volby, key, horizontal=True, disabled=False, index=0) -> str:
        # zobraz_prepinac_osoba(col1, col2, col3, col4, label, volby, key, horizontal=True, disabled=False, index=0) -> str:
        # zobraz_prepinac_cas(  col1, col2, col3,       label, volby, key, horizontal=True, disabled=False, index=0) -> str:
        # zobraz_prepinac_pada( col1, col2, col3,       label, volby, key, horizontal=True, disabled=False, index=0) -> str:

        # st.write(f"(>{cz_slv}<, >{pada_slv}<, >{aktivita_slv}<, >{tran_prezens_3sg_slv}<, >{tran_ppp_slv}<)")

        form.df_value["horizontal_verb"] = True
        # form.df_value['horizontal_verb'] = False

        # čas
        with col1:
            _form_tvar_verb_cas(col1, col2, col3)
        # pada
        with col2:
            _form_tvar_verb_pada(col1, col2, col3)
        # aktivita
        with col3:
            _form_tvar_verb_aktivita(col1, col2, col3)

        _form_tvar_verb_pad()

        _form_tvar_verb_rod_osoba_cislo()

        # casuj_k(slovo_in: str, cas_l: str, pada: str, osoba: int, cislo: str, pad: str, rod: str) -> str:
        form.df_tvary_slova["prefix"] = form.df_tvary_slova["kmen_0_tran_cz"] = form.df_tvary_slova[
            "koncovka_tran_cz"
        ] = form.df_tvary_slova["slovo_tran_cz"] = ""

        # Přiřazení kmene slova pro zpracování, základního tvaru pro daný čas
        form.df_tvary_slova["kmen_tran_cz"] = (
            form.df_tvary_slova["tran_ppp"]
            if (form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["casy_participa_set"])
            else form.df_tvary_slova["tran_prezens_3sg"]
        )  # PPP nebo 3. os. sg.

        (
            form.df_tvary_slova["prefix"],
            form.df_tvary_slova["kmen_0_tran_cz"],
            form.df_tvary_slova["koncovka_tran_cz"],
            form.df_tvary_slova["slovo_tran_cz"],
        ) = casuj_k(
            # PPP nebo 3. os. sg.
            slovo_in=form.df_tvary_slova["kmen_tran_cz"],
            # a-, i-, u- kmen
            x_kmen=form.df_tvary_slova["x_kmen"],
            # ["prezent", "PPP", "imperfekt"], ["přítomný", "PPP", "minulý"]
            cas_l=form.df_vybrane_slovo[form.df_klice["key_cas"]],
            # ["parasmai", "átmané"]
            pada=form.df_vybrane_slovo[form.df_klice["key_pada"]],
            # [1, 2, 3]
            osoba=osoba_na_int(form.df_vybrane_slovo[form.df_klice["key_osoba"]]),
            # ["sg.", "du.", "pl."]
            cislo=form.df_vybrane_slovo[form.df_klice["key_cislo"]],
            # ["N", "Ak", "I", "D", "Abl", "G", "L", "V"]
            pad=form.df_vybrane_slovo[form.df_klice["key_pad"]],
            # ["m", "n", "f"]
            rod=form.df_vybrane_slovo[form.df_klice["key_rod"]],
        )

        form.df_tvary_slova["kmen_tran_iast"] = transliterate_czech_v_to_iast(
            form.df_tvary_slova["kmen_tran_cz"]
        )
        form.df_tvary_slova["kmen_dev"] = transliterate_czech_v_to_deva(
            form.df_tvary_slova["kmen_tran_cz"]
        )

        form.df_tvary_slova["slovo_tran_iast"] = transliterate_czech_v_to_iast(
            form.df_tvary_slova["slovo_tran_cz"]
        )
        form.df_tvary_slova["slovo_dev"] = transliterate_czech_v_to_deva(
            form.df_tvary_slova["slovo_tran_cz"]
        )

        # st.write(f"(>{cz_slv}<, >{pada_slv}<, >{aktivita_slv}<, >{tran_prezens_3sg_slv}<, >{tran_ppp_slv}<)")
        # st.write(f"(>{tran_kmen_slv}<, >{tran_ppp_slv}<, >{cas_slv}<, >{pada_slv}<, >{osoba_slv}<, >{pad_slv}<, >{rod_slv}<, >{cislo_slv}<)")
        # st.write(f"(>{prefix}<, >{kmen}<, >{koncovka}<, >{slovo_out}<)")

        # if cas_slv == "PPP" or cas_slv == "PMA" or cas_slv == "PPA" or cas_slv == "PPF":
        # Vypiš "verb"
        if form.df_tvary_slova["slovo_tran_cz"]:
            # Popis tvaru
            # (N, m, sg.)
            # popis_tvaru_pj = f"({pad_pj}, {rod_pj}, {cislo_pj})"
            if form.df_vybrane_slovo[form.df_klice["key_cas"]] in ss["casy_participa_set"]:
                # (N m sg.)
                form.df_tvary_slova["popis_tvaru"] = (
                    f"({form.df_vybrane_slovo[form.df_klice['key_cas']]} {form.df_vybrane_slovo[form.df_klice['key_pad']]} {form.df_vybrane_slovo[form.df_klice['key_rod']]} {form.df_vybrane_slovo[form.df_klice['key_cislo']]})"
                )
            else:
                # (přítomný parasmai 1. sg.)
                form.df_tvary_slova["popis_tvaru"] = (
                    f"({form.df_vybrane_slovo[form.df_klice['key_cas']]} {form.df_vybrane_slovo[form.df_klice['key_pada']]}pada {form.df_vybrane_slovo[form.df_klice['key_aktivita']]} {form.df_vybrane_slovo[form.df_klice['key_osoba']]}. os. {form.df_vybrane_slovo[form.df_klice['key_cislo']]})"
                )

            form.df_tvary_slova["popis_tvaru"] = " ".join(
                form.df_tvary_slova["popis_tvaru"].split()
            )
            # devaḥ (N m sg.)
            form.df_tvary_slova["slovo_tran_cz_popis"] = (
                f"{form.df_tvary_slova['slovo_tran_cz']} {form.df_tvary_slova['popis_tvaru']}"
            )

            # st.write(f"(prefix_slv >{prefix_slv}<) ", f"(koncovka_slv >{koncovka_slv}<)")
            # st.write(f"(tran_kmen_slv >{tran_kmen_slv}<) ", f"(tran_prezens_3sg_slv >{tran_prezens_3sg_slv}< )", f"(tran_ppp_slv >{tran_ppp_slv}<)")

            # kmen_tran_cz_slv

            # Výpis tvarů slova "verb"
            ss["matice_vypis"] = {
                # typ slova "sub" "adj", "pron", "verb", "ost"
                "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
                "cz": form.df_vybrane_slovo.get(form.df_klice["key_cz"]),
                # a-, i-, u- kmen
                "x_kmen": form.df_tvary_slova["x_kmen"],
                "kmen_tran_cz": form.df_tvary_slova["tran_kmen"],
                "tran_prezens_3sg": form.df_tvary_slova["tran_prezens_3sg"],
                "tran_ppp": form.df_tvary_slova["tran_ppp"],
                "kmen_dev": form.df_tvary_slova["dev_kmen"],
                "dev_prezens_3sg": form.df_tvary_slova["dev_prezens_3sg"],
                "dev_ppp": form.df_tvary_slova["dev_ppp"],
                "cas": form.df_vybrane_slovo[form.df_klice["key_cas"]],
                "pad": form.df_vybrane_slovo[form.df_klice["key_pad"]],
                "pada": form.df_vybrane_slovo[form.df_klice["key_pada"]],
                "aktiv": form.df_vybrane_slovo[form.df_klice["key_aktivita"]],
                "rod": form.df_vybrane_slovo[form.df_klice["key_rod"]],
                "osoba": f"{form.df_vybrane_slovo[form.df_klice['key_osoba']]}. os.",
                "cislo": form.df_vybrane_slovo[form.df_klice["key_cislo"]],
                "prefix": form.df_tvary_slova["prefix"],
                "kmen_0_tran_cz": form.df_tvary_slova["kmen_0_tran_cz"],
                "koncovka_tran_cz": form.df_tvary_slova["koncovka_tran_cz"],
                "slovo_tran_cz": form.df_tvary_slova["slovo_tran_cz"],
                "slovo_tran_iast": form.df_tvary_slova["slovo_tran_iast"],
                "slovo_dev": form.df_tvary_slova["slovo_dev"],
            }

            # Zapiš "verb"
            # Sestavení nového řádku, tj. slovo s parametry, prefix, kmen, koncovka, slovo_out
            # zobraz_toast(text = f"Koncovka >{koncovka}<", trvani = 20)
            ss["slovo"] = form.df_vybrane_slovo.get(form.df_klice["key_cz"])
            ss["matice_nove_slovo"] = {
                # typ slova "sub" "adj", "pron", "verb", "ost"
                "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
                f"cz_{form.df_klice['koncovka']}": form.df_vybrane_slovo.get(
                    form.df_klice["key_cz"]
                ),
                # a-, i-, u- kmen
                f"x_kmen_{form.df_klice['koncovka']}": form.df_tvary_slova["x_kmen"],
                f"kmen_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova["kmen_tran_cz"],
                f"kmen_tran_iast_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "kmen_tran_iast"
                ],
                f"kmen_dev_{form.df_klice['koncovka']}": form.df_tvary_slova["kmen_dev"],
                f"cas_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_cas"]],
                f"pad_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_pad"]],
                f"pada_{form.df_klice['koncovka']}": form.df_vybrane_slovo[
                    form.df_klice["key_pada"]
                ],
                f"aktivita_{form.df_klice['koncovka']}": form.df_vybrane_slovo[
                    form.df_klice["key_aktivita"]
                ],
                f"rod_{form.df_klice['koncovka']}": form.df_vybrane_slovo[form.df_klice["key_rod"]],
                f"osoba_{form.df_klice['koncovka']}": form.df_vybrane_slovo[
                    form.df_klice["key_osoba"]
                ],
                f"cislo_{form.df_klice['koncovka']}": form.df_vybrane_slovo[
                    form.df_klice["key_cislo"]
                ],
                f"prefix_{form.df_klice['koncovka']}": form.df_tvary_slova["prefix"],
                f"kmen_0_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "kmen_0_tran_cz"
                ],
                f"koncovka_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "koncovka_tran_cz"
                ],
                f"slovo_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_tran_cz"],
                f"slovo_tran_iast_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "slovo_tran_iast"
                ],
                f"slovo_dev_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_dev"],
                f"popis_tvaru_{form.df_klice['koncovka']}": form.df_tvary_slova["popis_tvaru"],
                f"slovo_tran_cz_{form.df_klice['koncovka']}_popis": form.df_tvary_slova[
                    "slovo_tran_cz_popis"
                ],
            }

            return (
                ss["matice_vypis"],
                ss["slovo"],
                ss["matice_nove_slovo"],
            )
            # return

        else:
            st.sidebar.write("❗️ [verb] Nelze získat tvar pro zadané parametry.")

    else:
        st.sidebar.write("❗️ [verb] Nelze získat tvar pro zadané parametry - SLOVESO.")
    # dump_state("_form_slovo END")


def _form_tvar_ost() -> tuple[dict, str, dict]:
    """
    Tvarování slova - nic - typů "ost"
    """

    ss = st.session_state

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # cz;transliterace;devanagari
    # Pokud je vybráno slovo, zobraz další možnosti
    if form.df_vybrane_slovo.get(form.df_klice["key_cz"]):
        # Vybere řádky a z nich 1. (0.) kde je zvolené slovo
        r_vybrane_slovo = form.df_slovnik[form.df_klice["koncovka"]][
            form.df_slovnik[form.df_klice["koncovka"]]["cz"]
            == form.df_vybrane_slovo.get(form.df_klice["key_cz"])
        ].iloc[0]
        # Z tohoto řádku vybere položky - kmen, devanagari
        # v cz vědecké transliteraci na konci bez pomlčky
        form.df_tvary_slova["slovo_tran_cz"] = r_vybrane_slovo["transliterace"]
        form.df_tvary_slova["slovo_tran_iast"] = transliterate_czech_v_to_iast(
            form.df_tvary_slova["slovo_tran_cz"]
        )
        # kmen v sanskrtu v dévanágarí bez pomlčky
        form.df_tvary_slova["slovo_dev"] = r_vybrane_slovo["devanagari"]

        # Vypiš
        if form.df_tvary_slova["slovo_tran_cz"]:
            # Popis tvaru
            # popis_tvaru_aj = f"({pad_aj}, {rod_aj}, {cislo_aj})"
            # popis_tvaru_aj = f"({pad_aj} {rod_aj} {cislo_aj})"
            # slovo_tran_cz_aj_popis = f"{slovo_tran_cz_aj} {popis_tvaru_aj}"

            # Výpis tvarů slova "ost"
            ss["matice_vypis"] = {
                # typ slova "sub" "adj", "pron", "verb", "ost"
                "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
                "cz": form.df_vybrane_slovo.get(form.df_klice["key_cz"]),
                "slovo_tran_cz": form.df_tvary_slova["slovo_tran_cz"],
                "slovo_tran_iast": form.df_tvary_slova["slovo_tran_iast"],
                "slovo_dev": form.df_tvary_slova["slovo_dev"],
            }

            # Zapiš "ost"
            # Sestavení nového řádku, tj. slovo s parametry
            ss["slovo"] = form.df_vybrane_slovo.get(form.df_klice["key_cz"])
            ss["matice_nove_slovo"] = {
                # typ slova "sub" "adj", "pron", "verb", "ost"
                "typ": form.df_vybrane_slovo[form.df_klice["key_typ"]],
                f"cz_{form.df_klice['koncovka']}": form.df_vybrane_slovo.get(
                    form.df_klice["key_cz"]
                ),
                f"slovo_tran_cz_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_tran_cz"],
                f"slovo_tran_iast_{form.df_klice['koncovka']}": form.df_tvary_slova[
                    "slovo_tran_iast"
                ],
                f"slovo_dev_{form.df_klice['koncovka']}": form.df_tvary_slova["slovo_dev"],
            }

            return (
                ss["matice_vypis"],
                ss["slovo"],
                ss["matice_nove_slovo"],
            )

        else:
            st.sidebar.write("❗️ [ost] Nelze získat tvar pro zadané parametry.")
    else:
        st.sidebar.write("❗️ [ost] Nelze získat tvar pro zadané parametry - OSTATNÍ.")
    # dump_state("_form_slovo END")


# VRACÍ slovo, nove_slovo (hodnoty tvarování, hodnoty zobrazení)
def vyber_slova_form() -> tuple[dict, str, dict]:
    """
    Výběr a tvarování slova - hlavní
    """

    ss = st.session_state

    ss["init"] += 1
    if ss["cfg"]["f_debug"]:
        ss.write("**ss['init']:**", ss.get("init"))

    # zobraz_toast(text=f"Před Edituji - {ss['index_edit_word']} + 1. slovo >{ss['slovo']}<", trvani=20)
    # st.sidebar.write(f"**Před - {ss['index_edit_word']} + 1. slovo >{ss['slovo']}<**")
    # Form_Slovo_Editace (df_slovnik, df_vybrane_slovo, df_tvary_slova, df_klice, df_value)
    _form_data()

    # st.sidebar.write("**f_edit:**", ss.get('f_edit'))
    # st.sidebar.write("**index_edit_word:**", ss.get('index_edit_word'))
    # st.sidebar.write("**form.index_edit:**", getattr(form, "index_edit", None))
    # st.sidebar.write("**len matice_vety:**", len(ss.get('matice_vety', [])))

    # instance třídy pro ...
    # - sledování stavu editace (Drží aktuální stav výběru a editace jednoho slova.)
    # - číselníky, položky voleb formuláře
    #   pad, rod, osoba, cislo, cas, pada, aktivita, casy
    # - klíče formuláře
    # - průběžná data formuláře
    # - výstup
    form: Form_Slovo_Editace = ss["form_slovo_editace"]

    # with st.sidebar.form("vyber_slova"):
    # with st.sidebar:
    if True:

        # Směr překladu

        # Vrácení slova ke změně tvaru
        if ss["f_edit"]:

            # if (
            #     "index_edit_word" in ss
            #     and ss['index_edit_word'] is not None
            #     and ss['index_edit_word'] >= 0
            # ):

            # Načti slovo, zobraz formulář na úpravu
            # form.f_edit = True
            # form.index_edit = ss['index_edit_word']

            if ss.get("matice_vety") and 0 <= form.index_edit < len(ss["matice_vety"]):
                form.slovo_k_editaci = ss["matice_vety"][form.index_edit]
                # je-li slovo k editaci neměl by se měnit slovní druh ani slovo
                # slovní druh se nemění, pokud je slovo k editaci
                form.f_typ_disable = True
                # slovo se nemění, pokud je slovo k editaci
                form.f_slovo_disable = True
                # slovo_test = ss['matice_vety'][form.index_edit].get("cz_TEST", "")
                # zobraz_toast(text=f"Edituji '{form.index_edit}' + 1. slovo >{slovo_test}<", trvani=5)
            else:
                form.slovo_k_editaci = None  # nebo prázdný dict {}
                form.f_typ_disable = False
                form.f_slovo_disable = False
                zobraz_toast(text=" ⚠️ Prázdné slovo / věta.", trvani=5)

        else:
            pass

            # Není-li editace lze měnit slovní druh a slovo
            form.f_typ_disable = False
            form.f_slovo_disable = False

        # Výběr slov
        col1, col2 = st.columns(2, border=False)

        # Výběr slovníku (slovniky, typ_slova)
        with col1:
            _form_typ()

        # Výběr slova dle druhu
        with col2:
            _form_slovo()

        # Zvol tvar
        # V danou chvíli zobrazuji jen jeden slovní druh
        # 🔹 PODSTATNÉ JMÉNO, substantivum, sub
        # 🔹 PŘÍDAVNÉ JMÉNO, adjektivum, adj
        # if form.df_vybrane_slovo[form.df_klice['key_typ']] in ("sub", "adj", "pron", "verb", "ost"):
        if form.df_vybrane_slovo[form.df_klice["key_typ"]] in {"sub", "adj"}:
            _form_tvar_sub()

        # 🔹 ZÁJMENO, pronominum, pron
        elif form.df_vybrane_slovo[form.df_klice["key_typ"]] in {
            "pron",
        }:
            _form_tvar_pron()

        # 🔹 SLOVESO, verbum, verb
        elif form.df_vybrane_slovo[form.df_klice["key_typ"]] in ("verb",):
            _form_tvar_verb()

        # 🔹 OSTATNÍ, ost
        elif form.df_vybrane_slovo[form.df_klice["key_typ"]] in ("ost"):
            _form_tvar_ost()

        else:
            st.sidebar.write(
                "❗️ [vše] Nelze získat tvar pro zadané parametry - neznámý slovní druh."
            )
        # dump_state("_form_slovo END")

        # st.sidebar.write(f"**Po - {ss['index_edit_word']} + 1. slovo >{ss['slovo']}<**")
        return
