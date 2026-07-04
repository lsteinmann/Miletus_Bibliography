import pandas as pd
import os
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

class LatexGenerator:
    """
    Generates LaTeX files for bibliography exports (by year, author, and tags).
    """
    
    def __init__(self, bib_csv_path: str = "data/Milet_Bibliography_CSV.csv", 
                 tags_client: 'TagClient' = None):
        """
        Initialize the LaTeX generator.
        
        Args:
            bib_csv_path (str): Path to the bibliography CSV file
            tags_client (TagClient): Tag client instance for tag processing
        """
        self.bib_csv_path = bib_csv_path
        self.tags_client = tags_client
        self.bib_df = None
        self._load_bibliography()
    
    def _load_bibliography(self):
        """Load and clean the bibliography data."""
        # Read CSV
        self.bib_df = pd.read_csv(self.bib_csv_path, encoding="UTF-8", na_strings="")
        
        # Remove completely NA columns
        na_cols = self.bib_df.isnull().all(axis=0)
        self.bib_df = self.bib_df.loc[:, ~na_cols]
        
        # Convert types
        self.bib_df = self.bib_df.convert_dtypes()
        
        # Handle citation keys
        if 'citationKey' not in self.bib_df.columns:
            # If citationKey column doesn't exist, create it from Key column
            self.bib_df['citationKey'] = self.bib_df['Key']
        
        # Remove entries without citation keys
        missing_keys = self.bib_df['citationKey'].isna() | (self.bib_df['citationKey'] == '')
        if missing_keys.any():
            print(f"Warning: {missing_keys.sum()} entries missing citation keys")
            # Keep only entries with valid citation keys
            self.bib_df = self.bib_df[~missing_keys]
    
    def _get_sort_locale(self) -> str:
        """Get the sorting locale for Turkish characters."""
        return "tr_TR"
    
    def generate_by_year(self, output_path: str = "out/bibsections_by_year.tex") -> str:
        """
        Generate LaTeX sections by publication year.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        # Get years table
        years = self.bib_df['Publication.Year'].dropna().astype(int).unique()
        years = sorted(years, reverse=True)
        
        # Generate defbibcheck definitions
        defbibcheck_lines = []
        for year in years:
            defbibcheck_lines.append(f"\\defbibcheck{{yr{year}}}{{%\n"
                                   f"  \\iffieldint{{year}}%\n"
                                   f"  {{\\ifnumequal{{\\thefield{{year}}}}{{{year}}}%%\n"
                                   f"    {{}}%\n"
                                   f"    {{\\skipentry}}}%\n"
                                   f"  }}{{\\skipentry}}}}\n\n")
        
        # Save defbibcheck
        defbibcheck_content = "".join(defbibcheck_lines)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(defbibcheck_content)
        print(f"Saved: {output_path}")
        
        # Generate bibsections
        bibsections_lines = []
        for year in years:
            # Section header
            section_line = f"\\section*{{{year}}}\n"
            toc_line = f"\\addcontentsline{{toc}}{{section}}{{{year}}}%\n"
            bib_line = f"\\printbibliography[check=yr{year},heading=none,env=compactbib]\n"
            
            bibsections_lines.extend([section_line, toc_line, bib_line])
        
        # Save bibsections
        bibsections_content = "".join(bibsections_lines)
        bibsections_path = output_path.replace("_by_year.tex", "_by_year.tex")
        with open(bibsections_path, 'w', encoding='utf-8') as f:
            f.write(bibsections_content)
        print(f"Saved: {bibsections_path}")
        
        return bibsections_content
    
    def generate_by_author(self, output_path: str = "out/bibstructure_by_author.tex") -> str:
        """
        Generate LaTeX structure by author.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        # Get all authors and split them
        authors = self.bib_df['Author'].dropna().tolist()
        author_lists = [author.split('; ') if pd.notna(author) else [] for author in authors]
        
        # Flatten and get unique authors
        all_authors = []
        for author_list in author_lists:
            all_authors.extend(author_list)
        
        # Remove duplicates and sort
        unique_authors = sorted(set(all_authors), key=lambda x: x.lower())
        
        # Group by first letter (using Turkish locale for sorting)
        author_groups = {}
        for author in unique_authors:
            first_letter = author[0].upper() if author else ''
            if first_letter not in author_groups:
                author_groups[first_letter] = []
            author_groups[first_letter].append(author)
        
        # Sort letters
        sorted_letters = sorted(author_groups.keys())
        
        # Generate content
        bibstructure_lines = []
        
        for letter in sorted_letters:
            # Section for letter
            bibstructure_lines.append(f"\\section{{{letter}}}\n")
            
            # For each author in this letter group
            for author in author_groups[letter]:
                # Find all entries for this author
                author_mask = self.bib_df['Author'].str.contains(f'^{re.escape(author)}$', 
                                                                regex=True, na=False)
                author_entries = self.bib_df[author_mask]
                
                if not author_entries.empty:
                    # Sort by year then title
                    author_entries = author_entries.sort_values(['Publication.Year', 'Title'], 
                                                               key=lambda x: x.apply(lambda y: str(y).lower()))
                    
                    # Get citation keys
                    citation_keys = author_entries['citationKey'].tolist()
                    num_pubs = len(citation_keys)
                    
                    # Build citation lines
                    citation_lines = [f"\\fullcite{{{key}}}" for key in citation_keys]
                    citation_content = "\n\n".join(citation_lines)
                    
                    # Section header with publication count
                    section_header = (f"\\subsection[{author} ({num_pubs})]{{{author}}}\n")
                    bibstructure_lines.append(section_header)
                    bibstructure_lines.append(citation_content)
                    bibstructure_lines.append("\n")
        
        # Save content
        content = "".join(bibstructure_lines)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {output_path}")
        
        return content
    
    def generate_by_tag(self, output_path: str = "out/bibstructure_by_keyword.tex") -> str:
        """
        Generate LaTeX structure by tags.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        if not self.tags_client:
            raise ValueError("TagClient is required for tag-based generation")
        
        # Get all tags from the tag system
        all_tags = self.tags_client.get_all_tags()
        
        # Get manual tags from bibliography
        manual_tags = self.bib_df['Manual.Tags'].dropna().tolist()
        # Split tags by semicolon
        tag_lists = [tag.split('; ') for tag in manual_tags]
        
        # Create mapping from key to tags
        key_to_tags = dict(zip(self.bib_df['Key'], self.bib_df['Manual.Tags'].dropna()))
        
        # Generate content
        bibstructure_lines = []
        
        for tag_name in all_tags:
            # Get tag info
            tag_info = self.tags_client.get_tag_info(tag_name)
            if not tag_info:
                continue
                
            # Find all entries with this tag
            matching_keys = []
            for key, tags_str in key_to_tags.items():
                if tag_name in tags_str:
                    matching_keys.append(key)
            
            if not matching_keys:
                continue
            
            # Get subset of bibliography
            subset = self.bib_df[self.bib_df['Key'].isin(matching_keys)]
            
            # Determine section type
            section_type = tag_info.get('hierarchy', 'section')
            
            # Get display name (remove prefix)
            display_name = tag_info.get('DE', tag_name)
            clean_display_name = display_name.split(": ", 1)[-1] if ": " in display_name else display_name
            
            # Create section header
            if section_type == 'section':
                section_header = f"\\section{{{clean_display_name}}}\n"
            elif section_type == 'subsection':
                section_header = f"\\subsection{{{clean_display_name}}}\n"
            elif section_type == 'subsubsection':
                section_header = f"\\subsubsection{{{clean_display_name}}}\n"
            else:
                section_header = f"\\section{{{clean_display_name}}}\n"
            
            bibstructure_lines.append(section_header)
            
            # Get citation keys for this tag
            citation_keys = subset['citationKey'].dropna().tolist()
            
            if citation_keys:
                # Sort by appropriate criteria based on tag
                if tag_name == "01 Grabungs und Arbeitsberichte":
                    # Sort by year, then author
                    subset_sorted = subset.sort_values(['Publication.Year', 'Author'], 
                                                     key=lambda x: x.apply(lambda y: str(y).lower()))
                else:
                    # Sort by author, then year
                    subset_sorted = subset.sort_values(['Author', 'Publication.Year'], 
                                                     key=lambda x: x.apply(lambda y: str(y).lower()))
                
                citation_keys = subset_sorted['citationKey'].dropna().tolist()
                
                # Build citation lines
                citation_lines = [f"\\fullcite{{{key}}}" for key in citation_keys]
                citation_content = "\n\n".join(citation_lines)
                bibstructure_lines.append(citation_content)
            
            bibstructure_lines.append("\n\n")
        
        # Save content
        content = "".join(bibstructure_lines)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {output_path}")
        
        return content
    
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
    from src.tag_client import TagClient
    tags = TagClient()
    
    # Initialize LaTeX generator
    latex_gen = LatexGenerator(tags_client=tags)
    
    # Generate all files
    latex_gen.generate_all()
    
    print("LaTeX generation complete!")