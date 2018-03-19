class ModelNotExistsError(Exception):
    """
    Raised when trying to create a model which doesn't exist.
    """
    pass

class OutputNotExistsError(Exception):
    """
    Raised when trying to create an output which doesn't exist.
    """
    pass