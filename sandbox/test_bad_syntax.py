from bad_syntax import *

def test_calculate_sum_normal_case():
    """
    Test calculate_sum function with normal case.
    """
    assert calculate_sum(1, 2) == 3

def test_calculate_sum_negative_numbers():
    """
    Test calculate_sum function with negative numbers.
    """
    assert calculate_sum(-1, -2) == -3

def test_calculate_sum_mixed_numbers():
    """
    Test calculate_sum function with mixed numbers.
    """
    assert calculate_sum(-1, 2) == 1

def test_calculate_sum_zero():
    """
    Test calculate_sum function with zero.
    """
    assert calculate_sum(0, 0) == 0

def test_calculate_sum_non_numeric_input():
    """
    Test calculate_sum function with non-numeric input.
    """
    try:
        calculate_sum('a', 2)
        assert False, "Expected TypeError"
    except TypeError:
        pass

def test_calculate_sum_single_argument():
    """
    Test calculate_sum function with single argument.
    """
    try:
        calculate_sum(1)
        assert False, "Expected TypeError"
    except TypeError:
        pass

def test_calculate_sum_no_arguments():
    """
    Test calculate_sum function with no arguments.
    """
    try:
        calculate_sum()
        assert False, "Expected TypeError"
    except TypeError:
        pass