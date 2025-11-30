# helpers/loader_csv.py
# nacti_soubor, nacti_csv

# import
import os
import streamlit as st
import pandas as pd
import csv

# Vlastní moduly
from helpers.ui_display import zobraz_toast


def nacti_soubor(cesta: str, encoding: str = "utf-8") -> str | None:
    """
    Načte textový soubor "cesta" a vrátí jeho obsah.
    V případě chyby zobrazí toast a vrátí None.
    """
    soubor = os.path.basename(cesta)
    adresar = os.path.dirname(cesta) or "."
    if not os.path.exists(path=cesta):
        zobraz_toast(
            text=f"Soubor '{soubor}' nebyl nalezen v adresáři '{adresar}'.", icon="⚠️", trvani=3
        )
        return None
    try:
        with open(file=cesta, encoding=encoding) as f:
            obsah = f.read()
        return obsah
    except Exception as e:
        zobraz_toast(
            text=f"Chyba při čtení souboru '{soubor}' v adresáři '{adresar}: {e}",
            icon="⚠️",
            trvani=3,
        )
        return None


def nacti_csv(
    cesta: str, sloupec_trideni: str = None, zobraz: bool = False, typ: str = "dataframe"
) -> pd.DataFrame | list[dict]:
    """
    Načte CSV, buď jako pandas DataFrame, nebo jako list slovníků, volitelně setřídí a zobrazí ve Streamlit.

    Args:
        cesta (str):           Cesta k CSV souboru.
        sloupec_trideni (str): (pouze pro DataFrame) Název sloupce, podle kterého se má seřadit (cz).
        zobraz (bool):         (pouze pro DataFrame) Má se zobrazit tabulka v aplikaci?
        typ (str):             Typ struktury - "dataframe" nebo "list" – co má funkce vrátit.

    Returns:
        pd.DataFrame nebo list[dict]: Načtená data.
    """
    try:
        if typ == "dataframe":
            # načtení do pandas
            df = pd.read_csv(filepath_or_buffer=cesta, sep=";", encoding="utf-8")
            if sloupec_trideni and sloupec_trideni in df.columns:
                # Seřazení přímo v df bez přiřazování a vytváření nové seřazené kopie
                df.sort_values(by=sloupec_trideni, inplace=True)
            if zobraz:
                st.dataframe(data=df)
            return df

        elif typ == "list":
            # načtení jako list slovníků
            with open(file=cesta, mode="r", encoding="utf-8", newline="") as f:
                data = list(csv.DictReader(f, delimiter=";"))
            # načtení do listu slovníků - rozložený ekvivalent
            # data = []
            # with open(cesta, mode = "r", encoding="utf-8", newline = '') as f:
            #     reader = csv.DictReader(f, delimiter=";")
            #     data   = [row for row in reader]

            # případné třídění podle sloupce
            if sloupec_trideni and len(data) > 0 and sloupec_trideni in data[0]:
                data = sorted(iterable=data, key=lambda x: x[sloupec_trideni])
            return data

        else:
            raise ValueError(f"Neznámý typ načtení '{typ}': použij 'dataframe' nebo 'list'.")

    except Exception as e:
        # st.error(f"❌ Chyba při načítání {cesta}: {e}")
        zobraz_toast(text=f"❌ Chyba při načítání {cesta}: {e}", icon="⚠️", trvani=3.0)
        return pd.DataFrame() if typ == "dataframe" else []
