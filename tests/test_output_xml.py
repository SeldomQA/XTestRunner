import os
import unittest

from XTestRunner import XMLTestRunner
from config import REPORTS_DIR


class TestDemo(unittest.TestCase):
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


if __name__ == '__main__':
    xml_report = os.path.join(REPORTS_DIR, "test_output_xml.xml")
    with open(xml_report, 'wb') as fp:
        unittest.main(testRunner=XMLTestRunner(output=fp))
