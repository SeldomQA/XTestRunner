import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import SMTP


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
    report = "./reports/send_email_result.html"
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            title='测试发送邮件',
            description=['类型：测试发送邮件', '执行人：虫师']
        ))
    # 发邮件功能
    # 使用126邮箱发送时password应为授权码而非用户密码，须在邮箱客户端设置开启授权码
    # 使用gmail邮箱发送时password为用户密码，须在gmail客户端开启安全性较低的应用的访问权限
    smtp = SMTP(user="sender@qq.com", password="xxx", host="smtp.qq.com")
    smtp.sender(to="fnngj@126.com", subject="XTestRunner测试邮件", attachments=report)
