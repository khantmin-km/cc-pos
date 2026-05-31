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


class UnauthorizedError(ServiceError):
    pass


class ModifierValidationError(ConflictError):
    def __init__(self, details: list[dict], message: str = "Modifier validation failed"):
        super().__init__(message)
        self.code = "MODIFIER_VALIDATION_FAILED"
        self.message = message
        self.details = details
