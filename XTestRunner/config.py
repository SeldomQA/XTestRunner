
class Config:
    language = "en"  # en/ zh-CN


class RunResult:
    """
    Test run results
    """
    title = "XTestRunner Test Report"
    tester = "Anonymous"
    passed = 0
    failed = 0
    errors = 0
    skipped = 0


def label(*labels):
    """
    Test case classification label

    Usage:
        @label('quick')
        class MyTest(unittest.TestCase):
            def test_foo(self):
                pass
    """

    def inner(cls):
        # append labels to class
        cls._labels = set(labels) | getattr(cls, '_labels', set())
        return cls

    return inner
