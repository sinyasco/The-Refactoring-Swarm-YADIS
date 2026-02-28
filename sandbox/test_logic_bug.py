from logic_bug import *

def test_count_down_normal_case():
    """
    Test count_down function with a normal case.
    It should print numbers from n to 1.
    """
    import io
    import sys
    capturedOutput = io.StringIO()  # Create StringIO object
    sys.stdout = capturedOutput  # Redirect stdout
    count_down(5)
    sys.stdout = sys.__stdout__  # Reset stdout
    output = capturedOutput.getvalue().strip()
    assert output == "5\n4\n3\n2\n1", "count_down function does not work as expected"

def test_count_down_edge_case_zero():
    """
    Test count_down function with an edge case (n = 0).
    It should not print anything.
    """
    import io
    import sys
    capturedOutput = io.StringIO()  # Create StringIO object
    sys.stdout = capturedOutput  # Redirect stdout
    count_down(0)
    sys.stdout = sys.__stdout__  # Reset stdout
    output = capturedOutput.getvalue().strip()
    assert output == "", "count_down function does not work as expected for n = 0"

def test_count_down_edge_case_negative():
    """
    Test count_down function with an edge case (n < 0).
    It should not print anything.
    """
    import io
    import sys
    capturedOutput = io.StringIO()  # Create StringIO object
    sys.stdout = capturedOutput  # Redirect stdout
    count_down(-5)
    sys.stdout = sys.__stdout__  # Reset stdout
    output = capturedOutput.getvalue().strip()
    assert output == "", "count_down function does not work as expected for n < 0"

def test_count_down_bug():
    """
    Test count_down function with the known bug.
    It should not enter an infinite loop.
    """
    import io
    import sys
    capturedOutput = io.StringIO()  # Create StringIO object
    sys.stdout = capturedOutput  # Redirect stdout
    try:
        count_down(5)
    except KeyboardInterrupt:
        pass
    sys.stdout = sys.__stdout__  # Reset stdout
    output = capturedOutput.getvalue().strip()
    assert output != "", "count_down function does not work as expected due to the bug"