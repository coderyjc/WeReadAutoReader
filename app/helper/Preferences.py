# -*- coding: utf-8 -*-

"""
@File    : Preferences.py
@Time    : 2022/9/27 15:46
@Author  : DoooReyn<jl88744653@gmail.com>
@Desc    : 软件配置
"""
from json import dumps, JSONDecodeError, loads
from os.path import exists

# QSettings 存在读取和保存无效的问题，自己写一个来代替
from helper.Cmm import Cmm


READER_SPEED_MIN = 1
READER_SPEED_MAX = 10


def normalize_reader_speed(value):
    try:
        speed = int(value)
    except (TypeError, ValueError):
        speed = READER_SPEED_MIN
    return max(READER_SPEED_MIN, min(READER_SPEED_MAX, speed))


class UserKey:
    """用户配置存储项"""

    class General:
        Lang = 'general.i18n_lang'
        WinRect = 'general.win_rect'

    class Reader:
        Scrollable = 'reader.scrollable'
        Speed = 'reader.speed'
        LatestUrl = 'reader.latest_url'

    class Timing:
        WinRect = 'timing.win_rect'
        Enabled = 'timing.enabled'
        Segments = 'timing.segments'
        CountdownMinutes = 'timing.countdown_minutes'
        LegacyEveryDay = 'timing.every_day'
        LegacyStartTime = 'timing.start_time'
        LegacyStopTime = 'timing.stop_time'



# 默认用户存储数据
default_user_data = {
    UserKey.Reader.Speed: 1,
    UserKey.Reader.Scrollable: False,
    UserKey.Reader.LatestUrl: 'https://weread.qq.com/',
    UserKey.General.Lang: 'CN',
    UserKey.General.WinRect: [120, 80, 1120, 720],
    UserKey.Timing.WinRect: [300, 180, 640, 520],
    UserKey.Timing.Enabled: False,
    UserKey.Timing.Segments: [],
    UserKey.Timing.CountdownMinutes: 30
}


@Cmm.Decorator.Singleton
class Preferences:
    """用户存储管理器"""

    def __init__(self):
        self._data = {}
        self.config_at = Cmm.appConfigAt()

    def init(self):
        """初始化：创建配置、读取数据到内存"""
        Cmm.mkdir(Cmm.appStorageAt())
        self._read()

    def _read(self):
        """读取数据到内存"""
        if exists(self.config_at):
            try:
                with open(self.config_at, 'r', encoding='utf-8') as f:
                    self._data = loads(f.read())
                    self._sync()
            except JSONDecodeError:
                self._saveDefault()
        else:
            self._saveDefault()

    def _saveDefault(self):
        """保存默认数据"""
        self._data = default_user_data
        self.save()

    def _sync(self):
        """数据同步"""
        for k, v in default_user_data.items():
            if self._data.get(k) is None:
                self._data.setdefault(k, v)

        if not self._data.get(UserKey.Timing.Segments):
            legacy_enabled = self._data.get(UserKey.Timing.LegacyEveryDay)
            legacy_start = self._data.get(UserKey.Timing.LegacyStartTime)
            legacy_stop = self._data.get(UserKey.Timing.LegacyStopTime)
            if legacy_enabled and legacy_start is not None and legacy_stop is not None and legacy_start != legacy_stop:
                self._data[UserKey.Timing.Enabled] = True
                self._data[UserKey.Timing.Segments] = [{
                    'start': int(legacy_start),
                    'stop': int(legacy_stop),
                    'enabled': True,
                }]

        self._data[UserKey.Reader.Speed] = normalize_reader_speed(self._data.get(UserKey.Reader.Speed))

    def save(self):
        """保存数据"""
        with open(self.config_at, 'w', encoding='utf-8') as f:
            f.write(dumps(self._data, indent=2))

    def get(self, key: str):
        """获取数据"""
        return self._data[key]

    def set(self, key: str, value):
        """修改数据"""
        self._data[key] = value
        self.save()


gPreferences = Preferences()
