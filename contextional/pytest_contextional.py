from __future__ import absolute_import

import sys
from time import time

from contextional.contextional import (
    GroupTestCase,
    get_next_test_from_helper,
    get_level_stack,
    NullGroup,
    Group,
    Case,
    CascadingFailureError,
    LOGGER,
)

import pytest
from _pytest.terminal import TerminalReporter
from _pytest import runner
from _pytest.runner import TestReport, skip, CallInfo
from _pytest._code.code import ExceptionInfo, ReprEntry, FormattedExcinfo


@pytest.mark.trylast
def pytest_configure(config):
    if hasattr(config, 'slaveinput'):
        return  # xdist slave, we are already active on the master
    # Get the standard terminal reporter plugin...
    standard_reporter = config.pluginmanager.getplugin('terminalreporter')
    contextional_reporter = ContextionalTerminalReporter(standard_reporter)

    # ...and replace it with our own instafailing reporter.
    config.pluginmanager.unregister(standard_reporter)
    config.pluginmanager.register(contextional_reporter, 'terminalreporter')


def pytest_runtest_protocol(item, nextitem):
    if item.obj == GroupTestCase.runTest:
        case = get_next_test_from_helper()
        # the current test is a GroupTestCase test
        item.ihook.pytest_runtest_logstart(
            nodeid=case._description + " ",
            location=case,
        )
        item._nodeid = "  " * (case._group._level + 1) + case._description + " "
        item._location = case
    else:
        item.ihook.pytest_runtest_logstart(
            nodeid=item.nodeid,
            location=item.location,
        )
    runner.runtestprotocol(item, nextitem=nextitem)
    return True


def pytest_runtest_teardown(item, nextitem):
    __tracebackhide__ = True
    if isinstance(item._location, Case):
        handle_teardowns(item)


def handle_teardowns(item):
    __tracebackhide__ = True
    case = item._location

    td_lvl = case._teardown_level
    if td_lvl is not None:
        if td_lvl is NullGroup:
            stop_index = None
        else:
            stop_index = case._helper._level_stack.index(td_lvl)
        teardown_groups = case._helper._level_stack[:stop_index:-1]
        if case._group._cascading_failure_in_progress:
            ignored_teardown_groups = list(teardown_groups)
            for group in ignored_teardown_groups:
                if not group._cascading_failure_root:
                    LOGGER.debug(
                        "CASCADING FAILURE - Not tearing down group:\n{}"
                        .format(
                            group._get_full_ancestry_description(True),
                        ),
                    )
                    teardown_groups.remove(group)
                    case._helper._level_stack.remove(group)
                else:
                    break
        if teardown_groups:
            if td_lvl is NullGroup:
                end_desc = "  (Null)"
            else:
                end_desc = td_lvl._get_full_ancestry_description(True)
            LOGGER.debug(
                "Tearing down group:\n{}\nto:\n{}".format(
                    case._group._get_full_ancestry_description(True),
                    end_desc,
                ),
            )
            for group in teardown_groups:
                if group in case._helper._level_stack:
                    LOGGER.debug(
                        "Tearing down group:\n{}"
                        .format(
                            group._get_full_ancestry_description(True),
                        ),
                    )
                    start_time = time()
                    try:
                        group._teardown_group()
                    except:
                        # handle error during group setup
                        excinfo = ExceptionInfo()
                        stop_time = time()
                        nodeid = "  " * group._level + group._description
                        location = group
                        keywords = {}
                        outcome = "failed"
                        longrepr = excinfo.getrepr()
                        when = "teardown"
                        sections = []
                        duration = stop_time - start_time
                        context_lines = [
                            "Context:",
                            "",
                        ]
                        for group in list(reversed(group._ancestry)):
                            context_lines.append(
                                "  {}{}".format(
                                    "  " * group._level,
                                    group._description,
                                ),
                            )
                        context_lines[-1] = ">" + context_lines[-1][1:]
                        entry = ReprEntry(context_lines, None, None, None, "long")
                        if hasattr(longrepr, "chain"):
                            reprtraceback = longrepr.chain[0][0]
                        else:
                            reprtraceback = longrepr.reprtraceback
                        reprtraceback.reprentries.insert(0, entry)
                        report = TestReport(
                            nodeid,
                            location,
                            keywords,
                            outcome,
                            longrepr,
                            when,
                            sections,
                            duration,
                        )
                        item.ihook.pytest_runtest_logreport(report=report)



