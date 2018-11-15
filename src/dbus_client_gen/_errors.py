# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Exception hierarchy for this package.
"""


class DbusClientError(Exception):
    """
    Top-level error.
    """
    pass


class DbusClientGenerationError(DbusClientError):
    """
    Exception during generation of classes.
    """
    pass


class DbusClientRuntimeError(DbusClientError):
    """
    Exception raised during execution of generated classes.
    """

    def __init__(self, message, interface_name):
        """
        Initialize with a message and an interface name.

        :param str message: the error message
        :param str interface_name: the interface name
        """
        super(DbusClientRuntimeError, self).__init__(message)
        self.interface_name = interface_name


class DbusClientMissingSearchPropertiesError(DbusClientRuntimeError):
    """
    Exception returned when searching GMO result finds expected properties
    missing.
    """

    def __init__(self, message, interface_name, query_keys, data_keys):
        """
        Initialize exception.

        :param str message: the error message
        :param str interface_name: the interface name
        :param query_keys: names of properties used in query
        :type query_keys: list of str
        :param data_keys: the keys actually available in the data
        :type data_keys: list of str
        """
        super(DbusClientMissingSearchPropertiesError, self).__init__(
            message, interface_name)
        self.query_keys = query_keys
        self.data_keys = data_keys


class DbusClientUnknownSearchPropertiesError(DbusClientRuntimeError):
    """
    Exception returned when a query is specified with a property that is
    not found in the given interface.
    """

    def __init__(self, message, interface_name, specified, allowed):
        """
        Initialize exception.

        :param str message: the error message
        :param str interface_name: the interface name
        :param specified: the specified keys
        :type specified: list of str
        :param allowed: the allowed keys
        :type allowed: list of str
        """
        super(DbusClientUnknownSearchPropertiesError, self).__init__(
            message, interface_name)
        self.specified = specified
        self.allowed = allowed


class DbusClientMissingPropertyError(
        DbusClientRuntimeError):  # pragma: no cover
    """
    Exception returned when GMO data does not contain the property name.
    """

    def __init__(self, message, interface_name, property_name):
        """
        Initialize exception.

        :param str message: the error message
        :param str interface_name: the interface name
        :param str property_name: the name of the property to look up
        """
        super(DbusClientMissingPropertyError, self).__init__(
            message, interface_name)
        self.property_name = property_name


class DbusClientMissingInterfaceError(DbusClientRuntimeError):
    """
    Exception returned when GMO data does not contain the interface name.
    """

    def __init__(self, message, interface_name):
        """
        Initialize exception.

        :param str message: the error message
        :param str interface_name: the interface name
        """
        # Note that if this is not disabled, pylint complains about
        # super-init-not-called instead.
        # pylint: disable=useless-super-delegation
        super(DbusClientMissingInterfaceError, self).__init__(
            message, interface_name)


class DbusClientSearchConditionError(DbusClientRuntimeError):
    """
    Exception raised when the search result does not match specified
    requirements.
    """

    def __init__(self, message, interface_name):
        """
        Initialize exception.

        :param str message: the error message
        :param str interface_name: the interface name
        """
        # Note that if this is not disabled, pylint complains about
        # super-init-not-called instead.
        # pylint: disable=useless-super-delegation
        super(DbusClientSearchConditionError, self).__init__(
            message, interface_name)


class DbusClientUniqueResultError(DbusClientSearchConditionError):
    """
    Exception raised when the search result does not yield a unique item.
    """

    def __init__(self, message, interface_name, props, result):
        """
        Initialize exception.

        :param str message: the error message
        :param str interface_name: the interface name
        :param dict props: the list of properties for this interface to match
        :param list result: the list of objects found via the search string
        """
        super(DbusClientUniqueResultError, self).__init__(
            message, interface_name)
        self.props = props
        self.result = result
