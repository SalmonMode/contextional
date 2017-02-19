import unittest
import inspect

class Helper(unittest.TestCase):
    """A singleton used to keep object persistent during test execution.

    Most, if not all objects that have the Helper instance as an attribute will
    have custom __getattr__, __setattr__, and __delattr__ methods that defer
    most attribute requests to this helper to enure that they have access to
    the `unittest.TestCase` assert methods and any objects that the helper is
    holding.
    """

    def __init__(self):
        self._current_level = 0

    def runTest(self):
        pass


helper = Helper()


class GroupManager(object):
    """A manager for groups, and their fixtures, child groups, and tests.

    A group manager is used to handle constructing groups, and their fixtures,
    child groups, and tests through the various decorators it provides.
    """
    _helper = helper
    desc_pre = "A "
    desc_post = ""

    def __init__(self, description, desc_pre=None, desc_post=None):
        if desc_pre is None:
            desc_pre = self.desc_pre
        if desc_post is None:
            desc_post = self.desc_post
        self._group = Group(
            "{pre}{desc}{post}".format(
                pre=desc_pre,
                desc=description,
                post=desc_post,
                ),
        )

    def __getattr__(self, attr):
        return getattr(self._helper, attr)

    def __setattr__(self, attr, value):
        if attr in self.__dict__.keys() or attr == "_group":
            super(GroupManager, self).__setattr__(attr, value)
        else:
            setattr(self._helper, attr, value)

    def __delattr__(self, attr):
        if attr in self.__dict__.keys() or attr == "_group":
            super(GroupManager, self).__delattr__(attr)
        else:
            delattr(self._helper, attr)


class GroupTestCase(unittest.TestCase):

    """The base test class for a Group.

    All Groups will have to create a class that represents the tests for that
    Group. This should be the class those classes inherit from in order to
    ensure they all perform the necessary steps requied of them.
    """

    _helper = helper
    _setups = []
    _group = None
    _is_last = False

    def __str__(self):
        return str(getattr(self, self._testMethodName))

    def __getattr__(self, attr):
        return getattr(self._helper, attr)

    def __setattr__(self, attr, value):
        if attr in self.__dict__.keys():
            super(GroupTestCase, self).__setattr__(attr, value)
        else:
            setattr(self._helper, attr, value)

    def __delattr__(self, attr):
        if attr in self.__dict__.keys():
            super(GroupTestCase, self).__delattr__(attr)
        else:
            delattr(self._helper, attr)

    @classmethod
    def setUpClass(cls):
        if len(cls._current_level) == 0:
            # tell the last GroupTestCase that will run that it needs to run
            # all the remaining teardowns
            cls._group._last_test_class._is_last = True
        diff = cls._group._level - cls._helper._current_level
        setup_ancestry = list(reversed(cls._group._ancestry))[diff:]
        for group in setup_ancestry:
            for setup in group._setups:
                args, _, _, _ = inspect.getargspec(setup)
                if args:
                    setup(cls)
                else:
                    setup()
        cls._helper._current_level = cls._group._level

    def setUp(self):
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
        teardown_ancestry = list(reversed(cls._group._ancestry))
        stop_level = 0 if cls._is_last else cls._group._level_to_teardown_to
        teardown_ancestry = teardown_ancestry[stop_level:]
        for group in teardown_ancestry:
            for teardown in teardown_ancestry:
                args, _, _, _ = inspect.getargspec(teardown)
                if args:
                    teardown(cls)
                else:
                    teardown()
        cls._helper._current_level = stop_level


class GroupAncestry(object):
    """The ancestry of a specific Group from child to ancestor.

    GroupAncestry is a descriptor of the Group class, which can be used to
    easily access the ancestry (the parent Groups) of that Group instance.

    If groups are declared like this:

        with such.A("A") as it:
            with it.having("B"):
                with it.having("C"):
                    # do something

    Group A would be the parent of Group B, and Group B would be the parent of
    Group C. So the ancestry would look like this:

        [C, B, A]
    """


    def __init__(self):
        pass

    def __get__(self, instance, owner):
        self._ancestry = []
        group = instance
        while group:
            self._ancestry.append(group)
            group = getattr(group, "parent", None)
        return self


class Group(object):
    """A group of tests, with common fixtures and description"""

    _ancestry = GroupAncestry()
    _level = 0

    def __init__(self, description, parent=None):
        self.description = description
        self.parent = parent
        self._level = 0 if parent is None else parent._level + 1
        self._cases = []
        self._setups = []
        self._teardowns = []
        self._test_setups = []
        self._test_teardowns = []
        self._children = []
        self._level_to_teardown_to = self._level - 1

    def _build_test_cases(self, mod):
        """Build the test cases for this Group.

        The group of the main GroupManager represents the root of a tree. Each
        group should be considered a branch, capable of having leaves or other
        branches as its children, and each test case should be considered a
        leaf.

        If a branch has no leaves on either itself, or any of its descendant
        branches, then it's considered useless, and nothing will happen with
        it, even if it has setups or teardowns.
        """
        if self._cases:
            last_test_case = None

            # build test cases

            for i, case in enumerate(self._cases):
                test_setups = self._test_setups
                if i == 0:
                    # first test is responsible for running the group setups
                    test_setups[:0] = self._setups
                # make TestCase here

        for child in self._children:
            if len(self._cases) == 0:
                child._descriptions[:0] = self._descriptions
                child._setups[:0] = self._setups
            last_test_case = child._build_test_cases()

        if last_test_case is not None:
            last_test_case._teardowns += self._teardowns

        return last_test_case

    def _make_test_class(self):
        test_class = type(object)
