# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Top-level classes and methods.
"""

from ._errors import (
    DbusClientError,
    DbusClientGenerationError,
    DbusClientMissingInterfaceError,
    DbusClientMissingPropertyError,
    DbusClientMissingSearchPropertiesError,
    DbusClientRuntimeError,
    DbusClientSearchConditionError,
    DbusClientUniqueResultError,
    DbusClientUnknownSearchPropertiesError,
)
from ._managed_objects import managed_object_class
from ._managed_objects_queries import GMOQuery, mo_query_builder
from ._version import __version__
