# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Top-level classes and methods.
"""

from ._errors import DbusClientError
from ._errors import DbusClientGenerationError
from ._errors import DbusClientMissingInterfaceError
from ._errors import DbusClientMissingPropertyError
from ._errors import DbusClientMissingSearchPropertiesError
from ._errors import DbusClientRuntimeError
from ._errors import DbusClientSearchConditionError
from ._errors import DbusClientUnknownSearchPropertiesError
from ._errors import DbusClientUniqueResultError

from ._managed_objects import managed_object_class
from ._managed_objects_queries import mo_query_builder
from ._managed_objects_queries import GMOQuery
