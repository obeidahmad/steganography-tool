class IncorrectFileTypeException(Exception):
    """Raised when the file type (extension) is incorrect"""
    pass


class DataTooLongException(Exception):
    """Raised when stego data is bigger than max capacity"""
    pass


class MissingParameterException(Exception):
    """Raised when a usually optional parameter is needed but not available"""
    pass
