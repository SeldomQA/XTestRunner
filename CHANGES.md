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