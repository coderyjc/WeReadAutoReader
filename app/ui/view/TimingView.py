# -*- coding: utf-8 -*-

"""
@File    : TimingView.py
@Desc    : 嵌入式定时自动阅读面板
"""
from typing import Any, Dict, List

from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
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

from helper.Preferences import UserKey, gPreferences
from helper.Signals import gSignals


DAY_MS = 24 * 60 * 60 * 1000


TIMING_STYLE = """
QFrame#InlineTimingPanel {
    background: rgba(255, 255, 255, 118);
    border: 1px solid rgba(125, 187, 231, 125);
    border-radius: 12px;
}
QLabel#PanelTitle {
    color: #16202a;
    font-family: "Microsoft YaHei UI";
    font-size: 16px;
    font-weight: 700;
}
QLabel#PanelEyebrow {
    color: #1f75b8;
    font-family: "Consolas", "Microsoft YaHei UI";
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0px;
}
QLabel#SectionTitle {
    color: #16202a;
    font-size: 13px;
    font-weight: 700;
}
QLabel#FieldLabel,
QLabel#MetaText {
    color: #637384;
    font-size: 12px;
}
QFrame#TaskPanel,
QFrame#TimerPanel {
    background: rgba(255, 255, 255, 172);
    border: 1px solid #d7d0c2;
    border-radius: 10px;
}
QListWidget,
QTimeEdit,
QSpinBox {
    min-height: 30px;
    padding: 4px 9px;
    padding-right: 28px;
    border-radius: 8px;
    border: 1px solid #cfd8de;
    background: rgba(255, 255, 255, 220);
    color: #16202a;
    selection-background-color: #1f75d6;
    selection-color: #ffffff;
}
QListWidget {
    padding: 6px;
    outline: none;
}
QListWidget::item {
    min-height: 28px;
    padding: 4px 8px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f75d6, stop:1 #13a887);
    color: #ffffff;
}
QTimeEdit::up-button,
QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid #cfd8de;
    border-top-right-radius: 8px;
    background: rgba(231, 244, 255, 210);
}
QTimeEdit::down-button,
QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 22px;
    border-left: 1px solid #cfd8de;
    border-bottom-right-radius: 8px;
    background: rgba(255, 240, 216, 210);
}
QTimeEdit::up-button:hover,
QSpinBox::up-button:hover,
QTimeEdit::down-button:hover,
QSpinBox::down-button:hover {
    background: #ffffff;
}
QTimeEdit::up-arrow,
QSpinBox::up-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 5px solid #1f75d6;
}
QTimeEdit::down-arrow,
QSpinBox::down-arrow {
    image: none;
    width: 0;
    height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #13a887;
}
QPushButton {
    min-height: 30px;
    padding: 5px 13px;
    border-radius: 8px;
    border: 1px solid #cfd8de;
    background: rgba(255, 255, 255, 196);
    color: #16202a;
    font-weight: 600;
}
QPushButton:hover {
    background: #ffffff;
    border-color: #7dbbe7;
}
QPushButton:disabled {
    color: #a6b0ba;
    background: rgba(238, 244, 249, 185);
}
QPushButton#PrimaryButton {
    border-color: #1f75d6;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #1f75d6, stop:1 #13a887);
    color: #ffffff;
    font-weight: 700;
}
QPushButton#PrimaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2f83e2, stop:1 #21b896);
}
QPushButton#DangerButton {
    color: #b64a2f;
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
QPushButton#EnableSegmentButton,
QPushButton#DisableSegmentButton {
    min-width: 50px;
    padding-left: 12px;
    padding-right: 12px;
}
QPushButton#EnableSegmentButton:checked {
    background: #e4f7ef;
    border-color: #13a887;
    color: #0f6f60;
}
QPushButton#DisableSegmentButton:checked {
    background: #fff0d8;
    border-color: #d98d2f;
    color: #9a4d17;
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


class TimingPanel(QFrame):
    """主窗口内嵌的定时设置面板。"""

    collapse_requested = Signal()

    def __init__(self, parent=None):
        super(TimingPanel, self).__init__(parent)

        self.segments = _normalize_segments(gPreferences.get(UserKey.Timing.Segments))
        self.setObjectName("InlineTimingPanel")
        self.setStyleSheet(TIMING_STYLE)
        self.setupUi()
        self.setupPreferences()
        self.setupSignals()
        self.refreshTaskList()

    def setupUi(self):
        self.ui_eyebrow = QLabel("SCHEDULE BOARD")
        self.ui_eyebrow.setObjectName("PanelEyebrow")
        self.ui_title = QLabel("定时自动阅读")
        self.ui_title.setObjectName("PanelTitle")
        self.ui_title_stack = QVBoxLayout()
        self.ui_title_stack.setContentsMargins(0, 0, 0, 0)
        self.ui_title_stack.setSpacing(2)
        self.ui_title_stack.addWidget(self.ui_eyebrow)
        self.ui_title_stack.addWidget(self.ui_title)

        self.ui_btn_collapse = QPushButton("收起")
        self.ui_btn_collapse.setObjectName("QuietButton")

        self.ui_task_title = QLabel("每日时间段")
        self.ui_task_title.setObjectName("SectionTitle")
        self.ui_task_list = QListWidget()
        self.ui_task_list.setMaximumHeight(118)

        self.ui_lab_start = QLabel("开始")
        self.ui_lab_start.setObjectName("FieldLabel")
        self.ui_time_start = QTimeEdit()
        self.ui_time_start.setDisplayFormat("HH:mm")

        self.ui_lab_stop = QLabel("结束")
        self.ui_lab_stop.setObjectName("FieldLabel")
        self.ui_time_stop = QTimeEdit()
        self.ui_time_stop.setDisplayFormat("HH:mm")

        self.ui_lab_state = QLabel("状态")
        self.ui_lab_state.setObjectName("FieldLabel")
        self.ui_btn_task_enable = QPushButton("启用")
        self.ui_btn_task_enable.setObjectName("EnableSegmentButton")
        self.ui_btn_task_enable.setCheckable(True)
        self.ui_btn_task_disable = QPushButton("停用")
        self.ui_btn_task_disable.setObjectName("DisableSegmentButton")
        self.ui_btn_task_disable.setCheckable(True)
        self.ui_task_state_group = QButtonGroup(self)
        self.ui_task_state_group.setExclusive(True)
        self.ui_task_state_group.addButton(self.ui_btn_task_enable)
        self.ui_task_state_group.addButton(self.ui_btn_task_disable)
        self.ui_btn_task_enable.setChecked(True)

        self.ui_btn_add = QPushButton("新增")
        self.ui_btn_add.setObjectName("PrimaryButton")
        self.ui_btn_update = QPushButton("更新")
        self.ui_btn_remove = QPushButton("删除")
        self.ui_btn_remove.setObjectName("DangerButton")

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
        self.ui_btn_timer_stop.setObjectName("QuietButton")

        self.ui_header = QHBoxLayout()
        self.ui_header.setContentsMargins(0, 0, 0, 0)
        self.ui_header.setSpacing(12)
        self.ui_header.addLayout(self.ui_title_stack, 1)
        self.ui_header.addWidget(self.ui_btn_collapse)

        self.ui_task_panel = QFrame()
        self.ui_task_panel.setObjectName("TaskPanel")
        self.ui_task_panel_layout = QVBoxLayout(self.ui_task_panel)
        self.ui_task_panel_layout.setContentsMargins(12, 10, 12, 12)
        self.ui_task_panel_layout.setSpacing(8)

        self.ui_editor = QHBoxLayout()
        self.ui_editor.setContentsMargins(0, 0, 0, 0)
        self.ui_editor.setSpacing(8)
        self.ui_editor.addWidget(self.ui_lab_start)
        self.ui_editor.addWidget(self.ui_time_start)
        self.ui_editor.addWidget(self.ui_lab_stop)
        self.ui_editor.addWidget(self.ui_time_stop)
        self.ui_editor.addWidget(self.ui_lab_state)
        self.ui_editor.addWidget(self.ui_btn_task_enable)
        self.ui_editor.addWidget(self.ui_btn_task_disable)
        self.ui_editor.addStretch(1)

        self.ui_task_buttons = QHBoxLayout()
        self.ui_task_buttons.setContentsMargins(0, 0, 0, 0)
        self.ui_task_buttons.setSpacing(8)
        self.ui_task_buttons.addWidget(self.ui_btn_add)
        self.ui_task_buttons.addWidget(self.ui_btn_update)
        self.ui_task_buttons.addWidget(self.ui_btn_remove)
        self.ui_task_buttons.addStretch(1)

        self.ui_task_panel_layout.addWidget(self.ui_task_title)
        self.ui_task_panel_layout.addWidget(self.ui_task_list)
        self.ui_task_panel_layout.addLayout(self.ui_editor)
        self.ui_task_panel_layout.addLayout(self.ui_task_buttons)

        self.ui_timer_panel = QFrame()
        self.ui_timer_panel.setObjectName("TimerPanel")
        self.ui_timer_panel_layout = QVBoxLayout(self.ui_timer_panel)
        self.ui_timer_panel_layout.setContentsMargins(12, 10, 12, 12)
        self.ui_timer_panel_layout.setSpacing(8)

        self.ui_timer_row = QHBoxLayout()
        self.ui_timer_row.setContentsMargins(0, 0, 0, 0)
        self.ui_timer_row.setSpacing(8)
        self.ui_timer_row.addWidget(self.ui_timer_minutes)
        self.ui_timer_row.addWidget(self.ui_btn_timer_start)
        self.ui_timer_row.addWidget(self.ui_btn_timer_stop)

        self.ui_timer_panel_layout.addWidget(self.ui_timer_title)
        self.ui_timer_panel_layout.addLayout(self.ui_timer_row)
        self.ui_timer_panel_layout.addWidget(self.ui_timer_status)
        self.ui_timer_panel_layout.addStretch(1)

        self.ui_body = QHBoxLayout()
        self.ui_body.setContentsMargins(0, 0, 0, 0)
        self.ui_body.setSpacing(12)
        self.ui_body.addWidget(self.ui_task_panel, 3)
        self.ui_body.addWidget(self.ui_timer_panel, 2)

        self.ui_layout = QVBoxLayout(self)
        self.ui_layout.setContentsMargins(14, 12, 14, 14)
        self.ui_layout.setSpacing(10)
        self.ui_layout.addLayout(self.ui_header)
        self.ui_layout.addLayout(self.ui_body)

    def setupSignals(self):
        self.ui_task_list.currentRowChanged.connect(self.onTaskSelected)
        self.ui_btn_task_enable.clicked.connect(self.onTaskStateChanged)
        self.ui_btn_task_disable.clicked.connect(self.onTaskStateChanged)
        self.ui_btn_add.clicked.connect(self.onAddClicked)
        self.ui_btn_update.clicked.connect(self.onUpdateClicked)
        self.ui_btn_remove.clicked.connect(self.onRemoveClicked)
        self.ui_btn_timer_start.clicked.connect(self.onTimerStartClicked)
        self.ui_btn_timer_stop.clicked.connect(self.onTimerStopClicked)
        self.ui_btn_collapse.clicked.connect(self.collapse_requested.emit)

    def setupPreferences(self):
        self.ui_timer_minutes.setValue(gPreferences.get(UserKey.Timing.CountdownMinutes))
        now = QTime.currentTime().addSecs(60)
        start = QTime(now.hour(), now.minute(), 0)
        self.ui_time_start.setTime(start)
        self.ui_time_stop.setTime(start.addSecs(60 * 30))
        self.setTaskStateButtons(True)

    def refreshTaskList(self, selected_row: int = -1):
        self.ui_task_list.blockSignals(True)
        self.ui_task_list.clear()
        for segment in self.segments:
            self.ui_task_list.addItem(self.makeTaskItem(segment))
        self.ui_task_list.blockSignals(False)

        if self.segments:
            row = selected_row if 0 <= selected_row < len(self.segments) else 0
            self.ui_task_list.setCurrentRow(row)
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
        self.ui_btn_update.setEnabled(has_selection)
        self.ui_btn_remove.setEnabled(has_selection)
        if not has_selection:
            self.setTaskStateButtons(True)
            return

        segment = self.segments[row]
        self.ui_time_start.setTime(_ms_to_time(segment['start']))
        self.ui_time_stop.setTime(_ms_to_time(segment['stop']))
        self.setTaskStateButtons(segment.get('enabled', True))

    def setTaskStateButtons(self, enabled: bool):
        self.ui_btn_task_enable.blockSignals(True)
        self.ui_btn_task_disable.blockSignals(True)
        self.ui_btn_task_enable.setChecked(enabled)
        self.ui_btn_task_disable.setChecked(not enabled)
        self.ui_btn_task_enable.blockSignals(False)
        self.ui_btn_task_disable.blockSignals(False)

    def onTaskStateChanged(self):
        row = self.ui_task_list.currentRow()
        if not 0 <= row < len(self.segments):
            return

        self.segments[row]['enabled'] = self.ui_btn_task_enable.isChecked()
        self.persistSegments()
        self.refreshTaskList(row)

    def buildSegmentFromEditor(self) -> Dict[str, Any]:
        start = _time_to_ms(self.ui_time_start.time())
        stop = _time_to_ms(self.ui_time_stop.time())
        if start == stop:
            raise ValueError("开始和结束不能相同")
        return {
            'start': start,
            'stop': stop,
            'enabled': self.ui_btn_task_enable.isChecked(),
        }

    def persistSegments(self, *_):
        self.segments = _normalize_segments(self.segments)
        gPreferences.set(UserKey.Timing.Segments, self.segments)
        gSignals.timing_tasks_changed.emit()

    def onAddClicked(self):
        try:
            self.segments.append(self.buildSegmentFromEditor())
        except ValueError as error:
            QMessageBox.warning(self, "时间段无效", str(error))
            return

        self.persistSegments()
        selected = len(_normalize_segments(self.segments)) - 1
        self.refreshTaskList(selected)

    def onUpdateClicked(self):
        row = self.ui_task_list.currentRow()
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
        row = self.ui_task_list.currentRow()
        if not 0 <= row < len(self.segments):
            return

        self.segments.pop(row)
        self.persistSegments()
        self.refreshTaskList(min(row, len(self.segments) - 1))

    def onTimerStartClicked(self):
        minutes = self.ui_timer_minutes.value()
        gPreferences.set(UserKey.Timing.CountdownMinutes, minutes)
        self.setCountdownStatus("已启动")
        gSignals.timing_countdown_started.emit(minutes)

    def onTimerStopClicked(self):
        self.setCountdownStatus("未运行")
        gSignals.timing_countdown_stopped.emit()

    def setCountdownStatus(self, text: str):
        self.ui_timer_status.setText(text)
