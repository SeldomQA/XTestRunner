import io
import sys
import time
import copy
from unittest import TestResult
from typing import Any, Optional, List


class OutputRedirector:
    """
    Wrapper to redirect stdout or stderr
    """

    def __init__(self, fp: Any):
        self.fp = fp
        self.stdbak = fp

    def write(self, s: str) -> None:
        self.fp.write(s)
        self.stdbak.write(f"{s}\n")

    def writelines(self, lines: List[str]) -> None:
        self.fp.writelines(lines)

    def flush(self) -> None:
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


class _TestResult(TestResult):
    """
    note: _TestResult is a pure representation of results.
    It lacks the output and reporting ability compared to unittest._TextTestResult.
    """

    def __init__(self, verbosity: int = 1, rerun: int = 0, logger: Optional[Any] = None):
        super().__init__()
        self.stdout0: Optional[Any] = None
        self.stderr0: Optional[Any] = None
        self.success_count: int = 0
        self.failure_count: int = 0
        self.error_count: int = 0
        self.skip_count: int = 0
        self.verbosity: int = verbosity
        self.rerun: int = rerun
        self.status: int = 0
        self.runs: int = 0
        self.result: list = []
        self.case_start_time: Optional[float] = None
        self.case_end_time: Optional[float] = None
        self.output_buffer: Optional[io.StringIO] = None
        self.test_obj: Optional[Any] = None
        self.sub_test_list: list = []
        self.stdout_proxy: Any = sys.stderr
        self.logger: Optional[Any] = logger
        self.logger_handler_id: Optional[Any] = None
        self.status = 0
        self.runs = 0
        self.result = []
        self.case_start_time = None
        self.case_end_time = None
        self.output_buffer = None
        self.test_obj = None
        self.sub_test_list = []
        self.stdout_proxy = sys.stderr
        self.logger = logger
        self.logger_handler_id = None

    def startTest(self, test: Any) -> None:
        self.case_start_time = time.time()
        test.images = getattr(test, "images", [])
        test.runtime = getattr(test, "runtime", None)

        self.output_buffer = io.StringIO()
        if self.logger is not None:
            self.logger_handler_id = self.logger.logger.add(
                self.output_buffer,
                level=self.logger._level,
                colorize=False,
                format=self.logger._console_format
            )

        stdout_redirector.fp = self.output_buffer
        stderr_redirector.fp = self.output_buffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self) -> str:
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            self.stdout0 = None

        if self.stderr0:
            sys.stderr = self.stderr0
            self.stderr0 = None

        if self.logger is not None:
            try:
                self.logger.logger.remove(self.logger_handler_id)
            except ValueError:
                ...

        if self.output_buffer is not None:
            return self.output_buffer.getvalue()
        else:
            return "setUpClass/start_class error."

    def stopTest(self, test: Any) -> None:
        """
        Usually one of addSuccess, addError or addFailure would have been called.
        But there are some path in unittest that would bypass this.
        We must disconnect stdout in stopTest(), which is guaranteed to be called.
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

        self.case_end_time = time.time()
        case_run_time = self.case_end_time - self.case_start_time
        test.runtime = round(case_run_time, 2)

    def addSuccess(self, test: Any) -> None:
        self.status = 0
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.' + str(self.success_count))

    def addError(self, test: Any, err: Any) -> None:
        self.status = 1
        if self.runs < self.rerun:
            return
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if type(getattr(test, "driver", "")).__name__ == 'WebDriver':
            driver = getattr(test, "driver")
            try:
                test.images.append(driver.get_screenshot_as_base64())
            except BaseException:
                ...
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test: Any, err: Any) -> None:
        self.status = 1
        if self.runs < self.rerun:
            return
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if type(getattr(test, "driver", "")).__name__ == 'WebDriver':
            driver = getattr(test, "driver")
            try:
                test.images.append(driver.get_screenshot_as_base64())
            except BaseException:
                ...
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')

    def addSkip(self, test: Any, reason: str) -> None:
        self.skip_count += 1
        self.status = 0
        TestResult.addSkip(self, test, reason)
        output = self.complete_output()
        self.result.append((3, test, output, reason))
        if self.verbosity > 1:
            sys.stderr.write('S')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('S')

    def addSubTest(self, test: Any, subtest: Any, err: Optional[Any]) -> None:
        if err is not None:
            if getattr(self, 'failfast', False):
                self.stop()
            if issubclass(err[0], test.failureException):
                self.failure_count += 1
                errors = self.failures
                errors.append((subtest, self._exc_info_to_string(err, subtest)))
                output = self.complete_output()
                self.result.append((1, test, output + '\nSubTestCase Failed:\n' + str(subtest),
                                    self._exc_info_to_string(err, subtest)))
                if self.verbosity > 1:
                    sys.stderr.write('F  ')
                    sys.stderr.write(str(subtest))
                    sys.stderr.write('\n')
                else:
                    sys.stderr.write('F')
            else:
                self.error_count += 1
                errors = self.errors
                errors.append((subtest, self._exc_info_to_string(err, subtest)))
                output = self.complete_output()
                self.result.append(
                    (2, test, output + '\nSubTestCase Error:\n' + str(subtest), self._exc_info_to_string(err, subtest)))
                if self.verbosity > 1:
                    sys.stderr.write('E  ')
                    sys.stderr.write(str(subtest))
                    sys.stderr.write('\n')
                else:
                    sys.stderr.write('E')
            self._mirrorOutput = True
        else:
            self.sub_test_list.append(subtest)
            self.sub_test_list.append(test)
            self.success_count += 1
            output = self.complete_output()
            self.result.append((0, test, output + '\nSubTestCase Pass:\n' + str(subtest), ''))
            if self.verbosity > 1:
                sys.stderr.write('ok ')
                sys.stderr.write(str(subtest))
                sys.stderr.write('\n')
            else:
                sys.stderr.write('.')