class ContextionalTerminalReporter(TerminalReporter):

    def __init__(self, reporter):
        TerminalReporter.__init__(self, reporter.config)
        self._tw = reporter._tw
        self._sessionstarttime = reporter._sessionstarttime

    def pytest_runtest_logstart(self, nodeid, location):
        # ensure that the path is printed before the
        # 1st test of a module starts running
        if self.showlongtestinfo:
            if isinstance(location, Case):
                self.setup_contextional_groups(nodeid, location)
                line = "  " * (location._group._level + 1) + nodeid + " "
                self.write_ensure_prefix(line, "")
            else:
                line = self._locationline(nodeid, *location)
                self.write_ensure_prefix(line, "")
        elif self.showfspath:
            fsid = nodeid.split("::")[0]
            self.write_fspath_result(fsid, "")

    def setup_contextional_groups(self, nodeid, location):
        __tracebackhide__ = True
        setup_ancestry = list(reversed(location._group._ancestry))
        for group in setup_ancestry:
            if group not in group._helper._level_stack:
                line = "  " * group._level
                line += group._description + " "
                self.write_ensure_prefix(line, "")
                start_time = time()
                try:
                    group._setup_group()
                except:
                    # handle error during group setup
                    excinfo = ExceptionInfo()
                    stop_time = time()
                    nodeid = "  " * group._level + group._description
                    location = group
                    keywords = {}
                    outcome = "failed"
                    longrepr = excinfo.getrepr()
                    when = "setup"
                    sections = []
                    duration = stop_time - start_time
                    context_lines = [
                        "Context:",
                        "",
                    ]
                    for group in list(reversed(group._ancestry)):
                        context_lines.append(
                            "  {}{}".format(
                                "  " * group._level,
                                group._description,
                            ),
                        )
                    context_lines[-1] = ">" + context_lines[-1][1:]
                    entry = ReprEntry(context_lines, None, None, None, "long")
                    if hasattr(longrepr, "chain"):
                        reprtraceback = longrepr.chain[0][0]
                    else:
                        reprtraceback = longrepr.reprtraceback
                    reprtraceback.reprentries.insert(0, entry)
                    report = TestReport(
                        nodeid,
                        location,
                        keywords,
                        outcome,
                        longrepr,
                        when,
                        sections,
                        duration,
                    )
                    self.pytest_runtest_logreport(report)

    def pytest_runtest_logreport(self, report):
        # write output after test name while tests are still running
        rep = report
        res = self.config.hook.pytest_report_teststatus(report=rep)
        cat, letter, word = res
        self.stats.setdefault(cat, []).append(rep)
        self._tests_ran = True
        if not letter and not word:
            # probably passed setup/teardown
            return
        if self.verbosity <= 0:
            if not hasattr(rep, 'node') and self.showfspath:
                self.write_fspath_result(rep.nodeid, letter)
            else:
                self._tw.write(letter)
        else:
            if isinstance(word, tuple):
                word, markup = word
            else:
                if rep.passed:
                    markup = {'green':True}
                elif rep.failed:
                    markup = {'red':True}
                elif rep.skipped:
                    markup = {'yellow':True}
            if isinstance(rep.location, (Group, Case)):
                line = rep.nodeid + " "
                self.write_ensure_prefix(line, word, **markup)
            else:
                line = self._locationline(rep.nodeid, *rep.location)
                if not hasattr(rep, 'node'):

                    self.write_ensure_prefix(line, word, **markup)
                    #self._tw.write(word, **markup)
                else:
                    self.ensure_newline()
                    if hasattr(rep, 'node'):
                        self._tw.write("[%s] " % rep.node.gateway.id)
                    self._tw.write(word, **markup)
                    self._tw.write(" " + line)
                    self.currentfspath = -2

    def summary_failures(self):
        if self.config.option.tbstyle != "no":
            reports = self.getreports('failed')
            if not reports:
                return
            self.write_sep("=", "FAILURES")
            for rep in reports:
                if self.config.option.tbstyle == "line":
                    line = self._getcrashline(rep)
                    self.write_line(line)
                else:
                    if isinstance(rep.location, Case):
                        msg = rep.location._group._root_group._description
                    else:
                        msg = self._getfailureheadline(rep)
                    markup = {'red': True, 'bold': True}
                    self.write_sep("_", msg, **markup)
                    self._outrep_summary(rep)
                    for report in self.getreports(''):
                        if report.nodeid == rep.nodeid and report.when == 'teardown':
                            self.print_teardown_sections(report)

    def summary_errors(self):
        if self.config.option.tbstyle != "no":
            reports = self.getreports('error')
            if not reports:
                return
            self.write_sep("=", "ERRORS")
            for rep in self.stats['error']:
                if isinstance(rep.location, Case):
                    msg = rep.location._group._root_group._description
                elif isinstance(rep.location, Group):
                    msg = rep.location._root_group._description
                else:
                    msg = self._getfailureheadline(rep)
                if not hasattr(rep, 'when'):
                    # collect
                    msg = "ERROR collecting " + msg
                elif rep.when == "setup":
                    if isinstance(rep.location, Group):
                        msg = "ERROR at setup of " + rep.location._description
                    else:
                        msg = "ERROR at setup of " + msg
                elif rep.when == "teardown":
                    if isinstance(rep.location, Group):
                        msg = "ERROR at teardown of " + rep.location._description
                    else:
                        msg = "ERROR at teardown of " + msg
                self.write_sep("_", msg)
                self._outrep_summary(rep)


