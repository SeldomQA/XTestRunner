![](./XTestRunner_logo.jpg)

> Modern style test report based on unittest framework.

基于unittest框架现代风格测试报告。

### 特点

* 漂亮测试报告让你更愿意做测试。
* 支持`单元`、`Web UI`、`API` 各种类型的测试。
* 支持`Selenium`运行失败/错误自动截图。
* 支持失败重跑。
* 支持标签黑、白名单。
* 支持发邮件功能。
* 支持多语言`en`、`zh-CN` 等。


## Report

![](./img/test_report.png)


## Install

```shell
> pip install XTestRunner
```

If you want to keep up with the latest version, you can install with github repository url:

```shell
> pip install -U git+https://github.com/SeldomQA/XTestRunner.git@master
```

## demo

查看更多使用 [例子](./test)。

* 单元测试 

```python
import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import label


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

    @label("fail")
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
            description='describe: ... ',
            language='en',
            blacklist=["fail"],
        )
        runner.run(suit)
```

__`HTMLTestRunner`类说明__

* `stream`: 指定报告的路径。
* `title`: 报告的标题。
* `description`: 报告的描述, 支持`str`、`list`两种类型。
* `language`: 支持中文`zh-CN`, 默认`en`。
* `blacklist/whitelist`: 黑白名单。
  * 白名单：`whitelist=["fail"]`  只有使用`@label("fail")`装饰的用例执行。
  * 黑名单：`blacklist=["fail"]`  只有使用`@label("fail")`装饰的用例不被执行。

__`run()`方法说明__

* `suit`: 运行的测试套件。
* `rerun`: 重跑次数。
* `save_last_run`: 是否保存最后一个结果。

## 感谢

感谢从以下项目中得到思路和帮助。

* [HTMLTestRunner](http://tungwaiyip.info/software/HTMLTestRunner.html)

* [HTMLTestRunner_cn](https://github.com/GoverSky/HTMLTestRunner_cn)

* [Theme style](https://clever-dashboard.webpixels.work/pages/tasks/list-view.html)
