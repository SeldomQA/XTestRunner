import unittest
from XTestRunner import label
from XTestRunner.HTMLTestRunner import HTMLTestRunner

"""
支持白黑名单

* 白名单：whitelist=["base"]  只有使用@label("base")装饰的用例执行
* 黑名单：blacklist=["slow"]  只有使用@label("slow")装饰的用例不被执行
"""


class LabelTest(unittest.TestCase):

    @label("base")
    def test_label_base(self):
        self.assertEqual(1+1, 2)

    @label("slow")
    def test_label_slow(self):
        self.assertEqual(1, 2)

    def test_no_label(self):
        self.assertEqual(2+3, 5)


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTest(LabelTest("test_label_base"))
    suit.addTest(LabelTest("test_label_slow"))
    suit.addTest(LabelTest("test_no_label"))

    with(open('./reports/label_result.html', 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='<project name>test report',
            description='describe: ... ',
            whitelist=["base"],  # 设置黑白名单
        )
        runner.run(suit)
