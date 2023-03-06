## 发送消息

XTestRunner支持发送不同类型的通知。

### 发送邮件

1. 使用126邮箱发送时password应为授权码而非用户密码，须在邮箱客户端设置开启授权码
2. 使用gmail邮箱发送时password为用户密码，须在gmail客户端开启安全性较低的应用的访问权限

```python
import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import SMTP
class TestEmail(unittest.TestCase):
    """测试用例说明"""

    def test_success(self):
        self.assertEqual(2 + 3, 5)

    @unittest.skip("skip case")
    def test_skip(self):
        pass

    def test_fail(self):
        self.assertEqual(5, 6)

    def test_error(self):
        self.assertEqual(a, 6)


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTests([
        TestEmail("test_success"),
        TestEmail("test_skip"),
        TestEmail("test_fail"),
        TestEmail("test_error")
    ])

    report = "./reports/email_result.html"
    with(open(report, 'wb')) as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='测试发送邮件',
            tester='虫师',
            description=['类型：测试发送邮件'],
            language="zh-CN"
        )
        runner.run(suit)
        # 发送邮件方式 1：send_email()方法
        runner.send_email(
            user="sender@qq.com",
            password="xxx",
            host="smtp.qq.com",
            to="recipient@126.com",
            attachments=report,
            ssl=True
        )
    # 发送方式 2：SMTP类
    smtp = SMTP(user="sender@qq.com", password="xxx", host="smtp.qq.com", ssl=True)
    smtp.sender(to="recipient@126.com", subject="XTestRunner测试邮件", attachments=report)
```

__参数说明__

* user: 邮箱用户名。
* password: 邮箱密码。
* host: 协议，例如："smtp.qq.com" 。
* to: 收件人，例如："recipient@126.com" 或者 ["aa@qq.com", "bb@qq.com"] 。
* subject: 邮件标题。
* attachments: 附件，可以指定生成的测试报告。
* ssl: 如果设为True使用SMTP_SSL() ，否则使用 SMTP() 

__邮件展示__

![](../img/test_mail.png)


### 发送钉钉

* 示例

```python
import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import DingTalk


class TestDing(unittest.TestCase):
    """
    测试用例说明
    """

    def test_success(self):
        ...

    
if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTests([
        TestDing("test_success"),
        TestDing("test_skip"),
        TestDing("test_fail"),
        TestDing("test_error")
    ])

    report = "./reports/test_send_dingtalk.html"
    with open(report, 'wb') as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='测试发送钉钉',
            tester='虫师',
            description=['类型：测试发送钉钉'],
            language="zh-CN"
        )
        runner.run(suit)
        # 方式一： send_dingtalk() 方法
        runner.send_dingtalk(
            access_token="690900b5ce6d5d10bb1218b8e64a4e2b55f96a6d116aaf50",
            key="xxxx",
            app_secret="xxxxx",
            at_mobiles=[13700000000, 13800000000],
            is_at_all=False,
        )

    # 方式二： DingTalk 类
    ding = DingTalk(
        access_token="690900b5ce6d5d10bb1218b8e64a4e2b55f96a6d116aaf50",
        key="xxxx",
        app_secret="xxxxx",
        at_mobiles=[13700000000, 13800000000],
        is_at_all=False
    )
    ding.sender()
```

帮助文档:
https://open.dingtalk.com/document/group/enterprise-created-chatbot
* access_token:  钉钉机器人的access_token
* key: 如果钉钉机器人安全设置了关键字，则需要传入对应的关键字。
* app_secret: 如果钉钉机器人安全设置了签名，则需要传入对应的密钥。
* at_mobiles: 发送通知钉钉中要@人的手机号列表，如：[137xxx, 188xxx]。
* is_at_all: 是否@所有人，默认为False, 设为True则会@所有人。

### 发送飞书

* 示例

```python

import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import FeiShu


class TestDing(unittest.TestCase):
    """
    测试用例说明
    """

    def test_success(self):
        ...


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTests([
        TestDing("test_success"),
        TestDing("test_skip"),
        TestDing("test_fail"),
        TestDing("test_error")
    ])

    report = "./reports/test_send_feishu.html"
    with open(report, 'wb') as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='测试发送钉钉',
            tester='虫师',
            description=['类型：测试发送钉钉'],
            language="zh-CN"
        )
        runner.run(suit)
        # 方式一： send_dingtalk() 方法
        runner.send_feishu(
            url="https://open.feishu.cn/open-apis/bot/v2/hook/XXX-XXX",
            secret="XXX",
            feishu_href='http://www.baidu.com',
            user_id='all',
            user_name='所有人'
        )

    # 方式二： FeiShu 类
    ding = FeiShu(
        url="https://open.feishu.cn/open-apis/bot/v2/hook/XXX-XXX",
        secret="XXX",
        feishu_href='http://www.baidu.com',
        user_id='all',
        user_name='所有人'
    )
    ding.feishu_notice()
```

帮助文档:
https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN
* url: 飞书机器人的Webhook地址
* key: （非必传：str类型）如果飞书机器人安全设置了关键字，则需要传入对应的关键字
* secret:（非必传:str类型）如果飞书机器人安全设置了签名，则需要传入对应的密钥
* user_id: （非必传，str类型）发送通知飞书中要@人的open_id，如："ou_xxxxxxx"，所有人则必填，"all"
* user_name: 是否@所有人，默认为None,@个人需填名称如，"张三"，设为 "所有人" 则会@所有人
* feishu_href:测试报告连接地址，默认为None，需要填写具体的地址信息，如：https://www.baidu.com


### 发送微信

* 示例

```python
import unittest
from XTestRunner import HTMLTestRunner
from XTestRunner import Weinxin

class TestDing(unittest.TestCase):
    """
    测试用例说明
    """

    def test_success(self):
        ...


if __name__ == '__main__':
    suit = unittest.TestSuite()
    suit.addTests([
        TestDing("test_success"),
        TestDing("test_skip"),
        TestDing("test_fail"),
        TestDing("test_error")
    ])

    report = "./reports/dingtalk_result.html"
    with open(report, 'wb') as fp:
        runner = HTMLTestRunner(
            stream=fp,
            title='测试发送钉钉',
            tester='虫师',
            description=['类型：测试发送钉钉'],
            language="zh-CN"
        )
        runner.run(suit)
        # 方式一： send_dingtalk() 方法
        runner.send_weixin(
            access_token="50327a8c-59c3-4be7-bf44-a7ad4ec749b59",
            at_mobiles=[13700000000, 18800000000],
            is_at_all=False,
        )

    # 方式二： FeiShu 类
    weixin = Weinxin(
        access_token="50327a8c-59c3-4be7-bf44-a7ad4ec749b59",
        at_mobiles=[13700000000, 18800000000],
        is_at_all=False,
    )
    weixin.send_text(text="\n ### 附加信息")
    weixin.send_markdown(append="\n ### 附加信息")

```

帮助文档:
https://developer.work.weixin.qq.com/document/path/91770
* access_token:  企业微信机器人的Webhook地址的key
* at_mobiles: 发送通知企业微信中要@人的手机号列表，如：[137xxx, 188xxx]。
* is_at_all: 是否@所有人，默认为False, 设为True则会@所有人。