def pytest_runtest_makereport(item, call):
    when = call.when
    duration = call.stop-call.start
    keywords = dict([(x,1) for x in item.keywords])
    excinfo = call.excinfo
    sections = []
    if not call.excinfo:
        outcome = "passed"
        longrepr = None
    else:
        if not isinstance(excinfo, ExceptionInfo):
            outcome = "failed"
            longrepr = excinfo
        elif excinfo.errisinstance(skip.Exception):
            outcome = "skipped"
            r = excinfo._getreprcrash()
            longrepr = (str(r.path), r.lineno, r.message)
        else:
            outcome = "failed"
            if call.when == "call":
                if isinstance(item.location, Case):
                    longrepr = item.repr_failure(excinfo)
                    context_lines = "Context:\n\n"
                    ancestry = list(reversed(item.location._group._ancestry))
                    for group in ancestry:
                        context_lines += "  {indent}{description}\n".format(
                            indent=("  " * group._level),
                            description=group._description,
                        )
                    context_lines += "> {description}\n".format(
                        description=item.nodeid,
                    )
                    context_lines = context_lines.split("\n")
                    if excinfo.errisinstance(CascadingFailureError):
                        context_lines.append("E       CASCADING FAILURE")

                    entry = ReprEntry(context_lines, None, None, None, "long")
                    if hasattr(longrepr, "chain"):
                        reprtraceback = longrepr.chain[0][0]
                    else:
                        reprtraceback = longrepr.reprtraceback
                    if excinfo.errisinstance(CascadingFailureError):
                        reprtraceback.reprentries[0] = entry
                    else:
                        reprtraceback.reprentries.insert(0, entry)
                else:
                    longrepr = item.repr_failure(excinfo)
            else: # exception in setup or teardown
                longrepr = item._repr_failure_py(excinfo,
                                            style=item.config.option.tbstyle)
    for rwhen, key, content in item._report_sections:
        sections.append(("Captured %s %s" %(key, rwhen), content))
    return TestReport(item.nodeid, item.location,
                      keywords, outcome, longrepr, when,
                      sections, duration)
