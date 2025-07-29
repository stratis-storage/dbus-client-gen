# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Deterministic testing of method generation and execution.
"""

# isort: STDLIB
import unittest
import xml.etree.ElementTree as ET  # nosec B405

# isort: LOCAL
from dbus_client_gen import GMOQuery, managed_object_class, mo_query_builder
from dbus_client_gen._errors import (
    DbusClientGenerationError,
    DbusClientUniqueResultError,
)


class DeterministicTestCase(unittest.TestCase):
    """
    Test some things more easily tested deterministically.
    """

    def test_malformed_data(self):
        """
        Pick up a key error on malformed introspection data. The introspection
        data is malformed because one of the attributes of the element should
        be its name.
        """
        with self.assertRaises(DbusClientGenerationError):
            managed_object_class("Fail", ET.Element("name", {}))
        with self.assertRaises(DbusClientGenerationError):
            mo_query_builder(ET.Element("name", {}))

    def test_unique_match(self):
        """
        Test successful unique match.
        """
        query = GMOQuery(
            "interface_name", {"prop_name": "prop_value"}
        ).require_unique_match()

        test_item = ("op", {"interface_name": {"prop_name": "prop_value"}})

        search_result = list(query.search({test_item[0]: test_item[1]}))
        self.assertEqual(len(search_result), 1)

        self.assertEqual(search_result[0], test_item)

    def test_unique_match_failure(self):
        """
        Fail to get the unique match because no match criterion provided.
        """
        with self.assertRaises(DbusClientUniqueResultError):
            GMOQuery(
                "interface_name", {"prop_name": "prop_value"}
            ).require_unique_match().search({})
