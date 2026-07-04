import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import homogenize_latex_encoding, convert_to_unicode

# I cannot remember why these processes were different and I do not know how
# I should find out. 

class BibCleaner:
    """
    Loads and cleans BibTeX and BibLaTeX files to e.g. fix characters and formats.
    """
    def __init__(self):
        print("Hi.")

    def clean_bibtex(self, filename):
        with open(filename, encoding="utf8") as file:
            parser = BibTexParser()
            parser.encoding = "utf-8"
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = False
            parser.common_strings = False
            parser.customization = homogenize_latex_encoding
            bib_database = bibtexparser.load(file, parser=parser)
        # print(bib_database.entries)
        writer = BibTexWriter()
        writer.order_entries_by=None
        writer.display_order
        with open(filename, 'w', encoding='utf-8') as bibfile:
            bibfile.write(writer.write(bib_database))

    def clean_biblatex(self, filename):
        with open(filename, encoding="utf8") as file:
            parser = BibTexParser()
            parser.encoding = "utf-8"
            parser.ignore_nonstandard_types = False
            parser.homogenize_fields = True
            parser.common_strings = False
            bib_database = bibtexparser.load(file, parser=parser)
        
        # print(bib_database.entries)
        writer = BibTexWriter()
        writer.order_entries_by = None #('author', 'year')
        with open(filename, 'w', encoding='utf-8') as bibfile:
            bibfile.write(writer.write(bib_database))





