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
from pathlib import Path


class JSObfuscator:
    def __init__(self, options=None):
        """初始化JavaScript混淆器"""
        self.default_options = {
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
            "transformObjectKeys": True,
            "unicodeEscapeSequence": False
        }
        
        # 如果启用了debugProtection，则添加debugProtectionInterval选项
        if self.default_options.get("debugProtection", False):
            self.default_options["debugProtectionInterval"] = 1000  # 设置为1000毫秒
        
        self.options = self.default_options.copy()
        if options:
            # 确保如果用户提供的配置启用了debugProtection但没有提供debugProtectionInterval，添加一个默认值
            if options.get("debugProtection", False) and "debugProtectionInterval" not in options:
                options["debugProtectionInterval"] = 1000
                
            # 如果用户禁用了debugProtection但提供了debugProtectionInterval，则移除它
            if not options.get("debugProtection", False) and "debugProtectionInterval" in options:
                del options["debugProtectionInterval"]
                
            self.options.update(options)
            
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
    
    def obfuscate_js(self, js_code):
        """混淆单个JS代码字符串"""
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as temp_in:
            temp_in.write(js_code.encode('utf-8'))
            temp_in_path = temp_in.name
            
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as temp_out:
            temp_out_path = temp_out.name
            
        # 创建配置文件
        config_path = tempfile.mktemp(suffix='.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.options, f)
            
        try:
            # 执行混淆
            cmd = ["npx", "javascript-obfuscator", 
                  temp_in_path, 
                  "--output", temp_out_path,
                  "--config", config_path]
            
            self._run_npm_command(cmd)
            
            # 读取混淆后的代码
            with open(temp_out_path, 'r', encoding='utf-8') as f:
                obfuscated_code = f.read()
                
            return obfuscated_code
        
        finally:
            # 清理临时文件
            for path in [temp_in_path, temp_out_path, config_path]:
                try:
                    os.unlink(path)
                except:
                    pass
    
    def obfuscate_file(self, input_file, output_file=None):
        """混淆单个JS文件"""
        if not output_file:
            output_file = input_file
            
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                js_code = f.read()
                
            obfuscated_code = self.obfuscate_js(js_code)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(obfuscated_code)
                
            return True
        except Exception as e:
            print(f"混淆文件 {input_file} 时出错: {str(e)}")
            return False
    
    def obfuscate_directory(self, input_dir, output_dir=None, recursive=True):
        """混淆目录中的所有JS文件"""
        input_dir = Path(input_dir)
        
        if not output_dir:
            output_dir = input_dir
        else:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
        
        # 获取所有JS文件
        js_files = []
        if recursive:
            for root, _, files in os.walk(input_dir):
                for file in files:
                    if file.endswith('.js'):
                        js_files.append(Path(root) / file)
        else:
            js_files = list(input_dir.glob('*.js'))
            
        total_files = len(js_files)
        processed_files = 0
        success_files = 0
        
        print(f"找到 {total_files} 个JS文件需要混淆")
        
        for js_file in js_files:
            rel_path = js_file.relative_to(input_dir)
            out_file = output_dir / rel_path
            
            # 确保输出目录存在
            out_file.parent.mkdir(parents=True, exist_ok=True)
            
            processed_files += 1
            print(f"[{processed_files}/{total_files}] 正在混淆: {rel_path}")
            
            if self.obfuscate_file(str(js_file), str(out_file)):
                success_files += 1
                
        print(f"混淆完成: {success_files}/{total_files} 个文件成功混淆")
        return success_files, total_files


def main():
    parser = argparse.ArgumentParser(description='JavaScript代码混淆工具')
    parser.add_argument('input', help='输入JS文件或目录')
    parser.add_argument('-o', '--output', help='输出JS文件或目录 (默认覆盖输入)')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-c', '--config', help='混淆配置文件 (JSON格式)')
    
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
            obfuscator.obfuscate_directory(args.input, output_dir, args.recursive)
            return 0
    except Exception as e:
        print(f"错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 