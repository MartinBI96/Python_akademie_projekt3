
"""
projekt.py: třetí projekt do Engeto Online Python Akademie

author: Martin Beles
email: martinbeles1996@gmail.com
discord: martin_71829 
"""

import requests
from bs4 import BeautifulSoup
import csv
import argparse

def get_soup(url):
    """Stáhne HTML obsah stránky a vrátí BeautifulSoup objekt."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Chyba při načítání stránky: {response.status_code}")
    return BeautifulSoup(response.text, 'html.parser')

def extract_links_and_info(soup):
    """Extrahuje odkazy, kódy a názvy obcí z úvodní stránky územního celku."""
    data = []
    tables = soup.find_all('table', {'class': 'table'})  # Najde všechny tabulky
    for table in tables:
        for row in table.find_all('tr')[2:]:  # První dva řádky jsou hlavičky
            cells = row.find_all('td')
            if len(cells) > 1:
                link = cells[0].find('a')  # Odkaz ve sloupci "číslo"
                kod_obce = cells[0].text.strip()  # Kód obce
                nazev_obce = cells[1].text.strip()  # Název obce
                if link:
                    data.append({
                        'url': link['href'],
                        'kód obce': kod_obce,
                        'název obce': nazev_obce
                    })
    return data

def extract_voting_data(soup):
    """Extrahuje výsledky hlasování pro danou obec."""
    data = {}
    tables = soup.find_all('table', {'class': 'table'})  # Najde všechny tabulky

    # Počet hlasů
    data['voliči v seznamu'] = soup.find('td', {'headers': 'sa2'}).text.strip()
    data['vydané obálky'] = soup.find('td', {'headers': 'sa3'}).text.strip()
    data['platné hlasy'] = soup.find('td', {'headers': 'sa6'}).text.strip()

    # Výsledky stran (dle pořadí v tabulce na webu)
    parties = []
    for table in tables[1:]:  # První tabulka je základní informace, další jsou strany
        for row in table.find_all('tr')[2:]:  # První dva řádky jsou hlavičky
            cells = row.find_all('td')
            if len(cells) > 1:
                strana = cells[1].text.strip()
                hlasy = cells[2].text.strip()
                data[strana] = hlasy
                if strana not in parties:
                    parties.append(strana)
    
    return data, parties

def main():
    """Hlavní funkce skriptu."""
    parser = argparse.ArgumentParser(description="Web scraping výsledků voleb.")
    parser.add_argument('url', help="URL územního celku")
    parser.add_argument('output', help="Název výstupního souboru CSV")
    args = parser.parse_args()

    # Zpracování úvodní stránky
    soup = get_soup(args.url)
    obce_info = extract_links_and_info(soup)

    # Extrakce dat pro každou obec
    results = []
    all_parties = []
    for obec in obce_info:
        full_url = f"https://www.volby.cz/pls/ps2017nss/{obec['url']}"
        soup = get_soup(full_url)
        data, parties = extract_voting_data(soup)
        data['kód obce'] = obec['kód obce']
        data['název obce'] = obec['název obce']
        results.append(data)
        for party in parties:
            if party not in all_parties:
                all_parties.append(party)

    # Zápis výsledků do CSV souboru
    with open(args.output, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['kód obce', 'název obce', 'voliči v seznamu', 'vydané obálky', 'platné hlasy'] + all_parties
        writer.writerow(header)

        for result in results:
            row = [
                result.get('kód obce', ''),
                result.get('název obce', ''),
                result.get('voliči v seznamu', ''),
                result.get('vydané obálky', ''),
                result.get('platné hlasy', ''),
            ]
            for strana in all_parties:
                row.append(result.get(strana, 0))
            writer.writerow(row)

if __name__ == "__main__":
    main()
