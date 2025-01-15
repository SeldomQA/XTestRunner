import os.path
import time
import shutil


class Config:
    language = "en"  # en/ zh-CN


class RunResult:
    """
    Test run results
    """
    title = "XTestRunner Test Report"
    tester = "Anonymous"
    start_time = time.strftime("%Y-%m-%d %H:%M:%S")
    end_time = time.strftime("%Y-%m-%d %H:%M:%S")
    duration = "0:00:00"
    passed = 0
    failed = 0
    errors = 0
    skipped = 0
    count = 0
    pass_rate = 0.00
    failure_rate = 0.00
    error_rate = 0.00
    skip_rate = 0.00


def label(*labels):
    """
    Test case classification label

    Usage:
        @label('quick')
        class MyTest(unittest.TestCase):
            def test_foo(self):
                pass
    """

    def inner(cls):
        # append labels to class
        cls._labels = set(labels) | getattr(cls, '_labels', set())
        return cls

    return inner


def static_file(is_local_style=False, report_path: str = None) -> dict:
    """
    static file path
    :param is_local_style:
    :param report_path:
    :return:
    """
    if is_local_style is True:
        if report_path is None:
            raise FileNotFoundError("report path is null")

        report_dir = os.path.dirname(report_path)
        dst_static_dir = os.path.join(report_dir, "static")
        root_dir = os.path.dirname(os.path.abspath(__file__))
        src_static_dir = os.path.join(root_dir, "html", "static")
        # copy static file
        shutil.copytree(src_static_dir, dst_static_dir, dirs_exist_ok=True)
        # local static file
        jquery_url = echarts_url = "static/js/"
        css_url = "static/css/"
        png_url = "static/images/"
    else:
        jquery_url = "https://libs.baidu.com/jquery/2.0.0/"
        echarts_url = "https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.2/"
        css_url = png_url = "https://telegraph-image-cq2.pages.dev/"

    static_dir = {
        "jquery_url": jquery_url,
        "echarts_url": echarts_url,
        "css_url": css_url,
        "png_url": png_url
    }
    return static_dir
