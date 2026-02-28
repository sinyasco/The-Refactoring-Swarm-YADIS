from messy_code import *

def test_is_within_range_value_normal_case():
    """
    Checks if the function returns True for a value within the specified range.
    """
    assert is_within_range_value(50) == True

def test_is_within_range_value_edge_case_min_exclusive():
    """
    Checks if the function returns False for the minimum exclusive value.
    """
    assert is_within_range_value(MIN_EXCLUSIVE) == False

def test_is_within_range_value_edge_case_max_exclusive():
    """
    Checks if the function returns False for the maximum exclusive value.
    """
    assert is_within_range_value(MAX_EXCLUSIVE) == False

def test_is_within_range_value_error_case_non_integer():
    """
    Checks if the function raises a TypeError for a non-integer input.
    """
    try:
        is_within_range_value("50")
        assert False, "Expected TypeError to be raised"
    except TypeError as e:
        assert str(e).startswith("Input must be an integer")

def test_is_within_range_value_error_case_float():
    """
    Checks if the function raises a TypeError for a float input.
    """
    try:
        is_within_range_value(50.5)
        assert False, "Expected TypeError to be raised"
    except TypeError as e:
        assert str(e).startswith("Input must be an integer")

def test_is_within_range_value_error_case_security_risk():
    """
    Checks if the function's error message includes the actual value, which could be a security risk.
    """
    try:
        is_within_range_value("50")
        assert False, "Expected TypeError to be raised"
    except TypeError as e:
        assert "50" in str(e), "Error message should not include the actual value to prevent potential security risks"

def test_is_within_range_value_docstring():
    """
    Checks if the function's docstring follows Python documentation conventions.
    """
    import inspect
    docstring = inspect.getdoc(is_within_range_value)
    assert docstring is not None, "Function is missing a docstring"
    assert "Args:" in docstring, "Docstring is missing Args section"
    assert "Returns:" in docstring, "Docstring is missing Returns section"
    assert "Raises:" in docstring, "Docstring is missing Raises section"

def test_is_within_range_value_function_name():
    """
    Checks if the function name follows Python naming conventions.
    """
    import re
    assert re.match("^[a-z_][a-z0-9_]*$", is_within_range_value.__name__), "Function name does not follow Python naming conventions"

def test_is_within_range_value_variable_names():
    """
    Checks if the variable names follow Python naming conventions.
    """
    import inspect
    source_code = inspect.getsource(is_within_range_value)
    variable_names = [word for word in source_code.split() if word.isidentifier()]
    for variable_name in variable_names:
        assert re.match("^[a-z_][a-z0-9_]*$", variable_name), f"Variable name '{variable_name}' does not follow Python naming conventions"