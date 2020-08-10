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
    composite,
    fixed_dictionaries,
    frozensets,
    just,
    sampled_from,
    text,
)

# isort: FIRSTPARTY
from hs_dbus_signature import dbus_signatures

_TEXT_SET = string.ascii_letters + string.digits + string.punctuation
_TEXT_STRATEGY = text(_TEXT_SET, min_size=1, max_size=10)


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


def arg_strategy(*, min_children=0, max_children=None, dbus_signature_args=None):
    """
    Build a strategy to generate data for an introspection arg.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None
    :param dbus_signature_args: to override dbus_signatures defaults
    :type dbus_signature_args: dict of str * object or NoneType
    """
    return builds(
        Arg,
        fixed_dictionaries(
            {
                "name": _TEXT_STRATEGY,
                "type": dbus_signatures(
                    **({} if dbus_signature_args is None else dbus_signature_args)
                ),
                "direction": sampled_from(["in", "out"]),
            }
        ),
        frozensets(annotation_strategy(), min_size=min_children, max_size=max_children),
    )


@composite
def interface_strategy(  # pylint: disable=too-many-locals
    # pylint: disable=bad-continuation
    draw,
    *,
    min_children=0,
    max_children=None,
    min_annotations=0,
    max_annotations=None,
    min_methods=0,
    max_methods=None,
    min_properties=0,
    max_properties=None,
    min_signals=0,
    max_signals=None,
    dbus_signature_args=None,
):
    """
    Build a strategy to generate data for an introspection interface.

    :param min_children: minimum value for component strategies
    :type min_children: non-negative int
    :param max_children: maximum value for component strategies
    :type max_children: non-negative int or None
    :param min annotations: minimum number of annotations
    :type max_annotations: non-negative int
    :param max_annotations: maximum number of annotations
    :type max_annotations: non-negative int or None
    :param min methods: minimum number of methods
    :type max_methods: non-negative int
    :param max_methods: maximum number of methods
    :type max_methods: non-negative int or None
    :param min properties: minimum number of properties
    :type max_properties: non-negative int
    :param max_properties: maximum number of properties
    :type max_properties: non-negative int or None
    :param min signals: minimum number of signals
    :type max_signals: non-negative int
    :param max_signals: maximum number of signals
    :type max_signals: non-negative int or None
    :param dbus_signature_args: to override dbus_signatures defaults
    :type dbus_signature_args: dict of str * object or NoneType
    """
    annotations = draw(
        frozensets(
            annotation_strategy(), min_size=min_annotations, max_size=max_annotations
        )
    )
    methods = draw(
        frozensets(
            method_strategy(  # pylint: disable=no-value-for-parameter
                min_children=min_children,
                max_children=max_children,
                min_annotations=min_children,
                max_annotations=max_children,
                min_args=min_children,
                max_args=max_children,
                dbus_signature_args=dbus_signature_args,
            ),
            min_size=min_methods,
            max_size=max_methods,
        )
    )
    properties = draw(
        frozensets(
            property_strategy(
                min_children=min_children,
                max_children=max_children,
                dbus_signature_args=dbus_signature_args,
            ),
            min_size=min_properties,
            max_size=max_properties,
        )
    )
    signals = draw(
        frozensets(
            signal_strategy(  # pylint: disable=no-value-for-parameter
                min_children=min_children,
                max_children=max_children,
                min_annotations=min_children,
                max_annotations=max_children,
                min_signal_args=min_children,
                max_signal_args=max_children,
                dbus_signature_args=dbus_signature_args,
            ),
            min_size=min_signals,
            max_size=max_signals,
        )
    )
    attrs = draw(fixed_dictionaries({"name": _TEXT_STRATEGY}))

    return Interface(attrs, annotations | methods | properties | signals)


