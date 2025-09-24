#!/usr/bin/env python3
"""
测试js_obfuscator.py的混淆功能
"""

import os
import sys
from js_obfuscator import JSObfuscator

def test_single_file():
    """测试单个文件混淆"""
    print("🧪 测试单个文件混淆...")
    
    # 创建测试JS文件
    test_js_content = """
function calculateSum(a, b) {
    const result = a + b;
    console.log("Sum of " + a + " and " + b + " is: " + result);
    return result;
}

const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((acc, curr) => acc + curr, 0);
console.log("Total sum:", sum);

class Calculator {
    constructor() {
        this.value = 0;
    }
    
    add(num) {
        this.value += num;
        return this;
    }
    
    getValue() {
        return this.value;
    }
}

const calc = new Calculator();
calc.add(10).add(20);
console.log("Calculator value:", calc.getValue());
"""
    
    test_input_file = "test_input.js"
    test_output_file = "test_output.js"
    
    try:
        # 写入测试文件
        with open(test_input_file, 'w', encoding='utf-8') as f:
            f.write(test_js_content)
        
        # 初始化混淆器
        obfuscator = JSObfuscator()
        
        # 混淆文件
        obfuscator.obfuscate_file(test_input_file, test_output_file)
        
        # 检查输出文件
        if os.path.exists(test_output_file):
            with open(test_output_file, 'r', encoding='utf-8') as f:
                obfuscated_content = f.read()
            
            print(f"✅ 单个文件混淆成功！")
            print(f"📊 原始大小: {len(test_js_content)} 字符")
            print(f"📊 混淆后大小: {len(obfuscated_content)} 字符")
            print(f"📈 压缩比: {len(obfuscated_content)/len(test_js_content):.2f}")
            
            # 检查是否包含原始的关键字（应该被混淆）
            if "calculateSum" not in obfuscated_content and "console.log" not in obfuscated_content:
                print("✅ 代码已被正确混淆")
            else:
                print("⚠️  代码混淆可能不完整")
            
            # 显示部分混淆结果
            print("\n🔍 混淆结果预览:")
            print(obfuscated_content[:500] + "..." if len(obfuscated_content) > 500 else obfuscated_content)
            
        else:
            print("❌ 输出文件未生成")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    finally:
        # 清理测试文件
        for file in [test_input_file, test_output_file]:
            if os.path.exists(file):
                os.remove(file)

def test_code_string():
    """测试代码字符串混淆"""
    print("\n🧪 测试代码字符串混淆...")
    
    test_code = """
function testFunction() {
    const secretMessage = "This is a secret message";
    const apiKey = "sk-1234567890abcdef";
    console.log("Debug:", secretMessage);
    return secretMessage + " - " + apiKey;
}
"""
    
    try:
        obfuscator = JSObfuscator()
        obfuscated_code = obfuscator.obfuscate_js(test_code)
        
        print(f"✅ 代码字符串混淆成功！")
        print(f"📊 原始大小: {len(test_code)} 字符")
        print(f"📊 混淆后大小: {len(obfuscated_code)} 字符")
        
        # 检查是否包含原始的关键字
        if "testFunction" not in obfuscated_code and "secretMessage" not in obfuscated_code:
            print("✅ 代码已被正确混淆")
        else:
            print("⚠️  代码混淆可能不完整")
        
        print("\n🔍 混淆结果:")
        print(obfuscated_code)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_custom_options():
    """测试自定义选项"""
    print("\n🧪 测试自定义混淆选项...")
    
    test_code = """
function importantFunction() {
    const config = {
        apiUrl: "https://api.example.com",
        timeout: 5000,
        retries: 3
    };
    
    console.log("Configuration:", config);
    return config;
}
"""
    
    custom_options = {
        "controlFlowFlattening": True,
        "controlFlowFlatteningThreshold": 0.8,
        "deadCodeInjection": True,
        "deadCodeInjectionThreshold": 0.5,
        "stringArray": True,
        "stringArrayThreshold": 0.8,
        "transformObjectKeys": True,
        "unicodeEscapeSequence": True
    }
    
    try:
        obfuscator = JSObfuscator(custom_options)
        obfuscated_code = obfuscator.obfuscate_js(test_code)
        
        print(f"✅ 自定义选项混淆成功！")
        print(f"📊 原始大小: {len(test_code)} 字符")
        print(f"📊 混淆后大小: {len(obfuscated_code)} 字符")
        
        # 检查是否包含原始的关键字
        if "importantFunction" not in obfuscated_code and "apiUrl" not in obfuscated_code:
            print("✅ 代码已被正确混淆")
        else:
            print("⚠️  代码混淆可能不完整")
        
        print("\n🔍 自定义选项混淆结果预览:")
        print(obfuscated_code[:300] + "..." if len(obfuscated_code) > 300 else obfuscated_code)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试 js_obfuscator.py\n")
    
    # 检查Node.js和javascript-obfuscator
    print("🔍 检查环境...")
    try:
        obfuscator = JSObfuscator()
        print("✅ 环境检查通过")
    except Exception as e:
        print(f"❌ 环境检查失败: {e}")
        sys.exit(1)
    
    # 运行测试
    test_code_string()
    test_custom_options()
    test_single_file()
    
    print("\n🎉 所有测试完成！")