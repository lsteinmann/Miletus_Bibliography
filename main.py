import os
from src.tag_client import TagClient
from src.zotero_client import ZoteroClient
from src.bib_handler import BibHandler
from src.latex_generator import LatexGenerator
from src.data_checker import DataChecker

if __name__ == "__main__":
    zotero = ZoteroClient()
    limit = 0  # 0 for "no limit" = all items

    # We get and save the bibliography here.
    # RIS is the format that needs least processing:
    print("Hi! I am building the Miletus Bibliography now.\n")
    print("------------------------------------------------------------------")
    print("------------------------- Let's go. ------------------------------")
    print("----------------------------------------------------------------\n")
    if not os.path.exists("out/data"):
        print("Creating the 'out/data'-directory...")
        os.makedirs("out/data")

    print("Getting RIS from Zotero:")
    ris = zotero.get_ris(limit=limit)
    filename = "out/data/Milet_Bibliography_RIS.ris"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(ris)
    print(f"Written data to {filename}.\n")
    print("----------------------------------------------------------------\n")

    print("Getting JSON from Zotero:")
    json = zotero.get_json(limit=limit)
    filename = "out/data/Milet_Bibliography_JSON.json"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json)
    print(f"Written data to {filename}.\n")
    print("----------------------------------------------------------------\n")

    print("Getting CSV from Zotero:")
    csv = zotero.get_csv(limit=limit)
    filename = "out/data/Milet_Bibliography_CSV.csv"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(csv)
    print(f"Written data to {filename}.\n")
    print("----------------------------------------------------------------\n")

    # BibTeX and BibLaTeX need some cleaning up, as there are many
    # strictly not really compatible characters from german and
    # turkish alphabet in the database, and the Zotero API seems to
    # put in 0 effort in cleaning the data to be actually compatibly
    # with LaTeX.
    bib_handler = BibHandler()

    print("Getting BibLaTeX from Zotero:")
    biblatex = zotero.get_biblatex(limit=limit)
    filename = "out/data/Milet_Bibliography_BibLaTeX.bib"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(biblatex)
    print(f"Written data to {filename}")
    bib_handler.clean_biblatex_file(filename)
    print(f"Cleaned {filename} for compatibility.\n")
    print("----------------------------------------------------------------\n")

    print("Getting BibTeX from Zotero:")
    bibtex = zotero.get_bibtex(limit=limit)
    filename = "out/data/Milet_Bibliography_BibTeX.bib"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(bibtex)
    print(f"Written data to {filename}")
    bib_handler.clean_bibtex_file(filename)
    print(f"Cleaned {filename} for compatibility.\n")
    print("----------------------------------------------------------------\n")

    print("So far so good. Now I will check the Bibliography for problems.\n")
    print("------------------------------------------------------------------")
    print("------------------------- Let's go. ------------------------------")
    print("----------------------------------------------------------------\n")
    if not os.path.exists("out/logs"):
        print("Creating the 'out/logs'-directory...")
        os.makedirs("out/logs")

    tag_client = TagClient()
    data_checker = DataChecker(
        items=zotero.json_data,
        tags=tag_client,
        logfile="out/logs/check_result.log"
    )

    data_checker.check_all()

    print("Finally, I will build the LaTeX-files!\n")
    print("------------------------------------------------------------------")
    print("------------------------- Let's go. ------------------------------")
    print("----------------------------------------------------------------\n")
    if not os.path.exists("out/tex"):
        print("Creating the 'out/tex'-directory...")
        os.makedirs("out/tex")

    texgen = LatexGenerator(tags=tag_client, json_data=zotero.json_data)

    texgen.generate_by_author(
        output_path="out/tex/bibstructure_by_author.tex"
    )
    texgen.generate_by_tag(
        output_path="out/tex/bibstructure_by_keyword.tex"
    )
    texgen.generate_by_year(
        output_path_sections="out/tex/bibsections_by_year.tex",
        output_path_check="out/tex/defbibcheck_by_year.tex"
    )
