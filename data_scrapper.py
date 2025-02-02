
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
    """Extracts HTML content of the website and returns BeautifulSoup object."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Chyba při načítání stránky: {response.status_code}")
    return BeautifulSoup(response.text, 'html.parser')

def extract_links_and_info(soup):
    """Extracts links, codes and names of the municipalities from the website of a region."""
    data = []
    tables = soup.find_all('table', {'class': 'table'})  # Finds all tables
    for table in tables:
        for row in table.find_all('tr')[2:]:  # First two rows are headers
            cells = row.find_all('td')
            if len(cells) > 1:
                link = cells[0].find('a')  
                kod_obce = cells[0].text.strip()  # Municipality code
                nazev_obce = cells[1].text.strip()  # Municipality name
                if link:
                    data.append({
                        'url': link['href'],
                        'kód obce': kod_obce,
                        'název obce': nazev_obce
                    })
    return data

def get_voting_data(soup):
    """Extracts election results in a given municipality."""
    data = {}
    tables = soup.find_all('table', {'class': 'table'})  # Finds all tables

    # Votes
    data['voliči v seznamu'] = soup.find('td', {'headers': 'sa2'}).text.strip()
    data['vydané obálky'] = soup.find('td', {'headers': 'sa3'}).text.strip()
    data['platné hlasy'] = soup.find('td', {'headers': 'sa6'}).text.strip()

    # Party results (according to the order in the table)
    parties = []
    for table in tables[1:]:  # Firs table is just general information
        for row in table.find_all('tr')[2:]:  # First two rows are headers
            cells = row.find_all('td')
            if len(cells) > 1:
                strana = cells[1].text.strip()
                hlasy = cells[2].text.strip()
                data[strana] = hlasy
                if strana not in parties:
                    parties.append(strana)
    
    return data, parties

def get_municipalities(url):
    """Extracts a list of municipalities and all links to their detailed results."""
    soup = get_soup(url)
    return extract_links_and_info(soup)

def process_data(municipality_info):
    """Process municipalitity parameters and election results together."""
    results = []
    all_parties = set()

    for obec in municipality_info:
        full_url = f"https://www.volby.cz/pls/ps2017nss/{obec['url']}"
        soup = get_soup(full_url)
        data, parties = get_voting_data(soup)
        data['kód obce'] = obec['kód obce']
        data['název obce'] = obec['název obce']
        results.append(data)
        all_parties.update(parties)

    return results, sorted(all_parties)  # Set guarantees unique party names

def save_to_csv(results, all_parties, output_file):
    """Saves the data to CSV file."""
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        header = ['Code', 'Location', 'Registered', 'Envelopes', 'Valid'] + all_parties
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

def main():
    """Main function of the script only calls all fuctions together."""
    parser = argparse.ArgumentParser(description="Web scraping výsledků voleb.")
    parser.add_argument('url', help="URL územního celku")
    parser.add_argument('output', help="Název výstupního souboru CSV")
    args = parser.parse_args()

    # Get municipalities info
    municipality_info = get_municipalities(args.url)

    # Get election data for each municipality
    results, all_parties = process_data(municipality_info)

    # Save to a CSV file
    save_to_csv(results, all_parties, args.output)

if __name__ == "__main__":
    main()
