import csv
import re
from typing import List, Optional, Dict, Any, Union

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
        print("Initializing the TagClient for the Miletus Bibliography.")
        self.tags = {}
        self._build_tags_dict(tags_csv_path)

    def _build_tags_dict(self, path):
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file, delimiter=";")
            for row in reader:
                if row["Gruppe"] == "":
                    continue
                if row["Untergruppe_1"] == "" and row["Untergruppe_2"] == "":
                    this_key = row["Gruppe"]
                    parent = None
                    section_type = "section"
                    #print("Adding section: " + row["Gruppe"] + " - " + row["DE"])
                elif row["Untergruppe_2"] == "":
                    this_key = row["Gruppe"] + "-" + row["Untergruppe_1"]
                    parent = row["Gruppe"]
                    section_type = "subsection"
                    #print("Adding subsection: " + this_key + " - " + row["DE"])
                else: 
                    this_key = row["Gruppe"] + "-" + row["Untergruppe_1"] + "-" + row["Untergruppe_2"]
                    parent = row["Gruppe"] + "-" + row["Untergruppe_1"]
                    section_type = "subsubsection"
                    #print("Adding subsubsection: " + this_key + " - " + row["DE"])
                # I have to remove "-" - this is absolutely hilarious. The result is a grammar nightmare. 
                # But that is how it is in the Database. I don't know why.
                tag = this_key + " " + row["DE"].replace("-", "")

               
                this = {
                    "tag": tag,
                    "section_type": section_type,
                    "key": this_key,
                    "DE": row["DE"],
                    "TR": row["TR"],
                    "EN": row["EN"],
                    "parent": parent,
                    "children": []
                }
                if this_key not in self.tags:
                    self.tags[this_key] = this
                

                #print("Key: " + this_key + "\t\t\t\t Tag: " + tag)
                #print(this)
    
    
    def _tag_to_key(self, tag: str) -> str:
        match = re.match(r'^([0-9-]+)', tag)
        if match:
            return match.group(1) 
        else:
            return None

    def get_parent(self, tag: str) -> Optional[str]:
        """
        Get the parent tag of a given tag.
        
        Args:
            tag_name (str): The tag name to find parent for
            
        Returns:
            Optional[str]: Parent tag name or None if not found
        """
        key = self._tag_to_key(tag)
        if key:
            this_tag = self.get_tag_info(key)
            parent = self.get_tag_info(this_tag["parent"])
            if parent:
                return parent["tag"]
            else: 
                return None
        else:
            return None

    def get_children(self, tag: str) -> List[str]:
        """
        Get all child tags of a given tag.
        
        Args:
            tag_name (str): The tag name to find children for
            
        Returns:
            List[str]: List of child tag names
        """
        key = self._tag_to_key(tag)
        children = []
        if key:
            for x in self.tags:
                if self.tags[x]["parent"] == key:
                    children.append(self.tags[x]["tag"])
            return children
        else:
            return None
    
    def get_all_tags(self) -> List[str]:
        """
        Get all available tag names.
        
        Returns:
            List[str]: List of all tag names
        """
        tag_names = []
        for key in self.tags:
            tag_names.append(self.tags[key]["tag"])
        return tag_names
    
    def get_tag_info(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        Get complete information about a specific tag.
        
        Args:
            tag_name (str): The tag name to get info for
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with tag information or None if not found
        """
        if tag:
            key = self._tag_to_key(tag)
            return self.tags[key]
        else:
            return None
    
    def get_hierarchy_level(self, tags: Union[str, List[str]]) -> Optional[Union[str, List[str]]]:
        """
        Get the hierarchy level(s) for one or more tag names.

        Args:
            tags (str or list): A single tag name or a list of tag names

        Returns:
            Optional[str or list]: Hierarchy level(s) or None if not found.
            - If input is a str → returns str or None
            - If input is a list → returns list of str or None values (in same order)
        """
        # Handle single string input
        if isinstance(tags, str):
            tags = [tags]  # Convert to list for uniform processing

        levels = []
        for x in tags: 
            key = self._tag_to_key(x)
            if key: 
                res = self.tags[key]
                levels.append(res["section_type"])

        # Return single value if input was a string, otherwise return list
        if isinstance(tags, str):
            return levels[0]  # Return single value
        else:
            return levels  # Return list of values

# Example usage // Test demo:
if __name__ == "__main__":
    print("\n -------------------------------------------------------------------")
    print("\n -------------------------------------------------------------------")
    # Initialize the tag client
    tag_client = TagClient()

    #quit()

    print("This is the Tests for the  TagClient for Miletus Bibliography.")
    print("This is printed so you can manually check if I am behaving correctly.")
    print("\n -------------------------------------------------------------------")
    print("All tags found in the current csv:\n")
    print(tag_client.get_all_tags())


    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_parent'-method using the tag '02-01 Topographie: Prähistorisch':\n")
    test_tag = "02 Allgemeine Darstellungen / Topographie"
    parent = tag_client.get_parent(test_tag)
    print(f"Parent of {test_tag}: \n {parent}")
    
    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_parent'-method using the tag '02-01 Topographie: Prähistorisch':\n")
    test_tag = "02-01 Topographie: Prähistorisch"
    parent = tag_client.get_parent(test_tag)
    print(f"Parent of {test_tag}: \n {parent}")
    
    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_parent'-method using the tag '03-05-09 Keramik: Mittelalter':\n")
    test_tag = "03-05-09 Keramik: Mittelalter"
    parent = tag_client.get_parent(test_tag)
    print(f"Parent of {test_tag}: \n {parent}")
    
    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_parent'-method using the a non-existing tag:\n")
    test_tag = "Mittelalter"
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

    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_hierarchy_level'-method using the Tag '03-05 Funde: Keramik' :\n")
    level = tag_client.get_hierarchy_level("03-05 Funde: Keramik")
    print(f"Level of this tag: {level}")

    print("\n -------------------------------------------------------------------")
    print("An example of the 'get_hierarchy_level'-method using the Tag '03-05 Funde: Keramik' :\n")
    level = tag_client.get_hierarchy_level(["03-05 Funde: Keramik", "03 Funde aus Milet", "03-05-09 Keramik: Mittelalter"])
    print(f"Level of this tag: {level}")