# Codex Notes

这个文件写给后续接手本仓库的 AI。新对话开始时请优先读取它，再看 README 和源码。

## 用户偏好

- 这个项目是用户自用并二次开发，不需要保留原项目的旧宣传、旧更新日志、旧 TODO、旧问题记录。
- 后续执行任务时，如果遇到反复出现的坑、环境限制、运行方式、隐含约定，请自动补充到本文件，并显式告知用户。
- 本项目以后优先使用 Conda 环境运行，不再优先使用 venv 或系统 Python。

## 当前项目状态

- README 已重写为面向二次开发的说明文档。
- 已删除旧资料文件：`CHANGELOG.md`、`TODO.md`、`Questions.md`。
- `licenses/` 目录也已删除，README 中已移除相关引用。
- 已新增 `environment.yml` 和 `scripts/run-conda.ps1`。
- 当前推荐 Conda 环境名：`wxreader-py37`。
- 主窗口已按 Apple/HIG 风格重做为“自动阅读控制台”，不是完整阅读器 UI。
- 已删除功能：帮助、关于、赞助、笔记导出、全屏、通知按钮、读完 GET 通知、旧工具栏/旧菜单动作。
- 已删除旧 UI/资源文件：`app/conf/Menus.py`、`app/ui/view/ToolbarAction.py`、`app/ui/view/SponsorView.py`、`app/ui/view/NoticeView.py`、`app/ui/view/BadNotice.py`、`app/ui/view/OptionsView.py`、`resources/html/`、`resources/img/`、未使用的 SVG 图标。
- 已删除通知相关 helper：`app/helper/NetHelper.py`、`app/helper/ThreadRunner.py`。

## Conda 环境

- 环境路径：`D:\dev\miniconda\envs\wxreader-py37`
- Python 版本：`3.7.16`
- 已验证依赖：
  - `PySide6 6.4.3`
  - `cefpython3 66.0`
  - `PyInstaller 5.13.2`
- 运行应用：

```powershell
.\scripts\run-conda.ps1
```

- 调试模式：

```powershell
.\scripts\run-conda.ps1 -Debug
```

- 手动运行：

```powershell
conda run -n wxreader-py37 python .\app\Application.py
```

## 已知坑

- `cefpython3==66.0` 是关键约束，只支持 Python 3.7 这一类旧环境；不要随手升级到 Python 3.8+。
- `pip` 安装依赖时可能被 Windows 系统代理影响，表现为 `ProxyError` 或找不到 `PySide6`。本机环境已设置 `NO_PROXY=*` 和 `no_proxy=*` 到 `wxreader-py37`。
- 如果需要重新补装 pip 依赖，优先使用清华 PyPI 镜像：

```powershell
$env:NO_PROXY='*'
$env:no_proxy='*'
conda run -n wxreader-py37 python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --default-timeout 100
```

- 不要直接用系统 Python 运行本项目，很容易因为 Python 版本或 CEF/PySide6 不匹配出问题。
- 在 IDE 中需要把 `app/` 标记为 Sources Root，否则 `from conf...`、`from helper...` 这类导入会被标红。
- 当前终端对中文输出不友好；用 Conda 跑脚本并打印中文时，必要时先设置 `$env:PYTHONIOENCODING='utf-8'`，或输出 ASCII 转义结果。
- 该项目没有自动化测试；改动 CEF、Qt 主窗口、定时状态机或 `resources/js/inject.js` 后，需要人工验证登录、打开书籍、自动滚动、翻页、暂停、每日任务、计时器、退出保存。

## 代码注意事项

- 程序入口是 `app/Application.py`。
- 主窗口逻辑在 `app/ui/view/WindowView.py`。
- 定时任务和计时器 UI 在 `app/ui/view/TimingView.py`。
- CEF 嵌入和 Python/JS 绑定在 `app/ui/view/CefView.py`。
- 微信读书页面自动化逻辑主要在 `resources/js/inject.js`，高度依赖微信读书 DOM class；如果微信读书改版，优先检查这里。
- 当前 Python/JS 绑定只保留自动阅读相关能力：`doScroll`、`nextChapter`、`alert`、`updateState`、`sendAction`。
- 不要把帮助、关于、赞助、笔记导出、全屏、通知等旧功能加回来；用户明确要求删除，并且此项目自用，不当完整阅读器。
- 主界面不展示 URL，不提供步幅调节；`+/-` 每次固定调整速度 1。
- 顶部控制栏不要再把标题、状态、操作按钮、速度条和 URL 塞进同一个 `QGridLayout`。旧布局在窗口较窄或旧配置尺寸下会导致按钮重叠、速度条显示不全；当前结构是标题/状态一行、按钮一行、速度条一行。
- CEF 子窗口首次创建时可能拿到布局前的小尺寸，表现为微信读书网页缩在左上角。当前通过 `CefView.syncBrowserGeometry()` 和 `WindowView.showEvent/resizeEvent` 延迟同步尺寸，不要删掉这些同步调用。
- 每日任务不要再用“当前秒 == 开始秒/结束秒”的精确字符串比较。当前逻辑判断“当前时间是否处于任一启用时间段内”，可避免轮询错过触发秒。
- 每日任务只停止自己开启的自动阅读；用户手动开启的自动阅读不会被每日任务结束时间误停。
- 计时器是一次性命令：启动后立即开启自动阅读，到点停止。若计时器在每日任务时间段内停止阅读，会抑制同一时间段内的自动重启，直到离开该时间段。
- `CefModel.ShortCut.values` 只能放无修饰键快捷键；不要把 `Quit` 放进去，否则用户在网页里按普通 `Q` 也可能触发退出。退出只走 `Alt+Q` 分支。
- `F12` 当前打开定时自动阅读窗口，不再打开通知设置。
- 用户配置由 `app/helper/Preferences.py` 管理，写入 JSON；历史上放弃过 `QSettings`，不要无准备混用两套配置。
- 新增或修改 `resources/` 后需要重新生成 Qt 资源：

```powershell
conda run -n wxreader-py37 python .\scripts\rcc\Rcc.py
```

- `scripts/rcc/Rcc.py` 已修过一个坑：旧版使用相对 `__file__` 且不等待 `pyside6-rcc`，可能生成空的 `app/conf/Resources.py`。如果资源导入报 `qInitResources` 缺失，优先检查资源生成是否成功。

## 后续维护建议

- 优先保证环境可复现：`environment.yml`、`requirements.txt`、README 和实际可运行环境要保持一致。
- 如果准备升级 Python，需要先替换或重做 WebView/CEF 方案。
- 如果继续增强自动阅读功能，应先把 `inject.js` 中 DOM 选择器集中管理，减少微信读书改版带来的维护成本。
