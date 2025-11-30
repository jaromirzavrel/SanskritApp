# helpers/gramatika.py
import streamlit as st
import pandas as pd


def zobraz_gramaticka_pravidla():
    st.subheader("📚 Gramatická pravidla")

    # Základní sandhi
    st.markdown("### 🧪 Sandhi (spojování hlásek)")
    sandhi_df = pd.read_csv("data/pravidla_sandhi.csv")
    st.dataframe(sandhi_df)
    st.markdown("### 🧪 Sandhi cele (spojování hlásek v celých slovech)")
    sandhi_c_df = pd.read_csv("data/pravidla_sandhi_c.csv")
    st.dataframe(sandhi_c_df)

    # Stavba věty
    st.markdown("### 🧱 Stavba sanskrtské věty")
    st.markdown(
        """
    Sanskrtské věty jsou **flexibilní v pořadí slov**, ale obvykle:
    - **Přívlastek** následuje (či předchází) podstatné jméno, **shoduje se v pádě, rodě, čísle**
    - **Zájmena** často přiléhají ke slovesům nebo určují větný člen
    - **Sloveso** bývá na **konci**

    **Příklad**:
    - **uttamáḥ déváḥ vadanti** → *Nejlepší bohové mluví*
    - (N m pl.) (N m pl.) (prézent, parasmai padam, aktivum 3. os. pl.)
    """
    )

    # Příklony
    st.markdown("### 🔗 Příklony a spojky")
    st.markdown(
        """
    - **'ča'** = a (např. rámaḥ ča lakṣmaṇaḥ ča → rámaś ča lakṣmaṇaś ča)
    - **'éva'** = právě, pouze (zdůraznění)
    - **'api'** = také, dokonce
    - Obvykle stojí za slovem, k němuž se vztahují
    """
    )

    # Výběr gramatických pravidel
    st.markdown("### 📖 Výběr gramatických pravidel")
    st.markdown("Zobrazit konkrétní gramatická pravidla:")

    moznosti = {
        "Skloňování podstatných jmen": "data/pravidla_sklonovani.csv",
        "Zájmena a jejich tvary": "data/pravidla_zajmena.csv",
        "Časování sloves": "data/pravidla_casovani.csv",
        "Pravidla sandhi (hláskové změny)": "data/pravidla_sandhi.csv",
        "Pravidla sandhi cele (hláskové změny)": "data/pravidla_sandhi_c.csv",
    }

    volba = st.selectbox("📘 Vyber typ pravidel:", list(moznosti.keys()))

    try:
        df = pd.read_csv(moznosti[volba])
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ Chyba při načítání: {e}")
