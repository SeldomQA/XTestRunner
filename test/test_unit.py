import unittest
from TestRunner import HTMLTestRunner
from TestRunner import SMTP


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


class TestDemo2(unittest.TestCase):

    def test_success(self):
        self.assertEqual(2 + 2, 4)


class TestDemo3(unittest.TestCase):

    def test_fail(self):
        self.assertEqual(3, 4)


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTest(TestDemo("test_success"))
    suit.addTest(TestDemo("test_skip"))
    suit.addTest(TestDemo("test_fail"))
    suit.addTest(TestDemo("test_error"))
    suit.addTest(TestDemo2("test_success"))
    suit.addTest(TestDemo3("test_fail"))

    report = "./result.html"
    with(open(report, 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='Seldom自动化测试报告',
            description='单元测试'
        )
        runner.run(suit)
    # 发邮件功能
    # 使用126邮箱发送时password应为授权码而非用户密码，须在邮箱客户端设置开启授权码
    # 使用gmail邮箱发送时password为用户密码，须在gmail客户端开启安全性较低的应用的访问权限
    smtp = SMTP(user="user@126.com", password="123", host="smtp.126.com")
    smtp.sender(to="user@126.com", attachments=report)
