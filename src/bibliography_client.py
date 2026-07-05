from typing import List, Any, Dict, Tuple
from language_services import transliterate

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
        self.__process_json(json)

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

            creators = data.get("creators", {})
            
            if key not in self.keys_to_authors:
                self.keys_to_authors[key] = []

            for creator in creators: 
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

    # ----------------------------------------------------- Data / Keys

    def get_data(self, key) -> List[Dict[str, None]]:
        return self.keys_to_data[key]

    def get_citationKey(self, key) -> str:
        data = self.keys_to_data[key]
        citationKey = data["citationKey"]
        return citationKey

    # ---------------------------------------------------------- Handle Authors

    def list_all_authors(self) -> Dict[str, None]:
        print("will return a list of Authors")
        return self.author_info

    def list_keys_to_authors(self) -> Dict[str, None]:
        return self.keys_to_authors

    def get_item_authors(self, key) -> List[Dict[str, None]]:
        return self.keys_to_authors[key]
    
    def get_keys_by_author(self, author: Tuple[str, str]) -> List[str]: 
        return self.author_info[author]["items"]
    
    def get_author(self, author: Tuple[str, str]) -> Dict[str, None]:
        return self.author_info[author]
    
    # ------------------------------------------------------------- Handle Tags
    def get_keys_by_tag(self, tag: str) -> List[str]:
        return self.tags_to_keys[tag]

    def get_tags(self, key) -> List[str]:
        tags = [tag['tag'] for tag in self.keys_to_data[key].get('tags', [])]
        return tags


if __name__ == "__main__":
    import json
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)

    bib = BibliographyClient(data)
    
    tmp = bib.list_all_authors()
    from language_services import sort_turkish
    print(sort_turkish(tmp, key_index=0))
