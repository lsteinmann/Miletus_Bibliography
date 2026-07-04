from typing import List, Dict, Any
import re
import pandas as pd

class LatexGenerator:
    """
    Generates LaTeX files for bibliography exports (by year, author, and tags).
    """
    
    def __init__(self, tags: 'TagClient' = None, items: List[Dict[str, Any]] = None):
        """
        Initialize the LaTeX generator.
        
        Args:
            tags (TagClient): Tag client instance for tag processing
        """
        self.tags = tags
        self.items = items
        self.data = self._reduce_data()
    
    def _reduce_data(self):
        data = []
        for item in self.items: 
            item_data = item.get('data', {})
            if item_data.get('itemType') != 'note':
                data.append(item_data)
            item.pop('data', None)
        return data

        
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
        pattern = re.compile(r'\b(\d{4})\b')
        for x in self.data:
            val = x.get('date', '')
            match = pattern.search(val)
            if match: 
                val = match.group(1)
                x['date'] = val
                years.append(val)

        years = sorted(set(years), key = int, reverse=True)
        # Iterate over each year and find matching entries in data
        for year in years:
            # Find all entries where date matches the current year
            matching_entries = [entry for entry in self.data if entry.get("date") == year]
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
    
    def get_list_of_authors(self):
        authors = []
        for x in self.data:
            creators = x.get('creators', '')
            for y in creators:
                authors.append(y)
        authors = pd.DataFrame(authors)
        unique_names = (
            authors.drop(columns=['creatorType', 'name'])
            .groupby(['firstName', 'lastName'], as_index=False)
            .size()
            .drop_duplicates(subset=['firstName', 'lastName'])
            .reset_index()
        )
        def transliterate_non_turkish(text):
            if pd.isna(text):
                return text
            # Keep Turkish chars, transliterate others
            turkish_chars = set('ığüöçşİĞÜÖÇŞ')
            return ''.join(char if char in turkish_chars else unidecode(char) for char in text)

        unique_names['firstName_lat'] = unique_names['firstName'].apply(transliterate_non_turkish)
        unique_names['lastName_lat'] = unique_names['lastName'].apply(transliterate_non_turkish)
        unique_names = unique_names.sort_values(by=['lastName_lat', 'firstName_lat'])
        unique_names['letter'] = unique_names['lastName_lat'].str[0].str.upper()

        return(unique_names)

    def generate_by_author(self, output_path: str = "out/bibstructure_by_author.tex") -> str:
        """
        Generate LaTeX structure by author.
        
        Args:
            output_path (str): Path to save the output file
            
        Returns:
            str: Generated LaTeX content
        """
        authors = self.get_list_of_authors()
        print(authors)

        file = open("out/bibstructure_by_author_v2.tex", "w")

        letters = set(authors['letter'])
        letters = sorted(letters)
        for letter in letters:
            file.writelines(f"\\section{{{letter}}}\n\n")
            subset = authors[authors['letter'] == letter]
            for _, row in subset.iterrows():
                file.writelines(f"\\subsection[{row['lastName_lat']}, {row['firstName_lat']} ({row['size']})]{{{row['lastName_lat']}, {row['firstName_lat']}}}\n")

            #print(authors.loc[authors['letter'] == letter])
        file.close()

    
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