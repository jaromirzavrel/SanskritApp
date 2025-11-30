# helpers/transliterate.py

# transliterate_deva_to_iast(text)    Přepis dévanágarí do IAST
# transliterate_iast_to_deva(text)    Přepis IAST do dévanágarí
# transliterate_iast_to_czech_v(text) Přepis IAST do Český vědecký
# transliterate_czech_v_to_iast(text) Přepis Český vědecký do IAST
# transliterate_iast_to_czech_f(text) Přepis IAST do Český fonetický, pro čtení
# transliterate_iast_to_czech_l(text) Přepis IAST do Český literární (zjednodušený pro běžné čtení)
# transliterate_czech_v_to_deva(text) Přepis Český vědecký do dévanágarí = czech_v to iast to deva

# import
import streamlit as st

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


# 📌 Přepis IAST do dévanágarí
def transliterate_iast_to_deva(text):
    if text is None:
        return ""
    return transliterate(text, sanscript.IAST, sanscript.DEVANAGARI)


# 📌 Přepis dévanágarí do IAST
def transliterate_deva_to_iast(text):
    if text is None:
        return ""
    return transliterate(text, sanscript.DEVANAGARI, sanscript.IAST)


# 📜 IAST → český přepis vědecký
# 📌 Přepis IAST do Český vědecký
def transliterate_iast_to_czech_v(text):
    if text is None:
        return ""
    return (
        text.replace("jh", "džh")
        .replace("jñ", "džñ")
        .replace("j", "dž")
        .replace("y", "j")
        .replace("ai", "ai")
        .replace("au", "au")
        .replace("kh", "kh")
        .replace("gh", "gh")
        .replace("ṭh", "ṭh")
        .replace("ḍh", "ḍh")
        .replace("th", "th")
        .replace("dh", "dh")
        .replace("ch", "čh")
        .replace("ph", "f")
        .replace("bh", "bh")
        .replace("a", "a")
        .replace("ā", "á")
        .replace("i", "i")
        .replace("ī", "í")
        .replace("u", "u")
        .replace("ū", "ú")
        .replace("e", "é")
        .replace("o", "ó")
        .replace("ṛ", "ṛ")
        .replace("ṝ", "ṝ")
        .replace("ḷ", "ḷ")
        .replace("ḹ", "ḹ")
        .replace("ṅ", "ṅ")
        .replace("ñ", "ñ")
        .replace("ṇ", "ṇ")
        .replace("n", "n")
        .replace("m", "m")
        .replace("ś", "ś")
        .replace("ṣ", "ṣ")
        .replace("k", "k")
        .replace("g", "g")
        .replace("ṭ", "ṭ")
        .replace("ḍ", "ḍ")
        .replace("t", "t")
        .replace("d", "d")
        .replace("ṃ", "ṃ")
        .replace("ḥ", "ḥ")
        .replace("h", "h")
        .replace("r", "r")
        .replace("l", "l")
        .replace("v", "v")
        .replace("c", "č")
        .replace("p", "p")
        .replace("b", "b")
        .replace("ʼ", "ʼ")
    )


# 📜 český přepis vědecký → IAST
# 📌 Přepis Český vědecký do IAST
def transliterate_czech_v_to_iast(text):
    if text is None:
        return ""
    return (
        text.replace("j", "y")
        .replace("džñ", "jñ")
        .replace("džh", "jh")
        .replace("dž", "j")
        .replace("ai", "ai")
        .replace("au", "au")
        .replace("kh", "kh")
        .replace("gh", "gh")
        .replace("ṭh", "ṭh")
        .replace("ḍh", "ḍh")
        .replace("th", "th")
        .replace("dh", "dh")
        .replace("čh", "ch")
        .replace("bh", "bh")
        .replace("p", "p")
        .replace("f", "ph")
        .replace("a", "a")
        .replace("á", "ā")
        .replace("i", "i")
        .replace("í", "ī")
        .replace("u", "u")
        .replace("ú", "ū")
        .replace("é", "e")
        .replace("ó", "o")
        .replace("ṛ", "ṛ")
        .replace("ṝ", "ṝ")
        .replace("ḷ", "ḷ")
        .replace("ḹ", "ḹ")
        .replace("ṅ", "ṅ")
        .replace("ñ", "ñ")
        .replace("ṇ", "ṇ")
        .replace("n", "n")
        .replace("m", "m")
        .replace("ś", "ś")
        .replace("ṣ", "ṣ")
        .replace("k", "k")
        .replace("g", "g")
        .replace("ṭ", "ṭ")
        .replace("ḍ", "ḍ")
        .replace("t", "t")
        .replace("d", "d")
        .replace("ṃ", "ṃ")
        .replace("ḥ", "ḥ")
        .replace("h", "h")
        .replace("r", "r")
        .replace("l", "l")
        .replace("v", "v")
        .replace("č", "c")
        .replace("b", "b")
        .replace("ʼ", "ʼ")
    )


# 📌 Přepis Český vědecký do dévanágarí = czech_v to iast to deva
def transliterate_czech_v_to_deva(text):
    if text is None:
        return ""
    return transliterate_iast_to_deva(transliterate_czech_v_to_iast(text))


# 📌 Přepis IAST do Český fonetický, pro čtení
def transliterate_iast_to_czech_f(text):
    if text is None:
        return ""
    return (
        text.replace("jñ", "gx")
        .replace("j", "dž")
        .replace("gx", "gj")
        .replace("y", "j")
        .replace("ch", "čh")
        .replace("c", "č")
        .replace("ph", "f")
        .replace("ṅ", "ng")
        .replace("ñ", "ň")
        .replace("ṇ", "ṇ")
        .replace("ī", "í")
        .replace("ṛ", "ṛi")
        .replace("ṝ", "ṝí")
        .replace("ā", "á")
        .replace("ū", "ú")
        .replace("e", "é")
        .replace("o", "ó")
        .replace("ḷ", "ḷ")
        .replace("ḹ", "ḹ")
        .replace("ś", "ś")
        .replace("ṣ", "ṣ")
        .replace("ṭ", "ṭ")
        .replace("ḍ", "ḍ")
        .replace("ṃ", "ṃ")
        .replace("ḥ", "ḥ")
        .replace("ʼ", "ʼ")
    )


# 📌 Přepis IAST do Český literární (zjednodušený pro běžné čtení)
def transliterate_iast_to_czech_l(text):
    if text is None:
        return ""
    return (
        text.replace("jñ", "gx")
        .replace("j", "dž")
        .replace("gx", "gj")
        .replace("y", "j")
        .replace("ch", "čh")
        .replace("c", "č")
        .replace("ph", "f")
        .replace("ṅ", "ng")
        .replace("ñ", "ň")
        .replace("ṇ", "n")
        .replace("ī", "í")
        .replace("ṛ", "ri")
        .replace("ṝ", "rí")
        .replace("ā", "á")
        .replace("ū", "ú")
        .replace("e", "é")
        .replace("o", "ó")
        .replace("ḷ", "l")
        .replace("ḹ", "ĺ")
        .replace("ṃ", "m")
        .replace("ḥ", "h")
        .replace("ṭ", "t")
        .replace("ḍ", "d")
        .replace("ś", "š")
        .replace("ṣ", "š")
        .replace("ʼ", "")
    )
