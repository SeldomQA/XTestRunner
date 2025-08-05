import io
import os
import re
import sys
import copy
import inspect
import datetime
from os import path
from io import StringIO
from typing import Any, Optional, List

# use direct import to bypass freezegun
from time import time
from unittest.result import failfast
from unittest import TestResult, TextTestResult

# Matches invalid XML1.0 unicode characters, like control characters:
# http://www.w3.org/TR/2006/REC-xml-20060816/#charsets
# http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python

sys.setrecursionlimit(2000)

_illegal_unichrs = [
    (0x00, 0x08), (0x0B, 0x0C), (0x0E, 0x1F),
    (0x7F, 0x84), (0x86, 0x9F),
    (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
]
if sys.maxunicode >= 0x10000:  # not narrow build
    _illegal_unichrs.extend([
        (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF),
        (0x3FFFE, 0x3FFFF), (0x4FFFE, 0x4FFFF),
        (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF),
        (0x9FFFE, 0x9FFFF), (0xAFFFE, 0xAFFFF),
        (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF),
        (0xFFFFE, 0xFFFFF), (0x10FFFE, 0x10FFFF),
    ])

_illegal_ranges = [
    "%s-%s" % (chr(low), chr(high))
    for (low, high) in _illegal_unichrs
]

INVALID_XML_1_0_UNICODE_RE = re.compile(u'[%s]' % u''.join(_illegal_ranges))

STDOUT_LINE = '\nStdout:\n%s'
STDERR_LINE = '\nStderr:\n%s'


def safe_unicode(data, encoding='utf8'):
    """Return a unicode string containing only valid XML characters.

    encoding - if data is a byte string it is first decoded to unicode
        using this encoding.
    """
    data = str(data)
    return INVALID_XML_1_0_UNICODE_RE.sub('', data)


def testcase_name(test_method):
    testcase = type(test_method)

    # Ignore module name if it is '__main__'
    module = testcase.__module__ + '.'
    if module == '__main__.':
        module = ''
    result = module + testcase.__name__
    return result


def resolve_filename(filename):
    # Try to make filename relative to current directory.
    try:
        rel_filename = os.path.relpath(filename)
    except ValueError:
        return filename
    # if not inside folder, keep as-is
    return filename if rel_filename.startswith('../') else rel_filename


class _DuplicateWriter(io.TextIOBase):
    """
    Duplicate output from the first handle to the second handle

    The second handle is expected to be a StringIO and not to block.
    """

    def __init__(self, first: io.TextIOBase, second: StringIO):
        super().__init__()
        self._first = first
        self._second = second

    def flush(self) -> None:
        self._first.flush()
        self._second.flush()

    def writable(self) -> bool:
        return True

    def getvalue(self) -> str:
        return self._second.getvalue()

    def writelines(self, lines) -> None:
        self._first.writelines(lines)
        self._second.writelines(lines)

    def write(self, b: str) -> int:
        try:
            self._first
        except AttributeError:
            return 0
        if isinstance(self._first, io.TextIOBase):
            wrote = self._first.write(b)
            if wrote is not None:
                self._second.write(b[:wrote])
            return wrote if wrote is not None else 0
        else:
            self._first.write(b)
            self._second.write(b)
            return len(b)


class _TestInfo:
    """
    This class keeps useful information about the execution of a test method.
    """

    SUCCESS, FAILURE, ERROR, SKIP = range(4)

    OUTCOME_ELEMENTS = {
        SUCCESS: None,
        FAILURE: 'failure',
        ERROR: 'error',
        SKIP: 'skipped',
    }

    def __init__(
        self,
        test_result: Any,
        test_method: Any,
        outcome: int = SUCCESS,
        err: Optional[Any] = None,
        subTest: Optional[Any] = None,
        filename: Optional[str] = None,
        lineno: Optional[int] = None,
        doc: Optional[str] = None,
    ):
        self.test_result = test_result
        self.outcome = outcome
        self.elapsed_time: float = 0.0
        self.timestamp: str = datetime.datetime.min.replace(microsecond=0).isoformat()
        if err is not None:
            if self.outcome != _TestInfo.SKIP:
                self.test_exception_name = safe_unicode(err[0].__name__)
                self.test_exception_message = safe_unicode(err[1])
            else:
                self.test_exception_message = safe_unicode(err)

        self.stdout = test_result._stdout_data
        self.stderr = test_result._stderr_data

        self.test_description = self.test_result.getDescription(test_method)
        self.test_exception_info = (
            '' if outcome in (self.SUCCESS, self.SKIP)
            else self.test_result._exc_info_to_string(err, test_method)
        )

        self.test_name = testcase_name(test_method)
        self.test_id = test_method.id()

        if subTest:
            self.test_id = subTest.id()
            self.test_description = self.test_result.getDescription(subTest)

        self.filename = filename
        self.lineno = lineno
        self.doc = doc
        self.images: List[Any] = []

    def id(self) -> str:
        return self.test_id

    def test_finished(self) -> None:
        """Save info that can only be calculated once a test has run."""
        self.elapsed_time = self.test_result.stop_time - self.test_result.start_time
        timestamp = datetime.datetime.fromtimestamp(self.test_result.stop_time)
        self.timestamp = timestamp.replace(microsecond=0).isoformat()

    def get_error_info(self) -> str:
        """Return a text representation of an exception thrown by a test method."""
        return self.test_exception_info


class _XMLTestResult(TextTestResult):
    """
    A test result class that can express test results in a XML report.

    Used by XMLTestRunner.
    """

    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1,
                 elapsed_times=True, properties=None, infoclass=None, logger=None, rerun=0):
        TextTestResult.__init__(self, stream, descriptions, verbosity)
        self._stdout_data = None
        self._stderr_data = None
        self._stdout_capture = StringIO()
        self.__stdout_saved = None
        self._stderr_capture = StringIO()
        self.__stderr_saved = None
        self.successes = []
        self.callback = None
        self.elapsed_times = elapsed_times
        self.properties = properties  # junit testsuite properties
        self.filename = None
        self.lineno = None
        self.doc = None
        self.logger = logger
        self.rerun = rerun
        self.status = 0
        self.runs = 0
        self.test_obj = None
        if infoclass is None:
            self.infoclass = _TestInfo
        else:
            self.infoclass = infoclass

    def _prepare_callback(
        self,
        test_info: _TestInfo,
        target_list: list,
        verbose_str: str,
        short_str: str,
        images: Optional[list] = None
    ) -> None:
        """
        Appends a `infoclass` to the given target list and sets a callback
        method to be called by stopTest method.
        """
        test_info.filename = self.filename
        test_info.lineno = self.lineno
        test_info.doc = self.doc
        target_list.append(test_info)
        if images is None:
            test_info.images = []
        else:
            test_info.images = images


        def callback() -> None:
            """Prints the test method outcome to the stream, as well as the elapsed time."""
            test_info.test_finished()
            # Ignore the elapsed times for a more reliable unit testing
            if not self.elapsed_times:
                self.start_time = self.stop_time = 0
            if self.showAll:
                self.stream.writeln(f'{verbose_str} ({test_info.elapsed_time:.3f}s)')
            elif self.dots:
                if isinstance(short_str, tuple) and len(short_str) == 2:
                    self.stream.write(short_str[1])
                else:
                    self.stream.write(short_str)
            self.stream.flush()

        self.callback = callback

    def startTest(self, test: Any) -> None:
        """
        Called before execute each test method.
        """
        self.start_time = time()
        test.images = getattr(test, "images", [])
        TestResult.startTest(self, test)

        try:
            if getattr(test, '_dt_test', None) is not None:
                # doctest.DocTestCase
                self.filename = test._dt_test.filename
                self.lineno = test._dt_test.lineno
            else:
                # regular unittest.TestCase?
                test_method = getattr(test, test._testMethodName)
                test_class = type(test)
                # Note: inspect can get confused with decorators, so use class.
                self.filename = inspect.getsourcefile(test_class)
                # Handle partial and partialmethod objects.
                test_method = getattr(test_method, 'func', test_method)
                _, self.lineno = inspect.getsourcelines(test_method)

                self.doc = test_method.__doc__
        except (AttributeError, IOError, TypeError):
            # issue #188, #189, #195
            # some frameworks can make test method opaque.
            pass

        if self.showAll:
            self.stream.write('  ' + self.getDescription(test))
            self.stream.write(" ... ")
            self.stream.flush()

    def _setupStdout(self) -> None:
        """
        Capture stdout / stderr by replacing sys.stdout / sys.stderr
        """
        super(_XMLTestResult, self)._setupStdout()
        self.__stdout_saved = sys.stdout
        sys.stdout = _DuplicateWriter(sys.stdout, self._stdout_capture)
        self.__stderr_saved = sys.stderr
        sys.stderr = _DuplicateWriter(sys.stderr, self._stderr_capture)
        if self.logger is not None:
            self.logger_handler_id = self.logger.logger.add(self._stdout_capture, level=self.logger._level,
                                                            colorize=False, format=self.logger._console_format)

    def _restoreStdout(self) -> None:
        """
        Stop capturing stdout / stderr and recover sys.stdout / sys.stderr
        """
        if self.__stdout_saved:
            sys.stdout = self.__stdout_saved
            self.__stdout_saved = None
        if self.__stderr_saved:
            sys.stderr = self.__stderr_saved
            self.__stderr_saved = None
        if self.logger is not None:
            try:
                self.logger.logger.remove(self.logger_handler_id)
            except ValueError:
                ...

        self._stdout_capture.seek(0)
        self._stdout_capture.truncate()
        self._stderr_capture.seek(0)
        self._stderr_capture.truncate()
        super(_XMLTestResult, self)._restoreStdout()

    def _save_output_data(self) -> None:
        self._stdout_data = self._stdout_capture.getvalue()
        self._stderr_data = self._stderr_capture.getvalue()

    def stopTest(self, test: Any) -> None:
        """
        Called after execute each test method.
        """
        if self.rerun and self.rerun >= 1:
            if self.status == 1:
                self.runs += 1
                if self.runs <= self.rerun:
                    test = copy.copy(test)
                    sys.stdout.write("Retesting... ")
                    sys.stdout.write(str(test))
                    sys.stdout.write(f"..{self.runs} \n")
                    doc = getattr(test, '_testMethodDoc', u"") or u''
                    if doc.find('->rerun') != -1:
                        doc = doc[:doc.find('->rerun')]
                    desc = f"{doc} ->rerun: {self.runs}"
                    if isinstance(desc, str):
                        desc = desc
                    test._testMethodDoc = desc
                    test(self)
                else:
                    self.status = 0
                    self.runs = 0
        self._save_output_data()
        # self._stdout_data = sys.stdout.getvalue()
        # self._stderr_data = sys.stderr.getvalue()

        TextTestResult.stopTest(self, test)
        self.stop_time = time()

        if self.callback and callable(self.callback):
            self.callback()
            self.callback = None

    def addSuccess(self, test: Any) -> None:
        """
        Called when a test executes successfully.
        """
        self.status = 0
        self._save_output_data()
        self._prepare_callback(
            self.infoclass(self, test), self.successes, 'ok', '.'
        )

    @failfast
    def addFailure(self, test: Any, err: Any) -> None:
        """
        Called when a test method fails.
        """
        self.status = 1
        # If it is less than the number of rerun, no failure is append
        if self.runs < self.rerun:
            self._save_output_data()
            self._restoreStdout()
            return
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.FAILURE, err)
        self.failures.append((
            testinfo,
            self._exc_info_to_string(err, test)
        ))
        if type(getattr(test, "driver", "")).__name__ == 'WebDriver':
            driver = getattr(test, "driver")
            try:
                test.images.append(driver.get_screenshot_as_base64())
            except BaseException:
                ...
        self._prepare_callback(testinfo, [], 'FAIL', 'F', images=test.images)

    @failfast
    def addError(self, test: Any, err: Any) -> None:
        """
        Called when a test method raises an error.
        """
        self.status = 1
        # If it is less than the number of rerun, no error is append
        if self.runs < self.rerun:
            self._save_output_data()
            self._restoreStdout()
            return
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.ERROR, err)
        self.errors.append((
            testinfo,
            self._exc_info_to_string(err, test)
        ))
        if type(getattr(test, "driver", "")).__name__ == 'WebDriver':
            driver = getattr(test, "driver")
            try:
                test.images.append(driver.get_screenshot_as_base64())
            except BaseException as msg:
                ...
        self._prepare_callback(testinfo, [], 'ERROR', 'E', images=test.images)

    def addSubTest(self, testcase: Any, test: Any, err: Any) -> None:
        """
        Called when a subTest method raises an error.
        """
        if err is not None:
            if issubclass(err[0], test.failureException):
                error_text = 'FAIL'
                error_value = self.infoclass.FAILURE
                error_list = self.failures
            else:
                error_text = 'ERROR'
                error_value = self.infoclass.ERROR
                error_list = self.errors

            self._save_output_data()

            testinfo = self.infoclass(
                self, testcase, error_value, err, subTest=test)
            error_list.append((
                testinfo,
                self._exc_info_to_string(err, testcase)
            ))
            self._prepare_callback(testinfo, [], error_text, error_list[0])
        else:
            self._save_output_data()
            self._restoreStdout()
            self._prepare_callback(
                self.infoclass(self, test), self.successes, 'ok', '.'
            )

    def addSkip(self, test: Any, reason: str) -> None:
        """
        Called when a test method was skipped.
        """
        self.status = 0
        self._save_output_data()
        testinfo = self.infoclass(
            self, test, self.infoclass.SKIP, reason)
        testinfo.test_exception_name = 'skip'
        testinfo.test_exception_message = reason
        self.skipped.append((testinfo, reason))
        self._prepare_callback(testinfo, [], 'skip', 's')

    def addExpectedFailure(self, test: Any, err: Any) -> None:
        """
        Missing in xmlrunner, copy-pasted from xmlrunner addError.
        """
        self._save_output_data()

        testinfo = self.infoclass(self, test, self.infoclass.SKIP, err)
        testinfo.test_exception_name = 'XFAIL'
        testinfo.test_exception_message = 'expected failure: {}'.format(testinfo.test_exception_message)

        self.expectedFailures.append((testinfo, self._exc_info_to_string(err, test)))
        self._prepare_callback(testinfo, [], 'expected failure', 'x')

    @failfast
    def addUnexpectedSuccess(self, test: Any) -> None:
        """
        Missing in xmlrunner, copy-pasted from xmlrunner addSuccess.
        """
        self._save_output_data()

        testinfo = self.infoclass(self, test)  # do not set outcome here because it will need exception
        testinfo.outcome = self.infoclass.ERROR
        # But since we want to have error outcome, we need to provide additional fields:
        testinfo.test_exception_name = 'UnexpectedSuccess'
        testinfo.test_exception_message = ('Unexpected success: This test was marked as expected failure but passed, '
                                           'please review it')

        self.unexpectedSuccesses.append((testinfo, 'unexpected success'))
        self._prepare_callback(testinfo, [], 'unexpected success', 'u')

    def printErrorList(self, flavour: str, errors: list) -> None:
        """
        Writes information about the FAIL or ERROR to the stream.
        """
        for test_info, dummy in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln(
                '%s [%.3fs]: %s' % (flavour, test_info.elapsed_time,
                                    test_info.test_description)
            )
            self.stream.writeln(self.separator2)
            self.stream.writeln('%s' % test_info.get_error_info())
            self.stream.flush()

    def _get_info_by_testcase(self) -> dict:
        """
        Organizes test results by TestCase module. This information is
        used during the report generation, where an XML report will be created
        for each TestCase.
        """
        tests_by_testcase = {}

        for tests in (self.successes, self.failures, self.errors,
                      self.skipped, self.expectedFailures, self.unexpectedSuccesses):
            for test_info in tests:
                if isinstance(test_info, tuple):
                    # This is a skipped, error or a failure test case
                    test_info = test_info[0]
                testcase_name = test_info.test_name
                if testcase_name not in tests_by_testcase:
                    tests_by_testcase[testcase_name] = []
                tests_by_testcase[testcase_name].append(test_info)

        return tests_by_testcase

    def _report_testsuite_properties(xml_testsuite: Any, xml_document: Any, properties: Optional[dict]) -> None:
        if properties:
            xml_properties = xml_document.createElement('properties')
            xml_testsuite.appendChild(xml_properties)
            for key, value in properties.items():
                prop = xml_document.createElement('property')
                prop.setAttribute('name', str(key))
                prop.setAttribute('value', str(value))
                xml_properties.appendChild(prop)

    _report_testsuite_properties = staticmethod(_report_testsuite_properties)

    def _report_testsuite(
        suite_name: str,
        tests: list,
        xml_document: Any,
        parentElement: Any,
        properties: Optional[dict]
    ) -> Any:
        """
        Appends the testsuite section to the XML document.
        """
        testsuite = xml_document.createElement('testsuite')
        parentElement.appendChild(testsuite)
        module_name = suite_name.rpartition('.')[0]
        file_name = module_name.replace('.', '/') + '.py'

        testsuite.setAttribute('name', suite_name)
        testsuite.setAttribute('tests', str(len(tests)))
        testsuite.setAttribute('file', file_name)

        testsuite.setAttribute(
            'time', '%.3f' % sum(map(lambda e: e.elapsed_time, tests))
        )
        if tests:
            testsuite.setAttribute(
                'timestamp', max(map(lambda e: e.timestamp, tests))
            )
        failures = filter(lambda e: e.outcome == e.FAILURE, tests)
        testsuite.setAttribute('failures', str(len(list(failures))))

        errors = filter(lambda e: e.outcome == e.ERROR, tests)
        testsuite.setAttribute('errors', str(len(list(errors))))

        skips = filter(lambda e: e.outcome == _TestInfo.SKIP, tests)
        testsuite.setAttribute('skipped', str(len(list(skips))))

        _XMLTestResult._report_testsuite_properties(
            testsuite, xml_document, properties)

        for test in tests:
            _XMLTestResult._report_testcase(test, testsuite, xml_document)

        return testsuite

    _report_testsuite = staticmethod(_report_testsuite)

    def _test_method_name(test_id: str) -> str:
        """
        Returns the test method name.
        """
        # Trick subtest referencing objects
        subtest_parts = test_id.split(' ')
        test_method_name = subtest_parts[0].split('.')[-1]
        subtest_method_name = [test_method_name] + subtest_parts[1:]
        return ' '.join(subtest_method_name)

    _test_method_name = staticmethod(_test_method_name)

    def _createCDATAsections(xmldoc: Any, node: Any, text: str) -> None:
        text = safe_unicode(text)
        pos = text.find(']]>')
        while pos >= 0:
            tmp = text[0:pos + 2]
            cdata = xmldoc.createCDATASection(tmp)
            node.appendChild(cdata)
            text = text[pos + 2:]
            pos = text.find(']]>')
        cdata = xmldoc.createCDATASection(text)
        node.appendChild(cdata)

    _createCDATAsections = staticmethod(_createCDATAsections)

    def _report_testcase(test_result: _TestInfo, xml_testsuite: Any, xml_document: Any) -> None:
        """
        Appends a testcase section to the XML document.
        """
        testcase = xml_document.createElement('testcase')
        xml_testsuite.appendChild(testcase)

        class_name = re.sub(r'^__main__.', '', test_result.id())

        # Trick subtest referencing objects
        class_name = class_name.split(' ')[0].rpartition('.')[0]

        testcase.setAttribute('classname', class_name)
        testcase.setAttribute(
            'name', _XMLTestResult._test_method_name(test_result.test_id)
        )
        testcase.setAttribute('time', '%.3f' % test_result.elapsed_time)
        testcase.setAttribute('timestamp', test_result.timestamp)

        if test_result.filename is not None:
            # Try to make filename relative to current directory.
            filename = resolve_filename(test_result.filename)
            testcase.setAttribute('file', filename)

        if test_result.lineno is not None:
            testcase.setAttribute('line', str(test_result.lineno))

        if test_result.doc is not None:
            comment = str(test_result.doc)
            # The use of '--' is forbidden in XML comments
            comment = comment.replace('--', '&#45;&#45;')
            # testcase.appendChild(xml_document.createComment(safe_unicode(comment)))
            doc = xml_document.createElement('doc')
            testcase.appendChild(doc)
            _XMLTestResult._createCDATAsections(
                xml_document, doc, comment)

        result_elem_name = test_result.OUTCOME_ELEMENTS[test_result.outcome]

        if result_elem_name is not None:
            result_elem = xml_document.createElement(result_elem_name)
            testcase.appendChild(result_elem)

            result_elem.setAttribute(
                'type',
                test_result.test_exception_name
            )
            result_elem.setAttribute(
                'message',
                test_result.test_exception_message
            )
            if test_result.get_error_info():
                error_info = safe_unicode(test_result.get_error_info())
                _XMLTestResult._createCDATAsections(
                    xml_document, result_elem, error_info)

        if test_result.stdout:
            systemout = xml_document.createElement('system-out')
            testcase.appendChild(systemout)
            _XMLTestResult._createCDATAsections(
                xml_document, systemout, test_result.stdout)

        if test_result.stderr:
            systemout = xml_document.createElement('system-err')
            testcase.appendChild(systemout)
            _XMLTestResult._createCDATAsections(
                xml_document, systemout, test_result.stderr)

        if len(test_result.images) != 0:
            for image in test_result.images:
                screenshot = xml_document.createElement('screenshot')
                screenshot.setAttribute('src', image)
                testcase.appendChild(screenshot)
                _XMLTestResult._createCDATAsections(
                    xml_document, screenshot, '')

    _report_testcase = staticmethod(_report_testcase)

    def generate_reports(self, test_runner: Any) -> None:
        """
        Generates the XML reports to a given XMLTestRunner object.
        """
        from xml.dom.minidom import Document
        all_results = self._get_info_by_testcase()

        outputHandledAsString = \
            isinstance(test_runner.output, str)

        if (outputHandledAsString and not os.path.exists(test_runner.output)):
            os.makedirs(test_runner.output)

        if not outputHandledAsString:
            doc = Document()
            testsuite = doc.createElement('testsuites')
            doc.appendChild(testsuite)
            parentElement = testsuite

        for suite, tests in all_results.items():
            if outputHandledAsString:
                doc = Document()
                parentElement = doc

            suite_name = suite
            if test_runner.outsuffix:
                # not checking with 'is not None', empty means no suffix.
                suite_name = '%s-%s' % (suite, test_runner.outsuffix)

            # Build the XML file
            testsuite = _XMLTestResult._report_testsuite(
                suite_name, tests, doc, parentElement, self.properties
            )

            if outputHandledAsString:
                xml_content = doc.toprettyxml(
                    indent='\t',
                    encoding=test_runner.encoding
                )
                filename = path.join(
                    test_runner.output,
                    'TEST-%s.xml' % suite_name)
                with open(filename, 'wb') as report_file:
                    report_file.write(xml_content)

                if self.showAll:
                    self.stream.writeln('Generated XML report: {}'.format(filename))

        if not outputHandledAsString:
            # Assume that test_runner.output is a stream
            xml_content = doc.toprettyxml(
                indent='\t',
                encoding=test_runner.encoding
            )
            test_runner.output.write(xml_content)

    def _exc_info_to_string(self, err: Any, test: Any) -> str:
        """Converts a sys.exc_info()-style tuple of values into a string."""
        return super()._exc_info_to_string(err, test)
