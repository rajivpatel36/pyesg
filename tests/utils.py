import os

def get_tests_directory() -> str:
    """
    Returns the path of the top level directory for tests.
    Returns: The path of the top level directory for tests.

    This is useful for constructing paths to the test files.
    """
    module_file_path = os.path.abspath(__file__)
    return os.path.dirname(module_file_path)
