import unittest
from time import sleep
from XTestRunner import HTMLTestRunner
from selenium import webdriver

"""
1.安装selenium
> pip install selenium

2.注意：驱动必须定义为 `driver`， 否则无法生成截图
"""


class YouTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = webdriver.Chrome()
        cls.base_url = "https://www.baidu.com"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()

    def test_success(self):
        """测试百度搜索：HTMLTestRunner """
        self.driver.get(self.base_url)
        self.driver.find_element_by_id("kw").send_keys("XTestRunner")
        self.driver.find_element_by_id("su").click()
        sleep(2)

    def test_error(self):
        """测试百度搜索，定位失败 """
        self.driver.get(self.base_url)
        self.driver.find_element_by_id("kw").send_keys("python")
        self.driver.find_element_by_id("su22").click()
        sleep(2)

    def test_fail(self):
        """测试百度搜索，断言失败 """
        self.driver.get(self.base_url)
        self.driver.find_element_by_id("kw").send_keys("unittest")
        self.images.append(self.driver.get_screenshot_as_base64())
        self.driver.find_element_by_id("su").click()
        sleep(2)
        self.images.append(self.driver.get_screenshot_as_base64())
        self.assertEqual(self.driver.title, "unittest")


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTest(YouTest("test_success"))
    suit.addTest(YouTest("test_error"))
    suit.addTest(YouTest("test_fail"))

    report = "./reports/selenium_result.html"
    with(open(report, 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='Seldom自动化测试报告',
            description=['类型：selenium', '操作系统：Windows', '浏览器：Chrome', '执行人：虫师']
        )
        runner.run(suit)
