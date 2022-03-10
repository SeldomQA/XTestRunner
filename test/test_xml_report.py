import unittest
from XTestRunner import XMLTestRunner


class TestXML(unittest.TestCase):
    """测试用例说明"""

    def test_success(self):
        """执行成功"""
        self.assertEqual(2 + 3, 5)

    @unittest.skip("skip case")
    def test_skip(self):
        pass

    def test_fail(self):
        self.assertEqual(5, 6)

    def test_error(self):
        self.assertEqual(a, 6)


class TestXML2(unittest.TestCase):

    def test_success(self):
        self.assertEqual(2 + 2, 4)


class TestXML3(unittest.TestCase):

    def test_fail(self):
        self.assertEqual(3, 4)


if __name__ == '__main__':
    # 定义报告
    report = "./reports/xml_result.xml"
    # 运行方式1
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=XMLTestRunner(output=fp))

    # 运行方式2
    # suit = unittest.TestSuite()
    # suit.addTests([
    #     TestXML("test_success"),
    #     TestXML("test_success"),
    #     TestXML("test_skip"),
    #     TestXML("test_fail"),
    #     TestXML("test_error"),
    #     TestXML2("test_success"),
    #     TestXML3("test_fail")
    # ])
    #
    # with(open(report, 'wb')) as fp:
    #     runner = XMLTestRunner(output=fp)
    #     runner.run(suit)
