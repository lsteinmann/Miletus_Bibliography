from typing import List, Dict, Any, Tuple
import pandas as pd

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
        self.log = []
        print("Initialized the DataChecker.")
    
    def find_duplicate_citation_keys(self):
        citation_keys = []
        for item in self.items:
            key = item.get('key', '')
            item_data = item.get('data', '')
            citation_key = item_data.get('citationKey', '')
            citation_keys.append({
                'Key': key,
                'citationKey': citation_key
            })
        citation_keys = pd.DataFrame(citation_keys)
        duplicates = citation_keys['citationKey'].duplicated(keep=False)
        print(duplicates)


# Example usage:
if __name__ == "__main__":
    import json
    # Initialize with tag client
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)
    
    data_checker = DataChecker(data)
