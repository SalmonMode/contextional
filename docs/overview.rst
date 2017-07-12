.. _overview:

========
Overview
========

Why Use Contextional?
~~~~~~~~~~~~~~~~~~~~~

**Short answer**

* fast and easy to use
* works with ``unittest``, ``unittest2``, ``nose``, and ``pytest``
* deterministic fixture and test order without being tied to a class
* might significantly improve functional test suite run time
* much better test output organization and readability (doesn't even need to be
  used for functional tests)

**Long answer**

If you use the standard ``unittest``\ /\ ``unittest2`` libraries to write
functional tests, you're likely to have a very complicated test suite, as the
only thing you should have in each test method should be a single assert, your
test classes should each only pertain to one specific scenario, and the setups
and teardowns for each test class should be completely isolated from and
independant of all the other test classes.

The more complex the thing you're testing is, the more scenarios you'll have to
cover, which means more test classes that you'll have to write. A properly made
functional test suite for a decently complex product can easily take a very
long time to run, as each test class will have to run every bit of setup
required for it to run and then completely tear it all down once it's finished
running all its tests.

It's not a best practice to have a test class try and rely on any previously
run classes when writing tests in the traditional fashion, as the order they
run in isn't deterministic.

That's where Contextional comes in.

Contextional uses a combination of ``with`` statements and decorators to let
you quickly and easily define fixtures and tests with easy-to-read descriptions
for each context and test. This is done to make sure each fixture and test
happens in a logical and deterministic order and that the test output is
organized and more idiomatic.

Installation
~~~~~~~~~~~~

You can install Contextional through ``pip`` with:

.. code-block:: none

    $ pip install contextional

Quick Example
~~~~~~~~~~~~~

Code::

    from contextional import GroupContextManager as GCM


    with GCM("Main Group") as MG:

        @GCM.add_setup
        def setUp():
            GCM.value = 1

        @GCM.add_test("value is 1")
        def test(case):
            case.assertEqual(GCM.value, 1)

        with GCM.add_group("Child Group"):

            @GCM.add_setup
            def setUp():
                GCM.value += 1

            @GCM.add_test("value is now 2")
            def test(case):
                case.assertEqual(GCM.value, 2)

    MG.create_tests()

Test output:

.. code-block:: none

    Main Group
      value is 1 ... ok
      Child Group
        value is now 2 ... ok
