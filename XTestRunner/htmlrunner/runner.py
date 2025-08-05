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
from typing import Any, Optional, List, Union

# default tile
DEFAULT_TITLE = 'XTestRunner Test Report'

# ---------------------------
# Define the HTML template directory
# --------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_DIR = os.path.join(BASE_DIR, "html")

env = Environment(loader=FileSystemLoader(HTML_DIR))


# Load HTML snippets as Jinja2 templates (use .render as method, not property)
TEMPLATE_HTML_TMPL = env.get_template("template.html").render
STYLESHEET_HTML_TMPL = env.get_template("stylesheet.html").render
REPORT_CLASS_TMPL = env.get_template("report_class.html").render
REPORT_TEST_WITH_OUTPUT_TMPL = env.get_template("report_test_with_output.html").render
REPORT_TEST_NO_OUTPUT_TMPL = env.get_template("report_test_no_output.html").render
IMG_TMPL = env.get_template("img_tmpl.html").render


class HTMLTestRunner:
    """
    Run the test class
    """

    def __init__(
        self,
        stream: Any = sys.stdout,
        verbosity: int = 1,
        title: Optional[str] = None,
        tester: str = "Anonymous",
        description: Optional[Union[str, List[str]]] = None,
        rerun: int = 0,
        language: str = "en",
        logger: Optional[Any] = None,
        local_style: bool = False,
        **kwargs
    ):
        self.stream = stream
        self.verbosity = verbosity
        self.rerun = rerun
        self.run_times = 0
        self.logger = logger
        self.local_style = local_style
        Config.language = language
        self.title = title if title is not None else DEFAULT_TITLE
        RunResult.title = self.title
        self.tester = tester
        RunResult.tester = tester
        if description is None:
            self.description = ""
        elif isinstance(description, str):
            self.description = description
        elif isinstance(description, list):
            self.description = "".join(f'<p>{desc}</p>' for desc in description)
        else:
            self.description = ""

        self.start_time: datetime.datetime = datetime.datetime.now()
        self.end_time: Optional[datetime.datetime] = None
        self.test_obj: Optional[Any] = None

        self.whitelist = set(kwargs.pop('whitelist', []))
        self.blacklist = set(kwargs.pop('blacklist', []))

    @classmethod
    def test_iter(cls, suite: Any):
        """
        Iterate through test suites, and yield individual tests
        """
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from cls.test_iter(test)
            else:
                yield test

    def run(self, testlist: Any) -> _TestResult:
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

    def sort_result(self, result_list: list) -> list:
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

    def get_report_attributes(self, result: _TestResult):
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

    def generate_report(self, test: Any, result: _TestResult) -> None:
        base, statistics = self.get_report_attributes(result)
        version = get_version()
        heading = self._generate_heading(base, statistics)
        report = self._generate_report(result)
        static = static_file(self.local_style, self.stream.name)

        html_content = TEMPLATE_HTML_TMPL(
            jquery_url=static["jquery_url"],
            echarts_url=static["echarts_url"],
            css_url=static["css_url"],
            png_url=static["png_url"],
            title=saxutils.escape(self.title),
            version=version,
            stylesheet=STYLESHEET_HTML_TMPL(),
            heading=heading,
            report=report,
            channel=self.run_times,
        )
        self.stream.write(html_content.encode('utf-8'))

    def _get_language_template(self, template_type: str) -> str:
        """
        Return the template filename for the given type and current language.
        template_type: 'heading' or 'report'
        """
        lang = Config.language
        mapping = {
            ("en", "heading"): "heading-en.html",
            ("zh-CN", "heading"): "heading-zh-CN.html",
            ("en", "report"): "report-en.html",
            ("zh-CN", "report"): "report-zh-CN.html",
        }
        try:
            return mapping[(lang, template_type)]
        except KeyError:
            raise EnvironmentError(f"The language '{lang}' is not supported for {template_type} template.")

    def _generate_heading(self, base: dict, statistics: dict) -> str:
        heading_html = self._get_language_template("heading")
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

    def _generate_report(self, result: _TestResult) -> str:
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
            row = REPORT_CLASS_TMPL(
                style="passClass" if num_pass > 0 else ("failClass" if num_fail > 0 else ("errorClass" if num_error > 0 else "skipClass")),
                name=name,
                desc=doc,
                count=num_pass + num_fail + num_error + num_skip,
                class_result=f"{tag['PASSED']}:{num_pass}, {tag['FAILURE']}:{num_fail}, {tag['ERRORS']}:{num_error}, {tag['SKIPPED']}:{num_skip}",
                cid=f'c{self.run_times}.{cid + 1}',
                detail=tag['DETAIL']
            )
            rows.append(row)

            for tid, (num, test, out, error) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, num, test, out, error)

        report_html = self._get_language_template("report")
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

    def _generate_report_test(
        self,
        rows: list,
        cid: int,
        tid: int,
        num: int,
        test: Any,
        out: Any,
        error: Any
    ) -> None:
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
        tmpl = REPORT_TEST_WITH_OUTPUT_TMPL if has_output else REPORT_TEST_NO_OUTPUT_TMPL

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

            screenshots_html = IMG_TMPL(images=tmp, img_view=tag["VIEW"], screenshots=tag["SCREENSHOTS"])
        else:
            screenshots_html = ""

        # add runtime
        if getattr(test, 'runtime', []):
            runtime = test.runtime
        else:
            runtime = "0.00"

        row = tmpl(
            progress_bar_class=(
                'bg-success' if num == 0 else ('bg-warning' if num == 1 else ('bg-danger' if num == 2 else 'bg-secondary'))
            ),
            progress_result=(
                tag["PASSED"] if num == 0 else (tag["FAILURE"] if num == 1 else (tag["ERRORS"] if num == 2 else tag["SKIPPED"]))
            ),
            progress_bar_style="width:100%",
            tid=tid,
            log_viewing=tag["LOG"],
            Class=('hiddenRow' if num == 0 else 'none'),
            style=('passCase' if num == 0 else ('failCase' if num == 1 else ('errorCase' if num == 2 else 'skipCase'))),
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
        to: Any,
        user: str,
        password: str,
        host: str,
        port: Optional[int] = None,
        ssl: bool = True,
        subject: Optional[str] = None,
        attachments: Optional[Any] = None
    ) -> None:
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
        key: Optional[str] = None,
        app_secret: Optional[str] = None,
        at_mobiles: Optional[List[str]] = None,
        is_at_all: bool = False,
        append: Optional[str] = None,
        text: Optional[str] = None
    ) -> None:
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
        key: Optional[str] = None,
        secret: Optional[str] = None,
        user_id: Optional[str] = None,
        user_name: Union[str, bool] = False,
        feishu_href: Optional[str] = None
    ) -> None:
        fs = FeiShu(url=url, key=key, secret=secret, user_id=user_id, user_name=user_name, feishu_href=feishu_href)
        fs.feishu_notice()

    @staticmethod
    def send_weixin(
        access_token: str,
        at_mobiles: Optional[List[str]] = None,
        is_at_all: Optional[bool] = None
    ) -> None:
        wx = Weinxin(access_token=access_token, at_mobiles=at_mobiles, is_at_all=is_at_all)
        wx.send_text()
