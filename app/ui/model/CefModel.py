# -*- coding: utf-8 -*-

"""
@File    : CefModel.py
@Time    : 2022/9/27 17:21
@Author  : DoooReyn<jl88744653@gmail.com>
@Desc    : cef 数据
"""


class CefModel:
    # 首页
    HOME_PAGE = "https://weread.qq.com"

    # 阅读页面
    BOOK_PAGE = "https://weread.qq.com/web/reader/"

    # CEF 刷新频率
    MS_CEF = 10

    # 自动阅读刷新频率
    MS_AUTO = 85

    class Action:
        """Js -> Python 动作"""

        # 滚动至底部
        ScrollToEnd = 1

        # 全书完
        ReadingFinished = 2

        values = (ScrollToEnd, ReadingFinished,)

    class ShortCut:
        """快捷键"""

        # ALT + Q
        Quit = 81
        # F4
        Home = 115
        # F5
        Reload = 116
        # F10
        Auto = 121
        # F12
        Timing = 123
        # =
        SpeedUp = 187
        # -
        SpeedDown = 189

        values = (
            Home, Reload, Auto, Timing, SpeedUp, SpeedDown,
        )

    class PyMethod:
        """Js to Py Binding"""
        UpdateState = 'updateState'
        SendAction = 'sendAction'

    class JsMethod:
        """Py to Js Binding"""
        NextChapter = 'nextChapter'
        DoScroll = 'doScroll'
        Alert = 'alert'

    @staticmethod
    def isBookUrl(url: str):
        """是否阅读页面"""
        return url.startswith(CefModel.BOOK_PAGE)
