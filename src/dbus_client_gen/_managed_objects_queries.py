# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Code for generating methods suitable for identifying objects in
the data structure returned by the GetManagedObjects() method.
"""

from ._errors import DbusClientGenerationError
from ._errors import DbusClientMissingSearchPropertiesError
from ._errors import DbusClientUnknownSearchPropertiesError


class GMOQuery(object):
    """
    Class that implements a query on the result of a D-Bus GetManagedObjects()
    call.
    """

    def __init__(self, filter_func):
        """
        Initialize the query with its function, which is run on a single
        entry in the GetManagedObjects result.
        """
        self._filter_func = filter_func

    def search(self, gmo_result):
        """
        Search a GetManagedObjects() result, generating any matches.

        :raises DbusClientMissingSearchPropertiesError:
        """
        return ((object_path, data)
                for (object_path, data) in gmo_result.items()
                if self._filter_func(data))

    # BOOLEAN OPERATORS
    # These operations are some of the more usual ones. Other operations can
    # easily be added as necessary. These operations contain the functionally
    # complete set of operations, {AND, NOT}, so will always be sufficient.

    def conjunction(self, other):
        """
        Compose self and other and return a new query which has the effect
        of a conjunction of self and other.
        """
        #pylint: disable=protected-access
        return GMOQuery(
            lambda item: self._filter_func(item) and other._filter_func(item))

    def disjunction(self, other):
        """
        Compose self and other and return a new query which has the effect
        of a disjunction of self and other.
        """
        #pylint: disable=protected-access
        return GMOQuery(
            lambda item: self._filter_func(item) or other._filter_func(item))

    def negation(self):
        """
        The negation of query.
        """
        return GMOQuery(lambda item: not self._filter_func(item))


def mo_query_builder(spec):
    """
    Returns a function that builds a GMOQuery object for an interface.

    :param spec: the specification of an interface
    :type spec: Element
    :returns: a function that builds a GMOQuery object
    :rtype: keywords -> GMOQuery
    """

    try:
        interface_name = spec.attrib['name']
    except KeyError as err:  # pragma: no cover
        raise DbusClientGenerationError(
            "No name attribute found for interface.") from err

    try:
        property_names = frozenset(
            p.attrib['name'] for p in spec.findall("./property"))
    except KeyError as err:  # pragma: no cover
        fmt_str = ("No name attribute found for some property belonging to "
                   "interface \"%s\"")
        raise DbusClientGenerationError(fmt_str % interface_name) from err

    def the_func(props=None):
        """
        Takes a list of key/value pairs representing properties
        and generates a GMOQuery object which implements the requested search.

        :param props: a specification of properties to restrict values
        :type props: dict of str * object or NoneType
        :returns: an appropriately constructed GMOQuery object
        :rtype: GMOQuery

        """
        props = dict() if props is None else props

        if not frozenset(props.keys()) <= property_names:
            fmt_str = (
                "These properties in the specified query are unknown to "
                "interface \"%s\": %s")
            unknown_properties = ", ".join(
                str(x) for x in frozenset(props.keys()) - property_names)
            raise DbusClientUnknownSearchPropertiesError(
                fmt_str % (interface_name, unknown_properties), interface_name,
                [key for key in props.keys()],
                [name for name in property_names])

        def filter_func(data):
            """
            Returns true if an item should be kept, false otherwise.

            :returns: true for acceptance, false for rejection
            :rtype: bool
            :raises DbusClientMissingSearchPropertiesError:
            """
            if interface_name not in data:
                return False
            sub_table = data[interface_name]

            try:
                return all(
                    sub_table[key] == value for (key, value) in props.items())
            except KeyError as err:
                fmt_str = ("Missing properties in data for some object in "
                           "interface \"%s\": %s")
                missing = ", ".join(
                    str(x) for x in
                    frozenset(props.keys()) - frozenset(sub_table.keys()))
                raise DbusClientMissingSearchPropertiesError(
                    fmt_str % (interface_name, missing), interface_name,
                    [x for x in props.keys()],
                    [x for x in sub_table.keys()]) from err

        return GMOQuery(filter_func)

    return the_func
