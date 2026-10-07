import csv
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

base_url = "https://wiki.guildwars2.com"
main_url = "https://wiki.guildwars2.com/wiki/Specialization"
csv_headers = ["Name", "Class", "Specialisation", "Tier", "Description"]

session = requests.Session()
session.headers.update({
    "User-Agent": "GW2WikiScraper/1.0 (Project Scraping Script)"
})

def get_soup(url: str) -> BeautifulSoup | None:
    """Fetch HTML content from URL and return a BeautifulSoup object."""
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def scrape_traits():
    soup = get_soup(main_url)
    if not soup:
        print("Could not retrieve main page.")
        return

    specs_list = soup.find_all("table", {"class": "skills table"})

    with open("traits-source.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(csv_headers)

        for table in specs_list:
            rows = table.find_all("tr")
            
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 3:
                    continue

                row_classes = row.get("class", [])
                if not row_classes:
                    continue
                profession = row_classes[0]

                spec = cols[0]
                spec_name = spec.get_text(strip=True, separator=" ")
                spec_link = spec.select_one("span a")

                if not spec_link or "href" not in spec_link.attrs:
                    continue

                spec_url = urljoin(base_url, spec_link["href"])
                spec_soup = get_soup(spec_url)
                if not spec_soup:
                    continue

                spec_tables = spec_soup.find_all(
                    "table", 
                    {"class": f"{profession} skills table"}, 
                    id=False
                )

                for spec_table in spec_tables:
                    for spec_row in spec_table.find_all("tr"):
                        spec_cols = spec_row.find_all("td")

                        if len(spec_cols) >= 4:
                            tier = spec_cols[0].get_text(strip=True, separator=" ")
                            name = spec_cols[1].get_text(strip=True, separator=" ")
                            description = spec_cols[3].get_text(" ", strip=True)
                            description = re.sub(r"\s+([,.])", r"\1", description)

                            row_data = [
                                name, 
                                profession.capitalize(), 
                                spec_name, 
                                tier, 
                                description
                            ]
                            print(row_data)
                            writer.writerow(row_data)

if __name__ == "__main__":
    scrape_traits()