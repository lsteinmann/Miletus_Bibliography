from typing import List, Any, Dict, Tuple, Optional
from src.language_services import transliterate, get_sorting_alphabet, sort_turkish, turkish_sort_key
from src.utils import extract_four_digits

# TODO
# - This could include a query by year, and I could manually build the 
#   year-wise bibliography same as the author-wise one; this would be better, 
#   because it would include the fucked-up year-entries as well such as 
#   1964/65 etc., as I am able to clean them up here much better than in the 
#   database itself (as that is prone to human error and zotero does not care.)

class BibliographyClient: 
    def __init__(
        self, 
        json: List[Dict[str, Any]] = None,
        tags: 'TagClient' = None
    ):
        print("The Author Client has been initialized. ;)")
        self.tags = tags

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
            
            year = extract_four_digits(data.get("date", "NA"))
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
                # If an author is listed twice, e.g. as bookAuthor and also author, 
                # they would be added twice and the key would be added twice to their
                # entry. Therefore in both cases I check if the author_key exists
                # already, and down there if the key already exists for the author.
                # I have to change this if I ever want to add roles somewhere.
                if author_key not in self.keys_to_authors[key]: 
                    self.keys_to_authors[key].append(author_key)
                if author_key not in self.author_info:
                    self.author_info[author_key] = {
                        "items": [],
                        "firstName": firstName,
                        "lastName": lastName, 
                        "firstName-latin": transliterate(firstName),
                        "lastName-latin": transliterate(lastName)
                    }
                if key not in self.author_info[author_key]["items"]:
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

    def _sort_by_year(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Expects: 
        [
            {
                "citationKey": "bla", 
                "year": "1234"
            },
            {
                "citationKey": "bla", 
                "year": "1235"
            }
        ]
        """
        result = sorted(items, key=lambda x: x["year"])
        return result

    def _sort_by_author(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Expects: 
        [
            {
                "citationKey": "bla", 
                "author": ("Müller", "Hans")
            },
            {
                "citationKey": "bla", 
                "author": ("Öztürk", "Mahmut")
            }
        ]
        """
        sorted_items = sort_turkish(items)
        return sorted_items

    def _sort_by_author_and_year(self, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
        def sort_key(item: Dict[str, str]) -> Tuple[Tuple, int, int]:
            # Validate required keys
            if "author" not in item or "year" not in item:
                raise KeyError(f"Missing 'author' or 'year' in item: {item}")
    
            author_tuple = item["author"]
            year_raw = item["year"]
    
            # Handle author
            if isinstance(author_tuple, str):
                last_name, first_name = author_tuple, ""
            elif isinstance(author_tuple, (tuple, list)) and len(author_tuple) >= 2:
                last_name, first_name = author_tuple[0], author_tuple[1]
            else:
                last_name, first_name = str(author_tuple), ""
    
            # Handle year: convert to int, but handle None and invalid values
            if year_raw is None:
                year_int = -1  # or float('-inf') if you want None to come first
            else:
                try:
                    year_int = int(year_raw)
                except (ValueError, TypeError):
                    year_int = float('inf')  # invalid years go last
    
            return (turkish_sort_key(last_name), turkish_sort_key(first_name), year_int)
    
        return sorted(items, key=sort_key)

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

    def get_data(self, key) -> Optional[Dict[str, None]]:
        """
        Returns a Dict containing all the 'data' object for the supplied key 
        in its original state. 

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            Dict: containing e.g. DOI, date, dateAdded, dateModified, creators (List[Dict]). 
                citationKey, title, and much more. All the entered data from Zotero.
        """
        if key in self.keys_to_data:
            return self.keys_to_data[key]
        else: 
            return None

    def get_citationKey(self, key) -> Optional[str]:
        """
        Returns the citationKey of the supplied key. 

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            str: citationKey as referenced in the .bib-files used for building LaTeX citations.
        """
        if key in self.keys_to_data:
            data = self.keys_to_data[key]
            citationKey = data["citationKey"]
            return citationKey
        else:
            return None

    def get_publication_year(self, key) -> Optional[str]:
        """
        Returns the "date" (publication year) of the supplied key. 

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            str: whatever is written in the date field.
        """
        if key in self.keys_to_data:
            data = self.keys_to_data[key]
            year = extract_four_digits(data.get("date", None))
            return year
        else: 
            return None

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
        associated with the item-key supplied as key. If there is no 
        author recorded as the 'author', then it will give all creators of 
        the item as (lastName, firstName)-Tuples.

        Args:
            key (str): The key (ID / key of the item in the Zotero database)

        Returns:
            List of Tuples[str, str]
        """
        authors = self.keys_to_authors[key]
        if len(authors) == 0:
            raw = self.get_data(key)
            authors = []
            for creator in raw["creators"]:
                first = creator.get("firstName", "NA")
                last = creator.get("lastName", "NA")
                authors.append((transliterate(last), transliterate(first)))
        if len(authors) == 1:
            return [authors]
        else: 
            return authors
    
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
    
    def get_sorted_author_groups(self) -> Dict[str, List[str]]:
        """Return authors grouped by letter with properly sorted items."""
        # Use your existing authors_by_letter and sort_turkish
        # Return a dict where each letter maps to a list of citationKeys

        # Migrate from LatexGenerator here. 
        pass

    def get_sorted_year_groups(self) -> List[str]:
        """Return years in descending order with proper sorting."""
        # Extract and sort years properly

        # Migrate from LatexGenerator here. 
        pass

    def get_sorted_tag_groups(self) -> Dict[str, List[str]]:
        """Return tags organized by hierarchy with proper sorting."""
        # Return a dict of tag -> ordered list of citationKeys
        structured_bib = {}
        all_tags = self.tags.get_all_tags()
        for tag in all_tags:
            #print("-----------------------------------------------------------------------")
            #print("--------------   " + tag + "    ------------------------------")
            #print("-----------------------------------------------------------------------")
            this_tag = self.tags.get_tag_info(tag)
            if tag == "01 Grabungs und Arbeitsberichte":
                # We are treating this one differently, because here we need 
                # everything sorted by year only - we don't care who authored it. 
                # This is the timeline.
                if tag not in structured_bib:
                    structured_bib[tag] = []
                keys = self.get_keys_by_tag(tag)
                items = []
                for key in keys: 
                    year = self.get_publication_year(key)
                    items.append({
                        "citationKey": self.get_citationKey(key), 
                        "year": extract_four_digits(year)
                    })
                items = self._sort_by_year(items)
                for item in items:
                    structured_bib[tag].append(item["citationKey"])
                continue
            # And this is for *all* other sections, subsections, and subsubsections.
            if tag not in structured_bib:
                structured_bib[tag] = []
            section_keys = self.get_keys_by_tag(tag)
            # This is also where a little bit of sillyness begins: 
            child_tags = set(self.tags.get_children(tag))
            keys_in_subsections = []
            for child_tag in child_tags:
                # I need all the keys that are linked to one of the child tags, 
                # as well as one of the "grandchildren" - if they exist.
                # If a third level is ever added to the bibliography, this will 
                # not actually work anymore. I mean, it will work, but it needs 
                # another level... or to be dynamic / recursive. 
                keys_in_subsections.extend(self.get_keys_by_tag(child_tag))
                grandchild_tags = set(self.tags.get_children(child_tag))
                # This simply won't run if the tag in questions has no children. 
                for grandchild_tag in grandchild_tags:
                    keys_in_subsections.extend(self.get_keys_by_tag(grandchild_tag))
            # Here we remove all items/keys that are present in one of the sub-sections of
            # this section from the current set of keys. 
            # Why are we doing this? All items are tagged with multiple tags. 
            # An item that would be tagged with one of the "sub" or "sub-sub"-section
            # tags will also be tagged with the highest section, usually. 
            # But we don't need all items to appear in these "broader" sections
            # when it will be clear from the structure of the pdf that they belong
            # to that larger group.  
            section_keys = set(section_keys) - set(keys_in_subsections)
            items = []
            # Since we want to always sort by (first recorded) author and then
            # year, we need to assemble the data:
            for key in section_keys:
                author = self.get_item_authors(key)
                if author: 
                    author = author[0]
                else:
                    author = ("NA", "NA")
                items.append({
                    "citationKey": self.get_citationKey(key), 
                    "author": author,
                    "year": self.get_publication_year(key)
                })
            items = self._sort_by_author_and_year(items)
            for item in items:
                structured_bib[tag].append(item["citationKey"])
            #print(structured_bib[tag])     
        return structured_bib


if __name__ == "__main__":
    import json
    from src.tag_client import TagClient

    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)
    tag_client = TagClient("data/tags/tags_sys.csv")

    bib = BibliographyClient(json=data,tags=tag_client)
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
        from src.language_services import sort_turkish
        print(sort_turkish(all_authors))

        print("----------- Tags:")
        tmp = bib.get_sorted_tag_groups()
        print(tmp)
