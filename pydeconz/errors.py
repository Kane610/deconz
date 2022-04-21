"""deCONZ errors."""


from typing import Any


class pydeconzException(Exception):
    """Base error for pydeconz.

    https://dresden-elektronik.github.io/deconz-rest-doc/errors/
    """


class BadRequest(pydeconzException):
    """The request was not formatted as expected or missing parameters."""


class BridgeBusy(pydeconzException):
    """The Bridge is busy, too many requests (more than 20)."""


class Forbidden(pydeconzException):
    """The caller has no rights to access the requested URI."""


class LinkButtonNotPressed(pydeconzException):
    """The Link button has not been pressed."""


class NotConnected(pydeconzException):
    """The Hardware is not connected."""


class RequestError(pydeconzException):
    """Unable to fulfill request.

    Raised when host or API cannot be reached.
    """


class ResourceNotFound(pydeconzException):
    """The requested resource (light, group, ...) was not found."""


class ResponseError(pydeconzException):
    """Invalid response."""


class Unauthorized(pydeconzException):
    """Authorization failed."""


ERRORS = {
    1: Unauthorized,  # Unauthorized user
    2: BadRequest,  # Body contains invalid JSON
    3: ResourceNotFound,  # Resource not available
    4: RequestError,  # Method not available for resource
    5: BadRequest,  # Missing parameters in body
    6: RequestError,  # Parameter not available
    7: RequestError,  # Invalid value for parameter
    8: RequestError,  # Parameter is not modifiable
    101: LinkButtonNotPressed,  # Link button not pressed
    901: BridgeBusy,  # May occur when sending too fast
    950: NotConnected,  # Hardware is not connected
    951: BridgeBusy,  # May occur when sending too fast
}


def raise_error(error: dict[str, Any]) -> None:
    """Raise error."""
    if error:
        if cls := ERRORS.get(error["type"]):
            raise cls(
                "{} {} {}".format(
                    error["type"],
                    error["address"],
                    error["description"],
                )
            )
        raise pydeconzException(error)
