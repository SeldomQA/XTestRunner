## 其他

XTestRunner还支持一些其他功能。

### 黑白名单

可以通过黑白名单选择要执行（或跳过）的用例。

* 支持白黑名单
  * 白名单：whitelist=["base"]  只有使用@label("base")装饰的用例执行
  * 黑名单：blacklist=["slow"]  只有使用@label("slow")装饰的用例不被执行

__测试用例__

```python
import unittest
from XTestRunner import label
from XTestRunner import HTMLTestRunner, XMLTestRunner


class LabelTest(unittest.TestCase):

    @label("base")
    def test_label_base(self):
        self.assertEqual(1+1, 2)

    @label("slow")
    def test_label_slow(self):
        self.assertEqual(1, 2)

    def test_no_label(self):
        self.assertEqual(2+3, 5)


if __name__ == '__main__':
    # HTML 报告
    report = './reports/test_label.html'
    with(open(report, 'wb')) as fp:
        unittest.main(testRunner=HTMLTestRunner(
            stream=fp,
            tester="虫师",
            title='<project name>test report',
            description='describe: ... ',
            # whitelist=["base"],  # 设置白名单
            blacklist=["slow"],  # 设置黑名单
        ))
    # XML 报告
    # report = './reports/test_label.xml'
    # with(open(report, 'wb')) as fp:
    #     unittest.main(testRunner=XMLTestRunner(
    #         output=fp,
    #         # whitelist=["base"],  # 设置白名单
    #         blacklist=["slow"],  # 设置黑名单
    #     ))

```

> 注意： 白名单和黑名单不要同时用，以免产生冲突。


### subTest

> 当您的测试之间存在非常小的差异时，例如某些参数，unittest 允许使用 subTest() 上下文管理器在测试方法的主体内区分它们。

XTestRunner 对 subTest 做了支持。

```python
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

```
