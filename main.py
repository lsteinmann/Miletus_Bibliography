from src.tag_client import TagClient
from src.zotero_client import ZoteroClient
from src.bib_cleaner import BibCleaner

if __name__ == "__main__":
    zotero = ZoteroClient()
    # Get and save the bibliography: 
    #zotero.get_and_export_data(limit=0) # limit=0 is default, and means: all items
    # It is not ideal that the filenames are not set in here. I should
    # consider moving the saving logic to this main file. It is not the
    # Zotero-clients business to do that, actually. 
    bib_cleaner = BibCleaner()
    bib_cleaner.clean_biblatex("data/Milet_Bibliography_BibLaTeX_v2.bib")
    bib_cleaner.clean_bibtex("data/Milet_Bibliography_BibTeX_v2.bib")

    tags = TagClient()
    
    
    