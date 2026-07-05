import os
from typing import List, Dict, Any

from src.tag_client import TagClient
from src.zotero_client import ZoteroClient
from src.bib_handler import BibHandler
from src.latex_generator import LatexGenerator
from src.data_checker import DataChecker
from src.bibliography_client import BibliographyClient

if __name__ == "__main__":
    zotero = ZoteroClient()
    limit = 0 # 0 for "no limit" = all items

    # We get and save the bibliography here. 
    # RIS is the format that needs least processing:
    print("Hi! I am building the Miletus Bibliography now.\n")
    print("-----------------------------------------------------------------------")
    print("------------------------- Let's go. -----------------------------------")
    print("-----------------------------------------------------------------------\n")
    print("Getting RIS from Zotero:")
    ris = zotero.get_ris(limit = limit)
    filename = "data/Milet_Bibliography_RIS.ris"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(ris)
    print(f"Written data to {filename}.\n")
    print("-----------------------------------------------------------------\n")

    print("Getting JSON from Zotero:")
    json = zotero.get_json(limit = limit)    
    filename = "data/Milet_Bibliography_JSON.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json)
    print(f"Written data to {filename}.\n")
    print("-----------------------------------------------------------------\n")

    print("Getting CSV from Zotero:")
    csv = zotero.get_csv(limit = limit)
    filename = "data/Milet_Bibliography_CSV.csv"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(csv)
    print(f"Written data to {filename}.\n")
    print("-----------------------------------------------------------------\n")
    
    
    # BibTeX and BibLaTeX need some cleaning up, as there are many 
    # strictly not really compatible characters from german and 
    # turkish alphabet in the database, and the Zotero API seems to 
    # put in 0 effort in cleaning the data to be actually compatibly 
    # with LaTeX.
    bib_handler = BibHandler()

    print("Getting BibLaTeX from Zotero:")
    biblatex = zotero.get_biblatex(limit = limit)
    filename = "data/Milet_Bibliography_BibLaTeX.bib"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(biblatex)
    print(f"Written data to {filename}")
    bib_handler.clean_biblatex_file(filename)
    print(f"Cleaned {filename} for compatibility.\n")
    print("-----------------------------------------------------------------\n")
    
    print("Getting BibTeX from Zotero:")
    bibtex = zotero.get_bibtex(limit = limit)
    filename = "data/Milet_Bibliography_BibTeX.bib"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(bibtex)
    print(f"Written data to {filename}")
    bib_handler.clean_bibtex_file(filename)
    print(f"Cleaned {filename} for compatibility.\n")
    print("-----------------------------------------------------------------\n")

    print("So far so good. Now I will check the Bibliography for problems.\n")
    print("-----------------------------------------------------------------------")
    print("------------------------- Let's go. -----------------------------------")
    print("-----------------------------------------------------------------------\n")
    tag_client = TagClient()
    data_checker = DataChecker(
        items=zotero.json_data, 
        tags=tag_client,
        logfile="out/check_result.log"
    )

    data_checker.find_missing_citation_keys()
    data_checker.find_duplicate_citation_keys()
    data_checker.find_items_without_tags()



    print("Finally, I will build the LaTeX-files!\n")
    print("-----------------------------------------------------------------------")
    print("------------------------- Let's go. -----------------------------------")
    print("-----------------------------------------------------------------------\n")
    
    texgen = LatexGenerator(tags = tag_client, json_data=zotero.json_data)

    texgen.generate_by_author("out/bibstructure_by_author.tex")
    texgen.generate_by_year("out/bibsections_by_year.tex")
    texgen.generate_by_tag("out/bibstructure_by_keyword.tex")

    