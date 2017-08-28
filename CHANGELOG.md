# Changelog

## [Unreleased]
### Fixed
- Actually fixed group description not displaying when running with nose and a
parent group caused a cascading failure.

## [1.4.1] - 2017-08-28
### Fixed
- Group description wasn't displaying when running with nose and a parent
group caused a cascading failure.
- Changelog.

## [1.4.0] - 2017-07-12
### Added
- ``GCM`` is now a built in alias for ``GroupContextManager``.

### Changed
- No longer need to use the name of the context manager (created with
``GroupContextManager``) to add tests/fixtures.
- No longer need to use the name of the context manager (created with
``GroupContextManager``) to access the shared namespace.
- Updated documentation.

## [1.3.1] - 2017-06-26
### Fixed
- No longer interferes with nose's ResultProxy class.

## [1.3.0] - 2017-06-23
### Changed
- ``globals()`` no longer needs to be passed to ``create_tests()``. NOTE: The
only reason this implementation works is due to the nature of ``locals()`` and
namespaces of modules always being implemented by a ``dict``. Luckily, test
loaders will almost always be looking at the namespace of modules (and you'll
likely only be putting Contextional tests in a module's namespace), so this
will work for almost all scenarios. For those that this doesn't work for, the
namespace object that you want to add the tests to can just be passed as an
argument to ``create_tests()``.
- Documentation to reflect the changes to ``create_tests()``.

### Fixed
- ``__init__()`` in ``Helper`` not calling parent's (``unittest.TestCase``)
``__init__()``.

## [1.2.1] - 2017-06-23
### Added
- Test suite for setuptools.

### Changed
- Updated readme.
- Removed unused code.
- Adjusted test structure to avoid accidental test discovery.
- How package info is stored (now only one file needs to be modified each
release to change the version number).
- Travis-CI script so that it uses the standard setuptools test command.

### Fixed
- Changelog release heading links.
- Some documentation.
- ``GroupTestCase.setUp`` and ``GroupTestCase.tearDown`` no longer show up in
pytest traceback.

## [1.2.0] - 2017-06-22
### Added
- Markdown links to version tags for release headings.
- Simple tests.
- Integration with Travis-CI.
- Shields to README.

### Changed
- Only ``Case`` objects should consider whether or not arguments need to be
passed to them.
- Removed ``get_level_stack``, as it was unnecessary.
- Dropped support for Python 2.6.

### Fixed
- Fixed line breaks in the changelog.
- Deprecation warnings about ``inspect.getargspec`` when using Python 3.

## [1.1.0] - 2017-06-21
### Added
- This CHANGELOG.
- Tests now write out Group descriptions as setups for those Groups are ran in
both pytest and nose (or any other testing framework that runs tests from
``unittest.TestCase`` classes in the standard fashion).
- Errors in Group setups and teardowns will be shown next to the Group's
description as they are written out during test runtime. If an error occurs
during a Group teardown, the Group's description will be written out again so
the error status can be shown next to it.

### Changed
- Cleaned up code by putting certain, common operations into functions and/or
properties.

### Fixed
- Logging level going to error instead of debug.
- Group setup errors not being raised.
- Test status now shows up properly in pytest when running the tests in a
non-verbose mode. This includes errors that occur during a Group setup or
teardown.

## [1.0.0] - 2017-06-14
### Added
- Robust support for ``pytest``.

## [0.9.0] - 2017-06-05
### Added
- More documentation regarding how to write advanced tests.

### Changed
- Only ``Group`` setUps should trigger a cascading failure. Tests should not
cause a cascading failure. If there is some criteria that must be validated in
order for a series of tests to be run, then that criteria should be validated
during the setUp of that ``Group``. This can, and should, influence how your
``Group``s and tests are structured
- Cascading failures are now on by default. It can be disabled for the setUps
of a particular ``Group`` by passing ``cascading_failure=False`` as a parameter
along with that ``Group``'s description.

### Fixed
- Some syntax in the documentation.

## [0.8.9] - 2017-06-02
### Added
- Cascading Failures. It can be enabled for the setUps of a particular
``Group`` by passing ``cascading_failure=True`` as a parameter along with that
``Group``'s description. If enabled, if the setUps or tests for a ``Group``
have an issue (error or failure), of the remaining setUps and tests of that
``Group`` (including those of descendant ``Group``s), the setUps will be
skipped, and the tests will automatically fail to show how widespread the
issue is.

### Fixed
- Indentation of the test's description in the header of failure reports.

## [0.8.8] - 2017-06-02
### Added
- Support for passing multiple ``GroupContextManager``s to ``includes`` and
``combine`` methods.

## [0.8.7] - 2017-06-01
### Changed
- Improved logging.

## [0.8.6] - 2017-06-01
### Fixed
- Teardown behavior.
 - Unified behavior with new classmethod, ``_teardown_to_level``.
 - Root level teardowns now fire properly when finishing tests without any
 issues.
 - ``helper`` now clears the level stack once all tests are during (on
 ``__del__`` of ``helper``) by running all teardowns of all ``Group``s still
 in the level stack, in the appropriate order.

## [0.8.5] - 2017-05-31
### Added
- Logging.

### Fixed
- Test name shown in fixture error report.

## [0.8.4] - 2017-04-18
### Changed
- Cleaned up code.

## [0.8.3] - 2017-04-18
### Fixed
- Should use ``__all__`` in ``__init__.py``, and only import what's
necessary.

## [0.8.2] - 2017-04-17
### Fixed
- Now shows context of Group-level fixture errors in the error report.

## [0.8.1] - 2017-03-27
### Changed
- ``merge`` is now ``combine``.

## [0.8.0] - 2017-03-22
### Added
- Ability to merge the contents of the root ``Group`` of one
``GroupContextManager`` with any ``Group`` of another ``GroupContextManager``,
using the ``merge`` method.

## [0.7.7] - 2017-03-22
### Added
- Now shows the full context of a test in the header of the failure report.

## [0.7.6] - 2017-03-21
### Fixed
- ``utilize_asserts`` now properly grabs functions that do not have a
``__func__``, and functions that aren't methods.

## [0.7.5] - 2017-03-21
### Fixed
- Forward compatibility issue caused by ``im_func``.

## [0.7.4] - 2017-03-20
### Fixed
- ``zip`` objects have no ``len`` in Python 3.

## [0.7.3] - 2017-03-20
### Changed
- This shouldn't refer to itself as a "DSL". It sounds weird and doesn't seem
to fit, since it uses standard Python syntax.

## [0.7.2] - 2017-03-20
### Changed
- Teardowns no longer take parameters. Only setUps should take them.

### Added
- Documentation using Sphinx.

## [0.7.1] - 2017-03-19
### Changed
- Docstrings now use Sphinx syntax.

## [0.7.0] - 2017-03-15
### Added
- Support for parameterized ``Group``s.

## [0.6.6] - 2017-03-15
### Fixed
- Docstring of ``runTest`` affecting test representation.

## [0.6.5] - 2017-03-13
### Added
- Docstrings.

## [0.6.0] - 2017-03-13
### Added
- Ability to use custom assert methods with ``utilize_asserts``.

## [0.5.1] - 2017-03-09
### Changed
- ``GroupContextManager`` can be its own context manager.
- Upgraded README

## [0.5.0] - 2017-03-09
### Added
- Contextional

[Unreleased]: https://github.com/SalmonMode/contextional/compare/1.4.1...HEAD
[1.4.1]: https://github.com/SalmonMode/contextional/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/SalmonMode/contextional/compare/1.3.1...1.4.0
[1.3.1]: https://github.com/SalmonMode/contextional/compare/1.3.0...1.3.1
[1.3.0]: https://github.com/SalmonMode/contextional/compare/1.2.1...1.3.0
[1.3.0]: https://github.com/SalmonMode/contextional/compare/1.2.1...1.3.0
[1.2.1]: https://github.com/SalmonMode/contextional/compare/1.2.0...1.2.1
[1.2.0]: https://github.com/SalmonMode/contextional/compare/1.1.0...1.2.0
[1.1.0]: https://github.com/SalmonMode/contextional/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/SalmonMode/contextional/compare/0.9.0...1.0.0
[0.9.0]: https://github.com/SalmonMode/contextional/compare/0.8.9...0.9.0
[0.8.9]: https://github.com/SalmonMode/contextional/compare/0.8.8...0.8.9
[0.8.8]: https://github.com/SalmonMode/contextional/compare/0.8.7...0.8.8
[0.8.7]: https://github.com/SalmonMode/contextional/compare/0.8.6...0.8.7
[0.8.6]: https://github.com/SalmonMode/contextional/compare/0.8.5...0.8.6
[0.8.5]: https://github.com/SalmonMode/contextional/compare/0.8.4...0.8.5
[0.8.4]: https://github.com/SalmonMode/contextional/compare/0.8.3...0.8.4
[0.8.3]: https://github.com/SalmonMode/contextional/compare/0.8.2...0.8.3
[0.8.2]: https://github.com/SalmonMode/contextional/compare/0.8.1...0.8.2
[0.8.1]: https://github.com/SalmonMode/contextional/compare/0.8.0...0.8.1
[0.8.0]: https://github.com/SalmonMode/contextional/compare/0.7.7...0.8.0
[0.7.7]: https://github.com/SalmonMode/contextional/compare/0.7.6...0.7.7
[0.7.6]: https://github.com/SalmonMode/contextional/compare/0.7.5...0.7.6
[0.7.5]: https://github.com/SalmonMode/contextional/compare/0.7.4...0.7.5
[0.7.4]: https://github.com/SalmonMode/contextional/compare/0.7.3...0.7.4
[0.7.3]: https://github.com/SalmonMode/contextional/compare/0.7.2...0.7.3
[0.7.2]: https://github.com/SalmonMode/contextional/compare/0.7.1...0.7.2
[0.7.1]: https://github.com/SalmonMode/contextional/compare/0.7.0...0.7.1
[0.7.0]: https://github.com/SalmonMode/contextional/compare/0.6.6...0.7.0
[0.6.6]: https://github.com/SalmonMode/contextional/compare/0.6.5...0.6.6
[0.6.5]: https://github.com/SalmonMode/contextional/compare/0.6.0...0.6.5
[0.6.0]: https://github.com/SalmonMode/contextional/compare/0.5.1...0.6.0
[0.5.1]: https://github.com/SalmonMode/contextional/compare/0.5.0...0.5.1
