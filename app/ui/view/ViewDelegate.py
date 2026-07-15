# -*- coding: utf-8 -*-

"""
@File    : ViewDelegate.py
@Time    : 2022/10/22 15:33
@Author  : DoooReyn<jl88744653@gmail.com>
@Desc    : 视图代理
"""
from PySide6.QtWidgets import QWidget

from helper.Preferences import gPreferences
from helper.Signals import gSignals


class ViewDelegate(object):
    """视图代理"""

    def __init__(self, win: QWidget, code: int, key: str):
        """
        视图
        :param win: 视图对象
        :param code: 视图代码
        :param key: 视图尺寸存储项
        """
        self.view: QWidget = win
        self.code: int = code
        self.key: str = key
        self.setWindowCode(code)
        self.setWinRectKey(key)

    def closeEvent(self, event):
        """视图关闭事件"""
        if self.key is not None:
            self.saveWinRect()
        if self.code > 0:
            gSignals.win_closed.emit(self.code)
        event.accept()

    def resizeEvent(self, event):
        """视图尺寸变化事件"""
        if self.key is not None:
            self.saveWinRect()
        event.accept()

    def setWindowCode(self, code: int):
        """设置视图代码"""
        self.code = code

    def setWinRectKey(self, kr: str):
        """设置视图尺寸存储项"""
        self.key = kr
        tx, ty, w, h = self.getWinRect()
        self.view.setGeometry(tx, ty, w, h)

    def getWinRect(self):
        """获取视图尺寸"""
        if self.key is not None:
            return [int(v) for v in gPreferences.get(self.key)]
        else:
            r = self.view.geometry()
            return r.topLeft().x(), r.topLeft().y(), r.width(), r.height()

    def saveWinRect(self):
        """保存视图尺寸"""
        if self.key is not None:
            r = self.view.geometry()
            r = [r.topLeft().x(), r.topLeft().y(), r.width(), r.height()]
            gPreferences.set(self.key, r)

