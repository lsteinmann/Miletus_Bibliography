from typing import List, Dict, Any, Tuple
import pandas as pd
import datetime

class DataChecker:
    """
    Checks the Bibliography-data for problematic entries.
    """
    
    def __init__(
        self, 
        items: List[Dict[str, Any]] = None, 
        tags: 'TagClient' = None,
        logfile: str = "out/check_result.log"
    ):
        """
        Initialize the DataChecker.
        
        Args:
            tags (TagClient): Tag client instance for tag processing
        """
        self.items = items
        self.logfile = logfile
        self.tags = tags
        self.clean_items = self._process_items()
        log = open(logfile, "w")
        log.writelines(f"Processing date and time: {datetime.datetime.now()}\n\n")
        log.close()
        print("Initialized the DataChecker.")
    
    def log(self, msg):
        with pd.option_context(
            'display.max_rows', None,
            'display.max_columns', None,
            'display.width', None,
            'display.max_colwidth', None
        ):
            print(msg)
            log = open(self.logfile, "a")
            log.write(f"{msg} \n\n")
            log.close()
        
    def _process_items(self) -> pd.DataFrame: 
        """
        Compiles a more compact df of the keys and tags for quicker checking,
        discards 'note'-itemTypes as those are not processed later anyway.
        """
        items = []
        for item in self.items:
            key = item.get('key', '')
            item_data = item.get('data', '')
            if item_data.get('itemType') == 'note': 
                pass
            else: 
                item_tags = []
                for tag in item_data.get('tags', []):
                    item_tags.append({
                        'tag': tag.get('tag', ''),
                        'level': self.tags.get_hierarchy_level(tag.get('tag', ''))
                    })
                meta = item.get('meta')
                creator = meta.get('createdByUser')
                items.append({
                    'Key': key,
                    'citationKey': item_data.get('citationKey', pd.NA),
                    'dateAdded': item_data.get('dateAdded', pd.NA),
                    'title': item_data.get('title', pd.NA),
                    'createdBy': creator.get('username', pd.NA),
                    'tags': item_tags
                })
        return pd.DataFrame(items)

    def find_missing_citation_keys(self):
        self.log("Checking for items with missing citationKeys...")
        missing = self.clean_items['citationKey'].isna()
        if missing.sum() > 0:
            self.log(f"Found {missing.sum()} items missing citationKeys:")
            self.log(self.clean_items[(self.clean_items['citationKey'].isna())])
            self.log("You need to check and fix these.")
        else: 
            self.log("There are no items with missing citationKeys - excellent.")

    def find_duplicate_citation_keys(self):
        self.log("Checking for duplicate citationKeys...")
        existing_keys = self.clean_items.dropna(subset=['citationKey'])
        duplicates = existing_keys['citationKey'].duplicated(keep=False)
        duplicate_rows = existing_keys[duplicates]
        if len(duplicate_rows.index) > 0:
            self.log(f"Found {len(duplicate_rows.index)} duplicate citationKeys:")
            self.log(duplicate_rows)
            self.log("You need to check and fix these.")
        else: 
            self.log("There are no duplicate citationKeys - excellent.")
    
    def find_items_without_tags(self): 
        missing_tags = []
        for _, item in self.clean_items.iterrows():
            tags = item['tags']
            all_none = all(tag.get('level') is None for tag in tags)
            if all_none and len(tags) > 0:
                missing_tags.append(item['Key'])
        if len(missing_tags) > 0:
            self.log(f"Found {len(missing_tags)} items without systematic tags:")
            result = self.clean_items.loc[(self.clean_items['Key'].isin(missing_tags))]
            self.log(result)

# Example usage:
if __name__ == "__main__":
    import json
    from tag_client import TagClient
    # Initialize with tag client
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)

    tags = TagClient()
    
    data_checker = DataChecker(data, tags, "out/check_result.log")
    data_checker.find_missing_citation_keys()
    data_checker.find_duplicate_citation_keys()
    data_checker.find_items_without_tags()
