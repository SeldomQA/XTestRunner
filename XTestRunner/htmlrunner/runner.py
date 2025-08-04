import os
import re
import sys
import unittest
import datetime
import functools
from xml.sax import saxutils
from jinja2 import Environment, FileSystemLoader
from XTestRunner.htmlrunner.result import _TestResult
from XTestRunner.htmlrunner.multi_language import language_tag
from XTestRunner.config import RunResult, Config, static_file
from XTestRunner.version import get_version
from XTestRunner._email import SMTP
from XTestRunner._dingtalk import DingTalk
from XTestRunner._feishu import FeiShu
from XTestRunner._weixin import Weinxin

# default tile
DEFAULT_TITLE = 'XTestRunner Test Report'

# ---------------------------
# Define the HTML template directory
# --------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_DIR = os.path.join(BASE_DIR, "html")

env = Environment(loader=FileSystemLoader(HTML_DIR))

# Load HTML snippets as Jinja2 templates
TEMPLATE_HTML_TMPL = env.get_template("template.html")
STYLESHEET_HTML_TMPL = env.get_template("stylesheet.html")
REPORT_CLASS_TMPL = env.get_template("report_class.html")
REPORT_TEST_WITH_OUTPUT_TMPL = env.get_template("report_test_with_output.html")
REPORT_TEST_NO_OUTPUT_TMPL = env.get_template("report_test_no_output.html")
IMG_TMPL = env.get_template("img_tmpl.html")


