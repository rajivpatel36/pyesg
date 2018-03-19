from collections import Counter
from typing import Iterable


def get_duplicates(x: Iterable):
    """
    Returns the duplicates in an iterable.
    Args:
        x: The iterable for which duplicates are to be found. The values should be hashable.

    Returns:
        The duplicate values in `x`
    """
    return [item for item, count in Counter(x).items() if count > 1]
