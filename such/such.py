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
        self._level_stack = []

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

    All Groups will have to create a class that represents each test for that
    Group. This should be the class those classes inherit from in order to
    ensure they all perform the necessary steps requied of them.
    """

    _helper = helper
    _group = None
    _is_last = False
    _description = ""
    _test_description = ""

    def __str__(self):
        return self._description

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
    def _set_test_description(cls, setup_ancestry):
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
            cls._test_description,
        )

    def _set_test_failure_description(self):
        ancestry = ":".join(reversed(self._group._ancestry))
        self._description = "{} ({})".format(self._test_description, ancestry)

    @classmethod
    def setUpClass(cls):
        stack_comp = zip(
            cls._helper._level_stack,
            list(reversed(cls._group._ancestry)),
        )
        branching_point = 0
        for i, level in enumerate(stack_comp):
            if level[0] == level[1]:
                continue
            else:
                branching_point = i

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
        teardown_level = 0 - cls._group._teardown_level._level
        teardown_ancestry = cls._group._ancestry[:teardown_level]
        for group in teardown_ancestry:
            for teardown in teardown_ancestry:
                args, _, _, _ = inspect.getargspec(teardown)
                if args:
                    teardown(cls)
                else:
                    teardown()
            cls._helper._level_stack.remove(group)

    def runTest(self):
        args, _, _, _ = inspect.getargspec(self._func)
        if args:
            self._func(self)
        else:
            self._func()


class Group(object):
    """A group of tests, with common fixtures and description"""

    def __init__(self, description, parent=None):
        self.description = description
        self._parent = parent
        self._cases = []
        self._setups = []
        self._teardowns = []
        self._test_setups = []
        self._test_teardowns = []
        self._children = []
        self._teardown_level = self

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
