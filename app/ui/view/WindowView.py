# -*- coding: utf-8 -*-

"""
@File    : WindowView.py
@Time    : 2022/10/7 15:09
@Author  : DoooReyn<jl88744653@gmail.com>
@Desc    : 主视图
"""
from typing import Any, Dict, Optional

from PySide6.QtCore import QDateTime, Qt, QTime, QTimer
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSlider,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from conf.Lang import LanguageKeys
from conf.ResMap import ResMap
from conf.Views import Views
from helper.Cmm import Cmm
from helper.GUI import GUI
from helper.I18n import I18n
from helper.Preferences import READER_SPEED_MAX, READER_SPEED_MIN, UserKey, gPreferences, normalize_reader_speed
from helper.Signals import gSignals
from ui.model.CefModel import CefModel
from ui.view.CefView import CefView
from ui.view.TimingView import TimingPanel
from ui.view.ViewDelegate import ViewDelegate


DAY_MS = 24 * 60 * 60 * 1000


DAYLIGHT_STYLE = """
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fff8eb, stop:0.52 #e7f4ff, stop:1 #fff0d8);
}
QWidget#RootSurface {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fff8eb, stop:0.52 #e7f4ff, stop:1 #fff0d8);
}
QWidget#BrowserSurface {
    background: #f2f7fb;
}
QFrame#ControlPanel {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #fffaf0, stop:0.48 #eef8ff, stop:1 #fff4df);
    border-bottom: 1px solid #d7d0c2;
}
QFrame#StatusPill {
    background: rgba(255, 255, 255, 178);
    border: 1px solid #d8d4ca;
    border-radius: 15px;
}
QFrame#StatusPill[active="true"] {
    background: #e4f7ef;
    border-color: #7fd6b1;
}
QLabel#Eyebrow {
    color: #1f75b8;
    font-family: "Consolas", "Microsoft YaHei UI";
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0px;
}
QLabel#AppTitle {
    color: #16202a;
    font-family: "Microsoft YaHei UI";
    font-size: 22px;
    font-weight: 700;
}
QLabel#AppSubtitle,
QLabel#Caption,
QLabel#MetaText {
    color: #637384;
    font-size: 12px;
}
QLabel#StatusText {
    color: #1c2a34;
    font-size: 13px;
    font-weight: 600;
}
QLabel#SpeedValue {
    color: #16202a;
    font-family: "Consolas", "Microsoft YaHei UI";
    font-size: 13px;
    font-weight: 700;
}
QPushButton {
    min-height: 34px;
    padding: 5px 15px;
    border-radius: 8px;
    border: 1px solid #cfd8de;
    background: rgba(255, 255, 255, 196);
    color: #16202a;
    font-size: 13px;
    font-weight: 600;
}
QPushButton:hover {
    background: #ffffff;
    border-color: #7dbbe7;
}
QPushButton:pressed {
    background: #e8f2fb;
}
QPushButton#PrimaryButton {
    min-height: 42px;
    padding: 7px 22px;
    border: 1px solid #1f75d6;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f75d6, stop:1 #13a887);
    color: #ffffff;
    font-weight: 700;
}
QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2f83e2, stop:1 #21b896);
    border-color: #2f83e2;
}
QPushButton#PrimaryButton:checked {
    border-color: #c75a32;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #d55d34, stop:1 #f0a13a);
    color: #ffffff;
}
QPushButton#SecondaryButton {
    background: transparent;
    border-color: #cfd8de;
    color: #1c2a34;
}
QPushButton#SecondaryButton:hover {
    background: rgba(255, 255, 255, 190);
    border-color: #7dbbe7;
}
QPushButton#SecondaryButton:checked {
    background: #e4f7ef;
    border-color: #13a887;
    color: #0f6f60;
}
QPushButton#QuietButton {
    background: transparent;
    border-color: transparent;
    color: #526272;
}
QPushButton#QuietButton:hover {
    background: rgba(255, 255, 255, 160);
    border-color: rgba(255, 255, 255, 160);
}
QSlider::groove:horizontal {
    height: 6px;
    border-radius: 3px;
    background: #d5e3ea;
}
QSlider::sub-page:horizontal {
    height: 6px;
    border-radius: 3px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f75d6, stop:1 #13a887);
}
QSlider::handle:horizontal {
    width: 20px;
    height: 20px;
    margin: -8px 0;
    border-radius: 10px;
    border: 2px solid #ffffff;
    background: #1f75d6;
}
QSlider::handle:horizontal:hover {
    background: #13a887;
}
"""


