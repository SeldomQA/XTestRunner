import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import Weinxin

"""
帮助文档:
https://developer.work.weixin.qq.com/document/path/91770
:param access_token:  企业微信机器人的Webhook地址的key
:param at_mobiles: 发送通知企业微信中要@人的手机号列表，如：[137xxx, 188xxx]。
:param is_at_all: 是否@所有人，默认为False, 设为True则会@所有人。
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

    report = "./reports/dingtalk_result.html"
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
        runner.send_weixin(
            access_token="50327a8c-59c3-4be7-bf44-a7ad4ec749b59",
            at_mobiles=[13700000000, 18800000000],
            is_at_all=False,
        )

    # 方式二： FeiShu 类
    weixin = Weinxin(
        access_token="50327a8c-59c3-4be7-bf44-a7ad4ec749b59",
        at_mobiles=[13700000000, 18800000000],
        is_at_all=False,
    )
    weixin.send_text(text="\n ### 附加信息")
    weixin.send_markdown(append="\n ### 附加信息")
