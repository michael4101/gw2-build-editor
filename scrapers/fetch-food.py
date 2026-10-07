import requests
from bs4 import BeautifulSoup
import csv
import re
from collections import defaultdict

url = "https://wiki.guildwars2.com/wiki/Food"

food_items = []
food_data = []
stats = ["Power", "Precision", "Toughness", "Vitality", "Ferocity", "ConditionDamage", "Expertise", "Concentration", "HealingPower"]

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
        print(f"Failed to fetch {url}: {e}.")
        return None


def scrape_food():
    soup = get_soup(url)
    if not soup:
        print("Could not retrieve main page.")
        return
    
    tables = soup.find_all("table" , {"class": "recipe table"})
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            
            if len(cols) >= 4:
                name = cols[2].get_text(strip=True)
                bonus = cols[3].get_text(separator=" ", strip=True).replace("+", "")
                pairs = re.findall(r"[+]?(\d{1,3})\s+([A-Za-z ]+?)(?=\s*\d|\s*$)", bonus)
                
                if pairs:
                    print(pairs)
                    food_items.append((name,pairs))
                else:
                    continue
                
                
            
                
                
    for food_name, food_stats in food_items:
        stats_dict = dict.fromkeys(stats, "")
        for number, stat in food_stats:
            stat_key = stat.replace(" ","")
            if stat_key in stats_dict:
                stats_dict[stat_key] = number
        food_data.append({"Food": food_name, **stats_dict})
                    
    with open("food-source.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Food"] + stats)
        writer.writeheader()
        writer.writerows(food_data)
        
if __name__ == "__main__":
    scrape_food()