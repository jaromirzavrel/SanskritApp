# helpers/sklonovani.py

import streamlit as st
import pandas as pd
import unicodedata

from typing import Tuple
from helpers.loader_csv import nacti_csv


def odstran_diacritiku(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def ziskej_koncovku_padu_k(x_kmen: str, pad: str, rod: str, cislo: str) -> str:
    # df = pd.read_csv("data/koncovky_pady_k.csv", sep=";")
    df = nacti_csv(
        cesta="data/koncovky_pady_k.csv", sloupec_trideni=None, zobraz=False, typ="dataframe"
    )

    # st.sidebar.write("🔍 Všechny řádky pro x_kmen='a' a rod='f':")
    # st.sidebar.write(df[(df["x_kmen"] == "a") & (df["rod"] == "m")])
    # st.sidebar.write(df[(df["x_kmen"] == "a") & (df["rod"] == "n")])
    # st.sidebar.write(df[(df["x_kmen"] == "a") & (df["rod"] == "f")])
    # st.sidebar.write(df[(df["x_kmen"] == "á") & (df["rod"] == "f")])

    # filtr = (
    #     (df["x_kmen"] == x_kmen) &
    #     (df["pad"] == pad) &
    #     (df['rod'] == rod) &
    #     (df["cislo"] == cislo)
    # )

    filtr = (
        (df["x_kmen"].apply(odstran_diacritiku) == odstran_diacritiku(x_kmen))
        & (df["pad"] == pad)
        & (df["rod"] == rod)
        & (df["cislo"] == cislo)
    )

    vysledky = df[filtr]

    # st.sidebar.write("🔍 Unikátní hodnoty sloupce rod:", df["rod"].unique().tolist())
    # st.sidebar.write(f"❗️ Zadaný pad >{pad}<")
    # st.sidebar.write(f"❗️ Zadaný rod >{rod}<")
    # st.sidebar.write(f"❗️ Zadaný cislo >{cislo}<")
    # st.sidebar.write(f"❗️ Zadaný filtr >{filtr}<")
    # st.sidebar.write(f"❗️ Zadaný vysledky >{vysledky}<")
    # st.sidebar.write(f"❗️ Zadané parametry pro získání koncovky. x_kmen >{x_kmen}<")

    if not vysledky.empty:
        return vysledky.iloc[0]["koncovka"]
    return ""


def sklonuj_k(slovo_in: str, pad: str, rod: str, cislo: str) -> tuple[str, str, str, str]:
    x_kmen = slovo_in.rstrip("- ")[-1]  # a-, i-, u- kmen
    koncovka_padu = ziskej_koncovku_padu_k(x_kmen, pad, rod, cislo)
    if koncovka_padu:
        kmen_0 = slovo_in.rstrip("aeiouáéíóú- ")  # Odstranění koncovky pro skloňování
        # slovo_out = kmen.join(koncovka)
        slovo_out = kmen_0 + koncovka_padu
        return x_kmen, kmen_0, koncovka_padu, slovo_out
    else:
        st.sidebar.write(
            f"❗️ Nelze získat koncovku pro zadané parametry. koncovka_padu >{koncovka_padu}<"
        )
        return None, None, None, None


# helpers/sklonovani.py
