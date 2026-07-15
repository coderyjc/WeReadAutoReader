# -*- coding: utf-8 -*-

"""
@File    : TimingView.py
@Desc    : 定时自动阅读窗口
"""
from typing import Any, Dict, List

from PySide6.QtCore import Qt, QTime
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
)

from conf.Views import Views
from helper.Preferences import UserKey, gPreferences
from helper.Signals import gSignals
from ui.view.ViewDelegate import ViewDelegate


DAY_MS = 24 * 60 * 60 * 1000


TIMING_STYLE = """
QDialog {
    background: #f5f5f7;
}
QLabel#Title {
    color: #1d1d1f;
    font-size: 18px;
    font-weight: 600;
}
QLabel#SectionTitle {
    color: #1d1d1f;
    font-size: 13px;
    font-weight: 600;
}
QLabel#FieldLabel,
QLabel#MetaText {
    color: #6e6e73;
    font-size: 12px;
}
QListWidget,
QTimeEdit,
QSpinBox {
    min-height: 30px;
    padding: 3px 8px;
    border-radius: 8px;
    border: 1px solid #d2d2d7;
    background: #ffffff;
    color: #1d1d1f;
    selection-background-color: #d9ecff;
    selection-color: #1d1d1f;
}
QListWidget {
    padding: 6px;
}
QListWidget::item {
    min-height: 30px;
    padding: 4px 8px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background: #d9ecff;
}
QCheckBox {
    color: #1d1d1f;
    font-size: 13px;
}
QPushButton {
    min-height: 30px;
    padding: 5px 14px;
    border-radius: 8px;
    border: 1px solid #d2d2d7;
    background: #ffffff;
    color: #1d1d1f;
}
QPushButton:hover {
    background: #f0f0f3;
}
QPushButton:disabled {
    color: #a1a1a6;
    background: #f5f5f7;
}
QPushButton#PrimaryButton {
    border-color: #0071e3;
    background: #0071e3;
    color: #ffffff;
    font-weight: 600;
}
QPushButton#PrimaryButton:hover {
    background: #147ce5;
}
"""


def _time_to_ms(time_value: QTime) -> int:
    return time_value.msecsSinceStartOfDay()


def _ms_to_time(value: int) -> QTime:
    return QTime.fromMSecsSinceStartOfDay(max(0, min(DAY_MS - 1, int(value))))


def _format_ms(value: int) -> str:
    return _ms_to_time(value).toString("HH:mm")


def _normalize_segments(raw_segments: Any) -> List[Dict[str, Any]]:
    normalized = []
    if not isinstance(raw_segments, list):
        return normalized

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
        normalized.append({
            'start': start,
            'stop': stop,
            'enabled': bool(item.get('enabled', True)),
        })
    return sorted(normalized, key=lambda segment: (segment['start'], segment['stop']))


