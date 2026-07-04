import os
from typing import List, Dict, Any

from src.tag_client import TagClient
from src.zotero_client import ZoteroClient
from src.bib_handler import BibHandler

def extract_citation_keys(data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Process Zotero JSON data to extract key and citationKey pairs.
    
    Args:
        json_data (List[Dict[str, Any]]): List of Zotero JSON items
        
    Returns:
        List[Dict[str, str]]: List of dictionaries with 'Key' and 'citationKey' fields
    """
    citation_keys = []
    
    for item in data:
        # Extract the required fields
        key = item.get('key', '')
        item_data = item.get('data', '')
        citation_key = item_data.get('citationKey', '')
        
        # Create the dictionary for this item
        citation_keys.append({
            'Key': key,
            'citationKey': citation_key
        })
    
    return citation_keys



if __name__ == "__main__":
    zotero = ZoteroClient()
    limit = 100 # 0 for "no limit" = all items

    # We get and save the bibliography here. 
    # RIS is the format that needs least processing:
    ris = zotero.get_ris(limit = limit)
    filename = "data/Milet_Bibliography_RIS.ris"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(ris)
    print(f"Written data to {filename}.")

    json = zotero.get_json(limit = limit)    
    filename = "data/Milet_Bibliography_JSON.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json)
    print(f"Written data to {filename}.")
    
    csv = zotero.get_csv(limit = limit)
    filename = "data/Milet_Bibliography_CSV.csv"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(csv)
    print(f"Written data to {filename}.")
    
    
    # BibTeX and BibLaTeX need some cleaning up, as there are many 
    # strictly not really compatible characters from german and 
    # turkish alphabet in the database, and the Zotero API seems to 
    # put in 0 effort in cleaning the data to be actually compatibly 
    # with LaTeX.
    bib_handler = BibHandler()
    biblatex = zotero.get_biblatex(limit = limit)
    filename = "data/Milet_Bibliography_BibLaTeX.bib"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(biblatex)
    print(f"Written data to {filename}")
    bib_handler.clean_biblatex_file(filename)
    print(f"Cleaned {filename} for compatibility.")
    
    bibtex = zotero.get_bibtex(limit = limit)
    filename = "data/Milet_Bibliography_BibTeX.bib"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(bibtex)
    print(f"Written data to {filename}")
    bib_handler.clean_bibtex_file(filename)
    print(f"Cleaned {filename} for compatibility.")

    tags = TagClient()
    citation_keys = extract_citation_keys(zotero.json_data)
    