class _View(ViewDelegate):
    """主视图 UI"""

    def __init__(self, win, code, key):
        super(_View, self).__init__(win, code, key)

        self.ui_root = QWidget(self.view)
        self.ui_root.setObjectName("RootSurface")

        self.ui_layout = QVBoxLayout(self.ui_root)
        self.ui_layout.setContentsMargins(0, 0, 0, 0)
        self.ui_layout.setSpacing(0)

        self.ui_panel = QFrame(self.ui_root)
        self.ui_panel.setObjectName("ControlPanel")
        self.ui_panel_layout = QVBoxLayout(self.ui_panel)
        self.ui_panel_layout.setContentsMargins(24, 18, 24, 18)
        self.ui_panel_layout.setSpacing(14)

        self.ui_eyebrow = QLabel("LOCAL READER AUTOMATION")
        self.ui_eyebrow.setObjectName("Eyebrow")
        self.ui_title = QLabel("微读自动阅读")
        self.ui_title.setObjectName("AppTitle")
        self.ui_subtitle = QLabel("Reader Automation Console")
        self.ui_subtitle.setObjectName("AppSubtitle")

        self.ui_title_box = QVBoxLayout()
        self.ui_title_box.setContentsMargins(0, 0, 0, 0)
        self.ui_title_box.setSpacing(3)
        self.ui_title_box.addWidget(self.ui_eyebrow)
        self.ui_title_box.addWidget(self.ui_title)
        self.ui_title_box.addWidget(self.ui_subtitle)

        self.ui_status_pill = QFrame()
        self.ui_status_pill.setObjectName("StatusPill")
        self.ui_status_pill.setProperty("active", False)
        self.ui_status_layout = QHBoxLayout(self.ui_status_pill)
        self.ui_status_layout.setContentsMargins(13, 6, 13, 6)
        self.ui_status_layout.setSpacing(8)
        self.ui_status_dot = QLabel("●")
        self.ui_status_dot.setObjectName("MetaText")
        self.ui_status_text = QLabel("待机")
        self.ui_status_text.setObjectName("StatusText")
        self.ui_status_layout.addWidget(self.ui_status_dot)
        self.ui_status_layout.addWidget(self.ui_status_text)

        self.ui_act_auto = QPushButton("开始自动阅读")
        self.ui_act_auto.setObjectName("PrimaryButton")
        self.ui_act_auto.setCheckable(True)
        self.ui_act_auto.setToolTip("切换自动阅读    F10")

        self.ui_act_home = QPushButton("首页")
        self.ui_act_home.setObjectName("SecondaryButton")
        self.ui_act_home.setToolTip("回到微信读书首页    F4")
        self.ui_act_refresh = QPushButton("刷新")
        self.ui_act_refresh.setObjectName("SecondaryButton")
        self.ui_act_refresh.setToolTip("刷新当前页面    F5")
        self.ui_act_timing = QPushButton("定时")
        self.ui_act_timing.setObjectName("SecondaryButton")
        self.ui_act_timing.setCheckable(True)
        self.ui_act_timing.setToolTip("设置每日任务和计时器    F12")
        self.ui_act_quit = QPushButton("退出")
        self.ui_act_quit.setObjectName("QuietButton")
        self.ui_act_quit.setToolTip("退出应用    Alt+Q")

        self.ui_speed_caption = QLabel("速度")
        self.ui_speed_caption.setObjectName("Caption")
        self.ui_speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.ui_speed_slider.setMinimum(READER_SPEED_MIN)
        self.ui_speed_slider.setMaximum(READER_SPEED_MAX)
        self.ui_speed_slider.setSingleStep(1)
        self.ui_speed_slider.setPageStep(1)
        self.ui_speed_slider.setMinimumWidth(160)
        self.ui_speed_slider.setMaximumWidth(220)
        self.ui_speed_value = QLabel("")
        self.ui_speed_value.setObjectName("SpeedValue")
        self.ui_speed_value.setMinimumWidth(24)
        self.ui_speed_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.ui_header_row = QHBoxLayout()
        self.ui_header_row.setContentsMargins(0, 0, 0, 0)
        self.ui_header_row.setSpacing(12)
        self.ui_header_row.addLayout(self.ui_title_box, 1)
        self.ui_header_row.addWidget(self.ui_status_pill, 0, Qt.AlignmentFlag.AlignRight)

        self.ui_primary_actions = QHBoxLayout()
        self.ui_primary_actions.setContentsMargins(0, 0, 0, 0)
        self.ui_primary_actions.setSpacing(8)
        self.ui_primary_actions.addWidget(self.ui_act_auto)
        self.ui_primary_actions.addWidget(self.ui_act_home)
        self.ui_primary_actions.addWidget(self.ui_act_refresh)
        self.ui_primary_actions.addWidget(self.ui_act_timing)
        self.ui_primary_actions.addWidget(self.ui_act_quit)
        self.ui_primary_actions.addStretch(1)
        self.ui_primary_actions.addWidget(self.ui_speed_caption)
        self.ui_primary_actions.addWidget(self.ui_speed_slider)
        self.ui_primary_actions.addWidget(self.ui_speed_value)

        self.ui_panel_layout.addLayout(self.ui_header_row)
        self.ui_panel_layout.addLayout(self.ui_primary_actions)

        self.ui_timing_panel = TimingPanel(self.ui_panel)
        self.ui_timing_panel.setVisible(False)
        self.ui_panel_layout.addWidget(self.ui_timing_panel)

        self.ui_cef = CefView(self.ui_root)
        self.ui_cef.setObjectName("BrowserSurface")

        self.ui_layout.addWidget(self.ui_panel)
        self.ui_layout.addWidget(self.ui_cef, 1)

        self.ui_tray = QSystemTrayIcon(self.view)
        self.ui_tray.setIcon(GUI.icon(ResMap.icon_app))
        self.ui_tray_menu = QMenu(self.view)
        self.ui_tray_quit = QAction("退出", self.ui_tray_menu)
        self.ui_tray_menu.addAction(self.ui_tray_quit)
        self.ui_tray.setContextMenu(self.ui_tray_menu)
        self.ui_tray.setToolTip("微读自动阅读")
        self.ui_tray.show()


