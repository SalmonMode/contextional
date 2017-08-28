from __future__ import (
    absolute_import,
    with_statement,
)

import logging
import sys
import unittest
import inspect
from random import getrandbits
from contextlib import contextmanager
from copy import deepcopy
from types import FunctionType
from collections import Mapping


class CascadingFailureError(AssertionError):
    """Raise in tests during a cascading failure."""


LOGGER = logging.getLogger(__name__)


class Helper(unittest.TestCase):
    """A singleton used to keep objects persistent during test execution.

    Most, if not all objects that have the Helper instance as an attribute will
    have custom __getattr__, __setattr__, and __delattr__ methods that defer
    most attribute requests to this helper to enure that they have access to
    the :class:`unittest.TestCase` assert methods and any objects that the
    helper is holding.
    """

    def __init__(self, *args, **kwargs):
        self._level_stack = []
        self._cases = []
        super(Helper, self).__init__(*args, **kwargs)

    def __del__(self):
        self._clear_stack()

    def _clear_stack(self):
        """Teardown the groups that are still in the level stack."""
        teardown_groups = self._level_stack[::-1]
        for group in teardown_groups:
            if group._teardowns:
                LOGGER.debug(
                    "Running tearDowns for group:\n{}".format(
                        group._get_full_ancestry_description(True),
                    ),
                )
                for i, teardown in enumerate(group._teardowns):
                    LOGGER.debug("Running tearDown #{}".format(i))
                    teardown()
            self._level_stack.remove(group)
        LOGGER.debug("Teardowns complete.")

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


def get_next_test_from_helper():
    return helper._cases[0]


class ContextionalTestResultProxy(object):

    def __init__(self, result):
        self._true_result = getattr(result, "result", result)
        self._result = result
        if hasattr(self._true_result, "stream"):
            self.stream = self._true_result.stream

    def __getattr__(self, name):
        if name == "showAll":
            return getattr(self._true_result, name)
        return getattr(self._result, name)

    def stopTest(self, test):
        if not test._is_pytest:
            test._teardown_to_level(test._case._teardown_level)
        self._result.stopTest(test)


