from typing import List, Dict, Any, Tuple
import datetime
import re


class DataChecker:
    """
    Checks the Bibliography-data for problematic entries.
    """

    def __init__(
        self,
        items: List[Dict[str, Any]] = None,
        tags: "TagClient" = None,
        logfile: str = "out/check_result.log",
    ):
        """
        Initialize the DataChecker.

        Args:
            tags (TagClient): Tag client instance for tag processing
        """
        self.items = {}
        self.clean_items = {}
        self._process_items(items)

        self.logfile = logfile
        self.tags = tags
        log = open(logfile, "w")
        log.writelines(f"Processing date and time: {datetime.datetime.now()}\n\n")
        log.close()
        print("Initialized the DataChecker.")

    def log(self, msg):
        print(msg)
        log = open(self.logfile, "a")
        log.write(f"{msg} \n\n")
        log.close()

    def _process_items(self, items: List[Dict[str, Any]]) -> Dict[str, None]:
        """
        Compiles a more compact dict of relevant info for quicker checking,
        discards 'note'-itemTypes as those are not processed later anyway.
        """
        for item in items:
            key = item.get("key", "")
            if key not in self.items:
                self.items[key] = item
            item_data = item.get("data", "")
            if item_data.get("itemType") == "note":
                continue
            else:
                meta = item.get("meta")
                creator_user = meta.get("createdByUser")
                tags = [tag["tag"] for tag in item_data.get("tags", [])]
                this_item = {
                    "key": key,
                    "citationKey": item_data.get("citationKey", None),
                    "title": item_data.get("title", None),
                    "tags": tags,
                    "date": item_data.get("date", None),
                    "creators": item_data.get("creators", []),
                    "dateAdded": item_data.get("dateAdded", None),
                    "createdBy": creator_user.get("username", None),
                }
                if key not in self.clean_items:
                    self.clean_items[key] = this_item

    def _log_item_info(self, key: str):
        item = self.clean_items[key]
        msg = (
            key
            + ": "
            + item["title"]
            + " (added by user "
            + item["createdBy"]
            + " on "
            + item["dateAdded"]
            + ")"
        )
        self.log(msg)

    def find_missing_citation_keys(self):
        self.log("----------------------------------------------------------\n")
        self.log("Checking for items with missing citationKeys...")
        missing = []
        for key in self.clean_items:
            if not self.clean_items[key]["citationKey"]:
                missing.append(key)
        if len(missing) > 0:
            self.log(f"Found {len(missing)} items missing citationKeys:")
            for key in missing:
                self._log_item_info(key)
            self.log("You need to check and fix these.")
        else:
            self.log("There are no items with missing citationKeys - excellent.")

    def find_duplicate_citation_keys(self):
        self.log("----------------------------------------------------------\n")
        self.log("Checking for duplicate citationKeys...")
        counts = {}
        multiple = []
        for key in self.clean_items:
            citKey = self.clean_items[key]["citationKey"]
            counts[citKey] = counts.get(citKey, 0) + 1
            if counts[citKey] > 1:
                multiple.append(key)
        if len(multiple) > 0:
            self.log(f"Found {len(multiple)} duplicate citationKeys:")
            for key in multiple:
                self._log_item_info(key)
            self.log("You need to check and fix these.")
        else:
            self.log("There are no duplicate citationKeys - excellent.")

    def find_items_without_tags(self):
        self.log("----------------------------------------------------------\n")
        missing_tags = []
        all_tags = self.tags.get_all_tags()
        for key in self.clean_items:
            tags = set(self.clean_items[key]["tags"])
            if tags.isdisjoint(all_tags):
                missing_tags.append(key)
        if len(missing_tags) > 0:
            self.log(f"Found {len(missing_tags)} items without systematic tags:")
            for key in missing_tags:
                self._log_item_info(key)
        else:
            self.log("All items have at least one systematic tag. Good Job.")

    def find_items_without_publication_date(self):
        self.log("----------------------------------------------------------\n")
        self.log("Checking for items with a malformed publication date / year...")
        pattern = r"^\d{4}$"
        missing_date = []
        for key in self.clean_items:
            date = self.clean_items[key]["date"]
            if not re.match(pattern, date):
                missing_date.append(key)
        if len(missing_date) > 0:
            self.log(
                f"Found {len(missing_date)} items without a well-formatted publication year:"
            )
            for key in missing_date:
                self._log_item_info(key)
            self.log(f"\nPlease fix them by reducing them to a four digit number.")
            self.log(
                "Otherwise, the bibliography-by-year-pdf may not be filled correctly."
            )
        else:
            self.log(
                "All items have four-digit-numbers as the publication year. Good Job."
            )

    def find_items_without_authors(self):
        self.log("----------------------------------------------------------\n")
        missing_authors = []
        for key in self.clean_items:
            creators = self.clean_items[key]["creators"]
            author_counter = []
            for creator in creators:
                role = creator.get("creatorType")
                if role == "author":
                    author_counter.append(role)
            if len(author_counter) < 1:
                missing_authors.append(key)
        if len(missing_authors) > 0:
            self.log(f"Found {len(missing_authors)} items without authors:")
            for key in missing_authors:
                self._log_item_info(key)
            self.log("\nThis may or may not be correct, please check!")
            self.log("Missing authors can cause problems when building the pdfs.")
        else:
            self.log("All items have at least one author. Good Job.")

    def check_all(self):
        self.find_missing_citation_keys()
        self.find_duplicate_citation_keys()
        self.find_items_without_tags()
        self.find_items_without_publication_date()
        self.find_items_without_authors()


# Example usage:
if __name__ == "__main__":
    import json
    from src.tag_client import TagClient

    # Initialize with tag client
    with open("data/Milet_Bibliography_JSON.json", "r") as file:
        data = json.load(file)

    tags = TagClient()
    data_checker = DataChecker(data, tags, "out/check_result.log")

    data_checker.find_missing_citation_keys()
    data_checker.find_duplicate_citation_keys()
    data_checker.find_items_without_tags()
    data_checker.find_items_without_publication_date()
    data_checker.find_items_without_authors()
