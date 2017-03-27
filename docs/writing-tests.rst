.. _writing-tests:

#############
Writing Tests
#############

The Basics
**********

Contextional utilizes contexts (\ ``with`` statements) so you can easily
control how your tests and fixtures play out.

You should know that any code you've written along side your fixture and test
definitions is getting run, so you can use this to your advantage to influence
how your fixtures and tests get defined. But none of the tests or fixtures you
defined will get used if you don't call :meth:`.create_tests` on the
:class:`.GroupContextManager` instance that you made (see below for
example usage).

This might seem odd, but it's required for two reasons:

1. It allows you to create a :class:`.GroupContextManager`, containing
   layers of tests and fixtures, that can be included in other
   :class:`.GroupContextManager` objects, and it will only get run if
   :meth:`.create_tests` is called by those :class:`.GroupContextManager`
   objects.
2. Contextional needs to modify the global namespace of the module you want the
   tests to be created in so that it can create the :class:`unittest.TestCase`
   classes in it, which is why you must pass :func:`.globals` to
   :meth:`.create_tests`.

**TL;DR** The examples below should answer most questions you have.

Order of Fixture Execution
==========================

Setups
------

When enterring a layer, all of the setups defined in that layer are executed,
in the order that they were defined.

Test Setups
-----------

Test-level setups are executed before every test that is defined in the same
layer as them.

Test Teardowns
--------------

Test-level teardowns are executed after every test that is defined in the same
layer as them.

Teardowns
---------

