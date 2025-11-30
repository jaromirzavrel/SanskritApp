# helpers/ui_display.py
#
# Zobrazovací procedury volané z více míst, ochrana proti zacyklení, udržení struktury do stromu
#
# Obsahuje:
# zobraz_toast, zobraz_vetu
#
# Volá:
#

# Importy
import streamlit as st
import pandas as pd
import json
import platform
import time
import inspect
import sys
import os

from pprint import pprint

# from streamlit.runtime.config import get_config
# ⚠️ Lepší způsob:
from streamlit.web.cli import _get_command_line_as_string
from streamlit.runtime.state import session_state
from streamlit.runtime.scriptrunner import get_script_run_ctx


def zobraz_toast(
    text: str,
    icon: str = "✅",
    trvani: float = 2.5,
    f_privileg: bool = False,
    f_debug: bool = False,
):

    ss = st.session_state

    if not ss["cfg"]["f_zobraz_toast_privileg"] or (
        (ss["cfg"]["f_zobraz_toast_privileg"] and f_privileg)
        or ((ss["cfg"]["f_zobraz_toast_debug"] and ss["cfg"]["f_debug"] and f_debug))
    ):
        if hasattr(st, "toast"):  # novější Streamlit
            st.toast(text, icon=icon)
        else:
            placeholder = st.empty()
            placeholder.success(text)
            time.sleep(trvani)
            placeholder.empty()


def dump_state(label="Stav", side=False):
    # target = st.sidebar if side else st
    target = st
    target.write(f"🧭 **{label}**")
    if st.session_state:
        target.json({k: str(v) for k, v in st.session_state.items()})
    else:
        target.write("❗️ Session state je prázdný.")


# 💡 Funkce pro zjištění aktuálního tématu Streamlit
def get_streamlit_theme():
    defaults = {
        "primaryColor": "#F63366",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
        "font": "sans serif",
    }
    theme = {}
    for k, default in defaults.items():
        theme[k] = st.get_option(f"theme.{k}") or default
    return theme


# 💡 Odhad systémového tématu (světlý/tmavý)
def get_system_theme():
    # Jednoduchý odhad podle jména systému – není 100% spolehlivý,
    # ale lze rozšířit o detekci přes JS
    return {
        "name": "light",
        "primaryColor": "#0078D4",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F3F3F3",
        "textColor": "#000000",
        "font": "Segoe UI" if platform.system() == "Windows" else "sans-serif",
    }


# 💡 Vykresli vizuální přehled barev
def show_color_blocks(title, colors):
    st.markdown(f"### 🎨 {title}")
    for k, v in colors.items():
        if k == "font":
            st.write(f"**{k}:** {v}")
        else:
            st.markdown(
                f"<div style='background-color:{v}; padding:8px; border-radius:8px;'>"
                f"<b>{k}</b>: {v}</div>",
                unsafe_allow_html=True,
            )


def get_theme_value(key, default):
    value = st.get_option(key)
    return value if value is not None else default


