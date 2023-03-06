import unittest
from XTestRunner import HTMLTestRunner
from random import randint


class TestDemo(unittest.TestCase):
    """测试用例说明"""

    def test_success(self):
        """执行成功"""
        self.assertEqual(2 + 3, 5)

    @unittest.skip("skip case")
    def test_skip(self):
        pass

    def test_fail(self):
        """ 失败用例 """
        num = randint(1, 5)
        self.assertEqual(num, 3)

    def test_error(self):
        """ 错误用例 """
        num = randint(1, 1)
        if num == 1:
            self.assertEqual(a, 2)


class TestDemo2(unittest.TestCase):

    def test_success(self):
        """成功用例2"""
        self.assertEqual(2 + 2, 4)


class TestDemo3(unittest.TestCase):

    def test_fail(self):
        """ 失败用例2 """
        num = randint(1, 5)
        self.assertEqual(num, 2)


if __name__ == '__main__':
    report = "./reports/test_unit.html"
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(fp, rerun=2))
