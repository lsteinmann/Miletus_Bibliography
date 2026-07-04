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
        
        # Remove rows where ALL values are missing/empty
        mask_all_na = self.tags_df.isnull().all(axis=1)
        self.tags_df = self.tags_df[~mask_all_na]
        
        # Create the 'tag' column by combining hierarchical tags
        self.tags_df['tag'] = (
            self.tags_df['Gruppe'].fillna('') + "-" + 
            self.tags_df['Untergruppe_1'].fillna('') + "-" + 
            self.tags_df['Untergruppe_2'].fillna('') + " " + 
            self.tags_df['DE'].fillna('')
        )
        
        # Clean up the tag string by removing unwanted patterns
        self.tags_df['tag'] = self.tags_df['tag'].str.replace('-NA', '', regex=False)
        self.tags_df['tag'] = self.tags_df['tag'].str.replace('--', '', regex=False)
        self.tags_df['tag'] = self.tags_df['tag'].str.replace('- ', ' ', regex=False)
        
        # Create the 'sys' column to determine hierarchy level
        # Section: Gruppe only (both Untergruppe_1 and Untergruppe_2 are NA)
        condition1 = self.tags_df['Untergruppe_1'].isna() & self.tags_df['Untergruppe_2'].isna()
        self.tags_df['sys'] = np.where(condition1, 'section', None)
        
        # Subsection: Gruppe and Untergruppe_1 present, Untergruppe_2 is NA
        condition2 = ~self.tags_df['Untergruppe_1'].isna() & self.tags_df['Untergruppe_2'].isna()
        self.tags_df['sys'] = np.where(condition2, 'subsection', self.tags_df['sys'])
        
        # Subsubsection: All three levels present
        condition3 = ~self.tags_df['Untergruppe_1'].isna() & ~self.tags_df['Untergruppe_2'].isna()
        self.tags_df['sys'] = np.where(condition3, 'subsubsection', self.tags_df['sys'])
    
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
        section_type = tag_info['sys']
        display_name = tag_info['DE']  # Using German as default
        
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
            return None
            
        tag_info = tag_row.iloc[0]
        gruppe = tag_info['Gruppe']
        untergruppe_1 = tag_info['Untergruppe_1']
        
        # If only Gruppe exists, no parent
        if pd.isna(untergruppe_1):
            return None
            
        # If Untergruppe_1 exists but not Untergruppe_2, parent is Gruppe + Untergruppe_1
        if pd.isna(tag_info['Untergruppe_2']):
            return f"{gruppe}-{untergruppe_1}"
            
        # If all three exist, parent is Gruppe + Untergruppe_1
        return f"{gruppe}-{untergruppe_1}"
    
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
        gruppe = tag_info['Gruppe']
        untergruppe_1 = tag_info['Untergruppe_1']
        untergruppe_2 = tag_info['Untergruppe_2']
        
        # Filter for children based on hierarchy
        if pd.isna(untergruppe_1) and pd.isna(untergruppe_2):
            # This is a top-level section, find all children
            children_mask = (
                (self.tags_df['Gruppe'] == gruppe) &
                (~self.tags_df['Untergruppe_1'].isna()) &
                (self.tags_df['Untergruppe_2'].isna())
            )
            return self.tags_df[children_mask]['tag'].tolist()
        elif pd.notna(untergruppe_1) and pd.isna(untergruppe_2):
            # This is a subsection, find all children
            children_mask = (
                (self.tags_df['Gruppe'] == gruppe) &
                (self.tags_df['Untergruppe_1'] == untergruppe_1) &
                (~self.tags_df['Untergruppe_2'].isna())
            )
            return self.tags_df[children_mask]['tag'].tolist()
        else:
            # This is a subsubsection or has no children
            return []
    
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
            
        return tag_row.iloc[0]['sys']

# Example usage:
if __name__ == "__main__":
    # Initialize the tag client
    tag_client = TagClient()
    
    # Test some methods
    print("All tags:", tag_client.get_all_tags()[:5])  # Show first 5
    
    # Test getting LaTeX section
    test_tag = "02-01 Topographie: Prähistorisch"
    latex_section = tag_client.get_latex_section(test_tag)
    print(f"LaTeX section for {test_tag}: {latex_section}")
    
    # Test getting parent
    parent = tag_client.get_parent(test_tag)
    print(f"Parent of {test_tag}: {parent}")
    
    # Test getting children
    children = tag_client.get_children("02 Allgemeine Darstellungen / Topographie")
    print(f"Children of top-level tag: {children[:3]}...")  # Show first 3