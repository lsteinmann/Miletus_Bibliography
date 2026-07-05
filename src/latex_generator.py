from typing import List, Dict, Any
from src.bibliography_client import BibliographyClient
from src.language_services import sort_turkish
from src.utils import extract_four_digits

class LatexGenerator:
    """
    Generates LaTeX files for bibliography exports (by year, author, and tags).
    """
    
    def __init__(
        self, 
        tags: 'TagClient' = None, 
        json_data: List[Dict[str, Any]] = None
    ):
        """
        Initialize the LaTeX generator.
        
        Args:
            tags (TagClient): Tag client instance for tag processing
            json_data (List of Dicts): The Bibliography as Exported from the Zotero API in JSON format. 
        """
        self.tags = tags
        self.bib = BibliographyClient(json_data)

        
    def generate_by_year(self, output_path: str = "out/bibsections_by_year.tex") -> str:
        """
        Generate LaTeX sections by publication year.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        # TODO cant set the other pass as a param
        sections_file = open("out/bibsections_by_year.tex", "w")
        bibcheck_file = open("out/defbibcheck_by_year.tex", "w")
        years = []
        # TODO : actually this sucks, because the bib file will not 
        # have all years in there correctly, so they will not be in the
        # pdf.
        # And I need to fix this somehow, probably I should generate the 
        # bib here myself, similar to the authors.  TODO
        years = self.bib.list_all_years()
        for year in years: 
            year = extract_four_digits(year)
        years = sorted(set(years), reverse=True)
        # Iterate over each year and find matching entries in data
        for year in years:
            # Find all entries where date matches the current year
            # matching_entries = [entry for entry in data if entry.get("date") == year]
            sections_file.writelines(f"\\section*{{{year}}}\n")
            sections_file.writelines(f"\\addcontentsline{{toc}}{{section}}{{{year}}}%\n")
            sections_file.writelines(f"\\printbibliography[check=yr{year},heading=none, env=compactbib]\n")
            bibcheck_file.writelines(f"\\defbibcheck{{yr{year}}}{{%\n")
            bibcheck_file.writelines("  \\iffieldint{year}\n")
            bibcheck_file.writelines("  {\\ifnumequal{\\thefield{year}}{" + year + "}\n")
            bibcheck_file.writelines("    {}\n")
            bibcheck_file.writelines("    {\\skipentry}}\n")
            bibcheck_file.writelines("  {\\skipentry}}\n\n\n")
        sections_file.close()
    

    def generate_by_author(self, output_path: str = "out/bibstructure_by_author.tex") -> str:
        """
        Generate LaTeX structure by author.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        file = open(output_path, "w")
        grouped_authors = self.bib.list_all_authors_by_letter()
        for letter in grouped_authors:
            subset = grouped_authors[letter]
            if len(subset) == 0:
                continue
            file.writelines(f"\\section{{{letter}}}\n\n")
            for author in subset:
                info = self.bib.get_author(author)
                name = info["lastName-latin"] + ", " + info["firstName-latin"]
                items = info["items"]
                subsection = f"\\subsection[{name} ({len(items)})]{{{name}}}\n" 
                file.writelines(subsection)
                sorted_items = []
                for item in items:
                    year = self.bib.get_publication_year(item)
                    sorted_items.append({
                        "citationKey": self.bib.get_citationKey(item), 
                        "year": extract_four_digits(year)
                    })
                sorted_items = sorted(sorted_items, key=lambda x: x["year"])

                for item in sorted_items: 
                    citationKey = item["citationKey"]
                    file.writelines(f"\\fullcite{{{citationKey}}}\n\n")
        file.close()

    
    def generate_by_tag(self, output_path: str = "out/bibstructure_by_keyword.tex") -> str:
        """
        Generate LaTeX structure by tags.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        print("Yes.")
    
    def generate_all(self):
        """Generate all LaTeX files."""
        print("Generating LaTeX files...")
        
        # Generate by year
        self.generate_by_year()
        
        # Generate by author
        self.generate_by_author()
        
        # Generate by tag
        self.generate_by_tag()
        
        print("All LaTeX files generated successfully!")

# Example usage:
if __name__ == "__main__":
    # Initialize with tag client
    import json
    from src.tag_client import TagClient
    # Initialize with tag client
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)

    tags = TagClient()
    latex_gen = LatexGenerator(tags=tags, json_data=data)
    
    latex_gen.generate_by_year("out/bibsections_by_year.tex")
    latex_gen.generate_by_author("out/bibstructure_by_author.tex")
    latex_gen.generate_by_tag("out/bibstructure_by_keyword.tex")

    # Generate all files
    #latex_gen.generate_all()
    
    print("LaTeX generation complete!")