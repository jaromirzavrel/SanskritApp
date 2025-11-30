# helpers/generovani_sandhi_json.py
# generovani_sandhi_pravidel,

# Při startu aplikace
# 1. se spustí funkce generovani_sandhi_pravidel() v helpers.generovani_sandhi_json
#    ta používá na vstupu "data/sandhi_pravidla_zdroj.csv"
# 2. ta vytvoří (nebo přepíše) "data/sandhi_pravidla.json"
# 3. pravidla se uloží do st.session_state.sandhi_pravidla
# 4. a ta se použijí funkcí apply_sandhi v helpers.sandhi_processor a vytvoří ze vstupní věty cz tran sandhi cz tran

# Příklad použití:
# pravidla = nacti_sandhi_pravidla("sandhi_pravidla.json")
# nova_veta, zmeny = proved_sandhi(veta, pravidla)

# import
import os
import shutil
import csv
import json
import streamlit as st

# Vlastní moduly
# from helpers.ui_display import zobraz_toast

# 1. typ               → visarga_special (sjednoceno s ostatními výjimkami visarga).
# 2. puvod             → jasně popisuje původní formu (saḥ) a podmínku (před a).
# 3. nasleduje         → samohláska „a-“.
# 4. vysledek          → správný výsledek „so'“.
# 5. priklad_cz        → ilustruje změnu.
# 6. priklad_iast      → ilustruje změnu.
# 7. devanagari_puvod  → originál verze.
# 8. devanagari_sandhi → sandhi verze.
# 9. preklad           → vysvětlení / poznámka.

# Cesta k CSV zdroji
# csv_file = "data/sandhi_pravidla_zdroj.csv"
csv_file = "data/sandhi_pravidla_zdroj_ui.csv"
# Cesta pro výsledný JSON
json_file_out = "data/sandhi_pravidla.json"


def generovani_sandhi_pravidel(
    in_file: str = "data/sandhi_pravidla_zdroj_ui.csv",
    json_file_out: str = "data/sandhi_pravidla.json",
) -> tuple[list[dict], list[dict]]:
    """
    Načte sandhi pravidla ze CSV, převede je do JSON a uloží do st.session_state.sandhi_pravidla
    """
    pravidla = []
    json_file_in = ""
    csv_file = ""

    # if in_file.endswith(".json"):
    # elif in_file.endswith(".csv"):
    # else:
    #     raise ValueError("Nepodporovaný formát pravidel. Použij JSON nebo CSV.")
    pripona = os.path.splitext(in_file)[1][1:]  # vrátí 'json'
    if pripona == "csv":
        csv_file = in_file
    elif pripona == "json":
        json_file_in = in_file
        # kopírování obsahu (včetně formátování, zachová 1:1)
        # shutil.copyfile(json_file_in, json_file_out) # provede přesnou kopii souboru (bez metadat, jako jsou práva nebo časy)
        shutil.copy2(json_file_in, json_file_out)  # kopírovat i metadata
        st.session_state["sandhi_pravidla_file"] = json_file_out
        # načtení obsahu
        with open(json_file_out, "r", encoding="utf-8") as f:
            data = json.load(f)

        # oddělené části
        sandhi_skupiny = data.get("skupiny", [])
        sandhi_pravidla = data.get("pravidla", [])

        return sandhi_skupiny, sandhi_pravidla
    else:
        return [], []

    # 1. Načtení CSV
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        # ✅ kontrola hlaviček
        expected_cols = [
            "typ",
            "puvod",
            "nasleduje",
            "vysledek",
            "priklad_cz",
            "priklad_iast",
            "devanagari_puvod",
            "devanagari_sandhi",
            "preklad",
        ]

        # if set(reader.fieldnames) != set(expected_cols):
        if reader.fieldnames != expected_cols:
            raise ValueError(f"Neočekávané hlavičky CSV: {reader.fieldnames}")

        for row in reader:
            # 2. Převod hodnot z řádku CSV na dict vhodný přímo pro JSON
            pravidlo = {
                "typ": (row.get("typ") or "").strip(),  # 1. typ pravidla, např. visarga_special
                "puvod": (row.get("puvod") or "").strip(),  # 2. popisuje původní formu, např. saḥ
                "nasleduje": (
                    row.get("nasleduje") or ""
                ).strip(),  # 3. podmínka, co následuje, např. a-
                "vysledek": (row.get("vysledek") or "").strip(),  # 4. správný výsledek, např. so'
                "priklad_cz": (row.get("priklad_cz") or "").strip(),  # 5. ilustruje změnu v češtině
                "priklad_iast": (
                    row.get("priklad_iast") or ""
                ).strip(),  # 6. ilustruje změnu v iast
                "devanagari_puvod": (
                    row.get("devanagari_puvod") or ""
                ).strip(),  # 7. originál verze
                "devanagari_sandhi": (
                    row.get("devanagari_sandhi") or ""
                ).strip(),  # 8. sandhi verze
                "preklad": (row.get("preklad") or "").strip(),  # 9. vysvětlení / poznámka
            }

            pravidla.append(pravidlo)

    # 3. Uložení do JSON
    with open(json_file_out, "w", encoding="utf-8") as f:
        json.dump(pravidla, f, ensure_ascii=False, indent=2)
        st.session_state["sandhi_pravidla_file"] = json_file_out

    # 4. Načtení do session_state
    # st.session_state["sandhi_pravidla"] = pravidla

    # zobraz_toast(text = f"JSON s {len(pravidla)} pravidly byl vytvořen: {json_file_out}", icon = "✅", trvani = 3.0)
    return pravidla


if __name__ == "__main__":
    generovani_sandhi_pravidel(csv_file, json_file_out)
