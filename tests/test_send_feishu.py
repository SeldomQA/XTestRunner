import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import FeiShu

"""
帮助文档:
https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN
:param url: 飞书机器人的Webhook地址
:param key: （非必传：str类型）如果飞书机器人安全设置了关键字，则需要传入对应的关键字
:param secret:（非必传:str类型）如果飞书机器人安全设置了签名，则需要传入对应的密钥
:param user_id: （非必传，str类型）发送通知飞书中要@人的open_id，如："ou_xxxxxxx"，所有人则必填，"all"
:param user_name: 是否@所有人，默认为None,@个人需填名称如，"张三"，设为 "所有人" 则会@所有人
:param feishu_href:测试报告连接地址，默认为None，需要填写具体的地址信息，如：https://www.baidu.com
:return:  发送成功返回 {"StatusCode":0,"StatusMessage":"success"}  发送失败返回 {"StatusCode":错误码,"msg":"失败原因"}
"""


class TestDing(unittest.TestCase):
    """
    测试用例说明
    """

    def test_success(self):
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
        TestDing("test_success"),
        TestDing("test_skip"),
        TestDing("test_fail"),
        TestDing("test_error")
    ])

    report = "./reports/test_send_feishu.html"
    with open(report, 'wb') as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='测试发送钉钉',
            tester='虫师',
            description=['类型：测试发送钉钉'],
            language="zh-CN"
        )
        runner.run(suit)
        # 方式一： send_dingtalk() 方法
        runner.send_feishu(
            url="https://open.feishu.cn/open-apis/bot/v2/hook/XXX-XXX",
            secret="XXX",
            feishu_href='http://www.baidu.com',
            user_id='all',
            user_name='所有人'
        )

    # 方式二： FeiShu 类
    ding = FeiShu(
        url="https://open.feishu.cn/open-apis/bot/v2/hook/XXX-XXX",
        secret="XXX",
        feishu_href='http://www.baidu.com',
        user_id='all',
        user_name='所有人'
    )
    ding.feishu_notice()

