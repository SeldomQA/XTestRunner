import time
import unittest
import functools

from unittest import TextTestRunner
from .result import _XMLTestResult

# http://www.iana.org/assignments/character-sets/character-sets.xhtml
UTF8 = 'UTF-8'


class XMLTestRunner(TextTestRunner):
    """
    A test runner class that outputs the results in JUnit like XML files.
    """

    def __init__(self, output='.',
                 outsuffix=None,
                 elapsed_times=True,
                 encoding=UTF8,
                 descriptions=True,
                 verbosity=1,
                 whitelist=None,
                 blacklist=None,
                 logger=None,
                 rerun=0,
                 **kwargs):
        super(XMLTestRunner, self).__init__(**kwargs)
        self.output = output
        self.encoding = encoding
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.logger = logger
        self.rerun = rerun
        # None means default timestamped suffix
        # '' (empty) means no suffix
        if outsuffix is None:
            outsuffix = time.strftime("%Y%m%d%H%M%S")
        self.outsuffix = outsuffix
        self.elapsed_times = elapsed_times

        self.whitelist = set([] if whitelist is None else whitelist)
        self.blacklist = set([] if blacklist is None else blacklist)

    @classmethod
    def test_iter(cls, suite):
        """
        Iterate through test suites, and yield individual tests
        """
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                for t in cls.test_iter(test):
                    yield t
            else:
                yield test

    def run(self, testlist):
        """
        Runs the given test case or test suite.
        """
        for test in self.test_iter(testlist):
            # Determine if test should be skipped
            skip = bool(self.whitelist)
            test_method = getattr(test, test._testMethodName)
            test_labels = getattr(test, '_labels', set()) | getattr(test_method, '_labels', set())
            if test_labels & self.whitelist:
                skip = False
            if test_labels & self.blacklist:
                skip = True

            if skip:
                # Test should be skipped.
                @functools.wraps(test_method)
                def skip_wrapper(*args, **kwargs):
                    raise unittest.SkipTest('label exclusion')

                skip_wrapper.__unittest_skip__ = True
                if len(self.whitelist) >= 1:
                    skip_wrapper.__unittest_skip_why__ = f'label whitelist {self.whitelist}'
                if len(self.blacklist) >= 1:
                    skip_wrapper.__unittest_skip_why__ = f'label blacklist {self.blacklist}'
                setattr(test, test._testMethodName, skip_wrapper)

        try:
            # Prepare the test execution
            # result = self._make_result()
            result = _XMLTestResult(stream=self.stream, descriptions=self.descriptions, verbosity=self.verbosity,
                                    elapsed_times=self.elapsed_times, logger=self.logger, rerun=self.rerun)
            result.failfast = self.failfast
            result.buffer = self.buffer
            if hasattr(testlist, 'properties'):
                # junit testsuite properties
                result.properties = testlist.properties

            # Print a nice header
            self.stream.writeln()
            self.stream.writeln('XTestRunner Running tests...')
            self.stream.writeln(result.separator2)

            # Execute tests
            start_time = time.monotonic()
            testlist(result)
            stop_time = time.monotonic()
            time_taken = stop_time - start_time

            # Print results
            result.printErrors()
            self.stream.writeln(result.separator2)
            run = result.testsRun
            self.stream.writeln("Ran %d test%s in %.3fs" % (
                run, run != 1 and "s" or "", time_taken)
                                )
            self.stream.writeln()

            # other metrics
            expectedFails = len(result.expectedFailures)
            unexpectedSuccesses = len(result.unexpectedSuccesses)
            skipped = len(result.skipped)

            # Error traces
            infos = []
            if not result.wasSuccessful():
                self.stream.write("FAILED")
                failed, errored = map(len, (result.failures, result.errors))
                if failed:
                    infos.append("failures={0}".format(failed))
                if errored:
                    infos.append("errors={0}".format(errored))
            else:
                self.stream.write("OK")

            if skipped:
                infos.append("skipped={0}".format(skipped))
            if expectedFails:
                infos.append("expected failures={0}".format(expectedFails))
            if unexpectedSuccesses:
                infos.append("unexpected successes={0}".format(
                    unexpectedSuccesses))

            if infos:
                self.stream.writeln(" ({0})".format(", ".join(infos)))
            else:
                self.stream.write("\n")

            # Generate reports
            self.stream.writeln()
            self.stream.writeln('Generating XML reports...')
            result.generate_reports(self)
        finally:
            pass

        return result