@composite
def method_strategy(
    # pylint: disable=bad-continuation
    draw,
    *,
    min_children=0,
    max_children=None,
    min_annotations=0,
    max_annotations=None,
    min_args=0,
    max_args=None,
    dbus_signature_args=None,
):
    """
    Build a strategy to generate data for an introspection method.

    :param min_children: min argument passed to component strategies
    :type min_children: non-negative int
    :param max_children: max argument passed to component strategies
    :type max_children: non-negative int or None
    :param min_annotations: the minimum number of annotation elements
    :type min_annotations: non-negative int
    :param max_annotations: the maximum number of annotation elements
    :type max_annotations: non-negative int or None
    :param min_args: the minimum number of arg elements
    :type min_args: non-negative int
    :param max_args: the maximum number of arg elements
    :type max_args: non-negative int or None
    :param dbus_signature_args: to override dbus_signatures defaults
    :type dbus_signature_args: dict of str * object or NoneType

    min_children and max_children are passed to component element strategies.
    """
    annotations = draw(
        frozensets(
            annotation_strategy(), min_size=min_annotations, max_size=max_annotations
        )
    )
    args = draw(
        frozensets(
            arg_strategy(
                min_children=min_children,
                max_children=max_children,
                dbus_signature_args=dbus_signature_args,
            ),
            min_size=min_args,
            max_size=max_args,
        )
    )
    attrs = draw(fixed_dictionaries({"name": _TEXT_STRATEGY}))

    return Method(attrs, annotations | args)


def property_strategy(*, min_children=0, max_children=None, dbus_signature_args=None):
    """
    Build a strategy to generate data for an introspection property.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None
    :param dbus_signature_args: to override dbus_signatures defaults
    :type dbus_signature_args: dict of str * object or NoneType
    """
    return builds(
        Property,
        fixed_dictionaries(
            {
                "name": _TEXT_STRATEGY,
                "type": dbus_signatures(
                    **({} if dbus_signature_args is None else dbus_signature_args)
                ),
                "access": sampled_from(["read", "write", "readwrite"]),
            }
        ),
        frozensets(annotation_strategy(), min_size=min_children, max_size=max_children),
    )


def signal_arg_strategy(*, min_children=0, max_children=None, dbus_signature_args=None):
    """
    Build a strategy to generate data for an introspection arg for signals.

    :param min_children: the minimum number of child elements
    :type min_children: non-negative int
    :param max_children: the maximum number of child elements
    :type max_children: non-negative int or None
    :param dbus_signature_args: to override dbus_signatures defaults
    :type dbus_signature_args: dict of str * object or NoneType
    """
    return builds(
        Arg,
        fixed_dictionaries(
            {
                "name": _TEXT_STRATEGY,
                "type": dbus_signatures(
                    **({} if dbus_signature_args is None else dbus_signature_args)
                ),
            }
        ),
        frozensets(annotation_strategy(), min_size=min_children, max_size=max_children),
    )


@composite
def signal_strategy(
    # pylint: disable=bad-continuation
    draw,
    *,
    min_children=0,
    max_children=None,
    min_annotations=0,
    max_annotations=None,
    min_signal_args=0,
    max_signal_args=None,
    dbus_signature_args=None,
):
    """
    Build a strategy to generate data for an introspection signal.

    :param min_children: min argument passed to component strategies
    :type min_children: non-negative int
    :param max_children: max argument passed to component strategies
    :type max_children: non-negative int or None
    :param min_annotations: the minimum number of annotation elements
    :type min_annotations: non-negative int
    :param max_annotations: the maximum number of annotation elements
    :type max_annotations: non-negative int or None
    :param min_signal_args: the minimum number of signal_arg elements
    :type min_signal_args: non-negative int
    :param max_signal_args: the maximum number of signal_arg elements
    :type max_signal_args: non-negative int or None
    :param dbus_signature_args: to override dbus_signatures defaults
    :type dbus_signature_args: dict of str * object or NoneType
    """
    annotations = draw(
        frozensets(
            annotation_strategy(), min_size=min_annotations, max_size=max_annotations
        )
    )
    signal_args = draw(
        frozensets(
            signal_arg_strategy(
                min_children=min_children,
                max_children=max_children,
                dbus_signature_args=dbus_signature_args,
            ),
            min_size=min_signal_args,
            max_size=max_signal_args,
        )
    )
    attrs = draw(fixed_dictionaries({"name": _TEXT_STRATEGY}))

    return Signal(attrs, annotations | signal_args)
