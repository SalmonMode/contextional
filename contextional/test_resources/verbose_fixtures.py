from contextional import GCM


with GCM("A") as A:

    @GCM.add_setup
    def setUp():
        pass

    @GCM.add_teardown
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        raise Exception
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup
    def setUp():
        raise Exception
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown
        def tearDown():
            raise Exception()

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown
        def tearDown():
            raise Exception()

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    @GCM.add_teardown
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown
        def tearDown():
            raise Exception()

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    @GCM.add_teardown
    def tearDown():
        raise Exception()
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown
        def tearDown():
            raise Exception()

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass

        @GCM.add_teardown
        def tearDown():
            raise Exception()

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup("setup w/ description")
    def setUp():
        pass

    @GCM.add_teardown("teardown w/ description")
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup("setup w/ description")
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            raise Exception()

        @GCM.add_teardown("teardown w/ description")
        def tearDown():
            pass


A.create_tests()


with GCM("A") as A:

    @GCM.add_setup
    def setUp():
        pass

    @GCM.add_teardown
    def tearDown():
        pass

    with GCM.add_group("B"):

        @GCM.add_setup
        def setUp():
            pass

        @GCM.add_test("some test")
        def test(case):
            pass

        @GCM.add_teardown
        def tearDown():
            pass


A.create_tests()


expected_stream_output = [
    "A",
    "  B",
    "    some test ... ok",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown w/ description ",
    "  # teardown w/ description ",
    "A",
    "  # setup w/ description ERROR",
    "  B",
    "    some test ... FAIL",
    "  # teardown w/ description ",
    "A",
    "  # setup (1/1) ERROR",
    "  B",
    "    some test ... FAIL",
    "  # teardown w/ description ",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown (1/2) ERROR",
    "  # teardown w/ description ",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown (1/2) ERROR",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown (1/2) ERROR",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown (1/2) ERROR",
    "  # teardown (1/2) ERROR",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown w/ description ",
    "    # teardown (2/3) ERROR",
    "  # teardown w/ description ",
    "A",
    "  # setup w/ description ",
    "  B",
    "    # setup w/ description ",
    "    some test ... ok",
    "    # teardown w/ description ERROR",
    "  # teardown w/ description ",
    "A",
    "  B",
    "    some test ... ok",
]
