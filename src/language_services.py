# Language Service: transliteration and sorting functions
from unidecode import unidecode

def transliterate(text: str):
    """
    Transliterate any text with non-Latin characters into Latin characters.
    Preserves Turkish special characters (ç, ğ, ı, ö, ş, ü) and handles all other scripts.
    
    Args:
        text (str): Text to transliterate
        
    Returns:
        str: Transliterated text with Latin characters
    """
    turkish_chars = set('ığüöçşİĞÜÖÇŞ')
    result = ''.join(char if char in turkish_chars else unidecode(char) for char in text)

    return result

# turkish_sort.py
def turkish_sort_key(text):
    """
    Generate a sort key for Turkish alphabet ordering.
    Handles Turkish-specific letter ordering (ç, ğ, ı, ö, ş, ü)
    and preserves case sensitivity.
    
    Args:
        text (str): String to generate sort key for
        
    Returns:
        tuple: Sort key tuple for proper Turkish alphabetical ordering
    """
    # Define Turkish alphabet order (excluding special characters)
    turkish_alphabet = 'abcçdefgğhıijklmnoöprsştuüvyz'
    
    # Create a mapping from each character to its position in Turkish alphabet
    char_to_index = {char: i for i, char in enumerate(turkish_alphabet)}
    
    # Convert to lowercase for consistent comparison
    text_lower = text.lower()
    
    # Build sort key by converting each character to its index
    # For characters not in Turkish alphabet, use a high index to place them at the end
    sort_key = []
    for char in text_lower:
        if char in char_to_index:
            sort_key.append(char_to_index[char])
        else:
            # Non-Turkish characters go after Turkish ones
            sort_key.append(len(char_to_index) + ord(char))
    
    return tuple(sort_key)


def sort_turkish(items, key_index=0, key_func=None):
    """
    Sort a list of items according to Turkish alphabet rules.
    Can handle lists of tuples, lists of lists, or any other iterable.
    
    Args:
        items (list): List of items to sort (tuples, lists, etc.)
        key_index (int): Index of the element to sort by (default: 0)
        key_func (callable): Optional function to extract the sort key from each item
        
    Returns:
        list: Sorted list of items
    """
    def get_sort_key(item):
        if key_func:
            # Use the provided key function
            return turkish_sort_key(key_func(item))
        
        # Extract the specified element from the item
        if isinstance(item, (list, tuple)):
            if key_index < len(item):
                return turkish_sort_key(str(item[key_index]))
            else:
                # If index is out of range, use empty string
                return turkish_sort_key("")
        else:
            # For non-iterable items, treat as string
            return turkish_sort_key(str(item))
    
    return sorted(items, key=get_sort_key)


# Example usage:
if __name__ == "__main__":
    # Test transliteration with various scripts including Turkish
    test_strings = [
        "Привет мир",           # Russian
        "שלום עולם",           # Hebrew
        "Γειά σου κόσμε",       # Greek
        "こんにちは世界",         # Japanese (Kanji)
        "مرحبا بالعالم",        # Arabic
        "Merhaba dünya",         # Turkish (with special chars)
        "Merhaba Kızıldağ",         # Turkish (with special chars)
        "Café",                  # French (accented)
        "München",               # German (umlaut)
    ]
    
    for text in test_strings:
        print(f"{text} -> {transliterate(text)}")

    print("-------------------------------------------------------------------")
    # Test sorting with Turkish-specific characters
    words = [
        "kalem", "kabak", "kış", "kışlık", "kız", "kızlık",
        "çanta", "çay", "çocuk", "çocuklar",
        "gözlük", "gözlükçü", "gözlükçü",
        "ıslak", "ıslaklık", "ıslaklık",
        "şeker", "şekerleme", "şekerleme",
        "ödül", "ödül", "ödül",
        "kütüphane", "kütüphane", "kütüphane"
    ]
    
    print("Original:", words)
    print("Turkish sorted:", sort_turkish(words))
    
    # Test with mixed case
    mixed_case = ["Kalem", "kalem", "KABAK", "kabak"]
    print("Mixed case:", mixed_case)
    print("Turkish sorted:", sort_turkish(mixed_case))

    # Test with tuples (name, age, city)
    people = [
        ("İsmail", 29, "Samsun"),
        ("Ali", 25, "Ankara"),
        ("Yusuf", 36, "Kahramanmaraş"),
        ("Mehmet", 26, "Diyarbakır"),
        ("Özlem", 24, "Trabzon"),
        ("Selin", 23, "Kocaeli"),
        ("Ayşe", 30, "İstanbul"),
        ("Cem", 22, "İzmir"),
        ("Zeynep", 20, "Van"),
        ("Derya", 28, "Bursa"),
        ("Tolga", 34, "Antalya"),
        ("Ferhat", 35, "Adana"),
        ("Gül", 27, "Konya"),
        ("Hakan", 32, "Mersin"),
        ("Kemal", 31, "Eskişehir"),
        ("Nuri", 33, "Gaziantep"),
        ("Umut", 21, "Bursa")
    ]
    
    print("Original:", [p[0] for p in people])
    sorted_people = sort_turkish(people, key_index=0)
    print("Turkish sorted:", [p[0] for p in sorted_people])