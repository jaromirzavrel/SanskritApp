# helpers/sandhi_processor.py
# SandhiProcessor, __init__, apply_sandhi_python, apply_sandhi_regex

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
import logging
import sys

# import pytest
import json
import re
import streamlit as st

from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Vlastní moduly
# from helpers.utils import urci_koncovku
from helpers.ui_display import zobraz_toast

sys.dont_write_bytecode = True  # zakázat .pyc soubory

json_file = "data/sandhi_pravidla.json"


# ==============================================================================================================================================


@dataclass
class SandhiContext:
    # Index (pozice v seznamu slov)
    index_slovo: int = -1  # index pro slova ve větě
    index_vzor: int = None  # index pro vzory/náhrady v pravidlech
    index_out: int = 0  # index pro log výstupu z procedury
    index_out_konci_na: int = 0  # index pro log výstupu z procedury _konci_na
    index_out_zacina_na: int = 0  # index pro log výstupu z procedury _zacina_na
    index_out_zpracuj_zacatek: int = 0  # index pro log výstupu z procedury _zpracuj_zacatek
    index_out_zpracuj_zacatek_nahrada: int = (
        0  # index pro log výstupu z procedury _zpracuj_zacatek_nahrada
    )

    # Vstupy pro dané spojení
    prvni: str = ""
    druhe: str = ""
    slovo: str = ""  # aktuální pracovní řetězec

    # Pravidla Vzor + Náhrady
    vzor_konec: str = ""
    vzor_zacatek: str = ""
    nahrada_konec: str = ""
    nahrada_zacatek: str = ""

    # Výsledek spojení
    spojeni: str = " "

    # Pole pro záznam změn
    zmeny: List[Dict] = field(default_factory=list)

    # Flagy
    f_nalezeno_vzor_konec: bool = False
    f_nalezeno_nahrada_konec: bool = False
    f_nalezeno_vzor_zacatek: bool = False
    f_nalezeno_nahrada_zacatek: bool = False
    f_dej_index_vzor: bool = False
    f_continue: bool = False
    f_break: bool = False

    # Vnitřní pole
    slova: List[str] = field(default_factory=list)
    pravidlo: Optional[Dict] = field(default_factory=dict)
    pravidlo_typ: str = ""
    pravidlo_konec: str = ""
    pravidlo_zacatek: str = ""
    pravidlo_nahrada_konec: str = ""
    pravidlo_nahrada_zacatek: str = ""
    pravidlo_podminky: Optional[Dict] = field(default_factory=dict)

    # ==============================================================================================================================================


