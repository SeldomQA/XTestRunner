import json
import requests
import unittest
from XTestRunner import HTMLTestRunner

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

    def test_get(self):
        """测试get接口 """
        r = requests.get("https://httpbin.org/get", params={"key": "value"})
        print(formatting(r.json()))

    def test_post(self):
        """测试post接口 """
        r = requests.post("https://httpbin.org/post", data={"key": "value"})
        print(formatting(r.json()))

    def test_put(self):
        """测试put接口 """
        r = requests.put("https://httpbin.org/put", data={"key": "value"})
        print(formatting(r.json()))

    def test_delete(self):
        """测试delete接口 """
        r = requests.delete("https://httpbin.org/delete", data={"key": "value"})
        print(formatting(r.json()))


if __name__ == '__main__':
    report = "./reports/test_api.html"
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            tester="虫师",
            title='api自动化测试报告',
            description=['类型：API', '地址：https://httpbin.org/']
        ))
