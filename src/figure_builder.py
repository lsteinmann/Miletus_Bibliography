from typing import List, Any, Dict, Tuple, Optional
from src.utils import extract_four_digits
from src.bibliography_client import BibliographyClient

class FigureBuilder:
    def __init__(
        self,
        json: List[Dict[str, Any]] = None,
        tags: "TagClient" = None
    ):
        print("The FigureBuilder has been initialized.")
        self.tags = tags
        self.bib = BibliographyClient(json=json, tags=tags)

    def __process_json(self, json: List[Dict[str, Any]] = None):
        print("Hi")

    def plot_count_by_year(self):
        years_dict = self.bib.years_to_keys


if __name__ == "__main__":
    import json
    from src.tag_client import TagClient

    with open("out/data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)
    tag_client = TagClient("data/tags/tags_sys.csv")

    figs = FigureBuilder(json=data, tags=tag_client)
    demo = True
    if demo:
        print("Hello World")
        figs.plot_count_by_year()