When exiting a layer (i.e. the tests defined in the layer and all of the
layer's descendant layers have all been executed), all of the teardowns defined
in that layer are executed, in the order that they were defined.

.. warning::
    Fixtures will only be executed for the layer that they are defined in.

    Test-level fixtures will only be used for the tests that were declared in
    the same layer that they were, and none of the tests in any descendant
    layers will execute them.

    Layer-level fixtures only execute once. Even if the layer that they were
    defined in has more than one child layer, they will still only be executed
    once.

.. warning::
    If a layer has no tests, nor does any of its descendant layers, then any
    fixtures declared in that layer will not be executed.

.. note::
    It doesn't matter if you define fixtures before or after fixtures of
    different types, tests, or child layers. The order in which you define a
    fixture is only relevant when compared to other fixtures of the same type.

    For example, you can define ``setup A``, then ``test 1``, and then ``setup
    B``, but ``setup A`` will still be executed before ``setup B``, and ``setup
    B`` will still be executed before ``test 1``.

Alternate Explanation
---------------------

Here's some pseudocode that might help clarify::

    def run_layer_tests(layer):
        # layer setups
        for setup in layer.setups:
            setup()

        # tests
        for test in layer.tests:
            # test setups
            for test_setup in layer.test_setups:
                test_setup()

            test()

            # test teardowns
            for test_teardown in layer.test_teardowns:
                test_teardown()

        # child layers
        for child_layer in layer.children:
            run_layer_tests(child_layer)

        # layer teardowns
        for teardown in layer.teardowns:
            teardown()

Getting Started
===============

Do I need to install anything?
------------------------------

Yes, you'll need to install ``contextional`` through ``pip``, like so:

.. code-block:: none

    $ pip install contextional

Do I need to import anything?
-----------------------------

Yes, but luckily, you only need to import :class:`.GroupContextManager`, like
this::

    from contextional import GroupContextManager

How do I create the first layer?
--------------------------------

To create the first layer, you'll just need to import
:class:`.GroupContextManager` and use a ``with`` statement to create a
:class:`.GroupContextManager` instance while giving the first layer of that
:class:`.GroupContextManager` a description. That instance is what you'll be
using to add fixtures, tests, and child layers.

Here's what this looks like::

    from contextional import GroupContextManager


    with GroupContextManager("First Layer") as FL:

Here we've given the first layer a description of "First Layer", and created a
:class:`.GroupContextManager` instance, ``FL``, that we can use to add
fixtures, tests, and child layers.

How do I add a test?
--------------------

For that, you would use :meth:`.GroupContextManager.add_test`, which is a
decorator that takes a single argument (the description of the test).

Here's what it will look like once we've added a test::

    from contextional import GroupContextManager


    with GroupContextManager("First Layer") as FL:

        @FL.add_test("1 is True")
        def test(case):
            case.assertTrue(1)

How do I get the tests to run?
------------------------------

After you're done defining everything, you may have noticed that your tests
didn't actually run. That's likely because you will need to have your
:class:`.GroupContextManager` call :meth:`.create_tests`, and make sure you
pass it :func:`.globals` as an argument. This is what creates the stuff that
your testing framework will actually use.

Here's what it looks like::

    from contextional import GroupContextManager


    with GroupContextManager("First Layer") as FL:

        @FL.add_test("1 is True")
        def test(case):
            case.assertTrue(1)


    FL.create_tests(globals())

With that, you can just use your testing framework like you normally would, and
it will automatically detect and run these tests (assuming it works with tests
made with ``unittest``). For example, if you use ``nosetests`` to run your
tests, you can just run it like this:

.. code-block:: none

    $ nosetests -v

If you do that, the test output for this would look something like this:

.. code-block:: none

    First Layer
      1 is True ... ok

Do I have to name the test "\ ``test``\ "?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Not at all; you can name it whatever you want. I just find that giving it a
name of ``test`` makes it easy and straightforward to read. But if you would
prefer to name it something else, you absolutely can. The same goes for
fixtures, as well.

In fact, every test and fixture that you define and decorate using the
:class:`.GroupContextManager`'s decorator methods will not exist after the
decorator is evaluated, as the decorator doesn't return a function to replace
it. This was done intentionally so that nothing is leftover that could
be found by the test discovery process that you wouldn't want to be found.

Does the test have to take an argument?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Nope. But if you have it take an argument, you can use that argument to access
the :class:`unittest.TestCase` assert method and any assert methods you
provided with :class:`.GroupContextManager.utilize_asserts`.

Does the argument that the test takes have to be named "\ ``case``\ "?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Nope. It can be named whatever you want. Naming it "\ ``case``\ " is just a
suggestion.

Can the test take more than one argument?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Nope. It's either no arguments, or one argument.

If you're looking to do something like paramaterized tests, Contextional does
support it, but you'll have to go to the "Advanced" section below to find out
more about how to do that.

How do I add fixtures (i.e. setups and teardowns)?
--------------------------------------------------

Adding fixtures is also done through a decorator. You have the following
options for fixtures:

* :meth:`.GroupContextManager.add_setup`
* :meth:`.GroupContextManager.add_test_setup`
* :meth:`.GroupContextManager.add_test_teardown`
* :meth:`.GroupContextManager.add_teardown`


To add a setup for the layer, you would do something like this::

    from contextional import GroupContextManager


    with GroupContextManager("Main Group") as MG:

        @MG.add_setup
        def setUp():
            MG.value = 1

        @MG.add_test("value is 1")
        def test(case):
            case.assertEqual(MG.value, 1)


    MG.create_tests(globals())

And with that, our test output would look like this:

.. code-block:: none

    Main Group
        value is 1 ... ok

You would take the same approach for all the other fixture types.

Can I have a layer with fixtures, but no tests?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yes, but in order for it to be used, that layer must have a descendant layer
that has tests. Otherwise, it will be ignored.

Also, if the fixtures are test-level fixtures (i.e. test setups and test
teardowns), then they will definitely not be used if there aren't any tests
defined in the same layer.

How do I predefine a :class:`.GroupContextManager` that I can use elsewhere?
----------------------------------------------------------------------------

Whenever you define a :class:`.GroupContextManager`, it doesn't *need* to have
its tests run. That only happens if you have it call :meth:`.create_tests`.
However, you can create a :class:`.GroupContextManager`, which contains layers
of fixtures and tests, that you can include in any other
:class:`.GroupContextManager` at any point, and even use it multiple times in
the same :class:`.GroupContextManager`.

To do this, you just need to create a :class:`.GroupContextManager` containing
the layers and fixtures that you want to use elsewhere, using the exact same
syntax that you would use with any other :class:`.GroupContextManager`, but
don't have it call :meth:`.create_tests`. Once you've done this, go to where
you are creating the :class:`.GroupContextManager` that you want to include
your predefined :class:`.GroupContextManager`, and have it call
:meth:`.includes` at the point that you want it to include the predefined
:class:`.GroupContextManager`.

The process looks something like this::

    from contextional import GroupContextManager


    with GroupContextManager("Predefined Group") PG:

        @PG.add_setup
        def setUp():
            PG.value += 1

        @PG.add_test("value is now 2")
        def test(case):
            case.assertEqual(PG.value, 2)


    with GroupContextManager("Main Group") as MG:

        @MG.add_setup
        def setUp():
            MG.value = 1

        @MG.add_test("value is 1")
        def test(case):
            case.assertEqual(MG.value, 1)

        MG.includes(PG)


    MG.create_tests(globals())

The output for this would look something like this:

.. code-block:: none

    Main Group
      value is 1 ... ok
      Predefined Group
        value is now 2 ... ok

Can I use the predefined :class:`.GroupContextManager` in more than one spot?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yep!

Even multiple times in the same :class:`.GroupContextManager`?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Yup!

What about in other modules than the one I created it in?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Absolutely!

The :class:`.GroupContextManager` that you want to include in other any
:class:`.GroupContextManager` is just like any other object. Even though it was
created using context managers, nothing really happens to it once the outermost
context is exited. Because of this, all you need to do is import it in the
module you want to use it.

So if you started it off by saying::

    with GroupContextManager("Includable Group") as IG:

then you would only need to say this in the module that would use it::

    from some.module import IG

What if I want to include the predefined tests, fixtures, and/or child groups
from a :class:`.GroupContextManager` alongside those from my current group?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can just use :meth:`combine`, then. It takes the tests, fixtures, and child
groups of a :class:`.GroupContextManager` and makes them part of the group
you're merging them into, so they won't just be added as a child group.

This is useful if you know you are going to be using identical tests but on
different things.

It looks something like this::

    def multiplier(num_1, num_2):
        return num_1 * num_2


    with GroupContextManager("value test") as vt:

        @vt.add_test("value")
        def test(case):
            case.assertEqual(
                vt.value,
                vt.expected_value,
            )

    with GroupContextManager("Main Group") as MG:

        with MG.add_group("2 and 3"):

            @MG.add_setup
            def setUp():
                MG.value = multiplier(2, 3)
                MG.expected_value = 6

            MG.combine(vt)

        with MG.add_group("3 and 5"):

            @MG.add_setup
            def setUp():
                MG.value = multiplier(3, 5)
                MG.expected_value = 15

            MG.combine(vt)


Output:

.. code-block:: none

    Main Group
      value is 1 ... ok
      Sub Group
        value is still 1 ... ok

How can my fixtures and tests use persistent resources as they run?
------------------------------------------------------------------------

Normally, when working with :class:`unittest.TestCase`, you could use class
attributes in :meth:`setUpClass` or :meth:`tearDownClass` (i.e. :obj:`cls`), or
instance attributes in :meth:`setUp` or :meth:`tearDown` (i.e. :obj:`self`) to
give your fixtures and tests access to persistent resources.

To let you do something similar, Contextional uses some Python magic to let
each :class:`.GroupContextManager` access a shared, persistent namespace.

You may have noticed it in the examples above, but the shared, persistent
namespace is accessed through the variable name for whatever
:class:`.GroupContextManager` you are building at that moment. For example,
take a look at the following code::

    from contextional import GroupContextManager


    with GroupContextManager("Predefined Group") PG:

        @PG.add_test("value is 1")
        def test(case):
            case.assertEqual(PG.value, 1)


    with GroupContextManager("Main Group") as MG:

        @MG.add_setup
        def setUp():
            MG.value = 1

        MG.includes(PG)


    MG.create_tests(globals())

In the test, while building the :class:`.GroupContextManager` named ``PG``,
\ ``PG.value`` is referenced, but at no point was a ``PG.value`` set...

... or so it would seem.

While building ``MG``, in its ``setUp``, we set ``MG.value`` to ``1``. That's
where ``PG.value`` gets set. This is because both ``MG`` and ``PG`` are
accessing the same persistent namespace in order to store and reference
resources.

**TL;DR** Make the resource an attribute of the :class:`.GroupContextManager`
that you're currently building (this should be done in a fixture), and other
fixtures and tests can reference it as an attribute of the
:class:`.GroupContextManager` that they were defined in.

For an example, check out how the code above handles the ``value`` attribute of
the ``MG`` and ``PG`` :class:`.GroupContextManager` instances.

Can I see a simple example to get me started?
--------------------------------------------------

Sure! Here you go::

    from contextional import GroupContextManager


    with GroupContextManager("Predefined Group") PG:

        @PG.add_test("value is still 1")
        def test(case):
            case.assertEqual(PG.value, 1)


    with GroupContextManager("Main Group") as MG:

        @MG.add_setup
        def setUp():
            MG.value = 1

        @MG.add_test("value is 1")
        def test(case):
            case.assertEqual(MG.value, 1)

        MG.includes(PG)

        with MG.add_group("Child Group"):

            @MG.add_setup
            def setUp():
                MG.value += 1

            @MG.add_test("value is now 2")
            def test(case):
                case.assertEqual(MG.value, 2)

        with MG.add_group("Another Child Group"):

            @MG.add_setup
            def setUp():
                MG.value += 1

            @MG.add_test("value is now 3")
            def test(case):
                case.assertEqual(MG.value, 3)

That would output the following:

.. code-block:: none

    Main Group
      value is 1 ... ok
      Predefined Group
        value is still 1 ... ok
      Child Group
        value is now 2 ... ok
      Another Child Group
        value is now 3 ... ok

Advanced Usage
**************

Parameterization
================

Contextional handles parameterization by allowing you to pass
parameters to :meth:`.add_group`. If parameters are passed,
Contextional will make one version of the parameterized group for
each set of parameters, so if you have 5 sets of parameters for a
group, 5 versions of that group will be created. All of the child
groups of the parameterized group will be included in each version
of the parameterized group.

How do I format the sets of parameters that I want to use?
----------------------------------------------------------

There's actually 2 parts to this that you can utilize.

Collections of Sets (or "Collections of Collections")
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, is how you provide the collection of sets.

You can either put each set of parameters into a ``set``/\ ``list``/
\ ``tuple``, like so::

    with GroupContextManager("Main Group") as MG:

        my_params = (
            (1, 3, 5),
            (2, 4, 6),
        )
        with MG.add_group("Parameterized Group:", params=my_params):

or you can put them in a ``Mapping`` (e.g. a ``dict``), like this::

    with GroupContextManager("Main Group") as MG:

        my_params = {
            "odds": (1, 3, 5),
            "evens": (2, 4, 6),
        }
        with MG.add_group("Parameterized Group:", params=my_params):

The difference, is in the test output. Each version of the parameterized group
will need to distinguish itself from the other versions of itself so that
someone reading the test output can more easily tell where a problem occured
(if there was one). To do this, the description of the group is changed.

If the collection of sets used was a ``set``/\ ``list``/\ ``tuple``, then the
set of parameters itself will be appended to the group's normal description. In
the example above, you would see the output look like this:

.. code-block:: none

    Main Group
      Parameterized Group: (1, 3, 5)
        ...
      Parameterized Group: (2, 4, 6)
        ...

If the collection of sets used was a ``Mapping``, then the key for the set of
parameters itself will be appended to the group's normal description. In the
example above, you would see the output look like this:

.. code-block:: none

    Main Group
      Parameterized Group: odds
        ...
      Parameterized Group: evens
        ...

The Sets of Parameters Themselves
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Regardless of what kind of collection the sets of parameters are put into
together, the individual set of parameters that each version of the group uses
will be unpacked and passed as arguments to each of the :meth:`setUp` functions
that were defined in the root layer of the parameterized group. Child groups of
the parameterized group will not have the parameters passed to them. It is up
to the :meth:`setUp` function(s) of parameterized group to make sure their
child groups can access the parameters, if needed.

If a set of parameters is a ``set``/\ ``list``/\ ``tuple``, then it will be
unpacked with a single ``*``, so you can either have your :meth:`setUp`
functions catch them all with a ``*args``, or just make sure they take the
right number of ordered arguments. It will look something like this::

    with GroupContextManager("Main Group") as MG:

        my_params = (
            (1, 3, 5),
            (2, 4, 6),
        )
        with MG.add_group("Parameterized Group:", params=my_params):

            @MG.add_setup
            def setUp(*args):
                # some code

            @MG.add_setup
            def setUp(num_1, num_2, num_3):
                # some code

If a set of parameters is a ``Mapping`` (e.g. a ``dict``), then it will be
unpacked with a ``**``, so your :meth:`setUp` functions can catch them all with
a ``**kwargs``, or they can accept the appropriately name keyword arguments.
That will look something like this::

    with GroupContextManager("Main Group") as MG:

        my_params = (
            {
                "num_1": 1,
                "num_2": 3,
                "num_3": 5,
            },
            {
                "num_1": 2,
                "num_2": 4,
                "num_3": 6,
            },
        )
        with MG.add_group("Parameterized Group:", params=my_params):

            @MG.add_setup
            def setUp(**kwargs):
                # some code

            @MG.add_setup
            def setUp(num_1, num_2, num_3):
                # some code

This allows you to set default values for your parameters, and control how much
flexibility you want with your parameters.
