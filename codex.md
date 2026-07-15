# Codex Notes

这个文件写给后续接手本仓库的 AI。新对话开始时请优先读取它，再看 README 和源码。

## 用户偏好

- 这个项目是用户自用并二次开发，不需要保留原项目的旧宣传、旧更新日志、旧 TODO、旧问题记录。
- 后续执行任务时，如果遇到反复出现的坑、环境限制、运行方式、隐含约定，请自动补充到本文件。
- 本项目以后优先使用 Conda 环境运行，不再优先使用 venv 或系统 Python。

## 当前项目状态

- README 已重写为面向二次开发的说明文档。
- 已删除旧资料文件：`CHANGELOG.md`、`TODO.md`、`Questions.md`。
- `licenses/` 目录也已删除，README 中已移除相关引用。
- 已新增 `environment.yml` 和 `scripts/run-conda.ps1`。
- 当前推荐 Conda 环境名：`wxreader-py37`。

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

- 不要直接用系统 Python 运行本项目；很容易因为 Python 版本或 CEF/PySide6 不匹配出问题。
- 在 IDE 中需要把 `app/` 标记为 Sources Root，否则 `from conf...`、`from helper...` 这类导入会被标红。
- 该项目没有自动化测试；改动 CEF、Qt 主窗口或 `resources/js/inject.js` 后，需要人工验证登录、打开书籍、自动滚动、翻页、暂停、导出笔记、退出保存。

## 代码注意事项

- 程序入口是 `app/Application.py`。
- 主窗口逻辑在 `app/ui/view/WindowView.py`。
- CEF 嵌入和 Python/JS 绑定在 `app/ui/view/CefView.py`。
- 微信读书页面自动化逻辑主要在 `resources/js/inject.js`，高度依赖微信读书 DOM class；如果微信读书改版，优先检查这里。
- 用户配置由 `app/helper/Preferences.py` 管理，写入 JSON；历史上放弃过 `QSettings`，不要无准备混用两套配置。
- 新增或修改 `resources/` 后需要重新生成 Qt 资源：

```powershell
conda run -n wxreader-py37 python .\scripts\rcc\Rcc.py
```

## 后续维护建议

- 优先保证环境可复现：`environment.yml`、`requirements.txt`、README 和实际可运行环境要保持一致。
- 如果准备升级 Python，需要先替换或重做 WebView/CEF 方案。
- 如果继续增强自动阅读功能，应先把 `inject.js` 中 DOM 选择器集中管理，减少微信读书改版带来的维护成本。
