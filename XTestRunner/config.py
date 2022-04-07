import time


class Config:
    language = "en"  # en/ zh-CN


class RunResult:
    """
    Test run results
    """
    title = "XTestRunner Test Report"
    tester = "Anonymous"
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = time.strftime("%Y-%m-%d %H:%M:%S")
    duration = "0:00:00"
    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    count = 0
    pass_rate = 0.00
    failure_rate = 0.00
    error_rate = 0.00
    skip_rate = 0.00


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