class GcmMaker(object):

    _helper = helper

    def __init__(self):
        self._current_context = None

    def __call__(self, description, cascading_failure=True):
        new_context = Context(description, cascading_failure)
        new_context._parent_context = self._current_context
        new_context._gcm = self
        self._current_context = new_context
        return self._current_context

    def __getattr__(self, attr):
        """Defer attribute lookups to helper."""
        return getattr(self._helper, attr)

    def __setattr__(self, attr, value):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys() or attr == "_group":
            super(Context, self).__setattr__(attr, value)
        else:
            setattr(self._helper, attr, value)

    def __delattr__(self, attr):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys() or attr == "_group":
            super(Context, self).__delattr__(attr)
        else:
            delattr(self._helper, attr)

    @property
    def add_test(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.add_test`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.add_test

    @property
    def add_group(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.add_group`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.add_group

    @property
    def add_setup(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.add_setup`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.add_setup

    @property
    def add_test_setup(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.add_test_setup`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.add_test_setup

    @property
    def add_teardown(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.add_teardown`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.add_teardown

    @property
    def add_test_teardown(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to
        :meth:`Context.add_test_teardown`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.add_test_teardown

    @property
    def includes(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.includes`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.includes

    @property
    def combine(self):
        """Forward the call to the current :class:`Context`.

        For a more detailed description, go to :meth:`Context.combine`.
        """

        if self._current_context is None:
            raise AttributeError("No current context.")
        return self._current_context.combine

    def utilize_asserts(self, container):
        """Allow the use of custom assert method in tests.

        :param container:
            A container of functions/methods to be used as assert methods
        :type container: class, list of functions, or function

        Accepts a class, list/set/dictionary of functions, or a function.

        If a class is passed in, this takes all the methods of that class and
        puts them into a dictionary, where the keys are the function names, and
        the values are the functions themselves. If a list or set is passed in,
        a dictionary is constructed using the names of the functions as the
        keys with the functions being the values. If a function is passed in,
        it is put into a dictionary, where the key is the function's name and
        the value is the function itself. If a dictionary is passed in, it is
        assumed that the keys are the function names, and the values are the
        functions themselves.

        Example::

            class CustomAsserts(object):

                def assertCustom(self, value):
                    if value != "custom":
                        raise AssertionError("value is not custom")

            GCM.utilize_asserts(CustomAsserts)

            with GCM("Main Group") as MG:

                @GCM.add_test("is custom")
                def test(case):
                    case.assertCustom("custom")

        Once the functions are parsed into a dictionary, they are each set as
        attributes of the :class:`.Helper`, using their dictionary keys as
        their method names, but only if they're would-be names start with
        "assert".
        """
        assert_methods = {}
        if inspect.isclass(container):
            c_funcs = inspect.getmembers(
                container,
                predicate=inspect.isfunction,
            )
            c_meths = inspect.getmembers(
                container,
                predicate=inspect.ismethod,
            )
            c_meths_funcs = list((n, m.__func__) for n, m in c_meths)
            assert_methods = {
                name: method for name, method in set(c_funcs + c_meths_funcs)
            }
        elif isinstance(container, list) or isinstance(container, set):
            assert_methods = {method.__name__: method for method in container}
        elif isinstance(container, dict):
            assert_methods = container
        elif isinstance(container, FunctionType):
            assert_methods = {container.__name__: container}
        else:
            raise TypeError(
                "Unexpected type. Must be class, list, dict, or function",
            )
        for name, method in assert_methods.items():
            if name.startswith("assert"):
                setattr(Helper, name, method)


GroupContextManager = GcmMaker()


class Context(object):
    """A context manager for groups, their fixtures, child groups, and tests.

    :param description: The description for the group of the current context.
    :type descrition: str.
    :param cascading_failure: Cascade the failure to all tests within the root
        group.
    :type cascading_failure: bool.

    A :class:`Context` is used to handle constructing groups, their fixtures,
    child groups, and tests through the various decorators and methods
    it provides.

    If ``cascading_failure`` is ``True``, and one of the setUps for this group
    throws an error, then the remaining setUps will be skipped and, of the
    remaining setUps and tests within this group (including those of
    descendant groups), the setUps will be skipped, and the tests will
    automatically fail.

    In the event of a cascading failure, all tearDowns of this group (but
    not the descendant groups) will still be run, so, if there are any,
    they should be able to handle a situation where one or more of the
    setUps for this group didn't run all the way through without any
    problems.

    A cascading failure can only be triggered by a setUp that exists at the
    top level of this group. If a setUp of a descendant group has an issue, it
    will not cause a cascading failure of this group.

    Example::

        with GCM("Main Group") as MG:

            @GCM.add_test("something")
            def test(case):
                case.assertTrue(True)

        MG.create_tests()
    """

    _helper = helper
    _current_manager = None

    def __init__(self, description, cascading_failure=True):
        self._group = Group(description, cascading_failure=cascading_failure)

    def __enter__(self):
        """Track and provided the context manager when entering the context."""
        self._old_manager = self.__class__._current_manager
        self.__class__._current_manager = self
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Stop tracking the context manager and handle exiting the context."""
        self.__class__._current_manager = self._old_manager
        if exc_type is None:
            return True

    def __getattr__(self, attr):
        """Defer attribute lookups to helper."""
        return getattr(self._helper, attr)

    def __setattr__(self, attr, value):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys() or attr == "_group":
            super(Context, self).__setattr__(attr, value)
        else:
            setattr(self._helper, attr, value)

    def __delattr__(self, attr):
        """Defer attribute lookups to helper."""
        if attr in self.__dict__.keys() or attr == "_group":
            super(Context, self).__delattr__(attr)
        else:
            delattr(self._helper, attr)

    def add_test(self, func):
        """Add the decorated function to the current group as a test.

        :param func: The test description or the test function itself
        :type func: str or function

        This decorator takes an optional argument for the description of the
        test case. If not provided, the docstring of the function will be used
        as the test case's description.

        Example::

            with GCM("Main Group") as MG:

                @GCM.add_test("something")
                def test(case):
                    case.assertTrue(True)

        .. note::
            To avoid any extra functions running by accident, this decorator
            will NOT return any replacement function. The decorated function
            will no longer exist in the global namespace of the module it was
            declared in once the decorator is evaluated.
        """

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
    def add_group(self, description, cascading_failure=True, params=()):
        """Use a new child group of the parent group for this context.

        :param description: The description of the group for the context
        :type description: str
        :param cascading_failure: Cascade the failure to all tests within this
            group.
        :type descrition: bool.
        :param params: The collection of sets of parameters
        :type params: collection

        If ``cascading_failure`` is ``True``, and one of the setUps for this
        group throws an error, then the remaining setUps will be skipped and,
        of the remaining setUps and tests within this group (including those of
        descendant groups), the setUps will be skipped, and the tests will
        automatically fail.

        In the event of a cascading failure, all tearDowns of this group (but
        not the descendant groups) will still be run, so, if there are any,
        they should be able to handle a situation where one or more of the
        setUps for this group didn't run all the way through without any
        problems.

        A cascading failure can only be triggered by a setUp that exists at the
        top level of this group. If a setUp of a descendant group has an issue,
        it will not cause a cascading failure of this group.

        If provided with parameters, a duplicate group will be made for each
        set of parameters (if any are provided) where each set of parameters is
        passed to both the setups and teardowns for that group.

        If the parameters are just a sequence of parameters (i.e. a set, tuple,
        or list), then the group's description will show the particular set of
        parameters used for that group. If it is a mapping, the key for each
        set will be applied to the end of the group's description instead. Each
        set of parameters can either be a set/tuple/list, or a Mapping if you
        want keyword arguments to be passed to your setups/teardowns. For
        example, the following code::

            with GCM("Some Group") as SG:

                params = (
                    {
                        "num_1": 1,
                        "num_2": 2,
                        "num_3": 3,
                    },
                    {
                        "num_3": 3,
                        "num_2": 2,
                        "num_1": 1,
                    },
                )
                with GCM.add_group("Child Group", params=params):

                    @GCM.add_setup
                    def setUp(num_1, num_2, num_3):
                        GCM.sum = num_1 + num_2 + num_3

                    @GCM.add_test("sum is 6")
                    def test(case):
                        case.assertEqual(GCM.sum, 6)

                params = {
                    "set #1": (1, 2, 3),
                    "set #2": (3, 2, 1),
                }
                with GCM.add_group("Another Child Group", params=params):

                    @GCM.add_setup
                    def setUp(num_1, num_2, num_3):
                        GCM.sum = num_1 + num_2 + num_3

                    @GCM.add_test("sum is 6")
                    def test(case):
                        case.assertEqual(GCM.sum, 6)

        will show the following output:

        .. code-block:: none

            Some Group
              Child Group {'num_1': 1, 'num_2': 2, 'num_3': 3}
                sum is 6 ... ok
              Child Group {'num_1': 1, 'num_2': 2, 'num_3': 3}
                sum is 6 ... ok
              Another Child Group set #2
                sum is 6 ... ok
              Another Child Group set #1
                sum is 6 ... ok


        """
        last_group = self._group
        self._group = last_group._add_child(description, cascading_failure)
        yield self

        no_params = params == ()

        group_identifiers = []
        if isinstance(params, Mapping):
            group_identifiers = params.keys()
        elif no_params:
            group_identifiers = [0]
        else:
            group_identifiers = range(len(params))
        for gid in group_identifiers:
            args = () if no_params else params[gid]
            new_group = deepcopy(self._group)
            new_group._parent = last_group
            new_group._args = args
            if isinstance(params, Mapping):
                new_group._description += " {}".format(gid)
            elif no_params:
                pass
            else:
                new_group._description += " {}".format(params[gid])
            last_group._children.append(new_group)
        original_new_child = self._group
        self._group = last_group
        self._group._children.remove(original_new_child)

    def add_setup(self, func):
        """Add the decorated function to the current context as a setup.

        :param func:
            A function to be used for a setup of the group for the current
            context
        :type func: function

        This setup will only be run once, and it will be run by the first test
        case within the group. If the current group has no test cases, then the
        first test case of any of the current group's descendants will run the
        setup before running any of its own. If the current group does not
        have any test cases and none of its descendants have any test cases,
        then the setup will not get run.

        While the setup must be run by the actual test cases themselves (as
        that's the only opportunity to run code), it might be easiest to
        imagine that the setups for a group get run only as you step in to that
        group from its parent.

        Example::

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.thing = 1

                @GCM.add_test("thing is 1")
                def test(case):
                    case.assertEqual(
                        GCM.thing,
                        1,
                    )

        .. note::
            To avoid any extra functions running by accident, this decorator
            will NOT return any replacement function. The decorated function
            will no longer exist in the global namespace of the module it was
            declared in once the decorator is evaluated.
        """
        self._group._setups.append(func)

    def add_test_setup(self, func):
        """Add the decorated function to the current context as a test setup.

        :param func:
            A function to be used for a setup of the tests of the group of the
            current context
        :type func: function

        This test setup will be run once before each test case in the current
        group. If the current group has no test cases, then this test setup
        will never be run, even if a descendant of the current group has test
        cases.

        Example::

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.thing = 0

                @GCM.add_test_setup
                def setUpTest():
                    GCM.thing += 1

                @GCM.add_test("thing is 1")
                def test(case):
                    case.assertEqual(
                        GCM.thing,
                        1,
                    )

        .. note::
            To avoid any extra functions running by accident, this decorator
            will NOT return any replacement function. The decorated function
            will no longer exist in the global namespace of the module it was
            declared in once the decorator is evaluated.
        """
        self._group._test_setups.append(func)

    def add_teardown(self, func):
        """Add the decorated function to the current context as a teardown.

        :param func:
            A function to be used for a teardown of the group of the current
            context
        :type func: function

        This teardown will only be run once, and it will be run by the last
        test case within the group, including the test cases of the group's
        descendants. If the current group has test cases, but its descendants
        also have test cases, then only the single last test case of its
        descendants will run the teardown after running its own teardowns. If
        the current group does not have any test cases and none of its
        descendants have any test cases, then the teardown will not get run.

        While the teardowns must be run by the actual test cases themselves (as
        that's the only opportunity to run code), it might be easiest to
        imagine that the teardowns for a group get run only as you step out of
        that group, back up to its parent group.

        Example::

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.thing = 0

                with GCM.add_group("Child A"):

                    @GCM.add_setup
                    def setUp():
                        GCM.thing += 2

                    @GCM.add_teardown
                    def tearDown():
                        GCM.thing -= 1

                    @GCM.add_test("thing is 2")
                    def test(case):
                        case.assertEqual(
                            GCM.thing,
                            2,
                        )

                with GCM.add_group("Child B"):

                    @GCM.add_test("thing is now 1")
                    def test(case):
                        case.assertEqual(
                            GCM.thing,
                            1,
                        )

        .. note::
            To avoid any extra functions running by accident, this decorator
            will NOT return any replacement function. The decorated function
            will no longer exist in the global namespace of the module it was
            declared in once the decorator is evaluated.
        """
        self._group._teardowns.append(func)

    def add_test_teardown(self, func):
        """Add the decorated function to the current group as a test teardown.

        :param func:
            A function to be used for a teardown of the tests of the group of
            the current context
        :type func: function

        This test teardown will be run once after each test case in the current
        group. If the current group has no test cases, then this test teardown
        will never be run, even if a descendant of the current group has test
        cases.

        Example::

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.thing = 0

                @GCM.add_test_setup
                def setUpTest():
                    GCM.thing += 1

                @GCM.add_test_teardown
                def setUpTest():
                    GCM.thing -= 1

                @GCM.add_test("thing is 1")
                def test(case):
                    case.assertEqual(
                        GCM.thing,
                        1,
                    )

                @GCM.add_test("thing is still 1")
                def test(case):
                    case.assertEqual(
                        GCM.thing,
                        1,
                    )

        .. note::
            To avoid any extra functions running by accident, this decorator
            will NOT return any replacement function. The decorated function
            will no longer exist in the global namespace of the module it was
            declared in once the decorator is evaluated.
        """
        self._group._test_teardowns.append(func)

    @classmethod
    def utilize_asserts(cls, container):
        """Allow the use of custom assert method in tests.

        :param container:
            A container of functions/methods to be used as assert methods
        :type container: class, list of functions, or function

        Accepts a class, list/set/dictionary of functions, or a function.

        If a class is passed in, this takes all the methods of that class and
        puts them into a dictionary, where the keys are the function names, and
        the values are the functions themselves. If a list or set is passed in,
        a dictionary is constructed using the names of the functions as the
        keys with the functions being the values. If a function is passed in,
        it is put into a dictionary, where the key is the function's name and
        the value is the function itself. If a dictionary is passed in, it is
        assumed that the keys are the function names, and the values are the
        functions themselves.

        Example::

            class CustomAsserts(object):

                def assertCustom(self, value):
                    if value != "custom":
                        raise AssertionError("value is not custom")

            GCM.utilize_asserts(CustomAsserts)

            with GCM("Main Group") as MG:

                @GCM.add_test("is custom")
                def test(case):
                    case.assertCustom("custom")

        Once the functions are parsed into a dictionary, they are each set as
        attributes of the :class:`.Helper`, using their dictionary keys as
        their method names, but only if they're would-be names start with
        "assert".
        """
        assert_methods = {}
        if inspect.isclass(container):
            c_funcs = inspect.getmembers(
                container,
                predicate=inspect.isfunction,
            )
            c_meths = inspect.getmembers(
                container,
                predicate=inspect.ismethod,
            )
            c_meths_funcs = list((n, m.__func__) for n, m in c_meths)
            assert_methods = {
                name: method for name, method in set(c_funcs + c_meths_funcs)
            }
        elif isinstance(container, list) or isinstance(container, set):
            assert_methods = {method.__name__: method for method in container}
        elif isinstance(container, dict):
            assert_methods = container
        elif isinstance(container, FunctionType):
            assert_methods = {container.__name__: container}
        else:
            raise TypeError(
                "Unexpected type. Must be class, list, dict, or function",
            )
        for name, method in assert_methods.items():
            if name.startswith("assert"):
                setattr(Helper, name, method)

    def includes(self, *contexts):
        """Graft a :class:`.Context` group structure here.

        :param contexts:
            The :class:`.Context` objects that contain the group
            structures you want to include in the group of the current context,
            in the order they are listed.
        :type contexts: :class:`.Context`

        For each :class:`.Context` instance that was passed, take
        the root group of a it, make a deepcopy of it, and append it to this
        :class:`.Context`'s current group's children so that copies
        of all of its tests get run within the context of the current group in
        the order and structure they were originally defined in.

        Example::

            with GCM("Predefined Group") as PG:

                @GCM.add_test("value is 1")
                def test(case):
                    case.assertEqual(
                        GCM.value,
                        1,
                    )

                with GCM.add_group("Sub Group"):

                    @GCM.add_teardown
                    def tearDown():
                        GCM.value = 2

                    @GCM.add_test("value is still 1")
                    def test(case):
                        case.assertEqual(
                            GCM.value,
                            1,
                        )

            with GCM("Another Predefined Group") as APG:

                @GCM.add_test("value is now 2")
                def test(case):
                    case.assertEqual(
                        GCM.value,
                        2,
                    )

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.value = 1

                GCM.includes(
                    PG,
                    APG,
                )

        Output:

        .. code-block:: none

            Main Group
              Predefined Group
                value is 1 ... ok
                Sub Group
                  value is still 1 ... ok
              AnotherPredefined Group
                value is now 2 ... ok
        """
        for context in contexts:
            if not isinstance(context, Context):
                raise TypeError(
                    "method only accepts Context objects",
                )
            group_copy = deepcopy(context._group)
            group_copy._parent = self._group
            self._group._children.append(group_copy)

    def combine(self, *contexts):
        """Use the contents of a :class:`.Context`'s root group.

        :param contexts:
            The :class:`.Context` objects containing the group
            structures you want to combine with the group of the current
            context.
        :type contexts: :class:`.Context`

        For each :class:`.Context` instance that was passed, take
        the root group of a it, make a deepcopy of it, and append each of its
        tests, fixtures, and child groups to the respective lists of the group
        of the current context.

        Example::

            with GCM("Predefined Group") as PG:

                @GCM.add_test("value is 1")
                def test(case):
                    case.assertEqual(
                        GCM.value,
                        1,
                    )

                with GCM.add_group("Sub Group"):

                    @GCM.add_teardown
                    def tearDown():
                        GCM.value = 2

                    @GCM.add_test("value is still 1")
                    def test(case):
                        case.assertEqual(
                            GCM.value,
                            1,
                        )

            with GCM("Another Predefined Group") as APG:

                @GCM.add_test("value is still 1 here")
                def test(case):
                    case.assertEqual(
                        GCM.value,
                        1,
                    )

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.value = 1

                GCM.combine(
                    PG,
                    APG,
                )

        Output:

        .. code-block:: none

            Main Group
              value is 1 ... ok
              value is now 2 ... FAIL
              Sub Group
                value is still 1 ... ok
        """
        for context in contexts:
            if not isinstance(context, Context):
                raise TypeError(
                    "method only accepts Context objects",
                )
            group_copy = deepcopy(context._group)
            self._group._setups += group_copy._setups
            self._group._test_setups += group_copy._test_setups
            for case in group_copy._cases:
                case._group = self._group
                self._group._cases.append(case)
            self._group._test_teardowns += group_copy._test_teardowns
            self._group._teardowns += group_copy._teardowns
            for child in group_copy._children:
                child._parent = self._group
                self._group._children.append(child)

    def create_tests(self, mod=None):
        """Create the tests that will be discovered by the testing framework.

        :param mod: :func:`.globals`

        This walks through the tree of groups and test cases, creating the
        :class:`.Case` instances that the :attr:`._helper` holds, and a
        :class:`.TestCase` class for each :class:`.Case` instance to run that
        :class:`.Case` instance.

        This method will try to add the :class:`.TestCase` classes to the
        namespace of the module that :meth:`.create_tests` was called in. This
        behavor should only be trusted when :meth:`.create_tests` is called in
        the local namespace of the module (i.e. not inside a function, class,
        etc.), and if there's any issues, the namespace object can be passed as
        an argument to :meth:`.create_tests` (usually done with
        :func:`.globals`).

        Only :class:`.Context` instances that call this method will
        have their tests run. If a :class:`.Context` instance does
        not call this method, it should only be so that its group structure
        could be included in another :class:`.Context`'s structure.

        Example::

            with GCM("Main Group") as MG:

                @GCM.add_setup
                def setUp():
                    GCM.value = 1

                @GCM.add_test("value is 1")
                def test(case):
                    case.assertEqual(
                        GCM.value,
                        1,
                    )

            MG.create_tests()
        """
        if mod is None:
            mod = inspect.stack()[1][0].f_locals
        plugin = "contextional.pytest_contextional"
        if "pytest_plugins" in mod:
            str_type = str if sys.version_info >= (3, 0) else basestring
            if isinstance(mod["pytest_plugins"], tuple):
                mod["pytest_plugins"] = list(mod["pytest_plugins"])
            if isinstance(mod["pytest_plugins"], list):
                mod["pytest_plugins"].append(plugin)
            elif isinstance(mod["pytest_plugins"], str_type):
                mod["pytest_plugins"] = [
                    mod["pytest_plugins"],
                    "contextional.pytest_contextional",
                ]
        else:
            mod["pytest_plugins"] = [
                "contextional.pytest_contextional",
            ]
        start_test_count = self._helper._get_test_count()
        self._group._build_test_cases(mod)
        if self._helper._get_test_count() > start_test_count:
            self._helper._set_teardown_level_for_last_case(NullGroup)


class GroupTestCase(object):
    """The base test class for a Group.

    All Groups will have to create a class that represents each test for that
    Group. This should be the class those classes inherit from in order to
    ensure they all perform the necessary steps requied of them.
    """

    _helper = helper
    _root_group_hash = None
    _description = ""
    _full_description = ""
    _currentResult = None
    _err_info = None
    _err = None
    _is_pytest = False

    def __str__(self):
        """String representation of the test case.

        While the tests are running, the test case's description should only
        contain what is necessary, based on what tests have already run. After
        the tests have run, in the test results output, the test case's
        description should have its entire ancestry listed so that the
        failed/errored/skipped test has the necessary context (in the event
        that two test cases have the same name, but are in different contexts).

        This method allows the test case to alter it's description so that
        during runtime, you will see this:

        .. code-block:: none

            Group A
                Group B
                    test #1 ... ok
                Group C
                    test #2 ... FAIL

        instead of this:

        .. code-block:: none

            Group A
                Group B
                    test #1 ... ok
            Group A
                Group C
                    test #2 ... FAIL

        but the test case's description in the test result output will look
        like this:

        .. code-block:: none

            Group A
                Group C
                    test #2
        """
        if self._case._test_started:
            return self._case._full_description
        else:
            return self._case._inline_description

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

    @staticmethod
    def _find_common_ancestor(ancestry_a, ancestry_b):
        """Common ancestry between two :class:`.Group`s.

        If one :class:`.Group` has an ancestry of:

        .. code-block:: none

            [C, B, A]

        and another has an ancestry of

        .. code-block:: none

            [D, B, A]

        They would have a common ancestry of:

        .. code-block:: none

            [B, A]

        This is useful for determining where two :class:`.Group`s branch off
        from each other.
        """

        stack_comp = list(
            zip(
                ancestry_a,
                ancestry_b,
            ),
        )
        branching_point = len(stack_comp)
        for i, level in enumerate(stack_comp):
            if level[0] == level[1]:
                continue
            else:
                branching_point = i
                break
        common_ancestor = NullGroup
        if branching_point > 0:
            common_ancestor = ancestry_a[branching_point - 1]
        return common_ancestor

    @classmethod
    def setUpClass(cls):
        """The preparations for the test case class that's about to be run.

        The :meth:`.setUpClass` method gets the next test case from the
        :attr:`._helper` if it doesn't already have one. That test case will
        later be used to figure out what setups/teardowns need to be run, and
        also to run the actual test.
        """
        __tracebackhide__ = True
        cls._case = cls._helper._get_next_test()
        cls._group = cls._case._group

    def setUp(self):
        """The preparations required to be run before each test in the group.

        This is also where the description of the current test case is modified
        to include its full ancestry, so that, in the event that this test case
        fails, errors, or is skipped, the test's description in the results
        output provides the complete context for this test case.
        """
        __tracebackhide__ = True
        self._auto_fail = any(
            group._cascading_failure_in_progress
            for group in self._group._ancestry,
        )
        self._case._test_started = True
        if self._auto_fail is True:
            LOGGER.debug(
                "CASCADING FAILURE - Not setting up for test:\n{}".format(
                    self._group._get_full_ancestry_description(indented=True),
                    ("  " * (self._group._level + 1)),
                    self._case._description,
                ),
            )
            return
        LOGGER.debug(
            "Running test setUps for test:\n{}\n{}{}".format(
                self._group._get_full_ancestry_description(indented=True),
                ("  " * (self._group._level + 1)),
                self._case._description,
            ),
        )
        try:
            for i, setup in enumerate(self._group._test_setups):
                LOGGER.debug("Running test setUp #{}".format(i))
                setup()
                LOGGER.debug("test setUp #{} complete.".format(i))
        except Exception:
            LOGGER.debug(
                "Couldn't complete setups for the test due to exception.",
                exc_info=True,
            )
            if self._group._cascading_failure:
                LOGGER.debug("Preparing for cascading failure.")
                self.__class__._auto_fail = True
                self._group._cascading_failure_in_progress = True
            raise
        LOGGER.debug("Test setups complete.")

    def tearDown(self):
        """The cleanup required to be run after each test in the group."""
        __tracebackhide__ = True
        if self._auto_fail is True:
            LOGGER.debug(
                "CASCADING FAILURE - Not tearing down test:\n{}".format(
                    self._group._get_full_ancestry_description(indented=True),
                    ("  " * (self._group._level + 1)),
                    self._case._description,
                ),
            )
            return
        LOGGER.debug(
            "Running test tearDowns for test:\n{}\n{}{}".format(
                self._group._get_full_ancestry_description(indented=True),
                ("  " * (self._group._level + 1)),
                self._case._description,
            ),
        )
        try:
            for i, teardown in enumerate(self._group._test_teardowns):
                LOGGER.debug("Running test tearDown #{}".format(i))
                teardown()
                LOGGER.debug("test tearDown #{} complete.".format(i))
        except Exception:
            LOGGER.debug(
                "Couldn't complete teardowns for the test due to exception.",
                exc_info=True,
            )
            if self._group._cascading_failure:
                LOGGER.debug("Preparing for cascading failure.")
                self.__class__._auto_fail = True
                self._group._cascading_failure_in_progress = True
            raise
        LOGGER.debug("Test teardowns complete.")

    def _teardown_to_level(self, td_level):
        if td_level is None:
            return
        if td_level is NullGroup:
            stop_index = None
        else:
            try:
                stop_index = self._helper._level_stack.index(td_level)
            except IndexError:
                raise IndexError(
                    "Cannot teardown to desired level from current stack.",
                )
        teardown_groups = self._helper._level_stack[:stop_index:-1]
        for group in teardown_groups:
            group._teardown_group(result=self.temp_result)
        LOGGER.debug("Teardowns complete.")

    def _teardown_to_common_level(self):
        self._teardown_to_level(
            self._find_common_ancestor(
                self._helper._level_stack,
                self._group._setup_ancestry,
            ),
        )

    def run(self, result=None):
        __tracebackhide__ = True
        self._currentResult = result
        # nose uses a ResultProxy class, but keeps the actual result as an
        # attribute of the proxy object
        self.temp_result = ContextionalTestResultProxy(result)

        self._auto_fail = False
        for group in self._group._ancestry:
            self._auto_fail = group._cascading_failure_in_progress
            if self._auto_fail is True:
                break

        if self._auto_fail:
            LOGGER.debug(
                "CASCADING FAILURE - Not setting up group:\n{}".format(
                    str(self._group),
                ),
            )

            for group in self._group._setup_ancestry:
                if group not in self._helper._level_stack:
                    self._helper._level_stack.append(group)

            return super(GroupTestCase, self).run(self.temp_result)

        LOGGER.debug("Setting up group:\n{}".format(str(self._group)))
        self._teardown_to_common_level()

        for group in self._group._setup_ancestry:
            group._setup_group(result=self.temp_result)

        LOGGER.debug("Setups complete.")

        x = super(GroupTestCase, self).run(self.temp_result)
        return x

    def runTest(self):
        __tracebackhide__ = True
        if self._auto_fail is True:
            LOGGER.debug(
                "CASCADING FAILURE - Not running test:\n{}".format(
                    self._case._full_description,
                ),
            )
            raise CascadingFailureError()
        LOGGER.debug("Running test:\n{}".format(self._case._full_description))
        # Execute the actual test case function.
        try:
            self._case(self)
        except Exception:
            LOGGER.debug(
                "Test completed unsuccessfully.",
                exc_info=True,
            )
            raise
        LOGGER.debug("Test completed successfully.")


TEST_CLASS_NAME_TEMPLATE = "ContextionalCase_{}"


class Group(object):
    """A group of tests, with common fixtures and description."""

    _helper = helper

    def __init__(self, description, cascading_failure=True, args=(),
                 parent=None):
        self._description = description
        self._parent = parent
        self._cascading_failure = cascading_failure
        self._cascading_failure_in_progress = False
        self._cascading_failure_root = False
        self._args = args
        self._cases = []
        self._setups = []
        self._teardowns = []
        self._test_setups = []
        self._test_teardowns = []
        self._children = []
        self._teardown_level = self
        self._last_test_case = None

    def __str__(self):
        return self._get_full_ancestry_description(indented=True)

    @property
    def _level(self):
        """The level of the group within the tree structure.

        This is defined by:
            1 + the number of connections between the group and the root group.
        """
        level = 0
        parent = self._parent
        while parent is not None:
            level += 1
            parent = parent._parent
        return level

    @property
    def _ancestry(self):
        """The ancestry of a specific :class:`.Group` from child to ancestor.

        If groups are declared like this::

            with GCM("A") as MG:
                with GCM.add_group("B"):
                    with GCM.add_group("C"):
                        # do something

        Group A would be the parent of Group B, and Group B would be the parent
        of Group C. So the ancestry would look like this:

        .. code-block:: none

            [C, B, A]
        """
        ancestry = []
        group = self
        while group is not None:
            ancestry.append(group)
            group = getattr(group, "_parent", None)
        return ancestry

    @property
    def _setup_ancestry(self):
        """The ancestry of a specific :class:`.Group` from ancestor to child.

        If groups are declared like this::

            with GCM("A") as MG:
                with GCM.add_group("B"):
                    with GCM.add_group("C"):
                        # do something

        Group A would be the parent of Group B, and Group B would be the parent
        of Group C. So the setup ancestry would look like this:

        .. code-block:: none

            [A, B, C]
        """
        return list(reversed(self._ancestry))

    def _get_full_ancestry_description(self, indented=False):
        """The ancestry of a specific :class:`.Group` from ancestor to child.

        If groups are declared like this::

            with GCM("A") as MG:
                with GCM.add_group("B"):
                    with GCM.add_group("C"):
                        # do something

        Group A would be the parent of Group B, and Group B would be the parent
        of Group C. So the ancestry would look like this:

        .. code-block:: none

            [C, B, A]

        But this returns the formatted version of the ancestry from ancestor to
        child, as it would appear in the test output. It would look like this
        for the previous example:

        .. code-block:: none

            A
              B
                C

        If ``indented`` is ``True``, then each line will be indented with two
        spaces in addition to the normal indentation based on the level of
        each :class:`.Group`.
        """

        padding = "  " if indented else ""
        full_desc = ""
        group_ancestry = list(reversed(self._ancestry))
        for ancestor in group_ancestry[:-1]:
            full_desc += "{padding}{indent}{desc}\n".format(
                padding=padding,
                indent=("  " * ancestor._level),
                desc=ancestor._description,
            )
        # the last group does not need a new line after it
        full_desc += "{padding}{indent}{desc}".format(
            padding=padding,
            indent=("  " * group_ancestry[-1]._level),
            desc=group_ancestry[-1]._description,
        )
        return full_desc

    @property
    def _inline_description(self):
        return "  " * self._level + self._description

    @property
    def _root_group(self):
        """The root group of the :class:`.Context` instance."""
        return self._ancestry[-1]

    def _build_test_cases(self, mod):
        """Build the test cases for this :class:`.Group`.

        The group of the main :class:`.Context` represents the root
        of a tree. Each group should be considered a branch, capable of having
        leaves or other branches as its children, and each test case should be
        considered aleaf.

        If a branch has no leaves on either itself, or any of its descendant
        branches, then it's considered useless, and nothing will happen with
        it, even if it has setups or teardowns.
        """
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

        start_test_count = self._helper._get_test_count()
        for child in self._children:
            child._build_test_cases(mod)
            end_test_count = self._helper._get_test_count()
            if end_test_count > start_test_count:
                self._helper._set_teardown_level_for_last_case(self)
                start_test_count = end_test_count

    def _add_child(self, child_description, cascading_failure=False):
        """Add a child :class:`.Group` instance to the current group.

        The child :class:`.Group` must be appended to the current
        :class:`.Group`\ 's list of children, and it must be aware that the
        current :class:`.Group` is its parent.
        """
        child = Group(
            child_description,
            cascading_failure=cascading_failure,
            parent=self,
        )
        self._children.append(child)
        return child

    def _setup_group(self, result=None):
        """Setup the :class:`Group`.

        Check if any ancestor :class:`Group`s caused a cascading failure. If
        so, do nothing. Otherwise, run the setups for the group.

        """
        __tracebackhide__ = True
        if self in self._helper._level_stack:
            # setup for this group has already been attempted
            return
        self._helper._level_stack.append(self)

        if result is not None:
            if hasattr(result, "stream"):
                if result.showAll:
                    result.stream.write(self._inline_description + " ")

        self._cascading_failure_in_progress = any(
            group._cascading_failure_in_progress for group in self._ancestry,
        )
        if self._cascading_failure_in_progress:
            LOGGER.debug(
                "CASCADING FAILURE - Not setting up group:\n{}".format(
                    str(self),
                ),
            )
            return
        LOGGER.debug("Running setUps for group:\n{}".format(str(self)))
        try:
            for i, setup in enumerate(self._setups):
                LOGGER.debug("Running setUp #{}".format(i))
                if isinstance(self._args, Mapping):
                    setup(**self._args)
                else:
                    setup(*self._args)
                LOGGER.debug("setUp #{} complete.".format(i))
        except:
            LOGGER.debug("Group setup failed.", exc_info=True)
            if self._cascading_failure:
                LOGGER.debug("Triggering cascading failure.")
                self._cascading_failure_in_progress = True
                self._cascading_failure_root = True
            if result is not None:
                repr = GroupRepr(self)
                if hasattr(result, "_result"):
                    if hasattr(result._result, "test"):
                        old_result_test = result._result.test
                        result._result.test = repr
                result.addError(repr, sys.exc_info())
                if hasattr(result, "_result"):
                    if hasattr(result._result, "test"):
                        result._result.test = old_result_test
            else:
                raise
        else:
            if result is not None:
                if hasattr(result, "stream"):
                    if result.showAll:
                        result.stream.writeln()
        LOGGER.debug("Done setting up group.")

    def _teardown_group(self, result=None):
        """Teardown the :class:`Group`.

        Check if there's currently a cascading failure. If so, find what level
        it began at.any ancestor :class:`Group`s caused a cascading failure. If
        so, do nothing. Otherwise, run the setups for the group.

        """
        __tracebackhide__ = True
        if self not in self._helper._level_stack:
            # teardowns for this group has already been attempted
            return
        if self._cascading_failure_in_progress:
            if not self._cascading_failure_root:
                LOGGER.debug(
                    "CASCADING FAILURE - Not tearing down group:\n{}".format(
                        str(self),
                    ),
                )
                self._helper._level_stack.remove(self)
                return
        if self._teardowns:
            LOGGER.debug("Running tearDowns for group:\n{}".format(str(self)))
            try:
                for i, teardown in enumerate(self._teardowns):
                    LOGGER.debug("Running tearDown #{}".format(i))
                    teardown()
                LOGGER.debug("tearDown #{} complete.".format(i))
            except:
                LOGGER.debug("Group teardown failed.", exc_info=True)
                if result is not None:
                    if hasattr(result, "stream"):
                        if result.showAll:
                            result.stream.write(self._inline_description + " ")
                    repr = GroupRepr(self)
                    if hasattr(result, "_result"):
                        if hasattr(result._result, "test"):
                            old_result_test = result._result.test
                            result._result.test = repr
                    result.addError(repr, sys.exc_info())
                    if hasattr(result, "_result"):
                        if hasattr(result._result, "test"):
                            result._result.test = old_result_test
                else:
                    self._helper._level_stack.remove(self)
                    raise
        self._helper._level_stack.remove(self)
        LOGGER.debug("Done tearing down group.")


class NullGroup(object):
    """Represents the ultimate teardown level.

    This class is only used as a :class:`.Case`'s :attr:`._teardown_level` to
    signal that it is the very last one in the :class:`Context`,
    so all teardowns should be run once it is complete, and the
    :class:`.Helper`'s :attr:`_level_stack` should then be empty.
    """

    pass


class Case(object):
    """Information about the test case.

    This includes the :class:`Group` that this test case belongs to, the test
    case's description, the :class:`Group` level that this test case will need
    to teardown to if needed (`None` by default), and the actual function that
    performs the test.
    """

    _helper = helper
    _exc_info = None

    def __init__(self, group, func, description):
        self._group = group
        self._func = func
        self._description = description
        self._teardown_level = None
        self._test_started = False

    def __call__(self, testcase, *args):
        """Performs the actual test."""
        __tracebackhide__ = True
        self._helper = testcase
        if sys.version_info >= (3, 0):
            funcargs = inspect.getfullargspec(self._func).args
        else:
            funcargs = inspect.getargspec(self._func)[0]
        if funcargs:
            self._func(testcase, *args)
        else:
            self._func()

    @property
    def _inline_description(self):
        return "  " * (self._group._level + 1) + self._description

    @property
    def _full_description(self):
        desc = "\n{}\n{}{}".format(
            str(self._group),
            ("  " * (self._group._level + 2)),
            self._description,
        )
        return desc

    def __getattr__(self, attr):
        """Defer attribute lookups to helper."""
        return getattr(self._helper, attr)


class GroupRepr(object):

    failureException = AssertionError

    def __init__(self, group):
        self._group = group

    def __str__(self):
        return "\n" + str(self._group)

    def shortDescription(self):
        return None


class CaseRepr(object):

    failureException = AssertionError

    def __init__(self, case):
        self._case = case

    def __str__(self):
        desc = "\n{}\n{}{}".format(
            str(self._case._group),
            ("  " * (self._case._group._level + 2)),
            self._case._description,
        )
        return desc

    def shortDescription(self):
        return None
