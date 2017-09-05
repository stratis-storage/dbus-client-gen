"""
Test generation of class for invoking dbus methods.
"""

import os
import unittest

import xml.etree.ElementTree as ET

from dbus_client_gen import mo_query_builder
from dbus_client_gen import managed_object_class

from dbus_client_gen._errors import DbusClientRuntimeError


class TestCase(unittest.TestCase):
    """
    Test the behavior of various auto-generated classes
    """

    _DIRNAME = os.path.dirname(__file__)

    def setUp(self):
        """
        Read introspection data.
        """
        self._data = dict()
        datadir = os.path.join(self._DIRNAME, "data")
        for name in os.listdir(datadir):
            if name[-4:] != '.xml':
                continue
            path = os.path.join(datadir, name)
            with open(path) as opath:
                self._data[name] = ET.fromstring("".join(opath.readlines()))


    def testGMOReader(self):
        """
        Test that GMO reader from interface spec has the correct methods.

        Verify that empty table for an object always raises an exception.
        """
        for name, spec in self._data.items():
            klass = managed_object_class(name, spec)
            for prop in spec.findall("./property"):
                name = prop.attrib['name']
                self.assertTrue(hasattr(klass, name))
                table = {spec.attrib['name']: {name: "tank"}}
                obj = klass(table)
                self.assertTrue(hasattr(obj, name))
                self.assertEqual(getattr(obj, name)(), "tank")
            with self.assertRaises(DbusClientRuntimeError):
                klass(dict())

    def testGMOQuery(self):
        """
        Test that gmo query builder returns a thing for an interface.
        """
        for spec in self._data.values():
            query = mo_query_builder(spec)

            with self.assertRaises(DbusClientRuntimeError):
                list(query(dict(), {"bogus": None}))

            properties = [p.attrib['name'] for p in spec.findall("./property")]
            name = spec.attrib['name']
            table = {
               'junk': {name: dict((k, None) for k in properties)},
               'other': {"interface": dict()},
               'nomatch': {name: dict((k, 2) for k in properties)},
            }

            if properties:
                self.assertEqual(
                   len(list(query(table, dict((k, None) for k in properties)))),
                   1
                )
                with self.assertRaises(DbusClientRuntimeError):
                    table = {"junk": {name: dict()}}
                    list(query(table, dict((k, None) for k in properties)))
            else:
                self.assertEqual(
                   len(list(query(table, dict((k, None) for k in properties)))),
                   2
                )
