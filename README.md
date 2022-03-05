# XTestRunner

> A next-generation unittest test report.

下一代unittest单元测试框架测试报告。

## Report

![](./img/test_report.png)


## install

```shell
> git clone https://github.com/SeldomQA/XTestRunner
> cd XTestRunner/
> python setup.py install
```

## demo

* 单元测试 

```python
import unittest
from XTestRunner import HTMLTestRunner


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


class TestDemo2(unittest.TestCase):

  def test_success(self):
    self.assertEqual(2 + 2, 4)


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

  with(open('./reports/result.html', 'wb')) as fp:
    runner = HTMLTestRunner(
      stream=fp,
      title='<project name>test report',
      description='describe: ... '
    )
    runner.run(suit)
```

__`HTMLTestRunner`类说明__

* stream ： 指定报告的路径
* title ： 报告的标题
* description ： 报告的描述

__`run()`方法说明__
* suit ： 运行的测试套件
* rerun ：重跑次数
* save_last_run ：是否保存最后一个结果

## 感谢

感谢从以下项目中得到思路和帮助。

* [HTMLTestRunner](http://tungwaiyip.info/software/HTMLTestRunner.html)

* [HTMLTestRunner_cn](https://github.com/GoverSky/HTMLTestRunner_cn)

* [Theme style](https://clever-dashboard.webpixels.work/pages/tasks/list-view.html)
