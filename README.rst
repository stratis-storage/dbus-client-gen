A Python Library for Generating D-Bus Client Code
=================================================

Introduction
------------
This library contains a few methods that consume an XML specification of
a D-Bus interface and return classes or functions that may be useful in
constructing a python D-Bus client. The XML specification has the
format of the data returned by the Introspect() method of the Introspectable
interface.

Methods
-------

managed_object_class
^^^^^^^^^^^^^^^^^^^^
  This function consumes the spec for a single interface and returns a class
  which constructs objects which wrap the table for a particular object in the
  format returned by the GetManagedObjects() method of the ObjectManager
  interface. Each object has an instance method for each property of the
  interface.

mo_query_builder
^^^^^^^^^^^^^^^^^
  This function consumes the spec for a single interface and returns a function
  which implements a query on the whole object returned by a GetManagedObjects()
  call. The query function takes two arguments: the GetManagedObjects() object
  and a dict of key/value pairs. The query function generates pairs of the
  object path and corresponding table which match all the key/value pairs in
  the table.


Errors
------
This library exports the exception type  DbusClientError and all its subtypes.
It constitutes a bug if an error of any other type is propagated during class
generation or when the methods of the class are executed.

The following shows the error heirarchy. Entries after the dash indicate
additional fields beyond the message which the exception contains. Only leaves
of the error class heirarchy are constructed directly.


DbusClientError

    * DbusClientGenerationError
      This exception is raised if an error occurs while generating a method.
      Such an exception would result from introspection data which lacked the
      necessary attributes or entries.

    * DbusClientRuntimeError - interface name
      This exception is raised if there is an error while the generated method
      is executing.

        - DbusClientMissingInterfaceError
          This exception is raisded if when constructing a managed object it
          turns out that its argument does not have an entry for the
          expected interface.

        - DbusClientMissingPropertyError - property name
          This exception is raised if when reading a value for a managed
          object it turns out that the value corresponding to that property
          is not available.

        - DbusClientMissingSearchPropertiesError - too many fields to list here
          This exception is raised if when traversing a GetManagedObjects()
          result the keys used by the query have no corresponding values in the
          result.

        - DbusClientUnknownSearchPropertiesError -- too many fields to list here
          This exception is raised if the search properties specified can not
          be found in the specified interface.