class SandhiProcessor:

    # ==============================================================================================================================================

    def __init__(
        self,
        json_file: str = "data/sandhi_pravidla.json",
        skupiny: dict | None = None,
        pravidla: list | None = None,
        *,
        f_cache: bool = True,
        f_log: bool = False,
    ):
        """
        Inicializace SandhiEngine.

        Parametry:
        ----------
        json_file : str
            Soubor se sandhi pravidly (pokud pravidla nejsou předána ručně).

        skupiny : dict | None
            Slovník pojmenovaných skupin (samohlásky, měkké souhl., aj.).
            Pokud není zadán → načte se ze souboru.

        pravidla : list | None
            Seznam všech pravidel sandhi.
            Pokud není zadán → načte se ze souboru.

        f_cache : bool
            Aktivovat výsledkový cache (urychlí transformace).

        f_log : bool
            Zapnout logování detailních informací.
        """

        # Nastavit logování
        self.f_log = f_log
        self.f_cache = f_cache

        # Interní cache
        self.cache = {}  # klíč = vstupní věta, hodnota = výsledek

        # načtení skupin/pravidel z param nebo souboru
        # if skupiny is not None:
        #     self.skupiny = skupiny

        # if pravidla is not None:
        #     self.pravidla = pravidla

        # Pokud nejsou dodána skupiny nebo pravidla → načíst ze souboru
        # Načti data ze souboru, pokud nejsou předána ručně
        # if getattr(self, "skupiny", None) is None or getattr(self, "pravidla", None) is None:
        if skupiny is None or pravidla is None:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"skupiny": {}, "pravidla": []}

            # Použije se pouze tehdy, pokud nebylo předáno jako argument
            if skupiny is None:
                self.skupiny = data.get("skupiny", {})
            if pravidla is None:
                self.pravidla = data.get("pravidla", [])

        # Atributy objektu (hluboké kopie pro bezpečnost)
        self.skupiny = dict(skupiny) if skupiny is not None else {}
        self.pravidla = list(pravidla) if pravidla is not None else []

        # Validace
        self._validate()

        # Rozšířená příprava pravidel (např. pre-kompilace vzorů)
        self._prepare_rules()

        if self.f_log:
            logging.debug("SandhiEngine inicializován.")

    # ==============================================================================================================================================
    def _nacti_json(self, json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # ==============================================================================================================================================
    def _validate(self):
        if not isinstance(self.skupiny, dict):
            raise TypeError("skupiny musí být dict")

        if not isinstance(self.pravidla, list):
            raise TypeError("pravidla musí být list")

        for p in self.pravidla:
            if not isinstance(p, dict):
                raise TypeError("každé pravidlo musí být dict")

    # ==============================================================================================================================================
    def _prepare_rules(self):
        # preproces: odstraň mezery, doplň defaulty, předpočítej výrazy, atd.
        for p in self.pravidla:
            p["konec"] = p.get("konec", "") or ""
            p["zacatek"] = p.get("zacatek", "") or ""

    # ==============================================================================================================================================
    def _log_pravidlo(self, ctx: SandhiContext, nadpis: str):

        if not st.session_state["cfg"]["f_log"]:
            return

        log_txt = f"""
        {nadpis}
          index_out                         >{ctx.index_out}<
          index_out_konci_na                >{ctx.index_out_konci_na}<
          index_out_zacina_na               >{ctx.index_out_zacina_na}<
          index_out_zpracuj_zacatek         >{ctx.index_out_zpracuj_zacatek}<
          index_out_zpracuj_zacatek_nahrada >{ctx.index_out_zpracuj_zacatek_nahrada}<
          f_nalezeno_vzor_konec             >{ctx.f_nalezeno_vzor_konec}<
          f_nalezeno_nahrada_konec          >{ctx.f_nalezeno_nahrada_konec}<
          f_nalezeno_vzor_zacatek           >{ctx.f_nalezeno_vzor_zacatek}<
          f_nalezeno_nahrada_zacatek        >{ctx.f_nalezeno_nahrada_zacatek}<
          f_continue                        >{ctx.f_continue}<
          prvni                             >{ctx.prvni}<
          druhe                             >{ctx.druhe}<
          pravidlo_typ                      >{ctx.pravidlo.get('typ', '')}<
          pravidlo_konec                    >{ctx.pravidlo.get('konec', '')}<
          pravidlo_nahrada_konec            >{ctx.pravidlo.get('nahrada_konec', '')}<
          pravidlo_zacatek                  >{ctx.pravidlo.get('zacatek', '')}<
          pravidlo_nahrada_zacatek          >{ctx.pravidlo.get('nahrada_zacatek', '')}<
          pravidlo_podminky                 >{ctx.pravidlo.get('podminky', '')}<
        """

        if st.session_state["cfg"]["f_log"]:
            logging.debug(log_txt)

    # ==============================================================================================================================================

    # Pomocná funkce - začíná-li slovo na vzorek - konkrétní, nebo ze skupiny
    # "a-"
    # "*samohlaska_vse-" ["k","kh","p","ph","f","ś","ṣ","s"]
    # ["a-","á-","u-","ú-","é-","ó-"]
    def _zacina_na(
        self,
        ctx: SandhiContext,
        slovo: str,
        vzor: str | list[str] | None,
    ) -> tuple[bool, str]:
        """Zjistí, zda slovo začíná na vzor nebo na začátek z pojmenované skupiny nebo seznamu (list)."""

        if not vzor:
            ctx.index_out_zacina_na = 1
            return False, ""

        # Pokud je vzorek typu list
        if isinstance(vzor, list):

            # Projde prvky seznamu (list) a volá samu sebe
            for v in sorted(vzor, key=len, reverse=True):
                f_nalezeno, z = self._zacina_na(ctx=ctx, slovo=slovo, vzor=v)
                if f_nalezeno:
                    ctx.index_out_zacina_na = 2
                    return True, z

            ctx.index_out_zacina_na = 3
            return False, ""

        vzor = vzor.strip("-")

        # pokud začíná hvězdičkou pak za ní následuje název skupiny na kterou odkazuje
        if vzor.startswith("*"):

            # odstraní z názvu případné znaky
            jmeno = vzor.strip("*-")
            # pokud skupina tohoto jména nexistuje návrat, jinak pokračovat
            if jmeno not in self.skupiny:
                ctx.index_out_zacina_na = 4
                return False, ""

            vzor_sorted = sorted(self.skupiny[jmeno], key=len, reverse=True)
            # seřadí prvky supiny (list) dle déky a pak bere jeden po druhém
            for zacina in vzor_sorted:
                vz = zacina.strip("-")
                # a kontroluje jestli vzorek je na začátku slova
                # u kterého najde shodu vrátí True = našel jsem, a hodnotu vzorku začátku
                if slovo.startswith(vz):
                    ctx.index_out_zacina_na = 5
                    return True, vz
            # nenajde-li žádný vhodný vzorek vrátí False = nenašel jsem, a prázdný řetězec""
            ctx.index_out_zacina_na = 6
            return False, ""
        else:
            vz = vzor
            # kontroluje jestli je vzorek na začátku slova
            ctx.index_out_zacina_na = 7
            return (True, vz) if slovo.startswith(vz) else (False, "")

    def _normalize_vzor(self, vzor: str | list[str] | None) -> list[str]:
        # výchozí hodnota - neočekávaný typ
        vzory = []

        # --- 3. PRAVIDLO - LIST VZORŮ ---
        # --- 3. Pokud je vzor seznam ---
        # Pokud je vzorek typu list (např. ["-as", "-aḥ"]), zkus každý
        if isinstance(vzor, list):
            # Primární list z pravidla
            vzory = vzor

        # --- 4. STRING SKUPINA / VZOR ---
        elif isinstance(vzor, str):

            # Není-li to list pak je to prostý string a
            # začíná-li hvězdičkou je to odkaz na skupinu
            # jinak je to prostý řetězec - přímo vzor
            vz = vzor.strip("-")

            # --- 4.1 HVĚZDIČKOVÁ SKUPINA ---
            # --- 4.1 SKUPINA "*..." ---
            # Pokud vzorek začíná hvězdičkou, je to odkaz na skupinu
            if vz.startswith("*"):

                # Skupina
                jmeno = vz.strip("*-")

                if jmeno not in self.skupiny:
                    # vrací - nalezeno, vzor, idx (musí být ctx.f_dej_index_vzor True pro pravidlo, False pro skupinu)
                    return vzory

                vzory = self.skupiny.get(jmeno, [])

            else:
                # Prostý řetězec string - přímo vzor
                vzory = [vz]  # zabalíme do listu pro další zpracování

        return vzory

    def _konci_na(  # noqa: C901
        self,
        ctx: SandhiContext,
        slovo: str | None = None,
        # slovo_override: str | None = None,
        vzor: str | list[str] | None = None,
        # index_override: int | None = None,
    ) -> tuple[bool, str, int | None]:
        """
        Sjednocená verze:
        - List (pravidlo)
        - Skupiny "*..."
        - Prostý string
        - Náhrady podle indexu

        Zjistí, zda slovo končí na konec z pojmenované skupiny nebo seznamu (list) nebo na vzor.
        ve slově hledá vzor, případně pořadí vzoru, nebo vrací vzor z pořadí
        vrátí - nalezeno, co nalezl, pořadí, nebo vrací vzor z pořadí
        *
        Kontextová verze původní funkce _konci_na().
        - Pokud je třeba zpracovat skutečné slovo, použije ctx.slovo / ctx.prvni.
        - Pokud se vyhodnocují náhrady, použije se slovo_override = "".
        - f_dej_index_vzor a index se berou z ctx (ne z parametrů), pokud nejsou override.
        - Vrací tuple (nalezeno: bool, nalezený_vzor: str, index: Optional[int]).
        """

        # --- 1. Ochrana proti None, Pokud není vzor, nemůže být shoda ---
        # vzor může být list, str (* skupina ta je list, hodnota str) nebo None
        # if vzor is None:
        # if not vzor:  # je řešeno ve volající procedůře
        #     return False, "", None

        # --- 2. Vstupní hodnoty ---
        slovo = slovo or ""
        # slovo = (
        #     slovo_override
        #     if slovo_override is not None
        #     else (ctx.slovo or ctx.prvni or "")
        # )

        # Vždy dostaneme list nebo None
        vzory = self._normalize_vzor(vzor=vzor)

        if not vzory:
            ctx.index_out_konci_na = 1
            return False, "", None

        # 1. Skupina Náhrada podle indexu (slovo == "")
        # Když je f_dej_index_vzor a index a slovo == "" vrať hodnotu z pořadí → náhrada
        # (není oštřeno neplatnost indexu) (pro náhradu)
        # vrací odpovídající náhradu podle pořadí, indexu vzoru ze seznamu, list v pravidle
        if slovo == "":
            # Hledej podle pořadí
            if ctx.f_dej_index_vzor:
                if ctx.index_vzor is not None:
                    try:
                        # vrací - nalezeno, vzor, idx (musí být ctx.f_dej_index_vzor True pro pravidlo, False pro skupinu)
                        ctx.index_out_konci_na = 2
                        return (True, vzory[ctx.index_vzor], None)
                    except IndexError:
                        ctx.index_out_konci_na = 3
                        return False, "", None
            elif len(vzory) == 1:
                try:
                    # vrací - nalezeno, vzor, idx (musí být ctx.f_dej_index_vzor True pro pravidlo, False pro skupinu)
                    ctx.index_out_konci_na = 4
                    return (True, vzory[0], None)
                except IndexError:
                    ctx.index_out_konci_na = 5
                    return False, "", None

        # 2. Normální režim – setřídit pokud netřeba zachovat pořadí
        # Když je dej index - netřídit
        vzory_sorted = sorted(vzory, key=len, reverse=True)

        # 3. Vyhodnocení jednotlivých vzorů
        # Prohledávání seznamu — lokální index
        # --- Vyhledání shody ---
        # idx = 0
        for idx, v in enumerate(vzory_sorted):
            # položka listu - skupiny
            vz = v.strip("-")

            # slovo končí na položku ze skupiny na indexu idx
            # Test konce
            if slovo.endswith(vz):
                # na skupinu není vázána náhrada konec ani začátek
                # ctx.f_dej_index_vzor se používá pro seznam, list který je přímo v pravidle s odpovídajícími náhradami v pravidle
                # primární list musí být unique, řazený vůči odpovídajícím sekundárním, pak musí být ctx.f_dej_index_vzor True
                # ctx.vzor_konec = vz
                # ctx.index = len(slovo) - len(vz)
                # ctx.index_vzor = idx if ctx.f_dej_index_vzor else None
                ctx.index_vzor = vzory.index(v) if ctx.f_dej_index_vzor else None
                # vrací - nalezeno, vzor, idx (musí být ctx.f_dej_index_vzor True pro pravidlo, False pro skupinu)
                ctx.index_out_konci_na = 6
                return True, vz, ctx.index_vzor
            # idx = idx + 1

            # return True, vz, (idx if not ctx.f_dej_index_vzor else ctx.index_vzor)

        # když slovo nekončí na žádnou položku ze skupiny
        # vrací - nalezeno, vzor, idx (musí být ctx.f_dej_index_vzor True pro pravidlo, False pro skupinu)
        ctx.index_out_konci_na = 7
        return False, "", None

    # ==============================================================================================================================================
    def _zpracuj_konec(self, ctx: SandhiContext) -> SandhiContext:
        """
        Zpracuje konec prvního slova podle pravidla ve ctx.pravidlo.
        Aktualizuje:
        ctx.index_vzor,
        ctx.f_dej_index_vzor,
        ctx.vzor_konec,
        ctx.f_nalezeno_vzor_konec,
        ctx.f_continue,
        ctx.f_break,
        """

        # ====================== RESET VŠECH STAVŮ ======================
        ctx.index_vzor = None  # reset indexu pro pravidla vybraného vzoru (list)
        ctx.f_dej_index_vzor = False  # dej index v seznamu vzorů a náhrady
        ctx.vzor_konec = ""  # nalezený vzor konce
        ctx.f_nalezeno_vzor_konec = False  # zda byl vzor nalezen
        # ctx.f_continue = False  # signál pro “přejít na další pravidlo”
        # ctx.f_break = False  # nalezeno signál pro “ukončit zpracování pravidel”

        # ========== 1. NAČTENÍ VZORU ==========
        # Kontrola konců prvního slova
        # Pokud pravidlo nemá definován vzor konce → pokračuje se na další pravidlo
        konec_vzor = ctx.pravidlo.get("konec", "")
        # if konec_vzor in {None, ""}:
        if not konec_vzor:
            ctx.f_continue = True
            # ctx.index_out = ctx.index_out + 1
            ctx.index_out = 1
            return ctx

        # ========== 2. NAČTENÍ PODMÍNEK ==========
        # je-li pravidlo vzor i náhrada list pak třeba vybírat dle indexu proto f_dej_index_vzor
        podminky = ctx.pravidlo.get("podminky", {})
        # ctx.index_vzor bude pořadí vzoru konce a také pořadí náhrady
        ctx.f_dej_index_vzor = podminky.get("f_dej_index_vzor", False)

        # ========== 3. VYHLEDÁNÍ KONCE ==========
        # --- zpracování konce prvního slova (konec může být list nebo string) ---
        # Může být seznam, odkaz na skupinu, hodnota
        # Kontrola konce prvního slova podle vzoru pravidla
        (
            ctx.f_nalezeno_vzor_konec,
            ctx.vzor_konec,
            ctx.index_vzor,
        ) = self._konci_na(
            ctx=ctx,
            slovo=ctx.prvni,
            # slovo_override=ctx.prvni,
            vzor=konec_vzor,  # může být skupina, seznam, hodnota
            # index_override=None,
        )

        # 4. Nenalezeno → toto pravidlo se vynechá
        # Pokdud slovo nemá konec dle vzorku pravidla jde na další pravidlo, vzorek
        # jinak pokračuje v běhu na kontrolu začátků
        # nedostatečné ošetřuje jen konkrétní vzorek ne seznamy
        if not ctx.f_nalezeno_vzor_konec:
            ctx.f_continue = True
            ctx.index_out = 2
            return ctx

        if ctx.vzor_konec is None or (isinstance(ctx.vzor_konec, str) and ctx.vzor_konec == ""):
            ctx.f_continue = True
            ctx.index_out = 3
            return ctx

        # 5. Nalezeno → pokračujeme na náhradu konce
        ctx.f_continue = False
        ctx.index_out = 4

        # Logging
        self._log_pravidlo(ctx=ctx, nadpis="Nalezen konec:")

        return ctx

    def _zpracuj_konec_nahrada(self, ctx: SandhiContext) -> SandhiContext:
        """
        Zpracuje náhradu konce prvního slova a aktualizuje ctx.
        """

        # Reset výstupů
        ctx.nahrada_konec = ""
        ctx.f_nalezeno_nahrada_konec = False
        ctx.f_continue = False

        # náhrada konec je konkétní hodnota ale i ["-iḥ","-éḥ","-uḥ","-óḥ"] nahradí celý vzorek
        # (jen někde jsou více možností) ["b","p"], ["d","n"]
        # může být "_" ponechat původní, bez změny
        # může být "x" vypustit celý vzorek z konce (zatím není)
        # Může být seznam, odkaz na skupinu, hodnota
        # Získat definici náhrady z pravidla
        konec_nahr = ctx.pravidlo.get("nahrada_konec", "")

        # Prázdná náhrada = nepokračovat, ale nevykonávat nic
        # if konec_nahr in {None, ""}:
        if not konec_nahr:
            ctx.f_continue = True
            ctx.index_out = 5
            return ctx

        # "_" → ponechat původní konec (žádná změna, ale pravidlo pokračuje)
        if konec_nahr == "_":
            ctx.nahrada_konec = "_"
            ctx.f_nalezeno_nahrada_konec = True
            ctx.f_continue = False
            ctx.index_out = 6
            return ctx

        # "x" → vypustit celý konec
        if konec_nahr == "x":
            ctx.nahrada_konec = ""
            ctx.f_nalezeno_nahrada_konec = True
            ctx.f_continue = False
            ctx.index_out = 7
            return ctx

        # --- Normální výpočet (konci_na) ---
        # Náhrady vždy vyhodnocujeme na prázdném „slovu“ = neporovnáváme konce
        # Může být seznam, odkaz na skupinu, hodnota
        (
            ctx.f_nalezeno_nahrada_konec,
            ctx.nahrada_konec,
            ctx.index_vzor,
        ) = self._konci_na(
            ctx=ctx,
            slovo="",
            # slovo_override="",
            vzor=konec_nahr,
            # index_override=None,
        )

        # Kontroly
        # Pokud náhrada nebyla nalezena → pravidlo se ukončí
        if not ctx.f_nalezeno_nahrada_konec:
            ctx.f_continue = True
            ctx.index_out = 8
            return ctx

        if not ctx.nahrada_konec:
            ctx.f_continue = True
            ctx.index_out = 9
            return ctx

        # Nalezeno, vracíme
        ctx.f_continue = False
        ctx.index_out = 10
        return ctx

    def _zpracuj_zacatek(self, ctx: SandhiContext) -> SandhiContext:
        """
        Zpracuje vzor začátku druhého slova.
        Výsledek uloží do:
            ctx.f_nalezeno_vzor_zacatek
            ctx.vzor_zacatek
            ctx.f_continue
        """

        ctx.f_continue = False
        ctx.vzor_zacatek = ""
        ctx.f_nalezeno_vzor_zacatek = False

        # --- 1. vzor začátku ---
        # ========== 1. NAČTENÍ VZORU ==========
        # Může být seznam, odkaz na skupinu, hodnota
        zacatek_vzor = ctx.pravidlo.get("zacatek", "")

        if not zacatek_vzor:
            ctx.f_continue = True
            ctx.index_out_zpracuj_zacatek = 1
            return ctx

        # --- 2. kontrola začátku ---
        # ========== 2. VYHLEDÁNÍ ZAČÁTKU ==========
        # Kontrola začátku druhého slova podle vzoru pravidla
        ctx.f_nalezeno_vzor_zacatek, ctx.vzor_zacatek = self._zacina_na(
            ctx=ctx, slovo=ctx.druhe, vzor=zacatek_vzor
        )

        # 3. Nenalezeno → toto pravidlo se vynechá
        # pokdud začátek druhého slova není dle vzorku pravidla jde na další pravidlo, vzorek
        # jinak pokračuje v běhu na provedení náhrad vzorků sandhi
        if not ctx.f_nalezeno_vzor_zacatek:

            ctx.f_continue = True
            ctx.index_out_zpracuj_zacatek = 2

            # Logging
            self._log_pravidlo(ctx=ctx, nadpis="Nenalezen začátek:")

            return ctx

        if not ctx.vzor_zacatek:

            ctx.f_continue = True
            ctx.index_out_zpracuj_zacatek = 3

            # Logging
            self._log_pravidlo(ctx=ctx, nadpis="Nenalezen vzor začátek:")

            return ctx

        # 4. Nalezeno → pokračujeme na náhradu začátku
        ctx.f_continue = False
        ctx.index_out_zpracuj_zacatek = 4

        # --- 3. LOG nalezeného začátku ---
        # Logging
        self._log_pravidlo(ctx=ctx, nadpis="Nalezen začátek:")

        return ctx

    def _zpracuj_zacatek_nahrada(self, ctx: SandhiContext) -> SandhiContext:
        """
        Zpracuje náhradu začátku druhého slova (aktualizuje ctx.spojeni, ctx.nahrada_zacatek).
        Pokud pravidlo nemá nahradu začátku -> ctx.f_continue = True (pokračuj dalším pravidlem).
        Pokud podmínky nesplňují (např. !pad, !cislo) -> ctx.f_continue = True (není vhodné pravidlo).
        """

        from helpers.utils import urci_koncovku

        # return f_continue, spojeni, nahrada_zacatek, pravidlo_typ

        ctx.f_continue = False
        # prav_typ = ""
        ctx.f_nalezeno_nahrada_zacatek = False
        ctx.nahrada_zacatek = ""
        ctx.spojeni = ctx.spojeni or " "

        # náhrada začátek může začínat + plus tj. slova se spojí
        # tj. pro druhé slovo nepřidáme mezeru (spojeni = "")
        # pokud nezačíná plus musíme mu přidat na začátek mezeru (spojeni = " ")
        # může být "_" ponechat původní, bez změny
        # může být "x" vypustit celý vzorek začátku
        # náhrada začátek je konkétní hodnota nahradí celý vzorek
        # náhrada začátek není seznam, ani skupina
        zacatek_nahr = ctx.pravidlo.get("nahrada_zacatek", "").strip("-")
        # print(f"Začátek>{zacatek_nahr}< spojení >{spojeni}<")
        # zobraz_toast(f"Začátek>{zacatek_nahr}< spojení >{spojeni}<", trvani = 5, f_privileg = True)
        if not zacatek_nahr:
            # žádná náhrada začátku -> není to vhodné pravidlo
            ctx.f_continue = True
            ctx.index_out_zpracuj_zacatek_nahrada = 1
            return ctx

        # spojení: pokud začíná + => bez mezery, jinak mezera
        if zacatek_nahr.startswith("+"):
            # zobraz_toast(f"Začátek>{zacatek_nahr}< spojení >{spojeni}<", trvani = 5, f_privileg = True)
            ctx.spojeni = ""
            ctx.nahrada_zacatek = zacatek_nahr.strip("+")  # _xzn
        else:
            # zobraz_toast(f"Začátek>{zacatek_nahr}< spojení >{spojeni}<", trvani = 5, f_privileg = True)
            ctx.spojeni = " "
            ctx.nahrada_zacatek = zacatek_nahr

        # kontrola podmínek (pad, cislo, ...) - pokud jsou definovány a nesplňují -> není vhodné pravidlo
        # prav_typ = ctx.pravidlo.get('typ', '')
        podminky = ctx.pravidlo.get("podminky", {})

        if podminky:
            podm_pad = podminky.get("pad", "")
            podm_cislo = podminky.get("cislo", "")

            # if not podm_pad == "" or not podm_cislo == "":
            if podm_pad or podm_cislo:
                # aktualni_slovo = st.session_state['matice_vety'][i]
                aktualni_slovo = (
                    ctx.slova[ctx.index_slovo]
                    if ctx.slova and 0 <= ctx.index_slovo < len(ctx.slova)
                    else None
                )
                if aktualni_slovo:
                    # najít koncovku (typ) a pád v řádku tvaru, podobně jako jinde v kódu
                    aktualni_typ = aktualni_slovo.get("typ", "")
                    slovni_druh = st.session_state["slovni_druh"]

                    r_typ = next(
                        (r for r in slovni_druh if r["typ"] == aktualni_typ), slovni_druh[0]
                    )

                    koncovka = urci_koncovku(r_typ["typ"])  # (utils.py)
                    # koncovka = r_typ['typ']

                    aktualni_pad = aktualni_slovo.get(f"pad_{koncovka}", "")
                    aktualni_cislo = aktualni_slovo.get(f"cislo_{koncovka}", "")

                if podm_pad and podm_pad.startswith("!"):
                    podm_ne_pad = podm_pad.strip("!")
                    # Nesmí být tento pád, tento pád ne sandhi
                    # Ikdyž jsem slova nabral tak je nemusím vracet pokud je bez sandhi
                    if aktualni_pad == podm_ne_pad:
                        ctx.f_continue = True  # další slovo
                        ctx.index_out_zpracuj_zacatek_nahrada = 2
                        return ctx

                if podm_cislo and podm_cislo.startswith("!"):
                    podm_ne_cislo = podm_cislo.strip("!")
                    # Nesmí být toto číslo, toto číslo ne sandhi
                    # Ikdyž jsem slova nabral tak je nemusím vracet pokud je bez sandhi
                    if aktualni_cislo == podm_ne_cislo:
                        ctx.f_continue = True  # další slovo
                        ctx.index_out_zpracuj_zacatek_nahrada = 3
                        return ctx
        else:
            podm_cislo = ""
            podm_pad = ""

        # pokud jsme došli sem => náhrada začátku platí
        ctx.f_nalezeno_nahrada_zacatek = True
        ctx.f_continue = False

        ctx.index_out_zpracuj_zacatek_nahrada = 4
        return ctx

    def _nahrada_nahrada(self, ctx: SandhiContext) -> SandhiContext:
        """
        Provede náhradu podle pravidla a vrátí (f_break, slova, zmeny)
        """

        prvni = ctx.prvni
        druhe = ctx.druhe

        # --- náhrada konce prvního ---
        # prvni, vzor_konec, nahrada_konec
        if ctx.nahrada_konec.startswith("_"):  # bez změny
            nove_prvni = prvni
        elif ctx.nahrada_konec.startswith("x"):  # vypustit
            nove_prvni = prvni[: -len(ctx.vzor_konec)]
        else:  # nahradit
            nove_prvni = prvni[: -len(ctx.vzor_konec)] + ctx.nahrada_konec

        # --- náhrada začátku druhého ---
        # logika nahrazení začátku druhého
        # Náhrada začátku druhého slova podle typu označení v nahr_zacatek
        # druhe, vzor_zacatek, nahrada_zacatek
        if ctx.nahrada_zacatek.startswith("_"):  # bez změny
            nove_druhe = ctx.spojeni + druhe
        elif ctx.nahrada_zacatek.startswith("x"):  # vypustit
            nove_druhe = ctx.spojeni + druhe[len(ctx.vzor_zacatek) :]
        else:  # nahradit
            nove_druhe = ctx.spojeni + ctx.nahrada_zacatek + druhe[len(ctx.vzor_zacatek) :]

        # OK

        nova_dvojice = nove_prvni + nove_druhe

        # OK
        # --- zapsat změnu ---
        ctx.zmeny.append(
            {
                "index_slovo": ctx.index_slovo,
                "puvod": prvni + " " + druhe,
                "novy": nova_dvojice,
                "pravidlo": ctx.pravidlo.get("typ", ""),
            }
        )

        # --- uložit do slov ---
        # if not hasattr(ctx, "pslova") or ctx.pslova is None:
        #     ctx.pslova = ctx.slova.copy()
        ctx.slova[ctx.index_slovo] = nove_prvni
        ctx.slova[ctx.index_slovo + 1] = nove_druhe

        ctx.prvni = ctx.slova[ctx.index_slovo]
        ctx.druhe = ctx.slova[ctx.index_slovo + 1]

        # Logging
        self._log_pravidlo(ctx=ctx, nadpis="Výsledek:")

        ctx.f_break = True  # první vhodná varianta
        return ctx

    def zaver_1(self, ctx: SandhiContext):
        #     i: int | None = None,
        #     slova: list[str] | None = None,
        #     druhe: str = "",
        i = ctx.index_slovo
        nove_druhe = ctx.slova[i + 1]

        if not ctx.f_nalezeno_vzor_konec or (
            ctx.f_nalezeno_vzor_konec and not ctx.f_nalezeno_vzor_zacatek
        ):
            ctx.spojeni = " "
            nove_druhe = ctx.spojeni + ctx.druhe
            ctx.slova[i + 1] = nove_druhe

        # Logging
        # log_txt = f"""Za slovem:
        #   f_nalezeno_vzor_konec    >{ctx.f_nalezeno_vzor_konec}<
        #   f_nalezeno_vzor_zacatek  >{ctx.f_nalezeno_vzor_zacatek}<
        #   nove_druhe               >{nove_druhe}<
        # """
        log_txt = f"""Za slovem:
          nove_druhe                  >{nove_druhe}<
        """
        self._log_pravidlo(ctx=ctx, nadpis=log_txt)

    def zaver_2(self, ctx: SandhiContext):

        # Logging
        self._log_pravidlo(ctx=ctx, nadpis="KONEC:")

    def aplikuj_sandhi(self, veta: str) -> tuple[str, list]:
        """
        Hlavní vstupní bod procesoru Sandhi.
        Přijímá větu jako string.
        Aplikuje pravidla Sandhi podle JSON struktury pomocí SandhiContext.
        Vrací výslednou větu a seznam změn
        (věta_po_sandhi, seznam_změn).
        """

        # 1. Split (rozdělení) na slova
        slova = veta.split()
        if not slova:
            return "", []

        # 2. Inicializace kontextu
        ctx = SandhiContext(
            index_slovo=-1,
            index_vzor=None,
            prvni="",
            druhe="",
            slovo="",
            slova=slova.copy(),
            zmeny=[],
            spojeni=" ",
            pravidlo={},
            vzor_konec="",
            vzor_zacatek="",
            nahrada_konec="",
            nahrada_zacatek="",
            f_nalezeno_vzor_konec=False,
            f_nalezeno_nahrada_konec=False,
            f_nalezeno_vzor_zacatek=False,
            f_nalezeno_nahrada_zacatek=False,
            f_dej_index_vzor=False,
            f_continue=False,
            f_break=False,
        )

        # ----- Hlavní smyčka - procházení slov ------------
        # Pro každá dvě po sobě jdoucí slova
        for i in range(len(slova) - 1):
            ctx.index_slovo = i  # i-té 1. slovo
            ctx.index_vzor = None  # reset indexu pro pravidla
            ctx.prvni = ctx.slova[i]
            ctx.druhe = ctx.slova[i + 1]
            ctx.slovo = ctx.prvni  # <-- nutné: výchozí "upravené" první slovo
            # ctx.pslova = ctx.slova.copy()
            ctx.spojeni = " "

            ctx.pravidlo = {}
            ctx.vzor_konec = ""
            ctx.vzor_zacatek = ""
            ctx.nahrada_konec = ""
            ctx.nahrada_zacatek = ""

            ctx.f_nalezeno_vzor_konec = False
            ctx.f_nalezeno_nahrada_konec = False
            ctx.f_nalezeno_vzor_zacatek = False
            ctx.f_nalezeno_nahrada_zacatek = False
            ctx.f_continue = False
            ctx.f_break = False

            # druhe = spojeni + druhe

            # 4. Procházení pravidel
            # Iterace přes pravidla - hledáme první relevantní
            for pravidlo in self.pravidla:  # načtou se v __init__
                # načte vzorek pravidla - řádek
                ctx.pravidlo = pravidlo

                # log_txt = f"""
                # Začátek cyklu pravidel:
                #   pravidlo_typ             >{ctx.pravidlo.get('typ', '')}<
                #   pravidlo_konec           >{ctx.pravidlo.get('konec', '')}<
                #   pravidlo_zacatek         >{ctx.pravidlo.get('zacatek', '')}<
                #   pravidlo_nahrada_konec   >{ctx.pravidlo.get('nahrada_konec', '')}<
                #   pravidlo_nahrada_zacatek >{ctx.pravidlo.get('nahrada_zacatek', '')}<
                #   pravidlo_podminky        >{ctx.pravidlo.get('podminky', {})}<
                # """

                # if st.session_state['cfg']['f_log']:
                #     logging.debug(log_txt)
                # zobraz_toast(log_txt, trvani = 5, f_privileg = True)

                # --- KONEC ---
                # Zpracování konce prvního slova
                ctx = self._zpracuj_konec(ctx)
                self._log_pravidlo(ctx=ctx, nadpis="Po _zpracuj_konec:")

                if ctx.f_continue:
                    continue  # další pravidlo

                # kontrola začátků druhého slova
                # v pravidlo není položka varianty mám rozepsáno
                # for varianta in pravidlo['varianty']:
                #     zacatek_vzor = varianta['zacatek']
                #     nahr_konec   = varianta.get('nahrada_konec', '').replace("-", "")
                #     nahr_zacatek = varianta.get('nahrada_zacatek', '')
                #     typ          = pravidlo.get('typ', '')

                # for varianta in pravidlo['zacatek']:
                if True:

                    # --- náhrada konce ---
                    # Zpracování náhrady konce
                    ctx = self._zpracuj_konec_nahrada(ctx)
                    self._log_pravidlo(ctx=ctx, nadpis="Po _zpracuj_konec_nahrada:")

                    if ctx.f_continue:
                        continue  # další pravidlo

                    # --- začátek ---
                    # Zpracování začátku druhého slova
                    ctx = self._zpracuj_zacatek(ctx)
                    self._log_pravidlo(ctx=ctx, nadpis="Po _zpracuj_zacatek:")

                    if ctx.f_continue:
                        continue  # další pravidlo

                    # --- náhrada začátku ---
                    # Náhrada začátku
                    ctx = self._zpracuj_zacatek_nahrada(ctx)
                    self._log_pravidlo(ctx=ctx, nadpis="Po _zpracuj_zacatek_nahrada:")

                    if ctx.f_continue:
                        continue  # další pravidlo

                    # --- pravidlo má náhradu obou stran ---
                    # Pokud obě strany mají nalezené vzory, a náhrady proveď vlastní náhradu
                    # (metoda _nahrada_nahrada by měla upravit ctx.slovo a ctx.druhe, doplnit ctx.zmeny a nastavit ctx.f_break = True)
                    ctx = self._nahrada_nahrada(ctx)
                    self._log_pravidlo(ctx=ctx, nadpis="Po _nahrada_nahrada:")

                    # po úspěšné náhradě přerušujeme hledání dalších pravidel pro tuto dvojici
                    if ctx.f_break:
                        break

                    # pokud _nahrada_nahrada nenalezla použitelnou náhradu,
                    # může být vhodné pokračovat v hledání dalších pravidel
                    # (v takovém případě nic nekazíme a běží další pravidlo)

                # else:
                #     continue
                # break  # první vhodné pravidlo
            # End for pravidla

            # po vyčerpání pravidel / break => zpracuj výsledky pro tuto dvojici

            # 5. Během smyčky uložíme slova zpět
            # Nutný zápis zpět do seznamu slov (kvůli per-partes dalšímu zpracování)
            #  - ctx.slovo je upravené první slovo
            #  - ctx.druhe je upravené druhé slovo (může obsahovat spojení na začátku)
            # aktualizace slov
            # slova[i] = ctx.slova[i]
            # slova[i + 1] = ctx.slova[i + 1]
            # slova[i] = ctx.slovo
            # slova[i] = ctx.prvni
            # slova[i + 1] = ctx.druhe

            # synchronizuj v kontextu: (volitelné, ale udržuje konzistenci)
            # ctx.slova = slova

            # Uzavření kroku
            # Konec smyčky přes pravidla pro tuto dvojici
            # Provést závěrečné zpracování/report (volitelně)
            self.zaver_1(ctx)
            self._log_pravidlo(ctx=ctx, nadpis="Po zaver_1:")

        # End for slova
        # Chybí zpracování podmínek - pád, číslo - nutno předat i větu s parametry slov
        # Jak je ošetřeno když nemají vzor aby slova nevypadla.
        # Beru slova a vracím změny, když nevrátím změny zůstává původní.

        # 6. Celkový závěr
        # Konec hlavní smyčky přes dvojice
        self.zaver_2(ctx)
        self._log_pravidlo(ctx=ctx, nadpis="Po zaver_2:")

        # 7. Výsledná věta
        # Spojení všech ne-prázdných tokenů (pozor: ctx.druhe může již obsahovat počáteční mezeru/spojení)
        vysledna_veta = "".join([s for s in ctx.slova if s])

        # Vrátíme větu a zmeny
        # zobraz_toast(f"Po sandhi >{vysledna_veta}<", trvani = 5, f_privileg = True)
        return vysledna_veta, ctx.zmeny


# ==============================================================================================================================================

if __name__ == "__main__":
    sp = SandhiProcessor(json_file)
    vstup = "naraḥ gaččhati atra adja"

    vysledek, zmeny = sp.aplikuj_sandhi(vstup)

    print("Původní text:", vstup)
    print("Výsledek:    ", vysledek)
    print("Změny:")
    for z in zmeny:
        print(f" - {z['puvod']} → {z['novy']} (pravidlo: {z['pravidlo']})")
