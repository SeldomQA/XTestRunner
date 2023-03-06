import unittest
from XTestRunner import HTMLTestRunner, XMLTestRunner
import xmlrunner


class NumbersTest(unittest.TestCase):

    def test_even(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        # self.assertEqual(1, 2)
        for i in range(0, 6):
            with self.subTest(i=i):
                self.assertEqual(i % 2, 0)

    def test_even_success(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        self.assertEqual(1, 1)


if __name__ == '__main__':
    report = "./test_subTest.html"
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(
            fp, rerun=3, language="zh-CN"
        ))

    # report = "./test_subTest.xml"
    # with(open(report, 'wb')) as fp:
    #     unittest.main(testRunner=XMLTestRunner(
    #         fp
    #     ))

    # unittest.main(
    #     testRunner=xmlrunner.XMLTestRunner(output='./test-reports-111.xml'),
    #     # these make sure that some options that are not applicable
    #     # remain hidden from the help menu.
    #     failfast=False, buffer=False, catchbreak=False)
    #
