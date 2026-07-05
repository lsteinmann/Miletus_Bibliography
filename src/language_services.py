# Language Service: transliteration and sorting functions
from unidecode import unidecode


def get_sorting_alphabet() -> str:
    return "aäbcçdefgğhıijklmnoöpqrsştuüvwxyz"


def transliterate(text: str):
    """
    Transliterate any text with non-Latin characters into Latin characters.
    Preserves Turkish and German special characters (ç, ğ, ı, ä, ö, ş, ß, ü)
    and handles all other scripts.

    Args:
        text (str): Text to transliterate

    Returns:
        str: Transliterated text with Latin characters
    """
    # I actually do not want to use unidecode because it strips way too many
    # characters; However, there seems to be no better library that I have found
    # so far and R was much more capable in this transliteration-business.
    preserve_chars = set("ığäüöçşßİĞÄÜÖÇŞ")
    # these are common german and turkish characters that I would like to keep.
    result = "".join(
        char if char in preserve_chars else unidecode(char) for char in text
    )

    return result


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
    turkish_alphabet = get_sorting_alphabet()

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


def sort_turkish(name_tuples):
    """
    Sort a list of (lastName, firstName) tuples according to Turkish alphabetical ordering.
    First sorts by lastName, then by firstName (both using Turkish alphabet rules).

    Args:
        name_tuples (list): List of tuples (lastName, firstName)

    Returns:
        list: Sorted list of tuples
    """

    def get_sort_key(item):
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            x, y = str(item[0]), str(item[1])
            return (turkish_sort_key(x), turkish_sort_key(y))
        else:
            # Handle edge cases
            return (turkish_sort_key(str(item)),)

    return sorted(name_tuples, key=get_sort_key)


# Example usage:
if __name__ == "__main__":
    # Test transliteration with various scripts including Turkish
    test_strings = [
        "Привет мир",  # Russian
        "שלום עולם",  # Hebrew
        "Γειά σου κόσμε",  # Greek
        "こんにちは世界",  # Japanese (Kanji)
        "مرحبا بالعالم",  # Arabic
        "Merhaba dünya",  # Turkish (with special chars)
        "Merhaba Kızıldağ",  # Turkish (with special chars)
        "Café",  # French (accented)
        "München",  # German (umlaut)
    ]

    for text in test_strings:
        print(f"{text} -> {transliterate(text)}")

    print("-------------------------------------------------------------------")
    # Test sorting with Turkish-specific characters
    words = [
        "kalem",
        "kabak",
        "kış",
        "kışlık",
        "kız",
        "kızlık",
        "çanta",
        "çay",
        "çocuk",
        "çocuklar",
        "gözlük",
        "gözlükçü",
        "gözlükçü",
        "ıslak",
        "ıslaklık",
        "ıslaklık",
        "şeker",
        "şekerleme",
        "şekerleme",
        "ödül",
        "ödül",
        "ödül",
        "kütüphane",
        "kütüphane",
        "kütüphane",
    ]

    print("Original:", words)
    print("Turkish sorted:", sort_turkish(words))

    # Test with mixed case
    mixed_case = ["Kalem", "kalem", "KABAK", "kabak"]
    print("Mixed case:", mixed_case)
    print("Turkish sorted:", sort_turkish(mixed_case))

    # Test with tuples (name, age, city)
    people = [
        ("İsmail", "Samsun"),
        ("Ali", "Ankara"),
        ("Yusuf", "Kahramanmaraş"),
        ("Mehmet", "Diyarbakır"),
        ("Özlem", "Trabzon"),
        ("Selin", "Kocaeli"),
        ("Ayşe", "İstanbul"),
        ("Cem", "İzmir"),
        ("Zeynep", "Van"),
        ("Derya", "Bursa"),
        ("Tolga", "Antalya"),
        ("Ferhat", "Adana"),
        ("Gül", "Konya"),
        ("Hakan", "Mersin"),
        ("Kemal", "Eskişehir"),
        ("Nuri", "Gaziantep"),
        # Should not break here
        ("Umut", 2, "Bursa"),
    ]

    print("Original:", [p[0] for p in people])
    sorted_people = sort_turkish(people)
    print("Turkish sorted:", [p[0] for p in sorted_people])
