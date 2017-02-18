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
