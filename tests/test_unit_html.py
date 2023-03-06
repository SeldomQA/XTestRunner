import unittest
from XTestRunner import HTMLTestRunner


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
    suit = unittest.TestSuite()
    suit.addTests([
        TestDemo("test_success"),
        TestDemo("test_skip"),
        TestDemo("test_fail"),
        TestDemo("test_error")
    ])

    html_report = './reports/test_unit_html.html'
    with open(html_report, 'wb') as fp:
        runner = HTMLTestRunner(
            stream=fp,
            tester="虫师",
            title='<project name>test report',
            description='describe: ... ',
            language='en',
            rerun=3
        )
        runner.run(suit)
