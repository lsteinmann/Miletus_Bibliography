# The Miletus Bibliography	<a href='https://www.miletgrabung.uni-hamburg.de/material/bibliographie.html'><img src='data/figures/milet-logo-tr.png' align="right" height="150" /></a>

<!-- badges: start -->
[![latest release](https://img.shields.io/github/v/release/Miletus-Excavation/Miletus_Bibliography?label=latest%20release)](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest)
![Status](https://github.com/Miletus-Excavation/Miletus_Bibliography/actions/workflows/bibliography-pipeline.yml/badge.svg)
<!-- badges: end -->

# README
This repository contains the code to format the Miletus Bibliography from Zotero-Exports to the formats used on the [Miletus Excavation Website](https://www.miletgrabung.uni-hamburg.de/en/material/bibliographie.html) along with the LaTeX-files used to publish the Bibliography as pdf-files. 

# Updates

All bibliography files and their PDF exports are updated automatically on the first day of each month from the state of the [Zotero group library](https://www.zotero.org/groups/4475959/milet_bibliography) at that time.

# The Miletus Bibliography

The Miletus Bibliography aims to provide a complete overview of the publications of the Miletus excavation as well as those that deal significantly with the ancient polis of Miletus and its history and archaeology.

![Publications in the Miletus Bibliography by Year](out/figures/mil-pubs-by-year-type.png "Publications in the Miletus Bibliography by Year")

The bibliography is edited and managed in a [publicly accessible Zotero group library](https://www.zotero.org/groups/4475959/milet_bibliography). By joining the group, anyone has access to a synchronized version of the bibliography via their Zotero client. For those that prefer other literature management software, the website of the Miletus Excavation offers exports of the bibliography in various formats as downloads, namely: [BibLaTeX](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/Milet_Bibliography_BibLaTeX.bib), [BibTeX](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/Milet_Bibliography_BibTeX.bib), [CSV](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/Milet_Bibliography_CSV.csv), [RIS](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/Milet_Bibliography_RIS.ris). These should cover the option to import into any literature management software.

A searchable online-version of the bibliography is available on the [homepage of the Miletus Excavation](https://www.miletgrabung.uni-hamburg.de/material/bibliographie.html) as well. It is selectable by keyword, author, year of publication and series or journal. Please note: this list may take few seconds to load. For those who prefer the bibliography in PDF-format, three different versions are provided alongside all the above: 

* [Milet-Bibliographie, by keyword (PDF)](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/milet-bibliographie-by-tag-pdf.pdf)
    This is an export of the Bibliography ordered according to the [System of Keywords](https://www.miletgrabung.uni-hamburg.de/en/material/bibliographie/bib-tags.html).
* [Milet-Bibliographie, chronological (PDF)](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/milet-bibliographie-by-year-pdf.pdf)
    Chronologically ordered, with a section on each year in which publications exist. 
* [Milet-Bibliographie, by author (PDF)](https://github.com/Miletus-Excavation/Miletus_Bibliography/releases/latest/download/milet-bibliographie-by-author-pdf.pdf)
   This version contains a section on each primary or contributing author sorted alphabetically by last name. The section of each author contains all the works this person has contributed to. 

The references in these files are in accordance with the citation guidelines of the [German Archaeological Institute](https://www.dainst.org/publikationen/publizieren-beim-dai/richtlinien). The BibTeX-citation style used for the exports was developed by [Lukas Bossert](http://lukascbossert.github.io/biblatex-archaeologie/). A citation style for Zotero that follows the same rules can be found in the [Zotero Style Repository](https://www.zotero.org/styles) or directly downloaded from there [via this link](https://www.zotero.org/styles/deutsches-archaologisches-institut). 


# History and Contributors
The bibliography has been offered as a [PDF version for download](https://doi.org/10.25592/uhhfdm.8678) for many years by [Sabine Huy](https://orcid.org/0000-0001-7401-3662) in the course of her work at the Miletus Archive at the *Ruhr-Universität Bochum* and later the *Universität Hamburg*. With the collaboration of Caitlin Bamford and Silas Munnecke, the list was converted into a [database version](https://www.zotero.org/groups/4475959/milet_bibliography) as of 2022 and has since been maintained by [Lisa Steinmann](https://orcid.org/0000-0002-2215-1243).


## Context
The scripts and LaTeX-files were produced during my work for the [Miletus Excavation](https://www.miletgrabung.uni-hamburg.de/) in the course of the DFG/ANR-funded project ["Life Forms in the Megapolis: Miletus in the Longue Durée"](https://www.kulturwissenschaften.uni-hamburg.de/ka/forschung/lebensformen-megapolis.html). 


# Development and Usage

Start by setting up the virtual environment with python:

```python 
python3 - m venv venv
source venv/bin/activate
```

Install the required libraries: 

```
pip install -r requirements.txt
```

You can run the whole python pipeline from `main.py`: 

```
python3 -m main
```

Or check each submodule: 

```
python3 -m src.zotero_client
python3 -m src.bibliography_client
python3 -m src.tag_client
python3 -m src.data_checker
python3 -m src.latex_generator
```


# Tools
Some of the code has been ported from R to python using Qwen 3 Coder along my mental model of the project. I made this transparent in the commit messages. Generally, all commits / changes are human-made if not stated otherwise. 