class HTMLTestRunner(object):
    """
    Run the test class
    """

    def __init__(self,
                 stream=sys.stdout,
                 verbosity=1,
                 title=None,
                 tester="Anonymous",
                 description=None,
                 rerun=0,
                 language="en",
                 logger=None,
                 local_style=False,
                 **kwargs):
        self.stream = stream
        self.verbosity = verbosity
        self.rerun = rerun
        self.run_times = 0
        self.logger = logger
        self.local_style = local_style
        Config.language = language
        if title is None:
            self.title = DEFAULT_TITLE
        else:
            self.title = title
        RunResult.title = self.title
        self.tester = tester
        RunResult.tester = tester
        if description is None:
            self.description = ""
        elif isinstance(description, str):
            self.description = description
        elif isinstance(description, list):
            self.description = ""
            for desc in description:
                p_tag = '<p>' + desc + '</p>'
                self.description = self.description + p_tag
        else:
            self.description = ""

        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.test_obj = None

        self.whitelist = set(kwargs.pop('whitelist', []))
        self.blacklist = set(kwargs.pop('blacklist', []))

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
        Run the given test case or test suite.
        """

        print('\nXTestRunner Running tests...\n')
        print('----------------------------------------------------------------------')
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

        result = _TestResult(self.verbosity, rerun=self.rerun, logger=self.logger)
        testlist(result)
        self.end_time = datetime.datetime.now()
        self.run_times += 1
        self.generate_report(testlist, result)

        print("Generating HTML reports...")
        return result

    def sort_result(self, result_list):
        """
        unittest does not seems to run in any particular order.
        Here at least we want to group them together by class.
        """
        run_map = {}
        classes = []
        for num, test, out, error in result_list:
            cls = test.__class__
            if cls not in run_map:
                run_map[cls] = []
                classes.append(cls)
            run_map[cls].append((num, test, out, error))
        r = [(cls, run_map[cls]) for cls in classes]
        return r

    def get_report_attributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        start_time_format = str(self.start_time)[:19]
        end_time_format = str(self.end_time)[:19]
        duration = str(self.end_time - self.start_time)[:-3]

        RunResult.start_time = start_time_format
        RunResult.end_time = end_time_format
        RunResult.duration = duration
        RunResult.passed = result.success_count
        RunResult.failed = result.failure_count
        RunResult.errors = result.error_count
        RunResult.skipped = result.skip_count
        count = RunResult.passed + RunResult.failed + RunResult.errors + RunResult.skipped
        p_percent = '0.00'
        e_percent = '0.00'
        f_percent = '0.00'
        s_percent = '0.00'
        if count > 0:
            p_percent = '{:.2%}'.format(RunResult.passed / count)
            e_percent = '{:.2%}'.format(RunResult.errors / count)
            f_percent = '{:.2%}'.format(RunResult.failed / count)
            s_percent = '{:.2%}'.format(RunResult.skipped / count)

        RunResult.count = count
        RunResult.pass_rate = p_percent
        RunResult.error_rate = e_percent
        RunResult.failure_rate = f_percent
        RunResult.skip_rate = s_percent

        base_info = {
            "start_time": start_time_format,
            "end_time": end_time_format,
            "duration": duration
        }

        statistics_info = {
            "p": {
                "number": RunResult.passed,
                "percent": p_percent
            },
            "e": {
                "number": RunResult.errors,
                "percent": e_percent
            },
            "f": {
                "number": RunResult.failed,
                "percent": f_percent
            },
            "s": {
                "number": RunResult.skipped,
                "percent": s_percent
            },
        }

        return base_info, statistics_info

    def generate_report(self, test, result):
        base, statistics = self.get_report_attributes(result)

        version = get_version()
        heading = self._generate_heading(base, statistics)
        report = self._generate_report(result)
        static = static_file(self.local_style, self.stream.name)

        html_content = TEMPLATE_HTML_TMPL.render(
            jquery_url=static["jquery_url"],
            echarts_url=static["echarts_url"],
            css_url=static["css_url"],
            png_url=static["png_url"],
            title=saxutils.escape(self.title),
            version=version,
            stylesheet=STYLESHEET_HTML_TMPL.render(),
            heading=heading,
            report=report,
            channel=self.run_times,
        )
        self.stream.write(html_content.encode('utf8'))

    def _generate_heading(self, base, statistics):
        if Config.language == "en":
            heading_html = "heading-en.html"
        elif Config.language == "zh-CN":
            heading_html = "heading-zh-CN.html"
        else:
            raise EnvironmentError("The language is not supported")
        static = static_file(self.local_style, self.stream.name)
        heading = env.get_template(heading_html).render(
            title=self.title,
            png_url=static["png_url"],
            start_time=base["start_time"],
            end_time=base["end_time"],
            duration=base["duration"],
            tester=self.tester,
            description=self.description,
            p_number=statistics["p"]["number"],
            p_percent=statistics["p"]["percent"],
            f_number=statistics["f"]["number"],
            f_percent=statistics["f"]["percent"],
            e_number=statistics["e"]["number"],
            e_percent=statistics["e"]["percent"],
            s_number=statistics["s"]["number"],
            s_percent=statistics["s"]["percent"],
        )
        return heading

    def _generate_report(self, result):
        rows = []
        sorted_result = self.sort_result(result.result)
        for cid, (cls, cls_results) in enumerate(sorted_result):
            # subtotal for a class
            num_pass = num_fail = num_error = num_skip = 0
            for num, test, out, error in cls_results:
                if num == 0:
                    num_pass += 1
                elif num == 1:
                    num_fail += 1
                elif num == 2:
                    num_error += 1
                else:
                    num_skip += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name = f"{cls.__module__}.{cls.__name__}"
            doc = cls.__doc__ or ""
            # desc = doc and '%s: %s' % (name, doc) or name
            tag = language_tag(Config.language)
            row = REPORT_CLASS_TMPL.render(
                style=num_pass > 0 and "passClass" or (
                        num_fail > 0 and 'failClass' or (num_error > 0 and 'errorClass' or 'skipClass')),
                name=name,
                desc=doc,
                count=num_pass + num_fail + num_error + num_skip,
                class_result=f"{tag['PASSED']}:{num_pass}, {tag['FAILURE']}:{num_fail}, {tag['ERRORS']}:{num_error}, {tag['SKIPPED']}:{num_skip}",
                cid='c{}.{}'.format(self.run_times, cid + 1),
                detail=tag['DETAIL']
            )
            rows.append(row)

            for tid, (num, test, out, error) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, num, test, out, error)

        if Config.language == "en":
            report_html = "report-en.html"
        elif Config.language == "zh-CN":
            report_html = "report-zh-CN.html"
        else:
            raise EnvironmentError("The language is not supported")
        report = env.get_template(report_html).render(
            test_list=''.join(rows),
            count=str(result.success_count + result.failure_count + result.error_count + result.skip_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            skip=str(result.skip_count),
            channel=str(self.run_times),
        )
        return report

    def _generate_report_test(self, rows, cid, tid, num, test, out, error):
        # e.g. 'pt1.1', 'ft1.1','et1.1', 'st1.1' etc
        has_output = bool(out or error)
        if num == 0:
            tmp = "p"
        elif num == 1:
            tmp = "f"
        elif num == 2:
            tmp = "e"
        else:
            tmp = "s"
        tid = tmp + 't{}.{}.{}'.format(self.run_times, cid + 1, tid + 1)
        # tid = (n == 0 and 'p' or 'f') + 't%s.%s' % (cid + 1, tid + 1)
        name = test.id().split('.')[-1]
        # match subTest: desc='xx'
        desc_single_match = re.search(r'desc=\'([^\']*)\'', out)
        desc_double_match = re.search(r'desc="([^"]*)"', out)
        if desc_single_match:
            doc = desc_single_match.group(1)
        elif desc_double_match:
            doc = desc_double_match.group(1)
        else:
            doc = test.shortDescription() or ""
        # desc = doc and ('%s: %s' % (name, doc)) or name
        tmpl = has_output and REPORT_TEST_WITH_OUTPUT_TMPL.render or REPORT_TEST_NO_OUTPUT_TMPL.render

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(out, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formatting
            # uo = unicode(o.encode('string_escape'))
            uo = out
        else:
            uo = out
        if isinstance(error, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formatting
            # ue = unicode(e.encode('string_escape'))
            ue = error
        else:
            ue = error
        script = """{id}: {output}""".format(
            id=tid,
            output=saxutils.escape(uo + ue),
        )
        tag = language_tag(Config.language)
        # add image
        if getattr(test, 'images', []):
            tmp = ""
            for i, img in enumerate(test.images):
                if i == 0:
                    tmp += f'<img src="data:image/jpg;base64,{img}" style="display: block;" class="img"/>\n'
                else:
                    tmp += f'<img src="data:image/jpg;base64,{img}" style="display: none;" class="img"/>\n'

            screenshots_html = IMG_TMPL.render(images=tmp, img_view=tag["VIEW"], screenshots=tag["SCREENSHOTS"])
        else:
            screenshots_html = """"""

        # add runtime
        if getattr(test, 'runtime', []):
            runtime = test.runtime
        else:
            runtime = "0.00"

        row = tmpl(
            progress_bar_class=num == 0 and 'bg-success' or (
                    num == 1 and 'bg-warning' or (num == 2 and 'bg-danger' or 'bg-secondary')),
            progress_result=num == 0 and tag["PASSED"] or (
                    num == 1 and tag["FAILURE"] or (num == 2 and tag["ERRORS"] or tag["SKIPPED"])),
            progress_bar_style="width:100%",
            tid=tid,
            log_viewing=tag["LOG"],
            Class=(num == 0 and 'hiddenRow' or 'none'),
            style=num == 0 and 'passCase' or (num == 1 and 'failCase' or (num == 2 and 'errorCase' or 'skipCase')),
            casename=name,
            desc=doc,
            runtime=runtime,
            log_title=name,
            log_detailed=tag["DETAILED_LOG"],
            script=script,
            img=screenshots_html
        )
        rows.append(row)
        if not has_output:
            return

    @staticmethod
    def send_email(
            to: any,
            user: str,
            password: str,
            host: str,
            port: int = None,
            ssl: bool = True,
            subject: str = None,
            attachments=None):
        """
        Send test result to email
        :param to:
        :param user:
        :param password:
        :param host:
        :param port:
        :param ssl:
        :param subject:
        :param attachments:
        """
        smtp = SMTP(user=user, password=password, host=host, port=port, ssl=ssl)
        smtp.sender(to=to, subject=subject, attachments=attachments)

    @staticmethod
    def send_dingtalk(
            access_token: str,
            key: str = None,
            app_secret: str = None,
            at_mobiles: list = None,
            is_at_all: bool = False,
            append: str = None,
            text: str = None):
        """
        send dingtalk notice
        :param access_token:
        :param key:
        :param app_secret:
        :param at_mobiles:
        :param is_at_all:
        :param append:
        :param text:
        :return:
        """
        ding = DingTalk(access_token=access_token, key=key, app_secret=app_secret, at_mobiles=at_mobiles,
                        is_at_all=is_at_all)
        ding.sender(append=append, text=text)

    @staticmethod
    def send_feishu(
            url: str,
            key: str = None,
            secret: str = None,
            user_id: str = None,
            user_name: str = False,
            feishu_href: str = None):

        fs = FeiShu(url=url, key=key, secret=secret, user_id=user_id, user_name=user_name, feishu_href=feishu_href)
        fs.feishu_notice()

    @staticmethod
    def send_weixin(
            access_token: str,
            at_mobiles: list = None,
            is_at_all: bool = None):

        wx = Weinxin(access_token=access_token, at_mobiles=at_mobiles, is_at_all=is_at_all)
        wx.send_text()
