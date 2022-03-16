import requests
import unittest
from XTestRunner import HTMLTestRunner

"""
* 安装requests
> pip install requests
"""


class YouTest(unittest.TestCase):

    def test_get(self):
        """测试get接口 """
        r = requests.get("https://httpbin.org/get", params={"key":"value"})
        print(r.json())

    def test_post(self):
        """测试post接口 """
        r = requests.post("https://httpbin.org/post", data={"key":"value"})
        print(r.json())

    def test_put(self):
        """测试put接口 """
        r = requests.put("https://httpbin.org/put", data={"key":"value"})
        print(r.json())

    def test_delete(self):
        """测试delete接口 """
        r = requests.delete("https://httpbin.org/delete", data={"key":"value"})
        print(r.json())


if __name__ == '__main__':
    report = "./reports/api_result.html"
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            tester="虫师",
            title='Seldom自动化测试报告',
            description=['类型：API', '地址：https://httpbin.org/']
        ))
