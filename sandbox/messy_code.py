min_exclusive = 0
max_exclusive = 100

def is_within_range(value_to_check):
    """
    Checks if the input value is within the specified range.

    Args:
        value_to_check: The value to check.

    Returns:
        True if the input value is within the specified range, False otherwise.

    Raises:
        TypeError: If the input is not an integer.
    """
    if not isinstance(value_to_check, int):
        raise TypeError("Input must be an integer. Expected an integer within the exclusive range ({}, {})".format(min_exclusive, max_exclusive))
    return min_exclusive < value_to_check < max_exclusive