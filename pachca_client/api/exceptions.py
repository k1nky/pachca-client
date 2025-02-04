
class PachcaClientException(Exception):
    pass


class PachcaClientUnexpectedResponseException(PachcaClientException):
    pass


class PachcaClientBadRequestException(PachcaClientException):
    pass


class PachcaClientEntryNotFound(PachcaClientException):
    pass


class PachcaClientNotResolved(PachcaClientException):
    pass


class PachcaAlreadyExists(PachcaClientException):
    pass
