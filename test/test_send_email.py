import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import SMTP

"""
说明：
1.使用126邮箱发送时password应为授权码而非用户密码，须在邮箱客户端设置开启授权码
2.使用gmail邮箱发送时password为用户密码，须在gmail客户端开启安全性较低的应用的访问权限
"""


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

    report = "./test/reports/email_result.html"
    with(open(report, 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='测试发送邮件',
            tester='虫师',
            description=['类型：测试发送邮件'],
            language="zh-CN"
        )
        runner.run(suit)
        # 发送邮件方式 1：send_email()方法
        runner.send_email(
            user="sender@qq.com",
            password="xxx",
            host="smtp.qq.com",
            to="recipient@126.com",
            subject="测试邮件",
            attachments=report
        )
    # 发送方式 2：SMTP类
    smtp = SMTP(user="sender@qq.com", password="xxx", host="smtp.qq.com")
    smtp.sender(to="recipient@126.com", subject="XTestRunner测试邮件", attachments=report)
