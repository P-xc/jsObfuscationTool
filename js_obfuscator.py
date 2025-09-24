#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import jsbeautifier
import subprocess
import tempfile
import shutil
import argparse
import re
from pathlib import Path
import configparser
from typing import Dict, Any, Optional, Union


class JSObfuscator:
    def __init__(self, options: Optional[Dict[str, Any]] = None, config_file: Optional[str] = None, config_section: str = "DEFAULT"):
        """
        JavaScript 混淆器
        
        Args:
            options: 混淆选项字典
            config_file: INI配置文件路径（可选）
            config_section: 配置文件中使用的section名称（默认：DEFAULT）
        """
        # 加载配置
        self.config = self._load_config(config_file, config_section)
        
        # 合并用户提供的选项
        if options:
            self._merge_options(self.config, options)
        
        self.options = self.config
        
        # 检查Node.js是否已安装
        if not self._check_nodejs_installed():
            raise RuntimeError("未检测到Node.js。请先安装Node.js: https://nodejs.org/")
            
        # 检查是否安装了javascript-obfuscator
        try:
            self._run_npm_command(["npx", "javascript-obfuscator", "--version"])
        except Exception:
            print("正在安装javascript-obfuscator...")
            try:
                self._run_npm_command(["npm", "install", "-g", "javascript-obfuscator"])
            except Exception as e:
                raise RuntimeError(f"安装javascript-obfuscator失败: {str(e)}。请手动运行: npm install -g javascript-obfuscator")
    
    def _merge_options(self, target, source):
        """递归合并选项字典"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_options(target[key], value)
            else:
                target[key] = value
        
        # 确保如果启用了debugProtection但没有提供debugProtectionInterval，添加一个默认值
        if target.get("debugProtection", False) and "debugProtectionInterval" not in target:
            target["debugProtectionInterval"] = 1000
            
        # 如果禁用了debugProtection但提供了debugProtectionInterval，则移除它
        if not target.get("debugProtection", False) and "debugProtectionInterval" in target:
            del target["debugProtectionInterval"]

    def _load_config(self, config_file: Optional[str] = None, config_section: str = "DEFAULT") -> Dict[str, Any]:
        """
        从INI配置文件加载混淆选项
        
        Args:
            config_file: INI配置文件路径，如果为None则使用默认配置
            config_section: 配置文件中使用的section名称
            
        Returns:
            混淆选项字典
        """
        # 获取默认配置
        config_dict = self._get_default_options()
        
        # 如果没有指定配置文件，返回默认配置
        if not config_file:
            return config_dict
        
        # 检查配置文件是否存在
        config_path = Path(config_file)
        if not config_path.exists():
            print(f"⚠️  配置文件 {config_file} 不存在，使用默认配置")
            return config_dict
        
        try:
            # 读取INI配置文件
            config_parser = configparser.ConfigParser()
            config_parser.read(config_path, encoding='utf-8')
            
            # 检查指定的section是否存在
            if config_section not in config_parser:
                available_sections = list(config_parser.sections())
                print(f"⚠️  配置section '{config_section}' 不存在，可用sections: {available_sections}")
                print(f"使用默认配置")
                return config_dict
            
            # 从指定section读取配置
            section_config = config_parser[config_section]
            
            # 转换配置值为正确的类型
            loaded_config = {}
            for key, default_value in config_dict.items():
                if key in section_config:
                    config_value = section_config[key]
                    # 根据默认值类型转换配置值
                    if isinstance(default_value, bool):
                        loaded_config[key] = config_value.lower() in ('true', '1', 'yes', 'on')
                    elif isinstance(default_value, (int, float)):
                        loaded_config[key] = type(default_value)(config_value)
                    elif isinstance(default_value, list):
                        # 处理列表类型（如stringArrayEncoding）
                        if config_value.strip():
                            loaded_config[key] = [item.strip() for item in config_value.split(',')]
                        else:
                            loaded_config[key] = []
                    else:
                        loaded_config[key] = config_value
                else:
                    loaded_config[key] = default_value
            
            print(f"✅ 成功从 {config_file}[{config_section}] 加载配置")
            return loaded_config
            
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            print("使用默认配置")
            return config_dict
      
    def _get_default_options(self) -> Dict[str, Any]:
        """
        获取默认混淆选项
        
        Returns:
            默认混淆选项字典
        """
        default_options = {
            "compact": True,
            "controlFlowFlattening": True,
            "controlFlowFlatteningThreshold": 0.7,
            "deadCodeInjection": True,
            "deadCodeInjectionThreshold": 0.4,
            "debugProtection": False,
            "disableConsoleOutput": True,
            "identifierNamesGenerator": "hexadecimal",
            "log": False,
            "renameGlobals": False,
            "rotateStringArray": True,
            "selfDefending": True,
            "shuffleStringArray": True,
            "splitStrings": True,
            "splitStringsChunkLength": 10,
            "stringArray": True,
            "stringArrayEncoding": ["base64"],
            "stringArrayThreshold": 0.75,
            "transformObjectKeys": False,  # 默认禁用，避免对象属性访问问题
            "unicodeEscapeSequence": False
        }
        
        # 如果启用了debugProtection，则添加debugProtectionInterval选项
        if default_options.get("debugProtection", False):
            default_options["debugProtectionInterval"] = 1000  # 设置为1000毫秒
            
        return default_options
            
    def _check_nodejs_installed(self):
        """检查Node.js是否已安装"""
        try:
            # 尝试运行node --version
            result = self._run_npm_command(["node", "--version"], capture_output=True)
            print(f"检测到Node.js版本: {result.stdout.decode('utf-8').strip()}")
            return True
        except Exception:
            return False
            
    def _run_npm_command(self, cmd, capture_output=False):
        """运行npm相关命令，处理Windows和其他系统的区别"""
        try:
            # 在Windows上，可能需要添加.cmd后缀
            if sys.platform == "win32" and cmd[0] in ["npm", "npx"]:
                cmd[0] = cmd[0] + ".cmd"
                
            return subprocess.run(
                cmd,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            if isinstance(e, FileNotFoundError):
                raise FileNotFoundError(f"找不到命令: {cmd[0]}。请确保Node.js已正确安装并添加到系统PATH中。")
            else:
                raise e
    
    def beautify_js(self, js_code):
        """美化JS代码"""
        opts = jsbeautifier.default_options()
        opts.indent_size = 2
        return jsbeautifier.beautify(js_code, opts)
    
    def is_browser_extension_background(self, file_path, js_code):
        """判断是否为浏览器扩展的background.js文件"""
        file_name = os.path.basename(file_path).lower()
        
        # 检查文件名是否为background.js
        if file_name == "background.js":
            # 检查代码中是否包含浏览器扩展API的特征
            extension_apis = [
                "chrome\\.runtime", "chrome\\.tabs", "chrome\\.storage",
                "browser\\.runtime", "browser\\.tabs", "browser\\.storage",
                "chrome\\.contextMenus", "browser\\.contextMenus",
                "chrome\\.webRequest", "browser\\.webRequest",
                "chrome\\.extension", "browser\\.extension"
            ]
            
            for api in extension_apis:
                if re.search(api, js_code):
                    return True
        
        return False
    
    def get_obfuscation_options_for_file(self, file_path, js_code):
        """根据文件类型获取适合的混淆选项"""
        options = self.options.copy()
        
        # 检查是否为浏览器扩展的background.js
        if self.is_browser_extension_background(file_path, js_code):
            print(f"检测到浏览器扩展的background.js文件: {file_path}")
            print("使用特殊混淆选项，避免使用window对象")
            
            # 为background.js设置特殊选项
            options.update({
                "target": "browser",  # 设置目标环境为浏览器
                "browserify": False,  # 不使用browserify
                "domainLock": [],     # 不使用域名锁定
                "selfDefending": False,  # 禁用自我保护，可能会导致问题
                "stringArray": True,
                "stringArrayCallsTransform": False,  # 不转换字符串数组调用
                "stringArrayWrappersCount": 1,
                "stringArrayWrappersType": "variable",
                "stringArrayThreshold": 0.75,
                "transformObjectKeys": False,  # 不转换对象键，避免API调用问题
            })
        else:
            # 对于其他JS文件，也检查是否需要禁用transformObjectKeys
            if self._should_disable_transform_object_keys(js_code):
                print(f"检测到代码中包含对象属性访问，禁用transformObjectKeys: {file_path}")
                options["transformObjectKeys"] = False
        
        return options
    
    def _should_disable_transform_object_keys(self, js_code):
        """
        检查代码中是否包含需要保留对象键名的模式
        
        Args:
            js_code (str): JavaScript代码
            
        Returns:
            bool: 如果应该禁用transformObjectKeys则返回True
        """
        # 检查常见的对象属性访问模式
        patterns = [
            r'\w+\.\w+',           # obj.prop
            r'\w+\[\s*[\'"`]\w+[\'"`]\s*\]',  # obj['prop'] 或 obj["prop"]
            r'console\.',           # console对象
            r'window\.',            # window对象
            r'document\.',          # document对象
            r'localStorage\.',      # localStorage
            r'sessionStorage\.',    # sessionStorage
            r'location\.',         # location对象
            r'navigator\.',         # navigator对象
            r'fetch\(',             # fetch API
            r'XMLHttpRequest',      # XMLHttpRequest
            r'addEventListener',    # 事件监听
            r'removeEventListener',  # 移除事件监听
            r'querySelector',       # DOM选择器
            r'querySelectorAll',    # DOM选择器全部
            r'getElementById',      # 通过ID获取元素
            r'getElementsBy',      # 通过其他方式获取元素
            r'createElement',       # 创建元素
            r'appendChild',         # 添加子元素
            r'removeChild',          # 移除子元素
            r'setAttribute',        # 设置属性
            r'getAttribute',        # 获取属性
            r'style\.',              # style属性
            r'classList\.',         # classList属性
            r'innerHTML',           # innerHTML
            r'innerText',           # innerText
            r'textContent',         # textContent
            r'value',               # input值
            r'addEventListener',    # 事件监听
            r'setTimeout',          # 定时器
            r'setInterval',         # 间隔定时器
            r'clearTimeout',        # 清除定时器
            r'clearInterval',       # 清除间隔定时器
            r'Promise',             # Promise
            r'async\s+function',     # async函数
            r'await\s+',            # await关键字
            r'try\s*{',              # try块
            r'catch\s*\(',           # catch块
            r'finally\s*{',         # finally块
            r'throw\s+',             # throw语句
            r'JSON\.',               # JSON对象
            r'Math\.',               # Math对象
            r'Date\.',               # Date对象
            r'Array\.',              # Array对象
            r'Object\.',             # Object对象
            r'String\.',             # String对象
            r'Number\.',             # Number对象
            r'Boolean\.',            # Boolean对象
            r'RegExp\.',             # RegExp对象
            r'Error\.',              # Error对象
        ]
        
        import re
        for pattern in patterns:
            if re.search(pattern, js_code, re.IGNORECASE):
                return True
        
        return False
    
    def obfuscate_js(self, js_code, file_path=None):
        """混淆单个JS代码字符串"""
        # 获取适合该文件的混淆选项
        options = self.options
        if file_path:
            options = self.get_obfuscation_options_for_file(file_path, js_code)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as temp_in:
            temp_in.write(js_code.encode('utf-8'))
            temp_in_path = temp_in.name
            
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as temp_out:
            temp_out_path = temp_out.name
            
        # 创建配置文件
        config_path = tempfile.mktemp(suffix='.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(options, f)
            
        try:
            # 构建javascript-obfuscator命令
            cmd = ["npx", "javascript-obfuscator", 
                  temp_in_path, 
                  "--output", temp_out_path,
                  "--config", config_path]
            
            # 执行混淆命令 - 使用shell=True在Windows上更可靠
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell=True)
            
            # 读取混淆后的代码
            with open(temp_out_path, 'r', encoding='utf-8') as f:
                obfuscated_code = f.read()
            
            # 如果是background.js文件，进行额外处理
            if file_path and self.is_browser_extension_background(file_path, js_code):
                # 替换可能导致问题的全局引用
                obfuscated_code = self._fix_background_js_code(obfuscated_code)
                
            return obfuscated_code
        
        except subprocess.CalledProcessError as e:
            # 清理临时文件
            for path in [temp_in_path, temp_out_path, config_path]:
                try:
                    os.unlink(path)
                except:
                    pass
            raise RuntimeError(f"JavaScript混淆失败: {e.stderr}")
        except Exception as e:
            # 清理临时文件
            for path in [temp_in_path, temp_out_path, config_path]:
                try:
                    os.unlink(path)
                except:
                    pass
            raise RuntimeError(f"JavaScript混淆失败: {str(e)}")
    
    def _fix_background_js_code(self, code):
        """修复background.js混淆后的代码，替换window引用"""
        # 替换直接的window引用
        code = re.sub(r'(?<!\w)window(?!\w)', 'self', code)
        
        # 添加安全检查，确保代码在扩展环境中正常运行
        safe_header = """
