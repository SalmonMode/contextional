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


class Group(object):
    """A group of tests, with common fixtures and description"""

    def __init__(self, description, parent=None):
        self.description = description
        self.parent = parent
        self._cases = []
        self._setups = []
        self._teardowns = []
        self._test_setups = []
        self._test_teardowns = []
        self._children = []

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
        last_test_case = None
        if self._cases:
            last_test_case = self._cases[-1]

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
