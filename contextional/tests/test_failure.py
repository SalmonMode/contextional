from __future__ import absolute_import

import unittest

from contextional.tests.tools import SilentTestRunner
from contextional.test_resources.failure import expected_stream_output


class TestFailureResult(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_program = unittest.TestProgram(
            module="contextional.test_resources.failure",
            testRunner=SilentTestRunner,
            argv=["contextional/tests/test_failure.py"],
            exit=False,
            verbosity=2,
        )
        cls.test_results = test_program.result
        cls.stream_output = cls.test_results.test_run_output

    def test_tests_run_count(self):
        self.assertEqual(
            self.test_results.testsRun,
            11,
        )

    def test_failures_count(self):
        self.assertEqual(
            len(self.test_results.failures),
            4,
        )

    def test_errors_count(self):
        self.assertEqual(
            len(self.test_results.errors),
            4,
        )

    def test_stream_output(self):
        self.assertEqual(
            self.stream_output,
            expected_stream_output,
        )


if __name__ == '__main__':
    unittest.main()
