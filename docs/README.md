# XTestRunner 文档 [中文版]

unittest单元测试框架：

https://docs.python.org/3/library/unittest.html

## 安装

* pip安装

```shell
> pip install XTestRunner
```


## 使用文档

* [HTML/XML测试报告](./test_report.md)
  * [HTML测试报告](./test_report.md#HTML测试报告)
  * [XML测试报告](./test_report.md#XML测试报告)

* [不同类型的测试](./test_type.md)
  * [单元测试](./test_type.md#单元测试)
  * [Selenium Web测试](./test_type.md#SeleniumWeb测试)
  * [API 接口测试](./test_type.md#API接口测试)

* [发送消息](./send_notice.md)
  * [发送邮件](./send_notice.md#发送邮件)
  * [发送钉钉](./send_notice.md#发送钉钉)
  * [发送飞书](./send_notice.md#发送飞书)
  * [发送微信](./send_notice.md#发送微信)

* [其他功能](./other.md)
  * [黑白名单](./other.md#黑白名单)


## 例子

* [生成HTML报告](../tests/test_unit_html.py)

* [生成XML报告](../tests/test_unit_xml.py)

* [单元测试](../tests/test_unit.py)

* [Selenium自动化测试](../tests/test_selenium.py)

* [requests接口测试](../tests/test_api.py)

* [发送邮件](../tests/test_send_email.py)

* [发送钉钉消息](../tests/test_send_dingtalk.py)

* [发送飞书消息](../tests/test_send_feishu.py)

* [发送企微消息](../tests/test_send_weixin.py)

* [黑白名单](../tests/test_label.py)




