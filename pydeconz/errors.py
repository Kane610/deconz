"""deCONZ errors."""


class pydeconzException(Exception):
    """Base error for pydeconz.

    https://dresden-elektronik.github.io/deconz-rest-doc/errors/
    """


class RequestError(pydeconzException):
    """Unable to fulfill request.

    Raised when host or API cannot be reached.
    """


class ResponseError(pydeconzException):
    """Invalid response."""


class Unauthorized(pydeconzException):
    """Authorization failed."""


class BadRequest(pydeconzException):
    """The request was not formatted as expected or missing parameters."""


class Forbidden(pydeconzException):
    """The caller has no rights to access the requested URI."""


class ResourceNotFound(pydeconzException):
    """The requested resource (light, group, ...) was not found."""


ERRORS = {
    1: Unauthorized,  # Unauthorized user
    2: BadRequest,  # Body contains invalid JSON
    3: ResourceNotFound,  # Resource not available
    4: RequestError,  # Method not available for resource
    5: BadRequest,  # Missing parameters in body
    6: RequestError,  # Parameter not available
    7: RequestError,  # Invalid value for parameter
    8: RequestError,  # Parameter is not modifiable
}


def raise_error(error):
    if error:
        cls = ERRORS.get(error['type'], pydeconzException)
        raise cls("{} {}".format(error['address'], error['description']))
