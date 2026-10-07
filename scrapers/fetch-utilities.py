import requests
from bs4 import BeautifulSoup
import re
import csv



url = "https://wiki.guildwars2.com/wiki/Utility_item"

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

utility_items = []
utility_effects = ["Name","Level","Derived_Bonus_1","Derived_Bonus_2","Karma_Bonus","Magic_Find_Bonus","Gold_Bonus","Healthy_Bonus","Shared_Bonus_1","Shared_Bonus_2","Movement_Speed_Bonus","Experience_Bonus"]

full_names_dict = {
    "Healing" : "Healing Power",
    "Condition" : "Condition Damage"
    }

def scrape_utilities():
    soup=get_soup(url)
    if not soup:
        print("Could not retrieve page.")
        return
    
    tables = soup.find_all("table", {"data-filter-id": "utility-table"})
    for table in tables:
        rows = table.find_all("tr")
        
        for row in rows:
            
            item_dict = {}
            cols = row.find_all("td")
            
            if len(cols) >= 4:
                level = cols[0].get_text(strip=True)
                name = cols[2].get_text(strip=True)
                bonus = cols[3].text

                item_dict["Name"] = name
                item_dict["Level"] = level
                

                derived_pattern = re.compile(
                    r"Gain\s+([\w ]+)\s+Equal\s+to\s+(\d+%?)\s+of\s+Your\s+([A-Za-z ]+?)(?=(?:Gain\b|\b))",
                    flags=re.IGNORECASE
                    )
                shared_pattern = re.compile(
                    r"Gain\s+(\d[.]\d%?)\s+Increased\s+([\w ]+)\s+to\s+Other\s+Allies\s+for\s+Every\s+(\d+%?)\s+([A-Za-z ]+?)(?=(?:Gain\b|\b))",
                    flags=re.IGNORECASE
                    )
                derived = derived_pattern.findall(bonus)            
                karma_bonus = re.findall(r"([+]\d+%?) Karma", bonus)
                magic_find_bonus = re.findall(r"([+]\d+%?) Magic Find", bonus)
                gold_bonus = re.findall(r"([+]\d+%?) Gold from Monsters", bonus)
                healthy_bonus = re.findall(r"Gain (\d+) ([\w ]+) When Health above 90%", bonus)
                shared_bonus = shared_pattern.findall(bonus)
                movement_speed_bonus = re.findall(r"Gain (\d+%?) Increased Movement speed", bonus)
                experience = re.findall(r"([+]\d+%?) Experience from Kills", bonus, flags=re.IGNORECASE)
                

                if derived:
                     
                    for i in range(len(derived)):
                        num = i + 1
                        item_dict["Derived_Bonus" + f"_{num}"] = {
                        "Gain_Stat" : (),
                        "Percent" : (),
                        "From_Stat" : ()
                        }
                       
                        from_stat = derived[i][2]
                        if from_stat in full_names_dict:
                            from_stat = full_names_dict[from_stat]
                            
                        item_dict["Derived_Bonus" + f"_{num}"]["Gain_Stat"] = derived[i][0].strip()
                        item_dict["Derived_Bonus" + f"_{num}"]["Percent"] = derived[i][1].strip()
                        item_dict["Derived_Bonus" + f"_{num}"]["From_Stat"] = derived[i][2].strip()
                        
                if karma_bonus:
                    for percent in karma_bonus:
                        item_dict["Karma_Bonus"] = percent.strip("+")   
                if magic_find_bonus:
                    for percent in magic_find_bonus:
                        item_dict["Magic_Find_Bonus"] = percent.strip("+")          
                if gold_bonus:
                    for percent in gold_bonus:
                        item_dict["Gold_Bonus"] = percent.strip("+")    
                if healthy_bonus:
                    for gain_amount, gain_stat in healthy_bonus:
                        item_dict["Healthy_Bonus"] = {
                            "Gain": gain_amount,
                            "Gain_Stat": gain_stat
                            }
                        
                if shared_bonus:
                    
                    for i in range(len(shared_bonus)):
                        num = i + 1
                        item_dict["Shared_Bonus" + f"_{num}"] = {
                        "Percent" : (),
                        "Gain_Stat" : (),
                        "For_Amount" : (),
                        "For_Stat": ()
                        }                    
                        gain_stat = shared_bonus[i][1]
                        for_stat = shared_bonus[i][3]
                        if gain_stat in full_names_dict:
                            gain_stat = full_names_dict[gain_stat]
                        if for_stat in full_names_dict:
                            for_stat = full_names_dict[for_stat]
                        
                        item_dict["Shared_Bonus" + f"_{num}"]["Percent"] = shared_bonus[i][0].strip()
                        item_dict["Shared_Bonus" + f"_{num}"]["Gain_Stat"] = shared_bonus[i][1].strip()
                        item_dict["Shared_Bonus" + f"_{num}"]["For_Amount"] = shared_bonus[i][2].strip()
                        item_dict["Shared_Bonus" + f"_{num}"]["For_Stat"] = shared_bonus[i][3].strip()
                                           
                if movement_speed_bonus:
                    for percent in movement_speed_bonus:
                        item_dict["Movement_Speed_Bonus"] = percent.strip("+")                    
                if experience:
                    for percent in experience:
                        item_dict["Experience_Bonus"] = percent.strip("+")
                
                utility_items.append({**item_dict})
           
    sections = {
        "Derived_Bonus_1": ["Gain_Stat", "Percent", "From_Stat"],
        "Derived_Bonus_2": ["Gain_Stat", "Percent", "From_Stat"],
        "Karma_Bonus": ["Percent"],
        "Magic_Find_Bonus": ["Percent"],
        "Gold_Bonus": ["Percent"],
        "Healthy_Bonus": ["Gain", "Gain_Stat"],
        "Shared_Bonus_1": ["Percent", "Gain_Stat", "For_Amount", "For_Stat"],
        "Shared_Bonus_2": ["Percent", "Gain_Stat", "For_Amount", "For_Stat"],
        "Movement_Speed_Bonus": ["Percent"],
        "Experience_Bonus": ["Percent"]
    }
    
    top_header = ["Name"]
    sub_header = [""]

    for section, subfields in sections.items():
        top_header.append(section.replace("_", " "))
        top_header.extend([""] * (len(subfields) - 1))    
        sub_header.extend(subfields)

        

    for i in utility_items:
        print(i) 

    with open("utilities-source.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(top_header)
        writer.writerow(sub_header)
        for item in utility_items:
            row = [item["Name"]]
            for section, subfields in sections.items():
                bonus = item.get(section, {})
                if not isinstance(bonus, dict):
                    row.append(bonus)
                else:
                    for key in subfields:
                        values = bonus.get(key, [""])
                        if isinstance(values, str):
                            values = [values]
                        row.append(", ".join(values))
                
            writer.writerow(row)
if __name__ == "__main__":
    scrape_utilities()




        
      
        
        
    
