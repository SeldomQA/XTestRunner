import os
import unittest
from XTestRunner import HTMLTestRunner

test_dir = os.path.dirname(os.path.abspath(__file__))
suit = unittest.defaultTestLoader.discover(test_dir, "test_*.py")

if __name__ == '__main__':
    report = "./reports/all_result.html"
    with(open(report, 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='unittest单元测试测试报告',
            description=['类型：单元测试', '执行人：虫师']
        )
        runner.run(suit)
