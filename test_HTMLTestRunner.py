import HTMLTestRunner
import unittest


class TestDemo(unittest.TestCase):
    """
    测试用例说明
    """

    def test_success(self):
        """
        执行成功
        """
        self.assertEqual(2+3, 5)

    @unittest.skip("skip case")
    def test_skip(self):
        pass
    
    def test_fail(self):
        self.assertEqual(5, 6)

    def test_error(self):
        self.assertEqual(a, 6)


class TestDemo2(unittest.TestCase):

    def test_success(self):
        self.assertEqual(2+2, 4)


class TestDemo3(unittest.TestCase):

    def test_fail(self):
        self.assertEqual(3, 4)


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTest(TestDemo("test_success"))
    suit.addTest(TestDemo("test_skip"))
    suit.addTest(TestDemo("test_fail"))
    suit.addTest(TestDemo("test_error"))
    suit.addTest(TestDemo2("test_success"))
    suit.addTest(TestDemo3("test_fail"))

    fp = open('./result.html', 'wb')
    runner = HTMLTestRunner.HTMLTestRunner(
        stream=fp,
        title='<project name>test report',
        description='describe: ... '
    )

    runner.run(suit)
    fp.close()
