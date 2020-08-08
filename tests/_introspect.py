"""
D-Bus introspection data strategy.
"""

# pylint: disable=fixme
# TODO: When this strategy is fully mature, port it to a separate library.
# It is correct according to the dtd, except that attributes intended to be
# D-Bus signatures supply only a valid D-Bus signature, rather than arbitrary
# CDATA.

# isort: STDLIB
import string
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

# isort: THIRDPARTY
from hypothesis.strategies import (
    builds,
    fixed_dictionaries,
    frozensets,
    just,
    recursive,
    sampled_from,
    text,
)

# isort: FIRSTPARTY
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
    return builds(
        Annotation,
        fixed_dictionaries({"name": _TEXT_STRATEGY, "value": _TEXT_STRATEGY}),
        just(frozenset()),
    )


def arg_strategy(*, min_children=0, max_children=None):
    """
    Build a strategy to generate data for an introspection arg.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None
    """
    return builds(
        Arg,
        fixed_dictionaries(
            {
                "name": _TEXT_STRATEGY,
                "type": dbus_signatures(),
                "direction": sampled_from(["in", "out"]),
            }
        ),
        frozensets(annotation_strategy(), min_size=min_children, max_size=max_children),
    )


def interface_strategy(*, min_children=0, max_children=None):
    """
    Build a strategy to generate data for an introspection interface.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None

    min_children and max_children are passed to component element strategies.
    """
    return builds(
        Interface,
        fixed_dictionaries({"name": _TEXT_STRATEGY}),
        frozensets(
            annotation_strategy()
            | property_strategy(min_children=min_children, max_children=max_children)
            | method_strategy(min_children=min_children, max_children=max_children)
            | signal_strategy(min_children=min_children, max_children=max_children),
            min_size=min_children,
            max_size=max_children,
        ),
    )


def method_strategy(*, min_children=0, max_children=None):
    """
    Build a strategy to generate data for an introspection method.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None

    min_children and max_children are passed to component element strategies.
    """
    return builds(
        Method,
        fixed_dictionaries({"name": _TEXT_STRATEGY}),
        frozensets(
            annotation_strategy()
            | arg_strategy(min_children=min_children, max_children=max_children),
            min_size=min_children,
            max_size=max_children,
        ),
    )


def _node_function(strat):
    return builds(Node, fixed_dictionaries({"name": _TEXT_STRATEGY}), frozensets(strat))


def node_strategy():
    """
    Build a strategy to generate data for an introspection node.
    """
    return recursive(interface_strategy(), _node_function)


def property_strategy(*, min_children=0, max_children=None):
    """
    Build a strategy to generate data for an introspection property.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None
    """
    return builds(
        Property,
        fixed_dictionaries(
            {
                "name": _TEXT_STRATEGY,
                "type": dbus_signatures(),
                "access": sampled_from(["read", "write", "readwrite"]),
            }
        ),
        frozensets(annotation_strategy(), min_size=min_children, max_size=max_children),
    )


def signal_arg_strategy(*, min_children=0, max_children=None):
    """
    Build a strategy to generate data for an introspection arg for signals.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None
    """
    return builds(
        Arg,
        fixed_dictionaries({"name": _TEXT_STRATEGY, "type": dbus_signatures()}),
        frozensets(annotation_strategy(), min_size=min_children, max_size=max_children),
    )


def signal_strategy(*, min_children=0, max_children=None):
    """
    Build a strategy to generate data for an introspection signal.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None

    min_children and max_children are passed to component element strategies.
    """
    return builds(
        Signal,
        fixed_dictionaries({"name": _TEXT_STRATEGY}),
        frozensets(
            annotation_strategy()
            | signal_arg_strategy(min_children=min_children, max_children=max_children),
            min_size=min_children,
            max_size=max_children,
        ),
    )
