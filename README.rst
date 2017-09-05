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
