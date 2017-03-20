# `contextional`
A context-based functional testing tool for Python

## Installation

To install it, just run:

```shell
pip install contextional
```

## "`contex`-`tional`?"

It's a portmanteau of the words "context" and "functional". These words were chosen because the tool works by using context managers (`with` statements), and allows you to write functional tests (testing as you go).

## What does it do?

`contextional` does 3 things:

1. It gives you more organized test output by breaking tests into a hierarchical structure based on how the tests were defined, letting you provide descriptive names for each layer of the hierarchy as well as the tests themselves.
2. It lets you predefine a heirarchy of tests that can be easily reused in as many places as you'd like.
3. It allows you to control the exact order in which your tests and fixtures occur, which can be extremely useful for writing comprehensive, functional test suites where you need to test as you go.

## What does it look like?

### code:

```python
from contextional import GroupContextManager


with GroupContextManager("Predefined Group") as predefined_c:

    @predefined_c.add_test("value is still 2")
    def test(case):
        case.assertEqual(
            predefined_c.value,
            2,
        )


with GroupContextManager("Main Group") as c:

    @c.add_setup
    def setUp():
        c.value = 0

    @c.add_test_setup
    def testSetUp():
        c.value += 1

    @c.add_test("value is 1")
    def test(case):
        case.assertEqual(
            c.value,
            1,
        )

    @c.add_test("value is 2")
    def test():
        assert c.value == 2

    with c.add_group("Child Group"):

        @c.add_setup
        def setUp():
            c.value += 1

        @c.add_test("value is now 3")
        def test():
            assert c.value == 3

        @c.add_teardown
        def tearDown():
            c.value -= 1

    c.includes(predefined_c)


c.create_tests(globals())
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
