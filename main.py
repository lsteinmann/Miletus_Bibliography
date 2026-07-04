from src.tag_client import TagClient
from src.zotero_client import ZoteroClient

if __name__ == "__main__":
    zotero = ZoteroClient()
    # Get and save the bibliography: 
    zotero.get_and_export_data(limit=0) # limit=0 is default, and means: all items

    tags = TagClient()
    
    
    