// 浏览器扩展环境适配
var globalThis = globalThis || self || window || {};
if (typeof window === 'undefined') { var window = self || globalThis; }

"""
        return safe_header + code
    
    def obfuscate_file(self, input_file, output_file=None):
        """混淆单个JS文件"""
        if not output_file:
            output_file = input_file
            
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                js_code = f.read()
                
            obfuscated_code = self.obfuscate_js(js_code, input_file)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated_code)
                
            return True
        except Exception as e:
            print(f"混淆文件 {input_file} 时出错: {str(e)}")
            return False
    
    def obfuscate_directory(self, input_dir, output_dir=None, recursive=True, copy_non_js=True):
        """混淆目录中的所有JS文件，并可选择复制非JS文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录（默认与输入目录相同）
            recursive: 是否递归处理子目录
            copy_non_js: 是否复制非JS文件到输出目录
        """
        input_dir = Path(input_dir)
        
        if not output_dir:
            output_dir = input_dir
        else:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
        
        # 获取所有文件
        all_files = []
        js_files = []
        non_js_files = []
        
        if recursive:
            for root, _, files in os.walk(input_dir):
                for file in files:
                    file_path = Path(root) / file
                    if file.endswith('.js'):
                        js_files.append(file_path)
                    elif copy_non_js:
                        non_js_files.append(file_path)
        else:
            for file_path in input_dir.glob('*'):
                if file_path.is_file():
                    if file_path.suffix == '.js':
                        js_files.append(file_path)
                    elif copy_non_js:
                        non_js_files.append(file_path)
            
        total_js_files = len(js_files)
        total_non_js_files = len(non_js_files)
        processed_files = 0
        success_files = 0
        copied_files = 0
        
        print(f"找到 {total_js_files} 个JS文件需要混淆")
        if copy_non_js:
            print(f"找到 {total_non_js_files} 个非JS文件需要复制")
        
        # 处理JS文件
        for js_file in js_files:
            rel_path = js_file.relative_to(input_dir)
            out_file = output_dir / rel_path
            
            # 确保输出目录存在
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            processed_files += 1
            print(f"[{processed_files}/{total_js_files}] 正在混淆: {rel_path}")
            
            if self.obfuscate_file(str(js_file), str(out_file)):
                success_files += 1
        
        # 复制非JS文件
        if copy_non_js and non_js_files:
            print(f"开始复制非JS文件...")
            for non_js_file in non_js_files:
                rel_path = non_js_file.relative_to(input_dir)
                out_file = output_dir / rel_path
                
                # 确保输出目录存在
                out_file.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    shutil.copy2(non_js_file, out_file)
                    copied_files += 1
                except Exception as e:
                    print(f"复制文件 {non_js_file} 时出错: {str(e)}")
            
            print(f"复制完成: {copied_files}/{total_non_js_files} 个非JS文件成功复制")
                
        print(f"混淆完成: {success_files}/{total_js_files} 个JS文件成功混淆")
        return success_files, total_js_files, copied_files, total_non_js_files


def main():
    parser = argparse.ArgumentParser(description='JavaScript代码混淆工具')
    parser.add_argument('input', help='输入JS文件或目录')
    parser.add_argument('-o', '--output', help='输出JS文件或目录 (默认覆盖输入)')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-c', '--config', help='混淆配置文件 (JSON格式)')
    parser.add_argument('--no-copy', action='store_true', help='不复制非JS文件')
    
    args = parser.parse_args()
    
    # 加载配置
    options = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                options = json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            return 1
    
    try:
        obfuscator = JSObfuscator(options)
        
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"错误: 输入路径 '{args.input}' 不存在")
            return 1
        
        if input_path.is_file():
            if not input_path.name.endswith('.js'):
                print(f"警告: 输入文件 '{args.input}' 不是JS文件")
                return 1
                
            output_file = args.output if args.output else args.input
            success = obfuscator.obfuscate_file(args.input, output_file)
            return 0 if success else 1
        else:
            output_dir = args.output if args.output else args.input
            copy_non_js = not args.no_copy
            obfuscator.obfuscate_directory(args.input, output_dir, args.recursive, copy_non_js)
            return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())