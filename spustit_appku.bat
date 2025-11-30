@echo off
REM Spustí Streamlit aplikaci
REM ======================================================
REM  Spustí Streamlit aplikaci – SanskritApp
REM  Používá lokální virtuální prostředí, pokud existuje
REM ======================================================

chcp 65001 > nul

title Sanskrtská aplikace – Streamlit
echo.
echo Spouštím sanskrtskou aplikaci...
echo (Pokud je potřeba, zavři předchozí okna)

REM Přepne se do složky, kde je umístěna aplikace
REM 
cd /d "%~dp0"

REM Pokud existuje lokální virtuální prostředí, aktivuj ho
IF EXIST "venv\Scripts\activate.bat" (
    echo Aktivuji lokální virtuální prostředí...
    call venv\Scripts\activate.bat
) ELSE (
    echo Virtuální prostředí nebylo nalezeno – používá se globální Python.
)

REM Spustí aplikaci
REM Spusť Streamlit aplikaci

echo Spouštím Streamlit...
REM 
echo streamlit run app.py --server.enableCORS true --server.enableXsrfProtection true
streamlit run app.py --server.enableCORS true --server.enableXsrfProtection true

REM echo streamlit run app.py
REM streamlit run app.py

echo ------------------------------------------
echo Aplikace byla ukončena.

pause
