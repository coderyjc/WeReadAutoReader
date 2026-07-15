# WxReader / 微读自动阅读器

WxReader 是一个基于 **PySide6 + cefpython3** 的微信读书桌面客户端辅助工具。它把微信读书网页嵌入到 Qt 窗口中，通过注入 JavaScript 实现自动滚动、自动翻页、笔记导出、阅读完成通知等能力。

这个仓库是一个老项目的二次开发起点。本文档优先面向接手维护者，说明如何跑起来、代码怎么分布、哪些地方容易踩坑。

## 当前状态

- 最新记录版本：`2.0.2`，打包 manifest 中的生产版本为 `2.0.2.1`。
- 技术栈：Python、PySide6、cefpython3、PyInstaller、NSIS。
- 入口文件：`app/Application.py`。
- 默认 Conda 环境：`wxreader-py37`。
- 主要运行平台：Windows。代码里包含部分跨平台判断，但快捷键捕获、系统音效、安装包脚本都明显偏 Windows。
- Python 版本限制：建议使用 **Python 3.7**。`cefpython3==66.0` 不支持 Python 3.8+，这是继续维护时最重要的环境约束。
- 当前仓库没有自动化测试用例；变更后需要人工运行应用验证核心阅读流程。

## 功能概览

- 嵌入微信读书首页与阅读页：默认打开 `https://weread.qq.com/`。
- 自动阅读：按设定速度周期性滚动阅读页。
- 自动翻页：滚动到底部后触发下一章/下一页。
- 暂停条件：页面加载中、选中文本、打开目录或笔记面板等状态会暂停滚动。
- 笔记导出：在阅读页导出微信读书笔记为 Markdown 文件。
- 阅读完成通知：全书读完后播放提示音，并可向配置的 GET 接口发起请求。
- 定时阅读：可配置每天开始/停止自动阅读的时间。
- 状态保存：窗口位置、阅读速度、最新 URL、定时设置等写入本地 JSON 配置。

## 快速开始

### 1. 准备环境

本项目优先使用 Conda 环境。首次拉取仓库后，在项目根目录运行：

```powershell
conda env create -f environment.yml
```

如果环境已经存在，后续同步依赖用：

```powershell
conda env update -f environment.yml --prune
```

### 2. 启动应用

推荐直接用脚本启动，脚本会自动通过 `wxreader-py37` 环境运行：

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

调试模式：

```powershell
conda run -n wxreader-py37 python .\app\Application.py --DEBUG
```

在 PyCharm 等 IDE 中开发时，建议把 `app/` 标记为 `Sources Root`，否则 `from conf...`、`from helper...` 这类导入可能被 IDE 标成 unresolved。

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
| `F1` | 打开帮助 |
| `F2` | 打开关于 |
| `F3` | 打开赞助 |
| `F4` | 回到首页 |
| `F5` | 刷新页面 |
| `F6` | 显示/隐藏工具栏 |
| `F8` | 导出笔记 |
| `F9` | 切换主题，目前 UI 中禁用 |
| `F10` | 切换自动阅读 |
| `F11` | 切换全屏 |
| `F12` | 打开选项 |
| `+` / `-` | 加快/降低滚动速度 |
| `Alt+Q` | 退出应用 |

阅读页内还会监听方向键、`Home`、`End`、`PgUp`、`PgDn` 等浏览器原生滚动/翻页操作。

## 目录结构

```text
.
├── app/                    # 应用源码
│   ├── Application.py       # 程序入口，初始化 Qt、CEF、配置和主窗口
│   ├── conf/                # 配置、语言包、资源映射、菜单定义
│   ├── helper/              # 通用工具、偏好设置、信号、网络请求、线程辅助
│   └── ui/                  # Qt 视图与 CEF 模型
├── resources/               # HTML、JS、图标、主题、图片等资源
│   └── js/inject.js         # 注入微信读书页面的核心脚本
├── scripts/
│   ├── rcc/Rcc.py           # 生成 Qt 资源文件和 ResMap
│   ├── package/             # PyInstaller + NSIS 打包脚本
│   └── run-conda.ps1        # 使用 wxreader-py37 启动应用
├── environment.yml          # Conda 环境定义
└── requirements.txt         # 运行和打包依赖
```

