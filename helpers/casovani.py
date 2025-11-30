# helpers/casovani.py

# import
import streamlit as st
import pandas as pd
import numpy as np

from helpers.loader_csv import nacti_csv
from helpers.sklonovani import ziskej_koncovku_padu_k

# koncovky_casy_d.csv 9 ř. cas_l;pada;aktiv;osoba;cislo;koncovka;pozn
# koncovky_casy_k.csv 3 ř. lakara;cas_l;cas_cz;pada;aktiv;osoba;prefix;k_sg;k_du;k_pl;pozn OK


def ziskej_koncovku_casu_d(cas_l: str, pada: str, osoba: int, cislo: str) -> str:
    # df = pd.read_csv("data/koncovky_casy_d.csv", sep=";")
    df = nacti_csv(
        cesta="data/koncovky_casy_d.csv", sloupec_trideni=None, zobraz=False, typ="dataframe"
    )
    filtr = (
        (df["cas_l"] == cas_l)
        & (df["pada"] == pada)
        & (df["osoba"] == osoba)
        & (df["cislo"] == cislo)
    )
    vysledky = df[filtr]
    if not vysledky.empty:
        return vysledky.iloc[0]["koncovka"]
    return ""


def ziskej_koncovku_casu_k(cas_l: str, pada: str, osoba: int, cislo: str) -> tuple[str, str]:
    # df = pd.read_csv("data/koncovky_casy_k.csv", sep=";")
    df = nacti_csv(
        cesta="data/koncovky_casy_k.csv", sloupec_trideni=None, zobraz=False, typ="dataframe"
    )
    filtr = (df["cas_l"] == cas_l) & (df["pada"] == pada) & (df["osoba"] == osoba)
    vysledky = df[filtr]
    if not vysledky.empty:
        k_cislo = f"k_{cislo.rstrip('. ')}"
        # st.write(f"(k_cislo>{k_cislo}<, vysledky>{vysledky}<)")

        if k_cislo in vysledky.columns:
            row = vysledky.iloc[0]
            prefix = row.get("prefix", "")
            koncovka_casu = row.get(k_cislo, "")

            # Pokud je hodnota NaN, převést na prázdný řetězec
            if isinstance(prefix, float) and pd.isna(prefix):
                prefix = ""
            if isinstance(koncovka_casu, float) and pd.isna(koncovka_casu):
                koncovka_casu = ""

            # st.write(f"(prefix>{prefix}<, koncovka>{koncovka}<)")
            # Vrátí prefix a koncovku pro dané číslo
            return prefix, koncovka_casu
    return "", ""


def ziskej_kmen(slovo_in: str, x_kmen: str, cas_l: str, pada: str) -> tuple[str, str]:
    prefix = ""
    kmen_0 = ""
    koncovka_vzoru = ""

    if cas_l == "PPP":
        koncovka_vzoru = x_kmen
    else:
        # Získání koncovky vzoru tj. prezent - přítomný čas 3. os. sg.
        prefix, koncovka_vzoru = ziskej_koncovku_casu_k("prezent", pada, 3, "sg.")

    len_vzoru = len(koncovka_vzoru)

    # kmen_0 = slovo_in.rstrip("aeiouáéíóú- ")  # Odstranění koncovky pro skloňování
    # Zkontroluj, zda slovo končí na danou koncovku
    koncovka_slova = slovo_in[-len_vzoru:] if len_vzoru > 0 else ""
    # st.write(f"(slovo_in >{slovo_in}<, cas_l >{cas_l}<, pada >{pada}<, prefix >{prefix}<, kmen_0 >{kmen_0}<, >{koncovka_vzoru}<, len_vzoru >{len_vzoru}<, koncovka_slova >{koncovka_slova}<)")
    if koncovka_slova == koncovka_vzoru:
        # Odstraň koncovku → vrať kmen
        kmen_0 = slovo_in[:-len_vzoru]
        # st.write(f"(slovo_in >{slovo_in}<, cas_l >{cas_l}<, pada >{pada}<, prefix >{prefix}<, kmen_0 >{kmen_0}<, >{koncovka_vzoru}<, len_vzoru >{len_vzoru}<, koncovka_slova >{koncovka_slova}<)")
        return prefix, kmen_0
    else:
        # Neshoda → vrať původní slovo (nebo např. prázdný řetězec)
        return prefix, slovo_in  # nebo return ""


def casuj_k(
    slovo_in: str, x_kmen: str, cas_l: str, pada: str, osoba: int, cislo: str, pad: str, rod: str
) -> tuple[str, str, str, str]:
    prefix = ""
    kmen_0 = ""
    koncovka_casu = ""
    slovo_out = ""

    # Získání kmene
    prefix, kmen_0 = ziskej_kmen(slovo_in, x_kmen, cas_l, pada)
    if kmen_0 == "":
        return prefix, slovo_in  # Pokud se nepodařilo získat kmen, vrať původní slovo

    # Získání koncovky
    if cas_l == "PPP":
        koncovka_casu = ziskej_koncovku_padu_k(x_kmen, pad, rod, cislo)
    else:
        # st.write(f"(>prefix, koncovka<)")
        # st.write(f"(>{cas_l}<, >{pada}<, >{osoba}<, >{cislo}<)")
        # chybně název času
        prefix, koncovka_casu = ziskej_koncovku_casu_k(cas_l, pada, osoba, cislo)
        # st.write(f"(>{prefix}<, >{koncovka}<)")

    # Přidání koncovky
    slovo_out = prefix + kmen_0 + koncovka_casu
    return prefix, kmen_0, koncovka_casu, slovo_out
