from typing import List, Any, Dict, Tuple
from language_services import transliterate, get_sorting_alphabet, sort_turkish

# TODO
# - This could include a query by year, and I could manually build the 
#   year-wise bibliography same as the author-wise one; this would be better, 
#   because it would include the fucked-up year-entries as well such as 
#   1964/65 etc., as I am able to clean them up here much better than in the 
#   database itself (as that is prone to human error and zotero does not care.)

class BibliographyClient: 
    def __init__(self, json: List[Dict[str, Any]] = None):
        print("The Author Client has been initialized. ;)")
        self.keys_to_data = {}
        self.keys_to_meta = {}
        self.author_info = {}
        self.keys_to_authors = {}
        self.tags_to_keys = {}
        self.years_to_keys = {}
        self.__process_json(json)
        self.authors_by_letter = self.__prepare_letter_groups()

    def __process_json(self, json: List[Dict[str, Any]] = None):
        print("Processing the Bibliography for easy access:")
        print(" -- Warnings may appear here; see the output of the DataChecker for more info --")
        print("---")
        for item in json:
            data = item.get("data", {})
            meta = item.get("meta", {})
            key = item.get("key", None)
            citationKey = data.get("citationKey", None)
            if citationKey:
                # I can only handle and process Items that do have a 
                # citationKey. Otherwise the whole TeX-concept will not work at all. 
                if key not in self.keys_to_data:
                    self.keys_to_data[key] = data
                else: 
                    print(f"WARNING: Item {key} alreaedy exists. This should not have happened.")
                if key not in self.keys_to_meta:
                    self.keys_to_meta[key] = meta
                else: 
                    print(f"WARNING: Item {key} alreaedy exists. This should not have happened.")
            else: 
                print(f"WARNING: Item {key} has no 'citationKey' and will not be processed.")
                print(f"    ('itemType': {data.get("itemType", "NA")},")
                print(f"     added on {data.get("dateAdded", "NA")}).")
                print("---")
            
            tags = data.get("tags", None)
            if tags:
                for tag in tags:
                    tagname = tag.get("tag", None)
                    if tagname not in self.tags_to_keys:
                        self.tags_to_keys[tagname] = []
                    self.tags_to_keys[tagname].append(key)
            
            year = data.get("date", "NA")
            if year not in self.years_to_keys: 
                self.years_to_keys[year] = []
            self.years_to_keys[year].append(key)

            creators = data.get("creators", {})
            
            if key not in self.keys_to_authors:
                self.keys_to_authors[key] = []

            for creator in creators: 
                role = creator.get("creatorType", "NA")
                if role == "editor":
                    # Editors should not be listed as authors; if somehow this
                    # field is empty, we still add the person, mainly because I
                    # don't know what is going on and want to err on the side of
                    # inclusion. 
                    continue
                # I checked what using transliteration as key did to the length
                # of the author list and it went from 1085 (without) to 1084 (with)
                # Now, I do not know if this is good or bad, but I assume it is good. 
                # If I wanted to be very diligent I should check who got merged, but 
                # I won't do that now.  
                firstName = creator.get("firstName", "NA")
                lastName = creator.get("lastName", "NA")
                firstName_latin = transliterate(firstName)
                lastName_latin = transliterate(lastName)

                author_key = (lastName_latin, firstName_latin)
                self.keys_to_authors[key].append(author_key)
                if author_key not in self.author_info:
                    self.author_info[author_key] = {
                        "items": [],
                        "firstName": firstName,
                        "lastName": lastName, 
                        "firstName-latin": transliterate(firstName),
                        "lastName-latin": transliterate(lastName)
                    }
                self.author_info[author_key]["items"].append(key)

    def __prepare_letter_groups(self):
        sorting_alphabet = list(get_sorting_alphabet().upper())
        authors_by_letter = {}
        for letter in sorting_alphabet:
            authors_by_letter[letter] = []
        
        # This is not unneccessary, I am sorting them here so that iterating
        # over this elsewhere will already be in the order I want it in. 
        sorted_authors = sort_turkish(self.author_info.keys())
        for author in sorted_authors:
            first_letter = author[0][0].upper()
            if first_letter in authors_by_letter:
                authors_by_letter[first_letter].append(author)
            else: 
                print(f"WARNING! -- Did not anticipate {first_letter} showing up, and it is thus not in the sorting alphabet.")
        return authors_by_letter

    # ----------------------------------------------------- Data / Keys

    def list_all_keys(self) -> List[str]:
        """
        Returns a list of all item-keys. 

        Args:
            None

        Returns:
            List[str] of item-keys
        """
        keys = self.keys_to_data.keys()
        return keys

    def get_data(self, key) -> Dict[str, None]:
        """
        Returns a Dict containing all the 'data' object for the supplied key 
        in its original state. 

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            Dict: containing e.g. DOI, date, dateAdded, dateModified, creators (List[Dict]). 
                citationKey, title, and much more. All the entered data from Zotero.
        """
        return self.keys_to_data[key]

    def get_citationKey(self, key) -> str:
        """
        Returns the citationKey of the supplied key. 

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            str: citationKey as referenced in the .bib-files used for building LaTeX citations.
        """
        data = self.keys_to_data[key]
        citationKey = data["citationKey"]
        return citationKey

    # ------------------------------------------------- Handle Publication Date
    def list_all_years(self) -> List[str]:
        """
        Returns a list of all publication dates. 

        Args:
            None

        Returns:
            List[str] of publication dates (years, ideally)
        """
        years = self.years_to_keys.keys()
        return years
    
    def get_keys_by_year(self, year: str) -> List[str]:
        """
        Returns a List of item-keys associated with this publication date.

        Args:
            year (str): The year / publication date

        Returns:
            List of item-keys associated with the publication date
        """
        years = self.years_to_keys.keys()
        return years

    # ---------------------------------------------------------- Handle Authors

    def list_all_author_info(self) -> Dict[str, None]:
        """
        Returns a Dict of the full info on all authors indexed by the 
        Tuple of (lastName, firstName) 

        Args:
            None

        Returns:
            Dict of full Author Info.
        """
        return self.author_info

    def list_all_authors_by_letter(self) -> Dict[str, None]:
        """
        Returns a Dict of all author-keys grouped and indexed by the 
        first letter of their last name.

        Args:
            None

        Returns:
            Dict of Letters and author-keys (Tuple of lastName, firstName)
        """
        return self.authors_by_letter

    def get_author(self, author: Tuple[str, str]) -> Dict[str, None]:
        """
        Returns a Dict of the full info this author.
        
        Args:
            author (Tuple(str, str)): The author-key (Tuple of (lastName, firstName)) 

        Returns:
            Dict with list of item-keys, first and last name in original and transliterated state.
        """
        return self.author_info[author]

    def list_all_keys_to_authors(self) -> Dict[str, None]:
        """
        Returns a Dict of all item-keys and the author-keys 
        (Tuple of (lastName, firstName)) associated with them.

        Args:
            None

        Returns:
            Dict of item-key with author-keys
        """
        return self.keys_to_authors

    def get_item_authors(self, key) -> List[Tuple[str, str]]:
        """
        Returns a List of author-keys (Tuple of (lastName, firstName)) 
        associated with the item-key supplied as key.

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            List of Tuples[str, str]
        """
        return self.keys_to_authors[key]
    
    def get_keys_by_author(self, author: Tuple[str, str]) -> List[str]: 
        """
        Returns a List of item-keys authored/edited by this author.
        
        Args:
            author (Tuple(str, str)): The author-key (Tuple of (lastName, firstName)) 

        Returns:
            List of item-keys associated with the author supplied as author
        """
        return self.author_info[author]["items"]
    
    # ------------------------------------------------------------- Handle Tags
    def get_keys_by_tag(self, tag: str) -> List[str]:
        """
        Returns a List of item-keys tagged with the supllied string.
        
        Args:
            tag (str): The tag to query for 

        Returns:
            List[str] of item-keys tagged with this string
        """
        return self.tags_to_keys[tag]

    def get_tags(self, key) -> List[str]:
        """
        Returns a List of all tags this item-key is tagged with.
        
        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            List[str] of tags
        """
        tags = [tag['tag'] for tag in self.keys_to_data[key].get('tags', [])]
        return tags


