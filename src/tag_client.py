import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any

class TagClient:
    """
    A client for managing hierarchical tag systems from Zotero.
    Handles tag parsing, hierarchy determination, and LaTeX formatting.
    """
    
    def __init__(self, tags_csv_path: str = "data/tags/tags_sys.csv"):
        """
        Initialize the TagClient with tag data from CSV.
        
        Args:
            tags_csv_path (str): Path to the tags CSV file
        """
        self.tags_csv_path = tags_csv_path
        self.tags_df = None
        self._load_and_clean_tags()
    
    def _load_and_clean_tags(self):
        """
        Load and clean the tags CSV data, removing empty rows and processing tags.
        """
        # Read the CSV file
        self.tags_df = pd.read_csv(
            self.tags_csv_path, 
            sep=";", 
            encoding="UTF-8", 
            dtype=str
        )
        
        # The csv-file is supposed to be very human-readable, thus some rows
        # are completely empty, providing some good visual divisions for people
        # editing it / filling in more tags. 
        # We need to remove them here to be able to process the file, though:
        mask_all_na = self.tags_df.isnull().all(axis=1)
        self.tags_df = self.tags_df[~mask_all_na]
        
        # The tags are recorded in the zotero group database in a specific way, 
        # by combining the numbers with the (german!) titles of groups and 
        # their sub-groups, which we need to arrange again here, since I 
        # did not want duplication in the table itself. That may not have been a
        # wise choice, in hindsight. 
        self.tags_df['tag'] = (
            self.tags_df['Gruppe'].fillna('') + "-" + 
            self.tags_df['Untergruppe_1'].fillna('') + "-" + 
            self.tags_df['Untergruppe_2'].fillna('') + " " + 
            self.tags_df['DE'].fillna('')
        )
        
        # Remove unwanted patterns from the tag string
        self.tags_df['tag'] = self.tags_df['tag'].str.replace('--', '', regex=False)
        self.tags_df['tag'] = self.tags_df['tag'].str.replace('- ', ' ', regex=False)
        
        # Create the 'hierarchy' column for quick access to hierarchy level
        # Section: Gruppe only (both Untergruppe_1 and Untergruppe_2 are NA)
        condition1 = self.tags_df['Untergruppe_1'].isna() & self.tags_df['Untergruppe_2'].isna()
        self.tags_df['hierarchy'] = np.where(condition1, 'section', None)
        
        # Subsection: Gruppe and Untergruppe_1 present, Untergruppe_2 is NA
        condition2 = ~self.tags_df['Untergruppe_1'].isna() & self.tags_df['Untergruppe_2'].isna()
        self.tags_df['hierarchy'] = np.where(condition2, 'subsection', self.tags_df['hierarchy'])
        
        # Subsubsection: All three levels present
        condition3 = ~self.tags_df['Untergruppe_1'].isna() & ~self.tags_df['Untergruppe_2'].isna()
        self.tags_df['hierarchy'] = np.where(condition3, 'subsubsection', self.tags_df['hierarchy'])
    
    def get_latex_section(self, tag_name: str) -> Optional[str]:
        """
        Get the LaTeX section command for a given tag.
        
        Args:
            tag_name (str): The tag name to get LaTeX section for
            
        Returns:
            Optional[str]: LaTeX section command or None if not found
        """
        # Find matching tag
        tag_row = self.tags_df[self.tags_df['tag'] == tag_name]
        
        if tag_row.empty:
            return None
            
        tag_info = tag_row.iloc[0]
        section_type = tag_info['hierarchy']
        # Here we have the future option to make multi-lingual
        # pdf-files out of this. 
        display_name = tag_info['DE'] 
        ## TODO
        
        # Remove the prefix (like "01 ", "02 ", etc.) for display name
        clean_display_name = display_name.split(": ", 1)[-1] if ": " in display_name else display_name
        
        if section_type == 'section':
            return f"\\section{{{clean_display_name}}}"
        elif section_type == 'subsection':
            return f"\\subsection{{{clean_display_name}}}"
        elif section_type == 'subsubsection':
            return f"\\subsubsection{{{clean_display_name}}}"
        else:
            return None
    
    def get_parent(self, tag_name: str) -> Optional[str]:
        """
        Get the parent tag of a given tag.
        
        Args:
            tag_name (str): The tag name to find parent for
            
        Returns:
            Optional[str]: Parent tag name or None if not found
        """
        tag_row = self.tags_df[self.tags_df['tag'] == tag_name]
        
        if tag_row.empty:
            # I think this never happens.
            return None

        # This does not do what it should yet. But I have not figured out what it should do. 
        # This, we simply return the highest level hierarchy:
        tag_info = tag_row.iloc[0]
        parent = self.tags_df.loc[(self.tags_df['Gruppe'] == tag_info['Gruppe']) & (self.tags_df['hierarchy'] == 'section')]
        # TODO fix as needed later

        return parent['tag'].to_string()
    
    def get_children(self, tag_name: str) -> List[str]:
        """
        Get all child tags of a given tag.
        
        Args:
            tag_name (str): The tag name to find children for
            
        Returns:
            List[str]: List of child tag names
        """
        # Find the tag row
        tag_row = self.tags_df[self.tags_df['tag'] == tag_name]
        
        if tag_row.empty:
            return []
            
        tag_info = tag_row.iloc[0]
        if tag_info['hierarchy'] == 'section': 
            children = self.tags_df.loc[(self.tags_df['Gruppe'] == tag_info['Gruppe'])]
            children = children.loc[(children['hierarchy'] != 'section')]
        if tag_info['hierarchy'] == 'subsection': 
            children = self.tags_df.loc[(self.tags_df['Gruppe'] == tag_info['Gruppe']) & (self.tags_df['Untergruppe_1'] == tag_info['Untergruppe_1'])]
            children = children.loc[(children['hierarchy'] != 'section')]
            children = children.loc[(children['hierarchy'] != 'subsection')]
        if tag_info['hierarchy'] == 'subsubsection': 
            children = None
        
        return children['tag'].tolist()
    
    def get_all_tags(self) -> List[str]:
        """
        Get all available tag names.
        
        Returns:
            List[str]: List of all tag names
        """
        return self.tags_df['tag'].tolist()
    
    def get_tag_info(self, tag_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a specific tag.
        
        Args:
            tag_name (str): The tag name to get info for
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with tag information or None if not found
        """
        tag_row = self.tags_df[self.tags_df['tag'] == tag_name]
        
        if tag_row.empty:
            return None
            
        return tag_row.iloc[0].to_dict()
    
    def get_hierarchy_level(self, tag_name: str) -> Optional[str]:
        """
        Get the hierarchy level (section, subsection, subsubsection) of a tag.
        
        Args:
            tag_name (str): The tag name to check
            
        Returns:
            Optional[str]: Hierarchy level or None if not found
        """
        tag_row = self.tags_df[self.tags_df['tag'] == tag_name]
        
        if tag_row.empty:
            return None
            
        return tag_row.iloc[0]['hierarchy']

# Example usage // Test demo:
if __name__ == "__main__":
    # Initialize the tag client
    tag_client = TagClient()
    
    print("This is the TagClient for Miletus Bibliography.")
    print("This is printed so you can manually check if I am behaving correctly.")
    print("\n -------------------------------------------------------------------")
    print("All tags found in the current csv:\n")
    print(tag_client.get_all_tags())

    print("\n -------------------------------------------------------------------")
    
    print("An example section head for the LaTeX template using the tag '02-01 Topographie: Prähistorisch':\n")
    test_tag = "02-01 Topographie: Prähistorisch"
    latex_section = tag_client.get_latex_section(test_tag)
    print(f"LaTeX section for {test_tag}: \n {latex_section}")
    
    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_parent'-method using the tag '02-01 Topographie: Prähistorisch':\n")
    parent = tag_client.get_parent(test_tag)
    print(f"Parent of {test_tag}: \n {parent}")
    
    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_parent'-method using the tag '03-05-09 Keramik: Mittelalter':\n")
    parent = tag_client.get_parent(test_tag)
    print(f"Parent of {test_tag}: \n {parent}")
    
    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_children'-method using the Tag '02 Allgemeine Darstellungen / Topographie' :\n")
    children = tag_client.get_children("02 Allgemeine Darstellungen / Topographie")
    print(f"Children of top-level tag: {children}")

    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_children'-method using the Tag '03 Funde aus Milet' :\n")
    children = tag_client.get_children("03 Funde aus Milet")
    print(f"Children of top-level tag: {children}")

    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_children'-method using the Tag '03-05 Funde: Keramik' :\n")
    children = tag_client.get_children("03-05 Funde: Keramik")
    print(f"Children of top-level tag: {children}")