def vypis_streamlit_system_info():
    st.markdown("🧭 **Streamlit – systémové parametry**")

    # Verze Streamlit a Pythonu
    st.write("**Verze Streamlit:**", st.__version__)
    st.write("**Verze Python:**", sys.version)

    # Aktuální adresář
    st.write("**Aktuální adresář:**", os.getcwd())

    # Session state
    st.write("**Session state:**")
    st.json(st.session_state)

    # Secrets – bez ohledu na config
    try:
        st.write("**Secrets:**")
        if st.secrets:
            st.json(st.secrets)
        else:
            st.write("Žádný secrets.toml nebyl nalezen.")
    except Exception as e:
        st.write(f"Chyba při načítání secrets: {e}")

    # Environment proměnné začínající na STREAMLIT_
    st.write("**Environment proměnné (STREAMLIT_*):**")
    env_vars = {k: v for k, v in os.environ.items() if k.startswith("STREAMLIT")}
    if env_vars:
        st.json(env_vars)
    else:
        st.write("{žádné: nenastavené}")

    # Vrátí aktuální barevné schéma (light/dark)
    # theme = st.runtime.get_instance()._session_data.main_script_path
    # st.write(f"Aktuální barevné schéma (light/dark): {theme}")

    st.write("🎨 Aktuální Streamlit téma:")

    ctx = get_script_run_ctx()
    st.write(f"ctx.session_id: {ctx.session_id}")

    # st.write("Primary color:", st.get_option("theme.primaryColor"))
    # st.write("Background color:", st.get_option("theme.backgroundColor"))
    # st.write("Secondary background:", st.get_option("theme.secondaryBackgroundColor"))
    # st.write("Text color:", st.get_option("theme.textColor"))
    # st.write("Font:", st.get_option("theme.font"))

    st.write(
        {
            "primaryColor": get_theme_value("theme.primaryColor", "#F63366"),
            "backgroundColor": get_theme_value("theme.backgroundColor", "#FFFFFF"),
            "secondaryBackgroundColor": get_theme_value(
                "theme.secondaryBackgroundColor", "#F0F2F6"
            ),
            "textColor": get_theme_value("theme.textColor", "#262730"),
            "font": get_theme_value("theme.font", "sans serif"),
        }
    )

    st.title("🎨 Porovnání barev – Streamlit vs. systém")
    st.write("Zobrazuje aktuální barvy použité ve Streamlit aplikaci a odhad systémových barev.")

    col1, col2 = st.columns(2)
    with col1:
        show_color_blocks("Aktuální téma Streamlit", get_streamlit_theme())
    with col2:
        show_color_blocks("Odhadované systémové barvy", get_system_theme())

    # 💡 Volitelně zobraz jako JSON pro porovnání
    st.subheader("📋 Data (JSON)")
    st.json(
        {
            "Streamlit": get_streamlit_theme(),
            "Systém": get_system_theme(),
        }
    )


def zobraz_config(path):

    # vypis_streamlit_system_info()

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            st.code(f.read(), language="toml")
    else:
        st.info(f"Soubor nenalezen: {path}")


def vypis_konfiguraci():

    # vypis_streamlit_system_info()

    st.write("### 🧭 Streamlit konfigurace")
    st.write("**Verze:**", st.__version__)

    st.write("Aktuální adresář:", os.getcwd())

    # Session state
    st.write("#### Session state:")
    st.json(dict(st.session_state))

    # Secrets (pokud jsou)
    if hasattr(st, "secrets"):
        st.write("#### Secrets:")
        try:
            st.json(st.secrets)
        except Exception:
            st.info("Žádný soubor secrets.toml nebyl nalezen.")

    # Environment proměnné Streamlitu
    st.write("#### Environment proměnné (STREAMLIT_*):")
    env_vars = {k: v for k, v in os.environ.items() if k.startswith("STREAMLIT")}
    st.json(env_vars or {"žádné": "nenastavené"})

    # cfg = get_config()
    # st.write("Aktivní interní Streamlit konfigurace:")
    # st.json(cfg._config)

    # Globální config
    st.write("Globální config:")
    zobraz_config(os.path.expanduser("~/.streamlit/config.toml"))

    # Lokální config projektu
    st.write("Lokální config projektu:")
    zobraz_config(".streamlit/config.toml")


# Výstup - konec, vpravo
# ================================================================
# Výpis sestavené věty - tabulka z "matice_vet"


def zobraz_vetu(kdo_vola: str = "neznámý"):
    # if "veta_tran_cz" not in st.session_state or not st.session_state['veta_tran_cz']:
    #     # st.info("Zatím nebyla sestavena žádná věta.")
    #     zobraz_toast(text = "1 - Zatím nebyla věta sestavena.", icon = "⚠️", trvani = 2.5)
    #     return

    if st.session_state["matice_vet"]:
        vety_df = pd.DataFrame(st.session_state["matice_vet"])
        # st.dataframe(vety_df, hide_index=True, use_container_width=True)

        # Zobrazení s nastavením šířky sloupců
        # time.sleep(1)
        st.data_editor(
            vety_df,
            column_config={
                "Varianta": st.column_config.Column(
                    f"Varianta - {kdo_vola}", width="auto"  # pixely
                ),
                "Věta": st.column_config.Column("Věta", width="large"),  # malé, medium, large, auto
            },
            hide_index=True,
            # use_container_width=True,
            width="stretch",  # ← náhrada za use_container_width=True
            key=f"editor_vety_{kdo_vola}_{id(vety_df)}",  # <- unikátní klíč
        )
