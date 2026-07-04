import requests
import time
from typing import List, Dict, Any
import json

class ZoteroClient:
    """
    A client for fetching data from Zotero Group Library API.
    Handles pagination and different export formats.
    """
    
    def __init__(self, group_id: str = "4475959"):
        """
        Initialize the ZoteroClient.
        
        Args:
            group_id (str): Zotero group ID; the default 4475959 is the Miletus Bibliography.
        """
        self.group_id = group_id
        self.base_url = f"https://api.zotero.org/groups/{group_id}/items"
        self.headers = {
            'Accept': 'application/json'
        }
        self.format_types = frozenset(["csv", "json", "biblatex", "bibtex", "ris"])
        self.csv_data = None
        self.json_data = None
    
    def _get_total_items(self) -> int:
        """
        Get the total number of items in the Zotero group library.
        
        Returns:
            int: Total number of items
        """
        response = requests.get(
            self.base_url,
            headers=self.headers,
            params={'limit': 1, 'v': 3}
        )
        response.raise_for_status()
        return int(response.headers.get('Total-Results', 0))
    
    def _fetch_items_batch(self, start_index: int, format_type: str = "csv", batch_size: int = 100) -> str:
        """
        Fetch a batch of items from Zotero API.
        
        Args:
            start_index (int): Starting index for batch
            format_type (str): Format type ("csv", "json", "biblatex", "bibtex", "ris")
            
        Returns:
            str: Raw response data
        """
        params = {
            'limit': batch_size,
            'start': start_index,
            'v': 3
        }
        
        # Set format parameter based on type
        if format_type in self.format_types:
            params['format'] = format_type
        else: 
            raise Exception(f"Format must be one of {format_types}")
        
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            
            # Handle HTTP errors
            if response.status_code == 403:
                raise Exception("Authentication failed. Check your API key.")
            elif response.status_code == 503:
                raise Exception("Server under maintenance. Try again later.")
            elif response.status_code != 200:
                response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching items starting at {start_index}: {e}")
            raise
    
    def _fetch_items(self, format_type: str = "csv", limit: int = 0) -> List[str]:
        """
        Generalized internal method to fetch all items in batches.
        
        Args:
            format_type (str): Format type to fetch
            limit (int): 0 means no limit, otherwise sets the maximum of items to fetch
            
        Returns:
            List[str]: List of raw response texts for each batch
        """
        # Get total items count
        total_items = self._get_total_items()
        print(f"Found {total_items} items in Zotero library")

        if limit == 0:
            fetch_limit = total_items
        else: 
            fetch_limit = limit
        
        # Generate sequence for batching, a batch should not be larger than 100, 
        # but if we want to fetch less than 100 items... well this is not correct either
        # but enough for testing right now.
        if fetch_limit >= 100: 
            batch_size = 100
        else: 
            batch_size = fetch_limit
        sequences = list(range(0, fetch_limit, batch_size))
        
        all_responses = []
        
        for i, start_index in enumerate(sequences):
            print(f"Fetching batch {i+1}/{len(sequences)} (items {start_index}-{min(start_index+batch_size, fetch_limit)})")
            
            try:
                response_data = self._fetch_items_batch(start_index, format_type, batch_size)
                all_responses.append(response_data)
                
                # Be respectful to the API - add delay between requests
                if i < len(sequences) - 1:  # Don't sleep after the last batch
                    time.sleep(1)  # Wait 1 second between requests
                    
            except Exception as e:
                print(f"Failed to fetch batch {i+1}: {e}")
                raise
        
        return all_responses
    
    def get_csv(self, limit: int = 0) -> str:
        """
        Get all items in CSV format.
        
        Returns:
            str: Combined CSV data
        """
        responses = self._fetch_items("csv", limit = limit)
        result = '\n'.join(responses)
        self.csv_data = result

        return result 
    
    def get_json(self, limit: int = 0) -> List[Dict[str, Any]]:
        """
        Get all items in JSON format.
        
        Returns:
            List[Dict[str, Any]]: List of JSON objects
        """
        all_items = []
        responses = self._fetch_items("json", limit = limit)
        for response in responses:
            data = json.loads(response)
            all_items.extend(data)
    
        self.json_data = all_items
        result = json.dumps(all_items, ensure_ascii=False, sort_keys=True)
        return result
    
    def get_biblatex(self, limit: int = 0) -> str:
        """
        Get all items in BibLaTeX format.
        
        Returns:
            str: Combined BibLaTeX data
        """
        responses = self._fetch_items("biblatex", limit = limit)
        result = '\n'.join(responses)

        return result
    
    def get_bibtex(self, limit: int = 0) -> str:
        """
        Get all items in BibTeX format.
        
        Returns:
            str: Combined BibTeX data
        """
        responses = self._fetch_items("bibtex", limit = limit)
        result = '\n'.join(responses)

        return result
    
    def get_ris(self, limit: int = 0) -> str:
        """
        Get all items in RIS format.
        
        Returns:
            str: Combined RIS data
        """
        responses = self._fetch_items("ris", limit = limit)
        result = '\n'.join(responses)

        return result

    
# Example usage:
if __name__ == "__main__":
    # Initialize the Zotero client
    zotero = ZoteroClient()

    # Get and save the bibliography: 
    csv = zotero.get_csv(limit=10)
    print(csv)
