# JavaScript代码混淆工具

这是一个用Python编写的JavaScript代码混淆工具，可以混淆单个JS文件或整个目录中的所有JS文件，而不影响代码的功能。

## 环境要求

- Python 3.6+
- Node.js（必须安装并添加到系统PATH中）

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

### 混淆单个文件

```bash
python js_obfuscator.py path/to/file.js -o path/to/output.js
```

### 混淆整个目录

```bash
python js_obfuscator.py path/to/directory -o path/to/output_directory -r
```

参数说明：
- `-o`, `--output`: 指定输出文件或目录（可选，默认覆盖原文件）
- `-r`, `--recursive`: 递归处理子目录中的JS文件
- `-c`, `--config`: 指定混淆配置文件（JSON格式）

### 自定义混淆配置

可以通过修改`config.json`文件来自定义混淆选项，然后使用`-c`参数指定配置文件：

```bash
python js_obfuscator.py path/to/directory -c config.json
```

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

## 常见问题

1. 如果遇到"找不到命令: node"或"找不到命令: npm.cmd"等错误，请确保Node.js已正确安装并添加到系统PATH中。
2. Windows系统下可能需要以管理员权限运行命令提示符或PowerShell来全局安装Node.js包。

## 注意事项

1. 混淆后的代码可能会增加文件大小
2. 过度混淆可能会影响代码执行效率
3. 某些特殊的JavaScript代码结构可能在混淆后出现问题，请在正式使用前进行充分测试 