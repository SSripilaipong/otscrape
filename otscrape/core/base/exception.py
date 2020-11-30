class DropCommandException(Exception):
    pass


class LoaderNotAvailableException(Exception):
    pass


class LoadingFailedException(Exception):
    pass


class PoolWorkerFailedException(Exception):
    pass


class FatalException(Exception):
    pass


class InvalidPageStructureException(FatalException):
    pass


class StateOnWaitingException(Exception):
    pass
