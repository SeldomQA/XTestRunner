import requests
import unittest
from time import sleep
from TestRunner import HTMLTestRunner


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
    suit = unittest.TestSuite()
    suit.addTest(YouTest("test_get"))
    suit.addTest(YouTest("test_post"))
    suit.addTest(YouTest("test_put"))
    suit.addTest(YouTest("test_delete"))

    report = "./interface_result.html"
    with(open(report, 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='Seldom自动化测试报告',
            description='测试接口：http://httpbin.org'
        )
        runner.run(suit)