## 核心实现

### 应用启动

`app/Application.py` 完成以下初始化：

1. 读取 `--DEBUG` 参数。
2. 注册 CEF 异常代理。
3. 初始化 Qt 资源。
4. 初始化用户配置。
5. 创建 `QApplication`。
6. 初始化 CEF，并设置缓存、Cookie、语言包和 GPU 相关参数。
7. 创建并显示 `WindowView`。

### 主窗口与工具栏

`app/ui/view/WindowView.py` 是主窗口。它负责：

- 创建工具栏、状态栏、系统托盘和 CEF 视图。
- 启动 CEF message loop 定时器。
- 启动自动阅读定时器。
- 启动定时阅读检查定时器。
- 响应工具栏动作和 CEF 捕获到的快捷键。

### CEF 与页面脚本

`app/ui/view/CefView.py` 负责把 CEF browser 嵌入 Qt 窗口，并建立 Python 与 JS 的双向调用：

- Python 调 JS：`doScroll`、`nextChapter`、`exportNotes`、`changeTheme`、`alert`。
- JS 调 Python：`updateState`、`sendAction`、`savedNotes`。

`resources/js/inject.js` 是网页自动化的关键文件。它依赖微信读书页面 DOM 选择器实现：

- 自动滚动。
- 检测是否到底。
- 下一章/下一页。
- 全书读完判断。
- 选中状态检测。
- 笔记内容格式化和导出。

如果微信读书改版，优先检查这个文件里的选择器。

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

打包脚本位于 `scripts/package/`。

### 一键打包

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

打包流程会：

1. 读取 `scripts/package/package.json`。
2. 从模板生成 `pyinstaller.spec` 和 `package.nsi`。
3. 运行 PyInstaller。
4. 删除部分冗余 CEF/PySide6 资源。
5. 生成便携版 zip。
6. 在 Windows 下调用 NSIS 生成安装包。
7. 输出 SHA256。

### 依赖工具

- PyInstaller：来自 `requirements.txt`。
- NSIS：生成安装包时需要，并且 `makensis` 需要在环境变量中。
- UPX：可选，仅在使用 `-U` 时需要，脚本默认查找 `scripts/package/upx`。

更多原始说明见 `scripts/package/README.md`。

## 二次开发注意事项

- **先锁定 Python 3.7。** 当前 CEF 依赖是最大兼容风险。若要升级 Python，需要先替换或重做 WebView 方案。
- **微信读书 DOM 不是稳定 API。** 自动滚动、导出笔记、翻页、主题切换都依赖页面 class 名和结构，改版后可能失效。
- **主题切换目前不可用。** `F9` 对应动作在 UI 中被禁用，原因是微信读书页面相关入口已经变化。
- **快捷键由 CEF 捕获再转发给 Qt。** 代码当前只在 Windows 的 CEF key event 中处理快捷键。
- **没有测试兜底。** 修改 `inject.js`、`CefView.py`、`WindowView.py` 后至少人工验证：登录、打开书籍、自动滚动、翻页、暂停、导出笔记、退出保存。
- **配置读写是自定义 JSON。** 项目曾放弃 `QSettings`，不要在不了解迁移影响时混用两套配置方案。

## 维护建议

如果要继续做较大规模改造，建议按优先级处理：

1. 补一份最小可运行环境说明或脚本，固定 Python 3.7 与依赖源。
2. 为 `inject.js` 的 DOM 选择器增加集中配置或容错探测。
3. 梳理 CEF 方案是否继续维护；如果要支持新 Python，需要评估 Qt WebEngine、WebView2 或其他方案。
4. 为配置读写、URL 判断、笔记格式化补单元测试。
5. 把打包流程迁移到更可重复的脚本或 CI。
