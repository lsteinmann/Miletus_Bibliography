from typing import List, Any, Dict, Tuple, Optional
from src.utils import extract_four_digits
from src.bibliography_client import BibliographyClient
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np

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

    def plot_count_by_year(
        self,
        output_path: str = "out/figures/mil-pubs-by-year.png"
    ):
        years_dict = self.bib.years_to_keys
        year_counts = Counter()
        for year_str, items in years_dict.items():
            if not year_str or year_str == '' or year_str == 'NA':
                continue
            year = int(year_str)
            year_counts[year] += len(items)

        x_start = (min(year_counts.keys()) // 25) * 25
        x_end = ((max(year_counts.keys()) + 24) // 25) * 25

        bins = np.arange(x_start-25, x_end+25, 5)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        bin_counts, _ = np.histogram(list(year_counts.keys()), bins=bins, weights=list(year_counts.values()))
        plt.figure(figsize=(12, 5), dpi=100)  # 1200x500 px at 100 DPI
        plt.bar(
            bin_centers, bin_counts, width=5,
            color="#3b515b", alpha=0.8, edgecolor='none'
        )

        x_ticks = np.arange(x_start, x_end+25, 25)
        plt.xlim(x_start, x_end)
        plt.xticks(x_ticks, fontsize=15)
        y_max = max(bin_counts) * 1.1
        plt.ylim(0, y_max)

        plt.xlabel("Year of Publication", fontsize=15)
        plt.ylabel("Number of Publications", fontsize=15)
        plt.title("Entries in the Miletus Bibliography Database", fontsize=24)

        plt.grid(
            True, which='major', axis='y', color='#999999',
            linestyle='-', linewidth=0.8
        )
        plt.grid(
            True, which='major', axis='x', color='#999999',
            linestyle='-.', linewidth=0.8
        )

        plt.tight_layout()
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        print(f"Saved: {output_path}")


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
        figs.plot_count_by_year("out/figures/mil-pubs-by-year.png")
