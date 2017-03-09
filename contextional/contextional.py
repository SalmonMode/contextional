from __future__ import (
    absolute_import,
    with_statement,
)
import unittest
import inspect
from random import getrandbits
from contextlib import contextmanager
from copy import deepcopy
from types import FunctionType


class Helper(unittest.TestCase):
    """A singleton used to keep objects persistent during test execution.

    Most, if not all objects that have the Helper instance as an attribute will
    have custom __getattr__, __setattr__, and __delattr__ methods that defer
    most attribute requests to this helper to enure that they have access to
    the `unittest.TestCase` assert methods and any objects that the helper is
    holding.
    """

    def __init__(self):
        self._level_stack = []
        self._cases = []

    def _get_test_count(self):
        """The number of test cases created at the current moment."""
        return len(self._cases)

    def _set_teardown_level_for_last_case(self, level):
        """Set the teardown level of the last test case that was created."""
        self._cases[-1]._teardown_level = level

    def _add_case(self, case):
        """Add a test case to the queue."""
        self._cases.append(case)

    def _get_next_test(self):
        """Get the next test from the queue."""
        try:
            return self._cases.pop(0)
        except IndexError:
            raise IndexError("more test classes than test cases")

    def runTest(self):
        pass


helper = Helper()


class GroupContextManager(object):
    """A manager for groups, and their fixtures, child groups, and tests.

    A group manager is used to handle constructing groups, and their fixtures,
    child groups, and tests through the various decorators it provides.
    """
    _helper = helper

    def __init__(self, description):
        self._group = Group(description)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is None:
            return True

    def __getattr__(self, attr):
        """Defer attribute lookups to helper."""
        return getattr(self._helper, attr)

    def __setattr__(self, attr, value):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys() or attr == "_group":
            super(GroupContextManager, self).__setattr__(attr, value)
        else:
            setattr(self._helper, attr, value)

    def __delattr__(self, attr):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys() or attr == "_group":
            super(GroupContextManager, self).__delattr__(attr)
        else:
            delattr(self._helper, attr)

    def add_test(self, func):

        if isinstance(func, FunctionType):
            desc = func.__doc__
        else:
            desc = func

        def decorator(f):
            case = Case(self._group, f, desc)
            self._group._cases.append(case)

        if isinstance(func, FunctionType):
            decorator(func)
        else:
            return decorator

    @contextmanager
    def add_group(self, description):
        last_group = self._group
        self._group = last_group._add_child(description)
        yield self
        self._group = last_group

    def add_setup(self, func):
        self._group._setups.append(func)

    def add_test_setup(self, func):
        self._group._test_setups.append(func)

    def add_teardown(self, func):
        self._group._teardowns.append(func)

    def add_test_teardown(self, func):
        self._group._test_teardowns.append(func)

    def includes(self, context):
        if not isinstance(context, GroupContextManager):
            raise TypeError("method only accepts GroupContextManager objects")
        group_copy = deepcopy(context._group)
        group_copy._parent = self._group
        self._group._children.append(group_copy)

    def create_tests(self, mod):
        self._group._build_test_cases(mod)


