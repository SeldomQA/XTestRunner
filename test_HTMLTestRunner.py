import HTMLTestRunner
import unittest

class TestDemo(unittest.TestCase):

    def test_success(self):
        self.assertEqual(5, 5)

    def test_success2(self):
        self.assertEqual(20, 20)
    
    def test_fail(self):
        self.assertEqual(5, 6)

    def test_error(self):
        self.assertEqual(a, 6)

if __name__ == '__main__':
    testunit=unittest.TestSuite()
    testunit.addTest(TestDemo("test_success"))
    testunit.addTest(TestDemo("test_success2"))
    testunit.addTest(TestDemo("test_fail"))
    testunit.addTest(TestDemo("test_error"))

    fp = open('./result.html', 'wb')
    runner =HTMLTestRunner.HTMLTestRunner(stream=fp,
                                          title=u'<project name>test report',
                                          description=u'describe: ... ')

    runner.run(testunit)
    fp.close()
