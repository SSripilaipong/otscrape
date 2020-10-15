class DropCommandException(Exception):
    pass


class LoaderNotAvailableException(Exception):
    pass


class FatalException(Exception):
    pass


class InvalidPageStructureException(FatalException):
    pass
