#!/usr/bin/env python3
"""
测试INI配置文件功能
"""

import os
import sys
from js_obfuscator import JSObfuscator

def test_ini_config():
    """测试INI配置文件加载和使用"""
    print("🧪 测试INI配置文件功能...")
    
    # 测试代码
    test_code = """
function calculateTotal(items) {
    const result = {
        total: 0,
        count: items.length
    };
    
    for (let item of items) {
        result.total += item.price * item.quantity;
    }
    
    return result;
}

const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 3 }
];

console.log('Total:', calculateTotal(items));
"""
    
    # 测试1: 使用默认配置
    print("\n📋 测试1: 使用默认配置")
    try:
        obfuscator = JSObfuscator()
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ 默认配置混淆成功，大小: {len(obfuscated)} 字符")
        print(f"配置选项: transformObjectKeys={obfuscator.options.get('transformObjectKeys', '未设置')}")
        print(f"配置选项: debugProtection={obfuscator.options.get('debugProtection', '未设置')}")
    except Exception as e:
        print(f"❌ 默认配置测试失败: {e}")
    
    # 测试2: 使用BALANCED配置
    print("\n📋 测试2: 使用BALANCED配置")
    try:
        obfuscator = JSObfuscator(config_file="obfuscator_config.ini", config_section="BALANCED")
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ BALANCED配置混淆成功，大小: {len(obfuscated)} 字符")
        print(f"配置选项: transformObjectKeys={obfuscator.options.get('transformObjectKeys', '未设置')}")
        print(f"配置选项: controlFlowFlatteningThreshold={obfuscator.options.get('controlFlowFlatteningThreshold', '未设置')}")
        print(f"配置选项: stringArrayThreshold={obfuscator.options.get('stringArrayThreshold', '未设置')}")
    except Exception as e:
        print(f"❌ BALANCED配置测试失败: {e}")
    
    # 测试3: 使用AGGRESSIVE配置
    print("\n📋 测试3: 使用AGGRESSIVE配置")
    try:
        obfuscator = JSObfuscator(config_file="obfuscator_config.ini", config_section="AGGRESSIVE")
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ AGGRESSIVE配置混淆成功，大小: {len(obfuscated)} 字符")
        print(f"配置选项: transformObjectKeys={obfuscator.options.get('transformObjectKeys', '未设置')}")
        print(f"配置选项: debugProtection={obfuscator.options.get('debugProtection', '未设置')}")
        print(f"配置选项: renameGlobals={obfuscator.options.get('renameGlobals', '未设置')}")
    except Exception as e:
        print(f"❌ AGGRESSIVE配置测试失败: {e}")
    
    # 测试4: 使用MINIMAL配置
    print("\n📋 测试4: 使用MINIMAL配置")
    try:
        obfuscator = JSObfuscator(config_file="obfuscator_config.ini", config_section="MINIMAL")
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ MINIMAL配置混淆成功，大小: {len(obfuscated)} 字符")
        print(f"配置选项: compact={obfuscator.options.get('compact', '未设置')}")
        print(f"配置选项: stringArray={obfuscator.options.get('stringArray', '未设置')}")
        print(f"配置选项: controlFlowFlattening={obfuscator.options.get('controlFlowFlattening', '未设置')}")
    except Exception as e:
        print(f"❌ MINIMAL配置测试失败: {e}")
    
    # 测试5: 使用DEBUG配置
    print("\n📋 测试5: 使用DEBUG配置")
    try:
        obfuscator = JSObfuscator(config_file="obfuscator_config.ini", config_section="DEBUG")
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ DEBUG配置混淆成功，大小: {len(obfuscated)} 字符")
        print(f"配置选项: compact={obfuscator.options.get('compact', '未设置')}")
        print(f"配置选项: log={obfuscator.options.get('log', '未设置')}")
        print(f"配置选项: stringArray={obfuscator.options.get('stringArray', '未设置')}")
    except Exception as e:
        print(f"❌ DEBUG配置测试失败: {e}")
    
    # 测试6: 配置文件不存在的情况
    print("\n📋 测试6: 配置文件不存在的情况")
    try:
        obfuscator = JSObfuscator(config_file="non_existent_config.ini")
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ 配置文件不存在时回退到默认配置，混淆成功，大小: {len(obfuscated)} 字符")
    except Exception as e:
        print(f"❌ 配置文件不存在测试失败: {e}")
    
    # 测试7: 配置文件存在但section不存在的情况
    print("\n📋 测试7: 配置文件存在但section不存在的情况")
    try:
        obfuscator = JSObfuscator(config_file="obfuscator_config.ini", config_section="NON_EXISTENT")
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ section不存在时回退到默认配置，混淆成功，大小: {len(obfuscated)} 字符")
    except Exception as e:
        print(f"❌ section不存在测试失败: {e}")
    
    # 测试8: 配置文件 + 用户选项的组合
    print("\n📋 测试8: 配置文件 + 用户选项的组合")
    try:
        user_options = {
            "transformObjectKeys": True,
            "debugProtection": True
        }
        obfuscator = JSObfuscator(
            options=user_options,
            config_file="obfuscator_config.ini",
            config_section="BALANCED"
        )
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ 配置文件+用户选项组合成功，大小: {len(obfuscated)} 字符")
        print(f"配置选项: transformObjectKeys={obfuscator.options.get('transformObjectKeys', '未设置')} (用户覆盖)")
        print(f"配置选项: debugProtection={obfuscator.options.get('debugProtection', '未设置')} (用户覆盖)")
        print(f"配置选项: controlFlowFlatteningThreshold={obfuscator.options.get('controlFlowFlatteningThreshold', '未设置')} (来自配置文件)")
    except Exception as e:
        print(f"❌ 配置文件+用户选项组合测试失败: {e}")

