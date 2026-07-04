from typing import List, Dict, Any, Tuple
import pandas as pd
import datetime

class DataChecker:
    """
    Checks the Bibliography-data for problematic entries.
    """
    
    def __init__(self, items: List[Dict[str, Any]] = None, logfile: str = "out/check_result.log"):
        """
        Initialize the DataChecker.
        
        Args:
            tags (TagClient): Tag client instance for tag processing
        """
        self.items = items
        self.logfile = logfile
        log = open(logfile, "w")
        log.writelines(f"Processing date and time: {datetime.datetime.now()}\n\n")
        log.close()
        print("Initialized the DataChecker.")
    
    def log(self, msg):
        print(msg)
        log = open(self.logfile, "a")
        log.write(f"{msg} \n\n")
        log.close()


    def find_duplicate_citation_keys(self):
        self.log("Checking for duplicate citationKeys...")
        citation_keys = []
        for item in self.items:
            key = item.get('key', '')
            item_data = item.get('data', '')
            if item_data.get('itemType') == 'note': 
                pass
            else: 
                meta = item.get('meta')
                creator = meta.get('createdByUser')
                citation_keys.append({
                    'Key': key,
                    'citationKey': item_data.get('citationKey', ''),
                    'dateAdded': item_data.get('dateAdded', ''),
                    'title': item_data.get('title', ''),
                    'createdBy': creator.get('username')
                })
        citation_keys = pd.DataFrame(citation_keys)
        duplicates = citation_keys['citationKey'].duplicated(keep=False)
        duplicate_rows = citation_keys[duplicates]
        if len(duplicate_rows.index) > 0:
            self.log(f"Found {len(duplicate_rows.index)} duplicate citationKeys:")
            self.log(duplicate_rows)
            self.log("You need to check and fix these.")
        else: 
            self.log("There are no duplicate citationKeys - excellent.")


# Example usage:
if __name__ == "__main__":
    import json
    # Initialize with tag client
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)
    
    data_checker = DataChecker(data)
    data_checker.find_duplicate_citation_keys()
