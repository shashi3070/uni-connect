class UniConnectError(Exception):
    pass


class ConfigurationError(UniConnectError):
    pass


class ConnectionError(UniConnectError):
    pass


class AuthenticationError(ConnectionError):
    pass


class NotSupportedError(UniConnectError):
    pass


class DriverNotFoundError(ConfigurationError):
    pass


class HealthCheckError(ConnectionError):
    pass
