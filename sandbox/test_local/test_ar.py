from ar import hello

def test_hello_variable_exists():
    """
    Checks if the hello variable exists in the module.
    """
    assert 'hello' in globals(), "The hello variable does not exist"

def test_hello_variable_is_string():
    """
    Checks if the hello variable is a string.
    """
    assert isinstance(hello, str), "The hello variable is not a string"

def test_hello_variable_value():
    """
    Checks if the hello variable has the expected value.
    """
    assert hello == "Hello, World!", "The hello variable has an unexpected value"

def test_hello_variable_is_not_empty():
    """
    Checks if the hello variable is not empty.
    """
    assert len(hello) > 0, "The hello variable is empty"

def test_hello_variable_prints_correctly(capsys):
    """
    Checks if the hello variable prints correctly.
    """
    print(hello)
    captured = capsys.readouterr()
    assert captured.out == "Hello, World!\n", "The hello variable does not print correctly"