from __future__ import absolute_import


from contextional import GroupContextManager as GCM


with GCM("setups") as setups:

    @setups.add_setup
    def setUp():
        setups.test_value = 0

    @setups.add_setup
    def setUp():
        setups.test_value += 1

    @setups.add_test_setup
    def setUp():
        setups.test_value += 2

    @setups.add_test_setup
    def setUp():
        setups.test_value *= 3

with GCM("teardowns") as teardowns:

    @teardowns.add_test_teardown
    def tearDown():
        teardowns.test_value += 5

    @teardowns.add_test_teardown
    def tearDown():
        teardowns.test_value *= 6

    @teardowns.add_teardown
    def tearDown():
        teardowns.test_value += 7

    @teardowns.add_teardown
    def tearDown():
        teardowns.test_value *= 8


with GCM("Root Level Fixture Tests") as RLFT:

    RLFT.combine(
        setups,
        teardowns,
    )

    @RLFT.add_test("value is 9")
    def test(case):
        case.assertEqual(
            RLFT.test_value,
            9,
        )

    @RLFT.add_test("value is 258")
    def test(case):
        case.assertEqual(
            RLFT.test_value,
            258,
        )

    with RLFT.add_group("Only Test Teardowns Should've Happened"):

        @RLFT.add_test("value is 1578")
        def test(case):
            case.assertEqual(
                RLFT.test_value,
                1578,
            )


RLFT.create_tests(globals())


with GCM("Root Level Fixture Tests Part 2") as RLFT2:

    @RLFT2.add_test("value is now 12680")
    def test(case):
        case.assertEqual(
            RLFT2.test_value,
            12680,
        )


RLFT2.create_tests(globals())


with GCM("This Description Should Show Up") as include1:

    @include1.add_setup
    def setUp():
        include1.test_value = 0

    @include1.add_teardown
    def tearDown():
        include1.test_value += 1

    @include1.add_test("value is 0")
    def test(case):
        case.assertEqual(
            include1.test_value,
            0,
        )


with GCM("This Description Should Also Show Up") as include2:

    with include2.add_group("And So Should This"):

        @include2.add_test("value is 1")
        def test(case):
            case.assertEqual(
                include2.test_value,
                1,
            )


with GCM("Context Description of Deep Tests") as CDDT:

    CDDT.includes(
        include1,
        include2,
    )


CDDT.create_tests(globals())


expected_stream_output = [
    "Root Level Fixture Tests ",
    "  value is 9 ... ok",
    "  value is 258 ... ok",
    "  Only Test Teardowns Should've Happened ",
    "    value is 1578 ... ok",
    "Root Level Fixture Tests Part 2 ",
    "  value is now 12680 ... ok",
    "Context Description of Deep Tests ",
    "  This Description Should Show Up ",
    "    value is 0 ... ok",
    "  This Description Should Also Show Up ",
    "    And So Should This ",
    "      value is 1 ... ok",
]
