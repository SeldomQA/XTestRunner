from typing import Dict

# language map
LANGUAGE_TAGS = {
    "en": {
        "PASSED": "Passed",
        "FAILURE": "Failure",
        "ERRORS": "Errors",
        "SKIPPED": "Skipped",
        "LOG": "log",
        "DETAIL": "Detail",
        "DETAILED_LOG": "detailed log"

    },
    "zh-CN": {
        "PASSED": "通过",
        "FAILURE": "失败",
        "ERRORS": "错误",
        "SKIPPED": "跳过",
        "LOG": "日志",
        "DETAIL": "详情",
        "DETAILED_LOG": "日志详情"
    }
}


def language_tag(language: str = "en") -> Dict[str, str]:
    """
    get language tags

    :param language:
    :return:
    """
    if language not in LANGUAGE_TAGS:
        raise ValueError(f"Unsupported language code: {language}.")

    return LANGUAGE_TAGS[language]
