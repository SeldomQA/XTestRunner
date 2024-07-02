import os
import unittest

from XTestRunner import HTMLTestRunner
from config import REPORTS_DIR


class TestDemo(unittest.TestCase):
    """测试用例说明"""

    def test_success(self):
        """执行成功"""
        self.assertEqual(2 + 3, 5)

    @unittest.skip("skip case")
    def test_skip(self):
        pass

    def test_fail(self):
        self.assertEqual(5, 6)

    def test_error(self):
        self.assertEqual(a, 6)


if __name__ == '__main__':
    html_report = os.path.join(REPORTS_DIR, "test_output_html.html")
    with open(html_report, 'wb') as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            tester="bugmaster",
            title='<project name>test report',
            description='describe: ... ',
            language='en',
            footer=True
        ))
