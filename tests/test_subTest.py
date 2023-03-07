import unittest
from XTestRunner import HTMLTestRunner, XMLTestRunner


class MyTest(unittest.TestCase):

    def test_even(self):
        """
        Test that numbers between 0 and 5 are all even.
        """
        for i in range(0, 6):
            with self.subTest(i=i):
                self.assertEqual(i % 2, 0)


if __name__ == '__main__':
    report = "./reports/test_subTest.html"
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(fp))

    # report = "./reports/test_subTest.xml"
    # with(open(report, 'wb')) as fp:
    #     unittest.main(testRunner=XMLTestRunner(fp))
