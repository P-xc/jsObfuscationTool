# JavaScript代码混淆工具

这是一个用Python编写的JavaScript代码混淆工具，可以混淆单个JS文件或整个目录中的所有JS文件，而不影响代码的功能。提供命令行和图形界面两种使用方式。

## 环境要求

- Python 3.6+
- Node.js（必须安装并添加到系统PATH中）
- Tkinter（GUI界面需要，Python通常自带）

## 安装依赖

1. 首先，确保已安装Python和Node.js环境：
   - Python下载：https://www.python.org/downloads/
   - Node.js下载：https://nodejs.org/

2. 安装所需的Python依赖：

```bash
pip install -r requirements.txt
```

该工具会自动检查并安装必要的Node.js依赖（javascript-obfuscator）。如果自动安装失败，可以手动安装：

```bash
npm install -g javascript-obfuscator
```

## 使用方法

### 图形界面（GUI）

启动图形界面：

```bash
python js_obfuscator_gui.py
```

GUI界面包含三个选项卡：

1. **基本设置**：选择输入/输出文件或目录，设置基本选项
2. **高级设置**：配置详细的混淆参数
3. **运行日志**：显示混淆过程的日志信息

### 命令行界面（CLI）

#### 混淆单个文件

```bash
python js_obfuscator.py path/to/file.js -o path/to/output.js
```

#### 混淆整个目录

```bash
python js_obfuscator.py path/to/directory -o path/to/output_directory -r
```

参数说明：
- `-o`, `--output`: 指定输出文件或目录（可选，默认覆盖原文件）
- `-r`, `--recursive`: 递归处理子目录中的JS文件
- `-c`, `--config`: 指定混淆配置文件（JSON格式）
- `--no-copy`: 不复制非JS文件（默认会复制非JS文件到输出目录）

### 自定义混淆配置

可以通过修改`config.json`文件来自定义混淆选项，然后使用`-c`参数指定配置文件：

```bash
python js_obfuscator.py path/to/directory -c config.json
```

在GUI界面中，可以在"高级设置"选项卡中调整混淆参数，并通过"保存配置"按钮保存为JSON文件。

## 文件处理说明

- **JS文件**: 将被混淆处理，混淆后的代码会保持原有功能
- **非JS文件**: 默认会被直接复制到输出目录，保持原始项目结构完整
  - 在GUI中可以通过"复制非JS文件到输出目录"选项控制
  - 在命令行中可以使用`--no-copy`参数禁用此功能

## 特殊文件处理

### 浏览器扩展的background.js

工具会自动检测浏览器扩展的background.js文件（通过文件名和代码特征），并应用特殊的混淆设置：

- 设置目标环境为浏览器
- 禁用可能导致问题的混淆选项
- 添加环境适配代码，解决`window is not defined`错误
- 替换直接的window引用为self

这确保了混淆后的background.js文件可以在浏览器扩展的背景页环境中正常运行。

## 配置选项说明

- `compact`: 生成紧凑的代码
- `controlFlowFlattening`: 控制流平坦化，使代码更难理解
- `deadCodeInjection`: 注入无用代码
- `disableConsoleOutput`: 禁用console.log等输出
- `identifierNamesGenerator`: 标识符名称生成方式
- `renameGlobals`: 是否重命名全局变量
- `selfDefending`: 自我保护，防止格式化
- `stringArray`: 将字符串移到一个数组中
- `stringArrayEncoding`: 字符串数组编码方式
- 更多选项请参考[javascript-obfuscator文档](https://github.com/javascript-obfuscator/javascript-obfuscator)

## GUI界面功能

### 基本设置
- 选择输入文件或目录
- 选择输出文件或目录
- 设置是否递归处理子目录
- 设置是否复制非JS文件
- 加载或保存配置文件

### 高级设置
- 混淆选项：控制流平坦化、代码注入、调试保护等
- 数值选项：各种阈值和参数调整
- 字符串数组编码选项

### 运行日志
- 显示混淆过程的详细信息
- 清除日志功能

## 常见问题

1. 如果遇到"找不到命令: node"或"找不到命令: npm.cmd"等错误，请确保Node.js已正确安装并添加到系统PATH中。
2. Windows系统下可能需要以管理员权限运行命令提示符或PowerShell来全局安装Node.js包。
3. 如果GUI界面无法启动，请确保Python安装时包含了Tkinter库。
4. 如果混淆后的浏览器扩展脚本出现`window is not defined`错误，请确保使用最新版本的工具，它已经包含了对background.js的特殊处理。

## 注意事项

1. 混淆后的代码可能会增加文件大小
2. 过度混淆可能会影响代码执行效率
3. 某些特殊的JavaScript代码结构可能在混淆后出现问题，请在正式使用前进行充分测试 