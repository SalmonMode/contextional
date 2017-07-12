[![Build status][bs-img]][bs-link]
[![PyPI version][ppv-img]][ppv-link]
[![Docs][docs-img]][docs-link]

# Contextional
A context-based functional testing tool for Python

## Installation

To install it, just run:

```shell
pip install contextional
```

## "contex-tional?"

It's a portmanteau of the words "context" and "functional". These words were chosen because the tool works by using context managers (`with` statements), and allows you to write functional tests (testing as you go).

## What does it do?

Contextional does 3 things:

1. It gives you more organized test output by breaking tests into a hierarchical structure based on how the tests were defined, letting you provide descriptive names for each layer of the hierarchy as well as the tests themselves.
2. It lets you predefine a hierarchy of tests that can be easily reused in as many places as you'd like.
3. It allows you to control the exact order in which your tests and fixtures occur, which can be extremely useful for writing comprehensive, functional test suites where you need to test as you go.

## What does it look like?

### code:

```python
from contextional import GCM


with GCM("Predefined Group") as PG:

    @GCM.add_test("value is still 2")
    def test(case):
        case.assertEqual(
            GCM.value,
            2,
        )


with GCM("Main Group") as MG:

    @GCM.add_setup
    def setUp():
        GCM.value = 0

    @GCM.add_test_setup
    def testSetUp():
        GCM.value += 1

    @GCM.add_test("value is 1")
    def test(case):
        case.assertEqual(
            GCM.value,
            1,
        )

    @GCM.add_test("value is 2")
    def test():
        assert GCM.value == 2

    with GCM.add_group("Child Group"):

        @GCM.add_setup
        def setUp():
            GCM.value += 1

        @GCM.add_test("value is now 3")
        def test():
            assert GCM.value == 3

        @GCM.add_teardown
        def tearDown():
            GCM.value -= 1

    GCM.includes(PG)


MG.create_tests()
```

### output

```
Main Group
  value is 1 ... ok
  value is 2 ... ok
  Child Group
    value is now 3 ... ok
  Predefined Group
    value is still 2 ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.008s

OK
```

[bs-img]: https://travis-ci.org/SalmonMode/contextional.svg?branch=master
[bs-link]: https://travis-ci.org/SalmonMode/contextional
[ppv-img]: https://badge.fury.io/py/contextional.svg
[ppv-link]: https://badge.fury.io/py/contextional
[docs-img]: https://readthedocs.org/projects/pip/badge/
[docs-link]: http://contextional.readthedocs.io/
