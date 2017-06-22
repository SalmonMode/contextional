from __future__ import absolute_import

import unittest


class FakeStream(object):

    def __init__(self):
        self.output = ""

    def write(self, text):
        self.output += text

    def flush(self):
        pass


class TextTestResultHolder(unittest.runner.TextTestResult):

    def printErrors(self):
        self.test_run_output = self.stream.output.strip("\n").split("\n")
        super(TextTestResultHolder, self).printErrors()


class SilentTestRunner(unittest.TextTestRunner):

    def __init__(self, *args, **kwargs):
        kwargs["stream"] = FakeStream()
        kwargs["verbosity"] = 2
        kwargs["resultclass"] = TextTestResultHolder
        super(SilentTestRunner, self).__init__(*args, **kwargs)