if __name__ == "__main__":
    import json
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)

    bib = BibliographyClient(data)
    demo = True
    if demo: 
        # Get the data for one item:
        print(bib.get_data("9DBGRJ9A"))

        # Get the citationKey for one item:
        print(bib.get_citationKey("9DBGRJ9A"))

        # Get a Dict of all authors indexed by the Tuple of (lastName, firstName)
        all_authors = bib.list_all_author_info()
        print(all_authors)

        # Get a Dict of all authors indexed by the Tuple of (lastName, firstName)
        print(bib.list_all_authors_by_letter())

        #Get a Lis of all keys belongig to the author-key (lastName, firstName)
        print(bib.get_author(("Steinmann", "Lisa")))
        # Get a Dict of all keys and their respective author-key (lastName, firstName)
        print(bib.list_all_keys_to_authors())
        # Get a Dict of all keys and their respective author-key (lastName, firstName)
        print(bib.get_item_authors("9DBGRJ9A"))
        # Get a Lis of all keys belongig to the author-key (lastName, firstName)
        print(bib.get_keys_by_author(("Steinmann", "Lisa")))
        # Get a Lis of all keys belongig to the author-key (lastName, firstName)
        print(bib.get_keys_by_tag("16 Methodik, Vermessungsarbeiten"))
        # Get a Lis of all keys belongig to the author-key (lastName, firstName)
        print(bib.get_tags("9DBGRJ9A"))
        # Sorting all authors... is annoying, since we do want to use the turkish
        # locale for sorting in this Bibliography. Since setting the locale isn't 
        # super reliable especially in runners, we just use our own turkish-sort:
        from language_services import sort_turkish
        print(sort_turkish(all_authors))
