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
        self.keys = self._compile_keys()
        log = open(logfile, "w")
        log.writelines(f"Processing date and time: {datetime.datetime.now()}\n\n")
        log.close()
        print("Initialized the DataChecker.")
    
    def log(self, msg):
        print(msg)
        log = open(self.logfile, "a")
        log.write(f"{msg} \n\n")
        log.close()
        
    def _compile_keys(self) -> pd.DataFrame: 
        """
        Compiles a more compact df of the keys for quicker checking,
        discards 'note'-itemTypes as those are not processed later anyway.
        """
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
                    'citationKey': item_data.get('citationKey', pd.NA),
                    'dateAdded': item_data.get('dateAdded', pd.NA),
                    'title': item_data.get('title', pd.NA),
                    'createdBy': creator.get('username', pd.NA)
                })
        return pd.DataFrame(citation_keys)

    def find_missing_citation_keys(self):
        self.log("Checking for items with missing citationKeys...")
        missing = self.keys['citationKey'].isna()
        if missing.sum() > 0:
            self.log(f"Found {missing.sum()} items missing citationKeys:")
            self.log(self.keys[(self.keys['citationKey'].isna())])
            self.log("You need to check and fix these.")
        else: 
            self.log("There are no items with missing citationKeys - excellent.")

    def find_duplicate_citation_keys(self):
        self.log("Checking for duplicate citationKeys...")
        existing_keys = self.keys.dropna(subset=['citationKey'])
        duplicates = existing_keys['citationKey'].duplicated(keep=False)
        duplicate_rows = existing_keys[duplicates]
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
    data_checker.find_missing_citation_keys()
    data_checker.find_duplicate_citation_keys()
