# backend/app/services/errors.py


class ServiceError(Exception):
    pass


class NotFoundError(ServiceError):
    pass


class InvalidStateError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class SplitNotAllowedError(ServiceError):
    pass
