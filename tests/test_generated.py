"""
Test generation of class for invoking dbus methods.
"""

from os import environ
from os import sys
import random
import unittest

from hypothesis import given
from hypothesis import settings
from hypothesis import HealthCheck

from dbus_client_gen import mo_query_builder
from dbus_client_gen import managed_object_class

from dbus_client_gen._errors import DbusClientMissingInterfaceError
from dbus_client_gen._errors import DbusClientMissingPropertyError
from dbus_client_gen._errors import DbusClientMissingSearchPropertiesError
from dbus_client_gen._errors import DbusClientUniqueResultError
from dbus_client_gen._errors import DbusClientUnknownSearchPropertiesError

from ._introspect import interface_strategy

settings.register_profile("tracing", deadline=None)
if sys.gettrace() is not None or environ.get("TRAVIS") is not None:
    settings.load_profile("tracing")


class TestCase(unittest.TestCase):
    """
    Test the behavior of various auto-generated classes
    """

    @given(interface_strategy(max_children=30).map(lambda x: x.element()))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_managed_object(self, spec):
        """
        Test that the GMO object has the correct set of methods.

        Test that there is an exception if the table is missing its interface.

        Test that there is an exception if the subtable is missing an entry.
        """
        interface_name = spec.attrib["name"]
        klass = managed_object_class(interface_name, spec)
        property_names = [p.attrib["name"] for p in spec.findall("./property")]
        self.assertTrue(all(hasattr(klass, name) for name in property_names))

        with self.assertRaises(DbusClientMissingInterfaceError):
            klass({interface_name + "x": {}})

        table = {
            interface_name: dict(
                (name, random.randint(0, len(property_names)))
                for name in property_names
            )
        }
        table_interface = table[interface_name]
        obj = klass(table)
        self.assertTrue(
            all(
                getattr(obj, name)() == value
                for (name, value) in table_interface.items()
            )
        )

        if table_interface != dict():
            remove_name = random.choice(list(table_interface))
            del table_interface[remove_name]
            with self.assertRaises(DbusClientMissingPropertyError):
                getattr(obj, remove_name)()

    @given(interface_strategy(max_children=30).map(lambda x: x.element()))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def test_managed_object_query(self, spec):
        """
        Test that the query returns appropriate values for its query input.
        """
        query = mo_query_builder(spec)

        bad = {"bogus": None}
        with self.assertRaises(DbusClientUnknownSearchPropertiesError) as context:
            query(bad)
        exception = context.exception
        self.assertEqual(frozenset(exception.specified), frozenset(bad.keys()))

        properties = [p.attrib["name"] for p in spec.findall("./property")]
        name = spec.attrib["name"]
        table = {
            "junk": {name: dict((k, None) for k in properties)},
            "other": {"interface": dict()},
            "nomatch": {name: dict((k, 2) for k in properties)},
        }

        query_object = query(dict((k, None) for k in properties))
        result = list(query_object.search(table))
        if properties != []:
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0][0], "junk")

            result = query_object.require_unique_match().search(table)
            self.assertEqual(len(list(result)), 1)

            with self.assertRaises(DbusClientMissingSearchPropertiesError):
                table = {"junk": {name: dict()}}
                list(query(dict((k, None) for k in properties)).search(table))

        else:
            self.assertEqual(len(result), 2)
            self.assertEqual(
                frozenset(x[0] for x in result), frozenset(["junk", "nomatch"])
            )

            with self.assertRaises(DbusClientUniqueResultError):
                query_object.require_unique_match().search(table)