class _View(ViewDelegate):
    """定时窗口 UI"""

    def __init__(self, win, code, key):
        super(_View, self).__init__(win, code, key)

        self.ui_title = QLabel("定时自动阅读")
        self.ui_title.setObjectName("Title")

        self.ui_check_enabled = QCheckBox("启用每日任务")

        self.ui_task_title = QLabel("每日时间段")
        self.ui_task_title.setObjectName("SectionTitle")
        self.ui_task_list = QListWidget()

        self.ui_lab_start = QLabel("开始")
        self.ui_lab_start.setObjectName("FieldLabel")
        self.ui_time_start = QTimeEdit()
        self.ui_time_start.setDisplayFormat("HH:mm")

        self.ui_lab_stop = QLabel("结束")
        self.ui_lab_stop.setObjectName("FieldLabel")
        self.ui_time_stop = QTimeEdit()
        self.ui_time_stop.setDisplayFormat("HH:mm")

        self.ui_check_task_enabled = QCheckBox("启用所选")

        self.ui_btn_add = QPushButton("新增")
        self.ui_btn_add.setObjectName("PrimaryButton")
        self.ui_btn_update = QPushButton("更新")
        self.ui_btn_remove = QPushButton("删除")

        self.ui_timer_title = QLabel("计时器")
        self.ui_timer_title.setObjectName("SectionTitle")
        self.ui_timer_minutes = QSpinBox()
        self.ui_timer_minutes.setRange(1, 1440)
        self.ui_timer_minutes.setSuffix(" 分钟")
        self.ui_timer_status = QLabel("未运行")
        self.ui_timer_status.setObjectName("MetaText")
        self.ui_btn_timer_start = QPushButton("开始计时")
        self.ui_btn_timer_start.setObjectName("PrimaryButton")
        self.ui_btn_timer_stop = QPushButton("取消计时")

        self.ui_btn_close = QPushButton("关闭")

        self.ui_header = QHBoxLayout()
        self.ui_header.setContentsMargins(0, 0, 0, 0)
        self.ui_header.setSpacing(12)
        self.ui_header.addWidget(self.ui_title)
        self.ui_header.addStretch(1)
        self.ui_header.addWidget(self.ui_check_enabled)

        self.ui_editor = QHBoxLayout()
        self.ui_editor.setContentsMargins(0, 0, 0, 0)
        self.ui_editor.setSpacing(8)
        self.ui_editor.addWidget(self.ui_lab_start)
        self.ui_editor.addWidget(self.ui_time_start)
        self.ui_editor.addWidget(self.ui_lab_stop)
        self.ui_editor.addWidget(self.ui_time_stop)
        self.ui_editor.addWidget(self.ui_check_task_enabled)
        self.ui_editor.addStretch(1)

        self.ui_task_buttons = QHBoxLayout()
        self.ui_task_buttons.setContentsMargins(0, 0, 0, 0)
        self.ui_task_buttons.setSpacing(8)
        self.ui_task_buttons.addWidget(self.ui_btn_add)
        self.ui_task_buttons.addWidget(self.ui_btn_update)
        self.ui_task_buttons.addWidget(self.ui_btn_remove)
        self.ui_task_buttons.addStretch(1)

        self.ui_timer_row = QHBoxLayout()
        self.ui_timer_row.setContentsMargins(0, 0, 0, 0)
        self.ui_timer_row.setSpacing(8)
        self.ui_timer_row.addWidget(self.ui_timer_minutes)
        self.ui_timer_row.addWidget(self.ui_btn_timer_start)
        self.ui_timer_row.addWidget(self.ui_btn_timer_stop)
        self.ui_timer_row.addWidget(self.ui_timer_status)
        self.ui_timer_row.addStretch(1)

        self.ui_footer = QHBoxLayout()
        self.ui_footer.setContentsMargins(0, 0, 0, 0)
        self.ui_footer.addStretch(1)
        self.ui_footer.addWidget(self.ui_btn_close)

        self.ui_layout = QVBoxLayout()
        self.ui_layout.setContentsMargins(18, 16, 18, 16)
        self.ui_layout.setSpacing(12)
        self.ui_layout.addLayout(self.ui_header)
        self.ui_layout.addWidget(self.ui_task_title)
        self.ui_layout.addWidget(self.ui_task_list, 1)
        self.ui_layout.addLayout(self.ui_editor)
        self.ui_layout.addLayout(self.ui_task_buttons)
        self.ui_layout.addSpacing(6)
        self.ui_layout.addWidget(self.ui_timer_title)
        self.ui_layout.addLayout(self.ui_timer_row)
        self.ui_layout.addLayout(self.ui_footer)
        self.view.setLayout(self.ui_layout)


