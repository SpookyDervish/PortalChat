def abbreviate(s: str):
    """Create an acronym from a sentence.

    Args:
        s (str): The input sentence.

    Returns:
        acronym: A capitalized acronym created using the input sentence.
    """
    return ''.join(word[0].upper() for word in s.split())