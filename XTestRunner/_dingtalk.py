import os
import hmac
import time
import urllib
import base64
import hashlib
import requests
from jinja2 import Environment, FileSystemLoader
from XTestRunner.config import RunResult

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(BASE_DIR, "html")
env = Environment(loader=FileSystemLoader(HTML_DIR))


class DingTalk:
    """
    SendNail group notification
    help doc:
        https://open.dingtalk.com/document/group/enterprise-created-chatbot
    """

    def __init__(self,
                 access_token,
                 key: str = None,
                 app_secret: str = None,
                 at_mobiles: list = None,
                 is_at_all: bool = False):
        """
        :param access_token:  钉钉机器人的Webhook地址
        :param key: 如果钉钉机器人安全设置了关键字，则需要传入对应的关键字。
        :param app_secret: 如果钉钉机器人安全设置了签名，则需要传入对应的密钥。
        :param at_mobiles: 发送通知钉钉中要@人的手机号列表，如：[137xxx, 188xxx]。
        :param is_at_all: 是否@所有人，默认为False, 设为True则会@所有人。
        success:
                {"errcode":0, "errmsg":"ok"}
            fail:
                {"errcode":错误码, "errmsg":"失败原因"}
        """
        self.url = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}"
        self.key = key
        self.app_secret = app_secret
        self.at_mobiles = at_mobiles
        self.is_at_all = is_at_all

    @staticmethod
    def _get_notice_content():
        """
        get notice content
        """
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

    def _get_stamp(self) -> dict:
        """
        Counter sign
        """
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.app_secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.app_secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return {"sign": sign, "timestamp": timestamp}

    def sender(self, append: str = None, text: str = None):
        """
        send dingtalk notice
        :param append: appending sending information
        :param text : replace send message
        """
        res_text = self._get_notice_content()
        if append is not None:
            res_text = res_text + str(append)
        if text is not None:
            res_text = text

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": '{}({})'.format(RunResult.title, self.key),
                "text": res_text
            },
            "at": {
                "atMobiles": self.at_mobiles,
                "isAtAll": self.is_at_all
            }
        }
        params = {}
        if self.app_secret is not None:
            params = self._get_stamp()
        resp = requests.post(url=self.url, json=data, params=params).json()
        if resp["errcode"] == 0:
            print(" 📧 dingTalk sent successfully!!")
        else:
            print("❌ dingTalk failed to send!!")
            print(resp)
        return resp


if __name__ == '__main__':
    ding = DingTalk(
        access_token="690900b5ce6d5d10bb1218b8e64a4e2b55f96a6d116aaf50",
        key="xxxx",
        app_secret="xxxxx",
        at_mobiles=[13700000000, 13800000000],
        is_at_all=False,
    )
    ding.sender()
