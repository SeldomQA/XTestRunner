# -*- coding: utf-8 -*-
# @Author  : yingzi
# @Time    : 2022/8/29 下午10:47
# @File    : _feishu.py
# @Software: PyCharm
import hashlib
import base64
import hmac
import time
import requests
import os
from jinja2 import Environment, FileSystemLoader
from XTestRunner.config import RunResult


class FeiShu:
    """发送飞书群通知"""

    def __init__(self, url, key=None, secret=None, user_id=None, user_name=None, feishu_href=None):
        """
        :param url: 飞书机器人的Webhook地址
        :param key: （非必传：str类型）如果飞书机器人安全设置了关键字，则需要传入对应的关键字
        :param secret:（非必传:str类型）如果飞书机器人安全设置了签名，则需要传入对应的密钥
        :param user_id: （非必传，str类型）发送通知飞书中要@人的open_id，如："ou_xxxxxxx"，所有人则必填，"all"
        :param user_name: 是否@所有人，默认为None,@个人需填名称如，"张三"，设为 "所有人" 则会@所有人
        :param feishu_href:测试报告连接地址，默认为None，需要填写具体的地址信息，如：https://www.baidu.com
        :return:  发送成功返回 {"StatusCode":0,"StatusMessage":"success"}  发送失败返回 {"StatusCode":错误码,"msg":"失败原因"}
        """
        self.url = url
        self.key = key
        self.secret = secret
        self.user_id = user_id
        self.user_name = user_name
        self.feishu_href = feishu_href

    def get_stamp(self):
        """加签"""
        timestamp = int(time.time())  # 获取当前以秒为单位的时间戳
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')  # 对结果进行base64处理
        return {"sign": sign, "timestamp": timestamp}

    def send_info(self, data):
        """发送消息"""
        if self.secret:  # 判断是否需要加签
            params = self.get_stamp()
        else:
            params = None
        response = requests.post(url=self.url, json=data, params=params)  # 发送请求
        return response.text

    @staticmethod
    def __get_feishu_notice_content():
        """获取通知的内容"""
        template_path = os.path.join(os.path.dirname(__file__), '../XTestRunner/html')
        env = Environment(loader=FileSystemLoader(template_path))
        res_text = env.get_template('notice_tmp.md').render(
            title=RunResult.title,
            tester=RunResult.tester,
            start_time=RunResult.start_time,
            end_time=RunResult.end_time,
            duration=RunResult.duration,
            p_number=RunResult.passed,
            pass_rate=RunResult.pass_rate,
            f_number=RunResult.failed,
            failure_rate=RunResult.failure_rate,
            e_number=RunResult.errors,
            error_rate=RunResult.error_rate,
            s_number=RunResult.skipped,
            skip_rate=RunResult.skip_rate,
        )

        return res_text

    def feishu_notice(self):
        res_text = self.__get_feishu_notice_content()

        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": '{}'.format(RunResult.title),
                        "content": [
                            [{
                                "tag": "text",
                                "text": res_text
                            }
                            ],
                            [{
                                "tag": "text",
                                "text": "  * 报告链接: "
                            },
                                {
                                    "tag": "a",
                                    "text": "请点我查看报告详情",
                                    "href": self.feishu_href
                                },
                                {
                                    "tag": "at",
                                    "user_id": self.user_id,
                                    "user_name": self.user_name
                                }
                            ]
                        ]
                    }
                }
            }
        }

        res = self.send_info(data)
        return res


if __name__ == '__main__':
    feishu = FeiShu(
        url="https://open.feishu.cn/open-apis/bot/v2/hook/XXX-XXX",
        secret="XXX",
        feishu_href='http://www.baidu.com',
        user_id='all',
        user_name='所有人'
    ).feishu_notice()
