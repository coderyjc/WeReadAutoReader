# -*- coding: utf-8 -*-

"""
@File    : Lang.py
@Time    : 2022/9/27 16:20
@Author  : DoooReyn<jl88744653@gmail.com>
@Desc    : 语言包
"""

from enum import Enum, unique


class LanguageKeys:
    """当前 UI 仍在使用的语言键"""

    app_name = "app_name"
    debug_network_error = "debug_network_error"
    tips_auto_read_on = "tips_auto_read_on"


class _Languages:
    """语言包列表"""

    CN = {
        "app_name": "微读自动阅读",
        "debug_network_error": "网络似乎有点问题。\n错误代码: {0}\n错误信息: {1}",
        "tips_auto_read_on": "自动阅读中...",
    }


@unique
class LangPack(Enum):
    """语言包可选项"""

    CN = _Languages.CN
