# Scraper volebních výsledků

Tento projekt je Pythonový skript, který stahuje volební výsledky z webových stránek ČSÚ pro konkrétní územní celek. Výsledky jsou ukládány do výstupního souboru ve formátu `.csv`.

## Funkcionalita

- Skript přijímá dva argumenty z příkazové řádky:
  1. **URL odkaz** na volební okrsek (např. Prostějov).
  2. **Název výstupního souboru**, kam budou výsledky uloženy (např. `vysledky_prostejov.csv`).
- Stahuje HTML obsah z webu ČSÚ.
- Parsuje data z tabulek volebních výsledků.
- Ukládá data do CSV souboru s přehlednou strukturou.

## Použité knihovny

- `requests` – Pro stažení HTML obsahu z URL.
- `beautifulsoup4` – Pro analýzu a extrakci dat z HTML.
- `argparse` – Pro zpracování argumentů z příkazové řádky.
- `csv` – Pro generování CSV souboru.

## Instalace

1. Klonujte tento repozitář do svého počítače:
    git clone https://github.com/MartinBI96/Python_akademie_projekt3
2. Vytvořte si a aktivuje si virtuální prostředí (doporučeno, ale ne požadováno):
    python -m venv venv
    source venv/bin/activate       # pro Linux/MacOS
    venv\Scripts\activate          # pro Windows
3. Naistalujte požadované knihovny (uvedené v requirements.txt):
    pip install -r requirements.txt

## Použití 

Spusťte skripkt pomocí následujícího příkazu: 
  python web_scrapping_script.py "https://www.volby.cz/pls/ps2017nss/ps33?xjazyk=CZ&xkraj=2&xobec=529486" "vysledky_output.csv"