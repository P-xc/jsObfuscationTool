#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import json
import io
from contextlib import redirect_stdout

# 导入混淆器类
from js_obfuscator import JSObfuscator

class RedirectText:
    """重定向标准输出到Tkinter文本控件"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

class JSObfuscatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JavaScript代码混淆工具")
        self.root.geometry("800x600")
        
        # 设置窗口图标（如果有）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡控件
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # 创建基本选项卡
        self.basic_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.basic_tab, text="基本设置")
        
        # 创建高级选项卡
        self.advanced_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.advanced_tab, text="高级设置")
        
        # 创建日志选项卡
        self.log_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.log_tab, text="运行日志")
        
        self.tab_control.pack(fill=tk.BOTH, expand=True)
        
        # 设置基本选项卡
        self.setup_basic_tab()
        
        # 设置高级选项卡
        self.setup_advanced_tab()
        
        # 设置日志选项卡
        self.setup_log_tab()
        
        # 初始化混淆选项
        self.obfuscation_options = {}
        self.load_default_options()
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_basic_tab(self):
        """设置基本选项卡的UI元素"""
        # 创建输入/输出框架
        io_frame = ttk.LabelFrame(self.basic_tab, text="输入/输出", padding="10")
        io_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 输入选择
        input_frame = ttk.Frame(io_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="输入:").pack(side=tk.LEFT, padx=(0, 5))
        self.input_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(input_frame, text="选择文件", command=self.select_input_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(input_frame, text="选择文件夹", command=self.select_input_dir).pack(side=tk.LEFT)
        
        # 输出选择
        output_frame = ttk.Frame(io_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="输出:").pack(side=tk.LEFT, padx=(0, 5))
        self.output_var = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(output_frame, text="选择文件", command=self.select_output_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(output_frame, text="选择文件夹", command=self.select_output_dir).pack(side=tk.LEFT)
        
        # 基本选项框架
        options_frame = ttk.LabelFrame(self.basic_tab, text="基本选项", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 递归处理子目录
        self.recursive_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive_var).pack(anchor=tk.W, pady=5)
        
        # 复制非JS文件
        self.copy_non_js_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="复制非JS文件到输出目录", variable=self.copy_non_js_var).pack(anchor=tk.W, pady=5)
        
        # 配置文件
        config_frame = ttk.Frame(options_frame)
        config_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(config_frame, text="配置文件:").pack(side=tk.LEFT, padx=(0, 5))
        self.config_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.config_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(config_frame, text="选择文件", command=self.select_config_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT)
        
        # 操作按钮
        action_frame = ttk.Frame(self.basic_tab)
        action_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(action_frame, text="开始混淆", command=self.start_obfuscation, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(action_frame, text="重置", command=self.reset_form).pack(side=tk.RIGHT, padx=5)
        
        # 创建Accent样式
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
        
    def setup_advanced_tab(self):
        """设置高级选项卡的UI元素"""
        # 创建滚动框架
        canvas = tk.Canvas(self.advanced_tab)
        scrollbar = ttk.Scrollbar(self.advanced_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 混淆选项
        options_frame = ttk.LabelFrame(scrollable_frame, text="混淆选项", padding="10")
        options_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)
        
        # 创建混淆选项控件
        self.options_vars = {}
        
        # 布尔选项
        bool_options = [
            ("compact", "生成紧凑代码"),
            ("controlFlowFlattening", "控制流平坦化"),
            ("deadCodeInjection", "注入无用代码"),
            ("debugProtection", "调试保护"),
            ("disableConsoleOutput", "禁用控制台输出"),
            ("log", "记录日志"),
            ("renameGlobals", "重命名全局变量"),
            ("rotateStringArray", "旋转字符串数组"),
            ("selfDefending", "自我保护"),
            ("shuffleStringArray", "打乱字符串数组"),
            ("splitStrings", "分割字符串"),
            ("stringArray", "使用字符串数组"),
            ("transformObjectKeys", "转换对象键"),
            ("unicodeEscapeSequence", "Unicode转义序列")
        ]
        
        for i, (option, label) in enumerate(bool_options):
            row = i // 2
            col = i % 2
            
            self.options_vars[option] = tk.BooleanVar()
            ttk.Checkbutton(
                options_frame, 
                text=label, 
                variable=self.options_vars[option],
                command=lambda opt=option: self.update_option(opt)
            ).grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
        
        # 数值选项框架
        numeric_frame = ttk.LabelFrame(scrollable_frame, text="数值选项", padding="10")
        numeric_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)
        
        # 数值选项
        numeric_options = [
            ("controlFlowFlatteningThreshold", "控制流平坦化阈值", 0, 1),
            ("deadCodeInjectionThreshold", "无用代码注入阈值", 0, 1),
            ("stringArrayThreshold", "字符串数组阈值", 0, 1),
            ("splitStringsChunkLength", "字符串分割块长度", 1, 100)
        ]
        
        for i, (option, label, min_val, max_val) in enumerate(numeric_options):
            frame = ttk.Frame(numeric_frame)
            frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT, padx=(0, 5))
            
            self.options_vars[option] = tk.DoubleVar()
            if option == "splitStringsChunkLength":
                spinbox = ttk.Spinbox(
                    frame, 
                    from_=min_val, 
                    to=max_val, 
                    textvariable=self.options_vars[option],
                    increment=1,
                    width=10,
                    command=lambda opt=option: self.update_option(opt)
                )
            else:
                spinbox = ttk.Spinbox(
                    frame, 
                    from_=min_val, 
                    to=max_val, 
                    textvariable=self.options_vars[option],
                    increment=0.1,
                    width=10,
                    command=lambda opt=option: self.update_option(opt)
                )
            spinbox.pack(side=tk.LEFT)
            spinbox.bind("<KeyRelease>", lambda e, opt=option: self.update_option(opt))
        
        # 标识符生成器选项
        id_frame = ttk.Frame(numeric_frame)
        id_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(id_frame, text="标识符名称生成器:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.id_generator_var = tk.StringVar()
        id_combo = ttk.Combobox(
            id_frame, 
            textvariable=self.id_generator_var,
            values=["hexadecimal", "mangled", "mangled-shuffled"],
            width=20,
            state="readonly"
        )
        id_combo.pack(side=tk.LEFT)
        id_combo.bind("<<ComboboxSelected>>", lambda e: self.update_option("identifierNamesGenerator"))
        self.options_vars["identifierNamesGenerator"] = self.id_generator_var
        
        # 字符串数组编码选项
        encoding_frame = ttk.LabelFrame(scrollable_frame, text="字符串数组编码", padding="10")
        encoding_frame.pack(fill=tk.X, padx=10, pady=10, expand=True)
        
        self.encoding_vars = {
            "base64": tk.BooleanVar(),
            "rc4": tk.BooleanVar()
        }
        
        for i, (encoding, var) in enumerate(self.encoding_vars.items()):
            ttk.Checkbutton(
                encoding_frame, 
                text=encoding, 
                variable=var,
                command=self.update_string_array_encoding
            ).grid(row=0, column=i, sticky=tk.W, padx=10, pady=5)
    
    def setup_log_tab(self):
        """设置日志选项卡的UI元素"""
        # 创建日志文本框
        self.log_text = scrolledtext.ScrolledText(self.log_tab, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.log_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(button_frame, text="清除日志", command=self.clear_log).pack(side=tk.RIGHT)
    
    def select_input_file(self):
        """选择输入文件"""
        file_path = filedialog.askopenfilename(
            title="选择JavaScript文件",
            filetypes=[("JavaScript文件", "*.js"), ("所有文件", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)
    
    def select_input_dir(self):
        """选择输入目录"""
        dir_path = filedialog.askdirectory(title="选择输入目录")
        if dir_path:
            self.input_var.set(dir_path)
    
    def select_output_file(self):
        """选择输出文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存JavaScript文件",
            filetypes=[("JavaScript文件", "*.js"), ("所有文件", "*.*")],
            defaultextension=".js"
        )
        if file_path:
            self.output_var.set(file_path)
    
    def select_output_dir(self):
        """选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_var.set(dir_path)
    
    def select_config_file(self):
        """选择配置文件"""
        file_path = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        if file_path:
            self.config_var.set(file_path)
            self.load_config(file_path)
    
    def load_default_options(self):
        """加载默认混淆选项"""
        # 创建一个JSObfuscator实例以获取默认选项
        try:
            obfuscator = JSObfuscator()
            self.obfuscation_options = obfuscator.default_options.copy()
            
            # 更新UI控件
            self.update_ui_from_options()
        except Exception as e:
            messagebox.showerror("错误", f"加载默认选项时出错：{str(e)}")
    
    def load_config(self, config_file):
        """从配置文件加载混淆选项"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                options = json.load(f)
                self.obfuscation_options.update(options)
                
                # 更新UI控件
                self.update_ui_from_options()
                
                self.log(f"已加载配置文件: {config_file}")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置文件时出错：{str(e)}")
    
    def save_config(self):
        """保存混淆选项到配置文件"""
        file_path = filedialog.asksaveasfilename(
            title="保存配置文件",
            filetypes=[("JSON文件", "*.json")],
            defaultextension=".json"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.obfuscation_options, f, indent=2)
                    
                self.config_var.set(file_path)
                self.log(f"已保存配置文件: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存配置文件时出错：{str(e)}")
    
    def update_ui_from_options(self):
        """根据混淆选项更新UI控件"""
        for option, value in self.obfuscation_options.items():
            if option in self.options_vars:
                if option == "identifierNamesGenerator":
                    self.options_vars[option].set(value)
                elif isinstance(value, (bool, int, float)):
                    self.options_vars[option].set(value)
        
        # 更新字符串数组编码选项
        if "stringArrayEncoding" in self.obfuscation_options:
            encodings = self.obfuscation_options["stringArrayEncoding"]
            for encoding in self.encoding_vars:
                self.encoding_vars[encoding].set(encoding in encodings)
    
    def update_option(self, option):
        """更新混淆选项"""
        try:
            value = self.options_vars[option].get()
            
            # 特殊处理debugProtectionInterval
            if option == "debugProtection":
                if value and "debugProtectionInterval" not in self.obfuscation_options:
                    self.obfuscation_options["debugProtectionInterval"] = 1000
                elif not value and "debugProtectionInterval" in self.obfuscation_options:
                    del self.obfuscation_options["debugProtectionInterval"]
            
            self.obfuscation_options[option] = value
        except Exception as e:
            self.log(f"更新选项时出错: {str(e)}")
    
    def update_string_array_encoding(self):
        """更新字符串数组编码选项"""
        encodings = []
        for encoding, var in self.encoding_vars.items():
            if var.get():
                encodings.append(encoding)
        
        if not encodings:
            encodings = ["base64"]  # 默认至少选择一种编码
            self.encoding_vars["base64"].set(True)
        
        self.obfuscation_options["stringArrayEncoding"] = encodings
    
    def reset_form(self):
        """重置表单"""
        self.input_var.set("")
        self.output_var.set("")
        self.config_var.set("")
        self.recursive_var.set(True)
        self.copy_non_js_var.set(True)
        self.load_default_options()
        self.log("已重置表单")
    
    def clear_log(self):
        """清除日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def log(self, message):
        """添加日志消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_obfuscation(self):
        """开始混淆处理"""
        input_path = self.input_var.get().strip()
        output_path = self.output_var.get().strip()
        recursive = self.recursive_var.get()
        copy_non_js = self.copy_non_js_var.get()
        
        if not input_path:
            messagebox.showerror("错误", "请选择输入文件或目录")
            return
        
        # 创建并启动混淆线程
        threading.Thread(target=self.obfuscate, args=(input_path, output_path, recursive, copy_non_js), daemon=True).start()
    
    def obfuscate(self, input_path, output_path, recursive, copy_non_js):
        """执行混淆处理"""
        try:
            self.status_var.set("正在混淆...")
            self.log(f"开始混淆: {input_path}")
            
            # 重定向标准输出到日志窗口
            redirect = RedirectText(self.log_text)
            sys.stdout = redirect
            
            # 创建混淆器
            obfuscator = JSObfuscator(self.obfuscation_options)
            
            input_path_obj = Path(input_path)
            if input_path_obj.is_file():
                # 混淆单个文件
                if not output_path:
                    output_path = input_path
                
                success = obfuscator.obfuscate_file(input_path, output_path)
                if success:
                    self.log(f"文件混淆成功: {output_path}")
                else:
                    self.log(f"文件混淆失败: {input_path}")
            else:
                # 混淆目录
                if not output_path:
                    output_path = input_path
                
                success_js, total_js, copied_files, total_non_js = obfuscator.obfuscate_directory(
                    input_path, output_path, recursive, copy_non_js
                )
                self.log(f"目录混淆完成: {success_js}/{total_js} 个JS文件成功混淆")
                if copy_non_js and total_non_js > 0:
                    self.log(f"文件复制完成: {copied_files}/{total_non_js} 个非JS文件成功复制")
            
            self.status_var.set("混淆完成")
            
        except Exception as e:
            self.log(f"混淆过程中出错: {str(e)}")
            self.status_var.set("混淆失败")
        finally:
            # 恢复标准输出
            sys.stdout = sys.__stdout__

def main():
    root = tk.Tk()
    app = JSObfuscatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 