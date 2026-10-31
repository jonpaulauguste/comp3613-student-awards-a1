"""Domain errors raised by services.

They subclass ``ValueError`` so the HTML routes can keep catching ``ValueError``
and flashing the message, while the JSON API maps each type to a status code.
"""


class DomainError(ValueError):
    status_code = 400


class InvalidInputError(DomainError):
    """The request breaks a business rule (e.g. zero hours, not enough points)."""

    status_code = 400


class PermissionDeniedError(DomainError):
    """The user is logged in but may not act on this resource."""

    status_code = 403


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    """The resource is in a state that does not allow the action."""

    status_code = 409
