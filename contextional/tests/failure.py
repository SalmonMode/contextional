from __future__ import absolute_import

from contextional import GroupContextManager as GCM


with GCM("Standard Failures") as SFT:

    @SFT.add_setup
    def setUp():
        SFT.test_value = 0

    @SFT.add_test_setup
    def setUp():
        SFT.test_value += 1

    @SFT.add_test_teardown
    def tearDown():
        SFT.test_value += 2

    @SFT.add_teardown
    def tearDown():
        SFT.test_value += 3

    @SFT.add_test("fails if test setup ran")
    def test(case):
        case.assertEqual(
            SFT.test_value,
            0,
        )

    @SFT.add_test("test level fixtures should still run after a failure")
    def test(case):
        case.assertEqual(
            SFT.test_value,
            4,
        )


SFT.create_tests(globals())


with GCM("Standard Failures Part 2") as SFT2:

    @SFT2.add_test("group level fixtures should still run after a failure")
    def test(case):
        case.assertEqual(
            SFT2.test_value,
            9,
        )


SFT2.create_tests(globals())


with GCM("Cascading Failure") as CFT:

    @CFT.add_setup
    def setUp():
        CFT.test_value = 0

    @CFT.add_test_setup
    def setUp():
        CFT.test_value += 1

    @CFT.add_test_teardown
    def tearDown():
        CFT.test_value += 2

    @CFT.add_teardown
    def tearDown():
        CFT.test_value += 3

    @CFT.add_test("value is 1")
    def test(case):
        case.assertEqual(
            CFT.test_value,
            1,
        )

    with CFT.add_group("Cascading Failure Should Only Affect This Group"):

        @CFT.add_setup
        def setUp():
            raise Exception()

        @CFT.add_setup
        def setUp():
            CFT.test_value += 4

        @CFT.add_test_setup
        def setUp():
            CFT.test_value += 5

        @CFT.add_test_teardown
        def tearDown():
            CFT.test_value += 6

        @CFT.add_teardown
        def tearDown():
            CFT.test_value += 7

        @CFT.add_test("fails if cacading failure")
        def test(case):
            case.assertEqual(
                CFT.test_value,
                15,
            )

        with CFT.add_group("Cascading Failure Should Extend to This Group"):

            @CFT.add_setup
            def setUp():
                CFT.test_value += 8

            @CFT.add_test_setup
            def setUp():
                CFT.test_value += 9

            @CFT.add_test_teardown
            def tearDown():
                CFT.test_value += 10

            @CFT.add_teardown
            def tearDown():
                CFT.test_value += 11

            @CFT.add_test("fails if cacading failure")
            def test(case):
                case.assertEqual(
                    CFT.test_value,
                    45,
                )


CFT.create_tests(globals())


with GCM("Cascading Failure Part 2") as CFT2:

    @CFT2.add_test("group level fixtures should still run accordingly")
    def test(case):
        case.assertEqual(
            CFT2.test_value,
            24,
        )


with GCM("Cascading Failure Part 3") as CFT3:

    @CFT3.add_test("will pass")
    def test(case):
        pass

    with CFT3.add_group("Cascading Failure Should Only Affect This Group"):

        @CFT3.add_setup
        def setUp():
            raise Exception()

        @CFT3.add_test("will fail")
        def test(case):
            pass

    with CFT3.add_group("Cascading Failure Should Not Affect This Group"):

        @CFT3.add_test("will pass")
        def test(case):
            pass


CFT3.create_tests(globals())


with GCM("Setup Error") as SET:

    @SET.add_setup
    def setUp():
        raise Exception()

    @CFT2.add_test("will fail")
    def test(case):
        pass


SET.create_tests(globals())


with GCM("Test Setup Error") as TSET:

    @TSET.add_test_setup
    def setUp():
        raise Exception()

    @TSET.add_test("will error")
    def test(case):
        pass


TSET.create_tests(globals())


with GCM("Teardown Error") as TET:

    @TET.add_teardown
    def tearDown():
        raise Exception()

    @CFT2.add_test("will pass")
    def test(case):
        pass


TET.create_tests(globals())


with GCM("Test Teardown Error") as TTET:

    @TTET.add_test_teardown
    def tearDown():
        raise Exception()

    @TTET.add_test("will error")
    def test(case):
        pass


TTET.create_tests(globals())


expected_stream_output = [
    "Standard Failures ",
    "  fails if test setup ran ... FAIL",
    "  test level fixtures should still run after a failure ... ok",
    "Standard Failures Part 2 ",
    "  group level fixtures should still run after a failure ... ok",
    "Cascading Failure ",
    "  value is 1 ... ok",
    "  Cascading Failure Should Only Affect This Group ERROR",
    "    fails if cacading failure ... FAIL",
    "      fails if cacading failure ... FAIL",
    "Cascading Failure Part 3 ",
    "  will pass ... ok",
    "  Cascading Failure Should Only Affect This Group ERROR",
    "    will fail ... FAIL",
    "  Cascading Failure Should Not Affect This Group ",
    "    will pass ... ok",
    "Test Setup Error ",
    "  will error ... ERROR",
    "Test Teardown Error ",
    "  will error ... ERROR",
]
