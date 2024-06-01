import json
import os
import unittest

import requests

from XTestRunner import HTMLTestRunner
from config import REPORTS_DIR

"""
* 安装requests
> pip install requests
"""


def formatting(msg):
    """formatted message"""
    if isinstance(msg, dict):
        return json.dumps(msg, indent=2, ensure_ascii=False)
    return msg


class ApiTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.base_url = "https://httpbin.org"

    def test_get(self):
        """测试get接口 """
        r = requests.get(f"{self.base_url}/get", params={"key": "value"})
        print(formatting(r.json()))

    def test_post(self):
        """测试post接口 """
        r = requests.post(f"{self.base_url}/post", data={"key": "value"})
        print(formatting(r.json()))

    def test_put(self):
        """测试put接口 """
        r = requests.put(f"{self.base_url}/put", data={"key": "value"})
        print(formatting(r.json()))

    def test_delete(self):
        """测试delete接口 """
        r = requests.delete(f"{self.base_url}/delete", data={"key": "value"})
        print(formatting(r.json()))


if __name__ == '__main__':
    # HTML report
    html_report = os.path.join(REPORTS_DIR, "test_api_result.html")
    with open(html_report, 'wb') as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            tester="虫师",
            title='api自动化测试报告',
            description=['类型：API', '地址：https://httpbin.org/']
        ))
