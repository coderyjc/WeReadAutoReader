# WxReader / 微读自动阅读

![](./assets/banner.png)



WxReader 是一个基于 **PySide6 + cefpython3** 的微信读书自动阅读控制台。它**不是完整阅读器**，网页区域主要用于登录微信读书、打开目标书籍，并承载自动滚动脚本。

当前版本按个人自用和二次开发场景重新整理，只保留自动阅读相关功能。

## 当前状态

- 技术栈：Python 3.7、PySide6、cefpython3、PyInstaller、NSIS
- 入口文件：`app/Application.py`
- 推荐 Conda 环境：`wxreader-py37`
- 主要平台：Windows
- Python 版本限制：建议固定 **Python 3.7**，`cefpython3==66.0` 不支持 Python 3.8+
- 当前没有自动化测试，改动后需要人工验证核心阅读流程

## 保留功能

- 嵌入微信读书网页：默认打开 `https://weread.qq.com/`
- 自动阅读：按设定速度周期性滚动阅读页
- 自动翻页：滚动到底部后触发下一章/下一页
- 暂停条件：页面加载中、选中文本、打开目录或笔记面板等状态会暂停滚动
- 速度控制：主界面直接调节 1-10 档滚动速度，`+` / `-` 每次固定调整 1
- 每日任务：可维护多个每天自动阅读时间段
- 计时器：启动后立即开始自动阅读，到点自动停止
- 状态保存：窗口位置、阅读速度、最新 URL、每日任务等写入本地 JSON 配置

## 已删除功能

- 帮助
- 关于
- 赞助
- 笔记导出
- 全屏
- 通知按钮和读完后的 GET 通知
- 旧工具栏、旧菜单动作、旧帮助/赞助资源
- 步幅调节和“步幅 x 页面”功能

## 快速开始

### 1. 准备环境

本项目优先使用 Conda。首次拉取仓库后，在项目根目录运行：

```powershell
conda env create -f environment.yml
```

如果环境已经存在，后续同步依赖用：

```powershell
conda env update -f environment.yml --prune
```

### 2. 启动应用

推荐直接用脚本启动：

```powershell
.\scripts\run-conda.ps1
```

调试模式：

```powershell
.\scripts\run-conda.ps1 -Debug
```

也可以手动使用 Conda：

```powershell
conda run -n wxreader-py37 python .\app\Application.py
```

在 PyCharm 等 IDE 中开发时，建议把 `app/` 标记为 `Sources Root`。

### 3. 依赖安装补救

如果 `pip` 安装阶段因为 Windows 系统代理失败，可临时绕过代理并使用清华 PyPI 镜像补装：

```powershell
$env:NO_PROXY='*'
$env:no_proxy='*'
conda run -n wxreader-py37 python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --default-timeout 100
```

## 常用快捷键

| 快捷键 | 功能 |
| --- | --- |
| `F4` | 回到首页 |
| `F5` | 刷新页面 |
| `F10` | 切换自动阅读 |
| `F12` | 打开定时自动阅读 |
| `+` / `-` | 加快/降低滚动速度 |
| `Alt+Q` | 退出应用 |

## 目录结构

```text
.
├── app/                    # 应用源码
│   ├── Application.py       # 程序入口，初始化 Qt、CEF、配置和主窗口
│   ├── conf/                # 配置、语言包、资源映射
│   ├── helper/              # 通用工具、偏好设置、信号
│   └── ui/                  # Qt 视图与 CEF 模型
├── resources/               # 运行资源
│   ├── icon/app.ico         # 应用图标
│   ├── js/inject.js         # 注入微信读书页面的自动阅读脚本
│   └── theme/default.qss    # 应用基础样式
├── scripts/
│   ├── rcc/Rcc.py           # 生成 Qt 资源文件和 ResMap
│   ├── package/             # PyInstaller + NSIS 打包脚本
│   └── run-conda.ps1        # 使用 wxreader-py37 启动应用
├── codex.md                 # 给后续 AI 的开发注意事项
├── environment.yml          # Conda 环境定义
└── requirements.txt         # 运行和打包依赖
```

## 核心实现

### 应用启动

`app/Application.py` 负责初始化 Qt、CEF、用户配置和主窗口。

### 主窗口

`app/ui/view/WindowView.py` 是当前主界面，采用顶部控制台 + 网页区域的布局。顶部只放自动阅读相关控制：开始/暂停、首页、刷新、定时、退出、速度。

主界面不展示 URL 输入框，也不再提供步幅调节。

### 定时阅读

`app/ui/view/TimingView.py` 提供两个入口：

- 每日任务：维护多个每天生效的阅读时间段。
- 计时器：立即开始自动阅读，并在指定分钟数后停止。

调度逻辑在 `WindowView.onTimingReading()` 中，不再依赖“当前秒刚好等于开始/结束秒”。它会判断当前时间是否位于启用时间段内，因此不会因为轮询错过某一秒而失效。

### CEF 与页面脚本

`app/ui/view/CefView.py` 负责把 CEF browser 嵌入 Qt 窗口，并建立 Python 与 JS 的双向调用：

- Python 调 JS：`doScroll`、`nextChapter`、`alert`
- JS 调 Python：`updateState`、`sendAction`

`resources/js/inject.js` 是网页自动化的关键文件，负责自动滚动、到底检测、下一章/下一页、全书读完判断、选中状态检测。

如果微信读书改版，优先检查这个文件里的 DOM 选择器。

### 用户配置

配置由 `app/helper/Preferences.py` 管理，保存为 JSON。默认路径来自 Qt 的 `QStandardPaths.GenericConfigLocation`，并拼接应用名：

```text
<GenericConfigLocation>/WxReader/WxReader.json
```

CEF 缓存、Cookie 和日志也会放在同一个 `WxReader` 应用存储目录中。

## 资源更新

新增或修改 `resources/` 下的资源后，需要重新生成 Qt 资源文件：

```powershell
conda run -n wxreader-py37 python .\scripts\rcc\Rcc.py
```

该脚本会更新：

- `scripts/rcc/Resources.qrc`
- `app/conf/Resources.py`
- `app/conf/ResMap.py`

其中 `*.qrc` 被 `.gitignore` 忽略，`Resources.py` 和 `ResMap.py` 是运行时需要的代码文件。

## 打包

打包脚本位于 `scripts/package/`：

```powershell
cd .\scripts\package
conda run -n wxreader-py37 python .\bundle.py -V 2.0.2.1
```

常用参数：

| 参数 | 说明 |
| --- | --- |
| `-V a.b.c.d` | 必填，设置生产版本号 |
| `-D` | 调试模式 |
| `-U` | 使用 UPX 压缩 |
| `-C` | 禁用缓存，重新清理 `build/` 和 `dist/` |

## 二次开发注意事项

- **先锁定 Python 3.7。** 当前 CEF 依赖是最大兼容风险。
- **微信读书 DOM 不是稳定 API。** 自动滚动、暂停、翻页都依赖页面 class 名和结构。
- **快捷键由 CEF 捕获再转发给 Qt。** `Alt+Q` 是退出；不要把普通 `Q` 当退出快捷键。
- **没有测试兜底。** 修改 `inject.js`、`CefView.py`、`WindowView.py` 后至少人工验证：登录、打开书籍、自动滚动、翻页、暂停、每日任务、计时器、退出保存。
- **配置读写是自定义 JSON。** 项目曾放弃 `QSettings`，不要无准备混用两套配置方案。