def test_config_file_parsing():
    """测试配置文件解析功能"""
    print("\n\n🧪 测试配置文件解析功能...")
    
    # 创建测试配置文件
    test_config_content = """[TEST_CONFIG]
compact = true
controlFlowFlattening = true
controlFlowFlatteningThreshold = 0.85
deadCodeInjection = true
deadCodeInjectionThreshold = 0.5
debugProtection = false
disableConsoleOutput = true
log = false
renameGlobals = true
rotateStringArray = true
selfDefending = true
shuffleStringArray = true
splitStrings = true
splitStringsChunkLength = 8
stringArray = true
stringArrayEncoding = rc4,base64
stringArrayThreshold = 0.85
transformObjectKeys = true
unicodeEscapeSequence = true
identifierNamesGenerator = mangled
"""
    
    test_config_file = "test_config.ini"
    
    try:
        # 写入测试配置文件
        with open(test_config_file, 'w', encoding='utf-8') as f:
            f.write(test_config_content)
        
        print(f"✅ 创建测试配置文件: {test_config_file}")
        
        # 测试解析
        obfuscator = JSObfuscator(config_file=test_config_file, config_section="TEST_CONFIG")
        
        # 验证解析结果
        expected_values = {
            "compact": True,
            "controlFlowFlattening": True,
            "controlFlowFlatteningThreshold": 0.85,
            "deadCodeInjection": True,
            "deadCodeInjectionThreshold": 0.5,
            "debugProtection": False,
            "disableConsoleOutput": True,
            "log": False,
            "renameGlobals": True,
            "rotateStringArray": True,
            "selfDefending": True,
            "shuffleStringArray": True,
            "splitStrings": True,
            "splitStringsChunkLength": 8,
            "stringArray": True,
            "stringArrayEncoding": ["rc4", "base64"],
            "stringArrayThreshold": 0.85,
            "transformObjectKeys": True,
            "unicodeEscapeSequence": True,
            "identifierNamesGenerator": "mangled"
        }
        
        print("📋 验证解析结果:")
        all_correct = True
        for key, expected_value in expected_values.items():
            actual_value = obfuscator.options.get(key)
            if actual_value == expected_value:
                print(f"  ✅ {key}: {actual_value}")
            else:
                print(f"  ❌ {key}: 期望 {expected_value}, 实际 {actual_value}")
                all_correct = False
        
        if all_correct:
            print("✅ 所有配置项解析正确！")
        else:
            print("⚠️  部分配置项解析有误")
        
        # 测试混淆功能
        test_code = "function test() { return 'hello'; }"
        obfuscated = obfuscator.obfuscate_js(test_code, "test.js")
        print(f"✅ 配置解析后混淆功能正常，结果大小: {len(obfuscated)} 字符")
        
    except Exception as e:
        print(f"❌ 配置文件解析测试失败: {e}")
    finally:
        # 清理测试文件
        if os.path.exists(test_config_file):
            os.remove(test_config_file)
            print(f"🗑️  清理测试文件: {test_config_file}")

if __name__ == "__main__":
    print("🚀 开始测试 INI 配置文件功能\n")
    
    test_ini_config()
    test_config_file_parsing()
    
    print("\n🎉 所有测试完成！")