class TimingView(QDialog):
    """定时自动阅读设置"""

    def __init__(self):
        super(TimingView, self).__init__()

        self.segments = _normalize_segments(gPreferences.get(UserKey.Timing.Segments))
        self.view = _View(self, Views.Timing, UserKey.Timing.WinRect)
        self.setWindowTitle("定时自动阅读")
        self.setMinimumSize(640, 520)
        self.setModal(True)
        self.setStyleSheet(TIMING_STYLE)
        self.setupPreferences()
        self.setupSignals()
        self.refreshTaskList()

    def setupSignals(self):
        self.view.ui_check_enabled.toggled.connect(self.persistSegments)
        self.view.ui_task_list.currentRowChanged.connect(self.onTaskSelected)
        self.view.ui_btn_add.clicked.connect(self.onAddClicked)
        self.view.ui_btn_update.clicked.connect(self.onUpdateClicked)
        self.view.ui_btn_remove.clicked.connect(self.onRemoveClicked)
        self.view.ui_btn_timer_start.clicked.connect(self.onTimerStartClicked)
        self.view.ui_btn_timer_stop.clicked.connect(self.onTimerStopClicked)
        self.view.ui_btn_close.clicked.connect(self.close)

    def setupPreferences(self):
        self.view.ui_check_enabled.setChecked(gPreferences.get(UserKey.Timing.Enabled))
        self.view.ui_timer_minutes.setValue(gPreferences.get(UserKey.Timing.CountdownMinutes))
        now = QTime.currentTime().addSecs(60)
        start = QTime(now.hour(), now.minute(), 0)
        self.view.ui_time_start.setTime(start)
        self.view.ui_time_stop.setTime(start.addSecs(60 * 30))
        self.view.ui_check_task_enabled.setChecked(True)

    def refreshTaskList(self, selected_row: int = -1):
        self.view.ui_task_list.blockSignals(True)
        self.view.ui_task_list.clear()
        for segment in self.segments:
            self.view.ui_task_list.addItem(self.makeTaskItem(segment))
        self.view.ui_task_list.blockSignals(False)

        if self.segments:
            row = selected_row if 0 <= selected_row < len(self.segments) else 0
            self.view.ui_task_list.setCurrentRow(row)
        else:
            self.onTaskSelected(-1)

    def makeTaskItem(self, segment: Dict[str, Any]) -> QListWidgetItem:
        suffix = "  次日结束" if segment['stop'] < segment['start'] else ""
        state = "启用" if segment.get('enabled', True) else "停用"
        item = QListWidgetItem("%s - %s%s    %s" % (
            _format_ms(segment['start']),
            _format_ms(segment['stop']),
            suffix,
            state,
        ))
        item.setData(Qt.ItemDataRole.UserRole, dict(segment))
        return item

    def onTaskSelected(self, row: int):
        has_selection = 0 <= row < len(self.segments)
        self.view.ui_btn_update.setEnabled(has_selection)
        self.view.ui_btn_remove.setEnabled(has_selection)
        if not has_selection:
            self.view.ui_check_task_enabled.setChecked(True)
            return

        segment = self.segments[row]
        self.view.ui_time_start.setTime(_ms_to_time(segment['start']))
        self.view.ui_time_stop.setTime(_ms_to_time(segment['stop']))
        self.view.ui_check_task_enabled.setChecked(segment.get('enabled', True))

    def buildSegmentFromEditor(self) -> Dict[str, Any]:
        start = _time_to_ms(self.view.ui_time_start.time())
        stop = _time_to_ms(self.view.ui_time_stop.time())
        if start == stop:
            raise ValueError("开始和结束不能相同")
        return {
            'start': start,
            'stop': stop,
            'enabled': self.view.ui_check_task_enabled.isChecked(),
        }

    def persistSegments(self, *_):
        self.segments = _normalize_segments(self.segments)
        gPreferences.set(UserKey.Timing.Enabled, self.view.ui_check_enabled.isChecked())
        gPreferences.set(UserKey.Timing.Segments, self.segments)
        gSignals.timing_tasks_changed.emit()

    def onAddClicked(self):
        try:
            self.segments.append(self.buildSegmentFromEditor())
        except ValueError as error:
            QMessageBox.warning(self, "时间段无效", str(error))
            return

        if len(self.segments) == 1:
            self.view.ui_check_enabled.setChecked(True)
        self.persistSegments()
        selected = len(_normalize_segments(self.segments)) - 1
        self.refreshTaskList(selected)

    def onUpdateClicked(self):
        row = self.view.ui_task_list.currentRow()
        if not 0 <= row < len(self.segments):
            return

        try:
            self.segments[row] = self.buildSegmentFromEditor()
        except ValueError as error:
            QMessageBox.warning(self, "时间段无效", str(error))
            return

        self.persistSegments()
        self.refreshTaskList(row)

    def onRemoveClicked(self):
        row = self.view.ui_task_list.currentRow()
        if not 0 <= row < len(self.segments):
            return

        self.segments.pop(row)
        if not self.segments:
            self.view.ui_check_enabled.setChecked(False)
        self.persistSegments()
        self.refreshTaskList(min(row, len(self.segments) - 1))

    def onTimerStartClicked(self):
        minutes = self.view.ui_timer_minutes.value()
        gPreferences.set(UserKey.Timing.CountdownMinutes, minutes)
        self.view.ui_timer_status.setText("已启动")
        gSignals.timing_countdown_started.emit(minutes)

    def onTimerStopClicked(self):
        self.view.ui_timer_status.setText("未运行")
        gSignals.timing_countdown_stopped.emit()

    def closeEvent(self, event):
        self.view.closeEvent(event)
        super(TimingView, self).closeEvent(event)

    def resizeEvent(self, event):
        self.view.resizeEvent(event)
        super(TimingView, self).resizeEvent(event)
