import sys
import requests
from bs4 import BeautifulSoup
import csv

# Validate user arguments
def validate_arguments(args):
    if len(args) != 3:
        print("Usage: python scraper.py <URL> <output_file>")
        sys.exit(1)

    url = args[1]
    if not url.startswith("https://www.volby.cz/pls/ps2017nss/ps32"):
        print("Error: Invalid URL. Please provide a valid URL to a voting region.")
        sys.exit(1)

    output_file = args[2]
    if not output_file.endswith(".csv"):
        print("Error: Output file must have a .csv extension.")
        sys.exit(1)

    return url, output_file

# Scrape election results
def scrape_election_results(url, output_file):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract main table with list of municipalities
        municipality_tables = soup.find_all("table", {"class": "table"})
        
        # Parse municipality links and names
        municipality_data = []
        for table in municipality_tables:
            tr_rows = table.find_all("tr")[2:]  # Skip headers
        for tr_row in tr_rows:
            td_rows = tr_row.find_all("td")
            print(td_rows)
            if len(td_rows) < 2:
                continue
            code = td_rows[0].text.strip()
            name = td_rows[1].text.strip()
            link_appendix = td_rows[0].get("href")
            full_detailed_link = "https://www.volby.cz/pls/ps2017nss" + link_appendix
            municipality_data.append((code, name, full_detailed_link))
            
        # Scrape details for each municipality
        all_data = []
        for code, name, full_detailed_link in municipality_data:
            municipality_results = scrape_municipality_data(full_detailed_link)
            municipality_results['code'] = code
            municipality_results['name'] = name
            all_data.append(municipality_results)

        # Save data to CSV
        save_to_csv(all_data, output_file)

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to retrieve data. {e}")
        sys.exit(1)

# Scrape data for a single municipality
def scrape_municipality_data(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract voter statistics
    stats_table = soup.find('table', {'id': 'ps311_t1'})
    stats_cells = stats_table.find_all('td')
    registered = stats_cells[3].text.strip().replace('\xa0', '')
    envelopes = stats_cells[6].text.strip().replace('\xa0', '')
    valid = stats_cells[7].text.strip().replace('\xa0', '')
   
    # Extract party results
    results_table = soup.find('table', {"class": "table"})
    party_results = {}
    party_rows = results_table.find_all('tr')[2:]  # Skip headers
    for party in party_rows:
        cells = party.find_all('td')
        if len(cells) < 3:
            continue
        party_name = cells[1].text.strip()
        votes = cells[2].text.strip().replace('\xa0', '')
        party_results[party_name] = votes
        
    return {
        "Registered": registered,
        "Envelopes": envelopes,
        "Valid": valid,
        "Party_results": party_results
    }

# Save data to a CSV file
def save_to_csv(data, output_file):
    # Collect unique party names
    all_parties = []
    for entry in data:
        all_parties.append(entry["party_results"].keys())

    all_parties = sorted(all_parties)

    # Write CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write header
        headers = ["Code", "Name", "Registered", "Envelopes", "Valid"] + all_parties
        writer.writerow(headers)

        # Write data rows
        for entry in data:
            row = [
                entry['code'],
                entry['name'],
                entry['registered'],
                entry['envelopes'],
                entry['valid']
            ]
            for party in all_parties:
                row.append(entry['party_results'].get(party, '0'))
            writer.writerow(row)

# Main entry point
if __name__ == "__main__":
    url, output_csv = validate_arguments(sys.argv)
    scrape_election_results(url, output_csv)
