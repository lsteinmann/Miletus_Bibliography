import requests
import time
from typing import List, Dict, Any
import pandas as pd

class ZoteroClient:
    """
    A client for fetching data from Zotero Group Library API.
    Handles pagination and different export formats.
    """
    
    def __init__(self, group_id: str = "4475959"):
        """
        Initialize the ZoteroClient.
        
        Args:
            group_id (str): Zotero group ID
        """
        self.group_id = group_id
        self.base_url = f"https://api.zotero.org/groups/{group_id}/items"
        self.headers = {
            'Accept': 'application/json'
        }
    
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
    
    def _fetch_items_batch(self, start_index: int, format_type: str = "csv") -> str:
        """
        Fetch a batch of items from Zotero API.
        
        Args:
            start_index (int): Starting index for batch
            format_type (str): Format type ("csv", "json", "biblatex", "bibtex", "ris")
            
        Returns:
            str: Raw response data
        """
        params = {
            'limit': 100,
            'start': start_index,
            'v': 3
        }
        
        # Set format parameter based on type
        if format_type != "csv":
            params['format'] = format_type
        
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
    
    def _fetch_all_items(self, format_type: str = "csv") -> List[str]:
        """
        Generalized internal method to fetch all items in batches.
        
        Args:
            format_type (str): Format type to fetch
            
        Returns:
            List[str]: List of raw response texts for each batch
        """
        # Get total items count
        total_items = self._get_total_items()
        print(f"Found {total_items} items in Zotero library")
        
        # Generate sequence for batching
        batch_size = 100
        sequences = list(range(0, total_items, batch_size))
        
        all_responses = []
        
        for i, start_index in enumerate(sequences):
            print(f"Fetching batch {i+1}/{len(sequences)} (items {start_index}-{min(start_index+batch_size, total_items)})")
            
            try:
                response_data = self._fetch_items_batch(start_index, format_type)
                all_responses.append(response_data)
                
                # Be respectful to the API - add delay between requests
                if i < len(sequences) - 1:  # Don't sleep after the last batch
                    time.sleep(1)  # Wait 1 second between requests
                    
            except Exception as e:
                print(f"Failed to fetch batch {i+1}: {e}")
                raise
        
        return all_responses
    
    def get_csv(self) -> str:
        """
        Get all items in CSV format.
        
        Returns:
            str: Combined CSV data
        """
        responses = self._fetch_all_items("csv")
        return '\n'.join(responses)
    
    def get_json(self) -> List[Dict[str, Any]]:
        """
        Get all items in JSON format.
        
        Returns:
            List[Dict[str, Any]]: List of JSON objects
        """
        responses = self._fetch_all_items("json")
        # In a real implementation, you'd parse JSON here
        # For now, returning raw responses as strings
        return responses
    
    def get_biblatex(self) -> str:
        """
        Get all items in BibLaTeX format.
        
        Returns:
            str: Combined BibLaTeX data
        """
        responses = self._fetch_all_items("biblatex")
        return '\n'.join(responses)
    
    def get_bibtex(self) -> str:
        """
        Get all items in BibTeX format.
        
        Returns:
            str: Combined BibTeX data
        """
        responses = self._fetch_all_items("bibtex")
        return '\n'.join(responses)
    
    def get_ris(self) -> str:
        """
        Get all items in RIS format.
        
        Returns:
            str: Combined RIS data
        """
        responses = self._fetch_all_items("ris")
        return '\n'.join(responses)

# Example usage:
if __name__ == "__main__":
    # Initialize the Zotero client
    zotero = ZoteroClient()
    
    print("Zotero Client initialized successfully!")
    
    # Example of how to use it (uncomment to test):
    # csv_data = zotero.get_csv()
    # print(f"Got CSV data with {len(csv_data)} characters")