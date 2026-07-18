# WxReader / 微读自动阅读

![WxReader banner](./assets/banner.png)

WxReader 是一个基于 **PySide6 + cefpython3** 的微信读书自动阅读控制台。它不是完整阅读器，也不打算替代微信读书客户端；网页区域只负责登录、打开书籍和承载自动滚动脚本，桌面端主要提供自动阅读控制、定时任务和计时器。

这个仓库已经按个人自用和二次开发场景重新整理，旧的帮助、关于、赞助、笔记、全屏、通知等功能已移除。

## 当前状态

| 项目 | 内容 |
| --- | --- |
| 主要平台 | Windows |
| 技术栈 | Python 3.7、PySide6、cefpython3、PyInstaller |
| 推荐环境 | Conda 环境 `wxreader-py37` |
| 程序入口 | `app/Application.py` |
| 资源入口 | `resources/js/inject.js`、`resources/theme/default.qss` |
| 维护定位 | 自用工具，优先保证自动阅读相关流程稳定 |

> `cefpython3==66.0` 是本项目最硬的版本约束。请优先固定 Python 3.7，不要直接升级到 Python 3.8+。

## 功能

- 嵌入微信读书网页，默认打开 `https://weread.qq.com/`
- 自动滚动阅读页，速度范围为 `1-10`
- 滚动到底后自动触发下一章或下一页
- 页面加载、选中文字、打开目录或笔记面板等情况下自动暂停滚动
- 顶部控制栏提供开始/暂停、首页、刷新、定时、退出、速度调节
- 定时面板嵌入在顶部控制栏下方，不再使用独立窗口
- 每日时间段支持多条任务，每条可单独 `启用` 或 `停用`
- 计时器启动后立即开始自动阅读，到点自动停止，并在右上角状态框显示倒计时
- 用户配置、窗口位置、阅读速度、最新 URL、定时任务保存到本地 JSON

## 已移除

- 帮助
- 关于
- 赞助
- 笔记导出
- 全屏
- 通知按钮和读完后的 GET 通知
- URL 输入框
- 步幅调节和“步幅 x 页面”
- 旧工具栏、旧菜单动作和旧宣传/历史资料

## 快速开始

### 1. 创建 Conda 环境

在项目根目录运行：

```powershell
conda env create -f environment.yml
```

如果环境已经存在，使用下面命令同步：

```powershell
conda env update -f environment.yml --prune
```

### 2. 启动应用

推荐使用仓库内脚本：

```powershell
.\scripts\run-conda.ps1
```

调试模式：

```powershell
.\scripts\run-conda.ps1 -Debug
```

也可以手动启动：

```powershell
conda run -n wxreader-py37 python .\app\Application.py
```

### 3. 依赖安装补救

如果 Windows 代理导致 pip 安装失败，可临时绕过代理并使用清华 PyPI 镜像：

```powershell
$env:NO_PROXY='*'
$env:no_proxy='*'
conda run -n wxreader-py37 python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --default-timeout 100
```

## 使用说明

### 自动阅读

1. 启动应用并登录微信读书。
2. 打开一本书的阅读页面。
3. 点击顶部 `开始自动阅读`，或按 `F10`。
4. 用顶部速度条调整滚动速度，范围为 `1-10`。

### 每日时间段

点击顶部 `定时` 后，控制栏下方会展开定时面板。

- `新增`：添加一条每日自动阅读时间段。
- `更新`：修改当前选中的时间段。
- `删除`：删除当前选中的时间段。
- `启用` / `停用`：只控制当前选中的这一条时间段。

调度逻辑只判断当前时间是否落在某条已启用的时间段内。没有额外的“每日任务总开关”。

### 计时器

计时器是一次性任务：

1. 设置分钟数。
2. 点击 `开始计时`。
3. 应用立即开始自动阅读。
4. 到点后自动停止阅读并播放提示音。

计时器运行时，右上角状态框会显示 `计时 mm:ss` 或 `计时 hh:mm:ss`。

## 快捷键

| 快捷键 | 功能 |
| --- | --- |
| `F4` | 回到微信读书首页 |
| `F5` | 刷新当前页面 |
| `F10` | 切换自动阅读 |
| `F12` | 展开或收起定时面板 |
| `+` / `-` | 提高或降低阅读速度 |
| `Alt+Q` | 退出应用 |

## 项目结构

