"""
D-Bus introspection data strategy.
"""

# pylint: disable=fixme
# TODO: When this strategy is fully mature, port it to a separate library.
# It is correct according to the dtd, except that attributes intended to be
# D-Bus signatures supply only a valid D-Bus signature, rather than arbitrary
# CDATA.

from abc import ABC
from abc import abstractmethod

import string

import xml.etree.ElementTree as ET

from hypothesis.strategies import builds
from hypothesis.strategies import fixed_dictionaries
from hypothesis.strategies import just
from hypothesis.strategies import one_of
from hypothesis.strategies import recursive
from hypothesis.strategies import sampled_from
from hypothesis.strategies import sets
from hypothesis.strategies import text

from hs_dbus_signature import dbus_signatures

_TEXT_SET = string.ascii_letters + string.digits + string.punctuation
_TEXT_STRATEGY = text(_TEXT_SET, min_size=1)


class XMLElement(ABC):
    """
    An abstract class with a method for generating an element from its data.
    """

    def __init__(self, attrs, children):
        """
        Initializer.

        :param dict attrs: a dict of attributes
        :param set children: a set of children XMLElements
        """
        self.attrs = attrs
        self.children = children

    def element(self):
        """
        Generates an XML element from the data.

        :return: XML element
        :rtype: ET.Element
        """
        elt = ET.Element(self.name(), self.attrs)
        elt.extend(child.element() for child in self.children)
        return elt

    @abstractmethod
    def name(self):
        """
        Method which returns the tag for this class.
        """
        pass


class Annotation(XMLElement):
    """
    Class representing an annotation in the introspect dtd.
    """

    def name(self):
        return "annotation"


class Arg(XMLElement):
    """
    Class representing an arg in the introspect dtd.
    """

    @classmethod
    def name(cls):
        return "arg"


class Interface(XMLElement):
    """
    Class representing an interface in the introspect dtd.
    """

    @classmethod
    def name(cls):
        return "interface"


class Method(XMLElement):
    """
    Class representing a method in the introspect dtd.
    """

    @classmethod
    def name(cls):
        return "method"


class Node(XMLElement):
    """
    Class representing a node in the introspect dtd.
    """

    def name(self):
        return "node"


class Property(XMLElement):
    """
    Class representing a property in the introspect dtd.
    """

    @classmethod
    def name(cls):
        return "property"


class Signal(XMLElement):
    """
    Class representing a signal in the introspect dtd.
    """

    @classmethod
    def name(cls):
        return "signal"


def annotation_strategy():
    """
    Build a strategy to generate data for an introspection annotation.
    """
    return builds(Annotation,
                  fixed_dictionaries({
                      'name': _TEXT_STRATEGY,
                      'value': _TEXT_STRATEGY
                  }), just(frozenset()))


def arg_strategy():
    """
    Build a strategy to generate data for an introspection arg.
    """
    return builds(Arg,
                  fixed_dictionaries({
                      'name': _TEXT_STRATEGY,
                      'type': dbus_signatures(),
                      'direction': sampled_from(["in", "out"])
                  }), sets(annotation_strategy()))


def interface_strategy(*, min_children=None, max_children=None):
    """
    Build a strategy to generate data for an introspection interface.

    :param min_children: the minimum number of child elements in this interface
    :type min_children: non-negative int or None
    :param max_children: the maximum number of child elements in this interface
    :type max_children: non-negative int or None
    """
    return builds(Interface, fixed_dictionaries({
        'name': _TEXT_STRATEGY,
    }),
                  sets(
                      one_of(property_strategy(), method_strategy(),
                             annotation_strategy(), signal_strategy()),
                      min_size=min_children,
                      max_size=max_children))


def method_strategy():
    """
    Build a strategy to generate data for an introspection method.
    """
    return builds(Method, fixed_dictionaries({
        'name': _TEXT_STRATEGY,
    }), sets(one_of(arg_strategy(), annotation_strategy())))


def _node_function(strat):
    return builds(Node, fixed_dictionaries({
        'name': _TEXT_STRATEGY
    }), sets(strat))


def node_strategy():
    """
    Build a strategy to generate data for an introspection node.
    """
    return recursive(interface_strategy(), _node_function)


def property_strategy():
    """
    Build a strategy to generate data for an introspection property.
    """
    return builds(Property,
                  fixed_dictionaries({
                      'name':
                      _TEXT_STRATEGY,
                      'type':
                      dbus_signatures(),
                      'access':
                      sampled_from(["read", "write", "readwrite"])
                  }), sets(annotation_strategy()))


def signal_arg_strategy():
    """
    Build a strategy to generate data for an introspection arg for signals.
    """
    return builds(Arg,
                  fixed_dictionaries({
                      'name': _TEXT_STRATEGY,
                      'type': dbus_signatures(),
                  }), sets(annotation_strategy()))


def signal_strategy():
    """
    Build a strategy to generate data for an introspection signal.
    """
    return builds(Signal, fixed_dictionaries({
        'name': _TEXT_STRATEGY
    }), sets(one_of(signal_arg_strategy(), annotation_strategy())))