class GroupTestCase(object):
    """The base test class for a Group.

    All Groups will have to create a class that represents each test for that
    Group. This should be the class those classes inherit from in order to
    ensure they all perform the necessary steps requied of them.
    """

    _helper = helper
    _root_group_hash = None
    _description = ""

    def __str__(self):
        return self._description

    def __getattr__(self, attr):
        """Defer attribute lookups to helper."""
        return getattr(self._helper, attr)

    def __setattr__(self, attr, value):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys():
            super(GroupTestCase, self).__setattr__(attr, value)
        else:
            setattr(self._helper, attr, value)

    def __delattr__(self, attr):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys():
            super(GroupTestCase, self).__delattr__(attr)
        else:
            delattr(self._helper, attr)

    @classmethod
    def _set_test_description(cls, setup_ancestry):
        """Set the test's description that will go to stdout.

        This may include the descriptions of a test's ancestor groups. For
        example, in the following output:

            Group A
                Group B
                    test 1 ... ok
                    test 2 ... ok
                Group C
                    test 3 ... ok

        `test 1`'s description is:

            Group A
                Group B
                    test 1

        `test 2`'s description is:

                    test 2

        and `test 3`'s description is:

                Group C
                    test 3
        """
        indent = "  "
        for group in setup_ancestry:
            indentation = (indent * group._level)
            level_description = group._description
            cls._description += "{}{}\n".format(
                indentation,
                level_description,
            )
        cls._description += "{}{}".format(
            (indent * (cls._group._level + 1)),
            cls._case._description,
        )

    def _set_test_failure_description(self):
        """Set the description of the test in case it fails.

        If a test fails, just having the test's name won't be very
        informative, so it should provide the test's ancestry.
        """
        ancestry = list(reversed(self._case._group._ancestry))
        ancestry_description = "".join(g._description for g in ancestry)
        test_description = self._case._description
        self._description = "{} ({})".format(
            test_description,
            ancestry_description,
        )

    @classmethod
    def setUpClass(cls):
        cls._case = cls._helper._get_next_test()
        cls._group = cls._case._group
        cls._teardown_level = cls._case._teardown_level
        stack_comp = zip(
            cls._helper._level_stack,
            list(reversed(cls._group._ancestry)),
        )
        branching_point = len(stack_comp)
        for i, level in enumerate(stack_comp):
            if level[0] == level[1]:
                continue
            else:
                branching_point = i
                break

        teardown_stack = list(reversed(
            cls._helper._level_stack[branching_point:],
        ))
        for group in teardown_stack:
            for teardown in group._teardowns:
                args, _, _, _ = inspect.getargspec(teardown)
                if args:
                    teardown(cls)
                else:
                    teardown()
            cls._helper._level_stack.remove(group)

        setup_ancestry = list(reversed(cls._group._ancestry))[branching_point:]

        cls._set_test_description(setup_ancestry)

        for group in setup_ancestry:
            for setup in group._setups:
                args, _, _, _ = inspect.getargspec(setup)
                if args:
                    setup(cls)
                else:
                    setup()
            cls._helper._level_stack.append(group)

    def setUp(self):
        self._set_test_failure_description()
        for setup in self._group._test_setups:
            args, _, _, _ = inspect.getargspec(setup)
            if args:
                setup(self)
            else:
                setup()

    def tearDown(self):
        for teardown in self._group._test_teardowns:
            args, _, _, _ = inspect.getargspec(teardown)
            if args:
                teardown(self)
            else:
                teardown()

    @classmethod
    def tearDownClass(cls):
        if cls._teardown_level is not None:
            stop_index = cls._group._ancestry.index(cls._teardown_level) + 1
            teardown_ancestry = cls._group._ancestry[:stop_index]
            for group in teardown_ancestry:
                for teardown in group._teardowns:
                    args, _, _, _ = inspect.getargspec(teardown)
                    if args:
                        teardown(cls)
                    else:
                        teardown()
                cls._helper._level_stack.remove(group)

    def runTest(self):
        self._case(self)


TEST_CLASS_NAME_TEMPLATE = "ContextionalCase_{}"


class Group(object):
    """A group of tests, with common fixtures and description"""

    _helper = helper

    def __init__(self, description, parent=None):
        self._description = description
        self._parent = parent
        self._cases = []
        self._setups = []
        self._teardowns = []
        self._test_setups = []
        self._test_teardowns = []
        self._children = []
        self._teardown_level = self
        self._last_test_case = None

    @property
    def _level(self):
        level = 0
        parent = self._parent
        while parent is not None:
            level += 1
            parent = parent._parent
        return level

    @property
    def _ancestry(self):
        """The ancestry of a specific Group from child to ancestor.

        If groups are declared like this:

            with such.A("A") as it:
                with it.having("B"):
                    with it.having("C"):
                        # do something

        Group A would be the parent of Group B, and Group B would be the parent
        of Group C. So the ancestry would look like this:

            [C, B, A]
        """
        ancestry = []
        group = self
        while group is not None:
            ancestry.append(group)
            group = getattr(group, "_parent", None)
        return ancestry

    @property
    def _root_group(self):
        return self._ancestry[-1]

    def _build_test_cases(self, mod):
        """Build the test cases for this Group.

        The group of the main GroupContextManager represents the root of a
        tree. Each group should be considered a branch, capable of having
        leaves or other branches as its children, and each test case should be
        considered aleaf.

        If a branch has no leaves on either itself, or any of its descendant
        branches, then it's considered useless, and nothing will happen with
        it, even if it has setups or teardowns.
        """
        start_test_count = self._helper._get_test_count()
        if self._cases:
            # build test cases
            bases = (
                GroupTestCase,
                unittest.TestCase,
            )
            for case in self._cases:
                self._helper._add_case(case)
                case_name = TEST_CLASS_NAME_TEMPLATE.format(getrandbits(128))
                _test = type(case_name, bases, {})
                _test.__module__ = mod['__name__']
                mod[_test.__name__] = _test

        for child in self._children:
            child._build_test_cases(mod)

        end_test_count = self._helper._get_test_count()
        if end_test_count > start_test_count:
            self._helper._set_teardown_level_for_last_case(self)

    def _add_child(self, child_description):
        child = Group(child_description, parent=self)
        self._children.append(child)
        return child


class Case(object):

    _helper = helper

    def __init__(self, group, func, description):
        self._group = group
        self._func = func
        self._description = description
        self._teardown_level = None

    def __call__(self, testcase, *args):
        self._helper = testcase
        funcargs, _, _, _ = inspect.getargspec(self._func)
        if funcargs:
            self._func(testcase, *args)
        else:
            self._func()

    def __getattr__(self, attr):
        """Defer attribute lookups to helper."""
        return getattr(self._helper, attr)
