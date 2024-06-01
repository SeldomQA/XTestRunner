import os
import unittest

from XTestRunner import HTMLTestRunner
from XTestRunner import label
from config import REPORTS_DIR

"""
支持白黑名单

* 白名单：whitelist=["base"]  只有使用@label("base")装饰的用例执行
* 黑名单：blacklist=["slow"]  只有使用@label("slow")装饰的用例不被执行
"""


class LabelTest(unittest.TestCase):

    @label("base")
    def test_label_base(self):
        self.assertEqual(1 + 1, 2)

    @label("slow")
    def test_label_slow(self):
        self.assertEqual(1, 2)

    def test_no_label(self):
        self.assertEqual(2 + 3, 5)


if __name__ == '__main__':
    # HTML report
    html_report = os.path.join(REPORTS_DIR, "test_label_result.html")
    with open(html_report, 'wb') as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            tester="虫师",
            title='<project name>test report',
            description='describe: ... ',
            # whitelist=["base"],  # 设置白名单
            blacklist=["slow"],  # 设置黑名单
        ))
