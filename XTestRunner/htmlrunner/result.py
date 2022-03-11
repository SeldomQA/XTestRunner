import io
import sys
import time
import copy
from unittest import TestResult


class OutputRedirector(object):
    """
    Wrapper to redirect stdout or stderr
    """

    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)


class OneCase:
    obj = None
    error = 0
    failure = 0


class _TestResult(TestResult):
    """
    note: _TestResult is a pure representation of results.
    It lacks the output and reporting ability compares to unittest._TextTestResult.
    """

    def __init__(self, verbosity=1, rerun=0, save_last_run=False):
        TestResult.__init__(self)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.skip_count = 0
        self.verbosity = verbosity
        self.rerun = rerun
        self.save_last_run = save_last_run
        self.status = 0
        self.runs = 0
        self.result = []
        self.case_start_time = None
        self.case_end_time = None
        self.output_buffer = None
        self.test_obj = None

    def startTest(self, test):
        self.case_start_time = time.time()
        test.images = getattr(test, "images", [])
        test.runtime = getattr(test, "runtime", None)
        self.output_buffer = io.StringIO()
        stdout_redirector.fp = self.output_buffer
        stderr_redirector.fp = self.output_buffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.output_buffer.getvalue()

    def stopTest(self, test):
        """
        Usually one of addSuccess, addError or addFailure would have been called.
        But there are some path in unittest that would bypass this.
        We must disconnect stdout in stopTest(), which is guaranteed to be called.
        """
        if self.rerun and self.rerun >= 1:
            if self.status == 1:
                self.runs += 1
                if self.runs <= self.rerun:
                    if self.save_last_run is True:
                        t = self.result.pop(-1)
                        if t[0] == 1:
                            if self.failure_count > 1:
                                self.failure_count -= 1
                        else:
                            if self.error_count > 1:
                                self.error_count -= 1
                    test = copy.copy(test)
                    sys.stderr.write("Retesting... ")
                    sys.stderr.write(str(test))
                    sys.stderr.write(f"..{self.runs} \n")
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
        self.complete_output()
        self.case_end_time = time.time()
        case_run_time = self.case_end_time - self.case_start_time
        test.runtime = round(case_run_time, 2)

    def addSuccess(self, test):
        if (self.rerun > 1) and (OneCase.obj == test) and (OneCase.failure == 1):
            self.failure_count -= 1
            OneCase.obj = None
            OneCase.failure = 0
        if (self.rerun > 1) and (OneCase.obj == test) and (OneCase.error == 1):
            self.error_count -= 1
            OneCase.obj = None
            OneCase.error = 0
        self.success_count += 1
        self.status = 0
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.' + str(self.success_count))

    def addError(self, test, err):
        if self.test_obj != test:
            self.test_obj = test
            self.error_count += 1
            OneCase.obj = test
            OneCase.error = 1
        else:
            self.error_count += 0
        self.status = 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if type(getattr(test, "driver", "")).__name__ == 'WebDriver':
            driver = getattr(test, "driver")
            test.images.append(driver.get_screenshot_as_base64())
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        if self.test_obj != test:
            self.test_obj = test
            self.failure_count += 1
            OneCase.obj = test
            OneCase.failure = 1
        else:
            self.failure_count += 0
        self.status = 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if type(getattr(test, "driver", "")).__name__ == 'WebDriver':
            driver = getattr(test, "driver")
            test.images.append(driver.get_screenshot_as_base64())
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')

    def addSkip(self, test, reason):
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