class WindowView(QMainWindow):
    """应用主窗口"""

    def __init__(self):
        super(WindowView, self).__init__()

        self.timer_cef: Optional[QTimer] = None
        self.timer_reading: Optional[QTimer] = None
        self.timer_timing: Optional[QTimer] = None
        self.schedule_owned_reading = False
        self.schedule_suppressed_until_exit = False
        self.countdown_deadline_ms: Optional[int] = None
        self.view = _View(self, Views.Main, UserKey.General.WinRect)

        self.setupUi()
        self.setupSignals()
        self.setupCefTimer()
        self.setupReadingTimer()
        self.setupTimingTimer()

    def setupUi(self):
        """初始化 UI"""
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents, True)
        self.setMinimumSize(900, 600)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setWindowTitle("微读自动阅读")
        self.setWindowIcon(GUI.icon(ResMap.icon_app))
        self.setStyleSheet(DAYLIGHT_STYLE)
        self.setCentralWidget(self.view.ui_root)
        self.view.ui_cef.embedBrowser()
        self.view.ui_act_auto.setChecked(gPreferences.get(UserKey.Reader.Scrollable))
        self.view.ui_speed_slider.setValue(self.normalizedSpeed())
        self.refreshSpeed()
        self.refreshAutoState()
        if self.width() < 900 or self.height() < 600:
            self.resize(max(self.width(), 1040), max(self.height(), 700))
        QTimer.singleShot(0, self.syncCefGeometry)
        QTimer.singleShot(120, self.syncCefGeometry)

    def setupSignals(self):
        """关联信号"""
        self.view.ui_tray.activated.connect(self.onTrayActivated)
        self.view.ui_tray_quit.triggered.connect(self.onToolbarQuit)
        self.view.ui_act_auto.clicked.connect(self.onToolbarSetAuto)
        self.view.ui_act_home.clicked.connect(self.onToolbarBackHome)
        self.view.ui_act_refresh.clicked.connect(self.onToolbarReload)
        self.view.ui_act_timing.clicked.connect(self.onToolbarTiming)
        self.view.ui_act_quit.clicked.connect(self.onToolbarQuit)
        self.view.ui_speed_slider.valueChanged.connect(self.onSpeedChanged)
        self.view.ui_timing_panel.collapse_requested.connect(lambda: self.setTimingPanelVisible(False))
        gSignals.cef_short_cut.connect(self.onShortcutActivated)
        gSignals.reader_refresh_speed.connect(self.refreshSpeed)
        gSignals.reader_status_tip_updated.connect(self.refreshStatusTip)
        gSignals.reader_reading_finished.connect(self.onBookFinished)
        gSignals.timing_tasks_changed.connect(self.onTimingTasksChanged)
        gSignals.timing_countdown_started.connect(self.onCountdownStarted)
        gSignals.timing_countdown_stopped.connect(self.onCountdownStopped)

    def refreshStatusTip(self, tip: str):
        """刷新状态提示"""
        if self.countdown_deadline_ms is not None:
            self.refreshCountdownStatus()
            return

        if tip:
            self.view.ui_status_text.setText(tip)
        elif self.view.ui_act_auto.isChecked():
            self.view.ui_status_text.setText(I18n.text(LanguageKeys.tips_auto_read_on))
        else:
            self.view.ui_status_text.setText("待机")

    def countdownRemainingSeconds(self) -> int:
        """读取计时器剩余秒数。"""
        if self.countdown_deadline_ms is None:
            return 0

        remaining_ms = max(0, self.countdown_deadline_ms - QDateTime.currentMSecsSinceEpoch())
        return int((remaining_ms + 999) // 1000)

    def countdownStatusText(self) -> str:
        """格式化右上角状态框中的计时器读秒。"""
        seconds = self.countdownRemainingSeconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        second = seconds % 60
        if hours:
            return "计时 %02d:%02d:%02d" % (hours, minutes, second)
        return "计时 %02d:%02d" % (minutes, second)

    def refreshCountdownStatus(self):
        """同步计时器状态到顶部状态框和定时面板。"""
        if self.countdown_deadline_ms is None:
            return

        text = self.countdownStatusText()
        self.view.ui_status_text.setText(text)
        self.view.ui_timing_panel.setCountdownStatus(text)

    def refreshAutoState(self):
        """刷新自动阅读状态 UI"""
        checked = self.view.ui_act_auto.isChecked()
        self.view.ui_act_auto.setText("暂停自动阅读" if checked else "开始自动阅读")
        self.view.ui_status_pill.setProperty("active", checked)
        self.view.ui_status_dot.setText("●")
        self.view.ui_status_dot.setStyleSheet("color: #18a886;" if checked else "color: #8d9baa;")
        self.view.ui_status_pill.style().unpolish(self.view.ui_status_pill)
        self.view.ui_status_pill.style().polish(self.view.ui_status_pill)
        self.refreshStatusTip("")

    def onBookFinished(self):
        """全书完"""
        self.schedule_owned_reading = False
        self.countdown_deadline_ms = None
        self.view.ui_timing_panel.setCountdownStatus("未运行")
        self.setAutoReading(False, "已读完")
        self.activateWindow()
        self.showNormal()
        Cmm.playBeep()

    def onShortcutActivated(self, shortcut: int):
        """
        快捷键响应
        - CEF 会吞噬 Qt 事件，所以由 CEF 层监听后转发给 Qt。
        """
        if shortcut == CefModel.ShortCut.Quit:
            self.onToolbarQuit()
        elif shortcut == CefModel.ShortCut.Reload:
            self.onToolbarReload()
        elif shortcut == CefModel.ShortCut.Timing:
            self.onToolbarTiming()
        elif shortcut == CefModel.ShortCut.SpeedUp:
            self.onToolbarSpeedUp()
        elif shortcut == CefModel.ShortCut.SpeedDown:
            self.onToolbarSpeedDown()
        elif shortcut == CefModel.ShortCut.Home:
            self.onToolbarBackHome()
        elif shortcut == CefModel.ShortCut.Auto:
            self.onToolbarAuto()
        else:
            print(f'已移除的快捷键: {shortcut}')

    def refreshSpeed(self):
        """刷新阅读速度"""
        speed = self.normalizedSpeed()
        if self.view.ui_speed_slider.value() != speed:
            self.view.ui_speed_slider.blockSignals(True)
            self.view.ui_speed_slider.setValue(speed)
            self.view.ui_speed_slider.blockSignals(False)
        self.view.ui_speed_value.setText(str(speed))

    @staticmethod
    def normalizedSpeed() -> int:
        """读取并收敛到 1-10 的阅读速度。"""
        speed = normalize_reader_speed(gPreferences.get(UserKey.Reader.Speed))
        if speed != gPreferences.get(UserKey.Reader.Speed):
            gPreferences.set(UserKey.Reader.Speed, speed)
        return speed

    def setupCefTimer(self):
        """启动 CEF 更新定时器"""
        self.timer_cef = QTimer()
        self.timer_cef.timeout.connect(self.onRunCef)
        self.timer_cef.start(CefModel.MS_CEF)

    def setupReadingTimer(self):
        """启动阅读器更新定时器"""
        self.timer_reading = QTimer()
        self.timer_reading.timeout.connect(self.onAutoReading)
        self.timer_reading.start(CefModel.MS_AUTO)

    def setupTimingTimer(self):
        """启动定时阅读功能定时器"""
        self.timer_timing = QTimer()
        self.timer_timing.timeout.connect(self.onTimingReading)
        self.timer_timing.start(1000)

    def onRunCef(self):
        """CEF 更新"""
        self.view.ui_cef.runLoop()

    def syncCefGeometry(self):
        """同步 CEF 子窗口尺寸，避免首次显示时缩在左上角。"""
        self.view.ui_cef.syncBrowserGeometry()

    def stopCef(self):
        """停止 CEF 更新"""
        self.timer_reading.stop()
        self.timer_cef.stop()
        self.view.ui_cef.quit()

    def onToolbarAuto(self):
        """模拟自动阅读点击"""
        checked = self.view.ui_act_auto.isChecked()
        self.view.ui_act_auto.setChecked(not checked)
        self.onToolbarSetAuto()

    def setAutoReading(self, checked: bool, tip: str = "", trigger_cef: bool = True):
        """统一切换自动阅读状态。"""
        self.view.ui_act_auto.setChecked(checked)
        gPreferences.set(UserKey.Reader.Scrollable, checked)
        if trigger_cef:
            self.view.ui_cef.doAuto()
        self.refreshAutoState()
        if tip:
            self.refreshStatusTip(tip)

    def getTimingSegments(self):
        """读取并清洗每日任务时间段。"""
        raw_segments = gPreferences.get(UserKey.Timing.Segments)
        if not isinstance(raw_segments, list):
            return []

        segments = []
        for item in raw_segments:
            if not isinstance(item, dict):
                continue
            try:
                start = int(item.get('start'))
                stop = int(item.get('stop'))
            except (TypeError, ValueError):
                continue
            if start == stop or start < 0 or stop < 0 or start >= DAY_MS or stop >= DAY_MS:
                continue
            segments.append({
                'start': start,
                'stop': stop,
                'enabled': bool(item.get('enabled', True)),
            })
        return segments

    @staticmethod
    def isTimeInSegment(now_ms: int, segment: Dict[str, Any]) -> bool:
        """支持跨午夜时间段。"""
        start = segment['start']
        stop = segment['stop']
        if start < stop:
            return start <= now_ms < stop
        return now_ms >= start or now_ms < stop

    def isInsideTimingSegmentNow(self) -> bool:
        now_ms = QTime.currentTime().msecsSinceStartOfDay()
        return any(
            segment.get('enabled', True) and self.isTimeInSegment(now_ms, segment)
            for segment in self.getTimingSegments()
        )

    def onTimingReading(self):
        """定时阅读状态机。"""
        self.handleCountdown()
        self.handleTimingTasks()
        self.refreshCountdownStatus()

    def handleTimingTasks(self):
        """根据每日时间段启动或停止自动阅读。"""
        inside_segment = self.isInsideTimingSegmentNow()

        if not inside_segment:
            self.schedule_suppressed_until_exit = False
            if self.schedule_owned_reading:
                self.schedule_owned_reading = False
                if self.view.ui_act_auto.isChecked():
                    self.setAutoReading(False, "每日任务结束，已停止")
            return

        if self.schedule_suppressed_until_exit:
            return

        if not self.view.ui_act_auto.isChecked():
            self.schedule_owned_reading = True
            self.setAutoReading(True, "每日任务阅读中")
        elif self.schedule_owned_reading:
            self.refreshStatusTip("每日任务阅读中")

    def handleCountdown(self):
        """计时器到点后停止阅读。"""
        if self.countdown_deadline_ms is None:
            return

        if QDateTime.currentMSecsSinceEpoch() < self.countdown_deadline_ms:
            return

        self.countdown_deadline_ms = None
        self.schedule_owned_reading = False
        self.schedule_suppressed_until_exit = self.isInsideTimingSegmentNow()
        self.view.ui_timing_panel.setCountdownStatus("已结束")
        if self.view.ui_act_auto.isChecked():
            self.setAutoReading(False, "计时结束，已停止")
        else:
            self.refreshStatusTip("计时结束")
        Cmm.playBeep()

    def onTimingTasksChanged(self):
        """定时任务变更后立即重新评估。"""
        self.handleTimingTasks()

    def onCountdownStarted(self, minutes: int):
        """启动一次性计时阅读。"""
        self.countdown_deadline_ms = QDateTime.currentMSecsSinceEpoch() + max(1, int(minutes)) * 60 * 1000
        self.schedule_owned_reading = False
        self.schedule_suppressed_until_exit = False
        self.setAutoReading(True, "计时阅读中")
        self.refreshCountdownStatus()

    def onCountdownStopped(self):
        """取消计时器，不改变当前阅读状态。"""
        self.countdown_deadline_ms = None
        self.view.ui_timing_panel.setCountdownStatus("未运行")
        self.refreshStatusTip("")

    def onAutoReading(self):
        """阅读器更新"""
        self.view.ui_cef.doScroll()

    def closeEvent(self, event):
        """关闭事件：停止定时器、关闭 CEF、保存数据"""
        self.stopCef()
        self.view.closeEvent(event)
        super(WindowView, self).closeEvent(event)

    def resizeEvent(self, event):
        """视图尺寸变化事件"""
        self.view.resizeEvent(event)
        QTimer.singleShot(0, self.syncCefGeometry)
        super(WindowView, self).resizeEvent(event)

    def showEvent(self, event):
        """窗口显示后再同步一次 CEF 尺寸。"""
        super(WindowView, self).showEvent(event)
        QTimer.singleShot(0, self.syncCefGeometry)
        QTimer.singleShot(120, self.syncCefGeometry)

    def onTrayActivated(self, reason: QSystemTrayIcon.ActivationReason):
        """系统托盘图标触发事件"""
        if reason in (QSystemTrayIcon.ActivationReason.DoubleClick,
                      QSystemTrayIcon.ActivationReason.MiddleClick,
                      QSystemTrayIcon.ActivationReason.Trigger):
            self.activateWindow()
            self.showMaximized() if self.isMaximized() else self.showNormal()

    def onToolbarQuit(self):
        """退出阅读"""
        self.close()
        QApplication.exit()

    def onToolbarBackHome(self):
        """回到首页"""
        self.view.ui_cef.doBackHome()

    def onToolbarReload(self):
        """重新加载"""
        self.view.ui_cef.doReload()

    def onToolbarSetAuto(self):
        """切换自动阅读"""
        checked = self.view.ui_act_auto.isChecked()
        if not checked and self.countdown_deadline_ms is not None:
            self.countdown_deadline_ms = None
            self.view.ui_timing_panel.setCountdownStatus("未运行")
        self.schedule_owned_reading = False
        self.schedule_suppressed_until_exit = (not checked) and self.isInsideTimingSegmentNow()
        self.setAutoReading(checked)

    def onToolbarSpeedUp(self):
        """提高速度"""
        self.view.ui_speed_slider.setValue(min(READER_SPEED_MAX, self.view.ui_speed_slider.value() + 1))

    def onToolbarSpeedDown(self):
        """降低速度"""
        self.view.ui_speed_slider.setValue(max(READER_SPEED_MIN, self.view.ui_speed_slider.value() - 1))

    def onSpeedChanged(self, value: int):
        """速度变化事件"""
        gPreferences.set(UserKey.Reader.Speed, normalize_reader_speed(value))
        self.view.ui_cef.doSpeed()
        self.refreshSpeed()

    def setTimingPanelVisible(self, visible: bool):
        """展开或收起顶部定时面板。"""
        self.view.ui_timing_panel.setVisible(visible)
        self.view.ui_act_timing.blockSignals(True)
        self.view.ui_act_timing.setChecked(visible)
        self.view.ui_act_timing.blockSignals(False)
        self.view.ui_act_timing.setText("收起定时" if visible else "定时")
        QTimer.singleShot(0, self.syncCefGeometry)
        QTimer.singleShot(120, self.syncCefGeometry)

    def onToolbarTiming(self):
        """展开或收起定时面板。"""
        self.setTimingPanelVisible(not self.view.ui_timing_panel.isVisible())
