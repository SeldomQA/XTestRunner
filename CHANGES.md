### 1.7.0 版本
* 样式调整
  * 新增：统计数据 
  * 优化：概述样式调整 

### 1.6.3 版本
* 修复：email发送邮件提示：`STARTTLS extenstion not supported by server`，增加 tls 开关 
* 修复：HTML报告提示：handler ID 删除错误 

### 1.6.2 版本
* 修复`seldom/loguru`使用XTestRunner 日志错误
* HTML报告：修改 skip class/case 样式颜色 

### 1.6.1 版本
* 紧急修复 jinja2 版本依赖问题，升级jinja2=^3.1.2 版本

### 1.6.0 版本
* XML报告
  * 支持 `rerun` 重跑参数。
  * 修复 `subTest` 用例统计错误问题。
* HTML报告
  * 移除 `save_last_run` 参数， ⚠️ 不兼容修改。
  * 修改 `rerun` 传参位置，只保留最后执行结果， ⚠️ 不兼容修改。
  * 修复 error 用例统计错误。
* 邮件：支持SMTP_SSL和 SMTP, 增加`ssl`参数，详情查看文档。感谢 @wu-clan
* 微信：优化代码，提供`send_weixin()`方法，详情查看文档。
* 打包：`pyproject.toml` 替换 `setup.py` 感谢 @wu-clan

### 1.5.0 版本

* 新增飞书推送，感谢 @yingzi(3011456083@qq.com)
* 新增微信推送，感谢 @Yingqing Shan(yingqing.shan@sayweee.com)
* 修复：邮件发送错误： `smtplib.SMTP_SSL()` 改为 `smtplib.SMTP()`。
* 修复：测试类统计错误：测试类没有统计`跳过`的用例。

### 1.4.6 版本

* 修复 AttributeError 异常

### 1.4.5 版本

* 支持Seldom日志显示运行文件。

### 1.4.4 版本

* DingTalk 消息支持追加消息和自定义消息

### 1.4.3 版本

* xml报告优化：
  * 支持黑白名单：`whitelist\blacklist`。
  * 增加`<doc>` 标签，显示用例描述。
* HTML报告优化：
  * 修复截图错误

### 1.4.2 版本

* 该版本优化了若干样式：
  * `日志详情`采用弹窗，查看日志更方便。
  * `截图弹窗`采用统一的弹窗，同上。
  * `日志详情`第一行前面的空格去掉。@yongchin0821
  * `用例描述` 超过宽度自动换行。
* 其他：修改打印日志的获取。@yongchin0821

### 1.4.1 版本

* 功能：HTML报告支持`subTest()`统计用例。


### 1.4.0 版本

* 功能：HTML报告增加`结束时间`。
* 功能：邮件默认使用报告标题。
* 功能：邮件和钉钉消息提供更多信息：`开始时间`、`结束时间`、`运行时长`、`通过率`、`失败率`、`错误率`、`跳过率`。


### 1.3.2 版本

* 修复：用例总数统计未计算跳过的用例。
* 修复：用例数过大样式问题。

### 1.3.1 版本

* 修复：钉钉通知结果显示错误。

### 1.3.0 版本

* 功能：支持钉钉（dingtalk）发送通知 [文档](./docs/send_notice.md)。
* 功能：HTMLTestRunner类`run()`方法增加 `tester` 字段用于设置测试人员。
* 功能：邮件通知增加`标题` 和 `测试人员`。
* 修复：设置title未写入报告

### 1.2.0 版本

* 支持`XML`格式（XMLTestRunner）的报告。
* 优化邮件模板样式。
* HTMLTestRunner 运行增加打印。

### 1.1.1 版本

* `1.0.0` 打包的安装文件有严重的bug，已从 pypi 移除。
* 优化 selenium 截图样式。

### 1.1.0 版本

* 支持`黑`、`白`名单：通过给用例加上` @label("xx")` 装饰器，可以选择在执行的时候执行或跳过用例。
* 支持多语言：`en/zh-CN`, 默认`en`。
* 优化`概述`部分的样式。
* 设计全新的logo。

### XTestRunner 1.0.0

* 正式更名为`XTestRunner`, 支持 `pip` 安装。
* 使用全新的样式，更加现代化。
* 去掉EChart 饼状图，采用全新的卡片。
* 增加`通过率`, `失败率`，`错误率`，`跳过率` 等信息。

Change History
Version 1.0.0
* Add Jinjia Library
* All code refactoring

Version 0.9.0
* Increased repeat execution
* Added failure screenshots

Version 0.8.2
* Show output inline instead of popup window (Viorel Lupu).

Version in 0.8.1
* Validated XHTML (Wolfgang Borgert).
* Added description of test classes and test cases.

Version in 0.8.0
* Define TemplateMixing class for customization.
* Workaround a IE 6 bug that it does not treat <script> block as CDATA.

Version in 0.7.1
* Back port to Python 2.3 (Frank Horowitz).
* Fix missing scroll bars in detail log (Podi).