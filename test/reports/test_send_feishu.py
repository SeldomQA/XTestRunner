# !/usr/bin/env/python3
# -*- coding: utf-8 -*-
# @Author  : YingZi
# @Time    : 2022/8/29 下午10:56
# @Email   : yxdszlkc@163.com
# @File    : test_send_feishu.py
# @Software: PyCharm
import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import FeiShu


class TestDemo(unittest.TestCase):
    """测试用例说明"""

    def test_success(self):
        """执行成功"""
        self.assertEqual(8 + 4, 12)

    @unittest.skip("跳过用例")
    def test_skip(self):
        """跳过用例"""
        pass

    def test_fail(self):
        """失败用例"""
        self.assertEqual(5, 6)

    def test_error(self):
        """错误用例"""
        self.assertEqual('a', 6, msg="预期结果数据错误！")


if __name__ == '__main__':
    # 定义测试用例路径
    test_dir = '.'
    # 加载测试用例
    suit = unittest.defaultTestLoader.discover(test_dir, pattern='test_send_feishu.py')
    # 测试报告路径
    report = './reports/feishu_result.html'
    with open(report, 'wb') as fp:
        runner = HTMLTestRunner(
            tester='影子',
            stream=fp,
            title='集成测试报告',
            description=['类型：飞书消息推送', '操作系统：Windows', '浏览器：Chrome'],
            language='zh-CN',
            verbosity=2,
        )
        runner.run(suit)

        # 方法一
        runner.send_feishu(
            url="https://open.feishu.cn/open-apis/bot/v2/hook/XXXXX-XXX",
            secret="XXX",
            feishu_href='https://www.taobao.com',
            user_id='all',
            user_name='所有人'
        )

        # 方法二
        # feishu = FeiShu(
        #     url="XXXX",
        #     secret="XXX",
        #     feishu_href='http://www.baidu.com',
        #     # user_id='all',
        #     # user_name='所有人'
        # ).feishu_notice()