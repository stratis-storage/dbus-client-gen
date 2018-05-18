# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Code for generating methods suitable for identifying objects in
the data structure returned by the GetManagedObjects() method.
"""

from ._errors import DbusClientGenerationError
from ._errors import DbusClientMissingSearchPropertiesError


def mo_query_builder(spec):
    """
    Returns a function that builds a query method for an interface.
    This method encapsulates the locating of various managed objects
    according to the interface specifications.

    :param spec: the specification of an interface
    :type spec: Element
    """

    try:
        interface_name = spec.attrib['name']
    except KeyError as err:  # pragma: no cover
        raise DbusClientGenerationError(
            "No name attribute found for interface.") from err

    def the_func(gmo, props=None):
        """
        Takes a list of key/value pairs representing properties
        and locates the corresponding objects which implement
        the designated interface for the spec.

        :param gmo: the result of a GetManagedObjects() call
        :param props: a specification of properties to restrict values
        :type props: dict of str * object or NoneType
        :returns: a list of pairs of object path/dict for the interface
        :rtype: list of tuple of ObjectPath * dict

        The function has conjunctive semantics, i.e., the object
        must match for every item in props to be returned.
        If props is None or an empty dict all objects that implement
        the designated interface are returned.

        :raises DbusClientMissingSearchPropertiesError:
        """
        props = dict() if props is None else props

        for (object_path, data) in gmo.items():
            if interface_name not in data:
                continue
            sub_table = data[interface_name]

            try:
                if all(sub_table[key] == value
                       for (key, value) in props.items()):
                    yield (object_path, data)
            except KeyError as err:
                fmt_str = ("Missing properties in data for object \"%s\" for "
                           "interface \"%s\": %s")
                missing = ", ".join(
                    str(x) for x in
                    frozenset(props.keys()) - frozenset(sub_table.keys()))
                raise DbusClientMissingSearchPropertiesError(
                    fmt_str % (object_path, interface_name, missing),
                    interface_name, object_path, [x for x in props.keys()],
                    [x for x in sub_table.keys()]) from err

    return the_func
