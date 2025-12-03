
class ApiNotSupportedException(Exception):
    pass


class AccessDeniedException(Exception):
    pass


class MissingApiKeyException(Exception):
    pass


class BadApiKeyException(Exception):
    pass


class RateLimitException(Exception):
    pass
