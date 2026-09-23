# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Top-level classes and methods.
"""

from ._errors import DbusClientError as DbusClientError
from ._errors import DbusClientGenerationError as DbusClientGenerationError
from ._errors import DbusClientMissingInterfaceError as DbusClientMissingInterfaceError
from ._errors import DbusClientMissingPropertyError as DbusClientMissingPropertyError
from ._errors import (
    DbusClientMissingSearchPropertiesError as DbusClientMissingSearchPropertiesError,
)
from ._errors import DbusClientRuntimeError as DbusClientRuntimeError
from ._errors import DbusClientSearchConditionError as DbusClientSearchConditionError
from ._errors import DbusClientUniqueResultError as DbusClientUniqueResultError
from ._errors import (
    DbusClientUnknownSearchPropertiesError as DbusClientUnknownSearchPropertiesError,
)
from ._managed_objects import managed_object_class as managed_object_class
from ._managed_objects_queries import GMOQuery as GMOQuery
from ._managed_objects_queries import mo_query_builder as mo_query_builder
from ._version import __version__ as __version__