```text
.
├── app/
│   ├── Application.py       # 程序入口
│   ├── conf/                # 配置、语言、资源映射
│   ├── helper/              # 工具、偏好设置、全局信号
│   └── ui/
│       ├── model/           # CEF 相关模型
│       └── view/            # Qt 主窗口、定时面板、CEF 视图
├── resources/
│   ├── icon/app.ico         # 应用图标
│   ├── js/inject.js         # 注入微信读书页面的自动阅读脚本
│   └── theme/default.qss    # Qt 资源主题
├── scripts/
│   ├── run-conda.ps1        # Conda 启动脚本
│   ├── rcc/Rcc.py           # 生成 Qt 资源文件
│   └── package/             # 打包脚本
├── assets/
│   ├── app-icon.png         # 应用图标源图
│   └── banner.png           # 仓库首页图
├── codex.md                 # 后续 AI/开发者维护注意事项
├── environment.yml          # Conda 环境定义
└── requirements.txt         # pip 依赖
```

## 核心实现

### 主窗口

`app/ui/view/WindowView.py` 是主界面和状态机核心。它负责：

- 顶部控制栏布局
- 自动阅读按钮状态
- 速度调节
- 定时面板展开/收起
- 每日时间段调度
- 计时器倒计时状态
- CEF 子窗口尺寸同步

### 定时面板

`app/ui/view/TimingView.py` 现在提供的是嵌入式 `TimingPanel`，不是弹窗。每日时间段状态保存在 `timing.segments` 中，每条数据包含：

```json
{
  "start": 32400000,
  "stop": 36000000,
  "enabled": true
}
```

`enabled` 是唯一的定时启停控制。旧的 `timing.enabled` 全局开关已不再使用。

### CEF 和页面脚本

`app/ui/view/CefView.py` 负责嵌入 CEF，并建立 Python 与 JS 的双向调用。

- Python 调 JS：`doScroll`、`alert`
- JS 调 Python：`updateState`、`sendAction`
- 翻到下一节：JS 判断到底后通知 Python，Python 通过 CEF `SendKeyEvent` 直接发送右箭头按键

`resources/js/inject.js` 是自动阅读的关键文件。微信读书页面结构如果变化，优先检查这里的 DOM 选择器。

### 用户配置

用户配置由 `app/helper/Preferences.py` 管理，保存为 JSON。默认路径来自 Qt 的 `QStandardPaths.GenericConfigLocation`，并拼接应用名：

```text
<GenericConfigLocation>/WxReader/WxReader.json
```

CEF 缓存、Cookie 和日志也在同一个 `WxReader` 应用存储目录下。

## 资源更新

新增或修改 `resources/` 下的资源后，需要重新生成 Qt 资源文件：

```powershell
conda run -n wxreader-py37 python .\scripts\rcc\Rcc.py
```

该脚本会更新：

- `scripts/rcc/Resources.qrc`
- `app/conf/Resources.py`
- `app/conf/ResMap.py`

如果启动时报 `qInitResources` 相关错误，优先重新运行这条命令。

## 打包

打包脚本位于 `scripts/package/`：

```powershell
cd .\scripts\package
conda run -n wxreader-py37 python .\bundle.py -V 2.0.2.1 -C
```

常用参数：

| 参数 | 说明 |
| --- | --- |
| `-V a.b.c.d` | 必填，设置四段式版本号 |
| `-D` | 调试模式 |
| `-U` | 使用 UPX 压缩 |
| `-C` | 禁用缓存，重新清理 `build/` 和 `dist/` |

打包产物优先使用便携版：

```text
scripts/package/dist/WxReader/WxReader.exe
scripts/package/WxReader_v<version>_Portable.zip
```

这是 CEF/PySide6 的 onedir 程序，不要只复制单个 `WxReader.exe` 到别处运行；需要带上同目录依赖，或直接使用便携 zip。

NSIS 安装包依赖本机 `makensis`。如果没有安装 NSIS，脚本可能打印 `makensis` 不存在；这不影响便携版生成。

## 二次开发注意事项

- 优先使用 Conda 环境 `wxreader-py37`，不要直接用系统 Python。
- 在 IDE 中建议把 `app/` 标记为 Sources Root。
- 不要随手升级 Python 或 CEF；`cefpython3==66.0` 是最大兼容风险。
- 不要把帮助、关于、赞助、笔记导出、全屏、通知等旧功能加回来。
- 主界面不展示 URL，不提供步幅调节。
- 修改 CEF、Qt 主窗口、定时状态机或 `resources/js/inject.js` 后，需要人工验证登录、打开书籍、自动滚动、翻页、暂停、每日任务、计时器、退出保存。
- 本项目目前没有自动化测试；每次功能改动后至少运行：

```powershell
conda run -n wxreader-py37 python -m compileall app
```

更多面向后续 AI/开发者的维护记录见 `codex.md`。
